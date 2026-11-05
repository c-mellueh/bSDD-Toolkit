from __future__ import annotations

import pytest

from bsdd_web.ops import OpError

URI = "https://identifier.buildingsmart.org/uri/org/dict/1.0/class/"
PURI = "https://identifier.buildingsmart.org/uri/org/dict/1.0/prop/"


def test_create_class_slug_and_unique(h):
    code = h.run("class.create", data={"Name": "Über Wand"}, parent_code="Building")
    assert code == "Ueber-Wand"
    assert h.cls(code).ParentClassCode == "Building"
    with pytest.raises(OpError):
        h.run("class.create", data={"Code": "Wall", "Name": "dup"})


def test_rename_class_cascades(h):
    h.run("relation.add", kind="class", code="Door", relation={"RelationType": "IsSimilarTo", "RelatedClassUri": "Wall"})
    assert h.cls("Wall").ClassRelations[0].RelationType == "IsSimilarTo"  # inverse created
    h.run("class.update", code="Wall", data={"Code": "Wall2", "Name": "Wall 2"})
    assert h.cls("InnerWall").ParentClassCode == "Wall2"
    rel = h.cls("Door").ClassRelations[0]
    assert rel.RelatedClassUri == URI + "Wall2"
    assert rel.RelatedClassName == "Wall 2"


def test_move_prevents_cycles_and_orders(h):
    with pytest.raises(OpError):
        h.run("class.move", codes=["Building"], parent_code="InnerWall")
    h.run("class.move", codes=["Door"], parent_code="Wall", before_code="InnerWall")
    codes = [c.Code for c in h.d.Classes]
    assert codes.index("Door") < codes.index("InnerWall")
    assert h.cls("Door").ParentClassCode == "Wall"


def test_delete_reparents_and_removes_relations(h):
    h.run("relation.add", kind="class", code="Door", relation={"RelationType": "HasPart", "RelatedClassUri": "Wall"})
    assert h.cls("Wall").ClassRelations[0].RelationType == "IsPartOf"
    h.run("class.delete", codes=["Wall"])
    assert h.cls("Wall") is None
    assert h.cls("InnerWall").ParentClassCode == "Building"
    assert h.cls("Door").ClassRelations == []


def test_delete_recursive(h):
    h.run("class.delete", codes=["Building"], recursive=True)
    assert {c.Code for c in h.d.Classes} == {"Pset_Fire"}


def test_group(h):
    code = h.run("class.group", codes=["Wall", "Door", "InnerWall"], name="Elements")
    assert h.cls(code).ParentClassCode == "Building"
    assert h.cls("Wall").ParentClassCode == code
    assert h.cls("InnerWall").ParentClassCode == "Wall"


def test_paste_classes_remaps_codes(h):
    payload = {
        "classes": [h.cls("Wall").model_dump(mode="json"), h.cls("InnerWall").model_dump(mode="json")],
        "properties": [],
    }
    new = h.run("class.paste", payload=payload, parent_code="Door")
    assert new == ["Wall-2", "InnerWall-2"]
    assert h.cls("Wall-2").ParentClassCode == "Door"
    assert h.cls("InnerWall-2").ParentClassCode == "Wall-2"


def test_property_rename_cascades(h):
    h.run("relation.add", kind="property", code="Material", relation={"RelationType": "IsEqualTo", "RelatedPropertyUri": "Height"})
    h.run("prop.update", code="Height", data={"Code": "Hoehe"})
    assert h.cls("Wall").ClassProperties[0].PropertyCode == "Hoehe"
    assert h.prop("Material").PropertyRelations[0].RelatedPropertyUri == PURI + "Hoehe"
    assert h.prop("Hoehe").PropertyRelations[0].RelationType == "IsEqualTo"


def test_property_delete_removes_class_properties(h):
    h.run("prop.delete", codes=["Height"])
    assert [cp.Code for cp in h.cls("Wall").ClassProperties] == ["material"]


