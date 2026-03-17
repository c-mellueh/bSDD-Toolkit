"""
Tests for the bsdd_json module.

Covers models, class_utils, property_utils, and dictionary_utils.
These tests are pure-Python and do not require network access.
"""
from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from bsdd_json.models import (
    BsddAllowedValue,
    BsddClass,
    BsddClassProperty,
    BsddClassRelation,
    BsddDictionary,
    BsddProperty,
    BsddPropertyRelation,
)
from bsdd_json.utils import build_unique_code
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json.utils import property_utils as prop_utils

from .helpers import make_class, make_dictionary, make_property


# ===========================================================================
# 1. build_unique_code
# ===========================================================================

class TestBuildUniqueCode:
    def test_returns_base_when_not_in_list(self):
        assert build_unique_code("Wall", []) == "Wall"

    def test_appends_2_when_name_exists(self):
        assert build_unique_code("Wall", ["Wall"]) == "Wall-2"

    def test_increments_until_unique(self):
        existing = ["Wall", "Wall-2", "Wall-3"]
        assert build_unique_code("Wall", existing) == "Wall-4"

    def test_no_change_when_name_absent(self):
        assert build_unique_code("New", ["Old"]) == "New"

    def test_large_gap(self):
        existing = ["X", "X-2", "X-3", "X-4", "X-5"]
        assert build_unique_code("X", existing) == "X-6"


# ===========================================================================
# 2. dictionary_utils.slugify
# ===========================================================================


# ===========================================================================
# 9. BsddDictionary model
# ===========================================================================

class TestBsddDictionary:
    def test_required_fields(self, dictionary):
        assert dictionary.OrganizationCode == "TST"
        assert dictionary.DictionaryCode == "TEST_DICT"
        assert dictionary.DictionaryVersion == "1.0"
        assert dictionary.LanguageIsoCode == "en-GB"
        assert dictionary.LanguageOnly is False
        assert dictionary.UseOwnUri is False

    def test_default_collections_empty(self, dictionary):
        assert dictionary.Classes == []
        assert dictionary.Properties == []

    def test_default_license(self, dictionary):
        assert dictionary.License == "MIT"

    def test_model_post_init_sets_class_parents(self):
        cls = make_class("C1", "Class 1")
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls],
        )
        assert d.Classes[0].parent() is d

    def test_model_post_init_sets_property_parents(self):
        prop = make_property("P1", "Prop 1")
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Properties=[prop],
        )
        assert d.Properties[0].parent() is d

    def test_save_and_load_roundtrip(self, tmp_path):
        d = make_dictionary()
        path = str(tmp_path / "test.json")
        d.save(path)
        loaded = BsddDictionary.load(path)
        assert loaded.OrganizationCode == d.OrganizationCode
        assert loaded.DictionaryCode == d.DictionaryCode
        assert loaded.DictionaryVersion == d.DictionaryVersion

    def test_load_sets_parent_refs(self, tmp_path):
        cls = make_class("C1", "Class 1")
        prop = make_property("P1", "Prop 1")
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls], Properties=[prop],
        )
        path = str(tmp_path / "test.json")
        d.save(path)
        loaded = BsddDictionary.load(path)
        assert loaded.Classes[0].parent() is loaded
        assert loaded.Properties[0].parent() is loaded

    def test_sloppy_load_prunes_invalid_field(self, tmp_path):
        raw = {
            "OrganizationCode": "TST",
            "DictionaryCode": "TEST",
            "DictionaryVersion": "1.0",
            "LanguageIsoCode": "en-GB",
            "LanguageOnly": False,
            "UseOwnUri": False,
            "Status": "NOT_A_VALID_STATUS",
        }
        path = str(tmp_path / "bad.json")
        with open(path, "w") as f:
            json.dump(raw, f)
        d = BsddDictionary.load(path, sloppy=True)
        assert d is not None
        assert d.OrganizationCode == "TST"

    def test_strict_load_raises_on_invalid_field(self, tmp_path):
        raw = {
            "OrganizationCode": "TST",
            "DictionaryCode": "TEST",
            "DictionaryVersion": "1.0",
            "LanguageIsoCode": "en-GB",
            "LanguageOnly": False,
            "UseOwnUri": False,
            "Status": "NOT_A_VALID_STATUS",
        }
        path = str(tmp_path / "bad.json")
        with open(path, "w") as f:
            json.dump(raw, f)
        with pytest.raises(ValidationError):
            BsddDictionary.load(path, sloppy=False)

    def test_case_insensitive_validation(self):
        d = BsddDictionary.model_validate({
            "organizationCode": "TST",
            "dictionaryCode": "TEST",
            "dictionaryVersion": "1.0",
            "languageIsoCode": "en-GB",
            "languageOnly": False,
            "useOwnUri": False,
        })
        assert d.OrganizationCode == "TST"


