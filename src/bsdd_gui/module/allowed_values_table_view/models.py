from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import (
    QAbstractItemModel,
    Qt,
    QCoreApplication,
    QModelIndex,
    QSortFilterProxyModel,
)
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_parser.models import BsddDictionary, BsddClass, BsddClassProperty, BsddProperty
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import ItemModel


class AllowedValuesModel(ItemModel):

    def __init__(self, bsdd_property: BsddClassProperty | BsddProperty, *args, **kwargs):
        super().__init__(tool.AllowedValuesTableView, bsdd_property, *args, **kwargs)
        self.bsdd_data: BsddClassProperty | BsddProperty

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    @property
    def active_class(self):
        return tool.MainWindowWidget.get_active_class()

    @property
    def active_pset(self):
        return tool.MainWindowWidget.get_active_pset()

    def columnCount(self, /, parent=...):
        res = super().columnCount(parent)
        return res

    def rowCount(self, parent=QModelIndex()):
        if not self.bsdd_data:
            return 0
        if parent.isValid():
            return 0
        return len(self.bsdd_data.AllowedValues)

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()
        allowed_value = self.bsdd_data.AllowedValues[row]
        index = self.createIndex(row, column, allowed_value)
        return index

    def flags(self, index):
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> AllowedValuesModel:
        return super().sourceModel()
