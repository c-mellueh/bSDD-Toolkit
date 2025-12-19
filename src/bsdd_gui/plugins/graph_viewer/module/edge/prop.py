from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node
    from . import constants
    from PySide6.QtWidgets import QGraphicsPathItem


class GraphViewerEdgeProperties:
    def __init__(self):
        self.edge_drag_active: bool = False
        self.edge_drag_start_node: Node | None = None
        self.edge_preview_item: QGraphicsPathItem | None = None
        self.active_edge: constants.ALLOWED_EDGE_TYPES_TYPING = None
        self.orthogonal_edges: bool = False
        self.edges = list()
        self.filters: dict[constants.ALLOWED_EDGE_TYPES_TYPING, bool] = {
            et: True for et in constants.ALLOWED_EDGE_TYPES
        }
