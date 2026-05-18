from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import Field, field_validator
from pydantic_xml import BaseXmlModel, attr, element


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
    Field(pattern=r"^(https?|ftp|file)://[-a-zA-Z0-9+@#/%?=~_|!:,.;]*[-a-zA-Z0-9+@#/%=~_|]$"),
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


class SymbolInPropertyGroup(BaseXmlModel, tag="symbolsOfThePropertyInAGivenPropertyGroup"):
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
    relationOfThePropertyIdentifiersInTheInterconnectedDictionaries: List[PropertyDictRelation] = (
        element(default_factory=list)
    )  # PA014
    creatorsLanguage: Language = element()  # PA015
    namesInLanguage: List[NameInLanguage] = element(min_length=1)  # PA016
    definitionsInLanguage: List[DefinitionInLanguage] = element(min_length=1)  # PA017
    descriptionsInLanguage: List[DescriptionInLanguage] = element(default_factory=list)  # PA018
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
    namesOfTheDefiningValues: List[NameOfDefiningValue] = element(default_factory=list)  # PA034
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


# ===========================================================================
# ISO 23387 (referenced by ISO 7817-3) and ISO 7817-3 LOIN data classes
# ---------------------------------------------------------------------------
# Namespaces:
#   loin = https://iso.org/2024/LOIN              (ISO 7817-3 target namespace)
#   dt   = https://standards.iso.org/iso/23387/ed-2/en/  (ISO 23387 imported)
#
# Conventions:
#   * ISO 23387 types live in the "dt" namespace (elementFormDefault=qualified
#     in ISO 23387). Their classes carry ns="dt".
#   * ISO 7817-3 (LOIN) types have their target namespace declared on the root
#     element only; local elements appear unqualified in the produced XML
#     (matching the examples in ISO 7817-3 Annex C).
#   * The global attributes dt:GUID, dt:referenceURI and dt:about are always
#     emitted with the dt prefix.
# ===========================================================================

LOIN_NS = "https://iso.org/2024/LOIN"
DT_NS = "https://standards.iso.org/iso/23387/ed-2/en/"
LOIN_NSMAP = {"loin": LOIN_NS, "dt": DT_NS}


# ---------------------------------------------------------------------------
# Simple types / enumerations used by ISO 23387 + ISO 7817-3
# ---------------------------------------------------------------------------


class IsoScale(str, Enum):
    LINEAR = "LINEAR"
    LOGARITHMIC = "LOGARITHMIC"


class IsoBase(str, Enum):
    ONE = "ONE"
    TWO = "TWO"
    E = "E"
    PI = "PI"
    TEN = "TEN"


class IsoDataTypeName(str, Enum):
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    RATIONAL = "RATIONAL"
    REAL = "REAL"
    COMPLEX = "COMPLEX"
    STRING = "STRING"
    DATETIME = "DATETIME"


# Rational pattern from ISO 23387 RationalType
IsoRational = Annotated[str, Field(pattern=r"^[+-]?[0-9]+(/[1-9][0-9]*)?$")]


class LoinShapeAssembly(str, Enum):
    NOT_REQUIRED = "NotRequired"
    SINGLE_OBJECT_SINGULAR_SHAPE = "SingleObjectSingularShape"
    SINGLE_OBJECT_MULTIPLE_SHAPES = "SingleObjectMultipleShapes"
    MULTIPLE_OBJECTS = "MultipleObjects"


class LoinShapeRepresentation(str, Enum):
    NOT_REQUIRED = "NotRequired"
    SINGLE_BOUNDING_PRIMITIVE = "SingleBoundingPrimitive"
    OUTER_SHELL_AS_SINGULAR_SHAPE = "OuterShellAsSingularShape"
    OUTER_SHELL_AS_SEPARATE_SHAPES = "OuterShellAsSeparateShapes"


class LoinInsideGeometry(str, Enum):
    NOT_REQUIRED = "NotRequired"
    NO_INSIDE_GEOMETRY = "NoInsideGeometry"
    INSIDE_GEOMETRY_AS_PART_OF_SHAPE = "InsideGeometryAsPartOfShape"
    SEPARATE_SHAPES = "SeparateShapes"


class LoinConnections(str, Enum):
    NOT_REQUIRED = "NotRequired"
    NO_CONNECTIONS = "NoConnections"
    CONNECTIONS_AS_PART_OF_SHAPE = "ConnectionsAsPartOfShape"
    SEPARATE_SHAPES = "SeparateShapes"


