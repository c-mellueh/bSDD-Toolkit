from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)


class GraphSettingsWidget(QWidget):
    """Floating settings panel for Graph physics sliders."""

    def __init__(self, physics, parent=None):
        super().__init__(parent, f=Qt.Window)
        self.setWindowTitle("Graph Settings")
        self.physics = physics

        self._build_ui()
        self._sync_from_physics()

    def _build_ui(self):
        layout = QVBoxLayout(self)

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

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        btn_row.addWidget(self.btn_close)
        layout.addLayout(btn_row)

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
