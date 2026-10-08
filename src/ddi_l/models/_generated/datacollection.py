"""AUTO-GENERATED base dataclasses for DDI 3.3 — datacollection module.

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
from ddi_l.constants import DATA_COLLECTION_NS, REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class ActionToMinimizeLossesFields(MaintainableBase):
    """Describes action taken to minimize loss of data from the collection event. This may include a brief term, such as from a controlled vocabulary, and a full description of the actions taken. If multiple"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ActionToMinimizeLosses")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_action_to_minimize_losses: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_action_to_minimize_losses": (qn(DATA_COLLECTION_NS, "TypeOfActionToMinimizeLosses"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "TypeOfActionToMinimizeLosses"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class AdditionalDataCollectionFields(MaintainableBase):
    """Description of the method and mode of data collection in administering the pretest. Notes any additional data collected in the administration of the pretest."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "AdditionalDataCollection")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_additional_data: Optional[CodeValue] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_additional_data": (qn(DATA_COLLECTION_NS, "TypeOfAdditionalData"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "TypeOfAdditionalData"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class AggregationFields(MaintainableBase):
    """Describes the aggregation method and the variables used in the aggregation process. Identifies the method using an external controlled vocabulary and identifies the variables used either in-line or by"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Aggregation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    aggregation_method: Optional[CodeValue] = None  # [0..1]
    aggregation_variables: Optional[Element] = None  # [1..1]
    aggregation_variables_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "aggregation_method": (qn(REUSABLE_NS, "AggregationMethod"), "code_value", False),
        "aggregation_variables": (qn(DATA_COLLECTION_NS, "AggregationVariables"), "element", False),
        "aggregation_variables_reference": (qn(DATA_COLLECTION_NS, "AggregationVariablesReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "AggregationMethod"),
        qn(DATA_COLLECTION_NS, "AggregationVariables"),
        qn(DATA_COLLECTION_NS, "AggregationVariablesReference"),
    ]


@dataclass
class AggregationVariablesFields(MaintainableBase):
    """Identifies the independent and dependent variables used in the aggregation process. Note that in the case of calculating a percentage, mean, etc. of a dependent value against the total population of t"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "AggregationVariables")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    independent_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    dependent_variable_references: list[Reference] = field(default_factory=list)  # [1..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "independent_variable_references": (qn(DATA_COLLECTION_NS, "IndependentVariableReference"), "reference", True),
        "dependent_variable_references": (qn(DATA_COLLECTION_NS, "DependentVariableReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "IndependentVariableReference"),
        qn(DATA_COLLECTION_NS, "DependentVariableReference"),
    ]


@dataclass
class ApplicationDetailsFields(MaintainableBase):
    """Provides sample stage level details where needed. Repeat for individual stages or sub-stages."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ApplicationDetails")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    sampling_stage_reference: Optional[Reference] = None  # [0..1]
    sample_frame_reference: Optional[Reference] = None  # [0..1]
    frame_limitations: Optional[Element] = None  # [0..1]
    target_sample_sizes: list[Element] = field(default_factory=list)  # [0..*]
    date_of_sample: Optional[Element] = None  # [0..1]
    responsible_for_sampling_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "sampling_stage_reference": (qn(DATA_COLLECTION_NS, "SamplingStageReference"), "reference", False),
        "sample_frame_reference": (qn(DATA_COLLECTION_NS, "SampleFrameReference"), "reference", False),
        "frame_limitations": (qn(DATA_COLLECTION_NS, "FrameLimitations"), "element", False),
        "target_sample_sizes": (qn(DATA_COLLECTION_NS, "TargetSampleSize"), "element", True),
        "date_of_sample": (qn(DATA_COLLECTION_NS, "DateOfSample"), "element", False),
        "responsible_for_sampling_references": (qn(DATA_COLLECTION_NS, "ResponsibleForSamplingReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "SamplingStageReference"),
        qn(DATA_COLLECTION_NS, "SampleFrameReference"),
        qn(DATA_COLLECTION_NS, "FrameLimitations"),
        qn(DATA_COLLECTION_NS, "TargetSampleSize"),
        qn(DATA_COLLECTION_NS, "DateOfSample"),
        qn(DATA_COLLECTION_NS, "ResponsibleForSamplingReference"),
    ]


@dataclass
class AttachmentLocationFields(MaintainableBase):
    """Allows attachment of a response domain to a specific item in a code or category scheme. For example, attach a TextDomain to the value "Other"."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "AttachmentLocation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    code_references: list[Reference] = field(default_factory=list)  # [0..*]
    category_references: list[Reference] = field(default_factory=list)  # [0..*]
    domain_specific_values: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "code_references": (qn(REUSABLE_NS, "CodeReference"), "reference", True),
        "category_references": (qn(REUSABLE_NS, "CategoryReference"), "reference", True),
        "domain_specific_values": (qn(DATA_COLLECTION_NS, "DomainSpecificValue"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "CodeReference"),
        qn(REUSABLE_NS, "CategoryReference"),
        qn(DATA_COLLECTION_NS, "DomainSpecificValue"),
    ]


@dataclass
class CategoryDomainFields(MaintainableBase):
    """A response domain capturing a category (without an attached code) response for a question item. Includes standard response domain elements; OutParameter, designation of response cardinality, and a dec"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CategoryDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    category_scheme_reference: Optional[Reference] = None  # [1..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "category_scheme_reference": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class CellCoordinatesAsDefinedFields(MaintainableBase):
    """Defines one or more cells by defining the applicable values of each dimension as "all values", a "specific value" or a range. For example in a simple 2 dimensional grid where dimension rank-1 is displ"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CellCoordinatesAsDefined")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    select_dimensions: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "select_dimensions": (qn(DATA_COLLECTION_NS, "SelectDimension"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "SelectDimension"),
    ]


@dataclass
class CellLabelFields(MaintainableBase):
    """Provide a label to be included inside of a grid cell and defines the cell or cells that contain it. Supports multiple language versions of the same content as well as optional formatting of the conten"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CellLabel")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    contents: list[Element] = field(default_factory=list)  # [1..*]
    type_of_label: Optional[CodeValue] = None  # [0..1]
    grid_attachments: list[Element] = field(default_factory=list)  # [0..*]
    locationVariant: Optional[str] = None  # @attr
    validForStartDate: Optional[str] = None  # @attr
    validForEndDate: Optional[str] = None  # @attr
    maxLength: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "contents": (qn(REUSABLE_NS, "Content"), "element", True),
        "type_of_label": (qn(REUSABLE_NS, "TypeOfLabel"), "code_value", False),
        "grid_attachments": (qn(DATA_COLLECTION_NS, "GridAttachment"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "locationVariant": ("locationVariant", "str"),
        "validForStartDate": ("validForStartDate", "str"),
        "validForEndDate": ("validForEndDate", "str"),
        "maxLength": ("maxLength", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Content"),
        qn(REUSABLE_NS, "TypeOfLabel"),
        qn(DATA_COLLECTION_NS, "GridAttachment"),
    ]


@dataclass
class CodeDomainFields(MaintainableBase):
    """A response domain capturing a coded response (where both codes and their related category value are displayed) for a question. Includes standard response domain elements; OutParameter, designation of """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CodeDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    code_list_reference: Optional[Reference] = None  # [1..1]
    statistical_classification_reference: Optional[Reference] = None  # [1..1]
    code_subset_information: Optional[Element] = None  # [0..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    displayCode: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "code_list_reference": (qn(REUSABLE_NS, "CodeListReference"), "reference", False),
        "statistical_classification_reference": (qn(REUSABLE_NS, "StatisticalClassificationReference"), "reference", False),
        "code_subset_information": (qn(REUSABLE_NS, "CodeSubsetInformation"), "element", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "displayCode": ("displayCode", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "CodeListReference"),
        qn(REUSABLE_NS, "StatisticalClassificationReference"),
        qn(REUSABLE_NS, "CodeSubsetInformation"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class CognitiveExpertReviewActivityFields(MaintainableBase):
    """A substitution for DevelopmentActivity which requires no additional information other than the specification of the type of cognitive expert review taking place for development purposes."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CognitiveExpertReviewActivity")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    development_activity_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    desired_outcome: Optional[Element] = None  # [0..1]
    process_summary: Optional[Element] = None  # [0..1]
    recommended_staff_requirements: list[Element] = field(default_factory=list)  # [0..*]
    additional_required_resources: Optional[Element] = None  # [0..1]
    debriefing_process: Optional[Element] = None  # [0..1]
    type_of_cognitive_expert_review: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "development_activity_names": (qn(DATA_COLLECTION_NS, "DevelopmentActivityName"), "intl_string", True),
        "desired_outcome": (qn(DATA_COLLECTION_NS, "DesiredOutcome"), "element", False),
        "process_summary": (qn(DATA_COLLECTION_NS, "ProcessSummary"), "element", False),
        "recommended_staff_requirements": (qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"), "element", True),
        "additional_required_resources": (qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"), "element", False),
        "debriefing_process": (qn(DATA_COLLECTION_NS, "DebriefingProcess"), "element", False),
        "type_of_cognitive_expert_review": (qn(DATA_COLLECTION_NS, "TypeOfCognitiveExpertReview"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "DevelopmentActivityName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DesiredOutcome"),
        qn(DATA_COLLECTION_NS, "ProcessSummary"),
        qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"),
        qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"),
        qn(DATA_COLLECTION_NS, "DebriefingProcess"),
        qn(DATA_COLLECTION_NS, "TypeOfCognitiveExpertReview"),
    ]


@dataclass
class CognitiveInterviewActivityFields(MaintainableBase):
    """A substitution for DevelopmentActivity which requires no additional information other than the specification of the type of cognitive interview review taking place for development purposes."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CognitiveInterviewActivity")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    development_activity_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    desired_outcome: Optional[Element] = None  # [0..1]
    process_summary: Optional[Element] = None  # [0..1]
    recommended_staff_requirements: list[Element] = field(default_factory=list)  # [0..*]
    additional_required_resources: Optional[Element] = None  # [0..1]
    debriefing_process: Optional[Element] = None  # [0..1]
    type_of_cognitive_interview: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "development_activity_names": (qn(DATA_COLLECTION_NS, "DevelopmentActivityName"), "intl_string", True),
        "desired_outcome": (qn(DATA_COLLECTION_NS, "DesiredOutcome"), "element", False),
        "process_summary": (qn(DATA_COLLECTION_NS, "ProcessSummary"), "element", False),
        "recommended_staff_requirements": (qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"), "element", True),
        "additional_required_resources": (qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"), "element", False),
        "debriefing_process": (qn(DATA_COLLECTION_NS, "DebriefingProcess"), "element", False),
        "type_of_cognitive_interview": (qn(DATA_COLLECTION_NS, "TypeOfCognitiveInterview"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "DevelopmentActivityName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DesiredOutcome"),
        qn(DATA_COLLECTION_NS, "ProcessSummary"),
        qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"),
        qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"),
        qn(DATA_COLLECTION_NS, "DebriefingProcess"),
        qn(DATA_COLLECTION_NS, "TypeOfCognitiveInterview"),
    ]


@dataclass
class CollectionEventFields(MaintainableBase):
    """Information on a specific data collection event including details on who was involved in data collection, the source of the data, the date and frequency of collection, mode of collection, identificati"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CollectionEvent")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    data_collector_organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    data_sources: list[Element] = field(default_factory=list)  # [0..*]
    data_collection_date: Optional[Element] = None  # [0..1]
    data_collection_frequencies: list[Element] = field(default_factory=list)  # [0..*]
    mode_of_collections: list[Element] = field(default_factory=list)  # [0..*]
    instrument_references: list[Reference] = field(default_factory=list)  # [0..*]
    collection_situations: list[Element] = field(default_factory=list)  # [0..*]
    action_to_minimize_losses: list[Element] = field(default_factory=list)  # [0..*]
    quality_statement_references: list[Reference] = field(default_factory=list)  # [0..*]
    sample_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "CollectionEventName"), "intl_string", True),
        "data_collector_organization_references": (qn(DATA_COLLECTION_NS, "DataCollectorOrganizationReference"), "reference", True),
        "data_sources": (qn(DATA_COLLECTION_NS, "DataSource"), "element", True),
        "data_collection_date": (qn(DATA_COLLECTION_NS, "DataCollectionDate"), "element", False),
        "data_collection_frequencies": (qn(DATA_COLLECTION_NS, "DataCollectionFrequency"), "element", True),
        "mode_of_collections": (qn(DATA_COLLECTION_NS, "ModeOfCollection"), "element", True),
        "instrument_references": (qn(DATA_COLLECTION_NS, "InstrumentReference"), "reference", True),
        "collection_situations": (qn(DATA_COLLECTION_NS, "CollectionSituation"), "element", True),
        "action_to_minimize_losses": (qn(DATA_COLLECTION_NS, "ActionToMinimizeLosses"), "element", True),
        "quality_statement_references": (qn(REUSABLE_NS, "QualityStatementReference"), "reference", True),
        "sample_references": (qn(DATA_COLLECTION_NS, "SampleReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "CollectionEventName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DataCollectorOrganizationReference"),
        qn(DATA_COLLECTION_NS, "DataSource"),
        qn(DATA_COLLECTION_NS, "DataCollectionDate"),
        qn(DATA_COLLECTION_NS, "DataCollectionFrequency"),
        qn(DATA_COLLECTION_NS, "ModeOfCollection"),
        qn(DATA_COLLECTION_NS, "InstrumentReference"),
        qn(DATA_COLLECTION_NS, "CollectionSituation"),
        qn(DATA_COLLECTION_NS, "ActionToMinimizeLosses"),
        qn(REUSABLE_NS, "QualityStatementReference"),
        qn(DATA_COLLECTION_NS, "SampleReference"),
    ]


@dataclass
class CollectionSituationFields(MaintainableBase):
    """Describes the situation in which the data collection event takes place."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CollectionSituation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_collection_situation: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_collection_situation": (qn(DATA_COLLECTION_NS, "TypeOfCollectionSituation"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "TypeOfCollectionSituation"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class ComputationItemFields(MaintainableBase):
    """A form of control construct providing a code and assigning a variable to hold value of the code as used for computation in control construct flow. Member of the ControlConstruct substitution group."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ComputationItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    type_of_computation_item: Optional[CodeValue] = None  # [0..1]
    command_code: Optional[Element] = None  # [0..1]
    assigned_variable_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "type_of_computation_item": (qn(DATA_COLLECTION_NS, "TypeOfComputationItem"), "code_value", False),
        "command_code": (qn(REUSABLE_NS, "CommandCode"), "element", False),
        "assigned_variable_reference": (qn(DATA_COLLECTION_NS, "AssignedVariableReference"), "reference", False),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "TypeOfComputationItem"),
        qn(REUSABLE_NS, "CommandCode"),
        qn(DATA_COLLECTION_NS, "AssignedVariableReference"),
    ]


@dataclass
class ConditionalResultFields(MaintainableBase):
    """The text resulting from the conditional command. Supports structured content and the insertion of content by a source parameter. For example if a language has gender specific verb structures the resul"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ConditionalResult")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    texts: list[Element] = field(default_factory=list)  # [1..*]
    source_parameter_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "texts": (qn(DATA_COLLECTION_NS, "Text"), "element", True),
        "source_parameter_reference": (qn(REUSABLE_NS, "SourceParameterReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "Text"),
        qn(REUSABLE_NS, "SourceParameterReference"),
    ]


@dataclass
class ConditionalTextFields(MaintainableBase):
    """Text which has a changeable value depending on a stated condition, response to earlier questions, or as input from a set of metrics (pre-supplied data)."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ConditionalText")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    expression: Optional[Element] = None  # [1..1]
    if_then_else_text: Optional[Element] = None  # [1..1]
    source_parameter_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "expression": (qn(DATA_COLLECTION_NS, "Expression"), "element", False),
        "if_then_else_text": (qn(DATA_COLLECTION_NS, "IfThenElseText"), "element", False),
        "source_parameter_reference": (qn(REUSABLE_NS, "SourceParameterReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "Expression"),
        qn(DATA_COLLECTION_NS, "IfThenElseText"),
        qn(REUSABLE_NS, "SourceParameterReference"),
    ]


@dataclass
class ContentReviewActivityFields(MaintainableBase):
    """A substitution for DevelopmentActivity which requires no additional information other than the specification of the type of content review taking place for development purposes."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ContentReviewActivity")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    development_activity_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    desired_outcome: Optional[Element] = None  # [0..1]
    process_summary: Optional[Element] = None  # [0..1]
    recommended_staff_requirements: list[Element] = field(default_factory=list)  # [0..*]
    additional_required_resources: Optional[Element] = None  # [0..1]
    debriefing_process: Optional[Element] = None  # [0..1]
    type_of_content_review: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "development_activity_names": (qn(DATA_COLLECTION_NS, "DevelopmentActivityName"), "intl_string", True),
        "desired_outcome": (qn(DATA_COLLECTION_NS, "DesiredOutcome"), "element", False),
        "process_summary": (qn(DATA_COLLECTION_NS, "ProcessSummary"), "element", False),
        "recommended_staff_requirements": (qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"), "element", True),
        "additional_required_resources": (qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"), "element", False),
        "debriefing_process": (qn(DATA_COLLECTION_NS, "DebriefingProcess"), "element", False),
        "type_of_content_review": (qn(DATA_COLLECTION_NS, "TypeOfContentReview"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "DevelopmentActivityName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DesiredOutcome"),
        qn(DATA_COLLECTION_NS, "ProcessSummary"),
        qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"),
        qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"),
        qn(DATA_COLLECTION_NS, "DebriefingProcess"),
        qn(DATA_COLLECTION_NS, "TypeOfContentReview"),
    ]


@dataclass
class ControlConstructGroupFields(MaintainableBase):
    """Contains a group of ControlConstructs, which may describe an ordered or hierarchical relationship structure. Specifies the purpose of the group, a name, label, and description of the group, its relati"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ControlConstructGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_control_construct_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    control_construct_references: list[Reference] = field(default_factory=list)  # [0..*]
    control_construct_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_control_construct_group": (qn(DATA_COLLECTION_NS, "TypeOfControlConstructGroup"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "ControlConstructGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "control_construct_references": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", True),
        "control_construct_group_references": (qn(DATA_COLLECTION_NS, "ControlConstructGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfControlConstructGroup"),
        qn(DATA_COLLECTION_NS, "ControlConstructGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
        qn(DATA_COLLECTION_NS, "ControlConstructGroupReference"),
    ]


@dataclass
class ControlConstructSchemeFields(MaintainableBase):
    """A set of control constructs maintained by an agency and used in the instrument or computational instruction. ControlConstructs describe the ordering and flow of questions within an instrument or infor"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ControlConstructScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    control_construct_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    control_constructs: list[Element] = field(default_factory=list)  # [0..*]
    control_construct_references: list[Reference] = field(default_factory=list)  # [0..*]
    control_construct_groups: list[Element] = field(default_factory=list)  # [0..*]
    control_construct_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "ControlConstructSchemeName"), "intl_string", True),
        "control_construct_scheme_references": (qn(REUSABLE_NS, "ControlConstructSchemeReference"), "reference", True),
        "control_constructs": (qn(DATA_COLLECTION_NS, "ControlConstruct"), "element", True),
        "control_construct_references": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", True),
        "control_construct_groups": (qn(DATA_COLLECTION_NS, "ControlConstructGroup"), "element", True),
        "control_construct_group_references": (qn(DATA_COLLECTION_NS, "ControlConstructGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "ControlConstructSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ControlConstructSchemeReference"),
        qn(DATA_COLLECTION_NS, "ControlConstruct"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
        qn(DATA_COLLECTION_NS, "ControlConstructGroup"),
        qn(DATA_COLLECTION_NS, "ControlConstructGroupReference"),
    ]


@dataclass
class ControlConstructFields(MaintainableBase):
    """Provides the basic, extensible structure for control elements used in describing flow logic within the instrument. The only data point which is inherited by the extended constructs based on this type """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ControlConstruct")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
    ]


@dataclass
class CostStructureFields(MaintainableBase):
    """Budget and funding information related to the development work."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CostStructure")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    budgets: list[Element] = field(default_factory=list)  # [0..*]
    funding_informations: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "budgets": (qn(REUSABLE_NS, "Budget"), "element", True),
        "funding_informations": (qn(REUSABLE_NS, "FundingInformation"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Budget"),
        qn(REUSABLE_NS, "FundingInformation"),
    ]


@dataclass
class CreateSummaryFields(MaintainableBase):
    """Note that this is generally usable only with single valid response domain in grid. More complex uses should be carefully documented using details in CommandCode and Input/output Parameters."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CreateSummary")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    commands: list[Element] = field(default_factory=list)  # [0..*]
    command_files: list[Element] = field(default_factory=list)  # [0..*]
    structured_command: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "commands": (qn(REUSABLE_NS, "Command"), "element", True),
        "command_files": (qn(REUSABLE_NS, "CommandFile"), "element", True),
        "structured_command": (qn(REUSABLE_NS, "StructuredCommand"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Command"),
        qn(REUSABLE_NS, "CommandFile"),
        qn(REUSABLE_NS, "StructuredCommand"),
        qn(REUSABLE_NS, "Label"),
    ]


@dataclass
class DataAppraisalInformationFields(MaintainableBase):
    """Describes the result of data appraisal activities as a response rate and sampling error. May also list additional appraisal processes taken as a result of the initial appraisal process."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DataAppraisalInformation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    response_rates: list[Element] = field(default_factory=list)  # [0..*]
    sampling_errors: list[Element] = field(default_factory=list)  # [0..*]
    other_appraisal_process: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "response_rates": (qn(DATA_COLLECTION_NS, "ResponseRate"), "element", True),
        "sampling_errors": (qn(DATA_COLLECTION_NS, "SamplingError"), "element", True),
        "other_appraisal_process": (qn(DATA_COLLECTION_NS, "OtherAppraisalProcess"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "ResponseRate"),
        qn(DATA_COLLECTION_NS, "SamplingError"),
        qn(DATA_COLLECTION_NS, "OtherAppraisalProcess"),
    ]


@dataclass
class DataCaptureDevelopmentFields(MaintainableBase):
    """Data capture development covers the development planning, process, and outcome for a partial or full questionnaire. Development normally included the development of the question wording, possible resp"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DataCaptureDevelopment")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    development_plans: list[Element] = field(default_factory=list)  # [0..*]
    development_plan_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_implementations: list[Element] = field(default_factory=list)  # [0..*]
    development_implementation_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results: list[Element] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "DataCaptureDevelopmentName"), "intl_string", True),
        "development_plans": (qn(DATA_COLLECTION_NS, "DevelopmentPlan"), "element", True),
        "development_plan_references": (qn(DATA_COLLECTION_NS, "DevelopmentPlanReference"), "reference", True),
        "development_implementations": (qn(DATA_COLLECTION_NS, "DevelopmentImplementation"), "element", True),
        "development_implementation_references": (qn(DATA_COLLECTION_NS, "DevelopmentImplementationReference"), "reference", True),
        "development_results": (qn(DATA_COLLECTION_NS, "DevelopmentResults"), "element", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "DataCaptureDevelopmentName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DevelopmentPlan"),
        qn(DATA_COLLECTION_NS, "DevelopmentPlanReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentImplementation"),
        qn(DATA_COLLECTION_NS, "DevelopmentImplementationReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResults"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
    ]


@dataclass
class DataCollectionFrequencyFields(MaintainableBase):
    """Documents the intended frequency of data collection, for example monthly, yearly, weekly, etc., preferably using an optional controlled vocabulary in the IntendedFrequency element. Date of first colle"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DataCollectionFrequency")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    simple_date: Optional[Element] = None  # [1..1]
    historical_date: Optional[Element] = None  # [0..1]
    start_date: Optional[Element] = None  # [1..1]
    historical_start_date: Optional[Element] = None  # [0..1]
    end_date: Optional[Element] = None  # [0..1]
    historical_end_date: Optional[Element] = None  # [0..1]
    cycle: Optional[int] = None  # [0..1]
    intended_frequency: Optional[CodeValue] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "simple_date": (qn(REUSABLE_NS, "SimpleDate"), "element", False),
        "historical_date": (qn(REUSABLE_NS, "HistoricalDate"), "element", False),
        "start_date": (qn(REUSABLE_NS, "StartDate"), "element", False),
        "historical_start_date": (qn(REUSABLE_NS, "HistoricalStartDate"), "element", False),
        "end_date": (qn(REUSABLE_NS, "EndDate"), "element", False),
        "historical_end_date": (qn(REUSABLE_NS, "HistoricalEndDate"), "element", False),
        "cycle": (qn(REUSABLE_NS, "Cycle"), "int", False),
        "intended_frequency": (qn(DATA_COLLECTION_NS, "IntendedFrequency"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "SimpleDate"),
        qn(REUSABLE_NS, "HistoricalDate"),
        qn(REUSABLE_NS, "StartDate"),
        qn(REUSABLE_NS, "HistoricalStartDate"),
        qn(REUSABLE_NS, "EndDate"),
        qn(REUSABLE_NS, "HistoricalEndDate"),
        qn(REUSABLE_NS, "Cycle"),
        qn(REUSABLE_NS, "EndDate"),
        qn(REUSABLE_NS, "HistoricalEndDate"),
        qn(DATA_COLLECTION_NS, "IntendedFrequency"),
    ]


@dataclass
class DataCollectionMethodologyFields(MaintainableBase):
    """Methodologies pertaining to the overall data collection such as primary or secondary data collection, qualitative or quantitative methods, mixed method approaches, GPS capturing methods, methods for c"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DataCollectionMethodology")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_data_collection_methodology: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_data_collection_methodology": (qn(DATA_COLLECTION_NS, "TypeOfDataCollectionMethodology"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "TypeOfDataCollectionMethodology"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class DataCollectionFields(MaintainableBase):
    """A maintainable module containing information on activities related to data collection/capture and the processing required for the creation a data product. This section covers the methodologies, events"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DataCollection")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    data_collection_module_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    coverage: Optional[Element] = None  # [0..1]
    methodology: Optional[Element] = None  # [1..1]
    methodology_reference: Optional[Reference] = None  # [1..1]
    data_capture_development: Optional[Element] = None  # [1..1]
    data_capture_development_reference: Optional[Reference] = None  # [1..1]
    collection_events: list[Element] = field(default_factory=list)  # [0..*]
    question_schemes: list[Element] = field(default_factory=list)  # [0..*]
    question_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    measurement_schemes: list[Element] = field(default_factory=list)  # [0..*]
    measurement_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    control_construct_schemes: list[Element] = field(default_factory=list)  # [0..*]
    control_construct_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    interviewer_instruction_schemes: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    instrument_schemes: list[Element] = field(default_factory=list)  # [0..*]
    instrument_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    instruments: list[Element] = field(default_factory=list)  # [0..*]
    instrument_references: list[Reference] = field(default_factory=list)  # [0..*]
    processing_event_schemes: list[Element] = field(default_factory=list)  # [0..*]
    processing_event_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    processing_instruction_schemes: list[Element] = field(default_factory=list)  # [0..*]
    processing_instruction_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
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
        "data_collection_module_names": (qn(DATA_COLLECTION_NS, "DataCollectionModuleName"), "intl_string", True),
        "coverage": (qn(REUSABLE_NS, "Coverage"), "element", False),
        "methodology": (qn(DATA_COLLECTION_NS, "Methodology"), "element", False),
        "methodology_reference": (qn(DATA_COLLECTION_NS, "MethodologyReference"), "reference", False),
        "data_capture_development": (qn(DATA_COLLECTION_NS, "DataCaptureDevelopment"), "element", False),
        "data_capture_development_reference": (qn(DATA_COLLECTION_NS, "DataCaptureDevelopmentReference"), "reference", False),
        "collection_events": (qn(DATA_COLLECTION_NS, "CollectionEvent"), "element", True),
        "question_schemes": (qn(DATA_COLLECTION_NS, "QuestionScheme"), "element", True),
        "question_scheme_references": (qn(REUSABLE_NS, "QuestionSchemeReference"), "reference", True),
        "measurement_schemes": (qn(DATA_COLLECTION_NS, "MeasurementScheme"), "element", True),
        "measurement_scheme_references": (qn(REUSABLE_NS, "MeasurementSchemeReference"), "reference", True),
        "control_construct_schemes": (qn(DATA_COLLECTION_NS, "ControlConstructScheme"), "element", True),
        "control_construct_scheme_references": (qn(REUSABLE_NS, "ControlConstructSchemeReference"), "reference", True),
        "interviewer_instruction_schemes": (qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme"), "element", True),
        "interviewer_instruction_scheme_references": (qn(REUSABLE_NS, "InterviewerInstructionSchemeReference"), "reference", True),
        "instrument_schemes": (qn(DATA_COLLECTION_NS, "InstrumentScheme"), "element", True),
        "instrument_scheme_references": (qn(REUSABLE_NS, "InstrumentSchemeReference"), "reference", True),
        "instruments": (qn(DATA_COLLECTION_NS, "Instrument"), "element", True),
        "instrument_references": (qn(DATA_COLLECTION_NS, "InstrumentReference"), "reference", True),
        "processing_event_schemes": (qn(DATA_COLLECTION_NS, "ProcessingEventScheme"), "element", True),
        "processing_event_scheme_references": (qn(DATA_COLLECTION_NS, "ProcessingEventSchemeReference"), "reference", True),
        "processing_instruction_schemes": (qn(DATA_COLLECTION_NS, "ProcessingInstructionScheme"), "element", True),
        "processing_instruction_scheme_references": (qn(DATA_COLLECTION_NS, "ProcessingInstructionSchemeReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "DataCollectionModuleName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Coverage"),
        qn(DATA_COLLECTION_NS, "Methodology"),
        qn(DATA_COLLECTION_NS, "MethodologyReference"),
        qn(DATA_COLLECTION_NS, "DataCaptureDevelopment"),
        qn(DATA_COLLECTION_NS, "DataCaptureDevelopmentReference"),
        qn(DATA_COLLECTION_NS, "CollectionEvent"),
        qn(DATA_COLLECTION_NS, "QuestionScheme"),
        qn(REUSABLE_NS, "QuestionSchemeReference"),
        qn(DATA_COLLECTION_NS, "MeasurementScheme"),
        qn(REUSABLE_NS, "MeasurementSchemeReference"),
        qn(DATA_COLLECTION_NS, "ControlConstructScheme"),
        qn(REUSABLE_NS, "ControlConstructSchemeReference"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme"),
        qn(REUSABLE_NS, "InterviewerInstructionSchemeReference"),
        qn(DATA_COLLECTION_NS, "InstrumentScheme"),
        qn(REUSABLE_NS, "InstrumentSchemeReference"),
        qn(DATA_COLLECTION_NS, "Instrument"),
        qn(DATA_COLLECTION_NS, "InstrumentReference"),
        qn(DATA_COLLECTION_NS, "ProcessingEventScheme"),
        qn(DATA_COLLECTION_NS, "ProcessingEventSchemeReference"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionScheme"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionSchemeReference"),
        qn(DATA_COLLECTION_NS, "SamplingInformationScheme"),
        qn(REUSABLE_NS, "SamplingInformationSchemeReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityScheme"),
        qn(REUSABLE_NS, "DevelopmentActivitySchemeReference"),
    ]


@dataclass
class DataSourceFields(MaintainableBase):
    """Describes the source of the data. This may be a population group, an environmental object, a registry, published or unpublished data source, etc. Describes and provides a classification of the source,"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DataSource")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    source_description: Optional[Element] = None  # [0..1]
    source_types: list[CodeValue] = field(default_factory=list)  # [0..*]
    origins: list[Element] = field(default_factory=list)  # [0..*]
    source_characteristic: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "source_description": (qn(DATA_COLLECTION_NS, "SourceDescription"), "element", False),
        "source_types": (qn(DATA_COLLECTION_NS, "SourceType"), "code_value", True),
        "origins": (qn(DATA_COLLECTION_NS, "Origin"), "element", True),
        "source_characteristic": (qn(DATA_COLLECTION_NS, "SourceCharacteristic"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "SourceDescription"),
        qn(DATA_COLLECTION_NS, "SourceType"),
        qn(DATA_COLLECTION_NS, "Origin"),
        qn(DATA_COLLECTION_NS, "SourceCharacteristic"),
    ]


@dataclass
class DateTimeDomainFields(MaintainableBase):
    """A response domain capturing a date or time response for a question item. Contains the equivalent content of a DateTimeRepresentation including the format of the date field, a DateTypeCode, and restric"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DateTimeDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    date_field_format: Optional[CodeValue] = None  # [0..1]
    date_type_code: Optional[CodeValue] = None  # [1..1]
    ranges: list[Element] = field(default_factory=list)  # [0..*]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    regExp: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "date_field_format": (qn(REUSABLE_NS, "DateFieldFormat"), "code_value", False),
        "date_type_code": (qn(REUSABLE_NS, "DateTypeCode"), "code_value", False),
        "ranges": (qn(REUSABLE_NS, "Range"), "element", True),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "regExp": ("regExp", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "DateFieldFormat"),
        qn(REUSABLE_NS, "DateTypeCode"),
        qn(REUSABLE_NS, "Range"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class DebriefingProcessFields(MaintainableBase):
    """Describe the debriefing process. Specifies if debriefing is required."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DebriefingProcess")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    isRequired: Optional[bool] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isRequired": ("isRequired", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class DevelopmentActivityGroupFields(MaintainableBase):
    """Describes a group of Development Activities for administrative or conceptual purposes, which may be hierarchical. In addition to the standard name, label, and description contains references to includ"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DevelopmentActivityGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_development_activity_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    development_activity_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_activity_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_development_activity_group": (qn(DATA_COLLECTION_NS, "TypeOfDevelopmentActivityGroup"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "DevelopmentActivityGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "development_activity_references": (qn(DATA_COLLECTION_NS, "DevelopmentActivityReference"), "reference", True),
        "development_activity_group_references": (qn(DATA_COLLECTION_NS, "DevelopmentActivityGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfDevelopmentActivityGroup"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityGroupReference"),
    ]


@dataclass
class DevelopmentActivitySchemeFields(MaintainableBase):
    """A set of Development Activities maintained by an agency, and used in defining the development of a data capture object. In addition to the standard name, label, and description allows for the inclusio"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DevelopmentActivityScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    development_activity_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_activities: list[Element] = field(default_factory=list)  # [0..*]
    development_activity_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_activity_groups: list[Element] = field(default_factory=list)  # [0..*]
    development_activity_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "DevelopmentActivitySchemeName"), "intl_string", True),
        "development_activity_scheme_references": (qn(REUSABLE_NS, "DevelopmentActivitySchemeReference"), "reference", True),
        "development_activities": (qn(DATA_COLLECTION_NS, "DevelopmentActivity"), "element", True),
        "development_activity_references": (qn(DATA_COLLECTION_NS, "DevelopmentActivityReference"), "reference", True),
        "development_activity_groups": (qn(DATA_COLLECTION_NS, "DevelopmentActivityGroup"), "element", True),
        "development_activity_group_references": (qn(DATA_COLLECTION_NS, "DevelopmentActivityGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "DevelopmentActivitySchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "DevelopmentActivitySchemeReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivity"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityGroup"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityGroupReference"),
    ]


