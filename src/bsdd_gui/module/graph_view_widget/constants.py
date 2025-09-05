from __future__ import annotations

"""
Styling registries for easy expansion of visuals.

- EDGE_STYLE_MAP: per edge_type pen style
- NODE_COLOR_MAP: per node_type fill color
- NODE_SHAPE_MAP: per node_type shape keyword (rect, roundrect, ellipse)
"""

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
    "class": QColor(220, 60, 60),  # red
    "property": QColor(60, 120, 220),  # blue
    "demo": QColor(140, 200, 90),
    "generic": NODE_COLOR_DEFAULT,
}

NODE_SHAPE_MAP: dict[str, str] = {
    "class": "rect",
    "property": "roundrect",
    "demo": "rect",
    "generic": "rect",
}
