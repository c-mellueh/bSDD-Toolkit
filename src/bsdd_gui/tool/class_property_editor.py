from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_parser import BsddClassProperty
from bsdd_gui.module.class_property_editor import ui
from PySide6.QtWidgets import QLayout
from PySide6.QtCore import Signal
from bsdd_gui.module.class_property_editor import trigger
from bsdd_gui.presets.tool_presets import ViewHandler, ViewSignaller

if TYPE_CHECKING:
    from bsdd_gui.module.class_property_editor.prop import ClassPropertyEditorProperties


class Signaller(ViewSignaller):
    window_created = Signal(ui.ClassPropertyEditor)
    paste_clipboard = Signal(ui.ClassPropertyEditor)


class ClassPropertyEditor(ViewHandler):
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
