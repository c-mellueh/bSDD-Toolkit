from __future__ import annotations

from typing import Callable, Dict, Iterable, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal, QMargins, QCoreApplication
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QToolButton,
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
)
from bsdd_gui.presets.ui_presets import BaseWidget
from .qt import ui_Widget
from . import constants, trigger

if TYPE_CHECKING:
    from .ui import GraphWindow
    from ..scene_view.ui import GraphScene


class _SettingsWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("SettingsWidget")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)


class SettingsWidget(BaseWidget, ui_Widget.Ui_SettingsSidebar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        # self.setWindowFlag(Qt.WindowType.Widget,False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.scroll_area.setStyleSheet(constants.SETTINGS_STYLE_SHEET)
        self.scroll_area.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.scroll_area.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.scroll_layout.addStretch(1)
        trigger.widget_created(self)


class SettingsSidebar(QWidget):
    """Right-side overlay that hosts the EdgeTypeSettingsWidget and a
    collapsible arrow button. Intended to be parented to a QGraphicsView's
    viewport so it can overlay and match the viewport height.
    """

    # Emitted when expanded/collapsed state changes so the owner can reposition
    expandedChanged = Signal(bool)

    def __init__(
        self,
        graph_window: GraphWindow,
        allowed_edge_types: Iterable[str],
        on_toggle: Callable[[str, bool], None],
        parent: QWidget | None = None,
        expanded_width: int = 240,
    ) -> None:
        super().__init__(parent)
        trigger.widget_created(self)

        # Primary edge-type panel (kept for API methods below)
        from ..edge.ui import EdgeTypeSettingsWidget, EdgeRoutingWidget

        self._edge_types_panel = EdgeTypeSettingsWidget(allowed_edge_types, on_toggle, parent=None)
        try:
            self._edge_types_panel.edgeTypeActivated.connect(self._on_edge_type_chosen)
        except Exception:
            pass
        scene: GraphScene = self.graph_window.view.scene()
        from ..physics.ui import SettingsWidget as PhysicsWidget

        self._view_settings = PhysicsWidget(scene.physics, None)
        # Edge routing panel (straight vs right-angle)
        self._routing_settings = EdgeRoutingWidget(scene, None)
        # Node types panel
        try:
            from bsdd_gui.plugins.graph_viewer.module.graph_view_widget import constants as _const

            allowed_node_types = getattr(_const, "ALLOWED_NODE_TYPES", [])
        except Exception:
            allowed_node_types = []
        from ..node.ui import NodeTypeSettingsWidget

        self._node_types_panel = NodeTypeSettingsWidget(
            allowed_node_types,
            on_toggle=self._on_node_type_toggled,
            parent=None,
        )
        self._button_settings = ButtonWidget(None)
        self._scroll_layout.addWidget(self._node_types_panel)
        self._scroll_layout.addWidget(self._view_settings)
        self._scroll.setWidget(self._scroll_content)
        root.addWidget(self._scroll, 1)

    # Public API
    def get_flags(self) -> Dict[str, bool]:
        return self._edge_types_panel.get_flags()

    def set_flag(self, edge_type: str, value: bool) -> None:
        self._edge_types_panel.set_flag(edge_type, value)

    def _on_node_type_toggled(self, node_type: str, checked: bool) -> None:
        try:
            gw: GraphWindow = self.graph_window
            if hasattr(gw, "_on_node_type_toggled"):
                gw._on_node_type_toggled(node_type, checked)
        except Exception:
            pass
