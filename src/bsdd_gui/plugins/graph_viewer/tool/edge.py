
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.edge import ui,trigger

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.edge.prop import GraphViewerEdgeProperties

class Signals():
    pass

class Edge:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerEdgeProperties:
        return bsdd_gui.GraphViewerEdgeProperties

    @classmethod
    def _get_trigger(cls):
        return trigger
