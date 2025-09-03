from __future__ import annotations
from typing import TYPE_CHECKING, Type
import ctypes
import logging
from types import ModuleType
from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, QModelIndex, QItemSelectionModel
from PySide6.QtWidgets import QWidget, QAbstractItemView

import bsdd_gui

from bsdd_parser.models import BsddDictionary, BsddClass
from bsdd_parser.utils import bsdd_class as class_utils
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


class ClassTree(ItemViewTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> ClassTreeViewProperties:
        return bsdd_gui.ClassTreeProperties

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
        model = cls.get_model(bsdd_dictionary)
        if not model:
            logging.info(f"no Model found")
            return
        model.append_row(new_class)

    @classmethod
    def delete_selection(cls, view: ui.ClassView):
        trigger.delete_selection(view)  # can't be handled here because popup is required

    @classmethod
    def delete_class(cls, bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary):
        model: ClassTreeModel = cls.get_model(bsdd_dictionary)
        parent = class_utils.get_parent(bsdd_class)
        for child in class_utils.get_children(bsdd_class):
            model.move_row(child, parent)
        model.remove_row(bsdd_class)
        cls.signals.item_deleted.emit(bsdd_class)

    @classmethod
    def move_class(
        cls, bsdd_class: BsddClass, new_parent: BsddClass | None, bsdd_dictionary: BsddDictionary
    ):
        model: ClassTreeModel = cls.get_model(bsdd_dictionary)
        model.move_row(bsdd_class, new_parent)

    @classmethod
    def delete_class_with_children(cls, bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary):
        model: ClassTreeModel = cls.get_model(bsdd_dictionary)
        to_delete = []
        stack = [bsdd_class]
        while stack:
            n = stack.pop()
            to_delete.append(n)
            stack.extend(class_utils.get_children(n))

        for node in reversed(to_delete):
            model.remove_row(node)
            cls.signals.item_deleted.emit(node)
