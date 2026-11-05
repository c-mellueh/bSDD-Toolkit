"""IFC helper data (entity list and term splitting)."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

RESOURCES = Path(__file__).resolve().parent.parent / "resources"
_TERM = re.compile(r"^(Ifc[A-Za-z0-9]*?[a-z0-9])([A-Z][A-Z0-9_]*)?$")


def split_ifc_term(term: str) -> tuple[str, str | None]:
    """'IfcElectricMotorSYNCHRONOUS' -> ('IfcElectricMotor', 'SYNCHRONOUS')."""
    match = _TERM.match(term or "")
    if not match:
        return term, None
    entity, predefined = match.groups()
    return entity, predefined


@lru_cache(maxsize=1)
def ifc_classes() -> list[dict]:
    with (RESOURCES / "ifc_classes.json").open(encoding="utf-8") as f:
        data = json.load(f)
    keep = ("code", "name", "parentClassCode", "uri", "classType")
    return [{k: c.get(k) for k in keep} for c in data]


@lru_cache(maxsize=1)
def ifc_type_classes() -> list[str]:
    with (RESOURCES / "ifc_type_classes.json").open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def resource_json(name: str):
    with (RESOURCES / name).open(encoding="utf-8") as f:
        return json.load(f)