class LoinOpenings(str, Enum):
    NOT_REQUIRED = "NotRequired"
    NO_OPENINGS = "NoOpenings"
    OPENINGS_AS_PART_OF_SHAPE = "OpeningsAsPartOfShape"
    SEPARATE_SHAPES = "SeparateShapes"


class LoinOperatingAndClearanceZones(str, Enum):
    NOT_REQUIRED = "NotRequired"
    NO_ZONES = "NoZones"
    ZONES_AS_PART_OF_SHAPE = "ZonesAsPartOfShape"
    SEPARATE_SHAPES = "SeparateShapes"


class LoinFeatures(str, Enum):
    NOT_REQUIRED = "NotRequired"
    NO_FEATURES = "NoFeatures"
    FEATURES_AS_PART_OF_SHAPE = "FeaturesAsPartOfShape"
    SEPARATE_SHAPES = "SeparateShapes"


class LoinDimensionality(str, Enum):
    NOT_REQUIRED = "NotRequired"
    D0 = "0D"
    D1 = "1D"
    D2 = "2D"
    D3 = "3D"


class LoinAppearance(str, Enum):
    NOT_REQUIRED = "NotRequired"
    NO_APPEARANCE_INFORMATION = "NoAppearanceInformation"
    SYMBOLIC_BY_MAPPING = "SymbolicByMapping"
    SINGULAR_MATERIAL = "SingularMaterial"
    MULTIPLE_MATERIALS = "MultipleMaterials"
    CONCEPTUAL_APPEARANCE = "ConceptualAppearance"
    REALISTIC_APPEARANCE = "RealisticAppearance"


class LoinParametricBehaviour(str, Enum):
    NOT_REQUESTED = "NotRequested"
    REQUESTED = "Requested"


class LoinCoordinateReferenceSystemEnum(str, Enum):
    NOT_REQUIRED = "NotRequired"
    PROJECTED_CRS = "ProjectedCRS"
    ENGINEERING_CRS = "EngineeringCRS"
    GEOGRAPHIC_CRS = "GeographicCRS"


class LoinPositioningEnum(str, Enum):
    NOT_DEFINED = "NotDefined"
    ABSOLUTE = "Absolute"
    RELATIVE = "Relative"


# ---------------------------------------------------------------------------
# ISO 23387 - building blocks reused by ISO 7817-3
# ---------------------------------------------------------------------------


class DtRef(BaseXmlModel, ns="dt", nsmap=LOIN_NSMAP):
    """dt:ReferenceType — referenceURI and/or GUID, no element content."""

    reference_uri: Optional[str] = attr(name="referenceURI", ns="dt", default=None)
    guid: Optional[Guid] = attr(name="GUID", ns="dt", default=None)


class DtMultiLangText(BaseXmlModel, ns="dt", nsmap=LOIN_NSMAP):
    """dt:MultiLanguageTextType — text content with a 'language' attribute."""

    language: str = attr(name="language")
    text: str = ""


class IsoValue(BaseXmlModel, tag="Value", ns="dt", nsmap=LOIN_NSMAP):
    order: Optional[int] = attr(name="order", default=None)
    text: str = ""


class IsoValueList(BaseXmlModel, tag="ValueList", ns="dt", nsmap=LOIN_NSMAP):
    language: str = attr(name="language")
    values: List[IsoValue] = element(tag="Value", ns="dt", min_length=1)


class IsoPossibleValues(BaseXmlModel, tag="PossibleValues", ns="dt", nsmap=LOIN_NSMAP):
    value_lists: List[IsoValueList] = element(tag="ValueList", ns="dt", min_length=1)


class IsoBoundary(BaseXmlModel, ns="dt", nsmap=LOIN_NSMAP):
    value: str = attr(name="value")


class IsoDataFormat(BaseXmlModel, tag="DataFormat", ns="dt", nsmap=LOIN_NSMAP):
    value: str = attr(name="value")


class IsoDataType(BaseXmlModel, tag="DataType", ns="dt", nsmap=LOIN_NSMAP):
    """dt:DataTypeType — wraps DataType name + optional constraints."""

    name: Optional[IsoDataTypeName] = attr(name="name", default=None)
    min_inclusive: Optional[IsoBoundary] = element(tag="MinInclusive", ns="dt", default=None)
    min_exclusive: Optional[IsoBoundary] = element(tag="MinExclusive", ns="dt", default=None)
    max_inclusive: Optional[IsoBoundary] = element(tag="MaxInclusive", ns="dt", default=None)
    max_exclusive: Optional[IsoBoundary] = element(tag="MaxExclusive", ns="dt", default=None)
    data_format: Optional[IsoDataFormat] = element(tag="DataFormat", ns="dt", default=None)
    possible_values: Optional[IsoPossibleValues] = element(
        tag="PossibleValues", ns="dt", default=None
    )


