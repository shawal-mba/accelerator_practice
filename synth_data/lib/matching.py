"""Column-to-faker matching, type casting, and SQL identifier validation."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from faker import Faker

fake = Faker("zu_ZA")

# ── SQL identifier validation ────────────────────────────────────────────────

_IDENT_RE = re.compile(r"^[a-zA-Z0-9_]+$")


def ident(name: str) -> str:
    """Validate and return a SQL-safe identifier."""
    if not _IDENT_RE.match(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return name


# ── Column-name keyword matching ─────────────────────────────────────────────
# Checked top-to-bottom; first regex match wins.

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


def _match_column(
    col_name: str, type_map: dict[str, Callable[[], Any]], db_type: str
) -> Callable[[], Any]:
    """Pick a faker generator — name-based regex first, then type-based fallback."""
    lower = col_name.lower()
    for pattern, gen in COLUMN_KEYWORD_MAP:
        if re.search(pattern, lower):
            return gen
    return type_map.get(db_type, fake.word)


# ── BigQuery type map ────────────────────────────────────────────────────────
# Built from google-cloud-bigquery's SqlTypeNames / StandardSqlTypeNames enums.
# Aliases (INT64→INTEGER, FLOAT64→FLOAT, BOOL→BOOLEAN, STRUCT→RECORD) are included.

BQ_TYPE_MAP: dict[str, Callable[[], Any]] = {
    # scalar types
    "STRING": fake.word,
    "BYTES": lambda: fake.binary(10).hex(),
    "INTEGER": lambda: fake.pyint(min_value=0, max_value=100_000),
    "INT64": lambda: fake.pyint(min_value=0, max_value=100_000),
    "FLOAT": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "FLOAT64": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "NUMERIC": lambda: float(round(fake.pyfloat(min_value=0, max_value=10_000), 2)),
    "BIGNUMERIC": lambda: float(round(fake.pyfloat(min_value=0, max_value=10_000), 2)),
    "BOOLEAN": fake.boolean,
    "BOOL": fake.boolean,
    "DATE": lambda: fake.date_between(start_date="-5y", end_date="today").isoformat(),
    "DATETIME": lambda: fake.date_time_between(start_date="-5y").isoformat(),
    "TIMESTAMP": lambda: fake.date_time_between(start_date="-5y").isoformat(),
    "TIME": lambda: fake.time_object().isoformat(),
    "GEOGRAPHY": lambda: f"POINT({fake.longitude()} {fake.latitude()})",
    "JSON": fake.json,
    # composite types
    "RECORD": lambda: {},
    "STRUCT": lambda: {},
}


def match_column_bq(col_name: str, bq_type: str) -> Callable[[], Any]:
    """Pick a faker generator for a BigQuery column."""
    return _match_column(col_name, BQ_TYPE_MAP, bq_type.upper())


# ── Teradata type map ────────────────────────────────────────────────────────
# Type codes come from DBC.ColumnsV.ColumnType — not exposed by teradatasql.


def _td_ts() -> str:
    return fake.date_time_between(start_date="-5y", end_date="now").strftime("%Y-%m-%d %H:%M:%S")

TD_TYPE_MAP: dict[str, Callable[[], Any]] = {
    # character
    "CF": fake.word,
    "CV": fake.word,
    # integer
    "I": lambda: fake.pyint(min_value=0, max_value=100_000),
    "I1": lambda: fake.pyint(min_value=0, max_value=127),
    "I2": lambda: fake.pyint(min_value=0, max_value=32_767),
    "I3": lambda: fake.pyint(min_value=-2_147_483_648, max_value=2_147_483_647),
    "I8": lambda: fake.pyint(min_value=0, max_value=10_000_000),
    "I9": lambda: fake.pyint(min_value=-10_000_000, max_value=10_000_000),
    # decimal / float
    "D": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "F": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "N": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    # binary
    "BF": lambda: fake.binary(10).hex(),
    "BO": lambda: fake.binary(100).hex(),
    # date / time
    "DA": lambda: fake.date_between(start_date="-5y", end_date="today"),
    "TS": _td_ts,
    "OD": _td_ts,
    "TD": _td_ts,
    "TZ": _td_ts,
    "AT": lambda: fake.date_time_between(
        start_date="-5y", end_date="now"
    ).time().replace(microsecond=0),
    # interval
    "YR": lambda: "INTERVAL '1' YEAR",
    "MO": lambda: "INTERVAL '1' MONTH",
    "DY": lambda: "INTERVAL '1' DAY",
    "HR": lambda: "INTERVAL '1' HOUR",
    "MI": lambda: "INTERVAL '1' MINUTE",
    "SC": lambda: "INTERVAL '1' SECOND",
    "DM": lambda: "INTERVAL '1 00:01' DAY TO MINUTE",
    "DV": lambda: "INTERVAL '1 00:00:01' DAY TO SECOND",
    "FD": lambda: "INTERVAL '1 00' DAY TO HOUR",
    "FS": lambda: "INTERVAL '00:00:01' HOUR TO SECOND",
    "FT": lambda: "INTERVAL '00:01' HOUR TO MINUTE",
    "FY": lambda: "INTERVAL '0 00:01' MINUTE TO SECOND",
    # period
    "PD": lambda: (
        fake.date_between(start_date="-5y", end_date="-1y"),
        fake.date_between(start_date="-1y", end_date="+1y"),
    ),
    "PS": lambda: (
        fake.date_time_between(start_date="-5y", end_date="-1y").strftime("%Y-%m-%d %H:%M:%S"),
        fake.date_time_between(start_date="-1y", end_date="+1y").strftime("%Y-%m-%d %H:%M:%S"),
    ),
    # semi-structured
    "JN": fake.json,
    "XM": fake.xml,
    "UT": fake.uuid4,
}


def match_column_td(col_name: str, td_type: str) -> Callable[[], Any]:
    """Pick a faker generator for a Teradata column."""
    return _match_column(col_name, TD_TYPE_MAP, td_type.strip())


# ── Teradata inline SQL casting ──────────────────────────────────────────────
# These types cannot be used with parameterized queries and need CAST expressions.

INLINE_TYPES = frozenset({
    "TS", "OD", "TD", "TZ", "AT", "DA",
    "YR", "MO", "DY", "HR", "MI", "SC",
    "DM", "DV", "FD", "FS", "FT", "FY",
    "PD", "PS",
})


def _format_ts(value: Any) -> str:
    """Extract a TIMESTAMP string from a datetime or ISO string."""
    from datetime import datetime

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, str):
        return value.replace("T", " ").split(".")[0].split("+")[0].split("Z")[0]
    return str(value)


def _format_date(value: Any) -> str:
    """Extract a DATE string from a date or ISO string."""
    from datetime import date

    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str):
        return value.split("T")[0]
    return str(value)


def _format_time(value: Any) -> str:
    """Extract a TIME string from a time/datetime or string."""
    from datetime import datetime
    from datetime import time as dt_time

    if isinstance(value, (dt_time, datetime)):
        return value.strftime("%H:%M:%S")
    return str(value)


def cast_td_value(col_name: str, td_type: str, value: Any) -> str:
    """Return a SQL CAST expression for Teradata types that can't be parameterized."""
    if td_type in ("TS", "OD", "TD", "TZ"):
        return f"CAST('{_format_ts(value)}' AS TIMESTAMP(0))"
    if td_type == "DA":
        return f"DATE '{_format_date(value)}'"
    if td_type == "AT":
        return f"CAST('{_format_time(value)}' AS TIME(0))"
    if td_type == "PD":
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError(f"PD value must be a 2-tuple of dates, got {type(value).__name__}")
        d1, d2 = value
        return f"PERIOD(DATE '{d1}', DATE '{d2}')"
    if td_type == "PS":
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError(
                f"PS value must be a 2-tuple of timestamps, got {type(value).__name__}"
            )
        t1, t2 = value
        if isinstance(t1, str):
            return f"PERIOD(TIMESTAMP '{t1}', TIMESTAMP '{t2}')"
        return f"PERIOD(TIMESTAMP '{t1:%Y-%m-%d %H:%M:%S}', TIMESTAMP '{t2:%Y-%m-%d %H:%M:%S}')"
    if td_type in INLINE_TYPES:
        return str(value)
    return str(value)
