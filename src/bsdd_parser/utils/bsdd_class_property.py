from __future__ import annotations
from typing import TYPE_CHECKING

from bsdd_parser import BsddClassProperty, BsddProperty, BsddDictionary
import bsdd
from bsdd import Client
from . import bsdd_dictionary


class Cache:
    data = {}

    @classmethod
    def get_external_property(
        cls, bsdd_class_property: BsddClassProperty, client: bsdd.Client | None
    ) -> BsddClassProperty | None:
        from bsdd_parser.utils import bsdd_class_property as cp_utils

        def _make_request():
            if not cp_utils.is_external_ref(bsdd_class_property):
                return dict()
            c = Client() if client is None else client
            property_uri = bsdd_class_property.PropertyUri
            result = c.get_property(property_uri)

            if "statusCode" in result and result["statusCode"] == 400:
                return None
            return result

        uri = bsdd_class_property.PropertyUri
        if not uri:
            return None
        if uri not in cls.data:
            result = _make_request()
            if result is not None:
                result = BsddProperty.model_validate(result)
            cls.data[uri] = result
        return cls.data[uri]

    @classmethod
    def flush_data(cls):
        cls.data = dict()


def get_data_type(class_property: BsddClassProperty):

    if not is_external_ref(class_property):
        prop = get_internal_property(class_property)
        return prop.DataType


def is_external_ref(class_property: BsddClassProperty) -> bool:
    if class_property.PropertyUri and class_property.PropertyCode:
        raise ValueError(
            f"PropertyCode '{class_property.PropertyCode}'and PropertyUri '{class_property.PropertyUri}' are filled! only one is allowed!"
        )
    elif class_property.PropertyUri:
        return True
    else:
        return False


def get_internal_property(
    class_property: BsddClassProperty, bsdd_dictionary=None
) -> BsddProperty | None:
    if is_external_ref(class_property):
        return None
    bsdd_class = class_property.parent()
    if bsdd_dictionary is None and bsdd_class is None:
        return None
    if bsdd_dictionary is None:
        bsdd_dictionary = bsdd_class.parent()
    for p in bsdd_dictionary.Properties:
        if p.Code == class_property.PropertyCode:
            return p


def get_external_property(class_property: BsddClassProperty, client=None) -> BsddProperty | None:
    return Cache.get_external_property(class_property, client)


def get_all_property_codes(bsdd_dictionary: BsddDictionary) -> dict[str, BsddProperty]:
    return {p.Code: p for p in bsdd_dictionary.Properties}


def get_datatype(class_property: BsddClassProperty):
    if is_external_ref(class_property):
        bsdd_property = get_external_property(class_property)
    else:
        bsdd_property = get_internal_property(class_property)

    if bsdd_property is None:
        return ""
    return bsdd_property.DataType or "String"


def get_units(class_property: BsddClassProperty):
    if is_external_ref(class_property):
        bsdd_property = get_external_property(class_property)
    else:
        bsdd_property = get_internal_property(class_property)

    if bsdd_property is None:
        return []
    return bsdd_property.Units or []
