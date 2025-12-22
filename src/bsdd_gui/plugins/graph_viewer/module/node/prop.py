from __future__ import annotations
from . import constants, ui
from bsdd_gui.presets.prop_presets import BaseProperties

class GraphViewerNodeProperties(BaseProperties):
    def __init__(self):
        super().__init__()
        self.filters: dict[str, bool] = {nt: True for nt in constants.ALLOWED_NODE_TYPES}
        self.nodes: list[ui.Node] = list()
        self.settings_widget: ui.NodeTypeSettingsWidget = None
        self.allowed_nodes_types = constants.ALLOWED_NODE_TYPES

        self.color_map = constants.NODE_COLOR_MAP
        self.shape_map = constants.NODE_SHAPE_MAP
        self.text_padding = 10.0, 6.0
