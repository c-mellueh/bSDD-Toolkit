from __future__ import annotations
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json import *
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGraphicsObject,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QMainWindow,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QStatusBar,
)
from . import trigger
from bsdd_gui.module.graph_view_widget.view_ui import GraphScene, GraphView
from bsdd_gui.module.graph_view_widget.constants import ALLOWED_EDGE_TYPES, ALLOWED_NODE_TYPES
from bsdd_gui.module.graph_view_widget.ui_settings_widget import SettingsSidebar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.graphics_items import Node, Edge

from bsdd_gui.resources.icons import get_icon

class GraphWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Force-Directed Relationship Graph"))
        self.setWindowIcon(get_icon())
        self.scene = GraphScene()
        self.view = GraphView(self.scene)
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.addWidget(self.view)
        # Status bar for interactive prompts
        self.statusbar = QStatusBar(self)
        self._layout.addWidget(self.statusbar)
        # self._populate_demo()
        self.scene.create_scene_rect()
        self.resize(1000, 700)
        # Track whether we auto-paused due to the window being hidden
        self._auto_paused = False
        self._settings_widget = None
        # Visibility state and overlay settings panel
        self._edge_type_flags: Dict[str, bool] = {et: True for et in ALLOWED_EDGE_TYPES}
        self._node_type_flags: Dict[str, bool] = {nt: True for nt in ALLOWED_NODE_TYPES}
        try:
            self.settings_sidebar = SettingsSidebar(
                self,
                allowed_edge_types=ALLOWED_EDGE_TYPES,
                on_toggle=self._on_edge_type_toggled,
                parent=self.view.viewport(),
            )
            # Reposition when the sidebar is expanded/collapsed
            try:
                self.settings_sidebar.expandedChanged.connect(
                    lambda _: self._position_edge_settings()
                )
            except Exception:
                pass
            self.settings_sidebar.show()
            self._position_edge_settings()
        except Exception:
            # Fail-safe: if overlay can't be created (e.g., headless), skip
            self.settings_sidebar = None
        trigger.widget_created(self)

    # ---- Active edge type selection (from sidebar) ----
    def set_active_edge_type(self, edge_type: str | None):
        # Route to view for border style and creation mode
        try:
            self.view.set_create_edge_type(edge_type)
        except Exception:
            pass
        # Update status text
        try:
            if edge_type:
                self.statusbar.showMessage(f"Create {edge_type} Relationship")
            else:
                self.statusbar.clearMessage()
        except Exception:
            pass

    def get_active_edge_type(self) -> str | None:
        try:
            return getattr(self.view, "_create_edge_type", None)
        except Exception:
            return None

    # ---- Actions ----
    def _toggle_running(self):
        self.scene.set_running(not self.scene.running)
        self.btn_play.setText("Pause" if self.scene.running else "Play")
        # print(f"[DEBUG] GraphWindow._toggle_running: now running={self.scene.running}")

    def _apply_filters(self):
        # Use node type flags from the sidebar; fall back to showing all when missing
        node_flags: Dict[str, bool] = dict(self._node_type_flags)
        # Apply to scene
        self.scene.apply_filters(node_flags, self._edge_type_flags)

    def _on_edge_type_toggled(self, edge_type: str, checked: bool) -> None:
        self._edge_type_flags[edge_type] = checked
        self._apply_filters()

    def _on_node_type_toggled(self, node_type: str, checked: bool) -> None:
        self._node_type_flags[node_type] = checked
        self._apply_filters()

    def _position_edge_settings(self) -> None:
        if not hasattr(self, "settings_sidebar") or self.settings_sidebar is None:
            return
        try:
            vp = self.view.viewport()
            if vp is None:
                return
            margin = 6
            self.settings_sidebar.position_and_resize(vp.width(), vp.height(), margin=margin)
        except Exception:
            pass

    # ---- Visibility handling ----
    def hideEvent(self, event):
        # Auto-pause physics when the window is hidden to save CPU
        if self.scene.running:
            self.scene.set_running(False)
            self._auto_paused = True
            # Keep play button label consistent with state
            if hasattr(self, "btn_play"):
                self.btn_play.setText("Play")
        return super().hideEvent(event)

    def showEvent(self, event):
        # Resume physics only if we paused it due to being hidden
        if getattr(self, "_auto_paused", False):
            self.scene.set_running(True)
            self._auto_paused = False
            if hasattr(self, "btn_play"):
                self.btn_play.setText("Pause")
        # Keep overlay anchored
        self._position_edge_settings()
        return super().showEvent(event)

    def resizeEvent(self, event):
        # Re-anchor the overlay in the bottom-right corner of the viewport
        self._position_edge_settings()
        return super().resizeEvent(event)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = GraphWindow()
    w.show()
    sys.exit(app.exec())
