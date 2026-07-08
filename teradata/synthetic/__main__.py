import argparse
import sys

from .generator import generate


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic data from Teradata data dictionary")
    parser.add_argument("--env", default="dev", help="Environment (default: dev)")
    parser.add_argument("--databases", nargs="*", help="Filter to specific databases")
    parser.add_argument("--max-tables", type=int, default=50, help="Max tables (default: 50)")
    parser.add_argument("--rows", type=int, default=100, help="Rows per table (default: 100)")
    parser.add_argument("--output", help="Output DuckDB file path")
    parser.add_argument("--kinds", nargs="*", help="Filter by table kinds (e.g., Table View)")
    args = parser.parse_args()

    output_path = generate(
        environment=args.env,
        databases=args.databases,
        max_tables=args.max_tables,
        rows_per_table=args.rows,
        output_path=args.output,
        table_kinds=args.kinds,
    )
    print(f"\nTo query: duckdb {output_path}")


if __name__ == "__main__":
    main()
