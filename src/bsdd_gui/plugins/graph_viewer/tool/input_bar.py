from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.input_bar import ui, trigger
from bsdd_gui.presets.tool_presets import WidgetTool, WidgetSignals

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.input_bar.prop import GraphViewerInputBarProperties


class Signals(WidgetSignals):
    pass


class InputBar(WidgetTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerInputBarProperties:
        return bsdd_gui.GraphViewerInputBarProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        return ui.InputBar

    @classmethod
    def connect_widget_signals(cls, widget: ui.InputBar):
        widget.line_edit.returnPressed.connect(trigger.add_node)
        return super().connect_widget_signals(widget)

    @classmethod
    def get_widget(cls) -> ui.InputBar:
        widgets = cls.get_widgets()
        if widgets:
            return widgets[-1]

    @classmethod
    def get_text(cls):
        widget = cls.get_widget()
        if not widget:
            return ""
        return widget.line_edit.text()

    @classmethod
    def clear(cls):
        widget = cls.get_widget()
        if not widget:
            return 
        widget.line_edit.clear()