from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties, DialogProperties, ViewProperties


class IdsExporterProperties(ActionsProperties, DialogProperties):
    def __init__(self):
        super().__init__()
        self.property_count = dict()


class IdsClassViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
        self.checkstate_dict = {}


class IdsPropertyViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
        self.checkstate_dict = {}
