from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.presets.tool_presets import WidgetHandler, WidgetSignaller
from bsdd_parser import BsddClassProperty, BsddDictionary, BsddProperty
from bsdd_gui.module.property_editor import ui
from PySide6.QtWidgets import QLayout, QWidget, QCompleter
from PySide6.QtCore import Signal, QCoreApplication, Qt
from bsdd_gui.module.property_editor import trigger

if TYPE_CHECKING:
    from bsdd_gui.module.property_editor.prop import PropertyEditorProperties


class Signaller(WidgetSignaller):
    pass


class PropertyEditor(WidgetHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> PropertyEditorProperties:
        return bsdd_gui.PropertyEditorProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signaller.widget_requested.connect(trigger.create_window)
        cls.signaller.widget_created.connect(trigger.widget_created)
        cls.signaller.widget_created.connect(lambda w: cls.sync_from_model(w, w.data))
        cls.signaller.widget_closed.connect(trigger.widget_closed)
        # Autoupdate Values
        cls.signaller.field_changed.connect(lambda w, f: cls.sync_to_model(w, w.data, f))

    @classmethod
    def connect_widget_to_internal_signals(cls, widget: ui.PropertyEditor):
        widget.closed.connect(lambda w=widget: cls.signaller.widget_closed.emit(w))

    @classmethod
    def request_window(cls, bsdd_property: BsddProperty, parent=None):
        cls.signaller.widget_requested.emit(bsdd_property, parent)

    @classmethod
    def get_widget(cls, bsdd_class_property: BsddClassProperty) -> ui.PropertyEditor:
        return super().get_widget(bsdd_class_property)

    @classmethod
    def create_edit_widget(
        cls,
        bsdd_property: BsddProperty,
        parent: QWidget,
        mode="edit",
    ) -> ui.ClassPropertyEditor:
        prop = cls.get_properties()
        window = ui.PropertyEditor(bsdd_property, parent, mode=mode)
        window.setWindowFlag(Qt.Tool)
        prop.widgets.add(window)

        for plugin in prop.plugin_widget_list:
            layout: QLayout = getattr(window, plugin.layout_name)
            layout.insertWidget(plugin.index, plugin.widget())
            setattr(prop, plugin.key, plugin.value_getter)

        title = cls.create_window_title(bsdd_property)
        cls.get_widget(bsdd_property).setWindowTitle(title)  # TODO: Update Name Getter
        cls.signaller.widget_created.emit(window)
        return window

    @classmethod
    def create_window_title(cls, bsdd_property: BsddProperty):
        text = f"bSDD Property '{bsdd_property.Code}' v{bsdd_property.VersionNumber or 1}"
        return text
