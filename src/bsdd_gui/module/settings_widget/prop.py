from __future__ import annotations

from typing import Callable, TYPE_CHECKING, Type

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBox, QWidget

if TYPE_CHECKING:
    from . import ui


class SettingsWidgetProperties:
    page_dict: dict[str, list[Type[QWidget]]] = {}  # dict[pageName,list[Widget]]
    tab_widget_dict: dict[str, tuple[QToolBox, dict[str, QWidget]]] = {}
    accept_functions: list[Callable] = []
    widget: ui.Dialog = None
    actions: dict[str, QAction] = {}
