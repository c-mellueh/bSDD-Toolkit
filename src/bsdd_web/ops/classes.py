from __future__ import annotations

from typing import Any

from bsdd_json import BsddClass, BsddProperty
from bsdd_json.utils import dictionary_utils as dict_utils

from . import Ctx, OpError, op
from .helpers import (
    GOP,
    attach_class,
    attach_property,
    class_index,
    class_uri,
    classes_referencing,
    descendants,
    get_class,
    internal_code,
    merged,
    property_index,
    require_code,
    resolve_class_relation,
    same_uri,
    sync_class_inverse,
    unique_code,
)


def _validate_class(d, data: dict[str, Any], *, own_code: str | None = None) -> BsddClass:
    code = require_code(data.get("Code"))
    data["Code"] = code
    if not (data.get("Name") or "").strip():
        raise OpError("Name must not be empty")
    if code != own_code and code in class_index(d):
        raise OpError(f"Code '{code}' exists already")
    parent = data.get("ParentClassCode")
    if parent == "":
        data["ParentClassCode"] = None
    return BsddClass.model_validate(data)


@op("class.create")
def create_class(ctx: Ctx, data: dict[str, Any], parent_code: str | None = None) -> str:
    d = ctx.d
    data = dict(data)
    if not data.get("Code") and data.get("Name"):
        data["Code"] = unique_code(dict_utils.slugify(data["Name"]), class_index(d))
    if parent_code is not None:
        data["ParentClassCode"] = parent_code or None
    if data.get("ParentClassCode"):
        get_class(d, data["ParentClassCode"])
    relations = data.pop("ClassRelations", None) or []
    new = _validate_class(d, data)
    attach_class(d, new)
    d.Classes.append(new)
    if relations:
        new.ClassRelations = [resolve_class_relation(d, r) for r in relations]
        attach_class(d, new)
        sync_class_inverse(d, new, [], new.ClassRelations)
    return new.Code


@op("class.update")
def update_class(ctx: Ctx, code: str, data: dict[str, Any]) -> str:
    """Update fields of a class including cascades for code / name / relation changes."""
    d = ctx.d
    old = get_class(d, code)
    index = d.Classes.index(old)
    old_uri = class_uri(d, old)
    old_relations = list(old.ClassRelations)
    data = dict(data)
    relations_data = data.pop("ClassRelations", None)
    data.pop("ClassProperties", None)  # edited through class-property operations

    values = merged(old, data)
    if values.get("ParentClassCode"):
        if values["ParentClassCode"] == values["Code"] or values["ParentClassCode"] in descendants(d, code):
            raise OpError("A class cannot be its own parent")
        get_class(d, values["ParentClassCode"])
    new = _validate_class(d, values, own_code=code)
    if relations_data is not None:
        new.ClassRelations = [resolve_class_relation(d, r) for r in relations_data]
    attach_class(d, new)
    d.Classes[index] = new

    if new.Code != code:
        new_uri = class_uri(d, new)
        for child in d.Classes:
            if child.ParentClassCode == code:
                child.ParentClassCode = new.Code
        for c in d.Classes:
            for cr in c.ClassRelations:
                if same_uri(cr.RelatedClassUri, old_uri) or internal_code(d, cr.RelatedClassUri, "class") == code:
                    cr.RelatedClassUri = new_uri
        temp = ctx.extras.temporary_psets.pop(code, None)
        if temp:
            ctx.extras.temporary_psets[new.Code] = temp
        from bsdd_web.services.loin import rename_class

        rename_class(ctx.extras.loin, code, new.Code)

    if new.Name != old.Name:
        for c in d.Classes:
            for cr in c.ClassRelations:
                if internal_code(d, cr.RelatedClassUri, "class") == new.Code:
                    cr.RelatedClassName = new.Name
        if new.ClassType == GOP and old.ClassType == GOP:
            _rename_gop_psets(ctx, new, old.Name, new.Name)

    if relations_data is not None:
        sync_class_inverse(d, new, old_relations, new.ClassRelations)
    return new.Code


