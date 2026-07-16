"""synth-data: synthetic data generator for Teradata and BigQuery."""

from __future__ import annotations

import logging
import traceback
from dataclasses import dataclass
from io import StringIO
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table as RichTable

from schemas.schema_loader import load as load_schema
from src.adapters.output.console import (
    column_list,
    data_table,
    database_list,
    database_summary,
    dataset_list,
    dim,
    error,
    heading,
    seed_result_table,
    success,
    table_list,
)
from src.domain.fk import discover_fk_map, resolve_fk_overrides, validate_fk_map
from src.domain.ports import Database
from src.infrastructure.config import ConfigError, get_db
from src.infrastructure.logging import setup_file_log

console = Console()
logger = logging.getLogger(__name__)
app = typer.Typer()

ResultRow = tuple[str, int, str]


class SynthDataError(Exception): ...


@dataclass
class CliContext:
    engine: str
    project: str | None
    host: str | None
    user: str | None
    default_database: str | None

    def require_database(self, database: str | None) -> str:
        db = database or self.default_database
        if not db:
            raise typer.BadParameter("Missing argument 'DATABASE' or set DATABASE env var.")
        return db

    def get_db(self) -> Database:
        return get_db(self.engine, self.project, self.host, self.user)

    def kind_key(self) -> str:
        return "table_type" if self.engine == "bigquery" else "table_kind"

    def table_type(self) -> str:
        return "TABLE" if self.engine == "bigquery" else "T"


def _resolve_databases(db: Database, database: str) -> list[str]:
    if database == "all":
        return db.list_databases()
    return [database]


def _format_column(col: Any, engine: str) -> str:
    if engine == "bigquery":
        suffix = " [REPEATED]" if len(col) > 2 and col[2] else ""
        return f"{col[0]} ({col[1]}{suffix})"
    return f"{col[0]} ({col[1]})"


def _build_seed_report(db: Database, database: str, results: list[ResultRow], engine: str) -> str:
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


def _write_report(
    output: str | None, db: Database, database: str, results: list[ResultRow], engine: str
) -> None:
    if not output:
        return
    with open(output, "w") as f:
        f.write(_build_seed_report(db, database, results, engine))
    dim(f"\nReport written to {output}")


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
        force=True,
    )


def _run_on_databases(
    c: CliContext,
    database: str | None,
    operation: str,
    heading_template: str,
    *,
    schema_id: str | None = None,
) -> None:
    database = c.require_database(database)
    with c.get_db() as db:
        for db_name in _resolve_databases(db, database):
            setup_file_log(operation, c.engine, db_name)
            heading(heading_template.format(db_name))
            args = [db_name, load_schema(schema_id)] if schema_id else [db_name]
            result = getattr(db, operation)(*args)
            success(f"{operation} {len(result)} tables in {db_name}")


