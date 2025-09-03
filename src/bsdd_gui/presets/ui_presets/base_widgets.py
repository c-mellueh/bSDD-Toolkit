from __future__ import annotations
from PySide6.QtWidgets import QWidget, QDialog, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import Signal, Qt, QObject
from typing import TypeAlias
from bsdd_gui.resources.icons import get_icon


class BaseWidget(QWidget):
    closed = Signal()
    opened = Signal()


class BaseDialog(QDialog):

    def __init__(self, widget: FieldWidget, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self.button_box)
        self._widget: FieldWidget = widget
        self._widget.setParent(self)
        self.setWindowIcon(get_icon())


class FieldWidget(BaseWidget):

    def __init__(self, bsdd_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data: object = bsdd_data
        self.setWindowIcon(get_icon())
        self.opened.emit()

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)
