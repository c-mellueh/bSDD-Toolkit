from __future__ import annotations

import copy
import json
import logging
import weakref
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, ValidationError, model_validator

from .type_hints import (
    CLASS_RELATION_TYPE,
    CLASS_STATUS,
    CLASS_TYPE,
    COUNTRY_CODE,
    DATATYPE_TYPE,
    DOCUMENT_TYPE,
    LANGUAGE_ISO_CODE,
    PROPERTY_RELATION_TYPE,
    PROPERTY_STATUS,
    PROPERTY_VALUE_KIND_TYPE,
    STATUS,
    UNITS_TYPE,
)

logger = logging.getLogger(__name__)


def _lower_first(s: str) -> str:
    return s[:1].lower() + s[1:] if s else s


def _prune_error_path(data, loc):
    if not loc:
        return
    target = data
    for index, key in enumerate(loc):
        is_last = index == len(loc) - 1
        if isinstance(key, int):
            if not isinstance(target, list) or key >= len(target):
                return
            if is_last:
                target.pop(key)
                return
            target = target[key]
        else:
            if not isinstance(target, dict):
                return
            if key not in target:
                # error locations use the alias (lowerCamel), raw data may use PascalCase
                key = next((k for k in target if isinstance(k, str) and k.lower() == str(key).lower()), None)
                if key is None:
                    return
            if is_last:
                target.pop(key, None)
                return
            target = target.get(key)
            if target is None:
                return


def _get(data: dict, key: str):
    """Value of a PascalCase key, also accepting the lowerCamel alias."""
    return data.get(key, data.get(_lower_first(key)))


class CaseInsensitiveModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_lower_first)

    @model_validator(mode="before")
    @classmethod
    def _drop_null_list_items(cls, data):
        """Read ``[null]`` (as exported by the bSDD website for empty lists) as an empty list.

        ``null`` entries are removed from every list value, so ``[null]`` becomes ``[]``.
        """
        if isinstance(data, dict) and any(isinstance(v, list) and None in v for v in data.values()):
            return {k: [x for x in v if x is not None] if isinstance(v, list) else v for k, v in data.items()}
        return data


class BsddDictionary(CaseInsensitiveModel):
    OrganizationCode: str
    DictionaryCode: str
    DictionaryVersion: str
    LanguageIsoCode: LANGUAGE_ISO_CODE
    LanguageOnly: bool
    UseOwnUri: bool
    DictionaryName: str | None = None
    DictionaryUri: str | None = None
    License: str | None = "MIT"
    LicenseUrl: str | None = None
    ChangeRequestEmailAddress: str | None = None
    ModelVersion: str | None = "2.0"
    MoreInfoUrl: str | None = None
    QualityAssuranceProcedure: str | None = None
    QualityAssuranceProcedureUrl: str | None = None
    ReleaseDate: datetime | None = None
    Status: STATUS | None = None
    Classes: list[BsddClass] = Field(default_factory=list)
    Properties: list[BsddProperty] = Field(default_factory=list)

    @classmethod
    def load(cls, path: str, *, sloppy: bool = False) -> BsddDictionary:
        if not path:
            return None
        path = Path(path)
        if not path.exists():
            return None
        with path.open(encoding="utf-8") as f:
            raw = json.load(f)
        return cls.from_data(raw, sloppy=sloppy)

    @classmethod
    def from_data(cls, raw: dict, *, sloppy: bool = False) -> BsddDictionary:
        """Validate raw JSON data. With ``sloppy=True`` invalid parts are dropped until it validates."""
        if not sloppy:
            return cls.model_validate(raw)

        try:
            return cls.model_validate(raw)
        except ValidationError as exc:
            cleaned = copy.deepcopy(raw)
            errors = exc.errors()
            seen = set()
            while True:
                progress = False
                for error in errors:
                    loc = tuple(error.get("loc", ()))
                    if error.get("type") == "missing":
                        # a required field is missing: drop the whole containing element
                        loc = loc[:-1]
                    if not loc or loc in seen:
                        continue
                    seen.add(loc)
                    _prune_error_path(cleaned, loc)
                    progress = True
                try:
                    return cls.model_validate(cleaned)
                except ValidationError as new_exc:
                    errors = new_exc.errors()
                    if not progress:
                        raise

    def save(self, path):
        with Path(path).open("w", encoding="utf-8") as file:
            json.dump(self.model_dump(mode="json", exclude_none=True), file)

    # add Parent to children after loading
    def model_post_init(self, context):
        for c in self.Classes:
            c._set_parent(self)
        for p in self.Properties:
            p._set_parent(self)


