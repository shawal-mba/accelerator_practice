"""synth-data: synthetic data generator for Teradata and BigQuery."""

from __future__ import annotations

import logging
import os
import traceback
from io import StringIO
from typing import Any

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from src.bigquery import BigQueryDB
from src.fk import discover_fk_map, resolve_fk_overrides, validate_fk_map
from src.format import (
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
)
from src.log import setup_file_log
from src.protocol import Database
from src.teradata import TeradataDB

load_dotenv()

console = Console()

logger = logging.getLogger(__name__)

app = typer.Typer()

SCHEMAS = {
    "1": "schemas.test_schema",
    "2": "schemas.test_schema_2",
}


def _load_schema(schema_id: str) -> Any:
    """Load a test schema module by ID ('1' or '2')."""
    import importlib

    module_path = SCHEMAS.get(schema_id)
    if not module_path:
        valid = ", ".join(SCHEMAS)
        raise typer.BadParameter(f"Unknown schema '{schema_id}'. Choose from: {valid}")
    return importlib.import_module(module_path)


# ── Exceptions ───────────────────────────────────────────────────────────────


class SynthDataError(Exception):
    """Base exception for synth-data CLI."""


class ConfigError(SynthDataError):
    """Configuration or credential errors."""


class TableError(SynthDataError):
    """Table not found or inaccessible."""


# ── Helpers ──────────────────────────────────────────────────────────────────


def _get_db(engine: str, project: str | None, host: str | None, user: str | None) -> Database:
    if engine == "bigquery":
        project = project or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        if not project:
            raise ConfigError(
                "project is required for BigQuery. Pass --project or set GOOGLE_CLOUD_PROJECT."
            )
        db: Database = BigQueryDB(project=project)
    elif engine == "teradata":
        host = host or os.environ.get("TERADATA_HOST", "")
        user = user or os.environ.get("TERADATA_USER", "")
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


def _resolve_databases(db: Database, database: str) -> list[str]:
    """Return the list of databases to operate on.

    If *database* is ``"all"``, every database in the connection is returned.
    Otherwise a single-element list is returned.
    """
    if database == "all":
        return db.list_databases()
    return [database]


def _format_column(col: Any, engine: str) -> str:
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


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        force=True,
    )


def _require_database(database: str | None, ctx: typer.Context) -> str:
    db = database or ctx.obj.get("default_database")
    if not db:
        raise typer.BadParameter("Missing argument 'DATABASE' or set DATABASE env var.")
    return db


# ── CLI ──────────────────────────────────────────────────────────────────────


@app.callback()
def cli(
    ctx: typer.Context,
    engine: str = typer.Option(..., "--engine", "-e", help="Engine: bigquery or teradata"),
    project: str = typer.Option(
        None, "--project", envvar="GOOGLE_CLOUD_PROJECT", help="BigQuery project ID"
    ),
    host: str = typer.Option(
        None, "--host", envvar="TERADATA_HOST", help="Teradata host"
    ),
    user: str = typer.Option(
        None, "--user", envvar="TERADATA_USER", help="Teradata user"
    ),
    database: str = typer.Option(
        None, "--database", "-d", envvar="DATABASE", help="Default database/dataset"
    ),
    schema_id: str = typer.Option(
        "1", "--schema", help="Test schema (1 or 2)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable debug logging"
    ),
) -> None:
    """synth-data: synthetic data generator for Teradata and BigQuery."""
    if engine not in ("bigquery", "teradata"):
        raise typer.BadParameter("engine must be 'bigquery' or 'teradata'")
    ctx.obj = {
        "engine": engine,
        "project": project,
        "host": host,
        "user": user,
        "default_database": database,
        "schema": _load_schema(schema_id),
    }
    _setup_logging(verbose)


