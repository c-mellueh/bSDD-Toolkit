"""
Tests for the GroupOfProperties module (tool/group_of_properties.py).

Covers the pure state-management helpers that do not require a live Qt widget.
"""

from __future__ import annotations

import pytest
from bsdd_json.models import BsddClass, BsddClassProperty

from bsdd_gui.tool import GroupOfProperties
from bsdd_gui.tool.group_of_properties import GopClassView


# ---------------------------------------------------------------------------
# Fixture: restore active class/property state after each test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_active_state():
    yield
    GroupOfProperties.set_active_class(None)
    GroupOfProperties.set_active_property(None)


# ---------------------------------------------------------------------------
# generate_pset_name
# ---------------------------------------------------------------------------


class TestGeneratePsetName:
    def test_returns_class_name(self):
        cls = BsddClass(Code="C", Name="MyClass")
        assert GroupOfProperties.generate_pset_name(cls) == "MyClass"

    def test_returns_empty_string_for_none(self):
        assert GroupOfProperties.generate_pset_name(None) == ""


# ---------------------------------------------------------------------------
# get_active_class / set_active_class
# ---------------------------------------------------------------------------


class TestActiveClass:
    def test_default_active_class_is_none(self):
        GroupOfProperties.set_active_class(None)
        assert GroupOfProperties.get_active_class() is None

    def test_set_and_get_active_class(self):
        cls = BsddClass(Code="A", Name="A")
        GroupOfProperties.set_active_class(cls)
        assert GroupOfProperties.get_active_class() is cls


# ---------------------------------------------------------------------------
# get_active_property / set_active_property
# ---------------------------------------------------------------------------


class TestActiveProperty:
    def test_default_active_property_is_none(self):
        GroupOfProperties.set_active_property(None)
        assert GroupOfProperties.get_active_property() is None

    def test_set_and_get_active_property(self):
        prop = BsddClassProperty(Code="P", PropertySet="S", PropertyCode="X")
        GroupOfProperties.set_active_property(prop)
        assert GroupOfProperties.get_active_property() is prop


# ---------------------------------------------------------------------------
# GopClassView.get_allowed_class_types
# ---------------------------------------------------------------------------


class TestGopClassViewAllowedClassTypes:
    def test_contains_group_of_properties(self):
        types = GopClassView.get_allowed_class_types()
        assert "GroupOfProperties" in types

    def test_returns_list(self):
        assert isinstance(GopClassView.get_allowed_class_types(), list)
