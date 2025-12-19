from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.window import ui, trigger
from bsdd_gui.presets.tool_presets import ActionTool, FieldTool
from bsdd_gui.presets.signal_presets import FieldSignals

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.window.prop import GraphViewerWindowProperties


class Signals(FieldSignals):
    pass


class Window(ActionTool, FieldTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerWindowProperties:
        return bsdd_gui.GraphViewerWindowProperties

    @classmethod
    def _get_trigger(cls):
        return trigger
    
    @classmethod
    def _get_widget_class(cls):
        # Lazy import to avoid heavy cost on module load
        return ui.GraphWidget
