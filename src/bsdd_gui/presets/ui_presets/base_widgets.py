from __future__ import annotations
from PySide6.QtWidgets import QWidget, QDialog, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import Signal, Qt, QObject
from typing import TypeAlias
from bsdd_gui.resources.icons import get_icon


class BaseWidget(QWidget):
    closed = Signal()
    opened = Signal()
    hidden = Signal()
    shown = Signal()
    resized = Signal()
    entered = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setWindowFlag(Qt.WindowType.Window, True)

    def hideEvent(self, event):
        result = super().hideEvent(event)
        self.hidden.emit()
        return result

    def showEvent(self, event):
        result = super().showEvent(event)
        self.shown.emit()
        return result

    def resizeEvent(self, event):
        result = super().resizeEvent(event)
        self.resized.emit()
        return result

    def enterEvent(self, event):
        result = super().enterEvent(event)
        self.entered.emit()
        return result


class BaseWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlag(Qt.WindowType.Window, True)


class BaseDialog(QDialog):

    def __init__(self, widget: FieldWidget, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        # Layout
        self._layout = QVBoxLayout(self)
        self._widget: FieldWidget = widget
        widget.setWindowFlag(Qt.WindowType.Widget)
        self._layout.addWidget(self._widget)
        self._layout.addWidget(self.button_box)
        self.setWindowIcon(get_icon())


class FieldWidget(BaseWindow):

    def __init__(self, bsdd_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data: object = bsdd_data
        self.setWindowIcon(get_icon())
        self.opened.emit()

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)
