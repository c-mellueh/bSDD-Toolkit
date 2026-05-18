from __future__ import annotations
from . import ui
from bsdd_gui.presets.prop_presets import FieldProperties


class ClassPropertyEditorWidgetProperties(FieldProperties):
    def __init__(self):
        super().__init__()
        self.dialog: ui.ClassPropertyCreator = None
        self.splitter_settings: ui.SplitterSettings = None
