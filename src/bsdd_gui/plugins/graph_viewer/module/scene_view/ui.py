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

    # --- helpers ---------------------------------------------------------

    def _node_from_item(self, item) -> Node | None:
        # Moved to gv_tool.Node
        return None

    def _start_edge_drag(self, start_node: Node, scene_pos: QPointF) -> None:
        # Move to gv_tool.Edge
        pass

    def _update_edge_drag(self, scene_pos: QPointF) -> None:
        # Move to gv_tool.Edge
        pass

    def _finish_edge_drag(self, end_node: Node | None) -> None:
        # Move to gv_tool.Edge
        pass

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
        trigger.handle_drop_event(event)

    def mouseDoubleClickEvent(self, event):
        # On double-click, emit a tool-level signal when a Node is hit
        try:
            pos_view = self._event_qpoint(event)
            item = self._item_at_pos(pos_view)
            node = self._node_from_item(item)
            if node is not None:
                try:
                    gv_tool.GraphViewWidget.signals.node_double_clicked.emit(node)
                except Exception:
                    pass
                event.accept()
                return
        except Exception:
            pass
        super().mouseDoubleClickEvent(event)

    # ---- Help overlay helpers -------------------------------------------
    def _reposition_help_overlay(self) -> None:
        if not self._help_overlay:
            return
        vp = self.viewport()
        if vp is None:
            return
        margin = 16
        max_w = int(min(720, vp.width() - 2 * margin))
        if max_w < 120:
            max_w = max(120, vp.width() - 2 * margin)
        try:
            self._help_overlay.setMaximumWidth(max_w)
            self._help_overlay.adjustSize()
        except Exception:
            pass
        w = min(self._help_overlay.width(), max_w)
        h = self._help_overlay.height()
        x = int((vp.width() - w) / 2)
        y = int((vp.height() - h) / 2)
        self._help_overlay.setGeometry(x, y, w, h)
        try:
            self._help_overlay.raise_()
        except Exception:
            pass

    def _update_help_overlay_visibility(self) -> None:
        if not self._help_overlay:
            return
        try:
            sc: GraphScene = self.scene()
            has_nodes = bool(getattr(sc, "nodes", []) or [])
        except Exception:
            has_nodes = True
        self._help_overlay.setVisible(not has_nodes)

    def _on_scene_changed(self, *_):
        self._update_help_overlay_visibility()


class GraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.physics = Physics()
        self.timer = QTimer()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._tick)
        self.running = True
        self.timer.start()
        # Edge routing mode: False=straight, True=orthogonal (right-angles)
        self.orthogonal_edges: bool = False

    def _tick(self):
        if not self.running or not self.nodes:
            return
        self.physics.gravity_center = self.sceneRect().center()
        # Only simulate visible items
        vis_nodes = [n for n in self.nodes if n.isVisible()]
        vis_edges = [
            e
            for e in self.edges
            if e.isVisible() and e.start_node.isVisible() and e.end_node.isVisible()
        ]
        if vis_nodes:
            self.physics.step(vis_nodes, vis_edges, dt=1.0)
        # Update visible edges' geometry
        for e in vis_edges:
            e.update_path()

    def set_running(self, run: bool):
        self.running = run

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
