from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import QSortFilterProxyModel
from bsdd_gui.resources.icons import get_icon
from . import trigger
if TYPE_CHECKING:
    from .models import SortModel
class ClassView(QTreeView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.class_view_created(self)
    
    #typing
    def model(self) -> SortModel:
        return super().model()