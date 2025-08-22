from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui
from bsdd_gui.presets.prop_presets import ColumnHandlerProperties, ViewHandlerProperties


class PropertyTableProperties(ColumnHandlerProperties, ViewHandlerProperties):
    pass
