from __future__ import annotations

import logging
from uuid import UUID, uuid4

import bsdd

from bsdd_json import (
    BsddClass,
    BsddClassProperty,
    BsddDictionary,
    BsddProperty,
    BsddPropertyRelation,
)

from . import build_unique_code
from . import dictionary_utils as dict_utils
from .cache import BaseCache

logger = logging.getLogger(__name__)


def load_property(uri, include_classes=False, language_code="", client: bsdd.Client | None = None):
    result = _load_property_json(uri, include_classes, language_code, client)
    if result is None:
        return None
    prop = BsddProperty.model_validate(result)
    prop.OwnedUri = uri
    return prop


def _load_property_json(uri, include_classes=False, language_code="", client: bsdd.Client | None = None):
    if not dict_utils.is_uri(uri):
        return None
    # Load Client
    c = bsdd.Client() if client is None else client

    # Request from bSDD
    result = c.get_property(uri, include_classes, language_code)
    if not result:
        return None

    if "statusCode" in result and result["statusCode"] == 400:
        return None
    for key, value in result.items():
        if not value:
            result[key] = None

    for allowed_value in result.get("allowedValues", []):
        allowed_value["uri"] = None

    return result


class Cache(BaseCache):
    cache_filename = "external_property_cache.json"
    model_cls = BsddProperty
    label = "property"

    @classmethod
    def get_external_property(cls, property_uri: str, client: bsdd.Client | None = None) -> BsddProperty | None:
        return cls._get(property_uri, lambda: load_property(property_uri, client=client))


def get_data_type(class_property: BsddClassProperty, bsdd_dictionary: BsddDictionary = None):
    prop = get_property_by_class_property(class_property, bsdd_dictionary)

    if not prop:
        return None
    return prop.DataType


def get_dictionary_from_property(
    bsdd_property: BsddClassProperty | BsddProperty,
) -> BsddDictionary | None:
    if isinstance(bsdd_property, BsddClassProperty):
        bsdd_class = bsdd_property.parent()
        if bsdd_class is None:
            return None
        return bsdd_class.parent()
    if isinstance(bsdd_property, BsddProperty):
        return bsdd_property.parent()
    return None


def get_internal_property(class_property: BsddClassProperty, bsdd_dictionary=None) -> BsddProperty | None:
    from bsdd_json.utils.dictionary_utils import is_external_ref

    if class_property.OwnedUri and is_external_ref(class_property.OwnedUri, bsdd_dictionary):
        return None
    bsdd_class = class_property.parent()
    if bsdd_dictionary is None and bsdd_class is None:
        return None
    if bsdd_dictionary is None:
        bsdd_dictionary = bsdd_class.parent()
    for p in bsdd_dictionary.Properties:
        if p.Code == class_property.PropertyCode:
            return p
    return None


def get_external_property(class_property: BsddClassProperty, client=None) -> BsddProperty | None:
    from bsdd_gui import tool

    if tool.Project.get_offline_mode():
        return None
    return Cache.get_external_property(class_property.PropertyUri, client)


def get_property_code_dict(bsdd_dictionary: BsddDictionary) -> dict[str, BsddProperty]:
    return {p.Code: p for p in bsdd_dictionary.Properties}


def get_units(class_property: BsddClassProperty):
    prop = get_property_by_class_property(class_property)

    if prop is None:
        return []
    return prop.Units or []


def get_classes_with_bsdd_property(property_code: str, bsdd_dictionary: BsddDictionary):
    is_external = property_code.startswith("https://")

    def _has_prop(c: BsddClass):
        return any(
            (is_external and p.PropertyUri == property_code) or (not is_external and p.PropertyCode == property_code) for p in c.ClassProperties
        )

    return list(filter(_has_prop, bsdd_dictionary.Classes))


def get_class_properties_from_property_code(property_code: str, bsdd_dictionary: BsddDictionary) -> list[BsddClassProperty]:
    bsdd_class_properties = []
    for bsdd_class in bsdd_dictionary.Classes:
        bsdd_class_properties.extend(cp for cp in bsdd_class.ClassProperties if cp.PropertyCode == property_code)
    return bsdd_class_properties


def get_class_properties_from_property_uri(
    property_uri: str,
    bsdd_dictionary: BsddDictionary,
) -> list[BsddClassProperty]:
    bsdd_class_properties = []
    for bsdd_class in bsdd_dictionary.Classes:
        bsdd_class_properties.extend(cp for cp in bsdd_class.ClassProperties if cp.PropertyUri == property_uri)
    return bsdd_class_properties


