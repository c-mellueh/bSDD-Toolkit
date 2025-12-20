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
        if getattr(node, "node_shape", None) == node_constants.SHAPE_STYPE_ELLIPSE:
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
        cfg = constants.EDGE_STYLE_MAP.get(self.edge_type, constants.EDGE_STYLE_DEFAULT)
        color = cfg.get("color", constants.EDGE_STYLE_DEFAULT["color"])  # type: ignore[index]
        width = float(cfg.get("width", constants.EDGE_STYLE_DEFAULT["width"]))
        style = cfg.get("style", constants.EDGE_STYLE_DEFAULT["style"])  # type: ignore[index]
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

    # Emitted when a legend icon is double-clicked to choose creation type
    edgeTypeActivated = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(8, 8, 8, 8)
        self._root.setSpacing(6)

        # Ensure it can stretch vertically when hosted in a sidebar
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setLayout(self._root)

    # def get_flags(self) -> Dict[str, bool]:
    #     return {et: sw.isChecked() for et, sw in self._switches.items()}

    # def set_flag(self, edge_type: str, value: bool) -> None:
    #     sw = self._switches.get(edge_type)
    #     if sw is not None:
    #         sw.blockSignals(True)
    #         try:
    #             sw.setChecked(bool(value))
    #         finally:
    #             sw.blockSignals(False)


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
