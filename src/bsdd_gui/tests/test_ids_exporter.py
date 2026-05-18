"""
Tests for the IdsExporter module (tool/ids_exporter.py).

Covers the pure-Python helpers that do not require a live Qt widget or
IDS file access.
"""
from __future__ import annotations

from bsdd_json.models import BsddClass, BsddClassProperty, BsddDictionary

from bsdd_gui.tool import IdsExporter


def _make_dict() -> BsddDictionary:
    return BsddDictionary(
        OrganizationCode="TST",
        DictionaryCode="D",
        DictionaryVersion="1.0",
        LanguageIsoCode="en-GB",
        LanguageOnly=False,
        UseOwnUri=False,
    )


# ---------------------------------------------------------------------------
# build_inherited_checkstate_dict
# ---------------------------------------------------------------------------

class TestBuildInheritedCheckstateDict:
    def test_empty_list(self):
        result = IdsExporter.build_inherited_checkstate_dict([], {})
        assert result == {}

    def test_root_class_defaults_to_true(self):
        cls = BsddClass(Code="A", Name="A")
        result = IdsExporter.build_inherited_checkstate_dict([cls], {})
        assert result["A"] is True

    def test_root_class_disabled(self):
        cls = BsddClass(Code="A", Name="A")
        result = IdsExporter.build_inherited_checkstate_dict([cls], {"A": False})
        assert result["A"] is False

    def test_child_inherits_disabled_parent(self):
        bsdd_dict = _make_dict()
        parent = BsddClass(Code="P", Name="Parent")
        child = BsddClass(Code="C", Name="Child", ParentClassCode="P")
        bsdd_dict.Classes = [parent, child]
        parent._set_parent(bsdd_dict)
        child._set_parent(bsdd_dict)
        # parent is disabled — child should also be False
        result = IdsExporter.build_inherited_checkstate_dict([parent, child], {"P": False})
        assert result["P"] is False
        assert result["C"] is False

    def test_child_stays_enabled_when_parent_enabled(self):
        bsdd_dict = _make_dict()
        parent = BsddClass(Code="P", Name="Parent")
        child = BsddClass(Code="C", Name="Child", ParentClassCode="P")
        bsdd_dict.Classes = [parent, child]
        parent._set_parent(bsdd_dict)
        child._set_parent(bsdd_dict)
        result = IdsExporter.build_inherited_checkstate_dict([parent, child], {})
        assert result["P"] is True
        assert result["C"] is True


# ---------------------------------------------------------------------------
# is_class_active
# ---------------------------------------------------------------------------

class TestIsClassActive:
    def test_returns_true_by_default(self):
        cls = BsddClass(Code="A", Name="A")
        assert IdsExporter.is_class_active(cls, {}, False) is True

    def test_returns_false_when_disabled(self):
        cls = BsddClass(Code="A", Name="A")
        assert IdsExporter.is_class_active(cls, {"A": False}, False) is False

    def test_inherit_false_returns_setting_directly(self):
        cls = BsddClass(Code="A", Name="A")
        assert IdsExporter.is_class_active(cls, {"A": True}, False) is True

    def test_inherit_true_no_parent_returns_checkstate(self):
        cls = BsddClass(Code="A", Name="A")  # no ParentClassCode
        assert IdsExporter.is_class_active(cls, {"A": True}, True) is True


# ---------------------------------------------------------------------------
# is_class_prop_active
# ---------------------------------------------------------------------------

class TestIsClassPropActive:
    def test_returns_true_when_pset_not_in_settings(self):
        cp = BsddClassProperty(Code="P", PropertySet="PS", PropertyCode="X")
        assert IdsExporter.is_class_prop_active(cp, {}) is True

    def test_returns_false_when_pset_checked_false(self):
        cp = BsddClassProperty(Code="P", PropertySet="PS", PropertyCode="X")
        assert IdsExporter.is_class_prop_active(cp, {"PS": {"checked": False}}) is False

    def test_returns_property_state_when_pset_enabled(self):
        cp = BsddClassProperty(Code="P", PropertySet="PS", PropertyCode="X")
        settings = {"PS": {"checked": True, "properties": {"P": False}}}
        assert IdsExporter.is_class_prop_active(cp, settings) is False

    def test_returns_true_when_pset_enabled_and_prop_not_in_settings(self):
        cp = BsddClassProperty(Code="P", PropertySet="PS", PropertyCode="X")
        settings = {"PS": {"checked": True, "properties": {}}}
        assert IdsExporter.is_class_prop_active(cp, settings) is True


# ---------------------------------------------------------------------------
# get_data_type
# ---------------------------------------------------------------------------

class TestGetDataType:
    def test_unknown_type_returns_ifctext(self):
        result = IdsExporter.get_data_type("UnknownType", "https://example.com/prop", {})
        assert result == "IFCTEXT"

    def test_known_type_in_custom_mapping(self):
        mapping = {"String": "IfcLabel"}
        result = IdsExporter.get_data_type("String", "https://example.com/prop", mapping)
        assert result == "IfcLabel"

    def test_property_uri_overrides_datatype_mapping(self):
        uri = "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/AcousticRating"
        result = IdsExporter.get_data_type("String", uri, {})
        assert result == "IfcLabel"

    def test_another_known_property_uri(self):
        uri = "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/ThermalTransmittance"
        result = IdsExporter.get_data_type("Real", uri, {})
        assert result == "IfcThermalTransmittanceMeasure"
