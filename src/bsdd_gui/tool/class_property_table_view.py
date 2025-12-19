from __future__ import annotations
from typing import TYPE_CHECKING, Type
import logging

from PySide6.QtCore import QModelIndex, QObject, Signal, Qt

import bsdd_gui
from bsdd_json.models import BsddClassProperty, BsddClass

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
        return bsdd_gui.ClassPropertyTableViewProperties

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
    def get_models_by_class(cls, bsdd_class: BsddClass) -> list[models.ClassPropertyTableModel]:
        return [model for model in cls.get_models() if model.active_class == bsdd_class]

    @classmethod
    def add_class_property(cls, class_property: BsddClassProperty, bsdd_class: BsddClass):
        if class_property in bsdd_class.ClassProperties:
            return
        affected_models = cls.get_models_by_class(bsdd_class)
        for model in affected_models:
            row = model.rowCount()
            model.beginInsertRows(QModelIndex(), row, row)

        bsdd_class.ClassProperties.append(class_property)
        class_property._set_parent(bsdd_class)

        for model in affected_models:
            model.endInsertRows()

        cls.signals.item_added.emit(class_property)

    @classmethod
    def remove_property(cls, bsdd_class: BsddClass, class_property: BsddClassProperty):
        affected_models = cls.get_models_by_class(bsdd_class)
        for model in affected_models:
            row = model.get_row_for_data(class_property)
            model.beginRemoveRows(QModelIndex(), row, row)

        bsdd_class.ClassProperties.remove(class_property)

        for model in affected_models:
            model.endRemoveRows()

        cls.signals.item_removed.emit(class_property)

    @classmethod
    def delete_selection(cls, view: ui.ClassPropertyTable):
        class_properties = cls.get_selected(view)
        bsdd_class = view.model().sourceModel().active_class

        for prop in class_properties:
            cls.remove_property(bsdd_class, prop)

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()

    @classmethod
    def connect_view_signals(cls, view: ui.ClassPropertyTable):
        view.doubleClicked.connect(lambda _, v=view: cls.request_info(v))

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
    def request_info(cls, view: ui.ClassPropertyTable):
        index = view.selectedIndexes()[0]
        index = view.model().mapToSource(index)
        bsdd_class_property = index.internalPointer()
        if not bsdd_class_property:
            return
        cls.signals.property_info_requested.emit(bsdd_class_property)
