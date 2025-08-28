from __future__ import annotations
from typing import TYPE_CHECKING, Optional, get_origin, Union, get_args
from types import NoneType  # Python 3.10+
import logging

import bsdd_gui
from bsdd_gui.presets.tool_presets import WidgetHandler, ModuleHandler
from PySide6.QtCore import Qt, QDateTime, QObject, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QWidget,
    QLineEdit,
    QLabel,
)
from datetime import datetime
from bsdd_gui import tool
from bsdd_gui.module.dictionary_editor import constants, ui
from bsdd_parser import BsddDictionary

if TYPE_CHECKING:
    from bsdd_gui.module.dictionary_editor.prop import DictionaryEditorProperties


class Signaller(QObject):
    window_requested = Signal()


class DictionaryEditor(WidgetHandler, ModuleHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> DictionaryEditorProperties:
        return bsdd_gui.DictionaryEditorProperties

    @classmethod
    def create_widget(cls, bsdd_dictionary: BsddDictionary) -> ui.DictionaryEditor:
        prop = cls.get_properties()
        widget = ui.DictionaryEditor(bsdd_dictionary)
        prop.widgets.add(widget)

    @classmethod
    def get_widget(cls, bsdd_dictionary: BsddDictionary) -> ui.DictionaryEditor:
        widgets = [
            widget for widget in cls.get_properties().widgets if widget.data == bsdd_dictionary
        ]
        if len(widgets) > 1:
            logging.warning(f"Multiple PropertyWindows")
        elif not widgets:
            return None
        return widgets[0]

    @classmethod
    def unwrap_type(cls, tp):
        origin = get_origin(tp)
        if origin is None:
            return tp
        if origin is list or origin is dict:
            return origin  # keep container info if needed
        if origin is Union:
            args = [a for a in get_args(tp) if a is not type(None)]
            if args:
                return cls.unwrap_type(args[0])
        return tp

    @classmethod
    def fill_dictionary_widget(cls, widget: ui.DictionaryEditor) -> QWidget:
        """
        Create Widget for Dictionary Settings and fills QFormLayout
        Makes widget creation modular. If you add a field to the dictionary in its definition,
        a line will be added to the widget. As far as the datatype is string bool oder datetime others need to be implemented.
        :return: DictionaryWidget
        """
        # add Layout to Widget
        layout: QFormLayout = widget.layout()
        # list all Properties which aren't lists of elements
        presets = constants.DICTIONARY_PRESETS
        properties = [
            (name, cls.unwrap_type(field.annotation), presets.get(name))
            for name, field in BsddDictionary.model_fields.items()
            if name not in ["Classes", "Properties"]
        ]

        # Fill QFormLayout
        for index, (name, datatype, preset) in enumerate(properties):  # Iterate over all proeprties
            if datatype == str:
                if preset is None:
                    # create input line
                    w = QLineEdit()
                    w.textChanged.connect(lambda text, n=name: widget.value_changed.emit(n, text))
                else:
                    # create text dropdown
                    w = QComboBox()
                    w.addItems(preset)
                    w.currentTextChanged.connect(
                        lambda text, n=name: widget.value_changed.emit(n, text)
                    )

            # create checkbox
            elif datatype == bool:
                w = QCheckBox()
                w.checkStateChanged.connect(
                    lambda state, n=name: widget.value_changed.emit(n, state)
                )

            # create input line
            elif datatype == datetime:
                w = ui.DateTimeWithNow()
                w.dt_edit.dateTimeChanged.connect(
                    lambda time, n=name: widget.value_changed.emit(n, time)
                )

            # handle exceptions
            else:
                logging.info(f"Datatype: '{datatype}' not supported")
                w = QLineEdit()
                w.textChanged.connect(lambda text, n=name: widget.value_changed.emit(n, text))

            widget.fields[name] = w
            # fill line of QFormLayout
            layout.setWidget(index, QFormLayout.ItemRole.FieldRole, w)
            layout.setWidget(index, QFormLayout.ItemRole.LabelRole, QLabel(name))
        return widget

    @classmethod
    def get_dictionary_values(cls, widget: ui.DictionaryEditor):
        value_dict = dict()
        for field_name, field in widget.fields.items():
            if isinstance(field, QLineEdit):
                value_dict[field_name] = field.text()
            elif isinstance(field, QComboBox):
                value_dict[field_name] = field.currentText()
            elif isinstance(field, QCheckBox):
                value_dict[field_name] = field.isChecked()
            elif isinstance(field, ui.DateTimeWithNow):
                value_dict[field_name] = field.dt_edit.dateTime().toPython()
            else:
                raise TypeError(f"Unsupported widget type: {type(widget)}")
        return value_dict

    @classmethod
    def set_dictionary_values(
        cls, widget: ui.DictionaryEditor, value_dict: dict[str, str | bool | datetime]
    ):
        for name, value in value_dict.items():
            field = widget.fields.get(name)
            if not field:
                continue
            if isinstance(field, QLineEdit):
                field.setText(value)
            elif isinstance(field, QComboBox):
                field.setCurrentText(value)
            elif isinstance(field, QCheckBox):
                field.setChecked(value)
            elif isinstance(field, ui.DateTimeWithNow):
                value: datetime
                field.dt_edit.setDateTime(
                    QDateTime.fromSecsSinceEpoch(int(value.timestamp()), Qt.UTC)
                )

    @classmethod
    def attach_validation(cls, widget: QWidget, *, checkbox_empty_if_unchecked=True) -> None:
        def _run():
            cls.validate_widget(widget, checkbox_empty_if_unchecked=checkbox_empty_if_unchecked)

        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(_run)
        elif isinstance(widget, QComboBox):
            # cover both editable and non-editable
            widget.currentIndexChanged.connect(lambda *_: _run())
            widget.currentTextChanged.connect(lambda *_: _run())
        elif isinstance(widget, QCheckBox):
            widget.stateChanged.connect(lambda *_: _run())

        # initial pass
        _run()

    @classmethod
    def is_optional(cls, annotation) -> bool:
        origin = get_origin(annotation)
        if origin is Union:
            args = get_args(annotation)
            return NoneType in args
        return False

    @classmethod
    def color_required_fields(cls, widget: ui.DictionaryEditor):

        for name, field in BsddDictionary.model_fields.items():
            if name in ["Classes", "Properties"]:
                continue
            if cls.is_optional(field.annotation):
                continue
            cls.attach_validation(widget.fields[name], checkbox_empty_if_unchecked=False)

    @classmethod
    def is_empty(cls, widget: QWidget, *, checkbox_empty_if_unchecked=False) -> bool:
        if isinstance(widget, QLineEdit):
            return widget.text().strip() == ""
        if isinstance(widget, QComboBox):
            # Consider empty if no selection or the current text is empty
            # (works for both editable and non-editable combos)
            if widget.currentIndex() < 0:
                return True
            return widget.currentText().strip() == ""
        if isinstance(widget, QCheckBox):
            # Define what "empty" means for a checkbox.
            # Most UIs treat "unchecked" as empty only for required booleans.
            if widget.isTristate():
                return widget.checkState() == Qt.PartiallyChecked  # treat indeterminate as empty
            return (not widget.isChecked()) if checkbox_empty_if_unchecked else False
        # Unsupported widgets are never "empty" here
        return False

    @classmethod
    def validate_widget(cls, widget: QWidget, *, checkbox_empty_if_unchecked=True) -> bool:
        from bsdd_gui import tool

        empty = cls.is_empty(widget, checkbox_empty_if_unchecked=checkbox_empty_if_unchecked)
        tool.Util.set_invalid(widget, empty)
        return not empty

    @classmethod
    def all_inputs_are_valid(cls, widget: ui.DictionaryEditor):
        return not bool(cls.get_missing_inputs(widget))

    @classmethod
    def get_missing_inputs(cls, widget: ui.DictionaryEditor):
        missing_inputs = list()
        for name, field in BsddDictionary.model_fields.items():
            if name in ["Classes", "Properties"]:
                continue
            if cls.is_optional(field.annotation):
                continue
            field_widget = widget.fields[name]
            if cls.is_empty(field_widget):
                missing_inputs.append(name)
        return missing_inputs

    @classmethod
    def update_dictionary_value(cls, bsdd_dictionary: BsddDictionary, name, value):
        if name not in BsddDictionary.model_fields:
            return
        if isinstance(value, str):
            pass
        elif isinstance(value, Qt.CheckState):
            value = tool.Util.checkstate_to_bool(value)
        elif isinstance(value, QDateTime):
            value = value.toPython()
        setattr(bsdd_dictionary, name, value)
