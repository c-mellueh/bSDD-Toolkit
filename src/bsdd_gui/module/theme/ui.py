from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QAbstractItemView, QWidget

from bsdd_gui.resources.icons import get_icon


class ViewZoomFilter(QObject):
    """App-wide filter: Ctrl + mouse wheel over an item view zooms all views."""

    def eventFilter(self, watched, event):
        if event.type() != QEvent.Type.Wheel:
            return False
        if not isinstance(watched, QWidget):
            return False
        if not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            return False
        if self._parent_item_view(watched) is None:
            return False
        delta = event.angleDelta().y()
        if delta == 0:
            return False
        from . import trigger

        trigger.view_zoom_scrolled(1 if delta > 0 else -1)
        return True

    @staticmethod
    def _parent_item_view(widget: QWidget) -> QAbstractItemView | None:
        while widget is not None:
            if isinstance(widget, QAbstractItemView):
                return widget
            widget = widget.parentWidget()
        return None


class SettingsWidget(QWidget):
    def __init__(self, *args, **kwargs):
        from .qt.ui_Widget import Ui_ThemeSettings

        super().__init__(*args, **kwargs)
        self.ui = Ui_ThemeSettings()
        self.ui.setupUi(self)
        self.setWindowIcon(get_icon())

        from . import trigger

        trigger.settings_widget_created(self)