class DtConceptType(BaseXmlModel, ns="dt", nsmap=LOIN_NSMAP):
    """dt:ConceptType — abstract base for ISO 23387 concepts.

    Holds the GUID, the (required) dateOfCreation, plus the common
    descriptive elements that ConceptType defines as an unbounded choice.
    """

    # Attributes
    about: Optional[str] = attr(name="about", ns="dt", default=None)
    guid: Guid = attr(name="GUID", ns="dt")
    date_of_creation: datetime = attr(name="dateOfCreation")

    # Elements — every dt:ConceptType-derived element nests its children in
    # the dt namespace because ISO 23387 declares elementFormDefault=qualified.
    names: List[DtMultiLangText] = element(tag="Name", ns="dt", min_length=1)
    definition: Optional[DtMultiLangText] = element(tag="Definition", ns="dt", default=None)
    reference_document_refs: List[DtRef] = element(
        tag="ReferenceDocumentRef", ns="dt", default_factory=list
    )
    descriptions: List[DtMultiLangText] = element(tag="Description", ns="dt", default_factory=list)
    examples: List[DtMultiLangText] = element(tag="Example", ns="dt", default_factory=list)
    similar_to_refs: List[DtRef] = element(tag="SimilarToRef", ns="dt", default_factory=list)
    language_of_creator: Optional[str] = element(tag="LanguageOfCreator", ns="dt", default=None)
    country_of_origin: Optional[str] = element(tag="CountryOfOrigin", ns="dt", default=None)
    visual_representation: List[str] = element(
        tag="VisualRepresentation", ns="dt", default_factory=list
    )
    major_version: Optional[int] = element(tag="MajorVersion", ns="dt", default=None)
    minor_version: Optional[int] = element(tag="MinorVersion", ns="dt", default=None)
    status: List[str] = element(tag="Status", ns="dt", default_factory=list)
    replaced_objects_refs: List[DtRef] = element(
        tag="ReplacedObjectsRef", ns="dt", default_factory=list
    )
    deprecation_explanation: List[str] = element(
        tag="DeprecationExplanation", ns="dt", default_factory=list
    )
    dictionary_ref: Optional[DtRef] = element(tag="DictionaryRef", ns="dt", default=None)


class DtSubjectType(DtConceptType):
    """dt:SubjectType — ConceptType + HasPartRef / IsSubtypeOfRef."""

    has_part_refs: List[DtRef] = element(tag="HasPartRef", ns="dt", default_factory=list)
    is_subtype_of_ref: Optional[DtRef] = element(tag="IsSubtypeOfRef", ns="dt", default=None)


class IsoObjectType(DtSubjectType):
    """dt:ObjectTypeType — represents a kind of object."""

    pass


class IsoGroupOfProperties(DtSubjectType):
    """dt:GroupOfPropertiesType — groups properties (HasPropertyRef 1..*)."""

    has_property_refs: List[DtRef] = element(tag="HasPropertyRef", ns="dt", min_length=1)


class IsoProperty(DtConceptType):
    """dt:PropertyType — represents a property used in a data template."""

    data_type: IsoDataType = element(tag="DataType", ns="dt")
    symbols: List[str] = element(tag="Symbol", ns="dt", default_factory=list)
    dimension_ref: Optional[DtRef] = element(tag="DimensionRef", ns="dt", default=None)
    unit_refs: List[DtRef] = element(tag="UnitRef", ns="dt", default_factory=list)
    quantity_kind_refs: List[DtRef] = element(tag="QuantityKindRef", ns="dt", default_factory=list)
    is_dependent_on_refs: List[DtRef] = element(
        tag="IsDependentOnRef", ns="dt", default_factory=list
    )
    is_specialization_of_ref: Optional[DtRef] = element(
        tag="IsSpecializationOfRef", ns="dt", default=None
    )


class IsoUnit(DtConceptType):
    """dt:UnitType — a unit of measurement."""

    symbols: List[DtMultiLangText] = element(tag="Symbol", ns="dt", default_factory=list)
    dimension_ref: DtRef = element(tag="DimensionRef", ns="dt")
    scale: IsoScale = element(tag="Scale", ns="dt")
    base: IsoBase = element(tag="Base", ns="dt")
    coefficient: IsoRational = element(tag="Coefficient", ns="dt")
    offset: IsoRational = element(tag="Offset", ns="dt")


