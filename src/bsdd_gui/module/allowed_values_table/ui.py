from __future__ import annotations

from typing import TYPE_CHECKING
from PySide6.QtCore import Qt
from . import trigger
from bsdd_parser import BsddClassProperty, BsddProperty
from bsdd_gui.presets.view_presets import TableItemView

if TYPE_CHECKING:
    from . import models


class AllowedValuesTable(TableItemView):

    def __init__(self, bsdd_property: BsddClassProperty | BsddProperty, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data: BsddClassProperty | BsddProperty = bsdd_property
        self.horizontalHeader().setStretchLastSection(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def model(self) -> models.SortModel:
        return super().model()

    def closeEvent(self, event):
        trigger.view_closed(self)
        return super().closeEvent(event)
