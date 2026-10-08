"""AUTO-GENERATED base dataclasses for DDI 3.3 — conceptualcomponent module.

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
from ddi_l.constants import CONCEPTUAL_COMPONENT_NS, REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class ConceptGroupFields(MaintainableBase):
    """Allows for grouping of concepts; groups may have a hierarchical structure. This structure should not be used to model semantic concept hierarchies - for this purpose, use the SubclassOfReference eleme"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    type_of_concept_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    grouping_universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    grouping_concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    concept_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    isAdministrativeOnly: Optional[bool] = None  # @attr
    isConcept: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_concept_group": (qn(CONCEPTUAL_COMPONENT_NS, "TypeOfConceptGroup"), "code_value", False),
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroupName"), "intl_string", True),
        "grouping_universe_references": (qn(CONCEPTUAL_COMPONENT_NS, "GroupingUniverseReference"), "reference", True),
        "grouping_concept_reference": (qn(CONCEPTUAL_COMPONENT_NS, "GroupingConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "concept_references": (qn(REUSABLE_NS, "ConceptReference"), "reference", True),
        "concept_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroupReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "isOrdered": ("isOrdered", "bool"),
        "isAdministrativeOnly": ("isAdministrativeOnly", "bool"),
        "isConcept": ("isConcept", "bool"),
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
        qn(CONCEPTUAL_COMPONENT_NS, "TypeOfConceptGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(CONCEPTUAL_COMPONENT_NS, "GroupingUniverseReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GroupingConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroupReference"),
    ]


@dataclass
class ConceptSchemeFields(MaintainableBase):
    """A comprehensive list of the concepts measured by the data that are being documented that is maintained by an agency. In addition to the standard name, label, and description, allows for the inclusion """

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "ConceptScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    concept_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    vocabulary: Optional[Element] = None  # [0..1]
    concepts: list[Element] = field(default_factory=list)  # [0..*]
    concept_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_groups: list[Element] = field(default_factory=list)  # [0..*]
    concept_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptSchemeName"), "intl_string", True),
        "concept_scheme_references": (qn(REUSABLE_NS, "ConceptSchemeReference"), "reference", True),
        "vocabulary": (qn(CONCEPTUAL_COMPONENT_NS, "Vocabulary"), "element", False),
        "concepts": (qn(CONCEPTUAL_COMPONENT_NS, "Concept"), "element", True),
        "concept_references": (qn(REUSABLE_NS, "ConceptReference"), "reference", True),
        "concept_groups": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroup"), "element", True),
        "concept_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ConceptSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "Vocabulary"),
        qn(CONCEPTUAL_COMPONENT_NS, "Concept"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroupReference"),
    ]


@dataclass
class ConceptFields(MaintainableBase):
    """Describes a concept per ISO/IEC 11179. In addition to the standard name, label, and description, can identify similar concepts, the concept which this concept is a subclass of, a concept that is used """

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "Concept")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    similar_concepts: list[Element] = field(default_factory=list)  # [0..*]
    subclass_of_references: list[Reference] = field(default_factory=list)  # [0..*]
    excludes_concept_references: list[Reference] = field(default_factory=list)  # [0..*]
    includes_concept_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isCharacteristic: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptName"), "intl_string", True),
        "similar_concepts": (qn(CONCEPTUAL_COMPONENT_NS, "SimilarConcept"), "element", True),
        "subclass_of_references": (qn(CONCEPTUAL_COMPONENT_NS, "SubclassOfReference"), "reference", True),
        "excludes_concept_references": (qn(CONCEPTUAL_COMPONENT_NS, "ExcludesConceptReference"), "reference", True),
        "includes_concept_references": (qn(CONCEPTUAL_COMPONENT_NS, "IncludesConceptReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "isCharacteristic": ("isCharacteristic", "bool"),
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
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(CONCEPTUAL_COMPONENT_NS, "SimilarConcept"),
        qn(CONCEPTUAL_COMPONENT_NS, "SubclassOfReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "ExcludesConceptReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "IncludesConceptReference"),
    ]


@dataclass
class ConceptualComponentFields(MaintainableBase):
    """A maintainable module for the conceptual components of the study or group of studies. Conceptual components include the objects used to describe the concepts the study is examining, the universe (popu"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "ConceptualComponent")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    conceptual_component_module_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    coverage: Optional[Element] = None  # [0..1]
    concept_schemes: list[Element] = field(default_factory=list)  # [0..*]
    concept_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    universe_schemes: list[Element] = field(default_factory=list)  # [0..*]
    universe_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    conceptual_variable_schemes: list[Element] = field(default_factory=list)  # [0..*]
    conceptual_variable_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_structure_schemes: list[Element] = field(default_factory=list)  # [0..*]
    geographic_structure_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_location_schemes: list[Element] = field(default_factory=list)  # [0..*]
    geographic_location_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    unit_type_schemes: list[Element] = field(default_factory=list)  # [0..*]
    unit_type_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "conceptual_component_module_names": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualComponentModuleName"), "intl_string", True),
        "coverage": (qn(REUSABLE_NS, "Coverage"), "element", False),
        "concept_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptScheme"), "element", True),
        "concept_scheme_references": (qn(REUSABLE_NS, "ConceptSchemeReference"), "reference", True),
        "universe_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseScheme"), "element", True),
        "universe_scheme_references": (qn(REUSABLE_NS, "UniverseSchemeReference"), "reference", True),
        "conceptual_variable_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableScheme"), "element", True),
        "conceptual_variable_scheme_references": (qn(REUSABLE_NS, "ConceptualVariableSchemeReference"), "reference", True),
        "geographic_structure_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureScheme"), "element", True),
        "geographic_structure_scheme_references": (qn(REUSABLE_NS, "GeographicStructureSchemeReference"), "reference", True),
        "geographic_location_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationScheme"), "element", True),
        "geographic_location_scheme_references": (qn(REUSABLE_NS, "GeographicLocationSchemeReference"), "reference", True),
        "unit_type_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeScheme"), "element", True),
        "unit_type_scheme_references": (qn(REUSABLE_NS, "UnitTypeSchemeReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualComponentModuleName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Coverage"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptScheme"),
        qn(REUSABLE_NS, "ConceptSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseScheme"),
        qn(REUSABLE_NS, "UniverseSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableScheme"),
        qn(REUSABLE_NS, "ConceptualVariableSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureScheme"),
        qn(REUSABLE_NS, "GeographicStructureSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationScheme"),
        qn(REUSABLE_NS, "GeographicLocationSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeScheme"),
        qn(REUSABLE_NS, "UnitTypeSchemeReference"),
    ]


@dataclass
class ConceptualVariableGroupFields(MaintainableBase):
    """Contains a group of ConceptualVariables, which may describe an ordered or hierarchical relationship structure. ConceptualVariables may be grouped for a wide range of reasons including conceptual or un"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    type_of_conceptual_variable_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    conceptual_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    conceptual_variable_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_conceptual_variable_group": (qn(CONCEPTUAL_COMPONENT_NS, "TypeOfConceptualVariableGroup"), "code_value", False),
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "conceptual_variable_references": (qn(REUSABLE_NS, "ConceptualVariableReference"), "reference", True),
        "conceptual_variable_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "TypeOfConceptualVariableGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "ConceptualVariableReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroupReference"),
    ]


