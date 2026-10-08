# mypy: ignore-errors
from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.document import DDIDocument
from ddi_l.index import Index
from ddi_l.models import (
    CodeList,
    Concept,
    ConceptualComponent,
    ConceptualVariable,
    DataCollection,
    Group,
    InternationalString,
    LogicalProduct,
    QualityScheme,
    QuestionItem,
    Reference,
    StudyUnit,
    UnitType,
    Variable,
    qn,
)
from ddi_l.models.base import MaintainableBase
from tests.helpers.synthetic_maintainable import synthetic_maintainable


def _attach_urn(resource, urn: str) -> None:
    """Append a URN element to the resource's other_elements collection.

    Args:
        resource: Maintainable instance receiving a URN child.
        urn: Identifier string to append as URN content.
    """
    element = create_element(qn(REUSABLE_NS, "URN"))
    element.text = urn
    resource.other_elements.append(element)


def _build_document() -> DDIDocument:
    """Construct a StudyUnit document with linked maintainables for indexing."""
    concept = Concept(
        agency="agency.test",
        identifier="concept-age",
        version="1.0",
        names=[InternationalString(text="Age", child_tag="String")],
        descriptions=[
            InternationalString(
                text="Underlying concept for measuring the respondent age.",
                child_tag="Content",
            )
        ],
    )
    _attach_urn(concept, "urn:ddi:concept:concept-age")

    unit_type = UnitType(
        agency="agency.test",
        identifier="unit-type",
        version="1.0",
        labels=[InternationalString(text="Person", child_tag="Content")],
        descriptions=[
            InternationalString(
                text="Individuals participating in the study.",
                child_tag="Content",
            )
        ],
        concept_reference=Reference(
            type_of_object="Concept",
            agency="agency.test",
            identifier="concept-age",
            version="1.0",
            urn="urn:ddi:concept:concept-age",
        ),
    )
    _attach_urn(unit_type, "urn:ddi:unit-type:unit-type")

    conceptual_variable = ConceptualVariable(
        agency="agency.test",
        identifier="conceptual-variable",
        version="1.0",
        names=[InternationalString(text="Age of person", child_tag="String")],
        labels=[InternationalString(text="Age", child_tag="Content")],
        descriptions=[
            InternationalString(
                text="Respondent age recorded in completed years.",
                child_tag="Content",
            )
        ],
        concept_reference=Reference(
            type_of_object="Concept",
            agency="agency.test",
            identifier="concept-age",
            version="1.0",
            urn="urn:ddi:concept:concept-age",
        ),
        unit_type_reference=Reference(
            type_of_object="UnitType",
            agency="agency.test",
            identifier="unit-type",
            version="1.0",
            urn="urn:ddi:unit-type:unit-type",
        ),
    )
    _attach_urn(conceptual_variable, "urn:ddi:conceptual-variable:1")

    conceptual_component = ConceptualComponent(
        agency="agency.test",
        identifier="concept-component",
        version="1.0",
        concepts=[concept],
        conceptual_variables=[conceptual_variable],
        unit_types=[unit_type],
        has_conceptual_variable_scheme=True,
        has_unit_type_scheme=True,
    )
    _attach_urn(conceptual_component, "urn:ddi:conceptual-component:1")

    question = QuestionItem(
        agency="agency.test",
        identifier="q1",
        version="1.0",
        question_texts=[InternationalString(text="How old are you?")],
    )
    _attach_urn(question, "urn:ddi:question:q1")

    code_list_reference = Reference(
        type_of_object="CodeList",
        agency="external.agency",
        identifier="CL1",
        version="1.0",
        urn="urn:ddi:codelist:CL1",
    )
    question.other_elements.append(code_list_reference.to_xml("CodeListReference"))

    data_collection = DataCollection(
        agency="agency.test",
        identifier="dc1",
        version="1.0",
        questions=[question],
    )
    _attach_urn(data_collection, "urn:ddi:data-collection:dc1")

    variable = Variable(
        agency="agency.test",
        identifier="var-age",
        version="1.0",
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency="agency.test",
                identifier="q1",
                version="1.0",
            )
        ],
        concept_references=[
            Reference(
                type_of_object="Concept",
                agency="agency.test",
                identifier="concept-age",
                version="1.0",
            )
        ],
    )
    _attach_urn(variable, "urn:ddi:variable:var-age")

    logical_product = LogicalProduct(
        agency="agency.test",
        identifier="lp1",
        version="1.0",
        variables=[variable],
    )
    _attach_urn(logical_product, "urn:ddi:logical-product:lp1")

    study_unit = StudyUnit(
        agency="agency.test",
        identifier="study1",
        version="1.0",
        data_collections=[data_collection],
        logical_products=[logical_product],
        conceptual_components=[conceptual_component],
    )
    _attach_urn(study_unit, "urn:ddi:study-unit:study1")

    document = DDIDocument.create(
        agency="agency.test",
        identifier="doc",
        version="1.0",
    )
    document.add_study_unit(study_unit)
    return document


