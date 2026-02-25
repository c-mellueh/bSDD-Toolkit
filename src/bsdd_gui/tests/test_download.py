"""
Tests for the Download module (tool/download.py).

Only the pure-Python helpers are tested here; the threading / HTTP logic
that requires a live bSDD server is out of scope.
"""
from __future__ import annotations

import pytest
from bsdd_gui.tool import Download


# ---------------------------------------------------------------------------
# swap_codes
# ---------------------------------------------------------------------------

class TestSwapCodes:
    def test_renames_key(self):
        d = {"old_key": "value", "other": "x"}
        Download.swap_codes(d, "old_key", "new_key")
        assert "new_key" in d
        assert "old_key" not in d

    def test_preserves_value(self):
        d = {"old_key": 42}
        Download.swap_codes(d, "old_key", "new_key")
        assert d["new_key"] == 42

    def test_does_nothing_when_key_missing(self):
        d = {"other": "x"}
        Download.swap_codes(d, "missing", "new_key")
        assert d == {"other": "x"}

    def test_does_not_affect_other_keys(self):
        d = {"a": 1, "b": 2}
        Download.swap_codes(d, "a", "c")
        assert d["b"] == 2
        assert "a" not in d
        assert d["c"] == 1

    def test_empty_dict_is_no_op(self):
        d = {}
        Download.swap_codes(d, "key", "new")
        assert d == {}

    def test_rename_to_same_name_removes_key(self):
        # swap_codes writes new then pops old; when old == new the key is deleted
        d = {"key": "val"}
        Download.swap_codes(d, "key", "key")
        assert d == {}
