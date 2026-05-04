from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties,FieldProperties

from bsdd_gui.module.iso_export.datamodel import (
    Language,Country,Property
)
from bsdd_json import BsddProperty
class IsoExportProperties(ActionsProperties,FieldProperties):
    def __init__(self):
        super().__init__()
        self.language = Language("de-DE")
        self.country = Country("DE")
        self.property_groups = {}
        self.bsdd_properties:dict[BsddProperty,Property] = {}