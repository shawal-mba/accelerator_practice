"""Test schema definitions for Teradata — covers all column types and FK relationships."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import teradatasql

logger = logging.getLogger(__name__)

# Schema definitions: list of (table_name, DDL, description)
TEST_TABLES: list[tuple[str, str, str]] = [
    # ── 1. All scalar types ──────────────────────────────────────────────
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
    # ── 2. CLOB / BLOB ───────────────────────────────────────────────────
    (
        "test_types_lob",
        """CREATE TABLE {db}.test_types_lob (
            id            INTEGER NOT NULL PRIMARY KEY,
            col_clob      CLOB(1000),
            col_blob      BLOB(1000)
        )""",
        "Exercises LOB types.",
    ),
    # ── 3. JSON ──────────────────────────────────────────────────────────
    (
        "test_types_json",
        """CREATE TABLE {db}.test_types_json (
            id            INTEGER NOT NULL PRIMARY KEY,
            col_json      JSON(1000)
        )""",
        "Exercises JSON type.",
    ),
    # ── 4. Interval types ────────────────────────────────────────────────
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
    # ── 5. Period types ──────────────────────────────────────────────────
    (
        "test_types_period",
        """CREATE TABLE {db}.test_types_period (
            id            INTEGER NOT NULL PRIMARY KEY,
            col_period_dt PERIOD(DATE),
            col_period_ts PERIOD(TIMESTAMP(0))
        )""",
        "Exercises PERIOD types.",
    ),
    # ── 6. Parent table: products ────────────────────────────────────────
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
    # ── 7. Parent table: customers ───────────────────────────────────────
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
    # ── 8. Child table: orders (FK → customers) ─────────────────────────
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
    # ── 9. Child table: order_items (FK → orders, FK → products) ────────
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
    # ── 10. Nullable-heavy table ──────────────────────────────────────────
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
    # ── 11. Large-width table ────────────────────────────────────────────
    (
        "test_wide",
        """CREATE TABLE {db}.test_wide (
            id INTEGER NOT NULL PRIMARY KEY
            {col_defs}
        )""",
        "50 VARCHAR columns — stress-tests wide inserts.",
    ),
]

# Build the wide table DDL dynamically
_wide_col_defs = "".join(f",\n            col_{i:03d} VARCHAR(100)" for i in range(50))


def _fmt(ddl: str) -> str:
    if "{col_defs}" in ddl:
        return ddl.format(db="{db}", col_defs=_wide_col_defs)
    return ddl.format(db="{db}")


TEST_TABLES = [(name, _fmt(ddl), desc) for name, ddl, desc in TEST_TABLES]

# Seed order matters: parents before children.
SEED_ORDER: list[tuple[str, int]] = [
    ("test_types_scalar", 10),
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

# Foreign key relationships: child_col → (parent_table, parent_col)
FK_MAP: dict[str, dict[str, tuple[str, str]]] = {
    "test_orders": {
        "customer_id": ("test_customers", "customer_id"),
    },
    "test_order_items": {
        "order_id": ("test_orders", "order_id"),
        "product_id": ("test_products", "product_id"),
    },
}


def create_tables(database: str, conn: teradatasql.TeradataConnection) -> list[str]:
    """Create all test tables. Returns list of table names created."""
    created: list[str] = []
    with conn.cursor() as cur:
        try:
            cur.execute(f"CREATE DATABASE {database} AS PERMANENT = 1e8, SPOOL = 1e8")
            logger.info("Created database %s", database)
        except Exception as exc:
            if "already exists" in str(exc).lower():
                logger.info("Database %s already exists", database)
            else:
                logger.error("Error creating database %s: %s", database, exc)
                return created

        for table_name, ddl, _ in TEST_TABLES:
            try:
                cur.execute(ddl.format(db=database))
                created.append(table_name)
                logger.info("Created %s", table_name)
            except Exception as exc:
                if "already exists" in str(exc).lower():
                    created.append(table_name)
                    logger.info("%s already exists", table_name)
                else:
                    logger.error("Error creating %s: %s", table_name, exc)
    return created


def drop_tables(database: str, conn: teradatasql.TeradataConnection) -> list[str]:
    """Drop all test tables. Returns list of table names dropped."""
    dropped: list[str] = []
    with conn.cursor() as cur:
        for table_name, _, _ in reversed(TEST_TABLES):
            try:
                cur.execute(f"DROP TABLE {database}.{table_name}")
                dropped.append(table_name)
                logger.info("Dropped %s", table_name)
            except Exception as exc:
                if "does not exist" not in str(exc).lower():
                    logger.error("Error dropping %s: %s", table_name, exc)
    return dropped