# ===========================================================================
# 10. BsddClass model
# ===========================================================================

class TestBsddClass:
    def test_required_fields(self):
        c = make_class("C1", "My Class")
        assert c.Code == "C1"
        assert c.Name == "My Class"

    def test_default_class_type(self):
        assert make_class("C1", "Class").ClassType == "Class"

    def test_parent_initially_none(self):
        assert make_class("C1", "Class").parent() is None

    def test_set_parent(self):
        d = make_dictionary()
        c = make_class("C1", "Class")
        c._set_parent(d)
        assert c.parent() is d

    def test_class_properties_default_empty(self):
        assert make_class("C1", "Class").ClassProperties == []

    def test_class_relations_default_empty(self):
        assert make_class("C1", "Class").ClassRelations == []

    def test_model_post_init_sets_class_property_parents(self):
        cp = BsddClassProperty(Code="CP1", PropertyCode="PROP1")
        c = BsddClass(Code="C1", Name="Class 1", ClassProperties=[cp])
        assert c.ClassProperties[0].parent() is c

    def test_model_post_init_sets_class_relation_parents(self):
        cr = BsddClassRelation(
            RelationType="IsChildOf",
            RelatedClassUri="https://identifier.buildingsmart.org/uri/tst/test/1.0/class/ROOT",
        )
        c = BsddClass(Code="C1", Name="Class 1", ClassRelations=[cr])
        assert c.ClassRelations[0].parent() is c

    def test_apply_code_side_effects_raises_on_empty(self):
        c = make_class("C1", "Class")
        with pytest.raises(ValueError, match="Empty Code"):
            c._apply_code_side_effects("")

    def test_apply_code_side_effects_raises_on_whitespace(self):
        c = make_class("C1", "Class")
        with pytest.raises(ValueError, match="Empty Code"):
            c._apply_code_side_effects("   ")

    def test_apply_code_side_effects_raises_on_duplicate(self):
        c1 = make_class("C1", "Class 1")
        c2 = make_class("C2", "Class 2")
        BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[c1, c2],
        )
        with pytest.raises(ValueError, match="exists already"):
            c2._apply_code_side_effects("C1")

    def test_apply_code_side_effects_propagates_to_children(self):
        child = make_class("CHILD", "Child", ParentClassCode="PARENT")
        parent = make_class("PARENT", "Parent")
        BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[parent, child],
        )
        parent._apply_code_side_effects("NEW_PARENT")
        assert child.ParentClassCode == "NEW_PARENT"


# ===========================================================================
# 11. BsddClassProperty validation
# ===========================================================================

class TestBsddClassProperty:
    def test_property_code_only_valid(self):
        cp = BsddClassProperty(Code="CP1", PropertyCode="PROP1")
        assert cp.PropertyCode == "PROP1"
        assert cp.PropertyUri is None

    def test_property_uri_only_valid(self):
        cp = BsddClassProperty(
            Code="CP1",
            PropertyUri="https://identifier.buildingsmart.org/uri/tst/test/1.0/prop/P1",
        )
        assert cp.PropertyUri is not None
        assert cp.PropertyCode is None

    def test_both_code_and_uri_raises(self):
        with pytest.raises(ValidationError):
            BsddClassProperty(
                Code="CP1",
                PropertyCode="PROP1",
                PropertyUri="https://identifier.buildingsmart.org/uri/tst/test/1.0/prop/P1",
            )

    def test_neither_code_nor_uri_raises(self):
        with pytest.raises(ValidationError):
            BsddClassProperty(Code="CP1")

    def test_whitespace_only_code_treated_as_none(self):
        with pytest.raises(ValidationError):
            BsddClassProperty(Code="CP1", PropertyCode="   ")

    def test_parent_initially_none(self):
        cp = BsddClassProperty(Code="CP1", PropertyCode="P1")
        assert cp.parent() is None

    def test_set_parent(self):
        c = make_class("C1", "Class")
        cp = BsddClassProperty(Code="CP1", PropertyCode="P1")
        cp._set_parent(c)
        assert cp.parent() is c


