from __future__ import annotations
from PySide6.QtWidgets import QWidget, QDialog, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import Signal, Qt
from typing import TypeAlias


class BaseDialog(QDialog):
    def __init__(self, widget: BaseWidget, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self.button_box)
        self._widget: BaseWidget = widget
        self._widget.setParent(self)


class BaseWidget(QWidget):
    closed = Signal()

    def __init__(self, bsdd_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data: object = bsdd_data

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)
