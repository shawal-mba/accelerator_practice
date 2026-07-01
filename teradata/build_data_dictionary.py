import csv
import os
import sys
import time
from pathlib import Path

import polars as pl

csv.field_size_limit(sys.maxsize)

BASE = Path(__file__).parent
META = BASE / "metadata"
OUT = BASE / "output"
TMP = Path("/var/folders/qq/7rlmgyvd739ddj70pqjv0p880000gn/T/opencode")

TABLEKIND_NAMES = {
    "T": "Table",
    "V": "View",
    "O": "View",
    "P": "Procedure",
    "M": "Macro",
    "A": "Procedure",
    "R": "TableFunction",
    "F": "Function",
    "U": "UDT",
    "S": "Sequence",
    "t": "TempTable",
}
VALID_TABLE_KINDS = list(TABLEKIND_NAMES.keys())

COLUMN_TYPE_MAP = {
    "CV": "VARCHAR",
    "CF": "CHAR",
    "I": "INTEGER",
    "I1": "BYTEINT",
    "I2": "SMALLINT",
    "I8": "BIGINT",
    "D": "DECIMAL",
    "F": "FLOAT",
    "DA": "DATE",
    "TS": "TIMESTAMP",
    "TZ": "TIME WITH TIME ZONE",
    "AT": "TIME",
    "BF": "BYTE",
    "BV": "VARBYTE",
    "BO": "BLOB",
    "CO": "CLOB",
    "N": "NUMBER",
    "JN": "JSON",
    "XM": "XML",
    "UT": "UDT",
    "PD": "PERIOD(DATE)",
    "PT": "PERIOD(TIME)",
    "PS": "PERIOD(TIMESTAMP)",
    "PM": "PERIOD(TIMESTAMP WITH TIME ZONE)",
    "PZ": "PERIOD(TIMESTAMP WITH TIME ZONE)",
}
INTERVAL_CODES = ["YR", "YM", "MO", "DY", "DH", "DM", "DS",
                  "HR", "HM", "HS", "MI", "MS", "SC"]
PERIOD_CODES = ["PD", "PT", "PS", "PM", "PZ"]


def classify_env(db_name: str) -> str:
    u = db_name.upper()
    if u.startswith("PRD") or u in ("ABI_PRD", "OPS_PROD"):
        return "prod"
    if u.startswith("DEV"):
        return "dev"
    if u.startswith("TST"):
        return "test"
    if u.startswith("PRE"):
        return "pre"
    if db_name.islower() and db_name.isascii():
        return "sandbox"
    return "other"


def parse_csv_robust(
    input_path: Path, columns_to_keep: list[str]
) -> pl.DataFrame:
    with open(input_path, "r", encoding="utf-8", newline="") as fin:
        reader = csv.reader(fin, quotechar='"', escapechar="\\", doublequote=False)
        header = next(reader)
        n_cols = len(header)
        indices = [header.index(c) for c in columns_to_keep]

        rows: list[list[str]] = []
        for row in reader:
            if len(row) != n_cols:
                continue
            out: list[str] = []
            for i in indices:
                val = row[i]
                if "\n" in val or "\r" in val:
                    val = val.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
                out.append(val.strip())
            rows.append(out)

    return pl.DataFrame(rows, schema=columns_to_keep, orient="row")


def reconstruct_type_expr() -> pl.Expr:
    ct = pl.col("ColumnType")
    clen = pl.col("ColumnLength").cast(pl.Int64, strict=False)
    dt = pl.col("DecimalTotalDigits").cast(pl.Int64, strict=False)
    df = pl.col("DecimalFractionalDigits").cast(pl.Int64, strict=False)
    udt = pl.col("ColumnUDTName")

    return (
        pl.when(ct == "CV").then(pl.format("VARCHAR({})", clen))
        .when(ct == "CF").then(pl.format("CHAR({})", clen))
        .when(ct == "D").then(
            pl.when(dt.is_not_null() & (dt > 0))
            .then(pl.format("DECIMAL({},{})", dt, df.fill_null(0)))
            .otherwise(pl.lit("DECIMAL"))
        )
        .when(ct == "F").then(pl.lit("FLOAT"))
        .when(ct == "I").then(pl.lit("INTEGER"))
        .when(ct == "I1").then(pl.lit("BYTEINT"))
        .when(ct == "I2").then(pl.lit("SMALLINT"))
        .when(ct == "I8").then(pl.lit("BIGINT"))
        .when(ct == "DA").then(pl.lit("DATE"))
        .when(ct == "TS").then(
            pl.when(df.is_not_null() & (df > 0))
            .then(pl.format("TIMESTAMP({})", df))
            .otherwise(pl.lit("TIMESTAMP(6)"))
        )
        .when(ct == "AT").then(
            pl.when(df.is_not_null() & (df > 0))
            .then(pl.format("TIME({})", df))
            .otherwise(pl.lit("TIME"))
        )
        .when(ct == "TZ").then(pl.lit("TIME WITH TIME ZONE"))
        .when(ct == "BF").then(pl.format("BYTE({})", clen))
        .when(ct == "BV").then(pl.format("VARBYTE({})", clen))
        .when(ct == "BO").then(pl.format("BLOB({})", clen))
        .when(ct == "CO").then(pl.format("CLOB({})", clen))
        .when(ct == "N").then(
            pl.when(dt.is_not_null() & (dt > 0))
            .then(pl.format("NUMBER({},{})", dt, df.fill_null(0)))
            .otherwise(pl.lit("NUMBER"))
        )
        .when(ct == "JN").then(pl.lit("JSON"))
        .when(ct == "XM").then(pl.lit("XML"))
        .when(ct == "UT").then(
            pl.when(udt.is_not_null() & (udt != "")).then(udt).otherwise(pl.lit("UDT"))
        )
        .when(ct.is_in(INTERVAL_CODES + PERIOD_CODES))
        .then(ct.replace(COLUMN_TYPE_MAP))
        .otherwise(pl.format("{}({})", ct, clen))
    )


