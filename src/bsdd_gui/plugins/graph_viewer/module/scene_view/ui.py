from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from . import trigger
from .qt import ui_Buttons
from bsdd_gui.plugins.graph_viewer.module.settings.ui import _SettingsWidget


class GraphView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)

    def scene(self) -> GraphScene:
        return super().scene()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            factor = 1.25 if event.angleDelta().y() > 0 else 0.8
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event):
        # Keep overlays anchored in viewport coordinates
        trigger.resize_event(event)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        # Log scene coordinates for every mouse click
        if trigger.mouse_press_event(event):
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if trigger.mouse_release_event(event):
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if trigger.mouse_move_event(event):
            super().mouseMoveEvent(event)

    # ---- Drag & Drop integration ----

    def dragEnterEvent(self, event):
        if trigger.drag_enter_event(event):
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if trigger.drag_move_event(event):
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        trigger.drop_event(event)

    def mouseDoubleClickEvent(self, event):
        # On double-click, emit a tool-level signal when a Node is hit
        if trigger.double_click_event(event):
            super().mouseDoubleClickEvent(event)


class GraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()


class ButtonWidget(_SettingsWidget, ui_Buttons.Ui_Form):
    """Floating settings panel for Graph physics sliders."""

    def __init__(self, parent=None):
        super().__init__(parent, f=Qt.Window)
        self.setupUi(self)
