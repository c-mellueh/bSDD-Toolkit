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
from bsdd_gui.presets.ui_presets import BaseDialog, BaseWidget
from bsdd_parser import BsddClassProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_SplitterSettings import Ui_SplitterSettings
from .qt.ui_Window import Ui_PropertyWindow


class ClassPropertyCreator(BaseDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_button = self.button_box.addButton("Create", QDialogButtonBox.ActionRole)


class ClassPropertyEditor(BaseWidget, Ui_PropertyWindow):
    closed = Signal()

    def __init__(self, bsdd_class_property: BsddClassProperty, *args, mode="edit", **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.mode = mode  # edit or new
        self.bsdd_data = bsdd_class_property
        trigger.widget_created(self)

    def enterEvent(self, event):
        trigger.update_window(self)
        return super().enterEvent(event)

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)
