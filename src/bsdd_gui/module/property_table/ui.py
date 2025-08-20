from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QTableWidget

class PropertyTable(QTableWidget):
    def __init__(self, *args):
        super().__init__(*args)