from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import (
    Qt,
    QModelIndex,
    QSortFilterProxyModel,
)
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_json.models import BsddDictionary, BsddClass, BsddProperty
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import ItemModel
from PySide6.QtTest import QAbstractItemModelTester
import json

from .constants import JSON_MIME, CODES_MIME


class ClassTreeModel(ItemModel):

    def __init__(self, bsdd_dictionary: BsddDictionary, tl=None, *args, **kwargs):
        if tl is None:
            tl = tool.ClassTreeView
        super().__init__(tl, bsdd_dictionary, *args, **kwargs)
        self.bsdd_data: BsddDictionary

    @property
    def bsdd_dictionary(self):
        return self.bsdd_data

    def hasChildren(self, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return False
        return super().hasChildren(parent)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return 0
        if not parent.isValid():
            return len(cl_utils.get_root_classes(self.bsdd_dictionary))
        else:
            bsdd_class: BsddClass = parent.internalPointer()
            return len(cl_utils.get_children(bsdd_class))

    def index(self, row: int, column: int, parent=QModelIndex()):
        # Für Eltern in Spalte != 0 KEINE Kinder liefern
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        if not parent.isValid():
            roots = cl_utils.get_root_classes(self.bsdd_dictionary)
            if 0 <= row < len(roots):
                return self.createIndex(row, column, roots[row])
            return QModelIndex()

        parent = parent.siblingAtColumn(0)  # optional, schadet nicht
        parent_class: BsddClass = parent.internalPointer()
        children = cl_utils.get_children(parent_class)
        if 0 <= row < len(children):
            return self.createIndex(row, column, children[row])
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        node: BsddClass = index.internalPointer()
        if not node.ParentClassCode:
            return QModelIndex()  # root hat keinen Parent

        parent_cls = cl_utils.get_class_by_code(self.bsdd_dictionary, node.ParentClassCode)
        if parent_cls is None:
            return QModelIndex()

        # Geschwister des Elterns ermitteln – exakt wie in index():
        gp_code = parent_cls.ParentClassCode
        if gp_code:
            gp_cls = cl_utils.get_class_by_code(self.bsdd_dictionary, gp_code)
            siblings = (
                cl_utils.get_children(gp_cls)
                if gp_cls is not None
                else cl_utils.get_root_classes(self.bsdd_dictionary)
            )
        else:
            siblings = cl_utils.get_root_classes(self.bsdd_dictionary)

        try:
            row = siblings.index(parent_cls)
        except ValueError:
            return QModelIndex()

        return self.createIndex(row, 0, parent_cls)

    def _get_current_parent_index(self, bsdd_class: BsddClass):
        # Determine the correct parent index in the CURRENT hierarchy
        if bsdd_class.ParentClassCode:
            parent_class = cl_utils.get_class_by_code(
                self.bsdd_dictionary, bsdd_class.ParentClassCode
            )
            if parent_class is None:
                parent_index = QModelIndex()
            else:
                parent_index = self._index_for_class(parent_class)
        else:
            parent_index = QModelIndex()
        return parent_index

    def _parent_and_siblings(self, c: BsddClass) -> tuple[QModelIndex, list[BsddClass]]:
        """Ermittle *aktuellen* Parent-Index und die *aktuelle* Geschwisterliste von c."""
        if c.ParentClassCode:
            parent_cls = cl_utils.get_class_by_code(self.bsdd_dictionary, c.ParentClassCode)
            if parent_cls is not None:
                parent_index = self._index_for_class(parent_cls)
                siblings = cl_utils.get_children(parent_cls)
                return parent_index, siblings
        # Root-Fall
        return QModelIndex(), cl_utils.get_root_classes(self.bsdd_dictionary)

    def _index_for_class(self, cls: BsddClass) -> QModelIndex:
        """Return the QModelIndex for an existing class object."""
        # find its parent chain to build the index properly
        parent_code = cls.ParentClassCode
        if parent_code:
            parent_cls = cl_utils.get_class_by_code(self.bsdd_dictionary, parent_code)
            gp_idx = self._index_for_class(parent_cls)  # recurse to get parent's parent index
            # children of the parent
            children = cl_utils.get_children(parent_cls)
            row = children.index(cls)
            return self.index(row, 0, gp_idx)
        else:
            # root class
            roots = cl_utils.get_root_classes(self.bsdd_dictionary)
            if cls in roots:
                row = roots.index(cls)
            else:
                row = -1
            return self.index(row, 0, QModelIndex())

    def flags(self, index: QModelIndex):
        base = super().flags(index)
        if not index.isValid():
            return base | Qt.ItemIsDropEnabled & ~Qt.ItemIsEditable
        if index.column() == 0:
            return (
                base
                | Qt.ItemIsDragEnabled
                | Qt.ItemIsDropEnabled
                | Qt.ItemIsEditable & ~Qt.ItemIsEditable
            )
        return base & ~Qt.ItemIsEditable

    def supportedDropActions(self):
        # allow both move (internal) and copy (external)
        return Qt.MoveAction | Qt.CopyAction

    def mimeTypes(self):
        # include JSON for cross-instance, and an internal code-list for fast moves
        return [JSON_MIME, "application/json", CODES_MIME, "text/plain"]

    def mimeData(self, indexes):
        from bsdd_gui.tool import ClassTreeView

        classes = ClassTreeView.get_selected(self)
        return ClassTreeView.generate_mime_data(classes)

    def canDropMimeData(self, data, action, row, column, parent: QModelIndex) -> bool:
        if parent.isValid() and parent.column() != 0:
            return False
        if action not in (Qt.MoveAction, Qt.CopyAction):
            return False
        if (
            data.hasFormat(JSON_MIME)
            or data.hasFormat("application/json")
            or data.hasFormat(CODES_MIME)
        ):
            return True
        return False

    def dropMimeData(self, data, action, row, column, parent: QModelIndex) -> bool:
        dest_parent = parent.siblingAtColumn(0) if parent.isValid() else QModelIndex()
        dest_parent_node = dest_parent.internalPointer() if dest_parent.isValid() else None

        if action == Qt.MoveAction and data.hasFormat(CODES_MIME):
            trigger.mime_move_event(self.bsdd_data, data, row, parent)
        elif action in (Qt.CopyAction, Qt.IgnoreAction):
            trigger.mime_copy_event(self.bsdd_data, data, parent)
        return True


class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSortLocaleAware(True)

    def sourceModel(self) -> ClassTreeModel:
        return super().sourceModel()
