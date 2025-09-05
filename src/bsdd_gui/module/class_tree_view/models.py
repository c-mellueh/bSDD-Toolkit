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
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_json.models import BsddDictionary, BsddClass, BsddProperty
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_gui import tool
from bsdd_gui.presets.models_presets import ItemModel
from PySide6.QtTest import QAbstractItemModelTester
import json

JSON_MIME = "application/bsdd-class+json;v=1"
CODES_MIME = "application/x-bsdd-classcode"  # for fast internal moves


class ClassTreeModel(ItemModel):

    def __init__(self, bsdd_dictionary: BsddDictionary, *args, **kwargs):
        super().__init__(tool.ClassTreeView, bsdd_dictionary, *args, **kwargs)
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

    def setData(self, index, value, /, role=...):
        return False

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

    def append_row(self, bsdd_class: BsddClass):
        parent_index = self._get_current_parent_index(bsdd_class)

        insert_row = self.rowCount(parent_index)  # current child count
        self.beginInsertRows(parent_index, insert_row, insert_row)
        # mutate your data
        self.bsdd_dictionary.Classes.append(bsdd_class)
        bsdd_class._set_parent(self.bsdd_dictionary)
        self.endInsertRows()

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

    def remove_row(self, bsdd_class: BsddClass) -> bool:
        old_index = self._index_for_class(bsdd_class)
        parent_index, siblings = self._parent_and_siblings(bsdd_class)
        row = old_index.row()

        self.beginRemoveRows(parent_index, row, row)
        cl_utils.remove_class(bsdd_class)  # entfernt das Objekt aus bsdd_dictionary.Classes
        self.endRemoveRows()
        return True

    def move_row(self, bsdd_class: BsddClass, new_parent: BsddClass | None):
        old_parent_index = self._get_current_parent_index(bsdd_class)
        new_parent_index = (
            QModelIndex() if new_parent is None else self._index_for_class(new_parent)
        )
        row = cl_utils.get_row_index(bsdd_class)
        new_row_count = self.rowCount(new_parent_index)
        self.beginMoveRows(old_parent_index, row, row, new_parent_index, new_row_count)
        bsdd_class.ParentClassCode = None if new_parent is None else new_parent.Code
        self.endMoveRows()

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
            row = roots.index(cls)
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
        sel = []
        seen_codes: set[str] = set()

        for idx in indexes:
            if not idx.isValid() or idx.column() != 0:
                continue
            node: BsddClass = idx.internalPointer()
            code = node.Code
            if code in seen_codes:
                continue
            seen_codes.add(code)
            sel.append(node)

        md = QMimeData()
        md.setData(
            JSON_MIME,
            QByteArray(self._classes_to_json_bytes(sel, include_subtree=True)),
        )
        md.setData(CODES_MIME, QByteArray(json.dumps([c.Code for c in sel]).encode("utf-8")))
        md.setText(json.dumps([c.Code for c in sel], ensure_ascii=False))
        return md

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
        # destination parent
        dest_parent = parent.siblingAtColumn(0) if parent.isValid() else QModelIndex()
        dest_parent_node = dest_parent.internalPointer() if dest_parent.isValid() else None

        if action == Qt.MoveAction and data.hasFormat(CODES_MIME):
            # internal MOVE within this dictionary
            codes = json.loads(bytes(data.data(CODES_MIME)).decode("utf-8"))
            if not codes:
                return False
            # one-at-a-time move (extend to multi later if needed)
            code = codes[0]
            node = cl_utils.get_class_by_code(self.bsdd_dictionary, code)
            if node is None:
                return False
            # destination row (append)
            dest_parent_index = (
                QModelIndex()
                if dest_parent_node is None
                else self._index_for_class(dest_parent_node)
            )
            dest_row = self.rowCount(dest_parent_index) if row == -1 else row
            return self._move_row_to(node, dest_parent_node, dest_row)

        # COPY: external (or internal copy via Ctrl)
        if action in (
            Qt.CopyAction,
            Qt.IgnoreAction,
        ):  # some platforms give Ignore before acceptProposedAction
            payload = None
            for fmt in (JSON_MIME, "application/json", "text/plain"):
                if data.hasFormat(fmt):
                    try:
                        b = bytes(data.data(fmt))
                        if fmt == "text/plain":
                            b = b.strip()
                        payload = json.loads(b.decode("utf-8"))
                        break
                    except Exception:
                        pass
            if payload is None:
                return False
            return self._import_classes_payload(payload, dest_parent_node, row)
        return False

    def _is_descendant(self, maybe_ancestor: BsddClass, node: BsddClass) -> bool:
        cur = node
        while cur and cur.ParentClassCode:
            if cur.ParentClassCode == maybe_ancestor.Code:
                return True
            cur = cl_utils.get_class_by_code(self.bsdd_dictionary, cur.ParentClassCode)
        return False

    def _import_classes_payload(
        self, payload: dict, dest_parent: BsddClass | None, row_hint: int
    ) -> bool:
        """
        Import a flat list of classes (with ParentClassCode links) into *this* dictionary.
        - Fix code conflicts by renaming.
        - Rewire ParentClassCode for imported roots to dest_parent.
        - Insert in topological order; signal inserts incrementally.
        """
        if payload.get("kind") != "BsddClassTransfer" or "classes" not in payload:
            return False

        raw_classes = payload["classes"]
        raw_properties = payload["properties"]
        root_codes = set(payload.get("roots", []))

        # 1) build code -> raw map; compute depth to sort parents before children
        class_code_dict = {
            rc["Code"]: rc for rc in raw_classes if isinstance(rc, dict) and "Code" in rc
        }
        property_code_dict = {
            rp["Code"]: rp for rp in raw_properties if isinstance(rp, dict) and "Code" in rp
        }

        def depth_of(code: str) -> int:
            d = 0
            seen = set()
            c = class_code_dict.get(code)
            while (
                c
                and c.get("ParentClassCode") in class_code_dict
                and c.get("ParentClassCode") not in seen
            ):
                seen.add(c["Code"])
                c = class_code_dict.get(c.get("ParentClassCode"))
                d += 1
            return d

        ordered_class_codes = sorted(class_code_dict.keys(), key=depth_of)  # parents first

        # 2) conflict-safe code mapping
        existing_classes = set(cl_utils.get_all_class_codes(self.bsdd_dictionary))
        existing_properties = set(prop_utils.get_property_code_dict(self.bsdd_dictionary))

        old2new = {}

        def unique_code(wish: str, existing_classes) -> str:
            if wish not in existing_classes and wish not in old2new.values():
                existing_classes.add(wish)
                return wish
            base = wish
            i = 2
            while True:
                cand = f"{base} ({i})"
                if cand not in existing_classes and cand not in old2new.values():
                    existing_classes.add(cand)
                    return cand
                i += 1

        # 3) create & insert classes (parents first), adjusting codes/parents
        for class_code in ordered_class_codes:
            rc = dict(class_code_dict[class_code])  # copy
            # new code (unique in target)
            new_code = unique_code(rc["Code"])
            old2new[rc["Code"]] = new_code
            rc["Code"] = new_code

            # fix ParentClassCode:
            p = rc.get("ParentClassCode")
            if p in old2new:
                rc["ParentClassCode"] = old2new[p]
            else:
                # imported root -> attach to dest_parent in this dictionary (or stay root)
                if rc["Code"] in (old2new[c] for c in root_codes):
                    rc["ParentClassCode"] = dest_parent.Code if dest_parent is not None else None
                else:
                    # parent outside import and not destination: make it root
                    rc["ParentClassCode"] = None

            # build model instance
            try:
                node = BsddClass.model_validate(rc)
            except Exception:
                # if invalid, skip this one (or log)
                continue

            # insert with proper signals (parent must exist now)
            self.append_row(node)  # your append_row sets _parent_ref and signals insert

        # 4) Insert Properties
        #
        # that don't exist so far
        for property_code, property_json in property_code_dict.items():

            if property_code in existing_properties:
                continue
            try:
                node = BsddProperty.model_validate(property_json)
                self.bsdd_dictionary.Properties.append(node)
            except Exception:
                # if invalid, skip this one (or log)
                continue
        return True

    def _move_row_to(
        self, bsdd_class: BsddClass, new_parent: BsddClass | None, dest_row: int
    ) -> bool:
        """Move one row (with subtree) to new_parent at dest_row using beginMoveRows/endMoveRows."""
        old_parent_index = self._get_current_parent_index(bsdd_class)
        new_parent_index = (
            QModelIndex() if new_parent is None else self._index_for_class(new_parent)
        )

        # current position of the node among its siblings
        siblings_src = (
            cl_utils.get_root_classes(self.bsdd_dictionary)
            if not bsdd_class.ParentClassCode
            else cl_utils.get_children(
                cl_utils.get_class_by_code(self.bsdd_dictionary, bsdd_class.ParentClassCode)
            )
        )
        try:
            src_row = siblings_src.index(bsdd_class)
        except ValueError:
            return False

        # Clamp destination
        dest_row = max(0, min(dest_row, self.rowCount(new_parent_index)))

        if not self.beginMoveRows(old_parent_index, src_row, src_row, new_parent_index, dest_row):
            return False

        # Mutate data model: reparent
        bsdd_class.ParentClassCode = None if new_parent is None else new_parent.Code

        self.endMoveRows()
        return True

    def _collect_subtree(self, root: BsddClass) -> list[BsddClass]:
        out, stack = [], [root]
        seen_codes: set[str] = set()
        while stack:
            n = stack.pop()
            if n.Code in seen_codes:
                continue
            seen_codes.add(n.Code)
            out.append(n)
            stack.extend(cl_utils.get_children(n))
        return out

    def _classes_to_json_bytes(self, classes: list[BsddClass], *, include_subtree: bool) -> bytes:
        # flat list of class dicts (optionally entire subtrees of each selection)
        export_list = []
        roots = []
        seen_class_code = set()
        seen_property_code = set()

        dictionary_properties = list()

        def add_property(p: BsddProperty):
            if p.Code in seen_property_code:
                return
            dictionary_properties.append(p.model_dump(mode="json"))

        def add_class(c: BsddClass):
            if c.Code in seen_class_code:
                return
            seen_class_code.add(c.Code)
            export_list.append(c.model_dump(mode="json"))
            for cp in c.ClassProperties:
                if not cp.PropertyCode:
                    continue
                add_property(prop_utils.get_internal_property(cp))

        for c in classes:
            roots.append(c.Code)
            if include_subtree:
                for n in self._collect_subtree(c):
                    add_class(n)
            else:
                add_class(c)

        payload = {
            "kind": "BsddClassTransfer",
            "version": 1,
            "roots": roots,  # which items were dragged
            "classes": export_list,  # flat list, parents by ParentClassCode
            "properties": dictionary_properties,
        }
        return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class SortModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSortLocaleAware(True)

    def sourceModel(self) -> ClassTreeModel:
        return super().sourceModel()
