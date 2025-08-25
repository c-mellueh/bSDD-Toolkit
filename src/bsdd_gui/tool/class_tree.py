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
    pass


class ClassTree(ColumnHandler, ViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> ClassTreeProperties:
        return bsdd_gui.ClassTreeProperties

    @classmethod
    def connect_signals(cls):
        cls.signaller.model_refresh_requested.connect(trigger.reset_class_views)

    @classmethod
    def create_model(cls, bsdd_dictionary: BsddDictionary):
        model = models.ClassTreeModel(bsdd_dictionary)
        cls.get_properties().models.add(model)
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
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
        model: models.ClassTreeModel
        parent_class = class_utils.get_class_by_code(bsdd_dictionary, new_class.ParentClassCode)
        # if parent_class is None:
        # child_count = 0 if parent_class is None else len(class_utils.get_children(parent_class))
        for model in cls.get_properties().models:
            parent_index = QModelIndex()
            if parent_class:
                row = class_utils.get_row_index(parent_class)
                parent_index = model.createIndex(row, 0, parent_class)
            child_count = model.rowCount(parent_index)
            model.beginInsertRows(parent_index, child_count, child_count)
        bsdd_dictionary.Classes.append(new_class)
        for model in cls.get_properties().models:
            model.endInsertRows()
