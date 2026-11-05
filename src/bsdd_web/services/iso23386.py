"""ISO 23386 XML export (property groups + properties)."""

from __future__ import annotations

import re
import uuid
from datetime import datetime

from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary, BsddProperty

from bsdd_web.ops.helpers import class_uri, property_uri

from .iso_datamodel import Container, DefinitionInLanguage, NameInLanguage, PhysicalQuantity, Property, PropertyGroup
from .loin import Selection
from .resolve import resolver_for

_NS = uuid.UUID("6f1c3a52-6d0b-4c38-9a3e-2c51d3b3f0a1")
_LANG_RE = re.compile(r"^[a-z]{2}-[A-Z]{2}$")
_COUNTRY_RE = re.compile(r"^[A-Z]{2}$")


def _guid(uid: str | None, fallback_key: str) -> uuid.UUID:
    if uid:
        try:
            return uuid.UUID(str(uid))
        except ValueError:
            pass
    # deterministic: the same element gets the same GUID on every export
    return uuid.uuid5(_NS, fallback_key)


def _status(value: str | None) -> str:
    if value and value.lower() in ("active", "inactive"):
        return value.lower()
    return "active"


def _text(value: str | None, default: str = "undefined") -> str:
    value = (value or "").strip()
    return value[:1500] if value else default


class _Builder:
    def __init__(self, d: BsddDictionary, selection: Selection):
        self.d = d
        self.sel = selection
        self.resolve = resolver_for(d)
        lang = d.LanguageIsoCode if _LANG_RE.match(d.LanguageIsoCode or "") else "en-GB"
        self.language = lang
        self.country = lang.split("-")[1]
        self.now = datetime.now().replace(microsecond=0)
        self.groups: dict[str, dict] = {}  # class code -> {guid, xml, bsdd_class}
        self.properties: dict[str, Property] = {}  # property key -> xml property

    def countries(self, values) -> list[str]:
        out = [c for c in (values or []) if _COUNTRY_RE.match(str(c))]
        return out or [self.country]

    def create_group(self, c: BsddClass, mode: str) -> dict:
        guid = _guid(c.Uid, class_uri(self.d, c))
        xml = PropertyGroup(
            guid=guid,
            status=_status(c.Status),
            dateOfCreation=self.now,
            dateOfRevision=self.now,
            dateOfVersion=self.now,
            versionNumber=c.VersionNumber or 1,
            revisionNumber=c.RevisionNumber or 1,
            creatorsLanguage=self.language,
            namesInLanguage=[NameInLanguage(name=_text(c.Name, c.Code), language=self.language)],
            definitionsInLanguage=[DefinitionInLanguage(definition=_text(c.Definition), language=self.language)],
            visualRepresentation=[c.VisualRepresentationUri] if c.VisualRepresentationUri else [],
            countryOfUse=self.countries(c.CountriesOfUse),
            countryOfOrigin=c.CountryOfOrigin if _COUNTRY_RE.match(c.CountryOfOrigin or "") else self.country,
            categoryOfGroupOfProperties=mode,
        )
        entry = {"guid": guid, "xml": xml, "bsdd_class": c}
        self.groups[c.Code] = entry
        return entry

    def property_key(self, prop: BsddProperty, cp: BsddClassProperty) -> str:
        return prop.OwnedUri or cp.PropertyUri or property_uri(self.d, prop)

    def create_property(self, cp: BsddClassProperty, prop: BsddProperty, group_guid: uuid.UUID) -> Property:
        key = self.property_key(prop, cp)
        return Property(
            guid=_guid(prop.Uid, key),
            status=_status(prop.Status),
            dateOfCreation=self.now,
            dateOfRevision=self.now,
            dateOfVersion=self.now,
            versionNumber=prop.VersionNumber or 1,
            revisionNumber=prop.RevisionNumber or 1,
            creatorsLanguage=self.language,
            namesInLanguage=[NameInLanguage(name=_text(prop.Name, prop.Code), language=self.language)],
            definitionsInLanguage=[DefinitionInLanguage(definition=_text(self.resolve.definition(cp)), language=self.language)],
            groupOfProperties=[group_guid],
            countryOfUse=self.countries(prop.CountriesOfUse),
            physicalQuantity=[PhysicalQuantity(siUnit="without", language=self.language)],
            dataType=(prop.DataType or "String").upper(),
            dynamicProperty="no",
        )

    def add_property(self, cp: BsddClassProperty, group: dict) -> None:
        prop = self.resolve.property(cp)
        if prop is None:
            return
        key = self.property_key(prop, cp)
        xml = self.properties.get(key)
        if xml is None:
            self.properties[key] = self.create_property(cp, prop, group["guid"])
        elif group["guid"] not in xml.groupOfProperties:
            xml.groupOfProperties.append(group["guid"])

    def build(self) -> Container:
        d = self.d
        # 1) GroupOfProperties classes become "name property set" groups
        pset_dict = self.sel.pset_dict(d)
        for c in d.Classes:
            if c.ClassType != "GroupOfProperties" or c.Name not in pset_dict:
                continue
            group = self.create_group(c, "name property set")
            for cp in c.ClassProperties:
                if cp.Code in pset_dict[c.Name]:
                    self.add_property(cp, group)
        # 2) selected classes
        for c in d.Classes:
            if c.ClassType != "Class" or not self.sel.class_included(c):
                continue
            group = self.create_group(c, "class")
            for cp in c.ClassProperties:
                if self.sel.property_included(c, cp):
                    self.add_property(cp, group)
        # 3) parent relations between exported classes
        for code, entry in self.groups.items():
            parent = entry["bsdd_class"].ParentClassCode
            if parent and parent in self.groups and entry["bsdd_class"].ClassType == "Class":
                entry["xml"].parentGroupOfProperties = self.groups[parent]["guid"]
        self.remove_inherited()
        return Container(propertyGroup=[g["xml"] for g in self.groups.values()], property_=list(self.properties.values()))

    def remove_inherited(self) -> None:
        """A property assigned to a class and to one of its ancestors is only kept on the ancestor."""
        by_guid = {g["guid"]: g for g in self.groups.values()}
        index = {c.Code: c for c in self.d.Classes}

        def ancestors(c: BsddClass) -> set[str]:
            out, cur = set(), c.ParentClassCode
            while cur and cur not in out:
                out.add(cur)
                cur = index[cur].ParentClassCode if cur in index else None
            return out

        for xml in self.properties.values():
            if len(xml.groupOfProperties) <= 1:
                continue
            groups = [by_guid[g] for g in xml.groupOfProperties if g in by_guid]
            codes = {g["bsdd_class"].Code for g in groups}
            keep = [g["guid"] for g in groups if not (ancestors(g["bsdd_class"]) & codes)]
            xml.groupOfProperties = keep + [g for g in xml.groupOfProperties if g not in by_guid]


def export_iso23386(d: BsddDictionary, selection: Selection) -> tuple[bytes, int]:
    builder = _Builder(d, selection)
    container = builder.build()
    xml = container.to_xml(encoding="UTF-8", xml_declaration=True, exclude_none=True, exclude_unset=True)
    return xml, len(builder.groups)
