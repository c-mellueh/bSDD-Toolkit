"""
Tests for the ClassEditorWidget module (tool/class_editor_widget.py).

Covers the pure validators that do not require a live Qt dialog.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from bsdd_json.models import BsddClass, BsddDictionary

from bsdd_gui.tool import ClassEditorWidget


def _make_dict(*classes: BsddClass) -> BsddDictionary:
    d = BsddDictionary(
        OrganizationCode="TST",
        DictionaryCode="D",
        DictionaryVersion="1.0",
        LanguageIsoCode="en-GB",
        LanguageOnly=False,
        UseOwnUri=False,
    )
    d.Classes.extend(classes)
    return d


def _widget_for(bsdd_class: BsddClass) -> MagicMock:
    w = MagicMock()
    w.bsdd_data = bsdd_class
    return w


# ---------------------------------------------------------------------------
# is_code_valid
# ---------------------------------------------------------------------------


class TestIsCodeValid:
    def test_empty_code_is_invalid(self):
        cls = BsddClass(Code="A", Name="A")
        d = _make_dict(cls)
        assert ClassEditorWidget.is_code_valid("", _widget_for(cls), d) is False

    def test_unique_code_is_valid(self):
        cls = BsddClass(Code="A", Name="A")
        d = _make_dict(cls)
        assert ClassEditorWidget.is_code_valid("B", _widget_for(cls), d) is True

    def test_same_code_as_self_is_valid(self):
        cls = BsddClass(Code="A", Name="A")
        d = _make_dict(cls)
        assert ClassEditorWidget.is_code_valid("A", _widget_for(cls), d) is True

    def test_code_used_by_other_class_is_invalid(self):
        cls1 = BsddClass(Code="A", Name="A")
        cls2 = BsddClass(Code="B", Name="B")
        d = _make_dict(cls1, cls2)
        # Editing cls1 but trying to use cls2's code
        assert ClassEditorWidget.is_code_valid("B", _widget_for(cls1), d) is False


# ---------------------------------------------------------------------------
# is_name_valid
# ---------------------------------------------------------------------------


class TestIsNameValid:
    def test_nonempty_name_is_valid(self):
        assert ClassEditorWidget.is_name_valid("Wall", None, None) is True

    def test_empty_name_is_invalid(self):
        assert ClassEditorWidget.is_name_valid("", None, None) is False

    def test_whitespace_only_is_invalid(self):
        assert ClassEditorWidget.is_name_valid("   ", None, None) is False
