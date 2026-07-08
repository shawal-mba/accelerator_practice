from __future__ import annotations

import logging

from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)

console = Console()

STYLE_HEADING = "bold cyan"
STYLE_COUNT = "yellow"
STYLE_SUCCESS = "bold green"
STYLE_ERROR = "bold red"
STYLE_TABLE_NAME = "bold"
STYLE_DIM = "dim"
STYLE_HIGHLIGHT = "bold magenta"


def heading(text: str) -> None:
    console.print(f"\n[bold]{text}[/bold]", style=STYLE_HEADING)


def success(text: str) -> None:
    console.print(text, style=STYLE_SUCCESS)


def error(text: str) -> None:
    console.print(text, style=STYLE_ERROR)


def info(text: str) -> None:
    console.print(text)


def dim(text: str) -> None:
    console.print(text, style=STYLE_DIM)


def database_list(databases: list[str]) -> None:
    table = Table(
        title=f"Databases ({len(databases)})",
        title_style=STYLE_HEADING,
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("#", style=STYLE_DIM, width=4)
    table.add_column("Database", style=STYLE_TABLE_NAME)
    for i, db in enumerate(databases, 1):
        table.add_row(str(i), db)
    console.print(table)


def table_list(database: str, tables: list[dict[str, str]]) -> None:
    table = Table(
        title=f"Tables in {database}",
        title_style=STYLE_HEADING,
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("#", style=STYLE_DIM, width=4)
    table.add_column("Table", style=STYLE_TABLE_NAME)
    table.add_column("Kind", style=STYLE_DIM)
    for i, t in enumerate(tables, 1):
        table.add_row(str(i), t["table_name"], t["table_kind"])
    console.print(table)
    dim(f"Total: {len(tables)}")


def column_list(database: str, table: str, columns: list[tuple]) -> None:
    t = Table(
        title=f"Columns in {database}.{table}",
        title_style=STYLE_HEADING,
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
        padding=(0, 2),
    )
    t.add_column("#", style=STYLE_DIM, width=4)
    t.add_column("Column", style=STYLE_TABLE_NAME)
    t.add_column("Type", style=STYLE_DIM)
    for i, (col_name, td_type) in enumerate(columns, 1):
        t.add_row(str(i), col_name, td_type)
    console.print(t)


def seed_result_table(results: list[tuple[str, int, str]]) -> None:
    table = Table(
        title="Seed Results",
        title_style=STYLE_HEADING,
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("Table", style=STYLE_TABLE_NAME)
    table.add_column("Rows", justify="right")
    table.add_column("Status")
    for name, inserted, status in results:
        if status == "ok":
            table.add_row(name, str(inserted), f"[green]{status}[/green]")
        else:
            table.add_row(name, "-", f"[red]{status}[/red]")
    console.print(table)


def seed_result(name: str, inserted: int, status: str) -> None:
    if status == "ok":
        console.print(f"  {name}", style=STYLE_TABLE_NAME, end="")
        console.print(f": {inserted} rows", style=STYLE_SUCCESS)
    else:
        console.print(f"  {name}", style=STYLE_TABLE_NAME, end="")
        console.print(f": {status}", style=STYLE_ERROR)


def data_table(col_names: list[str], rows: list[tuple], max_width: int = 40) -> None:
    table = Table(show_header=True, header_style="bold cyan", show_lines=False, padding=(0, 1))
    for name in col_names:
        table.add_column(name, overflow="fold", max_width=max_width)
    for row in rows:
        table.add_row(*(str(v) if v is not None else "[dim]NULL[/dim]" for v in row))
    console.print(table)


def summary(total_tables: int, total_rows: int) -> None:
    console.print(
        f"\n[bold]Summary:[/bold] {total_tables} tables processed, {total_rows} total rows",
        style=STYLE_HIGHLIGHT,
    )


def created(count: int) -> None:
    success(f"Created {count} tables")


def dropped(count: int) -> None:
    success(f"Dropped {count} tables")
