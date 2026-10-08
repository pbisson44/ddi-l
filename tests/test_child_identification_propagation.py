"""Tests for automatic propagation of maintainable child identification metadata."""

from uuid import uuid5

from ddi_l.constants import IDENTIFIER_NAMESPACE
from ddi_l.models.datacollection import QuestionItem, QuestionScheme
from ddi_l.models.logicalproduct import CodeList, LogicalProduct, Variable


def _expected_identifier(*parts: str) -> str:
    return str(uuid5(IDENTIFIER_NAMESPACE, ":".join(parts)))


def test_question_scheme_propagates_child_metadata() -> None:
    item_one = QuestionItem()
    item_two = QuestionItem()

    QuestionScheme(
        agency="org.example",
        version="2",
        identifier="scheme",
        question_items=[item_one, item_two],
    )

    assert item_one.agency == "org.example"
    assert item_one.version == "2"
    assert item_one._auto_identifier == _expected_identifier(
        "org.example", "scheme", "question-item"
    )
    assert item_one._inherited_identifier_suffixes == ("question-item",)

    assert item_two.agency == "org.example"
    assert item_two.version == "2"
    assert item_two._auto_identifier == _expected_identifier(
        "org.example", "scheme", "question-item-2"
    )
    assert item_two._inherited_identifier_suffixes == ("question-item-2",)


def test_logical_product_propagates_child_metadata() -> None:
    variable_one = Variable()
    variable_two = Variable()
    code_list = CodeList()

    LogicalProduct(
        agency="org.example",
        version="1",
        identifier="logical",
        variables=[variable_one, variable_two],
        code_lists=[code_list],
    )

    assert variable_one.agency == "org.example"
    assert variable_one.version == "1"
    assert variable_one._auto_identifier == _expected_identifier(
        "org.example", "logical", "variable"
    )
    assert variable_one._inherited_identifier_suffixes == ("variable",)

    assert variable_two.agency == "org.example"
    assert variable_two.version == "1"
    assert variable_two._auto_identifier == _expected_identifier(
        "org.example", "logical", "variable-2"
    )
    assert variable_two._inherited_identifier_suffixes == ("variable-2",)

    assert code_list.agency == "org.example"
    assert code_list.version == "1"
    assert code_list._auto_identifier == _expected_identifier(
        "org.example", "logical", "code-list"
    )
    assert code_list._inherited_identifier_suffixes == ("code-list",)
