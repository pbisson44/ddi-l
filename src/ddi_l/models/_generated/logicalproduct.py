"""AUTO-GENERATED base dataclasses for DDI 3.3 — logicalproduct module.

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
from ddi_l.constants import LOGICAL_PRODUCT_NS, REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class AggregationDefinitionFields(MaintainableBase):
    """Identifies the independent (denominator) and dependent (numerator) dimensions for calculating aggregate measures such as percent. When two or more independent or dependent dimensions are listed here, """

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "AggregationDefinition")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    independent_dimensions: list[int] = field(default_factory=list)  # [0..*]
    dependent_dimensions: list[int] = field(default_factory=list)  # [0..*]
    isNCubeUniverse: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "independent_dimensions": (qn(LOGICAL_PRODUCT_NS, "IndependentDimension"), "int", True),
        "dependent_dimensions": (qn(LOGICAL_PRODUCT_NS, "DependentDimension"), "int", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isNCubeUniverse": ("isNCubeUniverse", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "IndependentDimension"),
        qn(LOGICAL_PRODUCT_NS, "DependentDimension"),
    ]


@dataclass
class AttributeFields(MaintainableBase):
    """An attribute may be any object which should be attached to all or part of the NCube. It may be defined as a Variable or contain textual content (such as a footnote)."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Attribute")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    variable_reference: Optional[Reference] = None  # [1..1]
    attachment_value: Optional[str] = None  # [1..1]
    attachment_region_reference: Optional[Reference] = None  # [0..1]
    measure_definition_references: list[Reference] = field(default_factory=list)  # [0..*]
    values: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    attachmentLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
        "attachment_value": (qn(LOGICAL_PRODUCT_NS, "AttachmentValue"), "str", False),
        "attachment_region_reference": (qn(LOGICAL_PRODUCT_NS, "AttachmentRegionReference"), "reference", False),
        "measure_definition_references": (qn(REUSABLE_NS, "MeasureDefinitionReference"), "reference", True),
        "values": (qn(REUSABLE_NS, "Value"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "attachmentLevel": ("attachmentLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "VariableReference"),
        qn(LOGICAL_PRODUCT_NS, "AttachmentValue"),
        qn(LOGICAL_PRODUCT_NS, "AttachmentRegionReference"),
        qn(REUSABLE_NS, "MeasureDefinitionReference"),
        qn(REUSABLE_NS, "Value"),
    ]


@dataclass
class BaseLogicalProductFields(MaintainableBase):
    """This is an abstract structure which serves as a substitution base for current and future LogicalProduct definitions relating to specific data types. Used as an extension base for all other LogicalProd"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "BaseLogicalProduct")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    logical_product_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    coverage: Optional[Element] = None  # [0..1]
    data_relationships: list[Element] = field(default_factory=list)  # [0..*]
    data_relationship_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "logical_product_names": (qn(LOGICAL_PRODUCT_NS, "LogicalProductName"), "intl_string", True),
        "coverage": (qn(REUSABLE_NS, "Coverage"), "element", False),
        "data_relationships": (qn(LOGICAL_PRODUCT_NS, "DataRelationship"), "element", True),
        "data_relationship_references": (qn(REUSABLE_NS, "DataRelationshipReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "LogicalProductName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Coverage"),
        qn(LOGICAL_PRODUCT_NS, "DataRelationship"),
        qn(REUSABLE_NS, "DataRelationshipReference"),
    ]


@dataclass
class CaseIdentificationFields(MaintainableBase):
    """Describes the information needed to identify an individual case within a record type. This may be the variable or concatenated variable used to identify a unique case of a particular record type. Ofte"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CaseIdentification")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    fixed_identifier: Optional[Element] = None  # [1..1]
    conditional_identifier: Optional[Element] = None  # [1..1]
    isPrimary: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "fixed_identifier": (qn(LOGICAL_PRODUCT_NS, "FixedIdentifier"), "element", False),
        "conditional_identifier": (qn(LOGICAL_PRODUCT_NS, "ConditionalIdentifier"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isPrimary": ("isPrimary", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "FixedIdentifier"),
        qn(LOGICAL_PRODUCT_NS, "ConditionalIdentifier"),
    ]


@dataclass
class CaseLawFields(MaintainableBase):
    """Refers to a case law ruling related to the Classification Item."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CaseLaw")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    case_law_date: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "CaseLawName"), "intl_string", True),
        "case_law_date": (qn(LOGICAL_PRODUCT_NS, "CaseLawDate"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "CaseLawName"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "CaseLawDate"),
    ]


@dataclass
class CaseSpecificationFields(MaintainableBase):
    """Case specification allows different unique identifiers to be used based on the value of an identified variable. In some cases the value of a variable (such as a geographic level) results in a differen"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CaseSpecification")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    conditional_variable_reference: Optional[Reference] = None  # [1..1]
    variable_references: list[Reference] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "conditional_variable_reference": (qn(LOGICAL_PRODUCT_NS, "ConditionalVariableReference"), "reference", False),
        "variable_references": (qn(REUSABLE_NS, "VariableReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "ConditionalVariableReference"),
        qn(REUSABLE_NS, "VariableReference"),
    ]


@dataclass
class CategoryGroupFields(MaintainableBase):
    """Contains a group of Category descriptions, which may be ordered or hierarchical. In addition to the name, label, and description of the group, the structure allows for defining the group as a valid ca"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CategoryGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    type_of_category_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    defining_category_reference: Optional[Reference] = None  # [0..1]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    category_references: list[Reference] = field(default_factory=list)  # [0..*]
    category_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_category_group": (qn(LOGICAL_PRODUCT_NS, "TypeOfCategoryGroup"), "code_value", False),
        "names": (qn(LOGICAL_PRODUCT_NS, "CategoryGroupName"), "intl_string", True),
        "defining_category_reference": (qn(LOGICAL_PRODUCT_NS, "DefiningCategoryReference"), "reference", False),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "category_references": (qn(REUSABLE_NS, "CategoryReference"), "reference", True),
        "category_group_references": (qn(LOGICAL_PRODUCT_NS, "CategoryGroupReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "TypeOfCategoryGroup"),
        qn(LOGICAL_PRODUCT_NS, "CategoryGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "DefiningCategoryReference"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "CategoryReference"),
        qn(LOGICAL_PRODUCT_NS, "CategoryGroupReference"),
    ]


@dataclass
class CategorySchemeFields(MaintainableBase):
    """A scheme containing a set of Categories managed by an agency. These are used to manage category definitions used as a domain for data element and basic content for a category representations. In addit"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CategoryScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    category_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    categories: list[Element] = field(default_factory=list)  # [0..*]
    category_references: list[Reference] = field(default_factory=list)  # [0..*]
    category_groups: list[Element] = field(default_factory=list)  # [0..*]
    category_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "CategorySchemeName"), "intl_string", True),
        "category_scheme_references": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", True),
        "categories": (qn(LOGICAL_PRODUCT_NS, "Category"), "element", True),
        "category_references": (qn(REUSABLE_NS, "CategoryReference"), "reference", True),
        "category_groups": (qn(LOGICAL_PRODUCT_NS, "CategoryGroup"), "element", True),
        "category_group_references": (qn(LOGICAL_PRODUCT_NS, "CategoryGroupReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "CategorySchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "Category"),
        qn(REUSABLE_NS, "CategoryReference"),
        qn(LOGICAL_PRODUCT_NS, "CategoryGroup"),
        qn(LOGICAL_PRODUCT_NS, "CategoryGroupReference"),
    ]