class IsoDimensionConcept(DtConceptType):
    """dt:DimensionType — physical dimension expressed via exponents."""

    amount_of_substance: Decimal = element(tag="DimensionExponentForAmountOfSubstance", ns="dt")
    electric_current: Decimal = element(tag="DimensionExponentForElectricCurrent", ns="dt")
    length: Decimal = element(tag="DimensionExponentForLength", ns="dt")
    luminous_intensity: Decimal = element(tag="DimensionExponentForLuminousIntensity", ns="dt")
    mass: Decimal = element(tag="DimensionExponentForMass", ns="dt")
    thermodynamic_temperature: Decimal = element(
        tag="DimensionExponentForThermodynamicTemperature", ns="dt"
    )
    time: Decimal = element(tag="DimensionExponentForTime", ns="dt")


class IsoQuantityKind(DtConceptType):
    """dt:QuantityKindType — a kind of quantity (e.g. Length, Mass)."""

    dimension_ref: DtRef = element(tag="DimensionRef", ns="dt")


class IsoReferenceDocument(DtConceptType):
    """dt:ReferenceDocumentType — a reference document."""

    date_of_publication: Optional[datetime] = element(
        tag="DateOfPublication", ns="dt", default=None
    )
    author: Optional[str] = element(tag="Author", ns="dt", default=None)
    isbn: Optional[str] = element(tag="ISBN", ns="dt", default=None)
    languages: List[str] = element(tag="Language", ns="dt", min_length=1)
    publisher: Optional[str] = element(tag="Publisher", ns="dt", default=None)
    uri: Optional[str] = element(tag="URI", ns="dt", default=None)


# ---------------------------------------------------------------------------
# ISO 7817-3 LOIN types
# Children of the LOIN root are unqualified in the XML output; the root
# carries the loin/dt namespace declarations.
# ---------------------------------------------------------------------------


class LoinPurpose(BaseXmlModel, tag="Purpose"):
    """loin:PurposeType — why information is needed."""

    guid: Guid = attr(name="GUID", ns="dt")

    names: List[DtMultiLangText] = element(tag="Name", min_length=1)
    definitions: List[DtMultiLangText] = element(tag="Definition", default_factory=list)
    reference_documents: List[DtRef] = element(tag="ReferenceDocument", default_factory=list)
    descriptions: List[DtMultiLangText] = element(tag="Description", default_factory=list)
    language: Optional[str] = element(tag="Language", default=None)
    region: Optional[str] = element(tag="Region", default=None)
    dictionary_ref: Optional[DtRef] = element(tag="DictionaryRef", default=None)


class LoinActor(BaseXmlModel):
    """loin:ActorType — providing/receiving actor in a transaction."""

    first_name: Optional[str] = attr(name="firstName", default=None)
    middle_name: Optional[str] = attr(name="middleName", default=None)
    last_name: Optional[str] = attr(name="lastName", default=None)
    affiliation: Optional[str] = attr(name="affiliation", default=None)
    guid: Guid = attr(name="GUID", ns="dt")

    role: DtMultiLangText = element(tag="Role")
    description: Optional[DtMultiLangText] = element(tag="Description", default=None)
    email_address: Optional[str] = element(tag="EMailAddress", default=None)


class LoinInformationDeliveryMilestone(BaseXmlModel, tag="InformationDeliveryMilestone"):
    """loin:InformationDeliveryMilestoneType — when information is needed."""

    date: Optional[datetime] = attr(name="Date", default=None)
    guid: Guid = attr(name="GUID", ns="dt")

    names: List[DtMultiLangText] = element(tag="Name", min_length=1)
    descriptions: List[DtMultiLangText] = element(tag="Description", default_factory=list)
    reference_documents: List[DtRef] = element(tag="ReferenceDocument", default_factory=list)


class LoinPrerequisites(BaseXmlModel, tag="Prerequisites"):
    """loin:PrerequisitesType — purpose + milestone + two actors."""

    guid: Guid = attr(name="GUID", ns="dt")

    purpose: LoinPurpose = element(tag="Purpose")
    information_delivery_milestone: LoinInformationDeliveryMilestone = element(
        tag="InformationDeliveryMilestone"
    )
    providing_actor: LoinActor = element(tag="ProvidingActor")
    receiving_actor: LoinActor = element(tag="ReceivingActor")


