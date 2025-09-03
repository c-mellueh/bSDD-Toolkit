from __future__ import annotations
from bsdd_gui.presets.prop_presets import WidgetProperties
from PySide6.QtWidgets import QWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


class ClassEditorWidgetProperties(WidgetProperties):

    def __init__(self):
        super().__init__()
