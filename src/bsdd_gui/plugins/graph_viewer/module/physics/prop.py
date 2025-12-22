from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .data import Physics
    from PySide6.QtCore import QTimer
    from . import ui

from bsdd_gui.presets.prop_presets import PluginProperties


class GraphViewerPhysicsProperties(PluginProperties):
    def __init__(self):
        super().__init__()
        self.physics: Physics = None
        self.timer: QTimer = None
        self.running: bool = True
        self.auto_paused: bool = False
        self.settings_widget: ui.SettingsWidget = None
