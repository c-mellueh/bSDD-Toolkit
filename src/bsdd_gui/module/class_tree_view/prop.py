from __future__ import annotations

from typing import TYPE_CHECKING
from bsdd_gui.presets.prop_presets import ViewProperties
from bsdd_json import BsddDictionary

if TYPE_CHECKING:
    from . import models


class ClassTreeViewProperties(ViewProperties):
    models: dict[BsddDictionary, models.ClassTreeModel]
