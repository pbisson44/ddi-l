# mypy: ignore-errors
"""Round-trip tests for maintainable model helpers."""

from __future__ import annotations

import io
from collections.abc import Mapping
from pathlib import Path
from uuid import uuid5

import pytest

import ddi_l.models as models_module
from ddi_l import schema_loader
from ddi_l._etree import (
    Element,
    cleanup_namespaces,
    create_element,
    fromstring,
    parse_xml,
    tostring,
)
from ddi_l.constants import (
    COMPARATIVE_NS,
    DATA_COLLECTION_NS,
    DEFAULT_NSMAP,
    IDENTIFIER_NAMESPACE,
    INSTANCE_NS,
    LOGICAL_PRODUCT_NS,
    REUSABLE_NS,
    XML_NS,
)
from ddi_l.examples.tests.fixtures.models.regenerate import (
    FIXTURE_DEFAULT_AGENCY,
    _fixture_identifier,
)
from ddi_l.exceptions import DDIParseError
from ddi_l.io import iter_variables, read
from ddi_l.models import (
    Category,
    ClassificationFamily,
    ClassificationItem,
    ClassificationScheme,
    Comparison,
    ConceptMap,
    ConceptualVariable,
    DataCollection,
    Group,
    InformationClassification,
    LogicalProduct,
    MaintainableBase,
    ManagedMissingValuesRepresentation,
    PhysicalInstanceGroup,
    Process,
    ProcessingEvent,
    QualityScheme,
    QualityStandard,
    QualityStandardGroup,
    QualityStatement,
    QualityStatementGroup,
    QuestionMap,
    RepresentedVariable,
    SamplingPlan,
    StudyUnit,
    Variable,
    VariableMap,
    Weighting,
    WeightingMethodology,
    clone_element,
    qn,
)
from ddi_l.schema_loader import SchemaValidationError
from tests.helpers.maintainable_fixtures import (
    MODEL_FIXTURE_DIR,
    MODEL_FIXTURES,
    iter_maintainable_fixture_names,
)


def fixture_identifier(seed: str, *, agency: str = FIXTURE_DEFAULT_AGENCY) -> str:
    return _fixture_identifier(seed, agency=agency)


def fixture_urn(
    seed: str,
    *,
    version: str = "1",
    agency: str = FIXTURE_DEFAULT_AGENCY,
) -> str:
    return f"urn:ddi:{agency}:{fixture_identifier(seed, agency=agency)}:{version}"


def fixture_child_identifier(
    seed: str,
    *suffixes: str,
    agency: str = FIXTURE_DEFAULT_AGENCY,
) -> str:
    parts = [agency, fixture_identifier(seed, agency=agency), *suffixes]
    seed_value = ":".join(part for part in parts if part)
    return str(uuid5(IDENTIFIER_NAMESPACE, seed_value))


FIXTURE_DIR = MODEL_FIXTURE_DIR
PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = PROJECT_ROOT / "src" / "ddi_l" / "examples"

_NAMESPACE_OVERRIDES: Mapping[type[MaintainableBase], Mapping[str, str]] = {
    model: {prefix: uri for prefix, uri in (model.NSMAP or {}).items() if prefix}
    for model in MODEL_FIXTURES
}


_FRAGMENT_SCHEMA_GAP = "Not yet represented in the DDI 3.3 Fragment schema; validation requires schema support."


_VALIDATION_INCOMPATIBILITIES: Mapping[type[MaintainableBase], Mapping[str, str]] = {}


def _normalized_xml(element: Element, *, model: type[MaintainableBase]) -> str:
    """Normalize XML output for comparisons by pruning namespaces.

    Args:
        element: XML element produced from a maintainable instance.
        model: Maintainable model class providing namespace overrides.
    """
    working = fromstring(tostring(element, pretty_print=True))
    cleanup_namespaces(working, DEFAULT_NSMAP)
    working = fromstring(tostring(working, pretty_print=True))

    nsmap = dict(DEFAULT_NSMAP)
    nsmap.update(_NAMESPACE_OVERRIDES.get(model, {}))
    cleanup_namespaces(working, nsmap)

    return tostring(working, pretty_print=True).strip()


def _round_trip_cases():
    """Yield parametrization cases over every maintainable fixture."""
    for model, name in iter_maintainable_fixture_names():
        yield pytest.param(model, name, id=f"{model.__name__}-{name}")


def _validation_cases():
    """Yield parametrization cases for schema validation checks."""
    for model, fixtures in MODEL_FIXTURES.items():
        for name in fixtures:
            incompatibilities = _VALIDATION_INCOMPATIBILITIES.get(model, {})
            marks: list[pytest.MarkDecorator] = []
            if name in incompatibilities:
                marks.append(
                    pytest.mark.xfail(reason=incompatibilities[name], strict=True)
                )
            yield pytest.param(
                model,
                name,
                marks=marks,
                id=f"{model.__name__}-{name}",
            )


