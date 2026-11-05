"""Level of Information Need (ISO 7817-3) state, selection and XML I/O.

The LOIN state is kept as plain JSON in ``Extras.loin`` so that it can be shared
and patched like the rest of the project document::

    {
      "purposes":   [{"guid": str, "name": str}],
      "milestones": [{"guid": str, "name": str, "date": str | None}],
      "providing_actor": {...} | None,
      "receiving_actor": {...} | None,
      "added_classes": [class_code, ...],
      "specs": {"<purpose_guid>|<milestone_guid>": {
          "guid": str,
          "classes": [class_code, ...],
          "properties": {class_code: [[pset, class_property_code], ...]},
      }},
    }
"""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary

DEFAULT_PURPOSE_NAME = "PP 1"
DEFAULT_MILESTONE_NAME = "MS 1"
ACTOR_FIELDS = ("role", "first_name", "middle_name", "last_name", "affiliation", "email_address")


def _guid() -> str:
    return str(uuid.uuid4())


def spec_key(purpose_guid: str, milestone_guid: str) -> str:
    return f"{purpose_guid}|{milestone_guid}"


def default_state() -> dict[str, Any]:
    return {
        "purposes": [{"guid": _guid(), "name": DEFAULT_PURPOSE_NAME}],
        "milestones": [{"guid": _guid(), "name": DEFAULT_MILESTONE_NAME, "date": None}],
        "providing_actor": None,
        "receiving_actor": None,
        "added_classes": [],
        "specs": {},
    }


def ensure_state(state: dict[str, Any]) -> dict[str, Any]:
    """Fill a (possibly empty) state dict in place with defaults and return it."""
    if not state.get("purposes") and not state.get("milestones"):
        state.update(default_state())
    state.setdefault("purposes", [])
    state.setdefault("milestones", [])
    state.setdefault("providing_actor", None)
    state.setdefault("receiving_actor", None)
    state.setdefault("added_classes", [])
    state.setdefault("specs", {})
    return state


def get_spec(state: dict[str, Any], key: str, *, create: bool = False) -> dict[str, Any] | None:
    spec = state["specs"].get(key)
    if spec is None and create:
        p, _, m = key.partition("|")
        if not any(x["guid"] == p for x in state["purposes"]) or not any(x["guid"] == m for x in state["milestones"]):
            raise ValueError("Unknown purpose / milestone")
        spec = {"guid": _guid(), "classes": [], "properties": {}}
        state["specs"][key] = spec
    return spec


def all_spec_keys(state: dict[str, Any]) -> list[str]:
    return [spec_key(p["guid"], m["guid"]) for p in state.get("purposes", []) for m in state.get("milestones", [])]


# --------------------------------------------------------------------------- selection


@dataclass
class Selection:
    """Which classes / class properties an export should contain.

    ``everything=True`` selects the whole dictionary (no LOIN filtering).
    """

    everything: bool = True
    classes: set[str] = field(default_factory=set)
    properties: dict[str, set[tuple[str, str]]] = field(default_factory=dict)

    def class_included(self, bsdd_class: BsddClass) -> bool:
        return self.everything or bsdd_class.Code in self.classes

    def property_included(self, bsdd_class: BsddClass, cp: BsddClassProperty) -> bool:
        if self.everything:
            return True
        return (cp.PropertySet or "", cp.Code) in self.properties.get(bsdd_class.Code, set())

    def checked_classes(self, d: BsddDictionary) -> list[BsddClass]:
        return [c for c in d.Classes if self.class_included(c)]

    def pset_dict(self, d: BsddDictionary) -> dict[str, set[str]]:
        """pset name -> class-property codes included for any selected class."""
        out: dict[str, set[str]] = {}
        for c in d.Classes:
            if not self.class_included(c):
                continue
            for cp in c.ClassProperties:
                if self.property_included(c, cp):
                    out.setdefault(cp.PropertySet or "", set()).add(cp.Code)
        return out


