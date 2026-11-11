"""
Tests for the GroupOfProperties module (tool/group_of_properties.py).

Covers the pure state-management helpers that do not require a live Qt widget.
"""

from __future__ import annotations

import pytest
from bsdd_json.models import BsddClass, BsddClassProperty

from bsdd_gui.tool import GroupOfProperties
from bsdd_gui.tool.group_of_properties import GopClassView


# ---------------------------------------------------------------------------
# Fixture: restore active class/property state after each test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_active_state():
    yield
    GroupOfProperties.set_active_class(None)
    GroupOfProperties.set_active_property(None)


# ---------------------------------------------------------------------------
# generate_pset_name
# ---------------------------------------------------------------------------


class TestGeneratePsetName:
    def test_returns_class_name(self):
        cls = BsddClass(Code="C", Name="MyClass")
        assert GroupOfProperties.generate_pset_name(cls) == "MyClass"

    def test_returns_empty_string_for_none(self):
        assert GroupOfProperties.generate_pset_name(None) == ""


# ---------------------------------------------------------------------------
# get_active_class / set_active_class
# ---------------------------------------------------------------------------


class TestActiveClass:
    def test_default_active_class_is_none(self):
        GroupOfProperties.set_active_class(None)
        assert GroupOfProperties.get_active_class() is None

    def test_set_and_get_active_class(self):
        cls = BsddClass(Code="A", Name="A")
        GroupOfProperties.set_active_class(cls)
        assert GroupOfProperties.get_active_class() is cls


# ---------------------------------------------------------------------------
# get_active_property / set_active_property
# ---------------------------------------------------------------------------


class TestActiveProperty:
    def test_default_active_property_is_none(self):
        GroupOfProperties.set_active_property(None)
        assert GroupOfProperties.get_active_property() is None

    def test_set_and_get_active_property(self):
        prop = BsddClassProperty(Code="P", PropertySet="S", PropertyCode="X")
        GroupOfProperties.set_active_property(prop)
        assert GroupOfProperties.get_active_property() is prop


# ---------------------------------------------------------------------------
# GopClassView.get_allowed_class_types
# ---------------------------------------------------------------------------


class TestGopClassViewAllowedClassTypes:
    def test_contains_group_of_properties(self):
        types = GopClassView.get_allowed_class_types()
        assert "GroupOfProperties" in types

    def test_returns_list(self):
        assert isinstance(GopClassView.get_allowed_class_types(), list)


# ---------------------------------------------------------------------------
# Settings: code prefix, automatic creation, prefix rename
# ---------------------------------------------------------------------------


@pytest.fixture()
def temp_appdata(tmp_path, monkeypatch):
    from bsdd_gui.tool.appdata import Appdata

    ini = str(tmp_path / "settings.ini")
    monkeypatch.setattr(Appdata, "get_ini_path", classmethod(lambda cls: ini))
    monkeypatch.setattr(Appdata, "get_appdata_folder", classmethod(lambda cls: str(tmp_path)))
    return Appdata


class TestGopSettings:
    def test_defaults(self, temp_appdata):
        assert GroupOfProperties.get_prefix() == "EPset_"
        assert GroupOfProperties.is_auto_create() is False

    def test_roundtrip(self, temp_appdata):
        GroupOfProperties.set_prefix("X_")
        GroupOfProperties.set_auto_create(True)
        assert GroupOfProperties.get_prefix() == "X_"
        assert GroupOfProperties.is_auto_create() is True

    def test_empty_prefix_allowed(self, temp_appdata):
        GroupOfProperties.set_prefix("")
        assert GroupOfProperties.get_prefix() == ""

    @pytest.mark.parametrize("prefix", ["a b", "x/", "ä" * 31])
    def test_invalid_prefix(self, prefix):
        assert not GroupOfProperties.is_prefix_valid(prefix)


class TestCreateGroupOfProperties:
    def test_creates_prefixed_unique_code(self, dictionary):
        dictionary.Classes.append(BsddClass(Code="EPset_Fire-Safety", Name="Other"))
        gop = GroupOfProperties.create_group_of_properties("Fire Safety", "EPset_", dictionary)
        assert gop in dictionary.Classes
        assert gop.ClassType == "GroupOfProperties"
        assert gop.Name == "Fire Safety"
        assert gop.Code.startswith("EPset_Fire-Safety") and gop.Code != "EPset_Fire-Safety"


class TestRenamePrefix:
    def _setup(self, dictionary):
        from bsdd_json.models import BsddClassRelation
        from bsdd_json.utils import class_utils

        gop = BsddClass(Code="EPset_Fire", Name="Fire", ClassType="GroupOfProperties")
        other = BsddClass(Code="EPset_Wall", Name="Wall")  # not a GoP: stays
        wall = BsddClass(Code="Wall", Name="Wall")
        for c in (gop, other, wall):
            dictionary.Classes.append(c)
            c._set_parent(dictionary)
        uri = class_utils.build_bsdd_uri(gop, dictionary)
        rel = BsddClassRelation(RelationType="HasReference", RelatedClassUri=uri)
        wall.ClassRelations.append(rel)
        return gop, other, rel

    def test_renames_gops_and_relations(self, dictionary):
        from bsdd_json.utils import class_utils

        gop, other, rel = self._setup(dictionary)
        assert GroupOfProperties.rename_prefix("EPset_", "X_", dictionary) == 1
        assert gop.Code == "X_Fire"
        assert other.Code == "EPset_Wall"
        assert rel.RelatedClassUri == class_utils.build_bsdd_uri(gop, dictionary)

    def test_clash_changes_nothing(self, dictionary):
        gop, _, rel = self._setup(dictionary)
        dictionary.Classes.append(BsddClass(Code="X_Fire", Name="Taken"))
        before = rel.RelatedClassUri
        with pytest.raises(ValueError):
            GroupOfProperties.rename_prefix("EPset_", "X_", dictionary)
        assert gop.Code == "EPset_Fire"
        assert rel.RelatedClassUri == before
