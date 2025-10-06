from __future__ import annotations
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json import *
from bsdd_gui.module.graph_view_widget.constants import *
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from . import constants
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, QLineF
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPainterPath, QPen, QPolygonF
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


@dataclass
class EdgeData:
    a: "Node"
    b: "Node"
    weight: float = 1.0


class Edge(QGraphicsPathItem):

    def __init__(
        self,
        start_node: "Node",
        end_node: "Node",
        edge_type: str,
        weight: float = 1.0,
        edge_data=None,
    ):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight
        self.edge_type = edge_type
        self.setZValue(-1)
        # Allow selecting edges so users can delete relationships explicitly
        if self.edge_type != constants.PARENT_CLASS:
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.update_pen()
        # Arrow visuals
        self.arrow_length = 12.0
        self.arrow_width = 8.0
        self._arrow_polygon: QPolygonF | None = None
        self.update_path()
        self.edge_data = edge_data

    def __str__(self):
        return (
            f"{self.edge_type}: {self.start_node.bsdd_data.Code} -> {self.end_node.bsdd_data.Code}"
        )

    # --- geometry helpers -------------------------------------------------
    def _anchor_on_node(self, node: "Node", toward: QPointF, orto=False) -> QPointF:
        """Return point on node boundary in direction of 'toward'.
        Approximates node shape as its rectangle for rect/roundedrect, and
        as ellipse for ellipse shape.
        """
        c = node.pos()
        v = QPointF(toward.x() - c.x(), toward.y() - c.y())
        length = (v.x() ** 2 + v.y() ** 2) ** 0.5
        if length < 1e-6:
            return QPointF(c)
        normalized_x, normalized_y = v.x() / length, v.y() / length

        half_width, half_height = getattr(node, "_w", 24.0) / 2.0, getattr(node, "_h", 24.0) / 2.0
        # Ellipse intersection distance from center along direction u
        if getattr(node, "node_shape", None) == SHAPE_STYPE_ELLIPSE:
            import math

            denom = (normalized_x / max(half_width, 1e-6)) ** 2 + (
                normalized_y / max(half_height, 1e-6)
            ) ** 2
            t = 1.0 / math.sqrt(max(denom, 1e-9))
        else:
            # Rect/roundedrect: distance to edge along u
            tx = half_width / abs(normalized_x) if abs(normalized_x) > 1e-6 else float("inf")
            ty = half_height / abs(normalized_y) if abs(normalized_y) > 1e-6 else float("inf")
            t = min(tx, ty)
        if not orto:
            return QPointF(c.x() + normalized_x * t, c.y() + normalized_y * t)

        if abs(v.y()) < half_height:
            dw = normalized_x / abs(normalized_x) * half_width
            return QPointF(c.x() + dw, c.y())
        else:
            dh = normalized_y / abs(normalized_y) * half_height
            return QPointF(c.x(), c.y() + dh)

    def _ortho_mode_is_hor(self, node, toward):
        c = node.pos()
        v = QPointF(toward.x() - c.x(), toward.y() - c.y())
        return abs(v.y()) < self.arrow_length * 3

    def _ortho_start(self, node, toward, hor_mode):
        c = node.pos()
        v = QPointF(toward.x() - c.x(), toward.y() - c.y())
        halfe_width, half_height = getattr(node, "_w", 24.0) / 2.0, getattr(node, "_h", 24.0) / 2.0
        if hor_mode:
            dw = v.x() / abs(v.x()) * halfe_width if abs(v.x()) > 1e-6 else 0.0
            return QPointF(c.x() + dw, c.y())
        else:
            dh = v.y() / abs(v.y()) * half_height if abs(v.y()) > 1e-6 else 0.0
            return QPointF(c.x(), c.y() + dh)

    def _compute_arrow(self, p1: QPointF, p2: QPointF) -> QPolygonF:
        """Create an arrowhead polygon at p2, pointing from p1 -> p2."""
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        d = (dx * dx + dy * dy) ** 0.5
        if d < 1e-6:
            return QPolygonF()
        ux, uy = dx / d, dy / d
        # Orthogonal vector
        nx, ny = -uy, ux
        tail_x = p2.x() - ux * self.arrow_length
        tail_y = p2.y() - uy * self.arrow_length
        half_w = self.arrow_width / 2.0
        left = QPointF(tail_x + nx * half_w, tail_y + ny * half_w)
        right = QPointF(tail_x - nx * half_w, tail_y - ny * half_w)
        return QPolygonF([p2, left, right])

    def update_path(self):
        # Determine routing mode from scene
        sc = self.scene()
        orth = False
        try:
            orth = bool(getattr(sc, "orthogonal_edges", False))
        except Exception:
            orth = False

        # Compute anchors on node boundaries

        path = QPainterPath()
        if not orth:
            p_start = self._anchor_on_node(self.start_node, self.end_node.pos(), orth)
            p_end_tip = self._anchor_on_node(self.end_node, self.start_node.pos(), orth)
            path.moveTo(p_start)
            # Straight line with arrow margin
            v = QPointF(p_end_tip.x() - p_start.x(), p_end_tip.y() - p_start.y())
            d = (v.x() ** 2 + v.y() ** 2) ** 0.5
            if d > 1e-6:
                ux, uy = v.x() / d, v.y() / d
                p_end_line = QPointF(
                    p_end_tip.x() - ux * self.arrow_length,
                    p_end_tip.y() - uy * self.arrow_length,
                )
                last_base = QPointF(p_start)
            else:
                p_end_line = QPointF(p_end_tip)
                last_base = QPointF(p_start)
            path.lineTo(p_end_line)

        else:

            horizontal_mode = self._ortho_mode_is_hor(self.start_node, self.end_node.pos())
            p_start = self._ortho_start(self.start_node, self.end_node.pos(), horizontal_mode)
            p_end_tip = self._ortho_start(self.end_node, self.start_node.pos(), horizontal_mode)
            delta_x = p_end_tip.x() - p_start.x()
            delta_y = p_end_tip.y() - p_start.y()
            x_dir = delta_x / abs(delta_x) if abs(delta_x) > 1e-6 else 0.0
            y_dir = delta_y / abs(delta_y) if abs(delta_y) > 1e-6 else 0.0
            if horizontal_mode:
                x_height = p_end_tip.x() - self.arrow_length * x_dir * 3
                p1 = QPointF(x_height, p_start.y())
                p2 = QPointF(x_height, p_end_tip.y())
                p3 = QPointF(p_end_tip.x() - x_dir * self.arrow_length, p_end_tip.y())

            else:
                y_height = p_end_tip.y() - self.arrow_length * y_dir * 3
                p1 = QPointF(p_start.x(), y_height)
                p2 = QPointF(p_end_tip.x(), y_height)
                p3 = QPointF(p_end_tip.x(), p_end_tip.y() - y_dir * self.arrow_length)
            path.moveTo(p_start)
            path.lineTo(p1)
            path.lineTo(p2)
            path.lineTo(p3)
            last_base = QPointF(p3)

        self.setPath(path)
        # Arrow head aligned with the last segment direction
        self._arrow_polygon = self._compute_arrow(last_base, p_end_tip)

    def update_pen(self):
        # Style edges using registry; falls back to default
        cfg = EDGE_STYLE_MAP.get(self.edge_type, EDGE_STYLE_DEFAULT)
        color = cfg.get("color", EDGE_STYLE_DEFAULT["color"])  # type: ignore[index]
        width = float(cfg.get("width", EDGE_STYLE_DEFAULT["width"]))
        style = cfg.get("style", EDGE_STYLE_DEFAULT["style"])  # type: ignore[index]
        pen = QPen(color if isinstance(color, QColor) else QColor(130, 130, 150), width)
        pen.setCosmetic(True)
        try:
            pen.setStyle(style)  # type: ignore[arg-type]
        except Exception:
            pen.setStyle(Qt.SolidLine)
        self.setPen(pen)
        # No fill for arrow head
        self._arrow_brush = QBrush(Qt.NoBrush)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(Qt.NoBrush))
        path = self.path()

        # Custom selection visualization: soft glow under the edge instead of Qt's default rectangle
        if self.isSelected():
            base_pen = self.pen()
            glow_color = QColor(base_pen.color())
            try:
                glow_color.setAlpha(110)
            except Exception:
                pass
            glow_width = max(float(base_pen.widthF()) * 5.0, 10.0)
            glow_pen = QPen(glow_color, glow_width)
            glow_pen.setCosmetic(True)
            try:
                glow_pen.setStyle(Qt.SolidLine)
                glow_pen.setCapStyle(Qt.RoundCap)
                glow_pen.setJoinStyle(Qt.RoundJoin)
            except Exception:
                pass
            painter.setPen(glow_pen)
            painter.drawPath(path)
            # Glow around arrow outline too
            if self._arrow_polygon is not None and not self._arrow_polygon.isEmpty():
                painter.drawPolygon(self._arrow_polygon)

        # Draw the edge with its configured style
        painter.setPen(self.pen())
        painter.drawPath(path)

        # Draw arrow head on top (solid outline)
        if self._arrow_polygon is not None and not self._arrow_polygon.isEmpty():
            solid_pen = QPen(self.pen())
            try:
                solid_pen.setStyle(Qt.SolidLine)
            except Exception:
                pass
            painter.setPen(solid_pen)
            painter.drawPolygon(self._arrow_polygon)

    def boundingRect(self) -> QRectF:
        rect = super().boundingRect()
        try:
            if self._arrow_polygon is not None and not self._arrow_polygon.isEmpty():
                rect = rect.united(self._arrow_polygon.boundingRect())
        except Exception:
            pass
        # Add generous margin to accommodate selection glow
        return rect.adjusted(-12, -12, 12, 12)