def test_index_resolves_references_and_backlinks() -> None:
    """Index resolves references via identifiers and URNs for maintainables."""
    document = _build_document()
    index = document.build_index()

    question_ref = Reference(
        type_of_object="QuestionItem",
        agency="agency.test",
        identifier="q1",
        version="1.0",
    )
    question = index.resolve(question_ref)
    assert isinstance(question, QuestionItem)
    assert question.identifier == "q1"

    urn_ref = Reference(urn="urn:ddi:question:q1")
    assert index.resolve(urn_ref).identifier == "q1"

    variable = index.get_variable("var-age", agency="agency.test", version="1.0")
    assert variable.identifier == "var-age"

    conceptual_variable_ref = Reference(
        type_of_object="ConceptualVariable",
        agency="agency.test",
        identifier="conceptual-variable",
        version="1.0",
    )
    conceptual_variable = index.resolve(conceptual_variable_ref)
    assert isinstance(conceptual_variable, ConceptualVariable)
    assert conceptual_variable.identifier == "conceptual-variable"

    unit_type_ref = Reference(
        type_of_object="UnitType",
        agency="agency.test",
        identifier="unit-type",
        version="1.0",
    )
    unit_type = index.resolve(unit_type_ref)
    assert isinstance(unit_type, UnitType)
    assert unit_type.identifier == "unit-type"


def test_index_registers_conceptual_resources() -> None:
    """Index registers conceptual resources and resolves them by URN."""
    document = _build_document()
    index = document.build_index()

    conceptual_variables = list(index.iter_resources(ConceptualVariable))
    assert [item.identifier for item in conceptual_variables] == ["conceptual-variable"]

    unit_types = list(index.iter_resources(UnitType))
    assert [item.identifier for item in unit_types] == ["unit-type"]

    conceptual_variable = conceptual_variables[0]
    urn_match = index.resolve(Reference(urn="urn:ddi:conceptual-variable:1"))
    assert urn_match is conceptual_variable

    unit_type_match = index.resolve(
        Reference(
            type_of_object="UnitType",
            agency="agency.test",
            identifier="unit-type",
            version="1.0",
        )
    )
    assert unit_type_match is unit_types[0]


def test_register_fragment_accepts_newly_registered_maintainable() -> None:
    """register_fragment accepts maintainables defined after module import."""

    with synthetic_maintainable() as SyntheticMaintainable:
        index = Index()
        maintainable = SyntheticMaintainable(
            agency="synthetic.agency",
            identifier="synthetic-1",
            version="1.0",
            value="payload",
        )

        index.register_fragment(maintainable)

        registered = list(index.iter_resources(SyntheticMaintainable))
        assert registered == [maintainable]