# ===========================================================================
# 12. BsddAllowedValue model
# ===========================================================================

class TestBsddAllowedValue:
    def test_required_fields(self):
        av = BsddAllowedValue(Code="AV1", Value="Option A")
        assert av.Code == "AV1"
        assert av.Value == "Option A"

    def test_optional_fields_default_none(self):
        av = BsddAllowedValue(Code="AV1", Value="Option A")
        assert av.Description is None
        assert av.Uri is None
        assert av.SortNumber is None


# ===========================================================================
# 13. BsddProperty model
# ===========================================================================

class TestBsddProperty:
    def test_required_fields(self):
        p = make_property("P1", "Property 1")
        assert p.Code == "P1"
        assert p.Name == "Property 1"

    def test_parent_initially_none(self):
        assert make_property("P1", "Property 1").parent() is None

    def test_set_parent(self):
        d = make_dictionary()
        p = make_property("P1", "Property 1")
        p._set_parent(d)
        assert p.parent() is d

    def test_property_relations_default_empty(self):
        assert make_property("P1", "Property 1").PropertyRelations == []

    def test_allowed_values_default_empty(self):
        assert make_property("P1", "Property 1").AllowedValues == []

    def test_model_post_init_sets_relation_parents(self):
        pr = BsddPropertyRelation(
            RelatedPropertyUri="https://identifier.buildingsmart.org/uri/tst/test/1.0/prop/P2",
            RelationType="IsEqualTo",
        )
        p = BsddProperty(Code="P1", Name="Prop 1", PropertyRelations=[pr])
        assert p.PropertyRelations[0].parent() is p


# ===========================================================================
# 14. BsddPropertyRelation model
# ===========================================================================

class TestBsddPropertyRelation:
    def test_required_fields(self):
        pr = BsddPropertyRelation(
            RelatedPropertyUri="https://example.com/prop/P1",
            RelationType="IsEqualTo",
        )
        assert pr.RelatedPropertyUri == "https://example.com/prop/P1"
        assert pr.RelationType == "IsEqualTo"

    def test_set_parent(self):
        p = make_property("P1", "Prop 1")
        pr = BsddPropertyRelation(
            RelatedPropertyUri="https://example.com/prop/P2",
            RelationType="HasReference",
        )
        pr._set_parent(p)
        assert pr.parent() is p


# ===========================================================================
# 15. BsddClassRelation model
# ===========================================================================

class TestBsddClassRelation:
    def test_required_fields(self):
        cr = BsddClassRelation(
            RelationType="IsChildOf",
            RelatedClassUri="https://example.com/class/Root",
        )
        assert cr.RelationType == "IsChildOf"
        assert cr.RelatedClassUri == "https://example.com/class/Root"

    def test_set_parent(self):
        c = make_class("C1", "Class 1")
        cr = BsddClassRelation(
            RelationType="IsChildOf",
            RelatedClassUri="https://example.com/class/Root",
        )
        cr._set_parent(c)
        assert cr.parent() is c


# ===========================================================================
# 16. class_utils – tree navigation
# ===========================================================================

