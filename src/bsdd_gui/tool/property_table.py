from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from PySide6.QtCore import QModelIndex,QObject,Signal,Qt

import bsdd_gui
from bsdd_parser.models import BsddClassProperty,BsddClass
from bsdd_gui.module.property_table import ui,models
if TYPE_CHECKING:
    from bsdd_gui.module.property_table.prop import PropertyTableProperties

class Signaller(QObject):
    model_refresh_requested = Signal()
    selection_changed = Signal(ui.PropertyTable,BsddClassProperty)

class PropertyTable:
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> PropertyTableProperties:
        return bsdd_gui.PropertyTableProperties

    @classmethod
    def register_view(cls, view: ui.PropertyTable):
        cls.get_properties().views.add(view)

    @classmethod
    def unregister_view(cls, view: ui.PropertyTable):
        cls.get_properties().views.pop(view)

    @classmethod
    def get_views(cls) -> set[ui.PropertyTable]:
        return cls.get_properties().views

    @classmethod
    def create_model(cls):
        model = models.PropertyTableModel()
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model

    @classmethod
    def on_current_changed(cls,view:ui.PropertyTable,curr:QModelIndex, prev):
        proxy_model = view.model()
        if not curr.isValid():
            return
        index = proxy_model.mapToSource(curr)
        cls.signaller.selection_changed.emit(view,index.internalPointer())

    @classmethod
    def reset_view(cls, view: ui.PropertyTable):
        source_model = view.model().sourceModel()
        source_model.beginResetModel()
        source_model.endResetModel()

    @classmethod
    def filter_properties_by_pset(cls, bsdd_class: BsddClass, pset_name: str):
        return [p for p in bsdd_class.ClassProperties if p.PropertySet == pset_name]
