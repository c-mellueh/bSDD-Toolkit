from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import (
    QAbstractItemModel,
    Qt,
    QCoreApplication,
    QModelIndex,
    QSortFilterProxyModel,
)
from bsdd_parser.models import BsddDictionary, BsddClass,BsddClassProperty
from bsdd_gui import tool
from bsdd_gui.presets.tool_presets import ColumnHandler
class TableModel(QAbstractItemModel):
    def __init__(self, tool:ColumnHandler,*args,**kwargs):
        self.tool = tool
        super().__init__(*args,**kwargs)
    
    def columnCount(self, /, parent = ...):
        return self.tool.get_column_count()
    
    def parent(self, index: QModelIndex):
        return QModelIndex()
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        bsdd_property: BsddClassProperty = index.internalPointer()
        getter_func = self.tool.get_value_functions()[index.column()]
        
        return getter_func(bsdd_property)
    
    def headerData(self, section, orientation, /, role = ...):
        if orientation == Qt.Orientation.Vertical:
            return None
        return self.tool.get_column_names()[section]
