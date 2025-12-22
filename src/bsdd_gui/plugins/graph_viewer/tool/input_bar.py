from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from bsdd_json import BsddDictionary
import bsdd_gui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCompleter
from bsdd_gui.plugins.graph_viewer.module.input_bar import ui, trigger
from bsdd_gui.presets.tool_presets import WidgetTool, WidgetSignals, PluginTool, PluginSignals
from bsdd_json.utils import class_utils
from bsdd_json.utils import property_utils as prop_utils

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.input_bar.prop import GraphViewerInputBarProperties


class Signals(PluginSignals, WidgetSignals):
    pass


class InputBar(PluginTool, WidgetTool):
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

    @classmethod
    def update_completer(cls, bsdd_dictionary: BsddDictionary):
        if not bsdd_dictionary:
            return
        entries = list(class_utils.get_all_class_codes(bsdd_dictionary).keys())
        entries += list(prop_utils.get_all_property_codes(bsdd_dictionary).keys())
        widget = cls.get_widget()
        if not widget:
            return
        completer = QCompleter(entries)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)  # substring match
        completer.setCompletionMode(QCompleter.PopupCompletion)
        widget.line_edit.setCompleter(completer)