@app.callback()
def cli(
    ctx: typer.Context,
    engine: str = typer.Option(..., "--engine", "-e", help="bigquery | teradata"),
    project: str = typer.Option(
        None, "--project", envvar="GOOGLE_CLOUD_PROJECT", help="BigQuery project ID"
    ),
    host: str = typer.Option(None, "--host", envvar="TERADATA_HOST", help="Teradata host"),
    user: str = typer.Option(None, "--user", envvar="TERADATA_USER", help="Teradata user"),
    database: str = typer.Option(
        None, "--database", "-d", envvar="DATABASE", help="Default database/dataset"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
) -> None:
    if engine not in ("bigquery", "teradata"):
        raise typer.BadParameter("engine must be 'bigquery' or 'teradata'")
    ctx.obj = CliContext(
        engine=engine, project=project, host=host, user=user, default_database=database
    )
    _setup_logging(verbose)


@app.command()
def analyse(
    ctx: typer.Context, database: str = typer.Argument(None, help="Database/dataset or 'all'")
) -> None:
    c: CliContext = ctx.obj
    database = database or c.default_database
    with c.get_db() as db:
        setup_file_log("analyse", c.engine, database or "all")
        if not database:
            datasets = db.list_databases()
            (dataset_list if c.engine == "bigquery" else database_list)(datasets)
        else:
            for db_name in _resolve_databases(db, database):
                tables = db.list_tables(db_name)
                table_list(db_name, tables, kind_key=c.kind_key())


@app.command(name="analyse-all")
def analyse_all(ctx: typer.Context) -> None:
    c: CliContext = ctx.obj
    with c.get_db() as db:
        kind_key = c.kind_key()
        info: list[tuple[str, int, int]] = []
        for db_name in db.list_databases():
            tables = db.list_tables(db_name)
            seedable = sum(1 for t in tables if t.get(kind_key) == c.table_type())
            info.append((db_name, len(tables), seedable))
        database_summary(info)


@app.command()
def seed(
    ctx: typer.Context,
    database: str = typer.Argument(None, help="Database/dataset or 'all'"),
    table: str = typer.Option(None, "--table", "-t", help="Table name (omit to seed all)"),
    rows: int = typer.Option(100, "--rows", help="Number of rows per table"),
    output: str = typer.Option(None, "--output", "-o", help="Write report to file"),
) -> None:
    c: CliContext = ctx.obj
    database = c.require_database(database)
    with c.get_db() as db:
        all_results: list[ResultRow] = []
        for db_name in _resolve_databases(db, database):
            if table:
                setup_file_log("seed", c.engine, db_name)
                columns = db.get_columns(db_name, table)
                if not columns:
                    all_results.append((f"{db_name}.{table}", 0, "no columns found"))
                    continue
                fk_map = validate_fk_map(db, db_name, discover_fk_map(db, db_name, [table]))
                parent_cache: dict[tuple[str, str], list[Any]] = {}
                fk_overrides = resolve_fk_overrides(db, db_name, table, fk_map, parent_cache)
                if fk_overrides is None:
                    all_results.append((f"{db_name}.{table}", 0, "skipped (parent empty)"))
                    continue
                column_list(db_name, table, columns, engine=c.engine)
                inserted = db.insert_fake_rows(
                    db_name, table, columns, num_rows=rows, fk_overrides=fk_overrides
                )
                all_results.append((f"{db_name}.{table}", inserted, "ok"))
            else:
                setup_file_log("seed-all", c.engine, db_name)
                heading(f"Seeding all tables in {db_name}...")
                all_results.extend(db.seed_all(db_name, num_rows=rows))
        seed_result_table(all_results)
        _write_report(output, db, database, all_results, c.engine)


@app.command()
def read(
    ctx: typer.Context,
    database: str = typer.Argument(None, help="Database/dataset"),
    table: str = typer.Argument(..., help="Table name"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max rows"),
) -> None:
    c: CliContext = ctx.obj
    database = c.require_database(database)
    with c.get_db() as db:
        setup_file_log("read", c.engine, database)
        col_names = db.get_column_names(database, table)
        rows = db.read_table(database, table, limit=limit)
        data_table(col_names, rows)
        dim(f"({len(rows)} rows)")


@app.command(name="create-schema")
def create_schema(
    ctx: typer.Context,
    database: str = typer.Argument(None, help="Database/dataset or 'all'"),
    schema_id: str = typer.Option("1", "--schema", help="Schema definition: 1 or 2"),
) -> None:
    _run_on_databases(
        ctx.obj, database, "create_schema", "Creating test tables in {}", schema_id=schema_id
    )


@app.command(name="drop-schema")
def drop_schema(
    ctx: typer.Context,
    database: str = typer.Argument(None, help="Database/dataset or 'all'"),
    schema_id: str = typer.Option("1", "--schema", help="Schema definition: 1 or 2"),
) -> None:
    _run_on_databases(
        ctx.obj, database, "drop_schema", "Dropping test tables in {}", schema_id=schema_id
    )


@app.command(name="purge-data")
def purge_data(
    ctx: typer.Context, database: str = typer.Argument(None, help="Database/dataset or 'all'")
) -> None:
    _run_on_databases(ctx.obj, database, "purge_data", "Purging all data in {}")


@app.command(name="seed-test")
def seed_test(
    ctx: typer.Context,
    database: str = typer.Argument(None, help="Database/dataset or 'all'"),
    schema_id: str = typer.Option("1", "--schema", help="Schema definition: 1 or 2"),
    output: str = typer.Option(None, "--output", "-o", help="Write report to file"),
) -> None:
    c: CliContext = ctx.obj
    database = c.require_database(database)
    schema = load_schema(schema_id)
    with c.get_db() as db:
        all_results: list[ResultRow] = []
        for db_name in _resolve_databases(db, database):
            setup_file_log("seed-test", c.engine, db_name)
            heading(f"Seeding test tables in {db_name} with referential integrity")
            results = db.seed_with_relations(db_name, schema.SEED_ORDER, schema.FK_MAP)
            seed_result_table(results)
            all_results.extend(results)
        _write_report(output, db, database, all_results, c.engine)


@app.command()
def verify(
    ctx: typer.Context,
    database: str = typer.Argument(None, help="Database/dataset"),
    schema_id: str = typer.Option("1", "--schema", help="Schema definition: 1 or 2"),
) -> None:
    c: CliContext = ctx.obj
    database = c.require_database(database)
    schema = load_schema(schema_id)
    with c.get_db() as db:
        for db_name in _resolve_databases(db, database):
            setup_file_log("verify", c.engine, db_name)
            heading(f"Verifying FK integrity in {db_name}")
            tables = [
                t["table_name"]
                for t in db.list_tables(db_name)
                if t.get(c.kind_key()) == c.table_type()
            ]
            fk_map = validate_fk_map(db, db_name, discover_fk_map(db, db_name, tables)) or {
                k: v for k, v in schema.FK_MAP.items() if k in set(tables)
            }
            if not fk_map:
                console.print(Panel("[dim]No foreign key relationships found.[/dim]"))
                continue
            t = RichTable(
                title=f"FK Integrity \u2014 {db_name}",
                show_header=True,
                header_style="bold",
                show_lines=False,
                padding=(0, 2),
            )
            t.add_column("Status", justify="center", width=6)
            t.add_column("Child", style="bold")
            t.add_column("Parent", style="dim")
            t.add_column("Detail")
            violations = 0
            checked = 0
            for child, fks in fk_map.items():
                for child_col, (parent_table, parent_col) in fks.items():
                    checked += 1
                    child_vals = set(db.read_column_values(db_name, child, child_col))
                    parent_vals = set(db.read_column_values(db_name, parent_table, parent_col))
                    orphans = child_vals - parent_vals
                    fk_str = f"{child}.{child_col}"
                    ref_str = f"{parent_table}.{parent_col}"
                    if orphans:
                        sample = list(orphans)[:5]
                        t.add_row(
                            "[red]FAIL[/red]",
                            fk_str,
                            ref_str,
                            f"{len(orphans)} orphan(s) (e.g. {sample})",
                        )
                        violations += 1
                    else:
                        t.add_row(
                            "[green]OK[/green]",
                            fk_str,
                            ref_str,
                            f"{len(child_vals)} values, all valid",
                        )
            console.print(Panel(t, border_style="green" if not violations else "red"))
            (error if violations else success)(
                f"{checked}/{checked} FK constraints checked in {db_name}"
            )


def main() -> None:
    try:
        app()
    except typer.Exit:
        raise
    except (ConfigError, SynthDataError) as exc:
        console.print(Panel(f"[bold red]{type(exc).__name__}:[/bold red]\n{exc}", title="Error"))
        raise SystemExit(1) from exc
    except Exception:
        console.print(
            Panel(
                f"[bold red]Unexpected error:[/bold red]\n{traceback.format_exc()}", title="Error"
            )
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
