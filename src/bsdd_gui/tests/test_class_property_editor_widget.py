"""
Tests for the ClassPropertyEditorWidget module (tool/class_property_editor_widget.py).

Covers the pure-Python helpers: create_window_title, get_property_reference,
is_property_reference_valid, create_temporary_property, and set_code.
"""
from __future__ import annotations

from bsdd_json.models import BsddClass, BsddClassProperty, BsddDictionary, BsddProperty

from bsdd_gui.tool import ClassPropertyEditorWidget


def _make_dict(*properties: BsddProperty) -> BsddDictionary:
    d = BsddDictionary(
        OrganizationCode="TST",
        DictionaryCode="D",
        DictionaryVersion="1.0",
        LanguageIsoCode="en-GB",
        LanguageOnly=False,
        UseOwnUri=False,
    )
    d.Properties.extend(properties)
    return d


def _make_cp(code="P1", pset="Pset_A", prop_code="PROP1") -> BsddClassProperty:
    return BsddClassProperty(Code=code, PropertySet=pset, PropertyCode=prop_code)


# ---------------------------------------------------------------------------
# create_window_title
# ---------------------------------------------------------------------------

class TestCreateWindowTitle:
    def test_no_pset_returns_code_only(self):
        cp = BsddClassProperty(Code="P1", PropertyCode="X")
        assert ClassPropertyEditorWidget.create_window_title(cp) == "P1"

    def test_with_pset_returns_pset_and_code(self):
        cp = _make_cp(code="P1", pset="Pset_A")
        result = ClassPropertyEditorWidget.create_window_title(cp)
        assert result == "Pset_A : P1"

    def test_with_parent_class_includes_class_name(self):
        cls = BsddClass(Code="C", Name="MyClass")
        cp = _make_cp(code="P1", pset="Pset_A")
        cp._set_parent(cls)
        result = ClassPropertyEditorWidget.create_window_title(cp)
        assert result == "MyClass : Pset_A : P1"


# ---------------------------------------------------------------------------
# get_property_reference
# ---------------------------------------------------------------------------

class TestGetPropertyReference:
    def test_returns_property_code_when_set(self):
        cp = _make_cp(prop_code="PROP1")
        assert ClassPropertyEditorWidget.get_property_reference(cp) == "PROP1"

    def test_returns_property_uri_when_no_code(self):
        cp = BsddClassProperty(Code="P1", PropertySet="S", PropertyUri="https://example.com/prop")
        assert ClassPropertyEditorWidget.get_property_reference(cp) == "https://example.com/prop"


# ---------------------------------------------------------------------------
# is_property_reference_valid
# ---------------------------------------------------------------------------

class TestIsPropertyReferenceValid:
    def test_uri_is_always_valid(self):
        cp = _make_cp()
        d = _make_dict()
        assert ClassPropertyEditorWidget.is_property_reference_valid(
            "https://example.com/prop", cp, d
        ) is True

    def test_unknown_code_is_invalid(self):
        cp = _make_cp()
        d = _make_dict()  # no properties in dict
        assert ClassPropertyEditorWidget.is_property_reference_valid("MISSING", cp, d) is False

    def test_existing_code_in_dict_is_valid(self):
        prop = BsddProperty(Code="PROP1", Name="PROP1", DataType="String")
        d = _make_dict(prop)
        cp = _make_cp(prop_code="PROP1")
        assert ClassPropertyEditorWidget.is_property_reference_valid("PROP1", cp, d) is True

    def test_code_already_used_by_sibling_is_invalid(self):
        prop = BsddProperty(Code="PROP1", Name="PROP1", DataType="String")
        d = _make_dict(prop)
        cls = BsddClass(Code="C", Name="C")
        # The check compares `value` against sibling ClassProperty *Codes* (not PropertyCodes).
        # cp1's Code is "PROP1", so trying to set cp2's reference to "PROP1" should fail.
        cp1 = BsddClassProperty(Code="PROP1", PropertySet="S", PropertyCode="PROP1")
        cp2 = BsddClassProperty(Code="P2", PropertySet="S", PropertyCode="OTHER")
        cp1._set_parent(cls)
        cp2._set_parent(cls)
        cls.ClassProperties = [cp1, cp2]
        assert ClassPropertyEditorWidget.is_property_reference_valid("PROP1", cp2, d) is False


# ---------------------------------------------------------------------------
# create_temporary_property
# ---------------------------------------------------------------------------

class TestCreateTemporaryProperty:
    def test_returns_class_property(self):
        cls = BsddClass(Code="C", Name="C")
        cp = ClassPropertyEditorWidget.create_temporary_property("Pset_A", cls)
        assert isinstance(cp, BsddClassProperty)

    def test_has_correct_property_set(self):
        cls = BsddClass(Code="C", Name="C")
        cp = ClassPropertyEditorWidget.create_temporary_property("Pset_A", cls)
        assert cp.PropertySet == "Pset_A"

    def test_parent_is_set(self):
        cls = BsddClass(Code="C", Name="C")
        cp = ClassPropertyEditorWidget.create_temporary_property("Pset_A", cls)
        assert cp.parent() is cls


# ---------------------------------------------------------------------------
# set_code
# ---------------------------------------------------------------------------

class TestSetCode:
    def test_updates_code(self):
        cp = _make_cp(code="old")
        ClassPropertyEditorWidget.set_code(cp, "new")
        assert cp.Code == "new"