def get_property_by_code(code: str, bsdd_dictionary: BsddDictionary) -> BsddProperty | None:
    if dict_utils.is_uri(code):
        logger.warning("function DEPRECATED get_property_by_code called with URI. Use get_property_by_uri instead.")
        return get_property_by_uri(code, bsdd_dictionary)
    return get_property_code_dict(bsdd_dictionary).get(code)


def get_code_by_uri(uri: str):
    parsed_url = dict_utils.parse_bsdd_url(uri)
    resouce_type = parsed_url.get("resource_type")
    resource_id = parsed_url.get("resource_id")
    if resouce_type == "prop":
        return resource_id
    path_segments = parsed_url["path_segments"]

    # Handle ClassProperty
    if resouce_type == "class" and "prop" not in path_segments:
        return None

    code_index = path_segments.index("prop") + 2
    if code_index >= len(path_segments):
        return None

    # Catches Bug in API (See https://github.com/buildingSMART/bSDD/issues/142)
    if path_segments.count("prop") > 1:
        return path_segments[-1]

    return path_segments[code_index]


def get_property_by_uri(uri: str, bsdd_dictionary: BsddDictionary):
    if dict_utils.is_uri(uri):
        if dict_utils.is_external_ref(uri, bsdd_dictionary):
            bsdd_property = Cache.get_external_property(uri)
        else:
            code = get_code_by_uri(uri)
            bsdd_property = get_all_property_codes(bsdd_dictionary).get(code)
    else:
        bsdd_property = get_all_property_codes(bsdd_dictionary).get(uri)
    return bsdd_property


def get_all_property_codes(bsdd_dictionary: BsddDictionary) -> dict[str, BsddClass]:
    return {c.Code: c for c in bsdd_dictionary.Properties}


