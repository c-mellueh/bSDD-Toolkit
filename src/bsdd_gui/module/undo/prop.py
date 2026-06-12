from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QAction


class UndoProperties:
    def __init__(self):
        self.undo_stack: list[str] = []
        self.redo_stack: list[str] = []
        self.last_state: str | None = None
        self.is_restoring: bool = False
        self.debounce_timer: QTimer | None = None
        self.actions: dict[str, QAction] = {}
