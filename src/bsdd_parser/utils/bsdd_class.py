from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional, Literal, Dict, List, Set
import logging

if TYPE_CHECKING:
    from bsdd_parser.models import BsddDictionary, BsddClass


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
    if not bsdd_class._parent_ref:
        return None
    return bsdd_class._parent_ref()


def get_parent(bsdd_class: BsddClass) -> BsddClass | None:
    bsdd_dictionary = get_dictionary_from_class(bsdd_class)
    if bsdd_class.ParentClassCode is None:
        return None
    return get_class_by_code(bsdd_dictionary, bsdd_class.ParentClassCode)


def get_class_by_code(bsdd_dictionary: BsddDictionary, code: str) -> BsddClass | None:
    return get_all_class_codes(bsdd_dictionary).get(code)


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
        dictionary = first._parent_ref() if getattr(first, "_parent_ref", None) else None
        if dictionary is None:
            raise ValueError("shared_parent: dictionary not provided and _parent_ref is not set.")

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
        code, _ = min(((code, depth_by_code[code]) for code in shared_codes), key=lambda x: x[1])
    else:  # "lowest"
        code, _ = max(((code, depth_by_code[code]) for code in shared_codes), key=lambda x: x[1])

    return get_class_by_code(dictionary, code)
