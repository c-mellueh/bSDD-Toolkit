from __future__ import annotations

from typing import Any

from bsdd_json import (
    BsddClass,
    BsddClassProperty,
    BsddClassRelation,
    BsddDictionary,
    BsddProperty,
    BsddPropertyRelation,
)
from bsdd_json.utils import build_unique_code
from bsdd_json.utils import dictionary_utils as dict_utils

from . import Ctx, OpError

GOP = "GroupOfProperties"

CLASS_INVERSE = {
    "IsChildOf": "IsParentOf",
    "IsParentOf": "IsChildOf",
    "HasPart": "IsPartOf",
    "IsPartOf": "HasPart",
    "IsEqualTo": "IsEqualTo",
    "IsSimilarTo": "IsSimilarTo",
}
PROPERTY_INVERSE = {"IsEqualTo": "IsEqualTo", "IsSimilarTo": "IsSimilarTo"}


def dump(model) -> dict[str, Any]:
    return model.model_dump(mode="json", exclude_none=True)


# --------------------------------------------------------------------------- lookups


def class_index(d: BsddDictionary) -> dict[str, BsddClass]:
    return {c.Code: c for c in d.Classes}


def property_index(d: BsddDictionary) -> dict[str, BsddProperty]:
    return {p.Code: p for p in d.Properties}


def get_class(d: BsddDictionary, code: str) -> BsddClass:
    for c in d.Classes:
        if c.Code == code:
            return c
    raise OpError(f"Class '{code}' not found")


def get_property(d: BsddDictionary, code: str) -> BsddProperty:
    for p in d.Properties:
        if p.Code == code:
            return p
    raise OpError(f"Property '{code}' not found")


def get_class_property(bsdd_class: BsddClass, code: str) -> BsddClassProperty:
    for cp in bsdd_class.ClassProperties:
        if cp.Code == code:
            return cp
    raise OpError(f"Class property '{code}' not found in class '{bsdd_class.Code}'")


def children(d: BsddDictionary, code: str) -> list[BsddClass]:
    return [c for c in d.Classes if c.ParentClassCode == code]


def descendants(d: BsddDictionary, code: str) -> set[str]:
    by_parent: dict[str, list[str]] = {}
    for c in d.Classes:
        if c.ParentClassCode:
            by_parent.setdefault(c.ParentClassCode, []).append(c.Code)
    out: set[str] = set()
    stack = [code]
    while stack:
        cur = stack.pop()
        for child in by_parent.get(cur, []):
            if child not in out:
                out.add(child)
                stack.append(child)
    return out


def pset_names(ctx: Ctx, bsdd_class: BsddClass) -> list[str]:
    names: list[str] = []
    for cp in bsdd_class.ClassProperties:
        if cp.PropertySet and cp.PropertySet not in names:
            names.append(cp.PropertySet)
    for name in ctx.extras.temporary_psets.get(bsdd_class.Code, []):
        if name not in names:
            names.append(name)
    return names


# --------------------------------------------------------------------------- URIs


def namespace(d: BsddDictionary) -> str:
    return f"{d.OrganizationCode}/{d.DictionaryCode}".lower()


def class_uri(d: BsddDictionary, bsdd_class: BsddClass | str) -> str:
    code = bsdd_class if isinstance(bsdd_class, str) else bsdd_class.Code
    data = {
        "namespace": [d.OrganizationCode, d.DictionaryCode],
        "version": d.DictionaryVersion,
        "resource_type": "class",
        "resource_id": code,
    }
    if d.UseOwnUri and d.DictionaryUri:
        data["host"] = _host(d.DictionaryUri)
    return dict_utils.build_bsdd_url(data)


def property_uri(d: BsddDictionary, prop: BsddProperty | str) -> str:
    code = prop if isinstance(prop, str) else prop.Code
    data = {
        "namespace": [d.OrganizationCode, d.DictionaryCode],
        "version": d.DictionaryVersion,
        "resource_type": "prop",
        "resource_id": code,
    }
    if d.UseOwnUri and d.DictionaryUri:
        data["host"] = _host(d.DictionaryUri)
    return dict_utils.build_bsdd_url(data)


def _host(uri: str) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(uri)
    return parsed.netloc or uri.strip("/")


def internal_code(d: BsddDictionary, uri: str | None, kind: str) -> str | None:
    """Return the code if ``uri`` points to a class/property of this dictionary (any version)."""
    if not uri or not dict_utils.is_uri(uri):
        return None
    parsed = dict_utils.parse_bsdd_url(uri)
    if (parsed.get("namespace") or "").lower() != namespace(d):
        return None
    rtype = parsed.get("resource_type")
    if kind == "class" and rtype != "class":
        return None
    if kind == "prop" and rtype not in ("prop", "property"):
        return None
    return parsed.get("resource_id")