def _wrap_in_fragment(element: Element) -> Element:
    """Wrap a maintainable element in a fragment instance for validation.

    Args:
        element: Maintainable XML element to embed in a fragment instance.
    """
    fragment_instance = create_element(
        qn(INSTANCE_NS, "FragmentInstance"), nsmap={None: INSTANCE_NS, "r": REUSABLE_NS}
    )
    fragment = create_element(qn(INSTANCE_NS, "Fragment"))
    fragment.append(clone_element(element))
    fragment_instance.append(fragment)
    return fragment_instance


@pytest.mark.parametrize("model_cls", list(MODEL_FIXTURES))
def test_fixture_definitions_cover_all_maintainables(
    model_cls: type[MaintainableBase],
) -> None:
    """Ensure every maintainable model has at least one configured fixture.

    Args:
        model_cls: Maintainable model type expected to have fixture coverage.
    """

    assert MODEL_FIXTURES.get(model_cls), (
        f"No fixtures registered for {model_cls.__name__}"
    )


@pytest.mark.parametrize(("model_cls", "fixture_name"), list(_round_trip_cases()))
def test_maintainable_round_trip(
    model_cls: type[MaintainableBase], fixture_name: str
) -> None:
    """Maintainable models round-trip through XML without structural drift.

    Args:
        model_cls: Maintainable model class under test.
        fixture_name: Fixture XML name representing the maintainable payload.
    """
    source = parse_xml(MODEL_FIXTURE_DIR / f"{fixture_name}.xml")
    instance = model_cls.from_xml(source)

    round_tripped = instance.to_xml()
    expected = parse_xml(MODEL_FIXTURE_DIR / f"{fixture_name}.golden.xml")

    assert _normalized_xml(round_tripped, model=model_cls) == _normalized_xml(
        expected, model=model_cls
    )


@pytest.mark.parametrize(("model_cls", "fixture_name"), list(_validation_cases()))
def test_validated_models_pass_schema(
    model_cls: type[MaintainableBase], fixture_name: str
) -> None:
    """Maintainable fixtures validate successfully against the schema.

    Args:
        model_cls: Maintainable model class under test.
        fixture_name: Fixture XML name representing the maintainable payload.
    """
    source = parse_xml(MODEL_FIXTURE_DIR / f"{fixture_name}.xml")
    instance = model_cls.from_xml(source)
    fragment = _wrap_in_fragment(instance.to_xml())
    schema_loader.validate(fragment)


@pytest.mark.parametrize(
    ("model_cls", "fixture_name"),
    [
        pytest.param(
            DataCollection,
            "data_collection_questionnaire",
            id="DataCollection-questionnaire",
        ),
        pytest.param(
            Process,
            "process_with_inline_components",
            id="Process-inline",
        ),
        pytest.param(
            SamplingPlan,
            "sampling_plan_minimal",
            id="SamplingPlan-minimal",
        ),
    ],
)
def test_representative_maintainables_validate(
    model_cls: type[MaintainableBase], fixture_name: str
) -> None:
    """Ensure key maintainables validate (or document schema gaps)."""

    source = parse_xml(MODEL_FIXTURE_DIR / f"{fixture_name}.xml")
    instance = model_cls.from_xml(source)
    fragment = _wrap_in_fragment(instance.to_xml())
    schema_loader.validate(fragment)


def test_information_classification_structured_fields() -> None:
    """Full InformationClassification exposes structured child elements."""
    element = parse_xml(MODEL_FIXTURE_DIR / "information_classification_full.xml")
    instance = InformationClassification.from_xml(element)

    assert instance.type_of_information_classification is not None
    assert instance.type_of_information_classification.text == "DataHandling"
    assert instance.level_of_information_classification is not None
    assert instance.level_of_information_classification.text == "Restricted"
    assert instance.agency_organization_reference is not None
    assert instance.agency_organization_reference.identifier == fixture_identifier(
        "security-team"
    )
    assert len(instance.data_handling_personnel_rules) == 2
    content_tags = {
        child.tag.split("}")[-1]
        for rule in instance.data_handling_personnel_rules
        for child in rule
    }
    assert content_tags == {"Content"}
    assert [
        rule.find(qn(REUSABLE_NS, "Content")).text
        for rule in instance.data_encryption_rules
    ] == ["Apply AES-256 encryption at rest."]
    assert len(instance.authorized_policy_sources) == 1

    serialized = instance.to_xml()
    rules = serialized.findall(qn(REUSABLE_NS, "DataTransferRules"))
    assert len(rules) == 1
    policy = serialized.find(qn(REUSABLE_NS, "AuthorizedPolicySource"))
    assert policy is not None
    assert policy.find(qn(REUSABLE_NS, "OtherMaterialReference")) is not None


