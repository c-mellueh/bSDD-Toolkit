from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.popups.prop import PopupsProperties


class Popups:
    @classmethod
    def get_properties(cls) -> PopupsProperties:
        return bsdd_gui.PopupsProperties
