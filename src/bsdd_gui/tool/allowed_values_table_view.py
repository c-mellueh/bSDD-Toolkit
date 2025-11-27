from __future__ import annotations
from typing import TYPE_CHECKING
from types import ModuleType
import logging
from PySide6.QtCore import Qt, QModelIndex, QCoreApplication, Signal
from PySide6.QtWidgets import QWidget
import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.allowed_values_table_view.prop import AllowedValuesTableViewProperties
    from bsdd_gui.module.class_property_editor_widget.ui import ClassPropertyEditor

from bsdd_gui.presets.tool_presets import ItemViewTool, ViewSignals
from bsdd_json import BsddClassProperty, BsddProperty, BsddAllowedValue
from bsdd_gui.module.allowed_values_table_view import models, ui, trigger
from bsdd_gui import tool


class Signals(ViewSignals):
    items_pasted = Signal(QWidget)#View


class AllowedValuesTableView(ItemViewTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> AllowedValuesTableViewProperties:
        return bsdd_gui.AllowedValuesTableViewProperties

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.items_pasted.connect(trigger.items_pasted)
    @classmethod
    def _get_model_class(cls) -> models.AllowedValuesModel:
        return models.AllowedValuesModel

    @classmethod
    def _get_proxy_model_class(cls) -> models.SortModel:
        return models.SortModel

    @classmethod
    def _get_trigger(cls) -> ModuleType:
        return trigger

    @classmethod
    def delete_selection(cls, view: ui.AllowedValuesTable):
        bsdd_property = cls.get_property_from_view(view)
        for allowed_value in cls.get_selected(view):
            if allowed_value in bsdd_property.AllowedValues:
                bsdd_property.AllowedValues.remove(allowed_value)
        cls.reset_view(view)

    @classmethod
    def get_selected(cls, view: ui.AllowedValuesTable) -> list[BsddAllowedValue]:
        return super().get_selected(view)

    @classmethod
    def create_model(
        cls, bsdd_property: BsddClassProperty | BsddProperty
    ) -> tuple[models.SortModel, models.AllowedValuesModel]:
        return super().create_model(bsdd_property)

    @classmethod
    def get_model(cls, prop: BsddClassProperty | BsddProperty) -> models.AllowedValuesModel:
        return super().get_model(prop)

    @classmethod
    def remove_model(cls, model: models.AllowedValuesModel):
        super().remove_model(model)

    @classmethod
    def set_code(cls, model: models.AllowedValuesModel, index: QModelIndex, value: str):
        if not value:
            return
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        allowed_value.Code = value

    @classmethod
    def set_value(cls, model: models.AllowedValuesModel, index: QModelIndex, value: str):
        if not value:
            return
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        if allowed_value.Code == allowed_value.Value:
            allowed_value.Code = value
        allowed_value.Value = value

    @classmethod
    def set_description(cls, model: models.AllowedValuesModel, index: QModelIndex, value: str):
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        allowed_value.Description = value if value else None

    @classmethod
    def set_sort_number(cls, model: models.AllowedValuesModel, index: QModelIndex, value: str):
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        allowed_value.SortNumber = value if value else None

    @classmethod
    def set_owned_uri(cls, model: models.AllowedValuesModel, index: QModelIndex, value: str):
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        allowed_value.OwnedUri = value if value else None

    @classmethod
    def append_new_value(cls, view: ui.AllowedValuesTable):
        """
        appends new Value and returns Index of Value
        :type view: ui.AllowedValuesTable
        """
        bsdd_property = cls.get_property_from_view(view)
        new_name = QCoreApplication.translate("AllowedValuesTable", "New Value")
        new_name = tool.Util.get_unique_name(
            new_name, [v.Code for v in bsdd_property.AllowedValues]
        )
        av = BsddAllowedValue(Code=new_name, Value=new_name)
        bsdd_property.AllowedValues.append(av)
        cls.reset_view(view)
        return len(bsdd_property.AllowedValues)-1

    @classmethod
    def get_view_from_property_editor(cls, widget: ClassPropertyEditor):
        return widget.tv_allowed_values

    @classmethod
    def handle_new_value_request(cls, widget: ClassPropertyEditor):
        table_view = cls.get_view_from_property_editor(widget)
        cls.append_new_value(table_view)

    @classmethod
    def remove_view_by_property_editor(cls, widget: ClassPropertyEditor):
        table_view = cls.get_view_from_property_editor(widget)
        if table_view:
            cls.unregister_view(table_view)

    @classmethod
    def get_property_from_view(
        cls, view: ui.AllowedValuesTable
    ) -> BsddClassProperty | BsddProperty:
        return view.model().sourceModel().bsdd_data