def test_information_classification_minimal_defaults() -> None:
    """Minimal InformationClassification omits optional structures."""
    element = parse_xml(MODEL_FIXTURE_DIR / "information_classification_minimal.xml")
    instance = InformationClassification.from_xml(element)

    assert instance.type_of_information_classification is None
    assert not instance.data_encryption_rules
    assert instance.agency_organization_reference is None

    serialized = instance.to_xml()
    assert serialized.findall(qn(REUSABLE_NS, "DataHandlingPersonnelRules")) == []


def test_comparison_multi_name_preserves_all_strings() -> None:
    """Comparison fixtures include multiple structured names across languages."""
    element = parse_xml(MODEL_FIXTURE_DIR / "comparison_multi_name.xml")
    instance = Comparison.from_xml(element)

    assert [name.lang for name in instance.names] == ["en", "fr", "es"]
    assert {name.text for name in instance.names} == {
        "Household vs Individual",
        "Ménages vs Individus",
        "Comparación secundaria",
    }

    serialized = instance.to_xml()
    containers = serialized.findall(qn(COMPARATIVE_NS, "ComparisonName"))
    assert len(containers) == 3
    assert all(container.findall(qn(REUSABLE_NS, "String")) for container in containers)


def test_comparison_map_helpers() -> None:
    """Comparison preserves inline maps and map references on round-trip."""

    element = parse_xml(MODEL_FIXTURE_DIR / "comparison_with_maps.xml")
    comparison = Comparison.from_xml(element)

    assert len(comparison.concept_maps) == 1
    assert len(comparison.concept_map_references) == 1
    assert len(comparison.variable_maps) == 1
    assert len(comparison.question_maps) == 1


def test_quality_standard_enriched_structures_round_trip() -> None:
    """QualityStandard preserves names and nested compliance definitions."""
    element = parse_xml(MODEL_FIXTURE_DIR / "quality_standard_enriched.xml")
    instance = QualityStandard.from_xml(element)

    assert [name.lang for name in instance.names] == ["en", "sv", "fr"]
    assert instance.standard_used is not None
    assert len(instance.compliance_definitions) == 2

    serialized = instance.to_xml()
    name_elements = serialized.findall(qn(REUSABLE_NS, "QualityStandardName"))
    assert len(name_elements) == 3
    assert serialized.find(qn(REUSABLE_NS, "Label")) is not None
    assert serialized.find(qn(REUSABLE_NS, "ComplianceDefinition")) is not None


def test_concept_map_item_correspondence() -> None:
    """Concept map fixture preserves item-level correspondences."""

    element = parse_xml(MODEL_FIXTURE_DIR / "concept_map_with_items.xml")
    concept_map = ConceptMap.from_xml(element)

    assert concept_map.type_of_mapped_item is not None
    assert concept_map.type_of_mapped_item.text == "Concept"
    assert len(concept_map.item_maps) == 2
    first_item = concept_map.item_maps[0]
    assert first_item.correspondence is not None
    assert first_item.correspondence.commonality_weight == 0.72


def test_variable_map_links_concept_map() -> None:
    """Variable map references the related concept map for context."""

    element = parse_xml(MODEL_FIXTURE_DIR / "variable_map_with_items.xml")
    variable_map = VariableMap.from_xml(element)

    assert variable_map.item_maps[0].related_map_references
    related = variable_map.item_maps[0].related_map_references[0]
    assert related.type_of_object == "ConceptMap"


def test_question_map_points_to_variable_map() -> None:
    """Question map items reference the variable map used for harmonisation."""

    element = parse_xml(MODEL_FIXTURE_DIR / "question_map_with_correspondence.xml")
    question_map = QuestionMap.from_xml(element)

    assert question_map.item_maps
    linkage = question_map.item_maps[0].related_map_references[0]
    assert linkage.type_of_object == "VariableMap"


def test_physical_instance_group_memberships() -> None:
    """Physical instance group captures nested membership and ordering."""

    element = parse_xml(MODEL_FIXTURE_DIR / "physical_instance_group_full.xml")
    instance = PhysicalInstanceGroup.from_xml(element)

    assert instance.isOrdered is True
    assert len(instance.physical_instance_references) == 2
    assert instance.physical_instance_group_references[
        0
    ].identifier == fixture_identifier("pig-minimal")


def test_group_helper_iterates_physical_instance_groups() -> None:
    """Group exposes inline physical instance groups via helper."""

    element = parse_xml(MODEL_FIXTURE_DIR / "physical_instance_group_minimal.xml")
    inline_group = PhysicalInstanceGroup.from_xml(element)
    group = Group(
        agency=FIXTURE_DEFAULT_AGENCY,
        identifier=fixture_identifier("group-with-pig"),
        version="1",
        physical_instance_groups=[inline_group],
    )

    assert len(group.physical_instance_groups) == 1


