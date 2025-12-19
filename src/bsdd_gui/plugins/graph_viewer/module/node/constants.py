from __future__ import annotations
from typing import Literal

"""
Styling registries for easy expansion of visuals.

- EDGE_STYLE_MAP: per edge_type pen style
- NODE_COLOR_MAP: per node_type fill color
- NODE_SHAPE_MAP: per node_type shape keyword (rect, roundedrect, ellipse)
"""
FILETYPE = "JSON Files (*.json);;all (*.*)"
PATH_NAME = "graph_view"

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

# Node Types
PROPERTY_NODE_TYPE = "Property"
CLASS_NODE_TYPE = "Class"
EXTERNAL_PROPERTY_NODE_TYPE = "ExternalProperty"
EXTERNAL_CLASS_NODE_TYPE = "ExternalClass"
IFC_NODE_TYPE = "IfcReference"

GENERIC_NODE_TYPE = "generic"

ALLOWED_NODE_TYPES = [
    EXTERNAL_PROPERTY_NODE_TYPE,
    PROPERTY_NODE_TYPE,
    CLASS_NODE_TYPE,
    EXTERNAL_CLASS_NODE_TYPE,
    IFC_NODE_TYPE,
]

NODE_TYPE_LABEL_MAP: dict[str, str] = {
    CLASS_NODE_TYPE: "Class",
    EXTERNAL_CLASS_NODE_TYPE: "External Class",
    PROPERTY_NODE_TYPE: "Property",
    EXTERNAL_PROPERTY_NODE_TYPE: "External Property",
    IFC_NODE_TYPE: "IfcReference",
    GENERIC_NODE_TYPE: "Generic",
}


# Node colors and shapes
NODE_COLOR_DEFAULT = QColor(80, 140, 255)
NODE_COLOR_MAP: dict[str, QColor] = {
    CLASS_NODE_TYPE: QColor(220, 60, 60),  # red
    EXTERNAL_CLASS_NODE_TYPE: QColor(220, 160, 60),  # orange
    IFC_NODE_TYPE: QColor(220, 60, 60, 100),  # red
    PROPERTY_NODE_TYPE: QColor(60, 120, 220),  # blue
    EXTERNAL_PROPERTY_NODE_TYPE: QColor(60, 180, 220),  # light blue
    GENERIC_NODE_TYPE: NODE_COLOR_DEFAULT,
}
SHAPE_STYPE_ELLIPSE = "ellipse"
SHAPE_STYLE_RECT = "rect"
SHAPE_STYLE_ROUNDED_RECT = "roundrect"
NODE_SHAPE_MAP: dict[str, str] = {
    CLASS_NODE_TYPE: SHAPE_STYLE_RECT,
    EXTERNAL_CLASS_NODE_TYPE: SHAPE_STYLE_RECT,
    IFC_NODE_TYPE: SHAPE_STYLE_RECT,
    PROPERTY_NODE_TYPE: SHAPE_STYLE_ROUNDED_RECT,
    EXTERNAL_PROPERTY_NODE_TYPE: SHAPE_STYLE_ROUNDED_RECT,
    "generic": SHAPE_STYLE_RECT,
}