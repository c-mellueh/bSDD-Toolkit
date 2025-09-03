from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SortModel
from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtWidgets import QStyledItemDelegate, QTableView, QWidget, QListView
from . import trigger
from bsdd_gui.presets.ui_presets import TableItemView


class PsetTableView(TableItemView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Neutralize hover accent color and unify selection color to a gray tone
        # Only affects this widget instance

        trigger.view_created(self)

    def model(self) -> SortModel:
        return super().model()
