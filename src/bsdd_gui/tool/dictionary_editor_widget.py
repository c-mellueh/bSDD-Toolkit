from __future__ import annotations
from typing import TYPE_CHECKING, Optional, get_origin, Union, get_args
from types import NoneType  # Python 3.10+
import logging
import re
import bsdd_gui
from bsdd_gui.presets.tool_presets import FieldTool, ActionTool, FieldSignals
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
from bsdd_gui.module.dictionary_editor_widget import constants, ui, trigger
from bsdd_json import BsddDictionary

if TYPE_CHECKING:
    from bsdd_gui.module.dictionary_editor_widget.prop import DictionaryEditorWidgetProperties


class Signals(FieldSignals):
    pass


class DictionaryEditorWidget(FieldTool, ActionTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> DictionaryEditorWidgetProperties:
        return bsdd_gui.DictionaryEditorWidgetProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        return ui.DictionaryEditor

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.field_changed.connect(lambda w, f: cls.sync_to_model(w, w.bsdd_data, f))

    @classmethod
    def create_widget(
        cls, bsdd_dictionary: BsddDictionary, parent_widget: QWidget
    ) -> ui.DictionaryEditor:
        return super().create_widget(bsdd_dictionary, parent_widget)

    @classmethod
    def get_widget(cls, bsdd_dictionary: BsddDictionary) -> ui.DictionaryEditor:
        return super().get_widget(bsdd_dictionary)

    @classmethod
    def get_name_from_field(cls, widget: ui.DictionaryEditor, field: QWidget):
        """Return the bSDD field name for a given UI field.

        The mapping follows the bSDD Dictionary schema as per the provided table.
        """
        mapping = {
            widget.le_org_code: "OrganizationCode",
            widget.le_dictionary_code: "DictionaryCode",
            widget.le_dictionary_name: "DictionaryName",
            widget.le_dictionary_version: "DictionaryVersion",
            widget.cb_language_iso: "LanguageIsoCode",
            widget.cb_language_only: "LanguageOnly",
            widget.cb_use_own_uri: "UseOwnUri",
            widget.le_dictionary_uri: "DictionaryUri",
            widget.le_license: "License",
            widget.le_license_url: "LicenseUrl",
            widget.le_change_request_mail: "ChangeRequestEmailAddress",
            widget.cb_model_version: "ModelVersion",
            widget.le_more_info: "MoreInfoUrl",
            widget.le_qa_procedure: "QualityAssuranceProcedure",
            widget.le_qa_procedure_url: "QualityAssuranceProcedureUrl",
            widget.de_release_date: "ReleaseDate",
            widget.cb_status: "Status",
        }
        return mapping.get(field)

    @classmethod
    def get_invalid_inputs(cls, widget: QWidget):
        function_dict = cls.get_properties().validator_functions.get(widget)
        if not function_dict:
            return []
        invalid_inputs = list()
        for f, (validator_function, result_function) in function_dict.items():
            value = cls.get_value_from_field(f)
            is_valid = validator_function(value, widget)
            if not is_valid:
                invalid_inputs.append(cls.get_name_from_field(widget, f))
        return invalid_inputs

    @classmethod
    def is_dictionary_code_valid(cls, value, widget):
        if value:
            return True
        return False

    @classmethod
    def is_org_code_valid(cls, value, widget):
        if value:
            return True
        return False

    @classmethod
    def is_dictionary_name_valid(cls, value, widget):
        if value:
            return True
        return False

    @classmethod
    def is_dictionary_version_valid(cls, value, widget):
        _version_pattern = re.compile(r"^(0|[1-9]\d*)(?:\.(0|[1-9]\d*)){0,2}$")
        return bool(_version_pattern.match(value))

    @classmethod
    def is_language_iso_valid(cls, value, widget):
        if value:
            return True
        return False

    @classmethod
    def is_dictionary_uri_valid(cls, value, widget: ui.DictionaryEditor):
        if widget.cb_use_own_uri.isChecked():
            if not value:
                return False
            return True
        else:
            if value:
                return False
            return True
