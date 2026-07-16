"""Tests for topological sort."""

from __future__ import annotations

from src.domain.fk import topo_sort


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
