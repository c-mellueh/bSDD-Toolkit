from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Callable, Dict
from bsdd_gui.plugins.graph_viewer.module.settings.ui import _SettingsWidget
from bsdd_gui.presets.ui_presets import ToggleSwitch
from bsdd_json import *
from . import constants
from bsdd_gui.plugins.graph_viewer.module.node import constants as node_constants
from PySide6.QtCore import QPointF, QRectF, Qt, QCoreApplication, Signal, QSize
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QWidget,
    QSizePolicy,
)
from . import trigger
from .qt import ui_RoutingWidget

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node


class Edge(QGraphicsPathItem):

    def __init__(
        self,
        start_node: Node,
        end_node: Node,
        edge_type: str,
    ):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.edge_type = edge_type
        self.setZValue(-1)
        # Allow selecting edges so users can delete relationships explicitly
        self.weight = 1.0
        self._arrow_polygon: QPolygonF | None = None

    def __str__(self):
        return (
            f"{self.edge_type}: {self.start_node.bsdd_data.Code} -> {self.end_node.bsdd_data.Code}"
        )

    # --- geometry helpers -------------------------------------------------

    def paint(self, painter: QPainter, option, widget=None):
        trigger.paint_path(painter, self)

    def boundingRect(self) -> QRectF:
        rect = super().boundingRect()
        try:
            if self._arrow_polygon is not None and not self._arrow_polygon.isEmpty():
                rect = rect.united(self._arrow_polygon.boundingRect())
        except Exception:
            pass
        # Add generous margin to accommodate selection glow
        return rect.adjusted(-12, -12, 12, 12)


class EdgeRoutingWidget(_SettingsWidget, ui_RoutingWidget.Ui_Form):
    """Simple panel to toggle between straight and right-angle edges."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, f=Qt.Window, **kwargs)
        self.setupUi(self)


class EdgeTypeSettingsWidget(_SettingsWidget):
    """
    Compact, floating panel with ToggleSwitches to control visibility
    of individual edge types.

    Parent should typically be the QGraphicsView viewport, so it overlays
    the scene and can be anchored in the bottom-right corner by the owner.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(8, 8, 8, 8)
        self.layout().setSpacing(6)

        # Ensure it can stretch vertically when hosted in a sidebar
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)


class _EdgeLegendIcon(QWidget):
    """Small widget that draws a sample line using the configured
    color/width/style for a given edge type.
    """

    edgeTypeActivated = Signal(str)

    def __init__(self, edge_type: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._edge_type = edge_type
        self.setFixedWidth(28)
        self.setFixedHeight(14)

    def sizeHint(self):
        return QSize(28, 14)

    def paintEvent(self, _):
        trigger.paint_edge_legend(self)

    def mouseDoubleClickEvent(self, event):
        try:
            self.edgeTypeActivated.emit(self._edge_type)
        except Exception:
            pass
        super().mouseDoubleClickEvent(event)
