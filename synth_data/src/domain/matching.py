"""Column-to-generator matching, type casting, and SQL identifier validation."""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date, datetime, timezone
from datetime import time as dt_time
from typing import Any

from src.domain.ports import DataGenerator

_IDENT_RE = re.compile(r"^[a-zA-Z0-9_]+$")


def ident(name: str) -> str:
    if not _IDENT_RE.match(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return name


def _build_column_keyword_map(gen: DataGenerator) -> list[tuple[str, Callable[[], Any]]]:
    return [
        (r"first_?name", gen.first_name),
        (r"last_?name|surname", gen.last_name),
        (r"full_?name|employee_?name", gen.name),
        (r"customer_?name", gen.first_name),
        (r"name", gen.name),
        (r"email|e_?mail", gen.email),
        (r"phone|mobile|cell", lambda: re.sub(r"x\d+$", "", gen.phone_number())),
        (r"address|street|addr", gen.street_address),
        (r"city", gen.city),
        (r"state|province|region", gen.province),
        (r"zip|postal|postcode", gen.postcode),
        (r"country", gen.country),
        (r"country_?code", gen.country_code),
        (r"latitude|lat", lambda: gen.latitude()),
        (r"longitude|lon|lng", lambda: gen.longitude()),
        (r"company|corp|organisation|organization", gen.company),
        (r"job_?title|title|role|position", gen.job),
        (
            r"price|amount|cost|salary|revenue|balance",
            lambda: round(gen.pyfloat(min_value=0, max_value=10_000), 2),
        ),
        (r"credit_?card|card_?number|cc_?num", gen.credit_card_number),
        (r"iban", gen.iban),
        (r"currency_?code", gen.currency_code),
        (r"ssn|social_?security", gen.ssn),
        (r"uuid|guid", gen.uuid4),
        (r"isbn", gen.isbn13),
        (r"mac_?address|mac", gen.mac_address),
        (
            r"created_?at|updated_?at|timestamp|datetime",
            lambda: gen.date_time_between(start_date="-5y").isoformat(),
        ),
        (
            r"date|day|dob|birth",
            lambda: gen.date_between(start_date="-5y", end_date="today").isoformat(),
        ),
        (r"year", lambda: str(gen.year())),
        (r"month", gen.month),
        (r"url|link|website", gen.url),
        (r"domain|hostname", gen.domain_name),
        (r"ip|ip_?address", gen.ipv4),
        (r"slug", gen.slug),
        (r"password|passwd", gen.password),
        (r"hash|sha|md5", gen.sha256),
        (r"mime|content_?type", gen.mime_type),
        (r"file_?ext|extension", gen.file_extension),
        (r"timezone|tz", gen.timezone),
        (r"text|description|comment|note|summary", gen.sentence),
        (r"color|colour|hex_?color", gen.hex_color),
        (r"lorem", gen.paragraph),
    ]


def _build_bq_type_map(gen: DataGenerator) -> dict[str, Callable[[], Any]]:
    return {
        "STRING": gen.word,
        "BYTES": lambda: gen.binary(10).hex(),
        "INTEGER": lambda: gen.pyint(min_value=1, max_value=50_000),
        "INT64": lambda: gen.pyint(min_value=1, max_value=50_000),
        "FLOAT": lambda: round(gen.pyfloat(min_value=1, max_value=9_999), 2),
        "FLOAT64": lambda: round(gen.pyfloat(min_value=1, max_value=9_999), 2),
        "NUMERIC": lambda: float(round(gen.pyfloat(min_value=1, max_value=9_999), 2)),
        "BIGNUMERIC": lambda: float(round(gen.pyfloat(min_value=1, max_value=9_999), 2)),
        "BOOLEAN": gen.boolean if hasattr(gen, "boolean") else lambda: False,
        "BOOL": gen.boolean if hasattr(gen, "boolean") else lambda: False,
        "DATE": lambda: gen.date_between(start_date="-5y", end_date="today").isoformat(),
        "DATETIME": lambda: gen.date_time_between(start_date="-5y").isoformat(),
        "TIMESTAMP": lambda: gen.date_time_between(start_date="-5y").isoformat(),
        "TIME": lambda: gen.time_object().isoformat(),
        "GEOGRAPHY": lambda: f"POINT({gen.longitude()} {gen.latitude()})",
        "JSON": gen.json,
        "RECORD": lambda: {},
        "STRUCT": lambda: {},
    }


def _build_td_type_map(gen: DataGenerator) -> dict[str, Callable[[], Any]]:
    def _td_ts() -> str:
        return gen.date_time_between(start_date="-5y", end_date="now").strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return {
        "CF": gen.word,
        "CV": gen.word,
        "CH": gen.word,
        "CHR": gen.word,
        "I": lambda: gen.pyint(min_value=1, max_value=50_000),
        "I1": lambda: gen.pyint(min_value=0, max_value=127),
        "I2": lambda: gen.pyint(min_value=0, max_value=32_767),
        "I3": lambda: gen.pyint(min_value=1, max_value=50_000),
        "I8": lambda: gen.pyint(min_value=1, max_value=50_000),
        "I9": lambda: gen.pyint(min_value=1, max_value=50_000),
        "BT": lambda: gen.pyint(min_value=0, max_value=127),
        "SM": lambda: gen.pyint(min_value=0, max_value=32_767),
        "D": lambda: round(gen.pyfloat(min_value=1, max_value=9_999), 2),
        "F": lambda: round(gen.pyfloat(min_value=1, max_value=9_999), 2),
        "N": lambda: round(gen.pyfloat(min_value=1, max_value=9_999), 2),
        "BF": lambda: gen.binary(10).hex(),
        "BO": lambda: gen.binary(100).hex(),
        "DA": lambda: gen.date_between(start_date="-5y", end_date="today"),
        "TS": _td_ts,
        "OD": _td_ts,
        "TD": _td_ts,
        "TZ": _td_ts,
        "AT": lambda: (
            gen.date_time_between(start_date="-5y", end_date="now").time().replace(microsecond=0)
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
            gen.date_between(start_date="-5y", end_date="-1y"),
            gen.date_between(start_date="-1y", end_date="+1y"),
        ),
        "PS": lambda: (
            gen.date_time_between(start_date="-5y", end_date="-1y").strftime("%Y-%m-%d %H:%M:%S"),
            gen.date_time_between(start_date="-1y", end_date="+1y").strftime("%Y-%m-%d %H:%M:%S"),
        ),
        "JN": gen.json,
        "XM": gen.xml,
        "UT": gen.uuid4,
        "CO": lambda: gen.text(max_nb_chars=200),
        "LOB": lambda: gen.binary(100).hex(),
    }


class Matcher:
    """Resolves column names and types to data generator callables.

    Holds the keyword map and type maps built from a specific DataGenerator
    implementation. Call match_column_bq / match_column_td to resolve.
    """

    def __init__(self, gen: DataGenerator) -> None:
        self._gen = gen
        self._keyword_map = _build_column_keyword_map(gen)
        self._bq_type_map = _build_bq_type_map(gen)
        self._td_type_map = _build_td_type_map(gen)

    def _match_column(
        self, col_name: str, type_map: dict[str, Callable[[], Any]], db_type: str
    ) -> Callable[[], Any]:
        lower = col_name.lower()
        for pattern, gen_fn in self._keyword_map:
            if re.search(pattern, lower):
                return gen_fn
        return type_map.get(db_type, self._gen.word)

    def match_column_bq(self, col_name: str, bq_type: str) -> Callable[[], Any]:
        return self._match_column(col_name, self._bq_type_map, bq_type.upper())

    def match_column_td(self, col_name: str, td_type: str) -> Callable[[], Any]:
        return self._match_column(col_name, self._td_type_map, td_type.strip())


# ---------------------------------------------------------------------------
# Module-level default (lazy initialisation).
# Call set_generator() at startup to plug in your DataGenerator implementation.
# ---------------------------------------------------------------------------

_matcher: Matcher | None = None


def set_generator(gen: DataGenerator) -> None:
    """Set the module-level DataGenerator used by match_column_bq / match_column_td."""
    global _matcher
    _matcher = Matcher(gen)


def match_column_bq(col_name: str, bq_type: str) -> Callable[[], Any]:
    if _matcher is None:
        raise RuntimeError("Generator not initialised. Call set_generator() first.")
    return _matcher.match_column_bq(col_name, bq_type)


def match_column_td(col_name: str, td_type: str) -> Callable[[], Any]:
    if _matcher is None:
        raise RuntimeError("Generator not initialised. Call set_generator() first.")
    return _matcher.match_column_td(col_name, td_type)


# ---------------------------------------------------------------------------
# Constants and helpers (unchanged)
# ---------------------------------------------------------------------------

INLINE_TYPES = frozenset(
    {
        "TS",
        "OD",
        "TD",
        "TZ",
        "AT",
        "DA",
        "YR",
        "MO",
        "DY",
        "HR",
        "MI",
        "SC",
        "DM",
        "DV",
        "FD",
        "FS",
        "FT",
        "FY",
        "PD",
        "PS",
    }
)


def _format_ts(value: Any) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            return value.replace("T", " ").split(".")[0].split("+")[0].split("Z")[0]
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _format_date(value: Any) -> str:
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return value.split("T")[0] if isinstance(value, str) else str(value)


def _format_time(value: Any) -> str:
    return value.strftime("%H:%M:%S") if isinstance(value, (dt_time, datetime)) else str(value)


def cast_td_value(col_name: str, td_type: str, value: Any) -> str:
    if td_type in ("TS", "OD", "TD", "TZ"):
        return f"CAST('{_format_ts(value)}' AS TIMESTAMP(0))"
    if td_type == "DA":
        return f"DATE '{_format_date(value)}'"
    if td_type == "AT":
        return f"CAST('{_format_time(value)}' AS TIME(0))"
    if td_type == "PD":
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError(f"PD value must be a 2-tuple of dates, got {type(value).__name__}")
        return f"PERIOD(DATE '{value[0]}', DATE '{value[1]}')"
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
