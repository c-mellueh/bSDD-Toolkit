"""
Tests for the SettingsWidget module (tool/settings_widget.py).

Covers add_page_to_toolbox, get_page_dict, and get_accept_functions without
opening a real dialog.
"""
from __future__ import annotations

import pytest
from bsdd_gui.tool import SettingsWidget


@pytest.fixture(autouse=True)
def _clear_settings_state():
    """Snapshot and restore page_dict / accept_functions around each test."""
    props = SettingsWidget.get_properties()
    old_page_dict = dict(props.page_dict)
    old_accept = list(props.accept_functions)
    props.page_dict.clear()
    props.accept_functions.clear()
    yield
    props.page_dict.clear()
    props.page_dict.update(old_page_dict)
    props.accept_functions.clear()
    props.accept_functions.extend(old_accept)


class TestAddPageToToolbox:
    def test_adds_page_name_to_dict(self):
        SettingsWidget.add_page_to_toolbox(lambda: None, "page_general", lambda: None)
        assert "page_general" in SettingsWidget.get_page_dict()

    def test_widget_function_stored_under_page_name(self):
        def wf():
            return None
        SettingsWidget.add_page_to_toolbox(wf, "page_general", lambda: None)
        assert wf in SettingsWidget.get_page_dict()["page_general"]

    def test_accept_function_is_stored(self):
        def af():
            return None
        SettingsWidget.add_page_to_toolbox(lambda: None, "page_general", af)
        assert af in SettingsWidget.get_accept_functions()

    def test_multiple_entries_for_same_page(self):
        wf1, wf2 = lambda: None, lambda: None
        SettingsWidget.add_page_to_toolbox(wf1, "page_general", lambda: None)
        SettingsWidget.add_page_to_toolbox(wf2, "page_general", lambda: None)
        assert len(SettingsWidget.get_page_dict()["page_general"]) == 2

    def test_different_pages_stored_separately(self):
        SettingsWidget.add_page_to_toolbox(lambda: None, "page_a", lambda: None)
        SettingsWidget.add_page_to_toolbox(lambda: None, "page_b", lambda: None)
        assert "page_a" in SettingsWidget.get_page_dict()
        assert "page_b" in SettingsWidget.get_page_dict()
