"""Resolve class properties to their property definitions (internal or external)."""

from __future__ import annotations

from bsdd_json import BsddClassProperty, BsddDictionary, BsddProperty
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils.cache import is_offline

from bsdd_web.ops.helpers import internal_code


class Resolver:
    def __init__(self, d: BsddDictionary):
        self.d = d
        self.by_code = {p.Code: p for p in d.Properties}

    def property(self, cp: BsddClassProperty) -> BsddProperty | None:
        if cp.PropertyCode:
            return self.by_code.get(cp.PropertyCode)
        if cp.PropertyUri:
            code = internal_code(self.d, cp.PropertyUri, "prop")
            if code:
                return self.by_code.get(code)
            if is_offline():
                return None
            try:
                return prop_utils.Cache.get_external_property(cp.PropertyUri)
            except Exception:  # noqa: BLE001 - network problems must not break exports
                return None
        return None

    def name(self, cp: BsddClassProperty) -> str:
        prop = self.property(cp)
        return prop.Name if prop else cp.Code

    def definition(self, cp: BsddClassProperty) -> str:
        if cp.Description:
            return cp.Description
        prop = self.property(cp)
        if not prop:
            return ""
        return prop.Description or prop.Definition or ""

    def data_type(self, cp: BsddClassProperty) -> str | None:
        prop = self.property(cp)
        return prop.DataType if prop else None

    def values(self, cp: BsddClassProperty):
        if cp.AllowedValues:
            return cp.AllowedValues
        prop = self.property(cp)
        return prop.AllowedValues if prop else []


def resolver_for(d: BsddDictionary) -> Resolver:
    return Resolver(d)
