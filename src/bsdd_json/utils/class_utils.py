from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional, Literal, Dict, List, Set
import logging
from . import dictionary_utils as dict_utils
import bsdd

from bsdd_json.models import BsddDictionary, BsddClass, BsddClassRelation


class Cache:
    data = {}

    @classmethod
    def get_external_class(
        cls, class_uri: str, client: bsdd.Client | None = None
    ) -> BsddClass | None:
        from bsdd_json.utils import property_utils as prop_utils

        def _make_request():
            if not dict_utils.is_uri(class_uri):
                return dict()
            c = bsdd.Client() if client is None else client
            result = c.get_class(
                class_uri,
                include_class_properties=False,
                include_class_relations=False,
                include_reverse_relations=False,
            )

            if "statusCode" in result and result["statusCode"] == 400:
                return None
            return result

        if not class_uri:
            return None
        if class_uri not in cls.data:
            result = _make_request()
            if result is not None:
                result = BsddClass.model_validate(result)
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
    if dict_utils.is_uri(code):
        bsdd_class = Cache.get_external_class(code)
    else:
        bsdd_class = get_all_class_codes(bsdd_dictionary).get(code)
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
        if old_uri["namespace"] != namespace: #skip external relations
            continue
        new_uri = dict(old_uri) #copy
        new_uri["namespace"] = namespace
        new_uri["version"] = version
        if old_uri != new_uri:
            relationship.RelatedClassUri = dict_utils.build_bsdd_url(new_uri)


def build_bsdd_uri(bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary):
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
