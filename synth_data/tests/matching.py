"""Tests for matching module."""

from __future__ import annotations

import pytest

from src.matching import (
    cast_td_value,
    ident,
    match_column_bq,
)


class TestIdent:
    def test_valid_with_numbers(self):
        """Identifiers containing digits are valid in SQL."""
        assert ident("table123") == "table123"

    def test_rejects_spaces(self):
        """Spaces are not allowed — would break SQL statements."""
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            ident("my table")

    def test_rejects_special_chars(self):
        """SQL injection via semicolons or other special chars must be blocked."""
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            ident("table; DROP TABLE x")

    def test_rejects_empty(self):
        """Empty strings are not valid identifiers."""
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            ident("")


class TestMatchColumnBQ:
    def test_name_pattern_matches_first_name(self):
        """Column named 'first_name' should use the first_name faker generator."""
        gen = match_column_bq("first_name", "STRING")
        result = gen()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_name_pattern_matches_email(self):
        """Column named 'email' should produce a value containing '@'."""
        gen = match_column_bq("email", "STRING")
        result = gen()
        assert "@" in result

    def test_price_pattern_matches(self):
        """Column named 'price' should produce a float, not a string or int."""
        gen = match_column_bq("price", "NUMERIC")
        result = gen()
        assert isinstance(result, float)

    def test_fallback_to_type_for_unknown_name(self):
        """Unrecognised column name should fall back to the BQ type map (INTEGER -> int)."""
        gen = match_column_bq("xyz_unknown", "INTEGER")
        result = gen()
        assert isinstance(result, int)

    def test_fallback_to_word_for_unknown_type(self):
        """Completely unknown type should fall back to fake.word."""
        gen = match_column_bq("xyz_unknown", "UNKNOWN_TYPE")
        result = gen()
        assert isinstance(result, str)


class TestCastTdValue:
    def test_timestamp_with_microseconds(self):
        """ISO timestamp with microseconds must strip them for Teradata TIMESTAMP(0)."""
        result = cast_td_value("col_ts", "TS", "2024-01-15T10:30:00.123456")
        assert result == "CAST('2024-01-15 10:30:00' AS TIMESTAMP(0))"

    def test_timestamp_with_timezone(self):
        """Timestamp with timezone offset must be converted to UTC before formatting."""
        result = cast_td_value("col_ts", "TS", "2024-01-15T10:30:00+05:00")
        assert "2024-01-15 05:30:00" in result

    def test_timestamp_with_z_suffix(self):
        """Z suffix (UTC) must be stripped and formatted as plain timestamp."""
        result = cast_td_value("col_ts", "TS", "2024-01-15T10:30:00Z")
        assert result == "CAST('2024-01-15 10:30:00' AS TIMESTAMP(0))"

    def test_interval_passthrough(self):
        """INTERVAL values are inline SQL and should pass through unchanged."""
        result = cast_td_value("col_int", "DY", "INTERVAL '1' DAY")
        assert result == "INTERVAL '1' DAY"

    def test_period_date_cast(self):
        """PERIOD(DATE) value must produce a PERIOD(DATE ..., DATE ...) expression."""
        result = cast_td_value("col_pd", "PD", ("2024-01-01", "2024-12-31"))
        assert "PERIOD(DATE" in result

    def test_period_timestamp_cast(self):
        """PERIOD(TIMESTAMP) value must produce a PERIOD(TIMESTAMP...) expression."""
        result = cast_td_value("col_pt", "PS", ("2024-01-01 00:00:00", "2024-12-31 23:59:59"))
        assert "PERIOD(TIMESTAMP" in result

    def test_pd_rejects_wrong_type(self):
        """PERIOD(DATE) must receive a 2-tuple, not a raw string."""
        with pytest.raises(ValueError, match="PD value must be a 2-tuple"):
            cast_td_value("col", "PD", "not-a-tuple")

    def test_ps_rejects_wrong_type(self):
        """PERIOD(TIMESTAMP) must receive a 2-tuple, not a list."""
        with pytest.raises(ValueError, match="PS value must be a 2-tuple"):
            cast_td_value("col", "PS", [1, 2])