@dataclass
class CategoryFields(MaintainableBase):
    """A description of a particular category or response. OECD Glossary of Statistical Terms: Generic term for items at any level within a classification, typically tabulation categories, sections, subsecti"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Category")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    generation: Optional[Element] = None  # [0..1]
    sub_category_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isMissing: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "CategoryName"), "intl_string", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "generation": (qn(LOGICAL_PRODUCT_NS, "Generation"), "element", False),
        "sub_category_references": (qn(LOGICAL_PRODUCT_NS, "SubCategoryReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "isMissing": ("isMissing", "bool"),
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
        qn(LOGICAL_PRODUCT_NS, "CategoryName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(LOGICAL_PRODUCT_NS, "Generation"),
        qn(LOGICAL_PRODUCT_NS, "SubCategoryReference"),
    ]


@dataclass
class ClassificationCorrespondenceTableFields(MaintainableBase):
    """A Correspondence Table expresses the relationship between two Statistical Classifications. These are typically: two versions from the same Classification Series; Statistical Classifications from diffe"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ClassificationCorrespondenceTable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    owner_references: list[Reference] = field(default_factory=list)  # [0..*]
    maintenance_unit_references: list[Reference] = field(default_factory=list)  # [0..*]
    contact_person_references: list[Reference] = field(default_factory=list)  # [0..*]
    publications: list[Element] = field(default_factory=list)  # [0..*]
    source_classification_reference: Optional[Reference] = None  # [0..1]
    target_classification_references: list[Reference] = field(default_factory=list)  # [0..*]
    source_level_reference: Optional[Reference] = None  # [0..1]
    target_level_references: list[Reference] = field(default_factory=list)  # [0..*]
    relationship_mapping_type: Optional[CodeValue] = None  # [0..1]
    maps: list[Element] = field(default_factory=list)  # [0..*]
    floating_map_date: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "Name"), "intl_string", True),
        "owner_references": (qn(LOGICAL_PRODUCT_NS, "OwnerReference"), "reference", True),
        "maintenance_unit_references": (qn(LOGICAL_PRODUCT_NS, "MaintenanceUnitReference"), "reference", True),
        "contact_person_references": (qn(LOGICAL_PRODUCT_NS, "ContactPersonReference"), "reference", True),
        "publications": (qn(REUSABLE_NS, "Publication"), "element", True),
        "source_classification_reference": (qn(LOGICAL_PRODUCT_NS, "SourceClassificationReference"), "reference", False),
        "target_classification_references": (qn(LOGICAL_PRODUCT_NS, "TargetClassificationReference"), "reference", True),
        "source_level_reference": (qn(LOGICAL_PRODUCT_NS, "SourceLevelReference"), "reference", False),
        "target_level_references": (qn(LOGICAL_PRODUCT_NS, "TargetLevelReference"), "reference", True),
        "relationship_mapping_type": (qn(LOGICAL_PRODUCT_NS, "RelationshipMappingType"), "code_value", False),
        "maps": (qn(LOGICAL_PRODUCT_NS, "Maps"), "element", True),
        "floating_map_date": (qn(LOGICAL_PRODUCT_NS, "FloatingMapDate"), "element", False),
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
        qn(REUSABLE_NS, "Name"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "OwnerReference"),
        qn(LOGICAL_PRODUCT_NS, "MaintenanceUnitReference"),
        qn(LOGICAL_PRODUCT_NS, "ContactPersonReference"),
        qn(REUSABLE_NS, "Publication"),
        qn(LOGICAL_PRODUCT_NS, "SourceClassificationReference"),
        qn(LOGICAL_PRODUCT_NS, "TargetClassificationReference"),
        qn(LOGICAL_PRODUCT_NS, "SourceLevelReference"),
        qn(LOGICAL_PRODUCT_NS, "TargetLevelReference"),
        qn(LOGICAL_PRODUCT_NS, "RelationshipMappingType"),
        qn(LOGICAL_PRODUCT_NS, "Maps"),
        qn(LOGICAL_PRODUCT_NS, "FloatingMapDate"),
    ]


@dataclass
class ClassificationFamilyFields(MaintainableBase):
    """A Classification Family is a group of Classification Series related from a particular point of view. The Classification Family is related by being based on a common concept (e.g. economic activity)."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ClassificationFamily")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    classification_series: list[Element] = field(default_factory=list)  # [0..*]
    classification_series_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "Name"), "intl_string", True),
        "classification_series": (qn(LOGICAL_PRODUCT_NS, "ClassificationSeries"), "element", True),
        "classification_series_references": (qn(REUSABLE_NS, "ClassificationSeriesReference"), "reference", True),
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
        qn(REUSABLE_NS, "Name"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationSeries"),
        qn(REUSABLE_NS, "ClassificationSeriesReference"),
    ]


@dataclass
class ClassificationIndexEntryFields(MaintainableBase):
    """A Classification Index Entry is a word or a short text (e.g. the name of a locality, an economic activity or an occupational title) describing a type of object/unit or object property to which a Class"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ClassificationIndexEntry")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    entry_text: Optional[Element] = None  # [0..1]
    codes_classification_item_reference: Optional[Reference] = None  # [0..1]
    valid_from: Optional[Element] = None  # [0..1]
    valid_to: Optional[Element] = None  # [0..1]
    coding_instructions: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "entry_text": (qn(LOGICAL_PRODUCT_NS, "EntryText"), "element", False),
        "codes_classification_item_reference": (qn(LOGICAL_PRODUCT_NS, "CodesClassificationItemReference"), "reference", False),
        "valid_from": (qn(LOGICAL_PRODUCT_NS, "ValidFrom"), "element", False),
        "valid_to": (qn(LOGICAL_PRODUCT_NS, "ValidTo"), "element", False),
        "coding_instructions": (qn(LOGICAL_PRODUCT_NS, "CodingInstructions"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "EntryText"),
        qn(LOGICAL_PRODUCT_NS, "CodesClassificationItemReference"),
        qn(LOGICAL_PRODUCT_NS, "ValidFrom"),
        qn(LOGICAL_PRODUCT_NS, "ValidTo"),
        qn(LOGICAL_PRODUCT_NS, "CodingInstructions"),
    ]


