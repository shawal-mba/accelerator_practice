import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable

from faker import Faker

fake = Faker()


@dataclass
class ColumnMeta:
    name: str
    data_type: str
    column_type: str
    is_nullable: bool
    column_length: int | None = None
    decimal_total_digits: int | None = None
    decimal_fractional_digits: int | None = None
    column_format: str = ""
    column_title: str = ""


@dataclass
class FakerStrategy:
    python_type: type
    generate: Callable[..., Any]
    nullable: bool = True


def _parse_decimal_type(data_type: str) -> tuple[int, int]:
    m = re.match(r"DECIMAL\((\d+),(\d+)\)", data_type)
    if m:
        return int(m.group(1)), int(m.group(2))
    return 18, 4


def _parse_varchar_size(data_type: str) -> int:
    m = re.match(r"VARCHAR\((\d+)\)", data_type)
    if m:
        return int(m.group(1))
    m = re.match(r"CHAR\((\d+)\)", data_type)
    if m:
        return int(m.group(1))
    return 100


_SUFFIX_STRATEGIES: dict[str, Callable[[ColumnMeta], FakerStrategy]] = {
    "_amt": lambda c: FakerStrategy(
        python_type=Decimal,
        generate=lambda: fake.pydecimal(
            left_digits=max(1, (c.decimal_total_digits or 18) - (c.decimal_fractional_digits or 4)),
            right_digits=c.decimal_fractional_digits or 4,
            positive=True,
        ),
    ),
    "_cnt": lambda c: FakerStrategy(
        python_type=int,
        generate=lambda: fake.random_int(min=0, max=1000),
    ),
    "_id": lambda c: FakerStrategy(
        python_type=int,
        generate=lambda: fake.random_int(min=1, max=999999999),
    ),
    "_uid": lambda c: FakerStrategy(
        python_type=int,
        generate=lambda: fake.random_int(min=1, max=999999999),
    ),
    "_dttm": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.date_time_between(start_date="-3y", end_date="now").strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    ),
    "_dt": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.date_between(start_date="-3y", end_date="today").strftime(
            "%Y-%m-%d"
        ),
    ),
    "_cd": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.lexify(text="???").upper(),
    ),
    "_nm": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.name(),
    ),
    "_name": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.name(),
    ),
    "_desc": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.sentence(nb_words=6),
    ),
    "_flg": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.random_element(["Y", "N"]),
    ),
    "_flag": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.random_element(["Y", "N"]),
    ),
    "_type": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.random_element(["TYPE_A", "TYPE_B", "TYPE_C"]),
    ),
    "_key": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.uuid4(),
    ),
    "_pct": lambda c: FakerStrategy(
        python_type=Decimal,
        generate=lambda: fake.pydecimal(left_digits=2, right_digits=2, min_value=0, max_value=100),
    ),
    "_val": lambda c: FakerStrategy(
        python_type=int,
        generate=lambda: fake.random_int(min=0, max=99999),
    ),
    "_stat": lambda c: FakerStrategy(
        python_type=str,
        generate=lambda: fake.random_element(["ACTIVE", "INACTIVE", "PENDING"]),
    ),
    "_rt": lambda c: FakerStrategy(
        python_type=Decimal,
        generate=lambda: fake.pydecimal(left_digits=2, right_digits=4, min_value=0, max_value=1),
    ),
}


def _char1_faker(c: ColumnMeta) -> FakerStrategy:
    title_lower = c.column_title.lower()
    name_lower = c.name.lower()
    if "flg" in name_lower or "flag" in name_lower or "ind" in name_lower:
        return FakerStrategy(
            python_type=str,
            generate=lambda: fake.random_element(["Y", "N"]),
        )
    return FakerStrategy(
        python_type=str,
        generate=lambda: fake.lexify(text="?" * (c.column_length or 1)),
    )


def _varchar_faker(c: ColumnMeta) -> FakerStrategy:
    max_len = c.column_length or 100
    name_lower = c.name.lower()
    title_lower = c.column_title.lower()

    if "msisdn" in name_lower or "phone" in name_lower:
        return FakerStrategy(
            python_type=str,
            generate=lambda: fake.msisdn()[:max_len],
        )
    if "email" in name_lower or "mail" in name_lower:
        return FakerStrategy(
            python_type=str,
            generate=lambda: fake.email()[:max_len],
        )
    if "url" in name_lower or "web" in name_lower:
        return FakerStrategy(
            python_type=str,
            generate=lambda: fake.url()[:max_len],
        )
    if "ip" in name_lower and "addr" in name_lower:
        return FakerStrategy(
            python_type=str,
            generate=lambda: fake.ipv4()[:max_len],
        )
    if max_len <= 5:
        return FakerStrategy(
            python_type=str,
            generate=lambda: fake.lexify(text="?" * max_len),
        )
    if max_len <= 20:
        return FakerStrategy(
            python_type=str,
            generate=lambda: fake.pystr(min_chars=1, max_chars=max_len),
        )
    return FakerStrategy(
        python_type=str,
        generate=lambda: fake.text(max_nb_chars=min(max_len, 200)),
    )


def _int_faker(c: ColumnMeta) -> FakerStrategy:
    name_lower = c.name.lower()
    if "batch" in name_lower or "etl" in name_lower:
        return FakerStrategy(
            python_type=int,
            generate=lambda: fake.random_int(min=1, max=999999),
        )
    return FakerStrategy(
        python_type=int,
        generate=lambda: fake.random_int(min=0, max=999999999),
    )


