"""Operations on the Level of Information Need state (``Extras.loin``)."""

from __future__ import annotations

import uuid
from typing import Any

from bsdd_web.services import loin as L

from . import Ctx, OpError, op


def _state(ctx: Ctx) -> dict[str, Any]:
    return L.ensure_state(ctx.extras.loin)


def _find(items: list[dict[str, Any]], guid: str) -> dict[str, Any]:
    for item in items:
        if item["guid"] == guid:
            return item
    raise OpError("Entry not found")


def _name(name: str) -> str:
    name = (name or "").strip()
    if not name:
        raise OpError("Name must not be empty")
    return name


@op("loin.init")
def init(ctx: Ctx) -> None:
    _state(ctx)


@op("loin.reset")
def reset(ctx: Ctx) -> None:
    ctx.extras.loin = L.default_state()


@op("loin.add_purpose")
def add_purpose(ctx: Ctx, name: str) -> str:
    state = _state(ctx)
    guid = str(uuid.uuid4())
    state["purposes"].append({"guid": guid, "name": _name(name)})
    return guid


@op("loin.add_milestone")
def add_milestone(ctx: Ctx, name: str, date: str | None = None) -> str:
    state = _state(ctx)
    guid = str(uuid.uuid4())
    state["milestones"].append({"guid": guid, "name": _name(name), "date": date or None})
    return guid


@op("loin.rename")
def rename(ctx: Ctx, kind: str, guid: str, name: str) -> None:
    state = _state(ctx)
    _find(state[_kind(kind)], guid)["name"] = _name(name)


@op("loin.set_milestone_date")
def set_milestone_date(ctx: Ctx, guid: str, date: str | None) -> None:
    _find(_state(ctx)["milestones"], guid)["date"] = date or None


@op("loin.remove")
def remove(ctx: Ctx, kind: str, guid: str) -> None:
    state = _state(ctx)
    key = _kind(kind)
    if len(state[key]) <= 1:
        raise OpError("At least one entry is required")
    state[key] = [x for x in state[key] if x["guid"] != guid]
    if state.get("matrix") is not None:
        valid = set(L.all_spec_keys(state))
        state["matrix"] = [k for k in state["matrix"] if k in valid]
    L.drop_dangling(state, {c.Code for c in ctx.d.Classes})


@op("loin.reorder")
def reorder(ctx: Ctx, kind: str, order: list[str]) -> None:
    state = _state(ctx)
    key = _kind(kind)
    by_guid = {x["guid"]: x for x in state[key]}
    ordered = [by_guid[g] for g in order if g in by_guid]
    ordered.extend(x for x in state[key] if x["guid"] not in order)
    state[key] = ordered


def _kind(kind: str) -> str:
    if kind not in ("purpose", "milestone"):
        raise OpError("kind must be 'purpose' or 'milestone'")
    return f"{kind}s"


@op("loin.set_actor")
def set_actor(ctx: Ctx, which: str, data: dict[str, Any] | None) -> None:
    if which not in ("providing", "receiving"):
        raise OpError("which must be 'providing' or 'receiving'")
    state = _state(ctx)
    if not data:
        state[f"{which}_actor"] = None
        return
    old = state.get(f"{which}_actor") or {}
    actor = {k: (data.get(k) or None) for k in L.ACTOR_FIELDS}
    actor["guid"] = old.get("guid") or str(uuid.uuid4())
    if not actor["role"]:
        raise OpError("Role must not be empty")
    state[f"{which}_actor"] = actor


@op("loin.add_classes")
def add_classes(ctx: Ctx, codes: list[str]) -> None:
    L.add_classes(_state(ctx), ctx.d, codes)


@op("loin.remove_class")
def remove_class(ctx: Ctx, code: str) -> None:
    L.remove_class(_state(ctx), ctx.d, code)


@op("loin.set_class_included")
def set_class_included(ctx: Ctx, spec: str, codes: list[str], included: bool, recursive: bool = False) -> None:
    try:
        L.set_class_included(_state(ctx), ctx.d, spec, codes, included, recursive)
    except ValueError as exc:
        raise OpError(str(exc)) from exc


@op("loin.set_properties_included")
def set_properties_included(
    ctx: Ctx,
    spec: str,
    class_code: str,
    items: list[list[str]],
    included: bool,
) -> None:
    try:
        L.set_properties_included(_state(ctx), ctx.d, spec, class_code, items, included)
    except ValueError as exc:
        raise OpError(str(exc)) from exc


@op("loin.set_matrix")
def set_matrix(ctx: Ctx, keys: list[str], active: bool) -> None:
    """Tick / untick purpose × milestone combinations in the matrix."""
    try:
        L.set_matrix(_state(ctx), keys, active)
    except ValueError as exc:
        raise OpError(str(exc)) from exc


@op("loin.import_xml")
def import_xml(ctx: Ctx, xml: str) -> int:
    try:
        state = L.parse_loin_xml(xml, ctx.d)
    except Exception as exc:  # noqa: BLE001 - invalid xml is a user error
        raise OpError(f"Could not read LOIN XML: {exc}") from exc
    if not state["purposes"]:
        raise OpError("The file does not contain any specification")
    ctx.extras.loin = state
    return len(state["specs"])


@op("loin.set_pset_properties_included")
def set_pset_properties_included(ctx: Ctx, spec: str, items: list[list[str]], included: bool) -> int:
    """Toggle property sets / properties across all classes of the dictionary (pset view)."""
    try:
        return L.set_pset_properties_included(_state(ctx), ctx.d, spec, items, included)
    except ValueError as exc:
        raise OpError(str(exc)) from exc
