import re
import time
from pathlib import Path

import duckdb
import polars as pl
from faker import Faker

fake = Faker()

BASE = Path(__file__).parent.parent
OUT = BASE / "output"


def _td_type_to_duckdb(data_type: str) -> str:
    dt = (data_type or "").strip().upper()
    if dt.startswith("VARCHAR"):
        m = re.match(r"VARCHAR\((\d+)\)", dt)
        size = int(m.group(1)) if m else 255
        return f"VARCHAR({min(size, 10000)})"
    if dt.startswith("CHAR"):
        m = re.match(r"CHAR\((\d+)\)", dt)
        size = int(m.group(1)) if m else 1
        return f"VARCHAR({size})"
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
        return "DOUBLE"
    if dt == "DATE":
        return "DATE"
    if dt.startswith("TIMESTAMP"):
        return "TIMESTAMP"
    if dt.startswith("TIME"):
        return "TIME"
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
    return "VARCHAR(1000)"


def _generate_value(col: dict) -> any:
    data_type = (col.get("DataType") or "").strip().upper()
    col_name = (col.get("ColumnName") or "").lower()
    nullable = col.get("IsNullable", True)
    col_len = col.get("ColumnLength")
    dec_total = col.get("DecimalTotalDigits")
    dec_frac = col.get("DecimalFractionalDigits")

    if nullable and fake.random_int(min=1, max=100) <= 15:
        return None

    if data_type == "INTEGER" or data_type == "INT":
        return fake.random_int(min=0, max=999999999)
    if data_type == "BIGINT":
        return fake.random_int(min=1, max=999999999999)
    if data_type == "SMALLINT":
        return fake.random_int(min=0, max=32767)
    if data_type == "BYTEINT":
        return fake.random_int(min=0, max=127)
    if data_type == "FLOAT":
        return fake.pyfloat(min_value=0, max_value=99999)
    if data_type == "DATE":
        return fake.date_between(start_date="-5y", end_date="today")
    if data_type.startswith("TIMESTAMP"):
        return fake.date_time_between(start_date="-5y", end_date="now")
    if data_type.startswith("TIME"):
        return fake.time_object()

    if data_type.startswith("DECIMAL"):
        m = re.match(r"DECIMAL\((\d+),(\d+)\)", data_type)
        if m:
            p, s = int(m.group(1)), int(m.group(2))
            left = max(1, p - s)
            return fake.pydecimal(left_digits=left, right_digits=s, positive=True)
        return fake.pydecimal(left_digits=14, right_digits=4, positive=True)

    if data_type.startswith("NUMBER"):
        m = re.match(r"NUMBER\((\d+),(\d+)\)", data_type)
        if m:
            p, s = int(m.group(1)), int(m.group(2))
            if s > 0:
                return fake.pydecimal(left_digits=max(1, p - s), right_digits=s, positive=True)
            return fake.random_int(min=0, max=10**min(p, 9))
        return fake.random_int(min=0, max=999999999)

    if data_type.startswith("VARCHAR") or data_type.startswith("CHAR") or not data_type:
        max_len = col_len or 100
        if not data_type and max_len == 0:
            max_len = 100

        if "flg" in col_name or "flag" in col_name or "ind" in col_name:
            return fake.random_element(["Y", "N"])
        if "msisdn" in col_name or "phone" in col_name:
            return fake.msisdn()[:max_len]
        if "email" in col_name or "mail" in col_name:
            return fake.email()[:max_len]
        if max_len <= 1:
            return fake.random_element(["Y", "N", "A", "B", "C"])
        if max_len <= 5:
            return fake.lexify(text="?" * max_len)
        if max_len <= 20:
            return fake.pystr(min_chars=1, max_chars=max_len)
        return fake.text(max_nb_chars=min(max_len, 200))

    return fake.pystr(min_chars=1, max_chars=50)


def load_data_dictionary(
    environment: str | None = None,
    databases: list[str] | None = None,
    table_kinds: list[str] | None = None,
) -> pl.DataFrame:
    dd = pl.read_parquet(OUT / "data_dictionary.parquet")

    if environment:
        dd = dd.filter(pl.col("Environment") == environment)
    if databases:
        dd = dd.filter(pl.col("DatabaseName").is_in(databases))
    if table_kinds:
        dd = dd.filter(pl.col("TableKind").is_in(table_kinds))

    return dd


