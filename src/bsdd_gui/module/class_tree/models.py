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
from bsdd_parser.models import BsddDictionary, BsddClass
from bsdd_gui import tool

class ClassTreeModel(QAbstractItemModel):

    def __init__(self, bsdd_dictionary: BsddDictionary, *args, **kwargs):
        self.bsdd_dictionary = bsdd_dictionary
        super().__init__(*args, **kwargs)

    def headerData(self, section, orientation, /, role=...):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                if section == 0:
                    return QCoreApplication.translate("ClassTree", "Class")
                if section == 1:
                    return QCoreApplication.translate("ClassTree", "Code")
                if section == 2:
                    return QCoreApplication.translate("ClassTree", "Status")
        return None

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return len(tool.ClassTree.get_root_classes(self.bsdd_dictionary))
        else:
            bsdd_class: BsddClass = parent.internalPointer()
            return len(tool.ClassTree.get_children(bsdd_class))

    def columnCount(self, parent=QModelIndex()):
        return 3

    def index(self, row: int, column: int, parent=QModelIndex()):
        if not parent.isValid():
            if 0 > row >= len(self.bsdd_dictionary.Classes):
                return QModelIndex()
            bsdd_class = tool.ClassTree.get_root_classes(self.bsdd_dictionary)[row]
            index = self.createIndex(row, column, bsdd_class)
            return index
        parent = parent.siblingAtColumn(0)
        parent_class: BsddClass = parent.internalPointer()
        children = tool.ClassTree.get_children(parent_class)
        if row >= len(children) or row <0:
            return QModelIndex()
        bsdd_class = children[row]
        index = self.createIndex(row, column, bsdd_class)
        return index

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.CheckStateRole):
            return None
        if Qt.ItemDataRole.DisplayRole != role:
            return None
        data:BsddClass = index.internalPointer()

        if index.column() == 0:
            return data.Name
        elif index.column()== 1:
            return data.Code
        elif index.column() == 2:
            return data.Status
        return None

    def setData(self, index, value, /, role = ...):
        return False

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()
        bsdd_class:BsddClass = index.internalPointer()
        if not bsdd_class.ParentClassCode:
            return QModelIndex()
        parent_class = tool.ClassTree.get_class_by_code(self.bsdd_dictionary,bsdd_class.ParentClassCode)
        row = tool.ClassTree.get_row_index(parent_class)

        return self.createIndex(row,0,parent_class)


#typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        self.super(*args, **kwargs)
    
    def sourceModel(self) -> ClassTreeModel:
        return super().sourceModel()
