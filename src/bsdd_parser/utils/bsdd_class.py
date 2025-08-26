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
    if bsdd_class._parent_ref is None:
        return []
    code = bsdd_class.Code
    bsdd_dictionary = bsdd_class._parent_ref()
    return [c for c in bsdd_dictionary.Classes if c.ParentClassCode == code]


def get_row_index(bsdd_class: BsddClass):
    bsdd_dictionary = bsdd_class._parent_ref()
    if not bsdd_class.ParentClassCode:
        return bsdd_dictionary.Classes.index(bsdd_class)
    parent_class = get_class_by_code(bsdd_dictionary, bsdd_class.ParentClassCode)
    return get_children(parent_class).index(bsdd_class)


def get_class_by_code(bsdd_dictionary: BsddDictionary, code: str):
    return get_all_class_codes(bsdd_dictionary).get(code)


def get_all_class_codes(bsdd_dictionary: BsddDictionary) -> dict[str, BsddClass]:
    return {c.Code: c for c in bsdd_dictionary.Classes}


def remove_class(bsdd_class: BsddClass):
    bsdd_dictionary = bsdd_class._parent_ref() if bsdd_class._parent_ref else None
    if not bsdd_dictionary:
        return

    for cl in bsdd_dictionary.Classes:
        if cl.ParentClassCode == bsdd_class.Code:
            cl.ParentClassCode = None
    bsdd_dictionary.Classes.remove(bsdd_class)
