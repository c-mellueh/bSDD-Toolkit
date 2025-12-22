from __future__ import annotations

from typing import Callable, Dict, Iterable, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal, QMargins, QCoreApplication
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QToolButton,
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
)
from bsdd_gui.presets.ui_presets import BaseWidget
from .qt import ui_Widget
from . import constants, trigger

if TYPE_CHECKING:
    from .ui import GraphWindow
    from ..scene_view.ui import GraphScene


class _SettingsWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("SettingsWidget")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)


class SettingsWidget(BaseWidget, ui_Widget.Ui_SettingsSidebar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.scroll_area.setStyleSheet(constants.SETTINGS_STYLE_SHEET)
        self.scroll_area.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.scroll_area.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.scroll_layout.addStretch(1)
        trigger.widget_created(self)
