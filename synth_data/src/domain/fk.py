"""Shared foreign-key resolution logic for database backends."""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Any

from src.domain.ports import Database


def resolve_fk_overrides(
    reader: Database,
    database: str,
    table_id: str,
    fk_map: dict[str, dict[str, tuple[str, str]]],
    parent_cache: dict[tuple[str, str], list[Any]],
) -> dict[str, list[Any]] | None:
    overrides: dict[str, list[Any]] = {}
    for child_col, (parent_table, parent_col) in fk_map.get(table_id, {}).items():
        key = (parent_table, parent_col)
        if key not in parent_cache:
            parent_cache[key] = reader.read_column_values(database, parent_table, parent_col)
        if not parent_cache[key]:
            return None
        overrides[child_col] = parent_cache[key]
    return overrides


def discover_fk_map(
    reader: Database,
    database: str,
    tables: list[str],
) -> dict[str, dict[str, tuple[str, str]]]:
    fk_map: dict[str, dict[str, tuple[str, str]]] = {}
    for table in tables:
        fks = reader.get_foreign_keys(database, table)
        if fks:
            fk_map[table] = {fk["column"]: (fk["ref_table"], fk["ref_column"]) for fk in fks}
    return fk_map


def validate_fk_map(
    checker: Database,
    database: str,
    fk_map: dict[str, dict[str, tuple[str, str]]],
) -> dict[str, dict[str, tuple[str, str]]]:
    log = logging.getLogger(__name__)
    validated: dict[str, dict[str, tuple[str, str]]] = {}
    for child, fks in fk_map.items():
        valid: dict[str, tuple[str, str]] = {}
        for child_col, (parent_table, parent_col) in fks.items():
            if not checker.table_exists(database, parent_table):
                log.warning(
                    "FK %s.%s -> %s.%s: parent table %s not found, skipping",
                    child,
                    child_col,
                    parent_table,
                    parent_col,
                    parent_table,
                )
                continue
            if not checker.column_exists(database, parent_table, parent_col):
                log.warning(
                    "FK %s.%s -> %s.%s: parent column %s not found, skipping",
                    child,
                    child_col,
                    parent_table,
                    parent_col,
                    parent_col,
                )
                continue
            valid[child_col] = (parent_table, parent_col)
        if valid:
            validated[child] = valid
    return validated


def topo_sort(
    tables: list[str],
    fk_map: dict[str, dict[str, tuple[str, str]]],
) -> list[str]:
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
    q: deque[str] = deque(t for t in tables if in_degree[t] == 0)
    result: list[str] = []
    while q:
        node = q.popleft()
        result.append(node)
        for dep in dependents[node]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                q.append(dep)
    for t in tables:
        if t not in result:
            result.append(t)
    return result