def test_index_backlinks_with_conceptual_resources() -> None:
    """Index resolves backlinks and questions referencing conceptual assets."""
    document = _build_document()
    index = document.build_index()

    question_ref = Reference(
        type_of_object="QuestionItem",
        agency="agency.test",
        identifier="q1",
        version="1.0",
    )
    question = index.resolve(question_ref)
    backlinks = index.get_variables_referencing_question(question)
    assert [variable.identifier for variable in backlinks] == ["var-age"]

    backlinks = index.get_variables_referencing_question(question_ref)
    assert {item.identifier for item in backlinks} == {"var-age"}

    external_code_list = CodeList(
        agency="external.agency",
        identifier="CL1",
        version="1.0",
        names=[InternationalString(text="Age codes", child_tag="String")],
    )
    _attach_urn(external_code_list, "urn:ddi:codelist:CL1")

    external_variable = Variable(
        agency="external.agency",
        identifier="var-ext",
        version="2.0",
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency="agency.test",
                identifier="q1",
                version="1.0",
            )
        ],
    )
    _attach_urn(external_variable, "urn:ddi:variable:var-ext")

    external_logical_product = LogicalProduct(
        agency="external.agency",
        identifier="lp-external",
        version="2.0",
        variables=[external_variable],
        code_lists=[external_code_list],
    )
    _attach_urn(external_logical_product, "urn:ddi:logical-product:external")

    index.register_fragment(external_logical_product)

    external_variable_resolved = index.get_variable(
        "var-ext", agency="external.agency", version="2.0"
    )
    assert external_variable_resolved.identifier == "var-ext"

    backlinks = index.get_variables_referencing_question(question_ref)
    assert {item.identifier for item in backlinks} == {"var-age", "var-ext"}

    resolved_code_list = index.resolve(
        Reference(urn="urn:ddi:codelist:CL1", type_of_object="CodeList")
    )
    assert isinstance(resolved_code_list, CodeList)
    assert resolved_code_list.identifier == "CL1"

    questions = index.find_questions(using_code_list=external_code_list)
    assert [item.identifier for item in questions] == ["q1"]

    questions = index.find_questions(
        using_code_list=Reference(
            type_of_object="CodeList",
            agency="external.agency",
            identifier="CL1",
            version="1.0",
        )
    )
    assert [item.identifier for item in questions] == ["q1"]

    questions = index.find_questions(using_code_list="urn:ddi:codelist:CL1")
    assert [item.identifier for item in questions] == ["q1"]

    duplicate_code_list = CodeList(
        agency="external.agency",
        identifier="CL1",
        version="1.0",
    )
    with pytest.raises(ValueError):
        index.register_fragment(
            LogicalProduct(
                agency="external.agency",
                identifier="lp-duplicate",
                version="1.0",
                code_lists=[duplicate_code_list],
            )
        )


def test_backlinks_resolve_partial_question_references() -> None:
    """Backlink rebuilding resolves references with partial identifiers."""

    index = Index()

    question = QuestionItem(
        agency="agency.test",
        identifier="q-partial",
        version="1.0",
    )
    question.urn = "urn:ddi:question:q-partial"

    variable_full = Variable(
        agency="agency.test",
        identifier="var-full",
        version="1.0",
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency="agency.test",
                identifier="q-partial",
                version="1.0",
            )
        ],
    )

    variable_version_only = Variable(
        agency="agency.test",
        identifier="var-version",
        version="1.0",
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                identifier="q-partial",
                version="1.0",
            )
        ],
    )

    variable_identifier_only = Variable(
        agency="agency.test",
        identifier="var-identifier",
        version="1.0",
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                identifier="q-partial",
            )
        ],
    )

    variable_urn = Variable(
        agency="agency.test",
        identifier="var-urn",
        version="1.0",
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                urn="urn:ddi:question:q-partial",
            )
        ],
    )

    index.register_fragment(
        question,
        variable_full,
        variable_version_only,
        variable_identifier_only,
        variable_urn,
    )

    backlinks = index.get_variables_referencing_question(question)
    assert {variable.identifier for variable in backlinks} == {
        "var-full",
        "var-version",
        "var-identifier",
        "var-urn",
    }


