from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties


class GraphViewWidgetProperties(ActionsProperties):
    def __init__(self):
        super().__init__()
        # keep references to opened windows if needed
        self.windows: list = []
