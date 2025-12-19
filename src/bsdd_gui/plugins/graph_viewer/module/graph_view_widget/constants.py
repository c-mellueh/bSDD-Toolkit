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

PROPERTY_DRAG = "property_drag"
CLASS_DRAG = "class_drag"
ALLOWED_DRAG_TYPES = Literal["property_drag", "class_drag"]


# Edge Type
C_P_REL = "ClassProperty"
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
IFC_REFERENCE_REL = "IfcReference"

ALLOWED_EDGE_TYPES = [
    C_P_REL,
    MATERIAL_REL,
    REFERENCE_REL,
    IS_EQUAL_REL,
    IS_SIMILAR_REL,
    IS_PARENT_REL,
    IS_CHILD_REL,
    HAS_PART_REL,
    IS_PART_REL,
    PARENT_CLASS,
    IFC_REFERENCE_REL,
]
CLASS_RELATIONS = [
    MATERIAL_REL,
    REFERENCE_REL,
    IS_EQUAL_REL,
    IS_SIMILAR_REL,
    IS_PARENT_REL,
    IS_CHILD_REL,
    HAS_PART_REL,
    IS_PART_REL,
    IFC_REFERENCE_REL,
]

PROPERTY_RELATIONS = [REFERENCE_REL, IS_EQUAL_REL, IS_SIMILAR_REL]

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
    "IfcReference",
]

# Edge pen styles
EDGE_STYLE_DEFAULT = {
    "style": Qt.SolidLine,
    "width": 1.5,
    "color": QColor(130, 130, 150),
}

EDGE_STYLE_MAP: dict[str, dict[str, object]] = {
    PARENT_CLASS: {
        "style": Qt.PenStyle.DotLine,
        "width": 1.5,
        "color": QColor("#06D6A0"),
        "enabled": True,
    },
    C_P_REL: {
        "style": Qt.PenStyle.DashDotDotLine,
        "width": 1.5,
        "color": QColor("#F8FFE5"),
        "enabled": True,
    },
    MATERIAL_REL: {
        "style": Qt.PenStyle.SolidLine,
        "width": 1.5,
        "color": QColor("#1B9AAA"),
        "enabled": True,
    },
    REFERENCE_REL: {
        "style": Qt.PenStyle.SolidLine,
        "width": 1.5,
        "color": QColor("#EF476F"),
        "enabled": True,
    },
    IS_EQUAL_REL: {
        "style": Qt.PenStyle.SolidLine,
        "width": 1.5,
        "color": QColor("#FFC43D"),
        "enabled": True,
    },
    IS_SIMILAR_REL: {
        "style": Qt.PenStyle.SolidLine,
        "width": 1.5,
        "color": QColor("#7D1538"),
        "enabled": True,
    },
    IS_PARENT_REL: {
        "style": Qt.PenStyle.SolidLine,
        "width": 1.5,
        "color": QColor("#80DACC3E"),
        "enabled": False,
    },
    IS_CHILD_REL: {
        "style": Qt.PenStyle.SolidLine,
        "width": 1.5,
        "color": QColor("#DACC3E"),
        "enabled": True,
    },
    HAS_PART_REL: {
        "style": Qt.PenStyle.SolidLine,
        "width": 1.5,
        "color": QColor("#807FB7BE"),
        "enabled": False,
    },
    IS_PART_REL: {
        "style": Qt.PenStyle.SolidLine,
        "width": 1.5,
        "color": QColor("#7FB7BE"),
        "enabled": True,
    },
    GENERIC_REL: {
        "style": Qt.PenStyle.SolidLine,
        "width": 1.5,
        "color": QColor("#9D2129"),
        "enabled": True,
    },
    IFC_REFERENCE_REL: {
        "style": Qt.PenStyle.SolidLine,
        "width": 1.5,
        "color": QColor("#213E9D78"),
        "enabled": True,
    },
}

# Display label mappings (to be translated in UI)
# These provide human-friendly names for types; UI should wrap with
# QCoreApplication.translate("GraphViewSettings", ...)
EDGE_TYPE_LABEL_MAP: dict[str, str] = {
    PARENT_CLASS: "Parent Class Code",
    C_P_REL: "Class Property",
    MATERIAL_REL: "Has Material",
    REFERENCE_REL: "Has Reference",
    IS_EQUAL_REL: "Is Equal To",
    IS_SIMILAR_REL: "Is Similar To",
    IS_PARENT_REL: "Is Parent Of",
    IS_CHILD_REL: "Is Child Of",
    HAS_PART_REL: "Has Part",
    IS_PART_REL: "Is Part Of",
    GENERIC_REL: "Generic",
}



# Scene sizing
# Extra padding added around the bounding box of current nodes when
# computing the scene rect, to allow panning into empty space.
SCENE_PADDING = 800  # pixels
# Minimum scene size to guarantee ample panning room even for tiny graphs.
SCENE_MIN_SIZE = 100_000  # width and height in pixels


X_MARGIN = 20
Y_MARGIN = 65

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