import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QPainter
from PySide6.QtWidgets import QMenu, QTreeView

from bsdd_gui import tool
from . import trigger
from .uc_ms import TwoRowHeaderView, ClassModel, get_filter_window, _current_purposes, _current_milestones, _column_to_guids
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
        self.customContextMenuRequested.connect(self._show_context_menu)
        trigger.class_view_created(self)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Delete:
            nodes = [
                idx.internalPointer()
                for idx in self.selectedIndexes()
                if idx.column() == 0 and idx.internalPointer() is not None
            ]
            for node in nodes:
                trigger.class_removed(node)
            return
        super().keyPressEvent(event)

    def _show_context_menu(self, pos) -> None:
        index = self.indexAt(pos)
        if not index.isValid():
            return
        node = index.internalPointer()
        if node is None:
            return
        menu = QMenu(self)
        name = getattr(node, "Name", None) or getattr(node, "Code", None) or "Class"
        menu.addAction(f"Remove '{name}'", lambda: trigger.class_removed(node))

        purposes = _current_purposes()
        milestones = _current_milestones()
        if purposes and milestones:
            # If the click landed on a specific UC×MS column, offer a fast-path direct action.
            model = self.model()
            prefix_cols = getattr(model, "_prefix_cols", 2)
            clicked_guids = _column_to_guids(index.column(), prefix_cols)
            if clicked_guids is not None:
                p_guid, m_guid = clicked_guids
                purpose = next((p for p in purposes if p.guid == p_guid), None)
                milestone = next((m for m in milestones if m.guid == m_guid), None)
                if purpose and milestone:
                    p_name = tool.PropertyPicker.purpose_display_name(purpose)
                    m_name = tool.PropertyPicker.milestone_display_name(milestone)
                    direct = menu.addAction(f"Apply '{p_name} × {m_name}' to children")
                    direct.triggered.connect(
                        lambda _checked, n=node, pg=p_guid, mg=m_guid: trigger.apply_checkstate_to_children(n, pg, mg)
                    )

            submenu = menu.addMenu("Apply to children")
            for purpose in purposes:
                for milestone in milestones:
                    p_name = tool.PropertyPicker.purpose_display_name(purpose)
                    m_name = tool.PropertyPicker.milestone_display_name(milestone)
                    included = tool.PropertyPicker.is_class_included(node, purpose.guid, milestone.guid)
                    action = submenu.addAction(f"{p_name} × {m_name}")
                    action.setCheckable(True)
                    action.setChecked(included)
                    p_guid = purpose.guid
                    m_guid = milestone.guid
                    action.triggered.connect(
                        lambda _checked, n=node, pg=p_guid, mg=m_guid: trigger.apply_checkstate_to_children(n, pg, mg)
                    )

        menu.exec(self.viewport().mapToGlobal(pos))

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
