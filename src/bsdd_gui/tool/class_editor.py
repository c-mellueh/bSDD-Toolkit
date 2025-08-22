from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QComboBox, QTextEdit
import bsdd_gui
from bsdd_gui.presets.tool_presets import WidgetSignaller, WidgetHandler
from bsdd_parser import BsddClass
from bsdd_gui.module.class_editor import trigger, ui

if TYPE_CHECKING:
    from bsdd_gui.module.class_editor.prop import ClassEditorProperties


class Signaller(WidgetSignaller):
    class_info_requested = Signal(BsddClass)


class ClassEditor(WidgetHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> ClassEditorProperties:
        return bsdd_gui.ClassEditorProperties

    @classmethod
    def connect_signaller(cls):
        cls.signaller.class_info_requested.connect(trigger.open_class_editor)

    @classmethod
    def create_widget(cls, bsdd_class: BsddClass):
        widget = ui.ClassEditor(bsdd_class)
        return widget

    @classmethod
    def register_field_getter(
        cls, class_editor: ui.ClassEditor, field: QWidget, getter_func: callable
    ):
        if not class_editor in cls.get_properties().field_getter:
            cls.get_properties().field_getter[class_editor] = dict()
        cls.get_properties().field_getter[class_editor][field] = getter_func

    @classmethod
    def register_field_setter(
        cls, class_editor: ui.ClassEditor, field: QWidget, setter_func: callable
    ):
        if not class_editor in cls.get_properties().field_getter:
            cls.get_properties().field_getter[class_editor] = dict()
        cls.get_properties().field_getter[class_editor][field] = getter_func

    @classmethod
    def sync_from_model(cls, class_editor: ui.ClassEditor):
        bsdd_class = class_editor.bsdd_class
        for field, getter_func in cls.get_properties().field_getter[class_editor].items():
            value = getter_func(bsdd_class)
            if isinstance(field, QLineEdit):
                field.setText(value)
            if isinstance(field, QLabel):
                field.setText(value)
            if isinstance(field, QComboBox):
                field.setCurrentText(value)
            if isinstance(field, QTextEdit):
                field.setPlainText(value)