def create_duckdb_tables(
    conn: duckdb.DuckDBPyConnection,
    dd: pl.DataFrame,
    max_tables: int | None = None,
) -> list[tuple[str, str, list[str]]]:
    tables = dd.select(["DatabaseName", "TableName"]).unique().sort("DatabaseName", "TableName")
    if max_tables:
        tables = tables.head(max_tables)

    created = []
    for row in tables.iter_rows(named=True):
        db = row["DatabaseName"]
        tbl = row["TableName"]
        safe_name = f"{db}__{tbl}".lower()
        tbl_cols = dd.filter(
            (pl.col("DatabaseName") == db) & (pl.col("TableName") == tbl)
        ).sort("ColumnId")

        if tbl_cols.height == 0:
            continue

        col_defs = []
        col_names = []
        for c in tbl_cols.iter_rows(named=True):
            td_name = c.get("ColumnName", "")
            if not td_name:
                continue
            sa_type = _td_type_to_duckdb(c.get("DataType", ""))
            nullable = c.get("IsNullable", True)
            null_str = "" if nullable else " NOT NULL"
            col_defs.append(f'"{td_name}" {sa_type}{null_str}')
            col_names.append(td_name)

        if not col_defs:
            continue

        ddl = f'CREATE TABLE IF NOT EXISTS "{safe_name}" (\n  ' + ",\n  ".join(col_defs) + "\n)"
        conn.execute(ddl)
        created.append((safe_name, f"{db}.{tbl}", col_names))

    return created


def insert_rows(
    conn: duckdb.DuckDBPyConnection,
    table_name: str,
    rows: list[dict],
    columns: list[str],
) -> None:
    if not rows:
        return
    placeholders = ", ".join(["?" for _ in columns])
    col_names = ", ".join([f'"{c}"' for c in columns])
    sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'
    data = [[row.get(c) for c in columns] for row in rows]
    conn.executemany(sql, data)


def generate(
    environment: str = "dev",
    databases: list[str] | None = None,
    max_tables: int = 50,
    rows_per_table: int = 100,
    output_path: str | Path | None = None,
    table_kinds: list[str] | None = None,
) -> Path:
    t0 = time.time()

    if output_path is None:
        output_path = OUT / f"synthetic_{environment}.duckdb"
    output_path = Path(output_path)

    print(f"[1/4] Loading data dictionary for environment={environment} ...")
    dd = load_data_dictionary(environment=environment, databases=databases, table_kinds=table_kinds)
    print(f"      {dd.height:,} column rows across {dd.select('TableName').n_unique():,} tables")

    print(f"[2/4] Creating DuckDB tables (max_tables={max_tables}) ...")
    conn = duckdb.connect(str(output_path))
    table_info = create_duckdb_tables(conn, dd, max_tables=max_tables)
    print(f"      {len(table_info)} tables created")

    if not table_info:
        print("      No tables to generate. Exiting.")
        conn.close()
        return output_path

    print(f"[3/4] Generating synthetic data (rows_per_table={rows_per_table}) ...")
    total_rows = 0
    for i, (safe_name, orig_name, columns) in enumerate(table_info):
        tbl_cols = dd.filter(
            (pl.col("DatabaseName") + "." + pl.col("TableName") == orig_name)
        ).sort("ColumnId").to_dicts()

        rows = []
        for _ in range(rows_per_table):
            row = {}
            for c in tbl_cols:
                td_name = c.get("ColumnName", "")
                if td_name:
                    row[td_name] = _generate_value(c)
            rows.append(row)

        if rows:
            insert_rows(conn, safe_name, rows, columns)
            total_rows += len(rows)

        if (i + 1) % 10 == 0 or i + 1 == len(table_info):
            print(f"      [{i+1}/{len(table_info)}] {total_rows:,} rows inserted")

    print(f"\n[4/4] Finalizing ...")
    conn.close()

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Output: {output_path}")
    print(f"  Tables: {len(table_info)}")
    print(f"  Rows:   {total_rows:,} ({rows_per_table}/table)")

    return output_path
