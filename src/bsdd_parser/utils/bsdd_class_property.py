from __future__ import annotations
from typing import TYPE_CHECKING

from bsdd_parser import BsddClassProperty, BsddProperty, BsddDictionary, BsddClass
import bsdd
from bsdd import Client
from . import bsdd_dictionary as dict_util


class Cache:
    data = {}

    @classmethod
    def get_external_property(
        cls, property_uri: str, client: bsdd.Client | None
    ) -> BsddClassProperty | None:
        from bsdd_parser.utils import bsdd_class_property as cp_utils

        def _make_request():
            if not dict_util.is_uri(property_uri):
                return dict()
            c = Client() if client is None else client
            result = c.get_property(property_uri)

            if "statusCode" in result and result["statusCode"] == 400:
                return None
            return result

        if not property_uri:
            return None
        if property_uri not in cls.data:
            result = _make_request()
            if result is not None:
                result = BsddProperty.model_validate(result)
            cls.data[property_uri] = result
        return cls.data[property_uri]

    @classmethod
    def flush_data(cls):
        cls.data = dict()


def get_data_type(class_property: BsddClassProperty):

    if not is_external_ref(class_property):
        prop = get_internal_property(class_property)
        if not prop:
            return None
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
    return Cache.get_external_property(class_property.PropertyUri, client)


def get_property_code_dict(bsdd_dictionary: BsddDictionary) -> dict[str, BsddProperty]:
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


def get_classes_with_bsdd_property(property_code: str, bsdd_dictionary: BsddDictionary):
    is_external = True if property_code.startswith("https://") else False

    def _has_prop(c: BsddClass):
        for p in c.ClassProperties:
            if is_external and p.PropertyUri == property_code:
                return True
            elif not is_external and p.PropertyCode == property_code:
                return True
        return False

    return list(filter(_has_prop, bsdd_dictionary.Classes))


def get_property_by_code(code: str, bsdd_dictionary: BsddDictionary) -> BsddProperty | None:
    if dict_util.is_uri(code):
        prop = Cache.get_external_property(code)
    else:
        prop = get_property_code_dict(bsdd_dictionary).get(code)
    return prop


def update_relations_to_new_uri(bsdd_proeprty: BsddProperty, bsdd_dictionary: BsddDictionary):
    namespace = f"{bsdd_dictionary.OrganizationCode}/{bsdd_dictionary.DictionaryCode}"
    version = bsdd_dictionary.DictionaryVersion

    for relationship in bsdd_proeprty.PropertyRelations:
        old_uri = dict_util.parse_bsdd_url(relationship.RelatedPropertyUri)
        new_uri = dict(old_uri)
        new_uri["namespace"] = namespace
        new_uri["version"] = version
        if old_uri != new_uri:
            relationship.RelatedPropertyUri = dict_util.build_bsdd_url(new_uri)


def build_bsdd_uri(bsdd_property: BsddProperty, bsdd_dictionary: BsddDictionary):
    data = {
        "namespace": [bsdd_dictionary.OrganizationCode, bsdd_dictionary.DictionaryCode],
        "version": bsdd_dictionary.DictionaryVersion,
        "resource_type": "property",
        "resource_id": bsdd_property.Code,
    }
    if bsdd_dictionary.UseOwnUri:
        data["host"] = bsdd_dictionary.DictionaryUri

    return dict_util.build_bsdd_url(data)
