"""Class properties, property sets and Group-of-Properties synchronisation."""

from __future__ import annotations

from typing import Any

from bsdd_json import BsddClass, BsddClassProperty, BsddClassRelation, BsddProperty
from bsdd_json.utils import dictionary_utils as dict_utils

from . import Ctx, OpError, op
from .helpers import (
    GOP,
    add_temporary_pset,
    attach_property,
    class_index,
    class_uri,
    classes_referencing,
    get_class,
    get_class_property,
    get_property,
    gop_by_name,
    internal_code,
    is_reference_to,
    linked_gop,
    merged,
    new_class_property,
    property_index,
    pset_names,
    require_code,
    unique_code,
)


def _cp_data(data: dict[str, Any]) -> dict[str, Any]:
    data = dict(data)
    for key in ("PropertyCode", "PropertyUri"):
        if isinstance(data.get(key), str) and not data[key].strip():
            data[key] = None
    return data


def _check_reference(ctx: Ctx, cp: BsddClassProperty) -> None:
    if cp.PropertyCode and cp.PropertyCode not in property_index(ctx.d):
        raise OpError(f"Property '{cp.PropertyCode}' does not exist in the dictionary")


def _gop_pset(gop: BsddClass) -> str:
    return gop.Name


# ----------------------------------------------------------------- GroupOfProperties


def _propagate_add(ctx: Ctx, gop: BsddClass, cp: BsddClassProperty) -> None:
    for c in classes_referencing(ctx.d, gop):
        if any(x.Code == cp.Code for x in c.ClassProperties):
            continue
        data = cp.model_dump(mode="json")
        data["PropertySet"] = _gop_pset(gop)
        c.ClassProperties.append(new_class_property(c, data))


def _relating(ctx: Ctx, gop: BsddClass, code: str, pset: str | None = None) -> list[BsddClassProperty]:
    pset = pset or _gop_pset(gop)
    out = []
    for c in classes_referencing(ctx.d, gop):
        out.extend(cp for cp in c.ClassProperties if cp.Code == code and cp.PropertySet == pset)
    return out


# ----------------------------------------------------------------- class properties


@op("cp.create")
def create_class_property(ctx: Ctx, class_code: str, data: dict[str, Any]) -> str:
    bsdd_class = get_class(ctx.d, class_code)
    data = _cp_data(data)
    existing = [cp.Code for cp in bsdd_class.ClassProperties]
    if not data.get("Code"):
        base = data.get("PropertyCode") or internal_code(ctx.d, data.get("PropertyUri"), "prop") or "property"
        if data.get("PropertyUri") and not data.get("PropertyCode"):
            from bsdd_json.utils import property_utils as prop_utils

            base = prop_utils.get_code_by_uri(data["PropertyUri"]) or base
        data["Code"] = unique_code(base, existing)
    data["Code"] = require_code(data["Code"])
    if data["Code"] in existing:
        raise OpError(f"Class property code '{data['Code']}' exists already in this class")
    if bsdd_class.ClassType == GOP:
        data["PropertySet"] = _gop_pset(bsdd_class)
    cp = new_class_property(bsdd_class, data)
    _check_reference(ctx, cp)
    bsdd_class.ClassProperties.append(cp)
    if bsdd_class.ClassType == GOP:
        _propagate_add(ctx, bsdd_class, cp)
    return cp.Code


@op("cp.add_properties")
def add_properties_to_class(
    ctx: Ctx,
    class_code: str,
    property_codes: list[str],
    pset: str | None = None,
) -> list[str]:
    """Create class properties from dictionary properties (like dropping them on a class)."""
    from bsdd_json.utils import property_utils as prop_utils

    bsdd_class = get_class(ctx.d, class_code)
    created = []
    for code in property_codes:
        prop = get_property(ctx.d, code)
        cp = prop_utils.create_class_property_from_property(prop, bsdd_class, ctx.d)
        cp.AllowedValues = []
        if pset:
            cp.PropertySet = pset
        if bsdd_class.ClassType == GOP:
            cp.PropertySet = _gop_pset(bsdd_class)
        cp._set_parent(bsdd_class)
        bsdd_class.ClassProperties.append(cp)
        if bsdd_class.ClassType == GOP:
            _propagate_add(ctx, bsdd_class, cp)
        created.append(cp.Code)
    return created


