from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import Field, field_validator
from pydantic_xml import BaseXmlModel, element


# ---------------------------------------------------------------------------
# Simple type aliases  (validation only – not XML markers)
# ---------------------------------------------------------------------------

MIN_DATETIME = datetime(1970, 1, 1, 12, 0, 0)

# [a-z]{2}-[A-Z]{2} or "IFC-IFC"
Language = Annotated[str, Field(pattern=r"^([a-z]{2}-[A-Z]{2}|IFC-IFC)$")]

# Two uppercase letters or "IFC"
Country = Annotated[str, Field(pattern=r"^([A-Z]{2}|IFC)$")]

# ISO 3166-2 subdivision, e.g. "DE-BY"
Subdivision = Annotated[str, Field(pattern=r"^[A-Z]{2}-[0-9A-Z]{1,4}$")]

# http/https/ftp/file URL
Url = Annotated[
    str,
    Field(
        pattern=r"^(https?|ftp|file)://[-a-zA-Z0-9+@#/%?=~_|!:,.;]*[-a-zA-Z0-9+@#/%=~_|]$"
    ),
]

# Non-empty string up to 1 500 characters
BimDeString = Annotated[str, Field(min_length=1, max_length=1500)]

# UUID / GUID – same pattern as [A-Fa-f0-9]{8}-…
Guid = UUID

# ISO 80000 dimension string, e.g. "1 0 0 0 0 0 0" or "without"
Dimension = Annotated[
    str,
    Field(
        pattern=r"^(([-]?(\d{1,3}|1000)(\.?\d{1,3})?\s){6}([-]?(\d{1,3}|1000)(\.?\d{1,3})?)|without)$"
    ),
]

# Boundary value pair: (min,max) in float notation
BoundaryValuePair = Annotated[
    str,
    Field(
        pattern=r"^\([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?,[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\)$"
    ),
]

# Version / revision numbers must be >= 1
VersionNumber = Annotated[int, Field(ge=1)]
RevisionNumber = Annotated[int, Field(ge=1)]


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class Status(str, Enum):
    active = "active"
    inactive = "inactive"


class DynamicProperty(str, Enum):
    yes = "yes"
    no = "no"


class CategoryOfGroupOfProperties(str, Enum):
    alternative_use = "alternative use"
    class_ = "class"
    composed_property = "composed property"
    domain = "domain"
    reference_document = "reference document"
    name_property_set = "name property set"


# ---------------------------------------------------------------------------
# Helper: datetime >= 1970-01-01T12:00:00
# ---------------------------------------------------------------------------

_DATE_FIELDS = (
    "dateOfCreation",
    "dateOfActivation",
    "dateOfLastChange",
    "dateOfRevision",
    "dateOfVersion",
    "dateOfDeactivation",
)


def _check_min_datetime(v: Optional[datetime]) -> Optional[datetime]:
    if v is not None and v.replace(tzinfo=None) < MIN_DATETIME:
        raise ValueError(f"Date must be >= {MIN_DATETIME}, got {v}")
    return v


# ---------------------------------------------------------------------------
# Shared nested models
# ---------------------------------------------------------------------------


class NameInLanguage(BaseXmlModel, tag="namesInLanguage"):
    name: BimDeString = element()
    language: Language = element()


class DefinitionInLanguage(BaseXmlModel, tag="definitionsInLanguage"):
    definition: BimDeString = element()
    language: Language = element()


class DescriptionInLanguage(BaseXmlModel, tag="descriptionsInLanguage"):
    description: BimDeString = element()
    language: Language = element()


class ExampleInLanguage(BaseXmlModel, tag="examplesInLanguage"):
    example: BimDeString = element()
    language: Language = element()


class PhysicalQuantity(BaseXmlModel, tag="physicalQuantity"):
    """PA027 – (siUnit | language) pair."""

    siUnit: BimDeString = element()
    language: Language = element()


class SymbolInPropertyGroup(
    BaseXmlModel, tag="symbolsOfThePropertyInAGivenPropertyGroup"
):
    """PA022 – (symbol, propGroupID) pair."""

    symbol: BimDeString = element()
    propGroupID: Guid = element()


