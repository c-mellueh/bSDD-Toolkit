"""
Tests for the Appdata module (tool/appdata.py).

All tests redirect the INI file to a temporary directory via monkeypatch so
that real user configuration is never touched.
"""
from __future__ import annotations

import pytest
from bsdd_gui.tool.appdata import Appdata, CustomConfigParser

SECTION = "test_section"


# ---------------------------------------------------------------------------
# Fixture: redirect Appdata to a temp folder
# ---------------------------------------------------------------------------

@pytest.fixture()
def appdata(tmp_path, monkeypatch):
    """Return Appdata with its INI file redirected to *tmp_path*."""
    ini = str(tmp_path / "config.ini")
    monkeypatch.setattr(Appdata, "get_ini_path", classmethod(lambda cls: ini))
    monkeypatch.setattr(
        Appdata, "get_appdata_folder", classmethod(lambda cls: str(tmp_path))
    )
    return Appdata


# ---------------------------------------------------------------------------
# 1. CustomConfigParser
# ---------------------------------------------------------------------------

class TestCustomConfigParser:
    def test_get_returns_none_for_missing_section(self):
        cfg = CustomConfigParser()
        assert cfg.get("no_section", "no_option") is None

    def test_get_returns_none_for_missing_option(self):
        cfg = CustomConfigParser()
        cfg.add_section("s")
        assert cfg.get("s", "missing") is None

    def test_set_and_get_string(self):
        cfg = CustomConfigParser()
        cfg.set("s", "key", "hello")
        # strings are stored with surrounding quotes, get strips them
        assert cfg.get("s", "key") == "hello"

    def test_set_and_get_list(self):
        cfg = CustomConfigParser()
        cfg.set("s", "key", ["a", "b", "c"])
        raw = cfg.get("s", "key")
        assert "a" in raw
        assert "b" in raw
        assert "c" in raw

    def test_getlist_splits_separator(self):
        cfg = CustomConfigParser()
        cfg.set("s", "paths", ["x", "y"])
        result = cfg.getlist("s", "paths")
        assert "x" in result
        assert "y" in result


# ---------------------------------------------------------------------------
# 2. Settings – read / write round-trips
# ---------------------------------------------------------------------------

class TestSettings:
    def test_string_setting_default(self, appdata):
        val = appdata.get_string_setting(SECTION, "missing", default="fallback")
        assert val == "fallback"

    def test_string_setting_roundtrip(self, appdata):
        appdata.set_setting(SECTION, "key", "hello")
        assert appdata.get_string_setting(SECTION, "key") == "hello"

    def test_bool_setting_default_false(self, appdata):
        assert appdata.get_bool_setting(SECTION, "flag", default=False) is False

    def test_bool_setting_roundtrip(self, appdata):
        appdata.set_setting(SECTION, "flag", True)
        assert appdata.get_bool_setting(SECTION, "flag") is True

    def test_int_setting_default(self, appdata):
        assert appdata.get_int_setting(SECTION, "num", default=42) == 42

    def test_int_setting_roundtrip(self, appdata):
        appdata.set_setting(SECTION, "num", 7)
        assert appdata.get_int_setting(SECTION, "num") == 7

    def test_float_setting_default(self, appdata):
        assert appdata.get_float_setting(SECTION, "f", default=3.14) == pytest.approx(3.14)

    def test_float_setting_roundtrip(self, appdata):
        appdata.set_setting(SECTION, "f", 2.718)
        assert appdata.get_float_setting(SECTION, "f") == pytest.approx(2.718)


# ---------------------------------------------------------------------------
# 3. Path management
# ---------------------------------------------------------------------------

class TestPaths:
    def test_get_paths_returns_empty_list_when_not_set(self, appdata):
        assert appdata.get_paths("nonexistent") == []

    def test_add_path_stores_path(self, appdata, tmp_path):
        p = str(tmp_path / "project.json")
        (tmp_path / "project.json").write_text("{}")
        appdata.add_path("recent", p)
        paths = appdata.get_paths("recent")
        import os
        assert os.path.abspath(p) in paths

    def test_add_path_most_recent_first(self, appdata, tmp_path):
        f1 = tmp_path / "a.json"
        f2 = tmp_path / "b.json"
        f1.write_text("{}")
        f2.write_text("{}")
        appdata.add_path("recent", str(f1))
        appdata.add_path("recent", str(f2))
        paths = appdata.get_paths("recent")
        import os
        assert paths[0] == os.path.abspath(str(f2))

    def test_add_path_deduplicates(self, appdata, tmp_path):
        f = tmp_path / "dup.json"
        f.write_text("{}")
        appdata.add_path("recent", str(f))
        appdata.add_path("recent", str(f))
        paths = appdata.get_paths("recent")
        import os
        count = paths.count(os.path.abspath(str(f)))
        assert count == 1

    def test_add_path_respects_max_entries(self, appdata, tmp_path):
        files = []
        for i in range(5):
            f = tmp_path / f"f{i}.json"
            f.write_text("{}")
            files.append(str(f))
        for f in files:
            appdata.add_path("recent", f, max_entries=3)
        paths = appdata.get_paths("recent")
        assert len(paths) == 3
