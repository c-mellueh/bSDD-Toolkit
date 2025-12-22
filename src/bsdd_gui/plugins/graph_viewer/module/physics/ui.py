from __future__ import annotations
from bsdd_gui.resources.icons import get_icon
from bsdd_gui.presets.ui_presets import BaseWindow
from bsdd_gui.plugins.graph_viewer.module.settings.ui import _SettingsWidget

from typing import Callable, Dict, Iterable, TYPE_CHECKING

from PySide6.QtCore import Qt, QSize, Signal, QMargins, QCoreApplication
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QToolButton,
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
    QSlider,
    QGridLayout,
)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush

from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.constants import (
    EDGE_STYLE_MAP,
    EDGE_STYLE_DEFAULT,
    NODE_COLOR_MAP,
    NODE_SHAPE_MAP,
    EDGE_TYPE_LABEL_MAP,
    NODE_TYPE_LABEL_MAP,
)

from bsdd_gui.presets.ui_presets.toggle_switch import ToggleSwitch

from .qt.ui_Widget import Ui_Form
class SettingsWidget(Ui_Form,_SettingsWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

