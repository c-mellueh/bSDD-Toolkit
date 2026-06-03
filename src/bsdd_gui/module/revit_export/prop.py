from __future__ import annotations
from bsdd_gui.presets.prop_presets import ActionsProperties, FieldProperties
from PySide6.QtCore import QThread, QObject
from typing import Literal

class RevitExportProperties(ActionsProperties, FieldProperties):
    def __init__(self):
        super().__init__()
        self.build_worker: QObject = None
        self.build_thread: QThread = None
        self.text_or_label:Literal["Text","Label"] = "Text"
        self.mode:Literal["CustomPropertySet", "SharedParameters"] = "CustomPropertySet"