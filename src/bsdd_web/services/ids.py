"""IDS (Information Delivery Specification) export using ifctester."""

from __future__ import annotations

import datetime
import tempfile
from pathlib import Path
from typing import Any

import ifctester
from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary
from ifctester.facet import Classification as ClassificationFacet
from ifctester.facet import Entity as EntityFacet
from ifctester.facet import Property as PropertyFacet
from ifctester.facet import Restriction
from ifctester.ids import Specification

from bsdd_web.ops.helpers import class_uri

from .ifc import RESOURCES, ifc_type_classes, split_ifc_term
from .loin import Selection
from .resolve import resolver_for

TEMPLATE = RESOURCES / "template.ids"

PROPERTY_DATATYPE_MAPPING = {
    f"https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/{k}": v
    for k, v in {
        "AcousticRating": "IfcLabel",
        "CapacityPeople": "IfcCountMeasure",
        "ClearDepth": "IfcPositiveLengthMeasure",
        "ClearHeight": "IfcPositiveLengthMeasure",
        "ClearWidth": "IfcPositiveLengthMeasure",
        "ExposureClass": "IfcLabel",
        "FireRating": "IfcLabel",
        "Height": "IfcPositiveLengthMeasure",
        "ModelReference": "IfcLabel",
        "SecurityRating": "IfcLabel",
        "StrengthClass": "IfcLabel",
        "StructuralClass": "IfcLabel",
        "SurfaceSpreadOfFlame": "IfcLabel",
        "ThermalTransmittance": "IfcThermalTransmittanceMeasure",
        "TileLength": "IfcPositiveLengthMeasure",
        "TileWidth": "IfcPositiveLengthMeasure",
    }.items()
}

DEFAULT_DATATYPE_MAPPING = {
    "boolean": "IFCBOOLEAN",
    "string": "IFCTEXT",
    "integer": "IFCINTEGER",
    "real": "IFCREAL",
    "character": "IFCTEXT",
    "time": "IFCDATETIME",
}

DEFAULT_SETTINGS: dict[str, Any] = {
    "classification": True,
    "type_objects": False,
    "main_pset": "",
    "main_property": "",
    "datatype": "IFCLABEL",
    "datatype_mapping": DEFAULT_DATATYPE_MAPPING,
}


def default_metadata(d: BsddDictionary) -> dict[str, Any]:
    return {
        "title": d.DictionaryName or d.DictionaryCode,
        "description": "",
        "author": "",
        "milestone": "",
        "purpose": "",
        "version": d.DictionaryVersion,
        "copyright": d.OrganizationCode,
        "date": datetime.date.today().isoformat(),
        "ifc_versions": ["IFC4X3_ADD2"],
    }


def main_property_candidates(d: BsddDictionary, selection: Selection) -> list[dict[str, Any]]:
    """Property sets and property names ordered by how often they occur (for the settings UI)."""
    resolve = resolver_for(d)
    counts: dict[str, dict[str, Any]] = {}
    for c in d.Classes:
        if c.ClassType != "Class" or not selection.class_included(c):
            continue
        seen = set()
        for cp in c.ClassProperties:
            name = resolve.name(cp)
            pset = cp.PropertySet or ""
            entry = counts.setdefault(pset, {"pset": pset, "count": 0, "properties": {}})
            if pset not in seen:
                entry["count"] += 1
                seen.add(pset)
            entry["properties"][name] = entry["properties"].get(name, 0) + 1
    out = []
    for entry in sorted(counts.values(), key=lambda e: -e["count"]):
        props = sorted(entry["properties"].items(), key=lambda kv: -kv[1])
        out.append({"pset": entry["pset"], "count": entry["count"], "properties": [p for p, _ in props]})
    return out


