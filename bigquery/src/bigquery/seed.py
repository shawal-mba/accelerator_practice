from __future__ import annotations

import logging
import random
import re
from typing import Any, Callable

from faker import Faker
from google.cloud import bigquery

from bigquery.analyze import list_tables

logger = logging.getLogger(__name__)

fake = Faker("zu_ZA")

# Column-name keyword -> faker generator.
# Checked top-to-bottom; first match wins.
COLUMN_KEYWORD_MAP: list[tuple[str, Callable[[], Any]]] = [
    # names
    (r"first_?name", fake.first_name),
    (r"last_?name|surname", fake.last_name),
    (r"full_?name|employee_?name", fake.name),
    (r"customer_?name", fake.first_name),
    (r"name", fake.name),
    # contact
    (r"email|e_?mail", fake.email),
    (r"phone|mobile|cell", fake.phone_number),
    # location
    (r"address|street|addr", fake.street_address),
    (r"city", fake.city),
    (r"state|province", fake.province),
    (r"zip|postal|postcode", fake.postcode),
    (r"country", fake.country_code),
    # company / job
    (r"company|corp|organisation|organization", fake.company),
    (r"job_?title|title|role|position", fake.job),
    # finance
    (
        r"price|amount|cost|salary|revenue|balance",
        lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    ),
    (r"credit_?card|card_?number|cc_?num", fake.credit_card_number),
    # ids
    (r"ssn|social_?security", fake.ssn),
    (r"uuid|guid", fake.uuid4),
    # dates
    (
        r"created_?at|updated_?at|timestamp|datetime",
        lambda: fake.date_time_between(start_date="-5y").isoformat(),
    ),
    (
        r"date|day|dob|birth",
        lambda: fake.date_between(start_date="-5y", end_date="today").isoformat(),
    ),
    # misc text
    (r"url|link|website", fake.url),
    (r"ip|ip_?address", fake.ipv4),
    (r"text|description|comment|note|summary", fake.sentence),
    (r"color|colour", fake.color_name),
    (r"lorem", fake.paragraph),
]

# BigQuery type string -> faker generator fallback
BQ_TYPE_MAP: dict[str, Callable[[], Any]] = {
    # string
    "STRING": fake.word,
    "BYTES": lambda: fake.binary(10).hex(),
    # numeric
    "INTEGER": lambda: fake.pyint(min_value=0, max_value=100_000),
    "INT64": lambda: fake.pyint(min_value=0, max_value=100_000),
    "FLOAT": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "FLOAT64": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "NUMERIC": lambda: float(round(fake.pyfloat(min_value=0, max_value=10_000), 2)),
    "BIGNUMERIC": lambda: float(round(fake.pyfloat(min_value=0, max_value=10_000), 2)),
    # boolean
    "BOOL": fake.boolean,
    "BOOLEAN": fake.boolean,
    # date / time
    "DATE": lambda: fake.date_between(start_date="-5y", end_date="today").isoformat(),
    "DATETIME": lambda: fake.date_time_between(start_date="-5y").isoformat(),
    "TIMESTAMP": lambda: fake.date_time_between(start_date="-5y").isoformat(),
    "TIME": lambda: fake.time_object().isoformat(),
    # complex
    "GEOGRAPHY": lambda: f"POINT({fake.longitude()} {fake.latitude()})",
    "JSON": fake.json,
    "RECORD": lambda: {},
    "STRUCT": lambda: {},
}


def _match_column(col_name: str, bq_type: str) -> Callable[[], Any]:
    """Pick a faker generator for a column based on its name and BigQuery type."""
    lower = col_name.lower()
    for pattern, gen in COLUMN_KEYWORD_MAP:
        if re.search(pattern, lower):
            return gen
    return BQ_TYPE_MAP.get(bq_type.upper(), fake.word)


def get_columns(client: bigquery.Client, dataset: str, table: str) -> list[tuple[str, str, bool]]:
    """Return [(column_name, bq_type, is_repeated)] for an existing table."""
    table_ref = client.get_table(f"{client.project}.{dataset}.{table}")
    return [(field.name, field.field_type, field.mode == "REPEATED") for field in table_ref.schema]


def read_column_values(
    client: bigquery.Client,
    dataset: str,
    table: str,
    column: str,
) -> list[Any]:
    """Read all distinct values of *column* from an existing table."""
    query = (
        f"SELECT DISTINCT `{column}` FROM `{client.project}.{dataset}.{table}` "
        f"WHERE `{column}` IS NOT NULL"
    )
    return [row[column] for row in client.query(query).result()]


