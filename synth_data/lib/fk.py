"""Shared foreign-key resolution logic for database backends."""

from __future__ import annotations

from typing import Any, Protocol


class ColumnReader(Protocol):
    """Minimal interface for reading a column's distinct values."""

    def read_column_values(self, database: str, table: str, column: str) -> list[Any]: ...


def resolve_fk_overrides(
    reader: ColumnReader,
    database: str,
    table_id: str,
    fk_map: dict[str, dict[str, tuple[str, str]]],
    parent_cache: dict[tuple[str, str], list[Any]],
) -> dict[str, list[Any]] | None:
    """Resolve FK parent values for *table_id*.

    Returns ``None`` when a parent table has no rows (caller should skip the
    child table).  Parent values are cached in *parent_cache* so that each
    parent column is read at most once.
    """
    overrides: dict[str, list[Any]] = {}
    for child_col, (parent_table, parent_col) in fk_map.get(table_id, {}).items():
        cache_key = (parent_table, parent_col)
        if cache_key not in parent_cache:
            parent_cache[cache_key] = reader.read_column_values(
                database, parent_table, parent_col
            )
        values = parent_cache[cache_key]
        if not values:
            return None
        overrides[child_col] = values
    return overrides
