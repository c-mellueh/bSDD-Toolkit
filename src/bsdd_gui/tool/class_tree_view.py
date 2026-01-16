from __future__ import annotations
from typing import TYPE_CHECKING, Type
import ctypes
import logging
from types import ModuleType
from PySide6.QtCore import (
    QObject,
    Signal,
    QSortFilterProxyModel,
    QModelIndex,
    QMimeData,
    QByteArray,
)
from PySide6.QtWidgets import QWidget, QAbstractItemView

import bsdd_gui
import json
from bsdd_json.models import BsddDictionary, BsddClass, BsddProperty, BsddClassProperty
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_gui.module.class_tree_view import ui, models, trigger, constants
from bsdd_gui.presets.tool_presets import ItemViewTool, ViewSignals
from bsdd_gui.module.util.constants import CLASS_CLIPBOARD_KIND

if TYPE_CHECKING:
    from bsdd_gui.module.class_tree_view.prop import ClassTreeViewProperties
    from bsdd_gui.module.class_tree_view.models import ClassTreeModel


class Signals(ViewSignals):
    group_selection_requested = Signal(ui.ClassView)
    search_requested = Signal(ui.ClassView)
    expand_selection_requested = Signal(ui.ClassView)
    collapse_selection_requested = Signal(ui.ClassView)
    class_parent_changed = Signal(BsddClass)
    copy_selection_requested = Signal(ui.ClassView)
    paste_requested = Signal(ui.ClassView)


