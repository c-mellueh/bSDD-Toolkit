from __future__ import annotations
from typing import TYPE_CHECKING
from bsdd_gui.presets.prop_presets import ModuleHandlerProperties

if TYPE_CHECKING:
    from bsdd_parser.models import BsddDictionary


class ProjectProperties(ModuleHandlerProperties):
    def __init__(self):
        super().__init__()
        self.project_dictionary: BsddDictionary = None
        self.dialog = None
        self.plugin_save_functions = list()
