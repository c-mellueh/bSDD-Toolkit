from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Signal
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QComboBox, QTextEdit
import bsdd_gui
from bsdd_gui.presets.tool_presets import WidgetSignaller, WidgetHandler
from bsdd_parser import BsddClass, BsddDictionary
from bsdd_gui.module.class_editor import trigger, ui
from bsdd_gui.presets.ui_presets import label_tags_input
from bsdd_parser.utils import bsdd_class as class_util

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
    def register_basic_field(cls, class_editor: ui.ClassEditor, field: QWidget, variable_name: str):
        cls.register_field_getter(class_editor, field, lambda c, vn=variable_name: getattr(c, vn))
        cls.register_field_setter(
            field, lambda v, w=class_editor, vn=variable_name: setattr(w.bsdd_class, vn, v)
        )

    @classmethod
    def register_field_getter(
        cls, class_editor: ui.ClassEditor, field: QWidget, getter_func: callable
    ):
        if not class_editor in cls.get_properties().field_getter:
            cls.get_properties().field_getter[class_editor] = dict()
        cls.get_properties().field_getter[class_editor][field] = getter_func

    @classmethod
    def register_field_setter(cls, field: QWidget, setter_func: callable):
        if isinstance(field, QLineEdit):
            field.textChanged.connect(setter_func)
        if isinstance(field, QComboBox):
            field.currentIndexChanged.connect(setter_func)
        if isinstance(field, QTextEdit):
            field.textChanged.connect(lambda f=field, sf=setter_func: sf(f.toPlainText()))
        if isinstance(field, label_tags_input.TagInput):
            field.tagsChanged.connect(setter_func)

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
            if isinstance(field, label_tags_input.TagInput):
                field.setTags(value)

    @classmethod
    def set_text_color(cls, widget: QLineEdit, color: str):
        widget.setStyleSheet(f"QLineEdit {{color:{color};}}")

    @classmethod
    def handle_code_color(cls, code, widget: ui.ClassEditor, bsdd_dict):
        if cls.is_code_allowed(code, widget, bsdd_dict):
            cls.set_text_color(widget.le_code, QPalette().color(QPalette.Text).name())
        else:
            cls.set_text_color(widget.le_code, "red")

    @classmethod
    def is_code_allowed(cls, code: str, widget: ui.ClassEditor, bsdd_dict: BsddDictionary):
        bsdd_class = widget.bsdd_class
        for c in bsdd_dict.Classes:
            if c.Code == code and c != bsdd_class:
                return False
        return True
