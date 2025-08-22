from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from PySide6.QtCore import QModelIndex,QObject,Signal,Qt
from bsdd_gui.module.property_set_table import ui,models
from bsdd_parser.models import BsddDictionary, BsddClass
if TYPE_CHECKING:
    from bsdd_gui.module.property_set_table.prop import PropertySetTableProperties

class Signaller(QObject):
    model_refresh_requested = Signal()
    selection_changed = Signal(ui.PsetTableView,str)


class PropertySetTable:
    signaller = Signaller()
    @classmethod
    def get_properties(cls) -> PropertySetTableProperties:
        return bsdd_gui.PropertySetTableProperties

    @classmethod
    def register_view(cls, view: ui.PsetTableView):
        cls.get_properties().views.add(view)

    @classmethod
    def unregister_view(cls, view: ui.PsetTableView):
        cls.get_properties().views.pop(view)

    @classmethod
    def get_views(cls) -> set[ui.PsetTableView]:
        return cls.get_properties().views

    @classmethod
    def create_model(cls,bsdd_dictionary:BsddDictionary):
        model = models.PsetListModel(bsdd_dictionary)
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model

    @classmethod
    def on_current_changed(cls,view:ui.PsetTableView,curr:QModelIndex, prev):
        proxy_model = view.model()
        if not curr.isValid():
            return
        index = proxy_model.mapToSource(curr)
        cls.signaller.selection_changed.emit(view,index.data(Qt.ItemDataRole.DisplayRole))

    @classmethod
    def reset_view(cls, view: ui.PsetTableView):
        source_model = view.model().sourceModel()
        source_model.beginResetModel()
        source_model.endResetModel()
        model = view.model()
        rc = model.rowCount()
        if not rc:
            return
        index = model.index(0, 0)
        view.setCurrentIndex(index)

    @classmethod
    def get_pset_list(cls, bsdd_class: BsddClass) -> list[str]:
        return list({cp.PropertySet for cp in bsdd_class.ClassProperties})
