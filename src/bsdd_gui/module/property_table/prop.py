from __future__ import annotations
from bsdd_gui.presets.prop_presets import (
    ActionsProperties,
    ViewProperties,
    WidgetProperties,
)
from bsdd_parser import BsddProperty


class PropertyTableProperties(ActionsProperties, WidgetProperties, ViewProperties):
    def __init__(self):
        super().__init__()
        self.active_property: BsddProperty = None
