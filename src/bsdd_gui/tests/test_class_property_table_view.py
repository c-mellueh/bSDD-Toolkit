"""
Tests for the ClassPropertyTableView module (tool/class_property_table_view.py).

Covers the pure-Python helpers that do not require a live Qt table view.
"""

from __future__ import annotations

from bsdd_json.models import BsddClass, BsddClassProperty, BsddAllowedValue

from bsdd_gui.tool import ClassPropertyTableView


def _make_class_with_props(*pset_names: str) -> BsddClass:
    cls = BsddClass(Code="CLS", Name="Class")
    for i, pset in enumerate(pset_names):
        cls.ClassProperties.append(
            BsddClassProperty(Code=f"P{i}", PropertySet=pset, PropertyCode=f"PROP{i}")
        )
    return cls


# ---------------------------------------------------------------------------
# filter_properties_by_pset
# ---------------------------------------------------------------------------


class TestFilterPropertiesByPset:
    def test_returns_matching_properties(self):
        cls = _make_class_with_props("Pset_A", "Pset_B", "Pset_A")
        result = ClassPropertyTableView.filter_properties_by_pset(cls, "Pset_A")
        assert len(result) == 2
        assert all(p.PropertySet == "Pset_A" for p in result)

    def test_returns_empty_for_unknown_pset(self):
        cls = _make_class_with_props("Pset_A")
        assert ClassPropertyTableView.filter_properties_by_pset(cls, "Pset_Z") == []

    def test_returns_empty_for_class_without_properties(self):
        cls = BsddClass(Code="X", Name="X")
        assert ClassPropertyTableView.filter_properties_by_pset(cls, "Pset_A") == []


# ---------------------------------------------------------------------------
# get_allowed_values
# ---------------------------------------------------------------------------


class TestGetAllowedValues:
    def test_empty_allowed_values_returns_empty_string(self):
        cp = BsddClassProperty(Code="P", PropertySet="S", PropertyCode="X")
        assert ClassPropertyTableView.get_allowed_values(cp) == ""

    def test_single_value(self):
        cp = BsddClassProperty(Code="P", PropertySet="S", PropertyCode="X")
        cp.AllowedValues.append(BsddAllowedValue(Code="v1", Value="Value1"))
        assert ClassPropertyTableView.get_allowed_values(cp) == "Value1"

    def test_multiple_values_joined_with_semicolon(self):
        cp = BsddClassProperty(Code="P", PropertySet="S", PropertyCode="X")
        cp.AllowedValues.append(BsddAllowedValue(Code="v1", Value="Alpha"))
        cp.AllowedValues.append(BsddAllowedValue(Code="v2", Value="Beta"))
        assert ClassPropertyTableView.get_allowed_values(cp) == "Alpha; Beta"


# ---------------------------------------------------------------------------
# set_allowed_class_types
# ---------------------------------------------------------------------------


class TestSetAllowedClassTypes:
    def test_stores_provided_types(self):
        ClassPropertyTableView.set_allowed_class_types(["Class", "GroupOfProperties"])
        props = ClassPropertyTableView.get_properties()
        assert "Class" in props.allowed_class_types
        assert "GroupOfProperties" in props.allowed_class_types

    def test_replaces_previous_types(self):
        ClassPropertyTableView.set_allowed_class_types(["Class"])
        ClassPropertyTableView.set_allowed_class_types(["Material"])
        props = ClassPropertyTableView.get_properties()
        assert props.allowed_class_types == ["Material"]
