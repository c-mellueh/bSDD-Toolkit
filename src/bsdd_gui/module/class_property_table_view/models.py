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
from bsdd_json.models import BsddDictionary, BsddClass, BsddClassProperty
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import ItemModel


class ClassPropertyTableModel(ItemModel):

    def __init__(self, bsdd_data, *args, **kwargs):
        super().__init__(tool.ClassPropertyTableView, bsdd_data, *args, **kwargs)

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    @property
    def active_class(self):
        return tool.MainWindowWidget.get_active_class()

    @property
    def active_pset(self):
        return tool.MainWindowWidget.get_active_pset()

    def rowCount(self, parent=QModelIndex()):
        if not self.active_class:
            return 0
        if not self.active_pset:
            return 0
        if parent.isValid():
            return 0
        rc = len(
            tool.ClassPropertyTableView.filter_properties_by_pset(
                self.active_class, self.active_pset
            )
        )
        return rc

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()
        bsdd_properties = tool.ClassPropertyTableView.filter_properties_by_pset(
            self.active_class, self.active_pset
        )
        bsdd_property = bsdd_properties[row]
        index = self.createIndex(row, column, bsdd_property)
        return index

    def setData(self, index, value, /, role=...):
        return False


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> ClassPropertyTableModel:
        return super().sourceModel()
