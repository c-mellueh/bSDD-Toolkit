from PySide6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QDateTimeEdit, QPushButton
from PySide6.QtCore import Signal, QDateTime, Qt, QMargins
from PySide6.QtGui import QCloseEvent
from typing import Any
from . import trigger
from bsdd_gui.resources.icons import get_icon
from bsdd_gui.presets.ui_presets import DateTimeWithNow as DTN, FieldWidget
from bsdd_json import BsddDictionary
from .qt.ui_DictionaryEditor import Ui_DictionaryForm


class DictionaryEditor(FieldWidget, Ui_DictionaryForm):
    value_changed = Signal(str, Any)

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        trigger.widget_created(self)


class DateTimeWithNow(DTN):
    def __init__(self):
        super().__init__()
