from __future__ import annotations

import re
from typing import Any

from bsdd_json import BsddDictionary
from bsdd_json.utils import dictionary_utils as dict_utils

from . import Ctx, OpError, op
from .helpers import class_uri, property_uri

VERSION_RE = re.compile(r"^(0|[1-9]\d*)(\.(0|[1-9]\d*)){0,2}$")
HEADER_FIELDS = {
    "OrganizationCode",
    "DictionaryCode",
    "DictionaryVersion",
    "LanguageIsoCode",
    "LanguageOnly",
    "UseOwnUri",
    "DictionaryName",
    "DictionaryUri",
    "License",
    "LicenseUrl",
    "ChangeRequestEmailAddress",
    "ModelVersion",
    "MoreInfoUrl",
    "QualityAssuranceProcedure",
    "QualityAssuranceProcedureUrl",
    "ReleaseDate",
    "Status",
}


def validate_header(values: dict[str, Any]) -> None:
    for key in ("OrganizationCode", "DictionaryCode", "LanguageIsoCode"):
        if not str(values.get(key) or "").strip():
            raise OpError(f"{key} must not be empty")
    if not VERSION_RE.match(str(values.get("DictionaryVersion") or "")):
        raise OpError("DictionaryVersion must look like 1, 1.0 or 1.0.0")
    if values.get("UseOwnUri") and not values.get("DictionaryUri"):
        raise OpError("DictionaryUri is required when UseOwnUri is set")


@op("dict.update")
def update_dictionary(ctx: Ctx, data: dict[str, Any]) -> None:
    """Update dictionary header fields; internal relation URIs follow code/version changes."""
    d = ctx.d
    unknown = set(data) - HEADER_FIELDS
    if unknown:
        raise OpError(f"Unknown dictionary fields: {', '.join(sorted(unknown))}")
    values = {k: v for k, v in d.model_dump(mode="json").items() if k in HEADER_FIELDS}
    values.update(data)
    if not values.get("UseOwnUri"):
        values["DictionaryUri"] = None
    validate_header(values)
    validated = BsddDictionary.model_validate({**values, "Classes": [], "Properties": []})

    old_ns = (d.OrganizationCode, d.DictionaryCode)
    old_state = (d.OrganizationCode, d.DictionaryCode, d.DictionaryVersion, d.UseOwnUri, d.DictionaryUri)

    def internal(uri: str | None, kind: str) -> str | None:
        if not uri or not dict_utils.is_uri(uri):
            return None
        parsed = dict_utils.parse_bsdd_url(uri)
        if (parsed.get("namespace") or "").lower() != f"{old_ns[0]}/{old_ns[1]}".lower():
            return None
        rtype = parsed.get("resource_type")
        if kind == "class" and rtype != "class":
            return None
        if kind == "prop" and rtype not in ("prop", "property"):
            return None
        return parsed.get("resource_id")

    # collect internal references before changing the header
    class_refs = []
    for c in d.Classes:
        for cr in c.ClassRelations:
            code = internal(cr.RelatedClassUri, "class")
            if code:
                class_refs.append((cr, code))
    prop_refs = []
    for p in d.Properties:
        for pr in p.PropertyRelations:
            code = internal(pr.RelatedPropertyUri, "prop")
            if code:
                prop_refs.append((pr, code))
    cp_refs = []
    for c in d.Classes:
        for cp in c.ClassProperties:
            code = internal(cp.PropertyUri, "prop")
            if code:
                cp_refs.append((cp, code))

    for key in HEADER_FIELDS:
        setattr(d, key, getattr(validated, key))

    new_state = (d.OrganizationCode, d.DictionaryCode, d.DictionaryVersion, d.UseOwnUri, d.DictionaryUri)
    if new_state != old_state:
        for cr, code in class_refs:
            cr.RelatedClassUri = class_uri(d, code)
        for pr, code in prop_refs:
            pr.RelatedPropertyUri = property_uri(d, code)
        for cp, code in cp_refs:
            cp.PropertyUri = property_uri(d, code)


@op("dict.replace")
def replace_dictionary(ctx: Ctx, dictionary: dict[str, Any]) -> None:
    """Replace the whole dictionary (used by the shell and re-imports)."""
    new = BsddDictionary.model_validate(dictionary)
    ctx.dictionary = new