class Node(QGraphicsObject):

    def __init__(
        self,
        bsdd_data: BsddClass | BsddProperty,
        radius: float = 12.0,
        color: QColor | None = None,
        is_external = False
    ):
        super().__init__()
        self.bsdd_data = bsdd_data
        self.is_external = is_external
        self.label = bsdd_data.Name if bsdd_data else str(bsdd_data)
        # radius retained for backward-compat, not used for drawing
        self.radius = radius
        self.node_type = "generic"

        if isinstance(bsdd_data, BsddProperty):
            self.node_type = PROPERTY_NODE_TYPE
        elif isinstance(bsdd_data, BsddClass):
            self.node_type = CLASS_NODE_TYPE
        else:
            self.node_type = "generic"
        # Resolve color and shape from registries unless explicitly provided
        resolved_color = color or NODE_COLOR_MAP.get(self.node_type, NODE_COLOR_DEFAULT)
        self.color = QColor(resolved_color)
        
        if self.is_external:
            print(bsdd_data.Name ,is_external)
            self.color.setAlpha(100)

        self.brush = QBrush(self.color)
        self.border = QPen(QColor(40, 60, 90), 1.2)
        self.border.setCosmetic(True)
        self.node_shape = NODE_SHAPE_MAP.get(self.node_type, NODE_SHAPE_MAP.get("generic", "rect"))

        self.velocity = QPointF(0.0, 0.0)
        self.fixed = False

        # Padding around text inside the rectangle
        self.pad_x = 10.0
        self.pad_y = 6.0
        # Initial size; refined on first paint using actual font metrics
        try:
            fm = QFontMetrics(QApplication.font())
            tr = fm.boundingRect(self.label)
            self._w = max(2 * self.radius, tr.width() + 2 * self.pad_x)
            self._h = max(2 * self.radius, tr.height() + 2 * self.pad_y)
        except Exception:
            # Fallback if no application font is available yet
            self._w = self._h = 2 * self.radius

        flags = (
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemSendsGeometryChanges
            | QGraphicsItem.ItemIsSelectable
        )

        self.setFlags(flags)
        self.setAcceptHoverEvents(True)

    def __str__(self):
        if hasattr(self.bsdd_data, "Code"):
            return f"Node: {self.bsdd_data.Code} ({self.node_type})"
        return f"Node: {self.bsdd_data} ({self.node_type})"

    def __repr__(self):
        return self.__str__()

    @property
    def bsdd_code(self):
        return self.bsdd_data.Code

    def boundingRect(self) -> QRectF:
        # Include a small margin for the border
        margin = 2.0
        return QRectF(
            -self._w / 2 - margin,
            -self._h / 2 - margin,
            self._w + 2 * margin,
            self._h + 2 * margin,
        )

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        if self.node_shape == SHAPE_STYPE_ELLIPSE:
            path.addEllipse(QRectF(-self._w / 2, -self._h / 2, self._w, self._h))
        elif self.node_shape == SHAPE_STYLE_ROUNDED_RECT:
            path.addRoundedRect(QRectF(-self._w / 2, -self._h / 2, self._w, self._h), 6, 6)
        elif self.node_shape == SHAPE_STYLE_RECT:  # rect
            path.addRect(QRectF(-self._w / 2, -self._h / 2, self._w, self._h))
        return path

    def _update_size_for_text(self, painter: Optional[QPainter] = None):
        # Compute size from current font metrics so the rectangle fits the text
        try:
            fm = painter.fontMetrics() if painter is not None else QFontMetrics(QApplication.font())
        except Exception:
            return  # can't compute metrics safely right now
        tr = fm.boundingRect(self.label)
        new_w = tr.width() + 2 * self.pad_x
        new_h = tr.height() + 2 * self.pad_y
        # Avoid excessive geometry changes for tiny fluctuations
        if abs(new_w - self._w) > 0.5 or abs(new_h - self._h) > 0.5:
            self.prepareGeometryChange()
            self._w = new_w
            self._h = new_h

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        # Ensure our rectangle matches current text size and font
        self._update_size_for_text(painter)
        painter.setPen(self.border)
        painter.setBrush(self.brush if not self.isSelected() else QBrush(QColor(255, 180, 90)))
        rect = QRectF(-self._w / 2, -self._h / 2, self._w, self._h)
        if self.node_shape == "ellipse":
            painter.drawEllipse(rect)
        elif self.node_shape == "roundrect":
            painter.drawRoundedRect(rect, 6, 6)
        else:
            painter.drawRect(rect)
        painter.setPen(QPen(QColor(20, 20, 30)))
        painter.drawText(rect, Qt.AlignCenter, self.label)

    def mouseDoubleClickEvent(self, event):
        # Emit tool signal when this node is double-clicked
        try:
            from bsdd_gui.tool.graph_view_widget import GraphViewWidget

            GraphViewWidget.signals.node_double_clicked.emit(self)
        except Exception:
            pass
        try:
            event.accept()
        except Exception:
            pass
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            sc = self.scene()
            if sc:
                for edge in sc.items():
                    if isinstance(edge, Edge) and (
                        edge.start_node is self or edge.end_node is self
                    ):
                        edge.update_path()
        return super().itemChange(change, value)