# --- AlphanumericalInformation ----------------------------------------------


class LoinGroupsOfProperties(BaseXmlModel, tag="GroupsOfProperties"):
    """Wrapper element holding inline GroupOfProperties and/or references."""

    # Internal Properties
    group_of_properties: List[IsoGroupOfProperties] = element(
        tag="GroupOfProperties", ns="dt", default_factory=list
    )
    # External Properties
    group_of_properties_refs: List[DtRef] = element(
        tag="GroupOfPropertiesRef", default_factory=list
    )


class LoinAlphanumericalInformation(BaseXmlModel, tag="AlphanumericalInformation"):
    """Container for alphanumerical requirements of an object type."""

    guid: Guid = attr(name="GUID", ns="dt")

    properties: List[IsoProperty] = element(tag="Property", ns="dt", default_factory=list)
    quantity_kinds: List[IsoQuantityKind] = element(
        tag="QuantityKind", ns="dt", default_factory=list
    )
    groups_of_properties: Optional[LoinGroupsOfProperties] = element(
        tag="GroupsOfProperties", default=None
    )
    reference_documents: List[IsoReferenceDocument] = element(
        tag="ReferenceDocument", ns="dt", default_factory=list
    )
    dimensions: List[IsoDimensionConcept] = element(tag="Dimension", ns="dt", default_factory=list)
    units: List[IsoUnit] = element(tag="Unit", ns="dt", default_factory=list)


# --- Documentation ----------------------------------------------------------


class LoinFormat(BaseXmlModel, tag="Format"):
    format_names: List[DtMultiLangText] = element(tag="FormatName", min_length=1)
    format_versions: List[DtMultiLangText] = element(tag="FormatVersion", min_length=1)
    format_specifications: List[DtRef] = element(tag="FormatSpecification", default_factory=list)


class LoinRequiredDocument(BaseXmlModel, tag="Document"):
    type: Optional[str] = attr(name="type", default=None)
    form: Optional[str] = attr(name="form", default=None)
    content: Optional[str] = attr(name="content", default=None)
    guid: Guid = attr(name="GUID", ns="dt")

    name: DtMultiLangText = element(tag="Name")
    reference_documents: List[DtRef] = element(tag="ReferenceDocument", default_factory=list)
    descriptions: List[DtMultiLangText] = element(tag="Description", default_factory=list)
    format: LoinFormat = element(tag="Format")


class LoinDocumentation(BaseXmlModel, tag="Documentation"):
    guid: Guid = attr(name="GUID", ns="dt")
    documents: List[LoinRequiredDocument] = element(tag="Document", default_factory=list)


# --- Geometrical information ------------------------------------------------


class LoinThresholdDimension(BaseXmlModel, tag="ThresholdDimension"):
    threshold: float = element(tag="Threshold")
    unit: IsoUnit = element(tag="Unit", ns="dt")
    definition: DtMultiLangText = element(tag="Definition")


class LoinShapeInfluence(BaseXmlModel, tag="ShapeInfluence"):
    inside_geometry: Optional[LoinInsideGeometry] = element(tag="InsideGeometry", default=None)
    connections: Optional[LoinConnections] = element(tag="Connections", default=None)
    openings: Optional[LoinOpenings] = element(tag="Openings", default=None)
    operating_and_clearance_zones: Optional[LoinOperatingAndClearanceZones] = element(
        tag="OperatingAndClearanceZones", default=None
    )
    features: Optional[LoinFeatures] = element(tag="Features", default=None)
    threshold_dimension: Optional[LoinThresholdDimension] = element(
        tag="ThresholdDimension", default=None
    )


class LoinDetail(BaseXmlModel, tag="Detail"):
    dictionary: Optional[DtRef] = element(tag="Dictionary", default=None)
    shape_assembly: Optional[LoinShapeAssembly] = element(tag="ShapeAssembly", default=None)
    shape_representation: Optional[LoinShapeRepresentation] = element(
        tag="ShapeRepresentation", default=None
    )
    shape_influence: Optional[LoinShapeInfluence] = element(tag="ShapeInfluence", default=None)


class LoinPositioning(BaseXmlModel, tag="Location"):
    relative_or_absolute: LoinPositioningEnum = element(tag="RelativeOrAbsolute")
    reference_object: Optional[str] = element(tag="ReferenceObject", default=None)