class DigitalFormat(BaseXmlModel, tag="digitalFormat"):
    """PA037 – (precision, unitOfMeasure) pair."""

    precision: BimDeString = element()
    unitOfMeasure: BimDeString = element()


class TextFormat(BaseXmlModel, tag="textFormat"):
    """PA038 – (encoding, numberOfCharacters) pair."""

    encoding: BimDeString = element()
    numberOfCharacters: BimDeString = element()


class PossibleValueInLanguage(BaseXmlModel, tag="listOfPossibleValuesInLanguage"):
    """PA039 – (possibleValue, language) pair."""

    possibleValue: BimDeString = element()
    language: Language = element()


class BoundaryValues(BaseXmlModel, tag="boundaryValues"):
    """PA040 – list of boundary-value pairs plus a unit."""

    boundaryValuePairs: List[BoundaryValuePair] = element(min_length=1)
    unit: BimDeString = element()


class NameOfDefiningValue(BaseXmlModel, tag="namesOfTheDefiningValues"):
    """PA034 – (name, language) pair for array column headers."""

    name: BimDeString = element()
    language: Language = element()


# ---------------------------------------------------------------------------
# Dictionary-relation nested models
# ---------------------------------------------------------------------------


class PropertyGroupDictRelation(
    BaseXmlModel,
    tag="relationOfThePropertyGroupIdentifiersInTheInterconnectedDictionaries",
):
    """GA014 – (propGroupID, interConDictID) pair."""

    propGroupID: BimDeString = element()
    interConDictID: BimDeString = element()


class PropertyDictRelation(
    BaseXmlModel,
    tag="relationOfThePropertyIdentifiersInTheInterconnectedDictionaries",
):
    """PA014 – (propertyID, interConDictID) pair."""

    propertyID: BimDeString = element()
    interConDictID: BimDeString = element()


# ---------------------------------------------------------------------------
# PropertyGroup (GA001–GA023)
# ---------------------------------------------------------------------------


class PropertyGroup(BaseXmlModel, tag="propertyGroup"):
    guid: Guid = element()  # GA001
    status: Status = element()  # GA002
    dateOfCreation: datetime = element()  # GA003
    dateOfActivation: Optional[datetime] = element(default=None)  # GA004
    dateOfLastChange: Optional[datetime] = element(default=None)  # GA005
    dateOfRevision: datetime = element()  # GA006
    dateOfVersion: datetime = element()  # GA007
    dateOfDeactivation: Optional[datetime] = element(default=None)  # GA008
    versionNumber: VersionNumber = element()  # GA009
    revisionNumber: RevisionNumber = element()  # GA010
    replaces: List[Guid] = element(default_factory=list)  # GA011
    replacedBy: List[Guid] = element(default_factory=list)  # GA012
    deprecationExplanation: Optional[BimDeString] = element(default=None)  # GA013
    relationOfThePropertyGroupIdentifiersInTheInterconnectedDictionaries: List[
        PropertyGroupDictRelation
    ] = element(default_factory=list)  # GA014
    creatorsLanguage: Language = element()  # GA015
    namesInLanguage: List[NameInLanguage] = element(min_length=1)  # GA016
    definitionsInLanguage: List[DefinitionInLanguage] = element(min_length=1)  # GA017
    visualRepresentation: List[Url] = element(default_factory=list)  # GA018
    countryOfUse: List[Country] = element(min_length=1)  # GA019
    subdivisionOfUse: List[Subdivision] = element(default_factory=list)  # GA020
    countryOfOrigin: Optional[Country] = element(default=None)  # GA021
    categoryOfGroupOfProperties: CategoryOfGroupOfProperties = element()  # GA022
    parentGroupOfProperties: Optional[Guid] = element(default=None)  # GA023

    @field_validator(*_DATE_FIELDS, mode="after")
    @classmethod
    def _validate_dates(cls, v: Optional[datetime]) -> Optional[datetime]:
        return _check_min_datetime(v)


