from __future__ import annotations
from bsdd_gui.presets.prop_presets import BaseProperties

class GraphViewerBuchheimProperties(BaseProperties):
    def __init__(self):
        super().__init__()
        self.children_dict = dict()
        self.parent_dict = dict()
        self.position_dict = dict()
        self.height_list = list()
