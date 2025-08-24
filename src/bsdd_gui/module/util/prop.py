from __future__ import annotations

from typing import TypedDict

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu


class MenuDict(TypedDict):
    submenu: list[MenuDict]
    actions: list[QAction]
    menu: QMenu
    name: str


class UtilProperties:
    shortcut = list()