@dataclass
class DevelopmentActivityFields(MaintainableBase):
    """An abstract element serving as the head of a substitution group. May be substituted by an valid object of substitution type DevelopmentActivity. Provides a set of objects available to all members of t"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DevelopmentActivity")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    desired_outcome: Optional[Element] = None  # [0..1]
    process_summary: Optional[Element] = None  # [0..1]
    recommended_staff_requirements: list[Element] = field(default_factory=list)  # [0..*]
    additional_required_resources: Optional[Element] = None  # [0..1]
    debriefing_process: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "DevelopmentActivityName"), "intl_string", True),
        "desired_outcome": (qn(DATA_COLLECTION_NS, "DesiredOutcome"), "element", False),
        "process_summary": (qn(DATA_COLLECTION_NS, "ProcessSummary"), "element", False),
        "recommended_staff_requirements": (qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"), "element", True),
        "additional_required_resources": (qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"), "element", False),
        "debriefing_process": (qn(DATA_COLLECTION_NS, "DebriefingProcess"), "element", False),
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
        qn(DATA_COLLECTION_NS, "DevelopmentActivityName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DesiredOutcome"),
        qn(DATA_COLLECTION_NS, "ProcessSummary"),
        qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"),
        qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"),
        qn(DATA_COLLECTION_NS, "DebriefingProcess"),
    ]


@dataclass
class DevelopmentImplementationFields(MaintainableBase):
    """Provides a name, label and description for the Development Implementation and lists the individual development activities which should take place. Note that the structure allows for a simple summary o"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DevelopmentImplementation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    development_plan_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_activity_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_objects: list[Element] = field(default_factory=list)  # [0..*]
    control_construct_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "DevelopmentImplementationName"), "intl_string", True),
        "development_plan_references": (qn(DATA_COLLECTION_NS, "DevelopmentPlanReference"), "reference", True),
        "development_activity_references": (qn(DATA_COLLECTION_NS, "DevelopmentActivityReference"), "reference", True),
        "development_objects": (qn(DATA_COLLECTION_NS, "DevelopmentObject"), "element", True),
        "control_construct_references": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "DevelopmentImplementationName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DevelopmentPlanReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentObject"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
    ]


