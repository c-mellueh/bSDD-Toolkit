from __future__ import annotations

from typing import Any

from bsdd_json import BsddProperty
from bsdd_json.utils import dictionary_utils as dict_utils

from . import Ctx, OpError, op
from .helpers import (
    attach_property,
    get_property,
    internal_code,
    merged,
    property_index,
    property_uri,
    require_code,
    resolve_property_relation,
    same_uri,
    sync_property_inverse,
    unique_code,
)


def _validate_property(d, data: dict[str, Any], *, own_code: str | None = None) -> BsddProperty:
    code = require_code(data.get("Code"))
    data["Code"] = code
    if not (data.get("Name") or "").strip():
        raise OpError("Name must not be empty")
    if code != own_code and code in property_index(d):
        raise OpError(f"Code '{code}' exists already")
    return BsddProperty.model_validate(data)


@op("prop.create")
def create_property(ctx: Ctx, data: dict[str, Any]) -> str:
    d = ctx.d
    data = dict(data)
    if not data.get("Code") and data.get("Name"):
        data["Code"] = unique_code(dict_utils.slugify(data["Name"]), property_index(d))
    data.setdefault("DataType", "String")
    relations = data.pop("PropertyRelations", None) or []
    prop = _validate_property(d, data)
    attach_property(d, prop)
    d.Properties.append(prop)
    if relations:
        prop.PropertyRelations = [resolve_property_relation(d, r) for r in relations]
        attach_property(d, prop)
        sync_property_inverse(d, prop, [], prop.PropertyRelations)
    return prop.Code


@op("prop.update")
def update_property(ctx: Ctx, code: str, data: dict[str, Any]) -> str:
    d = ctx.d
    old = get_property(d, code)
    index = d.Properties.index(old)
    old_uri = property_uri(d, old)
    old_relations = list(old.PropertyRelations)
    data = dict(data)
    relations_data = data.pop("PropertyRelations", None)
    new = _validate_property(d, merged(old, data), own_code=code)
    if relations_data is not None:
        new.PropertyRelations = [resolve_property_relation(d, r) for r in relations_data]
    attach_property(d, new)
    d.Properties[index] = new

    if new.Code != code:
        new_uri = property_uri(d, new)
        for c in d.Classes:
            for cp in c.ClassProperties:
                if cp.PropertyCode == code:
                    cp.PropertyCode = new.Code
                elif cp.PropertyUri and internal_code(d, cp.PropertyUri, "prop") == code:
                    cp.PropertyUri = new_uri
        for p in d.Properties:
            for pr in p.PropertyRelations:
                if same_uri(pr.RelatedPropertyUri, old_uri) or internal_code(d, pr.RelatedPropertyUri, "prop") == code:
                    pr.RelatedPropertyUri = new_uri
            for attr in ("ConnectedPropertyCodes", "DynamicParameterPropertyCodes"):
                values = getattr(p, attr)
                if values and code in values:
                    setattr(p, attr, [new.Code if v == code else v for v in values])

    if new.Name != old.Name:
        for p in d.Properties:
            for pr in p.PropertyRelations:
                if internal_code(d, pr.RelatedPropertyUri, "prop") == new.Code:
                    pr.RelatedPropertyName = new.Name

    if relations_data is not None:
        sync_property_inverse(d, new, old_relations, new.PropertyRelations)
    return new.Code


@op("prop.delete")
def delete_properties(ctx: Ctx, codes: list[str]) -> list[str]:
    """Delete properties and every class property / relation that references them."""
    d = ctx.d
    codes_set = {c for c in codes if c in property_index(d)}
    if not codes_set:
        return []
    for c in d.Classes:
        c.ClassProperties[:] = [
            cp
            for cp in c.ClassProperties
            if cp.PropertyCode not in codes_set and internal_code(d, cp.PropertyUri, "prop") not in codes_set
        ]
    d.Properties[:] = [p for p in d.Properties if p.Code not in codes_set]
    for p in d.Properties:
        p.PropertyRelations[:] = [pr for pr in p.PropertyRelations if internal_code(d, pr.RelatedPropertyUri, "prop") not in codes_set]
        for attr in ("ConnectedPropertyCodes", "DynamicParameterPropertyCodes"):
            values = getattr(p, attr)
            if values and set(values) & codes_set:
                setattr(p, attr, [v for v in values if v not in codes_set] or None)
    return sorted(codes_set)


@op("prop.paste")
def paste_properties(ctx: Ctx, payload: dict[str, Any]) -> list[str]:
    d = ctx.d
    raw = payload.get("properties") or []
    if not raw:
        raise OpError("Clipboard does not contain properties")
    existing = set(property_index(d))
    created = []
    for item in raw:
        data = dict(item)
        data["Code"] = unique_code(data.get("Code") or "property", existing)
        existing.add(data["Code"])
        data.pop("OwnedUri", None)
        prop = BsddProperty.model_validate(data)
        attach_property(d, prop)
        d.Properties.append(prop)
        created.append(prop.Code)
    return created
