from bsdd_gui.module.class_tree_view.models import ClassTreeModel as CTM
from bsdd_gui.presets.models_presets import ItemModel
from bsdd_gui.module.class_tree_view.models import SortModel as SM
from bsdd_gui import tool
from PySide6.QtCore import QModelIndex, Qt
from bsdd_json import BsddClass, BsddClassProperty
from bsdd_json.utils import property_utils as prop_utils


class ClassTreeModel(CTM):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data, tool.IdsClassView, *args, **kwargs)
        self.is_check_inerheritance_enabled = False

    def set_checkstate_inheritance(self, value: bool) -> None:
        self.is_check_inerheritance_enabled = value
        self._refresh_boolean_descendants(QModelIndex())

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

    def flags(self, index: QModelIndex):
        base = super().flags(index)
        getter_func = self.tool.value_getter_functions(self)[index.column()]
        value = getter_func(index.internalPointer())

        if isinstance(value, bool):
            base |= Qt.ItemFlag.ItemIsUserCheckable
            base &= ~Qt.ItemFlag.ItemIsEditable
            base &= ~Qt.ItemFlag.ItemIsUserTristate
            if not self._are_boolean_parents_enabled(index) and self.is_check_inerheritance_enabled:
                base &= ~Qt.ItemFlag.ItemIsEnabled
                base &= ~Qt.ItemFlag.ItemIsUserCheckable
        return base

    def setData(self, index, value, /, role=...):
        val = super().setData(index, value, role)
        if not val:
            return False
        if role == Qt.ItemDataRole.CheckStateRole:
            self._emit_row_changed(index)
            self._refresh_boolean_descendants(index)
            return True


class PropertyTreeModel(ItemModel):
    def __init__(self, data, *args, **kwargs):
        """
        self.bsdd_data is the active bsdd_class
        """
        super().__init__(tool.IdsPropertyView,data,  *args, **kwargs)
        self.bsdd_data: BsddClass = None

    def hasChildren(self, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return False
        return super().hasChildren(parent)

    def rowCount(self, /, parent=...):
        from bsdd_gui import tool
        if not self.bsdd_data:
            return 0
        if not parent.isValid():
            return len(tool.PropertySetTableView.get_pset_names_with_temporary(self.bsdd_data))
        else:
            pset_name = parent.internalPointer()
            c_properties = prop_utils.get_class_properties_by_pset_name(self.bsdd_data, pset_name)
            return len(c_properties)

    def index(self, row: int, column: int, parent=QModelIndex()):
        if not parent.isValid():
            psets = tool.PropertySetTableView.get_pset_names_with_temporary(self.bsdd_data)
            if row < 0 or row >= len(psets):
                return QModelIndex()
            return self.createIndex(row, column, psets[row])
        else:
            pset_name = parent.internalPointer()
            c_properties = prop_utils.get_class_properties_by_pset_name(self.bsdd_data, pset_name)
            if row < 0 or row >= len(c_properties):
                return QModelIndex()
            return self.createIndex(row, column, c_properties[row])

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()
        val = index.internalPointer()
        if isinstance(val, str):
            return QModelIndex()
        else:
            val: BsddClassProperty
            pset_name = val.PropertySet
            psets = tool.PropertySetTableView.get_pset_names_with_temporary(self.bsdd_data)
            if pset_name in psets:
                row = psets.index(pset_name)
                return self.createIndex(row, 0, pset_name)
            return QModelIndex()
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        val = index.internalPointer()
        if isinstance(val, str):
            if role == Qt.ItemDataRole.DisplayRole and index.column() == 0:
                return val
            return None
        else:
            return super().data(index, role)

    def headerData(self, section, orientation, /, role=...):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Vertical:
            return None
        return self.tool.get_column_names(self)[section]

class SortModel(SM):
    pass
