from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
import re
from bsdd_gui.module.ifc_helper.data import IfcHelperData

if TYPE_CHECKING:
    from bsdd_gui.module.ifc_helper.prop import IfcHelperProperties


class IfcHelper:
    @classmethod
    def get_properties(cls) -> IfcHelperProperties:
        return bsdd_gui.IfcHelperProperties

    @classmethod
    def split_ifc_term(cls, term: str):
        """
        Splits an IFC name like 'IfcElectricMotorSYNCHRONOUS' into:
        ('IfcElectricMotor', 'SYNCHRONOUS')

        If no predefined type is present, returns (term, None).
        """
        # Find where uppercase block starts after the main CamelCase part
        match = re.match(r"^(Ifc[A-Za-z0-9]+?)([A-Z_]+)?$", term)
        if match:
            entity, predefined = match.groups()
        return entity, predefined
        return term, None

    @classmethod
    def get_classes(cls):
        return IfcHelperData.get_classes()