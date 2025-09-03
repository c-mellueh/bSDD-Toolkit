from __future__ import annotations
from typing import Literal
from PySide6.QtCore import (
    QAbstractTableModel,
    QSortFilterProxyModel,
    QModelIndex,
    Qt,
    Signal,
)
from PySide6.QtWidgets import QWidget, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette, QIcon
from bsdd_gui.presets.ui_presets import BaseDialog, FieldWidget
from bsdd_gui.resources.icons import get_icon, get_link_icon
from bsdd_parser import BsddClassProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_Window import Ui_PropertyWindow


class PropertyCreator(BaseDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Layout
        self.new_button = self.button_box.addButton("Create", QDialogButtonBox.ActionRole)
        self._widget: PropertyEditor


class PropertyEditor(FieldWidget, Ui_PropertyWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.mode: Literal["edit"] | Literal["new"] = None  # edit or new
        trigger.widget_created(self)
