"""
Tests for window geometry persistence (tool/util.py) and the BaseWidget hooks.

Appdata is redirected to a temp folder so real user configuration is never
touched.
"""

from __future__ import annotations

import pytest

from bsdd_gui.presets.ui_presets import BaseWindow
from bsdd_gui.tool.appdata import Appdata
from bsdd_gui.tool.util import Util


@pytest.fixture()
def appdata(tmp_path, monkeypatch):
    ini = str(tmp_path / "config.ini")
    monkeypatch.setattr(Appdata, "get_ini_path", classmethod(lambda cls: ini))
    monkeypatch.setattr(Appdata, "get_appdata_folder", classmethod(lambda cls: str(tmp_path)))
    return Appdata


class TestGeometryRoundTrip:
    def test_save_and_restore(self, qapp, appdata):
        window = BaseWindow()
        window.resize(311, 222)
        Util.save_window_geometry(window)

        other = BaseWindow()
        assert Util.restore_window_geometry(other) is True
        assert (other.width(), other.height()) == (311, 222)
        window.deleteLater()
        other.deleteLater()

    def test_restore_without_saved_value(self, qapp, appdata):
        window = BaseWindow()
        assert Util.restore_window_geometry(window) is False
        window.deleteLater()

    def test_geometry_saved_per_class_name(self, qapp, appdata):
        window = BaseWindow()
        window.resize(300, 200)
        Util.save_window_geometry(window)
        value = appdata.get_string_setting("window_geometry", "BaseWindow")
        assert value

    def test_show_hide_persists_geometry(self, qapp, appdata):
        window = BaseWindow()
        window.show()
        window.resize(333, 244)
        window.hide()

        other = BaseWindow()
        other.show()
        assert (other.width(), other.height()) == (333, 244)
        other.hide()
        window.deleteLater()
        other.deleteLater()


class TestClampToScreen:
    def test_oversized_window_is_clamped(self, qapp, appdata):
        window = BaseWindow()
        window.resize(100_000, 100_000)
        Util.clamp_to_screen(window)
        available = window.screen().availableGeometry()
        assert window.width() <= available.width()
        assert window.height() <= available.height()
        window.deleteLater()
