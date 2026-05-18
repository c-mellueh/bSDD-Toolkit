"""
Tests for the Plugins module (tool/plugins.py).

Covers the helpers that inspect the bsdd_gui.plugins package structure.
These tests do not activate or deactivate any plugin.
"""
from __future__ import annotations

from bsdd_gui.tool import Plugins


class TestGetAvailablePlugins:
    def test_returns_list(self):
        plugins = Plugins.get_available_plugins()
        assert isinstance(plugins, list)

    def test_graph_viewer_is_available(self):
        plugins = Plugins.get_available_plugins()
        assert "graph_viewer" in plugins

    def test_result_is_sorted(self):
        plugins = Plugins.get_available_plugins()
        assert plugins == sorted(plugins)


class TestGetFriendlyName:
    def test_returns_string_for_graph_viewer(self):
        name = Plugins.get_friendly_name("graph_viewer")
        assert isinstance(name, str)

    def test_friendly_name_is_not_empty(self):
        name = Plugins.get_friendly_name("graph_viewer")
        assert name  # truthy / non-empty


class TestGetDescription:
    def test_returns_string_for_graph_viewer(self):
        desc = Plugins.get_description("graph_viewer")
        assert isinstance(desc, str)
