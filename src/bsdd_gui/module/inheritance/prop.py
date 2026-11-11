from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QAction

    from bsdd_json.utils.inheritance_utils import Snapshot

    from .ui import ProjectSettingsDialog


class InheritanceProperties:
    def __init__(self):
        #: class properties / links of every class after the last check
        self.snapshot: Snapshot | None = None
        #: the whole dictionary after the last check (restored if a change breaks the rules)
        self.last_good: str | None = None
        self.timer: QTimer | None = None
        self.action: QAction | None = None
        self.dialog: ProjectSettingsDialog | None = None