@op("cp.update")
def update_class_property(ctx: Ctx, class_code: str, code: str, data: dict[str, Any]) -> str:
    bsdd_class = get_class(ctx.d, class_code)
    old = get_class_property(bsdd_class, code)
    index = bsdd_class.ClassProperties.index(old)
    data = _cp_data(data)
    if "PropertyCode" in data and data["PropertyCode"]:
        data.setdefault("PropertyUri", None)
    if "PropertyUri" in data and data["PropertyUri"]:
        data.setdefault("PropertyCode", None)
    values = merged(old, data)
    values["Code"] = require_code(values.get("Code"))
    if values["Code"] != code and values["Code"] in [cp.Code for cp in bsdd_class.ClassProperties]:
        raise OpError(f"Class property code '{values['Code']}' exists already in this class")
    if bsdd_class.ClassType == GOP:
        values["PropertySet"] = _gop_pset(bsdd_class)
    new = new_class_property(bsdd_class, values)
    _check_reference(ctx, new)
    bsdd_class.ClassProperties[index] = new

    if bsdd_class.ClassType == GOP:
        old_values = old.model_dump(mode="json")
        changed = {k: v for k, v in new.model_dump(mode="json").items() if old_values.get(k) != v}
        changed.pop("PropertySet", None)
        changed.pop("AllowedValues", None)  # synced explicitly via gop.sync_allowed_values
        if changed:
            for target in _relating(ctx, bsdd_class, code):
                owner = target.parent()
                if owner is None:
                    continue
                if "Code" in changed and changed["Code"] in [x.Code for x in owner.ClassProperties]:
                    continue
                values = merged(target, changed)
                i = owner.ClassProperties.index(target)
                owner.ClassProperties[i] = new_class_property(owner, values)
    return new.Code


@op("cp.delete")
def delete_class_properties(ctx: Ctx, class_code: str, codes: list[str]) -> None:
    bsdd_class = get_class(ctx.d, class_code)
    codes_set = set(codes)
    removed = [cp for cp in bsdd_class.ClassProperties if cp.Code in codes_set]
    bsdd_class.ClassProperties[:] = [cp for cp in bsdd_class.ClassProperties if cp.Code not in codes_set]
    # keep the property set visible if it became empty
    for cp in removed:
        if cp.PropertySet and cp.PropertySet not in pset_names(ctx, bsdd_class):
            add_temporary_pset(ctx, bsdd_class.Code, cp.PropertySet)
    if bsdd_class.ClassType == GOP:
        pset = _gop_pset(bsdd_class)
        for owner in classes_referencing(ctx.d, bsdd_class):
            before = list(owner.ClassProperties)
            owner.ClassProperties[:] = [cp for cp in owner.ClassProperties if not (cp.Code in codes_set and cp.PropertySet == pset)]
            if len(before) != len(owner.ClassProperties) and pset not in pset_names(ctx, owner):
                add_temporary_pset(ctx, owner.Code, pset)


@op("cp.paste")
def paste_class_properties(
    ctx: Ctx,
    class_code: str,
    payload: dict[str, Any],
    pset: str | None = None,
) -> list[str]:
    bsdd_class = get_class(ctx.d, class_code)
    _paste_properties(ctx, payload.get("properties") or [])
    raw = payload.get("class_properties") or []
    if not raw:
        raise OpError("Clipboard does not contain class properties")
    created = []
    existing = [cp.Code for cp in bsdd_class.ClassProperties]
    for item in raw:
        data = _cp_data(item)
        data["Code"] = unique_code(data.get("Code") or "property", existing)
        existing.append(data["Code"])
        if pset:
            data["PropertySet"] = pset
        if bsdd_class.ClassType == GOP:
            data["PropertySet"] = _gop_pset(bsdd_class)
        data.pop("OwnedUri", None)
        cp = new_class_property(bsdd_class, data)
        bsdd_class.ClassProperties.append(cp)
        if bsdd_class.ClassType == GOP:
            _propagate_add(ctx, bsdd_class, cp)
        created.append(cp.Code)
    return created


