from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget
from PySide6.QtCore import (
    Qt,
    QCoreApplication,
    QModelIndex,
    QSortFilterProxyModel,
)
from PySide6.QtGui import QDragEnterEvent,QDragMoveEvent

from typing import Type
from bsdd_json.utils import class_utils
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_json.models import BsddDictionary, BsddClass
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import ItemModel
import qtawesome as qta


class PsetTableModel(ItemModel):

    def __init__(self, tl=None, bsdd_data: BsddDictionary = None, *args, **kwargs):
        super().__init__(tool.PropertySetTableView, bsdd_data, *args, **kwargs)
        self.bsdd_data: BsddDictionary
        self.tool: Type[tool.PropertySetTableView]

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
        if role != Qt.ItemDataRole.DecorationRole:
            return super().data(index, role)

        if index.column() != 0:
            return QModelIndex()
        if class_utils.is_pset_linked(self.active_class, index.internalPointer(), self.bsdd_data):
            return qta.icon("mdi.link-variant")
        else:
            return QModelIndex()

    def canDropMimeData(self, mimeData, action, row, column, parent):
        # Nur bestimmte MIME-Typen erlauben
        if mimeData.hasFormat("application/x-my-custom-type"):
            return True

        # z.B. Text explizit verbieten
        if mimeData.hasText():
            return False

        return False

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.source() is None:  # different process
            e.setDropAction(Qt.CopyAction)
            e.accept()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e: QDragMoveEvent):
        if e.source() is None:
            e.setDropAction(Qt.CopyAction)
            e.accept()
        else:
            super().dragMoveEvent(e)


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> PsetTableModel:
        return super().sourceModel()
