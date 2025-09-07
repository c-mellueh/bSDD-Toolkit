from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import (
    QAbstractItemModel,
    Qt,
    QCoreApplication,
    QModelIndex,
    QSortFilterProxyModel,
    QMimeData,
    QByteArray,
)
from bsdd_json.utils import property_utils as prop_utils
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_json.models import BsddDictionary, BsddClass, BsddClassProperty, BsddProperty
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import ItemModel
from .constants import JSON_MIME as PROP_JSON_MIME, CODES_MIME as PROP_CODES_MIME
from bsdd_gui.module.class_tree_view.constants import (
    JSON_MIME as CLASS_JSON_MIME,
)
import json


class PropertyTableModel(ItemModel):

    def __init__(self, *args, **kwargs):
        super().__init__(tool.PropertyTableWidget, None, *args, **kwargs)

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

    def get_row_from_property(self, bsdd_property: BsddProperty):
        for row in range(self.rowCount()):
            if self.index(row, 0).internalPointer() == bsdd_property:
                return row
        return -1

    def append_property(self, bsdd_property: BsddProperty):
        row = self.rowCount()
        self.beginInsertRows(QModelIndex(), row, row)
        self.bsdd_dictionary.Properties.append(bsdd_property)
        self.endInsertRows()

    def remove_property(self, bsdd_property: BsddProperty):
        row = self.get_row_from_property(bsdd_property)
        self.beginRemoveRows(QModelIndex(), row, row)
        self.bsdd_dictionary.Properties.remove(bsdd_property)
        self.endRemoveRows()

    # Drag & drop support (copy between instances)
    def flags(self, index: QModelIndex):
        base = super().flags(index)
        if not index.isValid():
            # allow dropping onto the view (root)
            return base | Qt.ItemIsDropEnabled
        # enable drag from rows; drop is only on root
        return base | Qt.ItemIsDragEnabled

    def supportedDropActions(self):
        # copy only; no internal reordering
        return Qt.CopyAction

    def mimeTypes(self):
        # include our JSON for cross-instance, and plain text of codes for convenience
        return [PROP_JSON_MIME, "application/json", "text/plain"]

    def _properties_to_json_bytes(self, props: list[BsddProperty]) -> bytes:
        payload = {
            "kind": "BsddPropertyTransfer",
            "version": 1,
            "properties": [p.model_dump(mode="json") for p in props],
            "codes": [p.Code for p in props],
        }
        return json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def mimeData(self, indexes):
        sel = []
        seen_codes: set[str] = set()
        for idx in indexes:
            if not idx.isValid() or idx.column() != 0:
                continue
            node: BsddProperty = idx.internalPointer()
            code = node.Code
            if code in seen_codes:
                continue
            seen_codes.add(code)
            sel.append(node)

        md = QMimeData()
        md.setData(PROP_JSON_MIME, QByteArray(self._properties_to_json_bytes(sel)))
        md.setText(json.dumps([p.Code for p in sel], ensure_ascii=False))
        return md

    def _get_payload_from_data(self, data: QMimeData):
        # Try multiple formats for robustness
        for fmt in (PROP_JSON_MIME, CLASS_JSON_MIME, "application/json", "text/plain"):
            if data.hasFormat(fmt):
                try:
                    b = bytes(data.data(fmt))
                    if fmt == "text/plain":
                        b = b.strip()
                    return json.loads(b.decode("utf-8"))
                except Exception:
                    continue
        return None

    def canDropMimeData(self, data, action, row, column, parent: QModelIndex) -> bool:
        if action not in (Qt.CopyAction, Qt.IgnoreAction):
            return False
        if data.hasFormat(PROP_JSON_MIME) or data.hasFormat(CLASS_JSON_MIME):
            return True
        # Also accept generic JSON if it looks like our payload
        if data.hasFormat("application/json") or data.hasFormat("text/plain"):
            payload = self._get_payload_from_data(data)
            if isinstance(payload, dict) and "properties" in payload:
                return True
        return False

    def dropMimeData(self, data, action, row, column, parent: QModelIndex) -> bool:
        payload = self._get_payload_from_data(data)
        if not isinstance(payload, dict):
            return False
        # accept both property and class-transfer payloads, but use only properties list
        props_json = payload.get("properties", [])
        if not isinstance(props_json, list):
            return False

        # existing property codes in target dictionary
        properties = tool.PropertyTableWidget.get_properties_from_mime_payload(
            payload, self.bsdd_dictionary
        )
        for bsdd_property in properties:
            tool.PropertyTableWidget.add_property_to_dictionary(bsdd_property, self.bsdd_dictionary)
        return True


class ClassTableModel(ItemModel):

    def __init__(self, *args, **kwargs):
        super().__init__(tool.PropertyTableWidget, None, *args, **kwargs)
        self._data = None

    @property
    def bsdd_dictionary(self):
        return tool.Project.get()

    @property
    def active_property(self) -> BsddProperty:
        return tool.PropertyTableWidget.get_active_property()

    @property
    def active_classes(self) -> list[BsddClass]:
        ap = self.active_property
        if not ap:
            return []
        if self._data is None:
            self._data = prop_utils.get_classes_with_bsdd_property(ap.Code, self.bsdd_dictionary)
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