def selection_from_state(state: dict[str, Any] | None, keys: list[str] | None) -> Selection:
    """Build a selection from LOIN specs. ``keys=None`` selects everything."""
    if keys is None:
        return Selection(everything=True)
    state = ensure_state(copy.deepcopy(state or {}))
    sel = Selection(everything=False)
    for key in keys:
        spec = state["specs"].get(key)
        if not spec:
            continue
        sel.classes.update(spec.get("classes", []))
        for class_code, items in spec.get("properties", {}).items():
            bucket = sel.properties.setdefault(class_code, set())
            bucket.update((pset or "", code) for pset, code in items)
    return sel


# --------------------------------------------------------------------------- mutations


def add_classes(state: dict[str, Any], d: BsddDictionary, codes: list[str]) -> None:
    existing = {c.Code: c for c in d.Classes}
    added = list(state["added_classes"])
    for code in codes:
        cur = existing.get(code)
        while cur is not None and cur.Code not in added:
            added.append(cur.Code)
            cur = existing.get(cur.ParentClassCode) if cur.ParentClassCode else None
    state["added_classes"] = added


def _descendants(d: BsddDictionary, code: str) -> list[str]:
    by_parent: dict[str, list[str]] = {}
    for c in d.Classes:
        if c.ParentClassCode:
            by_parent.setdefault(c.ParentClassCode, []).append(c.Code)
    out, stack = [], [code]
    while stack:
        cur = stack.pop()
        for child in by_parent.get(cur, []):
            if child not in out:
                out.append(child)
                stack.append(child)
    return out


def remove_class(state: dict[str, Any], d: BsddDictionary, code: str) -> None:
    to_remove = {code, *_descendants(d, code)}
    state["added_classes"] = [c for c in state["added_classes"] if c not in to_remove]
    for spec in state["specs"].values():
        spec["classes"] = [c for c in spec["classes"] if c not in to_remove]
        for c in to_remove:
            spec["properties"].pop(c, None)


def set_class_included(
    state: dict[str, Any],
    d: BsddDictionary,
    key: str,
    codes: list[str],
    included: bool,
    recursive: bool = False,
) -> None:
    spec = get_spec(state, key, create=True)
    targets: list[str] = []
    for code in codes:
        targets.append(code)
        if recursive:
            targets.extend(_descendants(d, code))
    if included:
        add_classes(state, d, targets)
        for code in targets:
            if code not in spec["classes"]:
                spec["classes"].append(code)
    else:
        spec["classes"] = [c for c in spec["classes"] if c not in targets]
        for code in targets:
            spec["properties"].pop(code, None)


def set_properties_included(
    state: dict[str, Any],
    d: BsddDictionary,
    key: str,
    class_code: str,
    items: list[list[str]],
    included: bool,
) -> None:
    spec = get_spec(state, key, create=True)
    bucket = [list(x) for x in spec["properties"].get(class_code, [])]
    keys = {(p or "", c) for p, c in items}
    if included:
        set_class_included(state, d, key, [class_code], True)
        for pset, code in sorted(keys):
            if [pset, code] not in bucket:
                bucket.append([pset, code])
    else:
        bucket = [x for x in bucket if (x[0] or "", x[1]) not in keys]
    if bucket:
        spec["properties"][class_code] = bucket
    else:
        spec["properties"].pop(class_code, None)


def rename_class(state: dict[str, Any], old: str, new: str) -> None:
    if not state:
        return
    state["added_classes"] = [new if c == old else c for c in state.get("added_classes", [])]
    for spec in state.get("specs", {}).values():
        spec["classes"] = [new if c == old else c for c in spec.get("classes", [])]
        if old in spec.get("properties", {}):
            spec["properties"][new] = spec["properties"].pop(old)


def drop_dangling(state: dict[str, Any], valid_codes: set[str]) -> None:
    if not state:
        return
    state["added_classes"] = [c for c in state.get("added_classes", []) if c in valid_codes]
    for spec in state.get("specs", {}).values():
        spec["classes"] = [c for c in spec.get("classes", []) if c in valid_codes]
        for c in list(spec.get("properties", {})):
            if c not in valid_codes:
                spec["properties"].pop(c)
    purposes = {p["guid"] for p in state.get("purposes", [])}
    milestones = {m["guid"] for m in state.get("milestones", [])}
    for key in list(state.get("specs", {})):
        p, _, m = key.partition("|")
        if p not in purposes or m not in milestones:
            state["specs"].pop(key)


