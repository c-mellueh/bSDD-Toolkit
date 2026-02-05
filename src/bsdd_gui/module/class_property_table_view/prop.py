from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui
    from bsdd_json.type_hints import CLASS_TYPE
from bsdd_gui.presets.prop_presets import ViewProperties


class ClassPropertyTableViewProperties(ViewProperties):
    def __init__(self):
        super().__init__()
        self.allowed_class_types: list[CLASS_TYPE] = list()