def test_weighting_usage_guide_round_trip() -> None:
    """Weighting fixture retains usage guidance and standard weights."""

    element = parse_xml(FIXTURE_DIR / "weighting_full.xml")
    weighting = Weighting.from_xml(element)

    assert weighting.analysis_unit is not None
    assert weighting.analysis_unit.text == "Household"
    assert weighting.usage_guide is not None
    assert weighting.usage_guide.examples[0].text.startswith(
        "Apply the household weight"
    )
    assert [weight.standard_weight_value for weight in weighting.standard_weights] == [
        1.0,
        0.85,
    ]

    serialized = weighting.to_xml()
    assert serialized.find(qn(DATA_COLLECTION_NS, "UsageGuide")) is not None


def test_weighting_methodology_round_trip() -> None:
    """Weighting methodology fixture captures classification details."""

    element = parse_xml(FIXTURE_DIR / "weighting_methodology_full.xml")
    methodology = WeightingMethodology.from_xml(element)

    assert methodology.type_of_weighting_methodology is not None
    assert methodology.type_of_weighting_methodology.text == "PostStratification"
    assert methodology.descriptions and methodology.descriptions[0].text.startswith(
        "Household-level calibration"
    )


def test_quality_statement_enriched_nested_content() -> None:
    """QualityStatement handles nested standards, references, and compliance entries."""
    element = parse_xml(FIXTURE_DIR / "quality_statement_enriched.xml")
    instance = QualityStatement.from_xml(element)

    assert len(instance.names) == 3
    assert instance.quality_standard is not None
    assert instance.quality_standard_reference is None
    assert instance.compliance_statement is not None
    assert len(instance.compliances) == 1

    serialized = instance.to_xml()
    assert len(serialized.findall(qn(REUSABLE_NS, "QualityStandard"))) == 1
    assert len(serialized.findall(qn(REUSABLE_NS, "QualityStandardReference"))) == 0
    assert len(serialized.findall(qn(REUSABLE_NS, "ComplianceStatement"))) == 1


def test_quality_statement_reference_round_trip() -> None:
    """QualityStatement minimal fixture retains quality standard references."""
    element = parse_xml(FIXTURE_DIR / "quality_statement_minimal.xml")
    instance = QualityStatement.from_xml(element)

    assert instance.quality_standard_reference is not None

    serialized = instance.to_xml()
    assert len(serialized.findall(qn(REUSABLE_NS, "QualityStandardReference"))) == 1


def test_quality_statement_group_enriched_flags() -> None:
    """QualityStatementGroup round-trips optional attributes and references."""
    element = parse_xml(FIXTURE_DIR / "quality_statement_group_enriched.xml")
    instance = QualityStatementGroup.from_xml(element)

    assert instance.isOrdered is False
    assert instance.type_of_quality_statement_group is not None
    assert instance.type_of_quality_statement_group.text == "Detailed"
    assert (
        instance.type_of_quality_statement_group.controlled_vocabulary_id
        == "QualityGroupType"
    )
    assert len(instance.universe_references) == 2
    assert len(instance.quality_statement_references) == 2
    assert len(instance.quality_statement_group_references) == 1

    serialized = instance.to_xml()
    assert serialized.get("isOrdered") == "false"
    type_element = serialized.find(qn(REUSABLE_NS, "TypeOfQualityStatementGroup"))
    assert type_element is not None
    assert type_element.get("controlledVocabularyID") == "QualityGroupType"
    assert len(serialized.findall(qn(REUSABLE_NS, "QualityStatementReference"))) == 2


def test_quality_standard_group_enriched_flags() -> None:
    """QualityStandardGroup retains ordering attributes and references."""
    element = parse_xml(FIXTURE_DIR / "quality_standard_group_enriched.xml")
    instance = QualityStandardGroup.from_xml(element)

    assert instance.isOrdered is True
    assert instance.type_of_quality_standard_group is not None
    assert instance.type_of_quality_standard_group.text == "Certification"
    assert (
        instance.type_of_quality_standard_group.controlled_vocabulary_id
        == "QualityGroupType"
    )
    assert len(instance.quality_standard_references) == 2
    assert len(instance.quality_standard_group_references) == 1

    serialized = instance.to_xml()
    assert serialized.get("isOrdered") == "true"
    type_element = serialized.find(qn(REUSABLE_NS, "TypeOfQualityStandardGroup"))
    assert type_element is not None
    assert type_element.get("controlledVocabularyID") == "QualityGroupType"
    assert len(serialized.findall(qn(REUSABLE_NS, "QualityStandardReference"))) == 2


