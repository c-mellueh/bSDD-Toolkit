from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QTableView
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent
from . import trigger
from bsdd_gui.presets.ui_presets import TableItemView

if TYPE_CHECKING:
    from . import models


class PropertyTable(TableItemView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def model(self) -> models.SortModel:
        return super().model()

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.source() is None:  # different process
            e.setDropAction(Qt.CopyAction)
            e.accept()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e: QDragEnterEvent):
        if e.source() is None:
            e.setDropAction(Qt.CopyAction)
            e.accept()
        else:
            super().dragMoveEvent(e)


class ClassTable(TableItemView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def model(self) -> models.SortModel:
        return super().model()
