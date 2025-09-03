from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent
from bsdd_gui.resources.icons import get_icon
from . import trigger

from bsdd_gui.presets.ui_presets import TreeItemView

if TYPE_CHECKING:
    from .models import SortModel


class ClassView(TreeItemView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.class_view_created(self)

    # typing
    def model(self) -> SortModel:
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
