from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SortModel
from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtWidgets import QStyledItemDelegate, QTableView, QWidget, QListView
from . import trigger


class PsetTableView(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.view_created(self)

    def model(self) -> SortModel:
        return super().model()
