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

from bsdd_gui.resources.icons import get_icon, get_link_icon
from bsdd_parser import BsddClassProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_Widget import Ui_Form
from bsdd_gui.presets.ui_presets import BaseWidget


class PropertyWidget(BaseWidget, Ui_Form):

    def __init__(self, *args, **kwargs):
        super().__init__(None, *args, **kwargs)
        self.setWindowIcon(get_icon())
        self.setupUi(self)
        trigger.widget_created(self)