@dataclass
class DevelopmentObjectFields(MaintainableBase):
    """A description of the development objects of a Development Implementation or Development Step. Supports a general description as well as specific references to allowed development objects."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DevelopmentObject")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    question_references: list[Reference] = field(default_factory=list)  # [0..*]
    measurement_references: list[Reference] = field(default_factory=list)  # [0..*]
    instrument_references: list[Reference] = field(default_factory=list)  # [0..*]
    control_construct_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "question_references": (qn(REUSABLE_NS, "QuestionReference"), "reference", True),
        "measurement_references": (qn(REUSABLE_NS, "MeasurementReference"), "reference", True),
        "instrument_references": (qn(DATA_COLLECTION_NS, "InstrumentReference"), "reference", True),
        "control_construct_references": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "QuestionReference"),
        qn(REUSABLE_NS, "MeasurementReference"),
        qn(DATA_COLLECTION_NS, "InstrumentReference"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
    ]


@dataclass
class DevelopmentPlanFields(MaintainableBase):
    """Provides a name, label and description for the Development Plan and lists the individual development activities which should take place."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DevelopmentPlan")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    development_objective: Optional[Element] = None  # [0..1]
    contact_references: list[Reference] = field(default_factory=list)  # [0..*]
    cost_structures: list[Element] = field(default_factory=list)  # [0..*]
    development_activity_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "DevelopmentPlanName"), "intl_string", True),
        "development_objective": (qn(DATA_COLLECTION_NS, "DevelopmentObjective"), "element", False),
        "contact_references": (qn(DATA_COLLECTION_NS, "ContactReference"), "reference", True),
        "cost_structures": (qn(DATA_COLLECTION_NS, "CostStructure"), "element", True),
        "development_activity_references": (qn(DATA_COLLECTION_NS, "DevelopmentActivityReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "DevelopmentPlanName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DevelopmentObjective"),
        qn(DATA_COLLECTION_NS, "ContactReference"),
        qn(DATA_COLLECTION_NS, "CostStructure"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityReference"),
    ]


@dataclass
class DevelopmentResultsFields(MaintainableBase):
    """Separates the capture of development implementation results from the process plan and general activities. Allows for capture of the overall results, details of individual steps, or separate iterations"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DevelopmentResults")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    development_implementation_references: list[Reference] = field(default_factory=list)  # [0..*]
    results_date: Optional[Element] = None  # [0..1]
    result_details: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "DevelopmentResultsName"), "intl_string", True),
        "development_implementation_references": (qn(DATA_COLLECTION_NS, "DevelopmentImplementationReference"), "reference", True),
        "results_date": (qn(DATA_COLLECTION_NS, "ResultsDate"), "element", False),
        "result_details": (qn(DATA_COLLECTION_NS, "ResultDetail"), "element", True),
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
        qn(DATA_COLLECTION_NS, "DevelopmentResultsName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DevelopmentImplementationReference"),
        qn(DATA_COLLECTION_NS, "ResultsDate"),
        qn(DATA_COLLECTION_NS, "ResultDetail"),
    ]


@dataclass
class DevelopmentStepFields(MaintainableBase):
    """A member of the ControlConstruct substitution group. Describes a Development Step implementing a Development Activity directed at a specific development object. Defines prerequisites, condition for ac"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DevelopmentStep")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_objects: list[Element] = field(default_factory=list)  # [0..*]
    development_activity_references: list[Reference] = field(default_factory=list)  # [0..*]
    responsible_agency_references: list[Reference] = field(default_factory=list)  # [0..*]
    prerequisites: list[Element] = field(default_factory=list)  # [0..*]
    condition_for_acceptances: list[Element] = field(default_factory=list)  # [0..*]
    activity_date: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "development_objects": (qn(DATA_COLLECTION_NS, "DevelopmentObject"), "element", True),
        "development_activity_references": (qn(DATA_COLLECTION_NS, "DevelopmentActivityReference"), "reference", True),
        "responsible_agency_references": (qn(DATA_COLLECTION_NS, "ResponsibleAgencyReference"), "reference", True),
        "prerequisites": (qn(DATA_COLLECTION_NS, "Prerequisite"), "element", True),
        "condition_for_acceptances": (qn(DATA_COLLECTION_NS, "ConditionForAcceptance"), "element", True),
        "activity_date": (qn(DATA_COLLECTION_NS, "ActivityDate"), "element", False),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentObject"),
        qn(DATA_COLLECTION_NS, "DevelopmentActivityReference"),
        qn(DATA_COLLECTION_NS, "ResponsibleAgencyReference"),
        qn(DATA_COLLECTION_NS, "Prerequisite"),
        qn(DATA_COLLECTION_NS, "ConditionForAcceptance"),
        qn(DATA_COLLECTION_NS, "ActivityDate"),
    ]


@dataclass
class DeviationFromSampleDesignFields(MaintainableBase):
    """Describes any deviations from the planned sample design. These may be for reasons of practicality, implementation issues, or other reasons. In addition to a narrative description allows for use of a b"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DeviationFromSampleDesign")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_deviation_from_sample_design: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_deviation_from_sample_design": (qn(DATA_COLLECTION_NS, "TypeOfDeviationFromSampleDesign"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "TypeOfDeviationFromSampleDesign"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class DistributionDomainFields(MaintainableBase):
    """A response domain capturing a distribution response for a question item. Includes standard response domain elements; OutParameter, designation of response cardinality, and a declaration of an offset d"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DistributionDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    distribution_value: Optional[float] = None  # [1..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    decimalPositions: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "distribution_value": (qn(REUSABLE_NS, "DistributionValue"), "float", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "decimalPositions": ("decimalPositions", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "DistributionValue"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class DomainReferenceFields(MaintainableBase):
    """Abstract type for the head of a substitution group that allows for the use of a response domain by reference. If specific values are used to denote missing values, these can be indicated as a space-de"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DomainReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_object: Optional[Element] = None  # [1..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
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
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class DomainSpecificValueFields(MaintainableBase):
    """Identifies the value of the ResponseDomain to which the new ResponseDomain is attached by specifying its attachmentBase number of the target ResponseDomain in the attribute attachmentDomain. Specifies"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DomainSpecificValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    values: list[Element] = field(default_factory=list)  # [1..*]
    attachmentDomain: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "values": (qn(REUSABLE_NS, "Value"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "attachmentDomain": ("attachmentDomain", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Value"),
    ]


@dataclass
class DynamicTextFields(MaintainableBase):
    """Structure supporting the use of dynamic text, where portions of the textual contend change depending on external information (pre-loaded data, response to an earlier query, environmental situations, e"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DynamicText")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    text_contents: list[Element] = field(default_factory=list)  # [1..*]
    isStructureRequired: Optional[bool] = None  # @attr
    audienceLanguage: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "text_contents": (qn(DATA_COLLECTION_NS, "TextContent"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isStructureRequired": ("isStructureRequired", "bool"),
        "audienceLanguage": ("audienceLanguage", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "TextContent"),
    ]


@dataclass
class ElseIfTextFields(MaintainableBase):
    """Use for multiple branching from a single point in the flow logic represented by the flow logic If, Then, ElseIf, Then, etc. This is a packaging element for an IfCondition and ThenConstructReference an"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ElseIfText")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    if_condition: Optional[Element] = None  # [0..1]
    then_result: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "if_condition": (qn(DATA_COLLECTION_NS, "IfCondition"), "element", False),
        "then_result": (qn(DATA_COLLECTION_NS, "ThenResult"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "IfCondition"),
        qn(DATA_COLLECTION_NS, "ThenResult"),
    ]


@dataclass
class ElseIfFields(MaintainableBase):
    """Use for multiple branching from a single point in the flow logic represented by the flow logic If, Then, ElseIf, Then, etc. This is a packaging element for an IfCondition and ThenConstructReference an"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ElseIf")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    if_condition: Optional[Element] = None  # [0..1]
    then_construct_reference: Optional[Reference] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "if_condition": (qn(DATA_COLLECTION_NS, "IfCondition"), "element", False),
        "then_construct_reference": (qn(DATA_COLLECTION_NS, "ThenConstructReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "IfCondition"),
        qn(DATA_COLLECTION_NS, "ThenConstructReference"),
    ]


@dataclass
class ExternalAidFields(MaintainableBase):
    """Description and link to the External Aid using the DDI Other Material structure."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ExternalAid")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    other_material: Optional[Element] = None  # [1..1]
    other_material_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "other_material": (qn(REUSABLE_NS, "OtherMaterial"), "element", False),
        "other_material_reference": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
    ]


