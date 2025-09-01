from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import (
    QAbstractItemModel,
    Qt,
    QCoreApplication,
    QModelIndex,
    QSortFilterProxyModel,
)
from bsdd_parser.utils import bsdd_class_property as cp_utils
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_parser.models import BsddDictionary, BsddClass, BsddClassProperty, BsddProperty
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import ItemModel


class PropertyModel(ItemModel):

    def __init__(self, bsdd_property: BsddProperty, *args, **kwargs):
        super().__init__(tool.PropertyTable, *args, **kwargs)
        self.bsdd_property = bsdd_property

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.bsdd_property.PropertyRelations)

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()
        relations = self.bsdd_property.PropertyRelations
        bsdd_property_relation = relations[row]
        index = self.createIndex(row, column, bsdd_property_relation)
        return index

    def setData(self, index, value, /, role=...):
        return False


class ClassModel(ItemModel):

    def __init__(self, bsdd_class: BsddClass, *args, **kwargs):
        super().__init__(tool.PropertyTable, *args, **kwargs)
        self.bsdd_class = bsdd_class

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.bsdd_class.ClassRelations)

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()
        relations = self.bsdd_class.ClassRelations
        bsdd_class_relation = relations[row]
        index = self.createIndex(row, column, bsdd_class_relation)
        return index

    def setData(self, index, value, /, role=...):
        return False

    def beginResetModel(self):
        self._data = None
        return super().beginResetModel()


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> PropertyModel | ClassModel:
        return super().sourceModel()
