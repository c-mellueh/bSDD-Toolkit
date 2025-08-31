from __future__ import annotations
from bsdd_gui.presets.prop_presets import (
    ModuleHandlerProperties,
    ViewHandlerProperties,
    ItemModelHandlerProperties,
)
from bsdd_parser import BsddProperty


class PropertyTableProperties(
    ModuleHandlerProperties, ViewHandlerProperties, ItemModelHandlerProperties
):
    def __init__(self):
        super().__init__()
        self.active_property: BsddProperty = None
