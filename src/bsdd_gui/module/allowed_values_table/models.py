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
from bsdd_gui.presets.models_presets import TableModel


class AllowedValuesModel(TableModel):

    def __init__(self, bsdd_property: BsddClassProperty | BsddProperty, *args, **kwargs):
        super().__init__(tool.PropertyTable, *args, **kwargs)
        self.bsdd_property = bsdd_property

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    @property
    def active_class(self):
        return tool.MainWindow.get_active_class()

    @property
    def active_pset(self):
        return tool.MainWindow.get_active_pset()

    def rowCount(self, parent=QModelIndex()):
        if not self.bsdd_property:
            return 0
        if parent.isValid():
            return 0
        return len(self.bsdd_property.AllowedValues)

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()
        allowed_value = self.bsdd_property.AllowedValues[row]
        index = self.createIndex(row, column, allowed_value)
        return index

    def setData(self, index, value, /, role=...):
        return False


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> AllowedValuesModel:
        return super().sourceModel()
