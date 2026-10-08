"""Shared maintainable model fixture definitions for round-trip tests."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from importlib import resources
from pathlib import Path

from ddi_l.models import (
    Archive,
    Category,
    ClassificationFamily,
    ClassificationItem,
    ClassificationScheme,
    ClassificationSeries,
    CodeList,
    CollectionActivity,
    CollectionEvent,
    Comparison,
    ComputationItem,
    Concept,
    ConceptMap,
    ConceptualComponent,
    ConceptualVariable,
    DataCaptureDevelopment,
    DataCaptureMethod,
    DataCollection,
    GeneralInstruction,
    GenerationInstruction,
    Group,
    IfThenElse,
    InformationClassification,
    Instruction,
    InstructionGroup,
    Instrument,
    InterviewerInstructionScheme,
    LogicalProduct,
    MaintainableBase,
    ManagedMissingValuesRepresentation,
    Methodology,
    MethodologyItem,
    MethodologyScheme,
    ObservationPlan,
    Organization,
    PhysicalInstance,
    PhysicalInstanceGroup,
    PhysicalStructure,
    Process,
    ProcessControl,
    ProcessControlScheme,
    ProcessingEvent,
    ProcessingEventScheme,
    ProcessingInstructionGroup,
    ProcessingInstructionScheme,
    ProcessMethod,
    ProcessMethodScheme,
    ProcessScheme,
    ProcessStep,
    ProcessStepScheme,
    QualityScheme,
    QualityStandard,
    QualityStandardGroup,
    QualityStatement,
    QualityStatementGroup,
    QuestionBlock,
    QuestionConstruct,
    QuestionGrid,
    QuestionGroup,
    QuestionItem,
    QuestionMap,
    QuestionScheme,
    RepresentedVariable,
    ResourcePackage,
    ReviewEvent,
    SamplingInformationGroup,
    SamplingInformationScheme,
    SamplingPlan,
    Sequence,
    StatementItem,
    StudyUnit,
    UnitType,
    Universe,
    Variable,
    VariableGroup,
    VariableMap,
    Weighting,
    WeightingMethodology,
)

MODEL_FIXTURE_DIR = Path(
    resources.files("ddi_l").joinpath("examples", "tests", "fixtures", "models")  # type: ignore[arg-type]
)

MODEL_FIXTURES: Mapping[type[MaintainableBase], Iterable[str]] = {
    Archive: ("archive_minimal", "archive_with_specific"),
    Category: ("category_representative",),
    ClassificationFamily: ("classification_family_nested",),
    ClassificationSeries: ("classification_series_with_scheme",),
    ClassificationScheme: ("classification_scheme_deep",),
    ClassificationItem: ("classification_item_nested",),
    CodeList: ("code_list_minimal", "code_list_full"),
    Comparison: (
        "comparison_minimal",
        "comparison_full",
        "comparison_multi_name",
        "comparison_with_maps",
    ),
    Concept: ("concept_minimal", "concept_full"),
    ConceptualComponent: (
        "conceptual_component_minimal",
        "conceptual_component_full",
        "conceptual_component_representative",
    ),
    ConceptualVariable: (
        "conceptual_variable_minimal",
        "conceptual_variable_full",
        "conceptual_variable_representative",
    ),
    ConceptMap: ("concept_map_with_items",),
    ComputationItem: ("computation_item_full",),
    DataCollection: (
        "data_collection_minimal",
        "data_collection_full",
        "data_collection_with_extra",
        "data_collection_questionnaire",
    ),
    CollectionEvent: ("collection_event_minimal",),
    CollectionActivity: (
        "collection_activity_administrative",
        "collection_activity_sensor",
    ),
    ObservationPlan: (
        "observation_plan_administrative",
        "observation_plan_sensor",
    ),
    DataCaptureMethod: (
        "data_capture_method_administrative",
        "data_capture_method_sensor",
    ),
    DataCaptureDevelopment: ("data_capture_development_minimal",),
    Methodology: ("methodology_nested",),
    MethodologyScheme: ("methodology_scheme_with_items",),
    MethodologyItem: ("methodology_item_sampling",),
    ReviewEvent: ("review_event_minimal",),
    GeneralInstruction: ("general_instruction_minimal",),
    GenerationInstruction: ("generation_instruction_minimal",),
    Group: ("group_minimal",),
    IfThenElse: ("if_then_else_full",),
    InformationClassification: (
        "information_classification_minimal",
        "information_classification_full",
    ),
    Instrument: ("instrument_minimal", "instrument_full"),
    Instruction: ("instruction_with_texts",),
    InstructionGroup: ("instruction_group_with_reference",),
    InterviewerInstructionScheme: ("interviewer_instruction_scheme_nested",),
    LogicalProduct: ("logical_product_minimal", "logical_product_full"),
    ManagedMissingValuesRepresentation: (
        "managed_missing_values_representation_minimal",
        "managed_missing_values_representation_full",
    ),
    Organization: ("organization_minimal",),
    Process: ("process_with_inline_components",),
    ProcessControl: ("process_control_minimal",),
    ProcessControlScheme: ("process_control_scheme_minimal",),
    ProcessMethod: ("process_method_with_command",),
    ProcessMethodScheme: ("process_method_scheme_minimal",),
    ProcessScheme: ("process_scheme_with_processes",),
    ProcessStep: ("process_step_with_components",),
    ProcessStepScheme: ("process_step_scheme_minimal",),
    PhysicalInstance: ("physical_instance_minimal",),
    PhysicalStructure: ("physical_structure_minimal", "physical_structure_full"),
    PhysicalInstanceGroup: (
        "physical_instance_group_minimal",
        "physical_instance_group_full",
    ),
    ProcessingEvent: ("processing_event_with_operations",),
    ProcessingEventScheme: ("processing_event_scheme_with_groups",),
    ProcessingInstructionGroup: ("processing_instruction_group_minimal",),
    ProcessingInstructionScheme: ("processing_instruction_scheme_minimal",),
    QuestionBlock: ("question_block_with_references",),
    QuestionGrid: ("question_grid_with_dimension",),
    QuestionGroup: ("question_group_with_references",),
    QuestionItem: ("question_item_minimal", "question_item_full"),
    QuestionMap: ("question_map_with_correspondence",),
    QuestionScheme: ("question_scheme_with_fragments",),
    QuestionConstruct: ("question_construct_full",),
    QualityScheme: ("quality_scheme_minimal", "quality_scheme_nested"),
    QualityStandard: ("quality_standard_minimal", "quality_standard_enriched"),
    QualityStandardGroup: (
        "quality_standard_group_minimal",
        "quality_standard_group_enriched",
    ),
    QualityStatement: (
        "quality_statement_minimal",
        "quality_statement_with_other_statement",
        "quality_statement_enriched",
    ),
    QualityStatementGroup: (
        "quality_statement_group_minimal",
        "quality_statement_group_enriched",
    ),
    RepresentedVariable: ("represented_variable_with_code",),
    ResourcePackage: ("resource_package_minimal",),
    Sequence: ("sequence_minimal",),
    StatementItem: ("statement_item_full",),
    StudyUnit: (
        "study_unit_minimal",
        "study_unit_with_inline_modules",
        "study_unit_with_conceptual_component",
    ),
    Universe: ("universe_minimal", "universe_full"),
    UnitType: ("unit_type_minimal", "unit_type_full", "unit_type_representative"),
    Variable: ("variable_minimal", "variable_full", "variable_enriched"),
    VariableGroup: ("variable_group_minimal",),
    VariableMap: ("variable_map_with_items",),
    Weighting: ("weighting_full",),
    WeightingMethodology: ("weighting_methodology_full",),
    SamplingPlan: ("sampling_plan_minimal",),
    SamplingInformationGroup: ("sampling_information_group_minimal",),
    SamplingInformationScheme: ("sampling_information_scheme_minimal",),
}


def iter_maintainable_fixture_names() -> Iterator[tuple[type[MaintainableBase], str]]:
    """Yield (model, fixture) pairs for all maintainable fixture samples."""

    for model, fixtures in MODEL_FIXTURES.items():
        for fixture in fixtures:
            yield model, fixture


def fixture_path(fixture_name: str) -> Path:
    """Return the XML fixture path for the provided maintainable sample."""

    return MODEL_FIXTURE_DIR / f"{fixture_name}.xml"


__all__ = [
    "MODEL_FIXTURES",
    "MODEL_FIXTURE_DIR",
    "fixture_path",
    "iter_maintainable_fixture_names",
]
