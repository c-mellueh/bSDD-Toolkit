"""
Tests for the MainWindowWidget module (tool/main_window_widget.py).

Covers the pure state-management helpers (active class, pset, property)
and is_console_visible(), which must return a bool on any platform.
"""
from __future__ import annotations

import pytest
from bsdd_json.models import BsddClass, BsddClassProperty

from bsdd_gui.tool import MainWindowWidget


# ---------------------------------------------------------------------------
# Fixture: restore active-state fields after each test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _restore_active_state():
    yield
    props = MainWindowWidget.get_properties()
    props.active_class = None
    props.active_pset = None
    props.active_property = None


# ---------------------------------------------------------------------------
# active_class
# ---------------------------------------------------------------------------

class TestActiveClass:
    def test_default_is_none(self):
        assert MainWindowWidget.get_active_class() is None

    def test_set_and_get(self):
        cls = BsddClass(Code="A", Name="A")
        MainWindowWidget.set_active_class(cls)
        assert MainWindowWidget.get_active_class() is cls

    def test_set_none_clears(self):
        cls = BsddClass(Code="A", Name="A")
        MainWindowWidget.set_active_class(cls)
        MainWindowWidget.set_active_class(None)
        assert MainWindowWidget.get_active_class() is None


# ---------------------------------------------------------------------------
# active_pset
# ---------------------------------------------------------------------------

class TestActivePset:
    def test_set_and_get(self):
        MainWindowWidget.set_active_pset("Pset_A")
        assert MainWindowWidget.get_active_pset() == "Pset_A"

    def test_overwrite(self):
        MainWindowWidget.set_active_pset("Pset_A")
        MainWindowWidget.set_active_pset("Pset_B")
        assert MainWindowWidget.get_active_pset() == "Pset_B"


# ---------------------------------------------------------------------------
# active_property
# ---------------------------------------------------------------------------

class TestActiveProperty:
    def test_set_and_get(self):
        prop = BsddClassProperty(Code="P", PropertySet="S", PropertyCode="X")
        MainWindowWidget.set_active_property(prop)
        assert MainWindowWidget.get_active_property() is prop

    def test_set_none_clears(self):
        prop = BsddClassProperty(Code="P", PropertySet="S", PropertyCode="X")
        MainWindowWidget.set_active_property(prop)
        MainWindowWidget.set_active_property(None)
        assert MainWindowWidget.get_active_property() is None


# ---------------------------------------------------------------------------
# is_console_visible
# ---------------------------------------------------------------------------

class TestIsConsoleVisible:
    def test_returns_bool(self):
        result = MainWindowWidget.is_console_visible()
        assert isinstance(result, bool)
