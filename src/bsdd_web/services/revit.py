"""Revit exports: user-defined IFC property set file and shared parameter file."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Literal

from bsdd_json import BsddClassProperty, BsddDictionary, BsddProperty
from jinja2 import Template

from bsdd_web.ops.helpers import property_uri

from .loin import Selection
from .resolve import resolver_for

Mode = Literal["CustomPropertySet", "SharedParameters"]
TEMPLATE = Path(__file__).resolve().parent.parent / "resources" / "shared_parameter_template.j2"
_NS = uuid.UUID("0b6f1e3e-21a4-4a8a-8f0c-6c7f6f1d9e55")

CUSTOM_PSET_TYPES = {"Boolean": "Boolean", "Character": "Label", "Integer": "Integer", "Real": "Real", "Time": "Time"}
SHARED_PARAMETER_TYPES = {
    "Boolean": "YESNO",
    "Character": "TEXT",
    "Integer": "INTEGER",
    "Real": "NUMBER",
    "String": "TEXT",
    "Time": "TIMEINTERVAL",
}


def _clean(text: str | None) -> str:
    return " ".join((text or "").replace("\t", " ").split())


def _datatype(prop: BsddProperty, mode: Mode, text_or_label: str) -> str:
    if mode == "CustomPropertySet":
        return CUSTOM_PSET_TYPES.get(prop.DataType or "", text_or_label)
    return SHARED_PARAMETER_TYPES.get(prop.DataType or "", "TEXT")


def _collect(d: BsddDictionary, selection: Selection):
    """pset name -> (ordered) list of (class property, property, ifc types of classes using it)."""
    resolve = resolver_for(d)
    gops = {c.Name: c for c in d.Classes if c.ClassType == "GroupOfProperties"}
    psets: dict[str, dict[str, tuple[BsddClassProperty, BsddProperty]]] = {}
    ifc_types: dict[str, set[str]] = {}
    for c in d.Classes:
        if c.ClassType != "Class" or not selection.class_included(c):
            continue
        for cp in c.ClassProperties:
            if not selection.property_included(c, cp):
                continue
            pset = cp.PropertySet or ""
            ifc_types.setdefault(pset, set()).update(c.RelatedIfcEntityNamesList or [])
            entries = psets.setdefault(pset, {})
            if cp.Code in entries:
                continue
            source = cp
            gop = gops.get(pset)
            if gop is not None:
                source = next((x for x in gop.ClassProperties if x.Code == cp.Code), cp)
            prop = resolve.property(source)
            if prop is not None:
                entries[cp.Code] = (source, prop)
    return psets, ifc_types


def export_custom_psets(d: BsddDictionary, selection: Selection, text_or_label: str = "Text") -> tuple[bytes, int]:
    psets, ifc_types = _collect(d, selection)
    lines: list[str] = []
    count = 0
    for pset, entries in psets.items():
        if not entries:
            continue
        lines.append("\t".join(["PropertySet:", pset, "I", ",".join(sorted(ifc_types.get(pset, [])))]))
        for _cp, prop in entries.values():
            lines.append("\t".join([_clean(prop.Name), _datatype(prop, "CustomPropertySet", text_or_label), f"{pset}.{_clean(prop.Name)}"]))
            count += 1
        lines.append("")
    return "\n".join(lines).encode("utf-8"), count


def export_shared_parameters(d: BsddDictionary, selection: Selection, group_name: str | None = None) -> tuple[bytes, int]:
    psets, _ = _collect(d, selection)
    params = []
    for pset, entries in psets.items():
        for _cp, prop in entries.values():
            if prop.Uid:
                try:
                    uid = uuid.UUID(str(prop.Uid))
                except ValueError:
                    uid = uuid.uuid5(_NS, str(prop.Uid))
            else:
                uid = uuid.uuid5(_NS, prop.OwnedUri or property_uri(d, prop))
            params.append(
                (uid, f"{pset}.{_clean(prop.Name)}", _datatype(prop, "SharedParameters", "TEXT"), "", 1, 1, _clean(prop.Definition), 1, 0),
            )
    text = Template(TEMPLATE.read_text(encoding="utf-8")).render(groups=[group_name or d.DictionaryCode or "bSDD"], params=params)
    return text.encode("utf-16"), len(params)