def _bigint_faker(c: ColumnMeta) -> FakerStrategy:
    return FakerStrategy(
        python_type=int,
        generate=lambda: fake.random_int(min=1, max=999999999999),
    )


def _decimal_faker(c: ColumnMeta) -> FakerStrategy:
    p = c.decimal_total_digits or 18
    s = c.decimal_fractional_digits or 4
    left = max(1, p - s)
    name_lower = c.name.lower()

    if "pct" in name_lower or "rate" in name_lower:
        return FakerStrategy(
            python_type=Decimal,
            generate=lambda: fake.pydecimal(left_digits=2, right_digits=2, min_value=0, max_value=100),
        )
    if any(x in name_lower for x in ["amt", "amount", "price", "cost", "revenue", "balance"]):
        return FakerStrategy(
            python_type=Decimal,
            generate=lambda: fake.pydecimal(left_digits=left, right_digits=s, positive=True),
        )
    return FakerStrategy(
        python_type=Decimal,
        generate=lambda: fake.pydecimal(left_digits=left, right_digits=s, positive=True),
    )


def _date_faker(c: ColumnMeta) -> FakerStrategy:
    return FakerStrategy(
        python_type=str,
        generate=lambda: fake.date_between(start_date="-5y", end_date="today").strftime("%Y-%m-%d"),
    )


def _timestamp_faker(c: ColumnMeta) -> FakerStrategy:
    return FakerStrategy(
        python_type=str,
        generate=lambda: fake.date_time_between(start_date="-5y", end_date="now").strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )


def _time_faker(c: ColumnMeta) -> FakerStrategy:
    return FakerStrategy(
        python_type=str,
        generate=lambda: fake.time(),
    )


def _float_faker(c: ColumnMeta) -> FakerStrategy:
    return FakerStrategy(
        python_type=float,
        generate=lambda: fake.pyfloat(min_value=0, max_value=99999),
    )


def _number_faker(c: ColumnMeta) -> FakerStrategy:
    p = c.decimal_total_digits or 18
    s = c.decimal_fractional_digits or 0
    if s > 0:
        return _decimal_faker(c)
    return FakerStrategy(
        python_type=int,
        generate=lambda: fake.random_int(min=0, max=10**min(p, 9)),
    )


def _interval_faker(c: ColumnMeta) -> FakerStrategy:
    return FakerStrategy(
        python_type=int,
        generate=lambda: fake.random_int(min=0, max=1000),
    )


_TYPE_MAP: dict[str, Callable[[ColumnMeta], FakerStrategy]] = {
    "INTEGER": _int_faker,
    "BIGINT": _bigint_faker,
    "SMALLINT": lambda c: FakerStrategy(python_type=int, generate=lambda: fake.random_int(min=0, max=32767)),
    "BYTEINT": lambda c: FakerStrategy(python_type=int, generate=lambda: fake.random_int(min=0, max=127)),
    "FLOAT": _float_faker,
    "DATE": _date_faker,
    "TIME": _time_faker,
    "TIME WITH TIME ZONE": _time_faker,
    "JSON": lambda c: FakerStrategy(python_type=str, generate=lambda: "{}"),
    "XML": lambda c: FakerStrategy(python_type=str, generate=lambda: "<root/>"),
    "DATASET": lambda c: FakerStrategy(python_type=str, generate=lambda: "{}"),
    "INTERVAL YEAR TO MONTH": _interval_faker,
    "INTERVAL SECOND": _interval_faker,
}


def get_faker_strategy(col: ColumnMeta) -> FakerStrategy:
    dt = (col.data_type or "").strip()
    name_lower = col.name.lower()

    for suffix, factory in _SUFFIX_STRATEGIES.items():
        if name_lower.endswith(suffix):
            strategy = factory(col)
            strategy.nullable = col.is_nullable
            return strategy

    if dt.startswith("VARCHAR") or dt.startswith("CHAR"):
        if dt == "CHAR(1)" or (dt.startswith("CHAR") and (col.column_length or 1) == 1):
            strategy = _char1_faker(col)
        else:
            strategy = _varchar_faker(col)
        strategy.nullable = col.is_nullable
        return strategy

    if dt.startswith("DECIMAL"):
        strategy = _decimal_faker(col)
        strategy.nullable = col.is_nullable
        return strategy

    if dt.startswith("TIMESTAMP"):
        strategy = _timestamp_faker(col)
        strategy.nullable = col.is_nullable
        return strategy

    if dt.startswith("NUMBER"):
        strategy = _number_faker(col)
        strategy.nullable = col.is_nullable
        return strategy

    if dt.startswith("INTERVAL"):
        strategy = _interval_faker(col)
        strategy.nullable = col.is_nullable
        return strategy

    if dt in _TYPE_MAP:
        strategy = _TYPE_MAP[dt](col)
        strategy.nullable = col.is_nullable
        return strategy

    if not dt:
        strategy = FakerStrategy(
            python_type=str,
            generate=lambda: fake.pystr(min_chars=1, max_chars=50),
        )
        strategy.nullable = col.is_nullable
        return strategy

    strategy = FakerStrategy(
        python_type=str,
        generate=lambda: fake.pystr(min_chars=1, max_chars=50),
    )
    strategy.nullable = col.is_nullable
    return strategy
