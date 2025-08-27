from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from PySide6.QtCore import QModelIndex, QObject, Signal, Qt

import bsdd_gui
from bsdd_parser.models import BsddClassProperty, BsddClass
from bsdd_parser.utils import bsdd_class_property as cp_utils

from bsdd_gui.module.property_table import ui, models
from bsdd_gui.presets.tool_presets import ColumnHandler, ViewHandler, ViewSignaller

if TYPE_CHECKING:
    from bsdd_gui.module.property_table.prop import PropertyTableProperties


class Signaller(ViewSignaller):
    property_info_requested = Signal(BsddClassProperty)
    reset_all_property_tables_requested = Signal()


class PropertyTable(ColumnHandler, ViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> PropertyTableProperties:
        return bsdd_gui.PropertyTableProperties

    @classmethod
    def create_model(cls):
        model = models.PropertyTableModel()
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model

    @classmethod
    def on_current_changed(cls, view: ui.PropertyTable, curr: QModelIndex, prev):
        proxy_model = view.model()
        if not curr.isValid():
            return
        index = proxy_model.mapToSource(curr)
        cls.signaller.selection_changed.emit(view, index.internalPointer())

    @classmethod
    def filter_properties_by_pset(
        cls, bsdd_class: BsddClass, pset_name: str
    ) -> list[BsddClassProperty]:
        return [p for p in bsdd_class.ClassProperties if p.PropertySet == pset_name]

    @classmethod
    def get_allowed_values(cls, class_property: BsddClassProperty):
        return "; ".join([v.Value for v in class_property.AllowedValues])

    @classmethod
    def get_row_of_property(cls, view: ui.PropertyTable, class_property: BsddClassProperty):
        model = view.model().sourceModel()

        for row in range(model.rowCount()):
            index = model.index(row, 0)
            if index.internalPointer() == class_property:
                return view.model().mapFromSource(index).row()
        return None

    @classmethod
    def select_row(cls, view: ui.PropertyTable, row_index: int):
        model = view.model()
        if row_index is None:
            return
        index = model.index(row_index, 0)
        if not index.isValid():
            return
        view.setCurrentIndex(index)

    @classmethod
    def remove_property(cls, bsdd_class: BsddClass, class_property: BsddClassProperty):
        if class_property in bsdd_class.ClassProperties:
            bsdd_class.ClassProperties.remove(class_property)
        else:
            logging.info(f"class_property '{class_property.Code}' not in class '{bsdd_class.Code}'")
