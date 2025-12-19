from __future__ import annotations
from typing import List, Dict

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
)

from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.graphics_items import Node, Edge
from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.physics import Physics
from bsdd_gui.module.class_tree_view.constants import JSON_MIME as CLASS_JSON_MIME
from bsdd_gui.module.property_table_widget.constants import (
    JSON_MIME as PROPERTY_JSON_MIME,
)
from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.constants import *
from . import trigger
from bsdd_gui.plugins.graph_viewer import tool as gv_tool


class GraphView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)

    def scene(self) -> GraphScene:
        return super().scene()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            factor = 1.25 if event.angleDelta().y() > 0 else 0.8
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event):
        # Keep overlays anchored in viewport coordinates
        trigger.resize_event(event)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        # Log scene coordinates for every mouse click
        if trigger.mouse_press_event(event):
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if trigger.mouse_release_event(event):
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if trigger.mouse_move_event(event):
            super().mouseMoveEvent(event)

    # ---- Drag & Drop integration ----

    def dragEnterEvent(self, event):
        if trigger.drag_enter_event(event):
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if trigger.drag_move_event(event):
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        trigger.drop_event(event)

    def mouseDoubleClickEvent(self, event):
        # On double-click, emit a tool-level signal when a Node is hit
        if trigger.double_click_event(event):
            super().mouseDoubleClickEvent(event)


class GraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
