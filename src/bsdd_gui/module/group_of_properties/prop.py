from __future__ import annotations
from bsdd_gui.presets.prop_presets import ViewProperties,FieldProperties,ActionsProperties
class GroupOfPropertiesProperties(ActionsProperties,FieldProperties):
    def __init__(self):
        super().__init__()
        self.active_class = None
class GopClassViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
        