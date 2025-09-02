from __future__ import annotations
from typing import TYPE_CHECKING
from types import ModuleType
import logging
from PySide6.QtCore import Qt, QModelIndex, QCoreApplication
import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.allowed_values_table.prop import AllowedValuesTableProperties
    from bsdd_gui.module.class_property_editor.ui import ClassPropertyEditor

from bsdd_gui.presets.tool_presets import ItemViewHandler, ViewSignals
from bsdd_parser import BsddClassProperty, BsddProperty, BsddAllowedValue
from bsdd_gui.module.allowed_values_table import models, ui, trigger
from bsdd_gui import tool


class Signaller(ViewSignals):
    pass


class AllowedValuesTable(ItemViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> AllowedValuesTableProperties:
        return bsdd_gui.AllowedValuesTableProperties

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()

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
        bsdd_property = view.bsdd_data
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
    def append_new_value(cls, widget: ui.AllowedValuesTable):
        model = widget.model().sourceModel()
        bsdd_property = model.bsdd_data
        new_name = QCoreApplication.translate("AllowedValuesTable", "New Value")
        new_name = tool.Util.get_unique_name(
            new_name, [v.Code for v in bsdd_property.AllowedValues]
        )
        av = BsddAllowedValue(Code=new_name, Value=new_name)
        bsdd_property.AllowedValues.append(av)
        cls.reset_view(widget)

    @classmethod
    def get_view_from_property_editor(cls, widget: ClassPropertyEditor):
        views = list()
        for table_view in cls.get_views():
            if widget.data == table_view.data:
                views.append(table_view)
        if len(views) > 1:
            logging.warning("Multiple Views!")
        if not views:
            return None
        return views[-1]

    @classmethod
    def handle_new_value_request(cls, widget: ClassPropertyEditor):
        table_view = cls.get_view_from_property_editor(widget)
        cls.append_new_value(table_view)

    @classmethod
    def create_view(cls, bsdd_property: BsddClassProperty | BsddProperty):
        view = ui.AllowedValuesTable(bsdd_property)
        cls._get_trigger.table_view_created(view)
        return view

    @classmethod
    def remove_view_by_property_editor(cls, widget: ClassPropertyEditor):
        table_view = cls.get_view_from_property_editor(widget)
        if table_view:
            cls.unregister_view(table_view)
