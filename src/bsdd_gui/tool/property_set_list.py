from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from PySide6.QtCore import QModelIndex,QObject,Signal,Qt
from bsdd_gui.module.property_set_list import ui,models
from bsdd_parser.models import BsddDictionary, BsddClass
if TYPE_CHECKING:
    from bsdd_gui.module.property_set_list.prop import PropertySetListProperties

class Signaller(QObject):
    model_refresh_requested = Signal()
    active_pset_changed = Signal(str)


class PropertySetList:
    signaller = Signaller()
    @classmethod
    def get_properties(cls) -> PropertySetListProperties:
        return bsdd_gui.PropertySetListProperties

    @classmethod
    def register_view(cls, view: ui.PsetListView):
        cls.get_properties().views.add(view)

    @classmethod
    def unregister_view(cls, view: ui.PsetListView):
        cls.get_properties().views.pop(view)

    @classmethod
    def get_views(cls) -> set[ui.PsetListView]:
        return cls.get_properties().views

    @classmethod
    def create_model(cls,bsdd_dictionary:BsddDictionary):
        model = models.PsetListModel(bsdd_dictionary)
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model

    @classmethod
    def on_current_changed(cls,view:ui.PsetListView,curr:QModelIndex, prev):
        proxy_model = view.model()
        if not curr.isValid():
            return
        index = proxy_model.mapToSource(curr)
        cls.signaller.active_pset_changed.emit(index.data(Qt.ItemDataRole.DisplayRole))

    @classmethod
    def reset_view(cls, view: ui.PsetListView):
        source_model = view.model().sourceModel()
        source_model.beginResetModel()
        source_model.endResetModel()

    @classmethod
    def get_pset_list(cls, bsdd_class: BsddClass) -> list[str]:
        return list({cp.PropertySet for cp in bsdd_class.ClassProperties})