def _paste_properties(ctx: Ctx, raw_properties: list[dict[str, Any]]) -> None:
    props = property_index(ctx.d)
    for raw in raw_properties:
        if raw.get("Code") and raw["Code"] not in props:
            prop = BsddProperty.model_validate(raw)
            attach_property(ctx.d, prop)
            ctx.d.Properties.append(prop)
            props[prop.Code] = prop


@op("cp.remove_property_from_classes")
def remove_property_from_classes(ctx: Ctx, property_code: str, class_codes: list[str]) -> None:
    """Remove every class property that references ``property_code`` from the given classes."""
    prop = get_property(ctx.d, property_code)
    for class_code in class_codes:
        bsdd_class = get_class(ctx.d, class_code)
        codes = [
            cp.Code
            for cp in bsdd_class.ClassProperties
            if cp.PropertyCode == property_code or (cp.PropertyUri and internal_code(ctx.d, cp.PropertyUri, "prop") == prop.Code)
        ]
        if codes:
            delete_class_properties(ctx, class_code, codes)


# ----------------------------------------------------------------- property sets


@op("pset.create")
def create_property_set(ctx: Ctx, class_code: str, name: str, auto_gop: bool = False, gop_prefix: str = "") -> str:
    """Create a property set; if a GroupOfProperties with this name exists, link it.

    With ``auto_gop`` a missing GroupOfProperties is created first (code = ``gop_prefix`` + name)
    and linked, so every new property set starts as a predefined, reusable one.
    """
    bsdd_class = get_class(ctx.d, class_code)
    name = (name or "").strip()
    if not name:
        raise OpError("Name must not be empty")
    existing = pset_names(ctx, bsdd_class)
    gop = gop_by_name(ctx.d, name)
    if gop is None and auto_gop and bsdd_class.ClassType != GOP and name not in existing:
        gop = _create_gop(ctx, name, gop_prefix)
    if gop is not None and gop is not bsdd_class and name not in existing:
        _link_gop(ctx, bsdd_class, gop)
        if name not in pset_names(ctx, bsdd_class):
            add_temporary_pset(ctx, bsdd_class.Code, name)
        return name
    name = unique_code(name, existing)
    add_temporary_pset(ctx, bsdd_class.Code, name)
    return name


def _create_gop(ctx: Ctx, name: str, prefix: str) -> BsddClass:
    """New, empty GroupOfProperties named ``name`` with the code ``prefix`` + slug of the name."""
    d = ctx.d
    prefix = (prefix or "").strip()
    if len(prefix) > 30 or not all(ch.isalnum() or ch in "_-." for ch in prefix):
        raise OpError("The prefix may only contain letters, digits, '_', '-' and '.' (max. 30 characters)")
    code = unique_code(f"{prefix}{dict_utils.slugify(name)}", class_index(d))
    gop = BsddClass.model_validate({"Code": code, "Name": name, "ClassType": GOP})
    gop._set_parent(d)
    d.Classes.append(gop)
    return gop


def _link_gop(ctx: Ctx, bsdd_class: BsddClass, gop: BsddClass) -> None:
    existing = {cp.Code for cp in bsdd_class.ClassProperties}
    for cp in gop.ClassProperties:
        if cp.Code in existing:
            continue
        data = cp.model_dump(mode="json")
        data["PropertySet"] = _gop_pset(gop)
        bsdd_class.ClassProperties.append(new_class_property(bsdd_class, data))
    if not any(is_reference_to(ctx.d, cr, gop) for cr in bsdd_class.ClassRelations):
        rel = BsddClassRelation(RelationType="HasReference", RelatedClassUri=class_uri(ctx.d, gop), RelatedClassName=gop.Name)
        rel._set_parent(bsdd_class)
        bsdd_class.ClassRelations.append(rel)


