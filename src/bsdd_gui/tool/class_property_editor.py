from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_parser import BsddClassProperty, BsddDictionary
from bsdd_gui.module.class_property_editor import ui
from PySide6.QtWidgets import QLayout
from PySide6.QtCore import Signal
from bsdd_gui.module.class_property_editor import trigger
from bsdd_gui.presets.tool_presets import WidgetHandler, WidgetSignaller
from urllib.parse import urlparse

from bsdd_parser.utils import bsdd_class_property as cp_utils
from bsdd_parser.utils import bsdd_class as c_utils


def is_uri(s: str) -> bool:
    try:
        result = urlparse(s)
        return all([result.scheme, result.netloc])  # requires scheme + host
    except ValueError:
        return False


if TYPE_CHECKING:
    from bsdd_gui.module.class_property_editor.prop import ClassPropertyEditorProperties
    from bsdd_gui.presets.ui_presets.line_edit_with_button import LineEditWithButton


class Signaller(WidgetSignaller):
    window_created = Signal(ui.ClassPropertyEditor)
    paste_clipboard = Signal(ui.ClassPropertyEditor)


class ClassPropertyEditor(WidgetHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> ClassPropertyEditorProperties:
        return bsdd_gui.ClassPropertyEditorProperties

    @classmethod
    def connect_signals(cls):
        cls.signaller.paste_clipboard.connect(trigger.paste_clipboard)
        cls.signaller.window_created.connect(trigger.window_created)

        cls.signaller.window_created.connect(
            lambda w: cls.sync_from_model(w, w.bsdd_class_property)
        )

    @classmethod
    def create_window(cls, bsdd_class_property: BsddClassProperty) -> ui.ClassPropertyEditor:
        prop = cls.get_properties()
        window = ui.ClassPropertyEditor(bsdd_class_property)
        prop.windows.append(window)

        for plugin in prop.plugin_widget_list:
            layout: QLayout = getattr(cls.get_window(), plugin.layout_name)
            layout.insertWidget(plugin.index, plugin.widget())
            setattr(prop, plugin.key, plugin.value_getter)

        title = cls.create_window_title(bsdd_class_property)
        cls.get_window(bsdd_class_property).setWindowTitle(title)  # TODO: Update Name Getter

        cls.signaller.window_created.emit(window)
        return window

    @classmethod
    def get_window(cls, bsdd_class_property: BsddClassProperty) -> ui.ClassPropertyEditor:
        for window in cls.get_properties().windows:
            if window.bsdd_class_property == bsdd_class_property:
                return window
        return None

    @classmethod
    def create_window_title(cls, bsdd_class_property: BsddClassProperty):
        SEPERATOR = " : "
        text = bsdd_class_property.Code
        pset = bsdd_class_property.PropertySet
        if not pset:
            return text
        text = pset + SEPERATOR + text
        som_class = bsdd_class_property._parent_ref
        if not som_class:
            return text
        return som_class().Name + SEPERATOR + text

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

    @classmethod
    def is_property_reference_valid(
        cls, value, bsdd_class_property: BsddClassProperty, bsdd_dictionary: BsddDictionary
    ):
        if is_uri(value):
            return True  # Todo: check if this really exists

        # Code doesn't exist
        if not value in cp_utils.get_all_property_codes(bsdd_dictionary):
            return False

        bsdd_class = bsdd_class_property._parent_ref()
        if value in [cp.Code for cp in bsdd_class.ClassProperties if cp != bsdd_class_property]:
            return False
        return True

    @classmethod
    def handle_property_reference_button(
        cls, widget: ui.ClassPropertyEditor, field: LineEditWithButton, is_valid: bool
    ):
        value = field.text()
        bsdd_class_property = widget.bsdd_class_property
        bsdd_class = bsdd_class_property._parent_ref() if bsdd_class_property._parent_ref else None
        bsdd_dictionary = (
            bsdd_class._parent_ref() if bsdd_class and bsdd_class._parent_ref else None
        )
        if not value:
            widget.le_property_reference.show_button(False)
        elif is_valid:
            widget.le_property_reference.show_button(False)
        elif is_uri(value):
            widget.le_property_reference.show_button(False)
        elif not bsdd_dictionary:
            widget.le_property_reference.show_button(False)
        elif value in cp_utils.get_all_property_codes(bsdd_dictionary):
            widget.le_property_reference.show_button(False)
        else:
            widget.le_property_reference.show_button(True)
