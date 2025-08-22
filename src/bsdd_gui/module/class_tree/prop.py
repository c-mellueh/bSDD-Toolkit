from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict
from bsdd_gui.presets.prop_presets import ViewHandlerProperties, ColumnHandlerProperties

if TYPE_CHECKING:
    from . import ui


class ClassTreeProperties(
    ViewHandlerProperties,
    ColumnHandlerProperties,
):
    pass
