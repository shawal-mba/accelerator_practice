from __future__ import annotations

import logging
import random
import re
from typing import TYPE_CHECKING, Any, Callable

from faker import Faker

if TYPE_CHECKING:
    import teradatasql

from teraremote.analyze import list_tables

logger = logging.getLogger(__name__)

fake = Faker("zu_ZA")

# Column-name keyword → faker generator.
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
        lambda: fake.date_time_between(start_date="-5y"),
    ),
    (r"date|day|dob|birth", lambda: fake.date_between(start_date="-5y", end_date="today")),
    # misc text
    (r"url|link|website", fake.url),
    (r"ip|ip_?address", fake.ipv4),
    (r"text|description|comment|note|summary", fake.sentence),
    (r"color|colour", fake.color_name),
    (r"lorem", fake.paragraph),
]

# Teradata type code → faker generator fallback
TD_TYPE_MAP: dict[str, Callable[[], Any]] = {
    # character
    "CF": fake.word,  # CHAR
    "CV": fake.word,  # VARCHAR
    # numeric integer
    "I": lambda: fake.pyint(min_value=0, max_value=100_000),  # INTEGER
    "I1": lambda: fake.pyint(min_value=0, max_value=127),  # BYTEINT
    "I2": lambda: fake.pyint(min_value=0, max_value=32_767),  # SMALLINT
    "I8": lambda: fake.pyint(min_value=0, max_value=10_000_000),  # BIGINT
    "I3": lambda: fake.pyint(min_value=-2_147_483_648, max_value=2_147_483_647),  # INTEGER SIGNED
    "I9": lambda: fake.pyint(min_value=-10_000_000, max_value=10_000_000),  # BIGINT SIGNED
    # numeric decimal
    "D": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),  # DECIMAL
    "F": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),  # FLOAT
    "N": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),  # NUMBER
    # byte / blob
    "BF": lambda: fake.binary(10).hex(),  # BYTE
    "BO": lambda: fake.binary(100).hex(),  # BLOB
    # date / time
    "DA": lambda: fake.date_between(start_date="-5y", end_date="today"),  # DATE
    "TS": lambda: fake.date_time_between(start_date="-5y", end_date="now").strftime(
        "%Y-%m-%d %H:%M:%S"
    ),  # TIMESTAMP
    "AT": lambda: (
        fake.date_time_between(start_date="-5y", end_date="now").time().replace(microsecond=0)
    ),  # TIME
    "OD": lambda: fake.date_time_between(start_date="-5y", end_date="now").strftime(
        "%Y-%m-%d %H:%M:%S"
    ),  # TIMESTAMP WITH TIME ZONE
    "TD": lambda: fake.date_time_between(start_date="-5y", end_date="now").strftime(
        "%Y-%m-%d %H:%M:%S"
    ),  # TIMESTAMP WITH LOCAL TIME ZONE
    "TZ": lambda: fake.date_time_between(start_date="-5y", end_date="now").strftime(
        "%Y-%m-%d %H:%M:%S"
    ),  # TIMESTAMP WITH TIME ZONE
    # interval — use proper INTERVAL literal syntax
    "YR": lambda: "INTERVAL '1' YEAR",  # INTERVAL YEAR
    "MO": lambda: "INTERVAL '1' MONTH",  # INTERVAL MONTH
    "DY": lambda: "INTERVAL '1' DAY",  # INTERVAL DAY
    "HR": lambda: "INTERVAL '1' HOUR",  # INTERVAL HOUR
    "MI": lambda: "INTERVAL '1' MINUTE",  # INTERVAL MINUTE
    "SC": lambda: "INTERVAL '1' SECOND",  # INTERVAL SECOND
    "DM": lambda: "INTERVAL '1 00:01' DAY TO MINUTE",  # INTERVAL DAY TO MINUTE
    "DV": lambda: "INTERVAL '1 00:00:01' DAY TO SECOND",  # INTERVAL DAY TO SECOND
    "FD": lambda: "INTERVAL '1 00' DAY TO HOUR",  # INTERVAL DAY TO HOUR
    "FS": lambda: "INTERVAL '00:00:01' HOUR TO SECOND",  # INTERVAL HOUR TO SECOND
    "FT": lambda: "INTERVAL '00:01' HOUR TO MINUTE",  # INTERVAL HOUR TO MINUTE
    "FY": lambda: "INTERVAL '0 00:01' MINUTE TO SECOND",  # INTERVAL MINUTE TO SECOND
    # period — use proper PERIOD literal syntax
    "PD": lambda: (
        fake.date_between(start_date="-5y", end_date="-1y"),
        fake.date_between(start_date="-1y", end_date="+1y"),
    ),  # PERIOD(DATE)
    "PS": lambda: (
        fake.date_time_between(start_date="-5y", end_date="-1y").strftime("%Y-%m-%d %H:%M:%S"),
        fake.date_time_between(start_date="-1y", end_date="+1y").strftime("%Y-%m-%d %H:%M:%S"),
    ),  # PERIOD(TIMESTAMP)
    # json / xml
    "JN": fake.json,  # JSON
    "XM": fake.xml,  # XML
    # rowid
    "UT": fake.uuid4,  # UNIQUE ROWID
}


