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

        if role != Qt.ItemDataRole.DisplayRole:
            return None
        getter_func = self.tool.value_getter_functions(self)[index.column()]
        return getter_func(index.internalPointer())

    def setData(self, index, value, /, role=...):
        if not index.isValid():
            return False
        if role == Qt.ItemDataRole.EditRole:
            setter_func = self.tool.value_setter_functions(self)[index.column()]
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

    def flags(self, index: QModelIndex):
        """Ensure items are selectable and enabled for keyboard navigation.

        Qt's default flags implementation may not include ItemIsSelectable,
        which prevents arrow-key navigation/selecting. This base implementation
        guarantees that valid indexes are both enabled and selectable.
        """
        base = super().flags(index)
        if not index.isValid():
            return base
        return base | Qt.ItemIsSelectable | Qt.ItemIsEnabled
