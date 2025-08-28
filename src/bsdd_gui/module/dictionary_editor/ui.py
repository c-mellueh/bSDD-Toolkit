from PySide6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QDateTimeEdit, QPushButton
from PySide6.QtCore import Signal, QDateTime, Qt, QMargins
from PySide6.QtGui import QCloseEvent
from typing import Any
from . import trigger
from bsdd_gui.resources.icons import get_icon
from bsdd_gui.presets.ui_presets.datetime_now import DateTimeWithNow as DTN
from bsdd_parser import BsddDictionary
from .qt.ui_DictionaryEditor import Ui_DictionaryForm


class DictionaryEditor(QWidget, Ui_DictionaryForm):
    closed = Signal()
    value_changed = Signal(str, Any)

    def __init__(self, bsdd_dictionary: BsddDictionary, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.data = bsdd_dictionary
        self.setLayout(QFormLayout())
        self.setWindowIcon(get_icon())

    def closeEvent(self, event: QCloseEvent):
        trigger.widget_close_requested(self, event)
        if event.isAccepted():
            self.closed.emit()


class DateTimeWithNow(DTN):
    def __init__(self):
        super().__init__()
