from __future__ import annotations
from typing import TYPE_CHECKING, Type
import logging

from PySide6.QtCore import QModelIndex, QObject, Signal, Qt

import bsdd_gui
from bsdd_parser.models import BsddClassProperty, BsddClass
from bsdd_parser.utils import bsdd_class_property as cp_utils

from bsdd_gui.module.class_property_table_view import ui, models, trigger
from bsdd_gui.presets.tool_presets import ItemViewTool, ViewSignals

if TYPE_CHECKING:
    from bsdd_gui.module.class_property_table_view.prop import ClassPropertyTableViewProperties


class Signals(ViewSignals):
    property_info_requested = Signal(BsddClassProperty)


class ClassPropertyTableView(ItemViewTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> ClassPropertyTableViewProperties:
        return bsdd_gui.ClassPropertyTableProperties

    @classmethod
    def _get_model_class(cls) -> Type[models.ClassPropertyTableModel]:
        return models.ClassPropertyTableModel

    @classmethod
    def _get_proxy_model_class(cls) -> Type[models.SortModel]:
        return models.SortModel

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def delete_selection(view: ui.ClassPropertyTable):
        # TODO
        return None

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()

    @classmethod
    def connect_view_signals(cls, view: ui.ClassPropertyTable):
        super().connect_view_signals(view)

    @classmethod
    def filter_properties_by_pset(
        cls, bsdd_class: BsddClass, pset_name: str
    ) -> list[BsddClassProperty]:
        return [p for p in bsdd_class.ClassProperties if p.PropertySet == pset_name]

    @classmethod
    def get_allowed_values(cls, class_property: BsddClassProperty):
        return "; ".join([v.Value for v in class_property.AllowedValues])

    @classmethod
    def get_row_of_property(cls, view: ui.ClassPropertyTable, class_property: BsddClassProperty):
        model = view.model().sourceModel()

        for row in range(model.rowCount()):
            index = model.index(row, 0)
            if index.internalPointer() == class_property:
                return view.model().mapFromSource(index).row()
        return None

    @classmethod
    def select_row(cls, view: ui.ClassPropertyTable, row_index: int):
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
