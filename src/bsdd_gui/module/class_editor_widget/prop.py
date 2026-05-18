from __future__ import annotations
from bsdd_gui.presets.prop_presets import DialogProperties
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class ClassEditorWidgetProperties(DialogProperties):
    def __init__(self):
        super().__init__()
        self.old_name_value = None
