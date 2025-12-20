from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .data import Physics
    from PySide6.QtCore import QTimer


class GraphViewerPhysicsProperties:
    def __init__(self):
        self.physics: Physics = None
        self.timer: QTimer = None
        self.running: bool = True
        self.auto_paused: bool = False
