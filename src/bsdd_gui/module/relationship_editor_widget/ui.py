from __future__ import annotations

from PySide6.QtCore import (
    QAbstractTableModel,
    QSortFilterProxyModel,
    QModelIndex,
    Qt,
    Signal,
)
from PySide6.QtWidgets import QWidget, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette, QIcon
from typing import Literal
from bsdd_gui.resources.icons import get_icon, get_link_icon
from bsdd_parser import BsddClass, BsddProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_Widget import Ui_Form


class RelationshipWidget(QWidget, Ui_Form):
    closed = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data = None
        self.mode: Literal["dialog"] | Literal["live"] = None
        self.setWindowIcon(get_icon())
        self.setupUi(self)

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)
