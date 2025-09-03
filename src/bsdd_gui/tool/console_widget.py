from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.module.console_widget import ui, trigger
from bsdd_gui.presets.tool_presets import WidgetTool
from bsdd_gui.presets.signal_presets import WidgetSignals

if TYPE_CHECKING:
    from bsdd_gui.module.console_widget.prop import ConsoleWidgetProperties


class ConsoleWidget(WidgetTool):
    signals = WidgetSignals()

    @classmethod
    def get_properties(cls) -> ConsoleWidgetProperties:
        return bsdd_gui.ConsoleWidgetProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        return ui.Console

    @classmethod
    def get_widget(cls):
        if not cls.get_widgets():
            return None
        return list(cls.get_widgets())[-1]

    @classmethod
    def create_widget(cls):
        if not cls.get_widgets():
            widget: ui.Console = super().create_widget()
            widget.show()
            widget.eval_in_thread()
            cls.register_widget(widget)
            cls.connect_widget_signals(widget)
        return cls.get_widget()
