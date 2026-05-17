import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QPainter
from PySide6.QtWidgets import QMenu, QTreeView

from bsdd_gui import tool
from . import trigger
from .uc_ms import TwoRowHeaderView, ClassModel, get_filter_window, _current_purposes, _current_milestones, _column_to_guids
from bsdd_gui.module.class_tree_view.constants import CODES_MIME, JSON_MIME


class _ContextMenu(QMenu):
    """QMenu that lets a submenu-parent action also respond to a direct click.

    Set ``action._direct_callback = callable`` on an action that has a submenu;
    clicking that action calls the callback instead of the default submenu toggle.
    Hovering still auto-expands the submenu as usual.
    """

    def mouseReleaseEvent(self, event):
        action = self.activeAction()
        if action is not None and getattr(action, "_direct_callback", None) is not None:
            self.hide()
            action._direct_callback()
            return
        super().mouseReleaseEvent(event)


class _UcMsViewMixin(QTreeView):
    """Adds the two-row UC/MS header and the 'Edit Use Cases / Milestones' context menu."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        header = TwoRowHeaderView(Qt.Orientation.Horizontal)
        self.setHeader(header)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        get_filter_window().register_view(self)

    def setModel(self, model) -> None:
        # Models that manage their own UC×MS columns expose register_view().
        # Anything else gets wrapped in ClassModel so it gains those columns.
        if model is not None and not hasattr(model, "register_view"):
            proxy = ClassModel(prefix_cols=2)
            proxy.setSourceModel(model)
            model = proxy
        if model is not None and hasattr(model, "register_view"):
            model.register_view(self)
        # Keep a strong Python reference so PySide6 can't GC the model wrapper
        # while C++ still holds a raw pointer — without this, signal connections
        # on the model are silently dropped after garbage collection.
        self._uc_ms_model = model
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
        menu = _ContextMenu(self)
        name = getattr(node, "Name", None) or getattr(node, "Code", None) or "Class"
        menu.addAction(f"Remove '{name}'", lambda: trigger.class_removed(node))

        purposes = _current_purposes()
        milestones = _current_milestones()
        if purposes and milestones:
            submenu = QMenu("Apply to children", menu)
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

            apply_action = menu.addMenu(submenu)

            model = self.model()
            prefix_cols = getattr(model, "_prefix_cols", 2)
            clicked_guids = _column_to_guids(index.column(), prefix_cols)
            if clicked_guids is not None:
                p_guid, m_guid = clicked_guids
                apply_action._direct_callback = (
                    lambda n=node, pg=p_guid, mg=m_guid: trigger.apply_checkstate_to_children(n, pg, mg)
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


class PsetView(_UcMsViewMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.pset_view_created(self)
