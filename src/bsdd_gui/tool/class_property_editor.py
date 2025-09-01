from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_parser import BsddClassProperty, BsddDictionary, BsddProperty
from bsdd_gui.module.class_property_editor import ui
from PySide6.QtWidgets import QLayout, QWidget, QCompleter
from PySide6.QtCore import Signal, QCoreApplication, Qt
from bsdd_gui.module.class_property_editor import trigger
from bsdd_gui.presets.tool_presets import WidgetHandler, WidgetSignaller
from urllib.parse import urlparse
from bsdd_gui.module.allowed_values_table.ui import AllowedValuesTable

from bsdd_parser.utils.bsdd_dictionary import is_uri
from bsdd_parser.utils import bsdd_class_property as cp_utils
from bsdd_gui.module.class_property_editor.constants import (
    BUTTON_MODE_EDIT,
    BUTTON_MODE_NEW,
    BUTTON_MODE_VIEW,
)


if TYPE_CHECKING:
    from bsdd_gui.module.class_property_editor.prop import ClassPropertyEditorProperties
    from bsdd_gui.presets.ui_presets.line_edit_with_button import LineEditWithButton


class Signaller(WidgetSignaller):
    paste_clipboard = Signal(ui.ClassPropertyEditor)
    property_reference_changed = Signal(BsddClassProperty)
    new_class_property_created = Signal(BsddClassProperty)

    new_value_requested = Signal(object)
    create_new_class_property_requested = Signal()
    edit_bsdd_property_requested = Signal(BsddProperty)  # BsddProperty not BsddClassProperty
    create_bsdd_property_requested = Signal(object)  # BsddProperty not BsddClassProperty
    property_specific_redraw_requested = Signal(ui.ClassPropertyEditor)


class ClassPropertyEditor(WidgetHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> ClassPropertyEditorProperties:
        return bsdd_gui.ClassPropertyEditorProperties

    @classmethod
    def request_property_specific_redraw(cls, widget: ui.ClassPropertyEditor):
        cls.signaller.property_specific_redraw_requested.emit(widget)

    @classmethod
    def connect_internal_signals(cls):
        cls.signaller.paste_clipboard.connect(trigger.paste_clipboard)
        cls.signaller.widget_created.connect(trigger.widget_created)
        cls.signaller.widget_closed.connect(trigger.window_closed)
        cls.signaller.widget_created.connect(lambda w: cls.sync_from_model(w, w.data))
        cls.signaller.property_reference_changed.connect(
            lambda cp: cls.request_property_specific_redraw(cls.get_window(cp))
        )
        cls.signaller.create_new_class_property_requested.connect(
            trigger.create_class_property_creator
        )
        # Autoupdate Values
        cls.signaller.field_changed.connect(lambda w, f: cls.sync_to_model(w, w.data, f))
        cls.signaller.property_specific_redraw_requested.connect(
            trigger.update_property_specific_fields
        )

    @classmethod
    def connect_widget_to_internal_signals(cls, widget: ui.ClassPropertyEditor):
        widget.closed.connect(lambda w=widget: cls.signaller.widget_closed.emit(w))
        widget.le_property_reference.button.clicked.connect(
            lambda _, w=widget: cls.handle_pr_button_press(w)
        )

        widget.pb_new_value.clicked.connect(
            lambda _, w=widget: cls.signaller.new_value_requested.emit(w)
        )

    @classmethod
    def create_create_dialog(cls, bsdd_class_property, parent, bsdd_dictionary: BsddDictionary):
        def validate_inputs(dial: ui.ClassPropertyCreator):
            widget = dial._editor_widget
            if cls.all_inputs_are_valid(widget):
                dial.accept()
            else:
                pass

        dialog = ui.ClassPropertyCreator(bsdd_class_property)
        cls.get_properties().dialog = dialog
        widget = cls.create_edit_widget(
            bsdd_class_property, parent, mode="new", bsdd_dictionary=bsdd_dictionary
        )
        cls.sync_from_model(widget, bsdd_class_property)
        dialog._layout.insertWidget(0, widget)
        dialog._editor_widget = widget
        dialog.new_button.clicked.connect(lambda _, d=dialog: validate_inputs(d))

        return dialog

    @classmethod
    def create_edit_widget(
        cls,
        bsdd_class_property: BsddClassProperty,
        parent: QWidget,
        mode="edit",
        bsdd_dictionary=None,
    ) -> ui.ClassPropertyEditor:
        prop = cls.get_properties()
        window = ui.ClassPropertyEditor(bsdd_class_property, parent, mode=mode)
        window.setWindowFlag(Qt.Tool)
        prop.widgets.add(window)
        if bsdd_dictionary:
            completer = cls.create_property_code_completer(bsdd_dictionary)
            window.le_property_reference.setCompleter(completer)
        for plugin in prop.plugin_widget_list:
            layout: QLayout = getattr(window, plugin.layout_name)
            layout.insertWidget(plugin.index, plugin.widget())
            setattr(prop, plugin.key, plugin.value_getter)

        title = cls.create_window_title(bsdd_class_property)
        cls.get_window(bsdd_class_property).setWindowTitle(title)  # TODO: Update Name Getter

        cls.signaller.widget_created.emit(window)
        return window

    @classmethod
    def create_property_code_completer(cls, bsdd_dictionary: BsddDictionary):
        all_codes = cp_utils.get_property_code_dict(bsdd_dictionary)
        completer = QCompleter(all_codes)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        return completer

    @classmethod
    def get_window(cls, bsdd_class_property: BsddClassProperty) -> ui.ClassPropertyEditor:
        windows = [
            widget for widget in cls.get_properties().widgets if widget.data == bsdd_class_property
        ]
        if len(windows) > 1:
            logging.warning(f"Multiple PropertyWindows")
        elif not windows:
            return None
        return windows[0]

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
    def show_property_info(cls, bsdd_class_property: BsddClassProperty):
        trigger.property_info_requested(bsdd_class_property)

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
        cls.signaller.property_reference_changed.emit(bsdd_class_property)

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
        bsdd_class_property = widget.data
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
            bsdd_property = cp_utils.get_internal_property(widget.data)
            cls.signaller.edit_bsdd_property_requested.emit(bsdd_property)
        elif line_edit.button_mode == BUTTON_MODE_NEW:
            bsdd_class_property: BsddClassProperty = widget.data
            code = widget.le_property_reference.text()
            blueprint = {
                "Code": code,
                "Name": code,
                "DataType": cp_utils.get_data_type(bsdd_class_property),
            }
            cls.signaller.create_bsdd_property_requested.emit(blueprint)

    @classmethod
    def update_allowed_units(cls, widget: ui.ClassPropertyEditor):
        bsdd_class_property = widget.data
        allowed_units = cp_utils.get_units(bsdd_class_property)
        current_unit = widget.cb_unit.currentText()
        index = allowed_units.index(current_unit) if current_unit in allowed_units else 0
        widget.cb_unit.clear()
        if allowed_units:
            widget.cb_unit.addItems(allowed_units)
            widget.cb_unit.setCurrentIndex(index)

    @classmethod
    def update_description_placeholder(cls, widget: ui.ClassPropertyEditor):
        bsdd_class_property = widget.data
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
        bsdd_class_property = widget.data
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
