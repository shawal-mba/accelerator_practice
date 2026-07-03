import csv
import sys
import time

import polars as pl

from .constants import META, COLUMN_TYPE_MAP, INTERVAL_CODES, PERIOD_CODES, VALID_TABLE_KINDS, TABLEKIND_NAMES

csv.field_size_limit(sys.maxsize)


def parse_csv_robust(
    input_path, columns_to_keep: list[str]
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
        pl.when(ct.is_null() | (ct == "")).then(None)
        .when(ct == "CV").then(pl.format("VARCHAR({})", clen))
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
        .when(ct == "++").then(pl.lit("INTERVAL YEAR TO MONTH"))
        .when(ct == "SZ").then(
            pl.when(clen.is_not_null() & (clen > 0))
            .then(pl.format("INTERVAL SECOND({})", df.fill_null(0)))
            .otherwise(pl.lit("INTERVAL SECOND"))
        )
        .when(ct == "DT").then(pl.lit("DATASET"))
        .when(ct == "VA").then(pl.format("VARCHAR({})", clen))
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


def load_indices() -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame]:
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
