from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import QWidget, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette, QIcon
from bsdd_gui.presets.ui_presets import BaseDialog, FieldWidget, BaseWindow
from bsdd_json import BsddClassProperty, BsddDictionary
from . import trigger
from bsdd_gui import tool
from .qt.ui_Widget import Ui_Form


class IdsWidget(FieldWidget, Ui_Form):
    def __init__(self, data: BsddDictionary, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        self.bsdd_data: BsddDictionary
        self.setupUi(self)

        trigger.widget_created(self)
