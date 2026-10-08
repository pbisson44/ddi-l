"""AUTO-GENERATED base dataclasses for DDI 3.3 — comparative module.

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
from ddi_l.constants import COMPARATIVE_NS, REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class ComparisonFields(MaintainableBase):
    """A maintainable module containing maps between objects of the same or similar type. Maps allow for pair-wise mapping of two objects by describing their similarities and differences in order to make ass"""

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "Comparison")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    concept_maps: list[Element] = field(default_factory=list)  # [0..*]
    concept_map_references: list[Reference] = field(default_factory=list)  # [0..*]
    variable_maps: list[Element] = field(default_factory=list)  # [0..*]
    variable_map_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_maps: list[Element] = field(default_factory=list)  # [0..*]
    question_map_references: list[Reference] = field(default_factory=list)  # [0..*]
    category_maps: list[Element] = field(default_factory=list)  # [0..*]
    category_map_references: list[Reference] = field(default_factory=list)  # [0..*]
    representation_maps: list[Element] = field(default_factory=list)  # [0..*]
    representation_map_references: list[Reference] = field(default_factory=list)  # [0..*]
    universe_maps: list[Element] = field(default_factory=list)  # [0..*]
    universe_map_references: list[Reference] = field(default_factory=list)  # [0..*]
    managed_item_maps: list[Element] = field(default_factory=list)  # [0..*]
    managed_item_map_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(COMPARATIVE_NS, "ComparisonName"), "intl_string", True),
        "concept_maps": (qn(COMPARATIVE_NS, "ConceptMap"), "element", True),
        "concept_map_references": (qn(COMPARATIVE_NS, "ConceptMapReference"), "reference", True),
        "variable_maps": (qn(COMPARATIVE_NS, "VariableMap"), "element", True),
        "variable_map_references": (qn(COMPARATIVE_NS, "VariableMapReference"), "reference", True),
        "question_maps": (qn(COMPARATIVE_NS, "QuestionMap"), "element", True),
        "question_map_references": (qn(COMPARATIVE_NS, "QuestionMapReference"), "reference", True),
        "category_maps": (qn(COMPARATIVE_NS, "CategoryMap"), "element", True),
        "category_map_references": (qn(COMPARATIVE_NS, "CategoryMapReference"), "reference", True),
        "representation_maps": (qn(COMPARATIVE_NS, "RepresentationMap"), "element", True),
        "representation_map_references": (qn(COMPARATIVE_NS, "RepresentationMapReference"), "reference", True),
        "universe_maps": (qn(COMPARATIVE_NS, "UniverseMap"), "element", True),
        "universe_map_references": (qn(COMPARATIVE_NS, "UniverseMapReference"), "reference", True),
        "managed_item_maps": (qn(COMPARATIVE_NS, "ManagedItemMap"), "element", True),
        "managed_item_map_references": (qn(COMPARATIVE_NS, "ManagedItemMapReference"), "reference", True),
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
        qn(COMPARATIVE_NS, "ComparisonName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(COMPARATIVE_NS, "ConceptMap"),
        qn(COMPARATIVE_NS, "ConceptMapReference"),
        qn(COMPARATIVE_NS, "VariableMap"),
        qn(COMPARATIVE_NS, "VariableMapReference"),
        qn(COMPARATIVE_NS, "QuestionMap"),
        qn(COMPARATIVE_NS, "QuestionMapReference"),
        qn(COMPARATIVE_NS, "CategoryMap"),
        qn(COMPARATIVE_NS, "CategoryMapReference"),
        qn(COMPARATIVE_NS, "RepresentationMap"),
        qn(COMPARATIVE_NS, "RepresentationMapReference"),
        qn(COMPARATIVE_NS, "UniverseMap"),
        qn(COMPARATIVE_NS, "UniverseMapReference"),
        qn(COMPARATIVE_NS, "ManagedItemMap"),
        qn(COMPARATIVE_NS, "ManagedItemMapReference"),
    ]


@dataclass
class CorrespondenceFields(MaintainableBase):
    """Describes the commonalities and differences between two items using a textual description of both commonalities and differences plus an optional coding of the type of commonality, a commonality expres"""

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "Correspondence")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp")
    commonality: Optional[Element] = None  # [0..1]
    difference: Optional[Element] = None  # [0..1]
    commonality_type_coded: Optional[CodeValue] = None  # [0..1]
    commonality_weight: Optional[Element] = None  # [0..1]
    user_defined_correspondence_properties: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "commonality": (qn(COMPARATIVE_NS, "Commonality"), "element", False),
        "difference": (qn(REUSABLE_NS, "Difference"), "element", False),
        "commonality_type_coded": (qn(COMPARATIVE_NS, "CommonalityTypeCoded"), "code_value", False),
        "commonality_weight": (qn(COMPARATIVE_NS, "CommonalityWeight"), "element", False),
        "user_defined_correspondence_properties": (qn(REUSABLE_NS, "UserDefinedCorrespondenceProperty"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(COMPARATIVE_NS, "Commonality"),
        qn(REUSABLE_NS, "Difference"),
        qn(COMPARATIVE_NS, "CommonalityTypeCoded"),
        qn(COMPARATIVE_NS, "CommonalityWeight"),
        qn(REUSABLE_NS, "UserDefinedCorrespondenceProperty"),
    ]


@dataclass
class GenericMapFields(MaintainableBase):
    """Maps the content of two different schemes of objects of the same type providing detail for the comparable items within those two schemes. Note that comparisons can be made between multiple items in th"""

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "GenericMap")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp")
    type_of_mapped_item: Optional[CodeValue] = None  # [0..1]
    map_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    source_scheme_reference: Optional[Reference] = None  # [0..1]
    target_scheme_reference: Optional[Reference] = None  # [0..1]
    correspondence: Optional[Element] = None  # [0..1]
    item_maps: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_mapped_item": (qn(COMPARATIVE_NS, "TypeOfMappedItem"), "code_value", False),
        "map_names": (qn(COMPARATIVE_NS, "MapName"), "intl_string", True),
        "source_scheme_reference": (qn(COMPARATIVE_NS, "SourceSchemeReference"), "reference", False),
        "target_scheme_reference": (qn(COMPARATIVE_NS, "TargetSchemeReference"), "reference", False),
        "correspondence": (qn(COMPARATIVE_NS, "Correspondence"), "element", False),
        "item_maps": (qn(COMPARATIVE_NS, "ItemMap"), "element", True),
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
        qn(COMPARATIVE_NS, "TypeOfMappedItem"),
        qn(COMPARATIVE_NS, "MapName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(COMPARATIVE_NS, "SourceSchemeReference"),
        qn(COMPARATIVE_NS, "TargetSchemeReference"),
        qn(COMPARATIVE_NS, "Correspondence"),
        qn(COMPARATIVE_NS, "ItemMap"),
    ]


@dataclass
class ItemMapFields(MaintainableBase):
    """Maps a Source and one or more Target items of the same type within the Source and Target Schemes identified."""

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "ItemMap")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp")
    source_item_reference: Optional[Reference] = None  # [0..1]
    target_item_references: list[Reference] = field(default_factory=list)  # [0..*]
    correspondence: Optional[Element] = None  # [0..1]
    related_map_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    alias: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "source_item_reference": (qn(COMPARATIVE_NS, "SourceItemReference"), "reference", False),
        "target_item_references": (qn(COMPARATIVE_NS, "TargetItemReference"), "reference", True),
        "correspondence": (qn(COMPARATIVE_NS, "Correspondence"), "element", False),
        "related_map_references": (qn(COMPARATIVE_NS, "RelatedMapReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "alias": ("alias", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(COMPARATIVE_NS, "SourceItemReference"),
        qn(COMPARATIVE_NS, "TargetItemReference"),
        qn(COMPARATIVE_NS, "Correspondence"),
        qn(COMPARATIVE_NS, "RelatedMapReference"),
    ]


@dataclass
class RepresentationMapFields(MaintainableBase):
    """Maps between any two managed representations. In addition to representation types held in a ManagagedRepresentationScheme, managed representations include CategoryScheme and coded representations whic"""

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "RepresentationMap")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    source_representation: Optional[Element] = None  # [1..1]
    target_representation: Optional[Element] = None  # [1..1]
    correspondence: Optional[Element] = None  # [0..1]
    processing_instruction_reference: Optional[Reference] = None  # [1..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    contextSpecificComparison: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(COMPARATIVE_NS, "RepresentationMapName"), "intl_string", True),
        "source_representation": (qn(COMPARATIVE_NS, "SourceRepresentation"), "element", False),
        "target_representation": (qn(COMPARATIVE_NS, "TargetRepresentation"), "element", False),
        "correspondence": (qn(COMPARATIVE_NS, "Correspondence"), "element", False),
        "processing_instruction_reference": (qn(REUSABLE_NS, "ProcessingInstructionReference"), "reference", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "contextSpecificComparison": ("contextSpecificComparison", "bool"),
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
        qn(COMPARATIVE_NS, "RepresentationMapName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(COMPARATIVE_NS, "SourceRepresentation"),
        qn(COMPARATIVE_NS, "TargetRepresentation"),
        qn(COMPARATIVE_NS, "Correspondence"),
        qn(REUSABLE_NS, "ProcessingInstructionReference"),
    ]


@dataclass
class SourceRepresentationFields(MaintainableBase):
    """Provides a reference to the managed content of a representation which may be a ManagedRepresentation or a specific CodeList, GeographicRepresentation, or GeographicLocation. Allows for the optional re"""

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "SourceRepresentation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp")
    managed_representation_reference: Optional[Reference] = None  # [1..1]
    category_scheme_reference: Optional[Reference] = None  # [1..1]
    code_list_reference: Optional[Reference] = None  # [1..1]
    geographic_structure_reference: Optional[Reference] = None  # [1..1]
    geographic_location_reference: Optional[Reference] = None  # [1..1]
    concept_reference: Optional[Reference] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "managed_representation_reference": (qn(REUSABLE_NS, "ManagedRepresentationReference"), "reference", False),
        "category_scheme_reference": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", False),
        "code_list_reference": (qn(REUSABLE_NS, "CodeListReference"), "reference", False),
        "geographic_structure_reference": (qn(REUSABLE_NS, "GeographicStructureReference"), "reference", False),
        "geographic_location_reference": (qn(REUSABLE_NS, "GeographicLocationReference"), "reference", False),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ManagedRepresentationReference"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
        qn(REUSABLE_NS, "CodeListReference"),
        qn(REUSABLE_NS, "GeographicStructureReference"),
        qn(REUSABLE_NS, "GeographicLocationReference"),
        qn(REUSABLE_NS, "ConceptReference"),
    ]


@dataclass
class TargetRepresentationFields(MaintainableBase):
    """Provides a reference to a codified representation. Supports the ability to limit code coverage as appropriate for the coding structure referenced."""

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "TargetRepresentation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp")
    managed_representation_reference: Optional[Reference] = None  # [1..1]
    category_scheme_reference: Optional[Reference] = None  # [1..1]
    code_list_reference: Optional[Reference] = None  # [1..1]
    code_subset_information: Optional[Element] = None  # [0..1]
    included_geographic_structure_codes: Optional[Element] = None  # [1..1]
    included_geographic_location_codes: Optional[Element] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "managed_representation_reference": (qn(REUSABLE_NS, "ManagedRepresentationReference"), "reference", False),
        "category_scheme_reference": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", False),
        "code_list_reference": (qn(REUSABLE_NS, "CodeListReference"), "reference", False),
        "code_subset_information": (qn(REUSABLE_NS, "CodeSubsetInformation"), "element", False),
        "included_geographic_structure_codes": (qn(REUSABLE_NS, "IncludedGeographicStructureCodes"), "element", False),
        "included_geographic_location_codes": (qn(REUSABLE_NS, "IncludedGeographicLocationCodes"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ManagedRepresentationReference"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
        qn(REUSABLE_NS, "CodeListReference"),
        qn(REUSABLE_NS, "CodeSubsetInformation"),
        qn(REUSABLE_NS, "IncludedGeographicStructureCodes"),
        qn(REUSABLE_NS, "IncludedGeographicLocationCodes"),
    ]