@dataclass
class ConceptualVariableSchemeFields(MaintainableBase):
    """A comprehensive list of the ConceptualVariables measured by the data that are being documented and/or maintained by an agency. In addition to the standard name, label, and description, allows for the """

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    conceptual_variable_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    conceptual_variables: list[Element] = field(default_factory=list)  # [0..*]
    conceptual_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    conceptual_variable_groups: list[Element] = field(default_factory=list)  # [0..*]
    conceptual_variable_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableSchemeName"), "intl_string", True),
        "conceptual_variable_scheme_references": (qn(REUSABLE_NS, "ConceptualVariableSchemeReference"), "reference", True),
        "conceptual_variables": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariable"), "element", True),
        "conceptual_variable_references": (qn(REUSABLE_NS, "ConceptualVariableReference"), "reference", True),
        "conceptual_variable_groups": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroup"), "element", True),
        "conceptual_variable_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ConceptualVariableSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariable"),
        qn(REUSABLE_NS, "ConceptualVariableReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroupReference"),
    ]


@dataclass
class ConceptualVariableFields(MaintainableBase):
    """Describes a ConceptualVariable which provides the link between a concept to a specific unit type (object) that defines this as a ConceptualVariable. In addition to the standard name, label, and descri"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    unit_type_reference: Optional[Reference] = None  # [0..1]
    category_scheme_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableName"), "intl_string", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "unit_type_reference": (qn(REUSABLE_NS, "UnitTypeReference"), "reference", False),
        "category_scheme_reference": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", False),
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
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "UnitTypeReference"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
    ]


@dataclass
class GeographicLocationGroupFields(MaintainableBase):
    """Contains a group of GeographicLocations, which may describe an ordered or hierarchical relationship structure. Specifies the purpose of the group, a name, label, and description of the group, its rela"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    type_of_geographic_location_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    geographic_location_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_location_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_geographic_location_group": (qn(CONCEPTUAL_COMPONENT_NS, "TypeOfGeographicLocationGroup"), "code_value", False),
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "geographic_location_references": (qn(REUSABLE_NS, "GeographicLocationReference"), "reference", True),
        "geographic_location_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "TypeOfGeographicLocationGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "GeographicLocationReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroupReference"),
    ]


