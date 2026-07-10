"""Tests for matching module."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from src.matching import (
    INLINE_TYPES,
    _format_date,
    _format_time,
    _format_ts,
    cast_td_value,
    ident,
    match_column_bq,
    match_column_td,
)


class TestIdent:
    def test_valid_with_numbers(self):
        assert ident("table123") == "table123"

    def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            ident("my table")

    def test_rejects_special_chars(self):
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            ident("table; DROP TABLE x")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            ident("")


class TestMatchColumnBQ:
    def test_name_pattern_matches_first_name(self):
        gen = match_column_bq("first_name", "STRING")
        result = gen()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_name_pattern_matches_email(self):
        gen = match_column_bq("email", "STRING")
        result = gen()
        assert "@" in result

    def test_price_pattern_matches(self):
        gen = match_column_bq("price", "NUMERIC")
        result = gen()
        assert isinstance(result, float)

    def test_fallback_to_type_for_unknown_name(self):
        gen = match_column_bq("xyz_unknown", "INTEGER")
        result = gen()
        assert isinstance(result, int)

    def test_fallback_to_word_for_unknown_type(self):
        gen = match_column_bq("xyz_unknown", "UNKNOWN_TYPE")
        result = gen()
        assert isinstance(result, str)


class TestMatchColumnTD:
    def test_name_pattern_matches_first_name(self):
        gen = match_column_td("first_name", "CV")
        result = gen()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_integer_type_code(self):
        gen = match_column_td("some_id", "I")
        result = gen()
        assert isinstance(result, int)

    def test_decimal_type_code(self):
        gen = match_column_td("amount", "D")
        result = gen()
        assert isinstance(result, float)

    def test_interval_passthrough(self):
        gen = match_column_td("duration", "DY")
        result = gen()
        assert isinstance(result, str)
        assert "INTERVAL" in result

    def test_period_date_type(self):
        gen = match_column_td("valid_period", "PD")
        result = gen()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_fallback_to_word_for_unknown_type(self):
        gen = match_column_td("xyz_unknown", "ZZ")
        result = gen()
        assert isinstance(result, str)


class TestInlineTypes:
    def test_inline_types_contains_expected_codes(self):
        for code in ("TS", "OD", "TD", "TZ", "AT", "DA", "DY", "PD", "PS"):
            assert code in INLINE_TYPES

    def test_inline_types_excludes_parametrized_codes(self):
        for code in ("CV", "CF", "I", "I1", "D", "F", "N"):
            assert code not in INLINE_TYPES


class TestFormatTs:
    def test_datetime_without_tz(self):
        dt = datetime(2024, 6, 15, 10, 30, 0)
        assert _format_ts(dt) == "2024-06-15 10:30:00"

    def test_datetime_with_utc_tz(self):
        dt = datetime(2024, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
        assert _format_ts(dt) == "2024-06-15 10:30:00"

    def test_iso_string_with_microseconds(self):
        assert _format_ts("2024-01-15T10:30:00.123456") == "2024-01-15 10:30:00"

    def test_iso_string_with_z(self):
        assert _format_ts("2024-01-15T10:30:00Z") == "2024-01-15 10:30:00"

    def test_iso_string_with_offset(self):
        result = _format_ts("2024-01-15T10:30:00+05:00")
        assert "2024-01-15 05:30:00" in result


class TestFormatDate:
    def test_date_object(self):
        d = date(2024, 6, 15)
        assert _format_date(d) == "2024-06-15"

    def test_iso_string(self):
        assert _format_date("2024-06-15") == "2024-06-15"

    def test_datetime_string_extracts_date(self):
        assert _format_date("2024-06-15T10:30:00") == "2024-06-15"


class TestFormatTime:
    def test_time_object(self):
        from datetime import time as dt_time
        t = dt_time(10, 30, 0)
        assert _format_time(t) == "10:30:00"

    def test_datetime_object(self):
        dt = datetime(2024, 6, 15, 14, 30, 0)
        assert _format_time(dt) == "14:30:00"


class TestCastTdValue:
    def test_timestamp_with_microseconds(self):
        result = cast_td_value("col_ts", "TS", "2024-01-15T10:30:00.123456")
        assert result == "CAST('2024-01-15 10:30:00' AS TIMESTAMP(0))"

    def test_timestamp_with_timezone(self):
        result = cast_td_value("col_ts", "TS", "2024-01-15T10:30:00+05:00")
        assert "2024-01-15 05:30:00" in result

    def test_timestamp_with_z_suffix(self):
        result = cast_td_value("col_ts", "TS", "2024-01-15T10:30:00Z")
        assert result == "CAST('2024-01-15 10:30:00' AS TIMESTAMP(0))"

    def test_interval_passthrough(self):
        result = cast_td_value("col_int", "DY", "INTERVAL '1' DAY")
        assert result == "INTERVAL '1' DAY"

    def test_period_date_cast(self):
        result = cast_td_value("col_pd", "PD", ("2024-01-01", "2024-12-31"))
        assert "PERIOD(DATE" in result

    def test_period_timestamp_cast(self):
        result = cast_td_value("col_pt", "PS", ("2024-01-01 00:00:00", "2024-12-31 23:59:59"))
        assert "PERIOD(TIMESTAMP" in result

    def test_pd_rejects_wrong_type(self):
        with pytest.raises(ValueError, match="PD value must be a 2-tuple"):
            cast_td_value("col", "PD", "not-a-tuple")

    def test_ps_rejects_wrong_type(self):
        with pytest.raises(ValueError, match="PS value must be a 2-tuple"):
            cast_td_value("col", "PS", [1, 2])
