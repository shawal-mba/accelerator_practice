"""Tests for synth_data common logic and schema definitions."""

from __future__ import annotations

import pytest

from lib.fk import topo_sort
from lib.matching import (
    cast_td_value,
    ident,
    match_column_bq,
)
from lib.test_schema import BQ_TEST_TABLES, FK_MAP, SEED_ORDER, TD_TEST_TABLES, _make_schema_field


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


class TestMakeSchemaField:
    def test_basic_field(self):
        """A simple dict should convert to a BigQuery SchemaField with correct attributes."""
        field = _make_schema_field({"name": "id", "type": "INTEGER", "mode": "REQUIRED"})
        assert field.name == "id"
        assert field.field_type == "INTEGER"
        assert field.mode == "REQUIRED"

    def test_nested_record(self):
        """RECORD fields with nested sub-fields should produce a SchemaField tree."""
        field = _make_schema_field(
            {
                "name": "address",
                "type": "RECORD",
                "mode": "NULLABLE",
                "fields": [
                    {"name": "street", "type": "STRING", "mode": "NULLABLE"},
                ],
            }
        )
        assert field.name == "address"
        assert field.field_type == "RECORD"
        assert len(field.fields) == 1
        assert field.fields[0].name == "street"


class TestBqSchema:
    def test_seed_order_has_all_tables(self):
        """Every BQ test table must appear in SEED_ORDER or it will never be seeded."""
        bq_ids = {t["name"] for t in BQ_TEST_TABLES}
        order_ids = {name for name, _ in SEED_ORDER}
        assert bq_ids <= order_ids

    def test_fk_map_points_to_valid_tables(self):
        """FK_MAP references must point to tables that actually exist in BQ_TEST_TABLES."""
        table_ids = {t["name"] for t in BQ_TEST_TABLES}
        for child, fks in FK_MAP.items():
            assert child in table_ids
            for _child_col, (parent_table, _parent_col) in fks.items():
                assert parent_table in table_ids

    def test_parents_before_children_in_seed_order(self):
        """Parent tables must appear before children in SEED_ORDER for FK resolution."""
        order = [name for name, _ in SEED_ORDER]
        assert order.index("test_products") < order.index("test_order_items")
        assert order.index("test_customers") < order.index("test_orders")
        assert order.index("test_orders") < order.index("test_order_items")


class TestTdSchema:
    def test_seed_order_covers_all_td_tables(self):
        """Every TD test table must appear in SEED_ORDER or it will never be seeded."""
        td_names = {t[0] for t in TD_TEST_TABLES}
        order_names = {name for name, _ in SEED_ORDER}
        assert td_names <= order_names

    def test_fk_map_points_to_valid_tables(self):
        """FK_MAP references must point to tables that actually exist in TD_TEST_TABLES."""
        table_names = {t[0] for t in TD_TEST_TABLES}
        for child, fks in FK_MAP.items():
            assert child in table_names
            for _child_col, (parent_table, _parent_col) in fks.items():
                assert parent_table in table_names


class TestTopoSort:
    def test_parents_before_children(self):
        """Parent tables must come before children in the output."""
        fk_map = {
            "orders": {"customer_id": ("customers", "id")},
            "items": {"order_id": ("orders", "id")},
        }
        result = topo_sort(["customers", "orders", "items"], fk_map)
        assert result.index("customers") < result.index("orders")
        assert result.index("orders") < result.index("items")

    def test_no_fks_preserves_order(self):
        """Tables without FKs should stay in their original order."""
        tables = ["alpha", "beta", "gamma"]
        assert topo_sort(tables, {}) == tables

    def test_ignores_fks_outside_table_set(self):
        """FK references to tables not in the input list are ignored."""
        fk_map = {
            "orders": {"customer_id": ("external_customers", "id")},
        }
        result = topo_sort(["orders", "products"], fk_map)
        assert result == ["orders", "products"]

    def test_cycle_appends_remaining(self):
        """If a cycle exists, remaining tables are appended in original order."""
        fk_map = {
            "a": {"x": ("b", "y")},
            "b": {"x": ("a", "y")},
        }
        result = topo_sort(["a", "b", "c"], fk_map)
        assert "c" in result
        assert len(result) == 3
