from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import (
    QFrame,
)
from bsdd_gui.presets.ui_presets import BaseWidget
from .qt import ui_Widget
from . import constants, trigger

if TYPE_CHECKING:
    pass


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
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_layout.addStretch(1)
        self.scroll_content.installEventFilter(self)
        trigger.widget_created(self)

    def eventFilter(self, watched, event):
        # Resize the sidebar to the content whenever the content layout changes.
        if watched is self.scroll_content and event.type() == QEvent.Type.LayoutRequest:
            trigger.content_layout_changed()
        return super().eventFilter(watched, event)
