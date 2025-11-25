from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties, DialogProperties, ViewProperties


class IdsExporterProperties(ActionsProperties, DialogProperties):
    def __init__(self):
        super().__init__()
        self.property_count = dict()
        self.setup_worker = None
        self.setup_thread = None
        self.waiting_worker = None
        self.waiting_thread = None
        self.waiting_widget = None
        self.specification_worker = None
        self.specification_thread = None
        self.specification_widget = None
        self.write_worker = None
        self.write_thread = None

class IdsClassViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
        self.checkstate_dict = {}


class IdsPropertyViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
        self.checkstate_dict = {}
