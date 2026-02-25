from __future__ import annotations
from bsdd_json import BsddDictionary
import pytest

from .helpers import make_class, make_dictionary, make_property


@pytest.fixture()
def populated_dictionary() -> BsddDictionary:
    """Dictionary with a small class/property tree for navigation tests.

    ROOT
    ├── CHILD1
    │   └── GRANDCHILD
    └── CHILD2
    """
    root = make_class("ROOT", "Root")
    child1 = make_class("CHILD1", "Child 1", ParentClassCode="ROOT")
    child2 = make_class("CHILD2", "Child 2", ParentClassCode="ROOT")
    grandchild = make_class("GRANDCHILD", "Grandchild", ParentClassCode="CHILD1")
    prop1 = make_property("PROP1", "Property 1")
    prop2 = make_property("PROP2", "Property 2")
    return BsddDictionary(
        OrganizationCode="TST",
        DictionaryCode="TEST",
        DictionaryVersion="1.0",
        LanguageIsoCode="en-GB",
        LanguageOnly=False,
        UseOwnUri=False,
        Classes=[root, child1, child2, grandchild],
        Properties=[prop1, prop2],
    )
