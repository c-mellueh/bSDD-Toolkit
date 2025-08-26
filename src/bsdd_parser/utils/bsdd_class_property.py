from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_parser import BsddClassProperty, BsddProperty, BsddDictionary
import bsdd
from bsdd import Client
from . import bsdd_dictionary


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


def get_internal_property(class_property: BsddClassProperty) -> BsddProperty | None:
    if is_external_ref(class_property):
        return None
    bsdd_class = class_property._parent_ref()
    bsdd_dictionary = bsdd_class._parent_ref()
    for p in bsdd_dictionary.Properties:
        if p.Code == class_property.PropertyCode:
            return p


def get_external_property(class_property: BsddClassProperty, client=None) -> dict | None:
    if not is_external_ref(class_property):
        return dict()
    client = Client() if client is None else client
    property_uri = class_property.PropertyUri
    bsdd_uri = bsdd_dictionary.get_dictionary_path_from_uri(property_uri)
    result = client.get_property(property_uri)

    if "statusCode" in result and result["statusCode"] == 400:
        return None
    return result


def get_all_property_codes(bsdd_dictionary: BsddDictionary) -> dict[str, BsddProperty]:
    return {p.Code: p for p in bsdd_dictionary.Properties}
