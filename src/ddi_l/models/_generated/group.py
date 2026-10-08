"""AUTO-GENERATED base dataclasses for DDI 3.3 — group module.

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
from ddi_l.constants import ARCHIVE_NS, COMPARATIVE_NS, CONCEPTUAL_COMPONENT_NS, DATA_COLLECTION_NS, DDI_PROFILE_NS, GROUP_NS, LOGICAL_PRODUCT_NS, PHYSICAL_DATA_PRODUCT_NS, PHYSICAL_INSTANCE_NS, REUSABLE_NS, STUDY_UNIT_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class ContentLinkingMapFields(MaintainableBase):
    """Contains a stack of links from the LocalAddedContent to the Depository content and provides instructions regarding the relationship between the local added content and the deposited content."""

    TAG: ClassVar[str] = qn(GROUP_NS, "ContentLinkingMap")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("g")
    linking_maps: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "linking_maps": (qn(GROUP_NS, "LinkingMap"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(GROUP_NS, "LinkingMap"),
    ]


@dataclass
class GroupFields(MaintainableBase):
    """A primary packaging and publication module within DDI containing a Group of StudyUnits. The Group structure allows metadata regarding multiple study units to be published as a structured entity. Studi"""

    TAG: ClassVar[str] = qn(GROUP_NS, "Group")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("g")
    type_of_group: Optional[CodeValue] = None  # [0..1]
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
    project_budgets: list[Element] = field(default_factory=list)  # [0..*]
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
    comparisons: list[Element] = field(default_factory=list)  # [0..*]
    comparison_references: list[Reference] = field(default_factory=list)  # [0..*]
    study_units: list[Element] = field(default_factory=list)  # [0..*]
    study_unit_references: list[Reference] = field(default_factory=list)  # [0..*]
    groups: list[Element] = field(default_factory=list)  # [0..*]
    group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    time: Optional[str] = None  # @attr
    captureInstrument: Optional[str] = None  # @attr
    panel: Optional[str] = None  # @attr
    geography: Optional[str] = None  # @attr
    dataProduct: Optional[str] = None  # @attr
    languageRelationship: Optional[str] = None  # @attr
    userDefinedGroupProperty: Optional[str] = None  # @attr
    userDefinedGroupPropertyValue: Optional[str] = None  # @attr
    isInheritable: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_group": (qn(GROUP_NS, "TypeOfGroup"), "code_value", False),
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
        "project_budgets": (qn(GROUP_NS, "ProjectBudget"), "element", True),
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
        "comparisons": (qn(COMPARATIVE_NS, "Comparison"), "element", True),
        "comparison_references": (qn(REUSABLE_NS, "ComparisonReference"), "reference", True),
        "study_units": (qn(STUDY_UNIT_NS, "StudyUnit"), "element", True),
        "study_unit_references": (qn(REUSABLE_NS, "StudyUnitReference"), "reference", True),
        "groups": (qn(GROUP_NS, "Group"), "element", True),
        "group_references": (qn(REUSABLE_NS, "GroupReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "lang": ("lang", "str"),
        "time": ("time", "str"),
        "captureInstrument": ("captureInstrument", "str"),
        "panel": ("panel", "str"),
        "geography": ("geography", "str"),
        "dataProduct": ("dataProduct", "str"),
        "languageRelationship": ("languageRelationship", "str"),
        "userDefinedGroupProperty": ("userDefinedGroupProperty", "str"),
        "userDefinedGroupPropertyValue": ("userDefinedGroupPropertyValue", "str"),
        "isInheritable": ("isInheritable", "bool"),
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
        qn(GROUP_NS, "TypeOfGroup"),
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
        qn(GROUP_NS, "ProjectBudget"),
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
        qn(COMPARATIVE_NS, "Comparison"),
        qn(REUSABLE_NS, "ComparisonReference"),
        qn(STUDY_UNIT_NS, "StudyUnit"),
        qn(REUSABLE_NS, "StudyUnitReference"),
        qn(GROUP_NS, "Group"),
        qn(REUSABLE_NS, "GroupReference"),
    ]


@dataclass
class LinkingMapFields(MaintainableBase):
    """Provides a link from a local object to a deposited object via reference and designates if the added material should Override, act as AddedContent, or DeleteContent in the original deposited material. """

    TAG: ClassVar[str] = qn(GROUP_NS, "LinkingMap")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("g")
    local_object_reference: Optional[Reference] = None  # [0..1]
    depository_object_reference: Optional[Reference] = None  # [1..1]
    relationship_action: Optional[CodeValue] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "local_object_reference": (qn(GROUP_NS, "LocalObjectReference"), "reference", False),
        "depository_object_reference": (qn(GROUP_NS, "DepositoryObjectReference"), "reference", False),
        "relationship_action": (qn(GROUP_NS, "RelationshipAction"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(GROUP_NS, "LocalObjectReference"),
        qn(GROUP_NS, "DepositoryObjectReference"),
        qn(GROUP_NS, "RelationshipAction"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class LocalAddedContentFields(MaintainableBase):
    """Allows a depository to provide locally created value added material and processing information in the appropriate packaging structure and to designate the relationship of added material to the origina"""

    TAG: ClassVar[str] = qn(GROUP_NS, "LocalAddedContent")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("g")
    content_linking_map: Optional[Element] = None  # [1..1]
    local_study_unit_contents: list[Element] = field(default_factory=list)  # [0..*]
    local_study_unit_content_references: list[Reference] = field(default_factory=list)  # [0..*]
    local_group_contents: list[Element] = field(default_factory=list)  # [0..*]
    local_group_content_references: list[Reference] = field(default_factory=list)  # [0..*]
    local_resource_package_contents: list[Element] = field(default_factory=list)  # [0..*]
    local_resource_package_content_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "content_linking_map": (qn(GROUP_NS, "ContentLinkingMap"), "element", False),
        "local_study_unit_contents": (qn(GROUP_NS, "LocalStudyUnitContent"), "element", True),
        "local_study_unit_content_references": (qn(GROUP_NS, "LocalStudyUnitContentReference"), "reference", True),
        "local_group_contents": (qn(GROUP_NS, "LocalGroupContent"), "element", True),
        "local_group_content_references": (qn(GROUP_NS, "LocalGroupContentReference"), "reference", True),
        "local_resource_package_contents": (qn(GROUP_NS, "LocalResourcePackageContent"), "element", True),
        "local_resource_package_content_references": (qn(GROUP_NS, "LocalResourcePackageContentReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(GROUP_NS, "ContentLinkingMap"),
        qn(GROUP_NS, "LocalStudyUnitContent"),
        qn(GROUP_NS, "LocalStudyUnitContentReference"),
        qn(GROUP_NS, "LocalGroupContent"),
        qn(GROUP_NS, "LocalGroupContentReference"),
        qn(GROUP_NS, "LocalResourcePackageContent"),
        qn(GROUP_NS, "LocalResourcePackageContentReference"),
    ]


@dataclass
class LocalHoldingPackageFields(MaintainableBase):
    """Allows a depository to hold the contents of a DDI StudyUnit, Group, or ResourcePackage as received while providing locally created value added material and processing information without having to alt"""

    TAG: ClassVar[str] = qn(GROUP_NS, "LocalHoldingPackage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("g")
    depository_study_unit_references: list[Reference] = field(default_factory=list)  # [0..*]
    depository_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    depository_resource_package_references: list[Reference] = field(default_factory=list)  # [0..*]
    defining_concept_reference: Optional[Reference] = None  # [0..1]
    local_added_content: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "depository_study_unit_references": (qn(GROUP_NS, "DepositoryStudyUnitReference"), "reference", True),
        "depository_group_references": (qn(GROUP_NS, "DepositoryGroupReference"), "reference", True),
        "depository_resource_package_references": (qn(GROUP_NS, "DepositoryResourcePackageReference"), "reference", True),
        "defining_concept_reference": (qn(REUSABLE_NS, "DefiningConceptReference"), "reference", False),
        "local_added_content": (qn(GROUP_NS, "LocalAddedContent"), "element", False),
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
        qn(GROUP_NS, "DepositoryStudyUnitReference"),
        qn(GROUP_NS, "DepositoryGroupReference"),
        qn(GROUP_NS, "DepositoryResourcePackageReference"),
        qn(REUSABLE_NS, "DefiningConceptReference"),
        qn(GROUP_NS, "LocalAddedContent"),
    ]


@dataclass
class ResourcePackageArchiveFields(MaintainableBase):
    """This is archive information specific to the creation, maintenance, and archiving of the ResourcePackage provided either in-line or by reference. This packaging element differentiates this "Archive" fr"""

    TAG: ClassVar[str] = qn(GROUP_NS, "ResourcePackageArchive")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("g")
    archives: list[Element] = field(default_factory=list)  # [0..*]
    archive_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "archives": (qn(ARCHIVE_NS, "Archive"), "element", True),
        "archive_references": (qn(REUSABLE_NS, "ArchiveReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "Archive"),
        qn(REUSABLE_NS, "ArchiveReference"),
    ]


@dataclass
class ResourcePackageFields(MaintainableBase):
    """The Resource Package is a specialized structure which is intended to hold reusable metadata outside of the structures of a single StudyUnit or Group. For example this may be common methodological appr"""

    TAG: ClassVar[str] = qn(GROUP_NS, "ResourcePackage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("g")
    citation: Optional[Element] = None  # [0..1]
    type_of_resource_package: Optional[CodeValue] = None  # [0..1]
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
    funding_informations: list[Element] = field(default_factory=list)  # [0..*]
    project_budgets: list[Element] = field(default_factory=list)  # [0..*]
    purpose: Optional[Element] = None  # [0..1]
    coverage: Optional[Element] = None  # [0..1]
    embargos: list[Element] = field(default_factory=list)  # [0..*]
    other_material_schemes: list[Element] = field(default_factory=list)  # [0..*]
    other_material_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    resource_package_archives: list[Element] = field(default_factory=list)  # [0..*]
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
    ddi_profiles: list[Element] = field(default_factory=list)  # [0..*]
    ddi_profile_references: list[Reference] = field(default_factory=list)  # [0..*]
    comparisons: list[Element] = field(default_factory=list)  # [0..*]
    comparison_references: list[Reference] = field(default_factory=list)  # [0..*]
    classification_families: list[Element] = field(default_factory=list)  # [0..*]
    classification_family_references: list[Reference] = field(default_factory=list)  # [0..*]
    classification_correspondence_tables: list[Element] = field(default_factory=list)  # [0..*]
    classification_correspondence_table_references: list[Reference] = field(default_factory=list)  # [0..*]
    organization_schemes: list[Element] = field(default_factory=list)  # [0..*]
    organization_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_schemes: list[Element] = field(default_factory=list)  # [0..*]
    concept_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    universe_schemes: list[Element] = field(default_factory=list)  # [0..*]
    universe_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    conceptual_variable_schemes: list[Element] = field(default_factory=list)  # [0..*]
    conceptual_variable_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    represented_variable_schemes: list[Element] = field(default_factory=list)  # [0..*]
    represented_variable_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_structure_schemes: list[Element] = field(default_factory=list)  # [0..*]
    geographic_structure_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_location_schemes: list[Element] = field(default_factory=list)  # [0..*]
    geographic_location_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    interviewer_instruction_schemes: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    control_construct_schemes: list[Element] = field(default_factory=list)  # [0..*]
    control_construct_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_schemes: list[Element] = field(default_factory=list)  # [0..*]
    question_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    measurement_schemes: list[Element] = field(default_factory=list)  # [0..*]
    measurement_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    category_schemes: list[Element] = field(default_factory=list)  # [0..*]
    category_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    code_list_schemes: list[Element] = field(default_factory=list)  # [0..*]
    code_list_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    n_cube_schemes: list[Element] = field(default_factory=list)  # [0..*]
    n_cube_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    variable_schemes: list[Element] = field(default_factory=list)  # [0..*]
    variable_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    physical_structure_schemes: list[Element] = field(default_factory=list)  # [0..*]
    physical_structure_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    record_layout_schemes: list[Element] = field(default_factory=list)  # [0..*]
    record_layout_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_schemes: list[Element] = field(default_factory=list)  # [0..*]
    quality_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    instrument_schemes: list[Element] = field(default_factory=list)  # [0..*]
    instrument_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    processing_event_schemes: list[Element] = field(default_factory=list)  # [0..*]
    processing_event_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    processing_instruction_schemes: list[Element] = field(default_factory=list)  # [0..*]
    processing_instruction_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    managed_representation_schemes: list[Element] = field(default_factory=list)  # [0..*]
    managed_representation_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    unit_type_schemes: list[Element] = field(default_factory=list)  # [0..*]
    unit_type_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    sampling_information_schemes: list[Element] = field(default_factory=list)  # [0..*]
    sampling_information_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_activity_schemes: list[Element] = field(default_factory=list)  # [0..*]
    development_activity_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "citation": (qn(REUSABLE_NS, "Citation"), "element", False),
        "type_of_resource_package": (qn(GROUP_NS, "TypeOfResourcePackage"), "code_value", False),
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
        "funding_informations": (qn(REUSABLE_NS, "FundingInformation"), "element", True),
        "project_budgets": (qn(GROUP_NS, "ProjectBudget"), "element", True),
        "purpose": (qn(REUSABLE_NS, "Purpose"), "element", False),
        "coverage": (qn(REUSABLE_NS, "Coverage"), "element", False),
        "embargos": (qn(REUSABLE_NS, "Embargo"), "element", True),
        "other_material_schemes": (qn(REUSABLE_NS, "OtherMaterialScheme"), "element", True),
        "other_material_scheme_references": (qn(REUSABLE_NS, "OtherMaterialSchemeReference"), "reference", True),
        "resource_package_archives": (qn(GROUP_NS, "ResourcePackageArchive"), "element", True),
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
        "ddi_profiles": (qn(DDI_PROFILE_NS, "DDIProfile"), "element", True),
        "ddi_profile_references": (qn(REUSABLE_NS, "DDIProfileReference"), "reference", True),
        "comparisons": (qn(COMPARATIVE_NS, "Comparison"), "element", True),
        "comparison_references": (qn(REUSABLE_NS, "ComparisonReference"), "reference", True),
        "classification_families": (qn(LOGICAL_PRODUCT_NS, "ClassificationFamily"), "element", True),
        "classification_family_references": (qn(REUSABLE_NS, "ClassificationFamilyReference"), "reference", True),
        "classification_correspondence_tables": (qn(LOGICAL_PRODUCT_NS, "ClassificationCorrespondenceTable"), "element", True),
        "classification_correspondence_table_references": (qn(REUSABLE_NS, "ClassificationCorrespondenceTableReference"), "reference", True),
        "organization_schemes": (qn(ARCHIVE_NS, "OrganizationScheme"), "element", True),
        "organization_scheme_references": (qn(REUSABLE_NS, "OrganizationSchemeReference"), "reference", True),
        "concept_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptScheme"), "element", True),
        "concept_scheme_references": (qn(REUSABLE_NS, "ConceptSchemeReference"), "reference", True),
        "universe_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseScheme"), "element", True),
        "universe_scheme_references": (qn(REUSABLE_NS, "UniverseSchemeReference"), "reference", True),
        "conceptual_variable_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableScheme"), "element", True),
        "conceptual_variable_scheme_references": (qn(REUSABLE_NS, "ConceptualVariableSchemeReference"), "reference", True),
        "represented_variable_schemes": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme"), "element", True),
        "represented_variable_scheme_references": (qn(REUSABLE_NS, "RepresentedVariableSchemeReference"), "reference", True),
        "geographic_structure_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureScheme"), "element", True),
        "geographic_structure_scheme_references": (qn(REUSABLE_NS, "GeographicStructureSchemeReference"), "reference", True),
        "geographic_location_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationScheme"), "element", True),
        "geographic_location_scheme_references": (qn(REUSABLE_NS, "GeographicLocationSchemeReference"), "reference", True),
        "interviewer_instruction_schemes": (qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme"), "element", True),
        "interviewer_instruction_scheme_references": (qn(REUSABLE_NS, "InterviewerInstructionSchemeReference"), "reference", True),
        "control_construct_schemes": (qn(DATA_COLLECTION_NS, "ControlConstructScheme"), "element", True),
        "control_construct_scheme_references": (qn(REUSABLE_NS, "ControlConstructSchemeReference"), "reference", True),
        "question_schemes": (qn(DATA_COLLECTION_NS, "QuestionScheme"), "element", True),
        "question_scheme_references": (qn(REUSABLE_NS, "QuestionSchemeReference"), "reference", True),
        "measurement_schemes": (qn(DATA_COLLECTION_NS, "MeasurementScheme"), "element", True),
        "measurement_scheme_references": (qn(REUSABLE_NS, "MeasurementSchemeReference"), "reference", True),
        "category_schemes": (qn(LOGICAL_PRODUCT_NS, "CategoryScheme"), "element", True),
        "category_scheme_references": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", True),
        "code_list_schemes": (qn(LOGICAL_PRODUCT_NS, "CodeListScheme"), "element", True),
        "code_list_scheme_references": (qn(REUSABLE_NS, "CodeListSchemeReference"), "reference", True),
        "n_cube_schemes": (qn(LOGICAL_PRODUCT_NS, "NCubeScheme"), "element", True),
        "n_cube_scheme_references": (qn(REUSABLE_NS, "NCubeSchemeReference"), "reference", True),
        "variable_schemes": (qn(LOGICAL_PRODUCT_NS, "VariableScheme"), "element", True),
        "variable_scheme_references": (qn(REUSABLE_NS, "VariableSchemeReference"), "reference", True),
        "physical_structure_schemes": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureScheme"), "element", True),
        "physical_structure_scheme_references": (qn(REUSABLE_NS, "PhysicalStructureSchemeReference"), "reference", True),
        "record_layout_schemes": (qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutScheme"), "element", True),
        "record_layout_scheme_references": (qn(REUSABLE_NS, "RecordLayoutSchemeReference"), "reference", True),
        "quality_schemes": (qn(REUSABLE_NS, "QualityScheme"), "element", True),
        "quality_scheme_references": (qn(REUSABLE_NS, "QualitySchemeReference"), "reference", True),
        "instrument_schemes": (qn(DATA_COLLECTION_NS, "InstrumentScheme"), "element", True),
        "instrument_scheme_references": (qn(REUSABLE_NS, "InstrumentSchemeReference"), "reference", True),
        "processing_event_schemes": (qn(DATA_COLLECTION_NS, "ProcessingEventScheme"), "element", True),
        "processing_event_scheme_references": (qn(DATA_COLLECTION_NS, "ProcessingEventSchemeReference"), "reference", True),
        "processing_instruction_schemes": (qn(DATA_COLLECTION_NS, "ProcessingInstructionScheme"), "element", True),
        "processing_instruction_scheme_references": (qn(DATA_COLLECTION_NS, "ProcessingInstructionSchemeReference"), "reference", True),
        "managed_representation_schemes": (qn(REUSABLE_NS, "ManagedRepresentationScheme"), "element", True),
        "managed_representation_scheme_references": (qn(REUSABLE_NS, "ManagedRepresentationSchemeReference"), "reference", True),
        "unit_type_schemes": (qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeScheme"), "element", True),
        "unit_type_scheme_references": (qn(REUSABLE_NS, "UnitTypeSchemeReference"), "reference", True),
        "sampling_information_schemes": (qn(DATA_COLLECTION_NS, "SamplingInformationScheme"), "element", True),
        "sampling_information_scheme_references": (qn(REUSABLE_NS, "SamplingInformationSchemeReference"), "reference", True),
        "development_activity_schemes": (qn(DATA_COLLECTION_NS, "DevelopmentActivityScheme"), "element", True),
        "development_activity_scheme_references": (qn(REUSABLE_NS, "DevelopmentActivitySchemeReference"), "reference", True),
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
        qn(REUSABLE_NS, "Citation"),
        qn(GROUP_NS, "TypeOfResourcePackage"),
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
        qn(REUSABLE_NS, "FundingInformation"),
        qn(GROUP_NS, "ProjectBudget"),
        qn(REUSABLE_NS, "Purpose"),
        qn(REUSABLE_NS, "Coverage"),
        qn(REUSABLE_NS, "Embargo"),
        qn(REUSABLE_NS, "OtherMaterialScheme"),
        qn(REUSABLE_NS, "OtherMaterialSchemeReference"),
        qn(GROUP_NS, "ResourcePackageArchive"),
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
        qn(DDI_PROFILE_NS, "DDIProfile"),
        qn(REUSABLE_NS, "DDIProfileReference"),
        qn(COMPARATIVE_NS, "Comparison"),
        qn(REUSABLE_NS, "ComparisonReference"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationFamily"),
        qn(REUSABLE_NS, "ClassificationFamilyReference"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationCorrespondenceTable"),
        qn(REUSABLE_NS, "ClassificationCorrespondenceTableReference"),
        qn(ARCHIVE_NS, "OrganizationScheme"),
        qn(REUSABLE_NS, "OrganizationSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptScheme"),
        qn(REUSABLE_NS, "ConceptSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseScheme"),
        qn(REUSABLE_NS, "UniverseSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableScheme"),
        qn(REUSABLE_NS, "ConceptualVariableSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme"),
        qn(REUSABLE_NS, "RepresentedVariableSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureScheme"),
        qn(REUSABLE_NS, "GeographicStructureSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationScheme"),
        qn(REUSABLE_NS, "GeographicLocationSchemeReference"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme"),
        qn(REUSABLE_NS, "InterviewerInstructionSchemeReference"),
        qn(DATA_COLLECTION_NS, "ControlConstructScheme"),
        qn(REUSABLE_NS, "ControlConstructSchemeReference"),
        qn(DATA_COLLECTION_NS, "QuestionScheme"),
        qn(REUSABLE_NS, "QuestionSchemeReference"),
        qn(DATA_COLLECTION_NS, "MeasurementScheme"),
        qn(REUSABLE_NS, "MeasurementSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "CategoryScheme"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "CodeListScheme"),
        qn(REUSABLE_NS, "CodeListSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "NCubeScheme"),
        qn(REUSABLE_NS, "NCubeSchemeReference"),
        qn(LOGICAL_PRODUCT_NS, "VariableScheme"),
        qn(REUSABLE_NS, "VariableSchemeReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureScheme"),
        qn(REUSABLE_NS, "PhysicalStructureSchemeReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutScheme"),
        qn(REUSABLE_NS, "RecordLayoutSchemeReference"),
        qn(REUSABLE_NS, "QualityScheme"),
        qn(REUSABLE_NS, "QualitySchemeReference"),
        qn(DATA_COLLECTION_NS, "InstrumentScheme"),
        qn(REUSABLE_NS, "InstrumentSchemeReference"),
        qn(DATA_COLLECTION_NS, "ProcessingEventScheme"),
        qn(DATA_COLLECTION_NS, "ProcessingEventSchemeReference"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionScheme"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionSchemeReference"),
        qn(REUSABLE_NS, "ManagedRepresentationScheme"),
        qn(REUSABLE_NS, "ManagedRepresentationSchemeReference"),
        qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeScheme"),
        qn(REUSABLE_NS, "UnitTypeSchemeReference"),
        qn(DATA_COLLECTION_NS, "SamplingInformationScheme"),
        qn(REUSABLE_NS, "SamplingInformationSchemeReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityScheme"),
        qn(REUSABLE_NS, "DevelopmentActivitySchemeReference"),
    ]

