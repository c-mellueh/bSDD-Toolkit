from __future__ import annotations
from bsdd_gui.presets.prop_presets import ViewProperties
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import models


class AllowedValuesTableViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
        self.model: list[models.AllowedValuesModel] = list()
