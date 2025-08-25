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


class Signaller(ViewSignaller):
    delete_selection_requested = Signal(ui.ClassView)
    group_selection_requested = Signal(ui.ClassView)
    search_requested = Signal(ui.ClassView)
    copy_requested = Signal(ui.ClassView)


class ClassTree(ColumnHandler, ViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> ClassTreeProperties:
        return bsdd_gui.ClassTreeProperties

    @classmethod
    def connect_signals(cls):
        cls.signaller.model_refresh_requested.connect(trigger.reset_class_views)
        cls.signaller.copy_requested.connect(trigger.copy_selected_class)

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
    def add_class_to_dictionary(cls, new_class: BsddClass, bsdd_dictionary: BsddDictionary):
        cls.get_properties().model.append_row(new_class)

    @classmethod
    def get_selected_class(cls, view: ui.ClassView):
        model = view.model().sourceModel()
        if not view.selectedIndexes():
            return None
        selected_index = view.selectedIndexes()[-1]
        index = view.model().mapToSource(selected_index)
        return index.internalPointer()
