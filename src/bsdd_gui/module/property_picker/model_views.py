from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu, QTreeView

from . import trigger
from .uc_ms import TwoRowHeaderView, UcMsColumnProxy, get_filter_window


class _UcMsViewMixin(QTreeView):
    """Adds the two-row UC/MS header and the 'Edit Use Cases / Milestones' context menu."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        header = TwoRowHeaderView(Qt.Orientation.Horizontal)
        self.setHeader(header)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_uc_ms_menu)
        get_filter_window().register_view(self)

    def setModel(self, model) -> None:
        if model is not None and not isinstance(model, UcMsColumnProxy):
            proxy = UcMsColumnProxy(prefix_cols=2)
            proxy.setSourceModel(model)
            model = proxy
        super().setModel(model)

    def _show_uc_ms_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.addAction("Edit Use Cases / Milestones", self._open_filter_window)
        menu.exec(self.viewport().mapToGlobal(pos))

    def _open_filter_window(self) -> None:
        win = get_filter_window()
        win.show()
        win.raise_()
        win.activateWindow()


class ClassView(_UcMsViewMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.class_view_created(self)


class PropertyView(_UcMsViewMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        trigger.property_view_created(self)
