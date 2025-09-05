from __future__ import annotations
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json import *
from bsdd_gui.module.graph_view_widget.constants import *
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

from PySide6.QtCore import (
    QPointF,
    QRectF,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPen,
)
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

    def __init__(self, a: "Node", b: "Node", weight: float = 1.0, edge_type: str = "generic"):
        super().__init__()
        self.a = a
        self.b = b
        self.weight = weight
        self.edge_type = edge_type
        self.setZValue(-1)
        self.update_pen()
        self.update_path()

    def update_path(self):
        path = QPainterPath()
        path.moveTo(self.a.pos())
        path.lineTo(self.b.pos())
        self.setPath(path)

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


class Node(QGraphicsObject):

    def __init__(
        self,
        label: str,
        radius: float = 12.0,
        color: QColor | None = None,
        node_type: str = "generic",
    ):
        super().__init__()
        self.label = label
        # radius retained for backward-compat, not used for drawing
        self.radius = radius
        self.node_type = node_type
        # Resolve color and shape from registries unless explicitly provided
        resolved_color = color or NODE_COLOR_MAP.get(node_type, NODE_COLOR_DEFAULT)
        self.color = resolved_color
        self.brush = QBrush(self.color)
        self.border = QPen(QColor(40, 60, 90), 1.2)
        self.border.setCosmetic(True)
        self.node_shape = NODE_SHAPE_MAP.get(node_type, NODE_SHAPE_MAP.get("generic", "rect"))

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

        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemSendsGeometryChanges
            | QGraphicsItem.ItemIsSelectable
        )
        self.setAcceptHoverEvents(True)

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
        if self.node_shape == "ellipse":
            path.addEllipse(QRectF(-self._w / 2, -self._h / 2, self._w, self._h))
        elif self.node_shape == "roundrect":
            path.addRoundedRect(QRectF(-self._w / 2, -self._h / 2, self._w, self._h), 6, 6)
        else:  # rect
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

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            sc = self.scene()
            if sc:
                for edge in sc.items():
                    if isinstance(edge, Edge) and (edge.a is self or edge.b is self):
                        edge.update_path()
        return super().itemChange(change, value)
