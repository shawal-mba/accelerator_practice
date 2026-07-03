import time

import polars as pl

from .constants import OUT
from .loaders import load_columns, load_tables, load_indices
from .transforms import classify_env, build_tables_summary


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
