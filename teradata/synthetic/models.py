import re
from typing import Any

import polars as pl
from sqlmodel import SQLModel, Field


def _sanitize_name(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if s and s[0].isdigit():
        s = "col_" + s
    return s.lower()


def _table_key(database: str, table: str) -> str:
    return f"{_sanitize_name(database)}__{_sanitize_name(table)}"


def _td_type_to_sqlalchemy(data_type: str) -> str:
    dt = (data_type or "").strip().upper()
    if dt.startswith("VARCHAR"):
        m = re.match(r"VARCHAR\((\d+)\)", dt)
        size = int(m.group(1)) if m else 255
        return f"VARCHAR({min(size, 10000)})"
    if dt.startswith("CHAR"):
        m = re.match(r"CHAR\((\d+)\)", dt)
        size = int(m.group(1)) if m else 1
        return f"CHAR({size})"
    if dt.startswith("DECIMAL"):
        m = re.match(r"DECIMAL\((\d+),(\d+)\)", dt)
        if m:
            return f"DECIMAL({m.group(1)},{m.group(2)})"
        return "DECIMAL(18,4)"
    if dt in ("INTEGER", "INT"):
        return "INTEGER"
    if dt == "BIGINT":
        return "BIGINT"
    if dt == "SMALLINT":
        return "SMALLINT"
    if dt == "BYTEINT":
        return "TINYINT"
    if dt == "FLOAT":
        return "FLOAT"
    if dt == "DATE":
        return "DATE"
    if dt.startswith("TIMESTAMP"):
        return "TIMESTAMP"
    if dt.startswith("TIME"):
        return "TIME"
    if dt == "JSON" or dt == "XML":
        return "TEXT"
    if dt.startswith("NUMBER"):
        m = re.match(r"NUMBER\((\d+),(\d+)\)", dt)
        if m:
            p, s = int(m.group(1)), int(m.group(2))
            if s > 0:
                return f"DECIMAL({p},{s})"
            if p <= 9:
                return "INTEGER"
            return "BIGINT"
        return "DECIMAL(18,4)"
    if dt.startswith("INTERVAL") or dt.startswith("PERIOD") or dt == "DATASET":
        return "TEXT"
    if dt in ("BLOB", "CLOB", "VARBYTE", "BYTE"):
        return "TEXT"
    return "TEXT"


def _python_type_from_sqlalchemy(sa_type: str) -> type:
    t = sa_type.upper()
    if "INT" in t:
        return int
    if "FLOAT" in t or "DOUBLE" in t:
        return float
    if "DECIMAL" in t or "NUMERIC" in t:
        return float
    return str


def build_table_model(
    database: str,
    table: str,
    columns_df: pl.DataFrame,
) -> type[SQLModel] | None:
    cols = columns_df.sort("ColumnId").to_dicts()
    if not cols:
        return None

    annotations: dict[str, Any] = {}
    field_map: dict[str, dict] = {}

    for col in cols:
        col_name = col.get("ColumnName", "")
        if not col_name:
            continue

        safe_name = _sanitize_name(col_name)
        data_type = col.get("DataType", "")
        is_nullable = col.get("IsNullable", True)
        sa_type = _td_type_to_sqlalchemy(data_type)
        py_type = _python_type_from_sqlalchemy(sa_type)

        if is_nullable:
            annotations[safe_name] = py_type | None
        else:
            annotations[safe_name] = py_type

        field_map[safe_name] = {
            "td_name": col_name,
            "sa_type": sa_type,
            "python_type": py_type,
            "nullable": is_nullable,
            "data_type": data_type,
        }

    if not annotations:
        return None

    tablename = _table_key(database, table)
    model = type(
        tablename,
        (SQLModel,),
        {
            "__tablename__": tablename,
            "__annotations__": annotations,
        },
    )
    model._field_map = field_map  # type: ignore
    model._table_key = f"{database}.{table}"  # type: ignore
    model._database = database  # type: ignore
    model._table_name = table  # type: ignore
    return model
