"""Teradata backend — implements the Database protocol."""

from __future__ import annotations

import logging
import random
from collections.abc import Sequence
from typing import Any

import teradatasql

from lib.matching import INLINE_TYPES, _ident, cast_td_value, match_column_td

logger = logging.getLogger(__name__)


class TeradataDB:
    """Teradata implementation of the Database protocol."""

    def __init__(self, host: str, user: str, password: str) -> None:
        self._host = host
        self._user = user
        self._password = password
        self._conn: teradatasql.TeradataConnection | None = None

    def __enter__(self) -> TeradataDB:
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def connect(self) -> None:
        self._conn = teradatasql.connect(
            None,
            host=self._host,
            user=self._user,
            password=self._password,
            encryptdata=True,
        )

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def conn(self) -> teradatasql.TeradataConnection:
        if self._conn is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._conn

    def list_databases(self) -> list[str]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT DatabaseName FROM DBC.DatabasesV ORDER BY 1")
            return [row[0] for row in cur.fetchall()]

    def list_tables(self, database: str) -> list[dict[str, str]]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT TableName, TableKind FROM DBC.TablesV WHERE DatabaseName = ? ORDER BY 1",
                [database],
            )
            return [{"table_name": row[0], "table_kind": row[1].strip()} for row in cur.fetchall()]

    def get_columns(self, database: str, table: str) -> Sequence[tuple[Any, ...]]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT ColumnName, ColumnType FROM DBC.ColumnsV "
                "WHERE DatabaseName = ? AND TableName = ? ORDER BY ColumnId",
                [database, table],
            )
            return [(row[0], row[1].strip()) for row in cur.fetchall()]

    def get_column_names(self, database: str, table: str) -> list[str]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT ColumnName FROM DBC.ColumnsV "
                "WHERE DatabaseName = ? AND TableName = ? ORDER BY ColumnId",
                [database, table],
            )
            return [row[0] for row in cur.fetchall()]

    def read_table(self, database: str, table: str, limit: int = 20) -> list[tuple]:
        db = _ident(database)
        tbl = _ident(table)
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {db}.{tbl} SAMPLE {limit}")
            return cur.fetchall()

    def read_column_values(self, database: str, table: str, column: str) -> list[Any]:
        db = _ident(database)
        tbl = _ident(table)
        col = _ident(column)
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT DISTINCT {col} FROM {db}.{tbl} WHERE {col} IS NOT NULL")
            return [row[0] for row in cur.fetchall()]

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

        generators = [match_column_td(name, td_type) for name, td_type in columns]
        col_name_list = [name for name, _ in columns]
        td_types = [td_type for _, td_type in columns]
        has_inline = any(t in INLINE_TYPES for t in td_types)

        db = _ident(database)
        tbl = _ident(table)
        inserted = 0
        with self.conn.cursor() as cur:
            for offset in range(0, num_rows, batch_size):
                batch = min(batch_size, num_rows - offset)
                if has_inline:
                    for _ in range(batch):
                        values: list[Any] = []
                        for i, gen in enumerate(generators):
                            col = col_name_list[i]
                            td_type = td_types[i]
                            if fk_overrides and col in fk_overrides:
                                raw = random.choice(fk_overrides[col])
                            else:
                                raw = gen()
                            if td_type in INLINE_TYPES:
                                values.append(cast_td_value(col, td_type, raw))
                            else:
                                values.append(raw)

                        parts = []
                        param_values = []
                        for i, val in enumerate(values):
                            if td_types[i] in INLINE_TYPES:
                                parts.append(val)
                            else:
                                parts.append("?")
                                param_values.append(val)

                        sql = (
                            f"INSERT INTO {db}.{tbl} "
                            f"({', '.join(col_name_list)}) "
                            f"VALUES ({', '.join(parts)})"
                        )
                        cur.execute(sql, param_values)
                        inserted += 1
                else:
                    col_names_str = ", ".join(col_name_list)
                    placeholders = ", ".join("?" for _ in columns)
                    sql = f"INSERT INTO {db}.{tbl} ({col_names_str}) VALUES ({placeholders})"
                    rows = []
                    for _ in range(batch):
                        row = []
                        for i, gen in enumerate(generators):
                            col = col_name_list[i]
                            if fk_overrides and col in fk_overrides:
                                row.append(random.choice(fk_overrides[col]))
                            else:
                                row.append(gen())
                        rows.append(row)
                    cur.executemany(sql, rows)
                    inserted += batch
        return inserted

    def seed_all(self, database: str, num_rows: int = 100) -> list[tuple[str, int, str]]:
        tables = self.list_tables(database)
        results: list[tuple[str, int, str]] = []
        for t in tables:
            name = t["table_name"]
            if t["table_kind"] != "T":
                results.append((name, 0, f"skipped ({t['table_kind']})"))
                continue
            try:
                columns = self.get_columns(database, name)
                if not columns:
                    results.append((name, 0, "no columns found"))
                    continue
                inserted = self.insert_fake_rows(database, name, columns, num_rows)
                results.append((name, inserted, "ok"))
            except (ValueError, RuntimeError, teradatasql.DatabaseError) as exc:
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
            except (ValueError, RuntimeError, teradatasql.DatabaseError) as exc:
                logger.warning("Failed to seed %s: %s", table_id, exc)
                results.append((table_id, 0, str(exc)))
        return results

    def create_schema(self, database: str) -> list[str]:
        from lib.test_schema import TD_TEST_TABLES

        db = _ident(database)
        created: list[str] = []
        with self.conn.cursor() as cur:
            try:
                cur.execute(f"CREATE DATABASE {db} AS PERMANENT = 1e8, SPOOL = 1e8")
                logger.info("Created database %s", database)
            except teradatasql.DatabaseError as exc:
                if "already exists" not in str(exc).lower():
                    logger.error("Error creating database %s: %s", database, exc)
                    return created
                logger.info("Database %s already exists", database)

            for table_name, ddl, _ in TD_TEST_TABLES:
                try:
                    cur.execute(ddl.format(db=db))
                    created.append(table_name)
                    logger.info("Created %s", table_name)
                except teradatasql.DatabaseError as exc:
                    if "already exists" not in str(exc).lower():
                        logger.error("Error creating %s: %s", table_name, exc)
                    else:
                        created.append(table_name)
                        logger.info("%s already exists", table_name)
        return created

    def drop_schema(self, database: str) -> list[str]:
        from lib.test_schema import TD_TEST_TABLES

        db = _ident(database)
        dropped: list[str] = []
        with self.conn.cursor() as cur:
            for table_name, _, _ in reversed(TD_TEST_TABLES):
                tbl = _ident(table_name)
                try:
                    cur.execute(f"DROP TABLE {db}.{tbl}")
                    dropped.append(table_name)
                    logger.info("Dropped %s", table_name)
                except teradatasql.DatabaseError as exc:
                    if "does not exist" not in str(exc).lower():
                        logger.error("Error dropping %s: %s", table_name, exc)
        return dropped
