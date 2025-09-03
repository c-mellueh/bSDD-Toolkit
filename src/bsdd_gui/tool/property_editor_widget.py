from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.presets.tool_presets import WidgetTool, WidgetSignals
from bsdd_parser import BsddClassProperty, BsddDictionary, BsddProperty
from bsdd_parser.utils import bsdd_class_property as cp_utils
from bsdd_gui.module.property_editor_widget import ui
from PySide6.QtWidgets import QLayout, QWidget, QCompleter
from PySide6.QtCore import Signal, QCoreApplication, Qt
from bsdd_gui.module.property_editor_widget import trigger

if TYPE_CHECKING:
    from bsdd_gui.module.property_editor_widget.prop import PropertyEditorWidgetProperties


class Signals(WidgetSignals):
    new_property_created = Signal(object)
    new_property_requested = Signal(object)  # blueprint: dict[] with property values


class PropertyEditorWidget(WidgetTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> PropertyEditorWidgetProperties:
        return bsdd_gui.PropertyEditorWidgetProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signals.widget_requested.connect(trigger.create_window)
        cls.signals.widget_created.connect(trigger.widget_created)
        cls.signals.widget_created.connect(lambda w: cls.sync_from_model(w, w.bsdd_data))
        cls.signals.widget_closed.connect(trigger.widget_closed)
        cls.signals.new_property_requested.connect(trigger.create_property_creator)
        # Autoupdate Values
        cls.signals.field_changed.connect(lambda w, f: cls.sync_to_model(w, w.bsdd_data, f))

    @classmethod
    def request_new_property(cls, blueprint: dict = None):
        cls.signals.new_property_requested.emit(blueprint)

    @classmethod
    def connect_widget_to_internal_signals(cls, widget: ui.PropertyEditor):
        w = widget
        w.closed.connect(lambda: cls.signals.widget_closed.emit(w))
        w.cb_description.toggled.connect(lambda: cls.update_description_visiblility(w))

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
        cls.signals.widget_created.emit(window)
        return window

    @classmethod
    def create_window_title(cls, bsdd_property: BsddProperty):
        text = f"bSDD Property '{bsdd_property.Code}' v{bsdd_property.VersionNumber or 1}"
        return text

    @classmethod
    def create_create_dialog(
        cls,
        bsdd_property: BsddProperty,
        parent,
    ) -> ui.PropertyCreator:
        def validate_inputs(dial: ui.PropertyCreator):
            widget = dial._editor_widget
            if cls.all_inputs_are_valid(widget):
                dial.accept()
            else:
                pass

        dialog = ui.PropertyCreator(bsdd_property)
        cls.get_properties().dialog = dialog
        widget = cls.create_edit_widget(bsdd_property, parent, mode="new")
        cls.sync_from_model(widget, bsdd_property)
        dialog._layout.insertWidget(0, widget)
        dialog._editor_widget = widget
        dialog.new_button.clicked.connect(lambda _, d=dialog: validate_inputs(d))
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
