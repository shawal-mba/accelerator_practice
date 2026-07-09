"""BigQuery backend — implements the Database protocol."""

from __future__ import annotations

import logging
import random
from collections.abc import Sequence
from typing import Any

from google.api_core.exceptions import GoogleAPIError, NotFound
from google.cloud import bigquery

from lib.matching import match_column_bq

logger = logging.getLogger(__name__)


class BigQueryDB:
    """BigQuery implementation of the Database protocol."""

    def __init__(self, project: str | None = None) -> None:
        self._project = project
        self._client: bigquery.Client | None = None

    def __enter__(self) -> BigQueryDB:
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def connect(self) -> None:
        self._client = bigquery.Client(project=self._project)

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    @property
    def client(self) -> bigquery.Client:
        if self._client is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._client

    @property
    def project(self) -> str:
        return self.client.project

    def list_databases(self) -> list[str]:
        return sorted(ds.dataset_id for ds in self.client.list_datasets())

    def list_tables(self, database: str) -> list[dict[str, str]]:
        tables = []
        for table in self.client.list_tables(f"{self.project}.{database}"):
            tables.append({"table_name": table.table_id, "table_type": table.table_type})
        return sorted(tables, key=lambda t: t["table_name"])

    def get_columns(self, database: str, table: str) -> Sequence[tuple[Any, ...]]:
        table_ref = self.client.get_table(f"{self.project}.{database}.{table}")
        return [
            (field.name, field.field_type, field.mode == "REPEATED") for field in table_ref.schema
        ]

    def get_column_names(self, database: str, table: str) -> list[str]:
        table_ref = self.client.get_table(f"{self.project}.{database}.{table}")
        return [field.name for field in table_ref.schema]

    def read_table(self, database: str, table: str, limit: int = 20) -> list[tuple]:
        query = f"SELECT * FROM `{self.project}.{database}.{table}` LIMIT {limit}"
        return [tuple(row.values()) for row in self.client.query(query).result()]

    def read_column_values(self, database: str, table: str, column: str) -> list[Any]:
        query = (
            f"SELECT DISTINCT `{column}` FROM `{self.project}.{database}.{table}` "
            f"WHERE `{column}` IS NOT NULL"
        )
        return [row[column] for row in self.client.query(query).result()]

    def insert_fake_rows(
        self,
        database: str,
        table: str,
        columns: Sequence[tuple[Any, ...]],
        num_rows: int = 100,
        batch_size: int = 50,
        fk_overrides: dict[str, list[Any]] | None = None,
    ) -> int:
        if not columns:
            raise ValueError(f"Table {database}.{table} has no columns")

        table_ref = self.client.get_table(f"{self.project}.{database}.{table}")

        record_gens: dict[str, list[tuple[str, Any]]] = {}
        for field in table_ref.schema:
            if field.field_type in ("RECORD", "STRUCT") and field.fields:
                record_gens[field.name] = [
                    (sub.name, match_column_bq(sub.name, sub.field_type)) for sub in field.fields
                ]

        generators = [match_column_bq(name, bq_type) for name, bq_type, _ in columns]
        col_names = [name for name, _, _ in columns]
        repeated_flags = [repeated for _, _, repeated in columns]

        inserted = 0
        for offset in range(0, num_rows, batch_size):
            batch = min(batch_size, num_rows - offset)
            rows = []
            for _ in range(batch):
                raw_values: list[Any] = []
                for i, gen in enumerate(generators):
                    col = col_names[i]
                    if fk_overrides and col in fk_overrides:
                        raw_values.append(random.choice(fk_overrides[col]))
                    elif col in record_gens:
                        raw_values.append({name: g() for name, g in record_gens[col]})
                    else:
                        raw_values.append(gen())
                row = dict(
                    zip(
                        col_names,
                        [v if not rep else [v] for v, rep in zip(raw_values, repeated_flags)],
                    )
                )
                rows.append(row)
            errors = self.client.insert_rows_json(table_ref, rows)
            if errors:
                raise RuntimeError(f"Insert errors: {errors}")
            inserted += batch
        return inserted

    def seed_all(self, database: str, num_rows: int = 100) -> list[tuple[str, int, str]]:
        tables = self.list_tables(database)
        results: list[tuple[str, int, str]] = []
        for t in tables:
            name = t["table_name"]
            if t["table_type"] != "TABLE":
                results.append((name, 0, f"skipped ({t['table_type']})"))
                continue
            try:
                columns = self.get_columns(database, name)
                if not columns:
                    results.append((name, 0, "no columns found"))
                    continue
                inserted = self.insert_fake_rows(database, name, columns, num_rows)
                results.append((name, inserted, "ok"))
            except (ValueError, RuntimeError) as exc:
                logger.warning("Failed to seed %s: %s", name, exc)
                results.append((name, 0, str(exc)))
        return results

    def seed_with_relations(
        self,
        database: str,
        seed_order: list[tuple[str, int]],
        fk_map: dict[str, dict[str, tuple[str, str]]],
    ) -> list[tuple[str, int, str]]:
        results: list[tuple[str, int, str]] = []
        parent_cache: dict[tuple[str, str], list[Any]] = {}

        for table_id, num_rows in seed_order:
            try:
                columns = self.get_columns(database, table_id)
                if not columns:
                    results.append((table_id, 0, "no columns found"))
                    continue

                fk_overrides: dict[str, list[Any]] = {}
                table_fks = fk_map.get(table_id, {})
                skip = False
                for child_col, (parent_table, parent_col) in table_fks.items():
                    cache_key = (parent_table, parent_col)
                    if cache_key not in parent_cache:
                        parent_cache[cache_key] = self.read_column_values(
                            database, parent_table, parent_col
                        )
                    values = parent_cache[cache_key]
                    if not values:
                        msg = f"parent {parent_table}.{parent_col} is empty"
                        results.append((table_id, 0, msg))
                        skip = True
                        break
                    fk_overrides[child_col] = values

                if skip:
                    continue

                inserted = self.insert_fake_rows(
                    database, table_id, columns, num_rows, fk_overrides=fk_overrides
                )
                results.append((table_id, inserted, "ok"))
            except (ValueError, RuntimeError) as exc:
                logger.warning("Failed to seed %s: %s", table_id, exc)
                results.append((table_id, 0, str(exc)))
        return results

    def create_schema(self, database: str) -> list[str]:
        from lib.test_schema import BQ_TEST_TABLES, _make_schema_field

        created: list[str] = []
        for t in BQ_TEST_TABLES:
            table_id = t["name"]
            schema_fields = t["columns"]
            description = t["description"]
            full_id = f"{self.project}.{database}.{table_id}"
            schema = [_make_schema_field(f) for f in schema_fields]
            table = bigquery.Table(full_id, schema=schema)
            table.description = description
            table = self.client.create_table(table, exists_ok=True)
            created.append(table_id)
            logger.info("Created %s (%d columns)", table_id, len(schema))
        return created

    def drop_schema(self, database: str) -> list[str]:
        from lib.test_schema import BQ_TEST_TABLES

        dropped: list[str] = []
        for table_id, _, _ in BQ_TEST_TABLES:
            full_id = f"{self.project}.{database}.{table_id}"
            try:
                self.client.delete_table(full_id, not_found_ok=True)
                dropped.append(table_id)
                logger.info("Dropped %s", table_id)
            except NotFound:
                logger.debug("Table %s not found, skipping", table_id)
            except GoogleAPIError as exc:
                logger.error("Error dropping %s: %s", table_id, exc)
        return dropped