# --------------------------------------------------------------------------- XML export


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _actor(data: dict[str, Any] | None, default_role: str):
    from .iso_datamodel import DtMultiLangText, LoinActor

    data = data or {}
    return LoinActor(
        guid=uuid.UUID(data["guid"]) if data.get("guid") else uuid.uuid4(),
        first_name=data.get("first_name") or None,
        middle_name=data.get("middle_name") or None,
        last_name=data.get("last_name") or None,
        affiliation=data.get("affiliation") or None,
        role=DtMultiLangText(language="en", text=data.get("role") or default_role),
        email_address=data.get("email_address") or None,
    )


def _property_uri(d: BsddDictionary, cp: BsddClassProperty) -> str | None:
    from bsdd_web.ops.helpers import property_uri

    if cp.PropertyUri:
        return cp.PropertyUri
    if cp.OwnedUri:
        return cp.OwnedUri
    if cp.PropertyCode:
        return property_uri(d, cp.PropertyCode)
    return None


def build_loin_xml(state: dict[str, Any], d: BsddDictionary, keys: list[str] | None = None) -> tuple[bytes, int]:
    """Create ISO 7817-3 XML for the given spec keys (default: all specs with content)."""
    from bsdd_web.ops.helpers import GOP, class_uri, linked_gop

    from .iso_datamodel import (
        DtMultiLangText,
        DtRef,
        IsoGroupOfProperties,
        IsoObjectType,
        LoinAlphanumericalInformation,
        LoinGroupsOfProperties,
        LoinInformationDeliveryMilestone,
        LoinLevelOfInformationNeed,
        LoinPrerequisites,
        LoinPurpose,
        LoinSpecification,
        LoinSpecificationPerObjectType,
    )

    state = ensure_state(copy.deepcopy(state or {}))
    classes = {c.Code: c for c in d.Classes}
    providing = _actor(state.get("providing_actor"), "Provider")
    receiving = _actor(state.get("receiving_actor"), "Receiver")
    selected = set(keys) if keys is not None else None

    specs = []
    for purpose in state["purposes"]:
        for milestone in state["milestones"]:
            key = spec_key(purpose["guid"], milestone["guid"])
            spec_state = state["specs"].get(key)
            if selected is not None and key not in selected:
                continue
            if selected is None and not (spec_state and spec_state.get("classes")):
                continue
            spec_state = spec_state or {"guid": _guid(), "classes": [], "properties": {}}
            date = milestone.get("date")
            per_object = []
            for code in spec_state.get("classes", []):
                bsdd_class = classes.get(code)
                if bsdd_class is None:
                    continue
                groups: dict[str, IsoGroupOfProperties] = {}
                group_refs: list[DtRef] = []
                chosen = spec_state.get("properties", {}).get(code, [])
                # A reference to a Group of Properties means "the whole group" (it is expanded to all
                # properties of the set on import), so only use it when every property of the set is
                # selected; otherwise reference the selected properties individually.
                chosen_keys = {((ps or ""), c) for ps, c in chosen}
                complete: dict[str, bool] = {}
                for x in bsdd_class.ClassProperties:
                    ps = x.PropertySet or ""
                    complete[ps] = complete.get(ps, True) and (ps, x.Code) in chosen_keys
                for pset, cp_code in chosen:
                    cp = next((x for x in bsdd_class.ClassProperties if x.Code == cp_code and (x.PropertySet or "") == pset), None)
                    if cp is None:
                        continue
                    gop = linked_gop(d, bsdd_class, pset) if pset and complete.get(pset) else None
                    if gop is not None and gop.ClassType == GOP:
                        uri = gop.OwnedUri or class_uri(d, gop)
                        if not any(r.reference_uri == uri for r in group_refs):
                            group_refs.append(DtRef(reference_uri=uri))
                        continue
                    ref = DtRef(reference_uri=_property_uri(d, cp))
                    group = groups.get(pset)
                    if group is None:
                        groups[pset] = IsoGroupOfProperties(
                            guid=uuid.uuid4(),
                            date_of_creation=_now(),
                            names=[DtMultiLangText(language="en", text=pset or "Properties")],
                            has_property_refs=[ref],
                        )
                    elif not any(r.reference_uri == ref.reference_uri for r in group.has_property_refs):
                        group.has_property_refs.append(ref)
                per_object.append(
                    LoinSpecificationPerObjectType(
                        guid=uuid.uuid4(),
                        date_of_creation=_now(),
                        names=[DtMultiLangText(language="en", text=bsdd_class.Name or bsdd_class.Code)],
                        object_type=IsoObjectType(
                            guid=uuid.uuid4(),
                            date_of_creation=_now(),
                            names=[DtMultiLangText(language="en", text=bsdd_class.Code)],
                        ),
                        alphanumerical_information=LoinAlphanumericalInformation(
                            guid=uuid.uuid4(),
                            groups_of_properties=LoinGroupsOfProperties(
                                group_of_properties=list(groups.values()),
                                group_of_properties_refs=group_refs,
                            ),
                        ),
                        definition=DtMultiLangText(language="en", text=bsdd_class.Definition or ""),
                    ),
                )
            specs.append(
                LoinSpecification(
                    name=f"{purpose['name']} – {milestone['name']}",
                    guid=uuid.UUID(spec_state["guid"]),
                    prerequisites=LoinPrerequisites(
                        guid=uuid.uuid4(),
                        purpose=LoinPurpose(guid=uuid.UUID(purpose["guid"]), names=[DtMultiLangText(language="en", text=purpose["name"])]),
                        information_delivery_milestone=LoinInformationDeliveryMilestone(
                            guid=uuid.UUID(milestone["guid"]),
                            date=date or None,
                            names=[DtMultiLangText(language="en", text=milestone["name"])],
                        ),
                        providing_actor=providing,
                        receiving_actor=receiving,
                    ),
                    specifications_per_object_type=per_object,
                ),
            )
    if not specs:
        raise ValueError("No LOIN specification selected or none contains classes")
    loin = LoinLevelOfInformationNeed(specifications=specs)
    # Same serialisation as the desktop app so files can be exchanged between both.
    return loin.to_xml(encoding="UTF-8", xml_declaration=True, exclude_none=True), len(specs)


