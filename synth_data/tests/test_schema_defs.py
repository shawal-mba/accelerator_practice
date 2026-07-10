"""Tests for schema definitions."""

from __future__ import annotations

import pytest

from schemas.schema_loader import load as _load_schema

_KNOWN_ORDER_VIOLATIONS: set[tuple[str, str]] = {
    ("towers", "customer_connections"),
}


@pytest.fixture(params=["1", "2"])
def schema(request):
    return _load_schema(request.param)


class TestMakeSchemaField:
    def test_basic_field(self, schema):
        field = schema._make_schema_field({"name": "id", "type": "INTEGER", "mode": "REQUIRED"})
        assert field.name == "id"
        assert field.field_type == "INTEGER"
        assert field.mode == "REQUIRED"

    def test_nested_record(self, schema):
        field = schema._make_schema_field(
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


class TestSchemaConsistency:
    def test_seed_order_has_all_tables(self, schema):
        bq_ids = {t["name"] for t in schema.BQ_TEST_TABLES}
        td_names = {t[0] for t in schema.TD_TEST_TABLES}
        order_set = {name for name, _ in schema.SEED_ORDER}
        assert bq_ids <= order_set, f"BQ tables missing from SEED_ORDER: {bq_ids - order_set}"
        assert td_names <= order_set, f"TD tables missing from SEED_ORDER: {td_names - order_set}"

    def test_fk_map_points_to_valid_tables(self, schema):
        all_names = {t[0] for t in schema.TD_TEST_TABLES}
        for child, fks in schema.FK_MAP.items():
            assert child in all_names, f"FK child {child!r} not in TD_TEST_TABLES"
            for child_col, (parent, parent_col) in fks.items():
                assert parent in all_names, (
                    f"FK parent {parent!r} (referenced by {child}.{child_col}) "
                    f"not in TD_TEST_TABLES"
                )

    def test_parents_before_children_in_seed_order(self, schema):
        order = {name: i for i, (name, _) in enumerate(schema.SEED_ORDER)}
        for child, fks in schema.FK_MAP.items():
            for _, (parent, _) in fks.items():
                if parent == child:
                    continue
                pair = (parent, child)
                if pair in _KNOWN_ORDER_VIOLATIONS:
                    continue
                assert parent in order, f"Parent {parent!r} not in SEED_ORDER"
                assert child in order, f"Child {child!r} not in SEED_ORDER"
                assert order[parent] < order[child], (
                    f"Parent {parent!r} (pos {order[parent]}) must appear "
                    f"before child {child!r} (pos {order[child]}) in SEED_ORDER"
                )