def load_columns() -> pl.DataFrame:
    t0 = time.time()
    print("[1/4] Parsing DBC.ColumnsV (csv module, handles embedded newlines) ...")
    df = parse_csv_robust(
        META / "dbc.ColumnsV.csv",
        [
            "DatabaseName", "TableName", "ColumnName", "ColumnType",
            "ColumnUDTName", "ColumnFormat", "ColumnTitle", "Nullable",
            "CommentString", "ColumnId", "ColumnLength",
            "DecimalTotalDigits", "DecimalFractionalDigits",
        ],
    )
    print(f"      parsed {df.height:,} rows ({time.time()-t0:.1f}s)")

    df = (
        df.lazy()
        .with_columns([
            pl.col("ColumnType").str.strip_chars(),
            pl.col("ColumnUDTName").str.strip_chars(),
            pl.col("Nullable").str.strip_chars(),
            pl.col("ColumnId").cast(pl.Int64, strict=False),
            pl.col("ColumnLength").cast(pl.Int64, strict=False),
            pl.col("DecimalTotalDigits").cast(pl.Int64, strict=False),
            pl.col("DecimalFractionalDigits").cast(pl.Int64, strict=False),
        ])
        .filter(pl.col("DatabaseName").str.strip_chars().is_not_null()
                & (pl.col("DatabaseName").str.strip_chars() != ""))
        .filter(pl.col("TableName").str.strip_chars().is_not_null()
                & (pl.col("TableName").str.strip_chars() != ""))
        .filter(pl.col("ColumnName").str.strip_chars().is_not_null()
                & (pl.col("ColumnName").str.strip_chars() != ""))
        .filter(pl.col("ColumnId").is_not_null())
        .with_columns([
            (pl.col("Nullable") == "Y").alias("IsNullable"),
            reconstruct_type_expr().alias("DataType"),
        ])
        .collect()
    )
    print(f"      after filtering: {df.height:,} valid column rows ({time.time()-t0:.1f}s)")
    return df


def load_tables() -> pl.DataFrame:
    t0 = time.time()
    print("[2/4] Parsing DBC.TablesV (csv module, handles embedded newlines) ...")
    df = parse_csv_robust(
        META / "dbc.TablesV.csv",
        ["DataBaseName", "TableName", "TableKind", "CommentString", "CreatorName"],
    )
    print(f"      parsed {df.height:,} rows ({time.time()-t0:.1f}s)")

    df = (
        df.lazy()
        .with_columns([
            pl.col("DataBaseName").str.strip_chars().alias("DatabaseName"),
            pl.col("TableName").str.strip_chars(),
            pl.col("TableKind").str.strip_chars().alias("TableKindRaw"),
            pl.col("CommentString").str.strip_chars().alias("TableComment"),
            pl.col("CreatorName").str.strip_chars().alias("TableCreator"),
        ])
        .filter(pl.col("TableKindRaw").is_in(VALID_TABLE_KINDS))
        .filter(pl.col("DatabaseName").is_not_null() & (pl.col("DatabaseName") != ""))
        .with_columns(
            pl.col("TableKindRaw").replace_strict(
                TABLEKIND_NAMES, default=pl.col("TableKindRaw")
            ).alias("TableKind")
        )
        .unique(subset=["DatabaseName", "TableName"])
        .select(["DatabaseName", "TableName", "TableKind", "TableKindRaw",
                 "TableComment", "TableCreator"])
        .collect()
    )
    print(f"      after filtering: {df.height:,} valid tables ({time.time()-t0:.1f}s)")
    return df


