
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.input_bar import ui,trigger

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.input_bar.prop import GraphViewerInputBarProperties

class Signals():
    pass

class InputBar:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerInputBarProperties:
        return bsdd_gui.GraphViewerInputBarProperties

    @classmethod
    def _get_trigger(cls):
        return trigger
