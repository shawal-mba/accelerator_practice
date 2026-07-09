"""Tests for synth_data common logic and schema definitions."""

from __future__ import annotations

import pytest

from lib.matching import (
    _ident,
    cast_td_value,
    match_column_bq,
    match_column_td,
)
from lib.test_schema import BQ_TEST_TABLES, FK_MAP, SEED_ORDER, TD_TEST_TABLES, _make_schema_field


class TestIdent:
    def test_valid_identifier(self):
        assert _ident("my_table") == "my_table"

    def test_valid_with_numbers(self):
        assert _ident("table123") == "table123"

    def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            _ident("my table")

    def test_rejects_special_chars(self):
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            _ident("table; DROP TABLE x")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            _ident("")


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

    def test_name_pattern_matches_email(self):
        gen = match_column_td("email", "CV")
        result = gen()
        assert "@" in result

    def test_price_pattern_matches(self):
        gen = match_column_td("price", "D")
        result = gen()
        assert isinstance(result, float)

    def test_fallback_to_type_for_unknown_name(self):
        gen = match_column_td("xyz_unknown", "I")
        result = gen()
        assert isinstance(result, int)

    def test_fallback_to_word_for_unknown_type(self):
        gen = match_column_td("xyz_unknown", "ZZ")
        result = gen()
        assert isinstance(result, str)


class TestCastTdValue:
    def test_timestamp_cast(self):
        result = cast_td_value("col_ts", "TS", "2024-01-15 10:30:00")
        assert "CAST(" in result
        assert "TIMESTAMP" in result

    def test_interval_passthrough(self):
        result = cast_td_value("col_int", "DY", "INTERVAL '1' DAY")
        assert result == "INTERVAL '1' DAY"

    def test_period_date_cast(self):
        result = cast_td_value("col_pd", "PD", ("2024-01-01", "2024-12-31"))
        assert "PERIOD(DATE" in result

    def test_period_timestamp_cast(self):
        result = cast_td_value("col_pt", "PS", ("2024-01-01 00:00:00", "2024-12-31 23:59:59"))
        assert "PERIOD(TIMESTAMP" in result

    def test_default_str_cast(self):
        result = cast_td_value("col_var", "CV", "hello")
        assert result == "hello"

    def test_pd_rejects_wrong_type(self):
        with pytest.raises(ValueError, match="PD value must be a 2-tuple"):
            cast_td_value("col", "PD", "not-a-tuple")

    def test_ps_rejects_wrong_type(self):
        with pytest.raises(ValueError, match="PS value must be a 2-tuple"):
            cast_td_value("col", "PS", [1, 2])


class TestMakeSchemaField:
    def test_basic_field(self):
        field = _make_schema_field({"name": "id", "type": "INTEGER", "mode": "REQUIRED"})
        assert field.name == "id"
        assert field.field_type == "INTEGER"
        assert field.mode == "REQUIRED"

    def test_nested_record(self):
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
        bq_ids = {t["name"] for t in BQ_TEST_TABLES}
        order_ids = {name for name, _ in SEED_ORDER}
        assert bq_ids <= order_ids

    def test_fk_map_points_to_valid_tables(self):
        table_ids = {t["name"] for t in BQ_TEST_TABLES}
        for child, fks in FK_MAP.items():
            assert child in table_ids
            for _child_col, (parent_table, _parent_col) in fks.items():
                assert parent_table in table_ids

    def test_parents_before_children_in_seed_order(self):
        order = [name for name, _ in SEED_ORDER]
        assert order.index("test_products") < order.index("test_order_items")
        assert order.index("test_customers") < order.index("test_orders")
        assert order.index("test_orders") < order.index("test_order_items")


class TestTdSchema:
    def test_seed_order_covers_all_td_tables(self):
        td_names = {t[0] for t in TD_TEST_TABLES}
        order_names = {name for name, _ in SEED_ORDER}
        assert td_names <= order_names

    def test_fk_map_points_to_valid_tables(self):
        table_names = {t[0] for t in TD_TEST_TABLES}
        for child, fks in FK_MAP.items():
            assert child in table_names
            for _child_col, (parent_table, _parent_col) in fks.items():
                assert parent_table in table_names
