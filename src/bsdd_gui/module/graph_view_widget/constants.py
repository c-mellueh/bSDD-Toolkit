from __future__ import annotations
from typing import Literal

"""
Styling registries for easy expansion of visuals.

- EDGE_STYLE_MAP: per edge_type pen style
- NODE_COLOR_MAP: per node_type fill color
- NODE_SHAPE_MAP: per node_type shape keyword (rect, roundedrect, ellipse)
"""


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

PROPERTY_DRAG = "property_drag"
CLASS_DRAG = "class_drag"
ALLOWED_DRAG_TYPES = Literal["property_drag", "class_drag"]
PROPERTY_NODE_TYPE = "property"
CLASS_NODE_TYPE = "bsdd_class"
GENERIC_NODE_TYPE = "generic"

# Edge pen styles
EDGE_STYLE_DEFAULT = {
    "style": Qt.SolidLine,
    "width": 1.5,
    "color": QColor(130, 130, 150),
}

EDGE_STYLE_MAP: dict[str, dict[str, object]] = {
    "class_rel": {"style": Qt.SolidLine, "width": 1.5, "color": QColor(130, 130, 150)},
    "class_to_prop": {
        "style": Qt.DotLine,
        "width": 1.5,
        "color": QColor(130, 130, 150),
    },
    "prop_rel": {"style": Qt.SolidLine, "width": 1.5, "color": QColor(130, 130, 150)},
    "demo": {"style": Qt.SolidLine, "width": 1.5, "color": QColor(130, 130, 150)},
}

# Node colors and shapes
NODE_COLOR_DEFAULT = QColor(80, 140, 255)
NODE_COLOR_MAP: dict[str, QColor] = {
    CLASS_NODE_TYPE: QColor(220, 60, 60),  # red
    PROPERTY_NODE_TYPE: QColor(60, 120, 220),  # blue
    GENERIC_NODE_TYPE: NODE_COLOR_DEFAULT,
}
SHAPE_STYPE_ELLIPSE = "ellipse"
SHAPE_STYLE_RECT = "rect"
SHAPE_STYLE_ROUNDED_RECT = "roundrect"
NODE_SHAPE_MAP: dict[str, str] = {
    CLASS_NODE_TYPE: SHAPE_STYLE_RECT,
    PROPERTY_NODE_TYPE: SHAPE_STYLE_ROUNDED_RECT,
    GENERIC_NODE_TYPE: SHAPE_STYLE_RECT,
}
