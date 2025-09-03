from __future__ import annotations

from pydantic import BaseModel

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, PrivateAttr, model_validator, ConfigDict
import json
import weakref
import logging


def _lower_first(s: str) -> str:
    return s[:1].lower() + s[1:] if s else s


class CaseInsensitiveModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_lower_first)


class BsddDictionary(CaseInsensitiveModel):
    OrganizationCode: str
    DictionaryCode: str
    DictionaryVersion: str
    LanguageIsoCode: str
    LanguageOnly: bool
    UseOwnUri: bool
    DictionaryName: Optional[str] = None
    DictionaryUri: Optional[str] = None
    License: Optional[str] = "MIT"
    LicenseUrl: Optional[str] = None
    ChangeRequestEmailAddress: Optional[str] = None
    ModelVersion: Optional[str] = "2.0"
    MoreInfoUrl: Optional[str] = None
    QualityAssuranceProcedure: Optional[str] = None
    QualityAssuranceProcedureUrl: Optional[str] = None
    ReleaseDate: Optional[datetime] = None
    Status: Optional[str] = None
    Classes: List[BsddClass] = Field(default_factory=list)
    Properties: List[BsddProperty] = Field(default_factory=list)

    @property
    def base(self) -> str:
        return self.DictionaryUri if self.UseOwnUri else "https://identifier.buildingsmart.org"

    @property
    def uri(self) -> str:
        return "/".join(
            [
                self.base(),
                "uri",
                self.OrganizationCode,
                str(self.DictionaryCode),
                str(self.DictionaryVersion),
            ]
        )

    @classmethod
    def load(cls, path) -> BsddDictionary:
        """Load from a JSON file and validate via the normalizer above."""
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # The model_validator(before) handles list/dict/nested shapes
        return cls.model_validate(raw)

    def save(self, path):
        with open(path, "w") as file:
            json.dump(self.model_dump(mode="json", exclude_none=True), file)

    def model_post_init(self, context):
        for c in self.Classes:
            c._set_parent(self)
        for p in self.Properties:
            p._set_parent(self)


class BsddClass(CaseInsensitiveModel):
    Code: str
    Name: str
    ClassType: str
    Definition: Optional[str] = None
    Description: Optional[str] = None
    ParentClassCode: Optional[str | None] = None
    RelatedIfcEntityNamesList: Optional[List[str]] = None
    Synonyms: Optional[List[str]] = None
    ActivationDateUtc: Optional[datetime] = None
    ReferenceCode: Optional[str] = None
    CountriesOfUse: Optional[List[str]] = None
    CountryOfOrigin: Optional[str] = None
    CreatorLanguageIsoCode: Optional[str] = None
    DeActivationDateUtc: Optional[datetime] = None
    DeprecationExplanation: Optional[str] = None
    DocumentReference: Optional[str] = None
    OwnedUri: Optional[str] = None
    ReplacedObjectCodes: Optional[List[str]] = None
    ReplacingObjectCodes: Optional[List[str]] = None
    RevisionDateUtc: Optional[datetime] = None
    RevisionNumber: Optional[int] = None
    Status: Optional[str] = None
    SubdivisionsOfUse: Optional[List[str]] = None
    Uid: Optional[str] = None
    VersionDateUtc: Optional[datetime] = None
    VersionNumber: Optional[int] = None
    VisualRepresentationUri: Optional[str] = None
    ClassProperties: List[BsddClassProperty] = Field(default_factory=list)
    ClassRelations: List[BsddClassRelation] = Field(default_factory=list)

    _parent_ref: Optional[weakref.ReferenceType["BsddDictionary"]] = PrivateAttr(default=None)

    def _set_parent(self, parent: "BsddDictionary") -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> Optional[BsddDictionary]:
        return self._parent_ref() if self._parent_ref is not None else None

    def model_post_init(self, context):
        for c in self.ClassProperties:
            c._set_parent(self)

    def _apply_code_side_effects(self, code: str) -> None:
        from bsdd_parser.utils import bsdd_class as class_utils

        if not code.strip():
            logging.info("Empty Code is not allowed")
            raise ValueError("Empty Code is not allowed")

        parent = self._parent_ref() if self._parent_ref else None
        if parent is not None and code in class_utils.get_all_class_codes(parent):
            logging.info(f"Code '{code}' exists already")
            raise ValueError(f"Code '{code}' exists already")

        # propagate to children
        for child in class_utils.get_children(self):
            child.ParentClassCode = code

    # # validate the field value itself (runs on parse and assignment validation)
    # @field_validator("Code", mode="before")
    # @classmethod
    # def _normalize_code(cls, v: str):
    #     if v is None:
    #         return v
    #     return v.strip()

    @model_validator(mode="after")
    def _after_init(self):
        # run once after parsing so JSON -> model path also triggers side-effects
        self._apply_code_side_effects(self.Code)
        return self

    # optional: a method to change Code at runtime with the same guarantees
    def set_code(self, code: str) -> None:
        if code == self.Code:
            return
        self._apply_code_side_effects(code)
        # assign without recursion (no property involved)
        object.__setattr__(self, "Code", code)