@dataclass
class ExternalInformationFields(MaintainableBase):
    """Description and link to the External Information using the DDI Other Material structure."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ExternalInformation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    other_material: Optional[Element] = None  # [1..1]
    other_material_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "other_material": (qn(REUSABLE_NS, "OtherMaterial"), "element", False),
        "other_material_reference": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
    ]


@dataclass
class ExternalInterviewerInstructionFields(MaintainableBase):
    """Specification of an external interviewer instruction not structured in DDI. Uses the structure of OtherMaterial to provide a citation, description, and locator for the object."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    other_material: Optional[Element] = None  # [1..1]
    other_material_reference: Optional[Reference] = None  # [1..1]
    instruction_attachment_locations: list[Element] = field(default_factory=list)  # [0..*]
    isDisplayed: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "other_material": (qn(REUSABLE_NS, "OtherMaterial"), "element", False),
        "other_material_reference": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", False),
        "instruction_attachment_locations": (qn(DATA_COLLECTION_NS, "InstructionAttachmentLocation"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isDisplayed": ("isDisplayed", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
        qn(DATA_COLLECTION_NS, "InstructionAttachmentLocation"),
    ]


@dataclass
class FixedCellValueFields(MaintainableBase):
    """Provides the ability to fix the value of a grid cell and defines the cell or cells. Designates the fixed value to be used and the location of the cell or cells within the grid."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "FixedCellValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    value: Optional[Element] = None  # [0..1]
    grid_attachments: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "value": (qn(REUSABLE_NS, "Value"), "element", False),
        "grid_attachments": (qn(DATA_COLLECTION_NS, "GridAttachment"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Value"),
        qn(DATA_COLLECTION_NS, "GridAttachment"),
    ]


@dataclass
class FocusGroupActivityFields(MaintainableBase):
    """A substitution for DevelopmentActivity which requires no additional information other than the specification of the type of Focus Group taking place for development purposes."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "FocusGroupActivity")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    development_activity_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    desired_outcome: Optional[Element] = None  # [0..1]
    process_summary: Optional[Element] = None  # [0..1]
    recommended_staff_requirements: list[Element] = field(default_factory=list)  # [0..*]
    additional_required_resources: Optional[Element] = None  # [0..1]
    debriefing_process: Optional[Element] = None  # [0..1]
    type_of_focus_group: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "development_activity_names": (qn(DATA_COLLECTION_NS, "DevelopmentActivityName"), "intl_string", True),
        "desired_outcome": (qn(DATA_COLLECTION_NS, "DesiredOutcome"), "element", False),
        "process_summary": (qn(DATA_COLLECTION_NS, "ProcessSummary"), "element", False),
        "recommended_staff_requirements": (qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"), "element", True),
        "additional_required_resources": (qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"), "element", False),
        "debriefing_process": (qn(DATA_COLLECTION_NS, "DebriefingProcess"), "element", False),
        "type_of_focus_group": (qn(DATA_COLLECTION_NS, "TypeOfFocusGroup"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "DevelopmentActivityName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DesiredOutcome"),
        qn(DATA_COLLECTION_NS, "ProcessSummary"),
        qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"),
        qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"),
        qn(DATA_COLLECTION_NS, "DebriefingProcess"),
        qn(DATA_COLLECTION_NS, "TypeOfFocusGroup"),
    ]


@dataclass
class GeneralInstructionFields(MaintainableBase):
    """Processing instructions that pertain to data collection or data processing overall such as handling of non-response to questions, imputation practices, suppression rules, etc. General instructions sho"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GeneralInstruction")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    command_codes: list[Element] = field(default_factory=list)  # [0..*]
    overridden_code_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOverride: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "command_codes": (qn(REUSABLE_NS, "CommandCode"), "element", True),
        "overridden_code_reference": (qn(DATA_COLLECTION_NS, "OverriddenCodeReference"), "reference", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "isOverride": ("isOverride", "bool"),
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
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "CommandCode"),
        qn(DATA_COLLECTION_NS, "OverriddenCodeReference"),
    ]


@dataclass
class GenerationInstructionFields(MaintainableBase):
    """Processing instructions for recodes, derivations from multiple question or variable sources, and derivations based on external sources. Instructions should be listed separately so they can be referenc"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GenerationInstruction")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    input_question_references: list[Reference] = field(default_factory=list)  # [0..*]
    input_measurement_references: list[Reference] = field(default_factory=list)  # [0..*]
    input_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    external_informations: list[Element] = field(default_factory=list)  # [0..*]
    command_codes: list[Element] = field(default_factory=list)  # [0..*]
    control_construct_references: list[Reference] = field(default_factory=list)  # [0..*]
    aggregation: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isDerived: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "input_question_references": (qn(DATA_COLLECTION_NS, "InputQuestionReference"), "reference", True),
        "input_measurement_references": (qn(DATA_COLLECTION_NS, "InputMeasurementReference"), "reference", True),
        "input_variable_references": (qn(DATA_COLLECTION_NS, "InputVariableReference"), "reference", True),
        "external_informations": (qn(DATA_COLLECTION_NS, "ExternalInformation"), "element", True),
        "command_codes": (qn(REUSABLE_NS, "CommandCode"), "element", True),
        "control_construct_references": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", True),
        "aggregation": (qn(DATA_COLLECTION_NS, "Aggregation"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "isDerived": ("isDerived", "bool"),
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
        qn(DATA_COLLECTION_NS, "InputQuestionReference"),
        qn(DATA_COLLECTION_NS, "InputMeasurementReference"),
        qn(DATA_COLLECTION_NS, "InputVariableReference"),
        qn(DATA_COLLECTION_NS, "ExternalInformation"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "CommandCode"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
        qn(DATA_COLLECTION_NS, "Aggregation"),
    ]


@dataclass
class GeographicDomainFields(MaintainableBase):
    """Structures the response domain for a geographic point to ensure collection of relevant information. The point may be associated with a polygon (such as the centroid of the polygon) or a line (end or s"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GeographicDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    datum: Optional[CodeValue] = None  # [1..1]
    coordinate_system: Optional[CodeValue] = None  # [1..1]
    coordinate_zone: Optional[CodeValue] = None  # [0..1]
    coordinate_source: Optional[CodeValue] = None  # [1..1]
    error_correction: Optional[CodeValue] = None  # [1..1]
    offset: Optional[str] = None  # [1..1]
    georeferenced_object: Optional[CodeValue] = None  # [1..1]
    address_match_type: Optional[CodeValue] = None  # [0..1]
    coordinate_pairs: list[Element] = field(default_factory=list)  # [1..*]
    alternate_offset: Optional[Element] = None  # [0..1]
    alternate_object: Optional[Element] = None  # [0..1]
    alternate_coordinate_system: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    pointFormat: Optional[str] = None  # @attr
    spatialPrimitive: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "datum": (qn(REUSABLE_NS, "Datum"), "code_value", False),
        "coordinate_system": (qn(REUSABLE_NS, "CoordinateSystem"), "code_value", False),
        "coordinate_zone": (qn(REUSABLE_NS, "CoordinateZone"), "code_value", False),
        "coordinate_source": (qn(REUSABLE_NS, "CoordinateSource"), "code_value", False),
        "error_correction": (qn(REUSABLE_NS, "ErrorCorrection"), "code_value", False),
        "offset": (qn(REUSABLE_NS, "Offset"), "str", False),
        "georeferenced_object": (qn(REUSABLE_NS, "GeoreferencedObject"), "code_value", False),
        "address_match_type": (qn(REUSABLE_NS, "AddressMatchType"), "code_value", False),
        "coordinate_pairs": (qn(REUSABLE_NS, "CoordinatePairs"), "element", True),
        "alternate_offset": (qn(REUSABLE_NS, "AlternateOffset"), "element", False),
        "alternate_object": (qn(REUSABLE_NS, "AlternateObject"), "element", False),
        "alternate_coordinate_system": (qn(REUSABLE_NS, "AlternateCoordinateSystem"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "pointFormat": ("pointFormat", "str"),
        "spatialPrimitive": ("spatialPrimitive", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "Datum"),
        qn(REUSABLE_NS, "CoordinateSystem"),
        qn(REUSABLE_NS, "CoordinateZone"),
        qn(REUSABLE_NS, "CoordinateSource"),
        qn(REUSABLE_NS, "ErrorCorrection"),
        qn(REUSABLE_NS, "Offset"),
        qn(REUSABLE_NS, "GeoreferencedObject"),
        qn(REUSABLE_NS, "AddressMatchType"),
        qn(REUSABLE_NS, "CoordinatePairs"),
        qn(REUSABLE_NS, "AlternateOffset"),
        qn(REUSABLE_NS, "AlternateObject"),
        qn(REUSABLE_NS, "AlternateCoordinateSystem"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class GeographicLocationCodeDomainFields(MaintainableBase):
    """A response domain capturing the name or code of a Geographic Location as a response for a question item. Includes standard response domain elements; OutParameter, designation of response cardinality, """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GeographicLocationCodeDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    included_geographic_location_codes: Optional[Element] = None  # [0..1]
    limited_code_segment_captured: Optional[Element] = None  # [0..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    displayCode: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "included_geographic_location_codes": (qn(REUSABLE_NS, "IncludedGeographicLocationCodes"), "element", False),
        "limited_code_segment_captured": (qn(REUSABLE_NS, "LimitedCodeSegmentCaptured"), "element", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "displayCode": ("displayCode", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "IncludedGeographicLocationCodes"),
        qn(REUSABLE_NS, "LimitedCodeSegmentCaptured"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class GeographicStructureCodeDomainFields(MaintainableBase):
    """A response domain capturing a geographic structure code as a response for a question item. Includes standard response domain elements; OutParameter, designation of response cardinality, and a declarat"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GeographicStructureCodeDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    included_geographic_structure_codes: Optional[Element] = None  # [0..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    displayCode: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "included_geographic_structure_codes": (qn(REUSABLE_NS, "IncludedGeographicStructureCodes"), "element", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "displayCode": ("displayCode", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "IncludedGeographicStructureCodes"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class GridAttachmentFields(MaintainableBase):
    """Identifies the cell or cells in a grid to which the item is attached by a reference to a specific cell coordinate in a grid or by identifying a range of values along a dimension."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GridAttachment")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    specific_cell_coordinates: list[str] = field(default_factory=list)  # [0..*]
    cell_coordinates_as_defineds: list[Element] = field(default_factory=list)  # [0..*]
    allCells: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "specific_cell_coordinates": (qn(DATA_COLLECTION_NS, "SpecificCellCoordinate"), "str", True),
        "cell_coordinates_as_defineds": (qn(DATA_COLLECTION_NS, "CellCoordinatesAsDefined"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "allCells": ("allCells", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "SpecificCellCoordinate"),
        qn(DATA_COLLECTION_NS, "CellCoordinatesAsDefined"),
    ]


@dataclass
class GridDimensionFields(MaintainableBase):
    """Describes each dimension of the grid including dimension rank (for the purpose of identifying a cell address), a text for the dimension, and optional labels and codes used as column and row stubs. May"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GridDimension")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    code_domain: Optional[Element] = None  # [1..1]
    roster: Optional[Element] = None  # [1..1]
    create_summary: Optional[Element] = None  # [0..1]
    rank: Optional[int] = None  # @attr
    displayCode: Optional[bool] = None  # @attr
    displayLabel: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "code_domain": (qn(DATA_COLLECTION_NS, "CodeDomain"), "element", False),
        "roster": (qn(DATA_COLLECTION_NS, "Roster"), "element", False),
        "create_summary": (qn(DATA_COLLECTION_NS, "CreateSummary"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "rank": ("rank", "int"),
        "displayCode": ("displayCode", "bool"),
        "displayLabel": ("displayLabel", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "CodeDomain"),
        qn(DATA_COLLECTION_NS, "Roster"),
        qn(DATA_COLLECTION_NS, "CreateSummary"),
    ]


@dataclass
class GridResponseDomainInMixedFields(MaintainableBase):
    """Designates the response domain and the cells using the specified response domain within a QuestionGrid. Supports the use of ResponseAttachmentLocation and attachmentBase for defining specific relation"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GridResponseDomainInMixed")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    response_domain: Optional[Element] = None  # [1..1]
    response_domain_reference: Optional[Reference] = None  # [1..1]
    response_attachment_location: Optional[Element] = None  # [0..1]
    grid_attachments: list[Element] = field(default_factory=list)  # [0..*]
    attachmentBase: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "response_domain": (qn(DATA_COLLECTION_NS, "ResponseDomain"), "element", False),
        "response_domain_reference": (qn(DATA_COLLECTION_NS, "ResponseDomainReference"), "reference", False),
        "response_attachment_location": (qn(DATA_COLLECTION_NS, "ResponseAttachmentLocation"), "element", False),
        "grid_attachments": (qn(DATA_COLLECTION_NS, "GridAttachment"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "attachmentBase": ("attachmentBase", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "ResponseDomain"),
        qn(DATA_COLLECTION_NS, "ResponseDomainReference"),
        qn(DATA_COLLECTION_NS, "ResponseAttachmentLocation"),
        qn(DATA_COLLECTION_NS, "GridAttachment"),
    ]


@dataclass
class IfThenElseTextFields(MaintainableBase):
    """Describes an if-then-else decision type for conditional text. IF the stated condition is met, the THEN clause is trigged, otherwise the ELSE clause is triggered. Contains an IfCondition (the condition"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "IfThenElseText")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    if_condition: Optional[Element] = None  # [0..1]
    then_result: Optional[Element] = None  # [0..1]
    else_if_texts: list[Element] = field(default_factory=list)  # [0..*]
    else_result: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "if_condition": (qn(DATA_COLLECTION_NS, "IfCondition"), "element", False),
        "then_result": (qn(DATA_COLLECTION_NS, "ThenResult"), "element", False),
        "else_if_texts": (qn(DATA_COLLECTION_NS, "ElseIfText"), "element", True),
        "else_result": (qn(DATA_COLLECTION_NS, "ElseResult"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "IfCondition"),
        qn(DATA_COLLECTION_NS, "ThenResult"),
        qn(DATA_COLLECTION_NS, "ElseIfText"),
        qn(DATA_COLLECTION_NS, "ElseResult"),
    ]


@dataclass
class IfThenElseFields(MaintainableBase):
    """A member of the ControlConstruct substitution group. Describes an if-then-else decision type of control construct. IF the stated condition is met, the THEN clause is trigged, otherwise the ELSE clause"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "IfThenElse")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    type_of_if_then_else: Optional[CodeValue] = None  # [0..1]
    if_condition: Optional[Element] = None  # [0..1]
    then_construct_reference: Optional[Reference] = None  # [0..1]
    else_ifs: list[Element] = field(default_factory=list)  # [0..*]
    else_construct_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "type_of_if_then_else": (qn(DATA_COLLECTION_NS, "TypeOfIfThenElse"), "code_value", False),
        "if_condition": (qn(DATA_COLLECTION_NS, "IfCondition"), "element", False),
        "then_construct_reference": (qn(DATA_COLLECTION_NS, "ThenConstructReference"), "reference", False),
        "else_ifs": (qn(DATA_COLLECTION_NS, "ElseIf"), "element", True),
        "else_construct_reference": (qn(DATA_COLLECTION_NS, "ElseConstructReference"), "reference", False),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "TypeOfIfThenElse"),
        qn(DATA_COLLECTION_NS, "IfCondition"),
        qn(DATA_COLLECTION_NS, "ThenConstructReference"),
        qn(DATA_COLLECTION_NS, "ElseIf"),
        qn(DATA_COLLECTION_NS, "ElseConstructReference"),
    ]


@dataclass
class InstructionAttachmentLocationFields(MaintainableBase):
    """Allows attachment of an instruction to a specific item in a question structure. For example, to a Label, QuestionText, ResponseDomain, Response domain value, or grid cell."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "InstructionAttachmentLocation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    attachment_locations: list[Element] = field(default_factory=list)  # [0..*]
    grid_attachments: list[Element] = field(default_factory=list)  # [0..*]
    attachToLabel: Optional[bool] = None  # @attr
    attachToQuestionText: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "attachment_locations": (qn(DATA_COLLECTION_NS, "AttachmentLocation"), "element", True),
        "grid_attachments": (qn(DATA_COLLECTION_NS, "GridAttachment"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "attachToLabel": ("attachToLabel", "bool"),
        "attachToQuestionText": ("attachToQuestionText", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "AttachmentLocation"),
        qn(DATA_COLLECTION_NS, "GridAttachment"),
    ]


@dataclass
class InstructionGroupFields(MaintainableBase):
    """Contains a group of Instructions, which may describe an ordered or hierarchical relationship structure. Specifies the purpose of the group, a name, label, and description of the group, its relationshi"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "InstructionGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_instruction_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    instruction_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_instruction_group": (qn(DATA_COLLECTION_NS, "TypeOfInstructionGroup"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "InstructionGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "instruction_references": (qn(DATA_COLLECTION_NS, "InstructionReference"), "reference", True),
        "instruction_group_references": (qn(DATA_COLLECTION_NS, "InstructionGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfInstructionGroup"),
        qn(DATA_COLLECTION_NS, "InstructionGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(DATA_COLLECTION_NS, "InstructionReference"),
        qn(DATA_COLLECTION_NS, "InstructionGroupReference"),
    ]


@dataclass
class InstructionFields(MaintainableBase):
    """Provides the content and description of a single instruction. In addition to the standard name, label, and description, an InParameter can be designated to specify information needed to process the dy"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Instruction")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    associated_images: list[Element] = field(default_factory=list)  # [0..*]
    instruction_texts: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "InstructionName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "associated_images": (qn(DATA_COLLECTION_NS, "AssociatedImage"), "element", True),
        "instruction_texts": (qn(DATA_COLLECTION_NS, "InstructionText"), "element", True),
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
        qn(DATA_COLLECTION_NS, "InstructionName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(DATA_COLLECTION_NS, "AssociatedImage"),
        qn(DATA_COLLECTION_NS, "InstructionText"),
    ]


@dataclass
class InstrumentGroupFields(MaintainableBase):
    """Describes a group of instruments for administrative or conceptual purposes, which may be hierarchical. In addition to the standard name, label, and description, contains references to the contained In"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "InstrumentGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_instrument_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    instrument_references: list[Reference] = field(default_factory=list)  # [0..*]
    instrument_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_instrument_group": (qn(DATA_COLLECTION_NS, "TypeOfInstrumentGroup"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "InstrumentGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "instrument_references": (qn(DATA_COLLECTION_NS, "InstrumentReference"), "reference", True),
        "instrument_group_references": (qn(DATA_COLLECTION_NS, "InstrumentGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfInstrumentGroup"),
        qn(DATA_COLLECTION_NS, "InstrumentGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(DATA_COLLECTION_NS, "InstrumentReference"),
        qn(DATA_COLLECTION_NS, "InstrumentGroupReference"),
    ]


@dataclass
class InstrumentSchemeFields(MaintainableBase):
    """Describes a set of instruments maintained by an agency. In addition to the standard name, label, and description, allows for the inclusion of an existing InstrumentScheme by reference and contains Ins"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "InstrumentScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    instrument_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    instruments: list[Element] = field(default_factory=list)  # [0..*]
    instrument_references: list[Reference] = field(default_factory=list)  # [0..*]
    instrument_groups: list[Element] = field(default_factory=list)  # [0..*]
    instrument_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "InstrumentSchemeName"), "intl_string", True),
        "instrument_scheme_references": (qn(REUSABLE_NS, "InstrumentSchemeReference"), "reference", True),
        "instruments": (qn(DATA_COLLECTION_NS, "Instrument"), "element", True),
        "instrument_references": (qn(DATA_COLLECTION_NS, "InstrumentReference"), "reference", True),
        "instrument_groups": (qn(DATA_COLLECTION_NS, "InstrumentGroup"), "element", True),
        "instrument_group_references": (qn(DATA_COLLECTION_NS, "InstrumentGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "InstrumentSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InstrumentSchemeReference"),
        qn(DATA_COLLECTION_NS, "Instrument"),
        qn(DATA_COLLECTION_NS, "InstrumentReference"),
        qn(DATA_COLLECTION_NS, "InstrumentGroup"),
        qn(DATA_COLLECTION_NS, "InstrumentGroupReference"),
    ]


@dataclass
class InstrumentFields(MaintainableBase):
    """Defines the type of instrument used for data collection or capture. In addition to the standard name, label, and description contains a classification of the type of instrument, a reference to an exte"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Instrument")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    type_of_instrument: Optional[CodeValue] = None  # [0..1]
    external_instrument_locations: list[str] = field(default_factory=list)  # [0..*]
    control_construct_reference: Optional[Reference] = None  # [0..1]
    fielded_languages: list[CodeValue] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "InstrumentName"), "intl_string", True),
        "type_of_instrument": (qn(DATA_COLLECTION_NS, "TypeOfInstrument"), "code_value", False),
        "external_instrument_locations": (qn(DATA_COLLECTION_NS, "ExternalInstrumentLocation"), "str", True),
        "control_construct_reference": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", False),
        "fielded_languages": (qn(DATA_COLLECTION_NS, "FieldedLanguages"), "code_value", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "InstrumentName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "TypeOfInstrument"),
        qn(DATA_COLLECTION_NS, "ExternalInstrumentLocation"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
        qn(DATA_COLLECTION_NS, "FieldedLanguages"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
    ]


@dataclass
class InterviewerInstructionReferenceFields(MaintainableBase):
    """Reference to an interviewer instruction expressed as DDI XML plus a flag to designate whether the instruction should always be displayed. TypeOfObject should be set to InterviewerInstruction."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "InterviewerInstructionReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_object: Optional[Element] = None  # [1..1]
    instruction_attachment_locations: list[Element] = field(default_factory=list)  # [0..*]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    isDisplayed: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "instruction_attachment_locations": (qn(DATA_COLLECTION_NS, "InstructionAttachmentLocation"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isExternal": ("isExternal", "bool"),
        "isReference": ("isReference", "bool"),
        "lateBound": ("lateBound", "bool"),
        "lateBoundRestriction": ("lateBoundRestriction", "str"),
        "objectLanguage": ("objectLanguage", "str"),
        "sourceContext": ("sourceContext", "str"),
        "isDisplayed": ("isDisplayed", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(DATA_COLLECTION_NS, "InstructionAttachmentLocation"),
    ]


@dataclass
class InterviewerInstructionSchemeFields(MaintainableBase):
    """A set of interviewer instructions to be displayed within the instrument, such as definitions, and explanations of terminology and questions. Content may also be used to provide the contents of an inst"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    interviewer_instruction_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    instructions: list[Element] = field(default_factory=list)  # [0..*]
    instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    instruction_groups: list[Element] = field(default_factory=list)  # [0..*]
    instruction_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "InterviewerInstructionSchemeName"), "intl_string", True),
        "interviewer_instruction_scheme_references": (qn(REUSABLE_NS, "InterviewerInstructionSchemeReference"), "reference", True),
        "instructions": (qn(DATA_COLLECTION_NS, "Instruction"), "element", True),
        "instruction_references": (qn(DATA_COLLECTION_NS, "InstructionReference"), "reference", True),
        "instruction_groups": (qn(DATA_COLLECTION_NS, "InstructionGroup"), "element", True),
        "instruction_group_references": (qn(DATA_COLLECTION_NS, "InstructionGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "InterviewerInstructionSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InterviewerInstructionSchemeReference"),
        qn(DATA_COLLECTION_NS, "Instruction"),
        qn(DATA_COLLECTION_NS, "InstructionReference"),
        qn(DATA_COLLECTION_NS, "InstructionGroup"),
        qn(DATA_COLLECTION_NS, "InstructionGroupReference"),
    ]


@dataclass
class LanguageAbilitySoughtFields(MaintainableBase):
    """Describes both minimum and preferred language abilities sought for the translation work as a set of source and target language requirements."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "LanguageAbilitySought")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    minimum_language_ability: Optional[Element] = None  # [0..1]
    preferred_language_ability: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "minimum_language_ability": (qn(DATA_COLLECTION_NS, "MinimumLanguageAbility"), "element", False),
        "preferred_language_ability": (qn(DATA_COLLECTION_NS, "PreferredLanguageAbility"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "MinimumLanguageAbility"),
        qn(DATA_COLLECTION_NS, "PreferredLanguageAbility"),
    ]


@dataclass
class LiteralTextFields(MaintainableBase):
    """Literal (static) text to be used in the instrument using the StructuredString structure plus an attribute allowing for the specification of white space to be preserved."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "LiteralText")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    text: Optional[Element] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "text": (qn(DATA_COLLECTION_NS, "Text"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "Text"),
    ]


@dataclass
class LocationDomainFields(MaintainableBase):
    """A response domain capturing a location response (mark on an image, recording, or object) for a question. Includes standard response domain elements; OutParameter, designation of response cardinality, """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "LocationDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    object: Optional[CodeValue] = None  # [0..1]
    actions: list[Element] = field(default_factory=list)  # [0..*]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "object": (qn(REUSABLE_NS, "Object"), "code_value", False),
        "actions": (qn(REUSABLE_NS, "Action"), "element", True),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "Object"),
        qn(REUSABLE_NS, "Action"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class LoopFields(MaintainableBase):
    """A member of the control construct substitution group. Describing an action which loops until a limiting condition is met. The ControlConstruct contained in the Loop operates on the LoopVariable until """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Loop")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    loop_variable_reference: Optional[Reference] = None  # [0..1]
    initial_value: Optional[Element] = None  # [0..1]
    loop_while: Optional[Element] = None  # [0..1]
    step_value: Optional[Element] = None  # [0..1]
    control_construct_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "loop_variable_reference": (qn(DATA_COLLECTION_NS, "LoopVariableReference"), "reference", False),
        "initial_value": (qn(DATA_COLLECTION_NS, "InitialValue"), "element", False),
        "loop_while": (qn(DATA_COLLECTION_NS, "LoopWhile"), "element", False),
        "step_value": (qn(DATA_COLLECTION_NS, "StepValue"), "element", False),
        "control_construct_reference": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", False),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "LoopVariableReference"),
        qn(DATA_COLLECTION_NS, "InitialValue"),
        qn(DATA_COLLECTION_NS, "LoopWhile"),
        qn(DATA_COLLECTION_NS, "StepValue"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
    ]


@dataclass
class MeasurementConstructFields(MaintainableBase):
    """A construct which ties measurement content to the programmatic logic of the control constructs. Contains a reference to a MeasurementItem, identifies the response unit, analysis unit, and universe. Ma"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "MeasurementConstruct")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    measurement_reference: Optional[Reference] = None  # [0..1]
    response_unit: Optional[CodeValue] = None  # [0..1]
    analysis_units: list[CodeValue] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    estimatedSecondsResponseTime: Optional[float] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "measurement_reference": (qn(REUSABLE_NS, "MeasurementReference"), "reference", False),
        "response_unit": (qn(DATA_COLLECTION_NS, "ResponseUnit"), "code_value", False),
        "analysis_units": (qn(REUSABLE_NS, "AnalysisUnit"), "code_value", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "estimatedSecondsResponseTime": ("estimatedSecondsResponseTime", "float"),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(REUSABLE_NS, "MeasurementReference"),
        qn(DATA_COLLECTION_NS, "ResponseUnit"),
        qn(REUSABLE_NS, "AnalysisUnit"),
        qn(REUSABLE_NS, "UniverseReference"),
    ]


@dataclass
class MeasurementGroupFields(MaintainableBase):
    """Contains a group of MeasurementItem, which may be ordered or hierarchical. In addition to the name, label, and description of the group, the structure allows for defining the type of group using an op"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "MeasurementGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_measurement_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    measurement_item_references: list[Reference] = field(default_factory=list)  # [0..*]
    measurement_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_measurement_group": (qn(DATA_COLLECTION_NS, "TypeOfMeasurementGroup"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "MeasurementGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "measurement_item_references": (qn(REUSABLE_NS, "MeasurementItemReference"), "reference", True),
        "measurement_group_references": (qn(DATA_COLLECTION_NS, "MeasurementGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfMeasurementGroup"),
        qn(DATA_COLLECTION_NS, "MeasurementGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "MeasurementItemReference"),
        qn(DATA_COLLECTION_NS, "MeasurementGroupReference"),
    ]


@dataclass
class MeasurementItemFields(MaintainableBase):
    """Structure a single Measurement which may contain one or more response domains (i.e., a list of valid category responses where if "Other" is indicated a text response can be used to specify the intent """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "MeasurementItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    type_of_measurement_items: list[CodeValue] = field(default_factory=list)  # [0..*]
    measurement_item_intent: Optional[Element] = None  # [0..1]
    response_domain: Optional[Element] = None  # [1..1]
    response_domain_reference: Optional[Reference] = None  # [1..1]
    structured_mixed_response_domain: Optional[Element] = None  # [1..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    concept_references: list[Reference] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    represented_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    estimatedSecondsResponseTime: Optional[float] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "MeasurementItemName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "type_of_measurement_items": (qn(DATA_COLLECTION_NS, "TypeOfMeasurementItem"), "code_value", True),
        "measurement_item_intent": (qn(DATA_COLLECTION_NS, "MeasurementItemIntent"), "element", False),
        "response_domain": (qn(DATA_COLLECTION_NS, "ResponseDomain"), "element", False),
        "response_domain_reference": (qn(DATA_COLLECTION_NS, "ResponseDomainReference"), "reference", False),
        "structured_mixed_response_domain": (qn(DATA_COLLECTION_NS, "StructuredMixedResponseDomain"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "concept_references": (qn(REUSABLE_NS, "ConceptReference"), "reference", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "represented_variable_references": (qn(REUSABLE_NS, "RepresentedVariableReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "estimatedSecondsResponseTime": ("estimatedSecondsResponseTime", "float"),
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
        qn(DATA_COLLECTION_NS, "MeasurementItemName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "TypeOfMeasurementItem"),
        qn(DATA_COLLECTION_NS, "MeasurementItemIntent"),
        qn(DATA_COLLECTION_NS, "ResponseDomain"),
        qn(DATA_COLLECTION_NS, "ResponseDomainReference"),
        qn(DATA_COLLECTION_NS, "StructuredMixedResponseDomain"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(REUSABLE_NS, "RepresentedVariableReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
    ]


@dataclass
class MeasurementSchemeFields(MaintainableBase):
    """Contains a set of MeasurementItems and MeasurementGroups. In addition to the standard name, label, and description of the MeasurementScheme, may contain another MeasurementScheme by reference, a listi"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "MeasurementScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    measurement_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    measurement_items: list[Element] = field(default_factory=list)  # [0..*]
    measurement_item_references: list[Reference] = field(default_factory=list)  # [0..*]
    measurement_groups: list[Element] = field(default_factory=list)  # [0..*]
    measurement_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "MeasurementSchemeName"), "intl_string", True),
        "measurement_scheme_references": (qn(REUSABLE_NS, "MeasurementSchemeReference"), "reference", True),
        "measurement_items": (qn(DATA_COLLECTION_NS, "MeasurementItem"), "element", True),
        "measurement_item_references": (qn(REUSABLE_NS, "MeasurementItemReference"), "reference", True),
        "measurement_groups": (qn(DATA_COLLECTION_NS, "MeasurementGroup"), "element", True),
        "measurement_group_references": (qn(DATA_COLLECTION_NS, "MeasurementGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "MeasurementSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "MeasurementSchemeReference"),
        qn(DATA_COLLECTION_NS, "MeasurementItem"),
        qn(REUSABLE_NS, "MeasurementItemReference"),
        qn(DATA_COLLECTION_NS, "MeasurementGroup"),
        qn(DATA_COLLECTION_NS, "MeasurementGroupReference"),
    ]


@dataclass
class MethodOfAdministrationFields(MaintainableBase):
    """Describes the method of pretest administration using a controlled vocabulary and description."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "MethodOfAdministration")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_administration_method: Optional[CodeValue] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_administration_method": (qn(DATA_COLLECTION_NS, "TypeOfAdministrationMethod"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "TypeOfAdministrationMethod"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class MethodologyFields(MaintainableBase):
    """Metadata regarding the methodologies used concerning data collection, determining the timing and repetition patterns for data collection, and sampling procedures. Identifies areas where there were dev"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Methodology")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    data_collection_methodologies: list[Element] = field(default_factory=list)  # [0..*]
    time_methods: list[Element] = field(default_factory=list)  # [0..*]
    weighting_methodologies: list[Element] = field(default_factory=list)  # [0..*]
    weighting_methodology_references: list[Reference] = field(default_factory=list)  # [0..*]
    sampling_procedures: list[Element] = field(default_factory=list)  # [0..*]
    deviation_from_sample_designs: list[Element] = field(default_factory=list)  # [0..*]
    data_collection_softwares: list[Element] = field(default_factory=list)  # [0..*]
    quality_statement_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "MethodologyName"), "intl_string", True),
        "data_collection_methodologies": (qn(DATA_COLLECTION_NS, "DataCollectionMethodology"), "element", True),
        "time_methods": (qn(DATA_COLLECTION_NS, "TimeMethod"), "element", True),
        "weighting_methodologies": (qn(DATA_COLLECTION_NS, "WeightingMethodology"), "element", True),
        "weighting_methodology_references": (qn(DATA_COLLECTION_NS, "WeightingMethodologyReference"), "reference", True),
        "sampling_procedures": (qn(DATA_COLLECTION_NS, "SamplingProcedure"), "element", True),
        "deviation_from_sample_designs": (qn(DATA_COLLECTION_NS, "DeviationFromSampleDesign"), "element", True),
        "data_collection_softwares": (qn(DATA_COLLECTION_NS, "DataCollectionSoftware"), "element", True),
        "quality_statement_references": (qn(REUSABLE_NS, "QualityStatementReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "MethodologyName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DataCollectionMethodology"),
        qn(DATA_COLLECTION_NS, "TimeMethod"),
        qn(DATA_COLLECTION_NS, "WeightingMethodology"),
        qn(DATA_COLLECTION_NS, "WeightingMethodologyReference"),
        qn(DATA_COLLECTION_NS, "SamplingProcedure"),
        qn(DATA_COLLECTION_NS, "DeviationFromSampleDesign"),
        qn(DATA_COLLECTION_NS, "DataCollectionSoftware"),
        qn(REUSABLE_NS, "QualityStatementReference"),
    ]


@dataclass
class ModeOfCollectionFields(MaintainableBase):
    """Describes the mode of collection, i.e., paper questionnaire, observation, web delivered questionnaire, computer assisted interview, automated data harvesting, etc. In addition to the narrative descrip"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ModeOfCollection")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_mode_of_collection: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_mode_of_collection": (qn(DATA_COLLECTION_NS, "TypeOfModeOfCollection"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "TypeOfModeOfCollection"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class ModeOfPretestCollectionFields(MaintainableBase):
    """Describes available aids for translation typed by a controlled vocabulary and a description."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ModeOfPretestCollection")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_pretest_collection_mode: Optional[CodeValue] = None  # [0..1]
    method_of_delivery: Optional[CodeValue] = None  # [0..1]
    isPrimary: Optional[bool] = None  # @attr
    isAudioFormatAvailable: Optional[bool] = None  # @attr
    isRecordedInterview: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_pretest_collection_mode": (qn(DATA_COLLECTION_NS, "TypeOfPretestCollectionMode"), "code_value", False),
        "method_of_delivery": (qn(DATA_COLLECTION_NS, "MethodOfDelivery"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isPrimary": ("isPrimary", "bool"),
        "isAudioFormatAvailable": ("isAudioFormatAvailable", "bool"),
        "isRecordedInterview": ("isRecordedInterview", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "TypeOfPretestCollectionMode"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "MethodOfDelivery"),
    ]


@dataclass
class NominalDomainFields(MaintainableBase):
    """A response domain capturing a nominal (check off) response for a question grid response. Includes standard response domain elements; OutParameter, designation of response cardinality, and a declaratio"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "NominalDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    regExp: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "regExp": ("regExp", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class NumericDomainFields(MaintainableBase):
    """A response domain capturing a numeric response (the intent is to analyze the response as a number) for a question. Contains the equivalent content of a NumericRepresentation including the numeric rang"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "NumericDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    number_ranges: list[Element] = field(default_factory=list)  # [0..*]
    numeric_type_code: Optional[CodeValue] = None  # [0..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    format: Optional[str] = None  # @attr
    scale: Optional[int] = None  # @attr
    decimalPositions: Optional[int] = None  # @attr
    interval: Optional[int] = None  # @attr
    accuracy: Optional[float] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "number_ranges": (qn(REUSABLE_NS, "NumberRange"), "element", True),
        "numeric_type_code": (qn(REUSABLE_NS, "NumericTypeCode"), "code_value", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "format": ("format", "str"),
        "scale": ("scale", "int"),
        "decimalPositions": ("decimalPositions", "int"),
        "interval": ("interval", "int"),
        "accuracy": ("accuracy", "float"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "NumberRange"),
        qn(REUSABLE_NS, "NumericTypeCode"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class OperationFields(MaintainableBase):
    """A generic operation description used as a type by specified operations. Describes the operation and identifies the organization or individual responsible for performing it."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Operation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    agency_organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "agency_organization_references": (qn(REUSABLE_NS, "AgencyOrganizationReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "AgencyOrganizationReference"),
    ]


@dataclass
class OriginFields(MaintainableBase):
    """A citation or URI for the source of the data. Note that this is an external reference, and should not be used to point to DDI descriptions of the data, or to DDI-encoded data."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Origin")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    citation: Optional[Element] = None  # [0..1]
    origin_location: Optional[str] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "citation": (qn(REUSABLE_NS, "Citation"), "element", False),
        "origin_location": (qn(DATA_COLLECTION_NS, "OriginLocation"), "str", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Citation"),
        qn(DATA_COLLECTION_NS, "OriginLocation"),
    ]


@dataclass
class PopulationSizeFields(MaintainableBase):
    """The target value of the sample size for the primary and any secondary or sub-population."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "PopulationSize")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    primary_population: Optional[Element] = None  # [0..1]
    secondary_populations: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "primary_population": (qn(DATA_COLLECTION_NS, "PrimaryPopulation"), "element", False),
        "secondary_populations": (qn(DATA_COLLECTION_NS, "SecondaryPopulation"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "PrimaryPopulation"),
        qn(DATA_COLLECTION_NS, "SecondaryPopulation"),
    ]


@dataclass
class PopulationFields(MaintainableBase):
    """Describe the population through a combination of textual description and reference to a structured Universe. If multiple universes are referenced, the overall universe is the intersect of the set of u"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Population")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
    ]