@dataclass
class ClassificationIndexFields(MaintainableBase):
    """A Classification Index is an ordered list (alphabetical, in code order etc) of Classification Index Entries. A Classification Index can relate to one particular or to several Statistical Classificatio"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ClassificationIndex")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    release_date: Optional[Element] = None  # [0..1]
    maintenance_unit_references: list[Reference] = field(default_factory=list)  # [0..*]
    contact_person_references: list[Reference] = field(default_factory=list)  # [0..*]
    publications: list[Element] = field(default_factory=list)  # [0..*]
    languages: list[str] = field(default_factory=list)  # [0..*]
    corrections: Optional[Element] = None  # [0..1]
    coding_instructions: Optional[Element] = None  # [0..1]
    classification_index_entries: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "Name"), "intl_string", True),
        "release_date": (qn(LOGICAL_PRODUCT_NS, "ReleaseDate"), "element", False),
        "maintenance_unit_references": (qn(LOGICAL_PRODUCT_NS, "MaintenanceUnitReference"), "reference", True),
        "contact_person_references": (qn(LOGICAL_PRODUCT_NS, "ContactPersonReference"), "reference", True),
        "publications": (qn(REUSABLE_NS, "Publication"), "element", True),
        "languages": (qn(LOGICAL_PRODUCT_NS, "Languages"), "str", True),
        "corrections": (qn(LOGICAL_PRODUCT_NS, "Corrections"), "element", False),
        "coding_instructions": (qn(LOGICAL_PRODUCT_NS, "CodingInstructions"), "element", False),
        "classification_index_entries": (qn(LOGICAL_PRODUCT_NS, "ClassificationIndexEntry"), "element", True),
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
        qn(REUSABLE_NS, "Name"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "ReleaseDate"),
        qn(LOGICAL_PRODUCT_NS, "MaintenanceUnitReference"),
        qn(LOGICAL_PRODUCT_NS, "ContactPersonReference"),
        qn(REUSABLE_NS, "Publication"),
        qn(LOGICAL_PRODUCT_NS, "Languages"),
        qn(LOGICAL_PRODUCT_NS, "Corrections"),
        qn(LOGICAL_PRODUCT_NS, "CodingInstructions"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationIndexEntry"),
    ]


@dataclass
class ClassificationItemFields(MaintainableBase):
    """A Classification Item represents a Category at a certain Level within a Statistical Classification. It defines the content and the borders of the category. An object/unit can be classified to one and """

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ClassificationItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    item_code: Optional[str] = None  # [0..1]
    defining_concept_references: list[Reference] = field(default_factory=list)  # [0..*]
    includes: Optional[Element] = None  # [0..1]
    includes_also: Optional[Element] = None  # [0..1]
    excludes: Optional[Element] = None  # [0..1]
    excluded_classification_item_references: list[Reference] = field(default_factory=list)  # [0..*]
    is_generated: Optional[bool] = None  # [0..1]
    is_valid: Optional[bool] = None  # [0..1]
    valid_from: Optional[Element] = None  # [0..1]
    valid_to: Optional[Element] = None  # [0..1]
    future_events: Optional[Element] = None  # [0..1]
    successor_classification_item_references: list[Reference] = field(default_factory=list)  # [0..*]
    changes_from_prior_version: Optional[Element] = None  # [0..1]
    updates: Optional[Element] = None  # [0..1]
    parent_classification_item_reference: Optional[Reference] = None  # [0..1]
    case_laws: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "Name"), "intl_string", True),
        "item_code": (qn(LOGICAL_PRODUCT_NS, "ItemCode"), "str", False),
        "defining_concept_references": (qn(REUSABLE_NS, "DefiningConceptReference"), "reference", True),
        "includes": (qn(LOGICAL_PRODUCT_NS, "Includes"), "element", False),
        "includes_also": (qn(LOGICAL_PRODUCT_NS, "IncludesAlso"), "element", False),
        "excludes": (qn(LOGICAL_PRODUCT_NS, "Excludes"), "element", False),
        "excluded_classification_item_references": (qn(LOGICAL_PRODUCT_NS, "ExcludedClassificationItemReference"), "reference", True),
        "is_generated": (qn(LOGICAL_PRODUCT_NS, "IsGenerated"), "bool", False),
        "is_valid": (qn(LOGICAL_PRODUCT_NS, "IsValid"), "bool", False),
        "valid_from": (qn(LOGICAL_PRODUCT_NS, "ValidFrom"), "element", False),
        "valid_to": (qn(LOGICAL_PRODUCT_NS, "ValidTo"), "element", False),
        "future_events": (qn(LOGICAL_PRODUCT_NS, "FutureEvents"), "element", False),
        "successor_classification_item_references": (qn(LOGICAL_PRODUCT_NS, "SuccessorClassificationItemReference"), "reference", True),
        "changes_from_prior_version": (qn(LOGICAL_PRODUCT_NS, "ChangesFromPriorVersion"), "element", False),
        "updates": (qn(LOGICAL_PRODUCT_NS, "Updates"), "element", False),
        "parent_classification_item_reference": (qn(LOGICAL_PRODUCT_NS, "ParentClassificationItemReference"), "reference", False),
        "case_laws": (qn(LOGICAL_PRODUCT_NS, "CaseLaw"), "element", True),
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
        qn(REUSABLE_NS, "Name"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "ItemCode"),
        qn(REUSABLE_NS, "DefiningConceptReference"),
        qn(LOGICAL_PRODUCT_NS, "Includes"),
        qn(LOGICAL_PRODUCT_NS, "IncludesAlso"),
        qn(LOGICAL_PRODUCT_NS, "Excludes"),
        qn(LOGICAL_PRODUCT_NS, "ExcludedClassificationItemReference"),
        qn(LOGICAL_PRODUCT_NS, "IsGenerated"),
        qn(LOGICAL_PRODUCT_NS, "IsValid"),
        qn(LOGICAL_PRODUCT_NS, "ValidFrom"),
        qn(LOGICAL_PRODUCT_NS, "ValidTo"),
        qn(LOGICAL_PRODUCT_NS, "FutureEvents"),
        qn(LOGICAL_PRODUCT_NS, "SuccessorClassificationItemReference"),
        qn(LOGICAL_PRODUCT_NS, "ChangesFromPriorVersion"),
        qn(LOGICAL_PRODUCT_NS, "Updates"),
        qn(LOGICAL_PRODUCT_NS, "ParentClassificationItemReference"),
        qn(LOGICAL_PRODUCT_NS, "CaseLaw"),
    ]


@dataclass
class ClassificationLevelFields(MaintainableBase):
    """A Statistical Classification has a structure which is composed of one or several Levels. A Level often is associated with a concept, which defines it. In a hierarchical Statistical Classification the """

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ClassificationLevel")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    level_code_type: Optional[CodeValue] = None  # [0..1]
    level_code_structure: Optional[CodeValue] = None  # [0..1]
    dummy_code: Optional[Element] = None  # [0..1]
    defining_concept_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "Name"), "intl_string", True),
        "level_code_type": (qn(LOGICAL_PRODUCT_NS, "LevelCodeType"), "code_value", False),
        "level_code_structure": (qn(LOGICAL_PRODUCT_NS, "LevelCodeStructure"), "code_value", False),
        "dummy_code": (qn(LOGICAL_PRODUCT_NS, "DummyCode"), "element", False),
        "defining_concept_references": (qn(REUSABLE_NS, "DefiningConceptReference"), "reference", True),
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
        qn(REUSABLE_NS, "Name"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "LevelCodeType"),
        qn(LOGICAL_PRODUCT_NS, "LevelCodeStructure"),
        qn(LOGICAL_PRODUCT_NS, "DummyCode"),
        qn(REUSABLE_NS, "DefiningConceptReference"),
    ]


@dataclass
class ClassificationMapFields(MaintainableBase):
    """A Map is an expression of the relation between a Classification Item in a source Statistical Classification and a corresponding Classification Item in the target Statistical Classification. The Map sh"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ClassificationMap")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    source_classification_item_reference: Optional[Reference] = None  # [0..1]
    target_classification_item_reference: Optional[Reference] = None  # [0..1]
    is_complete: Optional[bool] = None  # [0..1]
    valid_from: Optional[Element] = None  # [0..1]
    valid_to: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "source_classification_item_reference": (qn(LOGICAL_PRODUCT_NS, "SourceClassificationItemReference"), "reference", False),
        "target_classification_item_reference": (qn(LOGICAL_PRODUCT_NS, "TargetClassificationItemReference"), "reference", False),
        "is_complete": (qn(LOGICAL_PRODUCT_NS, "IsComplete"), "bool", False),
        "valid_from": (qn(LOGICAL_PRODUCT_NS, "ValidFrom"), "element", False),
        "valid_to": (qn(LOGICAL_PRODUCT_NS, "ValidTo"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "SourceClassificationItemReference"),
        qn(LOGICAL_PRODUCT_NS, "TargetClassificationItemReference"),
        qn(LOGICAL_PRODUCT_NS, "IsComplete"),
        qn(LOGICAL_PRODUCT_NS, "ValidFrom"),
        qn(LOGICAL_PRODUCT_NS, "ValidTo"),
    ]


