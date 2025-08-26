from __future__ import annotations

from PySide6.QtCore import (
    QAbstractTableModel,
    QSortFilterProxyModel,
    QModelIndex,
    Qt,
    Signal,
)
from PySide6.QtWidgets import QWidget, QWidget, QTableView
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette, QIcon

from bsdd_gui.resources.icons import get_icon, get_link_icon
from bsdd_parser import BsddClassProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_SplitterSettings import Ui_SplitterSettings


class PropertyWindow(QWidget):
    closed = Signal()

    def __init__(self, som_property: BsddClassProperty, *args, **kwargs):
        from .qt.ui_Window import Ui_PropertyWindow

        super().__init__(*args, **kwargs)
        self.setWindowIcon(get_icon())
        self.ui = Ui_PropertyWindow()
        self.ui.setupUi(self)
        self.som_property = som_property
        self.initial_fill = True
        trigger.window_created(self)

    def enterEvent(self, event):
        trigger.update_window(self)
        return super().enterEvent(event)

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)


class ValueView(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.som_property: BsddClassProperty = None

    def model(self) -> SortModel:
        return super().model()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_V and (event.modifiers() & Qt.ControlModifier):
            trigger.paste_clipboard(self)
        elif event.key() == Qt.Key.Key_C and (event.modifiers() & Qt.ControlModifier):
            trigger.copy_table_content(self)
        else:
            return super().keyPressEvent(event)


class SplitterSettings(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_SplitterSettings()
        self.ui.setupUi(self)
        trigger.splitter_settings_created(self)