class TestClassUtilsNavigation:
    def test_get_root_classes_returns_classes_without_parent(self, populated_dictionary):
        roots = cl_utils.get_root_classes(populated_dictionary)
        codes = {c.Code for c in roots}
        assert "ROOT" in codes
        assert "CHILD1" not in codes

    def test_get_root_classes_empty_for_none(self):
        assert cl_utils.get_root_classes(None) == []

    def test_get_children_returns_direct_children(self, populated_dictionary):
        root = cl_utils.get_class_by_code(populated_dictionary, "ROOT")
        children = cl_utils.get_children(root)
        codes = {c.Code for c in children}
        assert codes == {"CHILD1", "CHILD2"}

    def test_get_children_empty_for_leaf(self, populated_dictionary):
        grandchild = cl_utils.get_class_by_code(populated_dictionary, "GRANDCHILD")
        assert cl_utils.get_children(grandchild) == []

    def test_get_parent_returns_parent(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        parent = cl_utils.get_parent(child1)
        assert parent is not None
        assert parent.Code == "ROOT"

    def test_get_parent_returns_none_for_root(self, populated_dictionary):
        root = cl_utils.get_class_by_code(populated_dictionary, "ROOT")
        assert cl_utils.get_parent(root) is None

    def test_get_parent_returns_none_for_none_input(self):
        assert cl_utils.get_parent(None) is None

    def test_get_class_by_code_finds_class(self, populated_dictionary):
        c = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        assert c is not None
        assert c.Code == "CHILD1"

    def test_get_class_by_code_returns_none_for_missing(self, populated_dictionary):
        assert cl_utils.get_class_by_code(populated_dictionary, "MISSING") is None

    def test_get_all_class_codes_returns_all(self, populated_dictionary):
        codes = cl_utils.get_all_class_codes(populated_dictionary)
        assert isinstance(codes, dict)
        assert set(codes.keys()) == {"ROOT", "CHILD1", "CHILD2", "GRANDCHILD"}

    def test_get_row_index_root_is_zero(self, populated_dictionary):
        root = cl_utils.get_class_by_code(populated_dictionary, "ROOT")
        assert cl_utils.get_row_index(root) == 0

    def test_get_row_index_first_child_is_zero(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        assert cl_utils.get_row_index(child1) == 0

    def test_get_row_index_second_child_is_one(self, populated_dictionary):
        child2 = cl_utils.get_class_by_code(populated_dictionary, "CHILD2")
        assert cl_utils.get_row_index(child2) == 1


# ===========================================================================
# 17. class_utils – remove_class
# ===========================================================================

class TestRemoveClass:
    def test_removes_from_dictionary(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        cl_utils.remove_class(child1)
        assert cl_utils.get_class_by_code(populated_dictionary, "CHILD1") is None

    def test_orphans_children_on_removal(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        cl_utils.remove_class(child1)
        grandchild = cl_utils.get_class_by_code(populated_dictionary, "GRANDCHILD")
        assert grandchild.ParentClassCode is None

    def test_other_classes_unaffected(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        cl_utils.remove_class(child1)
        assert cl_utils.get_class_by_code(populated_dictionary, "CHILD2") is not None
        assert cl_utils.get_class_by_code(populated_dictionary, "ROOT") is not None


# ===========================================================================
# 18. class_utils – set_code
# ===========================================================================

class TestSetCode:
    def test_changes_code(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        cl_utils.set_code(child1, "NEW_CODE")
        assert child1.Code == "NEW_CODE"

    def test_same_code_is_noop(self, populated_dictionary):
        root = cl_utils.get_class_by_code(populated_dictionary, "ROOT")
        cl_utils.set_code(root, "ROOT")  # should not raise
        assert root.Code == "ROOT"

    def test_updates_children_parent_ref(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        cl_utils.set_code(child1, "CHILD1_RENAMED")
        grandchild = cl_utils.get_class_by_code(populated_dictionary, "GRANDCHILD")
        assert grandchild.ParentClassCode == "CHILD1_RENAMED"

    def test_raises_on_duplicate(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        with pytest.raises(ValueError):
            cl_utils.set_code(child1, "CHILD2")


# ===========================================================================
# 19. class_utils – shared_parent
# ===========================================================================

class TestSharedParent:
    def test_siblings_highest_is_common_root(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        child2 = cl_utils.get_class_by_code(populated_dictionary, "CHILD2")
        result = cl_utils.shared_parent([child1, child2], mode="highest")
        assert result is not None
        assert result.Code == "ROOT"

    def test_siblings_lowest_is_common_root(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        child2 = cl_utils.get_class_by_code(populated_dictionary, "CHILD2")
        result = cl_utils.shared_parent([child1, child2], mode="lowest")
        assert result is not None
        assert result.Code == "ROOT"

    def test_same_class_lowest_returns_itself(self, populated_dictionary):
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        result = cl_utils.shared_parent([child1, child1], mode="lowest")
        assert result.Code == "CHILD1"

    def test_parent_and_child_lowest_returns_child(self, populated_dictionary):
        root = cl_utils.get_class_by_code(populated_dictionary, "ROOT")
        child1 = cl_utils.get_class_by_code(populated_dictionary, "CHILD1")
        result = cl_utils.shared_parent([root, child1], mode="lowest")
        assert result.Code == "ROOT"

    def test_uncle_and_nephew_returns_common_root(self, populated_dictionary):
        child2 = cl_utils.get_class_by_code(populated_dictionary, "CHILD2")
        grandchild = cl_utils.get_class_by_code(populated_dictionary, "GRANDCHILD")
        result = cl_utils.shared_parent([child2, grandchild], mode="lowest")
        assert result.Code == "ROOT"

    def test_empty_list_returns_none(self, populated_dictionary):
        result = cl_utils.shared_parent([], dictionary=populated_dictionary)
        assert result is None


# ===========================================================================
# 20. class_utils – build_bsdd_uri
# ===========================================================================

class TestClassUtilsBuildUri:
    def test_uri_contains_expected_parts(self, populated_dictionary):
        root = cl_utils.get_class_by_code(populated_dictionary, "ROOT")
        uri = cl_utils.build_bsdd_uri(root, populated_dictionary)
        assert "TST" in uri
        assert "TEST" in uri
        assert "1.0" in uri
        assert "class" in uri
        assert "ROOT" in uri

    def test_returns_none_for_non_class(self, populated_dictionary):
        assert cl_utils.build_bsdd_uri("not a class", populated_dictionary) is None

    def test_uri_is_valid(self, populated_dictionary):
        root = cl_utils.get_class_by_code(populated_dictionary, "ROOT")
        uri = cl_utils.build_bsdd_uri(root, populated_dictionary)
        assert dict_utils.is_uri(uri)


# ===========================================================================
# 21. class_utils – is_ifc_reference
# ===========================================================================

class TestClassIsIfcReference:
    def test_class_with_ifc_uri(self):
        c = make_class(
            "C1", "Wall",
            OwnedUri="https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/Wall",
        )
        assert cl_utils.is_ifc_reference(c)

    def test_class_without_owned_uri(self):
        assert not cl_utils.is_ifc_reference(make_class("C1", "Wall"))

    def test_class_with_non_ifc_uri(self):
        c = make_class(
            "C1", "Wall",
            OwnedUri="https://identifier.buildingsmart.org/uri/hw/som/0.2.0/class/Wall",
        )
        assert not cl_utils.is_ifc_reference(c)


# ===========================================================================
# 22. class_utils – GroupOfProperties relations
# ===========================================================================

class TestGroupOfPropertiesRelations:
    def _make_pset_dictionary(self):
        pset = make_class("PSET1", "My PSet", ClassType="GroupOfProperties")
        wall = make_class("WALL", "Wall")
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[pset, wall],
        )
        pset_uri = cl_utils.build_bsdd_uri(pset, d)
        rel = BsddClassRelation(RelationType="HasReference", RelatedClassUri=pset_uri)
        d.Classes[1].ClassRelations.append(rel)
        rel._set_parent(d.Classes[1])
        return d

    def test_get_related_psets_finds_group(self):
        d = self._make_pset_dictionary()
        wall = cl_utils.get_class_by_code(d, "WALL")
        psets = cl_utils.get_related_psets(wall, d)
        assert len(psets) == 1
        assert psets[0].Code == "PSET1"

    def test_get_relating_pset_classes_finds_class(self):
        d = self._make_pset_dictionary()
        pset = cl_utils.get_class_by_code(d, "PSET1")
        relating = cl_utils.get_relating_pset_classes(pset, d)
        assert len(relating) == 1
        assert relating[0].Code == "WALL"

    def test_get_related_psets_empty_when_no_group(self, populated_dictionary):
        root = cl_utils.get_class_by_code(populated_dictionary, "ROOT")
        assert cl_utils.get_related_psets(root, populated_dictionary) == []


# ===========================================================================
# 23. class_utils – build_dummy_class
# ===========================================================================

class TestBuildDummyClass:
    def test_creates_class_from_uri(self):
        uri = "https://identifier.buildingsmart.org/uri/tst/test/1.0/class/MyClass"
        result = cl_utils.build_dummy_class(uri)
        assert result.Code == "MyClass"
        assert result.OwnedUri == uri


# ===========================================================================
# 24. property_utils – lookups
# ===========================================================================

class TestPropertyUtilsLookups:
    def test_get_property_by_code_finds_property(self, populated_dictionary):
        prop = prop_utils.get_property_by_code("PROP1", populated_dictionary)
        assert prop is not None
        assert prop.Code == "PROP1"

    def test_get_property_by_code_returns_none_for_missing(self, populated_dictionary):
        assert prop_utils.get_property_by_code("MISSING", populated_dictionary) is None

    def test_get_all_property_codes_returns_dict(self, populated_dictionary):
        codes = prop_utils.get_all_property_codes(populated_dictionary)
        assert isinstance(codes, dict)
        assert "PROP1" in codes
        assert "PROP2" in codes

    def test_get_property_code_dict(self, populated_dictionary):
        codes = prop_utils.get_property_code_dict(populated_dictionary)
        assert "PROP1" in codes


# ===========================================================================
# 25. property_utils – get_classes_with_bsdd_property
# ===========================================================================

class TestGetClassesWithBsddProperty:
    def _make_dict(self):
        prop = make_property("PROP1", "Property 1")
        cp = BsddClassProperty(Code="CP1", PropertyCode="PROP1")
        cls = BsddClass(Code="WALL", Name="Wall", ClassProperties=[cp])
        return BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls], Properties=[prop],
        )

    def test_finds_class_using_property_code(self):
        d = self._make_dict()
        classes = prop_utils.get_classes_with_bsdd_property("PROP1", d)
        assert len(classes) == 1
        assert classes[0].Code == "WALL"

    def test_returns_empty_for_unused_property(self):
        d = self._make_dict()
        assert prop_utils.get_classes_with_bsdd_property("PROP_UNUSED", d) == []


# ===========================================================================
# 26. property_utils – get_class_properties_from_property_code/uri
# ===========================================================================

class TestGetClassPropertiesFromCode:
    def _make_dict(self):
        cp1 = BsddClassProperty(Code="CP1", PropertyCode="PROP1")
        cp2 = BsddClassProperty(Code="CP2", PropertyCode="PROP1")
        cls1 = BsddClass(Code="C1", Name="Class 1", ClassProperties=[cp1])
        cls2 = BsddClass(Code="C2", Name="Class 2", ClassProperties=[cp2])
        return BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls1, cls2],
        )

    def test_finds_class_properties_by_code(self):
        d = self._make_dict()
        result = prop_utils.get_class_properties_from_property_code("PROP1", d)
        assert len(result) == 2

    def test_returns_empty_for_no_match(self):
        d = make_dictionary()
        assert prop_utils.get_class_properties_from_property_code("MISSING", d) == []

    def test_finds_class_properties_by_uri(self):
        uri = "https://identifier.buildingsmart.org/uri/tst/test/1.0/prop/EXT_PROP"
        cp = BsddClassProperty(Code="CP1", PropertyUri=uri)
        cls = BsddClass(Code="C1", Name="Class 1", ClassProperties=[cp])
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls],
        )
        result = prop_utils.get_class_properties_from_property_uri(uri, d)
        assert len(result) == 1


# ===========================================================================
# 27. property_utils – delete_property
# ===========================================================================

class TestDeleteProperty:
    def _make_dict(self):
        prop = make_property("PROP1", "Property 1")
        cp = BsddClassProperty(Code="CP1", PropertyCode="PROP1")
        cls = BsddClass(Code="WALL", Name="Wall", ClassProperties=[cp])
        return BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls], Properties=[prop],
        )

    def test_removes_property_from_dictionary(self):
        d = self._make_dict()
        prop = prop_utils.get_property_by_code("PROP1", d)
        prop_utils.delete_property(prop, d)
        assert prop not in d.Properties

    def test_removes_class_properties_referencing_it(self):
        d = self._make_dict()
        prop = prop_utils.get_property_by_code("PROP1", d)
        prop_utils.delete_property(prop, d)
        assert d.Classes[0].ClassProperties == []

    def test_returns_removed_class_properties(self):
        prop = make_property("PROP1", "Property 1")
        cp1 = BsddClassProperty(Code="CP1", PropertyCode="PROP1")
        cp2 = BsddClassProperty(Code="CP2", PropertyCode="PROP1")
        cls1 = BsddClass(Code="C1", Name="Class 1", ClassProperties=[cp1])
        cls2 = BsddClass(Code="C2", Name="Class 2", ClassProperties=[cp2])
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls1, cls2], Properties=[prop],
        )
        removed = prop_utils.delete_property(prop, d)
        assert len(removed) == 2


