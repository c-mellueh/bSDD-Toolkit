from __future__ import annotations
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json import BsddClass, BsddProperty, BsddDictionary
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Literal

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QTimer
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
from bsdd_gui import tool
from bsdd_gui.module.graph_view_widget.graphics_items import Node, Edge
from bsdd_gui.module.graph_view_widget.physics import Physics
from bsdd_gui.module.class_tree_view.constants import JSON_MIME as CLASS_JSON_MIME
from bsdd_gui.module.property_table_widget.constants import (
    JSON_MIME as PROPERTY_JSON_MIME,
)
from bsdd_gui.module.graph_view_widget.constants import *
from . import trigger


class GraphView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setAcceptDrops(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Edge-drawing interaction state
        self._edge_drag_active: bool = False
        self._edge_drag_start: Node | None = None
        self._edge_preview_item: QGraphicsPathItem | None = None
        # Selected edge type for creation (None = auto/heuristic)
        self._create_edge_type: str | None = None

    # --- public API ------------------------------------------------------
    def set_create_edge_type(self, edge_type: str | None) -> None:
        """Select edge type for interactive creation and update border style."""
        self._create_edge_type = edge_type
        # Apply a border to the view to reflect style
        if not edge_type:
            self.setStyleSheet("")
            return
        cfg = EDGE_STYLE_MAP.get(edge_type, EDGE_STYLE_DEFAULT)
        color = cfg.get("color", EDGE_STYLE_DEFAULT["color"])  # type: ignore[index]
        width = float(cfg.get("width", EDGE_STYLE_DEFAULT["width"]))
        style = cfg.get("style", EDGE_STYLE_DEFAULT["style"])  # type: ignore[index]
        # Map Qt pen style to CSS border style
        css_style = "solid"
        try:
            if style == Qt.PenStyle.DotLine:
                css_style = "dotted"
            elif style in (Qt.PenStyle.DashLine, Qt.PenStyle.DashDotLine, Qt.PenStyle.DashDotDotLine):
                css_style = "dashed"
        except Exception:
            css_style = "solid"
        if isinstance(color, QColor):
            r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
        else:
            r, g, b, a = 130, 130, 150, 255
        css = (
            f"QGraphicsView {{ border: {max(1, int(round(width)))}px {css_style} rgba({r}, {g}, {b}, 255); }}"
        )
        self.setStyleSheet(css)

    # --- helpers ---------------------------------------------------------
    def _event_qpoint(self, event) -> QPoint:
        try:
            p = event.position()
            return QPoint(int(p.x()), int(p.y()))
        except Exception:
            return event.pos()

    def _item_at_pos(self, pos_view: QPoint) -> QGraphicsItem | None:
        try:
            return self.itemAt(pos_view)
        except Exception:
            # Fallback if itemAt signature differs
            return None

    def _node_from_item(self, item) -> Node | None:
        it = item
        while it is not None:
            if isinstance(it, Node):
                return it
            try:
                it = it.parentItem()
            except Exception:
                break
        return None

    def _start_edge_drag(self, start_node: Node, scene_pos: QPointF) -> None:
        self._edge_drag_active = True
        self._edge_drag_start = start_node
        # Create a lightweight preview path
        path_item = QGraphicsPathItem()
        pen = QPen(QColor(200, 200, 210, 220))
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        pen.setWidthF(1.2)
        path_item.setPen(pen)
        path_item.setZValue(-0.5)  # above edges (-1), below nodes (0)
        self.scene().addItem(path_item)
        self._edge_preview_item = path_item
        self._update_edge_drag(scene_pos)

    def _update_edge_drag(self, scene_pos: QPointF) -> None:
        if not self._edge_drag_active or self._edge_preview_item is None:
            return
        if self._edge_drag_start is None:
            return
        p = QPainterPath()
        p.moveTo(self._edge_drag_start.pos())
        p.lineTo(scene_pos)
        self._edge_preview_item.setPath(p)

    def _finish_edge_drag(self, end_node: Node | None) -> None:
        # Remove preview
        if self._edge_preview_item is not None:
            try:
                self.scene().removeItem(self._edge_preview_item)
            except Exception:
                pass
            self._edge_preview_item = None

        start_node = self._edge_drag_start
        # Reset state
        self._edge_drag_active = False
        self._edge_drag_start = None

        if start_node is None or end_node is None:
            return
        if end_node is start_node:
            return

        # Decide edge type: use selected type if set, otherwise heuristic
        etype = self._create_edge_type
        if not etype:
            etype = (
                CLASS_PROPERTY_REL
                if getattr(start_node, "node_type", None) == CLASS_NODE_TYPE
                and getattr(end_node, "node_type", None) == PROPERTY_NODE_TYPE
                else GENERIC_REL
            )

        scene: GraphScene = self.scene()
        try:
            edge = tool.GraphViewWidget.create_edge(start_node, end_node, edge_type=etype)
            tool.GraphViewWidget.add_edge(scene, edge)
        except Exception:
            # Fallback: add directly if tool helper not available
            e = Edge(start_node, end_node, edge_type=etype)
            scene.addItem(e)
            try:
                scene.edges.append(e)
            except Exception:
                pass

        # Re-apply current visibility filters if widget is available
        try:
            w = tool.GraphViewWidget.get_widget()
            if w:
                w._apply_filters()
        except Exception:
            pass

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
        elif event.button() == Qt.LeftButton and (event.modifiers() & Qt.ShiftModifier):
            # Begin edge drawing if pressed on a Node
            pos_view = self._event_qpoint(event)
            item = self._item_at_pos(pos_view)
            node = self._node_from_item(item)
            if node is not None:
                scene_pos = self.mapToScene(pos_view)
                self._start_edge_drag(node, scene_pos)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        elif self._edge_drag_active and event.button() == Qt.LeftButton:
            pos_view = self._event_qpoint(event)
            item = self._item_at_pos(pos_view)
            node = self._node_from_item(item)
            self._finish_edge_drag(node)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._edge_drag_active:
            pos_view = self._event_qpoint(event)
            scene_pos = self.mapToScene(pos_view)
            self._update_edge_drag(scene_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

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

    def _get_drag_type(self, md) -> ALLOWED_DRAG_TYPES | None:
        if md.hasFormat(PROPERTY_JSON_MIME):
            return PROPERTY_DRAG
        if md.hasFormat(CLASS_JSON_MIME):
            return CLASS_DRAG
        return None

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
        trigger.handle_drop_event(event, self)


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
            show_edge = show_edge and e.start_node.isVisible() and e.end_node.isVisible()
            e.setVisible(show_edge)
        # Update scene rect after visibility changes
        self.auto_scene_rect()
