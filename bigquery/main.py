from __future__ import annotations

import argparse
import os
import sys
from io import StringIO

from bigquery.analyze import get_column_names, list_datasets, list_tables, read_table
from bigquery.connection import get_client
from bigquery.seed import get_columns, insert_fake_rows, seed_all, seed_with_relations
from bigquery.test_schema import FK_MAP, SEED_ORDER, create_tables, drop_tables


def _get_project(args: argparse.Namespace) -> str:
    project = args.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    if not project:
        sys.exit("Error: project is required. Pass --project or set GOOGLE_CLOUD_PROJECT.")
    return project


def cmd_analyze(args: argparse.Namespace) -> None:
    project = _get_project(args)
    client = get_client(project)
    try:
        datasets = list_datasets(client)
        if args.dataset:
            tables = list_tables(client, args.dataset)
            print(f"Tables in {args.dataset}:")
            for t in tables:
                print(f"  {t['table_name']}  ({t['table_type']})")
            print(f"\nTotal: {len(tables)}")
        else:
            print(f"Datasets ({len(datasets)}):")
            for ds in datasets:
                print(f"  {ds}")
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
                sys.exit(f"Error: table {args.dataset}.{args.table} not found or has no columns.")

            print(f"Columns detected in {args.dataset}.{args.table}:")
            for col_name, bq_type, is_repeated in columns:
                rep = " [REPEATED]" if is_repeated else ""
                print(f"  {col_name} ({bq_type}{rep})")

            inserted = insert_fake_rows(
                client, args.dataset, args.table, columns, num_rows=args.rows
            )
            print(f"\nInserted {inserted} rows into {args.dataset}.{args.table}")

            if args.output:
                report = _build_seed_report(
                    client,
                    args.dataset,
                    [(args.table, inserted, "ok")],
                )
                with open(args.output, "w") as f:
                    f.write(report)
                print(f"Report written to {args.output}")
        else:
            print(f"Seeding all tables in {args.dataset}...")
            results = seed_all(client, args.dataset, num_rows=args.rows)
            for name, inserted, status in results:
                if status == "ok":
                    print(f"  {name}: {inserted} rows")
                else:
                    print(f"  {name}: {status}")

            report = _build_seed_report(client, args.dataset, results)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(report)
                print(f"\nReport written to {args.output}")
            else:
                print(f"\n{report}")
    finally:
        client.close()


def cmd_read(args: argparse.Namespace) -> None:
    project = _get_project(args)
    client = get_client(project)
    try:
        col_names = get_column_names(client, args.dataset, args.table)
        rows = read_table(client, args.dataset, args.table, limit=args.limit)

        widths = [len(n) for n in col_names]
        str_rows = []
        for row in rows:
            cells = [str(v) for v in row]
            for i, cell in enumerate(cells):
                widths[i] = max(widths[i], len(cell))
            str_rows.append(cells)

        header = "  ".join(n.ljust(widths[i]) for i, n in enumerate(col_names))
        sep = "  ".join("-" * w for w in widths)

        print(header)
        print(sep)
        for cells in str_rows:
            print("  ".join(cells[i].ljust(widths[i]) for i in range(len(col_names))))
        print(f"\n({len(rows)} rows)")
    finally:
        client.close()


def cmd_create_schema(args: argparse.Namespace) -> None:
    project = _get_project(args)
    print(f"Creating test tables in {project}.{args.dataset}:")
    created = create_tables(project, args.dataset)
    print(f"\nCreated {len(created)} tables")


def cmd_drop_schema(args: argparse.Namespace) -> None:
    project = _get_project(args)
    print(f"Dropping test tables in {project}.{args.dataset}:")
    dropped = drop_tables(project, args.dataset)
    print(f"\nDropped {len(dropped)} tables")


def cmd_seed_test(args: argparse.Namespace) -> None:
    project = _get_project(args)
    client = get_client(project)
    try:
        print(f"Seeding test tables in {project}.{args.dataset} with referential integrity...")
        results = seed_with_relations(client, args.dataset, SEED_ORDER, FK_MAP)
        for name, inserted, status in results:
            if status == "ok":
                print(f"  {name}: {inserted} rows")
            else:
                print(f"  {name}: {status}")

        report = _build_seed_report(client, args.dataset, results)
        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"\nReport written to {args.output}")
        else:
            print(f"\n{report}")
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bigquery",
        description="Connect to Google BigQuery, analyse datasets, and generate test data.",
    )
    parser.add_argument("--project", help="GCP project (or env GOOGLE_CLOUD_PROJECT)")

    sub = parser.add_subparsers(dest="command")

    # --- analyze ---
    p_analyze = sub.add_parser("analyze", help="List datasets or tables")
    p_analyze.add_argument("--dataset", help="If provided, list tables in this dataset")

    # --- seed ---
    p_seed = sub.add_parser("seed", help="Insert fake data into existing table(s)")
    p_seed.add_argument("dataset", help="Target dataset")
    p_seed.add_argument("table", nargs="?", default=None, help="Table to seed (all if omitted)")
    p_seed.add_argument("--rows", type=int, default=100, help="Number of rows (100)")
    p_seed.add_argument("--output", "-o", help="Write report to file")

    # --- read ---
    p_read = sub.add_parser("read", help="Read rows from a table")
    p_read.add_argument("dataset", help="Target dataset")
    p_read.add_argument("table", help="Table to read")
    p_read.add_argument("--limit", type=int, default=20, help="Max rows (20)")

    # --- create-schema ---
    p_create = sub.add_parser("create-schema", help="Create test tables with all column types")
    p_create.add_argument("dataset", help="Target dataset")

    # --- drop-schema ---
    p_drop = sub.add_parser("drop-schema", help="Drop all test tables")
    p_drop.add_argument("dataset", help="Target dataset")

    # --- seed-test ---
    p_seed_test = sub.add_parser(
        "seed-test",
        help="Seed test tables with referential integrity",
    )
    p_seed_test.add_argument("dataset", help="Target dataset")
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
