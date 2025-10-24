from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import QWidget, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette, QIcon
from bsdd_gui.presets.ui_presets import BaseDialog, FieldWidget
from bsdd_json import BsddClassProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_Dialog import Ui_Dialog


class IdsDialog(BaseDialog,Ui_Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)       
        self.setupUi(self)
