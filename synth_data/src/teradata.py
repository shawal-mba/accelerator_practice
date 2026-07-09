"""Teradata backend — implements the Database protocol."""

from __future__ import annotations

import logging
import random
from collections.abc import Callable, Sequence
from typing import Any

import teradatasql

from src.fk import discover_fk_map, resolve_fk_overrides, topo_sort, validate_fk_map
from src.matching import INLINE_TYPES, cast_td_value, ident, match_column_td

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

    # ── Read operations ──────────────────────────────────────────────────────

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

    def table_exists(self, database: str, table: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM DBC.TablesV WHERE DatabaseName = ? AND TableName = ?",
                [database, table],
            )
            return cur.fetchone() is not None

    def column_exists(self, database: str, table: str, column: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM DBC.ColumnsV "
                "WHERE DatabaseName = ? AND TableName = ? AND ColumnName = ?",
                [database, table, column],
            )
            return cur.fetchone() is not None

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
        db, tbl = ident(database), ident(table)
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {db}.{tbl} SAMPLE {limit}")
            return cur.fetchall()

    def read_column_values(self, database: str, table: str, column: str) -> list[Any]:
        db, tbl, col = ident(database), ident(table), ident(column)
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT DISTINCT {col} FROM {db}.{tbl} WHERE {col} IS NOT NULL")
            return [row[0] for row in cur.fetchall()]

    def get_foreign_keys(self, database: str, table: str) -> list[dict[str, str]]:
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT c.ColumnName, p.DatabaseName, p.TableName, "
                    "c.ParentKeyColumn "
                    "FROM DBC.ChildrenV c "
                    "JOIN DBC.ParentsV p "
                    "  ON c.ChildDB = p.ParentDB AND c.ChildTable = p.ParentTable "
                    "WHERE c.DatabaseName = ? AND c.TableName = ?",
                    [database, table],
                )
                return [
                    {
                        "column": row[0],
                        "ref_table": row[2],
                        "ref_column": row[3],
                    }
                    for row in cur.fetchall()
                ]
        except teradatasql.DatabaseError:
            # DBC.ChildrenV / DBC.ParentsV may not exist on all Teradata versions
            return []

    # ── Write operations ─────────────────────────────────────────────────────

    def _generate_value(
        self,
        col: str,
        gen: Callable[[], Any],
        td_type: str,
        fk_overrides: dict[str, list[Any]] | None,
    ) -> Any:
        """Generate a single value for a column, applying FK override if present."""
        if fk_overrides and col in fk_overrides:
            raw = random.choice(fk_overrides[col])
        else:
            raw = gen()
        if td_type in INLINE_TYPES:
            return cast_td_value(col, td_type, raw)
        return raw

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

        generators = [match_column_td(n, t) for n, t in columns]
        col_names = [n for n, _ in columns]
        td_types = [t for _, t in columns]
        has_inline = any(t in INLINE_TYPES for t in td_types)

        db, tbl = ident(database), ident(table)
        inserted = 0
        with self.conn.cursor() as cur:
            for offset in range(0, num_rows, batch_size):
                batch = min(batch_size, num_rows - offset)
                if has_inline:
                    inserted += self._insert_inline(
                        cur, db, tbl, col_names, td_types, generators, fk_overrides, batch
                    )
                else:
                    inserted += self._insert_batched(
                        cur, db, tbl, col_names, generators, fk_overrides, batch
                    )
        return inserted

    def _insert_inline(
        self,
        cur: Any,
        db: str,
        tbl: str,
        col_names: list[str],
        td_types: list[str],
        generators: list[Callable[[], Any]],
        fk_overrides: dict[str, list[Any]] | None,
        batch: int,
    ) -> int:
        """Insert rows one-by-one with inline CAST expressions."""
        inserted = 0
        for _ in range(batch):
            values = [
                self._generate_value(col, gen, td_type, fk_overrides)
                for col, gen, td_type in zip(col_names, generators, td_types)
            ]

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
                f"({', '.join(col_names)}) VALUES ({', '.join(parts)})"
            )
            cur.execute(sql, param_values)
            inserted += 1
        return inserted

    def _insert_batched(
        self,
        cur: Any,
        db: str,
        tbl: str,
        col_names: list[str],
        generators: list[Callable[[], Any]],
        fk_overrides: dict[str, list[Any]] | None,
        batch: int,
    ) -> int:
        """Insert rows in bulk via executemany."""
        col_names_str = ", ".join(col_names)
        placeholders = ", ".join("?" for _ in col_names)
        sql = f"INSERT INTO {db}.{tbl} ({col_names_str}) VALUES ({placeholders})"

        rows = [
            [
                random.choice(fk_overrides[col]) if fk_overrides and col in fk_overrides else gen()
                for col, gen in zip(col_names, generators)
            ]
            for _ in range(batch)
        ]
        cur.executemany(sql, rows)
        return batch

    # ── Seed operations ──────────────────────────────────────────────────────

    def _is_seedable(self, table_meta: dict[str, str]) -> bool:
        return table_meta.get("table_kind") == "T"

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
        """Seed all seedable tables with automatic FK resolution.

        Discovers FK relationships from Teradata metadata and topologically
        sorts tables so parents are seeded first.  Falls back to the
        hardcoded ``FK_MAP`` / ``SEED_ORDER`` from ``test_schema`` when
        metadata discovery returns nothing (e.g. on Teradata Vantage Express
        where ``DBC.ParentsV`` may not exist).
        """
        from src.test_schema import FK_MAP as _FK_MAP
        from src.test_schema import SEED_ORDER as _SEED_ORDER

        results: list[tuple[str, int, str]] = []
        seedable = [
            t["table_name"]
            for t in self.list_tables(database)
            if self._is_seedable(t)
        ]
        fk_map = discover_fk_map(self, database, seedable)
        fk_map = validate_fk_map(self, database, fk_map)

        if fk_map:
            ordered = topo_sort(seedable, fk_map)
        else:
            # FK metadata unavailable — use hardcoded order for known test tables
            known = {name for name, _ in _SEED_ORDER}
            ordered = [name for name, _ in _SEED_ORDER if name in set(seedable)]
            ordered += [t for t in seedable if t not in known]
            fk_map = {k: v for k, v in _FK_MAP.items() if k in set(seedable)}

        parent_cache: dict[tuple[str, str], list[Any]] = {}

        for name in ordered:
            try:
                fk_overrides = resolve_fk_overrides(
                    self, database, name, fk_map, parent_cache
                )
                if fk_overrides is None:
                    logger.info("Skipping %s: parent table has no rows", name)
                    results.append((name, 0, "skipped (parent empty)"))
                    continue
                results.append(
                    self._seed_table(database, name, num_rows, fk_overrides)
                )
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
                fk_overrides = resolve_fk_overrides(
                    self, database, table_id, fk_map, parent_cache
                )
                if fk_overrides is None:
                    logger.info("Skipping %s: parent table has no rows", table_id)
                    results.append((table_id, 0, "skipped (parent empty)"))
                    continue
                results.append(self._seed_table(database, table_id, num_rows, fk_overrides))
            except (ValueError, RuntimeError, teradatasql.DatabaseError) as exc:
                logger.warning("Failed to seed %s: %s", table_id, exc)
                results.append((table_id, 0, str(exc)))
        return results

    # ── Schema management ────────────────────────────────────────────────────

    def create_schema(self, database: str) -> list[str]:
        from src.test_schema import TD_TEST_TABLES

        db = ident(database)
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
        from src.test_schema import TD_TEST_TABLES

        db = ident(database)
        dropped: list[str] = []
        with self.conn.cursor() as cur:
            for table_name, _, _ in reversed(TD_TEST_TABLES):
                tbl = ident(table_name)
                try:
                    cur.execute(f"DROP TABLE {db}.{tbl}")
                    dropped.append(table_name)
                    logger.info("Dropped %s", table_name)
                except teradatasql.DatabaseError as exc:
                    if "does not exist" not in str(exc).lower():
                        logger.error("Error dropping %s: %s", table_name, exc)
        return dropped

    def purge_data(self, database: str) -> list[str]:
        """Delete all rows from every table in *database*.

        Uses multiple passes: tables blocked by FK constraints on the first
        pass are retried after their dependents have been deleted.  Stops
        when a full pass makes no progress.
        """
        tables = [
            t["table_name"]
            for t in self.list_tables(database)
            if t.get("table_kind") == "T"
        ]

        purged: list[str] = []
        remaining = list(tables)

        with self.conn.cursor() as cur:
            for _pass in range(len(tables) + 1):
                still_remaining: list[str] = []
                for name in remaining:
                    db, tbl = ident(database), ident(name)
                    try:
                        cur.execute(f"DELETE FROM {db}.{tbl}")
                        purged.append(name)
                        logger.info("Purged %s", name)
                    except Exception as exc:
                        still_remaining.append(name)
                        logger.debug("Deferred %s: %s", name, exc)
                if not still_remaining or still_remaining == remaining:
                    remaining = still_remaining
                    break
                remaining = still_remaining

        for name in remaining:
            logger.warning("Could not purge %s (FK constraint blocks delete)", name)

        return purged
