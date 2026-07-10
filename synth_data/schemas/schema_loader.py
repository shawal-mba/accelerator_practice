"""Load a schema from a JSON definition file.

Usage::

    from schemas.schema_loader import load
    schema = load("1")           # schema_1.json
    schema = load(2)             # schema_2.json (int also works)
    schema = load("my_schema")   # schema_my_schema.json

The returned namespace has attributes:

    BQ_TEST_TABLES   – list of dicts for BigQuery table definitions
    TD_TEST_TABLES   – list of (name, ddl, description) tuples for Teradata
    SEED_ORDER       – list of (table_name, row_count) tuples
    FK_MAP           – dict[child_table][child_col] -> (parent_table, parent_col)
    _make_schema_field – function to convert a column dict to BigQuery SchemaField
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from google.cloud import bigquery

HERE = Path(__file__).resolve().parent


def _make_schema_field(f: dict) -> Any:
    """Convert a column dict to a BigQuery SchemaField."""
    d = dict(f)
    if "type" in d:
        d["field_type"] = d.pop("type")
    if "fields" in d:
        d["fields"] = [_make_schema_field(sub) for sub in d["fields"]]
    return bigquery.SchemaField(**d)


_VALID_IDS = {"1", "2", "td"}


def load(schema_id: str | int) -> SimpleNamespace:
    """Load a schema by ID (“1” or “2”) from the corresponding JSON file."""
    sid = str(schema_id)
    if sid not in _VALID_IDS:
        raise ValueError(f"Unknown schema '{sid}'. Valid IDs: {', '.join(sorted(_VALID_IDS))}")

    path = HERE / f"schema_{sid}.json"
    with open(path) as f:
        raw = json.load(f)

    raw["SEED_ORDER"] = [(name, rows) for name, rows in raw["SEED_ORDER"]]
    raw["FK_MAP"] = {
        child: {col: tuple(ref) for col, ref in fks.items()}
        for child, fks in raw["FK_MAP"].items()
    }
    ns = SimpleNamespace(**raw)
    ns._make_schema_field = _make_schema_field
    return ns
