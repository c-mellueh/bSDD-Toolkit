
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.physics import ui,trigger

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.physics.prop import GraphViewerPhysicsProperties

class Signals():
    pass

class Physics:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerPhysicsProperties:
        return bsdd_gui.GraphViewerPhysicsProperties

    @classmethod
    def _get_trigger(cls):
        return trigger
