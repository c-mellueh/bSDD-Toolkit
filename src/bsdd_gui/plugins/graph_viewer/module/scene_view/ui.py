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
        self.physics = Physics()
        self.timer = QTimer()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._tick)
        self.running = True
        self.timer.start()
        # Edge routing mode: False=straight, True=orthogonal (right-angles)
        self.orthogonal_edges: bool = False

    def _tick(self):
        return #core.Physics


    def set_orthogonal_edges(self, enabled: bool) -> None:
        """Enable/disable right-angle routing for edges and refresh paths."""
        self.orthogonal_edges = bool(enabled)
        # Update all edges to reflect the new routing mode
        for e in list(self.edges):
            try:
                e.update_path()
            except Exception:
                pass

    def clear_graph(self):
        for e in self.edges:
            self.removeItem(e)
        for n in self.nodes:
            self.removeItem(n)
        self.nodes.clear()
        self.edges.clear()

    def create_scene_rect(self):
        # Fit to visible nodes if any, with generous padding and minimum size
        half = SCENE_MIN_SIZE / 2.0
        self.setSceneRect(QRectF(-half, -half, SCENE_MIN_SIZE, SCENE_MIN_SIZE))

    # Apply visibility filters for nodes and edges
    def apply_filters(self, node_flags: Dict[str, bool], edge_flags: Dict[str, bool]):
        for n in self.nodes:
            show = node_flags.get(n.node_type, True)
            n.setVisible(show)
        for e in self.edges:
            show_edge = edge_flags.get(e.edge_type, True)
            show_edge = show_edge and e.start_node.isVisible() and e.end_node.isVisible()
            e.setVisible(show_edge)
