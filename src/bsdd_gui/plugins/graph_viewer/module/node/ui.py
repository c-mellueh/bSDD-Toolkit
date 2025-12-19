from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from bsdd_gui.resources.icons import get_icon
from bsdd_gui.presets.ui_presets import BaseWidget
from bsdd_json import BsddProperty, BsddClass
from . import constants
from PySide6.QtWidgets import QGraphicsObject, QApplication, QGraphicsItem
from PySide6.QtCore import Qt, QPointF, QRectF, QPointF
from PySide6.QtGui import QColor, QBrush, QPen, QFontMetrics, QPainterPath, QPainter
from bsdd_json.utils import class_utils as cl_utils


class Node(QGraphicsObject):

    def __init__(
        self,
        bsdd_data: BsddClass | BsddProperty,
        radius: float = 12.0,
        color: QColor | None = None,
        is_external=False,
    ):
        super().__init__()
        self.bsdd_data = bsdd_data
        self.is_external = is_external
        self.label = bsdd_data.Name if bsdd_data else str(bsdd_data)
        # radius retained for backward-compat, not used for drawing
        self.radius = radius
        self.node_type = "generic"

        if isinstance(bsdd_data, BsddProperty):
            if self.is_external:
                self.node_type = constants.EXTERNAL_PROPERTY_NODE_TYPE
            else:
                self.node_type = constants.PROPERTY_NODE_TYPE
        elif isinstance(bsdd_data, BsddClass):
            if cl_utils.is_ifc_reference(bsdd_data):
                self.node_type = constants.IFC_NODE_TYPE
            elif self.is_external:
                self.node_type = constants.EXTERNAL_CLASS_NODE_TYPE
            else:
                self.node_type = constants.CLASS_NODE_TYPE

        else:
            self.node_type = "generic"
        # Resolve color and shape from registries unless explicitly provided
        resolved_color = color or constants.NODE_COLOR_MAP.get(
            self.node_type, constants.NODE_COLOR_DEFAULT
        )
        self.color = QColor(resolved_color)
        self.brush = QBrush(self.color)
        self.border = QPen(QColor(40, 60, 90), 1.2)
        self.border.setCosmetic(True)
        self.node_shape = constants.NODE_SHAPE_MAP.get(
            self.node_type, constants.NODE_SHAPE_MAP.get("generic", "rect")
        )

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
        if self.node_shape == constants.SHAPE_STYPE_ELLIPSE:
            path.addEllipse(QRectF(-self._w / 2, -self._h / 2, self._w, self._h))
        elif self.node_shape == constants.SHAPE_STYLE_ROUNDED_RECT:
            path.addRoundedRect(QRectF(-self._w / 2, -self._h / 2, self._w, self._h), 6, 6)
        elif self.node_shape == constants.SHAPE_STYLE_RECT:  # rect
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
            from bsdd_gui.plugins.graph_viewer.tool.graph_view_widget import GraphViewWidget

            GraphViewWidget.signals.node_double_clicked.emit(self)
        except Exception:
            pass
        try:
            event.accept()
        except Exception:
            pass
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        from bsdd_gui.plugins.graph_viewer.module.edge.ui import Edge

        if change == QGraphicsItem.ItemPositionHasChanged:
            sc = self.scene()
            if sc:
                for edge in sc.items():
                    if isinstance(edge, Edge) and (
                        edge.start_node is self or edge.end_node is self
                    ):
                        edge.update_path()
        return super().itemChange(change, value)
