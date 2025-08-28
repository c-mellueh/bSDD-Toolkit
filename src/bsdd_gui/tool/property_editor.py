from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.presets.tool_presets import WidgetHandler, WidgetSignaller
from bsdd_parser import BsddClassProperty, BsddDictionary, BsddProperty
from bsdd_gui.module.class_property_editor import ui
from PySide6.QtWidgets import QLayout, QWidget, QCompleter
from PySide6.QtCore import Signal, QCoreApplication, Qt
from bsdd_gui.module.property_editor import trigger

if TYPE_CHECKING:
    from bsdd_gui.module.property_editor.prop import PropertyEditorProperties


class Signaller(WidgetSignaller):
    window_requested = Signal(BsddProperty)


class PropertyEditor(WidgetHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> PropertyEditorProperties:
        return bsdd_gui.PropertyEditorProperties

    @classmethod
    def connect_signals(cls):
        cls.signaller.window_requested.connect(trigger.create_window)

    @classmethod
    def request_window(cls, bsdd_property: BsddProperty):
        cls.signaller.window_requested.emit(bsdd_property)

    @classmethod
    def get_window(cls, bsdd_class_property: BsddClassProperty) -> ui.ClassPropertyEditor:
        windows = [
            widget
            for widget in cls.get_properties().widgets
            if widget.bsdd_property == bsdd_class_property
        ]
        if len(windows) > 1:
            logging.warning(f"Multiple PropertyWindows")
        elif not windows:
            return None
        return windows[0]

    @classmethod
    def create_edit_widget(
        cls,
        bsdd_property: BsddProperty,
        parent: QWidget,
        mode="edit",
    ) -> ui.ClassPropertyEditor:
        prop = cls.get_properties()
        window = ui.ClassPropertyEditor(bsdd_property, parent, mode=mode)
        window.setWindowFlag(Qt.Tool)
        prop.widgets.add(window)

        for plugin in prop.plugin_widget_list:
            layout: QLayout = getattr(window, plugin.layout_name)
            layout.insertWidget(plugin.index, plugin.widget())
            setattr(prop, plugin.key, plugin.value_getter)

        title = cls.create_window_title(bsdd_property)
        cls.get_window(bsdd_property).setWindowTitle(title)  # TODO: Update Name Getter
        cls.signaller.widget_created.emit(window)
        return window

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