def same_uri(a: str | None, b: str | None) -> bool:
    return dict_utils.normalize_uri(a) == dict_utils.normalize_uri(b)


# --------------------------------------------------------------------------- validation


def require_code(code: Any, what: str = "Code") -> str:
    if not isinstance(code, str) or not code.strip():
        raise OpError(f"{what} must not be empty")
    return code.strip()


def unique_code(base: str, existing) -> str:
    return build_unique_code(base, list(existing))


def merged(model, data: dict[str, Any]) -> dict[str, Any]:
    base = model.model_dump(mode="json")
    base.update(data or {})
    return base


def attach_class(d: BsddDictionary, bsdd_class: BsddClass) -> BsddClass:
    bsdd_class._set_parent(d)
    for cp in bsdd_class.ClassProperties:
        cp._set_parent(bsdd_class)
    for cr in bsdd_class.ClassRelations:
        cr._set_parent(bsdd_class)
    return bsdd_class


def attach_property(d: BsddDictionary, prop: BsddProperty) -> BsddProperty:
    prop._set_parent(d)
    for pr in prop.PropertyRelations:
        pr._set_parent(prop)
    return prop


def new_class_property(bsdd_class: BsddClass, data: dict[str, Any]) -> BsddClassProperty:
    cp = BsddClassProperty.model_validate(data)
    cp._set_parent(bsdd_class)
    return cp


# --------------------------------------------------------------------------- relations


def resolve_class_relation(d: BsddDictionary, data: dict[str, Any]) -> BsddClassRelation:
    """Build a class relation; ``RelatedClassUri`` may be an internal class code."""
    data = dict(data)
    target = (data.get("RelatedClassUri") or data.pop("RelatedClassCode", None) or "").strip()
    data.pop("RelatedClassCode", None)
    if not target:
        raise OpError("Relation target must not be empty")
    if dict_utils.is_uri(target):
        data["RelatedClassUri"] = target
        code = internal_code(d, target, "class")
        if code and not data.get("RelatedClassName"):
            related = class_index(d).get(code)
            if related:
                data["RelatedClassName"] = related.Name
    else:
        related = class_index(d).get(target)
        if related is None:
            raise OpError(f"Class '{target}' not found")
        data["RelatedClassUri"] = class_uri(d, related)
        data["RelatedClassName"] = related.Name
    if data.get("RelationType") != "HasMaterial":
        data.pop("Fraction", None)
    if not d.UseOwnUri:
        data.pop("OwnedUri", None)
    return BsddClassRelation.model_validate(data)


def resolve_property_relation(d: BsddDictionary, data: dict[str, Any]) -> BsddPropertyRelation:
    data = dict(data)
    target = (data.get("RelatedPropertyUri") or data.pop("RelatedPropertyCode", None) or "").strip()
    data.pop("RelatedPropertyCode", None)
    if not target:
        raise OpError("Relation target must not be empty")
    if dict_utils.is_uri(target):
        data["RelatedPropertyUri"] = target
        code = internal_code(d, target, "prop")
        if code and not data.get("RelatedPropertyName"):
            related = property_index(d).get(code)
            if related:
                data["RelatedPropertyName"] = related.Name
    else:
        related = property_index(d).get(target)
        if related is None:
            raise OpError(f"Property '{target}' not found")
        data["RelatedPropertyUri"] = property_uri(d, related)
        data["RelatedPropertyName"] = related.Name
    if not d.UseOwnUri:
        data.pop("OwnedUri", None)
    return BsddPropertyRelation.model_validate(data)


def _rel_key(uri: str, rtype: str) -> tuple[str, str]:
    return (dict_utils.normalize_uri(uri) or "", rtype)


def sync_class_inverse(
    d: BsddDictionary,
    start: BsddClass,
    old: list[BsddClassRelation],
    new: list[BsddClassRelation],
) -> None:
    """Add/remove inverse relations on internal target classes for changed relations."""
    old_keys = {_rel_key(r.RelatedClassUri, r.RelationType) for r in old}
    new_keys = {_rel_key(r.RelatedClassUri, r.RelationType) for r in new}
    start_uri = start.OwnedUri or class_uri(d, start)
    index = class_index(d)
    for relations, mode in ((old, "remove"), (new, "add")):
        for rel in relations:
            key = _rel_key(rel.RelatedClassUri, rel.RelationType)
            if mode == "remove" and key in new_keys:
                continue
            if mode == "add" and key in old_keys:
                continue
            inverse = CLASS_INVERSE.get(rel.RelationType)
            code = internal_code(d, rel.RelatedClassUri, "class")
            end = index.get(code) if code else None
            if not inverse or end is None or end is start:
                continue
            existing = [
                cr
                for cr in end.ClassRelations
                if cr.RelationType == inverse
                and (same_uri(cr.RelatedClassUri, start_uri) or internal_code(d, cr.RelatedClassUri, "class") == start.Code)
            ]
            if mode == "add" and not existing:
                cr = BsddClassRelation(RelationType=inverse, RelatedClassUri=start_uri, RelatedClassName=start.Name)
                cr._set_parent(end)
                end.ClassRelations.append(cr)
            elif mode == "remove":
                for cr in existing:
                    end.ClassRelations.remove(cr)


