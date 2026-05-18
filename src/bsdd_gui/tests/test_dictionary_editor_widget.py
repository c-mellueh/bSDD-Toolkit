"""
Tests for the DictionaryEditorWidget module (tool/dictionary_editor_widget.py).

Covers the pure validator class methods that do not require a live Qt widget.
The widget parameter is only used in is_dictionary_uri_valid, so None is
acceptable for all other validators.
"""
from __future__ import annotations

from bsdd_gui.tool import DictionaryEditorWidget


class TestIsDictionaryCodeValid:
    def test_nonempty_string_is_valid(self):
        assert DictionaryEditorWidget.is_dictionary_code_valid("TEST", None) is True

    def test_empty_string_is_invalid(self):
        assert DictionaryEditorWidget.is_dictionary_code_valid("", None) is False

    def test_none_is_invalid(self):
        assert DictionaryEditorWidget.is_dictionary_code_valid(None, None) is False


class TestIsOrgCodeValid:
    def test_nonempty_string_is_valid(self):
        assert DictionaryEditorWidget.is_org_code_valid("ORG", None) is True

    def test_empty_string_is_invalid(self):
        assert DictionaryEditorWidget.is_org_code_valid("", None) is False


class TestIsDictionaryNameValid:
    def test_nonempty_string_is_valid(self):
        assert DictionaryEditorWidget.is_dictionary_name_valid("My Dict", None) is True

    def test_empty_string_is_invalid(self):
        assert DictionaryEditorWidget.is_dictionary_name_valid("", None) is False


class TestIsDictionaryVersionValid:
    def test_major_only(self):
        assert DictionaryEditorWidget.is_dictionary_version_valid("1", None) is True

    def test_major_minor(self):
        assert DictionaryEditorWidget.is_dictionary_version_valid("1.0", None) is True

    def test_major_minor_patch(self):
        assert DictionaryEditorWidget.is_dictionary_version_valid("1.2.3", None) is True

    def test_zero_version(self):
        assert DictionaryEditorWidget.is_dictionary_version_valid("0", None) is True

    def test_leading_zero_on_major_is_invalid(self):
        assert DictionaryEditorWidget.is_dictionary_version_valid("01", None) is False

    def test_empty_is_invalid(self):
        assert DictionaryEditorWidget.is_dictionary_version_valid("", None) is False

    def test_four_parts_is_invalid(self):
        assert DictionaryEditorWidget.is_dictionary_version_valid("1.2.3.4", None) is False

    def test_alpha_chars_invalid(self):
        assert DictionaryEditorWidget.is_dictionary_version_valid("1.0a", None) is False


class TestIsLanguageIsoValid:
    def test_nonempty_code_is_valid(self):
        assert DictionaryEditorWidget.is_language_iso_valid("en-GB", None) is True

    def test_empty_is_invalid(self):
        assert DictionaryEditorWidget.is_language_iso_valid("", None) is False
