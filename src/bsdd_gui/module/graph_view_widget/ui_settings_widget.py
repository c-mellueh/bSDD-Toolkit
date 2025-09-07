from __future__ import annotations

from typing import Callable, Dict, Iterable, TYPE_CHECKING

from PySide6.QtCore import Qt, QSize, Signal, QMargins
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QToolButton,
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
    QSlider,
)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush

from bsdd_gui.module.graph_view_widget.constants import (
    EDGE_STYLE_MAP,
    EDGE_STYLE_DEFAULT,
    NODE_COLOR_MAP,
    NODE_SHAPE_MAP,
)

from bsdd_gui.presets.ui_presets.toggle_switch import ToggleSwitch
from .qt import ui_Buttons

if TYPE_CHECKING:
    from .ui import GraphWindow
    from .view_ui import GraphScene

SETTINGS_STYLE_SHEET = """
            QScrollArea { background: transparent; }
            QWidget#qt_scrollarea_viewport { background: transparent; }
            QWidget#ScrollContent { background: transparent;}
            QFrame#SettingsWidget {
                background: rgba(30, 30, 35, 200);
                border: 1px solid rgba(90, 90, 120, 140);
                border-radius: 6px;
            }
            QLabel#titleLabel {
                color: #ddd;
                font-weight: bold;
            }
            QLabel {
                color: #ddd;
            }
            """


class _SettingsWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("SettingsWidget")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)


class ButtonWidget(_SettingsWidget, ui_Buttons.Ui_Form):
    """Floating settings panel for Graph physics sliders."""

    def __init__(self, parent=None):
        super().__init__(parent, f=Qt.Window)
        self.setupUi(self)


class PhysicsWidget(_SettingsWidget):
    """Floating settings panel for Graph physics sliders."""

    def __init__(self, physics, parent=None):
        super().__init__(parent, f=Qt.Window)
        self.physics = physics
        self._build_ui()
        self._sync_from_physics()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Physics Settings")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        # Spring length (L0)
        self.lb_l0 = QLabel("L₀ (spring length)")
        self.sl_l0 = QSlider(Qt.Horizontal)
        self.sl_l0.setRange(50, 2000)
        self.sl_l0.setSingleStep(10)
        self.val_l0 = QLabel()
        self._add_row(layout, self.lb_l0, self.sl_l0, self.val_l0)
        self.sl_l0.valueChanged.connect(self._on_l0_changed)

        # k_spring (scaled by 100)
        self.lb_ks = QLabel("k_spring")
        self.sl_ks = QSlider(Qt.Horizontal)
        self.sl_ks.setRange(1, 100)  # 0.01 .. 10.00
        self.sl_ks.setSingleStep(1)
        self.val_ks = QLabel()
        self._add_row(layout, self.lb_ks, self.sl_ks, self.val_ks)
        self.sl_ks.valueChanged.connect(self._on_ks_changed)

        # k_repulsion
        self.lb_rep = QLabel("repulsion")
        self.sl_rep = QSlider(Qt.Horizontal)
        self.sl_rep.setRange(10, 10000)
        self.sl_rep.setSingleStep(10)
        self.val_rep = QLabel()
        self._add_row(layout, self.lb_rep, self.sl_rep, self.val_rep)
        self.sl_rep.valueChanged.connect(self._on_rep_changed)

    def _add_row(
        self, parent_layout: QVBoxLayout, label: QLabel, slider: QSlider, value_label: QLabel
    ):
        row = QHBoxLayout()
        row.addWidget(label)
        row.addWidget(slider, 1)
        value_label.setMinimumWidth(60)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(value_label)
        parent_layout.addLayout(row)

    def _sync_from_physics(self):
        # Avoid feedback loops by blocking signals while setting initial values
        self.sl_l0.blockSignals(True)
        self.sl_ks.blockSignals(True)
        self.sl_rep.blockSignals(True)
        try:
            self.sl_l0.setValue(int(self.physics.spring_length))
            self.sl_ks.setValue(int(self.physics.k_spring * 100))
            self.sl_rep.setValue(int(self.physics.k_repulsion))
        finally:
            self.sl_l0.blockSignals(False)
            self.sl_ks.blockSignals(False)
            self.sl_rep.blockSignals(False)
        self._update_value_labels()

    def _update_value_labels(self):
        self.val_l0.setText(f"{int(self.sl_l0.value())}")
        self.val_ks.setText(f"{self.sl_ks.value() / 100.0:.2f}")
        self.val_rep.setText(f"{int(self.sl_rep.value())}")

    # Handlers
    def _on_l0_changed(self, v: int):
        self.physics.spring_length = float(v)
        self._update_value_labels()

    def _on_ks_changed(self, v: int):
        self.physics.k_spring = float(v) / 1000.0
        self._update_value_labels()

    def _on_rep_changed(self, v: int):
        self.physics.k_repulsion = float(v)
        self._update_value_labels()


