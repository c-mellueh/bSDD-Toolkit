from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import ui

from bsdd_gui.presets.prop_presets import ColumnHandlerProperties
class PropertySetTableProperties(ColumnHandlerProperties):
    views:set[ui.PsetTableView] = set()
