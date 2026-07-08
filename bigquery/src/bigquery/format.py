from __future__ import annotations

from rich.console import Console
from rich.table import Table

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


def dataset_list(datasets: list[str]) -> None:
    heading(f"Datasets ({len(datasets)})")
    for ds in datasets:
        console.print(f"  {ds}", style=STYLE_TABLE_NAME)


def table_list(dataset: str, tables: list[dict[str, str]]) -> None:
    heading(f"Tables in {dataset}")
    for t in tables:
        name = t["table_name"]
        kind = t["table_type"]
        console.print(f"  {name}", style=STYLE_TABLE_NAME, end="")
        console.print(f"  ({kind})", style=STYLE_DIM)
    dim(f"\nTotal: {len(tables)}")


def column_list(dataset: str, table: str, columns: list[tuple]) -> None:
    heading(f"Columns in {dataset}.{table}")
    for col_name, bq_type, is_repeated in columns:
        rep = " [REPEATED]" if is_repeated else ""
        console.print(f"  {col_name}", style=STYLE_TABLE_NAME, end="")
        console.print(f" ({bq_type}{rep})", style=STYLE_DIM)


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


def seed_report_header(database: str, name: str) -> None:
    console.print(f"\n[bold]{database}.{name}[/bold]", style=STYLE_HEADING)


def summary(total_tables: int, total_rows: int) -> None:
    console.print(
        f"\n[bold]Summary:[/bold] {total_tables} tables processed, {total_rows} total rows",
        style=STYLE_HIGHLIGHT,
    )


def created(count: int) -> None:
    success(f"Created {count} tables")


def dropped(count: int) -> None:
    success(f"Dropped {count} tables")
