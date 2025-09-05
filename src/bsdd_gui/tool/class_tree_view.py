from __future__ import annotations
from typing import TYPE_CHECKING, Type
import ctypes
import logging
from types import ModuleType
from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, QModelIndex, QItemSelectionModel
from PySide6.QtWidgets import QWidget, QAbstractItemView

import bsdd_gui

from bsdd_json.models import BsddDictionary, BsddClass
from bsdd_json.utils import class_utils as cl_utils
from bsdd_gui.module.class_tree_view import ui, models, trigger
from bsdd_gui.presets.tool_presets import ItemViewTool, ViewSignals

if TYPE_CHECKING:
    from bsdd_gui.module.class_tree_view.prop import ClassTreeViewProperties
    from bsdd_gui.module.class_tree_view.models import ClassTreeModel


class Signals(ViewSignals):
    copy_selection_requested = Signal(ui.ClassView)
    group_selection_requested = Signal(ui.ClassView)
    search_requested = Signal(ui.ClassView)
    expand_selection_requested = Signal(ui.ClassView)
    collapse_selection_requested = Signal(ui.ClassView)
    class_parent_changed = Signal(BsddClass)


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
        cls.signals.copy_selection_requested.connect(trigger.copy_selected_class)
        cls.signals.group_selection_requested.connect(trigger.group_selection)
        cls.signals.search_requested.connect(trigger.search_class)

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
        model.append_class(new_class)
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
        cls, bsdd_class: BsddClass, new_parent: BsddClass | None, bsdd_dictionary: BsddDictionary
    ):
        model: ClassTreeModel = cls.get_model(bsdd_dictionary)
        old_parent_index = model._get_current_parent_index(bsdd_class)
        new_parent_index = (
            QModelIndex() if new_parent is None else model._index_for_class(new_parent)
        )
        row = cl_utils.get_row_index(bsdd_class)
        new_row_count = model.rowCount(new_parent_index)
        model.beginMoveRows(old_parent_index, row, row, new_parent_index, new_row_count)
        bsdd_class.ParentClassCode = None if new_parent is None else new_parent.Code
        model.endMoveRows()
        cls.signals.class_parent_changed(bsdd_class)

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
            cls.delete_class(bsdd_class, bsdd_dictionary)
