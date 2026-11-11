"""Strict inheritance: every child class has all class properties of its parent class.

A class property is identified by its property set and the property it points to (its "key").
Children may change the values of inherited class properties (allowed values, unit, required, …)
but not remove them or change their key. When strict inheritance is on, after every operation:

1. changes of a parent's class properties are passed on to its descendants
   (removed → removed, property set / property changed → changed as well, values → copied into
   descendants that still had the parent's old value),
2. an operation that removes an inherited class property from a child is refused,
3. missing inherited class properties are added to the children.

Links to Groups of Properties (HasReference relations, "predefined property sets") are inherited
the same way: a child has every such link of its parent and cannot remove it.
"""

from __future__ import annotations

from typing import Any

from bsdd_json import BsddClass, BsddClassProperty, BsddClassRelation, BsddDictionary
from bsdd_json.utils import dictionary_utils as dict_utils

from . import Ctx, OpError, op
from .helpers import GOP, class_index, class_uri, internal_code, is_reference_to, merged, new_class_property, unique_code

KEY_FIELDS = ("PropertySet", "PropertyCode", "PropertyUri")

#: operations that replace the dictionary wholesale: no guard/propagation, only completion
WHOLESALE_OPS = {"dict.replace", "dict.patch", "project.restore", "inheritance.set_strict"}

Key = tuple[str, str]


def cp_key(d: BsddDictionary, cp: BsddClassProperty | dict[str, Any]) -> Key:
    get = cp.get if isinstance(cp, dict) else (lambda k: getattr(cp, k))
    code = get("PropertyCode")
    uri = get("PropertyUri")
    if not code and uri:
        code = internal_code(d, uri, "prop")
    ref = f"code:{code}" if code else f"uri:{dict_utils.normalize_uri(uri) if uri else ''}"
    return (get("PropertySet") or "", ref)


def _parent(index: dict[str, BsddClass], c: BsddClass) -> BsddClass | None:
    """The parent that passes on class properties (groups of properties take no part)."""
    if c.ClassType == GOP or not c.ParentClassCode:
        return None
    parent = index.get(c.ParentClassCode)
    if parent is None or parent.ClassType == GOP:
        return None
    return parent


def _top_down(d: BsddDictionary) -> list[tuple[BsddClass, BsddClass]]:
    """(child, parent) pairs, parents before their children."""
    index = class_index(d)
    children: dict[str, list[BsddClass]] = {}
    roots = []
    for c in d.Classes:
        p = _parent(index, c)
        if p is None:
            roots.append(c)
        else:
            children.setdefault(p.Code, []).append(c)
    out = []
    seen: set[str] = set()
    stack = list(reversed(roots))
    while stack:
        cur = stack.pop()
        if cur.Code in seen:
            continue
        seen.add(cur.Code)
        for child in children.get(cur.Code, []):
            out.append((child, cur))
            stack.append(child)
    return out


def gop_links(d: BsddDictionary, c: BsddClass, gops: list[BsddClass] | None = None) -> set[str]:
    """Codes of the Groups of Properties ``c`` is linked to (HasReference)."""
    if gops is None:
        gops = [g for g in d.Classes if g.ClassType == GOP]
    return {g.Code for g in gops if g is not c and any(is_reference_to(d, cr, g) for cr in c.ClassRelations)}


Snapshot = dict[str, tuple[str | None, dict[Key, dict[str, Any]], set[str]]]


def snapshot(d: BsddDictionary) -> Snapshot:
    gops = [g for g in d.Classes if g.ClassType == GOP]
    return {
        c.Code: (
            c.ParentClassCode,
            {cp_key(d, cp): cp.model_dump(mode="json") for cp in c.ClassProperties},
            gop_links(d, c, gops),
        )
        for c in d.Classes
    }


def inherited_from(ctx: Ctx, c: BsddClass, cp: BsddClassProperty) -> BsddClass | None:
    if not ctx.extras.strict_inheritance:
        return None
    parent = _parent(class_index(ctx.d), c)
    if parent is None:
        return None
    key = cp_key(ctx.d, cp)
    return parent if any(cp_key(ctx.d, x) == key for x in parent.ClassProperties) else None


