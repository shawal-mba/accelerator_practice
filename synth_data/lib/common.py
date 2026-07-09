"""Shared faker configuration and column-matching logic."""

from __future__ import annotations

import re
from typing import Any, Callable

from faker import Faker

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
    "STRING": fake.word,
    "BYTES": lambda: fake.binary(10).hex(),
    "INTEGER": lambda: fake.pyint(min_value=0, max_value=100_000),
    "INT64": lambda: fake.pyint(min_value=0, max_value=100_000),
    "FLOAT": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "FLOAT64": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "NUMERIC": lambda: float(round(fake.pyfloat(min_value=0, max_value=10_000), 2)),
    "BIGNUMERIC": lambda: float(round(fake.pyfloat(min_value=0, max_value=10_000), 2)),
    "BOOL": fake.boolean,
    "BOOLEAN": fake.boolean,
    "DATE": lambda: fake.date_between(start_date="-5y", end_date="today").isoformat(),
    "DATETIME": lambda: fake.date_time_between(start_date="-5y").isoformat(),
    "TIMESTAMP": lambda: fake.date_time_between(start_date="-5y").isoformat(),
    "TIME": lambda: fake.time_object().isoformat(),
    "GEOGRAPHY": lambda: f"POINT({fake.longitude()} {fake.latitude()})",
    "JSON": fake.json,
    "RECORD": lambda: {},
    "STRUCT": lambda: {},
}

# Teradata type code -> faker generator fallback
TD_TYPE_MAP: dict[str, Callable[[], Any]] = {
    "CF": fake.word,
    "CV": fake.word,
    "I": lambda: fake.pyint(min_value=0, max_value=100_000),
    "I1": lambda: fake.pyint(min_value=0, max_value=127),
    "I2": lambda: fake.pyint(min_value=0, max_value=32_767),
    "I8": lambda: fake.pyint(min_value=0, max_value=10_000_000),
    "I3": lambda: fake.pyint(min_value=-2_147_483_648, max_value=2_147_483_647),
    "I9": lambda: fake.pyint(min_value=-10_000_000, max_value=10_000_000),
    "D": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "F": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "N": lambda: round(fake.pyfloat(min_value=0, max_value=10_000), 2),
    "BF": lambda: fake.binary(10).hex(),
    "BO": lambda: fake.binary(100).hex(),
    "DA": lambda: fake.date_between(start_date="-5y", end_date="today"),
    "TS": lambda: fake.date_time_between(start_date="-5y", end_date="now").strftime(
        "%Y-%m-%d %H:%M:%S"
    ),
    "AT": lambda: (
        fake.date_time_between(start_date="-5y", end_date="now").time().replace(microsecond=0)
    ),
    "OD": lambda: fake.date_time_between(start_date="-5y", end_date="now").strftime(
        "%Y-%m-%d %H:%M:%S"
    ),
    "TD": lambda: fake.date_time_between(start_date="-5y", end_date="now").strftime(
        "%Y-%m-%d %H:%M:%S"
    ),
    "TZ": lambda: fake.date_time_between(start_date="-5y", end_date="now").strftime(
        "%Y-%m-%d %H:%M:%S"
    ),
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
    "PD": lambda: (
        fake.date_between(start_date="-5y", end_date="-1y"),
        fake.date_between(start_date="-1y", end_date="+1y"),
    ),
    "PS": lambda: (
        fake.date_time_between(start_date="-5y", end_date="-1y").strftime("%Y-%m-%d %H:%M:%S"),
        fake.date_time_between(start_date="-1y", end_date="+1y").strftime("%Y-%m-%d %H:%M:%S"),
    ),
    "JN": fake.json,
    "XM": fake.xml,
    "UT": fake.uuid4,
}


def match_column_bq(col_name: str, bq_type: str) -> Callable[[], Any]:
    """Pick a faker generator for a column based on its name and BigQuery type."""
    lower = col_name.lower()
    for pattern, gen in COLUMN_KEYWORD_MAP:
        if re.search(pattern, lower):
            return gen
    return BQ_TYPE_MAP.get(bq_type.upper(), fake.word)


def match_column_td(col_name: str, td_type: str) -> Callable[[], Any]:
    """Pick a faker generator for a column based on its name and Teradata type."""
    lower = col_name.lower()
    for pattern, gen in COLUMN_KEYWORD_MAP:
        if re.search(pattern, lower):
            return gen
    return TD_TYPE_MAP.get(td_type.strip(), fake.word)


# Teradata types that cannot be inserted via parameterized queries
INLINE_TYPES = {
    "TS", "OD", "TD", "TZ", "AT",
    "YR", "MO", "DY", "HR", "MI", "SC",
    "DM", "DV", "FD", "FS", "FT", "FY",
    "PD", "PS",
}


def cast_td_value(col_name: str, td_type: str, value: Any) -> str:
    """Return a SQL CAST expression for Teradata types that can't be parameterized."""
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
        d1, d2 = value
        return f"PERIOD(DATE '{d1}', DATE '{d2}')"
    if td_type == "PS":
        t1, t2 = value
        if isinstance(t1, str):
            return f"PERIOD(TIMESTAMP '{t1}', TIMESTAMP '{t2}')"
        ts1 = t1.strftime("%Y-%m-%d %H:%M:%S")
        ts2 = t2.strftime("%Y-%m-%d %H:%M:%S")
        return f"PERIOD(TIMESTAMP '{ts1}', TIMESTAMP '{ts2}')"
    if td_type in ("YR", "MO", "DY", "HR", "MI", "SC", "DM", "DV", "FD", "FS", "FT", "FY"):
        return value
    return str(value)