@dataclass
class ClassificationSeriesFields(MaintainableBase):
    """A Classification Series is an ensemble of one or several consecutive Statistical Classifications under a particular heading (for example ISIC or ISCO)."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ClassificationSeries")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    series_context: Optional[CodeValue] = None  # [0..1]
    unit_type_classified_reference: Optional[Reference] = None  # [0..1]
    subject_areas: list[CodeValue] = field(default_factory=list)  # [0..*]
    owner_references: list[Reference] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    statistical_classifications: list[Element] = field(default_factory=list)  # [0..*]
    statistical_classification_references: list[Reference] = field(default_factory=list)  # [0..*]
    current_statistical_classification_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "Name"), "intl_string", True),
        "series_context": (qn(LOGICAL_PRODUCT_NS, "SeriesContext"), "code_value", False),
        "unit_type_classified_reference": (qn(LOGICAL_PRODUCT_NS, "UnitTypeClassifiedReference"), "reference", False),
        "subject_areas": (qn(LOGICAL_PRODUCT_NS, "SubjectArea"), "code_value", True),
        "owner_references": (qn(LOGICAL_PRODUCT_NS, "OwnerReference"), "reference", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "statistical_classifications": (qn(LOGICAL_PRODUCT_NS, "StatisticalClassification"), "element", True),
        "statistical_classification_references": (qn(REUSABLE_NS, "StatisticalClassificationReference"), "reference", True),
        "current_statistical_classification_reference": (qn(LOGICAL_PRODUCT_NS, "CurrentStatisticalClassificationReference"), "reference", False),
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
        qn(REUSABLE_NS, "Name"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "SeriesContext"),
        qn(LOGICAL_PRODUCT_NS, "UnitTypeClassifiedReference"),
        qn(LOGICAL_PRODUCT_NS, "SubjectArea"),
        qn(LOGICAL_PRODUCT_NS, "OwnerReference"),
        qn(REUSABLE_NS, "Keyword"),
        qn(LOGICAL_PRODUCT_NS, "StatisticalClassification"),
        qn(REUSABLE_NS, "StatisticalClassificationReference"),
        qn(LOGICAL_PRODUCT_NS, "CurrentStatisticalClassificationReference"),
    ]


@dataclass
class CodeListGroupFields(MaintainableBase):
    """A grouping of CodeLists for conceptual or administrative purposed. May be hierarchical."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CodeListGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    type_of_code_list_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    code_list_references: list[Reference] = field(default_factory=list)  # [0..*]
    code_list_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_code_list_group": (qn(LOGICAL_PRODUCT_NS, "TypeOfCodeListGroup"), "code_value", False),
        "names": (qn(LOGICAL_PRODUCT_NS, "CodeListGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "code_list_references": (qn(REUSABLE_NS, "CodeListReference"), "reference", True),
        "code_list_group_references": (qn(LOGICAL_PRODUCT_NS, "CodeListGroupReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "TypeOfCodeListGroup"),
        qn(LOGICAL_PRODUCT_NS, "CodeListGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "CodeListReference"),
        qn(LOGICAL_PRODUCT_NS, "CodeListGroupReference"),
    ]


@dataclass
class CodeListSchemeFields(MaintainableBase):
    """A scheme containing sets of CodeLists that are used by reference to define code representations used by value representations and response domains. In addition to the standard name, label, description"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CodeListScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    code_list_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    code_lists: list[Element] = field(default_factory=list)  # [0..*]
    code_list_references: list[Reference] = field(default_factory=list)  # [0..*]
    code_list_groups: list[Element] = field(default_factory=list)  # [0..*]
    code_list_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "CodeListSchemeName"), "intl_string", True),
        "code_list_scheme_references": (qn(REUSABLE_NS, "CodeListSchemeReference"), "reference", True),
        "code_lists": (qn(LOGICAL_PRODUCT_NS, "CodeList"), "element", True),
        "code_list_references": (qn(REUSABLE_NS, "CodeListReference"), "reference", True),
        "code_list_groups": (qn(LOGICAL_PRODUCT_NS, "CodeListGroup"), "element", True),
        "code_list_group_references": (qn(LOGICAL_PRODUCT_NS, "CodeListGroupReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "CodeListSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "CodeListSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "CodeList"),
        qn(REUSABLE_NS, "CodeListReference"),
        qn(LOGICAL_PRODUCT_NS, "CodeListGroup"),
        qn(LOGICAL_PRODUCT_NS, "CodeListGroupReference"),
    ]


@dataclass
class CodeListFields(MaintainableBase):
    """A structure used to associate a list of code values to specified categories. May be flat or hierarchical. This is a maintainable object. In addition to the standard name, label, and description the Co"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CodeList")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    code_list_references: list[Reference] = field(default_factory=list)  # [0..*]
    category_scheme_reference: Optional[Reference] = None  # [0..1]
    hierarchy_type: Optional[Element] = None  # [0..1]
    levels: list[Element] = field(default_factory=list)  # [0..*]
    codes: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    isSystemMissingValue: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "CodeListName"), "intl_string", True),
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "code_list_references": (qn(REUSABLE_NS, "CodeListReference"), "reference", True),
        "category_scheme_reference": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", False),
        "hierarchy_type": (qn(LOGICAL_PRODUCT_NS, "HierarchyType"), "element", False),
        "levels": (qn(LOGICAL_PRODUCT_NS, "Level"), "element", True),
        "codes": (qn(LOGICAL_PRODUCT_NS, "Code"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "lang": ("lang", "str"),
        "isSystemMissingValue": ("isSystemMissingValue", "bool"),
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
        qn(LOGICAL_PRODUCT_NS, "CodeListName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "CodeListReference"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "HierarchyType"),
        qn(LOGICAL_PRODUCT_NS, "Level"),
        qn(LOGICAL_PRODUCT_NS, "Code"),
    ]


@dataclass
class CodeFields(MaintainableBase):
    """A structure that links a unique value of a code to a specified category and provides information as to the location of the code within a hierarchy, whether it is discrete, represents a total for the C"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Code")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    category_reference: Optional[Reference] = None  # [1..1]
    value: Optional[Element] = None  # [1..1]
    codes: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    isDiscrete: Optional[bool] = None  # @attr
    levelNumber: Optional[int] = None  # @attr
    isComprehensive: Optional[str] = None  # @attr
    isTotal: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "category_reference": (qn(REUSABLE_NS, "CategoryReference"), "reference", False),
        "value": (qn(REUSABLE_NS, "Value"), "element", False),
        "codes": (qn(LOGICAL_PRODUCT_NS, "Code"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "isDiscrete": ("isDiscrete", "bool"),
        "levelNumber": ("levelNumber", "int"),
        "isComprehensive": ("isComprehensive", "str"),
        "isTotal": ("isTotal", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "CategoryReference"),
        qn(REUSABLE_NS, "Value"),
        qn(LOGICAL_PRODUCT_NS, "Code"),
    ]


@dataclass
class CohortFields(MaintainableBase):
    """Defines the included values of a dimension by means of individual value references or by defining a range of values to include. Allows the included values to be identified by reference to the Code, th"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Cohort")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    category_references: list[Reference] = field(default_factory=list)  # [0..*]
    code_references: list[Reference] = field(default_factory=list)  # [0..*]
    ranges: list[Element] = field(default_factory=list)  # [0..*]
    rank: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "category_references": (qn(REUSABLE_NS, "CategoryReference"), "reference", True),
        "code_references": (qn(REUSABLE_NS, "CodeReference"), "reference", True),
        "ranges": (qn(REUSABLE_NS, "Range"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "rank": ("rank", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "CategoryReference"),
        qn(REUSABLE_NS, "CodeReference"),
        qn(REUSABLE_NS, "Range"),
    ]


@dataclass
class ConcatenatedValueFields(MaintainableBase):
    """Lists the variables whose values when concatenated result in the value for this variable."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ConcatenatedValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    variable_references: list[Reference] = field(default_factory=list)  # [2..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_references": (qn(REUSABLE_NS, "VariableReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableReference"),
    ]


@dataclass
class ConditionalIdentifierFields(MaintainableBase):
    """Describes the information needed to identify a specific record or case within a record type. Repeating the field allows multiple means of identifying a case referencing multiple variables."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ConditionalIdentifier")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    case_specifications: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "case_specifications": (qn(LOGICAL_PRODUCT_NS, "CaseSpecification"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "CaseSpecification"),
    ]


@dataclass
class ConditionalVariableReferenceFields(MaintainableBase):
    """Value of variable indicating this record type, multiple entries allow for multiple valid values or ranges. Includes a reference to the variable an the specified related value. TypeOfObject should be s"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "ConditionalVariableReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    type_of_object: Optional[Element] = None  # [1..1]
    related_value: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "related_value": (qn(LOGICAL_PRODUCT_NS, "RelatedValue"), "element", False),
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
        qn(LOGICAL_PRODUCT_NS, "RelatedValue"),
    ]


@dataclass
class CoordinateRegionFields(MaintainableBase):
    """Defines the area of attachment for an NCube attribute. It may be defined as the NCube as a whole or as certain dimensions or values of dimensions."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CoordinateRegion")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    dimension_values: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "dimension_values": (qn(LOGICAL_PRODUCT_NS, "DimensionValue"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "DimensionValue"),
    ]


@dataclass
class DataRelationshipFields(MaintainableBase):
    """Describes the relationships among logical records in the dataset. Date Relationship is needed to create the appropriate link between the logical record and the physical storage description. Data Relat"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "DataRelationship")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    logical_records: list[Element] = field(default_factory=list)  # [0..*]
    record_relationships: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "DataRelationshipName"), "intl_string", True),
        "logical_records": (qn(LOGICAL_PRODUCT_NS, "LogicalRecord"), "element", True),
        "record_relationships": (qn(LOGICAL_PRODUCT_NS, "RecordRelationship"), "element", True),
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
        qn(LOGICAL_PRODUCT_NS, "DataRelationshipName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "LogicalRecord"),
        qn(LOGICAL_PRODUCT_NS, "RecordRelationship"),
    ]


@dataclass
class DefaultMissingValuesFields(MaintainableBase):
    """Identifies the default missing value parameter for the this logical record by referencing a ManagedMissingValuesRepresentation or by stating that there is a default missing values parameter used but i"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "DefaultMissingValues")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    missing_values_reference: Optional[Reference] = None  # [1..1]
    default_used_no_documentation: Optional[bool] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "missing_values_reference": (qn(LOGICAL_PRODUCT_NS, "MissingValuesReference"), "reference", False),
        "default_used_no_documentation": (qn(LOGICAL_PRODUCT_NS, "DefaultUsedNoDocumentation"), "bool", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "MissingValuesReference"),
        qn(LOGICAL_PRODUCT_NS, "DefaultUsedNoDocumentation"),
    ]


@dataclass
class DimensionFields(MaintainableBase):
    """A dimension is provided a rank and a reference to a variable that describes it. Cell locations are "addressed" by the value of their intersect on each dimension provided in rank order."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Dimension")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    variable_reference: Optional[Reference] = None  # [1..1]
    rank: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "rank": ("rank", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableReference"),
    ]


@dataclass
class FixedIdentifierFields(MaintainableBase):
    """Reference to the variable containing the unique identifier. This may be a concatenated variable which indicates the combination of variable required to create a unique identification. If more than one"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "FixedIdentifier")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_references": (qn(REUSABLE_NS, "VariableReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableReference"),
    ]


