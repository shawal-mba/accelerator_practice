"""Unified CLI for Teradata and BigQuery: analyse, seed, and test schemas."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from io import StringIO
from typing import Any

from dotenv import load_dotenv

from lib.bigquery import BigQueryDB
from lib.format import (
    column_list,
    created,
    data_table,
    database_list,
    dataset_list,
    dim,
    dropped,
    error,
    heading,
    seed_result_table,
    success,
    table_list,
    warning,
)
from lib.protocol import Database
from lib.teradata import TeradataDB
from lib.test_schema import FK_MAP, SEED_ORDER

load_dotenv()

logger = logging.getLogger(__name__)


class SynthDataError(Exception):
    """Base exception for synth-data CLI."""


class ConfigError(SynthDataError):
    """Configuration or credential errors."""


class TableError(SynthDataError):
    """Table not found or inaccessible."""


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        force=True,
    )


def _get_db(args: argparse.Namespace) -> Database:
    engine = args.engine
    if engine == "bigquery":
        project = args.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        if not project:
            raise ConfigError(
                "project is required for BigQuery. Pass --project or set GOOGLE_CLOUD_PROJECT."
            )
        db: Database = BigQueryDB(project=project)
    elif engine == "teradata":
        host = args.host or os.environ.get("TERADATA_HOST", "")
        user = args.user or os.environ.get("TERADATA_USER", "")
        password = os.environ.get("TERADATA_PASSWORD", "")
        if not all([host, user, password]):
            raise ConfigError(
                "host, user, and password are required for Teradata. "
                "Set TERADATA_HOST / TERADATA_USER / TERADATA_PASSWORD."
            )
        db = TeradataDB(host=host, user=user, password=password)
    else:
        raise ConfigError(f"Unknown engine: {engine}")
    return db


def _format_column(col: Any, engine: str) -> str:
    """Format a column tuple for display."""
    if engine == "bigquery":
        suffix = " [REPEATED]" if len(col) > 2 and col[2] else ""
        return f"{col[0]} ({col[1]}{suffix})"
    return f"{col[0]} ({col[1]})"


def _build_seed_report(
    db: Database, database: str, results: list[tuple[str, int, str]], engine: str
) -> str:
    buf = StringIO()
    total_inserted = 0
    for name, inserted, status in results:
        buf.write(f"=== {database}.{name} ===\n")
        if status == "ok":
            cols = db.get_columns(database, name)
            col_str = ", ".join(_format_column(c, engine) for c in cols)
            buf.write(f"Columns: {col_str}\n")
            buf.write(f"Inserted {inserted} rows\n\n")
            total_inserted += inserted
        else:
            buf.write(f"Status: {status}\n\n")
    buf.write(f"Summary: {len(results)} tables processed, {total_inserted} total rows\n")
    return buf.getvalue()


def cmd_analyze(args: argparse.Namespace) -> None:
    db = _get_db(args)
    with db:
        databases = db.list_databases()
        database = args.database or ""
        if database:
            tables = db.list_tables(database)
            kind_key = "table_type" if args.engine == "bigquery" else "table_kind"
            table_list(database, tables, kind_key=kind_key)
        elif args.engine == "bigquery":
            dataset_list(databases)
        else:
            database_list(databases)


def cmd_seed(args: argparse.Namespace) -> None:
    db = _get_db(args)
    with db:
        database = args.database
        if args.table:
            if args.table in FK_MAP:
                fk_cols = ", ".join(FK_MAP[args.table])
                warning(
                    f"Warning: {args.table} has FK columns ({fk_cols}) — "
                    f"random values will NOT match parent tables."
                )
                warning(
                    "  Use `seed-test` instead to maintain referential integrity.\n"
                )

            columns = db.get_columns(database, args.table)
            if not columns:
                raise TableError(f"{database}.{args.table} not found or has no columns.")

            column_list(database, args.table, columns, engine=args.engine)

            inserted = db.insert_fake_rows(database, args.table, columns, num_rows=args.rows)
            success(f"\nInserted {inserted} rows into {database}.{args.table}")

            if args.output:
                single = [(args.table, inserted, "ok")]
                report = _build_seed_report(db, database, single, args.engine)
                with open(args.output, "w") as f:
                    f.write(report)
                dim(f"Report written to {args.output}")
        else:
            heading(f"Seeding all tables in {database}...")
            results = db.seed_all(database, num_rows=args.rows)
            seed_result_table(results)

            report = _build_seed_report(db, database, results, args.engine)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(report)
                dim(f"\nReport written to {args.output}")


def cmd_read(args: argparse.Namespace) -> None:
    db = _get_db(args)
    with db:
        col_names = db.get_column_names(args.database, args.table)
        rows = db.read_table(args.database, args.table, limit=args.limit)
        data_table(col_names, rows)
        dim(f"({len(rows)} rows)")


def cmd_create_schema(args: argparse.Namespace) -> None:
    db = _get_db(args)
    with db:
        heading(f"Creating test tables in {args.database}")
        created_tables = db.create_schema(args.database)
        created(len(created_tables))


def cmd_drop_schema(args: argparse.Namespace) -> None:
    db = _get_db(args)
    with db:
        heading(f"Dropping test tables in {args.database}")
        dropped_tables = db.drop_schema(args.database)
        dropped(len(dropped_tables))


def cmd_seed_test(args: argparse.Namespace) -> None:
    db = _get_db(args)
    with db:
        heading(f"Seeding test tables in {args.database} with referential integrity")
        results = db.seed_with_relations(args.database, SEED_ORDER, FK_MAP)
        seed_result_table(results)

        report = _build_seed_report(db, args.database, results, args.engine)
        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            dim(f"\nReport written to {args.output}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="synth-data",
        description="Unified CLI for Teradata and BigQuery: analyse, seed, and test schemas.",
    )
    parser.add_argument(
        "--engine",
        choices=["bigquery", "teradata"],
        required=True,
        help="Database engine to use",
    )
    parser.add_argument(
        "--project",
        help="GCP project (BigQuery only, or env GOOGLE_CLOUD_PROJECT)",
    )
    parser.add_argument("--host", help="Teradata host (or env TERADATA_HOST)")
    parser.add_argument("--user", help="Teradata user (or env TERADATA_USER)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

    sub = parser.add_subparsers(dest="command")

    # --- analyze ---
    p_analyze = sub.add_parser("analyze", help="List databases/datasets or tables")
    p_analyze.add_argument("--database", help="If provided, list tables in this database/dataset")
    p_analyze.set_defaults(func=cmd_analyze)

    # --- seed ---
    p_seed = sub.add_parser("seed", help="Insert fake data into existing table(s)")
    p_seed.add_argument("database", help="Target database/dataset")
    p_seed.add_argument("table", nargs="?", default=None, help="Table to seed (all if omitted)")
    p_seed.add_argument("--rows", type=int, default=100, help="Number of rows (100)")
    p_seed.add_argument("--output", "-o", help="Write report to file")
    p_seed.set_defaults(func=cmd_seed)

    # --- read ---
    p_read = sub.add_parser("read", help="Read rows from a table")
    p_read.add_argument("database", help="Target database/dataset")
    p_read.add_argument("table", help="Table to read")
    p_read.add_argument("--limit", type=int, default=20, help="Max rows (20)")
    p_read.set_defaults(func=cmd_read)

    # --- create-schema ---
    p_create = sub.add_parser("create-schema", help="Create test tables with all column types")
    p_create.add_argument("database", help="Target database/dataset")
    p_create.set_defaults(func=cmd_create_schema)

    # --- drop-schema ---
    p_drop = sub.add_parser("drop-schema", help="Drop all test tables")
    p_drop.add_argument("database", help="Target database/dataset")
    p_drop.set_defaults(func=cmd_drop_schema)

    # --- seed-test ---
    p_seed_test = sub.add_parser(
        "seed-test",
        help="Seed test tables with referential integrity",
    )
    p_seed_test.add_argument("database", help="Target database/dataset")
    p_seed_test.add_argument("--output", "-o", help="Write report to file")
    p_seed_test.set_defaults(func=cmd_seed_test)

    args = parser.parse_args()
    _setup_logging(args.verbose)

    if not hasattr(args, "func"):
        parser.print_help()
        return

    try:
        args.func(args)
    except ConfigError as exc:
        error(f"Configuration error: {exc}")
        sys.exit(1)
    except TableError as exc:
        error(f"Table error: {exc}")
        sys.exit(1)
    except SynthDataError as exc:
        error(f"Error: {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        dim("\nInterrupted.")
        sys.exit(130)


if __name__ == "__main__":
    main()
