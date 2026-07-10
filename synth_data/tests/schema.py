"""Tests for schema definitions."""

from __future__ import annotations

import pytest

from src.test_schema import BQ_TEST_TABLES, FK_MAP, SEED_ORDER, TD_TEST_TABLES, _make_schema_field


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
        assert order.index("customers") < order.index("customer_accounts")
        assert order.index("customers") < order.index("invoices")
        assert order.index("customer_accounts") < order.index("payments")
        assert order.index("invoices") < order.index("invoice_items")


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
