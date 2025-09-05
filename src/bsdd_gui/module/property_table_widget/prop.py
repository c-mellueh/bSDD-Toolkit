from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties, ViewProperties, FieldProperties
from bsdd_json import BsddProperty


class PropertyTableWidgetProperties(ActionsProperties, FieldProperties, ViewProperties):
    def __init__(self):
        super().__init__()
        self.active_property: BsddProperty = None
