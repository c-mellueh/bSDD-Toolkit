"""Minimal JSON-Patch (RFC 6902 subset: add/remove/replace) diff and apply.

The diff short-circuits on equal subtrees (C-level ``==``), which keeps it fast for
large documents where a single operation only touches a few entries.
"""

from __future__ import annotations

import copy
from typing import Any

Patch = list[dict[str, Any]]


class PatchConflict(Exception):
    """Raised when a patch cannot be applied to the current document."""


def _escape(token: str | int) -> str:
    return str(token).replace("~", "~0").replace("/", "~1")


def _unescape(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def _join(path: str, token: str | int) -> str:
    return f"{path}/{_escape(token)}"


def diff(src: Any, dst: Any, path: str = "") -> Patch:
    """Return a patch that transforms ``src`` into ``dst``."""
    if src == dst:
        return []
    if isinstance(src, dict) and isinstance(dst, dict):
        ops: Patch = []
        for key in src:
            if key not in dst:
                ops.append({"op": "remove", "path": _join(path, key)})
        for key, value in dst.items():
            if key not in src:
                ops.append({"op": "add", "path": _join(path, key), "value": value})
            else:
                ops.extend(diff(src[key], value, _join(path, key)))
        return ops
    if isinstance(src, list) and isinstance(dst, list):
        return _diff_lists(src, dst, path)
    return [{"op": "replace", "path": path, "value": dst}]


def _diff_lists(src: list, dst: list, path: str) -> Patch:
    n_src, n_dst = len(src), len(dst)
    prefix = 0
    while prefix < n_src and prefix < n_dst and src[prefix] == dst[prefix]:
        prefix += 1
    suffix = 0
    while (
        suffix < n_src - prefix
        and suffix < n_dst - prefix
        and src[n_src - 1 - suffix] == dst[n_dst - 1 - suffix]
    ):
        suffix += 1
    src_mid = src[prefix : n_src - suffix]
    dst_mid = dst[prefix : n_dst - suffix]
    ops: Patch = []

    # Pure insertion / deletion of a contiguous block (very common: add or remove one item)
    if not src_mid:
        for i, value in enumerate(dst_mid):
            ops.append({"op": "add", "path": _join(path, prefix + i), "value": value})
        return ops
    if not dst_mid:
        for i in reversed(range(len(src_mid))):
            ops.append({"op": "remove", "path": _join(path, prefix + i)})
        return ops

    # Single element moved (e.g. reordering): detect remove+insert of an identical item
    if len(src_mid) == len(dst_mid) and len(src_mid) > 2:
        if src_mid[0] == dst_mid[-1] and src_mid[1:] == dst_mid[:-1]:
            return [
                {"op": "remove", "path": _join(path, prefix)},
                {"op": "add", "path": _join(path, prefix + len(dst_mid) - 1), "value": src_mid[0]},
            ]
        if src_mid[-1] == dst_mid[0] and src_mid[:-1] == dst_mid[1:]:
            return [
                {"op": "remove", "path": _join(path, prefix + len(src_mid) - 1)},
                {"op": "add", "path": _join(path, prefix), "value": src_mid[-1]},
            ]

    common = min(len(src_mid), len(dst_mid))
    for i in range(common):
        ops.extend(diff(src_mid[i], dst_mid[i], _join(path, prefix + i)))
    if len(src_mid) > common:
        for i in reversed(range(common, len(src_mid))):
            ops.append({"op": "remove", "path": _join(path, prefix + i)})
    else:
        for i in range(common, len(dst_mid)):
            ops.append({"op": "add", "path": _join(path, prefix + i), "value": dst_mid[i]})
    return ops


def _split(path: str) -> list[str]:
    if path == "":
        return []
    if not path.startswith("/"):
        raise PatchConflict(f"invalid path {path!r}")
    return [_unescape(t) for t in path[1:].split("/")]


def _resolve_parent(doc: Any, tokens: list[str]) -> Any:
    target = doc
    for token in tokens[:-1]:
        if isinstance(target, list):
            try:
                target = target[int(token)]
            except (ValueError, IndexError) as exc:
                raise PatchConflict(f"index {token} out of range") from exc
        elif isinstance(target, dict):
            if token not in target:
                raise PatchConflict(f"missing key {token}")
            target = target[token]
        else:
            raise PatchConflict("cannot traverse scalar")
    return target


def get_value(doc: Any, path: str) -> Any:
    tokens = _split(path)
    if not tokens:
        return doc
    parent = _resolve_parent(doc, tokens)
    last = tokens[-1]
    if isinstance(parent, list):
        try:
            return parent[int(last)]
        except (ValueError, IndexError) as exc:
            raise PatchConflict(f"index {last} out of range") from exc
    if isinstance(parent, dict):
        if last not in parent:
            raise PatchConflict(f"missing key {last}")
        return parent[last]
    raise PatchConflict("cannot traverse scalar")


def apply(doc: Any, patch: Patch, *, in_place: bool = False) -> Any:
    """Apply ``patch`` to ``doc`` and return the result."""
    if not in_place:
        doc = copy.deepcopy(doc)
    for op in patch:
        tokens = _split(op["path"])
        kind = op["op"]
        if not tokens:
            if kind in ("add", "replace"):
                doc = copy.deepcopy(op["value"])
                continue
            raise PatchConflict("cannot remove root")
        parent = _resolve_parent(doc, tokens)
        last = tokens[-1]
        if isinstance(parent, list):
            index = len(parent) if last == "-" else int(last)
            if kind == "add":
                if index > len(parent):
                    raise PatchConflict("add index out of range")
                parent.insert(index, copy.deepcopy(op["value"]))
            elif kind == "remove":
                if index >= len(parent):
                    raise PatchConflict("remove index out of range")
                parent.pop(index)
            elif kind == "replace":
                if index >= len(parent):
                    raise PatchConflict("replace index out of range")
                parent[index] = copy.deepcopy(op["value"])
        elif isinstance(parent, dict):
            if kind in ("add", "replace"):
                if kind == "replace" and last not in parent:
                    raise PatchConflict(f"replace of missing key {last}")
                parent[last] = copy.deepcopy(op["value"])
            elif kind == "remove":
                if last not in parent:
                    raise PatchConflict(f"remove of missing key {last}")
                del parent[last]
        else:
            raise PatchConflict("cannot modify scalar")
    return doc


def make_guards(after: Any, inverse: Patch, forward: Patch) -> list[Any]:
    """Record what each step of ``inverse`` expects to find, starting from ``after``.

    ``after`` is modified temporarily and restored by re-applying ``forward``.
    The guards are used by :func:`apply_guarded` to make sure an undo only
    happens if nobody changed the affected data in the meantime.
    """
    guards: list[Any] = []
    for op in inverse:
        guards.append(_expectation(after, op))
        apply(after, [op], in_place=True)
    apply(after, forward, in_place=True)
    return guards


def _expectation(doc: Any, op: dict[str, Any]) -> Any:
    tokens = _split(op["path"])
    if op["op"] == "add":
        parent = _resolve_parent(doc, tokens) if tokens else None
        if isinstance(parent, list):
            return {"len": len(parent)}
        return {"absent": True}
    return {"value": copy.deepcopy(get_value(doc, op["path"]))}


def apply_guarded(doc: Any, patch: Patch, guards: list[Any]) -> Any:
    """Apply ``patch`` to a copy of ``doc`` if every guard holds, else raise PatchConflict."""
    work = copy.deepcopy(doc)
    for op, guard in zip(patch, guards, strict=True):
        tokens = _split(op["path"])
        if "len" in guard:
            parent = _resolve_parent(work, tokens)
            if not isinstance(parent, list) or len(parent) != guard["len"]:
                raise PatchConflict("list changed")
        elif "absent" in guard:
            parent = _resolve_parent(work, tokens)
            if not isinstance(parent, dict) or tokens[-1] in parent:
                raise PatchConflict("key exists")
        elif get_value(work, op["path"]) != guard["value"]:
            raise PatchConflict("value changed")
        apply(work, [op], in_place=True)
    return work
