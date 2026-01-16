from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
import logging
from PySide6.QtCore import Signal, QCoreApplication
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QComboBox, QTextEdit, QDialogButtonBox
import bsdd_gui
from bsdd_gui.presets.tool_presets import DialogSignals, DialogTool
from bsdd_json import BsddClass, BsddDictionary
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_gui.module.class_editor_widget import trigger, ui

if TYPE_CHECKING:
    from bsdd_gui.module.class_editor_widget.prop import ClassEditorWidgetProperties


class Signals(DialogSignals):
    edit_class_requested = Signal(BsddClass)
    copy_class_requested = Signal(BsddClass)  # Class To Copy
    new_class_requested = Signal(BsddClass)  # Parent Class
    grouping_requested = Signal(list)
    new_class_created = Signal(
        BsddClass
    )  # the class is not added to the Dictionary So far, this gets handled by ClassTree
    related_ifc_removed = Signal(BsddClass, str)  # class, ifc code
    related_ifc_added = Signal(BsddClass, str)  # class, ifc code


class ClassEditorWidget(DialogTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> ClassEditorWidgetProperties:
        return bsdd_gui.ClassEditorWidgetProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        return ui.ClassEditor

    @classmethod
    def _get_dialog_class(cls):
        return ui.EditDialog

    @classmethod
    def create_dialog(cls, bsdd_class: BsddClass, parent_widget: QWidget):
        dialog: ui.EditDialog = super().create_dialog(bsdd_class, parent_widget)
        dialog.new_button.clicked.connect(lambda _, d=dialog: cls.validate_dialog(d))
        return dialog

    @classmethod
    def connect_signals(cls):
        cls.signals.edit_class_requested.connect(trigger.create_dialog)
        cls.signals.copy_class_requested.connect(trigger.copy_class)
        cls.signals.new_class_requested.connect(trigger.create_new_class)
        cls.signals.grouping_requested.connect(trigger.group_classes)

    @classmethod
    def connect_widget_signals(cls, widget: ui.ClassEditor):
        super().connect_widget_signals(widget)
        cls.get_properties().old_name_value = widget.le_name.text()
        widget.le_name.textEdited.connect(lambda t, w=widget: cls.update_code(w, t))
        w = widget
        w.cb_description.toggled.connect(lambda: cls.update_description_visiblility(w))

    @classmethod
    def update_description_visiblility(cls, widget: ui.ClassEditor):
        if widget.cb_description.isChecked():
            widget.te_description.setVisible(True)
            widget.bsdd_data.Description = widget.te_description.toPlainText()
        else:
            widget.te_description.setVisible(False)
            widget.bsdd_data.Description = None

    @classmethod
    def update_code(cls, widget: ui.ClassEditor, new_value: str):
        old_value = cls.get_properties().old_name_value
        if widget.le_code.text() == dict_utils.slugify(old_value):
            widget.le_code.setText(dict_utils.slugify(new_value))
        cls.get_properties().old_name_value = new_value

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
    def sync_to_model(
        cls, widget: ui.EditDialog, element: BsddClass, explicit_field: QWidget = None
    ):
        related_ifc = set(element.RelatedIfcEntityNamesList or [])
        super().sync_to_model(widget, element, explicit_field)
        update_related_ifc = set(element.RelatedIfcEntityNamesList or [])
        added_ifc = update_related_ifc - related_ifc
        removed_ifc = related_ifc - update_related_ifc

        for ifc_code in added_ifc:
            cls.signals.related_ifc_added.emit(element, ifc_code)
        for ifc_code in removed_ifc:
            cls.signals.related_ifc_removed.emit(element, ifc_code)
