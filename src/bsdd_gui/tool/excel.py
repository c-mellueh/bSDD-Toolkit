
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.excel.prop import ExcelProperties


class Excel:
    @classmethod
    def get_properties(cls) -> ExcelProperties:
        return bsdd_gui.ExcelProperties
