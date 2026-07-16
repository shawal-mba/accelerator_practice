"""Rich console output for CLI results."""

from __future__ import annotations

from collections.abc import Sequence

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

_HEADING = "bold cyan"
_SUCCESS = "bold green"
_ERROR = "bold red"
_WARN = "bold yellow"
_DIM = "dim"
_TABLE_NAME = "bold"


def heading(text: str) -> None:
    console.print(f"\n[bold]{text}[/bold]", style=_HEADING)


def success(text: str) -> None:
    console.print(Panel(text, style=_SUCCESS, border_style=_SUCCESS))


def error(text: str) -> None:
    console.print(Panel(text, style=_ERROR, border_style=_ERROR, title="Error"))


def dim(text: str) -> None:
    console.print(text, style=_DIM)


def _make_table(
    title: str,
    cols: list[tuple[str, str] | tuple[str, str, str]],
    rows: list[list[str]],
) -> None:
    t = Table(
        title=title,
        title_style=_HEADING,
        show_header=True,
        header_style=_HEADING,
        show_lines=False,
        padding=(0, 2),
    )
    for col_spec in cols:
        label = col_spec[0]
        style = col_spec[1] if len(col_spec) > 1 else ""
        justify = col_spec[2] if len(col_spec) > 2 else None
        t.add_column(label, style=style or None, justify=justify)
    for row in rows:
        t.add_row(*row)
    console.print(Panel(t, border_style=_HEADING))


def database_list(databases: list[str]) -> None:
    _make_table(
        "Databases",
        [("#", _DIM), ("Database", _TABLE_NAME)],
        [[str(i), d] for i, d in enumerate(databases, 1)],
    )


def dataset_list(datasets: list[str]) -> None:
    _make_table(
        "Datasets",
        [("#", _DIM), ("Dataset", _TABLE_NAME)],
        [[str(i), d] for i, d in enumerate(datasets, 1)],
    )


def table_list(database: str, tables: list[dict[str, str]], kind_key: str = "table_type") -> None:
    kind_label = "Type" if kind_key == "table_type" else "Kind"
    _make_table(
        f"Tables in {database} ({len(tables)})",
        [("#", _DIM), ("Table", _TABLE_NAME), (kind_label, _DIM)],
        [[str(i), t["table_name"], t.get(kind_key, "")] for i, t in enumerate(tables, 1)],
    )


def column_list(
    database: str,
    table: str,
    columns: Sequence[tuple],
    engine: str = "bigquery",
) -> None:
    cols: list[tuple[str, str]] = [("#", _DIM), ("Column", _TABLE_NAME), ("Type", _DIM)]
    rows: list[list[str]] = []
    if engine == "bigquery":
        cols.append(("Mode", _DIM))
        for i, (col_name, bq_type, is_repeated) in enumerate(columns, 1):
            rows.append([str(i), col_name, bq_type, "REPEATED" if is_repeated else "NULLABLE"])
    else:
        for i, (col_name, td_type) in enumerate(columns, 1):
            rows.append([str(i), col_name, td_type])
    _make_table(f"{database}.{table} ({len(columns)} columns)", cols, rows)


def seed_result_table(results: list[tuple[str, int, str]]) -> None:
    rows: list[list[str]] = []
    for name, inserted, status in results:
        if status == "ok":
            rows.append([name, str(inserted), f"[green]{status}[/green]"])
        else:
            short = status.split("\n")[0][:80]
            rows.append([name, "-", f"[red]{short}[/red]"])
    _make_table(
        f"Seed Results ({len(results)} tables)",
        [("Table", _TABLE_NAME), ("Rows", "", "right"), ("Status", "")],
        rows,
    )


def database_summary(
    databases: list[tuple[str, int, int]],
) -> None:
    total_dbs = len(databases)
    total_tables = sum(t for _, t, _ in databases)
    _make_table(
        f"Summary ({total_dbs} databases, {total_tables} tables)",
        [("Database", _TABLE_NAME), ("Tables", "", "right"), ("Seedable", "", "right")],
        [[d, str(t), str(s)] for d, t, s in databases],
    )


def data_table(col_names: list[str], rows: list[tuple], max_width: int = 40) -> None:
    t = Table(show_header=True, header_style=_HEADING, show_lines=False, padding=(0, 1))
    for name in col_names:
        t.add_column(name, overflow="fold", max_width=max_width)
    for row in rows:
        t.add_row(*(str(v) if v is not None else "[dim]NULL[/dim]" for v in row))
    console.print(Panel(t, title=f"{len(rows)} rows", border_style=_HEADING))