def unqualify(xml: bytes) -> bytes:
    """ISO 7817-3: only the root element is in the LOIN namespace, local elements are unqualified."""
    from lxml import etree

    from .iso_datamodel import LOIN_NS

    root = etree.fromstring(xml)
    prefix = f"{{{LOIN_NS}}}"
    for el in root.iter():
        if el is not root and isinstance(el.tag, str) and el.tag.startswith(prefix):
            el.tag = el.tag[len(prefix) :]
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)


def _qualify(xml: bytes) -> bytes:
    """Inverse of :func:`_unqualify` so the pydantic-xml models can parse standard files."""
    from lxml import etree

    from .iso_datamodel import LOIN_NS

    root = etree.fromstring(xml)
    for el in root:
        if isinstance(el.tag, str) and not el.tag.startswith("{"):
            el.tag = f"{{{LOIN_NS}}}{el.tag}"
    return etree.tostring(root, encoding="UTF-8")


# --------------------------------------------------------------------------- XML import


def _actor_to_dict(actor) -> dict[str, Any] | None:
    if actor is None:
        return None
    return {
        "guid": str(actor.guid),
        "role": actor.role.text if actor.role else "",
        "first_name": actor.first_name,
        "middle_name": actor.middle_name,
        "last_name": actor.last_name,
        "affiliation": actor.affiliation,
        "email_address": actor.email_address,
    }


