from __future__ import annotations

from bigquery.seed import _match_column
from bigquery.test_schema import FK_MAP, SEED_ORDER, TEST_TABLES, _make_schema_field


class TestMatchColumn:
    def test_name_pattern_matches_first_name(self):
        gen = _match_column("first_name", "STRING")
        result = gen()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_name_pattern_matches_email(self):
        gen = _match_column("email", "STRING")
        result = gen()
        assert "@" in result

    def test_price_pattern_matches(self):
        gen = _match_column("price", "NUMERIC")
        result = gen()
        assert isinstance(result, float)

    def test_fallback_to_type_for_unknown_name(self):
        gen = _match_column("xyz_unknown", "INTEGER")
        result = gen()
        assert isinstance(result, int)

    def test_fallback_to_word_for_unknown_type(self):
        gen = _match_column("xyz_unknown", "UNKNOWN_TYPE")
        result = gen()
        assert isinstance(result, str)


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


class TestTestSchema:
    def test_seed_order_has_all_tables(self):
        table_ids = [t[0] for t in TEST_TABLES]
        for table_id, _ in SEED_ORDER:
            assert table_id in table_ids

    def test_fk_map_points_to_valid_tables(self):
        table_ids = {t[0] for t in TEST_TABLES}
        for child, fks in FK_MAP.items():
            assert child in table_ids
            for _child_col, (parent_table, _parent_col) in fks.items():
                assert parent_table in table_ids

    def test_parents_before_children_in_seed_order(self):
        order = [name for name, _ in SEED_ORDER]
        assert order.index("test_products") < order.index("test_order_items")
        assert order.index("test_customers") < order.index("test_orders")
        assert order.index("test_orders") < order.index("test_order_items")
