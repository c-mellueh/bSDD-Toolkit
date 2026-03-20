from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties,WidgetProperties,ViewProperties

class PropertyPickerProperties(ActionsProperties,WidgetProperties):
    def __init__(self):
        super().__init__()



class IdsClassViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
        self.checkstate_dict = {}


class IdsPropertyViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
        self.checkstate_dict = {}