def sync_property_inverse(
    d: BsddDictionary,
    start: BsddProperty,
    old: list[BsddPropertyRelation],
    new: list[BsddPropertyRelation],
) -> None:
    old_keys = {_rel_key(r.RelatedPropertyUri, r.RelationType) for r in old}
    new_keys = {_rel_key(r.RelatedPropertyUri, r.RelationType) for r in new}
    start_uri = start.OwnedUri or property_uri(d, start)
    index = property_index(d)
    for relations, mode in ((old, "remove"), (new, "add")):
        for rel in relations:
            key = _rel_key(rel.RelatedPropertyUri, rel.RelationType)
            if mode == "remove" and key in new_keys:
                continue
            if mode == "add" and key in old_keys:
                continue
            inverse = PROPERTY_INVERSE.get(rel.RelationType)
            code = internal_code(d, rel.RelatedPropertyUri, "prop")
            end = index.get(code) if code else None
            if not inverse or end is None or end is start:
                continue
            existing = [
                pr
                for pr in end.PropertyRelations
                if pr.RelationType == inverse
                and (same_uri(pr.RelatedPropertyUri, start_uri) or internal_code(d, pr.RelatedPropertyUri, "prop") == start.Code)
            ]
            if mode == "add" and not existing:
                pr = BsddPropertyRelation(RelationType=inverse, RelatedPropertyUri=start_uri, RelatedPropertyName=start.Name)
                pr._set_parent(end)
                end.PropertyRelations.append(pr)
            elif mode == "remove":
                for pr in existing:
                    end.PropertyRelations.remove(pr)


# --------------------------------------------------------------------------- group of properties


def gop_by_name(d: BsddDictionary, name: str) -> BsddClass | None:
    for c in d.Classes:
        if c.ClassType == GOP and c.Name == name:
            return c
    return None


def is_reference_to(d: BsddDictionary, relation: BsddClassRelation, target: BsddClass) -> bool:
    if relation.RelationType != "HasReference":
        return False
    if internal_code(d, relation.RelatedClassUri, "class") == target.Code:
        return True
    return bool(target.OwnedUri and same_uri(relation.RelatedClassUri, target.OwnedUri))


def classes_referencing(d: BsddDictionary, gop: BsddClass) -> list[BsddClass]:
    return [c for c in d.Classes if c is not gop and any(is_reference_to(d, cr, gop) for cr in c.ClassRelations)]


def linked_gop(d: BsddDictionary, bsdd_class: BsddClass, pset_name: str) -> BsddClass | None:
    """The internal GroupOfProperties class that ``pset_name`` of ``bsdd_class`` is linked to."""
    for cr in bsdd_class.ClassRelations:
        if cr.RelationType != "HasReference":
            continue
        code = internal_code(d, cr.RelatedClassUri, "class")
        target = class_index(d).get(code) if code else None
        if target is not None and target.ClassType == GOP and target.Name == pset_name:
            return target
    return None


def normalize_extras(ctx: Ctx) -> None:
    """Drop temporary property sets that became real or whose class is gone."""
    index = class_index(ctx.dictionary)
    cleaned: dict[str, list[str]] = {}
    for code, names in ctx.extras.temporary_psets.items():
        bsdd_class = index.get(code)
        if bsdd_class is None:
            continue
        real = {cp.PropertySet for cp in bsdd_class.ClassProperties}
        keep = []
        for n in names:
            if n and n not in real and n not in keep:
                keep.append(n)
        if keep:
            cleaned[code] = keep
    ctx.extras.temporary_psets = cleaned
    if ctx.extras.loin:
        from bsdd_web.services.loin import drop_dangling

        drop_dangling(ctx.extras.loin, set(index))


def add_temporary_pset(ctx: Ctx, class_code: str, name: str) -> None:
    names = ctx.extras.temporary_psets.setdefault(class_code, [])
    if name not in names:
        names.append(name)
