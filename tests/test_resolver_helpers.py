import pytest

from ddi_l.maintainable_registry import (
    clear_registered_maintainables,
    register_maintainable,
    resolve,
)
from ddi_l.models.base import InternationalString, Reference
from ddi_l.models.datacollection import DataCollection, QuestionItem
from ddi_l.models.logicalproduct import LogicalProduct, Variable
from ddi_l.models.physical import PhysicalStructure
from ddi_l.models.study import StudyUnit


@pytest.fixture(autouse=True)
def _reset_registry() -> None:  # type: ignore[misc]
    clear_registered_maintainables()
    yield
    clear_registered_maintainables()


def _question(urn: str, identifier: str) -> QuestionItem:
    return QuestionItem(
        urn=urn,
        agency="agency.test",
        identifier=identifier,
        version="1.0",
        question_texts=[InternationalString(text="Question?")],
    )


def test_resolver_returns_registered_instances() -> None:
    question = _question("urn:ddi:agency.test:question:q1", "q1")
    register_maintainable(question)

    key = (question.agency, question.identifier, question.version)
    reference = Reference(
        type_of_object="QuestionItem",
        urn=question.urn,
        agency=question.agency,
        identifier=question.identifier,
        version=question.version,
    )

    assert resolve(question.urn) is question  # type: ignore[arg-type]
    assert resolve(key) is question
    assert resolve(reference) is question


def test_data_collection_get_questions_combines_inline_and_referenced() -> None:
    inline = _question("urn:ddi:agency.test:question:inline", "inline")
    referenced = _question("urn:ddi:agency.test:question:ref", "ref")
    register_maintainable(referenced)

    collection = DataCollection(
        urn="urn:ddi:agency.test:collection:1",
        agency="agency.test",
        identifier="collection-1",
        version="1.0",
        questions=[inline],
        question_item_references=[
            Reference(
                type_of_object="QuestionItem",
                urn=referenced.urn,
                agency=referenced.agency,
                identifier=referenced.identifier,
                version=referenced.version,
            )
        ],
    )

    questions = collection.get_questions()
    urns = {question._format_urn() for question in questions}
    assert urns == {inline._format_urn(), referenced._format_urn()}


def test_study_unit_helpers_include_inline_and_referenced_content() -> None:
    inline_question = _question("urn:ddi:agency.test:question:inline", "inline")
    referenced_question = _question("urn:ddi:agency.test:question:ref", "ref")
    register_maintainable(referenced_question)

    inline_collection = DataCollection(
        urn="urn:ddi:agency.test:collection:inline",
        agency="agency.test",
        identifier="collection-inline",
        version="1.0",
        questions=[inline_question],
    )
    referenced_collection = DataCollection(
        urn="urn:ddi:agency.test:collection:ref",
        agency="agency.test",
        identifier="collection-ref",
        version="1.0",
        questions=[referenced_question],
    )
    register_maintainable(referenced_collection)

    inline_variable = Variable(
        urn="urn:ddi:agency.test:variable:inline",
        agency="agency.test",
        identifier="variable-inline",
        version="1.0",
    )
    referenced_variable = Variable(
        urn="urn:ddi:agency.test:variable:ref",
        agency="agency.test",
        identifier="variable-ref",
        version="1.0",
    )
    register_maintainable(referenced_variable)

    variable_reference = Reference(
        type_of_object="Variable",
        urn=referenced_variable.urn,
        agency=referenced_variable.agency,
        identifier=referenced_variable.identifier,
        version=referenced_variable.version,
    )
    logical_product = LogicalProduct(
        urn="urn:ddi:agency.test:logical-product:1",
        agency="agency.test",
        identifier="logical-product-1",
        version="1.0",
        variables=[inline_variable],
        other_elements=[variable_reference.to_xml("VariableReference")],
    )

    inline_structure = PhysicalStructure(
        urn="urn:ddi:agency.test:physical:inline",
        agency="agency.test",
        identifier="physical-inline",
        version="1.0",
    )
    referenced_structure = PhysicalStructure(
        urn="urn:ddi:agency.test:physical:ref",
        agency="agency.test",
        identifier="physical-ref",
        version="1.0",
    )
    register_maintainable(referenced_structure)

    study = StudyUnit(
        urn="urn:ddi:agency.test:study:1",
        agency="agency.test",
        identifier="study-1",
        version="1.0",
        data_collections=[inline_collection],
        data_collection_references=[
            Reference(
                type_of_object="DataCollection",
                urn=referenced_collection.urn,
                agency=referenced_collection.agency,
                identifier=referenced_collection.identifier,
                version=referenced_collection.version,
            )
        ],
        logical_products=[logical_product],
        physical_structures=[inline_structure],
        physical_instance_references=[
            Reference(
                type_of_object="PhysicalStructure",
                urn=referenced_structure.urn,
                agency=referenced_structure.agency,
                identifier=referenced_structure.identifier,
                version=referenced_structure.version,
            )
        ],
    )

    variable_urns = {variable._format_urn() for variable in study.get_variables()}
    assert variable_urns == {
        inline_variable._format_urn(),
        referenced_variable._format_urn(),
    }

    question_urns = {question._format_urn() for question in study.get_questions()}
    assert question_urns == {
        inline_question._format_urn(),
        referenced_question._format_urn(),
    }

    dataset_urns = {dataset._format_urn() for dataset in study.get_datasets()}
    assert dataset_urns == {
        inline_structure._format_urn(),
        referenced_structure._format_urn(),
    }