# ---------------------------------------------------------------------------
# Property (PA001–PA040)
# ---------------------------------------------------------------------------


class Property(BaseXmlModel, tag="property"):
    guid: Guid = element()  # PA001
    status: Status = element()  # PA002
    dateOfCreation: datetime = element()  # PA003
    dateOfActivation: Optional[datetime] = element(default=None)  # PA004
    dateOfLastChange: Optional[datetime] = element(default=None)  # PA005
    dateOfRevision: datetime = element()  # PA006
    dateOfVersion: datetime = element()  # PA007
    dateOfDeactivation: Optional[datetime] = element(default=None)  # PA008
    versionNumber: VersionNumber = element()  # PA009
    revisionNumber: RevisionNumber = element()  # PA010
    replaces: List[Guid] = element(default_factory=list)  # PA011
    replacedBy: List[Guid] = element(default_factory=list)  # PA012
    deprecationExplanation: Optional[BimDeString] = element(default=None)  # PA013
    relationOfThePropertyIdentifiersInTheInterconnectedDictionaries: List[
        PropertyDictRelation
    ] = element(default_factory=list)  # PA014
    creatorsLanguage: Language = element()  # PA015
    namesInLanguage: List[NameInLanguage] = element(min_length=1)  # PA016
    definitionsInLanguage: List[DefinitionInLanguage] = element(min_length=1)  # PA017
    descriptionsInLanguage: List[DescriptionInLanguage] = element(
        default_factory=list
    )  # PA018
    examplesInLanguage: List[ExampleInLanguage] = element(default_factory=list)  # PA019
    connectedProperties: List[Guid] = element(default_factory=list)  # PA020
    groupOfProperties: List[Guid] = element(min_length=0)  # PA021
    symbolsOfThePropertyInAGivenPropertyGroup: List[SymbolInPropertyGroup] = element(
        default_factory=list
    )  # PA022
    visualRepresentation: List[Url] = element(default_factory=list)  # PA023
    countryOfUse: List[Country] = element(min_length=1)  # PA024
    subdivisionOfUse: List[Subdivision] = element(default_factory=list)  # PA025
    countryOfOrigin: Optional[Country] = element(default=None)  # PA026
    physicalQuantity: List[PhysicalQuantity] = element(min_length=1)  # PA027
    dimension: Optional[Dimension] = element(default=None)  # PA028
    methodOfMeasurement: Optional[BimDeString] = element(default=None)  # PA029
    dataType: BimDeString = element()  # PA030
    dynamicProperty: DynamicProperty = element()  # PA031
    parametersOfTheDynamicProperty: List[Guid] = element(default_factory=list)  # PA032
    units: List[BimDeString] = element(default_factory=list)  # PA033
    namesOfTheDefiningValues: List[NameOfDefiningValue] = element(
        default_factory=list
    )  # PA034
    definingValues: List[BimDeString] = element(default_factory=list)  # PA035
    tolerance: List[Decimal] = element(default_factory=list)  # PA036
    digitalFormat: List[DigitalFormat] = element(default_factory=list)  # PA037
    textFormat: Optional[TextFormat] = element(default=None)  # PA038
    listOfPossibleValuesInLanguage: List[PossibleValueInLanguage] = element(
        default_factory=list
    )  # PA039
    boundaryValues: List[BoundaryValues] = element(default_factory=list)  # PA040

    @field_validator(*_DATE_FIELDS, mode="after")
    @classmethod
    def _validate_dates(cls, v: Optional[datetime]) -> Optional[datetime]:
        return _check_min_datetime(v)


# ---------------------------------------------------------------------------
# Container – root element
# ---------------------------------------------------------------------------


class Container(BaseXmlModel, tag="Container"):
    propertyGroup: List[PropertyGroup] = element(default_factory=list)
    # "property" is a Python built-in, so the field is named property_ and the
    # XML tag is set explicitly to "property" via the nested model's class tag.
    property_: List[Property] = element(tag="property", default_factory=list)
