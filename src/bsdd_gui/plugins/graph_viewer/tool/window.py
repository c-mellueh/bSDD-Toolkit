
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.window import ui,trigger

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.window.prop import GraphViewerWindowProperties

class Signals():
    pass

class Window:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerWindowProperties:
        return bsdd_gui.GraphViewerWindowProperties

    @classmethod
    def _get_trigger(cls):
        return trigger
