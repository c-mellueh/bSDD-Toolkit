from __future__ import annotations
from bsdd_gui.presets.prop_presets import WidgetProperties
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


class GraphViewerSettingsProperties(WidgetProperties):
    def __init__(self):
        super().__init__()
        self.expanded_width = 240
        self.is_expanded = True