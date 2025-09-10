from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties, WidgetProperties


class GraphViewWidgetProperties(ActionsProperties, WidgetProperties):
    def __init__(self):
        super().__init__()
        self.position_dict = dict()
        self.height_list = list()
        self.children_dict = dict()
        self.parent_dict = dict()
