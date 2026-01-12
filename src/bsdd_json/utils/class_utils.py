from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional, Literal, Dict, List, Set
import logging
from . import dictionary_utils as dict_utils
import bsdd

from bsdd_json.models import BsddDictionary, BsddClass, BsddClassRelation


def load_class(
    class_uri: str,
    bsdd_dictionary: BsddDictionary,
    include_properties=False,
    include_relations=False,
    client: bsdd.Client | None = None,
):
    result = _load_class_json(
        class_uri, bsdd_dictionary, include_properties, include_relations, client
    )
    if not result:
        return None
    return BsddClass.model_validate(result)


def _load_class_json(
    class_uri: str,
    bsdd_dictionary: BsddDictionary,
    include_properties=False,
    include_relations=False,
    client: bsdd.Client | None = None,
) -> None | BsddClass:
    from . import property_utils as prop_utils

    if not dict_utils.is_uri(class_uri):
        return None
    # Load Client
    c = bsdd.Client() if client is None else client

    # Request from bSDD
    result = c.get_class(
        class_uri,
        include_class_properties=include_properties,
        include_class_relations=include_relations,
        include_reverse_relations=False,
    )
    if not result:
        return None

    if "statusCode" in result and result["statusCode"] == 400:
        return None

    for bsdd_prop in result.get("classProperties", []):
        code = prop_utils.get_code_by_uri(bsdd_prop.get("uri"))
        bsdd_prop["Code"] = code
        prop_uri = bsdd_prop["propertyUri"]

        if not dict_utils.is_external_ref(prop_uri, bsdd_dictionary):
            bsdd_prop["propertyUri"] = None
        else:
            bsdd_prop["propertyCode"] = None
        if bsdd_prop.get("description") == bsdd_prop.get("definition"):
            bsdd_prop["description"] = None

        for allowed_value in bsdd_prop.get("allowedValues", []):
            allowed_value["uri"] = None

    pr = result.get("parentClassReference")
    if pr:
        result["ParentClassCode"] = pr["code"]
    result["OwnedUri"] = class_uri
    result["RelatedIfcEntityNamesList"] = result.get("relatedIfcEntityNames", [])
    if result["referenceCode"] == result["code"]:
        result["referenceCode"] = None
    result["CreatorLanguageIsoCode"] = result.get("creatorLanguageCode")

    for key, value in result.items():
        if not value:
            result[key] = None

    # Remove IfcReferences that are handled by RelatedIfcEntityNamesList
    filtered_class_relations = list()
    for class_relation in list(result.get("classRelations", [])):
        cr_uri = class_relation.get("relatedClassUri")
        if not dict_utils.is_ifc_reference(cr_uri):
            filtered_class_relations.append(class_relation)
            continue
        if not class_relation["relationType"] == "HasReference":
            filtered_class_relations.append(class_relation)
            continue
        ifc_code = get_code_by_uri(cr_uri)
        if ifc_code not in result["RelatedIfcEntityNamesList"]:
            filtered_class_relations.append(class_relation)
    result["classRelations"] = filtered_class_relations

    return result


class Cache:
    data = {}

    @classmethod
    def get_external_class(
        cls,
        class_uri: str,
        bsdd_dictionary: BsddDictionary,
        include_properties=False,
        include_relations=False,
        client: bsdd.Client | None = None,
    ) -> BsddClass | None:
        from bsdd_json.utils import property_utils as prop_utils

        if not class_uri:
            return None
        if class_uri in cls.data:
            return cls.data[class_uri]

        result = load_class(
            class_uri, bsdd_dictionary, include_properties, include_relations, client
        )
        cls.data[class_uri] = result
        return cls.data[class_uri]

    @classmethod
    def flush_data(cls):
        cls.data = dict()


def get_root_classes(bsdd_dictionary: BsddDictionary):
    if bsdd_dictionary is None:
        return []
    return [c for c in bsdd_dictionary.Classes if not c.ParentClassCode]


