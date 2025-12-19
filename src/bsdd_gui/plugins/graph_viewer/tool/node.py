
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.node import ui,trigger

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.node.prop import GraphViewerNodeProperties

class Signals():
    pass

class Node:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerNodeProperties:
        return bsdd_gui.GraphViewerNodeProperties

    @classmethod
    def _get_trigger(cls):
        return trigger
