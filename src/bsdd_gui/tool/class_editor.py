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
    def add_validator(cls, widget, field, validator_function: callable, result_function: callable):
        if not widget in cls.get_properties().validator_functions:
            cls.get_properties().validator_functions[widget] = dict()
        cls.get_properties().validator_functions[widget][field] = (
            validator_function,
            result_function,
        )
        rf, vf, f, w = result_function, validator_function, field, widget
        if isinstance(f, QLineEdit):
            f.textChanged.connect(lambda text: rf(f, vf(text, w)))
        if isinstance(f, QComboBox):
            f.currentTextChanged.connect(lambda text: rf(f, vf(text, w)))
        if isinstance(f, QTextEdit):
            f.textChanged.connect(lambda: rf(f, vf(f.toPlainText(), w)))
        if isinstance(f, label_tags_input.TagInput):
            f.tagsChanged.connect(lambda: rf(f, vf(f.tags(), w)))

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
                field.setTags(value or [])

    @classmethod
    def validate_code(cls, code, widget: ui.ClassEditor, bsdd_dict):
        from bsdd_gui.tool import Util

        if cls.is_code_invalid(code, widget.bsdd_class, bsdd_dict):
            Util.set_invalid(widget.le_code, False)
        else:
            Util.set_invalid(widget.le_code, True)

    @classmethod
    def all_inputs_are_valid(cls, widget: ui.ClassEditor):
        if not cls.is_code_invalid(widget):
            return False

    @classmethod
    def is_code_invalid(cls, code: str, widget: ui.ClassEditor, bsdd_dict: BsddDictionary):
        if not code:
            return True
        bsdd_class = widget.bsdd_class
        for c in bsdd_dict.Classes:
            if c.Code == code and c != bsdd_class:
                return True

        return False

    @classmethod
    def is_name_invalid(cls, name: str, widget: ui.ClassEditor, bsdd_dict: BsddDictionary):
        if not name:
            return True
        return False

    @classmethod
    def create_new_class_dialog(cls, parent) -> ui.NewDialog:
        return ui.NewDialog(parent)