class EdgeTypeSettingsWidget(_SettingsWidget):
    """
    Compact, floating panel with ToggleSwitches to control visibility
    of individual edge types.

    Parent should typically be the QGraphicsView viewport, so it overlays
    the scene and can be anchored in the bottom-right corner by the owner.
    """

    # Emitted when a legend icon is double-clicked to choose creation type
    edgeTypeActivated = Signal(str)

    def __init__(
        self,
        allowed_edge_types: Iterable[str],
        on_toggle: Callable[[str, bool], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_toggle = on_toggle
        self._switches: Dict[str, ToggleSwitch] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)
        # Ensure it can stretch vertically when hosted in a sidebar
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        title = QLabel("Edge Types")
        title.setObjectName("titleLabel")
        root.addWidget(title)

        for et in allowed_edge_types:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)
            # Legend icon
            icon = _EdgeLegendIcon(str(et))
            try:
                icon.edgeTypeActivated.connect(
                    lambda etype=str(et): self.edgeTypeActivated.emit(etype)
                )
            except Exception:
                pass
            lbl = QLabel(str(et))
            lbl.setToolTip(str(et))
            sw = ToggleSwitch(checked=True)
            sw.toggled.connect(self._make_handler(et))
            self._switches[et] = sw
            row.addWidget(icon, 0)
            row.addWidget(lbl, 1)
            row.addWidget(sw, 0, alignment=Qt.AlignRight)
            root.addLayout(row)

    def _make_handler(self, edge_type: str):
        def _handler(checked: bool):
            if callable(self._on_toggle):
                self._on_toggle(edge_type, checked)

        return _handler

    def get_flags(self) -> Dict[str, bool]:
        return {et: sw.isChecked() for et, sw in self._switches.items()}

    def set_flag(self, edge_type: str, value: bool) -> None:
        sw = self._switches.get(edge_type)
        if sw is not None:
            sw.blockSignals(True)
            try:
                sw.setChecked(bool(value))
            finally:
                sw.blockSignals(False)