def update_internal_relations_to_new_version(bsdd_proeprty: BsddProperty, bsdd_dictionary: BsddDictionary):
    """If the Version of the given dictionary has changed, update all internal
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


def get_most_used_property_set(bsdd_property: BsddProperty, bsdd_dictionary: BsddDictionary) -> str | None:
    if bsdd_property.OwnedUri:
        class_properties = get_class_properties_from_property_uri(bsdd_property.OwnedUri, bsdd_dictionary)
    else:
        class_properties = get_class_properties_from_property_code(bsdd_property.Code, bsdd_dictionary)
    name_dict = {}
    for cp in class_properties:
        pset = cp.PropertySet
        if pset not in name_dict:
            name_dict[pset] = 0
        name_dict[pset] += 1
    sorted_list = sorted(name_dict.items(), key=lambda x: x[1], reverse=True)
    if not sorted_list:
        return None
    return sorted_list[0][0]


def create_class_property_from_property(bsdd_property: BsddProperty, bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary) -> BsddClassProperty:
    existing_codes = [p.Code for p in bsdd_class.ClassProperties]
    code = build_unique_code(bsdd_property.Code, existing_codes)
    if bsdd_property.OwnedUri:
        new_property = BsddClassProperty(Code=code, PropertyUri=bsdd_property.OwnedUri)
    else:
        new_property = BsddClassProperty(Code=code, PropertyCode=bsdd_property.Code)

    pset = get_most_used_property_set(bsdd_property, bsdd_dictionary) or "ExternalPset"
    if pset:
        new_property.PropertySet = pset
    if bsdd_property.Units:
        new_property.Unit = bsdd_property.Units[0]
    new_property.IsRequired = True
    new_property.AllowedValues = bsdd_property.AllowedValues
    return new_property


def get_property_relation(start_property: BsddProperty, end_uri: str, relation_type: str) -> BsddPropertyRelation | None:
    for relation in start_property.PropertyRelations:
        if relation.RelatedPropertyUri == end_uri and relation.RelationType == relation_type:
            return relation
    return None


def delete_property(bsdd_property: BsddProperty, bsdd_dictionary: BsddDictionary = None):
    bsdd_dictionary = bsdd_dictionary or bsdd_property._parent_ref()
    removed_class_properties = []
    for bsdd_class in get_classes_with_bsdd_property(bsdd_property.Code, bsdd_dictionary):
        for bsdd_class_property in list(bsdd_class.ClassProperties):
            if bsdd_class_property.PropertyCode == bsdd_property.Code:
                bsdd_class.ClassProperties.remove(bsdd_class_property)
                removed_class_properties.append(bsdd_class_property)
    bsdd_dictionary.Properties.remove(bsdd_property)
    return removed_class_properties


def get_name(class_property: BsddClassProperty, bsdd_dictionary=None):
    prop = get_property_by_class_property(class_property, bsdd_dictionary)
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


def get_property_by_class_property(class_prop: BsddClassProperty, bsdd_dictionary=None) -> BsddProperty | None:
    if bsdd_dictionary is None:
        bsdd_dictionary = get_dictionary_from_property(class_prop)
    if class_prop.PropertyUri:
        return get_property_by_uri(class_prop.PropertyUri, bsdd_dictionary)
    return get_property_by_code(class_prop.PropertyCode, bsdd_dictionary)


def get_class_properties_by_pset_name(bsdd_class: BsddClass, pset_name: str):
    return [p for p in bsdd_class.ClassProperties if p.PropertySet == pset_name]


def build_dummy_property(uri: str) -> BsddProperty:
    code = get_code_by_uri(uri)
    return BsddProperty(Code=code, Name=uri, OwnedUri=uri)


def find_parent_class(class_property: BsddClassProperty, bsdd_dictionary: BsddDictionary):
    def get_parent_class():
        for c in bsdd_dictionary.Classes:
            for cp in c.ClassProperties:
                if cp == class_property:
                    return c
        return None

    bsdd_class = class_property.parent()
    if not bsdd_class:
        bsdd_class = get_parent_class()
    if not bsdd_class:
        return None
    return bsdd_class


def is_class_property_linked(class_property: BsddClassProperty, bsdd_dictionary: BsddDictionary):
    from . import class_utils

    bsdd_class = class_property.parent()
    if not bsdd_class:
        bsdd_class = find_parent_class(class_property, bsdd_dictionary)
    if not bsdd_class:
        return False

    related_psets = class_utils.get_related_psets(bsdd_class, bsdd_dictionary)
    related_pset = {c.Name: c for c in related_psets}.get(class_property.PropertySet)
    if not related_pset:
        return False
    return class_property.Code in [cp.Code for cp in related_pset.ClassProperties]


def get_relating_properties(
    class_property: BsddClassProperty,
    bsdd_dictionary: BsddDictionary,
) -> list[BsddClassProperty]:
    """Get all Class Properties that are relating to the Class Property of a GroupOfProperties"""
    from . import class_utils

    bsdd_class = class_property.parent()

    if not bsdd_class:
        bsdd_class = find_parent_class(class_property, bsdd_dictionary)
    if not bsdd_class:
        return []
    if bsdd_class.ClassType != "GroupOfProperties":
        return []

    relatinge_properties: list[BsddClassProperty] = []
    for relating_class in class_utils.get_relating_pset_classes(bsdd_class, bsdd_dictionary):
        relatinge_properties.extend(p for p in relating_class.ClassProperties if p.Code == class_property.Code)
    return relatinge_properties


def get_definition(bsdd_class_property: BsddClassProperty, bsdd_dictionary: BsddDictionary) -> str:
    if bsdd_class_property.Description:
        return bsdd_class_property.Description

    bsdd_property = get_property_by_class_property(bsdd_class_property, bsdd_dictionary)
    if not bsdd_property:
        return ""

    if bsdd_property.Description:
        return bsdd_property.Description
    return bsdd_property.Definition or ""


def is_referencing_external_property(class_property: BsddClassProperty, bsdd_dictionary: BsddDictionary) -> bool:
    return bool(class_property.PropertyUri and dict_utils.is_external_ref(class_property.PropertyUri, bsdd_dictionary))


def get_uid(bsdd_property: BsddProperty) -> UUID:
    """Return the property's UID as a UUID, generating one if missing.

    Normalizes ``bsdd_property.Uid`` to a UUID: parses it if it's a string,
    keeps it as-is if it's already a UUID, or creates a fresh one if unset.
    The property's ``Uid`` is written back as a string in all cases.
    """
    if not bsdd_property.Uid:
        guid = uuid4()
    elif isinstance(bsdd_property.Uid, str):
        guid = UUID(bsdd_property.Uid)
    else:
        guid = bsdd_property.Uid
    bsdd_property.Uid = str(guid)
    return guid