def _match_column(col_name: str, td_type: str) -> Callable[[], Any]:
    """Pick a faker generator for a column based on its name and Teradata type."""
    lower = col_name.lower()
    for pattern, gen in COLUMN_KEYWORD_MAP:
        if re.search(pattern, lower):
            return gen
    # fall back to type-based generator, then generic word
    return TD_TYPE_MAP.get(td_type.strip(), fake.word)


def get_columns(
    conn: teradatasql.TeradataConnection, database: str, table_name: str
) -> list[tuple[str, str]]:
    """Return [(column_name, td_type_code)] for an existing table."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT ColumnName, ColumnType FROM DBC.ColumnsV "
            "WHERE DatabaseName = ? AND TableName = ? ORDER BY ColumnId",
            [database, table_name],
        )
        return [(row[0], row[1].strip()) for row in cur.fetchall()]


def read_column_values(
    conn: teradatasql.TeradataConnection,
    database: str,
    table: str,
    column: str,
) -> list[Any]:
    """Read all distinct values of *column* from an existing table."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT DISTINCT {column} FROM {database}.{table} WHERE {column} IS NOT NULL")
        return [row[0] for row in cur.fetchall()]


# Types that cannot be inserted via parameterized queries in Teradata
_INLINE_TYPES = {
    "TS",
    "OD",
    "TD",
    "TZ",
    "AT",
    # intervals
    "YR",
    "MO",
    "DY",
    "HR",
    "MI",
    "SC",
    # multi-element intervals
    "DM",
    "DV",
    "FD",
    "FS",
    "FT",
    "FY",
    # period
    "PD",
    "PS",
}


def _cast_value(col_name: str, td_type: str, value: Any) -> str:
    """Return a SQL CAST expression for types that can't be parameterized."""
    from datetime import datetime
    from datetime import time as dt_time

    if td_type in ("TS", "OD", "TD", "TZ"):
        if isinstance(value, datetime):
            ts_str = value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            ts_str = str(value)
        return f"CAST('{ts_str}' AS TIMESTAMP(0))"
    if td_type == "AT":
        if isinstance(value, dt_time):
            time_str = value.strftime("%H:%M:%S")
        elif isinstance(value, datetime):
            time_str = value.strftime("%H:%M:%S")
        else:
            time_str = str(value)
        return f"CAST('{time_str}' AS TIME(0))"
    if td_type == "PD":
        # PERIOD(DATE) → PERIOD(DATE '...', DATE '...')
        d1, d2 = value
        return f"PERIOD(DATE '{d1}', DATE '{d2}')"
    if td_type == "PS":
        # PERIOD(TIMESTAMP) → PERIOD(TIMESTAMP '...', TIMESTAMP '...')
        t1, t2 = value
        if isinstance(t1, str):
            return f"PERIOD(TIMESTAMP '{t1}', TIMESTAMP '{t2}')"
        ts1 = t1.strftime("%Y-%m-%d %H:%M:%S")
        ts2 = t2.strftime("%Y-%m-%d %H:%M:%S")
        return f"PERIOD(TIMESTAMP '{ts1}', TIMESTAMP '{ts2}')"
    # INTERVAL types — value is already a literal string like "INTERVAL '1' DAY"
    if td_type in ("YR", "MO", "DY", "HR", "MI", "SC", "DM", "DV", "FD", "FS", "FT", "FY"):
        return value  # already a SQL literal
    return str(value)


