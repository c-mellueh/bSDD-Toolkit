from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_parser import BsddClassProperty, BsddDictionary, BsddProperty
from bsdd_gui.module.class_property_editor_widget import ui
from PySide6.QtWidgets import QLayout, QWidget, QCompleter
from PySide6.QtCore import Signal, QCoreApplication, Qt
from bsdd_gui.module.class_property_editor_widget import trigger
from bsdd_gui.presets.tool_presets import DialogTool, DialogSignals
from urllib.parse import urlparse
from bsdd_gui.module.allowed_values_table_view.ui import AllowedValuesTable
from bsdd_gui.module.property_editor_widget import ui as property_editor_ui
from bsdd_parser.utils.bsdd_dictionary import is_uri
from bsdd_parser.utils import bsdd_class_property as cp_utils
from bsdd_gui.module.class_property_editor_widget.constants import (
    BUTTON_MODE_EDIT,
    BUTTON_MODE_NEW,
    BUTTON_MODE_VIEW,
)


if TYPE_CHECKING:
    from bsdd_gui.module.class_property_editor_widget.prop import (
        ClassPropertyEditorWidgetProperties,
    )
    from bsdd_gui.presets.ui_presets.line_edit_with_button import LineEditWithButton


class Signals(DialogSignals):
    paste_clipboard = Signal(ui.ClassPropertyEditor)
    property_reference_changed = Signal(BsddClassProperty)
    new_class_property_created = Signal(BsddClassProperty)

    new_value_requested = Signal(object)
    create_new_class_property_requested = Signal()
    edit_bsdd_property_requested = Signal(
        BsddProperty, QWidget
    )  # BsddProperty not BsddClassProperty,parentWidget
    create_bsdd_property_requested = Signal(object)  # BsddProperty not BsddClassProperty
    property_specific_redraw_requested = Signal(ui.ClassPropertyEditor)


