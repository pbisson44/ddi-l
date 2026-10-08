"""AUTO-GENERATED base dataclasses for DDI 3.3 — physicaldataproduct module.

These classes provide field definitions derived from the XSD schema.
Hand-written model classes inherit from these bases and add
``from_xml``, ``to_xml``, validation, and helper methods.

**Do not edit manually** — regenerate with:
    python -m codegen.generate_model_bases
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Optional

from ddi_l._etree import Element
from ddi_l.models.base import CodeValue, InternationalString, MaintainableBase, Reference
from ddi_l.constants import PHYSICAL_DATA_PRODUCT_NS, REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class BaseRecordLayoutFields(MaintainableBase):
    """This type structures an abstract element which is used only as the head of a substitution group. It contains a reference to the Physical Structure that is available for use in all of the substitute Re"""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "BaseRecordLayout")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    physical_structure_link_reference: Optional[Reference] = None  # [1..1]
    end_of_line_marker: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    textQualifier: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "physical_structure_link_reference": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference"), "reference", False),
        "end_of_line_marker": (qn(PHYSICAL_DATA_PRODUCT_NS, "EndOfLineMarker"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "textQualifier": ("textQualifier", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "VersionResponsibility"),
        qn(REUSABLE_NS, "VersionResponsibilityReference"),
        qn(REUSABLE_NS, "VersionRationale"),
        qn(REUSABLE_NS, "BasedOnObject"),
        qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "EndOfLineMarker"),
    ]


@dataclass
class DataItemFields(MaintainableBase):
    """Describes a single data item within the record, linking its description in a variable to its physical location in the stored record."""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "DataItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    variable_reference: Optional[Reference] = None  # [1..1]
    physical_location: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
        "physical_location": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalLocation"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalLocation"),
    ]


@dataclass
class GrossRecordStructureFields(MaintainableBase):
    """The gross or macro level structures of the record structure including the link to the LogicalRecord and information on the number and ordering of each Physical Segment of the LogicalRecord as stored i"""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "GrossRecordStructure")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    logical_record_reference: Optional[Reference] = None  # [1..1]
    physical_record_segments: list[Element] = field(default_factory=list)  # [1..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    numberOfPhysicalSegments: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "logical_record_reference": (qn(PHYSICAL_DATA_PRODUCT_NS, "LogicalRecordReference"), "reference", False),
        "physical_record_segments": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalRecordSegment"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "numberOfPhysicalSegments": ("numberOfPhysicalSegments", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "LogicalRecordReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalRecordSegment"),
    ]


@dataclass
class KeyVariableReferenceFields(MaintainableBase):
    """Reference to the Unique key variable for segment identification and the value it contains for the specific segment. TypeOfObject should be set to Variable."""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "KeyVariableReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    type_of_object: Optional[Element] = None  # [1..1]
    value: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "value": (qn(REUSABLE_NS, "Value"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isExternal": ("isExternal", "bool"),
        "isReference": ("isReference", "bool"),
        "lateBound": ("lateBound", "bool"),
        "lateBoundRestriction": ("lateBoundRestriction", "str"),
        "objectLanguage": ("objectLanguage", "str"),
        "sourceContext": ("sourceContext", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "Value"),
    ]


@dataclass
class PhysicalDataProductFields(MaintainableBase):
    """A module describing the physical storage structures of data files and the relationship of their internal objects to the logical (intellectual) description of the objects found in LogicalProduct. This """

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProduct")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    physical_structure_schemes: list[Element] = field(default_factory=list)  # [0..*]
    physical_structure_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    record_layout_schemes: list[Element] = field(default_factory=list)  # [0..*]
    record_layout_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProductName"), "intl_string", True),
        "physical_structure_schemes": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureScheme"), "element", True),
        "physical_structure_scheme_references": (qn(REUSABLE_NS, "PhysicalStructureSchemeReference"), "reference", True),
        "record_layout_schemes": (qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutScheme"), "element", True),
        "record_layout_scheme_references": (qn(REUSABLE_NS, "RecordLayoutSchemeReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "lang": ("lang", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "VersionResponsibility"),
        qn(REUSABLE_NS, "VersionResponsibilityReference"),
        qn(REUSABLE_NS, "VersionRationale"),
        qn(REUSABLE_NS, "BasedOnObject"),
        qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
        qn(REUSABLE_NS, "Note"),
        qn(REUSABLE_NS, "Software"),
        qn(REUSABLE_NS, "MetadataQuality"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProductName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureScheme"),
        qn(REUSABLE_NS, "PhysicalStructureSchemeReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutScheme"),
        qn(REUSABLE_NS, "RecordLayoutSchemeReference"),
    ]


@dataclass
class PhysicalLocationFields(MaintainableBase):
    """Description of the physical location of the value of the object in the data file. Includes information about the data item location and its data type/format if other than the default."""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalLocation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    storage_format: Optional[CodeValue] = None  # [0..1]
    delimiter: Optional[Element] = None  # [0..1]
    start_position: Optional[int] = None  # [0..1]
    array_position: Optional[int] = None  # [0..1]
    end_position: Optional[int] = None  # [0..1]
    width: Optional[int] = None  # [0..1]
    decimal_positions: Optional[int] = None  # [0..1]
    decimal_separator: Optional[Element] = None  # [0..1]
    digit_group_separator: Optional[Element] = None  # [0..1]
    language_of_data: Optional[Element] = None  # [0..1]
    locale_of_data: Optional[str] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "storage_format": (qn(PHYSICAL_DATA_PRODUCT_NS, "StorageFormat"), "code_value", False),
        "delimiter": (qn(PHYSICAL_DATA_PRODUCT_NS, "Delimiter"), "element", False),
        "start_position": (qn(PHYSICAL_DATA_PRODUCT_NS, "StartPosition"), "int", False),
        "array_position": (qn(PHYSICAL_DATA_PRODUCT_NS, "ArrayPosition"), "int", False),
        "end_position": (qn(PHYSICAL_DATA_PRODUCT_NS, "EndPosition"), "int", False),
        "width": (qn(PHYSICAL_DATA_PRODUCT_NS, "Width"), "int", False),
        "decimal_positions": (qn(PHYSICAL_DATA_PRODUCT_NS, "DecimalPositions"), "int", False),
        "decimal_separator": (qn(PHYSICAL_DATA_PRODUCT_NS, "DecimalSeparator"), "element", False),
        "digit_group_separator": (qn(PHYSICAL_DATA_PRODUCT_NS, "DigitGroupSeparator"), "element", False),
        "language_of_data": (qn(PHYSICAL_DATA_PRODUCT_NS, "LanguageOfData"), "element", False),
        "locale_of_data": (qn(PHYSICAL_DATA_PRODUCT_NS, "LocaleOfData"), "str", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(PHYSICAL_DATA_PRODUCT_NS, "StorageFormat"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "Delimiter"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "StartPosition"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "ArrayPosition"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "EndPosition"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "Width"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "DecimalPositions"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "DecimalSeparator"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "DigitGroupSeparator"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "LanguageOfData"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "LocaleOfData"),
    ]


@dataclass
class PhysicalRecordSegmentFields(MaintainableBase):
    """A description of the physical record segment as found in the data store. A logical record may be stored in one or more segments housed hierarchically in a single file or in separate data files. All lo"""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalRecordSegment")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    key_variable_reference: Optional[Reference] = None  # [0..1]
    file_name_identification: Optional[str] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    segmentOrder: Optional[int] = None  # @attr
    hasSegmentKey: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "key_variable_reference": (qn(PHYSICAL_DATA_PRODUCT_NS, "KeyVariableReference"), "reference", False),
        "file_name_identification": (qn(PHYSICAL_DATA_PRODUCT_NS, "FileNameIdentification"), "str", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "segmentOrder": ("segmentOrder", "int"),
        "hasSegmentKey": ("hasSegmentKey", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "KeyVariableReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "FileNameIdentification"),
    ]


@dataclass
class PhysicalStructureGroupFields(MaintainableBase):
    """A group of PhysicalStructure descriptions for administrative or conceptual purposes. May be hierarchical. In addition to the standard name, label, and description, allows for a brief classification of"""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    type_of_physical_structure_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    physical_structure_references: list[Reference] = field(default_factory=list)  # [0..*]
    physical_structure_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_physical_structure_group": (qn(PHYSICAL_DATA_PRODUCT_NS, "TypeOfPhysicalStructureGroup"), "code_value", False),
        "names": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "physical_structure_references": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureReference"), "reference", True),
        "physical_structure_group_references": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroupReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "isOrdered": ("isOrdered", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "VersionResponsibility"),
        qn(REUSABLE_NS, "VersionResponsibilityReference"),
        qn(REUSABLE_NS, "VersionRationale"),
        qn(REUSABLE_NS, "BasedOnObject"),
        qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "TypeOfPhysicalStructureGroup"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroupReference"),
    ]


@dataclass
class PhysicalStructureLinkReferenceFields(MaintainableBase):
    """References a PhysicalStructure description and the ID of the physical record segment from that is described by this record layout. TypeOfObject should be set to PhysicalStructure."""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    type_of_object: Optional[Element] = None  # [1..1]
    physical_record_segment_used: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "physical_record_segment_used": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalRecordSegmentUsed"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isExternal": ("isExternal", "bool"),
        "isReference": ("isReference", "bool"),
        "lateBound": ("lateBound", "bool"),
        "lateBoundRestriction": ("lateBoundRestriction", "str"),
        "objectLanguage": ("objectLanguage", "str"),
        "sourceContext": ("sourceContext", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalRecordSegmentUsed"),
    ]


@dataclass
class PhysicalStructureSchemeFields(MaintainableBase):
    """A scheme containing a set of PhysicalStructures containing descriptions of overall structure of a physical data storage format. These descriptions provide the primary link to the LogicalRecord found i"""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    physical_structure_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    physical_structures: list[Element] = field(default_factory=list)  # [0..*]
    physical_structure_references: list[Reference] = field(default_factory=list)  # [0..*]
    physical_structure_groups: list[Element] = field(default_factory=list)  # [0..*]
    physical_structure_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureSchemeName"), "intl_string", True),
        "physical_structure_scheme_references": (qn(REUSABLE_NS, "PhysicalStructureSchemeReference"), "reference", True),
        "physical_structures": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructure"), "element", True),
        "physical_structure_references": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureReference"), "reference", True),
        "physical_structure_groups": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroup"), "element", True),
        "physical_structure_group_references": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroupReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "lang": ("lang", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "VersionResponsibility"),
        qn(REUSABLE_NS, "VersionResponsibilityReference"),
        qn(REUSABLE_NS, "VersionRationale"),
        qn(REUSABLE_NS, "BasedOnObject"),
        qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
        qn(REUSABLE_NS, "Note"),
        qn(REUSABLE_NS, "Software"),
        qn(REUSABLE_NS, "MetadataQuality"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "PhysicalStructureSchemeReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructure"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroup"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroupReference"),
    ]


@dataclass
class PhysicalStructureFields(MaintainableBase):
    """Description of a PhysicalStructure providing the primary link to the LogicalRecord and general structural information. Each description can apply to one or more data files containing the same logical """

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructure")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    file_format: Optional[CodeValue] = None  # [0..1]
    default_data_type: Optional[CodeValue] = None  # [0..1]
    default_delimiter: Optional[Element] = None  # [0..1]
    default_decimal_positions: Optional[int] = None  # [0..1]
    default_decimal_separator: Optional[Element] = None  # [0..1]
    default_digit_group_separator: Optional[Element] = None  # [0..1]
    gross_record_structures: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureName"), "intl_string", True),
        "file_format": (qn(PHYSICAL_DATA_PRODUCT_NS, "FileFormat"), "code_value", False),
        "default_data_type": (qn(REUSABLE_NS, "DefaultDataType"), "code_value", False),
        "default_delimiter": (qn(REUSABLE_NS, "DefaultDelimiter"), "element", False),
        "default_decimal_positions": (qn(REUSABLE_NS, "DefaultDecimalPositions"), "int", False),
        "default_decimal_separator": (qn(REUSABLE_NS, "DefaultDecimalSeparator"), "element", False),
        "default_digit_group_separator": (qn(REUSABLE_NS, "DefaultDigitGroupSeparator"), "element", False),
        "gross_record_structures": (qn(PHYSICAL_DATA_PRODUCT_NS, "GrossRecordStructure"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "VersionResponsibility"),
        qn(REUSABLE_NS, "VersionResponsibilityReference"),
        qn(REUSABLE_NS, "VersionRationale"),
        qn(REUSABLE_NS, "BasedOnObject"),
        qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "FileFormat"),
        qn(REUSABLE_NS, "DefaultDataType"),
        qn(REUSABLE_NS, "DefaultDelimiter"),
        qn(REUSABLE_NS, "DefaultDecimalPositions"),
        qn(REUSABLE_NS, "DefaultDecimalSeparator"),
        qn(REUSABLE_NS, "DefaultDigitGroupSeparator"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "GrossRecordStructure"),
    ]


@dataclass
class RecordLayoutGroupFields(MaintainableBase):
    """Contains a group of RecordLayout descriptions for administrative or conceptual purposes, which may be hierarchical. In addition to the standard name, label, and description, allows for a classificatio"""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    type_of_record_layout_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    record_layout_references: list[Reference] = field(default_factory=list)  # [0..*]
    record_layout_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_record_layout_group": (qn(PHYSICAL_DATA_PRODUCT_NS, "TypeOfRecordLayoutGroup"), "code_value", False),
        "names": (qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "record_layout_references": (qn(REUSABLE_NS, "RecordLayoutReference"), "reference", True),
        "record_layout_group_references": (qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroupReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "isOrdered": ("isOrdered", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "VersionResponsibility"),
        qn(REUSABLE_NS, "VersionResponsibilityReference"),
        qn(REUSABLE_NS, "VersionRationale"),
        qn(REUSABLE_NS, "BasedOnObject"),
        qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "TypeOfRecordLayoutGroup"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "RecordLayoutReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroupReference"),
    ]


@dataclass
class RecordLayoutSchemeFields(MaintainableBase):
    """A scheme containing a set of RecordLayouts describing the location of individual data items within the physical record and how to address them (locate and retrieve). RecordLayouts provide a link to th"""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    record_layout_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    base_record_layouts: list[Element] = field(default_factory=list)  # [0..*]
    record_layout_references: list[Reference] = field(default_factory=list)  # [0..*]
    record_layout_groups: list[Element] = field(default_factory=list)  # [0..*]
    record_layout_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutSchemeName"), "intl_string", True),
        "record_layout_scheme_references": (qn(REUSABLE_NS, "RecordLayoutSchemeReference"), "reference", True),
        "base_record_layouts": (qn(PHYSICAL_DATA_PRODUCT_NS, "BaseRecordLayout"), "element", True),
        "record_layout_references": (qn(REUSABLE_NS, "RecordLayoutReference"), "reference", True),
        "record_layout_groups": (qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroup"), "element", True),
        "record_layout_group_references": (qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroupReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "lang": ("lang", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "VersionResponsibility"),
        qn(REUSABLE_NS, "VersionResponsibilityReference"),
        qn(REUSABLE_NS, "VersionRationale"),
        qn(REUSABLE_NS, "BasedOnObject"),
        qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
        qn(REUSABLE_NS, "Note"),
        qn(REUSABLE_NS, "Software"),
        qn(REUSABLE_NS, "MetadataQuality"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "RecordLayoutSchemeReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "BaseRecordLayout"),
        qn(REUSABLE_NS, "RecordLayoutReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroup"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroupReference"),
    ]


@dataclass
class RecordLayoutFields(MaintainableBase):
    """A member of the BaseRecordLayout substitution group intended for use with archival formats of microdata held in an external file with fixed or delimited locations for data items. In addition to the li"""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayout")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")
    physical_structure_link_reference: Optional[Reference] = None  # [1..1]
    end_of_line_marker: Optional[CodeValue] = None  # [0..1]
    character_set: Optional[CodeValue] = None  # [0..1]
    array_base: Optional[int] = None  # [1..1]
    default_variable_scheme_reference: Optional[Reference] = None  # [0..1]
    data_items: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    textQualifier: Optional[str] = None  # @attr
    namesOnFirstRow: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "physical_structure_link_reference": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference"), "reference", False),
        "end_of_line_marker": (qn(PHYSICAL_DATA_PRODUCT_NS, "EndOfLineMarker"), "code_value", False),
        "character_set": (qn(REUSABLE_NS, "CharacterSet"), "code_value", False),
        "array_base": (qn(REUSABLE_NS, "ArrayBase"), "int", False),
        "default_variable_scheme_reference": (qn(REUSABLE_NS, "DefaultVariableSchemeReference"), "reference", False),
        "data_items": (qn(PHYSICAL_DATA_PRODUCT_NS, "DataItem"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "textQualifier": ("textQualifier", "str"),
        "namesOnFirstRow": ("namesOnFirstRow", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "VersionResponsibility"),
        qn(REUSABLE_NS, "VersionResponsibilityReference"),
        qn(REUSABLE_NS, "VersionRationale"),
        qn(REUSABLE_NS, "BasedOnObject"),
        qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "EndOfLineMarker"),
        qn(REUSABLE_NS, "CharacterSet"),
        qn(REUSABLE_NS, "ArrayBase"),
        qn(REUSABLE_NS, "DefaultVariableSchemeReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "DataItem"),
    ]

