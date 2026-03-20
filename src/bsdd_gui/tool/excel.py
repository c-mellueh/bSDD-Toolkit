
from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Signal

import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool,FieldTool,FieldSignals
from bsdd_gui.module.excel import ui,trigger

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
        super().connect_widget_signals(widget)

