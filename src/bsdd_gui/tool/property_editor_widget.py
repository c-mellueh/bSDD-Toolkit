from __future__ import annotations
from typing import TYPE_CHECKING, Type
import logging

import bsdd_gui
from bsdd_gui.presets.tool_presets import DialogTool, DialogSignals
from bsdd_parser import BsddClassProperty, BsddDictionary, BsddProperty
from bsdd_parser.utils import bsdd_class_property as cp_utils
from bsdd_gui.module.property_editor_widget import ui
from PySide6.QtWidgets import QLayout, QWidget, QCompleter
from PySide6.QtCore import Signal, QCoreApplication, Qt
from bsdd_gui.module.property_editor_widget import trigger

if TYPE_CHECKING:
    from bsdd_gui.module.property_editor_widget.prop import PropertyEditorWidgetProperties


class Signals(DialogSignals):
    new_property_created = Signal(object)
    new_property_requested = Signal(
        object, QWidget
    )  # blueprint: dict[] with property values, ParentWidget


class PropertyEditorWidget(DialogTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> PropertyEditorWidgetProperties:
        return bsdd_gui.PropertyEditorWidgetProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls) -> Type[ui.PropertyEditor]:
        return ui.PropertyEditor

    @classmethod
    def _get_dialog_class(cls) -> Type[ui.PropertyCreator]:
        return ui.PropertyCreator

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.new_property_requested.connect(trigger.create_dialog)
        # Autoupdate Values
        cls.signals.field_changed.connect(lambda w, f: cls.sync_to_model(w, w.bsdd_data, f))

    @classmethod
    def request_new_property(cls, blueprint: dict = None, parent=None):
        cls.signals.new_property_requested.emit(blueprint, parent)

    @classmethod
    def connect_widget_signals(cls, widget: ui.PropertyEditor):
        super().connect_widget_signals(widget)
        w = widget
        w.cb_description.toggled.connect(lambda: cls.update_description_visiblility(w))

    @classmethod
    def get_widget(cls, bsdd_class_property: BsddClassProperty) -> ui.PropertyEditor:
        return super().get_widget(bsdd_class_property)

    @classmethod
    def create_widget(
        cls, bsdd_property: BsddProperty, parent: QWidget, mode="edit"
    ) -> ui.PropertyEditor:
        widget: ui.PropertyEditor = super().create_widget(bsdd_property, parent)
        widget.mode = mode
        widget.setWindowFlag(Qt.Tool)
        title = cls.create_window_title(bsdd_property)
        cls.get_widget(bsdd_property).setWindowTitle(title)  # TODO: Update Name Getter
        return widget

    @classmethod
    def create_window_title(cls, bsdd_property: BsddProperty):
        text = f"bSDD Property '{bsdd_property.Code}' v{bsdd_property.VersionNumber or 1}"
        return text

    @classmethod
    def create_dialog(cls, bsdd_property: BsddProperty, parent) -> ui.PropertyCreator:
        dialog: ui.PropertyCreator = super().create_dialog(bsdd_property, parent)
        dialog._widget.mode = "new"
        dialog.new_button.clicked.connect(lambda _, d=dialog: cls.validate_dialog(d))
        return dialog

    @classmethod
    def is_code_valid(cls, code: str, widget: ui.PropertyEditor, bsdd_dictionary: BsddDictionary):
        if not code:
            return False
        bsdd_property = widget.bsdd_data
        for prop in bsdd_dictionary.Properties:
            if prop.Code == code and prop != bsdd_property:
                return False
        return True

    @classmethod
    def is_name_valid(
        cls,
        name: str,
        widget: ui.PropertyEditor,
    ):
        return bool(name)

    @classmethod
    def is_datatype_valid(cls, datatype: str, widget: ui.PropertyEditor):
        return datatype in ["Boolean", "Character", "Integer", "Real", "String", "Tim"]

    @classmethod
    def update_description_visiblility(cls, widget: ui.PropertyEditor):
        if widget.cb_description.isChecked():
            widget.te_description.setVisible(True)
            widget.bsdd_data.Description = widget.te_description.toPlainText()
        else:
            widget.te_description.setVisible(False)
            widget.bsdd_data.Description = None

    @classmethod
    def generate_virtual_property(cls, code: str, model_dict: dict | None):
        model_dict = dict() if not model_dict else model_dict
        if "Code" not in model_dict:
            model_dict["Code"] = code
        if "Name" not in model_dict:
            model_dict["Name"] = code
        if "DataType" not in model_dict:
            model_dict["DataType"] = "String"
        return BsddProperty.model_validate(model_dict)
