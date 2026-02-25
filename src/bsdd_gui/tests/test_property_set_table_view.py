"""
Tests for the PropertySetTableView module (tool/property_set_table_view.py).

Covers the pure-Python property-set state helpers that do not require
a live Qt table view.
"""
from __future__ import annotations

import pytest
from bsdd_json.models import BsddClass, BsddClassProperty

from bsdd_gui.tool import PropertySetTableView


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _class_with_psets(*pset_names: str) -> BsddClass:
    """Build a BsddClass whose ClassProperties span the given pset names."""
    cls = BsddClass(Code="CLS", Name="Class")
    for i, pset in enumerate(pset_names):
        # BsddClassProperty requires exactly one of PropertyCode or PropertyUri
        cls.ClassProperties.append(
            BsddClassProperty(Code=f"CP{i}", PropertySet=pset, PropertyCode=f"PROP{i}")
        )
    return cls


# ---------------------------------------------------------------------------
# Fixture: ensure temporary pset state is clean between tests
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_temp_psets():
    """Wipe all temporary property-set entries before each test."""
    PropertySetTableView.get_properties().temporary_pset.clear()
    yield
    PropertySetTableView.get_properties().temporary_pset.clear()


# ---------------------------------------------------------------------------
# 1. get_temporary_psets
# ---------------------------------------------------------------------------

class TestGetTemporaryPsets:
    def test_returns_empty_list_when_no_temp_psets(self):
        cls = BsddClass(Code="A", Name="A")
        assert PropertySetTableView.get_temporary_psets(cls) == []

    def test_returns_added_pset(self):
        cls = BsddClass(Code="B", Name="B")
        PropertySetTableView.get_properties().temporary_pset["B"] = ["TmpPset"]
        result = PropertySetTableView.get_temporary_psets(cls)
        assert "TmpPset" in result


# ---------------------------------------------------------------------------
# 2. get_pset_names_with_temporary
# ---------------------------------------------------------------------------

class TestGetPsetNamesWithTemporary:
    def test_returns_empty_for_class_without_properties(self):
        cls = BsddClass(Code="E", Name="E")
        assert PropertySetTableView.get_pset_names_with_temporary(cls) == []

    def test_returns_none_for_none_class(self):
        assert PropertySetTableView.get_pset_names_with_temporary(None) == []

    def test_collects_pset_names_from_class_properties(self):
        cls = _class_with_psets("Pset_A", "Pset_B")
        result = PropertySetTableView.get_pset_names_with_temporary(cls)
        assert "Pset_A" in result
        assert "Pset_B" in result

    def test_deduplicates_pset_names(self):
        cls = _class_with_psets("Pset_A", "Pset_A", "Pset_B")
        result = PropertySetTableView.get_pset_names_with_temporary(cls)
        assert result.count("Pset_A") == 1

    def test_includes_temporary_psets(self):
        cls = BsddClass(Code="F", Name="F")
        PropertySetTableView.get_properties().temporary_pset["F"] = ["TmpPset"]
        result = PropertySetTableView.get_pset_names_with_temporary(cls)
        assert "TmpPset" in result

    def test_real_psets_come_before_temporary(self):
        cls = _class_with_psets("RealPset")
        PropertySetTableView.get_properties().temporary_pset["CLS"] = ["TmpPset"]
        result = PropertySetTableView.get_pset_names_with_temporary(cls)
        assert result.index("RealPset") < result.index("TmpPset")
