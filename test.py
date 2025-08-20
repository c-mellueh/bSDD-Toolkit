from __future__ import annotations

from pydantic import BaseModel

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field,PrivateAttr
import json
import weakref

class BsddDictionary(BaseModel):
    OrganizationCode: str
    DictionaryCode: str
    DictionaryName: str
    DictionaryVersion: str
    LanguageIsoCode: str
    LanguageOnly: bool
    UseOwnUri: bool
    DictionaryUri: str = ""
    License: str = "MIT"
    LicenseUrl: Optional[str] = None
    ChangeRequestEmailAddress: str = ""
    ModelVersion: str = "2.0"
    MoreInfoUrl: Optional[str] = None
    QualityAssuranceProcedure: Optional[str] = None
    QualityAssuranceProcedureUrl: Optional[str] = None
    ReleaseDate: Optional[datetime] = None
    Status: Optional[str] = None
    Classes: List[BsddClass] = Field(default_factory=list)
    Properties: List[BsddProperty] = Field(default_factory=list)

    def base(self) -> str:
        return (
            self.DictionaryUri
            if self.UseOwnUri
            else "https://identifier.buildingsmart.org"
        )

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

    def model_post_init(self, context):
        for c in self.Classes:
            c._set_parent(self)
    

class BsddClass(BaseModel):
    Code: str
    Name: str
    ClassType: str
    Definition: Optional[str] = None
    Description: Optional[str] = None
    ParentClassCode: Optional[str] = None
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


    def uri(self, dictionary: BsddDictionary) -> str:
        return "/".join([dictionary.uri(), "class", self.Code])

class BsddAllowedValue(BaseModel):
    Code: str
    Value: str
    Description: Optional[str] = None
    Uri: Optional[str] = None
    SortNumber: Optional[int] = None
    OwnedUri: Optional[str] = None


class BsddPropertyRelation(BaseModel):
    RelatedPropertyName: Optional[str] = None
    RelatedPropertyUri: str
    RelationType: str
    OwnedUri: Optional[str] = None


class BsddClassProperty(BaseModel):
    Code: str
    PropertyCode: str
    PropertyUri: str
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


class BsddProperty(BaseModel):
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


class BsddClassRelation(BaseModel):
    RelationType: str
    RelatedClassUri: str
    RelatedClassName: Optional[str] = None
    Fraction: Optional[float] = None
    OwnedUri: Optional[str] = None







t = BsddDictionary.load(r"./som-0.2.0.json")
out = t.model_dump_json(by_alias=True,exclude_none=True)
with open ("output.json","w") as file:
    file.write(out)