@dataclass
class GeographicLocationSchemeFields(MaintainableBase):
    """A Scheme containing a set of geographic locations, each for a single Geography type, e.g., States, OR Counties, OR Countries, etc. The geographic location element has to be repeated for each geography"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    geographic_location_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_locations: list[Element] = field(default_factory=list)  # [0..*]
    geographic_location_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_location_groups: list[Element] = field(default_factory=list)  # [0..*]
    geographic_location_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationSchemeName"), "intl_string", True),
        "geographic_location_scheme_references": (qn(REUSABLE_NS, "GeographicLocationSchemeReference"), "reference", True),
        "geographic_locations": (qn(REUSABLE_NS, "GeographicLocation"), "element", True),
        "geographic_location_references": (qn(REUSABLE_NS, "GeographicLocationReference"), "reference", True),
        "geographic_location_groups": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroup"), "element", True),
        "geographic_location_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "GeographicLocationSchemeReference"),
        qn(REUSABLE_NS, "GeographicLocation"),
        qn(REUSABLE_NS, "GeographicLocationReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroupReference"),
    ]


@dataclass
class GeographicStructureGroupFields(MaintainableBase):
    """Contains a group of GeographicStructures, which may describe an ordered or hierarchical relationship structure. Specifies the purpose of the group, a name, label, and description of the group, its rel"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    type_of_geographic_structure_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    geographic_structure_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_structure_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_geographic_structure_group": (qn(CONCEPTUAL_COMPONENT_NS, "TypeOfGeographicStructureGroup"), "code_value", False),
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "geographic_structure_references": (qn(REUSABLE_NS, "GeographicStructureReference"), "reference", True),
        "geographic_structure_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "TypeOfGeographicStructureGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "GeographicStructureReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroupReference"),
    ]


