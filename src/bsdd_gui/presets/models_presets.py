from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import (
    QAbstractItemModel,
    Qt,
    QCoreApplication,
    QModelIndex,
    QSortFilterProxyModel,
)
from bsdd_parser.models import BsddDictionary, BsddClass, BsddClassProperty
from bsdd_gui import tool
from bsdd_gui.presets.tool_presets import ColumnHandler


class TableModel(QAbstractItemModel):
    def __init__(self, tool: ColumnHandler, *args, **kwargs):
        self.tool = tool
        super().__init__(*args, **kwargs)

    def columnCount(self, /, parent=...):
        return self.tool.get_column_count(self)

    def parent(self, index: QModelIndex):
        return QModelIndex()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        getter_func = self.tool.get_value_functions(self)[index.column()]
        return getter_func(index.internalPointer())

    def setData(self, index, value, /, role=...):
        if not index.isValid():
            return False
        if role == Qt.ItemDataRole.EditRole:
            setter_func = self.tool.set_value_functions(self)[index.column()]
            if setter_func is None:
                return False
            setter_func(self, index, value)
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def headerData(self, section, orientation, /, role=...):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Vertical:
            return None
        return self.tool.get_column_names(self)[section]