@app.command()
def analyse(
    ctx: typer.Context,
    database: str = typer.Argument(
        None, help="Database/dataset (or 'all' for all databases)"
    ),
) -> None:
    """List databases/datasets or tables. Pass 'all' to list tables in every database."""
    db = _get_db(ctx.obj["engine"], ctx.obj["project"], ctx.obj["host"], ctx.obj["user"])
    engine = ctx.obj["engine"]
    database = database or ctx.obj.get("default_database")
    with db:
        log = setup_file_log("analyse", engine, database or "all")
        if not database:
            databases = db.list_databases()
            log.info("Listing databases: %d found", len(databases))
            if engine == "bigquery":
                dataset_list(databases)
            else:
                database_list(databases)
        elif database == "all":
            for db_name in db.list_databases():
                tables = db.list_tables(db_name)
                log.info("%s: %d tables", db_name, len(tables))
                kind_key = "table_type" if engine == "bigquery" else "table_kind"
                table_list(db_name, tables, kind_key=kind_key)
        else:
            tables = db.list_tables(database)
            log.info("%s: %d tables", database, len(tables))
            kind_key = "table_type" if engine == "bigquery" else "table_kind"
            table_list(database, tables, kind_key=kind_key)


@app.command()
def seed(
    ctx: typer.Context,
    database: str = typer.Argument(
        None, help="Database/dataset (or 'all' for all databases)"
    ),
    table: str = typer.Argument(
        None, help="Table name (omit to seed all tables)"
    ),
    rows: int = typer.Option(100, "--rows", help="Number of rows"),
    output: str = typer.Option(
        None, "--output", "-o", help="Write report to file"
    ),
) -> None:
    """Insert fake data into existing table(s). Pass 'all' as database to seed every database."""
    database = _require_database(database, ctx)
    db = _get_db(ctx.obj["engine"], ctx.obj["project"], ctx.obj["host"], ctx.obj["user"])
    engine = ctx.obj["engine"]
    with db:
        all_results: list[tuple[str, int, str]] = []
        for db_name in _resolve_databases(db, database):
            if table:
                log = setup_file_log("seed", engine, db_name)
                log.info("Seeding %s.%s (%d rows)", db_name, table, rows)

                columns = db.get_columns(db_name, table)
                if not columns:
                    console.print(f"[yellow]Skipping {db_name}.{table}: no columns found[/yellow]")
                    all_results.append((f"{db_name}.{table}", 0, "no columns found"))
                    continue

                fk_map = discover_fk_map(db, db_name, [table])
                fk_map = validate_fk_map(db, db_name, fk_map)
                log.info("FK map for %s: %s", table, fk_map)

                parent_cache: dict[tuple[str, str], list[Any]] = {}
                fk_overrides = resolve_fk_overrides(db, db_name, table, fk_map, parent_cache)
                if fk_overrides is None:
                    log.warning("Skipping %s: parent table has no rows", table)
                    console.print(
                        f"[yellow]Skipping {db_name}.{table}: parent table has no rows.[/yellow]"
                    )
                    all_results.append((f"{db_name}.{table}", 0, "skipped (parent empty)"))
                    continue
                if fk_overrides:
                    for col, vals in fk_overrides.items():
                        log.info("Resolved FK %s: %d parent values", col, len(vals))

                column_list(db_name, table, columns, engine=engine)

                inserted = db.insert_fake_rows(
                    db_name, table, columns, num_rows=rows, fk_overrides=fk_overrides
                )
                log.info("Inserted %d rows into %s.%s", inserted, db_name, table)
                success(f"\nInserted {inserted} rows into {db_name}.{table}")
                all_results.append((f"{db_name}.{table}", inserted, "ok"))
            else:
                log = setup_file_log("seed-all", engine, db_name)
                log.info("Seeding all tables in %s (%d rows each)", db_name, rows)

                heading(f"Seeding all tables in {db_name}...")

                results = db.seed_all(db_name, num_rows=rows)
                seed_result_table(results)

                for name, inserted, status in results:
                    log.info("%s: %s (%s)", name, inserted, status)
                all_results.extend(results)

        if output:
            report = _build_seed_report(db, database, all_results, engine)
            with open(output, "w") as f:
                f.write(report)
            dim(f"\nReport written to {output}")