def test_quality_scheme_nested_round_trip_structure() -> None:
    """QualityScheme with nested elements maintains group content and flags."""
    element = parse_xml(FIXTURE_DIR / "quality_scheme_nested.xml")
    instance = QualityScheme.from_xml(element)

    assert len(instance.names) == 3
    assert len(instance.quality_scheme_references) == 1
    assert len(instance.quality_statements) == 1
    assert len(instance.quality_statement_references) == 1
    assert len(instance.quality_standards) == 1
    assert len(instance.quality_standard_references) == 1
    assert len(instance.quality_statement_groups) == 1
    assert len(instance.quality_statement_group_references) == 1
    assert len(instance.quality_standard_groups) == 1
    assert len(instance.quality_standard_group_references) == 1
    assert instance.quality_statement_groups[0].get("isOrdered") == "false"
    assert instance.quality_standard_groups[0].get("isOrdered") == "true"

    serialized = instance.to_xml()
    assert len(serialized.findall(qn(REUSABLE_NS, "QualityStatement"))) == 1
    assert len(serialized.findall(qn(REUSABLE_NS, "QualityStatementGroup"))) == 1
    assert len(serialized.findall(qn(REUSABLE_NS, "QualityStandardGroup"))) == 1
    assert (
        serialized.find(qn(REUSABLE_NS, "QualityStatementGroup")).get("isOrdered")
        == "false"
    )
    assert (
        serialized.find(qn(REUSABLE_NS, "QualityStandardGroup")).get("isOrdered")
        == "true"
    )


def test_managed_missing_values_representation_round_trip() -> None:
    """ManagedMissingValuesRepresentation keeps metadata and extras intact."""
    element = parse_xml(FIXTURE_DIR / "managed_missing_values_representation_full.xml")
    instance = ManagedMissingValuesRepresentation.from_xml(element)

    assert instance.blank_is_missing_value is False
    assert instance.other_attributes == {}
    assert [name.text for name in instance.names] == [
        "Standard missing set",
        "Legacy format",
    ]
    assert (
        instance.missing_code_representations[0].other_attributes["missingValue"]
        == "-7"
    )
    numeric_range = instance.missing_numeric_representations[0].number_range
    assert numeric_range is not None
    assert numeric_range.low == "-9"
    assert instance.processing_instruction_reference is not None
    assert instance.processing_instruction_reference.identifier == fixture_identifier(
        "derive-missing"
    )
    assert len(instance.processing_instruction_reference_extras) == 1
    assert instance.processing_instruction_reference_extras[0].tag == qn(
        REUSABLE_NS, "Binding"
    )

    serialized = instance.to_xml()
    code_nodes = serialized.findall(qn(REUSABLE_NS, "MissingCodeRepresentation"))
    assert len(code_nodes) == 1
    pir_el = serialized.find(qn(REUSABLE_NS, "ProcessingInstructionReference"))
    assert pir_el is not None
    assert pir_el.find(qn(REUSABLE_NS, "Binding")) is not None
    assert serialized.get("isBlankMissingValue") == "false"
    assert serialized.get("scopeOfUniqueness") is None


def test_managed_missing_values_representation_minimal_defaults() -> None:
    """Minimal managed missing values representation leaves fields empty."""
    element = parse_xml(
        FIXTURE_DIR / "managed_missing_values_representation_minimal.xml"
    )
    instance = ManagedMissingValuesRepresentation.from_xml(element)

    assert instance.blank_is_missing_value is None
    assert not instance.names
    assert not instance.missing_code_representations

    serialized = instance.to_xml()
    assert serialized.get("isBlankMissingValue") is None


def test_classification_scheme_deep_hierarchy() -> None:
    """ClassificationScheme retains nested items, version metadata, and references."""

    element = parse_xml(FIXTURE_DIR / "classification_scheme_deep.xml")
    scheme = ClassificationScheme.from_xml(element)

    assert scheme.versionDate == "2024-03-15"
    assert scheme.isPublished is True
    assert scheme.is_current is True
    assert scheme.is_version is True
    assert scheme.updates_allowed is True
    assert scheme.level_contexts
    context = scheme.level_contexts[0]
    level_num = context.find(qn(LOGICAL_PRODUCT_NS, "LevelNumber"))
    assert level_num is not None and level_num.text == "1"
    items = context.findall(qn(LOGICAL_PRODUCT_NS, "ClassificationItem"))
    assert items
    item_code = items[0].find(qn(LOGICAL_PRODUCT_NS, "ItemCode"))
    assert item_code is not None and item_code.text == "A"
    item_refs = context.findall(qn(LOGICAL_PRODUCT_NS, "ClassificationItemReference"))
    assert item_refs
    item_ref_id = item_refs[0].find(qn(REUSABLE_NS, "ID"))
    assert item_ref_id is not None
    assert item_ref_id.text == fixture_identifier("class-item-B")

    serialized = scheme.to_xml()
    assert serialized.get("versionDate") == "2024-03-15"
    assert serialized.get("isPublished") == "true"
    concept_ref = serialized.find(f".//{qn(REUSABLE_NS, 'DefiningConceptReference')}")
    assert concept_ref is not None
    assert len(serialized.findall(qn(REUSABLE_NS, "CodeListReference"))) == 1


