from __future__ import annotations
from typing import TYPE_CHECKING, Optional, get_origin, Union, get_args
from types import NoneType  # Python 3.10+
import logging
import re
import bsdd_gui
from bsdd_gui.presets.tool_presets import WidgetHandler, ModuleHandler, WidgetSignaller
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
from bsdd_gui.module.dictionary_editor import constants, ui, trigger
from bsdd_parser import BsddDictionary

if TYPE_CHECKING:
    from bsdd_gui.module.dictionary_editor.prop import DictionaryEditorProperties


class Signaller(WidgetSignaller):
    pass


class DictionaryEditor(WidgetHandler, ModuleHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> DictionaryEditorProperties:
        return bsdd_gui.DictionaryEditorProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signaller.widget_requested.connect(trigger.create_widget)
        cls.signaller.widget_created.connect(trigger.widget_created)
        cls.signaller.widget_created.connect(lambda w: cls.sync_from_model(w, w.data))
        cls.signaller.widget_closed.connect(trigger.widget_closed)
        cls.signaller.field_changed.connect(lambda w, f: cls.sync_to_model(w, w.data, f))

    @classmethod
    def connect_widget_to_internal_signals(cls, widget: ui.DictionaryEditor):
        widget.closed.connect(lambda w=widget: cls.signaller.widget_closed.emit(w))

    @classmethod
    def create_widget(
        cls, bsdd_dictionary: BsddDictionary, parent_widget: QWidget
    ) -> ui.DictionaryEditor:
        prop = cls.get_properties()
        widget = ui.DictionaryEditor(bsdd_dictionary, parent_widget)
        prop.widgets.add(widget)
        cls.signaller.widget_created.emit(widget)
        return widget

    @classmethod
    def get_widget(cls, bsdd_dictionary: BsddDictionary) -> ui.DictionaryEditor:
        return super().get_widget(bsdd_dictionary)

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
