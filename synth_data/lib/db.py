"""Unified database protocol for BigQuery and Teradata."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Database(Protocol):
    """Interface that both BigQuery and Teradata backends implement."""

    def connect(self) -> None: ...

    def close(self) -> None: ...

    def list_databases(self) -> list[str]: ...

    def list_tables(self, database: str) -> list[dict[str, str]]: ...

    def get_columns(self, database: str, table: str) -> list[tuple[str, Any]]: ...

    def get_column_names(self, database: str, table: str) -> list[str]: ...

    def read_table(self, database: str, table: str, limit: int = 20) -> list[tuple]: ...

    def read_column_values(self, database: str, table: str, column: str) -> list[Any]: ...

    def insert_fake_rows(
        self,
        database: str,
        table: str,
        columns: list[tuple[str, Any]],
        num_rows: int = 100,
        batch_size: int = 50,
        fk_overrides: dict[str, list[Any]] | None = None,
    ) -> int: ...

    def seed_all(self, database: str, num_rows: int = 100) -> list[tuple[str, int, str]]: ...

    def seed_with_relations(
        self,
        database: str,
        seed_order: list[tuple[str, int]],
        fk_map: dict[str, dict[str, tuple[str, str]]],
    ) -> list[tuple[str, int, str]]: ...

    def create_schema(self, database: str) -> list[str]: ...

    def drop_schema(self, database: str) -> list[str]: ...