@dataclass
class PretestActivityFields(MaintainableBase):
    """A substitution for DevelopmentActivity which specifies the details for performing a pretest of a set of questions or questionnaire. Includes reference to the Sample Frame and Sample Method for the pre"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "PretestActivity")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    development_activity_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    desired_outcome: Optional[Element] = None  # [0..1]
    process_summary: Optional[Element] = None  # [0..1]
    recommended_staff_requirements: list[Element] = field(default_factory=list)  # [0..*]
    additional_required_resources: Optional[Element] = None  # [0..1]
    debriefing_process: Optional[Element] = None  # [0..1]
    sample_frame_reference: Optional[Reference] = None  # [0..1]
    sampling_plan_reference: Optional[Reference] = None  # [0..1]
    pretest_administrations: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "development_activity_names": (qn(DATA_COLLECTION_NS, "DevelopmentActivityName"), "intl_string", True),
        "desired_outcome": (qn(DATA_COLLECTION_NS, "DesiredOutcome"), "element", False),
        "process_summary": (qn(DATA_COLLECTION_NS, "ProcessSummary"), "element", False),
        "recommended_staff_requirements": (qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"), "element", True),
        "additional_required_resources": (qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"), "element", False),
        "debriefing_process": (qn(DATA_COLLECTION_NS, "DebriefingProcess"), "element", False),
        "sample_frame_reference": (qn(DATA_COLLECTION_NS, "SampleFrameReference"), "reference", False),
        "sampling_plan_reference": (qn(DATA_COLLECTION_NS, "SamplingPlanReference"), "reference", False),
        "pretest_administrations": (qn(DATA_COLLECTION_NS, "PretestAdministration"), "element", True),
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
        qn(DATA_COLLECTION_NS, "DevelopmentActivityName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DesiredOutcome"),
        qn(DATA_COLLECTION_NS, "ProcessSummary"),
        qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"),
        qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"),
        qn(DATA_COLLECTION_NS, "DebriefingProcess"),
        qn(DATA_COLLECTION_NS, "SampleFrameReference"),
        qn(DATA_COLLECTION_NS, "SamplingPlanReference"),
        qn(DATA_COLLECTION_NS, "PretestAdministration"),
    ]


@dataclass
class PretestAdministrationFields(MaintainableBase):
    """Description of the method and mode of data collection in administering the pretest. Notes any additional data collected in the administration of the pretest."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "PretestAdministration")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    method_of_administration: Optional[Element] = None  # [0..1]
    mode_of_pretest_collections: list[Element] = field(default_factory=list)  # [0..*]
    additional_data_collections: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "method_of_administration": (qn(DATA_COLLECTION_NS, "MethodOfAdministration"), "element", False),
        "mode_of_pretest_collections": (qn(DATA_COLLECTION_NS, "ModeOfPretestCollection"), "element", True),
        "additional_data_collections": (qn(DATA_COLLECTION_NS, "AdditionalDataCollection"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "MethodOfAdministration"),
        qn(DATA_COLLECTION_NS, "ModeOfPretestCollection"),
        qn(DATA_COLLECTION_NS, "AdditionalDataCollection"),
    ]


@dataclass
class ProcessingEventGroupFields(MaintainableBase):
    """Describes a group of processing events for administrative or conceptual purposes, which may be hierarchical. In addition to the standard name, label, and description contains references to included Pr"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ProcessingEventGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_processing_event_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    processing_event_references: list[Reference] = field(default_factory=list)  # [0..*]
    processing_event_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_processing_event_group": (qn(DATA_COLLECTION_NS, "TypeOfProcessingEventGroup"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "ProcessingEventGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "processing_event_references": (qn(DATA_COLLECTION_NS, "ProcessingEventReference"), "reference", True),
        "processing_event_group_references": (qn(DATA_COLLECTION_NS, "ProcessingEventGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfProcessingEventGroup"),
        qn(DATA_COLLECTION_NS, "ProcessingEventGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(DATA_COLLECTION_NS, "ProcessingEventReference"),
        qn(DATA_COLLECTION_NS, "ProcessingEventGroupReference"),
    ]


@dataclass
class ProcessingEventSchemeFields(MaintainableBase):
    """A set of processing events maintained by an agency, and used in the processing data during development, cleaning, converting to variables, aggregating, and comparing. In addition to the standard name,"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ProcessingEventScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    processing_event_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    processing_events: list[Element] = field(default_factory=list)  # [0..*]
    processing_event_references: list[Reference] = field(default_factory=list)  # [0..*]
    processing_event_groups: list[Element] = field(default_factory=list)  # [0..*]
    processing_event_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "ProcessingEventSchemeName"), "intl_string", True),
        "processing_event_scheme_references": (qn(DATA_COLLECTION_NS, "ProcessingEventSchemeReference"), "reference", True),
        "processing_events": (qn(DATA_COLLECTION_NS, "ProcessingEvent"), "element", True),
        "processing_event_references": (qn(DATA_COLLECTION_NS, "ProcessingEventReference"), "reference", True),
        "processing_event_groups": (qn(DATA_COLLECTION_NS, "ProcessingEventGroup"), "element", True),
        "processing_event_group_references": (qn(DATA_COLLECTION_NS, "ProcessingEventGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "ProcessingEventSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "ProcessingEventSchemeReference"),
        qn(DATA_COLLECTION_NS, "ProcessingEvent"),
        qn(DATA_COLLECTION_NS, "ProcessingEventReference"),
        qn(DATA_COLLECTION_NS, "ProcessingEventGroup"),
        qn(DATA_COLLECTION_NS, "ProcessingEventGroupReference"),
    ]


