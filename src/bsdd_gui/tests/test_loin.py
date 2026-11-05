"""
Tests for the LOIN tool (tool/loin.py): ISO 7817-3 representation of property selections.
"""

from __future__ import annotations

import pytest
from bsdd_json.models import BsddDictionary
from bsdd_json.utils import class_utils

from bsdd_gui import tool

GOP_URI_PLACEHOLDER = "__gop__"


@pytest.fixture()
def linked_dictionary():
    """A class whose pset 'Pset_Fire' is linked (HasReference) to a Group of Properties."""
    data = {
        "OrganizationCode": "org",
        "DictionaryCode": "dict",
        "DictionaryVersion": "1.0",
        "LanguageIsoCode": "en-GB",
        "LanguageOnly": False,
        "UseOwnUri": False,
        "Classes": [
            {
                "Code": "Pset_Fire",
                "Name": "Pset_Fire",
                "ClassType": "GroupOfProperties",
                "ClassProperties": [
                    {"Code": "rating", "PropertyCode": "FireRating", "PropertySet": "Pset_Fire"},
                    {"Code": "material", "PropertyCode": "Material", "PropertySet": "Pset_Fire"},
                ],
            },
            {
                "Code": "Wall",
                "Name": "Wall",
                "ClassProperties": [
                    {"Code": "rating", "PropertyCode": "FireRating", "PropertySet": "Pset_Fire"},
                    {"Code": "material", "PropertyCode": "Material", "PropertySet": "Pset_Fire"},
                ],
                "ClassRelations": [{"RelationType": "HasReference", "RelatedClassUri": GOP_URI_PLACEHOLDER}],
            },
        ],
        "Properties": [
            {"Code": "FireRating", "Name": "Fire rating", "DataType": "String"},
            {"Code": "Material", "Name": "Material", "DataType": "String"},
        ],
    }
    d = BsddDictionary.model_validate(data)
    gop = next(c for c in d.Classes if c.Code == "Pset_Fire")
    gop_uri = class_utils.build_bsdd_uri(gop, d)
    wall = next(c for c in d.Classes if c.Code == "Wall")
    wall.ClassRelations[0].RelatedClassUri = gop_uri
    props = tool.Project.get_properties()
    old = props.project_dictionary
    props.project_dictionary = d
    tool.Loin.reset()
    yield d, wall, gop_uri
    tool.Loin.reset()
    props.project_dictionary = old


def _groups(wall, purpose, milestone):
    spec = tool.Loin.get_or_create_spec(purpose.guid, milestone.guid)
    per_obj = tool.Loin._find_spec_per_object_type(spec, wall)
    return per_obj.alphanumerical_information.groups_of_properties


def test_partial_selection_of_linked_pset_is_not_exported_as_group_ref(linked_dictionary):
    d, wall, gop_uri = linked_dictionary
    assert class_utils.get_related_pset(wall, d, "Pset_Fire") is not None
    purpose = tool.Loin.add_purpose("UC")
    milestone = tool.Loin.add_milestone("MS")
    rating, material = wall.ClassProperties

    # one of two properties: individual reference, no group reference
    tool.Loin.set_property_included(wall, rating, purpose.guid, milestone.guid, True)
    groups = _groups(wall, purpose, milestone)
    assert groups.group_of_properties_refs == []
    assert len(groups.group_of_properties) == 1
    assert len(groups.group_of_properties[0].has_property_refs) == 1

    # all properties: a single reference to the group
    tool.Loin.set_property_included(wall, material, purpose.guid, milestone.guid, True)
    groups = _groups(wall, purpose, milestone)
    assert [r.reference_uri for r in groups.group_of_properties_refs] == [gop_uri]
    assert groups.group_of_properties == []

    # back to partial
    tool.Loin.set_property_included(wall, material, purpose.guid, milestone.guid, False)
    groups = _groups(wall, purpose, milestone)
    assert groups.group_of_properties_refs == []
    assert len(groups.group_of_properties[0].has_property_refs) == 1

    # nothing selected: nothing written for the pset
    tool.Loin.set_property_included(wall, rating, purpose.guid, milestone.guid, False)
    groups = _groups(wall, purpose, milestone)
    assert groups.group_of_properties_refs == [] and groups.group_of_properties == []
