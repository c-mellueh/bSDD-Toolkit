from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
import logging
from PySide6.QtCore import Signal, QCoreApplication
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QComboBox, QTextEdit, QDialogButtonBox
import bsdd_gui
from bsdd_gui.presets.tool_presets import WidgetSignals, WidgetTool
from bsdd_parser import BsddClass, BsddDictionary
from bsdd_gui.module.class_editor_widget import trigger, ui
from bsdd_gui.presets.ui_presets import label_tags_input
from bsdd_parser.utils import bsdd_class as class_utils

if TYPE_CHECKING:
    from bsdd_gui.module.class_editor_widget.prop import ClassEditorWidgetProperties


class Signals(WidgetSignals):
    edit_class_requested = Signal(BsddClass)
    copy_class_requested = Signal(BsddClass)  # Class To Copy
    new_class_requested = Signal(BsddClass)  # Parent Class
    grouping_requested = Signal(list)
    new_class_created = Signal(
        BsddClass
    )  # the class is not added to the Dictionary So far, this gets handled by ClassTree
    dialog_accepted = Signal(ui.ClassEditor)


class ClassEditor(WidgetTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> ClassEditorWidgetProperties:
        return bsdd_gui.ClassEditorProperties

    @classmethod
    def connect_signals(cls):
        cls.signals.edit_class_requested.connect(trigger.open_class_editor)
        cls.signals.copy_class_requested.connect(trigger.copy_class)
        cls.signals.new_class_requested.connect(trigger.create_new_class)
        cls.signals.grouping_requested.connect(trigger.group_classes)

    @classmethod
    def request_class_editor(cls, bsdd_class: BsddClass):
        cls.signals.edit_class_requested.emit(bsdd_class)

    @classmethod
    def request_class_copy(cls, bsdd_class: BsddClass):
        cls.signals.copy_class_requested.emit(bsdd_class)

    @classmethod
    def request_new_class(cls, parent=None):
        cls.signals.new_class_requested.emit(parent)

    @classmethod
    def request_class_grouping(cls, bsdd_classes: list[BsddClass]):
        cls.signals.grouping_requested.emit(bsdd_classes)

    @classmethod
    def create_widget(cls, bsdd_class: BsddClass):
        widget = ui.ClassEditor(bsdd_class)
        return widget

    @classmethod
    def is_code_valid(cls, code: str, widget: ui.ClassEditor, bsdd_dict: BsddDictionary):
        if not code:
            return False
        bsdd_class = widget.bsdd_data
        for c in bsdd_dict.Classes:
            if c.Code == code and c != bsdd_class:
                return False
        return True

    @classmethod
    def is_name_valid(cls, name: str, widget: ui.ClassEditor, bsdd_dict: BsddDictionary):
        if not name.strip():
            return False
        return True

    @classmethod
    def copy_class(cls, bsdd_class: BsddClass):
        return BsddClass(**bsdd_class.model_dump())

    @classmethod
    def create_class_editor_dialog(cls, bsdd_class: BsddClass, parent_widget: QWidget):
        def validate_inputs(dial: ui.EditDialog):
            widget = dial._editor_widget
            if cls.all_inputs_are_valid(widget):
                dial.accept()
            else:
                pass

        dialog = ui.EditDialog(parent_widget)
        widget = cls.create_widget(bsdd_class)
        cls.sync_from_model(widget, bsdd_class)
        dialog._layout.insertWidget(0, widget)
        dialog._editor_widget = widget
        dialog.new_button.clicked.connect(lambda _, d=dialog: validate_inputs(d))

        return dialog
