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
            roots = cl_utils.get_root_classes(self.bsdd_dictionary)
            if row < 0 or row >= len(roots):
                return QModelIndex()
            bsdd_class = roots[row]
            return self.createIndex(row, column, bsdd_class)
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

    def _get_current_parent_index(self, bsdd_class: BsddClass):
        # Determine the correct parent index in the CURRENT hierarchy
        if bsdd_class.ParentClassCode:
            parent_class = cl_utils.get_class_by_code(
                self.bsdd_dictionary, bsdd_class.ParentClassCode
            )
            if parent_class is None:
                parent_index = QModelIndex()
            else:
                parent_index = self._index_for_class(parent_class)
        else:
            parent_index = QModelIndex()
        return parent_index

    def append_row(self, bsdd_class: BsddClass):
        parent_index = self._get_current_parent_index(bsdd_class)

        insert_row = self.rowCount(parent_index)  # current child count
        self.beginInsertRows(parent_index, insert_row, insert_row)
        # mutate your data
        self.bsdd_dictionary.Classes.append(bsdd_class)
        bsdd_class._set_parent(self.bsdd_dictionary)
        self.endInsertRows()

    def remove_row(self, bsdd_class: BsddClass):
        parent_index = self._get_current_parent_index(bsdd_class)
        row = cl_utils.get_row_index(bsdd_class)
        self.beginRemoveRows(parent_index, row, row)
        cl_utils.remove_class(bsdd_class)
        self.endRemoveRows()

    def move_row(self, bsdd_class: BsddClass, new_parent: BsddClass | None):
        old_parent_index = self._get_current_parent_index(bsdd_class)
        new_parent_index = (
            QModelIndex() if new_parent is None else self._index_for_class(new_parent)
        )
        row = cl_utils.get_row_index(bsdd_class)
        new_row_count = self.rowCount(new_parent_index)
        self.beginMoveRows(old_parent_index, row, row, new_parent_index, new_row_count)
        bsdd_class.ParentClassCode = None if new_parent is None else new_parent.Code
        self.endMoveRows()

    def _index_for_class(self, cls: BsddClass) -> QModelIndex:
        """Return the QModelIndex for an existing class object."""
        # find its parent chain to build the index properly
        parent_code = cls.ParentClassCode
        if parent_code:
            parent_cls = cl_utils.get_class_by_code(self.bsdd_dictionary, parent_code)
            gp_idx = self._index_for_class(parent_cls)  # recurse to get parent's parent index
            # children of the parent
            children = cl_utils.get_children(parent_cls)
            row = children.index(cls)
            return self.index(row, 0, gp_idx)
        else:
            # root class
            roots = cl_utils.get_root_classes(self.bsdd_dictionary)
            row = roots.index(cls)
            return self.index(row, 0, QModelIndex())


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> ClassTreeModel:
        return super().sourceModel()
