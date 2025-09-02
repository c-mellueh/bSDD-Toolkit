from __future__ import annotations
from typing import TYPE_CHECKING
import bsdd

if TYPE_CHECKING:
    from bsdd_parser.models import BsddClassProperty
import bsdd_parser.utils.bsdd_class_property as cp_utils
from .constants import IFC_URI
from requests.exceptions import ReadTimeout
from bsdd_gui.resources.data import get_ifc_classes as ifc_backup


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
        if not "ifc_classes" in cls.bsdd_data:
            try:
                c = bsdd.Client()
                c1 = c.get_classes(IFC_URI, use_nested_classes=False, limit=1000)["classes"]
                c2 = c.get_classes(IFC_URI, use_nested_classes=False, offset=1000)["classes"]
                cls.data["ifc_classes"] = c1 + c2
            except ReadTimeout:
                cls.data["ifc_classes"] = ifc_backup()

        return cls.data["ifc_classes"]
