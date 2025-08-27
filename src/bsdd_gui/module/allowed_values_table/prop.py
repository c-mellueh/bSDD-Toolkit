from __future__ import annotations
from bsdd_gui.presets.prop_presets import ColumnHandlerProperties, ViewHandlerProperties


class AllowedValuesTableProperties(ColumnHandlerProperties, ViewHandlerProperties):
    def __init__(self):
        super().__init__()
