from __future__ import annotations
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json import *
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGraphicsObject,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QMainWindow,
    QToolBar,
    QToolButton,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QStatusBar,
)
from . import trigger
from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.view_ui import GraphScene, GraphView
from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.constants import (
    ALLOWED_EDGE_TYPES,
    ALLOWED_NODE_TYPES,
)
from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.ui_settings_widget import (
    SettingsSidebar,
)
from bsdd_gui.presets.ui_presets import BaseWindow
from bsdd_gui import tool
from typing import TYPE_CHECKING
import qtawesome as qta

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.graphics_items import Node, Edge

from bsdd_gui.resources.icons import get_icon


class GraphWindow(BaseWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

    def enterEvent(self, event):
        trigger.enter_window(self)
        return super().enterEvent(event)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = GraphWindow()
    w.show()
    sys.exit(app.exec())
