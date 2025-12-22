from __future__ import annotations
from bsdd_json import BsddProperty, BsddClass
from PySide6.QtWidgets import QGraphicsObject, QGraphicsItem, QWidget, QSizePolicy, QVBoxLayout
from PySide6.QtCore import QPointF, QRectF, QPointF, QSize, Signal
from PySide6.QtGui import QBrush, QPen, QPainterPath, QPainter
from bsdd_gui.plugins.graph_viewer.module.settings.ui import _SettingsWidget
from . import trigger


class Node(QGraphicsObject):
    double_clicked = Signal()
    item_changed = Signal(QGraphicsItem.GraphicsItemChange)

    def __init__(
        self,
        bsdd_data: BsddClass | BsddProperty,
        is_external=False,
    ):
        super().__init__()
        self.bsdd_data = bsdd_data
        self.is_external = is_external
        self.label = bsdd_data.Name if bsdd_data else str(bsdd_data)
        self.node_type = "generic"
        self.color: QPen = None
        self.brush: QBrush = None
        self.border: QPen = None
        self.velocity = QPointF(0.0, 0.0)
        self.fixed = False
        self._w = 1.0
        self._h = 1.0
        self.node_shape = None

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
        from bsdd_gui.plugins.graph_viewer.tool import Node as NodeTool

        return NodeTool.path_from_node_shape(self.node_shape, self._w, self._h)

    def paint(self, painter: QPainter, option, widget=None):
        trigger.paint_node(painter, self)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        self.item_changed.emit(change)
        return super().itemChange(change, value)


class NodeTypeSettingsWidget(_SettingsWidget):
    """Panel mirroring EdgeTypeSettingsWidget, but for node types."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(8, 8, 8, 8)
        self.layout().setSpacing(6)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)


class _NodeLegendIcon(QWidget):
    """Small icon preview of node color/shape."""

    def __init__(self, node_type: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._node_type = node_type
        self.setFixedWidth(28)
        self.setFixedHeight(14)

    def sizeHint(self):
        return QSize(28, 14)

    def paintEvent(self, _):
        trigger.paint_node_legend(self)
