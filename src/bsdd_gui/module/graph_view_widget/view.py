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
from bsdd_gui.module.class_tree_view.constants import JSON_MIME as CLASS_JSON_MIME


class GraphView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setAcceptDrops(True)
        
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

    # ---- Drag & Drop integration ----
    def _mime_has_bsdd_class(self, md) -> bool:
        try:
            if md.hasFormat(CLASS_JSON_MIME):
                return True
            if md.hasFormat("application/json"):
                return True
            if md.hasFormat("text/plain"):
                # expecting JSON array of codes as text
                return True
        except Exception:
            pass
        return False

    def dragEnterEvent(self, event):
        if self._mime_has_bsdd_class(event.mimeData()):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if self._mime_has_bsdd_class(event.mimeData()):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        md = event.mimeData()
        if not self._mime_has_bsdd_class(md):
            return super().dropEvent(event)

        # Determine drop position in scene coordinates (Qt6: position() returns QPointF)
        try:
            pos_view = event.position()
            # mapToScene expects int coordinates
            scene_pos = self.mapToScene(int(pos_view.x()), int(pos_view.y()))
        except Exception:
            scene_pos = self.mapToScene(event.pos())

        # Extract payload
        payload = None
        try:
            if md.hasFormat(CLASS_JSON_MIME):
                payload = bytes(md.data(CLASS_JSON_MIME)).decode("utf-8")
            elif md.hasFormat("application/json"):
                payload = bytes(md.data("application/json")).decode("utf-8")
            elif md.hasFormat("text/plain"):
                payload = bytes(md.data("text/plain")).decode("utf-8").strip()
        except Exception:
            payload = None

        import json

        codes_to_add: list[str] = []
        names_by_code: dict[str, str] = {}

        if payload:
            try:
                obj = json.loads(payload)
                # Two shapes are supported:
                # 1) { kind: 'BsddClassTransfer', roots: [...], classes: [{Code,Name,...}, ...] }
                # 2) [ "IFC123", "IFC234" ]
                if isinstance(obj, dict) and obj.get("kind") == "BsddClassTransfer":
                    roots = obj.get("roots") or []
                    classes = obj.get("classes") or []
                    # build map for lookup
                    for rc in classes:
                        if isinstance(rc, dict) and "Code" in rc:
                            code = rc.get("Code")
                            name = rc.get("Name") or rc.get("Code")
                            if code:
                                names_by_code[code] = name
                    # Use roots if present, else all class entries
                    if roots:
                        codes_to_add = [c for c in roots if isinstance(c, str)]
                    else:
                        codes_to_add = list(names_by_code.keys())
                elif isinstance(obj, list):
                    # list of codes
                    codes_to_add = [c for c in obj if isinstance(c, str)]
                else:
                    codes_to_add = []
            except Exception:
                codes_to_add = []

        if not codes_to_add:
            return super().dropEvent(event)

        # Add nodes for each code at/near drop position
        scene: GraphScene = self.scene()  # type: ignore[assignment]
        if not isinstance(scene, GraphScene):
            scene = self.scene()

        offset_step = QPointF(24.0, 18.0)
        cur = QPointF(scene_pos)

        for idx, code in enumerate(codes_to_add):
            # try to find existing node with matching bsdd_code
            existing = None
            for n in getattr(scene, "nodes", []):
                if isinstance(n, Node) and getattr(n, "bsdd_code", None) == code and n.node_type == "class":
                    existing = n
                    break
            label = names_by_code.get(code, code)
            if existing is not None:
                existing.setPos(cur)
            else:
                n = scene.add_node(label, pos=cur, node_type="class", bsdd_code=code)
            cur += offset_step

        # Keep physics running and adjust scene rect
        try:
            scene.auto_scene_rect()
        except Exception:
            pass

        event.acceptProposedAction()
        return
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
        bsdd_code: Optional[str] = None,
    ) -> Node:
        n = Node(label, color=color, node_type=node_type)
        if bsdd_code is not None:
            try:
                setattr(n, "bsdd_code", bsdd_code)
            except Exception:
                pass
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
