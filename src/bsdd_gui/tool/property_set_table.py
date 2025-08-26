from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from PySide6.QtCore import QModelIndex, QObject, Signal, Qt
from bsdd_gui.module.property_set_table import ui, models, trigger
from bsdd_gui.presets.tool_presets import ColumnHandler, ViewSignaller, ViewHandler
from bsdd_parser.models import BsddDictionary, BsddClass

if TYPE_CHECKING:
    from bsdd_gui.module.property_set_table.prop import PropertySetTableProperties


class Signaller(ViewSignaller):
    new_property_set_requested = Signal(BsddClass)


class PropertySetTable(ColumnHandler, ViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> PropertySetTableProperties:
        return bsdd_gui.PropertySetTableProperties

    @classmethod
    def connect_signals(cls):
        cls.signaller.new_property_set_requested.connect(trigger.create_new_property_set)
        cls.signaller.model_refresh_requested.connect(trigger.reset_views)

    @classmethod
    def create_model(cls, bsdd_dictionary: BsddDictionary):
        model = models.PsetTableModel(bsdd_dictionary)
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model

    @classmethod
    def on_current_changed(cls, view: ui.PsetTableView, curr: QModelIndex, prev):
        proxy_model = view.model()
        if not curr.isValid():
            return
        index = proxy_model.mapToSource(curr)
        cls.signaller.selection_changed.emit(view, index.data(Qt.ItemDataRole.DisplayRole))

    @classmethod
    def get_pset_list(cls, bsdd_class: BsddClass) -> list[str]:
        bsdd_properties = list()
        for cp in bsdd_class.ClassProperties:
            if cp.PropertySet not in bsdd_properties:
                bsdd_properties.append(cp.PropertySet)

        if bsdd_class.Code in cls.get_properties().temporary_pset:
            for property_set in cls.get_properties().temporary_pset[bsdd_class.Code]:
                bsdd_properties.append(property_set)
        return bsdd_properties

    @classmethod
    def select_row(cls, view: ui.PsetTableView, row_index: int):
        model = view.model()
        index = model.index(row_index, 0)
        if not index.isValid():
            return
        view.setCurrentIndex(index)

    @classmethod
    def get_row_by_name(cls, view: ui.PsetTableView, name: str):
        model = view.model()
        for row in range(model.rowCount()):
            pset_name = model.index(row, 0).data(Qt.ItemDataRole.DisplayRole)
            if name == pset_name:
                return row
        return None

    @classmethod
    def request_new_property_set(cls, bsdd_class: BsddClass):
        cls.signaller.new_property_set_requested.emit(bsdd_class)

    @classmethod
    def add_temporary_pset(cls, bsdd_class: BsddClass, name: str):
        class_code = bsdd_class.Code
        if not class_code in cls.get_properties().temporary_pset:
            cls.get_properties().temporary_pset[class_code] = list()
        cls.get_properties().temporary_pset[class_code].append(name)
