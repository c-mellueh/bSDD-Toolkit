"""
Tests for the Util module (tool/util.py).

Covers the pure-Python methods that do not require a running Qt UI.
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt

from bsdd_gui.tool import Util


# ---------------------------------------------------------------------------
# 1. get_unique_name
# ---------------------------------------------------------------------------


class TestGetUniqueName:
    def test_returns_base_name_when_not_in_list(self):
        assert Util.get_unique_name("Wall", []) == "Wall"

    def test_appends_index_when_name_exists(self):
        result = Util.get_unique_name("Wall", ["Wall"])
        assert result == "Wall-2"

    def test_increments_index_until_unique(self):
        existing = ["Wall", "Wall-2", "Wall-3"]
        assert Util.get_unique_name("Wall", existing) == "Wall-4"

    def test_slugify_flag_applies_to_base(self):
        result = Util.get_unique_name("My Wall", [], slugify=True)
        # slugify should produce lowercase-hyphenated form without spaces
        assert " " not in result

    def test_slugify_flag_applies_to_generated_name(self):
        result = Util.get_unique_name("My Wall", ["My Wall"], slugify=True)
        assert " " not in result


# ---------------------------------------------------------------------------
# 2. transform_guid
# ---------------------------------------------------------------------------


class TestTransformGuid:
    def test_adds_zero_width_after_uppercase(self):
        result = Util.transform_guid("ABC", add_zero_width=True)
        # each uppercase letter should be followed by U+200B
        assert "\u200b" in result
        assert result.count("\u200b") == 3  # A, B, C each get one

    def test_no_zero_width_returns_original(self):
        guid = "ABCdef123"
        assert Util.transform_guid(guid, add_zero_width=False) == guid

    def test_lowercase_letters_not_affected(self):
        result = Util.transform_guid("abc", add_zero_width=True)
        assert "\u200b" not in result


# ---------------------------------------------------------------------------
# 3. checkstate_to_bool / bool_to_checkstate
# ---------------------------------------------------------------------------


class TestCheckstateConversions:
    def test_checked_is_true(self):
        assert Util.checkstate_to_bool(Qt.CheckState.Checked) is True

    def test_unchecked_is_false(self):
        assert Util.checkstate_to_bool(Qt.CheckState.Unchecked) is False

    def test_true_maps_to_checked(self):
        assert Util.bool_to_checkstate(True) == Qt.CheckState.Checked

    def test_false_maps_to_unchecked(self):
        assert Util.bool_to_checkstate(False) == Qt.CheckState.Unchecked

    def test_roundtrip_true(self):
        assert Util.checkstate_to_bool(Util.bool_to_checkstate(True)) is True

    def test_roundtrip_false(self):
        assert Util.checkstate_to_bool(Util.bool_to_checkstate(False)) is False


# ---------------------------------------------------------------------------
# 4. create_directory
# ---------------------------------------------------------------------------


class TestCreateDirectory:
    def test_creates_nested_directory(self, tmp_path):
        target = tmp_path / "a" / "b" / "c"
        Util.create_directory(str(target))
        assert target.exists()

    def test_existing_directory_is_not_an_error(self, tmp_path):
        Util.create_directory(str(tmp_path))  # already exists
        assert tmp_path.exists()


# ---------------------------------------------------------------------------
# 5. create_tempfile
# ---------------------------------------------------------------------------


class TestCreateTempfile:
    def test_returns_string_path(self):
        path = Util.create_tempfile()
        assert isinstance(path, str)

    def test_custom_suffix(self):
        path = Util.create_tempfile(suffix=".json")
        assert path.endswith(".json")

    def test_timestamp_prefix(self):
        path = Util.create_tempfile(add_timestamp=True)
        filename = os.path.basename(path)
        # Timestamp format: YYYY-MM-DD-HH-MM-SS_
        import re

        assert re.match(r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_", filename)
