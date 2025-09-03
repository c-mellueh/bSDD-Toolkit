from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict
from bsdd_gui.presets.prop_presets import ViewProperties
from bsdd_parser import BsddDictionary

if TYPE_CHECKING:
    from . import ui, models


class ClassTreeViewProperties(
    ViewProperties,
):
    models: dict[BsddDictionary, models.ClassTreeModel]