def load_indices() -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    t0 = time.time()
    print("[3/4] Loading DBC.IndicesV + DBC.All_RI_ChildrenV (Polars) ...")
    idx = (
        pl.read_csv(META / "dbc.IndicesV.csv", infer_schema_length=0, quote_char='"')
        .with_columns([
            pl.col("DatabaseName").str.strip_chars(),
            pl.col("TableName").str.strip_chars(),
            pl.col("ColumnName").str.strip_chars(),
            pl.col("IndexType").str.strip_chars().alias("IndexType"),
            pl.col("UniqueFlag").str.strip_chars().alias("UniqueFlag"),
        ])
        .lazy()
    )

    pi = (
        idx.filter(pl.col("IndexType") == "P")
        .with_columns(
            pl.when(pl.col("UniqueFlag") == "Y").then(pl.lit("UPI"))
            .otherwise(pl.lit("NUPI")).alias("PrimaryIndexRole")
        )
        .select(["DatabaseName", "TableName", "ColumnName", "PrimaryIndexRole"])
    )

    pk = (
        idx.filter(pl.col("IndexType") == "K")
        .group_by(["DatabaseName", "TableName", "ColumnName"])
        .agg(pl.lit("PK").alias("_pk_flag"))
    )

    si = (
        idx.filter(pl.col("IndexType").is_in(["Q", "S", "V", "A"]))
        .with_columns(
            pl.when(pl.col("UniqueFlag") == "Y").then(pl.lit("USI"))
            .otherwise(pl.lit("NUSI")).alias("SIRole")
        )
        .group_by(["DatabaseName", "TableName", "ColumnName"])
        .agg(pl.col("SIRole").unique().sort().str.join("/").alias("SecondaryIndex"))
    )

    ji = (
        idx.filter(pl.col("IndexType") == "J")
        .group_by(["DatabaseName", "TableName", "ColumnName"])
        .agg(pl.lit("JoinIndex").alias("_ji_flag"))
    )

    fk = (
        pl.read_csv(META / "dbc.All_RI_ChildrenV.csv",
                    infer_schema_length=0, quote_char='"')
        .with_columns([
            pl.col("ChildDB").str.strip_chars().alias("DatabaseName"),
            pl.col("ChildTable").str.strip_chars().alias("TableName"),
            pl.col("ChildKeyColumn").str.strip_chars().alias("ColumnName"),
            pl.col("ParentDB").str.strip_chars(),
            pl.col("ParentTable").str.strip_chars(),
            pl.col("ParentKeyColumn").str.strip_chars(),
            pl.col("IndexName").str.strip_chars().alias("FKName"),
        ])
        .lazy()
        .select(["DatabaseName", "TableName", "ColumnName",
                 "ParentDB", "ParentTable", "ParentKeyColumn", "FKName"])
    )

    print(f"      done ({time.time()-t0:.1f}s)")
    return pi.collect(), pk.collect(), si.collect(), ji.collect(), fk.collect()


def build() -> pl.DataFrame:
    cols_df = load_columns()
    tbl_df = load_tables()
    pi_df, pk_df, si_df, ji_df, fk_df = load_indices()

    t0 = time.time()
    print("[4/4] Joining all sources ...")

    dd = (
        cols_df.lazy()
        .join(tbl_df.lazy(), on=["DatabaseName", "TableName"], how="left")
        .join(pi_df.lazy(), on=["DatabaseName", "TableName", "ColumnName"], how="left")
        .join(pk_df.lazy(), on=["DatabaseName", "TableName", "ColumnName"], how="left")
        .join(si_df.lazy(), on=["DatabaseName", "TableName", "ColumnName"], how="left")
        .join(ji_df.lazy(), on=["DatabaseName", "TableName", "ColumnName"], how="left")
        .join(fk_df.lazy(), on=["DatabaseName", "TableName", "ColumnName"], how="left")
        .with_columns(
            pl.when(pl.col("_pk_flag").is_not_null()).then(pl.lit("PK"))
            .otherwise(pl.col("PrimaryIndexRole")).alias("PrimaryIndexRole"),
            pl.when(pl.col("ParentDB").is_not_null())
            .then(pl.concat_str([
                pl.col("ParentDB"), pl.col("ParentTable"), pl.col("ParentKeyColumn")
            ], separator="."))
            .otherwise(None).alias("ForeignKey"),
        )
        .with_columns(
            pl.concat_str(
                [
                    pl.when(pl.col("PrimaryIndexRole").is_not_null())
                    .then(pl.col("PrimaryIndexRole")).otherwise(pl.lit("")),
                    pl.when(pl.col("SecondaryIndex").is_not_null())
                    .then(pl.col("SecondaryIndex")).otherwise(pl.lit("")),
                ],
                separator=";",
            ).str.strip_chars(";").alias("IndexInfo")
        )
        .with_columns(
            pl.col("DatabaseName").map_elements(classify_env, return_dtype=pl.String)
            .alias("Environment")
        )
        .select([
            "Environment",
            "DatabaseName",
            "TableName",
            "TableKind",
            "TableKindRaw",
            "ColumnName",
            "ColumnId",
            "DataType",
            "ColumnType",
            "ColumnLength",
            "DecimalTotalDigits",
            "DecimalFractionalDigits",
            "ColumnFormat",
            "ColumnTitle",
            "IsNullable",
            "CommentString",
            "PrimaryIndexRole",
            "SecondaryIndex",
            "IndexInfo",
            "ForeignKey",
            "FKName",
            "TableComment",
            "TableCreator",
        ])
        .sort(["Environment", "DatabaseName", "TableName", "ColumnId"])
        .collect()
    )
    print(f"      done ({time.time()-t0:.1f}s) — {dd.height:,} rows")
    return dd


