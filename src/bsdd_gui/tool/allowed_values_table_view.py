from __future__ import annotations
from typing import TYPE_CHECKING
from types import ModuleType
import logging
from PySide6.QtCore import Qt, QModelIndex, QCoreApplication, Signal, QAbstractItemModel
from PySide6.QtWidgets import QWidget, QAbstractItemDelegate, QLineEdit
import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.allowed_values_table_view.prop import AllowedValuesTableViewProperties
    from bsdd_gui.module.class_property_editor_widget.ui import ClassPropertyEditor

from bsdd_gui.presets.tool_presets import ItemViewTool, ViewSignals
from bsdd_json import BsddClassProperty, BsddProperty, BsddAllowedValue
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_gui.module.allowed_values_table_view import models, ui, trigger
from bsdd_gui import tool


class Signals(ViewSignals):
    items_pasted = Signal(QWidget)  # View
    value_changed = Signal(QModelIndex, str, str)  # Index, Old_Text, New_Text
    value_setted = Signal(QModelIndex, str)  # Index, New_Text
    edit_closed = Signal(object, object)  # Index


class AllowedValuesTableView(ItemViewTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> AllowedValuesTableViewProperties:
        return bsdd_gui.AllowedValuesTableViewProperties

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.items_pasted.connect(trigger.items_pasted)
        cls.signals.value_changed.connect(cls.update_code)
        cls.signals.value_setted.connect(cls.set_value)
        cls.signals.edit_closed.connect(cls.editor_closed)

    @classmethod
    def connect_view_signals(cls, view: ui.AllowedValuesTable):
        super().connect_view_signals(view)

        view.editor_closed.connect(cls.signals.edit_closed.emit)
        delegate: ui.LiveEditDelegate = view.itemDelegateForColumn(0)
        delegate.text_edited.connect(cls.signals.value_changed.emit)
        delegate.text_set.connect(cls.signals.value_setted.emit)

    @classmethod
    def editor_closed(cls, editor: QLineEdit, hints):
        if hints == QAbstractItemDelegate.EndEditHint.RevertModelCache:
            bsdd_data: BsddAllowedValue = editor._bsdd_value
            bsdd_data.Code = dict_utils.slugify(bsdd_data.Value)

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
    def update_code(cls, index: QModelIndex, old_text: str, new_text: str):

        if not new_text:
            return
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return

        model: models.AllowedValuesModel = index.model()
        if allowed_value.Code == dict_utils.slugify(old_text):
            sibling = model.index(index.row(), index.column() + 1)
            model.setData(sibling, dict_utils.slugify(new_text), Qt.ItemDataRole.EditRole)

    @classmethod
    def set_value(cls, index: QModelIndex, value: str):
        if not value:
            return
        allowed_value: BsddAllowedValue = index.internalPointer()
        if allowed_value is None:
            return
        if allowed_value.Code == dict_utils.slugify(allowed_value.Value):
            allowed_value.Code = dict_utils.slugify(value)
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
        new_name = dict_utils.slugify(QCoreApplication.translate("AllowedValuesTable", "New-Value"))
        new_name = tool.Util.get_unique_name(
            new_name, [v.Code for v in bsdd_property.AllowedValues]
        )
        av = BsddAllowedValue(Code=dict_utils.slugify(new_name), Value=new_name)
        bsdd_property.AllowedValues.append(av)
        cls.reset_view(view)
        return len(bsdd_property.AllowedValues) - 1

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
