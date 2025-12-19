from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node
    from PySide6.QtWidgets import QLabel
    from PySide6.QtCore import QPoint


class GraphViewerSceneViewProperties:
    def __init__(self):
        self._panning_mmb: bool = False
        self._pan_last_pos: QPoint | None = None
        self._help_overlay: QLabel | None = None # Help overlay: centered, non-interactive notification
