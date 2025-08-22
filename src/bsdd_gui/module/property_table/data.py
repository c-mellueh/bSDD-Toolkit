from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_parser.models import BsddClassProperty
import bsdd_parser.utils.bsdd_class_property as cp_utils


class PropertyData:
    data = {}

    @classmethod
    def get_external_property(cls, bsdd_class_property: BsddClassProperty) -> dict | None:
        uri = bsdd_class_property.PropertyUri
        if not uri:
            return None
        if uri not in cls.data:
            cls.data[uri] = cp_utils.get_external_property(bsdd_class_property)
        return cls.data[uri]

    @classmethod
    def flush_data(cls):
        cls.data = dict()