def get_children(bsdd_class: BsddClass):
    bsdd_dictionary = get_dictionary_from_class(bsdd_class)
    if bsdd_dictionary is None:
        return []
    code = bsdd_class.Code
    return [c for c in bsdd_dictionary.Classes if c.ParentClassCode == code]


def get_row_index(bsdd_class: BsddClass):
    bsdd_dictionary = get_dictionary_from_class(bsdd_class)
    if bsdd_dictionary is None:
        return -1
    if not bsdd_class.ParentClassCode:
        return bsdd_dictionary.Classes.index(bsdd_class)
    parent_class = get_class_by_code(bsdd_dictionary, bsdd_class.ParentClassCode)
    return get_children(parent_class).index(bsdd_class)


def get_dictionary_from_class(bsdd_class: BsddClass):
    return bsdd_class.parent()


def get_parent(bsdd_class: BsddClass) -> BsddClass | None:
    if bsdd_class is None:
        return None
    bsdd_dictionary = get_dictionary_from_class(bsdd_class)
    if bsdd_class.ParentClassCode is None:
        return None
    return get_class_by_code(bsdd_dictionary, bsdd_class.ParentClassCode)


def get_class_by_code(bsdd_dictionary: BsddDictionary, code: str) -> BsddClass | None:
    return get_all_class_codes(bsdd_dictionary).get(code)


def get_class_by_uri(bsdd_dictionary: BsddDictionary, uri: str) -> BsddClass | None:
    if dict_utils.is_uri(uri):
        if is_external_ref(uri, bsdd_dictionary):
            bsdd_class = Cache.get_external_class(uri, bsdd_dictionary)
        else:
            code = dict_utils.parse_bsdd_url(uri).get("resource_id")
            bsdd_class = get_all_class_codes(bsdd_dictionary).get(code)
    else:
        bsdd_class = get_all_class_codes(bsdd_dictionary).get(uri)
    return bsdd_class


def get_all_class_codes(bsdd_dictionary: BsddDictionary) -> dict[str, BsddClass]:
    return {c.Code: c for c in bsdd_dictionary.Classes}


def remove_class(bsdd_class: BsddClass):
    bsdd_dictionary = get_dictionary_from_class(bsdd_class)
    if not bsdd_dictionary:
        return

    for cl in bsdd_dictionary.Classes:
        if cl.ParentClassCode == bsdd_class.Code:
            cl.ParentClassCode = None
    bsdd_dictionary.Classes.remove(bsdd_class)


def _ancestors_topdown(c: BsddClass, d: BsddDictionary) -> List[BsddClass]:
    """List of ancestors from ROOT → self (includes self)."""
    path: List[BsddClass] = []
    cur: Optional[BsddClass] = c
    while cur is not None:
        path.append(cur)
        if not cur.ParentClassCode:
            break
        cur = get_class_by_code(d, cur.ParentClassCode)
    path.reverse()  # root depth=0 ... self at the end
    return path


def shared_parent(
    classes: Iterable[BsddClass],
    *,
    dictionary: Optional[BsddDictionary] = None,
    mode: Literal["highest", "lowest"] = "highest",
) -> Optional[BsddClass]:
    """
    Return the shared parent of all given classes.

    - mode="highest": the upmost (root-most) shared ancestor.
    - mode="lowest":  the closest (deepest) shared ancestor, i.e., LCA.

    Includes each class itself as an ancestor (so siblings return their direct parent;
    identical inputs return that class).
    Returns None if there is no common ancestor (e.g., different root trees).
    """
    cls_list = list(classes)
    if not cls_list:
        return None

    # Resolve dictionary if not passed
    if dictionary is None:
        first = cls_list[0]
        dictionary = first.parent()
        if dictionary is None:
            raise ValueError(
                "shared_parent: dictionary not provided and parent is not set."
            )

    # Build top-down ancestor path for the first class and an index by Code -> depth
    path0 = _ancestors_topdown(cls_list[0], dictionary)
    depth_by_code: Dict[str, int] = {c.Code: i for i, c in enumerate(path0)}

    # Intersect with ancestors of all remaining classes (by Code)
    shared_codes: Set[str] = set(depth_by_code.keys())
    for c in cls_list[1:]:
        path_codes = {a.Code for a in _ancestors_topdown(c, dictionary)}
        shared_codes &= path_codes
        if not shared_codes:
            return None

    # Choose highest (min depth) or lowest (max depth) among the shared set
    if mode == "highest":
        code, _ = min(
            ((code, depth_by_code[code]) for code in shared_codes), key=lambda x: x[1]
        )
    else:  # "lowest"
        code, _ = max(
            ((code, depth_by_code[code]) for code in shared_codes), key=lambda x: x[1]
        )

    return get_class_by_code(dictionary, code)


