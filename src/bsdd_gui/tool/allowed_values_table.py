from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Qt, Signal
import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.allowed_values_table.prop import AllowedValuesTableProperties

from bsdd_gui.presets.tool_presets import ColumnHandler, ViewHandler, ViewSignaller


class Signaller(ViewSignaller):
    pass


class AllowedValuesTable(ColumnHandler, ViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> AllowedValuesTableProperties:
        return bsdd_gui.AllowedValuesTableProperties
