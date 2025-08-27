from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Qt, QModelIndex
import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.allowed_values_table.prop import AllowedValuesTableProperties

from bsdd_gui.presets.tool_presets import ColumnHandler, ViewHandler, ViewSignaller
from bsdd_parser import BsddClassProperty, BsddProperty, BsddAllowedValue
from bsdd_gui.module.allowed_values_table import models


class Signaller(ViewSignaller):
    pass


class AllowedValuesTable(ColumnHandler, ViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> AllowedValuesTableProperties:
        return bsdd_gui.AllowedValuesTableProperties

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
        bsdd_property = model.bsdd_property
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        allowed_value.Code = value

    @classmethod
    def set_value(cls, model: models.AllowedValuesModel, index: QModelIndex, value: str):
        bsdd_property = model.bsdd_property
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        if allowed_value.Code == allowed_value.Value:
            allowed_value.Code = value
        allowed_value.Value = value

    @classmethod
    def set_description(cls, model: models.AllowedValuesModel, index: QModelIndex, value: str):
        bsdd_property = model.bsdd_property
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        allowed_value.Description = value

    @classmethod
    def set_sort_number(cls, model: models.AllowedValuesModel, index: QModelIndex, value: str):
        bsdd_property = model.bsdd_property
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        allowed_value.SortNumber = value

    @classmethod
    def set_owned_uri(cls, model: models.AllowedValuesModel, index: QModelIndex, value: str):
        bsdd_property = model.bsdd_property
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        allowed_value.OwnedUri = value
