"""Test schema definitions — BigQuery schemas + Teradata DDL."""

from __future__ import annotations

from google.cloud import bigquery

# ── BigQuery test tables ─────────────────────────────────────────────────────

BQ_TEST_TABLES: list[tuple[str, list[dict], str]] = [
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
    (
        "test_types_geography",
        [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "location", "type": "GEOGRAPHY", "mode": "NULLABLE"},
        ],
        "Exercises GEOGRAPHY type.",
    ),
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
    (
        "test_orders",
        [
            {"name": "order_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "order_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "total_amount", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
        ],
        "Child of test_customers.",
    ),
    (
        "test_order_items",
        [
            {"name": "item_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "order_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "product_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "quantity", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "unit_price", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "Child of test_orders + test_products.",
    ),
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
    (
        "test_wide",
        [{"name": f"col_{i:03d}", "type": "STRING", "mode": "NULLABLE"} for i in range(50)]
        + [{"name": "id", "type": "INTEGER", "mode": "REQUIRED"}],
        "50 string columns — stress-tests wide inserts.",
    ),
]

# ── Teradata test tables ─────────────────────────────────────────────────────

TD_TEST_TABLES_RAW: list[tuple[str, str, str]] = [
    (
        "test_types_scalar",
        """CREATE TABLE {db}.test_types_scalar (
            id            INTEGER NOT NULL PRIMARY KEY,
            col_varchar   VARCHAR(100),
            col_char      CHAR(20),
            col_integer   INTEGER,
            col_smallint  SMALLINT,
            col_bigint    BIGINT,
            col_byteint   BYTEINT,
            col_decimal   DECIMAL(10,2),
            col_float     FLOAT,
            col_date      DATE,
            col_timestamp TIMESTAMP(0),
            col_time      TIME(0)
        )""",
        "Exercises every scalar Teradata type.",
    ),
    (
        "test_types_lob",
        """CREATE TABLE {db}.test_types_lob (
            id            INTEGER NOT NULL PRIMARY KEY,
            col_clob      CLOB(1000),
            col_blob      BLOB(1000)
        )""",
        "Exercises LOB types.",
    ),
    (
        "test_types_json",
        """CREATE TABLE {db}.test_types_json (
            id            INTEGER NOT NULL PRIMARY KEY,
            col_json      JSON(1000)
        )""",
        "Exercises JSON type.",
    ),
    (
        "test_types_interval",
        """CREATE TABLE {db}.test_types_interval (
            id              INTEGER NOT NULL PRIMARY KEY,
            col_interval_yy INTERVAL YEAR(4),
            col_interval_mo INTERVAL MONTH(3),
            col_interval_dy INTERVAL DAY(4),
            col_interval_hr INTERVAL HOUR(3),
            col_interval_mn INTERVAL MINUTE(3),
            col_interval_sc INTERVAL SECOND(3,3)
        )""",
        "Exercises INTERVAL types.",
    ),
    (
        "test_types_period",
        """CREATE TABLE {db}.test_types_period (
            id            INTEGER NOT NULL PRIMARY KEY,
            col_period_dt PERIOD(DATE),
            col_period_ts PERIOD(TIMESTAMP(0))
        )""",
        "Exercises PERIOD types.",
    ),
    (
        "test_products",
        """CREATE TABLE {db}.test_products (
            product_id    INTEGER NOT NULL PRIMARY KEY,
            product_name  VARCHAR(100) NOT NULL,
            category      VARCHAR(50),
            price         DECIMAL(10,2),
            in_stock      BYTEINT DEFAULT 1
        )""",
        "Parent table for FK tests.",
    ),
    (
        "test_customers",
        """CREATE TABLE {db}.test_customers (
            customer_id   INTEGER NOT NULL PRIMARY KEY,
            first_name    VARCHAR(50) NOT NULL,
            last_name     VARCHAR(50) NOT NULL,
            email         VARCHAR(100),
            phone         VARCHAR(20),
            signup_date   DATE
        )""",
        "Parent table for FK tests.",
    ),
    (
        "test_orders",
        """CREATE TABLE {db}.test_orders (
            order_id      INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER NOT NULL REFERENCES {db}.test_customers(customer_id),
            order_date    DATE,
            total_amount  DECIMAL(12,2),
            status        VARCHAR(20)
        )""",
        "Child of test_customers.",
    ),
    (
        "test_order_items",
        """CREATE TABLE {db}.test_order_items (
            item_id       INTEGER NOT NULL PRIMARY KEY,
            order_id      INTEGER NOT NULL REFERENCES {db}.test_orders(order_id),
            product_id    INTEGER NOT NULL REFERENCES {db}.test_products(product_id),
            quantity      INTEGER DEFAULT 1,
            unit_price    DECIMAL(10,2)
        )""",
        "Child of test_orders + test_products.",
    ),
    (
        "test_nullable",
        """CREATE TABLE {db}.test_nullable (
            id            INTEGER NOT NULL PRIMARY KEY,
            opt_string    VARCHAR(100),
            opt_integer   INTEGER,
            opt_decimal   DECIMAL(10,2),
            opt_date      DATE,
            opt_float     FLOAT
        )""",
        "All columns nullable — tests NULL generation.",
    ),
    (
        "test_wide",
        """CREATE TABLE {db}.test_wide (
            id INTEGER NOT NULL PRIMARY KEY
            {col_defs}
        )""",
        "50 VARCHAR columns — stress-tests wide inserts.",
    ),
]

_wide_col_defs = "".join(f",\n            col_{i:03d} VARCHAR(100)" for i in range(50))


def _fmt_td(ddl: str) -> str:
    if "{col_defs}" in ddl:
        return ddl.format(db="{db}", col_defs=_wide_col_defs)
    return ddl.format(db="{db}")


TD_TEST_TABLES = [(name, _fmt_td(ddl), desc) for name, ddl, desc in TD_TEST_TABLES_RAW]

# ── Shared seed order & FK map ───────────────────────────────────────────────

SEED_ORDER: list[tuple[str, int]] = [
    ("test_types_scalar", 10),
    ("test_types_repeated", 10),
    ("test_types_struct", 10),
    ("test_types_geography", 10),
    ("test_types_lob", 10),
    ("test_types_json", 10),
    ("test_types_interval", 10),
    ("test_types_period", 10),
    ("test_products", 20),
    ("test_customers", 30),
    ("test_orders", 50),
    ("test_order_items", 100),
    ("test_nullable", 20),
    ("test_wide", 10),
]

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
    """Convert a dict to a BigQuery SchemaField."""
    f = dict(f)
    if "type" in f:
        f["field_type"] = f.pop("type")
    if "fields" in f:
        f["fields"] = [_make_schema_field(sub) for sub in f["fields"]]
    return bigquery.SchemaField(**f)
