"""Test schema definitions for BigQuery — covers all column types and FK relationships."""

from __future__ import annotations

import logging

from google.api_core.exceptions import GoogleAPIError, NotFound
from google.cloud import bigquery

logger = logging.getLogger(__name__)

# Schema definitions: list of (table_id, schema_fields, description)
# Each schema_field is a dict with keys: name, type, mode, description

TEST_TABLES: list[tuple[str, list[dict], str]] = [
    # ── 1. All scalar types ──────────────────────────────────────────────
    (
        "test_types_scalar",
        [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "col_string", "type": "STRING", "mode": "NULLABLE"},
            {"name": "col_bytes", "type": "BYTES", "mode": "NULLABLE"},
            {"name": "col_int", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "col_float", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "col_numeric", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "col_bignumeric", "type": "BIGNUMERIC", "mode": "NULLABLE"},
            {"name": "col_bool", "type": "BOOLEAN", "mode": "NULLABLE"},
            {"name": "col_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "col_datetime", "type": "DATETIME", "mode": "NULLABLE"},
            {"name": "col_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "col_time", "type": "TIME", "mode": "NULLABLE"},
            {"name": "col_json", "type": "JSON", "mode": "NULLABLE"},
        ],
        "Exercises every scalar BigQuery type.",
    ),
    # ── 2. Repeated / array columns ──────────────────────────────────────
    (
        "test_types_repeated",
        [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "tags", "type": "STRING", "mode": "REPEATED"},
            {"name": "scores", "type": "FLOAT64", "mode": "REPEATED"},
            {"name": "flags", "type": "BOOLEAN", "mode": "REPEATED"},
        ],
        "Exercises REPEATED (array) columns.",
    ),
    # ── 3. Struct / record columns ───────────────────────────────────────
    (
        "test_types_struct",
        [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {
                "name": "address",
                "type": "RECORD",
                "mode": "NULLABLE",
                "fields": [
                    {"name": "street", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "city", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "zip", "type": "STRING", "mode": "NULLABLE"},
                ],
            },
        ],
        "Exercises RECORD (struct) columns.",
    ),
    # ── 4. Geography ─────────────────────────────────────────────────────
    (
        "test_types_geography",
        [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "location", "type": "GEOGRAPHY", "mode": "NULLABLE"},
        ],
        "Exercises GEOGRAPHY type.",
    ),
    # ── 5. Parent table: products ────────────────────────────────────────
    (
        "test_products",
        [
            {"name": "product_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "product_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "category", "type": "STRING", "mode": "NULLABLE"},
            {"name": "price", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "in_stock", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "Parent table for FK tests.",
    ),
    # ── 6. Parent table: customers ───────────────────────────────────────
    (
        "test_customers",
        [
            {"name": "customer_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "first_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "last_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "email", "type": "STRING", "mode": "NULLABLE"},
            {"name": "phone", "type": "STRING", "mode": "NULLABLE"},
            {"name": "signup_date", "type": "DATE", "mode": "NULLABLE"},
        ],
        "Parent table for FK tests.",
    ),
    # ── 7. Child table: orders (FK → customers) ─────────────────────────
    (
        "test_orders",
        [
            {"name": "order_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "order_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "total_amount", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
        ],
        "Child of test_customers — customer_id is a logical FK.",
    ),
    # ── 8. Child table: order_items (FK → orders, FK → products) ────────
    (
        "test_order_items",
        [
            {"name": "item_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "order_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "product_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "quantity", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "unit_price", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "Child of test_orders + test_products — FK to both.",
    ),
    # ── 9. Nullable-heavy table ──────────────────────────────────────────
    (
        "test_nullable",
        [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "opt_string", "type": "STRING", "mode": "NULLABLE"},
            {"name": "opt_int", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "opt_float", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "opt_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "opt_bool", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "All columns nullable — tests NULL generation.",
    ),
    # ── 10. Large-cardinality table ──────────────────────────────────────
    (
        "test_wide",
        [{"name": f"col_{i:03d}", "type": "STRING", "mode": "NULLABLE"} for i in range(50)]
        + [{"name": "id", "type": "INTEGER", "mode": "REQUIRED"}],
        "50 string columns — stress-tests wide inserts.",
    ),
]

# Seed order matters: parents before children.
# Each entry: (table_id, seed_count)
SEED_ORDER: list[tuple[str, int]] = [
    ("test_types_scalar", 10),
    ("test_types_repeated", 10),
    ("test_types_struct", 10),
    ("test_types_geography", 10),
    ("test_products", 20),
    ("test_customers", 30),
    ("test_orders", 50),
    ("test_order_items", 100),
    ("test_nullable", 20),
    ("test_wide", 10),
]

# Foreign key relationships: child_col → (parent_table, parent_col)
# Used by seed to pull real values from parent tables.
FK_MAP: dict[str, dict[str, tuple[str, str]]] = {
    "test_orders": {
        "customer_id": ("test_customers", "customer_id"),
    },
    "test_order_items": {
        "order_id": ("test_orders", "order_id"),
        "product_id": ("test_products", "product_id"),
    },
}


def _make_schema_field(f: dict) -> bigquery.SchemaField:
    """Convert a dict to a SchemaField, mapping 'type' to 'field_type'."""
    f = dict(f)  # copy
    if "type" in f:
        f["field_type"] = f.pop("type")
    if "fields" in f:
        f["fields"] = [_make_schema_field(sub) for sub in f["fields"]]
    return bigquery.SchemaField(**f)


def create_tables(project: str, dataset: str) -> list[str]:
    """Create all test tables in the given dataset. Returns list of table IDs created."""
    client = bigquery.Client(project=project)
    created: list[str] = []

    for table_id, schema_fields, description in TEST_TABLES:
        full_id = f"{project}.{dataset}.{table_id}"
        schema = [_make_schema_field(f) for f in schema_fields]
        table = bigquery.Table(full_id, schema=schema)
        table.description = description
        table = client.create_table(table, exists_ok=True)
        created.append(table_id)
        logger.info("Created %s (%d columns)", table_id, len(schema))

    client.close()
    return created


def drop_tables(project: str, dataset: str) -> list[str]:
    """Drop all test tables. Returns list of table IDs dropped."""
    client = bigquery.Client(project=project)
    dropped: list[str] = []

    for table_id, _, _ in TEST_TABLES:
        full_id = f"{project}.{dataset}.{table_id}"
        try:
            client.delete_table(full_id, not_found_ok=True)
            dropped.append(table_id)
            logger.info("Dropped %s", table_id)
        except NotFound:
            logger.debug("Table %s not found, skipping", table_id)
        except GoogleAPIError as exc:
            logger.error("Error dropping %s: %s", table_id, exc)

    client.close()
    return dropped