def insert_fake_rows(
    conn: teradatasql.TeradataConnection,
    database: str,
    table_name: str,
    columns: list[tuple[str, str]],
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
        raise ValueError(f"Table {database}.{table_name} has no columns — refusing to insert.")

    generators = [_match_column(name, td_type) for name, td_type in columns]
    col_name_list = [name for name, _ in columns]
    td_types = [td_type for _, td_type in columns]

    # Check if any columns need inline SQL
    has_inline = any(t in _INLINE_TYPES for t in td_types)

    inserted = 0
    with conn.cursor() as cur:
        for offset in range(0, num_rows, batch_size):
            batch = min(batch_size, num_rows - offset)
            if has_inline:
                # Must use individual INSERT statements with CAST
                for _ in range(batch):
                    values: list[Any] = []
                    for i, gen in enumerate(generators):
                        col = col_name_list[i]
                        td_type = td_types[i]
                        if fk_overrides and col in fk_overrides:
                            raw = random.choice(fk_overrides[col])
                        else:
                            raw = gen()
                        if td_type in _INLINE_TYPES:
                            values.append(_cast_value(col, td_type, raw))
                        else:
                            values.append(raw)

                    # Build SQL with inline CAST values for special types
                    parts = []
                    param_values = []
                    for i, val in enumerate(values):
                        if td_types[i] in _INLINE_TYPES:
                            parts.append(val)  # already a SQL expression
                        else:
                            parts.append("?")
                            param_values.append(val)

                    sql = (
                        f"INSERT INTO {database}.{table_name} "
                        f"({', '.join(col_name_list)}) "
                        f"VALUES ({', '.join(parts)})"
                    )
                    cur.execute(sql, param_values)
                    inserted += 1
            else:
                # All columns can be parameterized — use executemany
                col_names_str = ", ".join(col_name_list)
                placeholders = ", ".join("?" for _ in columns)
                sql = (
                    f"INSERT INTO {database}.{table_name} "
                    f"({col_names_str}) VALUES ({placeholders})"
                )
                rows = []
                for _ in range(batch):
                    row = []
                    for i, gen in enumerate(generators):
                        col = col_name_list[i]
                        if fk_overrides and col in fk_overrides:
                            row.append(random.choice(fk_overrides[col]))
                        else:
                            row.append(gen())
                    rows.append(row)
                cur.executemany(sql, rows)
                inserted += batch
    return inserted


def seed_with_relations(
    conn: teradatasql.TeradataConnection,
    database: str,
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
    parent_cache: dict[tuple[str, str], list[Any]] = {}

    for table_id, num_rows in seed_order:
        try:
            columns = get_columns(conn, database, table_id)
            if not columns:
                results.append((table_id, 0, "no columns found"))
                continue

            fk_overrides: dict[str, list[Any]] = {}
            table_fks = fk_map.get(table_id, {})
            skip = False
            for child_col, (parent_table, parent_col) in table_fks.items():
                cache_key = (parent_table, parent_col)
                if cache_key not in parent_cache:
                    parent_cache[cache_key] = read_column_values(
                        conn, database, parent_table, parent_col
                    )
                values = parent_cache[cache_key]
                if not values:
                    results.append((table_id, 0, f"parent {parent_table}.{parent_col} is empty"))
                    skip = True
                    break
                fk_overrides[child_col] = values

            if skip:
                continue

            inserted = insert_fake_rows(
                conn, database, table_id, columns, num_rows, fk_overrides=fk_overrides
            )
            results.append((table_id, inserted, "ok"))
        except (ValueError, RuntimeError) as exc:
            logger.warning("Failed to seed %s: %s", table_id, exc)
            results.append((table_id, 0, str(exc)))
    return results


def seed_all(
    conn: teradatasql.TeradataConnection,
    database: str,
    num_rows: int = 100,
) -> list[tuple[str, int, str]]:
    """Seed every data table in *database*.

    Reads columns for each table first. Returns list of
    (table_name, rows_inserted, status) where status is 'ok' or an error.
    """
    tables = list_tables(conn, database)
    results: list[tuple[str, int, str]] = []
    for t in tables:
        name = t["table_name"]
        if t["table_kind"] != "T":
            results.append((name, 0, f"skipped ({t['table_kind']})"))
            continue
        try:
            columns = get_columns(conn, database, name)
            if not columns:
                results.append((name, 0, "no columns found"))
                continue
            inserted = insert_fake_rows(conn, database, name, columns, num_rows)
            results.append((name, inserted, "ok"))
        except (ValueError, RuntimeError) as exc:
            logger.warning("Failed to seed %s: %s", name, exc)
            results.append((name, 0, str(exc)))
    return results
