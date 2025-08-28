from PySide6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QDateTimeEdit, QPushButton
from PySide6.QtCore import Signal, QDateTime, Qt, QMargins
from typing import Any
from .toggle_switch import ToggleSwitch
from datetime import datetime


class DateTimeWithNow(QWidget):
    def __init__(self, *args, is_enabled=True, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QHBoxLayout(self)

        self.dt_edit = QDateTimeEdit(self)
        self.dt_edit.setCalendarPopup(True)  # nice calendar UI
        self.dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dt_edit.setTimeSpec(Qt.TimeSpec.LocalTime)  # or Qt.LocalTime

        self.now_btn = QPushButton("Now", self)
        self.now_btn.clicked.connect(self.set_now)

        self.active_toggle = ToggleSwitch(self, False)
        layout.addWidget(self.dt_edit)
        layout.addWidget(self.now_btn)
        layout.addWidget(self.active_toggle)
        self.layout().setContentsMargins(QMargins(0, 0, 0, 0))
        self.active_toggle.toggled.connect(self.enable_datetime_picker)
        self.active_toggle.setChecked(is_enabled)
        self.now_btn.setMaximumWidth(50)

    def enable_datetime_picker(self, state: bool):
        # self.now_btn.setEnabled(state)
        self.dt_edit.setEnabled(state)

    def set_now(self):
        self.set_active(True)
        self.dt_edit.setDateTime(QDateTime.currentDateTime())

    def is_active(self):
        return self.active_toggle.isChecked()

    def set_active(self, state: bool):
        self.active_toggle.setChecked(state)

    def get_time(self):
        if self.is_active():
            return self.dt_edit.dateTime().toPython()
        return None

    def set_time(self, value: datetime | None):
        if value is None:
            self.set_active(False)
        else:
            self.set_active(True)
            self.dt_edit.setDateTime(QDateTime.fromSecsSinceEpoch(int(value.timestamp()), Qt.UTC))