@dataclass
class GeographicStructureSchemeFields(MaintainableBase):
    """Contains information on the hierarchy of the geographic structure. In addition to the standard name, label, and description identifies one or more AuthorizedSources for the level codes/descriptions pr"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    geographic_structure_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_structures: list[Element] = field(default_factory=list)  # [0..*]
    geographic_structure_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_structure_groups: list[Element] = field(default_factory=list)  # [0..*]
    geographic_structure_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureSchemeName"), "intl_string", True),
        "geographic_structure_scheme_references": (qn(REUSABLE_NS, "GeographicStructureSchemeReference"), "reference", True),
        "geographic_structures": (qn(REUSABLE_NS, "GeographicStructure"), "element", True),
        "geographic_structure_references": (qn(REUSABLE_NS, "GeographicStructureReference"), "reference", True),
        "geographic_structure_groups": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroup"), "element", True),
        "geographic_structure_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "GeographicStructureSchemeReference"),
        qn(REUSABLE_NS, "GeographicStructure"),
        qn(REUSABLE_NS, "GeographicStructureReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroupReference"),
    ]


@dataclass
class SimilarConceptFields(MaintainableBase):
    """A reference to a concept with similar meaning and a description of their differences. Formal comparison is done using a ConceptMap. The similar concept structure allows specification of similar concep"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "SimilarConcept")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    similar_concept_reference: Optional[Reference] = None  # [1..1]
    difference: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "similar_concept_reference": (qn(CONCEPTUAL_COMPONENT_NS, "SimilarConceptReference"), "reference", False),
        "difference": (qn(REUSABLE_NS, "Difference"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(CONCEPTUAL_COMPONENT_NS, "SimilarConceptReference"),
        qn(REUSABLE_NS, "Difference"),
    ]


@dataclass
class SubUniverseClassFields(MaintainableBase):
    """A sub-universe group provides a definition to the universes contained within it. For example the Sub-Universe Group of Gender for the Universe Resident Population may contain the Universe Males and th"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClass")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    defining_concept_reference: Optional[Reference] = None  # [0..1]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    sub_universe_class_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClassName"), "intl_string", True),
        "defining_concept_reference": (qn(REUSABLE_NS, "DefiningConceptReference"), "reference", False),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "sub_universe_class_references": (qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClassReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClassName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "DefiningConceptReference"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClassReference"),
    ]


@dataclass
class UnitTypeGroupFields(MaintainableBase):
    """Contains a group of UnitTypes, which may describe an ordered or hierarchical relationship structure. Specifies the purpose of the group, a name, label, and description of the group, its relationship t"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    type_of_unit_type_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    unit_type_references: list[Reference] = field(default_factory=list)  # [0..*]
    unit_type_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_unit_type_group": (qn(CONCEPTUAL_COMPONENT_NS, "TypeOfUnitTypeGroup"), "code_value", False),
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "unit_type_references": (qn(REUSABLE_NS, "UnitTypeReference"), "reference", True),
        "unit_type_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "TypeOfUnitTypeGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "UnitTypeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroupReference"),
    ]