def test_class_property_validation(h):
    with pytest.raises(OpError):
        h.run("cp.create", class_code="Door", data={"PropertyCode": "Unknown", "PropertySet": "X"})
    code = h.run("cp.create", class_code="Door", data={"PropertyCode": "Height", "PropertySet": "Geo", "Unit": "m"})
    assert code == "Height"
    assert h.cls("Door").ClassProperties[0].Unit == "m"
    h.run("cp.update", class_code="Door", code="Height", data={"Unit": "mm", "PropertyUri": "https://example.org/x", "PropertyCode": None})
    cp = h.cls("Door").ClassProperties[0]
    assert cp.Unit == "mm" and cp.PropertyUri == "https://example.org/x" and cp.PropertyCode is None


def test_psets_temporary_rename_delete(h):
    name = h.run("pset.create", class_code="Door", name="Custom")
    assert h.ctx.extras.temporary_psets == {"Door": ["Custom"]}
    h.run("cp.add_properties", class_code="Door", property_codes=["Height"], pset=name)
    assert h.ctx.extras.temporary_psets == {}
    h.run("pset.rename", class_code="Door", old="Custom", new="Renamed")
    assert h.cls("Door").ClassProperties[0].PropertySet == "Renamed"
    h.run("pset.delete", class_code="Door", names=["Renamed"])
    assert h.cls("Door").ClassProperties == []


def test_group_of_properties_linking(h):
    h.run("pset.create", class_code="Door", name="Pset_Fire")
    door = h.cls("Door")
    assert [cp.Code for cp in door.ClassProperties] == ["rating"]
    assert door.ClassRelations[0].RelationType == "HasReference"
    # add to GoP -> propagated
    h.run("cp.create", class_code="Pset_Fire", data={"PropertyCode": "Material"})
    assert {cp.Code for cp in h.cls("Door").ClassProperties} == {"rating", "Material"}
    # edit on GoP -> mirrored
    h.run("cp.update", class_code="Pset_Fire", code="rating", data={"IsRequired": True})
    assert next(cp for cp in h.cls("Door").ClassProperties if cp.Code == "rating").IsRequired is True
    # sync allowed values
    h.run("cp.update", class_code="Pset_Fire", code="rating", data={"AllowedValues": [{"Code": "f30", "Value": "F30"}]})
    h.run("gop.sync_allowed_values", class_code="Pset_Fire", codes=["rating"])
    assert next(cp for cp in h.cls("Door").ClassProperties if cp.Code == "rating").AllowedValues[0].Code == "f30"
    # rename GoP -> pset renamed in referencing classes
    h.run("class.update", code="Pset_Fire", data={"Name": "Pset_FireSafety"})
    assert {cp.PropertySet for cp in h.cls("Door").ClassProperties} == {"Pset_FireSafety"}
    # delete pset removes relation
    h.run("pset.delete", class_code="Door", names=["Pset_FireSafety"])
    assert h.cls("Door").ClassRelations == []


def test_dictionary_version_change_rewrites_uris(h):
    h.run("relation.add", kind="class", code="Door", relation={"RelationType": "IsSimilarTo", "RelatedClassUri": "Wall"})
    h.run("dict.update", data={"DictionaryVersion": "2.0", "OrganizationCode": "neworg"})
    assert h.cls("Door").ClassRelations[0].RelatedClassUri == "https://identifier.buildingsmart.org/uri/neworg/dict/2.0/class/Wall"
    with pytest.raises(OpError):
        h.run("dict.update", data={"DictionaryVersion": "v2"})
    with pytest.raises(OpError):
        h.run("dict.update", data={"UseOwnUri": True})


