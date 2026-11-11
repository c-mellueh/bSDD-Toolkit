"""Strict inheritance: children always have all class properties of their parent."""

from __future__ import annotations

import pytest

from bsdd_web.ops import OpError


def keys(h, code):
    return sorted((cp.PropertySet, cp.PropertyCode) for cp in h.cls(code).ClassProperties)


@pytest.fixture
def strict(h):
    added = h.run("inheritance.set_strict", enabled=True)
    assert added == 2  # Wall's two class properties copied to Inner Wall
    return h


def test_enabling_fills_children(strict):
    h = strict
    assert keys(h, "InnerWall") == [("Common", "Material"), ("Geometry", "Height")]
    # values are copied
    inner_material = next(cp for cp in h.cls("InnerWall").ClassProperties if cp.PropertyCode == "Material")
    assert [v.Code for v in inner_material.AllowedValues] == ["concrete"]


def test_disabled_by_default_changes_nothing(h):
    assert h.cls("InnerWall").ClassProperties == []
    h.run("cp.add_properties", class_code="Building", property_codes=["Height"], pset="Base")
    assert h.cls("Wall").ClassProperties[0].PropertySet == "Geometry"
    assert len(h.cls("Wall").ClassProperties) == 2


def test_new_parent_property_goes_to_all_descendants(strict):
    h = strict
    h.run("cp.add_properties", class_code="Building", property_codes=["FireRating"], pset="Safety")
    for code in ("Wall", "Door", "InnerWall"):
        assert ("Safety", "FireRating") in keys(h, code)


def test_new_child_and_moved_class_get_parent_properties(strict):
    h = strict
    code = h.run("class.create", data={"Name": "Curtain Wall", "ParentClassCode": "Wall"})
    assert keys(h, code) == keys(h, "Wall")
    h.run("class.move", codes=["Door"], parent_code="Wall")
    assert set(keys(h, "Wall")) <= set(keys(h, "Door"))


def test_inherited_cannot_be_deleted_or_rekeyed_in_child(strict):
    h = strict
    with pytest.raises(OpError, match="inherited from 'Wall'"):
        h.run("cp.delete", class_code="InnerWall", codes=["height"])


def test_inherited_pset_cannot_be_renamed_or_deleted_in_child(h):
    h.run("inheritance.set_strict", enabled=True)
    with pytest.raises(OpError, match="inherited"):
        h.run("pset.rename", class_code="InnerWall", old="Geometry", new="Geo")


def test_inherited_property_reference_cannot_change_in_child(h):
    h.run("inheritance.set_strict", enabled=True)
    with pytest.raises(OpError, match="inherited"):
        h.run("cp.update", class_code="InnerWall", code="height", data={"PropertyCode": "Material"})


def test_child_values_can_be_changed(strict):
    h = strict
    h.run("cp.update", class_code="InnerWall", code="height", data={"IsRequired": False, "Unit": "mm"})
    cp = next(cp for cp in h.cls("InnerWall").ClassProperties if cp.Code == "height")
    assert cp.IsRequired is False and cp.Unit == "mm"


def test_parent_changes_propagate(strict):
    h = strict
    # value change: copied where the child still had the old value
    h.run("cp.update", class_code="InnerWall", code="height", data={"Unit": "mm"})
    h.run("cp.update", class_code="Wall", code="height", data={"IsRequired": False, "Unit": "cm"})
    inner = next(cp for cp in h.cls("InnerWall").ClassProperties if cp.Code == "height")
    assert inner.IsRequired is False
    assert inner.Unit == "mm"  # overridden in the child: kept
    # pset rename and delete
    h.run("pset.rename", class_code="Wall", old="Geometry", new="Dimensions")
    assert ("Dimensions", "Height") in keys(h, "InnerWall")
    assert ("Geometry", "Height") not in keys(h, "InnerWall")
    h.run("cp.delete", class_code="Wall", codes=["material"])
    assert keys(h, "InnerWall") == [("Dimensions", "Height")]


def test_child_own_properties_allowed(strict):
    h = strict
    h.run("cp.add_properties", class_code="InnerWall", property_codes=["FireRating"], pset="Safety")
    h.run("cp.delete", class_code="InnerWall", codes=[next(cp.Code for cp in h.cls("InnerWall").ClassProperties if cp.PropertyCode == "FireRating")])
    assert ("Safety", "FireRating") not in keys(h, "InnerWall")


def test_groups_of_properties_take_no_part(strict):
    h = strict
    assert h.cls("Pset_Fire").ClassProperties[0].PropertyCode == "FireRating"
    h.run("class.create", data={"Name": "Sub", "ParentClassCode": "Pset_Fire", "ClassType": "GroupOfProperties"})
    sub = next(c for c in h.d.Classes if c.Name == "Sub")
    assert sub.ClassProperties == []


def test_predefined_pset_link_is_inherited(strict):
    h = strict
    h.run("pset.create", class_code="Wall", name="Pset_Fire")
    links = lambda code: [cr.RelatedClassName for cr in h.cls(code).ClassRelations if cr.RelationType == "HasReference"]
    assert links("Wall") == ["Pset_Fire"]
    assert links("InnerWall") == ["Pset_Fire"]
    assert ("Pset_Fire", "FireRating") in keys(h, "InnerWall")
    # new child gets the link too
    code = h.run("class.create", data={"Name": "Curtain Wall", "ParentClassCode": "Wall"})
    assert links(code) == ["Pset_Fire"]
    # cannot be removed in the child
    with pytest.raises(OpError, match="inherited"):
        h.run("pset.delete", class_code="InnerWall", names=["Pset_Fire"])


def test_predefined_pset_link_removed_with_parent(strict):
    h = strict
    h.run("pset.create", class_code="Wall", name="Pset_Fire")
    h.run("pset.delete", class_code="Wall", names=["Pset_Fire"])
    assert not [cr for cr in h.cls("InnerWall").ClassRelations if cr.RelationType == "HasReference"]
    assert ("Pset_Fire", "FireRating") not in keys(h, "InnerWall")


def test_enabling_adds_existing_links(h):
    h.run("pset.create", class_code="Wall", name="Pset_Fire")
    assert not h.cls("InnerWall").ClassRelations
    h.run("inheritance.set_strict", enabled=True)
    assert [cr.RelatedClassName for cr in h.cls("InnerWall").ClassRelations] == ["Pset_Fire"]
