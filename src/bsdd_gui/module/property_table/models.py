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


class PropertyTableModel(ItemModel):

    def __init__(self, *args, **kwargs):
        super().__init__(tool.PropertyTable, *args, **kwargs)

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        rc = len(self.bsdd_dictionary.Properties)
        return rc

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()
        bsdd_properties = self.bsdd_dictionary.Properties
        bsdd_property = bsdd_properties[row]
        index = self.createIndex(row, column, bsdd_property)
        return index

    def setData(self, index, value, /, role=...):
        return False


class ClassTableModel(ItemModel):

    def __init__(self, *args, **kwargs):
        super().__init__(tool.PropertyTable, *args, **kwargs)
        self._data = None

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    @property
    def active_property(self) -> BsddProperty:
        return tool.PropertyTable.get_active_property()

    @property
    def active_classes(self) -> list[BsddClass]:
        ap = self.active_property
        if not ap:
            return []
        if self._data is None:
            self._data = cp_utils.get_classes_with_bsdd_property(ap.Code, self.bsdd_dictionary)
        return self._data

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.active_classes)

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()

        ac = self.active_classes
        if not ac:
            return QModelIndex()
        index = self.createIndex(row, column, ac[row])
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

    def sourceModel(self) -> PropertyTableModel:
        return super().sourceModel()
