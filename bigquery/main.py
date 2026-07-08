from __future__ import annotations

import argparse
import logging
import os
import sys
from io import StringIO

from bigquery.analyze import get_column_names, list_datasets, list_tables, read_table
from bigquery.connection import get_client
from bigquery.format import (
    column_list,
    created,
    data_table,
    dataset_list,
    dim,
    dropped,
    error,
    heading,
    seed_result_table,
    success,
    table_list,
)
from bigquery.seed import get_columns, insert_fake_rows, seed_all, seed_with_relations
from bigquery.test_schema import FK_MAP, SEED_ORDER, create_tables, drop_tables

logger = logging.getLogger(__name__)


class BigQueryError(Exception):
    """Base exception for bigquery CLI."""


class ConfigError(BigQueryError):
    """Configuration or credential errors."""


class TableError(BigQueryError):
    """Table not found or inaccessible."""


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        force=True,
    )


def _get_project(args: argparse.Namespace) -> str:
    project = args.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    if not project:
        raise ConfigError("project is required. Pass --project or set GOOGLE_CLOUD_PROJECT.")
    return project


def cmd_analyze(args: argparse.Namespace) -> None:
    project = _get_project(args)
    client = get_client(project)
    try:
        datasets = list_datasets(client)
        if args.dataset:
            tables = list_tables(client, args.dataset)
            table_list(args.dataset, tables)
        else:
            dataset_list(datasets)
    finally:
        client.close()


def _build_seed_report(client, dataset: str, results: list[tuple[str, int, str]]) -> str:
    buf = StringIO()
    total_inserted = 0
    for name, inserted, status in results:
        buf.write(f"=== {dataset}.{name} ===\n")
        if status == "ok":
            cols = get_columns(client, dataset, name)
            col_str = ", ".join(f"{c[0]} ({c[1]}{' [REPEATED]' if c[2] else ''})" for c in cols)
            buf.write(f"Columns: {col_str}\n")
            buf.write(f"Inserted {inserted} rows\n\n")
            total_inserted += inserted
        else:
            buf.write(f"Status: {status}\n\n")
    buf.write(f"Summary: {len(results)} tables processed, {total_inserted} total rows\n")
    return buf.getvalue()


def cmd_seed(args: argparse.Namespace) -> None:
    project = _get_project(args)
    client = get_client(project)
    try:
        if args.table:
            columns = get_columns(client, args.dataset, args.table)
            if not columns:
                raise TableError(f"{args.dataset}.{args.table} not found or has no columns.")

            column_list(args.dataset, args.table, columns)

            inserted = insert_fake_rows(
                client, args.dataset, args.table, columns, num_rows=args.rows
            )
            success(f"\nInserted {inserted} rows into {args.dataset}.{args.table}")

            if args.output:
                report = _build_seed_report(
                    client,
                    args.dataset,
                    [(args.table, inserted, "ok")],
                )
                with open(args.output, "w") as f:
                    f.write(report)
                dim(f"Report written to {args.output}")
        else:
            heading(f"Seeding all tables in {args.dataset}...")
            results = seed_all(client, args.dataset, num_rows=args.rows)
            seed_result_table(results)

            report = _build_seed_report(client, args.dataset, results)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(report)
                dim(f"\nReport written to {args.output}")
    finally:
        client.close()


def cmd_read(args: argparse.Namespace) -> None:
    project = _get_project(args)
    client = get_client(project)
    try:
        col_names = get_column_names(client, args.dataset, args.table)
        rows = read_table(client, args.dataset, args.table, limit=args.limit)
        data_table(col_names, rows)
        dim(f"({len(rows)} rows)")
    finally:
        client.close()


def cmd_create_schema(args: argparse.Namespace) -> None:
    project = _get_project(args)
    heading(f"Creating test tables in {project}.{args.dataset}")
    created_tables = create_tables(project, args.dataset)
    created(len(created_tables))


def cmd_drop_schema(args: argparse.Namespace) -> None:
    project = _get_project(args)
    heading(f"Dropping test tables in {project}.{args.dataset}")
    dropped_tables = drop_tables(project, args.dataset)
    dropped(len(dropped_tables))


def cmd_seed_test(args: argparse.Namespace) -> None:
    project = _get_project(args)
    client = get_client(project)
    try:
        heading(f"Seeding test tables in {project}.{args.dataset} with referential integrity")
        results = seed_with_relations(client, args.dataset, SEED_ORDER, FK_MAP)
        seed_result_table(results)

        report = _build_seed_report(client, args.dataset, results)
        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            dim(f"\nReport written to {args.output}")
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bigquery",
        description="Connect to Google BigQuery, analyse datasets, and generate test data.",
    )
    parser.add_argument("--project", help="GCP project (or env GOOGLE_CLOUD_PROJECT)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

    sub = parser.add_subparsers(dest="command")

    # --- analyze ---
    p_analyze = sub.add_parser("analyze", help="List datasets or tables")
    p_analyze.add_argument("--dataset", help="If provided, list tables in this dataset")
    p_analyze.set_defaults(func=cmd_analyze)

    # --- seed ---
    p_seed = sub.add_parser("seed", help="Insert fake data into existing table(s)")
    p_seed.add_argument("dataset", help="Target dataset")
    p_seed.add_argument("table", nargs="?", default=None, help="Table to seed (all if omitted)")
    p_seed.add_argument("--rows", type=int, default=100, help="Number of rows (100)")
    p_seed.add_argument("--output", "-o", help="Write report to file")
    p_seed.set_defaults(func=cmd_seed)

    # --- read ---
    p_read = sub.add_parser("read", help="Read rows from a table")
    p_read.add_argument("dataset", help="Target dataset")
    p_read.add_argument("table", help="Table to read")
    p_read.add_argument("--limit", type=int, default=20, help="Max rows (20)")
    p_read.set_defaults(func=cmd_read)

    # --- create-schema ---
    p_create = sub.add_parser("create-schema", help="Create test tables with all column types")
    p_create.add_argument("dataset", help="Target dataset")
    p_create.set_defaults(func=cmd_create_schema)

    # --- drop-schema ---
    p_drop = sub.add_parser("drop-schema", help="Drop all test tables")
    p_drop.add_argument("dataset", help="Target dataset")
    p_drop.set_defaults(func=cmd_drop_schema)

    # --- seed-test ---
    p_seed_test = sub.add_parser(
        "seed-test",
        help="Seed test tables with referential integrity",
    )
    p_seed_test.add_argument("dataset", help="Target dataset")
    p_seed_test.add_argument("--output", "-o", help="Write report to file")
    p_seed_test.set_defaults(func=cmd_seed_test)

    args = parser.parse_args()
    _setup_logging(args.verbose)

    if hasattr(args, "func"):
        try:
            args.func(args)
        except ConfigError as exc:
            error(f"Configuration error: {exc}")
            sys.exit(1)
        except TableError as exc:
            error(f"Table error: {exc}")
            sys.exit(1)
        except BigQueryError as exc:
            error(f"Error: {exc}")
            sys.exit(1)
        except KeyboardInterrupt:
            dim("\nInterrupted.")
            sys.exit(130)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
