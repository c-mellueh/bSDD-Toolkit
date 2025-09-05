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
    QSlider,
    QToolBar,
    QToolButton,
    QFileDialog,
)

from typing import TYPE_CHECKING
from bsdd_gui.module.graph_view_widget.graphics_items import Node, Edge
from bsdd_gui.module.graph_view_widget.physics import Physics


class GraphView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            factor = 1.25 if event.angleDelta().y() > 0 else 0.8
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake = type("Fake", (), {"button": lambda self: Qt.LeftButton})
            event = type(event)(event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)


class GraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.physics = Physics()
        self.timer = QTimer()
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._tick)
        self.running = True
        self.timer.start()

    def _tick(self):
        if not self.running or not self.nodes:
            return
        self.physics.gravity_center = self.sceneRect().center()
        # Only simulate visible items
        vis_nodes = [n for n in self.nodes if n.isVisible()]
        vis_edges = [e for e in self.edges if e.isVisible() and e.a.isVisible() and e.b.isVisible()]
        if vis_nodes:
            self.physics.step(vis_nodes, vis_edges, dt=1.0)
        # Update visible edges' geometry
        for e in vis_edges:
            e.update_path()

    def set_running(self, run: bool):
        self.running = run

    def add_node(
        self,
        label: str,
        pos: Optional[QPointF] = None,
        color: Optional[QColor] = None,
        node_type: str = "generic",
    ) -> Node:
        n = Node(label, color=color, node_type=node_type)
        p = (
            pos
            if pos is not None
            else QPointF(random.uniform(-150, 150), random.uniform(-150, 150))
        )
        n.setPos(p)
        self.addItem(n)
        self.nodes.append(n)
        return n

    def add_edge(self, a: Node, b: Node, weight: float = 1.0, edge_type: str = "generic") -> Edge:
        e = Edge(a, b, weight, edge_type=edge_type)
        self.addItem(e)
        self.edges.append(e)
        return e

    def clear_graph(self):
        for e in self.edges:
            self.removeItem(e)
        for n in self.nodes:
            self.removeItem(n)
        self.nodes.clear()
        self.edges.clear()

    def auto_scene_rect(self):
        # Fit to visible nodes if any
        vis = [n for n in self.nodes if n.isVisible()]
        items = vis if vis else self.nodes
        if not items:
            self.setSceneRect(QRectF(-200, -200, 400, 400))
            return
        xs = [n.pos().x() for n in items]
        ys = [n.pos().y() for n in items]
        minx, maxx = min(xs) - 120, max(xs) + 120
        miny, maxy = min(ys) - 120, max(ys) + 120
        self.setSceneRect(QRectF(minx, miny, maxx - minx, maxy - miny))

    # Apply visibility filters for nodes and edges
    def apply_filters(self, node_flags: Dict[str, bool], edge_flags: Dict[str, bool]):
        for n in self.nodes:
            show = node_flags.get(n.node_type, True)
            n.setVisible(show)
        for e in self.edges:
            show_edge = edge_flags.get(e.edge_type, True)
            show_edge = show_edge and e.a.isVisible() and e.b.isVisible()
            e.setVisible(show_edge)
        # Update scene rect after visibility changes
        self.auto_scene_rect()
