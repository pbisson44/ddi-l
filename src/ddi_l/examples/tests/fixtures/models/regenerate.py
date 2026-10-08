"""Utility script for regenerating model XML fixtures and golden outputs."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from uuid import UUID, uuid5

from ddi_l._etree import (
    Element,
    cleanup_namespaces,
    create_element,
    parse_xml,
    tostring,
)
from ddi_l.constants import (
    ARCHIVE_NS,
    COMPARATIVE_NS,
    CONCEPTUAL_COMPONENT_NS,
    DATA_COLLECTION_NS,
    DEFAULT_NSMAP,
    INSTANCE_NS,
    LOGICAL_PRODUCT_NS,
    PHYSICAL_DATA_PRODUCT_NS,
    REUSABLE_NS,
    STUDY_UNIT_NS,
)
from ddi_l.models import (
    Archive,
    Category,
    CodeList,
    CodeRepresentation,
    CollectionActivity,
    CollectionEvent,
    Comparison,
    ComputationItem,
    Concept,
    ConceptMap,
    ConceptualComponent,
    ConceptualVariable,
    DataCaptureMethod,
    DataCollection,
    IfThenElse,
    InformationClassification,
    Instrument,
    LogicalProduct,
    ManagedMissingValuesRepresentation,
    ObservationPlan,
    PhysicalInstanceGroup,
    PhysicalStructure,
    ProcessingEvent,
    ProcessingEventScheme,
    QuestionConstruct,
    QuestionItem,
    QuestionMap,
    RepresentedVariable,
    StatementItem,
    StudyUnit,
    UnitType,
    Universe,
    Variable,
    VariableMap,
    Weighting,
    WeightingMethodology,
)
from ddi_l.models.base import CodeValue, InternationalString, Reference, qn
from ddi_l.models.datacollection import ElseIf
from ddi_l.models.dissemination import (
    Correspondence,
    ItemMap,
    StandardWeight,
    UsageGuide,
)
from ddi_l.models.logicalproduct import (
    CodeItem,
    NumberRange,
    NumericRepresentation,
    TextRepresentation,
)

FIXTURE_DIR = Path(__file__).parent
QUALITY_OF_LIFE_PATH = Path(__file__).resolve().parents[3] / "Quality_of_Life.xml"


CANONICAL_PREFIXES = dict(DEFAULT_NSMAP)
CANONICAL_PREFIXES.update(
    {
        "a": ARCHIVE_NS,
        "c": CONCEPTUAL_COMPONENT_NS,
        "cmp": COMPARATIVE_NS,
        "d": DATA_COLLECTION_NS,
        "l": LOGICAL_PRODUCT_NS,
        "p": PHYSICAL_DATA_PRODUCT_NS,
        "s": STUDY_UNIT_NS,
    }
)


FIXTURE_DEFAULT_AGENCY = "ca.statcan"
FIXTURE_NAMESPACE = UUID("da543305-75a4-559f-b750-0ef55cc8ef52")


def _fixture_identifier(seed: str, *, agency: str = FIXTURE_DEFAULT_AGENCY) -> str:
    return str(uuid5(FIXTURE_NAMESPACE, f"{agency}:{seed}"))


def _fixture_identity(
    seed: str,
    *,
    agency: str = FIXTURE_DEFAULT_AGENCY,
    version: str = "1",
) -> dict[str, str]:
    return {
        "agency": agency,
        "identifier": _fixture_identifier(seed, agency=agency),
        "version": version,
    }


def _fixture_reference(
    seed: str,
    *,
    agency: str = FIXTURE_DEFAULT_AGENCY,
    version: str = "1",
    type_of_object: str | None = None,
) -> Reference:
    return Reference(
        type_of_object=type_of_object,
        **_fixture_identity(seed, agency=agency, version=version),
    )


@lru_cache
def _quality_of_life_document() -> Element:
    return parse_xml(QUALITY_OF_LIFE_PATH)


@lru_cache
def _quality_of_life_fragments() -> dict[str, list[Element]]:
    fragments: dict[str, list[Element]] = {}
    document = _quality_of_life_document()
    for fragment in document.findall(f".//{{{INSTANCE_NS}}}Fragment"):
        if not len(fragment):
            continue
        child = fragment[0]
        local = child.tag.split("}", 1)[1] if child.tag.startswith("{") else child.tag
        fragments.setdefault(local, []).append(child)
    return fragments


def _quality_of_life_fragment(
    local_name: str, identifier: str | None = None
) -> Element:
    candidates = _quality_of_life_fragments().get(local_name, [])
    for candidate in candidates:
        if identifier is None:
            return deepcopy(candidate)
        id_el = candidate.find(qn(REUSABLE_NS, "ID"))
        if id_el is not None and id_el.text == identifier:
            return deepcopy(candidate)
    available = [
        cand.findtext(qn(REUSABLE_NS, "ID"))
        for cand in candidates
        if cand.find(qn(REUSABLE_NS, "ID")) is not None
    ]
    available_text = ", ".join(filter(None, available)) or "<none>"
    raise ValueError(
        f"No {local_name} fragment with identifier {identifier!r} found in {QUALITY_OF_LIFE_PATH}."
        f" Available identifiers: {available_text}."
    )


def write_pair(name: str, element_builder) -> None:
    pretty_path = FIXTURE_DIR / f"{name}.xml"
    golden_path = FIXTURE_DIR / f"{name}.golden.xml"
    element = element_builder()
    cleanup_namespaces(element, CANONICAL_PREFIXES)
    pretty_path.write_text(tostring(element, pretty_print=True))
    golden_path.write_text(tostring(element, pretty_print=False))


def _build_command_code(language: str, *, description: str, content: str) -> Element:
    command_code = create_element(qn(REUSABLE_NS, "CommandCode"))
    command_code.append(
        InternationalString(
            text=description, lang="en", child_tag="Content"
        ).to_element("Description")
    )
    command = create_element(qn(REUSABLE_NS, "Command"))
    command.append(CodeValue(text=language).to_xml("ProgramLanguage"))
    command_content = create_element(qn(REUSABLE_NS, "CommandContent"))
    command_content.text = content
    command.append(command_content)
    command_code.append(command)
    return command_code


def information_classification_full() -> Element:
    policy_source = create_element(qn(REUSABLE_NS, "AuthorizedPolicySource"))
    policy_source.append(
        _fixture_reference("policy-manual", type_of_object="OtherMaterial").to_xml(
            "OtherMaterialReference"
        )
    )
    return InformationClassification(
        **_fixture_identity("info-class-secure"),
        type_of_information_classification=CodeValue(
            text="DataHandling",
            controlled_vocabulary_id="InfoClassType",
        ),
        level_of_information_classification=CodeValue(
            text="Restricted",
            controlled_vocabulary_id="InfoClassLevel",
        ),
        agency_organization_reference=_fixture_reference(
            "security-team", type_of_object="Organization"
        ),
        data_handling_personnel_rules=[
            InternationalString(
                text="Analysts must complete confidentiality training.",
                lang="en",
                child_tag="Content",
            ),
            InternationalString(
                text="Access reviews occur quarterly.",
                lang="en",
                child_tag="String",
            ),
        ],
        data_encryption_rules=[
            InternationalString(text="Apply AES-256 encryption at rest.", lang="en")
        ],
        data_storage_rules=[
            InternationalString(
                text="Store only on segmented secure servers.", lang="en"
            )
        ],
        disposal_rules=[
            InternationalString(text="Shred printed extracts after use.", lang="en")
        ],
        data_transfer_rules=[
            InternationalString(
                text="Transfer via managed SFTP endpoints only.", lang="en"
            )
        ],
        authorized_policy_sources=[policy_source],
    ).to_xml()


def information_classification_minimal() -> Element:
    return InformationClassification(
        **_fixture_identity("info-class-minimal"),
    ).to_xml()


def managed_missing_values_representation_full() -> Element:
    code_rep = CodeRepresentation(
        blank_is_missing_value=True,
        code_list_reference=Reference(
            type_of_object="CodeList",
            **_fixture_identity("codes-missing"),
        ),
        other_attributes={"missingValue": "-7"},
    )
    numeric_rep = NumericRepresentation(
        blank_is_missing_value=False,
        number_range=NumberRange(
            low="-9",
            high="-1",
            low_is_inclusive=True,
            high_is_inclusive=False,
        ),
        numeric_type_code="Integer",
        other_attributes={"missingValue": "-9 -8"},
    )
    generic_format = create_element(qn(REUSABLE_NS, "GenericOutputFormat"))
    generic_format.text = "Placeholder"
    text_rep = TextRepresentation(
        blank_is_missing_value=False,
        other_attributes={"maxLength": "16"},
        other_elements=[generic_format],
    )
    binding = create_element(qn(REUSABLE_NS, "Binding"))
    binding.append(
        Reference(
            type_of_object="OutParameter",
            **_fixture_identity("source-value"),
        ).to_xml("SourceParameterReference")
    )
    binding.append(
        Reference(
            type_of_object="InParameter",
            **_fixture_identity("target-value"),
        ).to_xml("TargetParameterReference")
    )
    return ManagedMissingValuesRepresentation(
        **_fixture_identity("missing-values-standard"),
        names=[
            InternationalString(
                text="Standard missing set", lang="en", child_tag="String"
            ),
            InternationalString(text="Legacy format", lang="en"),
        ],
        labels=[InternationalString(text="Managed missing values", lang="en")],
        missing_code_representations=[code_rep],
        missing_numeric_representations=[numeric_rep],
        missing_text_representations=[text_rep],
        processing_instruction_reference=Reference(
            type_of_object="GenerationInstruction",
            **_fixture_identity("derive-missing"),
        ),
        processing_instruction_reference_extras=[binding],
        blank_is_missing_value=False,
        other_attributes={"scopeOfUniqueness": "demo"},
    ).to_xml()


def managed_missing_values_representation_minimal() -> Element:
    return ManagedMissingValuesRepresentation(
        **_fixture_identity("missing-values-minimal"),
    ).to_xml()


def _build_if_condition(
    description: str, *, content: str, language: str = "python"
) -> Element:
    condition = create_element(qn(DATA_COLLECTION_NS, "IfCondition"))
    condition.append(
        _build_command_code(language, description=description, content=content)
    )
    return condition


def _processing_event_instance() -> ProcessingEvent:
    control_operation = create_element(qn(DATA_COLLECTION_NS, "ControlOperation"))
    control_operation.append(
        InternationalString(
            text="Validate incoming records", lang="en", child_tag="Content"
        ).to_element("Description")
    )
    control_operation.append(
        Reference(
            type_of_object="Organization",
            **_fixture_identity("quality-team"),
        ).to_xml("AgencyOrganizationReference")
    )

    cleaning_operation = create_element(qn(DATA_COLLECTION_NS, "CleaningOperation"))
    cleaning_operation.append(
        InternationalString(
            text="Remove duplicate records", lang="en", child_tag="Content"
        ).to_element("Description")
    )

    weighting_reference = Reference(
        type_of_object="Weighting",
        **_fixture_identity("weighting-2024"),
    )

    weighting_identity = _fixture_identity("weighting-2024")
    weighting = create_element(qn(DATA_COLLECTION_NS, "Weighting"))
    for tag, key in (
        ("Agency", "agency"),
        ("ID", "identifier"),
        ("Version", "version"),
    ):
        el = create_element(qn(REUSABLE_NS, tag))
        el.text = weighting_identity[key]
        weighting.append(el)
    weighting.append(
        CodeValue(text="PostStratification").to_xml(
            "TypeOfWeighting", namespace=DATA_COLLECTION_NS
        )
    )
    weighting.append(
        InternationalString(
            text="Post stratification weighting", lang="en", child_tag="Content"
        ).to_element("Description")
    )

    data_appraisal = create_element(qn(DATA_COLLECTION_NS, "DataAppraisalInformation"))
    response_rate = create_element(qn(DATA_COLLECTION_NS, "ResponseRate"))
    sample_size = create_element(qn(DATA_COLLECTION_NS, "SampleSize"))
    sample_size.text = "1000"
    response_rate.append(sample_size)
    responses = create_element(qn(DATA_COLLECTION_NS, "NumberOfResponses"))
    responses.text = "910"
    response_rate.append(responses)
    rate = create_element(qn(DATA_COLLECTION_NS, "SpecificResponseRate"))
    rate.text = "91.0"
    response_rate.append(rate)
    response_rate.append(
        InternationalString(
            text="Initial wave response", lang="en", child_tag="Content"
        ).to_element("Description")
    )
    data_appraisal.append(response_rate)
    data_appraisal.append(
        InternationalString(
            text="Sampling error below threshold", lang="en", child_tag="Content"
        ).to_element("SamplingError")
    )

    instruction_reference = Reference(
        type_of_object="GenerationInstruction",
        **_fixture_identity("gen-instruction-1"),
    ).to_xml("ProcessingInstructionReference")

    quality_reference = Reference(
        type_of_object="QualityStatement",
        **_fixture_identity("quality-2024"),
    )

    return ProcessingEvent(
        **_fixture_identity("processing-event-cleaning"),
        names=[InternationalString(text="Cleaning run", lang="en", child_tag="String")],
        control_operations=[control_operation],
        cleaning_operations=[cleaning_operation],
        weightings=[weighting],
        weighting_references=[weighting_reference],
        data_appraisal_information=[data_appraisal],
        processing_instruction_references=[instruction_reference],
        quality_statement_references=[quality_reference],
    )


def _processing_event_group_element(event: ProcessingEvent) -> Element:
    group = create_element(qn(DATA_COLLECTION_NS, "ProcessingEventGroup"))
    group_identity = _fixture_identity("processing-group")
    for tag, key in (
        ("Agency", "agency"),
        ("ID", "identifier"),
        ("Version", "version"),
    ):
        el = create_element(qn(REUSABLE_NS, tag))
        el.text = group_identity[key]
        group.append(el)
    group.append(
        CodeValue(text="QualityControl").to_xml(
            "TypeOfProcessingEventGroup", namespace=DATA_COLLECTION_NS
        )
    )
    name_container = create_element(qn(DATA_COLLECTION_NS, "ProcessingEventGroupName"))
    name_container.append(
        InternationalString(text="QA Checks", lang="en", child_tag="String").to_child(
            child_tag="String"
        )
    )
    group.append(name_container)
    group.append(
        InternationalString(
            text="Quality assurance events", lang="en", child_tag="Content"
        ).to_element("Label")
    )
    group.append(
        InternationalString(
            text="Checks performed after collection", lang="en", child_tag="Content"
        ).to_element("Description")
    )
    group.append(
        Reference(
            type_of_object="Universe",
            **_fixture_identity("universe-adults"),
        ).to_xml("UniverseReference")
    )
    group.append(
        Reference(
            type_of_object="Concept",
            **_fixture_identity("concept-quality"),
        ).to_xml("ConceptReference")
    )
    group.append(
        Reference(
            type_of_object="ProcessingEvent",
            agency=event.agency,
            identifier=event.identifier,
            version=event.version,
        ).to_xml("ProcessingEventReference", namespace=DATA_COLLECTION_NS)
    )
    group.set("isOrdered", "true")
    return group


def computation_item_full():
    return ComputationItem(
        **_fixture_identity("compute-weight"),
        construct_names=[
            InternationalString(
                text="Weight computation", lang="en", child_tag="String"
            )
        ],
        type_of_computation_item=CodeValue(text="WeightAdjustment"),
        command_code=_build_command_code(
            "python",
            description="Generate weight",
            content="weight = base_weight * factor",
        ),
        assigned_variable_reference=Reference(
            type_of_object="Variable",
            **_fixture_identity("var-weight"),
        ),
    ).to_xml()


def statement_item_full():
    display_text = create_element(qn(DATA_COLLECTION_NS, "DisplayText"))
    literal = create_element(qn(DATA_COLLECTION_NS, "LiteralText"))
    text_el = create_element(qn(DATA_COLLECTION_NS, "Text"))
    text_el.append(
        InternationalString(
            text="Please review your answers carefully.", lang="en", child_tag="Content"
        ).to_child()
    )
    literal.append(text_el)
    display_text.append(literal)
    return StatementItem(
        **_fixture_identity("statement-review"),
        construct_names=[
            InternationalString(text="Review statement", lang="en", child_tag="String")
        ],
        display_texts=[display_text],
    ).to_xml()


def if_then_else_full():
    then_reference = Reference(
        type_of_object="QuestionConstruct",
        **_fixture_identity("qc-income"),
    )
    else_reference = Reference(
        type_of_object="StatementItem",
        **_fixture_identity("statement-review"),
    )
    branch = ElseIf(
        if_condition=_build_if_condition(
            description="Income greater than threshold",
            content="income > 50000",
        ),
        then_construct_reference=Reference(
            type_of_object="ComputationItem",
            **_fixture_identity("compute-weight"),
        ),
    )
    return IfThenElse(
        **_fixture_identity("if-income-check"),
        construct_names=[
            InternationalString(text="Income logic", lang="en", child_tag="String")
        ],
        type_of_if_then_else=CodeValue(text="ConditionalFlow"),
        if_condition=_build_if_condition(
            description="Income missing", content="income is None"
        ),
        then_construct_reference=then_reference,
        else_if_branches=[branch],
        else_construct_reference=else_reference,
    ).to_xml()


def question_construct_full():
    response_sequence = create_element(qn(DATA_COLLECTION_NS, "ResponseSequence"))
    response_sequence.append(create_element(qn(DATA_COLLECTION_NS, "ItemSequenceType")))
    response_sequence[0].text = "InOrderOfAppearance"

    dimension_sequence = create_element(qn(DATA_COLLECTION_NS, "DimensionSequence"))
    dimension_sequence.append(
        create_element(qn(DATA_COLLECTION_NS, "ItemSequenceType"))
    )
    dimension_sequence[0].text = "Other"
    alternate_sequence = create_element(qn(DATA_COLLECTION_NS, "AlternateSequenceType"))
    alternate_sequence.append(
        InternationalString(
            text="Rotate daily", lang="en", child_tag="Content"
        ).to_element("Description")
    )
    dimension_sequence.append(alternate_sequence)

    return QuestionConstruct(
        **_fixture_identity("qc-income"),
        construct_names=[
            InternationalString(text="Income question", lang="en", child_tag="String")
        ],
        question_reference=Reference(
            type_of_object="QuestionItem",
            **_fixture_identity("question-income"),
        ),
        response_sequence=response_sequence,
        dimension_sequence=dimension_sequence,
        response_unit=CodeValue(
            text="Household", controlled_vocabulary_id="ResponseUnit"
        ),
        analysis_units=[
            CodeValue(text="Person", controlled_vocabulary_id="AnalysisUnit"),
            CodeValue(text="Household", controlled_vocabulary_id="AnalysisUnit"),
        ],
        universe_references=[
            Reference(
                type_of_object="Universe",
                **_fixture_identity("universe-adults"),
            )
        ],
        estimatedSecondsResponseTime=45.0,
    ).to_xml()


def processing_event_with_operations():
    return _processing_event_instance().to_xml()


def processing_event_scheme_with_groups():
    event = _processing_event_instance()
    group = _processing_event_group_element(event)
    return ProcessingEventScheme(
        **_fixture_identity("processing-scheme"),
        names=[
            InternationalString(text="Cleaning workflow", lang="en", child_tag="String")
        ],
        processing_event_scheme_references=[
            Reference(
                type_of_object="ProcessingEventScheme",
                **_fixture_identity("prior-scheme"),
            )
        ],
        processing_events=[event],
        processing_event_references=[
            Reference(
                type_of_object="ProcessingEvent",
                agency=event.agency,
                identifier=event.identifier,
                version=event.version,
            )
        ],
        processing_event_groups=[group],
        processing_event_group_references=[
            Reference(
                type_of_object="ProcessingEventGroup",
                **_fixture_identity("external-group"),
            )
        ],
    ).to_xml()


def data_collection_full():
    instrument = Instrument(
        **_fixture_identity("inst-1"),
        names=[
            InternationalString(text="Main instrument", lang="en", child_tag="String")
        ],
    )
    question = QuestionItem(
        **_fixture_identity("q1"),
        question_texts=[
            InternationalString(
                text="How satisfied are you?",
                lang="en",
                child_tag="Content",
                is_plain_text=True,
            )
        ],
    )
    return DataCollection(
        **_fixture_identity("collect-1"),
        instruments=[instrument],
        questions=[question],
    ).to_xml()


def data_collection_minimal():
    return DataCollection(
        **_fixture_identity("collect-empty"),
        instrument_references=[
            _fixture_reference("inst-empty", type_of_object="Instrument"),
        ],
    ).to_xml()


def data_collection_with_extra():
    return DataCollection(
        **_fixture_identity("collect-extra"),
        collection_events=[
            CollectionEvent(
                **_fixture_identity("collect-event-1"),
                names=[
                    InternationalString(text="Wave 1", lang="en", child_tag="String")
                ],
            )
        ],
    ).to_xml()


def collection_activity_administrative():
    return CollectionActivity(
        **_fixture_identity("activity-admin"),
        names=[
            InternationalString(
                text="Administrative records import", lang="en", child_tag="String"
            )
        ],
        activity_types=[
            CodeValue(text="BatchLoad", controlled_vocabulary_id="collection-mode")
        ],
        data_source_references=[
            Reference(
                type_of_object="DataSource",
                **_fixture_identity("admin-register"),
            )
        ],
        collection_event_references=[
            Reference(
                type_of_object="CollectionEvent",
                **_fixture_identity("collect-event-1"),
            )
        ],
        observation_plan_references=[
            Reference(
                type_of_object="ObservationPlan",
                **_fixture_identity("plan-admin"),
            )
        ],
    ).to_xml()


def collection_activity_sensor():
    return CollectionActivity(
        **_fixture_identity("activity-sensor"),
        names=[InternationalString(text="Sensor sweep", lang="en", child_tag="String")],
        activity_types=[
            CodeValue(
                text="AutomatedPolling", controlled_vocabulary_id="collection-mode"
            )
        ],
        data_source_references=[
            Reference(
                type_of_object="DataSource",
                **_fixture_identity("sensor-network"),
            )
        ],
        collection_event_references=[
            Reference(
                type_of_object="CollectionEvent",
                **_fixture_identity("collect-event-2"),
            )
        ],
        observation_plan_references=[
            Reference(
                type_of_object="ObservationPlan",
                **_fixture_identity("plan-sensor"),
            )
        ],
    ).to_xml()


def observation_plan_administrative():
    return ObservationPlan(
        **_fixture_identity("plan-admin"),
        names=[
            InternationalString(
                text="Quarterly register snapshot", lang="en", child_tag="String"
            )
        ],
        plan_types=[CodeValue(text="Administrative", controlled_vocabulary_id="plan")],
        observation_units=[
            CodeValue(text="Case", controlled_vocabulary_id="observation-unit")
        ],
        collection_activity_references=[
            Reference(
                type_of_object="CollectionActivity",
                **_fixture_identity("activity-admin"),
            )
        ],
        collection_event_references=[
            Reference(
                type_of_object="CollectionEvent",
                **_fixture_identity("collect-event-1"),
            )
        ],
        observation_sequence_references=[
            Reference(
                type_of_object="ObservationSequence",
                **_fixture_identity("sequence-admin"),
            )
        ],
    ).to_xml()


def observation_plan_sensor():
    return ObservationPlan(
        **_fixture_identity("plan-sensor"),
        names=[
            InternationalString(
                text="Hourly sensor pass", lang="en", child_tag="String"
            )
        ],
        plan_types=[CodeValue(text="Sensor", controlled_vocabulary_id="plan")],
        observation_units=[
            CodeValue(text="Station", controlled_vocabulary_id="observation-unit")
        ],
        collection_activity_references=[
            Reference(
                type_of_object="CollectionActivity",
                **_fixture_identity("activity-sensor"),
            )
        ],
        collection_event_references=[
            Reference(
                type_of_object="CollectionEvent",
                **_fixture_identity("collect-event-2"),
            )
        ],
        observation_sequence_references=[
            Reference(
                type_of_object="ObservationSequence",
                **_fixture_identity("sequence-sensor"),
            )
        ],
    ).to_xml()


def data_capture_method_administrative():
    return DataCaptureMethod(
        **_fixture_identity("capture-admin"),
        names=[
            InternationalString(
                text="Administrative pipeline", lang="en", child_tag="String"
            )
        ],
        method_types=[
            CodeValue(
                text="AdministrativeRecords", controlled_vocabulary_id="capture-method"
            )
        ],
        data_source_references=[
            Reference(
                type_of_object="DataSource",
                **_fixture_identity("admin-register"),
            )
        ],
        collection_activity_references=[
            Reference(
                type_of_object="CollectionActivity",
                **_fixture_identity("activity-admin"),
            )
        ],
        collection_event_references=[
            Reference(
                type_of_object="CollectionEvent",
                **_fixture_identity("collect-event-1"),
            )
        ],
        observation_plan_references=[
            Reference(
                type_of_object="ObservationPlan",
                **_fixture_identity("plan-admin"),
            )
        ],
    ).to_xml()


def data_capture_method_sensor():
    return DataCaptureMethod(
        **_fixture_identity("capture-sensor"),
        names=[
            InternationalString(
                text="Sensor network capture", lang="en", child_tag="String"
            )
        ],
        method_types=[
            CodeValue(text="SensorFeed", controlled_vocabulary_id="capture-method")
        ],
        data_source_references=[
            Reference(
                type_of_object="DataSource",
                **_fixture_identity("sensor-network"),
            )
        ],
        collection_activity_references=[
            Reference(
                type_of_object="CollectionActivity",
                **_fixture_identity("activity-sensor"),
            )
        ],
        collection_event_references=[
            Reference(
                type_of_object="CollectionEvent",
                **_fixture_identity("collect-event-2"),
            )
        ],
        observation_plan_references=[
            Reference(
                type_of_object="ObservationPlan",
                **_fixture_identity("plan-sensor"),
            )
        ],
    ).to_xml()


def instrument_full():
    return Instrument(
        **_fixture_identity("inst-1"),
        names=[
            InternationalString(text="Main instrument", lang="en", child_tag="String")
        ],
    ).to_xml()


def instrument_minimal():
    return Instrument(
        **_fixture_identity("inst-empty"),
    ).to_xml()


def question_item_full():
    return QuestionItem(
        **_fixture_identity("question-1"),
        question_texts=[
            InternationalString(
                text="How satisfied are you?",
                lang="en",
                child_tag="Content",
                is_plain_text=True,
            )
        ],
    ).to_xml()


def question_item_minimal():
    return QuestionItem(
        **_fixture_identity("question-empty"),
    ).to_xml()


def logical_product_full():
    code = CodeItem(
        **_fixture_identity("code-1"),
        value="1",
        category=Reference(
            type_of_object="CategoryScheme",
            **_fixture_identity("cat-1"),
        ),
    )
    code.children.append(
        CodeItem(
            **_fixture_identity("code-1-1"),
            value="1.1",
            category=Reference(
                type_of_object="CategoryScheme",
                **_fixture_identity("cat-1-1"),
            ),
        )
    )
    code_list = CodeList(
        **_fixture_identity("codes-1"),
        names=[
            InternationalString(
                text="Satisfaction codes", lang="en", child_tag="String"
            )
        ],
        recommended_datatype="integer",
        codes=[code],
    )
    variable = Variable(
        **_fixture_identity("var-1"),
        names=[InternationalString(text="Satisfaction", lang="en", child_tag="String")],
        concept_references=[
            Reference(
                **_fixture_identity("concept-1"),
                type_of_object="Concept",
            )
        ],
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                **_fixture_identity("question-q1"),
            )
        ],
    )
    return LogicalProduct(
        **_fixture_identity("logical-1"),
        code_lists=[code_list],
        variables=[variable],
    ).to_xml()


def logical_product_minimal():
    return LogicalProduct(
        **_fixture_identity("logical-empty"),
        other_elements=[
            _fixture_reference(
                "variable-scheme-empty", type_of_object="VariableScheme"
            ).to_xml("VariableSchemeReference"),
        ],
    ).to_xml()


def code_list_full():
    code = CodeItem(
        **_fixture_identity("code-1"),
        value="1",
        category=Reference(
            type_of_object="CategoryScheme",
            **_fixture_identity("cat-1"),
        ),
    )
    code.children.append(
        CodeItem(
            **_fixture_identity("code-1-1"),
            value="1.1",
            category=Reference(
                type_of_object="CategoryScheme",
                **_fixture_identity("cat-1-1"),
            ),
        )
    )
    return CodeList(
        **_fixture_identity("codes-1"),
        names=[
            InternationalString(
                text="Satisfaction codes", lang="en", child_tag="String"
            )
        ],
        recommended_datatype="integer",
        codes=[code],
    ).to_xml()


def code_list_minimal():
    return CodeList(
        **_fixture_identity("codes-empty"),
    ).to_xml()


def category_representative():
    fragment = _quality_of_life_fragment(
        "Category", "07339047-b749-43a9-b3d4-6e0889365b1d"
    )
    return Category.from_xml(fragment).to_xml()


def represented_variable_with_code():
    fragment = _quality_of_life_fragment(
        "RepresentedVariable", "79afe111-37e9-41a2-9538-dc27fbbe2448"
    )
    return RepresentedVariable.from_xml(fragment).to_xml()


def variable_enriched():
    fragment = _quality_of_life_fragment(
        "Variable", "1c4258d0-c9b7-4b5a-a3bb-1f88ed8fa9f8"
    )
    return Variable.from_xml(fragment).to_xml()


def variable_full():
    return Variable(
        **_fixture_identity("var-1"),
        names=[InternationalString(text="Satisfaction", lang="en", child_tag="String")],
        concept_references=[
            Reference(
                **_fixture_identity("concept-1"),
                type_of_object="Concept",
            )
        ],
        question_references=[
            Reference(
                **_fixture_identity("question-1"),
                type_of_object="QuestionItem",
            )
        ],
    ).to_xml()


def variable_minimal():
    return Variable(
        **_fixture_identity("var-empty"),
    ).to_xml()


def physical_structure_full():
    return PhysicalStructure(
        **_fixture_identity("physical-1"),
        names=[InternationalString(text="ASCII layout", lang="en", child_tag="String")],
        file_format="text/plain",
        default_data_type="string",
        default_delimiter="comma",
        default_decimal_positions="2",
        default_decimal_separator=".",
        default_digit_group_separator=" ",
    ).to_xml()


def physical_structure_minimal():
    return PhysicalStructure(
        **_fixture_identity("physical-empty"),
    ).to_xml()


def archive_with_specific():
    specific = create_element(qn(ARCHIVE_NS, "ArchiveSpecific"))
    access = create_element(qn(ARCHIVE_NS, "DefaultAccess"))
    access_identity = _fixture_identity("access-1")
    for tag, key in (
        ("Agency", "agency"),
        ("ID", "identifier"),
        ("Version", "version"),
    ):
        el = create_element(qn(REUSABLE_NS, tag))
        el.text = access_identity[key]
        access.append(el)
    name_el = create_element(qn(ARCHIVE_NS, "AccessTypeName"))
    name_el.append(
        InternationalString(
            text="Standard access", lang="en", child_tag="String"
        ).to_child()
    )
    access.append(name_el)
    restriction_el = create_element(qn(ARCHIVE_NS, "Restrictions"))
    restriction_el.append(
        InternationalString(text="None", is_plain_text=True).to_child()
    )
    access.append(restriction_el)
    specific.append(access)
    return Archive(
        **_fixture_identity("archive-1"),
        archive_module_names=[
            InternationalString(text="Main archive", lang="en", child_tag="String")
        ],
        archive_specifics=[specific],
    ).to_xml()


def archive_minimal():
    return Archive(
        **_fixture_identity("archive-empty"),
    ).to_xml()


def concept_full():
    return Concept(
        **_fixture_identity("concept-1"),
        names=[
            InternationalString(
                text="Satisfaction concept", lang="en", child_tag="String"
            )
        ],
    ).to_xml()


def concept_minimal():
    return Concept(
        **_fixture_identity("concept-empty"),
    ).to_xml()


def _build_representative_conceptual_variable() -> ConceptualVariable:
    return ConceptualVariable(
        **_fixture_identity("conceptual-variable-representative"),
        names=[
            InternationalString(
                text="Household size",
                lang="en",
                child_tag="String",
            )
        ],
        labels=[InternationalString(text="Household size", lang="en")],
        descriptions=[
            InternationalString(
                text="Number of usual residents forming one household.",
                lang="en",
            )
        ],
        concept_reference=Reference(
            type_of_object="Concept",
            **_fixture_identity("concept-household"),
        ),
        universe_references=[
            Reference(
                type_of_object="Universe",
                **_fixture_identity("universe-private-households"),
            )
        ],
        unit_type_reference=Reference(
            type_of_object="UnitType",
            **_fixture_identity("unit-type-household"),
        ),
        category_scheme_reference=Reference(
            type_of_object="CategoryScheme",
            **_fixture_identity("cats-household-size"),
        ),
    )


def _build_representative_unit_type() -> UnitType:
    return UnitType(
        **_fixture_identity("unit-type-household"),
        labels=[InternationalString(text="Household", lang="en")],
        descriptions=[
            InternationalString(
                text="Private dwellings treated as analysis units.",
                lang="en",
            )
        ],
        concept_reference=Reference(
            type_of_object="Concept",
            **_fixture_identity("concept-household"),
        ),
    )


def conceptual_component_full():
    concept = Concept(
        **_fixture_identity("concept-1"),
        names=[
            InternationalString(
                text="Satisfaction concept", lang="en", child_tag="String"
            )
        ],
    )
    universe = Universe(
        **_fixture_identity("universe-1"),
        names=[InternationalString(text="Adults 18+", lang="en", child_tag="String")],
    )
    unit_type = UnitType(
        **_fixture_identity("unit-type-1"),
        labels=[InternationalString(text="Person", lang="en")],
        concept_reference=Reference(
            type_of_object="Concept",
            **_fixture_identity("concept-1"),
        ),
    )
    conceptual_variable = ConceptualVariable(
        **_fixture_identity("conceptual-variable-1"),
        names=[
            InternationalString(
                text="Adult satisfaction",
                lang="en",
                child_tag="String",
            )
        ],
        labels=[InternationalString(text="Satisfaction for adults", lang="en")],
        descriptions=[
            InternationalString(text="Tracks satisfaction among adults.", lang="en")
        ],
        concept_reference=Reference(
            type_of_object="Concept",
            **_fixture_identity("concept-1"),
        ),
        universe_references=[
            Reference(
                type_of_object="Universe",
                **_fixture_identity("universe-1"),
            )
        ],
        unit_type_reference=Reference(
            type_of_object="UnitType",
            **_fixture_identity("unit-type-1"),
        ),
        category_scheme_references=[
            Reference(
                type_of_object="CategoryScheme",
                **_fixture_identity("cat-scheme-1"),
            )
        ],
    )
    return ConceptualComponent(
        **_fixture_identity("conceptual-1"),
        concepts=[concept],
        universes=[universe],
        conceptual_variables=[conceptual_variable],
        unit_types=[unit_type],
        has_concept_scheme=True,
        has_universe_scheme=True,
        has_conceptual_variable_scheme=True,
        has_unit_type_scheme=True,
    ).to_xml()


def conceptual_component_minimal():
    return ConceptualComponent(
        **_fixture_identity("conceptual-empty"),
    ).to_xml()


def conceptual_component_representative():
    concept = Concept(
        **_fixture_identity("concept-household"),
        names=[
            InternationalString(
                text="Household concept",
                lang="en",
                child_tag="String",
            )
        ],
        labels=[InternationalString(text="Household", lang="en")],
        descriptions=[
            InternationalString(
                text="Defines a single housing unit occupied by residents.",
                lang="en",
            )
        ],
    )
    universe = Universe(
        **_fixture_identity("universe-private-households"),
        names=[
            InternationalString(
                text="Private households", lang="en", child_tag="String"
            )
        ],
        descriptions=[
            InternationalString(
                text="All non-institutional households within the country.",
                lang="en",
            )
        ],
    )
    conceptual_variable = _build_representative_conceptual_variable()
    unit_type = _build_representative_unit_type()
    return ConceptualComponent(
        **_fixture_identity("conceptual-component-representative"),
        concepts=[concept],
        universes=[universe],
        conceptual_variables=[conceptual_variable],
        unit_types=[unit_type],
        has_concept_scheme=True,
        has_universe_scheme=True,
        has_conceptual_variable_scheme=True,
        has_unit_type_scheme=True,
    ).to_xml()


def conceptual_variable_full():
    return ConceptualVariable(
        **_fixture_identity("conceptual-variable-full"),
        names=[
            InternationalString(
                text="Adult satisfaction", lang="en", child_tag="String"
            )
        ],
        labels=[InternationalString(text="Satisfaction for adults", lang="en")],
        descriptions=[
            InternationalString(text="Tracks satisfaction among adults.", lang="en")
        ],
        concept_reference=Reference(
            type_of_object="Concept",
            **_fixture_identity("concept-1"),
        ),
        universe_references=[
            Reference(
                type_of_object="Universe",
                **_fixture_identity("universe-1"),
            )
        ],
        unit_type_reference=Reference(
            type_of_object="UnitType",
            **_fixture_identity("unit-type-1"),
        ),
        category_scheme_references=[
            Reference(
                type_of_object="CategoryScheme",
                **_fixture_identity("cat-scheme-standalone"),
            )
        ],
    ).to_xml()


def conceptual_variable_minimal():
    return ConceptualVariable(
        **_fixture_identity("conceptual-variable-empty"),
    ).to_xml()


def conceptual_variable_representative():
    return _build_representative_conceptual_variable().to_xml()


def unit_type_full():
    return UnitType(
        **_fixture_identity("unit-type-full"),
        labels=[InternationalString(text="Person", lang="en")],
        descriptions=[
            InternationalString(text="Individuals aged 18 and over.", lang="en")
        ],
        concept_reference=Reference(
            type_of_object="Concept",
            **_fixture_identity("concept-1"),
        ),
    ).to_xml()


def unit_type_minimal():
    return UnitType(
        **_fixture_identity("unit-type-empty"),
        concept_reference=Reference(
            type_of_object="Concept",
            **_fixture_identity("concept-1"),
        ),
    ).to_xml()


def unit_type_representative():
    return _build_representative_unit_type().to_xml()


def universe_full():
    return Universe(
        **_fixture_identity("universe-1"),
        names=[InternationalString(text="Adults 18+", lang="en", child_tag="String")],
    ).to_xml()


def universe_minimal():
    return Universe(
        **_fixture_identity("universe-empty"),
    ).to_xml()


def comparison_full():
    return Comparison(
        **_fixture_identity("comparison-1"),
        names=[
            InternationalString(text="Yearly comparison", lang="en", child_tag="String")
        ],
    ).to_xml()


def comparison_minimal():
    return Comparison(
        **_fixture_identity("comparison-empty"),
    ).to_xml()


def _concept_map_fixture() -> ConceptMap:
    commonality = Correspondence(
        commonalities=[
            InternationalString(
                text="Shared measurement intent", lang="en", child_tag="Content"
            )
        ],
        differences=[
            InternationalString(
                text="Target scheme narrows the scope", lang="en", child_tag="Content"
            )
        ],
        commonality_weight=0.85,
    )
    harmonised_concept_map = ConceptMap(
        **_fixture_identity("concept-map-harmonised"),
        names=[
            InternationalString(
                text="Household concept alignment", lang="en", child_tag="String"
            )
        ],
        type_of_mapped_item=CodeValue(text="Concept"),
        source_scheme_reference=Reference(
            type_of_object="ConceptScheme",
            **_fixture_identity("concepts-original"),
        ),
        target_scheme_reference=Reference(
            type_of_object="ConceptScheme",
            **_fixture_identity("concepts-harmonised", agency="harmonised.agency"),
        ),
        correspondence=commonality,
    )
    harmonised_concept_map.item_maps.extend(
        [
            ItemMap(
                **_fixture_identity("concept-map-item-1"),
                alias="c01",
                source_item_reference=Reference(
                    type_of_object="Concept",
                    **_fixture_identity("concept-income-household"),
                ),
                target_item_references=[
                    Reference(
                        type_of_object="Concept",
                        **_fixture_identity(
                            "concept-income-hh", agency="harmonised.agency"
                        ),
                    ),
                    Reference(
                        type_of_object="Concept",
                        **_fixture_identity(
                            "concept-income-alt", agency="harmonised.agency"
                        ),
                    ),
                ],
                correspondence=Correspondence(
                    commonalities=[
                        InternationalString(
                            text="Both capture household-level totals",
                            lang="en",
                            child_tag="Content",
                        )
                    ],
                    differences=[
                        InternationalString(
                            text="Harmonised definition excludes negative values",
                            lang="en",
                            child_tag="Content",
                        )
                    ],
                    commonality_weight=0.72,
                ),
                related_map_references=[
                    Reference(
                        type_of_object="VariableMap",
                        **_fixture_identity("variable-map-harmonised"),
                    )
                ],
            ),
            ItemMap(
                **_fixture_identity("concept-map-item-2"),
                alias="c02",
                source_item_reference=Reference(
                    type_of_object="Concept",
                    **_fixture_identity("concept-poverty-risk"),
                ),
                target_item_references=[
                    Reference(
                        type_of_object="Concept",
                        **_fixture_identity(
                            "concept-poverty-hrp", agency="harmonised.agency"
                        ),
                    )
                ],
                correspondence=Correspondence(
                    commonalities=[
                        InternationalString(
                            text="Both relate to poverty thresholds",
                            lang="en",
                            child_tag="Content",
                        )
                    ],
                    commonality_weight=0.9,
                ),
            ),
        ]
    )
    return harmonised_concept_map


def _variable_map_fixture() -> VariableMap:
    map_level_correspondence = Correspondence(
        commonalities=[
            InternationalString(
                text="Both derive from household totals", lang="en", child_tag="Content"
            )
        ],
        commonality_weight=0.65,
    )
    variable_map = VariableMap(
        **_fixture_identity("variable-map-harmonised"),
        names=[
            InternationalString(
                text="Income variable alignment", lang="en", child_tag="String"
            )
        ],
        type_of_mapped_item=CodeValue(text="Variable"),
        source_scheme_reference=Reference(
            type_of_object="VariableScheme",
            **_fixture_identity("variables-original"),
        ),
        target_scheme_reference=Reference(
            type_of_object="VariableScheme",
            **_fixture_identity("variables-harmonised", agency="harmonised.agency"),
        ),
        correspondence=map_level_correspondence,
    )
    variable_map.item_maps.append(
        ItemMap(
            **_fixture_identity("variable-map-item-1"),
            alias="v01",
            source_item_reference=Reference(
                type_of_object="Variable",
                **_fixture_identity("var-income-household"),
            ),
            target_item_references=[
                Reference(
                    type_of_object="Variable",
                    **_fixture_identity("var-income-hh", agency="harmonised.agency"),
                )
            ],
            correspondence=Correspondence(
                commonalities=[
                    InternationalString(
                        text="Same measurement units", lang="en", child_tag="Content"
                    )
                ],
                differences=[
                    InternationalString(
                        text="Harmonised variable trims outliers",
                        lang="en",
                        child_tag="Content",
                    )
                ],
                commonality_weight=0.6,
            ),
            related_map_references=[
                Reference(
                    type_of_object="ConceptMap",
                    **_fixture_identity("concept-map-harmonised"),
                ),
                Reference(
                    type_of_object="QuestionMap",
                    **_fixture_identity("question-map-harmonised"),
                ),
            ],
        )
    )
    return variable_map


def _question_map_fixture() -> QuestionMap:
    question_map = QuestionMap(
        **_fixture_identity("question-map-harmonised"),
        names=[
            InternationalString(
                text="Household income question", lang="en", child_tag="String"
            )
        ],
        type_of_mapped_item=CodeValue(text="Question"),
        source_scheme_reference=Reference(
            type_of_object="QuestionScheme",
            **_fixture_identity("questions-original"),
        ),
        target_scheme_reference=Reference(
            type_of_object="QuestionScheme",
            **_fixture_identity("questions-harmonised", agency="harmonised.agency"),
        ),
    )
    question_map.item_maps.append(
        ItemMap(
            **_fixture_identity("question-map-item-1"),
            source_item_reference=Reference(
                type_of_object="QuestionItem",
                **_fixture_identity("qi-income-household"),
            ),
            target_item_references=[
                Reference(
                    type_of_object="QuestionItem",
                    **_fixture_identity("qi-income-hh", agency="harmonised.agency"),
                )
            ],
            correspondence=Correspondence(
                commonalities=[
                    InternationalString(
                        text="Shared universe and response type",
                        lang="en",
                        child_tag="Content",
                    )
                ],
                commonality_weight=0.8,
            ),
            related_map_references=[
                Reference(
                    type_of_object="VariableMap",
                    **_fixture_identity("variable-map-harmonised"),
                )
            ],
        )
    )
    return question_map


def concept_map_with_items():
    return _concept_map_fixture().to_xml()


def variable_map_with_items():
    return _variable_map_fixture().to_xml()


def question_map_with_correspondence():
    return _question_map_fixture().to_xml()


def comparison_with_maps():
    concept_map = _concept_map_fixture()
    variable_map = _variable_map_fixture()
    question_map = _question_map_fixture()
    return Comparison(
        **_fixture_identity("comparison-harmonised"),
        names=[
            InternationalString(
                text="Harmonisation package", lang="en", child_tag="String"
            )
        ],
        concept_maps=[concept_map.to_xml()],
        concept_map_references=[
            Reference(
                type_of_object="ConceptMap",
                agency=concept_map.agency,
                identifier=concept_map.identifier,
                version=concept_map.version,
            )
        ],
        variable_maps=[variable_map.to_xml()],
        question_maps=[question_map.to_xml()],
        question_map_references=[
            Reference(
                type_of_object="QuestionMap",
                agency=question_map.agency,
                identifier=question_map.identifier,
                version=question_map.version,
            )
        ],
    ).to_xml()


def physical_instance_group_minimal():
    return PhysicalInstanceGroup(
        **_fixture_identity("pig-minimal"),
    ).to_xml()


def physical_instance_group_full():
    subject_el = create_element(qn(REUSABLE_NS, "Subject"))
    subject_el.text = "Economics"
    keyword_el = create_element(qn(REUSABLE_NS, "Keyword"))
    keyword_el.text = "Household income"
    return PhysicalInstanceGroup(
        **_fixture_identity("pig-harmonised"),
        type_of_physical_instance_group=CodeValue(text="HarmonisedRelease"),
        names=[
            InternationalString(
                text="Harmonised data bundle", lang="en", child_tag="String"
            )
        ],
        universe_references=[
            Reference(
                type_of_object="Universe",
                **_fixture_identity("universe-1"),
            )
        ],
        concept_reference=Reference(
            type_of_object="Concept",
            **_fixture_identity("concept-income-hh", agency="harmonised.agency"),
        ),
        subjects=[subject_el],
        keywords=[keyword_el],
        physical_instance_references=[
            Reference(
                type_of_object="PhysicalInstance",
                **_fixture_identity("pi-household-2019"),
            ),
            Reference(
                type_of_object="PhysicalInstance",
                **_fixture_identity("pi-household-2020"),
            ),
        ],
        physical_instance_group_references=[
            Reference(
                type_of_object="PhysicalInstanceGroup",
                **_fixture_identity("pig-minimal"),
            )
        ],
        is_ordered=True,
    ).to_xml()


def weighting_methodology_full():
    return WeightingMethodology(
        **_fixture_identity("weighting-methodology"),
        type_of_weighting_methodology=CodeValue(text="PostStratification"),
        descriptions=[
            InternationalString(
                text="Household-level calibration with demographic margins",
                lang="en",
                child_tag="Content",
            )
        ],
    ).to_xml()


def weighting_full():
    usage = UsageGuide(
        examples=[
            InternationalString(
                text="Apply the household weight for population totals",
                lang="en",
                child_tag="Content",
            )
        ],
        restrictions=[
            InternationalString(
                text="Not valid for sub-regional breakdowns",
                lang="en",
                child_tag="Content",
            )
        ],
        recommendations=[
            InternationalString(
                text="Pair with replicate weights for variance estimation",
                lang="en",
                child_tag="Content",
            )
        ],
        command_codes=[
            _build_command_code(
                "R",
                description="Create normalised weights",
                content="weights$household <- hh_weight / mean(hh_weight)",
            )
        ],
    )
    return Weighting(
        **_fixture_identity("weighting-harmonised"),
        type_of_weighting=CodeValue(text="Calibration"),
        descriptions=[
            InternationalString(
                text="Weights calibrated to household counts by region and household size.",
                lang="en",
                child_tag="Content",
            )
        ],
        weighting_methodology_references=[
            Reference(
                type_of_object="WeightingMethodology",
                **_fixture_identity("weighting-methodology"),
            )
        ],
        analysis_unit=CodeValue(text="Household"),
        usage_guide=usage,
        standard_weights=[
            StandardWeight(
                **_fixture_identity("hh-standard-weight"),
                standard_weight_value=1.0,
            ),
            StandardWeight(
                **_fixture_identity("hh-standard-weight-youth"),
                standard_weight_value=0.85,
            ),
        ],
        based_on_sample_references=[
            Reference(
                type_of_object="Sample",
                **_fixture_identity("sample-household"),
            )
        ],
    ).to_xml()


def study_unit_with_inline_modules():
    collection = DataCollection.from_xml(data_collection_full())
    logical = LogicalProduct.from_xml(logical_product_full())
    physical = PhysicalStructure.from_xml(physical_structure_full())
    archive = Archive.from_xml(archive_with_specific())
    concept = Concept.from_xml(concept_full())
    universe = Universe.from_xml(universe_full())
    component = ConceptualComponent(
        **_fixture_identity("study-1-conceptual"),
        concepts=[concept],
        universes=[universe],
    )
    return StudyUnit(
        **_fixture_identity("study-1"),
        data_collections=[collection],
        logical_products=[logical],
        physical_structures=[physical],
        archives=[archive],
        conceptual_components=[component],
    ).to_xml()


def study_unit_with_conceptual_component():
    component = ConceptualComponent.from_xml(conceptual_component_full())
    return StudyUnit(
        **_fixture_identity("study-with-concepts", agency="example.agency"),
        data_collection_references=[
            _fixture_reference("collect-1", type_of_object="DataCollection"),
        ],
        conceptual_components=[component],
    ).to_xml()


def study_unit_minimal():
    title_string = InternationalString(
        text="Census of population - 2026", child_tag="String"
    )
    title = create_element(qn(REUSABLE_NS, "Title"))
    title.append(title_string.to_child())
    citation = create_element(qn(REUSABLE_NS, "Citation"))
    citation.append(title)

    return StudyUnit(
        agency="example.agency",
        identifier="Census2026",
        version="1.0",
        citations=[citation],
        abstracts=[
            InternationalString(
                text="Statistics Canada's 2026 Census of Population study unit."
            )
        ],
        data_collection_references=[
            _fixture_reference(
                "collect-empty",
                agency="example.agency",
                version="1.0",
                type_of_object="DataCollection",
            ),
        ],
    ).to_xml()


BUILDERS = {
    "category_representative": category_representative,
    "code_list_full": code_list_full,
    "code_list_minimal": code_list_minimal,
    "conceptual_component_full": conceptual_component_full,
    "conceptual_component_minimal": conceptual_component_minimal,
    "conceptual_component_representative": conceptual_component_representative,
    "conceptual_variable_full": conceptual_variable_full,
    "conceptual_variable_minimal": conceptual_variable_minimal,
    "conceptual_variable_representative": conceptual_variable_representative,
    "computation_item_full": computation_item_full,
    "data_collection_full": data_collection_full,
    "data_collection_minimal": data_collection_minimal,
    "data_collection_with_extra": data_collection_with_extra,
    "collection_activity_administrative": collection_activity_administrative,
    "collection_activity_sensor": collection_activity_sensor,
    "observation_plan_administrative": observation_plan_administrative,
    "observation_plan_sensor": observation_plan_sensor,
    "data_capture_method_administrative": data_capture_method_administrative,
    "data_capture_method_sensor": data_capture_method_sensor,
    "if_then_else_full": if_then_else_full,
    "information_classification_full": information_classification_full,
    "information_classification_minimal": information_classification_minimal,
    "instrument_full": instrument_full,
    "instrument_minimal": instrument_minimal,
    "managed_missing_values_representation_full": managed_missing_values_representation_full,
    "managed_missing_values_representation_minimal": managed_missing_values_representation_minimal,
    "logical_product_full": logical_product_full,
    "logical_product_minimal": logical_product_minimal,
    "processing_event_scheme_with_groups": processing_event_scheme_with_groups,
    "processing_event_with_operations": processing_event_with_operations,
    "physical_structure_full": physical_structure_full,
    "physical_structure_minimal": physical_structure_minimal,
    "archive_with_specific": archive_with_specific,
    "archive_minimal": archive_minimal,
    "concept_full": concept_full,
    "concept_minimal": concept_minimal,
    "question_construct_full": question_construct_full,
    "question_item_full": question_item_full,
    "question_item_minimal": question_item_minimal,
    "represented_variable_with_code": represented_variable_with_code,
    "statement_item_full": statement_item_full,
    "universe_full": universe_full,
    "universe_minimal": universe_minimal,
    "unit_type_full": unit_type_full,
    "unit_type_minimal": unit_type_minimal,
    "unit_type_representative": unit_type_representative,
    "comparison_full": comparison_full,
    "comparison_minimal": comparison_minimal,
    "comparison_with_maps": comparison_with_maps,
    "concept_map_with_items": concept_map_with_items,
    "variable_map_with_items": variable_map_with_items,
    "question_map_with_correspondence": question_map_with_correspondence,
    "physical_instance_group_full": physical_instance_group_full,
    "physical_instance_group_minimal": physical_instance_group_minimal,
    "weighting_full": weighting_full,
    "weighting_methodology_full": weighting_methodology_full,
    "study_unit_with_conceptual_component": study_unit_with_conceptual_component,
    "study_unit_with_inline_modules": study_unit_with_inline_modules,
    "study_unit_minimal": study_unit_minimal,
    "variable_full": variable_full,
    "variable_enriched": variable_enriched,
    "variable_minimal": variable_minimal,
}


def main() -> None:
    for name, builder in sorted(BUILDERS.items()):
        write_pair(name, builder)


if __name__ == "__main__":
    main()