class LoinGeometricalInformation(BaseXmlModel, tag="GeometricalInformation"):
    guid: Guid = attr(name="GUID", ns="dt")
    placeholder: bool = attr(name="placeholder", default=False)

    detail: Optional[LoinDetail] = element(tag="Detail", default=None)
    dimensionality: Optional[LoinDimensionality] = element(tag="Dimensionality", default=None)
    appearance: Optional[LoinAppearance] = element(tag="Appearance", default=None)
    parametric_behaviour: Optional[LoinParametricBehaviour] = element(
        tag="ParametricBehaviour", default=None
    )
    location: Optional[LoinPositioning] = element(tag="Location", default=None)


# --- Geo-referencing --------------------------------------------------------


class LoinDatumRegistryReference(BaseXmlModel, tag="Type"):
    """loin:DatumRegistryReference — geodetic registry descriptor."""

    name: DtMultiLangText = element(tag="Name")
    descriptions: List[DtMultiLangText] = element(tag="Description", default_factory=list)
    registry_reference: Optional[DtRef] = element(tag="RegistryReference", default=None)


class LoinDatum(BaseXmlModel, tag="Datum"):
    """loin:DatumType — WKT2/EPSG identifier + registry reference."""

    name: str = element(tag="Name")
    type: LoinDatumRegistryReference = element(tag="Type")


class LoinCoordinateReferenceSystem(BaseXmlModel, tag="CoordinateReferenceSystem"):
    type: LoinCoordinateReferenceSystemEnum = element(tag="Type")
    datum: LoinDatum = element(tag="Datum")
    vertical_datum: Optional[LoinDatum] = element(tag="VerticalDatum", default=None)


class LoinModelCoordinateSystem(BaseXmlModel, tag="ModelCoordinateSystem"):
    is_projected: bool = element(tag="IsProjected")
    first_coordinate: Decimal = element(tag="FirstCoordinate")
    second_coordinate: Decimal = element(tag="SecondCoordinate")
    height: Decimal = element(tag="Height")
    x_axis_abscissa: Optional[Decimal] = element(tag="XAxisAbscissa", default=None)
    x_axis_ordinate: Optional[Decimal] = element(tag="XAxisOrdinate", default=None)
    unit_scale: Optional[Decimal] = element(tag="UnitScale", default=None)
    horizontal_scale: Optional[Decimal] = element(tag="HorizontalScale", default=None)


class LoinGeoReferencing(BaseXmlModel, tag="GeoReferencing"):
    coordinate_reference_system: Optional[LoinCoordinateReferenceSystem] = element(
        tag="CoordinateReferenceSystem", default=None
    )
    model_coordinate_systems: List[LoinModelCoordinateSystem] = element(
        tag="ModelCoordinateSystem", default_factory=list
    )


# --- SpecificationPerObjectType ---------------------------------------------
# Extends dt:ConceptType (so it carries the GUID, dateOfCreation and the
# ConceptType descriptive elements in the dt namespace) and adds the
# ObjectType, AlphanumericalInformation, Documentation and
# GeometricalInformation children (all in the LOIN — i.e. unqualified — XML
# namespace).


class LoinSpecificationPerObjectType(DtConceptType, tag="SpecificationPerObjectType"):
    object_type: IsoObjectType = element(tag="ObjectType", ns="dt")
    alphanumerical_information: Optional[LoinAlphanumericalInformation] = element(
        tag="AlphanumericalInformation", default=None
    )
    documentation: Optional[LoinDocumentation] = element(tag="Documentation", default=None)
    geometrical_information: Optional[LoinGeometricalInformation] = element(
        tag="GeometricalInformation", default=None
    )


# --- Specification ----------------------------------------------------------


class LoinSpecification(BaseXmlModel, tag="Specification"):
    name: str = attr(name="name")
    guid: Guid = attr(name="GUID", ns="dt")

    prerequisites: LoinPrerequisites = element(tag="Prerequisites")
    specifications_per_object_type: List[LoinSpecificationPerObjectType] = element(
        tag="SpecificationPerObjectType", default_factory=list
    )
    geo_referencing: Optional[LoinGeoReferencing] = element(tag="GeoReferencing", default=None)


# --- Root element -----------------------------------------------------------


class LoinLevelOfInformationNeed(
    BaseXmlModel,
    tag="LevelOfInformationNeed",
    ns="loin",
    nsmap=LOIN_NSMAP,
):
    """Root element of an ISO 7817-3 Level of Information Need document."""

    specifications: List[LoinSpecification] = element(tag="Specification", min_length=1)
