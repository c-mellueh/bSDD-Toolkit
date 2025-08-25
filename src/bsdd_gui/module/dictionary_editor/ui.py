from PySide6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QDateTimeEdit, QPushButton
from PySide6.QtCore import Signal, QDateTime, Qt, QMargins
from typing import Any
from . import trigger
from bsdd_gui.resources.icons import get_icon


class DictionaryEditor(QWidget):
    value_changed = Signal(str, Any)

    def __init__(self, *args, **kwargs):

        self.fields = dict()
        super().__init__(*args, **kwargs)
        self.setLayout(QFormLayout())
        trigger.widget_created(self)

    def closeEvent(self, event):
        trigger.widget_close_requested(self, event)


class DateTimeWithNow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)

        self.dt_edit = QDateTimeEdit(self)
        self.dt_edit.setCalendarPopup(True)  # nice calendar UI
        self.dt_edit.setDateTime(QDateTime.currentDateTime())
        self.dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dt_edit.setTimeSpec(Qt.TimeSpec.LocalTime)  # or Qt.LocalTime

        now_btn = QPushButton("Now", self)
        now_btn.clicked.connect(self.set_now)

        layout.addWidget(self.dt_edit)
        layout.addWidget(now_btn)
        self.setWindowIcon(get_icon())
        # self.setContentsMargins(QMargins(0,0,0,0))
        self.layout().setContentsMargins(QMargins(0, 0, 0, 0))

    def set_now(self):
        self.dt_edit.setDateTime(QDateTime.currentDateTime())
