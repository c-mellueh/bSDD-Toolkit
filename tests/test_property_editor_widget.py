"""
Tests for the PropertyEditorWidget module (tool/property_editor_widget.py).

Covers validators and the generate_virtual_property helper.
The widget parameter is mocked where needed.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from bsdd_json.models import BsddDictionary, BsddProperty

from bsdd_gui.tool import PropertyEditorWidget


def _make_dict() -> BsddDictionary:
    return BsddDictionary(
        OrganizationCode="TST",
        DictionaryCode="D",
        DictionaryVersion="1.0",
        LanguageIsoCode="en-GB",
        LanguageOnly=False,
        UseOwnUri=False,
    )


def _make_prop(code: str) -> BsddProperty:
    return BsddProperty(Code=code, Name=code, DataType="String")


def _widget_for(prop: BsddProperty) -> MagicMock:
    w = MagicMock()
    w.bsdd_data = prop
    return w


# ---------------------------------------------------------------------------
# is_code_valid
# ---------------------------------------------------------------------------

class TestIsCodeValid:
    def test_empty_code_is_invalid(self):
        d = _make_dict()
        prop = _make_prop("P1")
        assert PropertyEditorWidget.is_code_valid("", _widget_for(prop), d) is False

    def test_unique_code_is_valid(self):
        d = _make_dict()
        prop = _make_prop("P1")
        d.Properties.append(prop)
        # P2 does not exist yet
        assert PropertyEditorWidget.is_code_valid("P2", _widget_for(prop), d) is True

    def test_same_code_as_self_is_valid(self):
        d = _make_dict()
        prop = _make_prop("P1")
        d.Properties.append(prop)
        assert PropertyEditorWidget.is_code_valid("P1", _widget_for(prop), d) is True

    def test_code_used_by_other_property_is_invalid(self):
        d = _make_dict()
        prop1 = _make_prop("P1")
        prop2 = _make_prop("P2")
        d.Properties.extend([prop1, prop2])
        # Editing prop1 but trying to use P2's code
        assert PropertyEditorWidget.is_code_valid("P2", _widget_for(prop1), d) is False


# ---------------------------------------------------------------------------
# is_name_valid
# ---------------------------------------------------------------------------

class TestIsNameValid:
    def test_nonempty_name_is_valid(self):
        assert PropertyEditorWidget.is_name_valid("Wall", None) is True

    def test_empty_name_is_invalid(self):
        assert PropertyEditorWidget.is_name_valid("", None) is False


# ---------------------------------------------------------------------------
# is_datatype_valid
# ---------------------------------------------------------------------------

class TestIsDataTypeValid:
    @pytest.mark.parametrize("dt", ["Boolean", "Character", "Integer", "Real", "String", "Time"])
    def test_valid_datatypes(self, dt):
        assert PropertyEditorWidget.is_datatype_valid(dt, None) is True

    def test_invalid_datatype(self):
        assert PropertyEditorWidget.is_datatype_valid("Text", None) is False

    def test_empty_is_invalid(self):
        assert PropertyEditorWidget.is_datatype_valid("", None) is False


# ---------------------------------------------------------------------------
# generate_virtual_property
# ---------------------------------------------------------------------------

class TestGenerateVirtualProperty:
    def test_creates_property_with_default_values(self):
        prop = PropertyEditorWidget.generate_virtual_property("Wall", None)
        assert prop.Code == "Wall"
        assert prop.Name == "Wall"
        assert prop.DataType == "String"

    def test_model_dict_overrides_name(self):
        prop = PropertyEditorWidget.generate_virtual_property("Wall", {"Name": "My Wall"})
        assert prop.Code == "Wall"
        assert prop.Name == "My Wall"

    def test_model_dict_overrides_datatype(self):
        prop = PropertyEditorWidget.generate_virtual_property("Height", {"DataType": "Real"})
        assert prop.DataType == "Real"

    def test_model_dict_code_not_overridden_by_arg(self):
        # Code from model_dict takes precedence only if provided; here we also pass it
        prop = PropertyEditorWidget.generate_virtual_property("Default", {"Code": "Custom"})
        # Code in model_dict wins because it's already set before the "if not in" check
        assert prop.Code == "Custom"
