from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node
    from PySide6.QtWidgets import QLabel
    from PySide6.QtCore import QPoint
    from . import ui
    from bsdd_gui.plugins.graph_viewer.module.edge import constants as edge_constants


class GraphViewerSceneViewProperties:
    def __init__(self):
        self._panning_mmb: bool = False
        self._pan_last_pos: QPoint | None = None
        self._help_overlay: QLabel | None = (
            None  # Help overlay: centered, non-interactive notification
        )
        self._create_edge_type: edge_constants.ALLOWED_EDGE_TYPES_TYPING = None
        self._panning_mmb = False
        self.view:ui.GraphView = None
        self.scene:ui.GraphScene = None