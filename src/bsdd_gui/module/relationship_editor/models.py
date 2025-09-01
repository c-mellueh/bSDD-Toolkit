from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import (
    QAbstractItemModel,
    Qt,
    QCoreApplication,
    QModelIndex,
    QSortFilterProxyModel,
)
from typing import Literal
from bsdd_parser.utils import bsdd_class_property as cp_utils
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_parser.models import (
    BsddDictionary,
    BsddClass,
    BsddClassProperty,
    BsddProperty,
    BsddClassRelation,
    BsddPropertyRelation,
)
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import ItemModel


class PropertyModel(ItemModel):

    def __init__(
        self,
        bsdd_property: BsddProperty,
        mode: Literal["dialog"] | Literal["live"],
        *args,
        **kwargs,
    ):
        super().__init__(tool.RelationshipEditor, *args, **kwargs)
        self.bsdd_property = bsdd_property
        self.mode: Literal["dialog"] | Literal["live"] = mode
        self.virtual_append = list()
        self.virtual_remove = list()

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return (
            len(self.bsdd_property.PropertyRelations)
            + len(self.virtual_append)
            - len(self.virtual_remove)
        )

    def get_virtual_list(self) -> list[BsddClassRelation]:
        items = [cr for cr in self.bsdd_property.PropertyRelations if cr not in self.virtual_remove]
        return items + self.virtual_append

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()
        relations = self.get_virtual_list()
        bsdd_property_relation = relations[row]
        index = self.createIndex(row, column, bsdd_property_relation)
        return index

    def setData(self, index, value, /, role=...):
        return False

    def append_row(self, property_relation: BsddPropertyRelation):
        parent_index = QModelIndex()
        insert_row = self.rowCount(parent_index)  # current child count
        self.beginInsertRows(parent_index, insert_row, insert_row)
        self.bsdd_property.PropertyRelations.append(property_relation)
        self.endInsertRows()


class ClassModel(ItemModel):

    def __init__(
        self, bsdd_class: BsddClass, mode: Literal["dialog"] | Literal["live"], *args, **kwargs
    ):
        super().__init__(tool.RelationshipEditor, *args, **kwargs)
        self.bsdd_class = bsdd_class
        self.mode: Literal["dialog"] | Literal["live"] = mode
        self.virtual_append = list()
        self.virtual_remove = list()

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return (
            len(self.bsdd_class.ClassRelations)
            + len(self.virtual_append)
            - len(self.virtual_remove)
        )

    def get_virtual_list(self) -> list[BsddClassRelation]:
        items = [cr for cr in self.bsdd_class.ClassRelations if cr not in self.virtual_remove]
        return items + self.virtual_append

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()
        relations = self.get_virtual_list()
        bsdd_class_relation = relations[row]
        index = self.createIndex(row, column, bsdd_class_relation)
        return index

    def setData(self, index, value, /, role=...):
        return False

    def beginResetModel(self):
        self._data = None
        return super().beginResetModel()

    def append_row(self, class_relation: BsddClassRelation):
        parent_index = QModelIndex()
        insert_row = self.rowCount(parent_index)  # current child count
        self.beginInsertRows(parent_index, insert_row, insert_row)
        self.bsdd_class.ClassRelations.append(class_relation)
        self.endInsertRows()

    def append_virtual_row(self, class_relation: BsddClassRelation):
        parent_index = QModelIndex()
        insert_row = self.rowCount(parent_index)  # current child count
        self.beginInsertRows(parent_index, insert_row, insert_row)
        self.virtual_append.append(class_relation)
        self.endInsertRows()


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> PropertyModel | ClassModel:
        return super().sourceModel()
