from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.ifc_helper.prop import IfcHelperProperties


class IfcHelper:
    @classmethod
    def get_properties(cls) -> IfcHelperProperties:
        return bsdd_gui.IfcHelperProperties
