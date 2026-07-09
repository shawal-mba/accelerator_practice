"""BigQuery backend — implements the Database protocol."""

from __future__ import annotations

import logging
import random
from collections.abc import Callable, Sequence
from typing import Any

from google.api_core.exceptions import GoogleAPIError, NotFound
from google.cloud import bigquery

from lib.fk import resolve_fk_overrides
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

    # ── Read operations ──────────────────────────────────────────────────────

    def list_databases(self) -> list[str]:
        return sorted(ds.dataset_id for ds in self.client.list_datasets())

    def list_tables(self, database: str) -> list[dict[str, str]]:
        tables = []
        for table in self.client.list_tables(f"{self.project}.{database}"):
            tables.append({"table_name": table.table_id, "table_type": table.table_type})
        return sorted(tables, key=lambda t: t["table_name"])

    def get_columns(self, database: str, table: str) -> Sequence[tuple[Any, ...]]:
        ref = self.client.get_table(f"{self.project}.{database}.{table}")
        return [(f.name, f.field_type, f.mode == "REPEATED") for f in ref.schema]

    def get_column_names(self, database: str, table: str) -> list[str]:
        ref = self.client.get_table(f"{self.project}.{database}.{table}")
        return [f.name for f in ref.schema]

    def read_table(self, database: str, table: str, limit: int = 20) -> list[tuple]:
        query = f"SELECT * FROM `{self.project}.{database}.{table}` LIMIT {limit}"
        return [tuple(row.values()) for row in self.client.query(query).result()]

    def read_column_values(self, database: str, table: str, column: str) -> list[Any]:
        query = (
            f"SELECT DISTINCT `{column}` FROM `{self.project}.{database}.{table}` "
            f"WHERE `{column}` IS NOT NULL"
        )
        return [row[column] for row in self.client.query(query).result()]

    # ── Write operations ─────────────────────────────────────────────────────

    def _build_record_gens(
        self, schema: list[bigquery.SchemaField]
    ) -> dict[str, list[tuple[str, Callable[[], Any]]]]:
        """Build generators for RECORD/STRUCT sub-fields."""
        result: dict[str, list[tuple[str, Callable[[], Any]]]] = {}
        for field in schema:
            if field.field_type in ("RECORD", "STRUCT") and field.fields:
                result[field.name] = [
                    (sub.name, match_column_bq(sub.name, sub.field_type))
                    for sub in field.fields
                ]
        return result

    def _generate_row(
        self,
        col_names: list[str],
        generators: list[Callable[[], Any]],
        repeated_flags: list[bool],
        fk_overrides: dict[str, list[Any]] | None,
        record_gens: dict[str, list[tuple[str, Callable[[], Any]]]],
    ) -> dict[str, Any]:
        """Generate a single fake row as a dict."""
        values: list[Any] = []
        for i, gen in enumerate(generators):
            col = col_names[i]
            if fk_overrides and col in fk_overrides:
                values.append(random.choice(fk_overrides[col]))
            elif col in record_gens:
                values.append({name: g() for name, g in record_gens[col]})
            else:
                values.append(gen())

        return dict(
            zip(
                col_names,
                [v if not rep else [v] for v, rep in zip(values, repeated_flags)],
            )
        )

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
        record_gens = self._build_record_gens(table_ref.schema)
        generators = [match_column_bq(n, t) for n, t, _ in columns]
        col_names = [n for n, _, _ in columns]
        repeated = [r for _, _, r in columns]

        inserted = 0
        for offset in range(0, num_rows, batch_size):
            batch = min(batch_size, num_rows - offset)
            rows = [
                self._generate_row(col_names, generators, repeated, fk_overrides, record_gens)
                for _ in range(batch)
            ]
            errors = self.client.insert_rows_json(table_ref, rows)
            if errors:
                raise RuntimeError(f"Insert errors: {errors}")
            inserted += batch
        return inserted

    # ── Seed operations ──────────────────────────────────────────────────────

    def _is_seedable(self, table_meta: dict[str, str]) -> bool:
        return table_meta.get("table_type") == "TABLE"

    def _seed_table(
        self,
        database: str,
        name: str,
        num_rows: int,
        fk_overrides: dict[str, list[Any]] | None = None,
    ) -> tuple[str, int, str]:
        """Seed a single table. Returns (name, inserted, status)."""
        columns = self.get_columns(database, name)
        if not columns:
            return (name, 0, "no columns found")
        inserted = self.insert_fake_rows(
            database, name, columns, num_rows, fk_overrides=fk_overrides
        )
        return (name, inserted, "ok")

    def seed_all(self, database: str, num_rows: int = 100) -> list[tuple[str, int, str]]:
        results: list[tuple[str, int, str]] = []
        for t in self.list_tables(database):
            name = t["table_name"]
            if not self._is_seedable(t):
                results.append((name, 0, f"skipped ({t['table_type']})"))
                continue
            try:
                results.append(self._seed_table(database, name, num_rows))
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
                fk_overrides = resolve_fk_overrides(
                    self, database, table_id, fk_map, parent_cache
                )
                if fk_overrides is None:
                    continue  # parent empty — skip
                results.append(self._seed_table(database, table_id, num_rows, fk_overrides))
            except (ValueError, RuntimeError) as exc:
                logger.warning("Failed to seed %s: %s", table_id, exc)
                results.append((table_id, 0, str(exc)))
        return results

    # ── Schema management ────────────────────────────────────────────────────

    def create_schema(self, database: str) -> list[str]:
        from lib.test_schema import BQ_TEST_TABLES, _make_schema_field

        created: list[str] = []
        for t in BQ_TEST_TABLES:
            table_id = t["name"]
            full_id = f"{self.project}.{database}.{table_id}"
            schema = [_make_schema_field(f) for f in t["columns"]]
            table = bigquery.Table(full_id, schema=schema)
            table.description = t["description"]
            table = self.client.create_table(table, exists_ok=True)
            created.append(table_id)
            logger.info("Created %s (%d columns)", table_id, len(schema))
        return created

    def drop_schema(self, database: str) -> list[str]:
        from lib.test_schema import BQ_TEST_TABLES

        dropped: list[str] = []
        for t in BQ_TEST_TABLES:
            full_id = f"{self.project}.{database}.{t['name']}"
            try:
                self.client.delete_table(full_id, not_found_ok=True)
                dropped.append(t["name"])
                logger.info("Dropped %s", t["name"])
            except NotFound:
                logger.debug("Table %s not found, skipping", t["name"])
            except GoogleAPIError as exc:
                logger.error("Error dropping %s: %s", t["name"], exc)
        return dropped
