from PySide6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QDateTimeEdit, QPushButton
from PySide6.QtCore import Signal, QDateTime, Qt, QMargins
from typing import Any
from .toggle_switch import ItemWithToggleSwitch
from datetime import datetime


class DateTimeWithNow(ItemWithToggleSwitch):
    def __init__(self, *args, is_enabled=True, **kwargs):

        self.layout_container = QWidget()
        self.dt_layout = QHBoxLayout(self.layout_container)
        self.dt_edit = QDateTimeEdit()
        self.now_btn = QPushButton("Now")
        self.dt_layout.addWidget(self.dt_edit)
        self.dt_layout.addWidget(self.now_btn)
        super().__init__(
            self.layout_container, *args, toggle_pos="Right", toggle_is_on=is_enabled, **kwargs
        )
        self.now_btn.setMaximumWidth(50)
        self.now_btn.clicked.connect(self.set_now)
        self.dt_edit.setCalendarPopup(True)  # nice calendar UI
        self.dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dt_edit.setTimeSpec(Qt.TimeSpec.LocalTime)  # or Qt.LocalTime
        self.dt_layout.setContentsMargins(QMargins(0, 0, 0, 0))

    def enable_widget(self, state: bool):
        self.dt_edit.setEnabled(state)

    def set_now(self):
        self.set_active(True)
        self.dt_edit.setDateTime(QDateTime.currentDateTime())

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
