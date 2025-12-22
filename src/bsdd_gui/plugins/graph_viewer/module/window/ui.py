from __future__ import annotations
from typing import TYPE_CHECKING
from bsdd_gui.resources.icons import get_icon
from bsdd_gui.presets.ui_presets import FieldWidget
from .qt.ui_Widget import Ui_Form
from . import trigger
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class GraphWidget(FieldWidget, Ui_Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        trigger.widget_created(self)

    def resizeEvent(self, event):
        return super().resizeEvent(event)