def insert_fake_rows(
    client: bigquery.Client,
    dataset: str,
    table: str,
    columns: list[tuple[str, str, bool]],
    num_rows: int = 100,
    batch_size: int = 50,
    fk_overrides: dict[str, list[Any]] | None = None,
) -> int:
    """Insert fake data into an existing table.

    Args:
        fk_overrides: mapping of column_name -> list of real values to pick from.
                      Used for referential integrity on foreign-key columns.
    Returns the total number of rows inserted.
    """
    if not columns:
        raise ValueError(f"Table {dataset}.{table} has no columns — refusing to insert.")

    table_ref = client.get_table(f"{client.project}.{dataset}.{table}")

    # Build RECORD sub-field generators from schema
    record_gens: dict[str, list[tuple[str, Callable[[], Any]]]] = {}
    for field in table_ref.schema:
        if field.field_type in ("RECORD", "STRUCT") and field.fields:
            record_gens[field.name] = [
                (sub.name, _match_column(sub.name, sub.field_type)) for sub in field.fields
            ]

    generators = [_match_column(name, bq_type) for name, bq_type, _ in columns]
    col_names = [name for name, _, _ in columns]
    repeated_flags = [repeated for _, _, repeated in columns]

    inserted = 0
    for offset in range(0, num_rows, batch_size):
        batch = min(batch_size, num_rows - offset)
        rows = []
        for _ in range(batch):
            raw_values: list[Any] = []
            for i, gen in enumerate(generators):
                col = col_names[i]
                if fk_overrides and col in fk_overrides:
                    raw_values.append(random.choice(fk_overrides[col]))
                elif col in record_gens:
                    # Generate a dict for RECORD columns
                    raw_values.append({name: g() for name, g in record_gens[col]})
                else:
                    raw_values.append(gen())
            row = dict(
                zip(
                    col_names,
                    [v if not rep else [v] for v, rep in zip(raw_values, repeated_flags)],
                )
            )
            rows.append(row)
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            raise RuntimeError(f"Insert errors: {errors}")
        inserted += batch
    return inserted


def seed_with_relations(
    client: bigquery.Client,
    dataset: str,
    seed_order: list[tuple[str, int]],
    fk_map: dict[str, dict[str, tuple[str, str]]],
) -> list[tuple[str, int, str]]:
    """Seed tables in order, pulling real values for FK columns from parent tables.

    Args:
        seed_order: [(table_id, num_rows)] in dependency order.
        fk_map: {child_table: {child_col: (parent_table, parent_col)}}
    Returns list of (table_name, rows_inserted, status).
    """
    results: list[tuple[str, int, str]] = []
    # Cache of parent values: (parent_table, parent_col) -> list of values
    parent_cache: dict[tuple[str, str], list[Any]] = {}

    for table_id, num_rows in seed_order:
        try:
            columns = get_columns(client, dataset, table_id)
            if not columns:
                results.append((table_id, 0, "no columns found"))
                continue

            # Build FK overrides for this table
            fk_overrides: dict[str, list[Any]] = {}
            table_fks = fk_map.get(table_id, {})
            for child_col, (parent_table, parent_col) in table_fks.items():
                cache_key = (parent_table, parent_col)
                if cache_key not in parent_cache:
                    parent_cache[cache_key] = read_column_values(
                        client, dataset, parent_table, parent_col
                    )
                values = parent_cache[cache_key]
                if not values:
                    results.append((table_id, 0, f"parent {parent_table}.{parent_col} is empty"))
                    break
                fk_overrides[child_col] = values
            else:
                inserted = insert_fake_rows(
                    client, dataset, table_id, columns, num_rows, fk_overrides=fk_overrides
                )
                results.append((table_id, inserted, "ok"))
                continue
        except (ValueError, RuntimeError) as exc:
            logger.warning("Failed to seed %s: %s", table_id, exc)
            results.append((table_id, 0, str(exc)))
    return results


def seed_all(
    client: bigquery.Client,
    dataset: str,
    num_rows: int = 100,
) -> list[tuple[str, int, str]]:
    """Seed every table in *dataset*.

    Returns list of (table_name, rows_inserted, status).
    """
    tables = list_tables(client, dataset)
    results: list[tuple[str, int, str]] = []
    for t in tables:
        name = t["table_name"]
        if t["table_type"] != "TABLE":
            results.append((name, 0, f"skipped ({t['table_type']})"))
            continue
        try:
            columns = get_columns(client, dataset, name)
            if not columns:
                results.append((name, 0, "no columns found"))
                continue
            inserted = insert_fake_rows(client, dataset, name, columns, num_rows)
            results.append((name, inserted, "ok"))
        except (ValueError, RuntimeError) as exc:
            logger.warning("Failed to seed %s: %s", name, exc)
            results.append((name, 0, str(exc)))
    return results
