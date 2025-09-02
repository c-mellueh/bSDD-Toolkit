from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict
from bsdd_gui.presets.prop_presets import ViewHandlerProperties

if TYPE_CHECKING:
    from . import ui


class ClassTreeProperties(
    ViewHandlerProperties,
):
    pass
