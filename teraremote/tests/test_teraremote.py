from __future__ import annotations

from teraremote.seed import _cast_value, _match_column
from teraremote.test_schema import FK_MAP, SEED_ORDER, TEST_TABLES


class TestMatchColumn:
    def test_name_pattern_matches_first_name(self):
        gen = _match_column("first_name", "CV")
        result = gen()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_name_pattern_matches_email(self):
        gen = _match_column("email", "CV")
        result = gen()
        assert "@" in result

    def test_price_pattern_matches(self):
        gen = _match_column("price", "D")
        result = gen()
        assert isinstance(result, float)

    def test_fallback_to_type_for_unknown_name(self):
        gen = _match_column("xyz_unknown", "I")
        result = gen()
        assert isinstance(result, int)

    def test_fallback_to_word_for_unknown_type(self):
        gen = _match_column("xyz_unknown", "ZZ")
        result = gen()
        assert isinstance(result, str)


class TestCastValue:
    def test_timestamp_cast(self):
        result = _cast_value("col_ts", "TS", "2024-01-15 10:30:00")
        assert "CAST(" in result
        assert "TIMESTAMP" in result

    def test_interval_passthrough(self):
        result = _cast_value("col_int", "DY", "INTERVAL '1' DAY")
        assert result == "INTERVAL '1' DAY"

    def test_period_date_cast(self):
        result = _cast_value("col_pd", "PD", ("2024-01-01", "2024-12-31"))
        assert "PERIOD(DATE" in result

    def test_period_timestamp_cast(self):
        result = _cast_value("col_pt", "PS", ("2024-01-01 00:00:00", "2024-12-31 23:59:59"))
        assert "PERIOD(TIMESTAMP" in result

    def test_default_str_cast(self):
        result = _cast_value("col_var", "CV", "hello")
        assert result == "hello"


class TestTestSchema:
    def test_seed_order_has_all_tables(self):
        table_names = [t[0] for t in TEST_TABLES]
        for table_name, _ in SEED_ORDER:
            assert table_name in table_names

    def test_fk_map_points_to_valid_tables(self):
        table_names = {t[0] for t in TEST_TABLES}
        for child, fks in FK_MAP.items():
            assert child in table_names
            for _child_col, (parent_table, _parent_col) in fks.items():
                assert parent_table in table_names

    def test_parents_before_children_in_seed_order(self):
        order = [name for name, _ in SEED_ORDER]
        assert order.index("test_products") < order.index("test_order_items")
        assert order.index("test_customers") < order.index("test_orders")
        assert order.index("test_orders") < order.index("test_order_items")
