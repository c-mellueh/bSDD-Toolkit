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
from bsdd_parser.models import BsddDictionary, BsddClass,BsddClassProperty
from bsdd_gui import tool


class PropertyTableModel(QAbstractItemModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        if not self.active_class:
            return 0
        if not self.active_pset:
            return 0
        if parent.isValid():
            return 0
        rc = len(tool.PropertyTable.filter_properties_by_pset(self.active_class,self.active_pset))
        print(rc)
        return  rc
    def columnCount(self, /, parent = ...):
        return 5

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()
        bsdd_properties = tool.PropertyTable.filter_properties_by_pset(self.active_class,self.active_pset)
        bsdd_property = bsdd_properties[row]
        index = self.createIndex(row, column, bsdd_property)
        return index

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None
        
        col = index.column()
        bsdd_property:BsddClassProperty = index.internalPointer()
        if col == 0:
            return bsdd_property.Code
        if col == 1:
            return bsdd_property.IsRequired
        if col == 2:
            return tool.PropertyTable.get_datatype(bsdd_property)

    def setData(self, index, value, /, role = ...):
        return False

    def parent(self, index: QModelIndex):
        return QModelIndex()


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sourceModel(self) -> PropertyTableModel:
        return super().sourceModel()
