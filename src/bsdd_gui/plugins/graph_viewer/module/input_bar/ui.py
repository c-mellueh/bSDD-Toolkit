from __future__ import annotations
from bsdd_gui.presets.ui_presets import BaseWidget
from PySide6.QtWidgets import QHBoxLayout, QLineEdit
from . import constants, trigger


class InputBar(BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("nodeInputBar")
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(12, 12, 12, 6)
        self.layout().setSpacing(8)

        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(self.tr("Add node by Code or URI and press Enter"))
        self.line_edit.setClearButtonEnabled(True)
        self.line_edit.setStyleSheet(constants.STYLE_SHEET)
        self.layout().addWidget(self.line_edit)
        trigger.widget_created(self)
