from __future__ import annotations

from google.cloud import bigquery


def list_datasets(client: bigquery.Client) -> list[str]:
    """Return sorted list of dataset IDs in the project."""
    return sorted(ds.dataset_id for ds in client.list_datasets())


def list_tables(client: bigquery.Client, dataset: str) -> list[dict[str, str]]:
    """Return list of tables (and their types) for a given dataset."""
    tables = []
    for table in client.list_tables(f"{client.project}.{dataset}"):
        tables.append({"table_name": table.table_id, "table_type": table.table_type})
    return sorted(tables, key=lambda t: t["table_name"])


def get_column_names(client: bigquery.Client, dataset: str, table: str) -> list[str]:
    """Return column names for a table."""
    table_ref = client.get_table(f"{client.project}.{dataset}.{table}")
    return [field.name for field in table_ref.schema]


def read_table(
    client: bigquery.Client,
    dataset: str,
    table: str,
    limit: int = 20,
) -> list[tuple]:
    """Return rows from *table* capped at *limit*."""
    query = f"SELECT * FROM `{client.project}.{dataset}.{table}` LIMIT {limit}"
    return [tuple(row.values()) for row in client.query(query).result()]