@dataclass
class ProcessingEventFields(MaintainableBase):
    """ProcessingEvent can contain a number of operations of different types to express a range of events that occur together. For example a ProcessingEvent of a CleaningOperation may also include a referenc"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ProcessingEvent")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    control_operations: list[Element] = field(default_factory=list)  # [0..*]
    cleaning_operations: list[Element] = field(default_factory=list)  # [0..*]
    weightings: list[Element] = field(default_factory=list)  # [0..*]
    weighting_references: list[Reference] = field(default_factory=list)  # [0..*]
    data_appraisal_informations: list[Element] = field(default_factory=list)  # [0..*]
    processing_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_statement_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "ProcessingEventName"), "intl_string", True),
        "control_operations": (qn(DATA_COLLECTION_NS, "ControlOperation"), "element", True),
        "cleaning_operations": (qn(DATA_COLLECTION_NS, "CleaningOperation"), "element", True),
        "weightings": (qn(DATA_COLLECTION_NS, "Weighting"), "element", True),
        "weighting_references": (qn(DATA_COLLECTION_NS, "WeightingReference"), "reference", True),
        "data_appraisal_informations": (qn(DATA_COLLECTION_NS, "DataAppraisalInformation"), "element", True),
        "processing_instruction_references": (qn(REUSABLE_NS, "ProcessingInstructionReference"), "reference", True),
        "quality_statement_references": (qn(REUSABLE_NS, "QualityStatementReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "ProcessingEventName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "ControlOperation"),
        qn(DATA_COLLECTION_NS, "CleaningOperation"),
        qn(DATA_COLLECTION_NS, "Weighting"),
        qn(DATA_COLLECTION_NS, "WeightingReference"),
        qn(DATA_COLLECTION_NS, "DataAppraisalInformation"),
        qn(REUSABLE_NS, "ProcessingInstructionReference"),
        qn(REUSABLE_NS, "QualityStatementReference"),
    ]


@dataclass
class ProcessingInstructionGroupFields(MaintainableBase):
    """Describes a group of processing instructions for administrative or conceptual purposes, which may be hierarchical. In addition to the standard name, label, and description contains references to inclu"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ProcessingInstructionGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_processing_instruction_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    general_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    generation_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    processing_instruction_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_processing_instruction_group": (qn(DATA_COLLECTION_NS, "TypeOfProcessingInstructionGroup"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "ProcessingInstructionGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "general_instruction_references": (qn(DATA_COLLECTION_NS, "GeneralInstructionReference"), "reference", True),
        "generation_instruction_references": (qn(DATA_COLLECTION_NS, "GenerationInstructionReference"), "reference", True),
        "processing_instruction_group_references": (qn(DATA_COLLECTION_NS, "ProcessingInstructionGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfProcessingInstructionGroup"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(DATA_COLLECTION_NS, "GeneralInstructionReference"),
        qn(DATA_COLLECTION_NS, "GenerationInstructionReference"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionGroupReference"),
    ]


@dataclass
class ProcessingInstructionSchemeFields(MaintainableBase):
    """A set of Processing Instructions (General and Generation Instructions) maintained by an agency. In addition to the standard name, label, and description allows for the inclusion of an existing Process"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ProcessingInstructionScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    processing_instruction_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    general_instructions: list[Element] = field(default_factory=list)  # [0..*]
    general_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    generation_instructions: list[Element] = field(default_factory=list)  # [0..*]
    generation_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    processing_instruction_groups: list[Element] = field(default_factory=list)  # [0..*]
    processing_instruction_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "ProcessingInstructionSchemeName"), "intl_string", True),
        "processing_instruction_scheme_references": (qn(DATA_COLLECTION_NS, "ProcessingInstructionSchemeReference"), "reference", True),
        "general_instructions": (qn(DATA_COLLECTION_NS, "GeneralInstruction"), "element", True),
        "general_instruction_references": (qn(DATA_COLLECTION_NS, "GeneralInstructionReference"), "reference", True),
        "generation_instructions": (qn(DATA_COLLECTION_NS, "GenerationInstruction"), "element", True),
        "generation_instruction_references": (qn(DATA_COLLECTION_NS, "GenerationInstructionReference"), "reference", True),
        "processing_instruction_groups": (qn(DATA_COLLECTION_NS, "ProcessingInstructionGroup"), "element", True),
        "processing_instruction_group_references": (qn(DATA_COLLECTION_NS, "ProcessingInstructionGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "ProcessingInstructionSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionSchemeReference"),
        qn(DATA_COLLECTION_NS, "GeneralInstruction"),
        qn(DATA_COLLECTION_NS, "GeneralInstructionReference"),
        qn(DATA_COLLECTION_NS, "GenerationInstruction"),
        qn(DATA_COLLECTION_NS, "GenerationInstructionReference"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionGroup"),
        qn(DATA_COLLECTION_NS, "ProcessingInstructionGroupReference"),
    ]


@dataclass
class ProcessingInstructionFields(MaintainableBase):
    """Substitution group head for types of processing instruction."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ProcessingInstruction")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
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
    ]


@dataclass
class QuestionBlockFields(MaintainableBase):
    """A QuestionBlock is a specific structure used in educational and other types of testing where an object (Stimulus Material) is provided and a set of questions are asked regarding the object. The Questi"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionBlock")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    question_block_intent: Optional[Element] = None  # [0..1]
    stimulus_materials: list[Element] = field(default_factory=list)  # [0..*]
    question_item_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_grid_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_sequence: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    concept_references: list[Reference] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    estimatedSecondsResponseTime: Optional[float] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "names": (qn(DATA_COLLECTION_NS, "QuestionBlockName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "question_block_intent": (qn(DATA_COLLECTION_NS, "QuestionBlockIntent"), "element", False),
        "stimulus_materials": (qn(DATA_COLLECTION_NS, "StimulusMaterial"), "element", True),
        "question_item_references": (qn(DATA_COLLECTION_NS, "QuestionItemReference"), "reference", True),
        "question_grid_references": (qn(DATA_COLLECTION_NS, "QuestionGridReference"), "reference", True),
        "question_sequence": (qn(DATA_COLLECTION_NS, "QuestionSequence"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "concept_references": (qn(REUSABLE_NS, "ConceptReference"), "reference", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "estimatedSecondsResponseTime": ("estimatedSecondsResponseTime", "float"),
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
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "QuestionBlockName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "QuestionBlockIntent"),
        qn(DATA_COLLECTION_NS, "StimulusMaterial"),
        qn(DATA_COLLECTION_NS, "QuestionItemReference"),
        qn(DATA_COLLECTION_NS, "QuestionGridReference"),
        qn(DATA_COLLECTION_NS, "QuestionSequence"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
    ]


@dataclass
class QuestionConstructFields(MaintainableBase):
    """A member of the ControlConstruct substitution group. A construct which ties question content to the programmatic logic of the control constructs. Contains a reference to a QuestionItem, QuestionGrid o"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionConstruct")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_reference: Optional[Reference] = None  # [0..1]
    response_sequence: Optional[Element] = None  # [0..1]
    dimension_sequence: Optional[Element] = None  # [0..1]
    response_unit: Optional[CodeValue] = None  # [0..1]
    analysis_units: list[CodeValue] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    estimatedSecondsResponseTime: Optional[float] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "question_reference": (qn(REUSABLE_NS, "QuestionReference"), "reference", False),
        "response_sequence": (qn(DATA_COLLECTION_NS, "ResponseSequence"), "element", False),
        "dimension_sequence": (qn(DATA_COLLECTION_NS, "DimensionSequence"), "element", False),
        "response_unit": (qn(DATA_COLLECTION_NS, "ResponseUnit"), "code_value", False),
        "analysis_units": (qn(REUSABLE_NS, "AnalysisUnit"), "code_value", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "estimatedSecondsResponseTime": ("estimatedSecondsResponseTime", "float"),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(REUSABLE_NS, "QuestionReference"),
        qn(DATA_COLLECTION_NS, "ResponseSequence"),
        qn(DATA_COLLECTION_NS, "DimensionSequence"),
        qn(DATA_COLLECTION_NS, "ResponseUnit"),
        qn(REUSABLE_NS, "AnalysisUnit"),
        qn(REUSABLE_NS, "UniverseReference"),
    ]


@dataclass
class QuestionGridFields(MaintainableBase):
    """Structures the QuestionGrid as an NCube-like structure providing dimension information, labeling options, and response domains attached to one or more cells within the grid. Provides the intent of the"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionGrid")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    question_texts: list[Element] = field(default_factory=list)  # [0..*]
    question_intent: Optional[Element] = None  # [0..1]
    grid_dimensions: list[Element] = field(default_factory=list)  # [0..*]
    response_domain: Optional[Element] = None  # [1..1]
    response_domain_reference: Optional[Reference] = None  # [1..1]
    structured_mixed_grid_response_domain: Optional[Element] = None  # [1..1]
    cell_labels: list[Element] = field(default_factory=list)  # [0..*]
    fixed_cell_values: list[Element] = field(default_factory=list)  # [0..*]
    concept_references: list[Reference] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    represented_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    estimatedSecondsResponseTime: Optional[float] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "names": (qn(DATA_COLLECTION_NS, "QuestionGridName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "question_texts": (qn(DATA_COLLECTION_NS, "QuestionText"), "element", True),
        "question_intent": (qn(DATA_COLLECTION_NS, "QuestionIntent"), "element", False),
        "grid_dimensions": (qn(DATA_COLLECTION_NS, "GridDimension"), "element", True),
        "response_domain": (qn(DATA_COLLECTION_NS, "ResponseDomain"), "element", False),
        "response_domain_reference": (qn(DATA_COLLECTION_NS, "ResponseDomainReference"), "reference", False),
        "structured_mixed_grid_response_domain": (qn(DATA_COLLECTION_NS, "StructuredMixedGridResponseDomain"), "element", False),
        "cell_labels": (qn(DATA_COLLECTION_NS, "CellLabel"), "element", True),
        "fixed_cell_values": (qn(DATA_COLLECTION_NS, "FixedCellValue"), "element", True),
        "concept_references": (qn(REUSABLE_NS, "ConceptReference"), "reference", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "represented_variable_references": (qn(REUSABLE_NS, "RepresentedVariableReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "estimatedSecondsResponseTime": ("estimatedSecondsResponseTime", "float"),
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
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "QuestionGridName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "QuestionText"),
        qn(DATA_COLLECTION_NS, "QuestionIntent"),
        qn(DATA_COLLECTION_NS, "GridDimension"),
        qn(DATA_COLLECTION_NS, "ResponseDomain"),
        qn(DATA_COLLECTION_NS, "ResponseDomainReference"),
        qn(DATA_COLLECTION_NS, "StructuredMixedGridResponseDomain"),
        qn(DATA_COLLECTION_NS, "CellLabel"),
        qn(DATA_COLLECTION_NS, "FixedCellValue"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(REUSABLE_NS, "RepresentedVariableReference"),
    ]


@dataclass
class QuestionGroupFields(MaintainableBase):
    """Contains a group of Questions, which may be ordered or hierarchical. In addition to the name, label, and description of the group, the structure allows for defining the type of group using an optional"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_question_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    question_item_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_grid_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_block_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_question_group": (qn(DATA_COLLECTION_NS, "TypeOfQuestionGroup"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "QuestionGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "question_item_references": (qn(DATA_COLLECTION_NS, "QuestionItemReference"), "reference", True),
        "question_grid_references": (qn(DATA_COLLECTION_NS, "QuestionGridReference"), "reference", True),
        "question_block_references": (qn(DATA_COLLECTION_NS, "QuestionBlockReference"), "reference", True),
        "question_group_references": (qn(DATA_COLLECTION_NS, "QuestionGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfQuestionGroup"),
        qn(DATA_COLLECTION_NS, "QuestionGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(DATA_COLLECTION_NS, "QuestionItemReference"),
        qn(DATA_COLLECTION_NS, "QuestionGridReference"),
        qn(DATA_COLLECTION_NS, "QuestionBlockReference"),
        qn(DATA_COLLECTION_NS, "QuestionGroupReference"),
    ]


@dataclass
class QuestionItemFields(MaintainableBase):
    """Structure a single Question which may contain one or more response domains (i.e., a list of valid category responses where if "Other" is indicated a text response can be used to specify the intent of """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    question_texts: list[Element] = field(default_factory=list)  # [0..*]
    question_intent: Optional[Element] = None  # [0..1]
    response_domain: Optional[Element] = None  # [1..1]
    response_domain_reference: Optional[Reference] = None  # [1..1]
    structured_mixed_response_domain: Optional[Element] = None  # [1..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    concept_references: list[Reference] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    represented_variable_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    estimatedSecondsResponseTime: Optional[float] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "names": (qn(DATA_COLLECTION_NS, "QuestionItemName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "question_texts": (qn(DATA_COLLECTION_NS, "QuestionText"), "element", True),
        "question_intent": (qn(DATA_COLLECTION_NS, "QuestionIntent"), "element", False),
        "response_domain": (qn(DATA_COLLECTION_NS, "ResponseDomain"), "element", False),
        "response_domain_reference": (qn(DATA_COLLECTION_NS, "ResponseDomainReference"), "reference", False),
        "structured_mixed_response_domain": (qn(DATA_COLLECTION_NS, "StructuredMixedResponseDomain"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "concept_references": (qn(REUSABLE_NS, "ConceptReference"), "reference", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "represented_variable_references": (qn(REUSABLE_NS, "RepresentedVariableReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "estimatedSecondsResponseTime": ("estimatedSecondsResponseTime", "float"),
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
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "QuestionItemName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "QuestionText"),
        qn(DATA_COLLECTION_NS, "QuestionIntent"),
        qn(DATA_COLLECTION_NS, "ResponseDomain"),
        qn(DATA_COLLECTION_NS, "ResponseDomainReference"),
        qn(DATA_COLLECTION_NS, "StructuredMixedResponseDomain"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(REUSABLE_NS, "RepresentedVariableReference"),
    ]


@dataclass
class QuestionSchemeFields(MaintainableBase):
    """Contains a set of QuestionItems, QuestionGrids, QuestionBlocks, and QuestionGroups. In addition to the standard name, label, and description of the Question Scheme, may contain another QuestionScheme """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    question_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_items: list[Element] = field(default_factory=list)  # [0..*]
    question_item_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_grids: list[Element] = field(default_factory=list)  # [0..*]
    question_grid_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_blocks: list[Element] = field(default_factory=list)  # [0..*]
    question_block_references: list[Reference] = field(default_factory=list)  # [0..*]
    question_groups: list[Element] = field(default_factory=list)  # [0..*]
    question_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "QuestionSchemeName"), "intl_string", True),
        "question_scheme_references": (qn(REUSABLE_NS, "QuestionSchemeReference"), "reference", True),
        "question_items": (qn(DATA_COLLECTION_NS, "QuestionItem"), "element", True),
        "question_item_references": (qn(DATA_COLLECTION_NS, "QuestionItemReference"), "reference", True),
        "question_grids": (qn(DATA_COLLECTION_NS, "QuestionGrid"), "element", True),
        "question_grid_references": (qn(DATA_COLLECTION_NS, "QuestionGridReference"), "reference", True),
        "question_blocks": (qn(DATA_COLLECTION_NS, "QuestionBlock"), "element", True),
        "question_block_references": (qn(DATA_COLLECTION_NS, "QuestionBlockReference"), "reference", True),
        "question_groups": (qn(DATA_COLLECTION_NS, "QuestionGroup"), "element", True),
        "question_group_references": (qn(DATA_COLLECTION_NS, "QuestionGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "QuestionSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "QuestionSchemeReference"),
        qn(DATA_COLLECTION_NS, "QuestionItem"),
        qn(DATA_COLLECTION_NS, "QuestionItemReference"),
        qn(DATA_COLLECTION_NS, "QuestionGrid"),
        qn(DATA_COLLECTION_NS, "QuestionGridReference"),
        qn(DATA_COLLECTION_NS, "QuestionBlock"),
        qn(DATA_COLLECTION_NS, "QuestionBlockReference"),
        qn(DATA_COLLECTION_NS, "QuestionGroup"),
        qn(DATA_COLLECTION_NS, "QuestionGroupReference"),
    ]


@dataclass
class QuestionSequenceFields(MaintainableBase):
    """Describes the ordering of questions when not otherwise indicated. Extends the standard sequencing information to indicate how and if StimulusMaterial should be treated in the resequencing."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionSequence")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    item_sequence_type: Optional[Element] = None  # [1..1]
    alternate_sequence_type: Optional[Element] = None  # [0..1]
    handlingOfStimulusMaterial: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "item_sequence_type": (qn(DATA_COLLECTION_NS, "ItemSequenceType"), "element", False),
        "alternate_sequence_type": (qn(DATA_COLLECTION_NS, "AlternateSequenceType"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "handlingOfStimulusMaterial": ("handlingOfStimulusMaterial", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "ItemSequenceType"),
        qn(DATA_COLLECTION_NS, "AlternateSequenceType"),
    ]


@dataclass
class QuestionFields(MaintainableBase):
    """Serves as a common extension base for different forms of Questions"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Question")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
    ]


@dataclass
class RankingDomainFields(MaintainableBase):
    """A response domain capturing a ranking response which supports a "ranking" of categories. Generally used within a QuestionGrid. Includes standard response domain elements; OutParameter, designation of """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "RankingDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    ranking_range: Optional[Element] = None  # [1..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "ranking_range": (qn(REUSABLE_NS, "RankingRange"), "element", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "RankingRange"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class RecommendedStaffRequirementsFields(MaintainableBase):
    """Specify requirements for type of staffing needed to complete activity including the class of staff participating in the activity, requirements for those participants, and the recruitment process."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    staff_class: Optional[CodeValue] = None  # [1..1]
    participant_requirements: Optional[Element] = None  # [0..1]
    recruitment_process: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "staff_class": (qn(DATA_COLLECTION_NS, "StaffClass"), "code_value", False),
        "participant_requirements": (qn(DATA_COLLECTION_NS, "ParticipantRequirements"), "element", False),
        "recruitment_process": (qn(DATA_COLLECTION_NS, "RecruitmentProcess"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "StaffClass"),
        qn(DATA_COLLECTION_NS, "ParticipantRequirements"),
        qn(DATA_COLLECTION_NS, "RecruitmentProcess"),
    ]


@dataclass
class RepeatUntilFields(MaintainableBase):
    """A member of the ControlConstruct substitution group. Specifies a ControlConstruct to be repeated until a specified condition is met. Before each iteration the condition is tested. When the condition i"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "RepeatUntil")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    until_condition: Optional[Element] = None  # [0..1]
    until_construct_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "until_condition": (qn(DATA_COLLECTION_NS, "UntilCondition"), "element", False),
        "until_construct_reference": (qn(DATA_COLLECTION_NS, "UntilConstructReference"), "reference", False),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "UntilCondition"),
        qn(DATA_COLLECTION_NS, "UntilConstructReference"),
    ]


@dataclass
class RepeatWhileFields(MaintainableBase):
    """A member of the ControlConstruct substitution group. Specifies a ControlConstruct to be repeated while a specified condition is met. Before each iteration the condition is tested. When the condition i"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "RepeatWhile")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    while_condition: Optional[Element] = None  # [0..1]
    while_construct_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "while_condition": (qn(DATA_COLLECTION_NS, "WhileCondition"), "element", False),
        "while_construct_reference": (qn(DATA_COLLECTION_NS, "WhileConstructReference"), "reference", False),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "WhileCondition"),
        qn(DATA_COLLECTION_NS, "WhileConstructReference"),
    ]


@dataclass
class RequirementsAssessmentFields(MaintainableBase):
    """Description of whether specific requirements for the activities providing these results were met."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "RequirementsAssessment")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_requirements_assessment: Optional[CodeValue] = None  # [0..1]
    isSatisfied: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_requirements_assessment": (qn(DATA_COLLECTION_NS, "TypeOfRequirementsAssessment"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isSatisfied": ("isSatisfied", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "TypeOfRequirementsAssessment"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class ResourceUsedFields(MaintainableBase):
    """Provides a name, label and description for the Development Process and lists the individual development activities which should take place."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ResourceUsed")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_resource: Optional[CodeValue] = None  # [0..1]
    resource_object_reference: Optional[Reference] = None  # [0..1]
    resource_usage: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_resource": (qn(DATA_COLLECTION_NS, "TypeOfResource"), "code_value", False),
        "resource_object_reference": (qn(DATA_COLLECTION_NS, "ResourceObjectReference"), "reference", False),
        "resource_usage": (qn(DATA_COLLECTION_NS, "ResourceUsage"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "TypeOfResource"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "ResourceObjectReference"),
        qn(DATA_COLLECTION_NS, "ResourceUsage"),
    ]


@dataclass
class ResponseDomainInMixedFields(MaintainableBase):
    """A structure that provides both the response domain and information on how it should be attached, or related, to other specified response domains in the question. If no AttachmentLocation information i"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ResponseDomainInMixed")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    response_domain: Optional[Element] = None  # [1..1]
    response_domain_reference: Optional[Reference] = None  # [1..1]
    attachment_location: Optional[Element] = None  # [0..1]
    attachmentBase: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "response_domain": (qn(DATA_COLLECTION_NS, "ResponseDomain"), "element", False),
        "response_domain_reference": (qn(DATA_COLLECTION_NS, "ResponseDomainReference"), "reference", False),
        "attachment_location": (qn(DATA_COLLECTION_NS, "AttachmentLocation"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "attachmentBase": ("attachmentBase", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "ResponseDomain"),
        qn(DATA_COLLECTION_NS, "ResponseDomainReference"),
        qn(DATA_COLLECTION_NS, "AttachmentLocation"),
    ]


@dataclass
class ResponseRateFields(MaintainableBase):
    """A specific rate of response and/or a description of the rate of response for a specific processing event that includes data appraisal."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ResponseRate")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    sample_size: Optional[int] = None  # [0..1]
    number_of_responses: Optional[int] = None  # [0..1]
    specific_response_rate: Optional[float] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "sample_size": (qn(DATA_COLLECTION_NS, "SampleSize"), "int", False),
        "number_of_responses": (qn(DATA_COLLECTION_NS, "NumberOfResponses"), "int", False),
        "specific_response_rate": (qn(DATA_COLLECTION_NS, "SpecificResponseRate"), "float", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "SampleSize"),
        qn(DATA_COLLECTION_NS, "NumberOfResponses"),
        qn(DATA_COLLECTION_NS, "SpecificResponseRate"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class ResponseTextSetFields(MaintainableBase):
    """Provides a means of bundling multiple language versions of the same intended dynamic text together. This wrapper serves to differentiate between a case where multiple language content for a single Res"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ResponseTextSet")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    response_texts: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "response_texts": (qn(DATA_COLLECTION_NS, "ResponseText"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "ResponseText"),
    ]


@dataclass
class ResultDetailFields(MaintainableBase):
    """Details of specific results of the development plan and process. May refer to specific development activities or DevelopmentSteps within a DevelopmentProcess."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ResultDetail")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_result: Optional[CodeValue] = None  # [0..1]
    results_date: Optional[Element] = None  # [0..1]
    requirements_assessments: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_result": (qn(DATA_COLLECTION_NS, "TypeOfResult"), "code_value", False),
        "results_date": (qn(DATA_COLLECTION_NS, "ResultsDate"), "element", False),
        "requirements_assessments": (qn(DATA_COLLECTION_NS, "RequirementsAssessment"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "TypeOfResult"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "ResultsDate"),
        qn(DATA_COLLECTION_NS, "RequirementsAssessment"),
    ]


@dataclass
class RosterFields(MaintainableBase):
    """A roster is an unlabeled list of numbered rows or columns depending upon orientation. The numbers may or may not be displayed but will be used as information for creating the cell coordinate address. """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Roster")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    condition_for_continuation: Optional[Element] = None  # [0..1]
    baseCodeValue: Optional[int] = None  # @attr
    codeIterationValue: Optional[int] = None  # @attr
    minimumRequired: Optional[int] = None  # @attr
    maximumAllowed: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "condition_for_continuation": (qn(DATA_COLLECTION_NS, "ConditionForContinuation"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "baseCodeValue": ("baseCodeValue", "int"),
        "codeIterationValue": ("codeIterationValue", "int"),
        "minimumRequired": ("minimumRequired", "int"),
        "maximumAllowed": ("maximumAllowed", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Label"),
        qn(DATA_COLLECTION_NS, "ConditionForContinuation"),
    ]


@dataclass
class SampleFrameFields(MaintainableBase):
    """An inline description of a sample frame (the source material from which a sample is drawn), i.e. phone book, data base, etc. A sample frame is intended to be versioned over time and can be reused by m"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SampleFrame")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    valid_period: Optional[Element] = None  # [0..1]
    custodian_reference: Optional[Reference] = None  # [0..1]
    sample_frame_access: Optional[Element] = None  # [0..1]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    units_of_frame: Optional[Element] = None  # [0..1]
    frame_limitations: Optional[Element] = None  # [0..1]
    auxiliary_information: Optional[Element] = None  # [0..1]
    reference_period: Optional[Element] = None  # [0..1]
    update_procedure: Optional[Element] = None  # [0..1]
    source_frame_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "SampleFrameName"), "intl_string", True),
        "valid_period": (qn(DATA_COLLECTION_NS, "ValidPeriod"), "element", False),
        "custodian_reference": (qn(DATA_COLLECTION_NS, "CustodianReference"), "reference", False),
        "sample_frame_access": (qn(DATA_COLLECTION_NS, "SampleFrameAccess"), "element", False),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "units_of_frame": (qn(DATA_COLLECTION_NS, "UnitsOfFrame"), "element", False),
        "frame_limitations": (qn(DATA_COLLECTION_NS, "FrameLimitations"), "element", False),
        "auxiliary_information": (qn(DATA_COLLECTION_NS, "AuxiliaryInformation"), "element", False),
        "reference_period": (qn(DATA_COLLECTION_NS, "ReferencePeriod"), "element", False),
        "update_procedure": (qn(DATA_COLLECTION_NS, "UpdateProcedure"), "element", False),
        "source_frame_references": (qn(DATA_COLLECTION_NS, "SourceFrameReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "SampleFrameName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "ValidPeriod"),
        qn(DATA_COLLECTION_NS, "CustodianReference"),
        qn(DATA_COLLECTION_NS, "SampleFrameAccess"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(DATA_COLLECTION_NS, "UnitsOfFrame"),
        qn(DATA_COLLECTION_NS, "FrameLimitations"),
        qn(DATA_COLLECTION_NS, "AuxiliaryInformation"),
        qn(DATA_COLLECTION_NS, "ReferencePeriod"),
        qn(DATA_COLLECTION_NS, "UpdateProcedure"),
        qn(DATA_COLLECTION_NS, "SourceFrameReference"),
    ]


@dataclass
class SampleStepFields(MaintainableBase):
    """A ControlConstruct that provides a specialized act for generating a sample."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SampleStep")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    condition_for_acceptances: list[Element] = field(default_factory=list)  # [0..*]
    command_code: Optional[Element] = None  # [0..1]
    stratification: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "condition_for_acceptances": (qn(DATA_COLLECTION_NS, "ConditionForAcceptance"), "element", True),
        "command_code": (qn(REUSABLE_NS, "CommandCode"), "element", False),
        "stratification": (qn(DATA_COLLECTION_NS, "Stratification"), "element", False),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "ConditionForAcceptance"),
        qn(REUSABLE_NS, "CommandCode"),
        qn(DATA_COLLECTION_NS, "Stratification"),
    ]


@dataclass
class SampleFields(MaintainableBase):
    """Describes a sample created by the implementation of a sample plan."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Sample")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_sample: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    population_of_concerns: list[Element] = field(default_factory=list)  # [0..*]
    overall_target_sample_sizes: list[Element] = field(default_factory=list)  # [0..*]
    overall_sample_size: Optional[Element] = None  # [0..1]
    application_details: list[Element] = field(default_factory=list)  # [0..*]
    date_of_samples: list[Element] = field(default_factory=list)  # [0..*]
    sample_location_references: list[Reference] = field(default_factory=list)  # [0..*]
    sampling_plan_implemented_references: list[Reference] = field(default_factory=list)  # [0..*]
    sample_frame_used_references: list[Reference] = field(default_factory=list)  # [0..*]
    component_sample_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_sample": (qn(DATA_COLLECTION_NS, "TypeOfSample"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "SampleName"), "intl_string", True),
        "population_of_concerns": (qn(DATA_COLLECTION_NS, "PopulationOfConcern"), "element", True),
        "overall_target_sample_sizes": (qn(DATA_COLLECTION_NS, "OverallTargetSampleSize"), "element", True),
        "overall_sample_size": (qn(DATA_COLLECTION_NS, "OverallSampleSize"), "element", False),
        "application_details": (qn(DATA_COLLECTION_NS, "ApplicationDetails"), "element", True),
        "date_of_samples": (qn(DATA_COLLECTION_NS, "DateOfSample"), "element", True),
        "sample_location_references": (qn(DATA_COLLECTION_NS, "SampleLocationReference"), "reference", True),
        "sampling_plan_implemented_references": (qn(DATA_COLLECTION_NS, "SamplingPlanImplementedReference"), "reference", True),
        "sample_frame_used_references": (qn(DATA_COLLECTION_NS, "SampleFrameUsedReference"), "reference", True),
        "component_sample_references": (qn(DATA_COLLECTION_NS, "ComponentSampleReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfSample"),
        qn(DATA_COLLECTION_NS, "SampleName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "PopulationOfConcern"),
        qn(DATA_COLLECTION_NS, "OverallTargetSampleSize"),
        qn(DATA_COLLECTION_NS, "OverallSampleSize"),
        qn(DATA_COLLECTION_NS, "ApplicationDetails"),
        qn(DATA_COLLECTION_NS, "DateOfSample"),
        qn(DATA_COLLECTION_NS, "SampleLocationReference"),
        qn(DATA_COLLECTION_NS, "SamplingPlanImplementedReference"),
        qn(DATA_COLLECTION_NS, "SampleFrameUsedReference"),
        qn(DATA_COLLECTION_NS, "ComponentSampleReference"),
    ]


@dataclass
class SamplingInformationGroupFields(MaintainableBase):
    """A grouping of Sampling Information objects for administrative purposes. Contains a group of sampling information objects and/or sampling information groups, which may be hierarchical."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SamplingInformationGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_sampling_information_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    sample_frame_references: list[Reference] = field(default_factory=list)  # [0..*]
    sampling_plan_references: list[Reference] = field(default_factory=list)  # [0..*]
    sample_references: list[Reference] = field(default_factory=list)  # [0..*]
    sampling_information_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_sampling_information_group": (qn(DATA_COLLECTION_NS, "TypeOfSamplingInformationGroup"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "SamplingInformationGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "sample_frame_references": (qn(DATA_COLLECTION_NS, "SampleFrameReference"), "reference", True),
        "sampling_plan_references": (qn(DATA_COLLECTION_NS, "SamplingPlanReference"), "reference", True),
        "sample_references": (qn(DATA_COLLECTION_NS, "SampleReference"), "reference", True),
        "sampling_information_group_references": (qn(DATA_COLLECTION_NS, "SamplingInformationGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfSamplingInformationGroup"),
        qn(DATA_COLLECTION_NS, "SamplingInformationGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(DATA_COLLECTION_NS, "SampleFrameReference"),
        qn(DATA_COLLECTION_NS, "SamplingPlanReference"),
        qn(DATA_COLLECTION_NS, "SampleReference"),
        qn(DATA_COLLECTION_NS, "SamplingInformationGroupReference"),
    ]


@dataclass
class SamplingInformationSchemeFields(MaintainableBase):
    """A set of sampling information maintained by an agency including sampling plans, sample frames, and samples."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SamplingInformationScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    sampling_information_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    sample_frames: list[Element] = field(default_factory=list)  # [0..*]
    sample_frame_references: list[Reference] = field(default_factory=list)  # [0..*]
    sampling_plans: list[Element] = field(default_factory=list)  # [0..*]
    sampling_plan_references: list[Reference] = field(default_factory=list)  # [0..*]
    samples: list[Element] = field(default_factory=list)  # [0..*]
    sample_references: list[Reference] = field(default_factory=list)  # [0..*]
    sampling_information_groups: list[Element] = field(default_factory=list)  # [0..*]
    sampling_information_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DATA_COLLECTION_NS, "SamplingInformationSchemeName"), "intl_string", True),
        "sampling_information_scheme_references": (qn(REUSABLE_NS, "SamplingInformationSchemeReference"), "reference", True),
        "sample_frames": (qn(DATA_COLLECTION_NS, "SampleFrame"), "element", True),
        "sample_frame_references": (qn(DATA_COLLECTION_NS, "SampleFrameReference"), "reference", True),
        "sampling_plans": (qn(DATA_COLLECTION_NS, "SamplingPlan"), "element", True),
        "sampling_plan_references": (qn(DATA_COLLECTION_NS, "SamplingPlanReference"), "reference", True),
        "samples": (qn(DATA_COLLECTION_NS, "Sample"), "element", True),
        "sample_references": (qn(DATA_COLLECTION_NS, "SampleReference"), "reference", True),
        "sampling_information_groups": (qn(DATA_COLLECTION_NS, "SamplingInformationGroup"), "element", True),
        "sampling_information_group_references": (qn(DATA_COLLECTION_NS, "SamplingInformationGroupReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "SamplingInformationSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "SamplingInformationSchemeReference"),
        qn(DATA_COLLECTION_NS, "SampleFrame"),
        qn(DATA_COLLECTION_NS, "SampleFrameReference"),
        qn(DATA_COLLECTION_NS, "SamplingPlan"),
        qn(DATA_COLLECTION_NS, "SamplingPlanReference"),
        qn(DATA_COLLECTION_NS, "Sample"),
        qn(DATA_COLLECTION_NS, "SampleReference"),
        qn(DATA_COLLECTION_NS, "SamplingInformationGroup"),
        qn(DATA_COLLECTION_NS, "SamplingInformationGroupReference"),
    ]


