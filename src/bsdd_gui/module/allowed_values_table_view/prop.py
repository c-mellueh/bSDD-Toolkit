from __future__ import annotations
from bsdd_gui.presets.prop_presets import ViewProperties
from typing import TYPE_CHECKING
from bsdd_json import BsddClassProperty, BsddProperty

if TYPE_CHECKING:
    from . import ui, models


class AllowedValuesTableViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
        self.model: list[models.AllowedValuesModel] = list()
