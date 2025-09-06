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

# Node Types
PROPERTY_NODE_TYPE = "property"
CLASS_NODE_TYPE = "bsdd_class"
GENERIC_NODE_TYPE = "generic"

# Edge Type
CLASS_PROPERTY_REL = "ClassProperty"
MATERIAL_REL = "HasMaterial"
REFERENCE_REL = "HasReference"
IS_EQUAL_REL = "IsEqualTo"
IS_SIMILAR_REL = "IsSimilarTo"
IS_PARENT_REL = "IsParentOf"
IS_CHILD_REL = "IsChildOf"
HAS_PART_REL = "HasPart"
IS_PART_REL = "IsPartOf"
PARENT_CLASS = "ParentClassCode"
GENERIC_REL = "generic"

ALLOWED_EDGE_TYPES = [
    CLASS_PROPERTY_REL,
    MATERIAL_REL,
    REFERENCE_REL,
    IS_EQUAL_REL,
    IS_SIMILAR_REL,
    IS_PARENT_REL,
    IS_CHILD_REL,
    HAS_PART_REL,
    IS_PART_REL,
    PARENT_CLASS,
    GENERIC_REL,
]
ALLOWED_EDGE_TYPES_TYPING = Literal[
    "ClassProperty",
    "HasMaterial",
    "HasReference",
    "IsEqualTo",
    "IsSimilarTo",
    "IsParentOf",
    "IsChildOf",
    "HasPart",
    "IsPartOf",
    "ParentClassCode",
    "generic",
]

# Edge pen styles
EDGE_STYLE_DEFAULT = {
    "style": Qt.SolidLine,
    "width": 1.5,
    "color": QColor(130, 130, 150),
}

EDGE_STYLE_MAP: dict[str, dict[str, object]] = {
    PARENT_CLASS: {"style": Qt.PenStyle.DotLine, "width": 1.5, "color": QColor(130, 130, 0)},
    CLASS_PROPERTY_REL: {
        "style": Qt.PenStyle.DashDotDotLine,
        "width": 1.5,
        "color": QColor(130, 130, 20),
    },
    MATERIAL_REL: {"style": Qt.PenStyle.SolidLine, "width": 1.5, "color": QColor(130, 130, 40)},
    REFERENCE_REL: {"style": Qt.PenStyle.SolidLine, "width": 1.5, "color": QColor(130, 130, 60)},
    IS_EQUAL_REL: {"style": Qt.PenStyle.SolidLine, "width": 1.5, "color": QColor(130, 130, 80)},
    IS_SIMILAR_REL: {"style": Qt.PenStyle.SolidLine, "width": 1.5, "color": QColor(130, 130, 100)},
    IS_PARENT_REL: {"style": Qt.PenStyle.SolidLine, "width": 1.5, "color": QColor(130, 130, 120)},
    IS_CHILD_REL: {"style": Qt.PenStyle.SolidLine, "width": 1.5, "color": QColor(130, 130, 140)},
    HAS_PART_REL: {"style": Qt.PenStyle.SolidLine, "width": 1.5, "color": QColor(130, 130, 160)},
    IS_PART_REL: {"style": Qt.PenStyle.SolidLine, "width": 1.5, "color": QColor(130, 130, 180)},
    GENERIC_REL: {"style": Qt.PenStyle.SolidLine, "width": 1.5, "color": QColor(130, 130, 220)},
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
