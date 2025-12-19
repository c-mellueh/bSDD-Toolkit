
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.scene_view import ui,trigger

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.scene_view.prop import GraphViewerSceneViewProperties

class Signals():
    pass

class SceneView:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerSceneViewProperties:
        return bsdd_gui.GraphViewerSceneViewProperties

    @classmethod
    def _get_trigger(cls):
        return trigger
