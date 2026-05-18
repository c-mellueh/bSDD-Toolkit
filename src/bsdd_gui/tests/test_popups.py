"""
Tests for the Popups module (tool/popups.py).

The _get_path helper wraps QFileDialog but contains pure-Python extension-
appending logic after the dialog call.  QFileDialog is monkeypatched so
no real dialog ever opens.
"""

from __future__ import annotations

from unittest.mock import patch

from bsdd_gui.tool import Popups


def _open(return_value):
    """Context manager that patches QFileDialog.getOpenFileName."""
    return patch(
        "bsdd_gui.tool.popups.QFileDialog.getOpenFileName",
        return_value=return_value,
    )


def _save(return_value):
    """Context manager that patches QFileDialog.getSaveFileName."""
    return patch(
        "bsdd_gui.tool.popups.QFileDialog.getSaveFileName",
        return_value=return_value,
    )


# ---------------------------------------------------------------------------
# _get_path — open mode
# ---------------------------------------------------------------------------


class TestGetPathOpen:
    def test_appends_missing_extension(self):
        with _open(("/dir/file", "JSON Files (*.json)")):
            result = Popups._get_path("json", None, save=False)
        assert result == "/dir/file.json"

    def test_does_not_double_extension(self):
        with _open(("/dir/file.json", "JSON Files (*.json)")):
            result = Popups._get_path("json", None, save=False)
        assert result == "/dir/file.json"
        assert not result.endswith(".json.json")

    def test_extension_check_is_case_insensitive(self):
        with _open(("/dir/FILE.JSON", "JSON Files (*.json)")):
            result = Popups._get_path("json", None, save=False)
        assert result == "/dir/FILE.JSON"

    def test_empty_path_returns_empty(self):
        with _open(("", "")):
            result = Popups._get_path("json", None, save=False)
        assert result == ""

    def test_empty_end_returns_path_as_is(self):
        with _open(("/dir/file", "")):
            result = Popups._get_path("json", None, save=False)
        assert result == "/dir/file"


# ---------------------------------------------------------------------------
# _get_path — save mode
# ---------------------------------------------------------------------------


class TestGetPathSave:
    def test_appends_missing_extension_on_save(self):
        with _save(("/dir/out", "IDS Files (*.ids)")):
            result = Popups._get_path("ids", None, save=True)
        assert result == "/dir/out.ids"

    def test_does_not_double_extension_on_save(self):
        with _save(("/dir/out.ids", "IDS Files (*.ids)")):
            result = Popups._get_path("ids", None, save=True)
        assert result == "/dir/out.ids"


# ---------------------------------------------------------------------------
# _get_path — path pre-processing
# ---------------------------------------------------------------------------


class TestGetPathPreProcessing:
    def test_strips_extension_from_input_path_before_passing_to_dialog(self):
        """The input path's extension is stripped so the dialog starts without it."""
        with _open(("/dir/file.json", "JSON Files (*.json)")) as mock_open:
            Popups._get_path("json", None, path="/dir/file.json", save=False)
        args = mock_open.call_args[0]  # positional: (window, title, path, filter)
        passed_path = args[2]
        assert not passed_path.endswith(".json")

    def test_no_input_path_passes_none_to_dialog(self):
        with _open(("", "")) as mock_open:
            Popups._get_path("json", None, path=None, save=False)
        args = mock_open.call_args[0]
        passed_path = args[2]
        assert passed_path is None