def test_loin_selection_and_xml_roundtrip(h):
    from bsdd_web.services.loin import build_loin_xml, ensure_state, parse_loin_xml, selection_from_state, spec_key

    h.run("loin.init")
    state = h.ctx.extras.loin
    key = spec_key(state["purposes"][0]["guid"], state["milestones"][0]["guid"])
    h.run("loin.set_properties_included", spec=key, class_code="Wall", items=[["Geometry", "height"]], included=True)
    assert set(state["added_classes"]) == {"Wall", "Building"}
    sel = selection_from_state(state, [key])
    wall = h.cls("Wall")
    assert sel.class_included(wall)
    assert sel.property_included(wall, wall.ClassProperties[0])
    assert not sel.property_included(wall, wall.ClassProperties[1])
    xml, count = build_loin_xml(state, h.d, [key])
    assert count == 1
    parsed = ensure_state(parse_loin_xml(xml, h.d))
    assert parsed["specs"][key]["properties"]["Wall"] == [["Geometry", "height"]]
    # class rename follows
    h.run("class.update", code="Wall", data={"Code": "Wall2"})
    assert "Wall2" in h.ctx.extras.loin["specs"][key]["classes"]


def test_exports_run(h):
    from bsdd_web.services import excel, ids, iso23386, revit
    from bsdd_web.services.loin import Selection

    sel = Selection()
    data, n = excel.export_excel(h.d, sel, "de")
    assert data[:2] == b"PK" and n == 4
    import openpyxl, io

    wb = openpyxl.load_workbook(io.BytesIO(data))
    assert wb.sheetnames[0] == "Übersicht"
    xml, n = iso23386.export_iso23386(h.d, sel)
    assert b"<Container>" in xml
    txt, n = revit.export_custom_psets(h.d, sel)
    assert b"PropertySet:\tGeometry\tI\tIfcWallSTANDARD" in txt
    sp, n = revit.export_shared_parameters(h.d, sel)
    assert sp.decode("utf-16").startswith("# This is a Revit shared parameter file.")
    ids_xml, n = ids.export_ids(h.d, sel)
    assert b"Check for Wall" in ids_xml and n == 4


def test_ifc_split():
    from bsdd_web.services.ifc import split_ifc_term

    assert split_ifc_term("IfcElectricMotorSYNCHRONOUS") == ("IfcElectricMotor", "SYNCHRONOUS")
    assert split_ifc_term("IfcWall") == ("IfcWall", None)
    assert split_ifc_term("Something") == ("Something", None)


def _shell_patch(base, new):
    """What the in-browser shell sends: diff plus guards recorded against its base."""
    import copy

    from bsdd_web import jsonpatch as jp

    work = copy.deepcopy(base)
    patch = jp.diff(base, new)
    guards = []
    for step in patch:
        guards.append(jp._expectation(work, step))
        jp.apply(work, [step], in_place=True)
    return patch, guards


def test_dict_patch_merges_and_detects_conflicts(h):
    base = h.d.model_dump(mode="json", exclude_none=True)
    shell = h.d.model_copy(deep=True)
    wall = next(c for c in shell.Classes if c.Code == "Wall")
    wall.Description = "from shell"
    patch, guards = _shell_patch(base, shell.model_dump(mode="json", exclude_none=True))
    # someone else edits another class meanwhile: still applies, nothing is lost
    h.run("class.update", code="Door", data={"Definition": "edited in UI"})
    assert h.run("dict.patch", patch=patch, guards=guards) == len(patch)
    assert h.cls("Wall").Description == "from shell"
    assert h.cls("Door").Definition == "edited in UI"
    # a concurrent change of the same value is rejected instead of overwritten
    base = h.d.model_dump(mode="json", exclude_none=True)
    shell = h.d.model_copy(deep=True)
    next(c for c in shell.Classes if c.Code == "Wall").Description = "shell again"
    patch, guards = _shell_patch(base, shell.model_dump(mode="json", exclude_none=True))
    h.run("class.update", code="Wall", data={"Description": "UI wins"})
    with pytest.raises(OpError):
        h.run("dict.patch", patch=patch, guards=guards)
    assert h.cls("Wall").Description == "UI wins"