@dataclass
class SamplingPlanFields(MaintainableBase):
    """An inline description of a sampling plan (how the sample is drawn). A sampling plan is intended to be versioned over time and can be reused by multiple studies."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SamplingPlan")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_sampling_plan: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    intended_target_population: Optional[Element] = None  # [0..1]
    intended_survey_population: Optional[Element] = None  # [0..1]
    split_rationale: Optional[Element] = None  # [0..1]
    control_construct_reference: Optional[Reference] = None  # [0..1]
    stratification_rationale: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_sampling_plan": (qn(DATA_COLLECTION_NS, "TypeOfSamplingPlan"), "code_value", False),
        "names": (qn(DATA_COLLECTION_NS, "SamplingPlanName"), "intl_string", True),
        "intended_target_population": (qn(DATA_COLLECTION_NS, "IntendedTargetPopulation"), "element", False),
        "intended_survey_population": (qn(DATA_COLLECTION_NS, "IntendedSurveyPopulation"), "element", False),
        "split_rationale": (qn(DATA_COLLECTION_NS, "SplitRationale"), "element", False),
        "control_construct_reference": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", False),
        "stratification_rationale": (qn(DATA_COLLECTION_NS, "StratificationRationale"), "element", False),
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
        qn(DATA_COLLECTION_NS, "TypeOfSamplingPlan"),
        qn(DATA_COLLECTION_NS, "SamplingPlanName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "IntendedTargetPopulation"),
        qn(DATA_COLLECTION_NS, "IntendedSurveyPopulation"),
        qn(DATA_COLLECTION_NS, "SplitRationale"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
        qn(DATA_COLLECTION_NS, "StratificationRationale"),
    ]


@dataclass
class SamplingProcedureFields(MaintainableBase):
    """Describes a sampling procedure. If multiple sampling procedures were used repeat this element for each."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SamplingProcedure")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_sampling_procedure: Optional[CodeValue] = None  # [0..1]
    sampling_plan_reference: Optional[Reference] = None  # [0..1]
    sample_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_sampling_procedure": (qn(DATA_COLLECTION_NS, "TypeOfSamplingProcedure"), "code_value", False),
        "sampling_plan_reference": (qn(DATA_COLLECTION_NS, "SamplingPlanReference"), "reference", False),
        "sample_reference": (qn(DATA_COLLECTION_NS, "SampleReference"), "reference", False),
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
        qn(DATA_COLLECTION_NS, "TypeOfSamplingProcedure"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "SamplingPlanReference"),
        qn(DATA_COLLECTION_NS, "SampleReference"),
    ]


@dataclass
class SamplingStageFields(MaintainableBase):
    """A ControlConstruct that provides a sequence order within Sampling Stages expressed as control constructs."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SamplingStage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    type_of_sequences: list[CodeValue] = field(default_factory=list)  # [0..*]
    control_construct_references: list[Reference] = field(default_factory=list)  # [0..*]
    construct_sequence: Optional[Element] = None  # [0..1]
    frame_requirements: Optional[Element] = None  # [0..1]
    recommended_sample_frame_references: list[Reference] = field(default_factory=list)  # [0..*]
    stratifications: list[Element] = field(default_factory=list)  # [0..*]
    sampling_unit_reference: Optional[Reference] = None  # [0..1]
    selection_probability: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "type_of_sequences": (qn(DATA_COLLECTION_NS, "TypeOfSequence"), "code_value", True),
        "control_construct_references": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", True),
        "construct_sequence": (qn(DATA_COLLECTION_NS, "ConstructSequence"), "element", False),
        "frame_requirements": (qn(DATA_COLLECTION_NS, "FrameRequirements"), "element", False),
        "recommended_sample_frame_references": (qn(DATA_COLLECTION_NS, "RecommendedSampleFrameReference"), "reference", True),
        "stratifications": (qn(DATA_COLLECTION_NS, "Stratification"), "element", True),
        "sampling_unit_reference": (qn(DATA_COLLECTION_NS, "SamplingUnitReference"), "reference", False),
        "selection_probability": (qn(DATA_COLLECTION_NS, "SelectionProbability"), "element", False),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "TypeOfSequence"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
        qn(DATA_COLLECTION_NS, "ConstructSequence"),
        qn(DATA_COLLECTION_NS, "FrameRequirements"),
        qn(DATA_COLLECTION_NS, "RecommendedSampleFrameReference"),
        qn(DATA_COLLECTION_NS, "Stratification"),
        qn(DATA_COLLECTION_NS, "SamplingUnitReference"),
        qn(DATA_COLLECTION_NS, "SelectionProbability"),
    ]


@dataclass
class ScaleDomainFields(MaintainableBase):
    """A response domain capturing a scale response which describes a 1..n dimensional scale of various display types for a question item. Includes standard response domain elements; OutParameter, designatio"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ScaleDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    scale_dimensions: list[Element] = field(default_factory=list)  # [0..*]
    dimension_intersects: list[Element] = field(default_factory=list)  # [0..*]
    display_layout: Optional[CodeValue] = None  # [0..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "scale_dimensions": (qn(REUSABLE_NS, "ScaleDimension"), "element", True),
        "dimension_intersects": (qn(REUSABLE_NS, "DimensionIntersect"), "element", True),
        "display_layout": (qn(REUSABLE_NS, "DisplayLayout"), "code_value", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "ScaleDimension"),
        qn(REUSABLE_NS, "DimensionIntersect"),
        qn(REUSABLE_NS, "DisplayLayout"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class SelectDimensionFields(MaintainableBase):
    """For each dimension in the grid define the applicable values as "all values", a "specific value" or a range. If a rangeMinimum or rangeMaximum is provided without the other, the assumption is unbounded"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SelectDimension")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    rank: Optional[int] = None  # @attr
    allValues: Optional[bool] = None  # @attr
    specificValue: Optional[str] = None  # @attr
    rangeMinimum: Optional[str] = None  # @attr
    rangeMaximum: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "rank": ("rank", "int"),
        "allValues": ("allValues", "bool"),
        "specificValue": ("specificValue", "str"),
        "rangeMinimum": ("rangeMinimum", "str"),
        "rangeMaximum": ("rangeMaximum", "str"),
    }


@dataclass
class SequenceFields(MaintainableBase):
    """A member of the ControlConstruct substitution group. Provides a sequence order for operations expressed as control constructs. The sequence can be typed to support local processing or classification f"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Sequence")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    type_of_sequences: list[CodeValue] = field(default_factory=list)  # [0..*]
    control_construct_references: list[Reference] = field(default_factory=list)  # [0..*]
    construct_sequence: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "type_of_sequences": (qn(DATA_COLLECTION_NS, "TypeOfSequence"), "code_value", True),
        "control_construct_references": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", True),
        "construct_sequence": (qn(DATA_COLLECTION_NS, "ConstructSequence"), "element", False),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "TypeOfSequence"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
        qn(DATA_COLLECTION_NS, "ConstructSequence"),
    ]


@dataclass
class SizeFields(MaintainableBase):
    """Consists of an integer value and specification of the unit. The unit may be specified using a controlled vocabulary."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Size")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    unit_type_reference: Optional[Reference] = None  # [0..1]
    number_of_units: Optional[int] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "unit_type_reference": (qn(REUSABLE_NS, "UnitTypeReference"), "reference", False),
        "number_of_units": (qn(DATA_COLLECTION_NS, "NumberOfUnits"), "int", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "UnitTypeReference"),
        qn(DATA_COLLECTION_NS, "NumberOfUnits"),
    ]


@dataclass
class SourceReferenceFields(MaintainableBase):
    """Reference to an input used in the derivation or coding instruction. TypeOfObject should be set to Variable, QuestionItem, QuestionGrid, or MeasurementItem."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SourceReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_object: Optional[Element] = None  # [1..1]
    alias: Optional[str] = None  # [0..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "alias": (qn(REUSABLE_NS, "Alias"), "str", False),
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
        qn(REUSABLE_NS, "Alias"),
    ]


@dataclass
class SpecificSequenceFields(MaintainableBase):
    """Describes the ordering of items when not otherwise indicated. There are a set number of values for ItemSequenceType, but also a provision for describing an alternate ordering using a command language."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SpecificSequence")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    item_sequence_type: Optional[Element] = None  # [1..1]
    alternate_sequence_type: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "item_sequence_type": (qn(DATA_COLLECTION_NS, "ItemSequenceType"), "element", False),
        "alternate_sequence_type": (qn(DATA_COLLECTION_NS, "AlternateSequenceType"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "ItemSequenceType"),
        qn(DATA_COLLECTION_NS, "AlternateSequenceType"),
    ]


@dataclass
class SplitJoinFields(MaintainableBase):
    """A member of the ControlConstruct substitution group. The components of a SplitJoin consists of a number of process steps to be executed concurrently with partial synchronization. SplitJoin consists of"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SplitJoin")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    type_of_sequences: list[CodeValue] = field(default_factory=list)  # [0..*]
    control_construct_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "type_of_sequences": (qn(DATA_COLLECTION_NS, "TypeOfSequence"), "code_value", True),
        "control_construct_references": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "TypeOfSequence"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
    ]


