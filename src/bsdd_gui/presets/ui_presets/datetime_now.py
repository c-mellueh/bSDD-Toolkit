from PySide6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QDateTimeEdit, QPushButton
from PySide6.QtCore import Signal, QDateTime, Qt, QMargins
from typing import Any


class DateTimeWithNow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QHBoxLayout(self)

        self.dt_edit = QDateTimeEdit(self)
        self.dt_edit.setCalendarPopup(True)  # nice calendar UI
        self.dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dt_edit.setTimeSpec(Qt.TimeSpec.LocalTime)  # or Qt.LocalTime

        now_btn = QPushButton("Now", self)
        now_btn.clicked.connect(self.set_now)

        layout.addWidget(self.dt_edit)
        layout.addWidget(now_btn)
        self.layout().setContentsMargins(QMargins(0, 0, 0, 0))

    def set_now(self):
        self.dt_edit.setDateTime(QDateTime.currentDateTime())
