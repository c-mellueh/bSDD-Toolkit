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
from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.graphics_items import Node, Edge
from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.physics import Physics
from bsdd_gui.module.class_tree_view.constants import JSON_MIME as CLASS_JSON_MIME
from bsdd_gui.module.property_table_widget.constants import (
    JSON_MIME as PROPERTY_JSON_MIME,
)
from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.constants import *
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
        # Enable receiving key events
        try:
            self.setFocusPolicy(Qt.StrongFocus)
        except Exception:
            pass

        # Edge-drawing interaction state
        self._edge_drag_active: bool = False
        self._edge_drag_start: Node | None = None
        self._edge_preview_item: QGraphicsPathItem | None = None
        # Selected edge type for creation (None = auto/heuristic)
        self._create_edge_type: str | None = None
        # Middle-button panning state
        self._panning_mmb: bool = False
        self._pan_last_pos: QPoint | None = None

        # Help overlay: centered, non-interactive notification
        self._help_overlay: QLabel | None = None
        try:
            txt = self.tr(
                "Drag & drop classes or properties in the view to edit their relations.\n"
                "Hold Shift and drag between nodes to create relations.\n"
                "Double-click an edge legend in the settings tab to change relation style.\n"
                "Editing Parent-Class-Code relations isn't supported so far."
            )
            self._help_overlay = QLabel(txt, self.viewport())
            self._help_overlay.setWordWrap(True)
            self._help_overlay.setAlignment(Qt.AlignCenter)
            self._help_overlay.setTextInteractionFlags(Qt.NoTextInteraction)
            self._help_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self._help_overlay.setStyleSheet(
                """
                QLabel {
                    color: #e8e8f0;
                    background: rgba(25, 25, 35, 180);
                    border: 1px solid rgba(80, 90, 120, 160);
                    border-radius: 8px;
                    padding: 10px 14px;
                }
                """
            )
            self._reposition_help_overlay()
            self._update_help_overlay_visibility()
        except Exception:
            self._help_overlay = None

        # React to scene modifications to show/hide the help overlay
        try:
            self.scene().changed.connect(self._on_scene_changed)
        except Exception:
            pass

    # --- keyboard shortcuts ---------------------------------------------
    def keyPressEvent(self, event):
        key = event.key()
        # Toggle physics with Spacebar
        if key == Qt.Key_Space:
            try:
                tool.GraphViewWidget.toggle_running()
            except Exception:
                sc: GraphScene = self.scene()
                sc.set_running(not sc.running)
            event.accept()
            return
        # Delete selected nodes/relationships with Delete key
        if key in (Qt.Key_Delete,):
            sc: GraphScene = self.scene()
            if sc is not None:
                self._delete_selected(sc)
                event.accept()
                return
        super().keyPressEvent(event)

    def _delete_selected(self, sc: "GraphScene") -> None:
        trigger.delete_selection()

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
            elif style in (
                Qt.PenStyle.DashLine,
                Qt.PenStyle.DashDotLine,
                Qt.PenStyle.DashDotDotLine,
            ):
                css_style = "dashed"
        except Exception:
            css_style = "solid"
        if isinstance(color, QColor):
            r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
        else:
            r, g, b, a = 130, 130, 150, 255
        css = f"QGraphicsView {{ border: {max(1, int(round(width)))}px {css_style} rgba({r}, {g}, {b}, 255); }}"
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
        start = self._edge_drag_start.pos()
        p = QPainterPath()
        p.moveTo(start)
        # Match the scene's routing mode for the preview path
        orth = False
        try:
            sc: GraphScene = self.scene()
            orth = bool(getattr(sc, "orthogonal_edges", False))
        except Exception:
            orth = False
        if not orth:
            p.lineTo(scene_pos)
        else:
            # Create a short stub that leaves the node perpendicular (axis-aligned)
            dx = scene_pos.x() - start.x()
            dy = scene_pos.y() - start.y()
            stub_len = 14.0
            if abs(dx) >= abs(dy):
                s1 = QPointF(start.x() + (stub_len if dx >= 0 else -stub_len), start.y())
                m = QPointF(s1.x(), scene_pos.y())
            else:
                s1 = QPointF(start.x(), start.y() + (stub_len if dy >= 0 else -stub_len))
                m = QPointF(scene_pos.x(), s1.y())
            p.lineTo(s1)
            p.lineTo(m)
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
        trigger.create_relation(start_node, end_node, etype)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            factor = 1.25 if event.angleDelta().y() > 0 else 0.8
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event):
        # Keep overlays anchored in viewport coordinates
        try:
            self._reposition_help_overlay()
        except Exception:
            pass
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        # Log scene coordinates for every mouse click
        try:
            pos_view = self._event_qpoint(event)
            pos_scene = self.mapToScene(pos_view)
        except Exception:
            pass

        if event.button() == Qt.MiddleButton:
            # Start manual panning with middle mouse
            self._panning_mmb = True
            self._pan_last_pos = self._event_qpoint(event)
            try:
                self.setCursor(Qt.ClosedHandCursor)
            except Exception:
                pass
            event.accept()
            return
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
        if self._panning_mmb and event.button() == Qt.MiddleButton:
            self._panning_mmb = False
            self._pan_last_pos = None
            try:
                self.setCursor(Qt.ArrowCursor)
            except Exception:
                pass
            event.accept()
            return
        elif self._edge_drag_active and event.button() == Qt.LeftButton:
            pos_view = self._event_qpoint(event)
            item = self._item_at_pos(pos_view)
            node = self._node_from_item(item)
            self._finish_edge_drag(node)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning_mmb:
            # Drag the view by adjusting scrollbars
            cur = self._event_qpoint(event)
            if self._pan_last_pos is not None and cur is not None:
                delta = cur - self._pan_last_pos
                try:
                    self.horizontalScrollBar().setValue(
                        self.horizontalScrollBar().value() - int(delta.x())
                    )
                    self.verticalScrollBar().setValue(
                        self.verticalScrollBar().value() - int(delta.y())
                    )
                except Exception:
                    pass
            self._pan_last_pos = cur
            event.accept()
            return
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

    def mouseDoubleClickEvent(self, event):
        # On double-click, emit a tool-level signal when a Node is hit
        try:
            pos_view = self._event_qpoint(event)
            item = self._item_at_pos(pos_view)
            node = self._node_from_item(item)
            if node is not None:
                try:
                    tool.GraphViewWidget.signals.node_double_clicked.emit(node)
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