class BsddClass(CaseInsensitiveModel):
    @model_validator(mode="before")
    @classmethod
    def _fill_missing_class_property_codes(cls, data):
        """Give class properties without a Code (bSDD website exports) one derived from the property.

        Uses PropertyCode, otherwise the last segment of PropertyUri; if that code is already used in
        the class, the property set name is prefixed (and a number appended if still not unique).
        """
        if not isinstance(data, dict):
            return data
        key = "ClassProperties" if "ClassProperties" in data else "classProperties"
        items = data.get(key)
        if not isinstance(items, list) or not any(isinstance(cp, dict) and not _get(cp, "Code") for cp in items):
            return data
        used = {_get(cp, "Code") for cp in items if isinstance(cp, dict) and _get(cp, "Code")}
        fixed = []
        for item in items:
            if isinstance(item, dict) and not _get(item, "Code"):
                uri = _get(item, "PropertyUri") or ""
                base = _get(item, "PropertyCode") or uri.rstrip("/").rsplit("/", 1)[-1]
                if base:
                    code = base
                    if code in used and _get(item, "PropertySet"):
                        code = f"{_get(item, 'PropertySet')}_{base}"
                    n = 2
                    while code in used:
                        code = f"{base}_{n}"
                        n += 1
                    used.add(code)
                    fixed.append({**{k: v for k, v in item.items() if k not in ("Code", "code")}, "Code": code})
                    continue
            fixed.append(item)
        return {**data, key: fixed}

    Code: str
    Name: str
    ClassType: CLASS_TYPE = "Class"
    Definition: str | None = None
    Description: str | None = None
    ParentClassCode: str | None = None
    RelatedIfcEntityNamesList: list[str] | None = None
    Synonyms: list[str] | None = None
    ActivationDateUtc: datetime | None = None
    ReferenceCode: str | None = None
    CountriesOfUse: list[COUNTRY_CODE] | None = None
    CountryOfOrigin: COUNTRY_CODE | None = None
    CreatorLanguageIsoCode: LANGUAGE_ISO_CODE | None = None
    DeActivationDateUtc: datetime | None = None
    DeprecationExplanation: str | None = None
    DocumentReference: str | None = None
    OwnedUri: str | None = None
    ReplacedObjectCodes: list[str] | None = None
    ReplacingObjectCodes: list[str] | None = None
    RevisionDateUtc: datetime | None = None
    RevisionNumber: int | None = None
    Status: CLASS_STATUS | None = None
    SubdivisionsOfUse: list[str] | None = None
    Uid: str | None = None
    VersionDateUtc: datetime | None = None
    VersionNumber: int | None = None
    VisualRepresentationUri: str | None = None
    ClassProperties: list[BsddClassProperty] = Field(default_factory=list)
    ClassRelations: list[BsddClassRelation] = Field(default_factory=list)

    _parent_ref: weakref.ReferenceType[BsddDictionary] | None = PrivateAttr(
        default=None,
    )

    def _set_parent(self, parent: BsddDictionary) -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> BsddDictionary | None:
        return self._parent_ref() if self._parent_ref is not None else None

    def model_post_init(self, context):
        for c in self.ClassProperties:
            c._set_parent(self)
        for cr in self.ClassRelations:
            cr._set_parent(self)

    def _apply_code_side_effects(self, code: str) -> None:
        from bsdd_json.utils import class_utils as cl_utils

        if not code.strip():
            logger.info("Empty Code is not allowed")
            raise ValueError("Empty Code is not allowed")

        parent = self._parent_ref() if self._parent_ref else None
        if parent is not None and code in cl_utils.get_all_class_codes(parent):
            logger.info("Code '%s' exists already", code)
            raise ValueError(f"Code '{code}' exists already")

        # propagate to children
        for child in cl_utils.get_children(self):
            child.ParentClassCode = code


class BsddClassRelation(CaseInsensitiveModel):
    RelationType: CLASS_RELATION_TYPE
    RelatedClassUri: str
    RelatedClassName: str | None = None
    Fraction: float | None = None
    OwnedUri: str | None = None

    def _set_parent(self, parent: BsddClass) -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> BsddClass | None:
        return self._parent_ref() if self._parent_ref is not None else None


class BsddAllowedValue(CaseInsensitiveModel):
    Code: str
    Value: str
    Description: str | None = None
    Uri: str | None = None
    SortNumber: int | None = None
    OwnedUri: str | None = None