class _EdgeLegendIcon(QWidget):
    """Small widget that draws a sample line using the configured
    color/width/style for a given edge type.
    """

    def __init__(self, edge_type: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._edge_type = edge_type
        self.setFixedWidth(28)
        self.setFixedHeight(14)
        # Signal for activation (double-click selection)
        try:
            from PySide6.QtCore import Signal as _Signal  # type: ignore
        except Exception:
            _Signal = None
        # Dynamically attach a signal attribute if possible
        # But better: declare on class; see above in EdgeTypeSettingsWidget connection

    # Custom signal declared on class via Qt meta-object (added above)
    edgeTypeActivated = Signal(str)

    def sizeHint(self):
        return QSize(28, 14)

    def _pen_for_edge(self) -> QPen:
        cfg = EDGE_STYLE_MAP.get(self._edge_type, EDGE_STYLE_DEFAULT)
        color = cfg.get("color", EDGE_STYLE_DEFAULT["color"])  # type: ignore[index]
        width = float(cfg.get("width", EDGE_STYLE_DEFAULT["width"]))
        style = cfg.get("style", EDGE_STYLE_DEFAULT["style"])  # type: ignore[index]
        pen = QPen(color if isinstance(color, QColor) else QColor(130, 130, 150))
        pen.setCosmetic(True)
        pen.setWidthF(width)
        try:
            pen.setStyle(style)  # type: ignore[arg-type]
        except Exception:
            pass
        return pen

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        y = rect.center().y()
        x1 = rect.left() + 2
        x2 = rect.right() - 2
        pen = self._pen_for_edge()
        p.setPen(pen)
        p.drawLine(int(x1), int(y), int(x2), int(y))

    def mouseDoubleClickEvent(self, event):
        try:
            self.edgeTypeActivated.emit(self._edge_type)
        except Exception:
            pass
        super().mouseDoubleClickEvent(event)


class NodeTypeSettingsWidget(_SettingsWidget):
    """Panel mirroring EdgeTypeSettingsWidget, but for node types."""

    def __init__(
        self,
        allowed_node_types: Iterable[str],
        on_toggle: Callable[[str, bool], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_toggle = on_toggle
        self._switches: Dict[str, ToggleSwitch] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        title = QLabel("Node Types")
        title.setObjectName("titleLabel")
        root.addWidget(title)

        for nt in allowed_node_types:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)
            icon = _NodeLegendIcon(str(nt))
            lbl = QLabel(str(nt))
            lbl.setToolTip(str(nt))
            sw = ToggleSwitch(checked=True)
            sw.toggled.connect(self._make_handler(nt))
            self._switches[nt] = sw
            row.addWidget(icon, 0)
            row.addWidget(lbl, 1)
            row.addWidget(sw, 0, alignment=Qt.AlignRight)
            root.addLayout(row)

    def _make_handler(self, node_type: str):
        def _handler(checked: bool):
            if callable(self._on_toggle):
                self._on_toggle(node_type, checked)

        return _handler

    def get_flags(self) -> Dict[str, bool]:
        return {nt: sw.isChecked() for nt, sw in self._switches.items()}

    def set_flag(self, node_type: str, value: bool) -> None:
        sw = self._switches.get(node_type)
        if sw is not None:
            sw.blockSignals(True)
            try:
                sw.setChecked(bool(value))
            finally:
                sw.blockSignals(False)


class _NodeLegendIcon(QWidget):
    """Small icon preview of node color/shape."""

    def __init__(self, node_type: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._node_type = node_type
        self.setFixedWidth(28)
        self.setFixedHeight(14)

    def sizeHint(self):
        return QSize(28, 14)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect().adjusted(2, 2, -2, -2)
        color = NODE_COLOR_MAP.get(self._node_type, QColor(130, 130, 150))
        shape = NODE_SHAPE_MAP.get(self._node_type, "rect")
        pen = QPen(color)
        pen.setCosmetic(True)
        p.setPen(pen)
        brush = QBrush(Qt.BrushStyle.SolidPattern)
        brush.setColor(color)
        p.setBrush(brush)
        if shape == "ellipse":
            p.drawEllipse(rect)
        elif shape == "roundrect":
            p.drawRoundedRect(rect, 4, 4)
        else:
            p.drawRect(rect)


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
        self.graph_window = graph_window
        self._expanded_width = max(160, int(expanded_width))
        self._expanded = True

        self.setObjectName("SettingsSidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        # Ensure the overlay itself is fully transparent
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(
            """
            QWidget#SettingsSidebar {
                background: transparent;
            }
            """
        )

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._button_layout = QVBoxLayout()
        self._btn_layout_widget = QWidget()
        self._btn_layout_widget.setLayout(self._button_layout)
        self._btn_layout_widget.setContentsMargins(QMargins(0.0, 0.0, 0.0, 0.0))
        self._button_layout.setContentsMargins(QMargins(0.0, 0.0, 0.0, 0.0))

        # Collapse/Expand handle
        self._btn = QToolButton(self)
        self._btn.setArrowType(Qt.ArrowType.LeftArrow)
        self._btn.setCheckable(True)
        self._btn.setChecked(True)
        self._btn.clicked.connect(self._on_toggle_clicked)
        self._btn.setToolTip("Show/Hide edge types")
        self._btn.setFixedWidth(18)
        self._btn.setFixedHeight(18)

        self._btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self._button_layout.addWidget(self._btn)
        self.spacer_item = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self._button_layout.addItem(self.spacer_item)
        root.addWidget(self._btn_layout_widget)
        # Scroll area hosting a vertical stack of panels
        self._scroll = QScrollArea(self)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setWidgetResizable(True)
        # Make scroll area and its viewport fully transparent
        try:
            self._scroll.setAttribute(Qt.WA_TranslucentBackground, True)
            self._scroll.viewport().setAttribute(Qt.WA_TranslucentBackground, True)
        except Exception:
            pass
        self._scroll.setStyleSheet(SETTINGS_STYLE_SHEET)

        self._scroll_content = QWidget(self._scroll)
        self._scroll_content.setObjectName("ScrollContent")
        self._scroll_content.setAttribute(Qt.WA_StyledBackground, True)
        self._scroll_layout = QVBoxLayout(self._scroll_content)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(8)

        # Primary edge-type panel (kept for API methods below)
        self._edge_types_panel = EdgeTypeSettingsWidget(allowed_edge_types, on_toggle, parent=None)
        try:
            self._edge_types_panel.edgeTypeActivated.connect(self._on_edge_type_chosen)
        except Exception:
            pass
        scene: GraphScene = self.graph_window.view.scene()
        self._view_settings = PhysicsWidget(scene.physics, None)
        # Node types panel
        try:
            from bsdd_gui.module.graph_view_widget import constants as _const

            allowed_node_types = getattr(_const, "ALLOWED_NODE_TYPES", [])
        except Exception:
            allowed_node_types = []
        self._node_types_panel = NodeTypeSettingsWidget(
            allowed_node_types,
            on_toggle=self._on_node_type_toggled,
            parent=None,
        )
        self._button_settings = ButtonWidget(None)
        self._scroll_layout.addWidget(self._view_settings)
        self._scroll_layout.addWidget(self._node_types_panel)
        self._scroll_layout.addWidget(self._edge_types_panel)
        self._scroll_layout.addWidget(self._button_settings)

        self._scroll_layout.addStretch(1)

        self._scroll.setWidget(self._scroll_content)
        root.addWidget(self._scroll, 1)

        self._apply_expanded_state()

    # Public API
    def get_flags(self) -> Dict[str, bool]:
        return self._edge_types_panel.get_flags()

    def set_flag(self, edge_type: str, value: bool) -> None:
        self._edge_types_panel.set_flag(edge_type, value)

    def add_content_widget(self, widget: QWidget) -> None:
        """Append an arbitrary widget below the edge-type panel inside the
        scroll area. Useful for adding legends or extra controls.
        """
        # Insert before the final stretch, so it stays at the bottom
        # but above the stretchable spacer
        stretch_index = self._scroll_layout.count() - 1
        if stretch_index < 0:
            stretch_index = 0
        self._scroll_layout.insertWidget(stretch_index, widget)

    def set_expanded(self, expanded: bool) -> None:
        if self._expanded == bool(expanded):
            return
        self._expanded = bool(expanded)
        self._btn.setChecked(self._expanded)
        self._apply_expanded_state()
        # Notify owner (e.g., GraphWindow) to re-anchor on the right edge
        try:
            self.expandedChanged.emit(self._expanded)
        except Exception:
            pass

    def toggle(self) -> None:
        self.set_expanded(not self._expanded)

    def position_and_resize(
        self, viewport_width: int, viewport_height: int, margin: int = 0
    ) -> None:
        """Anchor to top-right of the given viewport size and stretch to full height."""
        width = self._btn.width() + (self._expanded_width if self._expanded else 0)
        x = max(0, viewport_width - width - margin)
        y = margin
        h = max(0, viewport_height - 2 * margin)
        self.setGeometry(x, y, width, h)

    # Internal
    def _apply_expanded_state(self) -> None:
        self._scroll.setVisible(self._expanded)
        self._btn.setArrowType(
            Qt.ArrowType.LeftArrow if not self._expanded else Qt.ArrowType.RightArrow
        )
        self.updateGeometry()

    def _on_toggle_clicked(self):
        self.set_expanded(self._btn.isChecked())

    def _on_edge_type_chosen(self, edge_type: str) -> None:
        try:
            # Toggle selection if same type chosen again
            gw: GraphWindow = self.graph_window
            if hasattr(gw, "get_active_edge_type") and callable(gw.get_active_edge_type):
                cur = gw.get_active_edge_type()
                if cur == edge_type:
                    edge_type = None  # deselect
            if hasattr(gw, "set_active_edge_type") and callable(gw.set_active_edge_type):
                gw.set_active_edge_type(edge_type)
        except Exception:
            pass

    def _on_node_type_toggled(self, node_type: str, checked: bool) -> None:
        try:
            gw: GraphWindow = self.graph_window
            if hasattr(gw, "_on_node_type_toggled"):
                gw._on_node_type_toggled(node_type, checked)
        except Exception:
            pass
