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
from bsdd_parser.utils import bsdd_class as cl_utils
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import TableModel


class ClassTreeModel(TableModel):

    def __init__(self, bsdd_dictionary: BsddDictionary, *args, **kwargs):
        super().__init__(tool.ClassTree, *args, **kwargs)

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return len(cl_utils.get_root_classes(self.bsdd_dictionary))
        else:
            bsdd_class: BsddClass = parent.internalPointer()
            return len(cl_utils.get_children(bsdd_class))

    def index(self, row: int, column: int, parent=QModelIndex()):
        if not parent.isValid():
            if 0 > row >= len(self.bsdd_dictionary.Classes):
                return QModelIndex()
            bsdd_class = cl_utils.get_root_classes(self.bsdd_dictionary)[row]
            index = self.createIndex(row, column, bsdd_class)
            return index
        parent = parent.siblingAtColumn(0)
        parent_class: BsddClass = parent.internalPointer()
        children = cl_utils.get_children(parent_class)
        if row >= len(children) or row < 0:
            return QModelIndex()
        bsdd_class = children[row]
        index = self.createIndex(row, column, bsdd_class)
        return index

    def setData(self, index, value, /, role=...):
        return False

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()
        bsdd_class: BsddClass = index.internalPointer()
        if not bsdd_class.ParentClassCode:
            return QModelIndex()
        parent_class = cl_utils.get_class_by_code(self.bsdd_dictionary, bsdd_class.ParentClassCode)
        row = cl_utils.get_row_index(parent_class)

        return self.createIndex(row, 0, parent_class)


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> ClassTreeModel:
        return super().sourceModel()
