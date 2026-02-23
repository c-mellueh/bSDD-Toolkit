"""
Tests for the class_tree_view module.

Coverage:
  - ClassTreeView pure-logic helpers  (no Qt model required)
  - ClassTreeModel  Qt item-model behaviour
  - ClassTreeView   operations on the model (add / delete / move)
  - classes_to_payload serialization
"""
from __future__ import annotations

import pytest
from PySide6.QtCore import QModelIndex
from bsdd_json.models import BsddClass, BsddDictionary
from bsdd_gui.tool import ClassTreeView


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_class(code: str, name: str | None = None, parent: str | None = None) -> BsddClass:
    return BsddClass(Code=code, Name=name or code, ParentClassCode=parent)


# ---------------------------------------------------------------------------
# 1. depth_of  –  pure Python, no Qt
# ---------------------------------------------------------------------------

class TestDepthOf:
    def test_root_class_has_depth_zero(self):
        classes = {"A": {"Code": "A"}}
        assert ClassTreeView.depth_of("A", classes) == 0

    def test_direct_child_has_depth_one(self):
        classes = {
            "A": {"Code": "A"},
            "B": {"Code": "B", "ParentClassCode": "A"},
        }
        assert ClassTreeView.depth_of("B", classes) == 1

    def test_grandchild_has_depth_two(self):
        classes = {
            "A": {"Code": "A"},
            "B": {"Code": "B", "ParentClassCode": "A"},
            "C": {"Code": "C", "ParentClassCode": "B"},
        }
        assert ClassTreeView.depth_of("C", classes) == 2

    def test_unknown_code_returns_zero(self):
        assert ClassTreeView.depth_of("MISSING", {}) == 0


# ---------------------------------------------------------------------------
# 2. is_payload_valid  –  pure Python, no Qt
# ---------------------------------------------------------------------------

class TestIsPayloadValid:
    def test_valid_payload(self):
        payload = {"kind": "BsddClassTransfer", "version": 1, "classes": []}
        assert ClassTreeView.is_payload_valid(payload) is True

    def test_wrong_kind_is_invalid(self):
        payload = {"kind": "SomethingElse", "classes": []}
        assert ClassTreeView.is_payload_valid(payload) is False

    def test_missing_classes_key_is_invalid(self):
        payload = {"kind": "BsddClassTransfer"}
        assert ClassTreeView.is_payload_valid(payload) is False

    def test_none_payload_is_invalid(self):
        assert ClassTreeView.is_payload_valid(None) is False

    def test_empty_dict_is_invalid(self):
        assert ClassTreeView.is_payload_valid({}) is False


# ---------------------------------------------------------------------------
# 3. create_class_from_mime  –  pure Python, no Qt
# ---------------------------------------------------------------------------

class TestCreateClassFromMime:
    def test_basic_creation(self):
        rc = {"Code": "OLD", "Name": "My Class", "ClassType": "Class"}
        result = ClassTreeView.create_class_from_mime(rc, "NEW", {}, set(), None)
        assert result is not None
        assert result.Code == "NEW"
        assert result.Name == "My Class"
        assert result.ParentClassCode is None

    def test_parent_code_is_remapped(self):
        rc = {"Code": "CHILD", "Name": "Child", "ClassType": "Class", "ParentClassCode": "OLD_P"}
        result = ClassTreeView.create_class_from_mime(rc, "CHILD_NEW", {"OLD_P": "NEW_P"}, set(), None)
        assert result.ParentClassCode == "NEW_P"

    def test_root_in_import_attaches_to_dest_parent(self):
        dest = make_class("DEST", "Destination")
        rc = {"Code": "ROOT", "Name": "Root", "ClassType": "Class"}
        # ROOT is in root_codes → should be attached to dest_parent
        result = ClassTreeView.create_class_from_mime(rc, "ROOT_NEW", {"ROOT": "ROOT_NEW"}, {"ROOT"}, dest)
        assert result.ParentClassCode == "DEST"

    def test_invalid_data_returns_none(self):
        # A missing required field like Name should produce None
        rc = {"Code": "X"}  # Name is required
        result = ClassTreeView.create_class_from_mime(rc, "X_NEW", {}, set(), None)
        assert result is None

    def test_get_allowed_class_types(self):
        types = ClassTreeView.get_allowed_class_types()
        assert "Class" in types
        assert "Material" in types
        assert "GroupOfProperties" not in types


