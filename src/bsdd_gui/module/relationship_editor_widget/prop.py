from __future__ import annotations
from bsdd_gui.presets.prop_presets import ViewProperties, FieldProperties
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


class RelationshipEditorWidgetProperties(ViewProperties, FieldProperties):
    def __init__(self):
        super().__init__()
        self.settings_widget: ui.SettingsWidget | None = None
