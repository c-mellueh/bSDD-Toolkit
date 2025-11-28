from __future__ import annotations
from typing import TYPE_CHECKING

from bsdd_json import (
    BsddClassProperty,
    BsddProperty,
    BsddDictionary,
    BsddClass,
    BsddPropertyRelation,
)
import bsdd
from bsdd import Client
from . import dictionary_utils as dict_utils
from . import build_unique_code
import logging


class Cache:
    data = {}

    @classmethod
    def get_external_property(
        cls, property_uri: str, client: bsdd.Client | None = None
    ) -> BsddClassProperty | None:
        from bsdd_json.utils import property_utils as prop_utils

        def _make_request():

            if not dict_utils.is_uri(property_uri):
                return dict()
            logging.debug(f"Load {property_uri}")
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

    prop = get_property_by_class_property(class_property)

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


def get_external_property(
    class_property: BsddClassProperty, client=None
) -> BsddProperty | None:
    from bsdd_gui import tool

    if tool.Project.get_offline_mode():
        return None
    return Cache.get_external_property(class_property.PropertyUri, client)


def get_property_code_dict(bsdd_dictionary: BsddDictionary) -> dict[str, BsddProperty]:
    return {p.Code: p for p in bsdd_dictionary.Properties}


def get_datatype(class_property: BsddClassProperty):
    prop = get_property_by_class_property(class_property)

    if prop is None:
        return ""
    return prop.DataType or "String"


def get_units(class_property: BsddClassProperty):
    prop = get_property_by_class_property(class_property)

    if prop is None:
        return []
    return prop.Units or []


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


def get_class_properties_from_property(
    property_code: str, bsdd_dictionary: BsddDictionary
) -> list[BsddClassProperty]:
    bsdd_class_properties = list()
    for bsdd_class in bsdd_dictionary.Classes:
        for bsdd_class_property in bsdd_class.ClassProperties:
            if bsdd_class_property.PropertyCode == property_code:
                bsdd_class_properties.append(bsdd_class_property)
    return bsdd_class_properties


def get_property_by_code(
    code: str, bsdd_dictionary: BsddDictionary
) -> BsddProperty | None:
    if dict_utils.is_uri(code):
        prop = Cache.get_external_property(code)
    else:
        prop = get_property_code_dict(bsdd_dictionary).get(code)
    return prop


def update_internal_relations_to_new_version(
    bsdd_proeprty: BsddProperty, bsdd_dictionary: BsddDictionary
):
    """
    If the Version of the given dictionary has changed, update all internal
    Property relations of the given property to point to the new version URIs.
    """
    namespace = f"{bsdd_dictionary.OrganizationCode}/{bsdd_dictionary.DictionaryCode}"
    version = bsdd_dictionary.DictionaryVersion
    for relationship in bsdd_proeprty.PropertyRelations:
        old_uri = dict_utils.parse_bsdd_url(relationship.RelatedPropertyUri)
        if old_uri["namespace"] != namespace:  # skip external relations
            continue
        new_uri = dict(old_uri)  # copy
        new_uri["namespace"] = namespace
        new_uri["version"] = version
        if old_uri != new_uri:
            relationship.RelatedPropertyUri = dict_utils.build_bsdd_url(new_uri)


def build_bsdd_uri(bsdd_property: BsddProperty, bsdd_dictionary: BsddDictionary):
    data = {
        "namespace": [bsdd_dictionary.OrganizationCode, bsdd_dictionary.DictionaryCode],
        "version": bsdd_dictionary.DictionaryVersion,
        "resource_type": "prop",
        "resource_id": bsdd_property.Code,
    }
    if bsdd_dictionary.UseOwnUri:
        data["host"] = bsdd_dictionary.DictionaryUri

    return dict_utils.build_bsdd_url(data)


def get_most_used_property_set(
    bsdd_property: BsddProperty, bsdd_dictionary: BsddDictionary
) -> str | None:
    class_properties = get_class_properties_from_property(
        bsdd_property.Code, bsdd_dictionary
    )
    name_dict = dict()
    for cp in class_properties:
        pset = cp.PropertySet
        if pset not in name_dict:
            name_dict[pset] = 0
        name_dict[pset] += 1
    sorted_list = sorted(name_dict.items(), key=lambda x: x[1], reverse=True)
    if not sorted_list:
        return None
    return sorted_list[0][0]


def create_class_property_from_internal_property(
    bsdd_property: BsddProperty, bsdd_class: BsddClass
) -> BsddClassProperty:
    existing_codes = [p.Code for p in bsdd_class.ClassProperties]
    code = build_unique_code(bsdd_property.Code, existing_codes)
    new_property = BsddClassProperty(Code=code, PropertyCode=bsdd_property.Code)
    pset = get_most_used_property_set(bsdd_property, bsdd_property._parent_ref())
    if pset:
        new_property.PropertySet = pset
    if bsdd_property.Units:
        new_property.Unit = BsddProperty.Units[0]
    new_property.IsRequired = True
    new_property.AllowedValues = bsdd_property.AllowedValues
    return new_property


def get_property_relation(
    start_property: BsddProperty, end_property: BsddProperty, relation_type: str
) -> BsddPropertyRelation | None:
    end_uri = build_bsdd_uri(end_property, end_property._parent_ref())
    for relation in start_property.PropertyRelations:
        if (
            relation.RelatedPropertyUri == end_uri
            and relation.RelationType == relation_type
        ):
            return relation
    return None


def delete_property(
    bsdd_property: BsddProperty, bsdd_dictionary: BsddDictionary = None
):
    bsdd_dictionary = (
        bsdd_property._parent_ref() if not bsdd_dictionary else bsdd_dictionary
    )
    removed_class_properties = list()
    for bsdd_class in get_classes_with_bsdd_property(
        bsdd_property.Code, bsdd_dictionary
    ):
        for bsdd_class_property in list(bsdd_class.ClassProperties):
            if bsdd_class_property.PropertyCode == bsdd_property.Code:
                bsdd_class.ClassProperties.remove(bsdd_class_property)
                removed_class_properties.append(bsdd_class_property)
    bsdd_dictionary.Properties.remove(bsdd_property)
    return removed_class_properties


def get_name(class_property: BsddClassProperty):
    prop = get_property_by_class_property(class_property)
    if not prop:
        return None
    return prop.Name


def get_values(class_property: BsddClassProperty):
    prop = get_property_by_class_property(class_property)
    if not prop:
        return None
    if class_property.AllowedValues:
        return class_property.AllowedValues
    if prop.AllowedValues:
        return prop.AllowedValues
    return []


def get_property_by_class_property(
    class_prop: BsddClassProperty,
) -> BsddProperty | None:
    if not is_external_ref(class_prop):
        return get_internal_property(class_prop)
    else:
        return get_external_property(class_prop)


def get_class_properties_by_pset_name(bsdd_class: BsddClass, pset_name: str):
    return [p for p in bsdd_class.ClassProperties if p.PropertySet == pset_name]