# ===========================================================================
# 28. property_utils – create_class_property_from_property
# ===========================================================================

class TestCreateClassPropertyFromProperty:
    def test_creates_with_property_code(self):
        prop = make_property("PROP1", "Property 1")
        cls = make_class("WALL", "Wall")
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls], Properties=[prop],
        )
        result = prop_utils.create_class_property_from_property(prop, cls, d)
        assert result.PropertyCode == "PROP1"
        assert result.IsRequired is True

    def test_creates_with_property_uri_when_owned_uri_set(self):
        prop = make_property(
            "PROP1", "Property 1",
            OwnedUri="https://identifier.buildingsmart.org/uri/tst/test/1.0/prop/PROP1",
        )
        cls = make_class("WALL", "Wall")
        d = make_dictionary()
        result = prop_utils.create_class_property_from_property(prop, cls, d)
        assert result.PropertyUri is not None
        assert result.PropertyCode is None

    def test_unique_code_on_conflict(self):
        prop = make_property("PROP1", "Property 1")
        cp_existing = BsddClassProperty(Code="PROP1", PropertyCode="PROP1")
        cls = BsddClass(Code="WALL", Name="Wall", ClassProperties=[cp_existing])
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls], Properties=[prop],
        )
        result = prop_utils.create_class_property_from_property(prop, cls, d)
        assert result.Code == "PROP1-2"

    def test_sets_first_unit_from_property(self):
        prop = make_property("PROP1", "Property 1", Units=["m"])
        cls = make_class("WALL", "Wall")
        d = make_dictionary()
        result = prop_utils.create_class_property_from_property(prop, cls, d)
        assert result.Unit == "m"


