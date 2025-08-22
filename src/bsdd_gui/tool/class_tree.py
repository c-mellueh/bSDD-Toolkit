from __future__ import annotations
from typing import TYPE_CHECKING, Any
import ctypes
import logging

from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel
from PySide6.QtWidgets import QWidget

import bsdd_gui

from bsdd_parser.models import BsddDictionary, BsddClass
from bsdd_gui.module.class_tree import ui, models, trigger
from bsdd_gui.presets.tool_presets import ViewHandler, ViewSignaller

if TYPE_CHECKING:
    from bsdd_gui.module.class_tree.prop import ClassTreeProperties


class Signaller(ViewSignaller):
    pass


class ClassTree(ViewHandler):
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
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model

    @classmethod
    def get_root_classes(cls, bsdd_dictionary: BsddDictionary):
        if bsdd_dictionary is None:
            return []
        return [c for c in bsdd_dictionary.Classes if not c.ParentClassCode]

    @classmethod
    def get_children(cls, bsdd_class: BsddClass):
        code = bsdd_class.Code
        bsdd_dictionary = bsdd_class._parent_ref()
        return [c for c in bsdd_dictionary.Classes if c.ParentClassCode == code]

    @classmethod
    def get_class_by_code(cls, bsdd_dictionary: BsddDictionary, code: str):
        return {c.Code: c for c in bsdd_dictionary.Classes}.get(code)

    @classmethod
    def get_row_index(cls, bsdd_class: BsddClass):
        bsdd_dictionary = bsdd_class._parent_ref()
        if not bsdd_class.ParentClassCode:
            return bsdd_dictionary.Classes.index(bsdd_class)
        parent_class = cls.get_class_by_code(bsdd_dictionary, bsdd_class.ParentClassCode)
        return cls.get_children(parent_class).index(bsdd_class)

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
