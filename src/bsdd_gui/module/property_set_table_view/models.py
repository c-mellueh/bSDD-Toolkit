from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget
from PySide6.QtCore import (
    Qt,
    QCoreApplication,
    QModelIndex,
    QSortFilterProxyModel,
)

from typing import Type
from bsdd_json.utils import class_utils
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_json.models import BsddDictionary, BsddClass
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import ItemModel
import qtawesome as qta
from bsdd_gui.module.class_tree_view.constants import (
    JSON_MIME as CLASS_JSON_MIME,
    CODES_MIME as CLASS_CODES_MIME,
)


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

    def flags(self, index: QModelIndex):
        base = super().flags(index)
        if not index.isValid():
            return base | Qt.ItemIsDropEnabled
        return base | Qt.ItemIsEditable | Qt.ItemIsDropEnabled

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def mimeTypes(self):
        return [CLASS_JSON_MIME, CLASS_CODES_MIME, "application/json", "text/plain"]

    def _get_payload_from_data(self, data):
        from bsdd_gui.tool import ClassTreeView

        return ClassTreeView.get_payload_from_data(data)

    def _get_codes_from_data(self, data):
        from bsdd_gui.tool import ClassTreeView

        codes = ClassTreeView.get_codes_from_data(data)
        if codes:
            return codes
        payload = self._get_payload_from_data(data)
        if isinstance(payload, dict):
            roots = payload.get("roots")
            if isinstance(roots, list):
                return [c for c in roots if isinstance(c, str)]
            classes = payload.get("classes")
            if isinstance(classes, list):
                return [
                    c.get("Code")
                    for c in classes
                    if isinstance(c, dict) and isinstance(c.get("Code"), str)
                ]
        return None

    def canDropMimeData(self, data, action, row, column, parent):
        if action not in (Qt.CopyAction, Qt.MoveAction, Qt.IgnoreAction):
            return False
        if not self.active_class:
            return False

        if not (
            data.hasFormat(CLASS_JSON_MIME)
            or data.hasFormat(CLASS_CODES_MIME)
            or data.hasFormat("application/json")
            or data.hasFormat("text/plain")
        ):
            return False

        codes = self._get_codes_from_data(data)
        if not codes:
            return False

        for code in codes:
            bsdd_class = class_utils.get_class_by_code(self.bsdd_data, code)
            if bsdd_class and bsdd_class.ClassType == "GroupOfProperties":
                return True
        return False

    def dropMimeData(self, data, action, row, column, parent):
        if not self.active_class:
            return False
        codes = self._get_codes_from_data(data)
        if not codes:
            return False

        related = tool.PropertySetTableView.get_related_psets(
            self.active_class, self.bsdd_data
        )
        related_names = {c.Name for c in related}
        added = False
        for code in codes:
            bsdd_class = class_utils.get_class_by_code(self.bsdd_data, code)
            if not bsdd_class or bsdd_class.ClassType != "GroupOfProperties":
                continue
            if bsdd_class.Name in related_names:
                continue
            tool.PropertySetTableView.create_connected_pset(
                bsdd_class.Name, self.active_class, self.bsdd_data
            )
            added = True

        if added:
            tool.PropertySetTableView.signals.model_refresh_requested.emit()
        return added


# typing
class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sourceModel(self) -> PsetTableModel:
        return super().sourceModel()