@op("pset.rename")
def rename_property_set(ctx: Ctx, class_code: str, old: str, new: str) -> str:
    bsdd_class = get_class(ctx.d, class_code)
    new = (new or "").strip()
    if not new:
        raise OpError("Name must not be empty")
    if new == old:
        return new
    if new in pset_names(ctx, bsdd_class):
        raise OpError(f"Property set '{new}' exists already")
    for cp in bsdd_class.ClassProperties:
        if (cp.PropertySet or "") == (old or ""):
            cp.PropertySet = new
    temp = ctx.extras.temporary_psets.get(class_code, [])
    ctx.extras.temporary_psets[class_code] = [new if n == old else n for n in temp]
    return new


@op("pset.delete")
def delete_property_sets(ctx: Ctx, class_code: str, names: list[str]) -> None:
    bsdd_class = get_class(ctx.d, class_code)
    names_set = set(names)
    for name in names_set:
        gop = linked_gop(ctx.d, bsdd_class, name)
        if gop is not None:
            bsdd_class.ClassRelations[:] = [cr for cr in bsdd_class.ClassRelations if not is_reference_to(ctx.d, cr, gop)]
    if bsdd_class.ClassType == GOP:
        # deleting the pset of a GroupOfProperties removes its properties everywhere
        codes = [cp.Code for cp in bsdd_class.ClassProperties if (cp.PropertySet or "") in names_set]
        delete_class_properties(ctx, class_code, codes)
    bsdd_class.ClassProperties[:] = [cp for cp in bsdd_class.ClassProperties if (cp.PropertySet or "") not in names_set]
    temp = ctx.extras.temporary_psets.get(class_code, [])
    ctx.extras.temporary_psets[class_code] = [n for n in temp if n not in names_set]


@op("pset.paste")
def paste_property_sets(ctx: Ctx, class_code: str, payload: dict[str, Any]) -> list[str]:
    bsdd_class = get_class(ctx.d, class_code)
    items = payload.get("items") or []
    if not items:
        raise OpError("Clipboard does not contain property sets")
    _paste_properties(ctx, payload.get("properties") or [])
    created = []
    for item in items:
        name = unique_code(item.get("name") or "PropertySet", pset_names(ctx, bsdd_class))
        existing = [cp.Code for cp in bsdd_class.ClassProperties]
        cps = item.get("properties") or []
        for raw in cps:
            data = _cp_data(raw)
            data["Code"] = unique_code(data.get("Code") or "property", existing)
            existing.append(data["Code"])
            data["PropertySet"] = name
            data.pop("OwnedUri", None)
            bsdd_class.ClassProperties.append(new_class_property(bsdd_class, data))
        if not cps:
            add_temporary_pset(ctx, bsdd_class.Code, name)
        created.append(name)
    return created


# ----------------------------------------------------------------- GoP actions


@op("gop.sync_allowed_values")
def sync_allowed_values(ctx: Ctx, class_code: str, codes: list[str]) -> int:
    gop = get_class(ctx.d, class_code)
    if gop.ClassType != GOP:
        raise OpError("Only available for GroupOfProperties classes")
    count = 0
    for code in codes:
        source = get_class_property(gop, code)
        for target in _relating(ctx, gop, code):
            target.AllowedValues = [v.model_copy(deep=True) for v in source.AllowedValues]
            count += 1
    return count


@op("gop.delete_synced_psets")
def delete_synced_psets(ctx: Ctx, codes: list[str]) -> None:
    for code in codes:
        gop = get_class(ctx.d, code)
        for owner in classes_referencing(ctx.d, gop):
            owner.ClassProperties[:] = [cp for cp in owner.ClassProperties if cp.PropertySet != _gop_pset(gop)]
            owner.ClassRelations[:] = [cr for cr in owner.ClassRelations if not is_reference_to(ctx.d, cr, gop)]
