from __future__ import annotations
from bsdd_gui.resources.icons import get_icon
from bsdd_gui.presets.ui_presets import BaseWidget
from bsdd_gui.plugins.graph_viewer.module.settings.ui import _SettingsWidget

from typing import Callable, Dict, Iterable, TYPE_CHECKING

from PySide6.QtCore import Qt, QSize, Signal, QMargins, QCoreApplication
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
    QGridLayout,
)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush

from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.constants import (
    EDGE_STYLE_MAP,
    EDGE_STYLE_DEFAULT,
    NODE_COLOR_MAP,
    NODE_SHAPE_MAP,
    EDGE_TYPE_LABEL_MAP,
    NODE_TYPE_LABEL_MAP,
)

from bsdd_gui.presets.ui_presets.toggle_switch import ToggleSwitch

class SettingsWidget(_SettingsWidget):
    """Floating settings panel for Graph physics sliders."""

    def __init__(self, physics, parent=None):
        super().__init__(parent, f=Qt.Window)
        self.physics = physics
        self._build_ui()
        self._sync_from_physics()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(QCoreApplication.translate("GraphViewSettings", "Physics Settings"))
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        # Spring length (L0)
        self.lb_l0 = QLabel(QCoreApplication.translate("GraphViewSettings", "L₀ (spring length)"))
        self.sl_l0 = QSlider(Qt.Horizontal)
        self.sl_l0.setRange(100, 750)
        self.sl_l0.setSingleStep(5)
        self.val_l0 = QLabel()
        self._add_row(layout, self.lb_l0, self.sl_l0, self.val_l0)
        self.sl_l0.valueChanged.connect(self._on_l0_changed)

        # k_spring (scaled by 100)
        self.lb_ks = QLabel(QCoreApplication.translate("GraphViewSettings", "k_spring"))
        self.sl_ks = QSlider(Qt.Horizontal)
        self.sl_ks.setRange(1, 100)  # 0.01 .. 10.00
        self.sl_ks.setSingleStep(1)
        self.val_ks = QLabel()
        self._add_row(layout, self.lb_ks, self.sl_ks, self.val_ks)
        self.sl_ks.valueChanged.connect(self._on_ks_changed)

        # k_repulsion
        self.lb_rep = QLabel(QCoreApplication.translate("GraphViewSettings", "repulsion"))
        self.sl_rep = QSlider(Qt.Horizontal)
        self.sl_rep.setRange(10, 2_500)
        self.sl_rep.setSingleStep(10)
        self.val_rep = QLabel()
        self._add_row(layout, self.lb_rep, self.sl_rep, self.val_rep)
        self.sl_rep.valueChanged.connect(self._on_rep_changed)

    def _add_row(
        self, parent_layout: QVBoxLayout, label: QLabel, slider: QSlider, value_label: QLabel
    ):
        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(slider, 1, 0, 1, 1)
        value_label.setMinimumWidth(60)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(value_label, 1, 1, 1, 1)
        parent_layout.addLayout(layout)

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
