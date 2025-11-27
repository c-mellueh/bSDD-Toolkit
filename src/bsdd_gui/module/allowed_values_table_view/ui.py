from __future__ import annotations

from typing import TYPE_CHECKING
from PySide6.QtCore import Qt
from . import trigger
from bsdd_json import BsddClassProperty, BsddProperty
from bsdd_gui.presets.ui_presets import TableItemView

if TYPE_CHECKING:
    from . import models


class AllowedValuesTable(TableItemView):

    def __init__(self, *args, bsdd_data=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data: BsddClassProperty | BsddProperty = bsdd_data
        self.horizontalHeader().setStretchLastSection(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        trigger.view_created(self)

    def model(self) -> models.SortModel:
        return super().model()
    
