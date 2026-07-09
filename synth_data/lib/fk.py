"""Shared foreign-key resolution logic for database backends.

Design choices
--------------

FK discovery is runtime-based rather than hardcoded because:
- The tool must work with **any** database schema, not just the predefined
  test tables.  Hardcoding FK maps in ``test_schema.py`` only covers the
  test fixtures; real databases have their own constraints.
- Database metadata (``INFORMATION_SCHEMA`` in BigQuery, ``DBC`` views in
  Teradata) already stores FK relationships.  Querying it keeps the code
  DRY and avoids schema drift between the tool and the actual database.

Topological sort (Kahn's algorithm) is used to determine seed order so
that parent rows always exist before child rows reference them.  If the
FK graph contains a cycle (e.g. mutual references), the remaining tables
are appended in their original order — this matches the "best effort"
behaviour expected when seeding test data.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Protocol


class ColumnReader(Protocol):
    """Minimal interface for reading a column's distinct values."""

    def read_column_values(self, database: str, table: str, column: str) -> list[Any]: ...


class ForeignKeyReader(Protocol):
    """Minimal interface for reading FK metadata."""

    def get_foreign_keys(
        self, database: str, table: str
    ) -> list[dict[str, str]]: ...


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


def discover_fk_map(
    reader: ForeignKeyReader,
    database: str,
    tables: list[str],
) -> dict[str, dict[str, tuple[str, str]]]:
    """Build an FK map by querying the database metadata for each table.

    Returns the same structure as ``FK_MAP`` in ``test_schema``:
    ``{child_table: {child_col: (parent_table, parent_col)}}``.
    """
    fk_map: dict[str, dict[str, tuple[str, str]]] = {}
    for table in tables:
        fks = reader.get_foreign_keys(database, table)
        if fks:
            fk_map[table] = {
                fk["column"]: (fk["ref_table"], fk["ref_column"])
                for fk in fks
            }
    return fk_map


def topo_sort(
    tables: list[str],
    fk_map: dict[str, dict[str, tuple[str, str]]],
) -> list[str]:
    """Return *tables* in dependency order (parents before children).

    Uses Kahn's algorithm. Tables with no FK dependencies come first.
    If a cycle is detected, the remaining tables are appended in original order.
    """
    table_set = set(tables)
    in_degree: dict[str, int] = {t: 0 for t in tables}
    dependents: dict[str, list[str]] = defaultdict(list)

    for child, fks in fk_map.items():
        if child not in table_set:
            continue
        for _child_col, (parent_table, _parent_col) in fks.items():
            if parent_table in table_set:
                in_degree[child] += 1
                dependents[parent_table].append(child)

    queue = deque(t for t in tables if in_degree[t] == 0)
    result: list[str] = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for dep in dependents[node]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    if len(result) != len(tables):
        for t in tables:
            if t not in result:
                result.append(t)

    return result