def _rename_gop_psets(ctx: Ctx, gop: BsddClass, old_name: str, new_name: str) -> None:
    for cp in gop.ClassProperties:
        if cp.PropertySet == old_name:
            cp.PropertySet = new_name
    for c in classes_referencing(ctx.d, gop):
        for cp in c.ClassProperties:
            if cp.PropertySet == old_name:
                cp.PropertySet = new_name
        temp = ctx.extras.temporary_psets.get(c.Code, [])
        ctx.extras.temporary_psets[c.Code] = [new_name if n == old_name else n for n in temp]


@op("class.delete")
def delete_classes(ctx: Ctx, codes: list[str], recursive: bool = False) -> list[str]:
    d = ctx.d
    index = class_index(d)
    to_delete: set[str] = set()
    for code in codes:
        if code not in index:
            continue
        to_delete.add(code)
        if recursive:
            to_delete |= descendants(d, code)
    if not to_delete:
        return []
    deleted_uris = {code: class_uri(d, index[code]) for code in to_delete}

    # re-parent surviving children to the nearest surviving ancestor
    for c in d.Classes:
        if c.Code in to_delete or c.ParentClassCode not in to_delete:
            continue
        parent = c.ParentClassCode
        while parent in to_delete:
            parent = index[parent].ParentClassCode
        c.ParentClassCode = parent

    d.Classes[:] = [c for c in d.Classes if c.Code not in to_delete]

    # remove dangling relations that point to deleted classes
    for c in d.Classes:
        c.ClassRelations[:] = [
            cr
            for cr in c.ClassRelations
            if internal_code(d, cr.RelatedClassUri, "class") not in to_delete
            and not any(same_uri(cr.RelatedClassUri, u) for u in deleted_uris.values())
        ]
    for code in to_delete:
        ctx.extras.temporary_psets.pop(code, None)
    return sorted(to_delete)


@op("class.move")
def move_classes(
    ctx: Ctx,
    codes: list[str],
    parent_code: str | None = None,
    before_code: str | None = None,
) -> None:
    """Move classes below ``parent_code`` (None = root), optionally before a sibling."""
    d = ctx.d
    index = class_index(d)
    if parent_code:
        get_class(d, parent_code)
    moving = [index[c] for c in codes if c in index]
    for c in moving:
        if parent_code and (parent_code == c.Code or parent_code in descendants(d, c.Code)):
            raise OpError(f"Cannot move '{c.Code}' into itself or one of its children")
    for c in moving:
        c.ParentClassCode = parent_code or None

    # keep list order meaningful: children are shown in list order
    remaining = [c for c in d.Classes if c not in moving]
    if before_code and before_code in index and index[before_code] not in moving:
        pos = remaining.index(index[before_code])
    else:
        pos = len(remaining)
    d.Classes[:] = remaining[:pos] + moving + remaining[pos:]


@op("class.group")
def group_classes(ctx: Ctx, codes: list[str], name: str, code: str | None = None) -> str:
    """Create a new class under the lowest shared parent and move ``codes`` into it."""
    d = ctx.d
    index = class_index(d)
    selection = [index[c] for c in codes if c in index]
    if not selection:
        raise OpError("Nothing selected")
    name = (name or "").strip()
    if not name:
        raise OpError("Name must not be empty")
    selected_codes = {c.Code for c in selection}

    def ancestors(c: BsddClass) -> list[str]:
        out = []
        seen = set()
        cur = c.ParentClassCode
        while cur and cur not in seen:
            seen.add(cur)
            out.append(cur)
            cur = index[cur].ParentClassCode if cur in index else None
        return out

    # top-level selected classes only (ignore those whose ancestor is selected too)
    tops = [c for c in selection if not (set(ancestors(c)) & selected_codes)]
    common: list[str] | None = None
    for c in tops:
        anc = ancestors(c)
        common = anc if common is None else [a for a in common if a in anc]
    parent = common[0] if common else None

    new_code = code.strip() if code else unique_code(dict_utils.slugify(name), index)
    if new_code in index:
        raise OpError(f"Code '{new_code}' exists already")
    group = BsddClass(Code=new_code, Name=name, ClassType=tops[0].ClassType, ParentClassCode=parent)
    attach_class(d, group)
    d.Classes.insert(d.Classes.index(tops[0]), group)
    for c in tops:
        c.ParentClassCode = new_code
    return new_code


