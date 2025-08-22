from __future__ import annotations
from bsdd_gui.presets.prop_presets import WidgetHandlerProperties
from PySide6.QtWidgets import QWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


class ClassEditorProperties(WidgetHandlerProperties):
    field_getter: dict[ui.ClassEditor, dict[QWidget, callable]] = (
        dict()
    )  # getter function for widgets of Window