@dataclass
class GenerationFields(MaintainableBase):
    """Description of the process used to generate the category content. Includes a reference to component parts, a description of the generation process, a structured command, and other materials that are n"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Generation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    component_references: list[Reference] = field(default_factory=list)  # [0..*]
    command_codes: list[Element] = field(default_factory=list)  # [0..*]
    other_materials: list[Element] = field(default_factory=list)  # [0..*]
    other_material_references: list[Reference] = field(default_factory=list)  # [0..*]
    isDerived: Optional[bool] = None  # @attr
    qualification: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "component_references": (qn(LOGICAL_PRODUCT_NS, "ComponentReference"), "reference", True),
        "command_codes": (qn(REUSABLE_NS, "CommandCode"), "element", True),
        "other_materials": (qn(REUSABLE_NS, "OtherMaterial"), "element", True),
        "other_material_references": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isDerived": ("isDerived", "bool"),
        "qualification": ("qualification", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "ComponentReference"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "CommandCode"),
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
    ]


@dataclass
class LevelContextFields(MaintainableBase):
    """Level Context provides the depth of a Level within a Statistical Classification together with its membership. Both depth and membership can be specified per Statistical Classification."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "LevelContext")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    level_number: Optional[int] = None  # [0..1]
    classification_level: Optional[Element] = None  # [1..1]
    classification_level_reference: Optional[Reference] = None  # [1..1]
    classification_items: list[Element] = field(default_factory=list)  # [0..*]
    classification_item_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "level_number": (qn(LOGICAL_PRODUCT_NS, "LevelNumber"), "int", False),
        "classification_level": (qn(LOGICAL_PRODUCT_NS, "ClassificationLevel"), "element", False),
        "classification_level_reference": (qn(LOGICAL_PRODUCT_NS, "ClassificationLevelReference"), "reference", False),
        "classification_items": (qn(LOGICAL_PRODUCT_NS, "ClassificationItem"), "element", True),
        "classification_item_references": (qn(LOGICAL_PRODUCT_NS, "ClassificationItemReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "LevelNumber"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationLevel"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationLevelReference"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationItem"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationItemReference"),
    ]


@dataclass
class LevelFields(MaintainableBase):
    """Used to describe the levels of the code list hierarchy. The level describes the nesting structure of a hierarchical coding structure. A level could have data attached to it (summary of its children) o"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Level")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    category_relationship: Optional[Element] = None  # [0..1]
    interval_increment: Optional[Element] = None  # [0..1]
    levelNumber: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "LevelName"), "intl_string", True),
        "category_relationship": (qn(LOGICAL_PRODUCT_NS, "CategoryRelationship"), "element", False),
        "interval_increment": (qn(LOGICAL_PRODUCT_NS, "IntervalIncrement"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "levelNumber": ("levelNumber", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "LevelName"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "CategoryRelationship"),
        qn(LOGICAL_PRODUCT_NS, "IntervalIncrement"),
    ]


@dataclass
class LogicalProductFields(MaintainableBase):
    """A module describing the logical (intellectual) contents of the quantitative data. It is a member of the substitution group BaseLogicalProduct and contains all of the common features of the BaseLogical"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "LogicalProduct")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    coverage: Optional[Element] = None  # [0..1]
    data_relationships: list[Element] = field(default_factory=list)  # [0..*]
    data_relationship_references: list[Reference] = field(default_factory=list)  # [0..*]
    category_schemes: list[Element] = field(default_factory=list)  # [0..*]
    category_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    code_list_schemes: list[Element] = field(default_factory=list)  # [0..*]
    code_list_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    managed_representation_schemes: list[Element] = field(default_factory=list)  # [0..*]
    managed_representation_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    represented_variable_schemes: list[Element] = field(default_factory=list)  # [0..*]
    represented_variable_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    variable_schemes: list[Element] = field(default_factory=list)  # [0..*]
    variable_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    n_cube_schemes: list[Element] = field(default_factory=list)  # [0..*]
    n_cube_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "LogicalProductName"), "intl_string", True),
        "coverage": (qn(REUSABLE_NS, "Coverage"), "element", False),
        "data_relationships": (qn(LOGICAL_PRODUCT_NS, "DataRelationship"), "element", True),
        "data_relationship_references": (qn(REUSABLE_NS, "DataRelationshipReference"), "reference", True),
        "category_schemes": (qn(LOGICAL_PRODUCT_NS, "CategoryScheme"), "element", True),
        "category_scheme_references": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", True),
        "code_list_schemes": (qn(LOGICAL_PRODUCT_NS, "CodeListScheme"), "element", True),
        "code_list_scheme_references": (qn(REUSABLE_NS, "CodeListSchemeReference"), "reference", True),
        "managed_representation_schemes": (qn(REUSABLE_NS, "ManagedRepresentationScheme"), "element", True),
        "managed_representation_scheme_references": (qn(REUSABLE_NS, "ManagedRepresentationSchemeReference"), "reference", True),
        "represented_variable_schemes": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme"), "element", True),
        "represented_variable_scheme_references": (qn(REUSABLE_NS, "RepresentedVariableSchemeReference"), "reference", True),
        "variable_schemes": (qn(LOGICAL_PRODUCT_NS, "VariableScheme"), "element", True),
        "variable_scheme_references": (qn(REUSABLE_NS, "VariableSchemeReference"), "reference", True),
        "n_cube_schemes": (qn(LOGICAL_PRODUCT_NS, "NCubeScheme"), "element", True),
        "n_cube_scheme_references": (qn(REUSABLE_NS, "NCubeSchemeReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "LogicalProductName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Coverage"),
        qn(LOGICAL_PRODUCT_NS, "DataRelationship"),
        qn(REUSABLE_NS, "DataRelationshipReference"),
        qn(LOGICAL_PRODUCT_NS, "CategoryScheme"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "CodeListScheme"),
        qn(REUSABLE_NS, "CodeListSchemeReference"),
        qn(REUSABLE_NS, "ManagedRepresentationScheme"),
        qn(REUSABLE_NS, "ManagedRepresentationSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme"),
        qn(REUSABLE_NS, "RepresentedVariableSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "VariableScheme"),
        qn(REUSABLE_NS, "VariableSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "NCubeScheme"),
        qn(REUSABLE_NS, "NCubeSchemeReference"),
    ]


@dataclass
class LogicalRecordFields(MaintainableBase):
    """A logical record is a description of all of the elements (variables or NCubes) related to a single case or analysis unit. Required to link a description of a physical record structure to its logical r"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "LogicalRecord")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    variable_value_reference: Optional[Reference] = None  # [0..1]
    support_for_multiple_segments: Optional[Element] = None  # [0..1]
    case_identifications: list[Element] = field(default_factory=list)  # [0..*]
    variables_in_record: Optional[Element] = None  # [1..1]
    n_cubes_in_record: Optional[Element] = None  # [1..1]
    default_missing_values: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    hasLocator: Optional[bool] = None  # @attr
    variableQuantity: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "LogicalRecordName"), "intl_string", True),
        "variable_value_reference": (qn(LOGICAL_PRODUCT_NS, "VariableValueReference"), "reference", False),
        "support_for_multiple_segments": (qn(LOGICAL_PRODUCT_NS, "SupportForMultipleSegments"), "element", False),
        "case_identifications": (qn(LOGICAL_PRODUCT_NS, "CaseIdentification"), "element", True),
        "variables_in_record": (qn(LOGICAL_PRODUCT_NS, "VariablesInRecord"), "element", False),
        "n_cubes_in_record": (qn(LOGICAL_PRODUCT_NS, "NCubesInRecord"), "element", False),
        "default_missing_values": (qn(LOGICAL_PRODUCT_NS, "DefaultMissingValues"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "hasLocator": ("hasLocator", "bool"),
        "variableQuantity": ("variableQuantity", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(LOGICAL_PRODUCT_NS, "LogicalRecordName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "VariableValueReference"),
        qn(LOGICAL_PRODUCT_NS, "SupportForMultipleSegments"),
        qn(LOGICAL_PRODUCT_NS, "CaseIdentification"),
        qn(LOGICAL_PRODUCT_NS, "VariablesInRecord"),
        qn(LOGICAL_PRODUCT_NS, "NCubesInRecord"),
        qn(LOGICAL_PRODUCT_NS, "DefaultMissingValues"),
    ]


@dataclass
class MeasureDefinitionFields(MaintainableBase):
    """Defines the structure and type of measure captured within the cells. This may be repeated to describe multiple measure for the cells (i.e., count, percent of universe, dimensional percent, index, text"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "MeasureDefinition")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    variable_reference: Optional[Reference] = None  # [1..1]
    aggregation_definition: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
        "aggregation_definition": (qn(LOGICAL_PRODUCT_NS, "AggregationDefinition"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "VariableReference"),
        qn(LOGICAL_PRODUCT_NS, "AggregationDefinition"),
    ]


@dataclass
class NCubeGroupFields(MaintainableBase):
    """Contains a group of NCubes, which may be ordered or hierarchical. In addition to the name, label, and description of the group, the structure allows for defining the type of group using an optional co"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "NCubeGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    type_of_n_cube_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    n_cube_references: list[Reference] = field(default_factory=list)  # [0..*]
    n_cube_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_n_cube_group": (qn(LOGICAL_PRODUCT_NS, "TypeOfNCubeGroup"), "code_value", False),
        "names": (qn(LOGICAL_PRODUCT_NS, "NCubeGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "n_cube_references": (qn(REUSABLE_NS, "NCubeReference"), "reference", True),
        "n_cube_group_references": (qn(LOGICAL_PRODUCT_NS, "NCubeGroupReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "TypeOfNCubeGroup"),
        qn(LOGICAL_PRODUCT_NS, "NCubeGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "NCubeReference"),
        qn(LOGICAL_PRODUCT_NS, "NCubeGroupReference"),
    ]


@dataclass
class NCubeSchemeFields(MaintainableBase):
    """A set of NCubes maintained by an agency and used to structure data items into relational structures. In addition to the standard name, label, and description of the scheme, contains descriptions of in"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "NCubeScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    n_cubes: list[Element] = field(default_factory=list)  # [0..*]
    n_cube_references: list[Reference] = field(default_factory=list)  # [0..*]
    n_cube_groups: list[Element] = field(default_factory=list)  # [0..*]
    n_cube_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    n_cube_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "NCubeSchemeName"), "intl_string", True),
        "n_cubes": (qn(LOGICAL_PRODUCT_NS, "NCube"), "element", True),
        "n_cube_references": (qn(REUSABLE_NS, "NCubeReference"), "reference", True),
        "n_cube_groups": (qn(LOGICAL_PRODUCT_NS, "NCubeGroup"), "element", True),
        "n_cube_group_references": (qn(LOGICAL_PRODUCT_NS, "NCubeGroupReference"), "reference", True),
        "n_cube_scheme_references": (qn(REUSABLE_NS, "NCubeSchemeReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "NCubeSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "NCube"),
        qn(REUSABLE_NS, "NCubeReference"),
        qn(LOGICAL_PRODUCT_NS, "NCubeGroup"),
        qn(LOGICAL_PRODUCT_NS, "NCubeGroupReference"),
        qn(REUSABLE_NS, "NCubeSchemeReference"),
    ]


@dataclass
class NCubeFields(MaintainableBase):
    """An NCube is a 1..n dimension structure which relates a set of individual values to each other by defining them within a matrix. The NCube may be the result of aggregations, cross-tabulation, time-seri"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "NCube")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    imputation_reference: Optional[Reference] = None  # [0..1]
    source_unit: Optional[CodeValue] = None  # [0..1]
    analysis_unit: Optional[CodeValue] = None  # [0..1]
    purpose: Optional[Element] = None  # [0..1]
    dimensions: list[Element] = field(default_factory=list)  # [0..*]
    coordinate_regions: list[Element] = field(default_factory=list)  # [0..*]
    measure_definitions: list[Element] = field(default_factory=list)  # [0..*]
    attributes: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    dimensionCount: Optional[int] = None  # @attr
    cellCount: Optional[int] = None  # @attr
    isClean: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "NCubeName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "imputation_reference": (qn(LOGICAL_PRODUCT_NS, "ImputationReference"), "reference", False),
        "source_unit": (qn(LOGICAL_PRODUCT_NS, "SourceUnit"), "code_value", False),
        "analysis_unit": (qn(REUSABLE_NS, "AnalysisUnit"), "code_value", False),
        "purpose": (qn(REUSABLE_NS, "Purpose"), "element", False),
        "dimensions": (qn(LOGICAL_PRODUCT_NS, "Dimension"), "element", True),
        "coordinate_regions": (qn(LOGICAL_PRODUCT_NS, "CoordinateRegion"), "element", True),
        "measure_definitions": (qn(LOGICAL_PRODUCT_NS, "MeasureDefinition"), "element", True),
        "attributes": (qn(LOGICAL_PRODUCT_NS, "Attribute"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "dimensionCount": ("dimensionCount", "int"),
        "cellCount": ("cellCount", "int"),
        "isClean": ("isClean", "bool"),
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
        qn(LOGICAL_PRODUCT_NS, "NCubeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(LOGICAL_PRODUCT_NS, "ImputationReference"),
        qn(LOGICAL_PRODUCT_NS, "SourceUnit"),
        qn(REUSABLE_NS, "AnalysisUnit"),
        qn(REUSABLE_NS, "Purpose"),
        qn(LOGICAL_PRODUCT_NS, "Dimension"),
        qn(LOGICAL_PRODUCT_NS, "CoordinateRegion"),
        qn(LOGICAL_PRODUCT_NS, "MeasureDefinition"),
        qn(LOGICAL_PRODUCT_NS, "Attribute"),
    ]


@dataclass
class NCubesInRecordFields(MaintainableBase):
    """Identifies the NCubes and any variables in the record external to NCube structures such as case identification variables that are contained in the logical record by indicating that all NCubes containe"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "NCubesInRecord")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    variables_in_record: Optional[Element] = None  # [0..1]
    n_cube_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    n_cube_references: list[Reference] = field(default_factory=list)  # [0..*]
    allNCubesInLogicalProduct: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variables_in_record": (qn(LOGICAL_PRODUCT_NS, "VariablesInRecord"), "element", False),
        "n_cube_scheme_references": (qn(REUSABLE_NS, "NCubeSchemeReference"), "reference", True),
        "n_cube_references": (qn(REUSABLE_NS, "NCubeReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "allNCubesInLogicalProduct": ("allNCubesInLogicalProduct", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "VariablesInRecord"),
        qn(REUSABLE_NS, "NCubeSchemeReference"),
        qn(REUSABLE_NS, "NCubeReference"),
    ]


@dataclass
class RecordRelationshipFields(MaintainableBase):
    """Describes the relationship between records of different types or of the same type within a longitudinal study. Identifies the key and linking value relationships. All relationships are pairwise. Multi"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "RecordRelationship")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    source_logical_record_reference: Optional[Reference] = None  # [1..1]
    target_logical_record_reference: Optional[Reference] = None  # [1..1]
    source_target_links: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    relationToTarget: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "RecordRelationshipName"), "intl_string", True),
        "source_logical_record_reference": (qn(LOGICAL_PRODUCT_NS, "SourceLogicalRecordReference"), "reference", False),
        "target_logical_record_reference": (qn(LOGICAL_PRODUCT_NS, "TargetLogicalRecordReference"), "reference", False),
        "source_target_links": (qn(LOGICAL_PRODUCT_NS, "SourceTargetLink"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "relationToTarget": ("relationToTarget", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(LOGICAL_PRODUCT_NS, "RecordRelationshipName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "SourceLogicalRecordReference"),
        qn(LOGICAL_PRODUCT_NS, "TargetLogicalRecordReference"),
        qn(LOGICAL_PRODUCT_NS, "SourceTargetLink"),
    ]


@dataclass
class RelatedValueFields(MaintainableBase):
    """The characteristic value expressed as a string with an indicator of the specific relationship of the variable value to the characteristic value. The default is "Equal". The value may be defined as con"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "RelatedValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    space: Optional[str] = None  # @attr
    type: Optional[str] = None  # @attr
    valueIsBlank: Optional[bool] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "space": ("space", "str"),
        "type": ("type", "str"),
        "valueIsBlank": ("valueIsBlank", "bool"),
    }


@dataclass
class RepresentedVariableGroupFields(MaintainableBase):
    """Contains a group of RepresentedVariables, which may describe an ordered or hierarchical relationship structure. RepresentedVariables may be grouped for a wide range of reasons including conceptual or """

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    type_of_represented_variable_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    represented_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    represented_variable_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_represented_variable_group": (qn(LOGICAL_PRODUCT_NS, "TypeOfRepresentedVariableGroup"), "code_value", False),
        "names": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "represented_variable_references": (qn(REUSABLE_NS, "RepresentedVariableReference"), "reference", True),
        "represented_variable_group_references": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroupReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "TypeOfRepresentedVariableGroup"),
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "RepresentedVariableReference"),
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroupReference"),
    ]