def test_index_registers_additional_maintainables() -> None:
    """Index registers maintainables beyond the core study components."""

    index = Index()

    group = Group(
        agency="agency.test",
        identifier="group-1",
        version="1.0",
    )
    _attach_urn(group, "urn:ddi:group:group-1")

    quality_scheme = QualityScheme(
        agency="agency.test",
        identifier="quality-scheme-1",
        version="1.0",
    )
    _attach_urn(quality_scheme, "urn:ddi:quality-scheme:1")

    index.register_fragment(group, quality_scheme)

    group_by_identifier = index.resolve(
        Reference(
            type_of_object="Group",
            agency="agency.test",
            identifier="group-1",
            version="1.0",
        )
    )
    assert group_by_identifier is group

    group_by_urn = index.resolve(Reference(urn="urn:ddi:group:group-1"))
    assert group_by_urn is group

    scheme_by_identifier = index.resolve(
        Reference(
            type_of_object="QualityScheme",
            agency="agency.test",
            identifier="quality-scheme-1",
            version="1.0",
        )
    )
    assert scheme_by_identifier is quality_scheme

    scheme_by_urn = index.resolve(Reference(urn="urn:ddi:quality-scheme:1"))
    assert scheme_by_urn is quality_scheme


def test_index_resolve_identifier_version_without_agency() -> None:
    """Resolution succeeds when only identifier and version are supplied."""

    index = Index()
    variable = Variable(
        agency="agency.one",
        identifier="shared",
        version="1.0",
    )
    index.register_fragment(variable)

    reference = Reference(
        type_of_object="Variable",
        identifier="shared",
        version="1.0",
    )
    assert index.resolve(reference) is variable


def test_index_resolve_identifier_version_without_agency_ambiguous() -> None:
    """Identifier + version resolution raises when multiple agencies match."""

    index = Index()
    variable_one = Variable(
        agency="agency.one",
        identifier="shared",
        version="1.0",
    )
    variable_two = Variable(
        agency="agency.two",
        identifier="shared",
        version="1.0",
    )
    index.register_fragment(variable_one, variable_two)

    reference = Reference(
        type_of_object="Variable",
        identifier="shared",
        version="1.0",
    )
    with pytest.raises(LookupError):
        index.resolve(reference)


def test_index_resolve_identifier_only_unique() -> None:
    """Identifier-only references resolve when a single match exists."""

    index = Index()
    question = QuestionItem(
        agency="agency.one",
        identifier="question",
    )
    index.register_fragment(question)

    reference = Reference(
        type_of_object="QuestionItem",
        identifier="question",
    )
    assert index.resolve(reference) is question


def test_index_resolve_identifier_only_ambiguous() -> None:
    """Identifier-only references raise when multiple matches exist."""

    index = Index()
    question_one = QuestionItem(
        agency="agency.one",
        identifier="duplicate",
    )
    question_two = QuestionItem(
        agency="agency.two",
        identifier="duplicate",
    )
    index.register_fragment(question_one, question_two)

    reference = Reference(
        type_of_object="QuestionItem",
        identifier="duplicate",
    )
    with pytest.raises(LookupError):
        index.resolve(reference)


def test_index_backlinks_handle_identifier_only_question_references() -> None:
    """Backlink computation resolves questions without invoking global resolve."""

    index = Index()
    question = QuestionItem(
        agency="agency.one",
        identifier="q1",
    )
    variable = Variable(
        agency="agency.one",
        identifier="var1",
        version="1.0",
        question_references=[
            Reference(
                type_of_object="QuestionItem",
                agency="agency.one",
                identifier="q1",
            )
        ],
    )

    index.register_fragment(question, variable)

    backlinks = index.get_variables_referencing_question(question)
    assert backlinks == [variable]


def test_register_fragment_accepts_late_registered_maintainable() -> None:
    """New maintainable subclasses remain eligible for registration."""

    @dataclass
    class LateMaintainable(MaintainableBase):
        TAG: ClassVar[str] = qn(INSTANCE_NS, "LateMaintainable")

    resource = LateMaintainable(
        agency="agency.one",
        identifier="late",
        version="1.0",
    )

    index = Index()
    index.register_fragment(resource)

    assert list(index.iter_resources(LateMaintainable)) == [resource]