class ClassTreeView(ItemViewTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> ClassTreeViewProperties:
        return bsdd_gui.ClassTreeViewProperties

    @classmethod
    def _get_model_class(cls) -> Type[models.ClassTreeModel]:
        return models.ClassTreeModel

    @classmethod
    def _get_proxy_model_class(cls) -> Type[models.SortModel]:
        return models.SortModel

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.group_selection_requested.connect(trigger.group_selection)
        cls.signals.search_requested.connect(trigger.search_class)
        cls.signals.expand_selection_requested.connect(cls.expand_selection)
        cls.signals.collapse_selection_requested.connect(cls.collapse_selection)
        cls.signals.copy_selection_requested.connect(trigger.copy_selected_classes_to_clipboard)
        cls.signals.paste_requested.connect(trigger.paste_classes_from_clipboard)

    @classmethod
    def get_selected(cls, view: ui.ClassView) -> list[BsddClass]:
        return super().get_selected(view)

    @classmethod
    def create_model(cls, bsdd_dictionary: BsddDictionary) -> models.ClassTreeModel:
        return super().create_model(bsdd_dictionary)

    @classmethod
    def request_search(cls, view: ui.ClassView):
        cls.signals.search_requested.emit(view)

    @classmethod
    def add_class_to_dictionary(cls, new_class: BsddClass, bsdd_dictionary: BsddDictionary):
        model: models.ClassTreeModel = cls.get_model(bsdd_dictionary)
        if not model:
            logging.info(f"no Model found")
            return
        parent_index = model._get_current_parent_index(new_class)

        insert_row = model.rowCount(parent_index)  # current child count
        model.beginInsertRows(parent_index, insert_row, insert_row)
        # mutate your data
        model.bsdd_dictionary.Classes.append(new_class)
        new_class._set_parent(model.bsdd_dictionary)
        model.endInsertRows()
        cls.signals.item_added.emit(new_class)

    @classmethod
    def delete_selection(cls, view: ui.ClassView):
        trigger.delete_selection(view)  # can't be handled here because popup is required

    @classmethod
    def delete_class(cls, bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary):

        parent = cl_utils.get_parent(bsdd_class)
        for child in cl_utils.get_children(bsdd_class):
            cls.move_class(child, parent, bsdd_dictionary)

        model: ClassTreeModel = cls.get_model(bsdd_dictionary)
        row = model._index_for_class(bsdd_class).row()
        parent_index, siblings = model._parent_and_siblings(bsdd_class)
        model.beginRemoveRows(parent_index, row, row)
        cl_utils.remove_class(bsdd_class)
        model.endRemoveRows()

        cls.signals.item_removed.emit(bsdd_class)

    @classmethod
    def move_class(
        cls,
        bsdd_class: BsddClass,
        new_parent: BsddClass | None,
        bsdd_dictionary: BsddDictionary,
        dest_row=1_000,
    ):
        model: models.ClassTreeModel = cls.get_model(bsdd_dictionary)
        """Move one row (with subtree) to new_parent at dest_row using beginMoveRows/endMoveRows."""
        old_parent_index = model._get_current_parent_index(bsdd_class)
        new_parent_index = (
            QModelIndex() if new_parent is None else model._index_for_class(new_parent)
        )

        # current position of the node among its siblings
        siblings_src = (
            cl_utils.get_root_classes(model.bsdd_dictionary)
            if not bsdd_class.ParentClassCode
            else cl_utils.get_children(
                cl_utils.get_class_by_code(model.bsdd_dictionary, bsdd_class.ParentClassCode)
            )
        )
        try:
            src_row = siblings_src.index(bsdd_class)
        except ValueError:
            return False

        # Clamp destination
        dest_row = max(0, min(dest_row, model.rowCount(new_parent_index)))

        if not model.beginMoveRows(old_parent_index, src_row, src_row, new_parent_index, dest_row):
            return False
        bsdd_class.ParentClassCode = new_parent.Code if new_parent else None
        model.endMoveRows()
        cls.signals.class_parent_changed.emit(bsdd_class)

    @classmethod
    def delete_class_with_children(cls, bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary):
        model: ClassTreeModel = cls.get_model(bsdd_dictionary)
        to_delete = []
        stack = [bsdd_class]
        while stack:
            n = stack.pop()
            to_delete.append(n)
            stack.extend(cl_utils.get_children(n))

        for node in reversed(to_delete):
            cls.delete_class(node, bsdd_dictionary)

    @classmethod
    def get_payload_from_data(cls, data) -> constants.PAYLOAD | None:
        payload = None
        for fmt in (constants.JSON_MIME, "application/json", "text/plain"):
            if data.hasFormat(fmt):
                try:
                    b = bytes(data.data(fmt))
                    if fmt == "text/plain":
                        b = b.strip()
                    payload = json.loads(b.decode("utf-8"))
                    return payload
                except Exception:
                    pass
        return payload

    @classmethod
    def get_codes_from_data(cls, data):
        payload = None
        for fmt in constants.CODES_MIME:
            if data.hasFormat(fmt):
                try:
                    b = bytes(data.data(fmt))
                    payload = json.loads(b.decode("utf-8"))
                    return payload
                except Exception:
                    pass
        return payload

    @classmethod
    def is_payload_valid(cls, payload: constants.PAYLOAD):
        if payload is None:
            return False
        if payload.get("kind") != CLASS_CLIPBOARD_KIND or "classes" not in payload:
            return False
        return True

    @classmethod
    def depth_of(cls, code: str, class_code_dict: dict[str, BsddClass]) -> int:
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

    @classmethod
    def create_class_from_mime(cls, rc, new_code, old2new, root_codes, dest_parent):

        rc["Code"] = new_code

        # fix ParentClassCode:
        p = rc.get("ParentClassCode")
        if p in old2new:
            rc["ParentClassCode"] = old2new[p]
        else:
            # imported root -> attach to dest_parent in this dictionary (or stay root)
            if rc["Code"] in (old2new.get(c) for c in root_codes):
                rc["ParentClassCode"] = dest_parent.Code if dest_parent is not None else None
            else:
                # parent outside import and not destination: make it root
                rc["ParentClassCode"] = None

        # build model instance
        try:
            node = BsddClass.model_validate(obj=rc)
        except Exception:
            # if invalid, skip this one (or log)
            node = None
        return node

    @classmethod
    def expand_selection(cls, tree: ui.ClassView):
        for index in tree.selectedIndexes():
            tree.expandRecursively(index)

    @classmethod
    def collapse_selection(cls, tree: ui.ClassView):
        for index in tree.selectedIndexes():
            tree.collapse(index)

    @classmethod
    def classes_to_payload(
        cls, classes: list[BsddClass], unexpanded_classes: set[str] | None = None
    ) -> constants.PAYLOAD:
        # flat list of class dicts (optionally entire subtrees of each selection)
        def _collect_unexpanded(root: BsddClass) -> list[BsddClass]:
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

        def add_property(p: BsddProperty):
            if p.Code in seen_property_code:
                return
            dictionary_properties.append(p.model_dump(mode="json"))
            seen_property_code.add(p.Code)

        def add_class(c: BsddClass):
            if c.Code in seen_class_code:
                return
            seen_class_code.add(c.Code)
            export_list.append(c.model_dump(mode="json"))
            for cp in c.ClassProperties:
                if not cp.PropertyCode:
                    continue
                internal_prop = prop_utils.get_internal_property(cp)
                if internal_prop:
                    add_property(internal_prop)

        export_list = []
        roots = []
        seen_class_code = set()
        seen_property_code = set()
        include_subtree_codes = (
            unexpanded_classes
            if unexpanded_classes is not None
            else {c.Code for c in classes if c.Code}
        )
        dictionary_properties = list()

        for c in classes:
            roots.append(c.Code)
            targets = _collect_unexpanded(c) if c.Code in include_subtree_codes else [c]
            for n in targets:
                add_class(n)

        payload = {
            "kind": CLASS_CLIPBOARD_KIND,
            "version": 1,
            "roots": roots,  # which items were dragged
            "classes": export_list,  # flat list, parents by ParentClassCode
            "properties": dictionary_properties,
        }
        return payload

    @classmethod
    def generate_mime_data(cls, classes: list[BsddClass], unexpanded_classes: list[str] = []):
        md = QMimeData()
        payload = cls.classes_to_payload(classes, unexpanded_classes)
        byte_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        md.setData(
            constants.JSON_MIME,
            QByteArray(byte_payload),
        )
        class_codes_bytes = QByteArray(json.dumps([c.Code for c in classes]).encode("utf-8"))
        md.setData(constants.CODES_MIME, class_codes_bytes)
        md.setText(json.dumps([c.Code for c in classes], ensure_ascii=False))
        return md

    @classmethod
    def request_copy_selection(cls, view: ui.ClassView):
        cls.signals.copy_selection_requested.emit(view)

    @classmethod
    def request_paste(cls, view: ui.ClassView):
        cls.signals.paste_requested.emit(view)

    @classmethod
    def get_index_from_bsdd_class(cls, bsdd_dictionary: BsddDictionary, bsdd_class: BsddClass):
        model: models.ClassTreeModel = cls.get_model(bsdd_dictionary)
        return model._index_for_class(bsdd_class)