@op("class.paste")
def paste_classes(ctx: Ctx, payload: dict[str, Any], parent_code: str | None = None) -> list[str]:
    """Insert copied classes (and referenced properties) with unique codes."""
    d = ctx.d
    if parent_code:
        get_class(d, parent_code)
    raw_classes = payload.get("classes") or []
    if not raw_classes:
        raise OpError("Clipboard does not contain classes")
    payload_codes = {c.get("Code") for c in raw_classes}

    def depth(c: dict[str, Any]) -> int:
        lookup = {x.get("Code"): x for x in raw_classes}
        n, cur, seen = 0, c.get("ParentClassCode"), set()
        while cur in lookup and cur not in seen:
            seen.add(cur)
            n += 1
            cur = lookup[cur].get("ParentClassCode")
        return n

    existing = set(class_index(d))
    code_map: dict[str, str] = {}
    new_codes: list[str] = []
    for raw in sorted(raw_classes, key=depth):
        data = dict(raw)
        old_code = data.get("Code") or dict_utils.slugify(data.get("Name", "class"))
        new_code = unique_code(old_code, existing)
        existing.add(new_code)
        code_map[old_code] = new_code
        data["Code"] = new_code
        old_parent = data.get("ParentClassCode")
        data["ParentClassCode"] = code_map.get(old_parent) if old_parent in payload_codes else (parent_code or None)
        data.pop("OwnedUri", None)
        new = BsddClass.model_validate(data)
        attach_class(d, new)
        d.Classes.append(new)
        new_codes.append(new_code)

    props = property_index(d)
    for raw in payload.get("properties") or []:
        if raw.get("Code") and raw["Code"] not in props:
            prop = BsddProperty.model_validate(raw)
            attach_property(d, prop)
            d.Properties.append(prop)
            props[prop.Code] = prop
    return new_codes


@op("relation.add")
def add_relation(ctx: Ctx, kind: str, code: str, relation: dict[str, Any]) -> None:
    """Add a single relation to a class or property (used by the graph view)."""
    from .helpers import get_property, resolve_property_relation, sync_property_inverse

    d = ctx.d
    if kind == "class":
        start = get_class(d, code)
        rel = resolve_class_relation(d, relation)
        if any(same_uri(r.RelatedClassUri, rel.RelatedClassUri) and r.RelationType == rel.RelationType for r in start.ClassRelations):
            raise OpError("Relation exists already")
        rel._set_parent(start)
        old = list(start.ClassRelations)
        start.ClassRelations.append(rel)
        sync_class_inverse(d, start, old, start.ClassRelations)
    elif kind == "property":
        start = get_property(d, code)
        rel = resolve_property_relation(d, relation)
        if any(same_uri(r.RelatedPropertyUri, rel.RelatedPropertyUri) and r.RelationType == rel.RelationType for r in start.PropertyRelations):
            raise OpError("Relation exists already")
        rel._set_parent(start)
        old = list(start.PropertyRelations)
        start.PropertyRelations.append(rel)
        sync_property_inverse(d, start, old, start.PropertyRelations)
    else:
        raise OpError(f"Unknown relation kind '{kind}'")


@op("relation.remove")
def remove_relation(ctx: Ctx, kind: str, code: str, index: int) -> None:
    from .helpers import get_property, sync_property_inverse

    d = ctx.d
    if kind == "class":
        start = get_class(d, code)
        if not 0 <= index < len(start.ClassRelations):
            raise OpError("Relation not found")
        old = list(start.ClassRelations)
        start.ClassRelations.pop(index)
        sync_class_inverse(d, start, old, start.ClassRelations)
    elif kind == "property":
        start = get_property(d, code)
        if not 0 <= index < len(start.PropertyRelations):
            raise OpError("Relation not found")
        old = list(start.PropertyRelations)
        start.PropertyRelations.pop(index)
        sync_property_inverse(d, start, old, start.PropertyRelations)
    else:
        raise OpError(f"Unknown relation kind '{kind}'")