def parse_loin_xml(xml: bytes | str, d: BsddDictionary) -> dict[str, Any]:
    """Parse ISO 7817-3 XML into a LOIN state dict."""
    from bsdd_web.ops.helpers import internal_code

    from .iso_datamodel import LoinLevelOfInformationNeed

    if isinstance(xml, str):
        xml = xml.encode("utf-8")
    loin = LoinLevelOfInformationNeed.from_xml(_qualify(xml))
    classes = {c.Code: c for c in d.Classes}
    gops_by_code = {c.Code: c for c in d.Classes if c.ClassType == "GroupOfProperties"}
    state: dict[str, Any] = {
        "purposes": [],
        "milestones": [],
        "providing_actor": None,
        "receiving_actor": None,
        "added_classes": [],
        "specs": {},
    }
    seen_p: set[str] = set()
    seen_m: set[str] = set()
    for spec in loin.specifications:
        purpose = spec.prerequisites.purpose
        milestone = spec.prerequisites.information_delivery_milestone
        pg, mg = str(purpose.guid), str(milestone.guid)
        if pg not in seen_p:
            seen_p.add(pg)
            state["purposes"].append({"guid": pg, "name": purpose.names[0].text if purpose.names else pg})
        if mg not in seen_m:
            seen_m.add(mg)
            state["milestones"].append(
                {
                    "guid": mg,
                    "name": milestone.names[0].text if milestone.names else mg,
                    "date": milestone.date.isoformat() if milestone.date else None,
                },
            )
        if state["providing_actor"] is None:
            state["providing_actor"] = _actor_to_dict(spec.prerequisites.providing_actor)
        if state["receiving_actor"] is None:
            state["receiving_actor"] = _actor_to_dict(spec.prerequisites.receiving_actor)

        spec_state = {"guid": str(spec.guid), "classes": [], "properties": {}}
        for per_obj in spec.specifications_per_object_type:
            code = per_obj.object_type.names[0].text if per_obj.object_type.names else None
            bsdd_class = classes.get(code) if code else None
            if bsdd_class is None:
                continue
            spec_state["classes"].append(code)
            items: list[list[str]] = []
            alpha = per_obj.alphanumerical_information
            groups = alpha.groups_of_properties if alpha else None
            if groups:
                for group in groups.group_of_properties:
                    pset = group.names[0].text if group.names else ""
                    for ref in group.has_property_refs:
                        uri = ref.reference_uri
                        prop_code = internal_code(d, uri, "prop")
                        for cp in bsdd_class.ClassProperties:
                            if (cp.PropertySet or "") != pset:
                                continue
                            if (prop_code and cp.PropertyCode == prop_code) or (uri and cp.PropertyUri == uri):
                                items.append([pset, cp.Code])
                for ref in groups.group_of_properties_refs:
                    gop_code = internal_code(d, ref.reference_uri, "class")
                    gop = gops_by_code.get(gop_code) if gop_code else None
                    if gop is None:
                        continue
                    items.extend([gop.Name, cp.Code] for cp in bsdd_class.ClassProperties if cp.PropertySet == gop.Name)
            if items:
                spec_state["properties"][code] = items
        state["specs"][spec_key(pg, mg)] = spec_state
        add_classes(state, d, spec_state["classes"])
    return state


def set_pset_properties_included(
    state: dict[str, Any],
    d: BsddDictionary,
    key: str,
    items: list[list[str]],
    included: bool,
) -> int:
    """Toggle (pset, class property code) pairs in every LOIN class that owns them.

    Mirrors the desktop pset tree: the view aggregates all classes added to the LOIN,
    toggling a property set or property applies to every one of those classes.
    Returns the number of classes touched.
    """
    wanted = {(p or "", c) for p, c in items}
    added = set(state.get("added_classes", []))
    touched = 0
    for bsdd_class in d.Classes:
        if bsdd_class.Code not in added:
            continue
        hits = [[cp.PropertySet or "", cp.Code] for cp in bsdd_class.ClassProperties if (cp.PropertySet or "", cp.Code) in wanted]
        if hits:
            set_properties_included(state, d, key, bsdd_class.Code, hits, included)
            touched += 1
    return touched
