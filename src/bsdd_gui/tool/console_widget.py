from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.module.shell_widget import ui, trigger
from bsdd_gui.presets.tool_presets import WidgetTool
from bsdd_gui.presets.signal_presets import WidgetSignals

if TYPE_CHECKING:
    from bsdd_gui.module.shell_widget.prop import ShellWidgetProperties


class ShellWidget(WidgetTool):
    signals = WidgetSignals()

    @classmethod
    def get_properties(cls) -> ShellWidgetProperties:
        return bsdd_gui.ShellWidgetProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        return ui.Shell

    @classmethod
    def get_widget(cls):
        if not cls.get_widgets():
            return None
        return cls.get_widgets()[-1]

    @classmethod
    def create_widget(cls):
        from bsdd_gui.tool import Project, MainWindowWidget
        from bsdd_json.utils import class_utils, property_utils, dictionary_utils

        if not cls.get_widgets():
            widget: ui.Shell = super().create_widget()
            widget.push_local_ns("tool", bsdd_gui.tool)
            widget.push_local_ns("P", Project)
            widget.push_local_ns("MW", MainWindowWidget)
            widget.push_local_ns("cl_utils", class_utils)
            widget.push_local_ns("prop_utils", property_utils)
            widget.push_local_ns("dict_utils", dictionary_utils)
            widget.show()
            widget.eval_in_thread()
            cls.register_widget(widget)
            cls.connect_widget_signals(widget)
        return cls.get_widget()