@dataclass
class RepresentedVariableSchemeFields(MaintainableBase):
    """A set of RepresentedVariables managed by an agency. RepresentedVariables are the core reusable parts of a Variable. RepresentedVariable maps to the GSIM Represented Variable. In addition to the standa"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    represented_variable_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    represented_variables: list[Element] = field(default_factory=list)  # [0..*]
    represented_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    represented_variable_groups: list[Element] = field(default_factory=list)  # [0..*]
    represented_variable_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariableSchemeName"), "intl_string", True),
        "represented_variable_scheme_references": (qn(REUSABLE_NS, "RepresentedVariableSchemeReference"), "reference", True),
        "represented_variables": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariable"), "element", True),
        "represented_variable_references": (qn(REUSABLE_NS, "RepresentedVariableReference"), "reference", True),
        "represented_variable_groups": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroup"), "element", True),
        "represented_variable_group_references": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroupReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariableSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "RepresentedVariableSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariable"),
        qn(REUSABLE_NS, "RepresentedVariableReference"),
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroup"),
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroupReference"),
    ]


@dataclass
class RepresentedVariableFields(MaintainableBase):
    """Describes a RepresentedVariable contained in the RepresentedVariableScheme. In addition to the standard name, label, and description a RepresentedVariable contains a reference to the Concept and Unive"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "RepresentedVariable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    conceptual_variable_reference: Optional[Reference] = None  # [1..1]
    unit_type_reference: Optional[Reference] = None  # [0..1]
    concept_reference: Optional[Reference] = None  # [0..1]
    category_scheme_reference: Optional[Reference] = None  # [1..1]
    value_representation: Optional[Element] = None  # [1..1]
    value_representation_reference: Optional[Reference] = None  # [1..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariableName"), "intl_string", True),
        "conceptual_variable_reference": (qn(REUSABLE_NS, "ConceptualVariableReference"), "reference", False),
        "unit_type_reference": (qn(REUSABLE_NS, "UnitTypeReference"), "reference", False),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "category_scheme_reference": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", False),
        "value_representation": (qn(REUSABLE_NS, "ValueRepresentation"), "element", False),
        "value_representation_reference": (qn(REUSABLE_NS, "ValueRepresentationReference"), "reference", False),
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
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariableName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ConceptualVariableReference"),
        qn(REUSABLE_NS, "UnitTypeReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
        qn(REUSABLE_NS, "ValueRepresentation"),
        qn(REUSABLE_NS, "ValueRepresentationReference"),
    ]


