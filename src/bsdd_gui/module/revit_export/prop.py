from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties, FieldProperties
from PySide6.QtCore import QThread, QObject


class RevitExportProperties(ActionsProperties, FieldProperties):
    def __init__(self):
        super().__init__()
        self.build_worker: QObject = None
        self.build_thread: QThread = None
        self.text_or_label = "Text"