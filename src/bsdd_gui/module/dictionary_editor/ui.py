from PySide6.QtWidgets import QWidget, QFormLayout
from PySide6.QtCore import Signal
from typing import Any
from . import trigger


class DictionaryEditor(QWidget):
    value_changed = Signal(str, Any)

    def __init__(self, *args, **kwargs):

        self.fields = dict()
        super().__init__(*args, **kwargs)
        self.setLayout(QFormLayout())
        trigger.widget_created(self)
