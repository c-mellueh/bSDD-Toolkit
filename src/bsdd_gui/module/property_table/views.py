from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QTableView
from . import trigger

if TYPE_CHECKING:
    from . import models


class PropertyTable(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def model(self) -> models.SortModel:
        return super().model()


class ClassTable(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def model(self) -> models.SortModel:
        return super().model()
