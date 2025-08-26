from __future__ import annotations
from typing import TYPE_CHECKING
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
