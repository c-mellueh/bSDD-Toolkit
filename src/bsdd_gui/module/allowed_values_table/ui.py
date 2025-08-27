from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QTableView
from . import trigger
from bsdd_parser import BsddClassProperty, BsddProperty

if TYPE_CHECKING:
    from . import models


class AllowedValuesTable(QTableView):

    def __init__(self, bsdd_property: BsddClassProperty | BsddProperty, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_property = bsdd_property
        trigger.table_view_created(self)

    def model(self) -> models.SortModel:
        return super().model()

    def closeEvent(self, event):
        trigger.table_closed(self)
        return super().closeEvent(event)
