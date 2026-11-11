"""Strict inheritance: every child class has all class properties of its parent class.

A class property is identified by its property set and the property it points to (its "key").
Children may change the values of inherited class properties (allowed values, unit, required, …)
but not remove them or change their key. When strict inheritance is on, after every change:

1. changes of a parent's class properties are passed on to its descendants
   (removed → removed, property set / property changed → changed as well, values → copied into
   descendants that still had the parent's old value)  -> :func:`propagate_and_guard`,
2. a change that removed an inherited class property from a child is refused
   (:class:`InheritanceError`)                          -> :func:`propagate_and_guard`,
3. missing inherited class properties are added to the children -> :func:`complete`.

Links to Groups of Properties (HasReference relations, "predefined property sets") are inherited
the same way: a child has every such link of its parent and cannot remove it.

Groups of Properties themselves take no part in inheritance.

Used by the web app (``bsdd_web.ops.inheritance``) and the desktop app (``bsdd_gui``).
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from bsdd_json.models import BsddClass, BsddClassProperty, BsddClassRelation, BsddDictionary
from bsdd_json.utils import build_unique_code
from bsdd_json.utils import dictionary_utils as dict_utils

GOP = "GroupOfProperties"
KEY_FIELDS = ("PropertySet", "PropertyCode", "PropertyUri")

Key = tuple[str, str]
#: class code -> (ParentClassCode, {key: class property dump}, codes of linked Groups of Properties)
Snapshot = dict[str, tuple[str | None, dict[Key, dict[str, Any]], set[str]]]


class InheritanceError(ValueError):
    """A change would remove something a child class inherits from its parent."""


# --------------------------------------------------------------------------- helpers


def _namespace(d: BsddDictionary) -> str:
    return f"{d.OrganizationCode}/{d.DictionaryCode}".lower()


def _internal_code(d: BsddDictionary, uri: str | None, kind: str) -> str | None:
    """The code if ``uri`` points to a class/property of this dictionary (any version)."""
    if not uri or not dict_utils.is_uri(uri):
        return None
    parsed = dict_utils.parse_bsdd_url(uri)
    if (parsed.get("namespace") or "").lower() != _namespace(d):
        return None
    rtype = parsed.get("resource_type")
    if kind == "class" and rtype != "class":
        return None
    if kind == "prop" and rtype not in ("prop", "property"):
        return None
    return parsed.get("resource_id")


def _class_uri(d: BsddDictionary, bsdd_class: BsddClass) -> str:
    data = {
        "namespace": [d.OrganizationCode, d.DictionaryCode],
        "version": d.DictionaryVersion,
        "resource_type": "class",
        "resource_id": bsdd_class.Code,
    }
    if d.UseOwnUri and d.DictionaryUri:
        parsed = urlparse(d.DictionaryUri)
        data["host"] = parsed.netloc or d.DictionaryUri.strip("/")
    return dict_utils.build_bsdd_url(data)


def _is_reference_to(d: BsddDictionary, relation: BsddClassRelation, target: BsddClass) -> bool:
    if relation.RelationType != "HasReference":
        return False
    if _internal_code(d, relation.RelatedClassUri, "class") == target.Code:
        return True
    return bool(target.OwnedUri and dict_utils.normalize_uri(relation.RelatedClassUri) == dict_utils.normalize_uri(target.OwnedUri))


def _new_class_property(owner: BsddClass, data: dict[str, Any]) -> BsddClassProperty:
    cp = BsddClassProperty.model_validate(data)
    cp._set_parent(owner)
    return cp


def _replace(owner: BsddClass, cp: BsddClassProperty, changes: dict[str, Any]) -> None:
    i = owner.ClassProperties.index(cp)
    data = cp.model_dump(mode="json")
    data.update(changes)
    owner.ClassProperties[i] = _new_class_property(owner, data)


def _gops(d: BsddDictionary) -> list[BsddClass]:
    return [g for g in d.Classes if g.ClassType == GOP]


# --------------------------------------------------------------------------- public API


def cp_key(d: BsddDictionary, cp: BsddClassProperty | dict[str, Any]) -> Key:
    get = cp.get if isinstance(cp, dict) else (lambda k: getattr(cp, k))
    code = get("PropertyCode")
    uri = get("PropertyUri")
    if not code and uri:
        code = _internal_code(d, uri, "prop")
    ref = f"code:{code}" if code else f"uri:{dict_utils.normalize_uri(uri) if uri else ''}"
    return (get("PropertySet") or "", ref)


def parent_of(d: BsddDictionary, c: BsddClass, index: dict[str, BsddClass] | None = None) -> BsddClass | None:
    """The parent that passes on class properties (Groups of Properties take no part)."""
    if c.ClassType == GOP or not c.ParentClassCode:
        return None
    if index is None:
        index = {x.Code: x for x in d.Classes}
    parent = index.get(c.ParentClassCode)
    if parent is None or parent.ClassType == GOP:
        return None
    return parent


def top_down(d: BsddDictionary) -> list[tuple[BsddClass, BsddClass]]:
    """(child, parent) pairs, parents before their children."""
    index = {c.Code: c for c in d.Classes}
    children: dict[str, list[BsddClass]] = {}
    roots = []
    for c in d.Classes:
        p = parent_of(d, c, index)
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
        gops = _gops(d)
    return {g.Code for g in gops if g is not c and any(_is_reference_to(d, cr, g) for cr in c.ClassRelations)}


def snapshot(d: BsddDictionary) -> Snapshot:
    gops = _gops(d)
    return {
        c.Code: (
            c.ParentClassCode,
            {cp_key(d, cp): cp.model_dump(mode="json") for cp in c.ClassProperties},
            gop_links(d, c, gops),
        )
        for c in d.Classes
    }


def inherited_from(d: BsddDictionary, c: BsddClass, cp: BsddClassProperty) -> BsddClass | None:
    """The parent ``cp`` is inherited from (None if it is the child's own class property)."""
    parent = parent_of(d, c)
    if parent is None:
        return None
    key = cp_key(d, cp)
    return parent if any(cp_key(d, x) == key for x in parent.ClassProperties) else None


def inherited_psets(d: BsddDictionary, c: BsddClass) -> set[str]:
    """Names of the property sets ``c`` inherits class properties for."""
    parent = parent_of(d, c)
    if parent is None:
        return set()
    return {cp.PropertySet for cp in parent.ClassProperties if cp.PropertySet}


def propagate_and_guard(d: BsddDictionary, before: Snapshot, raise_errors: bool = True) -> list[str]:
    """Pass the changes made since ``before`` on from parents to children.

    An inherited class property / link that disappeared from a child raises
    :class:`InheritanceError` (``raise_errors``) or is reported in the returned list.
    """
    index = {c.Code: c for c in d.Classes}
    gops = _gops(d)
    errors: list[str] = []

    def fail(message: str) -> None:
        if raise_errors:
            raise InheritanceError(message)
        errors.append(message)

    for child, parent in top_down(d):
        b_child = before.get(child.Code)
        b_parent = before.get(parent.Code)
        if b_child is None or b_parent is None or b_child[0] != parent.Code:
            continue  # new or moved class: only completed
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
                    f: v for f, v in new.items() if f not in KEY_FIELDS and f != "Code" and old.get(f) != v and mine.get(f) == old.get(f)
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
                child.ClassRelations[:] = [cr for cr in child.ClassRelations if not _is_reference_to(d, cr, gop)]
        child_links = gop_links(d, child, gops)
        for code in sorted((b_child[2] - child_links) & parent_links & b_parent[2]):
            name = index[code].Name if code in index else code
            fail(
                f"The link to the predefined property set '{name}' is inherited from '{parent.Name}' "
                "(strict inheritance) and can only be removed in the parent class"
            )

        # an inherited class property must not disappear from the child
        child_keys = {cp_key(d, cp) for cp in child.ClassProperties}
        for key, old in b_child[1].items():
            if key not in child_keys and key in parent_now and key in parent_before:
                fail(
                    f"'{old.get('Code')}' is inherited from '{parent.Name}' (strict inheritance): "
                    "it can only be removed, moved to another property set or pointed to another "
                    "property in the parent class"
                )
    return errors


def complete(d: BsddDictionary) -> int:
    """Add missing inherited links and class properties to all children.

    Returns the number of class properties added."""
    added = 0
    gops = _gops(d)
    index = {c.Code: c for c in d.Classes}
    for child, parent in top_down(d):
        for code in sorted(gop_links(d, parent, gops) - gop_links(d, child, gops)):
            gop = index[code]
            rel = BsddClassRelation(RelationType="HasReference", RelatedClassUri=_class_uri(d, gop), RelatedClassName=gop.Name)
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
            data["Code"] = build_unique_code(cp.Code, codes)
            codes.append(data["Code"])
            child.ClassProperties.append(_new_class_property(child, data))
            have.add(key)
            added += 1
    return added


def missing_count(d: BsddDictionary) -> int:
    """How many class properties :func:`complete` would add (without changing anything)."""
    return complete(BsddDictionary.model_validate(d.model_dump(mode="json")))