@app.command()
def read(
    ctx: typer.Context,
    database: str = typer.Argument(
        None, help="Database/dataset"
    ),
    table: str = typer.Argument(..., help="Table name"),
    limit: int = typer.Option(20, "--limit", help="Max rows"),
) -> None:
    """Read rows from a table."""
    database = _require_database(database, ctx)
    db = _get_db(ctx.obj["engine"], ctx.obj["project"], ctx.obj["host"], ctx.obj["user"])
    engine = ctx.obj["engine"]
    with db:
        log = setup_file_log("read", engine, database)
        log.info("Reading %s.%s (limit %d)", database, table, limit)
        col_names = db.get_column_names(database, table)
        rows = db.read_table(database, table, limit=limit)
        log.info("Read %d rows from %s.%s", len(rows), database, table)
        data_table(col_names, rows)
        dim(f"({len(rows)} rows)")


@app.command(name="create-schema")
def create_schema(
    ctx: typer.Context,
    database: str = typer.Argument(
        None, help="Database/dataset (or 'all')"
    ),
) -> None:
    """Create test tables. Pass 'all' for every database."""
    database = _require_database(database, ctx)
    db = _get_db(ctx.obj["engine"], ctx.obj["project"], ctx.obj["host"], ctx.obj["user"])
    engine = ctx.obj["engine"]
    schema = ctx.obj["schema"]
    with db:
        for db_name in _resolve_databases(db, database):
            log = setup_file_log("create-schema", engine, db_name)
            log.info("Creating test tables in %s", db_name)
            heading(f"Creating test tables in {db_name}")
            created_tables = db.create_schema(db_name, schema)
            log.info("Created %d tables in %s", len(created_tables), db_name)
            created(len(created_tables))


@app.command(name="drop-schema")
def drop_schema(
    ctx: typer.Context,
    database: str = typer.Argument(
        None, help="Database/dataset (or 'all')"
    ),
) -> None:
    """Drop all test tables. Pass 'all' for every database."""
    database = _require_database(database, ctx)
    db = _get_db(ctx.obj["engine"], ctx.obj["project"], ctx.obj["host"], ctx.obj["user"])
    engine = ctx.obj["engine"]
    schema = ctx.obj["schema"]
    with db:
        for db_name in _resolve_databases(db, database):
            log = setup_file_log("drop-schema", engine, db_name)
            log.info("Dropping test tables in %s", db_name)
            heading(f"Dropping test tables in {db_name}")
            dropped_tables = db.drop_schema(db_name, schema)
            log.info("Dropped %d tables in %s", len(dropped_tables), db_name)
            dropped(len(dropped_tables))


@app.command(name="purge-data")
def purge_data(
    ctx: typer.Context,
    database: str = typer.Argument(
        None, help="Database/dataset (or 'all')"
    ),
) -> None:
    """Delete all rows from every table. Pass 'all' to purge every database."""
    database = _require_database(database, ctx)
    db = _get_db(ctx.obj["engine"], ctx.obj["project"], ctx.obj["host"], ctx.obj["user"])
    engine = ctx.obj["engine"]
    with db:
        for db_name in _resolve_databases(db, database):
            log = setup_file_log("purge", engine, db_name)
            log.info("Purging all data in %s", db_name)

            heading(f"Purging all data in {db_name}")
            purged = db.purge_data(db_name)
            success(f"Purged {len(purged)} tables in {db_name}")
            log.info("Purged %d tables: %s", len(purged), purged)


@app.command(name="seed-test")
def seed_test(
    ctx: typer.Context,
    database: str = typer.Argument(
        None, help="Database/dataset (or 'all')"
    ),
    output: str = typer.Option(
        None, "--output", "-o", help="Write report to file"
    ),
) -> None:
    """Seed test tables with referential integrity. Pass 'all' for every database."""
    database = _require_database(database, ctx)
    db = _get_db(ctx.obj["engine"], ctx.obj["project"], ctx.obj["host"], ctx.obj["user"])
    engine = ctx.obj["engine"]
    schema = ctx.obj["schema"]
    SEED_ORDER = schema.SEED_ORDER
    FK_MAP = schema.FK_MAP
    with db:
        all_results: list[tuple[str, int, str]] = []
        for db_name in _resolve_databases(db, database):
            log = setup_file_log("seed-test", engine, db_name)
            log.info("Seeding test tables in %s with referential integrity", db_name)
            log.info("Seed order: %s", [name for name, _ in SEED_ORDER])
            log.info("FK map: %s", FK_MAP)

            heading(f"Seeding test tables in {db_name} with referential integrity")
            results = db.seed_with_relations(db_name, SEED_ORDER, FK_MAP)
            seed_result_table(results)

            for name, inserted, status in results:
                log.info("%s: %s (%s)", name, inserted, status)
            all_results.extend(results)

        if output:
            report = _build_seed_report(db, database, all_results, engine)
            with open(output, "w") as f:
                f.write(report)
            dim(f"Report written to {output}")