def test_classification_item_nested_metadata() -> None:
    """ClassificationItem handles hierarchical children and structured notes."""

    element = parse_xml(FIXTURE_DIR / "classification_item_nested.xml")
    item = ClassificationItem.from_xml(element)

    assert item.is_generated is True
    assert item.is_valid is True
    assert item.valid_from is not None
    assert item.valid_from.text == "2024-02-01"
    assert item.includes is not None
    includes_content = item.includes.find(qn(REUSABLE_NS, "Content"))
    assert includes_content is not None and includes_content.text.endswith(
        "operations."
    )
    assert item.future_events is not None
    future_content = item.future_events.find(qn(REUSABLE_NS, "Content"))
    assert future_content is not None and "updated" in future_content.text
    assert item.changes_from_prior_version is not None
    changes_content = item.changes_from_prior_version.find(qn(REUSABLE_NS, "Content"))
    assert changes_content is not None and "Renamed" in changes_content.text
    assert item.excluded_classification_item_references
    assert item.excluded_classification_item_references[
        0
    ].identifier == fixture_identifier("class-item-X")
    assert item.successor_classification_item_references
    assert item.successor_classification_item_references[
        0
    ].identifier == fixture_identifier("class-item-A-new")
    assert item.parent_classification_item_reference is not None
    assert item.parent_classification_item_reference.identifier == fixture_identifier(
        "class-item-parent"
    )

    serialized = item.to_xml()
    assert serialized.get("versionDate") == "2024-02-01"
    assert serialized.get("isPublished") == "true"
    concept_ref = serialized.find(f".//{qn(REUSABLE_NS, 'DefiningConceptReference')}")
    assert concept_ref is not None
    urn = concept_ref.find(qn(REUSABLE_NS, "URN"))
    assert urn is not None and urn.text == fixture_urn("concept-manufacturing")


def test_classification_family_nested_series() -> None:
    """ClassificationFamily retains inline series and references."""

    element = parse_xml(FIXTURE_DIR / "classification_family_nested.xml")
    family = ClassificationFamily.from_xml(element)

    assert family.names and family.names[0].text == "Economic Classification Family"
    assert len(family.classification_series) == 1
    series_el = family.classification_series[0]
    series_ctx = series_el.find(qn(LOGICAL_PRODUCT_NS, "SeriesContext"))
    assert series_ctx is not None and series_ctx.text == "International"
    stat_cls = series_el.findall(qn(LOGICAL_PRODUCT_NS, "StatisticalClassification"))
    assert stat_cls
    level_ctx = stat_cls[0].findall(qn(LOGICAL_PRODUCT_NS, "LevelContext"))
    assert level_ctx
    assert family.classification_series_references and (
        family.classification_series_references[0].type_of_object
        == "ClassificationSeries"
    )

    serialized = family.to_xml()
    assert len(serialized.findall(qn(LOGICAL_PRODUCT_NS, "ClassificationSeries"))) == 1
    assert (
        len(serialized.findall(qn(REUSABLE_NS, "ClassificationSeriesReference"))) == 1
    )


def test_category_representative_from_quality_of_life() -> None:
    """Category representative fixture round-trips multilingual content."""
    element = parse_xml(FIXTURE_DIR / "category_representative.xml")
    instance = Category.from_xml(element)

    assert instance.identifier == "07339047-b749-43a9-b3d4-6e0889365b1d"
    assert instance.isMissing is False
    assert [name.text for name in instance.names] == ["2", "2"]
    assert {name.lang for name in instance.names} == {"en-CA", "fr-CA"}
    assert {label.lang for label in instance.labels} == {"en-CA", "fr-CA"}

    serialized = instance.to_xml()
    assert serialized.get("isMissing") == "false"
    name_nodes = serialized.findall(qn(LOGICAL_PRODUCT_NS, "CategoryName"))
    assert len(name_nodes) == 2
    languages = {
        child.get(qn(XML_NS, "lang"))
        for node in name_nodes
        for child in node.findall(qn(REUSABLE_NS, "String"))
    }
    assert languages == {"en-CA", "fr-CA"}