@dataclass
class SourceTargetLinkFields(MaintainableBase):
    """Contains a set of variables, one from the source record and one from the target record used as all or part of a link between the source and target records."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "SourceTargetLink")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    source_link_variable_reference: Optional[Reference] = None  # [1..1]
    target_link_variable_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "source_link_variable_reference": (qn(LOGICAL_PRODUCT_NS, "SourceLinkVariableReference"), "reference", False),
        "target_link_variable_reference": (qn(LOGICAL_PRODUCT_NS, "TargetLinkVariableReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "SourceLinkVariableReference"),
        qn(LOGICAL_PRODUCT_NS, "TargetLinkVariableReference"),
    ]


@dataclass
class StatisticalClassificationFields(MaintainableBase):
    """A Statistical Classification is a set of categories which may be assigned to one or more variables registered in statistical surveys or administrative files, and used in the production and disseminati"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "StatisticalClassification")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    release_date: Optional[Element] = None  # [0..1]
    termination_date: Optional[Element] = None  # [0..1]
    is_current: Optional[bool] = None  # [0..1]
    maintenance_unit_references: list[Reference] = field(default_factory=list)  # [0..*]
    contact_person_references: list[Reference] = field(default_factory=list)  # [0..*]
    legal_bases: list[Element] = field(default_factory=list)  # [0..*]
    publications: list[Element] = field(default_factory=list)  # [0..*]
    copyright: Optional[Element] = None  # [0..1]
    is_dissemination_allowed: Optional[bool] = None  # [0..1]
    level_contexts: list[Element] = field(default_factory=list)  # [0..*]
    classification_indexs: list[Element] = field(default_factory=list)  # [0..*]
    classification_index_references: list[Reference] = field(default_factory=list)  # [0..*]
    is_version: Optional[bool] = None  # [0..1]
    is_update: Optional[bool] = None  # [0..1]
    is_floating: Optional[bool] = None  # [0..1]
    predecessor_reference: Optional[Reference] = None  # [0..1]
    successor_reference: Optional[Reference] = None  # [0..1]
    derived_from_reference: Optional[Reference] = None  # [0..1]
    changes_from_preceding: Optional[Element] = None  # [0..1]
    updates_allowed: Optional[bool] = None  # [0..1]
    permissible_updates: Optional[Element] = None  # [0..1]
    updates: Optional[Element] = None  # [0..1]
    variant_of_reference: Optional[Reference] = None  # [0..1]
    variant_changes_from_base: Optional[Element] = None  # [0..1]
    variant_purpose: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "Name"), "intl_string", True),
        "release_date": (qn(LOGICAL_PRODUCT_NS, "ReleaseDate"), "element", False),
        "termination_date": (qn(LOGICAL_PRODUCT_NS, "TerminationDate"), "element", False),
        "is_current": (qn(LOGICAL_PRODUCT_NS, "IsCurrent"), "bool", False),
        "maintenance_unit_references": (qn(LOGICAL_PRODUCT_NS, "MaintenanceUnitReference"), "reference", True),
        "contact_person_references": (qn(LOGICAL_PRODUCT_NS, "ContactPersonReference"), "reference", True),
        "legal_bases": (qn(LOGICAL_PRODUCT_NS, "LegalBase"), "element", True),
        "publications": (qn(REUSABLE_NS, "Publication"), "element", True),
        "copyright": (qn(REUSABLE_NS, "Copyright"), "element", False),
        "is_dissemination_allowed": (qn(LOGICAL_PRODUCT_NS, "IsDisseminationAllowed"), "bool", False),
        "level_contexts": (qn(LOGICAL_PRODUCT_NS, "LevelContext"), "element", True),
        "classification_indexs": (qn(LOGICAL_PRODUCT_NS, "ClassificationIndex"), "element", True),
        "classification_index_references": (qn(LOGICAL_PRODUCT_NS, "ClassificationIndexReference"), "reference", True),
        "is_version": (qn(LOGICAL_PRODUCT_NS, "IsVersion"), "bool", False),
        "is_update": (qn(LOGICAL_PRODUCT_NS, "IsUpdate"), "bool", False),
        "is_floating": (qn(LOGICAL_PRODUCT_NS, "IsFloating"), "bool", False),
        "predecessor_reference": (qn(LOGICAL_PRODUCT_NS, "PredecessorReference"), "reference", False),
        "successor_reference": (qn(LOGICAL_PRODUCT_NS, "SuccessorReference"), "reference", False),
        "derived_from_reference": (qn(LOGICAL_PRODUCT_NS, "DerivedFromReference"), "reference", False),
        "changes_from_preceding": (qn(LOGICAL_PRODUCT_NS, "ChangesFromPreceding"), "element", False),
        "updates_allowed": (qn(LOGICAL_PRODUCT_NS, "UpdatesAllowed"), "bool", False),
        "permissible_updates": (qn(LOGICAL_PRODUCT_NS, "PermissibleUpdates"), "element", False),
        "updates": (qn(LOGICAL_PRODUCT_NS, "Updates"), "element", False),
        "variant_of_reference": (qn(LOGICAL_PRODUCT_NS, "VariantOfReference"), "reference", False),
        "variant_changes_from_base": (qn(LOGICAL_PRODUCT_NS, "VariantChangesFromBase"), "element", False),
        "variant_purpose": (qn(LOGICAL_PRODUCT_NS, "VariantPurpose"), "element", False),
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
        qn(REUSABLE_NS, "Name"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(LOGICAL_PRODUCT_NS, "ReleaseDate"),
        qn(LOGICAL_PRODUCT_NS, "TerminationDate"),
        qn(LOGICAL_PRODUCT_NS, "IsCurrent"),
        qn(LOGICAL_PRODUCT_NS, "MaintenanceUnitReference"),
        qn(LOGICAL_PRODUCT_NS, "ContactPersonReference"),
        qn(LOGICAL_PRODUCT_NS, "LegalBase"),
        qn(REUSABLE_NS, "Publication"),
        qn(REUSABLE_NS, "Copyright"),
        qn(LOGICAL_PRODUCT_NS, "IsDisseminationAllowed"),
        qn(LOGICAL_PRODUCT_NS, "LevelContext"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationIndex"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationIndexReference"),
        qn(LOGICAL_PRODUCT_NS, "IsVersion"),
        qn(LOGICAL_PRODUCT_NS, "IsUpdate"),
        qn(LOGICAL_PRODUCT_NS, "IsFloating"),
        qn(LOGICAL_PRODUCT_NS, "PredecessorReference"),
        qn(LOGICAL_PRODUCT_NS, "SuccessorReference"),
        qn(LOGICAL_PRODUCT_NS, "DerivedFromReference"),
        qn(LOGICAL_PRODUCT_NS, "ChangesFromPreceding"),
        qn(LOGICAL_PRODUCT_NS, "UpdatesAllowed"),
        qn(LOGICAL_PRODUCT_NS, "PermissibleUpdates"),
        qn(LOGICAL_PRODUCT_NS, "Updates"),
        qn(LOGICAL_PRODUCT_NS, "VariantOfReference"),
        qn(LOGICAL_PRODUCT_NS, "VariantChangesFromBase"),
        qn(LOGICAL_PRODUCT_NS, "VariantPurpose"),
    ]


@dataclass
class SubCategoryReferenceFields(MaintainableBase):
    """Reference to one or more categories for which the current category is a broader definition. Allows for a reference to the narrower category and the ability to define the relationship as a specializati"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "SubCategoryReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    type_of_object: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    typeOfSubCategory: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isExternal": ("isExternal", "bool"),
        "isReference": ("isReference", "bool"),
        "lateBound": ("lateBound", "bool"),
        "lateBoundRestriction": ("lateBoundRestriction", "str"),
        "objectLanguage": ("objectLanguage", "str"),
        "sourceContext": ("sourceContext", "str"),
        "typeOfSubCategory": ("typeOfSubCategory", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "UserAttributePair"),
    ]


@dataclass
class VariableAttributeFields(MaintainableBase):
    """An attribute may be any other Variable which should be attached to or coupled with a Variable such as a weight, filter, or other related variable. The VariableAttribute may be typed using a Controlled"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "VariableAttribute")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    type_of_variable_attribute: Optional[CodeValue] = None  # [1..1]
    variable_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_variable_attribute": (qn(LOGICAL_PRODUCT_NS, "TypeOfVariableAttribute"), "code_value", False),
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "TypeOfVariableAttribute"),
        qn(REUSABLE_NS, "VariableReference"),
    ]