class _Builder:
    def __init__(self, d: BsddDictionary, selection: Selection, settings: dict[str, Any], metadata: dict[str, Any]):
        self.d = d
        self.sel = selection
        self.settings = {**DEFAULT_SETTINGS, **(settings or {})}
        self.mapping = {**DEFAULT_DATATYPE_MAPPING, **(self.settings.get("datatype_mapping") or {})}
        self.metadata = {**default_metadata(d), **(metadata or {})}
        self.resolve = resolver_for(d)
        self.type_classes = ifc_type_classes()

    def data_type(self, cp: BsddClassProperty) -> str:
        if cp.PropertyUri and cp.PropertyUri in PROPERTY_DATATYPE_MAPPING:
            return PROPERTY_DATATYPE_MAPPING[cp.PropertyUri].upper()
        dt = (self.resolve.data_type(cp) or "String").lower()
        return (self.mapping.get(dt) or "IFCTEXT").upper()

    def property_facet(self, cp: BsddClassProperty) -> PropertyFacet:
        value = None
        values = cp.AllowedValues
        if cp.Pattern:
            value = Restriction(options={"pattern": cp.Pattern})
        elif values:
            value = Restriction(options={"enumeration": [v.Value for v in values if v.Value is not None]})
        elif cp.PredefinedValue:
            value = cp.PredefinedValue
        return PropertyFacet(
            cp.PropertySet,
            self.resolve.name(cp),
            value,
            self.data_type(cp),
            cp.PropertyUri,
            cardinality="required" if cp.IsRequired else "optional",
        )

    def entity_requirements(self, c: BsddClass) -> list[EntityFacet]:
        entities: set[str] = set()
        predefined: set[str] = set()
        for ref in c.RelatedIfcEntityNamesList or []:
            entity, pt = split_ifc_term(ref)
            entities.add(entity.upper())
            predefined.add(pt or "NOTDEFINED")
            if self.settings.get("type_objects"):
                type_class = next((t for t in self.type_classes if t.startswith(entity) and t != entity), None)
                if type_class:
                    entities.add(type_class.upper())
        if not entities:
            return []
        req = EntityFacet()
        req.name = Restriction({"enumeration": sorted(entities)})
        if predefined and predefined != {"NOTDEFINED"}:
            req.predefinedType = Restriction({"enumeration": sorted(predefined)})
        return [req]

    def identifiers(self, c: BsddClass) -> list[str]:
        name = self.settings.get("main_property")
        pset = self.settings.get("main_pset")
        cp = next(
            (x for x in c.ClassProperties if self.resolve.name(x) == name and (not pset or x.PropertySet == pset)),
            None,
        )
        if cp is None or not cp.AllowedValues:
            return [c.Code]
        return [v.Value for v in cp.AllowedValues]

    def applicability(self, c: BsddClass):
        if self.settings.get("classification"):
            return ClassificationFacet(c.Code, self.d.DictionaryName or self.d.DictionaryCode, uri=class_uri(self.d, c), cardinality="optional")
        values = self.identifiers(c)
        value = values[0] if len(values) == 1 else Restriction(options={"enumeration": values})
        return PropertyFacet(self.settings.get("main_pset"), self.settings.get("main_property"), value, self.settings.get("datatype"), cardinality="optional")

    def build(self):
        ids = ifctester.ids.open(str(TEMPLATE))
        versions = self.metadata.get("ifc_versions") or ["IFC4X3_ADD2"]
        classes = sorted((c for c in self.d.Classes if c.ClassType == "Class" and self.sel.class_included(c)), key=lambda c: c.Code)
        if self.settings.get("classification"):
            ids.specifications = []
        else:
            if not self.settings.get("main_pset") or not self.settings.get("main_property"):
                raise ValueError("Select the property set and property that identify the classes")
            base = ids.specifications[0]
            identifiers = sorted({i for c in classes for i in self.identifiers(c)})
            req = PropertyFacet(
                self.settings["main_pset"],
                self.settings["main_property"],
                Restriction(options={"enumeration": identifiers}),
                self.settings.get("datatype"),
                cardinality="required",
            )
            base.requirements = [req]
            base.ifcVersion = versions
        for key in ("title", "description", "author", "milestone", "purpose", "version", "copyright", "date"):
            value = self.metadata.get(key)
            if value:
                ids.info[key] = value
            else:
                ids.info.pop(key, None)
        for c in classes:
            spec = Specification(f"Check for {c.Code}", ifcVersion=versions, identifier=c.Code, description="Auto-generated from bSDD")
            spec.applicability.append(self.applicability(c))
            for cp in c.ClassProperties:
                if self.sel.property_included(c, cp) and cp.PropertySet:
                    spec.requirements.append(self.property_facet(cp))
            spec.requirements += self.entity_requirements(c)
            ids.specifications.append(spec)
        return ids, len(classes)


def export_ids(
    d: BsddDictionary,
    selection: Selection,
    settings: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> tuple[bytes, int]:
    ids, count = _Builder(d, selection, settings or {}, metadata or {}).build()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "out.ids"
        ids.to_xml(str(path))
        return path.read_bytes(), count
