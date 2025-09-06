from __future__ import annotations

from typing import Callable, Dict, Iterable

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QToolButton,
    QSizePolicy,
    QScrollArea,
)
from PySide6.QtGui import QPainter, QPen, QColor

from bsdd_gui.module.graph_view_widget.constants import EDGE_STYLE_MAP, EDGE_STYLE_DEFAULT

from bsdd_gui.presets.ui_presets.toggle_switch import ToggleSwitch


class EdgeTypeSettingsWidget(QFrame):
    """
    Compact, floating panel with ToggleSwitches to control visibility
    of individual edge types.

    Parent should typically be the QGraphicsView viewport, so it overlays
    the scene and can be anchored in the bottom-right corner by the owner.
    """

    def __init__(
        self,
        allowed_edge_types: Iterable[str],
        on_toggle: Callable[[str, bool], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("EdgeTypeSettingsWidget")
        self._on_toggle = on_toggle
        self._switches: Dict[str, ToggleSwitch] = {}
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet(
            """
            QFrame#EdgeTypeSettingsWidget {
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
        )

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
        self.setFixedWidth(30)
        self.setFixedHeight(14)

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


class EdgeSettingsSidebar(QWidget):
    """Right-side overlay that hosts the EdgeTypeSettingsWidget and a
    collapsible arrow button. Intended to be parented to a QGraphicsView's
    viewport so it can overlay and match the viewport height.
    """

    # Emitted when expanded/collapsed state changes so the owner can reposition
    expandedChanged = Signal(bool)

    def __init__(
        self,
        allowed_edge_types: Iterable[str],
        on_toggle: Callable[[str, bool], None],
        parent: QWidget | None = None,
        expanded_width: int = 240,
    ) -> None:
        super().__init__(parent)
        self._expanded_width = max(160, int(expanded_width))
        self._expanded = True

        self.setObjectName("EdgeSettingsSidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            """
            QWidget#EdgeSettingsSidebar {
                background: transparent;
            }
            """
        )

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Collapse/Expand handle
        self._btn = QToolButton(self)
        self._btn.setArrowType(Qt.RightArrow)
        self._btn.setCheckable(True)
        self._btn.setChecked(True)
        self._btn.clicked.connect(self._on_toggle_clicked)
        self._btn.setToolTip("Show/Hide edge types")
        self._btn.setFixedWidth(18)
        self._btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        root.addWidget(self._btn)

        # Scroll area hosting the settings panel
        self._scroll = QScrollArea(self)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setWidgetResizable(True)
        self._content = EdgeTypeSettingsWidget(allowed_edge_types, on_toggle, parent=None)
        self._scroll.setWidget(self._content)
        root.addWidget(self._scroll, 1)

        self._apply_expanded_state()

    # Public API
    def get_flags(self) -> Dict[str, bool]:
        return self._content.get_flags()

    def set_flag(self, edge_type: str, value: bool) -> None:
        self._content.set_flag(edge_type, value)

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

    def position_and_resize(self, viewport_width: int, viewport_height: int, margin: int = 0) -> None:
        """Anchor to top-right of the given viewport size and stretch to full height."""
        width = self._btn.width() + (self._expanded_width if self._expanded else 0)
        x = max(0, viewport_width - width - margin)
        y = margin
        h = max(0, viewport_height - 2 * margin)
        self.setGeometry(x, y, width, h)

    # Internal
    def _apply_expanded_state(self) -> None:
        self._scroll.setVisible(self._expanded)
        self._btn.setArrowType(Qt.RightArrow if not self._expanded else Qt.LeftArrow)
        self.updateGeometry()

    def _on_toggle_clicked(self):
        self.set_expanded(self._btn.isChecked())