def update_internal_relations_to_new_version(
    bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary
):
    """
    If the Version of the given dictionary has changed, update all internal
    class relations of the given class to point to the new version URIs.
    """
    namespace = f"{bsdd_dictionary.OrganizationCode}/{bsdd_dictionary.DictionaryCode}"
    version = bsdd_dictionary.DictionaryVersion
    for relationship in bsdd_class.ClassRelations:
        old_uri = dict_utils.parse_bsdd_url(relationship.RelatedClassUri)
        if old_uri["namespace"] != namespace:  # skip external relations
            continue
        new_uri = dict(old_uri)  # copy
        new_uri["namespace"] = namespace
        new_uri["version"] = version
        if old_uri != new_uri:
            relationship.RelatedClassUri = dict_utils.build_bsdd_url(new_uri)


def build_bsdd_uri(bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary):
    if not isinstance(bsdd_class, BsddClass):
        return None
    data = {
        "namespace": [bsdd_dictionary.OrganizationCode, bsdd_dictionary.DictionaryCode],
        "version": bsdd_dictionary.DictionaryVersion,
        "resource_type": "class",
        "resource_id": bsdd_class.Code,
    }
    if bsdd_dictionary.UseOwnUri:
        data["host"] = bsdd_dictionary.DictionaryUri

    return dict_utils.build_bsdd_url(data)


def get_class_relation(
    start_class: BsddClass, end_class: BsddClass, relation_type: str
) -> BsddClassRelation | None:
    end_uri = (
        end_class.OwnedUri
        if not end_class.parent()
        else build_bsdd_uri(end_class, end_class._parent_ref())
    )
    for relation in start_class.ClassRelations:
        if (
            relation.RelatedClassUri == end_uri
            and relation.RelationType == relation_type
        ):
            return relation
    return None


def set_code(bsdd_class: BsddClass, code: str) -> None:
    if code == bsdd_class.Code:
        return
    bsdd_class._apply_code_side_effects(code)
    # assign without recursion (no property involved)
    object.__setattr__(bsdd_class, "Code", code)


def is_external_ref(uri: str, bsdd_dictionary: BsddDictionary) -> bool:
    if not uri:
        return False
    from .dictionary_utils import get_dictionary_path_from_uri, bsdd_dictionary_url

    dict_path = get_dictionary_path_from_uri(uri)
    if dict_path == bsdd_dictionary_url(bsdd_dictionary):
        return False
    return True


def is_ifc_reference(bsdd_class: BsddClass) -> bool:
    if not bsdd_class.OwnedUri:
        return False
    return dict_utils.is_ifc_reference(bsdd_class.OwnedUri)


def get_code_by_uri(uri: str):
    parsed_url = dict_utils.parse_bsdd_url(uri)
    resouce_type = parsed_url.get("resource_type")
    if not resouce_type == "class":
        return None

    resource_id = parsed_url.get("resource_id")
    return resource_id


def build_dummy_class(class_uri: str) -> BsddClass:
    class_code = get_code_by_uri(class_uri)
    return BsddClass(
        Code=class_code,
        Name=class_uri,
        OwnedUri=class_uri,
    )
