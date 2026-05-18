from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


from bsdd_gui.presets.prop_presets import WidgetProperties


class SearchWidgetProperties(WidgetProperties):
    filter_threshold: int = 65
    search_mode = 1  # 1 = Class 2= Property
    selected_info = None
