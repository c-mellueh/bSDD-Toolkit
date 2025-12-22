from __future__ import annotations
from typing import TYPE_CHECKING
from . import constants
from bsdd_gui.presets.prop_presets import PluginProperties

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node
    from PySide6.QtWidgets import QGraphicsPathItem
    from . import ui


class GraphViewerEdgeProperties(PluginProperties):

    def __init__(self):
        super().__init__()
        self.edge_drag_active: bool = False
        self.edge_drag_start_node: Node | None = None
        self.edge_preview_item: QGraphicsPathItem | None = None
        self.active_edge: constants.ALLOWED_EDGE_TYPES_TYPING = None
        self.orthogonal_edges: bool = False
        self.edges = list()
        self.filters: dict[constants.ALLOWED_EDGE_TYPES_TYPING, bool] = {
            et: True for et in constants.ALLOWED_EDGE_TYPES
        }
        self.edge_type_settings_widget: ui.EdgeTypeSettingsWidget = None
        self.edge_routing_settings_widget: ui.EdgeRoutingWidget = None

        self.allowed_edge_types = constants.ALLOWED_EDGE_TYPES
        self.arrow_length = 12.0
        self.arrow_width = 8.0
