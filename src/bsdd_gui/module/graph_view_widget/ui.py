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
    QGraphicsItem,
    QGraphicsObject,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QMainWindow,
    QToolBar,
    QToolButton,
    QFileDialog,
)

from bsdd_gui.module.graph_view_widget.view import GraphScene, GraphView
from bsdd_gui.module.graph_view_widget.settings_widget import GraphSettingsWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.graphics_items import Node, Edge


class GraphWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Force‑Directed Graph — PySide6 (Barnes–Hut)")
        self.scene = GraphScene()
        self.view = GraphView(self.scene)
        self.setCentralWidget(self.view)
        self._build_toolbar()
        # self._populate_demo()
        self.scene.auto_scene_rect()
        self.resize(1000, 700)
        # Track whether we auto-paused due to the window being hidden
        self._auto_paused = False

    def _build_toolbar(self):
        tb = QToolBar("Controls")
        tb.setMovable(False)
        self.addToolBar(tb)

        # Play/Pause
        self.btn_play = QToolButton()
        self.btn_play.setText("Pause")
        self.btn_play.clicked.connect(self._toggle_running)
        tb.addWidget(self.btn_play)

        # Re-center
        btn_center = QToolButton()
        btn_center.setText("Center")
        btn_center.clicked.connect(self._center_view)
        tb.addWidget(btn_center)

        # Clear
        btn_clear = QToolButton()
        btn_clear.setText("Clear")
        btn_clear.clicked.connect(self._clear)
        tb.addWidget(btn_clear)

        # Settings button
        btn_settings = QToolButton()
        btn_settings.setText("Settings")
        btn_settings.clicked.connect(self._open_settings)
        tb.addWidget(btn_settings)

        tb.addSeparator()

        # Node toggles
        tb.addWidget(QLabel("Nodes:"))
        self.tg_nodes_class = QToolButton()
        self.tg_nodes_class.setText("Classes")
        self.tg_nodes_class.setCheckable(True)
        self.tg_nodes_class.setChecked(True)
        self.tg_nodes_class.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_nodes_class)

        self.tg_nodes_prop = QToolButton()
        self.tg_nodes_prop.setText("Properties")
        self.tg_nodes_prop.setCheckable(True)
        self.tg_nodes_prop.setChecked(True)
        self.tg_nodes_prop.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_nodes_prop)

        tb.addSeparator()

        # Edge toggles
        tb.addWidget(QLabel("Edges:"))
        self.tg_edge_class_rel = QToolButton()
        self.tg_edge_class_rel.setText("Class↔Class")
        self.tg_edge_class_rel.setCheckable(True)
        self.tg_edge_class_rel.setChecked(True)
        self.tg_edge_class_rel.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_edge_class_rel)

        self.tg_edge_prop_rel = QToolButton()
        self.tg_edge_prop_rel.setText("Prop↔Prop")
        self.tg_edge_prop_rel.setCheckable(True)
        self.tg_edge_prop_rel.setChecked(True)
        self.tg_edge_prop_rel.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_edge_prop_rel)

        self.tg_edge_cl_to_prop = QToolButton()
        self.tg_edge_cl_to_prop.setText("Class→Prop")
        self.tg_edge_cl_to_prop.setCheckable(True)
        self.tg_edge_cl_to_prop.setChecked(True)
        self.tg_edge_cl_to_prop.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_edge_cl_to_prop)

    # ---- Actions ----
    def _toggle_running(self):
        self.scene.set_running(not self.scene.running)
        self.btn_play.setText("Pause" if self.scene.running else "Play")
        # print(f"[DEBUG] GraphWindow._toggle_running: now running={self.scene.running}")

    def _center_view(self):
        self.scene.auto_scene_rect()
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        # print("[DEBUG] GraphWindow._center_view: view centered on scene rect")

    def _clear(self):
        self.scene.clear_graph()
        # print("[DEBUG] GraphWindow._clear: scene cleared")

    def _open_settings(self):
        try:
            w = self._settings_widget
        except AttributeError:
            w = None
        if w is None or not w.isVisible():
            self._settings_widget = GraphSettingsWidget(self.scene.physics, self)
            w = self._settings_widget
        w.show()
        w.raise_()
        w.activateWindow()

    def _apply_filters(self):
        node_flags = {
            "class": (self.tg_nodes_class.isChecked() if hasattr(self, "tg_nodes_class") else True),
            "property": (
                self.tg_nodes_prop.isChecked() if hasattr(self, "tg_nodes_prop") else True
            ),
        }
        edge_flags = {
            "class_rel": (
                self.tg_edge_class_rel.isChecked() if hasattr(self, "tg_edge_class_rel") else True
            ),
            "prop_rel": (
                self.tg_edge_prop_rel.isChecked() if hasattr(self, "tg_edge_prop_rel") else True
            ),
            "class_to_prop": (
                self.tg_edge_cl_to_prop.isChecked() if hasattr(self, "tg_edge_cl_to_prop") else True
            ),
            # default types (e.g., demo) remain visible by default
        }
        # Apply to scene
        self.scene.apply_filters(node_flags, edge_flags)

        self.scene.auto_scene_rect()

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
        return super().showEvent(event)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = GraphWindow()
    w.show()
    sys.exit(app.exec())