# ===========================================================================
# 29. property_utils – build_bsdd_uri
# ===========================================================================

class TestPropertyUtilsBuildUri:
    def test_uri_contains_expected_parts(self):
        prop = make_property("PROP1", "Property 1")
        d = make_dictionary()
        uri = prop_utils.build_bsdd_uri(prop, d)
        assert "TST" in uri
        assert "TEST" in uri
        assert "1.0" in uri
        assert "prop" in uri
        assert "PROP1" in uri

    def test_uri_is_valid(self):
        prop = make_property("PROP1", "Property 1")
        d = make_dictionary()
        uri = prop_utils.build_bsdd_uri(prop, d)
        assert dict_utils.is_uri(uri)


# ===========================================================================
# 30. property_utils – get_most_used_property_set
# ===========================================================================

class TestGetMostUsedPropertySet:
    def test_returns_most_frequent_pset(self):
        prop = make_property("PROP1", "Property 1")
        cp1 = BsddClassProperty(Code="CP1", PropertyCode="PROP1", PropertySet="PsetA")
        cp2 = BsddClassProperty(Code="CP2", PropertyCode="PROP1", PropertySet="PsetA")
        cp3 = BsddClassProperty(Code="CP3", PropertyCode="PROP1", PropertySet="PsetB")
        cls = BsddClass(Code="C1", Name="C1", ClassProperties=[cp1, cp2, cp3])
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls], Properties=[prop],
        )
        assert prop_utils.get_most_used_property_set(prop, d) == "PsetA"

    def test_returns_none_for_unused_property(self):
        prop = make_property("PROP1", "Property 1")
        d = make_dictionary()
        d.Properties.append(prop)
        assert prop_utils.get_most_used_property_set(prop, d) is None


