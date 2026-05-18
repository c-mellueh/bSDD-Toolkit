from __future__ import annotations

from bsdd_json.models import BsddClass, BsddDictionary, BsddProperty


def make_dictionary(**kwargs) -> BsddDictionary:
    defaults = {
        "OrganizationCode": "TST",
        "DictionaryCode": "TEST",
        "DictionaryVersion": "1.0",
        "LanguageIsoCode": "en-GB",
        "LanguageOnly": False,
        "UseOwnUri": False,
    }
    defaults.update(kwargs)
    return BsddDictionary(**defaults)


def make_class(code: str, name: str, **kwargs) -> BsddClass:
    return BsddClass(Code=code, Name=name, **kwargs)


def make_property(code: str, name: str, **kwargs) -> BsddProperty:
    return BsddProperty(Code=code, Name=name, **kwargs)
