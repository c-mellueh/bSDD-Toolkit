from __future__ import annotations

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout

from bsdd_gui.presets.ui_presets import ToggleSwitch
from bsdd_gui.resources.icons import get_icon


class ProjectSettingsDialog(QDialog):
    """Settings stored next to the project file (apply to everyone working on it)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(get_icon())
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)

        self.label_info = QLabel(self)
        self.label_info.setWordWrap(True)
        layout.addWidget(self.label_info)

        row = QHBoxLayout()
        self.toggle_strict = ToggleSwitch(self)
        self.label_strict = QLabel(self)
        self.label_strict.setBuddy(self.toggle_strict)
        row.addWidget(self.toggle_strict)
        row.addWidget(self.label_strict, 1)
        layout.addLayout(row)

        self.label_description = QLabel(self)
        self.label_description.setWordWrap(True)
        layout.addWidget(self.label_description)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=self)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.retranslate_ui()

    def retranslate_ui(self):
        tr = QCoreApplication.translate
        self.setWindowTitle(tr("Inheritance", "Project Settings"))
        self.label_info.setText(
            tr(
                "Inheritance",
                "These settings are saved in a file next to the project file "
                "(<name>.bsdd-toolkit.json) and apply to everyone working on it.",
            )
        )
        self.label_strict.setText(tr("Inheritance", "Strict inheritance"))
        self.label_description.setText(
            tr(
                "Inheritance",
                "Every child class has all class properties and predefined property sets of its "
                "parent class. In child classes only the values of inherited class properties can "
                "be changed (allowed values, unit, required …); they cannot be removed or moved to "
                "another property set. Changes in a parent class are passed on to all its child "
                "classes; values a child class changed itself are kept.",
            )
        )
