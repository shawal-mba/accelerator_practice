"""Rich console output for CLI results."""

from __future__ import annotations

from collections.abc import Sequence

from rich.console import Console
from rich.table import Table

console = Console()

_HEADING = "bold cyan"
_SUCCESS = "bold green"
_ERROR = "bold red"
_TABLE_NAME = "bold"
_DIM = "dim"


# ── Simple messages ──────────────────────────────────────────────────────────


def heading(text: str) -> None:
    console.print(f"\n[bold]{text}[/bold]", style=_HEADING)


def success(text: str) -> None:
    console.print(text, style=_SUCCESS)


def error(text: str) -> None:
    console.print(text, style=_ERROR)


def dim(text: str) -> None:
    console.print(text, style=_DIM)


def created(count: int) -> None:
    success(f"Created {count} tables")


def dropped(count: int) -> None:
    success(f"Dropped {count} tables")


# ── Tables ───────────────────────────────────────────────────────────────────


def _entity_list(title: str, label: str, items: list[str]) -> None:
    table = Table(
        title=f"{title} ({len(items)})",
        title_style=_HEADING,
        show_header=True,
        header_style=_HEADING,
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("#", style=_DIM, width=4)
    table.add_column(label, style=_TABLE_NAME)
    for i, item in enumerate(items, 1):
        table.add_row(str(i), item)
    console.print(table)


def database_list(databases: list[str]) -> None:
    _entity_list("Databases", "Database", databases)


def dataset_list(datasets: list[str]) -> None:
    _entity_list("Datasets", "Dataset", datasets)


def table_list(database: str, tables: list[dict[str, str]], kind_key: str = "table_type") -> None:
    kind_label = "Type" if kind_key == "table_type" else "Kind"
    table = Table(
        title=f"Tables in {database}",
        title_style=_HEADING,
        show_header=True,
        header_style=_HEADING,
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("#", style=_DIM, width=4)
    table.add_column("Table", style=_TABLE_NAME)
    table.add_column(kind_label, style=_DIM)
    for i, t in enumerate(tables, 1):
        table.add_row(str(i), t["table_name"], t.get(kind_key, ""))
    console.print(table)
    dim(f"Total: {len(tables)}")


def column_list(
    database: str,
    table: str,
    columns: Sequence[tuple],
    engine: str = "bigquery",
) -> None:
    t = Table(
        title=f"Columns in {database}.{table}",
        title_style=_HEADING,
        show_header=True,
        header_style=_HEADING,
        show_lines=False,
        padding=(0, 2),
    )
    t.add_column("#", style=_DIM, width=4)
    t.add_column("Column", style=_TABLE_NAME)
    t.add_column("Type", style=_DIM)
    if engine == "bigquery":
        t.add_column("Mode", style=_DIM)
        for i, (col_name, bq_type, is_repeated) in enumerate(columns, 1):
            mode = "REPEATED" if is_repeated else "NULLABLE"
            t.add_row(str(i), col_name, bq_type, mode)
    else:
        for i, (col_name, td_type) in enumerate(columns, 1):
            t.add_row(str(i), col_name, td_type)
    console.print(t)


def seed_result_table(results: list[tuple[str, int, str]]) -> None:
    table = Table(
        title="Seed Results",
        title_style=_HEADING,
        show_header=True,
        header_style=_HEADING,
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("Table", style=_TABLE_NAME)
    table.add_column("Rows", justify="right")
    table.add_column("Status")
    for name, inserted, status in results:
        if status == "ok":
            table.add_row(name, str(inserted), f"[green]{status}[/green]")
        else:
            table.add_row(name, "-", f"[red]{status}[/red]")
    console.print(table)


def data_table(col_names: list[str], rows: list[tuple], max_width: int = 40) -> None:
    table = Table(show_header=True, header_style=_HEADING, show_lines=False, padding=(0, 1))
    for name in col_names:
        table.add_column(name, overflow="fold", max_width=max_width)
    for row in rows:
        table.add_row(*(str(v) if v is not None else "[dim]NULL[/dim]" for v in row))
    console.print(table)
