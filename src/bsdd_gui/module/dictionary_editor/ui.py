from PySide6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QDateTimeEdit, QPushButton
from PySide6.QtCore import Signal, QDateTime, Qt, QMargins
from typing import Any
from . import trigger
from bsdd_gui.resources.icons import get_icon
from bsdd_gui.presets.ui_presets.datetime_now import DateTimeWithNow as DTN


class DictionaryEditor(QWidget):
    value_changed = Signal(str, Any)

    def __init__(self, *args, **kwargs):

        self.fields = dict()
        super().__init__(*args, **kwargs)
        self.setLayout(QFormLayout())
        trigger.widget_created(self)

    def closeEvent(self, event):
        trigger.widget_close_requested(self, event)


class DateTimeWithNow(DTN):
    def __init__(self):
        super().__init__()