class BsddClassProperty(CaseInsensitiveModel):
    Code: str
    PropertyCode: str | None = None
    PropertyUri: str | None = None
    Description: str | None = None
    PropertySet: str | None = None
    Unit: str | None = None
    PredefinedValue: str | None = None
    IsRequired: bool | None = None
    IsWritable: bool | None = None
    MaxExclusive: float | None = None
    MaxInclusive: float | None = None
    MinExclusive: float | None = None
    MinInclusive: float | None = None
    Pattern: str | None = None
    OwnedUri: str | None = None
    PropertyType: Literal["Property", "Dependency"] | None = None
    SortNumber: int | None = None
    Symbol: str | None = None
    AllowedValues: list[BsddAllowedValue] = Field(default_factory=list)
    _parent_ref: weakref.ReferenceType[BsddClass] | None = PrivateAttr(
        default=None,
    )

    def _set_parent(self, parent: BsddClass) -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> BsddClass | None:
        return self._parent_ref() if self._parent_ref is not None else None

    @model_validator(mode="after")
    def _validate_property_code_or_uri(self):
        """Only one of PropertyCode or PropertyUri must be set (XOR)"""
        # normalize whitespace
        code = self.PropertyCode.strip() if self.PropertyCode and isinstance(self.PropertyCode, str) else None
        uri = self.PropertyUri.strip() if self.PropertyUri and isinstance(self.PropertyUri, str) else None

        # XOR: exactly one must be provided
        if bool(code) == bool(uri):
            raise ValueError(
                "Exactly one of PropertyCode or PropertyUri must be provided (not both, not neither)",
            )

        # assign normalized values back
        object.__setattr__(self, "PropertyCode", code)
        object.__setattr__(self, "PropertyUri", uri)
        return self


class BsddProperty(CaseInsensitiveModel):
    Code: str
    Name: str
    Definition: str | None = None
    Description: str | None = None
    DataType: DATATYPE_TYPE | None = None
    Units: list[UNITS_TYPE] | None = None
    Example: str | None = None
    ActivationDateUtc: datetime | None = None
    ConnectedPropertyCodes: list[str] | None = None
    CountriesOfUse: list[COUNTRY_CODE] | None = None
    CountryOfOrigin: COUNTRY_CODE | None = None
    CreatorLanguageIsoCode: LANGUAGE_ISO_CODE | None = None
    DeActivationDateUtc: datetime | None = None
    DeprecationExplanation: str | None = None
    Dimension: str | None = None
    DimensionLength: int | None = None
    DimensionMass: int | None = None
    DimensionTime: int | None = None
    DimensionElectricCurrent: int | None = None
    DimensionThermodynamicTemperature: int | None = None
    DimensionAmountOfSubstance: int | None = None
    DimensionLuminousIntensity: int | None = None
    DocumentReference: DOCUMENT_TYPE | None = None
    DynamicParameterPropertyCodes: list[str] | None = None
    IsDynamic: bool | None = None
    MaxExclusive: float | None = None
    MaxInclusive: float | None = None
    MinExclusive: float | None = None
    MinInclusive: float | None = None
    MethodOfMeasurement: str | None = None
    OwnedUri: str | None = None
    Pattern: str | None = None
    PhysicalQuantity: str | None = None
    PropertyValueKind: PROPERTY_VALUE_KIND_TYPE | None = None
    ReplacedObjectCodes: list[str] | None = None
    ReplacingObjectCodes: list[str] | None = None
    RevisionDateUtc: datetime | None = None
    RevisionNumber: int | None = None
    Status: PROPERTY_STATUS | None = None
    SubdivisionsOfUse: list[str] | None = None
    TextFormat: str | None = None
    Uid: str | None = None
    VersionDateUtc: datetime | None = None
    VersionNumber: int | None = None
    VisualRepresentationUri: str | None = None
    PropertyRelations: list[BsddPropertyRelation] = Field(default_factory=list)
    AllowedValues: list[BsddAllowedValue] = Field(default_factory=list)
    _parent_ref: weakref.ReferenceType[BsddDictionary] | None = PrivateAttr(
        default=None,
    )

    def _set_parent(self, parent: BsddDictionary) -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> BsddDictionary | None:
        return self._parent_ref() if self._parent_ref is not None else None

    def model_post_init(self, context):
        for pr in self.PropertyRelations:
            pr._set_parent(self)


class BsddPropertyRelation(CaseInsensitiveModel):
    RelatedPropertyName: str | None = None
    RelatedPropertyUri: str
    RelationType: PROPERTY_RELATION_TYPE
    OwnedUri: str | None = None

    def _set_parent(self, parent: BsddProperty) -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> BsddProperty | None:
        return self._parent_ref() if self._parent_ref is not None else None
