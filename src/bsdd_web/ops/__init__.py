"""Domain operations on a project document.

Every operation is a plain function ``fn(ctx, **args)`` registered under a name such as
``"class.update"``. Operations mutate ``ctx.dictionary`` / ``ctx.extras`` in place and may
return a JSON-serialisable result. Invalid input raises :class:`OpError`; the caller is
responsible for rolling back partial changes.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from bsdd_json import BsddDictionary
from pydantic import BaseModel, Field, ValidationError


class OpError(Exception):
    """User-facing error raised by an operation."""


class Extras(BaseModel):
    """Project data that is not part of the bSDD JSON itself."""

    #: empty property sets that only exist in the editor, keyed by class code
    temporary_psets: dict[str, list[str]] = Field(default_factory=dict)
    #: Level of Information Need state (see services.loin)
    loin: dict[str, Any] = Field(default_factory=dict)
    #: remembered settings of export dialogs, keyed by exporter name
    export_settings: dict[str, Any] = Field(default_factory=dict)
    #: every child class has all class properties of its parent (see ops.inheritance)
    strict_inheritance: bool = False


@dataclass
class Ctx:
    dictionary: BsddDictionary
    extras: Extras

    @property
    def d(self) -> BsddDictionary:
        return self.dictionary


OpFn = Callable[..., Any]
REGISTRY: dict[str, OpFn] = {}


def op(name: str) -> Callable[[OpFn], OpFn]:
    def deco(fn: OpFn) -> OpFn:
        REGISTRY[name] = fn
        return fn

    return deco


def format_validation_error(exc: ValidationError) -> str:
    parts = []
    for err in exc.errors()[:5]:
        loc = ".".join(str(x) for x in err.get("loc", ()))
        parts.append(f"{loc}: {err.get('msg')}" if loc else str(err.get("msg")))
    return "; ".join(parts)


def run(ctx: Ctx, name: str, args: dict[str, Any] | None) -> Any:
    fn = REGISTRY.get(name)
    if fn is None:
        raise OpError(f"Unknown operation '{name}'")
    from . import inheritance

    before = None
    if ctx.extras.strict_inheritance and name not in inheritance.WHOLESALE_OPS:
        before = inheritance.snapshot(ctx.dictionary)
    try:
        result = fn(ctx, **(args or {}))
        if ctx.extras.strict_inheritance:
            if before is not None:
                inheritance.propagate_and_guard(ctx, before)
            inheritance.complete(ctx)
    except ValidationError as exc:
        raise OpError(format_validation_error(exc)) from exc
    except TypeError as exc:
        # wrong/missing arguments
        if "argument" in str(exc):
            raise OpError(f"Invalid arguments for '{name}': {exc}") from exc
        raise
    from .helpers import normalize_extras

    normalize_extras(ctx)
    return result


# register all operations
from . import classes as _classes  # noqa: E402,F401
from . import class_properties as _class_properties  # noqa: E402,F401
from . import dictionary as _dictionary  # noqa: E402,F401
from . import properties as _properties  # noqa: E402,F401
from . import loin as _loin  # noqa: E402,F401
from . import inheritance as _inheritance  # noqa: E402,F401