@app.command()
def verify(
    ctx: typer.Context,
    database: str = typer.Argument(
        None, help="Database/dataset"
    ),
) -> None:
    """Check referential integrity of seeded data.

    Discovers all FK relationships and verifies that every child value
    exists in the parent table. Reports orphaned rows.
    """
    database = _require_database(database, ctx)
    db = _get_db(ctx.obj["engine"], ctx.obj["project"], ctx.obj["host"], ctx.obj["user"])
    engine = ctx.obj["engine"]
    schema = ctx.obj["schema"]
    with db:
        for db_name in _resolve_databases(db, database):
            log = setup_file_log("verify", engine, db_name)
            log.info("Verifying FK integrity in %s", db_name)
            heading(f"Verifying FK integrity in {db_name}")

            tables = [
                t["table_name"]
                for t in db.list_tables(db_name)
                if t.get("table_type" if engine == "bigquery" else "table_kind")
                == ("TABLE" if engine == "bigquery" else "T")
            ]
            fk_map = discover_fk_map(db, db_name, tables)
            fk_map = validate_fk_map(db, db_name, fk_map)

            if not fk_map:
                fk_map = {k: v for k, v in schema.FK_MAP.items() if k in set(tables)}

            if not fk_map:
                console.print(Panel("[dim]No foreign key relationships found.[/dim]"))
                log.info("No FK relationships found")
                continue

            from rich.table import Table as RichTable

            result_table = RichTable(
                title=f"FK Integrity \u2014 {db_name}",
                show_header=True,
                header_style="bold",
                show_lines=False,
                padding=(0, 2),
            )
            result_table.add_column("Status", justify="center", width=6)
            result_table.add_column("Child", style="bold")
            result_table.add_column("Parent", style="dim")
            result_table.add_column("Detail")

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
                        result_table.add_row(
                            "[red]FAIL[/red]",
                            fk_str,
                            ref_str,
                            f"{len(orphans)} orphan(s) (e.g. {sample})",
                        )
                        log.warning(
                            "FK violation: %s.%s -> %s.%s: %d orphans",
                            child,
                            child_col,
                            parent_table,
                            parent_col,
                            len(orphans),
                        )
                        violations += 1
                    else:
                        result_table.add_row(
                            "[green]OK[/green]",
                            fk_str,
                            ref_str,
                            f"{len(child_vals)} values, all valid",
                        )
                        log.info(
                            "FK ok: %s.%s -> %s.%s: %d values",
                            child,
                            child_col,
                            parent_table,
                            parent_col,
                            len(child_vals),
                        )

            console.print(Panel(result_table, border_style="green" if not violations else "red"))

            if violations:
                error(f"{violations}/{checked} FK constraint(s) violated in {db_name}")
                log.error("%d/%d FK constraints violated", violations, checked)
            else:
                success(f"{checked}/{checked} FK constraints valid in {db_name}")
                log.info("All %d FK constraints valid", checked)


def main() -> None:
    try:
        app()
    except typer.Exit:
        raise
    except (ConfigError, TableError, SynthDataError) as exc:
        console.print(
            Panel(f"[bold red]{type(exc).__name__}:[/bold red]\n{exc}", title="Error")
        )
        raise SystemExit(1) from exc
    except Exception:
        console.print(
            Panel(
                f"[bold red]Unexpected error:[/bold red]\n{traceback.format_exc()}",
                title="Error",
            )
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