# ===========================================================================
# 31. property_utils – get_class_properties_by_pset_name
# ===========================================================================

class TestGetClassPropertiesByPsetName:
    def test_filters_by_pset_name(self):
        cp1 = BsddClassProperty(Code="CP1", PropertyCode="P1", PropertySet="PsetA")
        cp2 = BsddClassProperty(Code="CP2", PropertyCode="P2", PropertySet="PsetB")
        cls = BsddClass(Code="C1", Name="Class 1", ClassProperties=[cp1, cp2])
        result = prop_utils.get_class_properties_by_pset_name(cls, "PsetA")
        assert len(result) == 1
        assert result[0].Code == "CP1"

    def test_returns_empty_for_no_match(self):
        cp1 = BsddClassProperty(Code="CP1", PropertyCode="P1", PropertySet="PsetA")
        cls = BsddClass(Code="C1", Name="Class 1", ClassProperties=[cp1])
        assert prop_utils.get_class_properties_by_pset_name(cls, "PsetX") == []


# ===========================================================================
# 32. property_utils – get_property_relation
# ===========================================================================

class TestGetPropertyRelation:
    def test_finds_matching_relation(self):
        uri = "https://identifier.buildingsmart.org/uri/tst/test/1.0/prop/P2"
        pr = BsddPropertyRelation(RelatedPropertyUri=uri, RelationType="IsEqualTo")
        prop = BsddProperty(Code="P1", Name="Prop 1", PropertyRelations=[pr])
        result = prop_utils.get_property_relation(prop, uri, "IsEqualTo")
        assert result is pr

    def test_returns_none_for_no_match(self):
        prop = BsddProperty(Code="P1", Name="Prop 1")
        assert prop_utils.get_property_relation(prop, "some_uri", "IsEqualTo") is None

    def test_does_not_match_wrong_relation_type(self):
        uri = "https://identifier.buildingsmart.org/uri/tst/test/1.0/prop/P2"
        pr = BsddPropertyRelation(RelatedPropertyUri=uri, RelationType="IsEqualTo")
        prop = BsddProperty(Code="P1", Name="Prop 1", PropertyRelations=[pr])
        assert prop_utils.get_property_relation(prop, uri, "HasReference") is None