@dataclass
class UnitTypeSchemeFields(MaintainableBase):
    """This scheme contains a set of Unit Types referenced by the metadata at different points in the lifecycle. In addition to the name, label, and description of the scheme, the structure supports the incl"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    unit_type_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    unit_types: list[Element] = field(default_factory=list)  # [0..*]
    unit_type_references: list[Reference] = field(default_factory=list)  # [0..*]
    unit_type_groups: list[Element] = field(default_factory=list)  # [0..*]
    unit_type_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeSchemeName"), "intl_string", True),
        "unit_type_scheme_references": (qn(REUSABLE_NS, "UnitTypeSchemeReference"), "reference", True),
        "unit_types": (qn(CONCEPTUAL_COMPONENT_NS, "UnitType"), "element", True),
        "unit_type_references": (qn(REUSABLE_NS, "UnitTypeReference"), "reference", True),
        "unit_type_groups": (qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroup"), "element", True),
        "unit_type_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UnitTypeSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "UnitType"),
        qn(REUSABLE_NS, "UnitTypeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroupReference"),
    ]


@dataclass
class UnitTypeFields(MaintainableBase):
    """A Unit Type is a class of objects of interest. A Unit Type is used to describe a class or group of Units based on a single characteristic with no specification of time and geography. For example, the """

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "UnitType")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [1..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "Name"), "intl_string", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
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
        qn(REUSABLE_NS, "ConceptReference"),
    ]


@dataclass
class UniverseGroupFields(MaintainableBase):
    """Contains a group of Universes, which may describe an ordered or hierarchical relationship structure. Specifies the purpose of the group, a name, label, and description of the group, its relationship t"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    type_of_universe_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    grouping_universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    grouping_concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    universe_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_universe_group": (qn(CONCEPTUAL_COMPONENT_NS, "TypeOfUniverseGroup"), "code_value", False),
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroupName"), "intl_string", True),
        "grouping_universe_references": (qn(CONCEPTUAL_COMPONENT_NS, "GroupingUniverseReference"), "reference", True),
        "grouping_concept_reference": (qn(CONCEPTUAL_COMPONENT_NS, "GroupingConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "universe_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "TypeOfUniverseGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(CONCEPTUAL_COMPONENT_NS, "GroupingUniverseReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GroupingConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroupReference"),
    ]


@dataclass
class UniverseSchemeFields(MaintainableBase):
    """Contains a set of Universe descriptions that may be organized into sub-universe structures. A Universe may also be known as a population. A Universe describes the "object" of a Data Element Concept or"""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "UniverseScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    universes: list[Element] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    universe_groups: list[Element] = field(default_factory=list)  # [0..*]
    universe_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseSchemeName"), "intl_string", True),
        "universe_scheme_references": (qn(REUSABLE_NS, "UniverseSchemeReference"), "reference", True),
        "universes": (qn(CONCEPTUAL_COMPONENT_NS, "Universe"), "element", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "universe_groups": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroup"), "element", True),
        "universe_group_references": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroupReference"), "reference", True),
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
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "Universe"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroupReference"),
    ]


@dataclass
class UniverseFields(MaintainableBase):
    """A Universe contextualizes a Unit Type by providing additional restriction characteristics. The class Universe covers both the GSIM 1.2 obects of Universe and Population, conflating them into a single """

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "Universe")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    defining_concept_reference: Optional[Reference] = None  # [0..1]
    unit_type_reference: Optional[Reference] = None  # [0..1]
    type_of_unit: Optional[CodeValue] = None  # [0..1]
    location_value_references: list[Reference] = field(default_factory=list)  # [0..*]
    geography_of_universe: Optional[Element] = None  # [0..1]
    time_periods: list[Element] = field(default_factory=list)  # [0..*]
    universe_generation_codes: list[Element] = field(default_factory=list)  # [0..*]
    sub_universe_class: list[Element] = field(default_factory=list)  # [0..*]
    sub_universe_class_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isInclusive: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseName"), "intl_string", True),
        "defining_concept_reference": (qn(REUSABLE_NS, "DefiningConceptReference"), "reference", False),
        "unit_type_reference": (qn(REUSABLE_NS, "UnitTypeReference"), "reference", False),
        "type_of_unit": (qn(CONCEPTUAL_COMPONENT_NS, "TypeOfUnit"), "code_value", False),
        "location_value_references": (qn(REUSABLE_NS, "LocationValueReference"), "reference", True),
        "geography_of_universe": (qn(CONCEPTUAL_COMPONENT_NS, "GeographyOfUniverse"), "element", False),
        "time_periods": (qn(CONCEPTUAL_COMPONENT_NS, "TimePeriod"), "element", True),
        "universe_generation_codes": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseGenerationCode"), "element", True),
        "sub_universe_class": (qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClass"), "element", True),
        "sub_universe_class_references": (qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClassReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "isInclusive": ("isInclusive", "bool"),
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
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "DefiningConceptReference"),
        qn(REUSABLE_NS, "UnitTypeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "TypeOfUnit"),
        qn(REUSABLE_NS, "LocationValueReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographyOfUniverse"),
        qn(CONCEPTUAL_COMPONENT_NS, "TimePeriod"),
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseGenerationCode"),
        qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClass"),
        qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClassReference"),
    ]


@dataclass
class VocabularyFields(MaintainableBase):
    """Provides information about the vocabulary used to create a concept scheme."""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "Vocabulary")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
    vocabulary_title: Optional[Element] = None  # [0..1]
    abbreviations: list[Element] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    uri: Optional[str] = None  # [0..1]
    xml_uri: Optional[str] = None  # [0..1]
    scheme: Optional[str] = None  # [0..1]
    scheme_uri: Optional[str] = None  # [0..1]
    comments: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "vocabulary_title": (qn(CONCEPTUAL_COMPONENT_NS, "VocabularyTitle"), "element", False),
        "abbreviations": (qn(REUSABLE_NS, "Abbreviation"), "element", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "uri": (qn(REUSABLE_NS, "URI"), "str", False),
        "xml_uri": (qn(CONCEPTUAL_COMPONENT_NS, "XML-URI"), "str", False),
        "scheme": (qn(CONCEPTUAL_COMPONENT_NS, "Scheme"), "str", False),
        "scheme_uri": (qn(CONCEPTUAL_COMPONENT_NS, "SchemeURI"), "str", False),
        "comments": (qn(CONCEPTUAL_COMPONENT_NS, "Comments"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(CONCEPTUAL_COMPONENT_NS, "VocabularyTitle"),
        qn(REUSABLE_NS, "Abbreviation"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "URI"),
        qn(CONCEPTUAL_COMPONENT_NS, "XML-URI"),
        qn(CONCEPTUAL_COMPONENT_NS, "Scheme"),
        qn(CONCEPTUAL_COMPONENT_NS, "SchemeURI"),
        qn(CONCEPTUAL_COMPONENT_NS, "Comments"),
    ]

