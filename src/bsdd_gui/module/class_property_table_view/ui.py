from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QTableView
from . import trigger
from bsdd_gui.presets.ui_presets import TableItemView

if TYPE_CHECKING:
    from . import models


class ClassPropertyTable(TableItemView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.view_created(self)

    def model(self) -> models.SortModel:
        return super().model()
