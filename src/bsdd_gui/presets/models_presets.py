from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import (
    QAbstractItemModel,
    Qt,
    QCoreApplication,
    QModelIndex,
    QSortFilterProxyModel,
)
from bsdd_json.models import BsddDictionary, BsddClass, BsddClassProperty
from bsdd_gui import tool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui.presets.tool_presets import ItemViewTool


class ItemModel(QAbstractItemModel):

    def __init__(self, tool: ItemViewTool, bsdd_data: object, *args, **kwargs):
        self.tool = tool
        self.bsdd_data = bsdd_data
        super().__init__(*args, **kwargs)

    def columnCount(self, /, parent=...):
        return self.tool.get_column_count(self)

    def parent(self, index: QModelIndex):
        return QModelIndex()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        getter_func = self.tool.value_getter_functions(self)[index.column()]
        value = getter_func(index.internalPointer())

        if isinstance(value, bool):
            if role == Qt.ItemDataRole.CheckStateRole:
                return Qt.CheckState.Checked if value else Qt.CheckState.Unchecked
            if role == Qt.ItemDataRole.EditRole:
                return value
            if role == Qt.ItemDataRole.DisplayRole:
                return None
            return None

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return value

        return None

    def setData(self, index, value, /, role=...):
        if not index.isValid():
            return False

        setter_func = self.tool.value_setter_functions(self)[index.column()]
        if setter_func is None:
            return False

        if role == Qt.ItemDataRole.CheckStateRole:
            # CheckStateRole passes an enum/int; convert to bool for the setter.
            new_value = value == Qt.CheckState.Checked
            setter_func(self, index, new_value)
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole, Qt.CheckStateRole])
            return True

        if role == Qt.ItemDataRole.EditRole:
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

    def flags(self, index: QModelIndex):
        """Ensure items are selectable and enabled for keyboard navigation.

        Qt's default flags implementation may not include ItemIsSelectable,
        which prevents arrow-key navigation/selecting. This base implementation
        guarantees that valid indexes are both enabled and selectable.
        """
        base = super().flags(index)
        if not index.isValid():
            return base

        base |= Qt.ItemIsSelectable | Qt.ItemIsEnabled

        getter_func = self.tool.value_getter_functions(self)[index.column()]
        value = getter_func(index.internalPointer())
        if isinstance(value, bool):
            base |= Qt.ItemIsUserCheckable
            base &= ~Qt.ItemIsEditable

        return base

    def get_row_for_data(self, data, parent=None):
        parent = QModelIndex() if parent is None else parent
        for row in range(self.rowCount(parent)):
            if self.index(row, 0).internalPointer() == data:
                return row
        return -1