# ===========================================================================
# 33. property_utils – build_dummy_property
# ===========================================================================

class TestBuildDummyProperty:
    def test_creates_property_from_prop_uri(self):
        uri = "https://identifier.buildingsmart.org/uri/tst/test/1.0/prop/MyProp"
        result = prop_utils.build_dummy_property(uri)
        assert result.Code == "MyProp"
        assert result.OwnedUri == uri


# ===========================================================================
# 34. property_utils – get_name, get_values, get_datatype, get_units
# ===========================================================================

class TestPropertyUtilsAccessors:
    def _make_dict_with_prop(self, **prop_kwargs):
        prop = make_property("P1", "My Property", **prop_kwargs)
        cp = BsddClassProperty(Code="CP1", PropertyCode="P1")
        cls = BsddClass(Code="C1", Name="Class 1", ClassProperties=[cp])
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls], Properties=[prop],
        )
        return d.Classes[0].ClassProperties[0], d

    def test_get_name_returns_property_name(self):
        cp, d = self._make_dict_with_prop()
        assert prop_utils.get_name(cp, d) == "My Property"

    def test_get_name_returns_none_for_missing_property(self):
        cp = BsddClassProperty(Code="CP1", PropertyCode="MISSING")
        assert prop_utils.get_name(cp, make_dictionary()) is None

    def test_get_datatype_returns_type_string(self):
        cp, d = self._make_dict_with_prop(DataType="String")
        assert prop_utils.get_datatype(cp, d) == "String"

    def test_get_datatype_defaults_to_string_when_none(self):
        cp, d = self._make_dict_with_prop()  # DataType not set
        assert prop_utils.get_datatype(cp, d) == "String"

    def test_get_units_returns_units(self):
        cp, d = self._make_dict_with_prop(Units=["m"])
        result = prop_utils.get_units(cp)
        assert result == ["m"]

    def test_get_units_returns_empty_when_no_units(self):
        cp, d = self._make_dict_with_prop()
        result = prop_utils.get_units(cp)
        assert result == []

    def test_get_values_from_class_property_allowed_values(self):
        av = BsddAllowedValue(Code="AV1", Value="Option A")
        prop = make_property("P1", "Property 1")
        cp = BsddClassProperty(Code="CP1", PropertyCode="P1", AllowedValues=[av])
        cls = BsddClass(Code="C1", Name="Class 1", ClassProperties=[cp])
        BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls], Properties=[prop],
        )
        result = prop_utils.get_values(cp)
        assert len(result) == 1
        assert result[0].Code == "AV1"

    def test_get_values_falls_back_to_property_allowed_values(self):
        av = BsddAllowedValue(Code="AV1", Value="Option A")
        prop = make_property("P1", "Property 1", AllowedValues=[av])
        cp = BsddClassProperty(Code="CP1", PropertyCode="P1")  # no local allowed values
        cls = BsddClass(Code="C1", Name="Class 1", ClassProperties=[cp])
        BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls], Properties=[prop],
        )
        result = prop_utils.get_values(cp)
        assert len(result) == 1


# ===========================================================================
# 35. property_utils – get_dictionary_from_property
# ===========================================================================

class TestGetDictionaryFromProperty:
    def test_from_bsdd_property(self):
        prop = make_property("P1", "Prop 1")
        d = make_dictionary()
        prop._set_parent(d)
        assert prop_utils.get_dictionary_from_property(prop) is d

    def test_from_class_property_with_parent_chain(self):
        cp = BsddClassProperty(Code="CP1", PropertyCode="P1")
        cls = BsddClass(Code="C1", Name="Class 1", ClassProperties=[cp])
        d = BsddDictionary(
            OrganizationCode="TST", DictionaryCode="TEST", DictionaryVersion="1.0",
            LanguageIsoCode="en-GB", LanguageOnly=False, UseOwnUri=False,
            Classes=[cls],
        )
        result = prop_utils.get_dictionary_from_property(d.Classes[0].ClassProperties[0])
        assert result is d

    def test_returns_none_for_orphan_class_property(self):
        cp = BsddClassProperty(Code="CP1", PropertyCode="P1")
        assert prop_utils.get_dictionary_from_property(cp) is None
