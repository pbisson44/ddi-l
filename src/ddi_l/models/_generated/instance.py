"""AUTO-GENERATED base dataclasses for DDI 3.3 — instance module.

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
from ddi_l.constants import ARCHIVE_NS, COMPARATIVE_NS, CONCEPTUAL_COMPONENT_NS, DATASET_NS, DATA_COLLECTION_NS, DDI_PROFILE_NS, GROUP_NS, INSTANCE_NS, LOGICAL_PRODUCT_NS, PHYSICAL_DATA_PRODUCT_NS, PHYSICAL_INSTANCE_NS, REUSABLE_NS, STUDY_UNIT_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class DDIInstanceFields(MaintainableBase):
    """DDIInstance is the top-level publication wrapper for any DDI document. All DDI content published as XML (with the exception of a Fragment intended for transmission) has DDIInstance as its top level st"""

    TAG: ClassVar[str] = qn(INSTANCE_NS, "DDIInstance")
    citation: Optional[Element] = None  # [0..1]
    coverage: Optional[Element] = None  # [0..1]
    groups: list[Element] = field(default_factory=list)  # [0..*]
    group_references: list[Reference] = field(default_factory=list)  # [0..*]
    resource_packages: list[Element] = field(default_factory=list)  # [0..*]
    resource_package_references: list[Reference] = field(default_factory=list)  # [0..*]
    local_holding_packages: list[Element] = field(default_factory=list)  # [0..*]
    local_holding_package_references: list[Reference] = field(default_factory=list)  # [0..*]
    study_units: list[Element] = field(default_factory=list)  # [0..*]
    study_unit_references: list[Reference] = field(default_factory=list)  # [0..*]
    ddi_profiles: list[Element] = field(default_factory=list)  # [0..*]
    ddi_profile_references: list[Reference] = field(default_factory=list)  # [0..*]
    translation_information: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "citation": (qn(REUSABLE_NS, "Citation"), "element", False),
        "coverage": (qn(REUSABLE_NS, "Coverage"), "element", False),
        "groups": (qn(GROUP_NS, "Group"), "element", True),
        "group_references": (qn(REUSABLE_NS, "GroupReference"), "reference", True),
        "resource_packages": (qn(GROUP_NS, "ResourcePackage"), "element", True),
        "resource_package_references": (qn(REUSABLE_NS, "ResourcePackageReference"), "reference", True),
        "local_holding_packages": (qn(GROUP_NS, "LocalHoldingPackage"), "element", True),
        "local_holding_package_references": (qn(REUSABLE_NS, "LocalHoldingPackageReference"), "reference", True),
        "study_units": (qn(STUDY_UNIT_NS, "StudyUnit"), "element", True),
        "study_unit_references": (qn(REUSABLE_NS, "StudyUnitReference"), "reference", True),
        "ddi_profiles": (qn(DDI_PROFILE_NS, "DDIProfile"), "element", True),
        "ddi_profile_references": (qn(REUSABLE_NS, "DDIProfileReference"), "reference", True),
        "translation_information": (qn(INSTANCE_NS, "TranslationInformation"), "element", False),
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
        qn(REUSABLE_NS, "Coverage"),
        qn(GROUP_NS, "Group"),
        qn(REUSABLE_NS, "GroupReference"),
        qn(GROUP_NS, "ResourcePackage"),
        qn(REUSABLE_NS, "ResourcePackageReference"),
        qn(GROUP_NS, "LocalHoldingPackage"),
        qn(REUSABLE_NS, "LocalHoldingPackageReference"),
        qn(STUDY_UNIT_NS, "StudyUnit"),
        qn(REUSABLE_NS, "StudyUnitReference"),
        qn(DDI_PROFILE_NS, "DDIProfile"),
        qn(REUSABLE_NS, "DDIProfileReference"),
        qn(INSTANCE_NS, "TranslationInformation"),
    ]


@dataclass
class FragmentInstanceFields(MaintainableBase):
    """A Fragment Instance is used to transfer maintainable or versionable objects plus any associated notes and other material in response to a query. TopLevelReference provides a record of the reference(s)"""

    TAG: ClassVar[str] = qn(INSTANCE_NS, "FragmentInstance")
    top_level_references: list[Reference] = field(default_factory=list)  # [0..*]
    fragments: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "top_level_references": (qn(INSTANCE_NS, "TopLevelReference"), "reference", True),
        "fragments": (qn(INSTANCE_NS, "Fragment"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(INSTANCE_NS, "TopLevelReference"),
        qn(INSTANCE_NS, "Fragment"),
    ]


@dataclass
class FragmentFields(MaintainableBase):
    """A Fragment is a means of transporting a maintainable or versionable object plus any associated notes and other material. The list of maintainables and versionables may occur in any order followed by a"""

    TAG: ClassVar[str] = qn(INSTANCE_NS, "Fragment")
    archive: Optional[Element] = None  # [1..1]
    base_logical_product: Optional[Element] = None  # [1..1]
    category_scheme: Optional[Element] = None  # [1..1]
    classification_family: Optional[Element] = None  # [1..1]
    code_list: Optional[Element] = None  # [1..1]
    code_list_scheme: Optional[Element] = None  # [1..1]
    comparison: Optional[Element] = None  # [1..1]
    concept_scheme: Optional[Element] = None  # [1..1]
    conceptual_component: Optional[Element] = None  # [1..1]
    conceptual_variable_scheme: Optional[Element] = None  # [1..1]
    control_construct_scheme: Optional[Element] = None  # [1..1]
    data_collection: Optional[Element] = None  # [1..1]
    development_activity_scheme: Optional[Element] = None  # [1..1]
    ddi_instance: Optional[Element] = None  # [1..1]
    ddi_profile: Optional[Element] = None  # [1..1]
    geographic_location_scheme: Optional[Element] = None  # [1..1]
    geographic_structure_scheme: Optional[Element] = None  # [1..1]
    group: Optional[Element] = None  # [1..1]
    instrument_scheme: Optional[Element] = None  # [1..1]
    interviewer_instruction_scheme: Optional[Element] = None  # [1..1]
    local_group_content: Optional[Element] = None  # [1..1]
    local_holding_package: Optional[Element] = None  # [1..1]
    local_resource_package_content: Optional[Element] = None  # [1..1]
    local_study_unit_content: Optional[Element] = None  # [1..1]
    managed_representation_scheme: Optional[Element] = None  # [1..1]
    measurement_scheme: Optional[Element] = None  # [1..1]
    n_cube_scheme: Optional[Element] = None  # [1..1]
    organization_scheme: Optional[Element] = None  # [1..1]
    other_material_scheme: Optional[Element] = None  # [1..1]
    physical_data_product: Optional[Element] = None  # [1..1]
    physical_instance: Optional[Element] = None  # [1..1]
    physical_structure_scheme: Optional[Element] = None  # [1..1]
    processing_event_scheme: Optional[Element] = None  # [1..1]
    processing_instruction_scheme: Optional[Element] = None  # [1..1]
    quality_scheme: Optional[Element] = None  # [1..1]
    question_scheme: Optional[Element] = None  # [1..1]
    record_layout_scheme: Optional[Element] = None  # [1..1]
    represented_variable_scheme: Optional[Element] = None  # [1..1]
    resource_package: Optional[Element] = None  # [1..1]
    sampling_information_scheme: Optional[Element] = None  # [1..1]
    study_unit: Optional[Element] = None  # [1..1]
    unit_type_scheme: Optional[Element] = None  # [1..1]
    universe_scheme: Optional[Element] = None  # [1..1]
    variable_scheme: Optional[Element] = None  # [1..1]
    approval_review: Optional[Element] = None  # [1..1]
    approval_review_document: Optional[Element] = None  # [1..1]
    category: Optional[Element] = None  # [1..1]
    category_group: Optional[Element] = None  # [1..1]
    category_map: Optional[Element] = None  # [1..1]
    classification_correspondence_table: Optional[Element] = None  # [1..1]
    classification_index: Optional[Element] = None  # [1..1]
    classification_item: Optional[Element] = None  # [1..1]
    classification_level: Optional[Element] = None  # [1..1]
    classification_series: Optional[Element] = None  # [1..1]
    code_list_group: Optional[Element] = None  # [1..1]
    cognitive_expert_review_activity: Optional[Element] = None  # [1..1]
    cognitive_interview_activity: Optional[Element] = None  # [1..1]
    computation_item: Optional[Element] = None  # [1..1]
    concept: Optional[Element] = None  # [1..1]
    concept_group: Optional[Element] = None  # [1..1]
    concept_map: Optional[Element] = None  # [1..1]
    conceptual_variable: Optional[Element] = None  # [1..1]
    conceptual_variable_group: Optional[Element] = None  # [1..1]
    content_review_activity: Optional[Element] = None  # [1..1]
    control_construct_group: Optional[Element] = None  # [1..1]
    data_capture_development: Optional[Element] = None  # [1..1]
    data_relationship: Optional[Element] = None  # [1..1]
    data_set: Optional[Element] = None  # [1..1]
    development_activity_group: Optional[Element] = None  # [1..1]
    development_plan: Optional[Element] = None  # [1..1]
    development_implementation: Optional[Element] = None  # [1..1]
    development_results: Optional[Element] = None  # [1..1]
    development_step: Optional[Element] = None  # [1..1]
    focus_group_activity: Optional[Element] = None  # [1..1]
    funding_document: Optional[Element] = None  # [1..1]
    general_instruction: Optional[Element] = None  # [1..1]
    generation_instruction: Optional[Element] = None  # [1..1]
    geographic_location: Optional[Element] = None  # [1..1]
    geographic_location_group: Optional[Element] = None  # [1..1]
    geographic_structure: Optional[Element] = None  # [1..1]
    geographic_structure_group: Optional[Element] = None  # [1..1]
    if_then_else: Optional[Element] = None  # [1..1]
    individual: Optional[Element] = None  # [1..1]
    information_classification: Optional[Element] = None  # [1..1]
    instruction: Optional[Element] = None  # [1..1]
    instruction_group: Optional[Element] = None  # [1..1]
    instrument: Optional[Element] = None  # [1..1]
    instrument_group: Optional[Element] = None  # [1..1]
    loop: Optional[Element] = None  # [1..1]
    managed_date_time_representation: Optional[Element] = None  # [1..1]
    managed_item_map: Optional[Element] = None  # [1..1]
    managed_missing_values_representation: Optional[Element] = None  # [1..1]
    managed_numeric_representation: Optional[Element] = None  # [1..1]
    managed_representation_group: Optional[Element] = None  # [1..1]
    managed_scale_representation: Optional[Element] = None  # [1..1]
    managed_text_representation: Optional[Element] = None  # [1..1]
    measurement_construct: Optional[Element] = None  # [1..1]
    measurement_group: Optional[Element] = None  # [1..1]
    measurement_item: Optional[Element] = None  # [1..1]
    methodology: Optional[Element] = None  # [1..1]
    n_cube: Optional[Element] = None  # [1..1]
    n_cube_group: Optional[Element] = None  # [1..1]
    n_cube_instance: Optional[Element] = None  # [1..1]
    organization: Optional[Element] = None  # [1..1]
    organization_group: Optional[Element] = None  # [1..1]
    other_material: Optional[Element] = None  # [1..1]
    other_material_group: Optional[Element] = None  # [1..1]
    physical_instance_group: Optional[Element] = None  # [1..1]
    physical_structure: Optional[Element] = None  # [1..1]
    physical_structure_group: Optional[Element] = None  # [1..1]
    pretest_activity: Optional[Element] = None  # [1..1]
    processing_event: Optional[Element] = None  # [1..1]
    processing_event_group: Optional[Element] = None  # [1..1]
    processing_instruction_group: Optional[Element] = None  # [1..1]
    quality_standard: Optional[Element] = None  # [1..1]
    quality_standard_group: Optional[Element] = None  # [1..1]
    quality_statement: Optional[Element] = None  # [1..1]
    quality_statement_group: Optional[Element] = None  # [1..1]
    question_block: Optional[Element] = None  # [1..1]
    question_construct: Optional[Element] = None  # [1..1]
    question_grid: Optional[Element] = None  # [1..1]
    question_group: Optional[Element] = None  # [1..1]
    question_item: Optional[Element] = None  # [1..1]
    question_map: Optional[Element] = None  # [1..1]
    record_layout: Optional[Element] = None  # [1..1]
    record_layout_group: Optional[Element] = None  # [1..1]
    relation: Optional[Element] = None  # [1..1]
    repeat_until: Optional[Element] = None  # [1..1]
    repeat_while: Optional[Element] = None  # [1..1]
    representation_map: Optional[Element] = None  # [1..1]
    represented_variable: Optional[Element] = None  # [1..1]
    represented_variable_group: Optional[Element] = None  # [1..1]
    sample: Optional[Element] = None  # [1..1]
    sample_frame: Optional[Element] = None  # [1..1]
    sample_step: Optional[Element] = None  # [1..1]
    sampling_information_group: Optional[Element] = None  # [1..1]
    sampling_plan: Optional[Element] = None  # [1..1]
    sampling_stage: Optional[Element] = None  # [1..1]
    sequence: Optional[Element] = None  # [1..1]
    split: Optional[Element] = None  # [1..1]
    split_join: Optional[Element] = None  # [1..1]
    statement_item: Optional[Element] = None  # [1..1]
    statistical_classification: Optional[Element] = None  # [1..1]
    sub_universe_class: Optional[Element] = None  # [1..1]
    translation_activity: Optional[Element] = None  # [1..1]
    unit_type: Optional[Element] = None  # [1..1]
    unit_type_group: Optional[Element] = None  # [1..1]
    universe: Optional[Element] = None  # [1..1]
    universe_group: Optional[Element] = None  # [1..1]
    universe_map: Optional[Element] = None  # [1..1]
    variable: Optional[Element] = None  # [1..1]
    variable_group: Optional[Element] = None  # [1..1]
    variable_map: Optional[Element] = None  # [1..1]
    variable_statistics: Optional[Element] = None  # [1..1]
    weighting: Optional[Element] = None  # [1..1]
    weighting_methodology: Optional[Element] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "archive": (qn(ARCHIVE_NS, "Archive"), "element", False),
        "base_logical_product": (qn(LOGICAL_PRODUCT_NS, "BaseLogicalProduct"), "element", False),
        "category_scheme": (qn(LOGICAL_PRODUCT_NS, "CategoryScheme"), "element", False),
        "classification_family": (qn(LOGICAL_PRODUCT_NS, "ClassificationFamily"), "element", False),
        "code_list": (qn(LOGICAL_PRODUCT_NS, "CodeList"), "element", False),
        "code_list_scheme": (qn(LOGICAL_PRODUCT_NS, "CodeListScheme"), "element", False),
        "comparison": (qn(COMPARATIVE_NS, "Comparison"), "element", False),
        "concept_scheme": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptScheme"), "element", False),
        "conceptual_component": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualComponent"), "element", False),
        "conceptual_variable_scheme": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableScheme"), "element", False),
        "control_construct_scheme": (qn(DATA_COLLECTION_NS, "ControlConstructScheme"), "element", False),
        "data_collection": (qn(DATA_COLLECTION_NS, "DataCollection"), "element", False),
        "development_activity_scheme": (qn(DATA_COLLECTION_NS, "DevelopmentActivityScheme"), "element", False),
        "ddi_instance": (qn(INSTANCE_NS, "DDIInstance"), "element", False),
        "ddi_profile": (qn(DDI_PROFILE_NS, "DDIProfile"), "element", False),
        "geographic_location_scheme": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationScheme"), "element", False),
        "geographic_structure_scheme": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureScheme"), "element", False),
        "group": (qn(GROUP_NS, "Group"), "element", False),
        "instrument_scheme": (qn(DATA_COLLECTION_NS, "InstrumentScheme"), "element", False),
        "interviewer_instruction_scheme": (qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme"), "element", False),
        "local_group_content": (qn(GROUP_NS, "LocalGroupContent"), "element", False),
        "local_holding_package": (qn(GROUP_NS, "LocalHoldingPackage"), "element", False),
        "local_resource_package_content": (qn(GROUP_NS, "LocalResourcePackageContent"), "element", False),
        "local_study_unit_content": (qn(GROUP_NS, "LocalStudyUnitContent"), "element", False),
        "managed_representation_scheme": (qn(REUSABLE_NS, "ManagedRepresentationScheme"), "element", False),
        "measurement_scheme": (qn(DATA_COLLECTION_NS, "MeasurementScheme"), "element", False),
        "n_cube_scheme": (qn(LOGICAL_PRODUCT_NS, "NCubeScheme"), "element", False),
        "organization_scheme": (qn(ARCHIVE_NS, "OrganizationScheme"), "element", False),
        "other_material_scheme": (qn(REUSABLE_NS, "OtherMaterialScheme"), "element", False),
        "physical_data_product": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProduct"), "element", False),
        "physical_instance": (qn(PHYSICAL_INSTANCE_NS, "PhysicalInstance"), "element", False),
        "physical_structure_scheme": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureScheme"), "element", False),
        "processing_event_scheme": (qn(DATA_COLLECTION_NS, "ProcessingEventScheme"), "element", False),
        "processing_instruction_scheme": (qn(DATA_COLLECTION_NS, "ProcessingInstructionScheme"), "element", False),
        "quality_scheme": (qn(REUSABLE_NS, "QualityScheme"), "element", False),
        "question_scheme": (qn(DATA_COLLECTION_NS, "QuestionScheme"), "element", False),
        "record_layout_scheme": (qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutScheme"), "element", False),
        "represented_variable_scheme": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme"), "element", False),
        "resource_package": (qn(GROUP_NS, "ResourcePackage"), "element", False),
        "sampling_information_scheme": (qn(DATA_COLLECTION_NS, "SamplingInformationScheme"), "element", False),
        "study_unit": (qn(STUDY_UNIT_NS, "StudyUnit"), "element", False),
        "unit_type_scheme": (qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeScheme"), "element", False),
        "universe_scheme": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseScheme"), "element", False),
        "variable_scheme": (qn(LOGICAL_PRODUCT_NS, "VariableScheme"), "element", False),
        "approval_review": (qn(REUSABLE_NS, "ApprovalReview"), "element", False),
        "approval_review_document": (qn(REUSABLE_NS, "ApprovalReviewDocument"), "element", False),
        "category": (qn(LOGICAL_PRODUCT_NS, "Category"), "element", False),
        "category_group": (qn(LOGICAL_PRODUCT_NS, "CategoryGroup"), "element", False),
        "category_map": (qn(COMPARATIVE_NS, "CategoryMap"), "element", False),
        "classification_correspondence_table": (qn(LOGICAL_PRODUCT_NS, "ClassificationCorrespondenceTable"), "element", False),
        "classification_index": (qn(LOGICAL_PRODUCT_NS, "ClassificationIndex"), "element", False),
        "classification_item": (qn(LOGICAL_PRODUCT_NS, "ClassificationItem"), "element", False),
        "classification_level": (qn(LOGICAL_PRODUCT_NS, "ClassificationLevel"), "element", False),
        "classification_series": (qn(LOGICAL_PRODUCT_NS, "ClassificationSeries"), "element", False),
        "code_list_group": (qn(LOGICAL_PRODUCT_NS, "CodeListGroup"), "element", False),
        "cognitive_expert_review_activity": (qn(DATA_COLLECTION_NS, "CognitiveExpertReviewActivity"), "element", False),
        "cognitive_interview_activity": (qn(DATA_COLLECTION_NS, "CognitiveInterviewActivity"), "element", False),
        "computation_item": (qn(DATA_COLLECTION_NS, "ComputationItem"), "element", False),
        "concept": (qn(CONCEPTUAL_COMPONENT_NS, "Concept"), "element", False),
        "concept_group": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroup"), "element", False),
        "concept_map": (qn(COMPARATIVE_NS, "ConceptMap"), "element", False),
        "conceptual_variable": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariable"), "element", False),
        "conceptual_variable_group": (qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroup"), "element", False),
        "content_review_activity": (qn(DATA_COLLECTION_NS, "ContentReviewActivity"), "element", False),
        "control_construct_group": (qn(DATA_COLLECTION_NS, "ControlConstructGroup"), "element", False),
        "data_capture_development": (qn(DATA_COLLECTION_NS, "DataCaptureDevelopment"), "element", False),
        "data_relationship": (qn(LOGICAL_PRODUCT_NS, "DataRelationship"), "element", False),
        "data_set": (qn(DATASET_NS, "DataSet"), "element", False),
        "development_activity_group": (qn(DATA_COLLECTION_NS, "DevelopmentActivityGroup"), "element", False),
        "development_plan": (qn(DATA_COLLECTION_NS, "DevelopmentPlan"), "element", False),
        "development_implementation": (qn(DATA_COLLECTION_NS, "DevelopmentImplementation"), "element", False),
        "development_results": (qn(DATA_COLLECTION_NS, "DevelopmentResults"), "element", False),
        "development_step": (qn(DATA_COLLECTION_NS, "DevelopmentStep"), "element", False),
        "focus_group_activity": (qn(DATA_COLLECTION_NS, "FocusGroupActivity"), "element", False),
        "funding_document": (qn(REUSABLE_NS, "FundingDocument"), "element", False),
        "general_instruction": (qn(DATA_COLLECTION_NS, "GeneralInstruction"), "element", False),
        "generation_instruction": (qn(DATA_COLLECTION_NS, "GenerationInstruction"), "element", False),
        "geographic_location": (qn(REUSABLE_NS, "GeographicLocation"), "element", False),
        "geographic_location_group": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroup"), "element", False),
        "geographic_structure": (qn(REUSABLE_NS, "GeographicStructure"), "element", False),
        "geographic_structure_group": (qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroup"), "element", False),
        "if_then_else": (qn(DATA_COLLECTION_NS, "IfThenElse"), "element", False),
        "individual": (qn(ARCHIVE_NS, "Individual"), "element", False),
        "information_classification": (qn(REUSABLE_NS, "InformationClassification"), "element", False),
        "instruction": (qn(DATA_COLLECTION_NS, "Instruction"), "element", False),
        "instruction_group": (qn(DATA_COLLECTION_NS, "InstructionGroup"), "element", False),
        "instrument": (qn(DATA_COLLECTION_NS, "Instrument"), "element", False),
        "instrument_group": (qn(DATA_COLLECTION_NS, "InstrumentGroup"), "element", False),
        "loop": (qn(DATA_COLLECTION_NS, "Loop"), "element", False),
        "managed_date_time_representation": (qn(REUSABLE_NS, "ManagedDateTimeRepresentation"), "element", False),
        "managed_item_map": (qn(COMPARATIVE_NS, "ManagedItemMap"), "element", False),
        "managed_missing_values_representation": (qn(REUSABLE_NS, "ManagedMissingValuesRepresentation"), "element", False),
        "managed_numeric_representation": (qn(REUSABLE_NS, "ManagedNumericRepresentation"), "element", False),
        "managed_representation_group": (qn(REUSABLE_NS, "ManagedRepresentationGroup"), "element", False),
        "managed_scale_representation": (qn(REUSABLE_NS, "ManagedScaleRepresentation"), "element", False),
        "managed_text_representation": (qn(REUSABLE_NS, "ManagedTextRepresentation"), "element", False),
        "measurement_construct": (qn(DATA_COLLECTION_NS, "MeasurementConstruct"), "element", False),
        "measurement_group": (qn(DATA_COLLECTION_NS, "MeasurementGroup"), "element", False),
        "measurement_item": (qn(DATA_COLLECTION_NS, "MeasurementItem"), "element", False),
        "methodology": (qn(DATA_COLLECTION_NS, "Methodology"), "element", False),
        "n_cube": (qn(LOGICAL_PRODUCT_NS, "NCube"), "element", False),
        "n_cube_group": (qn(LOGICAL_PRODUCT_NS, "NCubeGroup"), "element", False),
        "n_cube_instance": (qn("ddi:physicaldataproduct_ncube_inline:3_3", "NCubeInstance"), "element", False),
        "organization": (qn(ARCHIVE_NS, "Organization"), "element", False),
        "organization_group": (qn(ARCHIVE_NS, "OrganizationGroup"), "element", False),
        "other_material": (qn(REUSABLE_NS, "OtherMaterial"), "element", False),
        "other_material_group": (qn(REUSABLE_NS, "OtherMaterialGroup"), "element", False),
        "physical_instance_group": (qn(PHYSICAL_INSTANCE_NS, "PhysicalInstanceGroup"), "element", False),
        "physical_structure": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructure"), "element", False),
        "physical_structure_group": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroup"), "element", False),
        "pretest_activity": (qn(DATA_COLLECTION_NS, "PretestActivity"), "element", False),
        "processing_event": (qn(DATA_COLLECTION_NS, "ProcessingEvent"), "element", False),
        "processing_event_group": (qn(DATA_COLLECTION_NS, "ProcessingEventGroup"), "element", False),
        "processing_instruction_group": (qn(DATA_COLLECTION_NS, "ProcessingInstructionGroup"), "element", False),
        "quality_standard": (qn(REUSABLE_NS, "QualityStandard"), "element", False),
        "quality_standard_group": (qn(REUSABLE_NS, "QualityStandardGroup"), "element", False),
        "quality_statement": (qn(REUSABLE_NS, "QualityStatement"), "element", False),
        "quality_statement_group": (qn(REUSABLE_NS, "QualityStatementGroup"), "element", False),
        "question_block": (qn(DATA_COLLECTION_NS, "QuestionBlock"), "element", False),
        "question_construct": (qn(DATA_COLLECTION_NS, "QuestionConstruct"), "element", False),
        "question_grid": (qn(DATA_COLLECTION_NS, "QuestionGrid"), "element", False),
        "question_group": (qn(DATA_COLLECTION_NS, "QuestionGroup"), "element", False),
        "question_item": (qn(DATA_COLLECTION_NS, "QuestionItem"), "element", False),
        "question_map": (qn(COMPARATIVE_NS, "QuestionMap"), "element", False),
        "record_layout": (qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayout"), "element", False),
        "record_layout_group": (qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroup"), "element", False),
        "relation": (qn(ARCHIVE_NS, "Relation"), "element", False),
        "repeat_until": (qn(DATA_COLLECTION_NS, "RepeatUntil"), "element", False),
        "repeat_while": (qn(DATA_COLLECTION_NS, "RepeatWhile"), "element", False),
        "representation_map": (qn(COMPARATIVE_NS, "RepresentationMap"), "element", False),
        "represented_variable": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariable"), "element", False),
        "represented_variable_group": (qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroup"), "element", False),
        "sample": (qn(DATA_COLLECTION_NS, "Sample"), "element", False),
        "sample_frame": (qn(DATA_COLLECTION_NS, "SampleFrame"), "element", False),
        "sample_step": (qn(DATA_COLLECTION_NS, "SampleStep"), "element", False),
        "sampling_information_group": (qn(DATA_COLLECTION_NS, "SamplingInformationGroup"), "element", False),
        "sampling_plan": (qn(DATA_COLLECTION_NS, "SamplingPlan"), "element", False),
        "sampling_stage": (qn(DATA_COLLECTION_NS, "SamplingStage"), "element", False),
        "sequence": (qn(DATA_COLLECTION_NS, "Sequence"), "element", False),
        "split": (qn(DATA_COLLECTION_NS, "Split"), "element", False),
        "split_join": (qn(DATA_COLLECTION_NS, "SplitJoin"), "element", False),
        "statement_item": (qn(DATA_COLLECTION_NS, "StatementItem"), "element", False),
        "statistical_classification": (qn(LOGICAL_PRODUCT_NS, "StatisticalClassification"), "element", False),
        "sub_universe_class": (qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClass"), "element", False),
        "translation_activity": (qn(DATA_COLLECTION_NS, "TranslationActivity"), "element", False),
        "unit_type": (qn(CONCEPTUAL_COMPONENT_NS, "UnitType"), "element", False),
        "unit_type_group": (qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroup"), "element", False),
        "universe": (qn(CONCEPTUAL_COMPONENT_NS, "Universe"), "element", False),
        "universe_group": (qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroup"), "element", False),
        "universe_map": (qn(COMPARATIVE_NS, "UniverseMap"), "element", False),
        "variable": (qn(LOGICAL_PRODUCT_NS, "Variable"), "element", False),
        "variable_group": (qn(LOGICAL_PRODUCT_NS, "VariableGroup"), "element", False),
        "variable_map": (qn(COMPARATIVE_NS, "VariableMap"), "element", False),
        "variable_statistics": (qn(PHYSICAL_INSTANCE_NS, "VariableStatistics"), "element", False),
        "weighting": (qn(DATA_COLLECTION_NS, "Weighting"), "element", False),
        "weighting_methodology": (qn(DATA_COLLECTION_NS, "WeightingMethodology"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "Archive"),
        qn(LOGICAL_PRODUCT_NS, "BaseLogicalProduct"),
        qn(LOGICAL_PRODUCT_NS, "CategoryScheme"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationFamily"),
        qn(LOGICAL_PRODUCT_NS, "CodeList"),
        qn(LOGICAL_PRODUCT_NS, "CodeListScheme"),
        qn(COMPARATIVE_NS, "Comparison"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptScheme"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualComponent"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableScheme"),
        qn(DATA_COLLECTION_NS, "ControlConstructScheme"),
        qn(DATA_COLLECTION_NS, "DataCollection"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityScheme"),
        qn(INSTANCE_NS, "DDIInstance"),
        qn(DDI_PROFILE_NS, "DDIProfile"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationScheme"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureScheme"),
        qn(GROUP_NS, "Group"),
        qn(DATA_COLLECTION_NS, "InstrumentScheme"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme"),
        qn(GROUP_NS, "LocalGroupContent"),
        qn(GROUP_NS, "LocalHoldingPackage"),
        qn(GROUP_NS, "LocalResourcePackageContent"),
        qn(GROUP_NS, "LocalStudyUnitContent"),
        qn(REUSABLE_NS, "ManagedRepresentationScheme"),
        qn(DATA_COLLECTION_NS, "MeasurementScheme"),
        qn(LOGICAL_PRODUCT_NS, "NCubeScheme"),
        qn(ARCHIVE_NS, "OrganizationScheme"),
        qn(REUSABLE_NS, "OtherMaterialScheme"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProduct"),
        qn(PHYSICAL_INSTANCE_NS, "PhysicalInstance"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureScheme"),
        qn(DATA_COLLECTION_NS, "ProcessingEventScheme"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionScheme"),
        qn(REUSABLE_NS, "QualityScheme"),
        qn(DATA_COLLECTION_NS, "QuestionScheme"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutScheme"),
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme"),
        qn(GROUP_NS, "ResourcePackage"),
        qn(DATA_COLLECTION_NS, "SamplingInformationScheme"),
        qn(STUDY_UNIT_NS, "StudyUnit"),
        qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeScheme"),
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseScheme"),
        qn(LOGICAL_PRODUCT_NS, "VariableScheme"),
        qn(REUSABLE_NS, "ApprovalReview"),
        qn(REUSABLE_NS, "ApprovalReviewDocument"),
        qn(LOGICAL_PRODUCT_NS, "Category"),
        qn(LOGICAL_PRODUCT_NS, "CategoryGroup"),
        qn(COMPARATIVE_NS, "CategoryMap"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationCorrespondenceTable"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationIndex"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationItem"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationLevel"),
        qn(LOGICAL_PRODUCT_NS, "ClassificationSeries"),
        qn(LOGICAL_PRODUCT_NS, "CodeListGroup"),
        qn(DATA_COLLECTION_NS, "CognitiveExpertReviewActivity"),
        qn(DATA_COLLECTION_NS, "CognitiveInterviewActivity"),
        qn(DATA_COLLECTION_NS, "ComputationItem"),
        qn(CONCEPTUAL_COMPONENT_NS, "Concept"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptGroup"),
        qn(COMPARATIVE_NS, "ConceptMap"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariable"),
        qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableGroup"),
        qn(DATA_COLLECTION_NS, "ContentReviewActivity"),
        qn(DATA_COLLECTION_NS, "ControlConstructGroup"),
        qn(DATA_COLLECTION_NS, "DataCaptureDevelopment"),
        qn(LOGICAL_PRODUCT_NS, "DataRelationship"),
        qn(DATASET_NS, "DataSet"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityGroup"),
        qn(DATA_COLLECTION_NS, "DevelopmentPlan"),
        qn(DATA_COLLECTION_NS, "DevelopmentImplementation"),
        qn(DATA_COLLECTION_NS, "DevelopmentResults"),
        qn(DATA_COLLECTION_NS, "DevelopmentStep"),
        qn(DATA_COLLECTION_NS, "FocusGroupActivity"),
        qn(REUSABLE_NS, "FundingDocument"),
        qn(DATA_COLLECTION_NS, "GeneralInstruction"),
        qn(DATA_COLLECTION_NS, "GenerationInstruction"),
        qn(REUSABLE_NS, "GeographicLocation"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicLocationGroup"),
        qn(REUSABLE_NS, "GeographicStructure"),
        qn(CONCEPTUAL_COMPONENT_NS, "GeographicStructureGroup"),
        qn(DATA_COLLECTION_NS, "IfThenElse"),
        qn(ARCHIVE_NS, "Individual"),
        qn(REUSABLE_NS, "InformationClassification"),
        qn(DATA_COLLECTION_NS, "Instruction"),
        qn(DATA_COLLECTION_NS, "InstructionGroup"),
        qn(DATA_COLLECTION_NS, "Instrument"),
        qn(DATA_COLLECTION_NS, "InstrumentGroup"),
        qn(DATA_COLLECTION_NS, "Loop"),
        qn(REUSABLE_NS, "ManagedDateTimeRepresentation"),
        qn(COMPARATIVE_NS, "ManagedItemMap"),
        qn(REUSABLE_NS, "ManagedMissingValuesRepresentation"),
        qn(REUSABLE_NS, "ManagedNumericRepresentation"),
        qn(REUSABLE_NS, "ManagedRepresentationGroup"),
        qn(REUSABLE_NS, "ManagedScaleRepresentation"),
        qn(REUSABLE_NS, "ManagedTextRepresentation"),
        qn(DATA_COLLECTION_NS, "MeasurementConstruct"),
        qn(DATA_COLLECTION_NS, "MeasurementGroup"),
        qn(DATA_COLLECTION_NS, "MeasurementItem"),
        qn(DATA_COLLECTION_NS, "Methodology"),
        qn(LOGICAL_PRODUCT_NS, "NCube"),
        qn(LOGICAL_PRODUCT_NS, "NCubeGroup"),
        qn("ddi:physicaldataproduct_ncube_inline:3_3", "NCubeInstance"),
        qn("ddi:physicaldataproduct_ncube_normal:3_3", "NCubeInstance"),
        qn("ddi:physicaldataproduct_ncube_tabular:3_3", "NCubeInstance"),
        qn(ARCHIVE_NS, "Organization"),
        qn(ARCHIVE_NS, "OrganizationGroup"),
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialGroup"),
        qn(PHYSICAL_INSTANCE_NS, "PhysicalInstanceGroup"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructure"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureGroup"),
        qn(DATA_COLLECTION_NS, "PretestActivity"),
        qn(DATA_COLLECTION_NS, "ProcessingEvent"),
        qn(DATA_COLLECTION_NS, "ProcessingEventGroup"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionGroup"),
        qn(REUSABLE_NS, "QualityStandard"),
        qn(REUSABLE_NS, "QualityStandardGroup"),
        qn(REUSABLE_NS, "QualityStatement"),
        qn(REUSABLE_NS, "QualityStatementGroup"),
        qn(DATA_COLLECTION_NS, "QuestionBlock"),
        qn(DATA_COLLECTION_NS, "QuestionConstruct"),
        qn(DATA_COLLECTION_NS, "QuestionGrid"),
        qn(DATA_COLLECTION_NS, "QuestionGroup"),
        qn(DATA_COLLECTION_NS, "QuestionItem"),
        qn(COMPARATIVE_NS, "QuestionMap"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayout"),
        qn("ddi:physicaldataproduct_ncube_inline:3_3", "RecordLayout"),
        qn("ddi:physicaldataproduct_ncube_normal:3_3", "RecordLayout"),
        qn("ddi:physicaldataproduct_ncube_tabular:3_3", "RecordLayout"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "RecordLayout"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutGroup"),
        qn(ARCHIVE_NS, "Relation"),
        qn(DATA_COLLECTION_NS, "RepeatUntil"),
        qn(DATA_COLLECTION_NS, "RepeatWhile"),
        qn(COMPARATIVE_NS, "RepresentationMap"),
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariable"),
        qn(LOGICAL_PRODUCT_NS, "RepresentedVariableGroup"),
        qn(DATA_COLLECTION_NS, "Sample"),
        qn(DATA_COLLECTION_NS, "SampleFrame"),
        qn(DATA_COLLECTION_NS, "SampleStep"),
        qn(DATA_COLLECTION_NS, "SamplingInformationGroup"),
        qn(DATA_COLLECTION_NS, "SamplingPlan"),
        qn(DATA_COLLECTION_NS, "SamplingStage"),
        qn(DATA_COLLECTION_NS, "Sequence"),
        qn(DATA_COLLECTION_NS, "Split"),
        qn(DATA_COLLECTION_NS, "SplitJoin"),
        qn(DATA_COLLECTION_NS, "StatementItem"),
        qn(LOGICAL_PRODUCT_NS, "StatisticalClassification"),
        qn(CONCEPTUAL_COMPONENT_NS, "SubUniverseClass"),
        qn(DATA_COLLECTION_NS, "TranslationActivity"),
        qn(CONCEPTUAL_COMPONENT_NS, "UnitType"),
        qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeGroup"),
        qn(CONCEPTUAL_COMPONENT_NS, "Universe"),
        qn(CONCEPTUAL_COMPONENT_NS, "UniverseGroup"),
        qn(COMPARATIVE_NS, "UniverseMap"),
        qn(LOGICAL_PRODUCT_NS, "Variable"),
        qn(LOGICAL_PRODUCT_NS, "VariableGroup"),
        qn(COMPARATIVE_NS, "VariableMap"),
        qn(PHYSICAL_INSTANCE_NS, "VariableStatistics"),
        qn(DATA_COLLECTION_NS, "Weighting"),
        qn(DATA_COLLECTION_NS, "WeightingMethodology"),
        qn(REUSABLE_NS, "Note"),
    ]


@dataclass
class TranslationFields(MaintainableBase):
    """Provides the language of translation as well as a description of translation for the contents of the DDI Instance."""

    TAG: ClassVar[str] = qn(INSTANCE_NS, "Translation")
    languages: list[CodeValue] = field(default_factory=list)  # [0..*]
    i18n_text: Optional[str] = None  # [0..1]
    i18n_catalog: Optional[str] = None  # [0..1]
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "languages": (qn(REUSABLE_NS, "Language"), "code_value", True),
        "i18n_text": (qn(INSTANCE_NS, "I18n-text"), "str", False),
        "i18n_catalog": (qn(INSTANCE_NS, "I18n-catalog"), "str", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "lang": ("lang", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Language"),
        qn(INSTANCE_NS, "I18n-text"),
        qn(INSTANCE_NS, "I18n-catalog"),
        qn(REUSABLE_NS, "Description"),
    ]

