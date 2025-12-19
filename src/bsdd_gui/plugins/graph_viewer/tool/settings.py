
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.settings import ui,trigger

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.settings.prop import GraphViewerSettingsProperties

class Signals():
    pass

class Settings:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerSettingsProperties:
        return bsdd_gui.GraphViewerSettingsProperties

    @classmethod
    def _get_trigger(cls):
        return trigger