@dataclass
class VariableGroupFields(MaintainableBase):
    """Contains a group of Variables, which may be ordered or hierarchical. In addition to the name, label, and description of the group, the structure allows for defining the type of group using an optional"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "VariableGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    type_of_variable_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    variable_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_variable_group": (qn(LOGICAL_PRODUCT_NS, "TypeOfVariableGroup"), "code_value", False),
        "names": (qn(LOGICAL_PRODUCT_NS, "VariableGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "variable_references": (qn(REUSABLE_NS, "VariableReference"), "reference", True),
        "variable_group_references": (qn(LOGICAL_PRODUCT_NS, "VariableGroupReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "TypeOfVariableGroup"),
        qn(LOGICAL_PRODUCT_NS, "VariableGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "VariableReference"),
        qn(LOGICAL_PRODUCT_NS, "VariableGroupReference"),
    ]


@dataclass
class VariableRepresentationFields(MaintainableBase):
    """Describes the representation of the variable in the data set. Describes the function of the variable, variables or standard weights that may be used to weight this variable during analysis, imputation"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "VariableRepresentation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    variable_role: Optional[CodeValue] = None  # [0..1]
    weight_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    standard_weight_reference: Optional[Reference] = None  # [0..1]
    variable_attributes: list[Element] = field(default_factory=list)  # [0..*]
    imputation_reference: Optional[Reference] = None  # [0..1]
    concatenated_value: Optional[Element] = None  # [0..1]
    processing_instruction_reference: Optional[Reference] = None  # [0..1]
    value_representations: list[Element] = field(default_factory=list)  # [0..*]
    value_representation_references: list[Reference] = field(default_factory=list)  # [0..*]
    missing_values_reference: Optional[Reference] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    aggregation_method: Optional[CodeValue] = None  # [0..1]
    additivity: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_role": (qn(LOGICAL_PRODUCT_NS, "VariableRole"), "code_value", False),
        "weight_variable_references": (qn(REUSABLE_NS, "WeightVariableReference"), "reference", True),
        "standard_weight_reference": (qn(LOGICAL_PRODUCT_NS, "StandardWeightReference"), "reference", False),
        "variable_attributes": (qn(LOGICAL_PRODUCT_NS, "VariableAttribute"), "element", True),
        "imputation_reference": (qn(LOGICAL_PRODUCT_NS, "ImputationReference"), "reference", False),
        "concatenated_value": (qn(LOGICAL_PRODUCT_NS, "ConcatenatedValue"), "element", False),
        "processing_instruction_reference": (qn(REUSABLE_NS, "ProcessingInstructionReference"), "reference", False),
        "value_representations": (qn(REUSABLE_NS, "ValueRepresentation"), "element", True),
        "value_representation_references": (qn(REUSABLE_NS, "ValueRepresentationReference"), "reference", True),
        "missing_values_reference": (qn(LOGICAL_PRODUCT_NS, "MissingValuesReference"), "reference", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
        "aggregation_method": (qn(REUSABLE_NS, "AggregationMethod"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "additivity": ("additivity", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(LOGICAL_PRODUCT_NS, "VariableRole"),
        qn(REUSABLE_NS, "WeightVariableReference"),
        qn(LOGICAL_PRODUCT_NS, "StandardWeightReference"),
        qn(LOGICAL_PRODUCT_NS, "VariableAttribute"),
        qn(LOGICAL_PRODUCT_NS, "ImputationReference"),
        qn(LOGICAL_PRODUCT_NS, "ConcatenatedValue"),
        qn(REUSABLE_NS, "ProcessingInstructionReference"),
        qn(REUSABLE_NS, "ValueRepresentation"),
        qn(REUSABLE_NS, "ValueRepresentationReference"),
        qn(LOGICAL_PRODUCT_NS, "MissingValuesReference"),
        qn(REUSABLE_NS, "ContentDateOffset"),
        qn(REUSABLE_NS, "AggregationMethod"),
    ]


@dataclass
class VariableSchemeFields(MaintainableBase):
    """Contains a set of Variables and VariableGroups. In addition to the standard name, label, and description of the Variable Scheme, may contain another VariableScheme by reference, a listing of Variables"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "VariableScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    variable_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    variables: list[Element] = field(default_factory=list)  # [0..*]
    variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    variable_groups: list[Element] = field(default_factory=list)  # [0..*]
    variable_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "VariableSchemeName"), "intl_string", True),
        "variable_scheme_references": (qn(REUSABLE_NS, "VariableSchemeReference"), "reference", True),
        "variables": (qn(LOGICAL_PRODUCT_NS, "Variable"), "element", True),
        "variable_references": (qn(REUSABLE_NS, "VariableReference"), "reference", True),
        "variable_groups": (qn(LOGICAL_PRODUCT_NS, "VariableGroup"), "element", True),
        "variable_group_references": (qn(LOGICAL_PRODUCT_NS, "VariableGroupReference"), "reference", True),
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
        qn(LOGICAL_PRODUCT_NS, "VariableSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "VariableSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "Variable"),
        qn(REUSABLE_NS, "VariableReference"),
        qn(LOGICAL_PRODUCT_NS, "VariableGroup"),
        qn(LOGICAL_PRODUCT_NS, "VariableGroupReference"),
    ]


@dataclass
class VariableFields(MaintainableBase):
    """Describes the structure of a Variable. This is the applied expression of a data item within a data set and maps to the GSIM ImplementedVariable. In addition to the standard name, label, and descriptio"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Variable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    out_parameter: Optional[Element] = None  # [0..1]
    source_parameter_reference: Optional[Reference] = None  # [0..1]
    source_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    represented_variable_reference: Optional[Reference] = None  # [0..1]
    conceptual_variable_reference: Optional[Reference] = None  # [0..1]
    weighting_process_reference: Optional[Reference] = None  # [0..1]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    question_references: list[Reference] = field(default_factory=list)  # [0..*]
    measurement_references: list[Reference] = field(default_factory=list)  # [0..*]
    embargo_reference: Optional[Reference] = None  # [0..1]
    source_unit: Optional[CodeValue] = None  # [0..1]
    analysis_unit: Optional[CodeValue] = None  # [0..1]
    unit_type_reference: Optional[Reference] = None  # [0..1]
    variable_representation: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isTemporal: Optional[bool] = None  # @attr
    isGeographic: Optional[bool] = None  # @attr
    isWeight: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(LOGICAL_PRODUCT_NS, "VariableName"), "intl_string", True),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "source_parameter_reference": (qn(REUSABLE_NS, "SourceParameterReference"), "reference", False),
        "source_variable_references": (qn(REUSABLE_NS, "SourceVariableReference"), "reference", True),
        "represented_variable_reference": (qn(REUSABLE_NS, "RepresentedVariableReference"), "reference", False),
        "conceptual_variable_reference": (qn(REUSABLE_NS, "ConceptualVariableReference"), "reference", False),
        "weighting_process_reference": (qn(LOGICAL_PRODUCT_NS, "WeightingProcessReference"), "reference", False),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "question_references": (qn(REUSABLE_NS, "QuestionReference"), "reference", True),
        "measurement_references": (qn(REUSABLE_NS, "MeasurementReference"), "reference", True),
        "embargo_reference": (qn(LOGICAL_PRODUCT_NS, "EmbargoReference"), "reference", False),
        "source_unit": (qn(LOGICAL_PRODUCT_NS, "SourceUnit"), "code_value", False),
        "analysis_unit": (qn(REUSABLE_NS, "AnalysisUnit"), "code_value", False),
        "unit_type_reference": (qn(REUSABLE_NS, "UnitTypeReference"), "reference", False),
        "variable_representation": (qn(LOGICAL_PRODUCT_NS, "VariableRepresentation"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "isTemporal": ("isTemporal", "bool"),
        "isGeographic": ("isGeographic", "bool"),
        "isWeight": ("isWeight", "bool"),
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
        qn(LOGICAL_PRODUCT_NS, "VariableName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "SourceParameterReference"),
        qn(REUSABLE_NS, "SourceVariableReference"),
        qn(REUSABLE_NS, "RepresentedVariableReference"),
        qn(REUSABLE_NS, "ConceptualVariableReference"),
        qn(LOGICAL_PRODUCT_NS, "WeightingProcessReference"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "QuestionReference"),
        qn(REUSABLE_NS, "MeasurementReference"),
        qn(LOGICAL_PRODUCT_NS, "EmbargoReference"),
        qn(LOGICAL_PRODUCT_NS, "SourceUnit"),
        qn(REUSABLE_NS, "AnalysisUnit"),
        qn(REUSABLE_NS, "UnitTypeReference"),
        qn(LOGICAL_PRODUCT_NS, "VariableRepresentation"),
    ]


@dataclass
class VariableValueReferenceFields(MaintainableBase):
    """A reference to the variable containing the record type locator and the value being used. TypeOfObject should be set to Variable."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "VariableValueReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    variable_reference: Optional[Reference] = None  # [1..1]
    related_values: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
        "related_values": (qn(LOGICAL_PRODUCT_NS, "RelatedValue"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableReference"),
        qn(LOGICAL_PRODUCT_NS, "RelatedValue"),
    ]


@dataclass
class VariablesInRecordFields(MaintainableBase):
    """Identifies the variables contained in the logical record by indicating that all variable contained in the logical product are included, inclusion of a scheme of variable to include, or listing individ"""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "VariablesInRecord")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
    variable_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    variable_used_references: list[Reference] = field(default_factory=list)  # [0..*]
    allVariablesInLogicalProduct: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_scheme_references": (qn(REUSABLE_NS, "VariableSchemeReference"), "reference", True),
        "variable_used_references": (qn(LOGICAL_PRODUCT_NS, "VariableUsedReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "allVariablesInLogicalProduct": ("allVariablesInLogicalProduct", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "VariableUsedReference"),
    ]

