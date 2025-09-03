from __future__ import annotations
from bsdd_gui.presets.prop_presets import FieldProperties
from . import ui


class PropertyEditorWidgetProperties(FieldProperties):
    def __init__(self):
        super().__init__()
        self.dialog: ui.PropertyCreator = None
        self.plugin_widget_list = list()
