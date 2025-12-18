from __future__ import annotations
from typing import Literal
from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import QSizePolicy, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtGui import QStandardItem, QPalette, QIcon
from bsdd_gui.presets.ui_presets import BaseDialog, FieldWidget
from bsdd_gui.resources.icons import get_icon, get_link_icon
from bsdd_json import BsddClassProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_Widget import Ui_Form


class DownloadWidget(FieldWidget, Ui_Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        trigger.widget_created(self)
