from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties, FieldProperties
from typing import TypedDict
from bsdd_gui.module.iso_export.datamodel import Language, Country, Property
from bsdd_json import BsddClass, BsddProperty


class PGD(TypedDict):
    guid: str
    xml_pset: object
    properties: dict[str, dict]
    bsdd_class: object


PsetName = str
ClassPropertyCode = str
PropertyGroupDict = dict[PsetName, PGD]


class GPD(TypedDict):
    pset: BsddClass
    property_codes: object
    bsdd_property: set[ClassPropertyCode]


GroupPropertyDict = dict[ClassPropertyCode, GPD]


class IsoExportProperties(ActionsProperties, FieldProperties):
    def __init__(self):
        super().__init__()
        self.language = Language("de-DE")
        self.country = Country("DE")
        self.property_groups: PropertyGroupDict = {}
        self.bsdd_properties: dict[BsddProperty, Property] = {}
