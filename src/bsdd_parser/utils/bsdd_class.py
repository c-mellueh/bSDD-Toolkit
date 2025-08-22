from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_parser.models import BsddDictionary, BsddClass


def get_root_classes(bsdd_dictionary: BsddDictionary):
    if bsdd_dictionary is None:
        return []
    return [c for c in bsdd_dictionary.Classes if not c.ParentClassCode]


def get_children(bsdd_class: BsddClass):
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
    return {c.Code: c for c in bsdd_dictionary.Classes}.get(code)