# ---------------------------------------------------------------------------
# 4. ClassTreeModel – Qt item-model behaviour
# ---------------------------------------------------------------------------

class TestClassTreeModel:
    def test_empty_dictionary_has_no_rows(self, model_fixture):
        _, model, _ = model_fixture
        assert model.rowCount(QModelIndex()) == 0

    def test_root_classes_appear_as_rows(self, model_fixture):
        _, model, dictionary = model_fixture
        ClassTreeView.add_class_to_dictionary(make_class("A"), dictionary)
        ClassTreeView.add_class_to_dictionary(make_class("B"), dictionary)
        assert model.rowCount(QModelIndex()) == 2

    def test_child_class_appears_under_parent(self, model_fixture):
        _, model, dictionary = model_fixture
        parent = make_class("P")
        child = make_class("C", parent="P")
        ClassTreeView.add_class_to_dictionary(parent, dictionary)
        ClassTreeView.add_class_to_dictionary(child, dictionary)

        # One root row
        assert model.rowCount(QModelIndex()) == 1
        # One child row
        parent_index = model.index(0, 0, QModelIndex())
        assert model.rowCount(parent_index) == 1

    def test_group_of_properties_is_hidden(self, model_fixture):
        _, model, dictionary = model_fixture
        gop = BsddClass(Code="GOP", Name="Group", ClassType="GroupOfProperties")
        ClassTreeView.add_class_to_dictionary(gop, dictionary)
        # ClassTreeView filters out GroupOfProperties
        assert model.rowCount(QModelIndex()) == 0

    def test_index_internalPointer_returns_class(self, model_fixture):
        _, model, dictionary = model_fixture
        cls = make_class("X", "Class X")
        ClassTreeView.add_class_to_dictionary(cls, dictionary)

        idx = model.index(0, 0, QModelIndex())
        assert idx.internalPointer() is cls

    def test_parent_of_root_is_invalid(self, model_fixture):
        _, model, dictionary = model_fixture
        ClassTreeView.add_class_to_dictionary(make_class("R"), dictionary)

        idx = model.index(0, 0, QModelIndex())
        assert not model.parent(idx).isValid()

    def test_parent_of_child_is_parent_class(self, model_fixture):
        _, model, dictionary = model_fixture
        parent = make_class("P")
        child = make_class("C", parent="P")
        ClassTreeView.add_class_to_dictionary(parent, dictionary)
        ClassTreeView.add_class_to_dictionary(child, dictionary)

        parent_idx = model.index(0, 0, QModelIndex())
        child_idx = model.index(0, 0, parent_idx)
        computed_parent = model.parent(child_idx)

        assert computed_parent.internalPointer() is parent


# ---------------------------------------------------------------------------
# 5. add_class_to_dictionary
# ---------------------------------------------------------------------------

class TestAddClass:
    def test_class_is_added_to_dictionary(self, model_fixture):
        _, model, dictionary = model_fixture
        cls = make_class("NEW")
        ClassTreeView.add_class_to_dictionary(cls, dictionary)
        assert cls in dictionary.Classes

    def test_duplicate_code_is_not_added_twice(self, model_fixture):
        _, model, dictionary = model_fixture
        cls = make_class("DUP")
        ClassTreeView.add_class_to_dictionary(cls, dictionary)
        ClassTreeView.add_class_to_dictionary(cls, dictionary)
        assert dictionary.Classes.count(cls) == 1

    def test_group_of_properties_not_added_to_model(self, model_fixture):
        _, model, dictionary = model_fixture
        gop = BsddClass(Code="GOP", Name="G", ClassType="GroupOfProperties")
        ClassTreeView.add_class_to_dictionary(gop, dictionary)
        assert model.rowCount(QModelIndex()) == 0


# ---------------------------------------------------------------------------
# 6. delete_class
# ---------------------------------------------------------------------------