@dataclass
class SplitFields(MaintainableBase):
    """A member of the ControlConstruct substitution group. The components of a Split consists of a number of process steps to be executed concurrently with partial synchronization. Split completes as soon a"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Split")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    type_of_sequences: list[CodeValue] = field(default_factory=list)  # [0..*]
    control_construct_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "type_of_sequences": (qn(DATA_COLLECTION_NS, "TypeOfSequence"), "code_value", True),
        "control_construct_references": (qn(DATA_COLLECTION_NS, "ControlConstructReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "TypeOfSequence"),
        qn(DATA_COLLECTION_NS, "ControlConstructReference"),
    ]


@dataclass
class StandardWeightFields(MaintainableBase):
    """Provides an identified value for a standard weight expressed as an xs:float. This object may be referenced by a variable or statistic and used as a weight for analysis."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "StandardWeight")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    standard_weight_value: Optional[float] = None  # [1..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "standard_weight_value": (qn(DATA_COLLECTION_NS, "StandardWeightValue"), "float", False),
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
        qn(DATA_COLLECTION_NS, "StandardWeightValue"),
    ]


@dataclass
class StatementItemFields(MaintainableBase):
    """A textual statement used in the Instrument. A substitution for ControlConstruct. In addition to the objects found in ControlConstruct StatementItem adds the text for display at the specified point wit"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "StatementItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    construct_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    external_aids: list[Element] = field(default_factory=list)  # [0..*]
    external_interviewer_instructions: list[Element] = field(default_factory=list)  # [0..*]
    interviewer_instruction_references: list[Reference] = field(default_factory=list)  # [0..*]
    development_results_references: list[Reference] = field(default_factory=list)  # [0..*]
    display_texts: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "construct_names": (qn(DATA_COLLECTION_NS, "ConstructName"), "intl_string", True),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "external_aids": (qn(DATA_COLLECTION_NS, "ExternalAid"), "element", True),
        "external_interviewer_instructions": (qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"), "element", True),
        "interviewer_instruction_references": (qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"), "reference", True),
        "development_results_references": (qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"), "reference", True),
        "display_texts": (qn(DATA_COLLECTION_NS, "DisplayText"), "element", True),
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
        qn(DATA_COLLECTION_NS, "ConstructName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(DATA_COLLECTION_NS, "ExternalAid"),
        qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
        qn(DATA_COLLECTION_NS, "DevelopmentResultsReference"),
        qn(DATA_COLLECTION_NS, "DisplayText"),
    ]


@dataclass
class StimulusMaterialFields(MaintainableBase):
    """Description and link to the StimulusMaterial using the DDI Other Material structure."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "StimulusMaterial")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    other_material: Optional[Element] = None  # [1..1]
    other_material_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "other_material": (qn(REUSABLE_NS, "OtherMaterial"), "element", False),
        "other_material_reference": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
    ]


@dataclass
class StratificationRationaleFields(MaintainableBase):
    """Describe the purpose for stratifying your sample frame prior to sampling."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "StratificationRationale")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
    ]


@dataclass
class StratificationFields(MaintainableBase):
    """Describe all stratifications here. Note that each stratified group will be sampled using the same sampling plan. For example stratifying a state by ZIP Code areas in each of 5 mean income quintiles an"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Stratification")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    stratification_rationale: Optional[Element] = None  # [0..1]
    allocation_method: Optional[Element] = None  # [0..1]
    strataNumber: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "stratification_rationale": (qn(DATA_COLLECTION_NS, "StratificationRationale"), "element", False),
        "allocation_method": (qn(DATA_COLLECTION_NS, "AllocationMethod"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "strataNumber": ("strataNumber", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "StratificationRationale"),
        qn(DATA_COLLECTION_NS, "AllocationMethod"),
    ]


@dataclass
class StructuredMixedGridResponseDomainFields(MaintainableBase):
    """Contains a mixture of response domains for the grid cells. Each response domain can be attached to a specific region of the grid, for example a single column or row. It is assumed that each cell will """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "StructuredMixedGridResponseDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    grid_response_domain_in_mixeds: list[Element] = field(default_factory=list)  # [0..*]
    no_data_by_definitions: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "grid_response_domain_in_mixeds": (qn(DATA_COLLECTION_NS, "GridResponseDomainInMixed"), "element", True),
        "no_data_by_definitions": (qn(DATA_COLLECTION_NS, "NoDataByDefinition"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "GridResponseDomainInMixed"),
        qn(DATA_COLLECTION_NS, "NoDataByDefinition"),
    ]


@dataclass
class StructuredMixedResponseDomainFields(MaintainableBase):
    """A structure to allow for mixing multiple response domains in a single question. These may also include intervening text statements that are tightly bound to a response domain. A common example is the """

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "StructuredMixedResponseDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    response_text_sets: list[Element] = field(default_factory=list)  # [0..*]
    response_domain_in_mixeds: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "response_text_sets": (qn(DATA_COLLECTION_NS, "ResponseTextSet"), "element", True),
        "response_domain_in_mixeds": (qn(DATA_COLLECTION_NS, "ResponseDomainInMixed"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "ResponseTextSet"),
        qn(DATA_COLLECTION_NS, "ResponseDomainInMixed"),
    ]


@dataclass
class TargetSampleSizeFields(MaintainableBase):
    """The desired sample size for this particular sample plan express in relation to its strata number if relevant. Provides means of expressing the formula used for determining the sample size."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "TargetSampleSize")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    strata_number: Optional[int] = None  # [0..1]
    desired_sample_size: Optional[Element] = None  # [1..1]
    sample_size_formula_reference: Optional[Reference] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "strata_number": (qn(DATA_COLLECTION_NS, "StrataNumber"), "int", False),
        "desired_sample_size": (qn(DATA_COLLECTION_NS, "DesiredSampleSize"), "element", False),
        "sample_size_formula_reference": (qn(DATA_COLLECTION_NS, "SampleSizeFormulaReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "StrataNumber"),
        qn(DATA_COLLECTION_NS, "DesiredSampleSize"),
        qn(DATA_COLLECTION_NS, "SampleSizeFormulaReference"),
    ]


@dataclass
class TextContentFields(MaintainableBase):
    """Abstract type existing as the head of a substitution group. May be replaced by any valid member of the substitution group TextContent. Provides the common element Description to all members using Text"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "TextContent")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    pass
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class TextFields(MaintainableBase):
    """The static portion of the text expressed as a StructuredString with the ability to preserve whitespace if critical to the understanding of the content."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Text")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    h1s: list[Element] = field(default_factory=list)  # [0..*]
    h2s: list[Element] = field(default_factory=list)  # [0..*]
    h3s: list[Element] = field(default_factory=list)  # [0..*]
    h4s: list[Element] = field(default_factory=list)  # [0..*]
    h5s: list[Element] = field(default_factory=list)  # [0..*]
    h6s: list[Element] = field(default_factory=list)  # [0..*]
    uls: list[Element] = field(default_factory=list)  # [0..*]
    ols: list[Element] = field(default_factory=list)  # [0..*]
    dls: list[Element] = field(default_factory=list)  # [0..*]
    ps: list[Element] = field(default_factory=list)  # [0..*]
    divs: list[Element] = field(default_factory=list)  # [0..*]
    pres: list[Element] = field(default_factory=list)  # [0..*]
    blockquotes: list[Element] = field(default_factory=list)  # [0..*]
    address: list[Element] = field(default_factory=list)  # [0..*]
    hrs: list[Element] = field(default_factory=list)  # [0..*]
    tables: list[Element] = field(default_factory=list)  # [0..*]
    lang: Optional[str] = None  # @attr
    isTranslated: Optional[bool] = None  # @attr
    isTranslatable: Optional[bool] = None  # @attr
    translationSourceLanguage: Optional[str] = None  # @attr
    translationDate: Optional[str] = None  # @attr
    isPlainText: Optional[bool] = None  # @attr
    textFormat: Optional[str] = None  # @attr
    space: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "h1s": (qn("http://www.w3.org/1999/xhtml", "h1"), "element", True),
        "h2s": (qn("http://www.w3.org/1999/xhtml", "h2"), "element", True),
        "h3s": (qn("http://www.w3.org/1999/xhtml", "h3"), "element", True),
        "h4s": (qn("http://www.w3.org/1999/xhtml", "h4"), "element", True),
        "h5s": (qn("http://www.w3.org/1999/xhtml", "h5"), "element", True),
        "h6s": (qn("http://www.w3.org/1999/xhtml", "h6"), "element", True),
        "uls": (qn("http://www.w3.org/1999/xhtml", "ul"), "element", True),
        "ols": (qn("http://www.w3.org/1999/xhtml", "ol"), "element", True),
        "dls": (qn("http://www.w3.org/1999/xhtml", "dl"), "element", True),
        "ps": (qn("http://www.w3.org/1999/xhtml", "p"), "element", True),
        "divs": (qn("http://www.w3.org/1999/xhtml", "div"), "element", True),
        "pres": (qn("http://www.w3.org/1999/xhtml", "pre"), "element", True),
        "blockquotes": (qn("http://www.w3.org/1999/xhtml", "blockquote"), "element", True),
        "address": (qn("http://www.w3.org/1999/xhtml", "address"), "element", True),
        "hrs": (qn("http://www.w3.org/1999/xhtml", "hr"), "element", True),
        "tables": (qn("http://www.w3.org/1999/xhtml", "table"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "lang": ("lang", "str"),
        "isTranslated": ("isTranslated", "bool"),
        "isTranslatable": ("isTranslatable", "bool"),
        "translationSourceLanguage": ("translationSourceLanguage", "str"),
        "translationDate": ("translationDate", "str"),
        "isPlainText": ("isPlainText", "bool"),
        "textFormat": ("textFormat", "str"),
        "space": ("space", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn("http://www.w3.org/1999/xhtml", "h1"),
        qn("http://www.w3.org/1999/xhtml", "h2"),
        qn("http://www.w3.org/1999/xhtml", "h3"),
        qn("http://www.w3.org/1999/xhtml", "h4"),
        qn("http://www.w3.org/1999/xhtml", "h5"),
        qn("http://www.w3.org/1999/xhtml", "h6"),
        qn("http://www.w3.org/1999/xhtml", "ul"),
        qn("http://www.w3.org/1999/xhtml", "ol"),
        qn("http://www.w3.org/1999/xhtml", "dl"),
        qn("http://www.w3.org/1999/xhtml", "p"),
        qn("http://www.w3.org/1999/xhtml", "div"),
        qn("http://www.w3.org/1999/xhtml", "pre"),
        qn("http://www.w3.org/1999/xhtml", "blockquote"),
        qn("http://www.w3.org/1999/xhtml", "address"),
        qn("http://www.w3.org/1999/xhtml", "hr"),
        qn("http://www.w3.org/1999/xhtml", "table"),
    ]
    _MIXED: ClassVar[bool] = True


@dataclass
class TimeMethodFields(MaintainableBase):
    """Describes the time method or time dimension of the data collection. This may cover specific timing issues such as when a data collection instrument is fielded (time of year, month, week, day), intende"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "TimeMethod")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_time_method: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_time_method": (qn(DATA_COLLECTION_NS, "TypeOfTimeMethod"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "TypeOfTimeMethod"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class TranslationActivityFields(MaintainableBase):
    """A substitution for DevelopmentActivity which describes the specifics of translation, looking at source and target languages, aids available for translation, and translator requirements regarding langu"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "TranslationActivity")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    development_activity_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    desired_outcome: Optional[Element] = None  # [0..1]
    process_summary: Optional[Element] = None  # [0..1]
    recommended_staff_requirements: list[Element] = field(default_factory=list)  # [0..*]
    additional_required_resources: Optional[Element] = None  # [0..1]
    debriefing_process: Optional[Element] = None  # [0..1]
    translation_methods: list[Element] = field(default_factory=list)  # [0..*]
    translation_requirements: Optional[Element] = None  # [0..1]
    translation_aids: list[Element] = field(default_factory=list)  # [0..*]
    translator_requirements: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    translationSourceLanguage: Optional[str] = None  # @attr
    translationTargetLanguage: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "development_activity_names": (qn(DATA_COLLECTION_NS, "DevelopmentActivityName"), "intl_string", True),
        "desired_outcome": (qn(DATA_COLLECTION_NS, "DesiredOutcome"), "element", False),
        "process_summary": (qn(DATA_COLLECTION_NS, "ProcessSummary"), "element", False),
        "recommended_staff_requirements": (qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"), "element", True),
        "additional_required_resources": (qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"), "element", False),
        "debriefing_process": (qn(DATA_COLLECTION_NS, "DebriefingProcess"), "element", False),
        "translation_methods": (qn(DATA_COLLECTION_NS, "TranslationMethod"), "element", True),
        "translation_requirements": (qn(DATA_COLLECTION_NS, "TranslationRequirements"), "element", False),
        "translation_aids": (qn(DATA_COLLECTION_NS, "TranslationAid"), "element", True),
        "translator_requirements": (qn(DATA_COLLECTION_NS, "TranslatorRequirements"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "translationSourceLanguage": ("translationSourceLanguage", "str"),
        "translationTargetLanguage": ("translationTargetLanguage", "str"),
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
        qn(DATA_COLLECTION_NS, "DevelopmentActivityName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "DesiredOutcome"),
        qn(DATA_COLLECTION_NS, "ProcessSummary"),
        qn(DATA_COLLECTION_NS, "RecommendedStaffRequirements"),
        qn(DATA_COLLECTION_NS, "AdditionalRequiredResources"),
        qn(DATA_COLLECTION_NS, "DebriefingProcess"),
        qn(DATA_COLLECTION_NS, "TranslationMethod"),
        qn(DATA_COLLECTION_NS, "TranslationRequirements"),
        qn(DATA_COLLECTION_NS, "TranslationAid"),
        qn(DATA_COLLECTION_NS, "TranslatorRequirements"),
    ]


@dataclass
class TranslationAidResourceFields(MaintainableBase):
    """Provides a reference to the translation aid resource using the structure of OtherMaterial."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "TranslationAidResource")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    other_material: Optional[Element] = None  # [1..1]
    other_material_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "other_material": (qn(REUSABLE_NS, "OtherMaterial"), "element", False),
        "other_material_reference": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
    ]


@dataclass
class TranslationAidFields(MaintainableBase):
    """Describes available aids for translation typed by a controlled vocabulary and supporting a description and resource identification where appropriate. This may include items such as the availability of"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "TranslationAid")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_translation_aid: Optional[CodeValue] = None  # [0..1]
    translation_aid_resource: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_translation_aid": (qn(DATA_COLLECTION_NS, "TypeOfTranslationAid"), "code_value", False),
        "translation_aid_resource": (qn(DATA_COLLECTION_NS, "TranslationAidResource"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "TypeOfTranslationAid"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "TranslationAidResource"),
    ]


@dataclass
class TranslationMethodFields(MaintainableBase):
    """Describes both minimum and preferred language abilities sought for the translation work as a set of source and target language requirements."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "TranslationMethod")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_translation_method: Optional[CodeValue] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_translation_method": (qn(DATA_COLLECTION_NS, "TypeOfTranslationMethod"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "TypeOfTranslationMethod"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class TranslationRequirementsFields(MaintainableBase):
    """Provides a detailed description of the requirements for an acceptable translation and indicate if the translation should be oral and/or written. Supports multiple language versions of the same content"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "TranslationRequirements")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    isOral: Optional[bool] = None  # @attr
    isWritten: Optional[bool] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isOral": ("isOral", "bool"),
        "isWritten": ("isWritten", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class TranslatorRequirementsFields(MaintainableBase):
    """Describes both minimum and preferred language abilities sought for the translation work as a set of source and target language requirements."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "TranslatorRequirements")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    translation_source_language_ability: Optional[Element] = None  # [0..1]
    translation_target_language_ability: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "translation_source_language_ability": (qn(DATA_COLLECTION_NS, "TranslationSourceLanguageAbility"), "element", False),
        "translation_target_language_ability": (qn(DATA_COLLECTION_NS, "TranslationTargetLanguageAbility"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "TranslationSourceLanguageAbility"),
        qn(DATA_COLLECTION_NS, "TranslationTargetLanguageAbility"),
    ]


@dataclass
class UsageGuideFields(MaintainableBase):
    """A guide to the appropriate usage of the weights generated by the processing event."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "UsageGuide")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    usage_example: Optional[Element] = None  # [0..1]
    usage_restrictions: Optional[Element] = None  # [0..1]
    usage_recommendations: Optional[Element] = None  # [0..1]
    command_codes: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "usage_example": (qn(DATA_COLLECTION_NS, "UsageExample"), "element", False),
        "usage_restrictions": (qn(DATA_COLLECTION_NS, "UsageRestrictions"), "element", False),
        "usage_recommendations": (qn(DATA_COLLECTION_NS, "UsageRecommendations"), "element", False),
        "command_codes": (qn(REUSABLE_NS, "CommandCode"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATA_COLLECTION_NS, "UsageExample"),
        qn(DATA_COLLECTION_NS, "UsageRestrictions"),
        qn(DATA_COLLECTION_NS, "UsageRecommendations"),
        qn(REUSABLE_NS, "CommandCode"),
    ]


@dataclass
class WeightingMethodologyFields(MaintainableBase):
    """A basic structure for describing the methodology used for weighting. In addition to a descriptive narrative, the methodology may be classified by a short term or external controlled vocabulary."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "WeightingMethodology")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_weighting_methodology: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_weighting_methodology": (qn(DATA_COLLECTION_NS, "TypeOfWeightingMethodology"), "code_value", False),
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
        qn(DATA_COLLECTION_NS, "TypeOfWeightingMethodology"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class WeightingFields(MaintainableBase):
    """Describes the weighting used in the process. In addition to a description of the weighting process it may be designated as a specific type of weighting. If the data uses a standard weight (each record"""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Weighting")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    type_of_weighting: Optional[CodeValue] = None  # [0..1]
    weighting_methodology_references: list[Reference] = field(default_factory=list)  # [0..*]
    analysis_unit: Optional[CodeValue] = None  # [0..1]
    usage_guide: Optional[Element] = None  # [0..1]
    standard_weights: list[Element] = field(default_factory=list)  # [0..*]
    based_on_sample_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_weighting": (qn(DATA_COLLECTION_NS, "TypeOfWeighting"), "code_value", False),
        "weighting_methodology_references": (qn(DATA_COLLECTION_NS, "WeightingMethodologyReference"), "reference", True),
        "analysis_unit": (qn(REUSABLE_NS, "AnalysisUnit"), "code_value", False),
        "usage_guide": (qn(DATA_COLLECTION_NS, "UsageGuide"), "element", False),
        "standard_weights": (qn(DATA_COLLECTION_NS, "StandardWeight"), "element", True),
        "based_on_sample_references": (qn(DATA_COLLECTION_NS, "BasedOnSampleReference"), "reference", True),
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
        qn(DATA_COLLECTION_NS, "TypeOfWeighting"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "WeightingMethodologyReference"),
        qn(REUSABLE_NS, "AnalysisUnit"),
        qn(DATA_COLLECTION_NS, "UsageGuide"),
        qn(DATA_COLLECTION_NS, "StandardWeight"),
        qn(DATA_COLLECTION_NS, "BasedOnSampleReference"),
    ]

