from __future__ import annotations
from typing import TYPE_CHECKING, Any
import ctypes
import logging

from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, QModelIndex
from PySide6.QtWidgets import QWidget

import bsdd_gui

from bsdd_parser.models import BsddDictionary, BsddClass
from bsdd_parser.utils import bsdd_class as class_utils
from bsdd_gui.module.class_tree import ui, models, trigger
from bsdd_gui.presets.tool_presets import ColumnHandler, ViewHandler, ViewSignaller

if TYPE_CHECKING:
    from bsdd_gui.module.class_tree.prop import ClassTreeProperties
    from bsdd_gui.module.class_tree.models import ClassTreeModel


class Signaller(ViewSignaller):
    copy_selection_requested = Signal(ui.ClassView)
    delete_selection_requested = Signal(ui.ClassView)
    group_selection_requested = Signal(ui.ClassView)
    search_requested = Signal(ui.ClassView)
    expand_selection_requested = Signal(ui.ClassView)
    collapse_selection_requested = Signal(ui.ClassView)


class ClassTree(ColumnHandler, ViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> ClassTreeProperties:
        return bsdd_gui.ClassTreeProperties

    @classmethod
    def connect_signals(cls):
        cls.signaller.model_refresh_requested.connect(trigger.reset_class_views)
        cls.signaller.copy_selection_requested.connect(trigger.copy_selected_class)
        cls.signaller.delete_selection_requested.connect(trigger.delete_selection)

    @classmethod
    def connect_view_signals(cls, view: ui.ClassView):
        view.customContextMenuRequested.connect(lambda p: trigger.create_context_menu(view, p))

    @classmethod
    def create_model(cls, bsdd_dictionary: BsddDictionary):
        model = models.ClassTreeModel(bsdd_dictionary)
        cls.get_properties().model = model
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        sort_filter_model.setDynamicSortFilter(True)
        return sort_filter_model

    @classmethod
    def destroy_model(cls, model: models.ClassTreeModel):
        cls.get_properties().models.remove(model)

    @classmethod
    def on_selection_changed(cls, view: ui.ClassView, selected, deselected):
        proxy_model = view.model()
        proxy_indexes = selected.indexes()
        if not proxy_indexes:
            logging.debug("Selection cleared")
            return
        picked = [ix for ix in proxy_indexes if ix.column() == 0]
        for p_ix in picked:
            s_ix = proxy_model.mapToSource(p_ix)
            cls.signaller.selection_changed.emit(view, s_ix.internalPointer())

    @classmethod
    def on_current_changed(cls, view: ui.ClassView, curr, prev):
        proxy_model = view.model()
        if not curr.isValid():
            return
        index = proxy_model.mapToSource(curr)
        cls.signaller.selection_changed.emit(view, index.internalPointer())

    @classmethod
    def add_class_to_dictionary(cls, new_class: BsddClass):
        cls.get_properties().model.append_row(new_class)

    @classmethod
    def get_selected_classes(cls, view: ui.ClassView) -> list[BsddClass]:
        """Return BsddClass objects for the rows selected in column 0."""
        sel_model = view.selectionModel()
        if sel_model is None:
            return []

        # Only rows in column 0 (avoids duplicates across columns)
        indexes: list[QModelIndex] = sel_model.selectedRows(0)
        if not indexes:
            return []

        def to_source_index(idx: QModelIndex) -> QModelIndex:
            """Map an index through any proxy chain to the ultimate source model."""
            model = view.model()
            src_idx = idx
            # Walk down proxy chain if present
            while isinstance(model, QSortFilterProxyModel):
                src_idx = model.mapToSource(src_idx)
                model = model.sourceModel()
            return src_idx

        result: list[BsddClass] = []
        for proxy_idx in indexes:
            src_idx = to_source_index(proxy_idx)
            if not src_idx.isValid():
                continue
            obj = src_idx.internalPointer()
            if isinstance(obj, BsddClass):
                result.append(obj)

        return result

    @classmethod
    def delete_class(cls, bsdd_class: BsddClass):
        model: ClassTreeModel = cls.get_properties().model
        parent = class_utils.get_parent(bsdd_class)
        for child in class_utils.get_children(bsdd_class):
            model.move_row(child, parent)
        model.remove_row(bsdd_class)

    @classmethod
    def delete_class_with_children(cls, bsdd_class: BsddClass):
        model: ClassTreeModel = cls.get_properties().model
        to_delete = []
        stack = [bsdd_class]
        while stack:
            n = stack.pop()
            to_delete.append(n)
            stack.extend(class_utils.get_children(n))

        for node in reversed(to_delete):
            model.remove_row(node)
