
from __future__ import annotations
from typing import TYPE_CHECKING,TypedDict
import logging
from PySide6.QtCore import Signal

import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool,FieldTool,FieldSignals
from bsdd_gui.module.excel import ui,trigger

class PsetDict(TypedDict):
    checked: bool
    proeprties: dict[str, bool]


class BasicSettingsDict(TypedDict):
    inherit: bool
    classification: bool
    type_objects: bool
    main_pset: str
    main_property: str

class SettingsDict(TypedDict):
    class_settings: dict[str, bool]
    property_settings: dict[str, dict[str, PsetDict]]
    settings: BasicSettingsDict


if TYPE_CHECKING:
    from bsdd_gui.module.excel.prop import ExcelProperties

class Signals(FieldSignals):
    pass

class Excel(ActionTool,FieldTool):
    @classmethod
    def get_properties(cls) -> ExcelProperties:
        return bsdd_gui.ExcelProperties

    @classmethod
    def _get_widget_class(cls) -> type[ui.Widget]:
        return ui.Widget
    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def create_widget(cls, *args, **kwargs) -> ui.Widget:
        widget = cls._get_widget_class()(*args, **kwargs)
        cls.add_plugins_to_widget(widget)
        return widget

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()

    @classmethod
    def connect_widget_signals(cls, widget: ui.Widget):
        widget.pb_import.clicked.connect(lambda: trigger.import_settings(widget))
        widget.pb_export.clicked.connect(lambda: trigger.export_settings(widget))
        widget.pb_create.clicked.connect(lambda _, w=widget: trigger.export_ids(w))
        super().connect_widget_signals(widget)

    @classmethod
    def get_settings(cls, widget: ui.Widget) -> BasicSettingsDict:

        settings_dict = {
            # "inherit": widget.cb_inh.isChecked(),
            # "classification": widget.cb_clsf.isChecked(),
            # "type_objects": widget.cb_type_objects.isChecked(),
            # "main_pset": widget.cb_pset.currentText(),
            # "main_property": widget.cb_prop.currentText(),
            # "datatype": widget.cb_datatype.currentText(),
            # "datatype_mapping": cls.get_datatype_mapping(widget),
        }
        return settings_dict