import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QPainter
from PySide6.QtWidgets import QMenu, QTreeView

from . import trigger
from .uc_ms import TwoRowHeaderView, ClassModel, get_filter_window
from bsdd_gui.module.class_tree_view.constants import CODES_MIME, JSON_MIME


class _UcMsViewMixin(QTreeView):
    """Adds the two-row UC/MS header and the 'Edit Use Cases / Milestones' context menu."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        header = TwoRowHeaderView(Qt.Orientation.Horizontal)
        self.setHeader(header)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        get_filter_window().register_view(self)

    def setModel(self, model) -> None:
        if model is not None and not isinstance(model, ClassModel):
            proxy = ClassModel(prefix_cols=2)
            proxy.setSourceModel(model)
            model = proxy
        if isinstance(model, ClassModel):
            model.register_view(self)
        super().setModel(model)






class ClassView(_UcMsViewMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(False)
        trigger.class_view_created(self)

    def _accepted_mime(self, data) -> bool:
        return data.hasFormat(CODES_MIME) or data.hasFormat(JSON_MIME)

    def _extract_codes(self, data) -> list[str]:
        # JSON_MIME carries the full subtree for unexpanded classes, so prefer it.
        if data.hasFormat(JSON_MIME):
            try:
                payload = json.loads(bytes(data.data(JSON_MIME)).decode("utf-8"))
                codes = [c["Code"] for c in payload.get("classes", []) if c.get("Code")]
                if codes:
                    return codes
            except Exception:
                pass
        if data.hasFormat(CODES_MIME):
            try:
                return json.loads(bytes(data.data(CODES_MIME)).decode("utf-8"))
            except Exception:
                pass
        return []

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self._accepted_mime(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if self._accepted_mime(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        codes = self._extract_codes(event.mimeData())
        if codes:
            trigger.classes_dropped(codes)
            event.acceptProposedAction()
        else:
            event.ignore()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        model = self.model()
        if model is not None and model.rowCount() > 0:
            return
        painter = QPainter(self.viewport())
        painter.save()
        painter.setPen(self.palette().placeholderText().color())
        painter.drawText(
            self.viewport().rect(),
            Qt.AlignmentFlag.AlignCenter,
            "Drag & drop classes here",
        )
        painter.restore()


class PropertyView(_UcMsViewMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.property_view_created(self)
