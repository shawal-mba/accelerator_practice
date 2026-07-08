from __future__ import annotations

import argparse
import os
import sys
from io import StringIO

from teraremote.analyze import get_column_names, list_databases, list_tables, read_table
from teraremote.connection import get_connection
from teraremote.format import (
    column_list,
    created,
    data_table,
    database_list,
    dim,
    dropped,
    heading,
    seed_result,
    success,
    table_list,
)
from teraremote.seed import get_columns, insert_fake_rows, seed_all, seed_with_relations
from teraremote.test_schema import FK_MAP, SEED_ORDER, create_tables, drop_tables


def _get_creds(args: argparse.Namespace) -> tuple[str, str, str]:
    host = args.host or os.environ.get("TERADATA_HOST", "")
    user = args.user or os.environ.get("TERADATA_USER", "")
    password = args.password or os.environ.get("TERADATA_PASSWORD", "")
    if not all([host, user, password]):
        sys.exit(
            "Error: host, user, and password are required. "
            "Pass as arguments or set TERADATA_HOST / TERADATA_USER / TERADATA_PASSWORD."
        )
    return host, user, password


def cmd_analyze(args: argparse.Namespace) -> None:
    host, user, password = _get_creds(args)
    conn = get_connection(host, user, password)
    try:
        databases = list_databases(conn)
        if args.database:
            tables = list_tables(conn, args.database)
            table_list(args.database, tables)
        else:
            database_list(databases)
    finally:
        conn.close()


def _build_seed_report(conn, database: str, results: list[tuple[str, int, str]]) -> str:
    buf = StringIO()
    total_inserted = 0
    for name, inserted, status in results:
        buf.write(f"=== {database}.{name} ===\n")
        if status == "ok":
            cols = get_columns(conn, database, name)
            col_str = ", ".join(f"{c[0]} ({c[1]})" for c in cols)
            buf.write(f"Columns: {col_str}\n")
            buf.write(f"Inserted {inserted} rows\n\n")
            total_inserted += inserted
        else:
            buf.write(f"Status: {status}\n\n")
    buf.write(f"Summary: {len(results)} tables processed, {total_inserted} total rows\n")
    return buf.getvalue()


def cmd_seed(args: argparse.Namespace) -> None:
    host, user, password = _get_creds(args)
    conn = get_connection(host, user, password)
    try:
        if args.table:
            columns = get_columns(conn, args.database, args.table)
            if not columns:
                sys.exit(f"Error: table {args.database}.{args.table} not found or has no columns.")

            column_list(args.database, args.table, columns)

            inserted = insert_fake_rows(
                conn, args.database, args.table, columns, num_rows=args.rows
            )
            success(f"\nInserted {inserted} rows into {args.database}.{args.table}")

            if args.output:
                report = _build_seed_report(
                    conn,
                    args.database,
                    [(args.table, inserted, "ok")],
                )
                with open(args.output, "w") as f:
                    f.write(report)
                dim(f"Report written to {args.output}")
        else:
            heading(f"Seeding all tables in {args.database}...")
            results = seed_all(conn, args.database, num_rows=args.rows)
            for name, inserted, status in results:
                seed_result(name, inserted, status)

            report = _build_seed_report(conn, args.database, results)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(report)
                dim(f"\nReport written to {args.output}")
            else:
                print(report)
    finally:
        conn.close()


def cmd_read(args: argparse.Namespace) -> None:
    host, user, password = _get_creds(args)
    conn = get_connection(host, user, password)
    try:
        col_names = get_column_names(conn, args.database, args.table)
        rows = read_table(conn, args.database, args.table, limit=args.limit)
        data_table(col_names, rows)
        dim(f"({len(rows)} rows)")
    finally:
        conn.close()


def cmd_create_schema(args: argparse.Namespace) -> None:
    host, user, password = _get_creds(args)
    conn = get_connection(host, user, password)
    try:
        heading(f"Creating test tables in {args.database}")
        created_tables = create_tables(args.database, conn)
        created(len(created_tables))
    finally:
        conn.close()


def cmd_drop_schema(args: argparse.Namespace) -> None:
    host, user, password = _get_creds(args)
    conn = get_connection(host, user, password)
    try:
        heading(f"Dropping test tables in {args.database}")
        dropped_tables = drop_tables(args.database, conn)
        dropped(len(dropped_tables))
    finally:
        conn.close()


def cmd_seed_test(args: argparse.Namespace) -> None:
    host, user, password = _get_creds(args)
    conn = get_connection(host, user, password)
    try:
        heading(f"Seeding test tables in {args.database} with referential integrity")
        results = seed_with_relations(conn, args.database, SEED_ORDER, FK_MAP)
        for name, inserted, status in results:
            seed_result(name, inserted, status)

        report = _build_seed_report(conn, args.database, results)
        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            dim(f"\nReport written to {args.output}")
        else:
            print(report)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="teraremote",
        description="Connect to Teradata GCP, analyse DBs, and generate test data.",
    )
    parser.add_argument("--host", help="Teradata host (or env TERADATA_HOST)")
    parser.add_argument("--user", help="Teradata user (or env TERADATA_USER)")
    parser.add_argument("--password", help="Teradata password (or env TERADATA_PASSWORD)")

    sub = parser.add_subparsers(dest="command")

    # --- analyze ---
    p_analyze = sub.add_parser("analyze", help="List databases or tables")
    p_analyze.add_argument("--database", help="If provided, list tables in this database")

    # --- seed ---
    p_seed = sub.add_parser("seed", help="Insert fake data into existing table(s)")
    p_seed.add_argument("database", help="Target database")
    p_seed.add_argument("table", nargs="?", default=None, help="Table to seed (all if omitted)")
    p_seed.add_argument("--rows", type=int, default=100, help="Number of rows (100)")
    p_seed.add_argument("--output", "-o", help="Write report to file")

    # --- read ---
    p_read = sub.add_parser("read", help="Read rows from a table")
    p_read.add_argument("database", help="Target database")
    p_read.add_argument("table", help="Table to read")
    p_read.add_argument("--limit", type=int, default=20, help="Max rows (20)")

    # --- create-schema ---
    p_create = sub.add_parser("create-schema", help="Create test tables with all column types")
    p_create.add_argument("database", help="Target database")

    # --- drop-schema ---
    p_drop = sub.add_parser("drop-schema", help="Drop all test tables")
    p_drop.add_argument("database", help="Target database")

    # --- seed-test ---
    p_seed_test = sub.add_parser(
        "seed-test",
        help="Seed test tables with referential integrity",
    )
    p_seed_test.add_argument("database", help="Target database")
    p_seed_test.add_argument("--output", "-o", help="Write report to file")

    args = parser.parse_args()
    if args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "seed":
        cmd_seed(args)
    elif args.command == "read":
        cmd_read(args)
    elif args.command == "create-schema":
        cmd_create_schema(args)
    elif args.command == "drop-schema":
        cmd_drop_schema(args)
    elif args.command == "seed-test":
        cmd_seed_test(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
