from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import Qt, QByteArray, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDrag
from bsdd_gui.resources.icons import get_icon
from . import trigger
from .constants import JSON_MIME, CODES_MIME

from bsdd_gui.presets.ui_presets import TreeItemView
import json

if TYPE_CHECKING:
    from .models import SortModel


class ClassView(TreeItemView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.class_view_created(self)

    # typing
    def model(self) -> SortModel:
        return super().model()

    def mimeData(self, indexes):
        def _generate_subtree_codes():
            # Subtrees are expanded Trees which also will be added as root
            subtree_codes: set[str] = set()
            seen_codes: set[str] = set()
            classes = []
            for proxy_idx in indexes:
                if not proxy_idx.isValid() or proxy_idx.column() != 0:
                    continue
                src_idx = to_source(proxy_idx)
                if not src_idx.isValid():
                    continue
                node = src_idx.internalPointer()
                if node is None or node.Code in seen_codes:
                    continue
                seen_codes.add(node.Code)
                classes.append(node)
                if not self.isExpanded(proxy_idx):
                    subtree_codes.add(node.Code)
            return subtree_codes, classes

        from bsdd_gui.tool import ClassTreeView

        # include subtree only when the node is collapsed
        proxy_model = self.model()
        if proxy_model is None:
            return super().mimeData(indexes)
        source_model = (
            proxy_model.sourceModel() if hasattr(proxy_model, "sourceModel") else proxy_model
        )
        to_source = (
            proxy_model.mapToSource if hasattr(proxy_model, "mapToSource") else (lambda i: i)
        )

        subtree_codes, classes = _generate_subtree_codes()
        if not classes:
            return super().mimeData(indexes)
        return ClassTreeView.generate_mime_data(classes, subtree_codes)

    def startDrag(self, supported_actions):
        indexes = self.selectedIndexes()
        if not indexes:
            return
        drag = QDrag(self)
        mime = self.mimeData(indexes)
        if mime is None:
            return
        drag.setMimeData(mime)
        default_action = Qt.MoveAction if supported_actions & Qt.MoveAction else supported_actions
        drag.exec(supported_actions, default_action)

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
