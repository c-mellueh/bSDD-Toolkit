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
from bsdd_json.models import BsddDictionary, BsddClass
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import ItemModel


class PsetTableModel(ItemModel):

    def __init__(self, bsdd_dictionary: BsddDictionary, *args, **kwargs):
        super().__init__(tool.PropertySetTableView, bsdd_dictionary, *args, **kwargs)
        self.bsdd_data: BsddDictionary

    @property
    def active_class(self):
        return tool.MainWindowWidget.get_active_class()

    def rowCount(self, parent=QModelIndex()):
        if not self.active_class:
            return 0
        if not parent.isValid():
            return len(tool.PropertySetTableView.get_pset_names_with_temporary(self.active_class))

    def index(self, row: int, column: int, parent=QModelIndex()):
        if parent.isValid():
            return QModelIndex()

        if 0 > row >= len(self.rowCount()):
            return QModelIndex()

        pset_name = tool.PropertySetTableView.get_pset_names_with_temporary(self.active_class)[row]
        index = self.createIndex(row, column, pset_name)
        return index

    def flags(self, index):
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    # def setData(self, index: QModelIndex, value, role=Qt.EditRole):
    #     return super().setData(index,value,role)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        test = 0
        return super().data(index, role)


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> PsetTableModel:
        return super().sourceModel()