def test_represented_variable_numeric_range_and_references() -> None:
    """RepresentedVariable retains range metadata and references."""
    element = parse_xml(FIXTURE_DIR / "represented_variable_with_code.xml")
    instance = RepresentedVariable.from_xml(element)

    assert instance.identifier == "79afe111-37e9-41a2-9538-dc27fbbe2448"
    assert instance.conceptual_variable_reference is not None
    assert (
        instance.conceptual_variable_reference.identifier
        == "c804a92a-30f3-4b52-92df-0352966f6b44"
    )
    assert instance.numeric_representation is not None
    numeric = instance.numeric_representation
    assert numeric.blank_is_missing_value is False
    assert numeric.number_range is not None
    assert numeric.number_range.low == "0"
    assert numeric.number_range.high == "999"
    assert numeric.number_range.low_is_inclusive is False
    assert numeric.number_range.high_is_inclusive is False

    serialized = instance.to_xml()
    numeric_el = serialized.find(f".//{qn(REUSABLE_NS, 'NumericRepresentation')}")
    assert numeric_el is not None
    assert numeric_el.get("blankIsMissingValue") == "false"
    range_el = numeric_el.find(qn(REUSABLE_NS, "NumberRange"))
    assert range_el is not None
    low_el = range_el.find(qn(REUSABLE_NS, "Low"))
    high_el = range_el.find(qn(REUSABLE_NS, "High"))
    assert low_el is not None and low_el.get("isInclusive") == "false"
    assert high_el is not None and high_el.get("isInclusive") == "false"


def test_variable_enriched_includes_numeric_ranges_and_sources() -> None:
    """Enriched Variable preserves numeric range and source references."""
    element = parse_xml(FIXTURE_DIR / "variable_enriched.xml")
    instance = Variable.from_xml(element)

    assert instance.identifier == "1c4258d0-c9b7-4b5a-a3bb-1f88ed8fa9f8"
    assert len(instance.source_variable_references) == 4
    assert instance.represented_variable_reference is not None
    assert instance.variable_representation is not None
    representation = instance.variable_representation
    assert representation.numeric_representation is not None
    numeric = representation.numeric_representation
    assert numeric.blank_is_missing_value is False
    assert numeric.number_range is not None
    assert numeric.number_range.low == "15"
    assert numeric.number_range.high == "103"
    assert numeric.number_range.low_is_inclusive is False
    assert numeric.number_range.high_is_inclusive is False

    serialized = instance.to_xml()
    numeric_el = serialized.find(f".//{qn(REUSABLE_NS, 'NumericRepresentation')}")
    assert numeric_el is not None
    assert numeric_el.get("blankIsMissingValue") == "false"
    range_el = numeric_el.find(qn(REUSABLE_NS, "NumberRange"))
    assert range_el is not None
    low_el = range_el.find(qn(REUSABLE_NS, "Low"))
    high_el = range_el.find(qn(REUSABLE_NS, "High"))
    assert low_el is not None and low_el.text == "15"
    assert low_el.get("isInclusive") == "false"
    assert high_el is not None and high_el.text == "103"
    assert high_el.get("isInclusive") == "false"


def test_variable_round_trip_preserves_user_ids_from_fragment() -> None:
    """Variables retain r:UserID entries when parsed from sample fragment."""

    fragment_path = EXAMPLES_DIR / "Quality_of_Life.xml"
    document = read(fragment_path)

    target_payload: Element | None = None
    for payload in document.iter_fragment_payloads():
        if payload.tag != Variable.TAG:
            continue
        urn = payload.findtext(qn(REUSABLE_NS, "URN"))
        if urn == "urn:ddi:ca.statcan:a4798210-59f8-410d-912f-1afd2f0bb2f9:13":
            target_payload = payload
            break

    assert target_payload is not None, "expected variable with multiple UserID entries"

    instance = Variable.from_xml(target_payload)
    assert [uid.type_of_user_id for uid in instance.user_ids] == ["x", "x"]

    serialized = instance.to_xml()
    user_id_nodes = serialized.findall(qn(REUSABLE_NS, "UserID"))
    assert len(user_id_nodes) == 2
    assert [node.get("typeOfUserID") for node in user_id_nodes] == ["x", "x"]
    assert [node.text for node in user_id_nodes] == [None, None]

    version_responsibility_index = next(
        i
        for i, child in enumerate(serialized)
        if child.tag == qn(REUSABLE_NS, "VersionResponsibility")
    )
    first_user_id_index = next(
        i
        for i, child in enumerate(serialized)
        if child.tag == qn(REUSABLE_NS, "UserID")
    )
    assert first_user_id_index < version_responsibility_index


def test_iter_variables_streams_enriched_variable_fixture() -> None:
    """iter_variables yields enriched variable fixtures from stream payloads."""
    element = parse_xml(FIXTURE_DIR / "variable_enriched.xml")
    fragment = _wrap_in_fragment(element)
    payload = tostring(fragment, pretty_print=False)
    streamed = list(iter_variables(io.BytesIO(payload.encode("utf-8"))))
    assert len(streamed) == 1
    variable = streamed[0]
    assert variable.identifier == "1c4258d0-c9b7-4b5a-a3bb-1f88ed8fa9f8"
    assert variable.variable_representation is not None
    numeric = variable.variable_representation.numeric_representation
    assert numeric is not None
    assert numeric.number_range is not None
    assert numeric.number_range.high == "103"


