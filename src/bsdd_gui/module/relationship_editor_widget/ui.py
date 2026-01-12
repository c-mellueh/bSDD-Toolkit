from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import QWidget, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette, QIcon
from typing import Literal
from bsdd_gui.resources.icons import get_icon, get_link_icon
from bsdd_json import BsddClass, BsddProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_Widget import Ui_Form
from .qt.ui_Settings import Ui_Form as Ui_SettingsForm
from bsdd_gui.presets.ui_presets import BaseWidget


class RelationshipWidget(BaseWidget, Ui_Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data = None
        self.mode: Literal["dialog"] | Literal["live"] = None
        self.setupUi(Form=self)

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)


class SettingsWidget(BaseWidget, Ui_SettingsForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        trigger.settings_created(self)
