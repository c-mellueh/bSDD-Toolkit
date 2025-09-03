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
from bsdd_gui.presets.ui_presets import BaseDialog, FieldWidget
from bsdd_gui.resources.icons import get_icon, get_link_icon
from bsdd_parser import BsddClassProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_Window import Ui_PropertyWindow


class PropertyCreator(QDialog):
    def __init__(self, bsdd_class_property: BsddClassProperty, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data = bsdd_class_property
        self.setWindowIcon(get_icon())
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self.button_box)
        self.setLayout(self._layout)
        self._editor_widget: PropertyEditor = None
        self.new_button = self.button_box.addButton("Create", QDialogButtonBox.ActionRole)


class PropertyEditor(FieldWidget, Ui_PropertyWindow):
    def __init__(self, *args, mode="edit", **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.mode = mode  # edit or new
        trigger.widget_created(self)
