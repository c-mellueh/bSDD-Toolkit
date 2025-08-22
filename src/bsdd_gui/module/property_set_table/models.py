from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import (
    QAbstractListModel,
    Qt,
    QCoreApplication,
    QModelIndex,
    QSortFilterProxyModel,
)
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_parser.models import BsddDictionary, BsddClass
from bsdd_gui import tool


class PsetListModel(QAbstractListModel):

    def __init__(self, bsdd_dictionary: BsddDictionary, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    @property
    def active_class(self):
        return tool.MainWindow.get_active_class()

    def rowCount(self, parent=QModelIndex()):
        if not self.active_class:
            return 0
        if not parent.isValid():
            return len(tool.PropertySetTable.get_pset_list(self.active_class))

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()

        pset_name = tool.PropertySetTable.get_pset_list(self.active_class)[row]
        index = self.createIndex(row, column, pset_name)
        return index

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None
        pset_name = tool.PropertySetTable.get_pset_list(self.active_class)[index.row()]
        return pset_name

    def setData(self, index, value, /, role = ...):
        return False

    def parent(self, index: QModelIndex):
        return QModelIndex()


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sourceModel(self) -> PsetListModel:
        return super().sourceModel()
