from __future__ import annotations
from typing import TYPE_CHECKING
from bsdd_gui.presets.prop_presets import ActionsProperties

if TYPE_CHECKING:
    from bsdd_json.models import BsddDictionary
    from PySide6.QtWidgets import QMenu


class ProjectProperties(ActionsProperties):
    def __init__(self):
        super().__init__()
        self.project_dictionary: BsddDictionary = None
        self.dialog = None
        self.plugin_save_functions = list()
        self.offline_mode = False
        self.last_save: BsddDictionary = None
        self.recent_menu: QMenu | None = None
