"""AUTO-GENERATED base dataclasses for DDI 3.3 — studyunit module.

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
from ddi_l.models.base import CodeValue, MaintainableBase, Reference
from ddi_l.constants import ARCHIVE_NS, CONCEPTUAL_COMPONENT_NS, DATA_COLLECTION_NS, DDI_PROFILE_NS, LOGICAL_PRODUCT_NS, PHYSICAL_DATA_PRODUCT_NS, PHYSICAL_INSTANCE_NS, REUSABLE_NS, STUDY_UNIT_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class StudyUnitFields(MaintainableBase):
    """A primary packaging and publication module within DDI representing the purpose, background, development, data capture, and data products related to a study. In DDI a study is defined as a single coord"""

    TAG: ClassVar[str] = qn(STUDY_UNIT_NS, "StudyUnit")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("s")
    type_of_study_unit: Optional[CodeValue] = None  # [0..1]
    citation: Optional[Element] = None  # [0..1]
    abstract: Optional[Element] = None  # [0..1]
    authorization_sources: list[Element] = field(default_factory=list)  # [0..*]
    approval_review: Optional[Element] = None  # [1..1]
    approval_review_reference: Optional[Reference] = None  # [1..1]
    defining_concept_reference: Optional[Reference] = None  # [0..1]
    universe_reference: Optional[Reference] = None  # [0..1]
    series_statements: list[Element] = field(default_factory=list)  # [0..*]
    information_classifications: list[Element] = field(default_factory=list)  # [0..*]
    information_classification_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_statement_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_schemes: list[Element] = field(default_factory=list)  # [0..*]
    quality_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    ex_post_evaluations: list[Element] = field(default_factory=list)  # [0..*]
    funding_informations: list[Element] = field(default_factory=list)  # [0..*]
    study_budgets: list[Element] = field(default_factory=list)  # [0..*]
    purpose: Optional[Element] = None  # [0..1]
    coverage: Optional[Element] = None  # [0..1]
    analysis_units: list[CodeValue] = field(default_factory=list)  # [0..*]
    analysis_units_covered: Optional[Element] = None  # [0..1]
    kind_of_datas: list[Element] = field(default_factory=list)  # [0..*]
    general_data_formats: list[CodeValue] = field(default_factory=list)  # [0..*]
    required_resource_packages: Optional[Element] = None  # [0..1]
    embargos: list[Element] = field(default_factory=list)  # [0..*]
    other_material_schemes: list[Element] = field(default_factory=list)  # [0..*]
    other_material_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    conceptual_components: list[Element] = field(default_factory=list)  # [0..*]
    conceptual_component_references: list[Reference] = field(default_factory=list)  # [0..*]
    data_collections: list[Element] = field(default_factory=list)  # [0..*]
    data_collection_references: list[Reference] = field(default_factory=list)  # [0..*]
    base_logical_products: list[Element] = field(default_factory=list)  # [0..*]
    logical_product_references: list[Reference] = field(default_factory=list)  # [0..*]
    physical_data_products: list[Element] = field(default_factory=list)  # [0..*]
    physical_data_product_references: list[Reference] = field(default_factory=list)  # [0..*]
    physical_instances: list[Element] = field(default_factory=list)  # [0..*]
    physical_instance_references: list[Reference] = field(default_factory=list)  # [0..*]
    physical_instance_groups: list[Element] = field(default_factory=list)  # [0..*]
    physical_instance_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    archives: list[Element] = field(default_factory=list)  # [0..*]
    archive_references: list[Reference] = field(default_factory=list)  # [0..*]
    classification_families: list[Element] = field(default_factory=list)  # [0..*]
    classification_family_references: list[Reference] = field(default_factory=list)  # [0..*]
    ddi_profiles: list[Element] = field(default_factory=list)  # [0..*]
    ddi_profile_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_study_unit": (qn(STUDY_UNIT_NS, "TypeOfStudyUnit"), "code_value", False),
        "citation": (qn(REUSABLE_NS, "Citation"), "element", False),
        "abstract": (qn(REUSABLE_NS, "Abstract"), "element", False),
        "authorization_sources": (qn(REUSABLE_NS, "AuthorizationSource"), "element", True),
        "approval_review": (qn(REUSABLE_NS, "ApprovalReview"), "element", False),
        "approval_review_reference": (qn(REUSABLE_NS, "ApprovalReviewReference"), "reference", False),
        "defining_concept_reference": (qn(REUSABLE_NS, "DefiningConceptReference"), "reference", False),
        "universe_reference": (qn(REUSABLE_NS, "UniverseReference"), "reference", False),
        "series_statements": (qn(REUSABLE_NS, "SeriesStatement"), "element", True),
        "information_classifications": (qn(REUSABLE_NS, "InformationClassification"), "element", True),
        "information_classification_references": (qn(REUSABLE_NS, "InformationClassificationReference"), "reference", True),
        "quality_statement_references": (qn(REUSABLE_NS, "QualityStatementReference"), "reference", True),
        "quality_schemes": (qn(REUSABLE_NS, "QualityScheme"), "element", True),
        "quality_scheme_references": (qn(REUSABLE_NS, "QualitySchemeReference"), "reference", True),
        "ex_post_evaluations": (qn(REUSABLE_NS, "ExPostEvaluation"), "element", True),
        "funding_informations": (qn(REUSABLE_NS, "FundingInformation"), "element", True),
        "study_budgets": (qn(STUDY_UNIT_NS, "StudyBudget"), "element", True),
        "purpose": (qn(REUSABLE_NS, "Purpose"), "element", False),
        "coverage": (qn(REUSABLE_NS, "Coverage"), "element", False),
        "analysis_units": (qn(REUSABLE_NS, "AnalysisUnit"), "code_value", True),
        "analysis_units_covered": (qn(REUSABLE_NS, "AnalysisUnitsCovered"), "element", False),
        "kind_of_datas": (qn(REUSABLE_NS, "KindOfData"), "element", True),
        "general_data_formats": (qn(REUSABLE_NS, "GeneralDataFormat"), "code_value", True),
        "required_resource_packages": (qn(REUSABLE_NS, "RequiredResourcePackages"), "element", False),
        "embargos": (qn(REUSABLE_NS, "Embargo"), "element", True),
        "other_material_schemes": (qn(REUSABLE_NS, "OtherMaterialScheme"), "element", True),
        "other_material_scheme_references": (qn(REUSABLE_NS, "OtherMaterialSchemeReference"), "reference", True),
        "conceptual_components": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualComponent"), "element", True),
        "conceptual_component_references": (qn(REUSABLE_NS, "ConceptualComponentReference"), "reference", True),
        "data_collections": (qn(DATA_COLLECTION_NS, "DataCollection"), "element", True),
        "data_collection_references": (qn(REUSABLE_NS, "DataCollectionReference"), "reference", True),
        "base_logical_products": (qn(LOGICAL_PRODUCT_NS, "BaseLogicalProduct"), "element", True),
        "logical_product_references": (qn(REUSABLE_NS, "LogicalProductReference"), "reference", True),
        "physical_data_products": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProduct"), "element", True),
        "physical_data_product_references": (qn(REUSABLE_NS, "PhysicalDataProductReference"), "reference", True),
        "physical_instances": (qn(PHYSICAL_INSTANCE_NS, "PhysicalInstance"), "element", True),
        "physical_instance_references": (qn(REUSABLE_NS, "PhysicalInstanceReference"), "reference", True),
        "physical_instance_groups": (qn(PHYSICAL_INSTANCE_NS, "PhysicalInstanceGroup"), "element", True),
        "physical_instance_group_references": (qn(REUSABLE_NS, "PhysicalInstanceGroupReference"), "reference", True),
        "archives": (qn(ARCHIVE_NS, "Archive"), "element", True),
        "archive_references": (qn(REUSABLE_NS, "ArchiveReference"), "reference", True),
        "classification_families": (qn(LOGICAL_PRODUCT_NS, "ClassificationFamily"), "element", True),
        "classification_family_references": (qn(REUSABLE_NS, "ClassificationFamilyReference"), "reference", True),
        "ddi_profiles": (qn(DDI_PROFILE_NS, "DDIProfile"), "element", True),
        "ddi_profile_references": (qn(REUSABLE_NS, "DDIProfileReference"), "reference", True),
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
        qn(STUDY_UNIT_NS, "TypeOfStudyUnit"),
        qn(REUSABLE_NS, "Citation"),
        qn(REUSABLE_NS, "Abstract"),
        qn(REUSABLE_NS, "AuthorizationSource"),
        qn(REUSABLE_NS, "ApprovalReview"),
        qn(REUSABLE_NS, "ApprovalReviewReference"),
        qn(REUSABLE_NS, "DefiningConceptReference"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "SeriesStatement"),
        qn(REUSABLE_NS, "InformationClassification"),
        qn(REUSABLE_NS, "InformationClassificationReference"),
        qn(REUSABLE_NS, "QualityStatementReference"),
        qn(REUSABLE_NS, "QualityScheme"),
        qn(REUSABLE_NS, "QualitySchemeReference"),
        qn(REUSABLE_NS, "ExPostEvaluation"),
        qn(REUSABLE_NS, "FundingInformation"),
        qn(STUDY_UNIT_NS, "StudyBudget"),
        qn(REUSABLE_NS, "Purpose"),
        qn(REUSABLE_NS, "Coverage"),
        qn(REUSABLE_NS, "AnalysisUnit"),
        qn(REUSABLE_NS, "AnalysisUnitsCovered"),
        qn(REUSABLE_NS, "KindOfData"),
        qn(REUSABLE_NS, "GeneralDataFormat"),
        qn(REUSABLE_NS, "RequiredResourcePackages"),
        qn(REUSABLE_NS, "Embargo"),
        qn(REUSABLE_NS, "OtherMaterialScheme"),
        qn(REUSABLE_NS, "OtherMaterialSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualComponent"),
        qn(REUSABLE_NS, "ConceptualComponentReference"),
        qn(DATA_COLLECTION_NS, "DataCollection"),
        qn(REUSABLE_NS, "DataCollectionReference"),
        qn(LOGICAL_PRODUCT_NS, "BaseLogicalProduct"),
        qn(REUSABLE_NS, "LogicalProductReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProduct"),
        qn(REUSABLE_NS, "PhysicalDataProductReference"),
        qn(PHYSICAL_INSTANCE_NS, "PhysicalInstance"),
        qn(REUSABLE_NS, "PhysicalInstanceReference"),
        qn(PHYSICAL_INSTANCE_NS, "PhysicalInstanceGroup"),
        qn(REUSABLE_NS, "PhysicalInstanceGroupReference"),
        qn(ARCHIVE_NS, "Archive"),
        qn(REUSABLE_NS, "ArchiveReference"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationFamily"),
        qn(REUSABLE_NS, "ClassificationFamilyReference"),
        qn(DDI_PROFILE_NS, "DDIProfile"),
        qn(REUSABLE_NS, "DDIProfileReference"),
    ]

