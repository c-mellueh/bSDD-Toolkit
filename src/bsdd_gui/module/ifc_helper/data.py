from __future__ import annotations
from typing import TYPE_CHECKING
import bsdd

if TYPE_CHECKING:
    from bsdd_parser.models import BsddClassProperty
import bsdd_parser.utils.bsdd_class_property as cp_utils
from .constants import IFC_URI


class IfcHelperData:
    data = {}

    @classmethod
    def load(cls):
        cls.load_ifc_classes()

    @classmethod
    def flush_data(cls):
        cls.data = dict()

    @classmethod
    def get_classes(cls):
        if not "ifc_classes" in cls.data:
            cls.data["ifc_classes"] = bsdd.Client().get_classes(IFC_URI)
        return cls.data["ifc_classes"]
