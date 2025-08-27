from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Qt, QModelIndex, QCoreApplication
import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.allowed_values_table.prop import AllowedValuesTableProperties
    from bsdd_gui.module.class_property_editor.ui import ClassPropertyEditor

from bsdd_gui.presets.tool_presets import ColumnHandler, ViewHandler, ViewSignaller
from bsdd_parser import BsddClassProperty, BsddProperty, BsddAllowedValue
from bsdd_gui.module.allowed_values_table import models, ui, trigger
from bsdd_gui import tool


class Signaller(ViewSignaller):
    pass


class AllowedValuesTable(ColumnHandler, ViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> AllowedValuesTableProperties:
        return bsdd_gui.AllowedValuesTableProperties

    @classmethod
    def get_selected(cls, view: ui.AllowedValuesTable) -> list[BsddAllowedValue]:
        selected_values = list()
        for proxy_index in view.selectedIndexes():
            source_index = view.model().mapToSource(proxy_index)
            value = source_index.internalPointer()
            if value not in selected_values:
                selected_values.append(value)
        return selected_values

    @classmethod
    def connect_view_signals(cls, view: ui.AllowedValuesTable):
        view.customContextMenuRequested.connect(lambda p: trigger.create_context_menu(view, p))

    @classmethod
    def create_model(cls, bsdd_property: BsddClassProperty | BsddProperty):
        model = models.AllowedValuesModel(bsdd_property)
        cls.get_properties().model.append(model)
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model

    @classmethod
    def get_model(cls, prop: BsddClassProperty | BsddProperty) -> models.AllowedValuesModel:
        for model in cls.get_properties().model:
            if model.bsdd_property == prop:
                return model
        return None

    @classmethod
    def remove_model(cls, model: models.AllowedValuesModel):
        if model in cls.get_properties().model:
            cls.get_properties().model.remove(model)

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
        bsdd_property = model.bsdd_property
        new_name = QCoreApplication.translate("AllowedValuesTable", "New Value")
        new_name = tool.Util.get_unique_name(
            new_name, [v.Code for v in bsdd_property.AllowedValues]
        )
        av = BsddAllowedValue(Code=new_name, Value=new_name)
        bsdd_property.AllowedValues.append(av)
        cls.reset_view(widget)

    @classmethod
    def handle_new_value_request(cls, widget: ClassPropertyEditor):
        for table_widget in cls.get_widgets():
            if widget.bsdd_class_property == table_widget.bsdd_property:
                cls.append_new_value(table_widget)
                return

    @classmethod
    def delete_selection(cls, widget: ui.AllowedValuesTable):
        bsdd_property = widget.bsdd_property
        for allowed_value in cls.get_selected(widget):
            if allowed_value in bsdd_property.AllowedValues:
                bsdd_property.AllowedValues.remove(allowed_value)
        cls.reset_view(widget)