class TestDeleteClass:
    def test_class_is_removed_from_dictionary(self, model_fixture):
        _, model, dictionary = model_fixture
        cls = make_class("DEL")
        ClassTreeView.add_class_to_dictionary(cls, dictionary)
        assert model.rowCount(QModelIndex()) == 1

        ClassTreeView.delete_class(cls, dictionary)
        assert cls not in dictionary.Classes
        assert model.rowCount(QModelIndex()) == 0

    def test_children_are_reparented_on_delete(self, model_fixture):
        _, model, dictionary = model_fixture
        parent = make_class("P")
        child = make_class("C", parent="P")
        ClassTreeView.add_class_to_dictionary(parent, dictionary)
        ClassTreeView.add_class_to_dictionary(child, dictionary)

        ClassTreeView.delete_class(parent, dictionary)

        # Child survives and becomes a root
        assert child in dictionary.Classes
        assert child.ParentClassCode is None
        assert model.rowCount(QModelIndex()) == 1

    def test_delete_with_children_removes_entire_subtree(self, model_fixture):
        _, model, dictionary = model_fixture
        parent = make_class("P")
        child = make_class("C", parent="P")
        ClassTreeView.add_class_to_dictionary(parent, dictionary)
        ClassTreeView.add_class_to_dictionary(child, dictionary)

        ClassTreeView.delete_class_with_children(parent, dictionary)

        assert parent not in dictionary.Classes
        assert child not in dictionary.Classes
        assert model.rowCount(QModelIndex()) == 0


# ---------------------------------------------------------------------------
# 7. move_class
# ---------------------------------------------------------------------------

class TestMoveClass:
    def test_move_child_to_root(self, model_fixture):
        _, model, dictionary = model_fixture
        parent = make_class("P")
        child = make_class("C", parent="P")
        ClassTreeView.add_class_to_dictionary(parent, dictionary)
        ClassTreeView.add_class_to_dictionary(child, dictionary)

        ClassTreeView.move_class(child, None, dictionary)

        assert child.ParentClassCode is None
        assert model.rowCount(QModelIndex()) == 2

    def test_move_class_to_different_parent(self, model_fixture):
        _, model, dictionary = model_fixture
        p1 = make_class("P1")
        p2 = make_class("P2")
        child = make_class("C", parent="P1")
        for cls in (p1, p2, child):
            ClassTreeView.add_class_to_dictionary(cls, dictionary)

        ClassTreeView.move_class(child, p2, dictionary)

        assert child.ParentClassCode == "P2"


# ---------------------------------------------------------------------------
# 8. classes_to_payload
# ---------------------------------------------------------------------------

class TestClassesToPayload:
    def test_payload_has_required_keys(self, model_fixture):
        _, model, dictionary = model_fixture
        cls = make_class("A")
        ClassTreeView.add_class_to_dictionary(cls, dictionary)

        payload = ClassTreeView.classes_to_payload([cls])

        assert payload["kind"] == "BsddClassTransfer"
        assert "roots" in payload
        assert "classes" in payload
        assert "properties" in payload

    def test_root_codes_are_correct(self, model_fixture):
        _, model, dictionary = model_fixture
        cls = make_class("ROOT_X")
        ClassTreeView.add_class_to_dictionary(cls, dictionary)

        payload = ClassTreeView.classes_to_payload([cls])
        assert "ROOT_X" in payload["roots"]

    def test_collapsed_node_includes_subtree(self, model_fixture):
        _, model, dictionary = model_fixture
        parent = make_class("P")
        child = make_class("C", parent="P")
        ClassTreeView.add_class_to_dictionary(parent, dictionary)
        ClassTreeView.add_class_to_dictionary(child, dictionary)

        # P is "collapsed" → subtree should be included
        payload = ClassTreeView.classes_to_payload([parent], unexpanded_classes={"P"})
        codes = {c["Code"] for c in payload["classes"]}
        assert "P" in codes
        assert "C" in codes

    def test_expanded_node_excludes_subtree(self, model_fixture):
        _, model, dictionary = model_fixture
        parent = make_class("P")
        child = make_class("C", parent="P")
        ClassTreeView.add_class_to_dictionary(parent, dictionary)
        ClassTreeView.add_class_to_dictionary(child, dictionary)

        # P is "expanded" (not in unexpanded set) → only P itself
        payload = ClassTreeView.classes_to_payload([parent], unexpanded_classes=set())
        codes = {c["Code"] for c in payload["classes"]}
        assert "P" in codes
        assert "C" not in codes

    def test_no_duplicate_classes_in_payload(self, model_fixture):
        _, model, dictionary = model_fixture
        cls = make_class("ONCE")
        ClassTreeView.add_class_to_dictionary(cls, dictionary)

        payload = ClassTreeView.classes_to_payload([cls, cls])
        codes = [c["Code"] for c in payload["classes"]]
        assert codes.count("ONCE") == 1
