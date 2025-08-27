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
from .qt.ui_Window import Ui_PropertyWindow


class ClassPropertyEditor(QWidget, Ui_PropertyWindow):
    closed = Signal()

    def __init__(self, bsdd_class_property: BsddClassProperty, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowIcon(get_icon())
        self.setupUi(self)
        self.bsdd_class_property = bsdd_class_property
        self.initial_fill = True
        trigger.window_created(self)

    def enterEvent(self, event):
        trigger.update_window(self)
        return super().enterEvent(event)

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)
