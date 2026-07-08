from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import teradatasql


def list_databases(conn: teradatasql.TeradataConnection) -> list[str]:
    """Return sorted list of database names on the server."""
    with conn.cursor() as cur:
        cur.execute("SELECT DatabaseName FROM DBC.DatabasesV ORDER BY 1")
        return [row[0] for row in cur.fetchall()]


def list_tables(
    conn: teradatasql.TeradataConnection, database: str
) -> list[dict[str, str | None]]:
    """Return list of tables (and their types) for a given database."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT TableName, TableKind FROM DBC.TablesV WHERE DatabaseName = ? ORDER BY 1",
            [database],
        )
        return [{"table_name": row[0], "table_kind": row[1].strip()} for row in cur.fetchall()]


def read_table(
    conn: teradatasql.TeradataConnection,
    database: str,
    table_name: str,
    limit: int = 20,
) -> list[tuple]:
    """Return rows from *table_name* capped at *limit*."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {database}.{table_name} SAMPLE {limit}")
        return cur.fetchall()


def get_column_names(
    conn: teradatasql.TeradataConnection,
    database: str,
    table_name: str,
) -> list[str]:
    """Return column names for a table."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT ColumnName FROM DBC.ColumnsV "
            "WHERE DatabaseName = ? AND TableName = ? ORDER BY ColumnId",
            [database, table_name],
        )
        return [row[0] for row in cur.fetchall()]
