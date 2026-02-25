"""
Tests for the RelationshipEditorWidget module (tool/relationship_editor_widget.py).

Covers the pure data-model helpers: read_relation, make_class_relation_bidirectional,
and make_property_relation_bidirectional.  Signal emissions are not verified here.
"""
from __future__ import annotations

import pytest
from bsdd_json.models import (
    BsddClass,
    BsddClassRelation,
    BsddDictionary,
    BsddProperty,
    BsddPropertyRelation,
)
from bsdd_json.utils import class_utils
from bsdd_json.utils import property_utils as prop_utils

from bsdd_gui.tool import RelationshipEditorWidget


def _make_dict(classes=None, properties=None) -> BsddDictionary:
    bsdd_dict = BsddDictionary(
        OrganizationCode="TST",
        DictionaryCode="D",
        DictionaryVersion="1.0",
        LanguageIsoCode="en-GB",
        LanguageOnly=False,
        UseOwnUri=False,
    )
    if classes:
        bsdd_dict.Classes = classes
        for c in classes:
            c._set_parent(bsdd_dict)
    if properties:
        bsdd_dict.Properties = properties
        for p in properties:
            p._set_parent(bsdd_dict)
    return bsdd_dict


# ---------------------------------------------------------------------------
# read_relation
# ---------------------------------------------------------------------------

class TestReadRelation:
    def test_reads_class_relation(self):
        start = BsddClass(Code="A", Name="A")
        end = BsddClass(Code="B", Name="B")
        bsdd_dict = _make_dict(classes=[start, end])

        end_uri = class_utils.build_bsdd_uri(end, bsdd_dict)
        rel = BsddClassRelation(
            RelationType="IsChildOf",
            RelatedClassUri=end_uri,
            RelatedClassName="B",
        )
        rel._set_parent(start)

        start_data, end_data, rel_type = RelationshipEditorWidget.read_relation(rel, bsdd_dict)
        assert start_data is start
        assert end_data is end
        assert rel_type == "IsChildOf"

    def test_reads_property_relation(self):
        start = BsddProperty(Code="P1", Name="P1", DataType="String")
        end = BsddProperty(Code="P2", Name="P2", DataType="String")
        bsdd_dict = _make_dict(properties=[start, end])

        end_uri = prop_utils.build_bsdd_uri(end, bsdd_dict)
        rel = BsddPropertyRelation(
            RelationType="IsEqualTo",
            RelatedPropertyUri=end_uri,
            RelatedPropertyName="P2",
        )
        rel._set_parent(start)

        start_data, end_data, rel_type = RelationshipEditorWidget.read_relation(rel, bsdd_dict)
        assert start_data is start
        assert end_data is end
        assert rel_type == "IsEqualTo"


# ---------------------------------------------------------------------------
# make_class_relation_bidirectional
# ---------------------------------------------------------------------------

class TestMakeClassRelationBidirectional:
    def _setup(self):
        parent = BsddClass(Code="P", Name="Parent")
        child = BsddClass(Code="C", Name="Child")
        bsdd_dict = _make_dict(classes=[parent, child])
        return parent, child, bsdd_dict

    def test_adds_inverse_relation(self):
        parent, child, bsdd_dict = self._setup()
        child_uri = class_utils.build_bsdd_uri(child, bsdd_dict)

        rel = BsddClassRelation(
            RelationType="IsParentOf",
            RelatedClassUri=child_uri,
            RelatedClassName="Child",
        )
        rel._set_parent(parent)

        RelationshipEditorWidget.make_class_relation_bidirectional(rel, bsdd_dict, "add")

        parent_uri = class_utils.build_bsdd_uri(parent, bsdd_dict)
        assert any(
            cr.RelationType == "IsChildOf" and cr.RelatedClassUri == parent_uri
            for cr in child.ClassRelations
        )

    def test_does_not_add_duplicate(self):
        parent, child, bsdd_dict = self._setup()
        child_uri = class_utils.build_bsdd_uri(child, bsdd_dict)

        rel = BsddClassRelation(
            RelationType="IsParentOf",
            RelatedClassUri=child_uri,
            RelatedClassName="Child",
        )
        rel._set_parent(parent)

        RelationshipEditorWidget.make_class_relation_bidirectional(rel, bsdd_dict, "add")
        count_before = len(child.ClassRelations)
        RelationshipEditorWidget.make_class_relation_bidirectional(rel, bsdd_dict, "add")
        assert len(child.ClassRelations) == count_before

    def test_remove_removes_inverse_relation(self):
        parent, child, bsdd_dict = self._setup()
        child_uri = class_utils.build_bsdd_uri(child, bsdd_dict)
        parent_uri = class_utils.build_bsdd_uri(parent, bsdd_dict)

        rel = BsddClassRelation(
            RelationType="IsParentOf",
            RelatedClassUri=child_uri,
            RelatedClassName="Child",
        )
        rel._set_parent(parent)

        RelationshipEditorWidget.make_class_relation_bidirectional(rel, bsdd_dict, "add")
        assert any(cr.RelationType == "IsChildOf" for cr in child.ClassRelations)

        RelationshipEditorWidget.make_class_relation_bidirectional(rel, bsdd_dict, "remove")
        assert not any(cr.RelationType == "IsChildOf" for cr in child.ClassRelations)

    def test_unknown_relation_type_is_noop(self):
        parent, child, bsdd_dict = self._setup()
        child_uri = class_utils.build_bsdd_uri(child, bsdd_dict)

        rel = BsddClassRelation(
            RelationType="HasMaterial",
            RelatedClassUri=child_uri,
            RelatedClassName="Child",
        )
        rel._set_parent(parent)

        RelationshipEditorWidget.make_class_relation_bidirectional(rel, bsdd_dict, "add")
        assert child.ClassRelations == []


# ---------------------------------------------------------------------------
# make_property_relation_bidirectional
# ---------------------------------------------------------------------------

class TestMakePropertyRelationBidirectional:
    def test_adds_inverse_property_relation(self):
        p1 = BsddProperty(Code="P1", Name="P1", DataType="String")
        p2 = BsddProperty(Code="P2", Name="P2", DataType="String")
        bsdd_dict = _make_dict(properties=[p1, p2])

        p2_uri = prop_utils.build_bsdd_uri(p2, bsdd_dict)
        rel = BsddPropertyRelation(
            RelationType="IsEqualTo",
            RelatedPropertyUri=p2_uri,
            RelatedPropertyName="P2",
        )
        rel._set_parent(p1)

        RelationshipEditorWidget.make_property_relation_bidirectional(rel, bsdd_dict, "add")

        p1_uri = prop_utils.build_bsdd_uri(p1, bsdd_dict)
        assert any(
            pr.RelationType == "IsEqualTo" and pr.RelatedPropertyUri == p1_uri
            for pr in p2.PropertyRelations
        )
