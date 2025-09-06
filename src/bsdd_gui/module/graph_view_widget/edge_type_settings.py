from __future__ import annotations

from typing import Callable, Dict, Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
)

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

        title = QLabel("Edge Types")
        title.setObjectName("titleLabel")
        root.addWidget(title)

        for et in allowed_edge_types:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)
            lbl = QLabel(str(et))
            lbl.setToolTip(str(et))
            sw = ToggleSwitch(checked=True)
            sw.toggled.connect(self._make_handler(et))
            self._switches[et] = sw
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