def propagate_and_guard(ctx: Ctx, before: Snapshot) -> None:
    d = ctx.d
    index = class_index(d)
    gops = [g for g in d.Classes if g.ClassType == GOP]
    for child, parent in _top_down(d):
        b_child = before.get(child.Code)
        b_parent = before.get(parent.Code)
        if b_child is None or b_parent is None or b_child[0] != parent.Code:
            continue  # new or moved class: only completed below
        parent_before = b_parent[1]
        parent_now = {cp_key(d, cp): cp for cp in parent.ClassProperties}

        for key, old in parent_before.items():
            target = next((cp for cp in child.ClassProperties if cp_key(d, cp) == key), None)
            if target is None:
                continue
            if key in parent_now:
                # values changed in the parent: copy into the child where it still had the old value
                new = parent_now[key].model_dump(mode="json")
                mine = target.model_dump(mode="json")
                changes = {
                    f: v
                    for f, v in new.items()
                    if f not in KEY_FIELDS and f != "Code" and old.get(f) != v and mine.get(f) == old.get(f)
                }
                if changes:
                    _replace(child, target, changes)
                continue
            # key gone in the parent: renamed (same class property code) or removed
            renamed = next(
                (cp for cp in parent.ClassProperties if cp.Code == old.get("Code") and cp_key(d, cp) not in parent_before),
                None,
            )
            if renamed is not None:
                _replace(child, target, {f: getattr(renamed, f) for f in KEY_FIELDS})
            else:
                child.ClassProperties.remove(target)

        # links to Groups of Properties: removed in the parent -> removed in the child
        parent_links = gop_links(d, parent, gops)
        for code in b_parent[2] - parent_links:
            gop = index.get(code)
            if gop is not None:
                child.ClassRelations[:] = [cr for cr in child.ClassRelations if not is_reference_to(d, cr, gop)]
        child_links = gop_links(d, child, gops)
        for code in (b_child[2] - child_links) & parent_links & b_parent[2]:
            name = index[code].Name if code in index else code
            raise OpError(
                f"The link to the predefined property set '{name}' is inherited from '{parent.Name}' "
                "(strict inheritance) and can only be removed in the parent class"
            )

        # an inherited class property must not disappear from the child
        child_keys = {cp_key(d, cp) for cp in child.ClassProperties}
        for key, old in b_child[1].items():
            if key not in child_keys and key in parent_now and key in parent_before:
                raise OpError(
                    f"'{old.get('Code')}' is inherited from '{parent.Name}' (strict inheritance): "
                    "it can only be removed, moved to another property set or pointed to another "
                    "property in the parent class"
                )


def _replace(owner: BsddClass, cp: BsddClassProperty, changes: dict[str, Any]) -> None:
    i = owner.ClassProperties.index(cp)
    owner.ClassProperties[i] = new_class_property(owner, merged(cp, changes))


def complete(ctx: Ctx) -> int:
    """Add missing inherited class properties to all children. Returns the number added."""
    d = ctx.d
    added = 0
    gops = [g for g in d.Classes if g.ClassType == GOP]
    index = class_index(d)
    for child, parent in _top_down(d):
        # links to Groups of Properties
        for code in gop_links(d, parent, gops) - gop_links(d, child, gops):
            gop = index[code]
            rel = BsddClassRelation(RelationType="HasReference", RelatedClassUri=class_uri(d, gop), RelatedClassName=gop.Name)
            rel._set_parent(child)
            child.ClassRelations.append(rel)
        have = {cp_key(d, cp) for cp in child.ClassProperties}
        codes = [cp.Code for cp in child.ClassProperties]
        for cp in parent.ClassProperties:
            key = cp_key(d, cp)
            if key in have:
                continue
            data = cp.model_dump(mode="json")
            data.pop("OwnedUri", None)
            data["Code"] = unique_code(cp.Code, codes)
            codes.append(data["Code"])
            child.ClassProperties.append(new_class_property(child, data))
            have.add(key)
            added += 1
    return added


def missing_count(ctx: Ctx) -> int:
    """How many class properties ``complete`` would add (without changing anything)."""
    copy = Ctx(dictionary=BsddDictionary.model_validate(ctx.d.model_dump(mode="json")), extras=ctx.extras)
    return complete(copy)


@op("inheritance.set_strict")
def set_strict_inheritance(ctx: Ctx, enabled: bool) -> int:
    """Switch strict inheritance on/off. Switching on adds missing inherited class properties
    (returns how many)."""
    ctx.extras.strict_inheritance = bool(enabled)
    return complete(ctx) if enabled else 0
