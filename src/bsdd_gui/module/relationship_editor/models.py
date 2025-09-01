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


class RelationshipModel(ItemModel):

    def __init__(
        self,
        data: BsddClass | BsddProperty,
        mode: Literal["dialog"] | Literal["live"],
        *args,
        **kwargs,
    ):
        super().__init__(tool.RelationshipEditor, *args, **kwargs)
        self.item_data: BsddClass | BsddProperty = data
        self.mode: Literal["dialog"] | Literal["live"] = mode
        self.virtual_append: list[BsddClassRelation | BsddPropertyRelation] = []
        self.virtual_remove: list[BsddClassRelation | BsddPropertyRelation] = []

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        if isinstance(self.item_data, BsddClass):
            base_count = len(self.item_data.ClassRelations)
        else:
            base_count = len(self.item_data.PropertyRelations)
        return base_count + len(self.virtual_append) - len(self.virtual_remove)

    def get_virtual_list(self) -> list[BsddClassRelation | BsddPropertyRelation]:
        if isinstance(self.item_data, BsddClass):
            items = [cr for cr in self.item_data.ClassRelations if cr not in self.virtual_remove]
        else:
            items = [pr for pr in self.item_data.PropertyRelations if pr not in self.virtual_remove]
        return items + self.virtual_append

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()
        relations = self.get_virtual_list()
        relation = relations[row]
        index = self.createIndex(row, column, relation)
        return index

    def setData(self, index, value, /, role=...):
        return False

    def beginResetModel(self):
        self._data = None
        return super().beginResetModel()

    def append_row(self, relation: BsddClassRelation | BsddPropertyRelation):
        # Prevent duplicates for class relations (preserve previous ClassModel behavior)
        if isinstance(self.item_data, BsddClass):
            if relation in self.item_data.ClassRelations:
                return
        # Also avoid duplicate virtual appends
        if relation in self.virtual_append:
            return
        parent_index = QModelIndex()
        insert_row = self.rowCount(parent_index)  # current child count
        self.beginInsertRows(parent_index, insert_row, insert_row)
        if relation in self.virtual_remove and self.mode == "dialog":
            self.virtual_remove.remove(relation)
        else:
            if self.mode == "dialog":
                self.virtual_append.append(relation)
            else:
                if isinstance(self.item_data, BsddClass):
                    self.item_data.ClassRelations.append(relation)  # type: ignore[arg-type]
                else:
                    self.item_data.PropertyRelations.append(relation)  # type: ignore[arg-type]
        self.endInsertRows()


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> RelationshipModel:
        return super().sourceModel()
