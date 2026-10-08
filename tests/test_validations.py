"""Unit tests covering maintainable validation hooks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import pytest

from ddi_l.constants import DATA_COLLECTION_NS, LOGICAL_PRODUCT_NS, REUSABLE_NS
from ddi_l.exceptions import ModelValidationError
from ddi_l.models import (
    CollectionEvent,
    DataCollection,
    InternationalString,
    LogicalProduct,
    MaintainableBase,
    QuestionItem,
    Reference,
    StudyUnit,
    ValidationContext,
    Variable,
    qn,
)


@dataclass
class _DummyMaintainable(MaintainableBase):
    TAG: ClassVar[str] = qn(REUSABLE_NS, "DummyMaintainable")


def test_missing_identification_fields_raise() -> None:
    """Maintainables require identification metadata when URN is absent."""

    instance = _DummyMaintainable()

    with pytest.raises(
        ModelValidationError,
        match="requires agency, identifier, version when URN is not provided",
    ):
        instance.to_xml()


def test_urn_allows_missing_identification() -> None:
    """Providing a URN bypasses the additional identification requirements."""

    instance = _DummyMaintainable(urn="urn:ddi:demo:dummy:1.0")

    serialized = instance.to_xml()
    assert serialized.tag == qn(REUSABLE_NS, "DummyMaintainable")


def test_invalid_urn_is_rejected() -> None:
    """Maintainables reject URNs that do not match the canonical pattern."""

    instance = _DummyMaintainable(urn="not-a-urn")

    with pytest.raises(ModelValidationError, match="(?i)invalid urn"):
        instance.to_xml()


def test_identifier_pattern_enforced() -> None:
    """Identifiers must comply with the DDI IDType regular expression."""

    instance = _DummyMaintainable(
        agency="demo.agency", identifier="invalid id", version="1.0"
    )

    with pytest.raises(ModelValidationError, match="invalid identifier"):
        instance.to_xml()


def test_identifier_pattern_allows_valid_characters() -> None:
    """Valid identifier characters pass maintainable validation."""

    instance = _DummyMaintainable(
        agency="demo.agency", identifier="valid-ID_1.2", version="1.0"
    )

    serialized = instance.to_xml()
    identifier_el = serialized.find(qn(REUSABLE_NS, "ID"))
    assert identifier_el is not None
    assert identifier_el.text == "valid-ID_1.2"


def test_urn_pattern_allows_uppercase_prefix() -> None:
    """URN validation tolerates uppercase URN/DDI prefixes per the schema."""

    instance = _DummyMaintainable(
        urn="URN:DDI:demo.agency:valid-id:1.0",
        agency="demo.agency",
        identifier="valid-id",
        version="1.0",
    )

    serialized = instance.to_xml()
    urn_el = serialized.find(qn(REUSABLE_NS, "URN"))
    assert urn_el is not None
    assert urn_el.text == "URN:DDI:demo.agency:valid-id:1.0"


def test_study_unit_requires_collections_or_references() -> None:
    """StudyUnit validates that data collections are described."""

    study = StudyUnit(agency="demo.agency", identifier="study", version="1.0")

    with pytest.raises(
        ModelValidationError,
        match="StudyUnit requires at least one DataCollection or DataCollectionReference",
    ):
        study.to_xml()


def test_study_unit_duplicate_children_raise() -> None:
    """StudyUnit rejects duplicate inline maintainables."""

    collection_event_one = CollectionEvent(
        agency="demo.agency", identifier="collect-event-1", version="1.0"
    )
    collection_event_two = CollectionEvent(
        agency="demo.agency", identifier="collect-event-2", version="1.0"
    )
    base_collection_kwargs = dict(agency="demo.agency", version="1.0")
    data_collection_one = DataCollection(
        identifier="collect",
        collection_events=[collection_event_one],
        **base_collection_kwargs,  # type: ignore[arg-type]
    )
    data_collection_two = DataCollection(
        identifier="collect",
        collection_events=[collection_event_two],
        **base_collection_kwargs,  # type: ignore[arg-type]
    )
    study = StudyUnit(
        agency="demo.agency",
        identifier="study",
        version="1.0",
        data_collections=[data_collection_one, data_collection_two],
    )

    with pytest.raises(ModelValidationError, match="duplicate DataCollection"):
        study.to_xml()


def test_study_unit_with_reference_serializes() -> None:
    """StudyUnit passes validation when a data-collection reference is present."""

    study = StudyUnit(
        agency="demo.agency",
        identifier="study",
        version="1.0",
        data_collection_references=[
            Reference(
                agency="demo.agency",
                identifier="collect",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )

    serialized = study.to_xml()
    assert serialized.find(qn(REUSABLE_NS, "DataCollectionReference")) is not None


def test_data_collection_requires_content() -> None:
    """DataCollection enforces having inline content or references."""

    data_collection = DataCollection(
        agency="demo.agency", identifier="collect", version="1.0"
    )

    with pytest.raises(
        ModelValidationError,
        match="DataCollection requires collection events, instruments, questions, or references",
    ):
        data_collection.to_xml()


def test_data_collection_duplicate_questions_raise() -> None:
    """DataCollection enforces unique identifiers for question fragments."""

    question_one = QuestionItem(
        agency="demo.agency",
        identifier="q1",
        version="1.0",
        question_texts=[InternationalString(text="What is your age?")],
    )
    question_two = QuestionItem(
        agency="demo.agency",
        identifier="q1",
        version="1.0",
        question_texts=[InternationalString(text="What is your income?")],
    )
    data_collection = DataCollection(
        agency="demo.agency",
        identifier="collect",
        version="1.0",
        questions=[question_one, question_two],
    )

    with pytest.raises(ModelValidationError, match="duplicate QuestionItem"):
        data_collection.to_xml()


def test_data_collection_with_event_serializes() -> None:
    """A collection event is sufficient to satisfy DataCollection validation."""

    event = CollectionEvent(agency="demo.agency", identifier="event", version="1.0")
    data_collection = DataCollection(
        agency="demo.agency",
        identifier="collect",
        version="1.0",
        collection_events=[event],
    )

    serialized = data_collection.to_xml()
    assert serialized.find(qn(DATA_COLLECTION_NS, "CollectionEvent")) is not None


def test_logical_product_requires_variables_or_references() -> None:
    """LogicalProduct rejects serialization when empty."""

    logical_product = LogicalProduct(
        agency="demo.agency", identifier="logical", version="1.0"
    )

    with pytest.raises(
        ModelValidationError,
        match="LogicalProduct requires.*variables.*code lists.*or scheme references",
    ):
        logical_product.to_xml()


def test_logical_product_with_variable_serializes() -> None:
    """Inline variables allow LogicalProduct to pass validation."""

    variable = Variable(agency="demo.agency", identifier="var", version="1.0")
    logical_product = LogicalProduct(
        agency="demo.agency",
        identifier="logical",
        version="1.0",
        variables=[variable],
    )

    serialized = logical_product.to_xml()
    assert serialized.find(qn(LOGICAL_PRODUCT_NS, "VariableScheme")) is not None


# ============================================================================
# Cross-reference validation
# ============================================================================


def test_validation_context_registers_and_resolves():
    """ValidationContext registers maintainables and resolves references."""

    concept = _DummyMaintainable(
        agency="demo.agency", identifier="concept-1", version="1.0"
    )
    ctx = ValidationContext()
    ctx.register(concept)

    ref = Reference(
        agency="demo.agency",
        identifier="concept-1",
        version="1.0",
        type_of_object="DummyMaintainable",
    )
    assert ctx.can_resolve(ref) is True
    assert ctx.resolve(ref) is concept


def test_validation_context_rejects_unknown_reference():
    """ValidationContext reports unresolvable references."""

    ctx = ValidationContext()
    ref = Reference(
        agency="demo.agency",
        identifier="nonexistent",
        version="1.0",
        type_of_object="DummyMaintainable",
    )
    assert ctx.can_resolve(ref) is False
    assert ctx.resolve(ref) is None


def test_validate_tree_detects_dangling_references():
    """validate_tree finds unresolvable references in the object tree."""

    variable = Variable(
        agency="demo.agency",
        identifier="var-1",
        version="1.0",
        question_references=[
            Reference(
                agency="demo.agency",
                identifier="missing-question",
                version="1.0",
                type_of_object="QuestionItem",
            )
        ],
    )
    logical = LogicalProduct(
        agency="demo.agency",
        identifier="lp",
        version="1.0",
        variables=[variable],
    )

    warnings = logical.validate_tree()
    assert len(warnings) >= 1
    assert any("missing-question" in w.message for w in warnings)


def test_validate_tree_no_warnings_when_references_exist():
    """validate_tree returns no warnings when all references resolve."""

    question = QuestionItem(
        agency="demo.agency",
        identifier="q1",
        version="1.0",
        question_texts=[InternationalString(text="What?")],
    )
    variable = Variable(
        agency="demo.agency",
        identifier="var-1",
        version="1.0",
        question_references=[
            Reference(
                agency="demo.agency",
                identifier="q1",
                version="1.0",
                type_of_object="QuestionItem",
            )
        ],
    )

    # Build a context that knows about both objects
    ctx = ValidationContext()
    ctx.register(question)
    ctx.register(variable)

    warnings = variable.validate_references(ctx)
    assert warnings == []


def test_study_to_xml_emits_reference_warnings():
    """StudyUnit.to_xml() emits UserWarning for dangling references."""

    import warnings as _warnings

    study = StudyUnit(
        agency="demo.agency",
        identifier="study",
        version="1.0",
        data_collection_references=[
            Reference(
                agency="demo.agency",
                identifier="missing-dc",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )

    with _warnings.catch_warnings(record=True) as caught:
        _warnings.simplefilter("always")
        study.to_xml()

    ref_msgs = [w for w in caught if "missing-dc" in str(w.message)]
    assert len(ref_msgs) >= 1


def test_study_to_xml_skip_ref_validation():
    """StudyUnit.to_xml(validate_refs=False) skips reference checking."""

    import warnings as _warnings

    study = StudyUnit(
        agency="demo.agency",
        identifier="study",
        version="1.0",
        data_collection_references=[
            Reference(
                agency="demo.agency",
                identifier="missing-dc",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )

    with _warnings.catch_warnings(record=True) as caught:
        _warnings.simplefilter("always")
        study.to_xml(validate_refs=False)

    ref_msgs = [w for w in caught if "missing-dc" in str(w.message)]
    assert len(ref_msgs) == 0


def test_from_maintainable_walks_tree():
    """ValidationContext.from_maintainable registers all descendants."""

    event = CollectionEvent(agency="demo.agency", identifier="event-1", version="1.0")
    dc = DataCollection(
        agency="demo.agency",
        identifier="dc-1",
        version="1.0",
        collection_events=[event],
    )
    study = StudyUnit(
        agency="demo.agency",
        identifier="study",
        version="1.0",
        data_collections=[dc],
    )

    ctx = ValidationContext.from_maintainable(study)

    # All three should be registered
    for ident in ("study", "dc-1", "event-1"):
        ref = Reference(identifier=ident, type_of_object="test")
        assert ctx.can_resolve(ref), f"Expected {ident!r} to be resolvable"