class BsddAllowedValue(CaseInsensitiveModel):
    Code: str
    Value: str
    Description: Optional[str] = None
    Uri: Optional[str] = None
    SortNumber: Optional[int] = None
    OwnedUri: Optional[str] = None


class BsddPropertyRelation(CaseInsensitiveModel):
    RelatedPropertyName: Optional[str] = None
    RelatedPropertyUri: str
    RelationType: str
    OwnedUri: Optional[str] = None


class BsddClassProperty(CaseInsensitiveModel):
    Code: str
    PropertyCode: Optional[str] = None
    PropertyUri: Optional[str] = None
    Description: Optional[str] = None
    PropertySet: Optional[str] = None
    Unit: Optional[str] = None
    PredefinedValue: Optional[str] = None
    IsRequired: Optional[bool] = None
    IsWritable: Optional[bool] = None
    MaxExclusive: Optional[float] = None
    MaxInclusive: Optional[float] = None
    MinExclusive: Optional[float] = None
    MinInclusive: Optional[float] = None
    Pattern: Optional[str] = None
    OwnedUri: Optional[str] = None
    PropertyType: Optional[str] = None
    SortNumber: Optional[int] = None
    Symbol: Optional[str] = None
    AllowedValues: List[BsddAllowedValue] = Field(default_factory=list)
    _parent_ref: Optional[weakref.ReferenceType["BsddClass"]] = PrivateAttr(default=None)

    def _set_parent(self, parent: "BsddClass") -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> Optional[BsddClass]:
        return self._parent_ref() if self._parent_ref is not None else None

    @model_validator(mode="after")
    def _validate_property_code_or_uri(self):
        # normalize whitespace
        code = (
            self.PropertyCode.strip()
            if self.PropertyCode and isinstance(self.PropertyCode, str)
            else None
        )
        uri = (
            self.PropertyUri.strip()
            if self.PropertyUri and isinstance(self.PropertyUri, str)
            else None
        )

        # XOR: exactly one must be provided
        if bool(code) == bool(uri):
            raise ValueError(
                "Exactly one of PropertyCode or PropertyUri must be provided (not both, not neither)"
            )

        # assign normalized values back
        object.__setattr__(self, "PropertyCode", code)
        object.__setattr__(self, "PropertyUri", uri)
        return self


class BsddProperty(CaseInsensitiveModel):
    Code: str
    Name: str
    Definition: Optional[str] = None
    Description: Optional[str] = None
    DataType: Optional[str] = None
    Units: Optional[List[str]] = None
    Example: Optional[str] = None
    ActivationDateUtc: Optional[datetime] = None
    ConnectedPropertyCodes: Optional[List[str]] = None
    CountriesOfUse: Optional[List[str]] = None
    CountryOfOrigin: Optional[str] = None
    CreatorLanguageIsoCode: Optional[str] = None
    DeActivationDateUtc: Optional[datetime] = None
    DeprecationExplanation: Optional[str] = None
    Dimension: Optional[str] = None
    DimensionLength: Optional[int] = None
    DimensionMass: Optional[int] = None
    DimensionTime: Optional[int] = None
    DimensionElectricCurrent: Optional[int] = None
    DimensionThermodynamicTemperature: Optional[int] = None
    DimensionAmountOfSubstance: Optional[int] = None
    DimensionLuminousIntensity: Optional[int] = None
    DocumentReference: Optional[str] = None
    DynamicParameterPropertyCodes: Optional[List[str]] = None
    IsDynamic: Optional[bool] = None
    MaxExclusive: Optional[float] = None
    MaxInclusive: Optional[float] = None
    MinExclusive: Optional[float] = None
    MinInclusive: Optional[float] = None
    MethodOfMeasurement: Optional[str] = None
    OwnedUri: Optional[str] = None
    Pattern: Optional[str] = None
    PhysicalQuantity: Optional[str] = None
    PropertyValueKind: Optional[str] = None
    ReplacedObjectCodes: Optional[List[str]] = None
    ReplacingObjectCodes: Optional[List[str]] = None
    RevisionDateUtc: Optional[datetime] = None
    RevisionNumber: Optional[int] = None
    Status: Optional[str] = None
    SubdivisionsOfUse: Optional[List[str]] = None
    TextFormat: Optional[str] = None
    Uid: Optional[str] = None
    VersionDateUtc: Optional[datetime] = None
    VersionNumber: Optional[int] = None
    VisualRepresentationUri: Optional[str] = None
    PropertyRelations: List[BsddPropertyRelation] = Field(default_factory=list)
    AllowedValues: List[BsddAllowedValue] = Field(default_factory=list)
    _parent_ref: Optional[weakref.ReferenceType["BsddDictionary"]] = PrivateAttr(default=None)

    def _set_parent(self, parent: "BsddDictionary") -> None:
        self._parent_ref = weakref.ref(parent)

    def parent(self) -> Optional[BsddDictionary]:
        return self._parent_ref() if self._parent_ref is not None else None


class BsddClassRelation(CaseInsensitiveModel):
    RelationType: str
    RelatedClassUri: str
    RelatedClassName: Optional[str] = None
    Fraction: Optional[float] = None
    OwnedUri: Optional[str] = None