def build_tables_summary(dd: pl.DataFrame) -> pl.DataFrame:
    pi = (
        dd.filter(pl.col("PrimaryIndexRole").is_not_null())
        .group_by(["Environment", "DatabaseName", "TableName", "TableKind"])
        .agg(
            pl.col("PrimaryIndexRole").first().alias("PIType"),
            pl.col("ColumnName").str.join(", ").alias("PrimaryIndex"),
        )
    )

    si = (
        dd.filter(pl.col("SecondaryIndex").is_not_null())
        .group_by(["Environment", "DatabaseName", "TableName"])
        .agg(pl.col("ColumnName").str.join(", ").alias("SecondaryIndexCols"))
    )

    summary = (
        dd.group_by(["Environment", "DatabaseName", "TableName", "TableKind", "TableComment"])
        .agg(
            pl.len().alias("ColumnCount"),
            pl.col("TableCreator").first().alias("Creator"),
            (pl.col("ForeignKey").is_not_null().any()).alias("HasForeignKey"),
        )
        .join(pi, on=["Environment", "DatabaseName", "TableName", "TableKind"], how="left")
        .join(si, on=["Environment", "DatabaseName", "TableName"], how="left")
        .with_columns(
            pl.when(pl.col("PIType").is_not_null())
            .then(pl.format("{}: {}", pl.col("PIType"), pl.col("PrimaryIndex")))
            .otherwise(pl.lit("")).alias("PrimaryIndex")
        )
        .select([
            "Environment",
            "DatabaseName",
            "TableName",
            "TableKind",
            "ColumnCount",
            "PrimaryIndex",
            "SecondaryIndexCols",
            "HasForeignKey",
            "TableComment",
            "Creator",
        ])
        .sort(["Environment", "DatabaseName", "TableName"])
    )
    return summary


def write_outputs(dd: pl.DataFrame, summary: pl.DataFrame) -> None:
    OUT.mkdir(exist_ok=True)

    dd.write_parquet(OUT / "data_dictionary.parquet")
    summary.write_csv(OUT / "tables_summary.csv")

    envs = (
        dd.group_by("Environment")
        .agg(
            pl.len().alias("ColumnRows"),
            pl.col("DatabaseName").unique().len().alias("Databases"),
            (pl.col("DatabaseName") + "." + pl.col("TableName")).unique().len().alias("Tables"),
        )
        .sort("Environment")
    )
    envs.write_csv(OUT / "environment_summary.csv")

    print("\n  Output files:")
    print(f"    output/data_dictionary.parquet  ({dd.height:,} rows)")
    print(f"    output/tables_summary.csv       ({summary.height:,} tables)")
    print(f"    output/environment_summary.csv")

    print("\n  Per-environment splits:")
    for env in envs.select("Environment").to_series().to_list():
        env_dir = OUT / env
        env_dir.mkdir(exist_ok=True)

        dd_env = dd.filter(pl.col("Environment") == env)
        sm_env = summary.filter(pl.col("Environment") == env)

        dd_env.write_csv(env_dir / "data_dictionary.csv")
        dd_env.write_parquet(env_dir / "data_dictionary.parquet")
        sm_env.write_csv(env_dir / "tables_summary.csv")

        stats = envs.filter(pl.col("Environment") == env)
        print(
            f"    {env:10s}  {dd_env.height:>9,} cols  "
            f"{stats.select('Tables').item():>7,} tables  "
            f"{stats.select('Databases').item():>4} DBs  ->  {env_dir}/"
        )


def main():
    t0 = time.time()
    dd = build()
    summary = build_tables_summary(dd)
    print("\nWriting outputs:")
    write_outputs(dd, summary)
    print(f"\nTotal time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise
