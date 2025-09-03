from __future__ import annotations
from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget
from . import ui
from bsdd_parser import BsddClassProperty
from bsdd_gui.presets.prop_presets import FieldProperties


class ClassPropertyEditorWidgetProperties(FieldProperties):

    def __init__(self):
        super().__init__()
        self.dialog: ui.ClassPropertyCreator = None
        self.splitter_settings: ui.SplitterSettings = None