class ClassPropertyEditorWidget(DialogTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> ClassPropertyEditorWidgetProperties:
        return bsdd_gui.ClassPropertyEditorWidgetProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_dialog_class(cls):
        return ui.ClassPropertyCreator

    @classmethod
    def _get_widget_class(cls):
        return ui.ClassPropertyEditor

    @classmethod
    def request_property_specific_redraw(cls, widget: ui.ClassPropertyEditor):
        cls.signals.property_specific_redraw_requested.emit(widget)

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()

        #
        cls.signals.paste_clipboard.connect(trigger.paste_clipboard)
        cls.signals.property_reference_changed.connect(
            lambda cp: cls.request_property_specific_redraw(cls.get_widget(cp))
        )
        cls.signals.create_new_class_property_requested.connect(trigger.create_dialog)
        # Autoupdate Values
        cls.signals.field_changed.connect(lambda w, f: cls.sync_to_model(w, w.bsdd_data, f))
        cls.signals.property_specific_redraw_requested.connect(
            trigger.update_property_specific_fields
        )

        # unregister
        cls.signals.widget_closed.connect(cls.unregister_widget)
        cls.signals.widget_closed.connect(lambda w: cls.unregister_widget(w.tv_allowed_values))

    @classmethod
    def connect_widget_signals(cls, widget: ui.ClassPropertyEditor):
        super().connect_widget_signals(widget)
        widget.closed.connect(lambda w=widget: cls.signals.widget_closed.emit(w))
        widget.le_property_reference.button.clicked.connect(
            lambda _, w=widget: cls.handle_pr_button_press(w)
        )

        widget.pb_new_value.clicked.connect(
            lambda _, w=widget: cls.signals.new_value_requested.emit(w)
        )

    @classmethod
    def create_dialog(
        cls,
        bsdd_class_property: BsddClassProperty,
        parent: QWidget,
        bsdd_dictionary: BsddDictionary,
    ):
        widget = cls.create_widget(
            bsdd_class_property, None, mode="new", bsdd_dictionary=bsdd_dictionary
        )
        dialog = ui.ClassPropertyCreator(widget, parent)
        cls.sync_from_model(widget, bsdd_class_property)
        dialog._layout.insertWidget(0, widget)

        dialog.new_button.clicked.connect(lambda _, d=dialog: cls.validate_dialog(d))
        cls.get_properties().dialog = dialog
        return dialog

    @classmethod
    def create_widget(
        cls,
        bsdd_class_property: BsddClassProperty,
        parent: QWidget,
        mode="edit",
        bsdd_dictionary=None,
    ) -> ui.ClassPropertyEditor:

        widget: ui.ClassPropertyEditor = super().create_widget(
            bsdd_class_property, parent, mode=mode
        )
        widget.setWindowFlag(Qt.Tool)

        if bsdd_dictionary:
            completer = cls.create_property_code_completer(bsdd_dictionary)
            widget.le_property_reference.setCompleter(completer)
        widget.setWindowTitle(cls.create_window_title(bsdd_class_property))
        return widget

    @classmethod
    def create_property_code_completer(cls, bsdd_dictionary: BsddDictionary):
        all_codes = cp_utils.get_property_code_dict(bsdd_dictionary)
        completer = QCompleter(all_codes)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        return completer

    @classmethod
    def create_window_title(cls, bsdd_class_property: BsddClassProperty):
        SEPERATOR = " : "
        text = bsdd_class_property.Code
        pset = bsdd_class_property.PropertySet
        if not pset:
            return text
        text = pset + SEPERATOR + text
        bsdd_class = bsdd_class_property.parent()
        if not bsdd_class:
            return text
        return bsdd_class.Name + SEPERATOR + text

    @classmethod
    def get_property_reference(cls, bsdd_class_property: BsddClassProperty):
        if bsdd_class_property.PropertyCode:
            return bsdd_class_property.PropertyCode
        return bsdd_class_property.PropertyUri

    @classmethod
    def set_property_reference(
        cls, bsdd_class_property: BsddClassProperty, value: str, bsdd_dictionary: BsddDictionary
    ):
        if not cls.is_property_reference_valid(value, bsdd_class_property, bsdd_dictionary):
            return

        if is_uri(value):
            bsdd_class_property.PropertyCode = None
            bsdd_class_property.PropertyUri = value
        else:
            bsdd_class_property.PropertyCode = value
            bsdd_class_property.PropertyUri = None
        cls.signals.property_reference_changed.emit(bsdd_class_property)

    @classmethod
    def is_property_reference_valid(
        cls, value, bsdd_class_property: BsddClassProperty, bsdd_dictionary: BsddDictionary
    ):
        if is_uri(value):
            return True  # Todo: check if this really exists

        # Code doesn't exist
        if not value in cp_utils.get_property_code_dict(bsdd_dictionary):
            return False

        bsdd_class = bsdd_class_property.parent()
        if not bsdd_class:
            return True
        if value in [cp.Code for cp in bsdd_class.ClassProperties if cp != bsdd_class_property]:
            return False
        return True

    @classmethod
    def handle_property_reference_button(
        cls, widget: ui.ClassPropertyEditor, field: LineEditWithButton, is_valid: bool
    ):
        value = field.text()
        bsdd_class_property = widget.bsdd_data
        bsdd_class = bsdd_class_property.parent()
        bsdd_dictionary = bsdd_class.parent() if bsdd_class else None
        line_edit = widget.le_property_reference
        if not value:
            line_edit.show_button(False)
        elif is_uri(value):
            line_edit.show_button(True)
            line_edit.set_button_mode(BUTTON_MODE_VIEW)
            line_edit.set_button_text(QCoreApplication.translate("ClassPropertyEditor", "View"))
        elif is_valid:
            line_edit.show_button(True)
            line_edit.set_button_mode(BUTTON_MODE_EDIT)
            line_edit.set_button_text(QCoreApplication.translate("ClassPropertyEditor", "Edit"))
        elif not bsdd_dictionary:
            line_edit.show_button(False)
        elif value in cp_utils.get_property_code_dict(bsdd_dictionary):
            line_edit.show_button(True)
            line_edit.set_button_mode(BUTTON_MODE_EDIT)
            line_edit.set_button_text(QCoreApplication.translate("ClassPropertyEditor", "Edit"))
        else:
            line_edit.show_button(True)
            line_edit.set_button_mode(BUTTON_MODE_NEW)
            line_edit.set_button_text(QCoreApplication.translate("ClassPropertyEditor", "New"))

    @classmethod
    def handle_pr_button_press(cls, widget: ui.ClassPropertyEditor):
        line_edit = widget.le_property_reference
        if line_edit.button_mode == BUTTON_MODE_VIEW:
            pass  # TODO Open Website
        elif line_edit.button_mode == BUTTON_MODE_EDIT:
            bsdd_property = cp_utils.get_internal_property(widget.bsdd_data)
            cls.signals.edit_bsdd_property_requested.emit(bsdd_property, widget)
        elif line_edit.button_mode == BUTTON_MODE_NEW:
            bsdd_class_property: BsddClassProperty = widget.bsdd_data
            code = widget.le_property_reference.text()
            blueprint = {
                "Code": code,
                "Name": code,
                "DataType": cp_utils.get_data_type(bsdd_class_property) or "String",
            }
            cls.signals.create_bsdd_property_requested.emit(blueprint)

    @classmethod
    def update_allowed_units(cls, widget: ui.ClassPropertyEditor):
        bsdd_class_property = widget.bsdd_data
        allowed_units = cp_utils.get_units(bsdd_class_property)
        current_unit = widget.cb_unit.currentText()
        index = allowed_units.index(current_unit) if current_unit in allowed_units else 0
        widget.cb_unit.clear()
        if allowed_units:
            widget.cb_unit.addItems(allowed_units)
            widget.cb_unit.setCurrentIndex(index)

    @classmethod
    def update_description_placeholder(cls, widget: ui.ClassPropertyEditor):
        bsdd_class_property = widget.bsdd_data
        if cp_utils.is_external_ref(bsdd_class_property):
            class_property = cp_utils.get_external_property(bsdd_class_property)
        else:
            class_property = cp_utils.get_internal_property(bsdd_class_property)
        if not class_property:
            text = ""
        elif class_property.Description:
            text = class_property.Description
        elif class_property.Definition:
            text = class_property.Definition
        else:
            text = ""
        widget.te_description.setPlaceholderText(text)

    @classmethod
    def update_value_view(cls, widget: ui.ClassPropertyEditor):
        bsdd_class_property = widget.bsdd_data
        if cp_utils.is_external_ref(bsdd_class_property):
            bsdd_property = cp_utils.get_external_property(bsdd_class_property)
        else:
            bsdd_property = cp_utils.get_internal_property(bsdd_class_property)
        if not bsdd_property:
            return
        value_kind = bsdd_property.PropertyValueKind
        layout = widget.vl_values
        for row in range(layout.count()):
            item = layout.itemAt(row)
            widget = item.widget()
            if isinstance(widget, AllowedValuesTable) and (
                value_kind == "Single" or value_kind is None
            ):
                widget.setHidden(False)

    @classmethod
    def handle_field_changed(cls, parent_widget: property_editor_ui.PropertyEditor, field):
        for widget in cls.get_widgets():
            bsdd_class_property: BsddClassProperty = widget.bsdd_data
            internal_prop = cp_utils.get_internal_property(bsdd_class_property)
            if not internal_prop:
                continue
            if parent_widget.bsdd_data == internal_prop:
                cls.request_property_specific_redraw(widget)

    @classmethod
    def create_temporary_property(cls, property_set, bsdd_class):
        code = QCoreApplication.translate("ClassPropertyEditor", "New Code")
        bsdd_class_property = BsddClassProperty.model_validate(
            {"Code": code, "PropertyCode": code, "PropertyUri": None, "IsRequired": True}
        )
        bsdd_class_property.PropertySet = property_set
        bsdd_class_property._set_parent(bsdd_class)
        return bsdd_class_property

    ### Settings Window
    @classmethod
    def set_splitter_settings_widget(cls, widget: ui.SplitterSettings):
        cls.get_properties().splitter_settings = widget

    @classmethod
    def get_splitter_settings_widget(cls) -> ui.SplitterSettings:
        return cls.get_properties().splitter_settings

    @classmethod
    def connect_splitter_widget(cls, widget: ui.SplitterSettings):
        widget.ui.check_box_seperator.checkStateChanged.connect(
            lambda: trigger.splitter_checkstate_changed(widget)
        )

    @classmethod
    def get_splitter_settings_checkstate(cls, widget: ui.SplitterSettings) -> bool:
        return widget.ui.check_box_seperator.isChecked()

    @classmethod
    def get_splitter_settings_text(cls, widget: ui.SplitterSettings) -> str:
        return widget.ui.line_edit_seperator.text()

    @classmethod
    def validate_widgets(cls):
        for widget in cls.get_widgets():
            widget: ui.ClassPropertyEditor
            cls.validate_all_fields(widget)
