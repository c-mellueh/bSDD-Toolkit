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
            check_state = Qt.CheckState(value)
            if check_state == Qt.CheckState.PartiallyChecked:
                check_state = Qt.CheckState.Checked
            new_value = check_state == Qt.CheckState.Checked
            setter_func(self, index, new_value)
            self._emit_row_changed(index)
            self._refresh_boolean_descendants(index)
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

        base |= Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        getter_func = self.tool.value_getter_functions(self)[index.column()]
        value = getter_func(index.internalPointer())
        if isinstance(value, bool):
            base |= Qt.ItemFlag.ItemIsUserCheckable
            base &= ~Qt.ItemFlag.ItemIsEditable
            base &= ~Qt.ItemFlag.ItemIsUserTristate
            if not self._are_boolean_parents_enabled(index):
                base &= ~Qt.ItemFlag.ItemIsEnabled
                base &= ~Qt.ItemFlag.ItemIsUserCheckable

        return base

    def _are_boolean_parents_enabled(self, index: QModelIndex) -> bool:
        """Return True when all boolean ancestors of *index* are enabled/checked."""
        column = index.column()
        parent = index.parent()
        if not parent.isValid():
            return True

        getter_func = self.tool.value_getter_functions(self)[column]
        while parent.isValid():
            parent_value = getter_func(parent.internalPointer())
            if isinstance(parent_value, bool) and not parent_value:
                return False
            parent = parent.parent()
        return True

    def _refresh_boolean_descendants(self, index: QModelIndex) -> None:
        """Emit dataChanged for boolean descendants so views refresh their flags."""
        column = index.column()
        origin = index.siblingAtColumn(0) if index.isValid() else QModelIndex()
        stack = [origin]
        while stack:
            parent = stack.pop()
            rows = self.rowCount(parent)
            column_count = self.columnCount(parent)
            for row in range(rows):
                child_row_index = self.index(row, 0, parent)
                if not child_row_index.isValid():
                    continue
                if column_count:
                    last_col_index = self.index(row, column_count - 1, parent)
                    self.dataChanged.emit(child_row_index, last_col_index, [])
                child_checkbox_index = self.index(row, column, parent)
                if child_checkbox_index.isValid():
                    self._emit_row_changed(child_checkbox_index)
                stack.append(child_row_index)

    def _emit_row_changed(self, index: QModelIndex) -> None:
        """Emit dataChanged covering the entire row for *index*."""
        if not index.isValid():
            return
        parent = index.parent()
        column_count = self.columnCount(parent)
        if column_count == 0:
            return
        first = index.siblingAtColumn(0)
        last = index.siblingAtColumn(column_count - 1)
        self.dataChanged.emit(first, last, [])

    def get_row_for_data(self, data, parent=None):
        parent = QModelIndex() if parent is None else parent
        for row in range(self.rowCount(parent)):
            if self.index(row, 0).internalPointer() == data:
                return row
        return -1
