"""Strict inheritance for the web app.

The rules live in :mod:`bsdd_json.utils.inheritance_utils` (shared with the desktop app); this
module adapts them to the operation context and turns violations into :class:`OpError`.
"""

from __future__ import annotations

from bsdd_json import BsddClass, BsddClassProperty
from bsdd_json.utils import inheritance_utils as iu

from . import Ctx, OpError, op

KEY_FIELDS = iu.KEY_FIELDS
cp_key = iu.cp_key
gop_links = iu.gop_links
snapshot = iu.snapshot
Snapshot = iu.Snapshot

#: operations that replace the dictionary wholesale: no guard/propagation, only completion
WHOLESALE_OPS = {"dict.replace", "dict.patch", "project.restore", "inheritance.set_strict"}


def inherited_from(ctx: Ctx, c: BsddClass, cp: BsddClassProperty) -> BsddClass | None:
    if not ctx.extras.strict_inheritance:
        return None
    return iu.inherited_from(ctx.d, c, cp)


def propagate_and_guard(ctx: Ctx, before: Snapshot) -> None:
    try:
        iu.propagate_and_guard(ctx.d, before)
    except iu.InheritanceError as exc:
        raise OpError(str(exc)) from exc


def complete(ctx: Ctx) -> int:
    """Add missing inherited class properties to all children. Returns the number added."""
    return iu.complete(ctx.d)


def missing_count(ctx: Ctx) -> int:
    """How many class properties ``complete`` would add (without changing anything)."""
    return iu.missing_count(ctx.d)


@op("inheritance.set_strict")
def set_strict_inheritance(ctx: Ctx, enabled: bool) -> int:
    """Switch strict inheritance on/off. Switching on adds missing inherited class properties
    (returns how many)."""
    ctx.extras.strict_inheritance = bool(enabled)
    return complete(ctx) if enabled else 0