def test_logical_product_helper_filters() -> None:
    """LogicalProduct helpers surface scheme and identifier filters."""

    element = parse_xml(FIXTURE_DIR / "logical_product_full.xml")
    product = LogicalProduct.from_xml(element)

    variables = list(product.iter_variables())
    expected_variable_id = fixture_identifier("var-1")
    assert [variable.identifier for variable in variables] == [expected_variable_id]
    assert list(product.iter_variables(identifier=expected_variable_id)) == variables
    assert not list(product.iter_variables(identifier="missing"))
    variable_scheme_id = fixture_child_identifier("logical-1", "variable-scheme")
    assert (
        list(product.iter_variables(scheme_identifier=variable_scheme_id)) == variables
    )
    assert not list(
        product.iter_variables(
            scheme_identifier=fixture_child_identifier(
                "logical-1", "variable-scheme", "2"
            )
        )
    )

    code_lists = list(product.iter_code_lists())
    expected_code_list_id = fixture_identifier("codes-1")
    assert [code_list.identifier for code_list in code_lists] == [expected_code_list_id]
    assert list(product.iter_code_lists(identifier=expected_code_list_id)) == code_lists
    assert not list(product.iter_code_lists(identifier="missing"))
    code_list_scheme_id = fixture_child_identifier("logical-1", "code-list-scheme")
    assert (
        list(product.iter_code_lists(scheme_identifier=code_list_scheme_id))
        == code_lists
    )
    assert not list(
        product.iter_code_lists(
            scheme_identifier=fixture_child_identifier(
                "logical-1", "code-list-scheme", "2"
            )
        )
    )

    assert list(product.iter_derived_datasets()) == []


def test_study_unit_convenience_helpers() -> None:
    """StudyUnit exposes shortcuts for inline module lookups."""

    element = parse_xml(FIXTURE_DIR / "study_unit_with_inline_modules.xml")
    study = StudyUnit.from_xml(element)

    variables = list(study.iter_variables())
    expected_variable_id = fixture_identifier("var-1")
    assert [variable.identifier for variable in variables] == [expected_variable_id]
    assert list(study.iter_variables(identifier=expected_variable_id)) == variables
    assert not list(study.iter_variables(identifier="missing"))

    data_collections = list(study.iter_data_collections())
    expected_collection_id = fixture_identifier("collect-1")
    assert [collection.identifier for collection in data_collections] == [
        expected_collection_id
    ]
    assert (
        list(study.iter_data_collections(identifier=expected_collection_id))
        == data_collections
    )
    assert not list(study.iter_data_collections(identifier="missing"))

    dataset_identifier = fixture_identifier("physical-1")
    dataset = study.get_dataset(dataset_identifier)
    assert dataset is not None and dataset.identifier == dataset_identifier
    assert study.get_dataset("missing") is None


def _corrupt_identification(element: Element) -> Element:
    """Remove identification and corrupt tag name to simulate invalid XML.

    Args:
        element: Maintainable XML element to mutate before parsing.
    """
    identifier = element.find(qn(REUSABLE_NS, "ID"))
    if identifier is not None:
        element.remove(identifier)
    if element.tag.startswith("{"):
        namespace, local = element.tag[1:].split("}", 1)
        element.tag = f"{{{namespace}}}{local}Broken"
    else:
        element.tag = f"{element.tag}Broken"
    return element


@pytest.mark.parametrize(("model_cls", "fixture_name"), list(_round_trip_cases()))
def test_from_xml_rejects_invalid_documents(
    model_cls: type[MaintainableBase], fixture_name: str
) -> None:
    """from_xml raises when maintainable XML is missing identification.

    Args:
        model_cls: Maintainable model class expected to reject corrupted XML.
        fixture_name: Fixture XML name used as the corruption baseline.
    """
    broken = _corrupt_identification(parse_xml(FIXTURE_DIR / f"{fixture_name}.xml"))
    with pytest.raises((ValueError, SchemaValidationError, DDIParseError)):
        model_cls.from_xml(broken)


_EXPECTED_EXPORTS = {
    "Category": Category,
    "ConceptualVariable": ConceptualVariable,
    "InformationClassification": InformationClassification,
    "ProcessingEvent": ProcessingEvent,
    "RepresentedVariable": RepresentedVariable,
}


def test_models_module_re_exports_new_maintainables() -> None:
    """Ensure :mod:`ddi_l.models` exposes newly added maintainables."""

    for name, cls in _EXPECTED_EXPORTS.items():
        exported = getattr(models_module, name, None)
        assert exported is cls
        assert name in models_module.__all__
