import polars as pl

from .constants import OUT


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
