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
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QStatusBar,
)
from . import trigger
from bsdd_gui.module.graph_view_widget.view_ui import GraphScene, GraphView
from bsdd_gui.module.graph_view_widget.constants import ALLOWED_EDGE_TYPES, ALLOWED_NODE_TYPES
from bsdd_gui.module.graph_view_widget.ui_settings_widget import SettingsSidebar
from bsdd_gui.presets.ui_presets import BaseWidget
from bsdd_gui import tool
from typing import TYPE_CHECKING
import qtawesome as qta

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.graphics_items import Node, Edge

from bsdd_gui.resources.icons import get_icon


class GraphWindow(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Keep this as a separate window but parented to the main window so it closes with it
        self.setWindowTitle(self.tr("Force-Directed Relationship Graph"))
        self.setWindowIcon(get_icon())
        self.scene = GraphScene()
        self.view = GraphView(self.scene)
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)
        self._layout.addWidget(self._build_node_input_bar())
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

    def _build_node_input_bar(self) -> QWidget:
        bar = QWidget(self)
        bar.setObjectName("nodeInputBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 12, 12, 6)
        layout.setSpacing(8)

        self.node_input = QLineEdit(bar)
        self.node_input.setPlaceholderText(self.tr("Add node by Code or URI and press Enter"))
        self.node_input.setClearButtonEnabled(True)
        self.node_input.returnPressed.connect(lambda: trigger.add_node_by_lineinput(self))
        self.node_input.setStyleSheet(
            """
            QLineEdit {
                color: #e8ecf6;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #0f1320, stop:1 #182032);
                border: 1px solid #3e4d70;
                border-radius: 10px;
                padding: 10px 14px;
                selection-background-color: #5a8bff;
                font-weight: 600;
                letter-spacing: 0.2px;
            }
            QLineEdit:focus {
                border-color: #6ca4ff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #11172a, stop:1 #1d2438);
            }
            """
        )
        layout.addWidget(self.node_input)
        return bar

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

    def _scene_center_pos(self) -> QPointF:
        vp_rect = self.view.viewport().rect()
        center_point = vp_rect.center()
        try:
            return self.view.mapToScene(center_point)
        except Exception:
            return QPointF(0.0, 0.0)

    def _handle_node_input(self):
        query = self.node_input.text().strip()
        if not query:
            return
        bsdd_dictionary = tool.Project.get()
        if bsdd_dictionary is None:
            self.statusbar.showMessage(self.tr("No project loaded."))
            return

        # Resolve the query to a class or property by code or URI
        matches = []
        cls = cl_utils.get_class_by_code(bsdd_dictionary, query) or cl_utils.get_class_by_uri(
            bsdd_dictionary, query
        )
        prop = prop_utils.get_property_by_code(
            query, bsdd_dictionary
        ) or prop_utils.get_property_by_uri(query, bsdd_dictionary)
        if cls:
            matches.append(("class", cls))
        if prop:
            matches.append(("property", prop))

        if not matches:
            self.statusbar.showMessage(self.tr(f"No class or property found for '{query}'."), 3500)
            return

        # Import lazily to avoid circular imports at module load time
        from bsdd_gui.tool import graph_view_widget as gv_tool

        scene_pos = self._scene_center_pos()
        new_nodes: list[Node] = []
        for kind, item in matches:
            if kind == "class":
                new_nodes.extend(
                    gv_tool.GraphViewWidget.insert_classes_in_scene(
                        bsdd_dictionary, self.scene, [item], scene_pos
                    )
                )
            else:
                new_nodes.extend(
                    gv_tool.GraphViewWidget.insert_properties_in_scene(
                        bsdd_dictionary, self.scene, [item], scene_pos
                    )
                )

        if not new_nodes:
            self.statusbar.showMessage(self.tr("Node already present in the view."), 2500)
            return

        trigger.recalculate_edges()
        self._apply_filters()
        self.node_input.clear()
        self.statusbar.showMessage(
            self.tr(f"Added {len(new_nodes)} node(s) near the view center."), 2500
        )

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

    def enterEvent(self, event):
        trigger.enter_window(self)
        return super().enterEvent(event)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = GraphWindow()
    w.show()
    sys.exit(app.exec())
