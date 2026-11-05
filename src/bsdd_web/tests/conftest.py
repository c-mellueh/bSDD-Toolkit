from __future__ import annotations

import pytest
from bsdd_json import BsddDictionary
from bsdd_json.utils.cache import configure

from bsdd_web.ops import Ctx, Extras
from bsdd_web.ops import run as run_op

configure(offline=True)


def sample_data() -> dict:
    return {
        "OrganizationCode": "org",
        "DictionaryCode": "dict",
        "DictionaryVersion": "1.0",
        "LanguageIsoCode": "de-DE",
        "LanguageOnly": False,
        "UseOwnUri": False,
        "DictionaryName": "Sample",
        "Classes": [
            {"Code": "Building", "Name": "Building", "RelatedIfcEntityNamesList": ["IfcBuilding"]},
            {
                "Code": "Wall",
                "Name": "Wall",
                "ParentClassCode": "Building",
                "RelatedIfcEntityNamesList": ["IfcWallSTANDARD"],
                "ClassProperties": [
                    {"Code": "height", "PropertyCode": "Height", "PropertySet": "Geometry", "IsRequired": True},
                    {
                        "Code": "material",
                        "PropertyCode": "Material",
                        "PropertySet": "Common",
                        "AllowedValues": [{"Code": "concrete", "Value": "Concrete"}],
                    },
                ],
            },
            {"Code": "Door", "Name": "Door", "ParentClassCode": "Building"},
            {"Code": "InnerWall", "Name": "Inner Wall", "ParentClassCode": "Wall"},
            {
                "Code": "Pset_Fire",
                "Name": "Pset_Fire",
                "ClassType": "GroupOfProperties",
                "ClassProperties": [{"Code": "rating", "PropertyCode": "FireRating", "PropertySet": "Pset_Fire"}],
            },
        ],
        "Properties": [
            {"Code": "Height", "Name": "Height", "DataType": "Real", "Units": ["m"]},
            {"Code": "Material", "Name": "Material", "DataType": "String"},
            {"Code": "FireRating", "Name": "Fire rating", "DataType": "String"},
        ],
    }


class Harness:
    def __init__(self):
        self.ctx = Ctx(BsddDictionary.model_validate(sample_data()), Extras())

    @property
    def d(self) -> BsddDictionary:
        return self.ctx.dictionary

    def run(self, op_name: str, /, **args):
        return run_op(self.ctx, op_name, args)

    def cls(self, code: str):
        return next((c for c in self.d.Classes if c.Code == code), None)

    def prop(self, code: str):
        return next((p for p in self.d.Properties if p.Code == code), None)


@pytest.fixture
def h() -> Harness:
    return Harness()
