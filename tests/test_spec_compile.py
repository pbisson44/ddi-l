"""Compile spec expressions to Colectica conditions and read them back."""

from __future__ import annotations

import json
import re
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

import ddi_l
from ddi_l.colectica_logic import (
    Condition,
    GroupBool,
    LogicGroup,
    NativeCondition,
    Operator,
    Statement,
    StmtBool,
    parse_command,
    parse_condition,
    serialize_condition,
)
from ddi_l.spec.compile import (
    BlaiseDialect,
    CompiledCondition,
    UnverifiableConditionError,
    compile_condition,
    condition_to_expression,
    parse_blaise,
)
from ddi_l.spec.expression import (
    And,
    Arithmetic,
    Comparison,
    Date,
    Expression,
    ExpressionError,
    Identifier,
    Not,
    Number,
    Or,
    Predicate,
    String,
    Today,
    equivalent,
    format_expression,
    parse_expression,
)
from ddi_l.spec.semantics import LogicDependencyError, logic_available
from tests.helpers.examples import examples

FIXTURES = Path(__file__).parent / "fixtures" / "colectica"
NAMES = ("PetCount", "PetKind", "PetAge", "OwnerAge", "VisitDate")
SUBJECTS = {name: f"urn:ddi:int.example:in-{name}:1" for name in NAMES}
BY_SUBJECT = {urn: name for name, urn in SUBJECTS.items()}
CODES = {
    "PetKind": {
        value: f"urn:ddi:int.example:code-{value}:1" for value in ("2", "3", "01")
    }
}
CODE_VALUES = {urn: value for value, urn in CODES["PetKind"].items()}
DIALECT = BlaiseDialect(
    empty="EMPTY",
    refused="REFUSAL",
    today="SYSDATE",
    date="TODATE({year}, {month}, {day})",
)


def _compile(text: str, dialect: BlaiseDialect | None = DIALECT) -> CompiledCondition:
    return compile_condition(text, subjects=SUBJECTS, codes=CODES, dialect=dialect)


def _read_back(condition: Condition) -> str:
    stored = parse_command(condition.language, serialize_condition(condition))
    assert isinstance(stored, Condition)
    expression = condition_to_expression(
        stored, subject_name=BY_SUBJECT.get, code_value=CODE_VALUES.get
    )
    return format_expression(expression)


def _operators(condition: Condition) -> list[list[tuple[int, int]]]:
    return [
        [(int(s.stmt_bool), int(s.operator)) for s in group.statements]
        for group in condition.logic_groups
    ]


# ---- Neutral ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "operator", "value", "codes"),
    [
        ("PetCount = 3", Operator.EQUAL_TO, "3", []),
        ("PetCount != 3", Operator.NOT_EQUAL, "3", []),
        ("PetCount > 2.50", Operator.GREATER_THAN, "2.5", []),
        ("PetCount >= 2", Operator.GREATER_THAN_OR_EQUAL, "2", []),
        ("PetCount < 2", Operator.LESS_THAN, "2", []),
        ("3 > PetCount", Operator.LESS_THAN, "3", []),
        ("PetCount <= 2", Operator.LESS_THAN_OR_EQUAL, "2", []),
        ("empty(PetCount)", Operator.EMPTY, None, []),
        ("not empty(PetCount)", Operator.NOT_EMPTY, None, []),
        ("refused(PetCount)", Operator.REFUSED, None, []),
        ("not refused(PetCount)", Operator.NOT_REFUSED, None, []),
        ("PetKind = 2 or PetKind = 3", Operator.CONTAINS_ANY, None, ["2", "3"]),
        ("PetKind = 2 and PetKind = 3", Operator.CONTAINS_ALL, None, ["2", "3"]),
        ('PetKind = "01"', Operator.CONTAINS_ANY, None, ["01"]),
        ("PetKind != 2", Operator.CONTAINS_NONE, None, ["2"]),
        ("PetKind != 2 and PetKind != 3", Operator.CONTAINS_NONE, None, ["2", "3"]),
    ],
)
def test_each_known_operator_compiles_and_reads_back(
    text: str, operator: Operator, value: str | None, codes: list[str]
) -> None:
    compiled = _compile(text)
    assert compiled.fallback_reason is None
    condition = compiled.condition
    assert isinstance(condition, Condition)
    (group,) = condition.logic_groups
    (statement,) = group.statements
    assert statement.operator is operator
    assert statement.value == value
    assert statement.value_not_needed is (
        operator
        in (Operator.EMPTY, Operator.NOT_EMPTY, Operator.REFUSED, Operator.NOT_REFUSED)
    )
    assert statement.selected_codes == [CODES["PetKind"][code] for code in codes]
    assert condition.synopsis == format_expression(parse_expression(text))
    assert equivalent(_read_back(condition), text)


def test_groups_follow_the_parentheses() -> None:
    text = "PetKind = 2 and (PetCount > 2 or refused(PetCount))"
    condition = _compile(text).condition
    assert isinstance(condition, Condition)
    assert [int(g.group_bool) for g in condition.logic_groups] == [0, 1]
    assert _operators(condition) == [[(0, 11)], [(0, 3), (2, 14)]]
    assert equivalent(_read_back(condition), text)


def test_atoms_next_to_each_other_share_a_group() -> None:
    text = "PetCount = 1 and PetAge > 3 and (empty(OwnerAge) or OwnerAge > 17)"
    condition = _compile(text).condition
    assert isinstance(condition, Condition)
    assert _operators(condition) == [[(0, 1), (1, 3)], [(0, 7), (2, 3)]]
    assert equivalent(_read_back(condition), text)


def test_or_of_groups() -> None:
    text = "PetCount = 3 and PetAge = 4 or PetCount = 5"
    condition = _compile(text).condition
    assert isinstance(condition, Condition)
    assert [int(g.group_bool) for g in condition.logic_groups] == [0, 2]
    assert equivalent(_read_back(condition), text)


def test_missing_expands_into_one_group() -> None:
    condition = _compile("missing(PetAge) or PetAge > 30").condition
    assert isinstance(condition, Condition)
    assert _operators(condition) == [[(0, 7), (2, 14), (2, 3)]]


def test_answered_is_not_empty_and_not_refused() -> None:
    condition = _compile("answered(PetAge)").condition
    assert isinstance(condition, Condition)
    assert _operators(condition) == [[(0, 8), (1, 15)]]
    assert [s.value_not_needed for s in condition.logic_groups[0].statements] == [
        True,
        True,
    ]
    assert equivalent(_read_back(condition), "answered(PetAge)")
    condition = _compile("answered(PetAge) or PetCount = 1").condition
    assert isinstance(condition, Condition)
    assert [int(g.group_bool) for g in condition.logic_groups] == [0, 2]
    assert _operators(condition) == [[(0, 8), (1, 15)], [(0, 1)]]
    assert equivalent(_read_back(condition), "answered(PetAge) or PetCount = 1")


def test_codes_excluded_are_one_statement_only_in_an_and_group() -> None:
    text = "PetKind != 2 or PetKind != 3"
    condition = _compile(text).condition
    assert isinstance(condition, Condition)
    assert _operators(condition) == [[(0, 13), (2, 13)]]
    assert equivalent(_read_back(condition), text)
    text = 'PetKind = 2 and PetKind != 3 and PetKind != "01"'
    condition = _compile(text).condition
    assert isinstance(condition, Condition)
    assert _operators(condition) == [[(0, 11), (1, 13)]]
    assert condition.logic_groups[0].statements[1].selected_codes == [
        CODES["PetKind"]["3"],
        CODES["PetKind"]["01"],
    ]
    assert equivalent(_read_back(condition), text)


def test_codes_excluded_are_one_statement_in_an_or_group() -> None:
    text = "PetCount = 1 and (PetAge > 3 or PetKind != 2 and PetKind != 3)"
    condition = _compile(text).condition
    assert isinstance(condition, Condition)
    assert _operators(condition) == [[(0, 1)], [(0, 3), (2, 13)]]
    assert equivalent(_read_back(condition), text)


def test_an_answer_test_beside_a_comparison_stays_neutral() -> None:
    # PetKind = 2 already needs an answer, so answered(PetKind) adds nothing.
    condition = _compile("answered(PetKind) and PetKind = 2 and PetAge > 3").condition
    assert isinstance(condition, Condition)
    assert _operators(condition) == [[(0, 11), (1, 3)]]
    assert equivalent(_read_back(condition), "PetKind = 2 and PetAge > 3")


def test_a_choice_of_codes_is_one_statement_in_an_and_group() -> None:
    text = (
        "PetCount = 1 and (PetKind = 2 or PetKind = 3)"
        ' or PetCount = 4 and PetKind = "01"'
    )
    compiled = _compile(text)
    assert compiled.fallback_reason is None
    condition = compiled.condition
    assert isinstance(condition, Condition)
    assert [int(g.group_bool) for g in condition.logic_groups] == [0, 2]
    assert _operators(condition) == [[(0, 1), (1, 11)], [(0, 1), (1, 11)]]
    assert condition.logic_groups[0].statements[1].selected_codes == [
        CODES["PetKind"]["2"],
        CODES["PetKind"]["3"],
    ]
    assert equivalent(_read_back(condition), text)


def test_all_of_some_codes_is_one_statement_in_an_or_group() -> None:
    text = "PetCount = 1 and (PetAge > 3 or PetKind = 2 and PetKind = 3)"
    condition = _compile(text).condition
    assert isinstance(condition, Condition)
    assert _operators(condition) == [[(0, 1)], [(0, 3), (2, 12)]]
    assert equivalent(_read_back(condition), text)


def test_a_choice_of_codes_is_not_merged_with_the_same_question_beside_it() -> None:
    # Merged, PetKind = 2 and the choice would read as all three codes.
    text = 'PetKind = 2 and (PetKind = 3 or PetKind = "01") or PetCount = 4'
    condition = _compile(text).condition
    assert isinstance(condition, Condition)
    assert _operators(condition) == [[(0, 11), (1, 11)], [(0, 1)]]
    assert equivalent(_read_back(condition), text)


@pytest.mark.parametrize(
    "text",
    [
        # What follows a choice or a merged code stays in its group.
        "(PetKind = 2 or PetKind = 3) and PetAge > 1 or PetCount = 4",
        "PetKind = 2 or PetKind = 3 or PetAge > 1",
        # Codes joined by and merge into all of them, in either kind of group.
        "PetKind = 2 and PetKind = 3 and (PetAge > 1 or PetCount = 4)",
        "PetCount = 1 or PetKind = 2 and PetKind = 3",
        # Statements after a nested group start a new group.
        "PetCount = 1 and (PetAge > 1 or OwnerAge > 1) and PetCount < 9",
    ],
)
def test_groups_and_merged_codes_read_back(text: str) -> None:
    compiled = _compile(text)
    assert compiled.fallback_reason is None
    assert isinstance(compiled.condition, Condition)
    assert equivalent(_read_back(compiled.condition), text)


def test_the_written_json_is_what_colectica_writes() -> None:
    condition = _compile("PetCount > 0").condition
    assert isinstance(condition, Condition)
    assert json.loads(serialize_condition(condition)) == {
        "LogicGroups": [
            {
                "GroupBooleanType": 0,
                "Statements": [
                    {
                        "StatementBooleanType": 0,
                        "Subject": SUBJECTS["PetCount"],
                        "Operator": 3,
                        "Value": {
                            "Value": "0",
                            "ValueNotNeeded": False,
                            "SelectedCodes": [],
                        },
                    }
                ],
            }
        ],
        "Synopsis": "PetCount > 0",
        "Version": 1,
    }


def test_a_name_without_a_subject_or_a_code_is_an_error() -> None:
    with pytest.raises(ValueError, match="No subject for Unknown"):
        compile_condition("Unknown > 1", subjects=SUBJECTS)
    with pytest.raises(ValueError, match="PetKind has no code '9'"):
        _compile("PetKind = 9")


# ---- Fallback to Blaise -------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "reason", "blaise"),
    [
        (
            "not (PetCount = 1)",
            "'not PetCount = 1' negates a comparison",
            "NOT ({{PetCount}} = 1)",
        ),
        (
            "not (PetKind = 2 or PetKind = 3)",
            "negates a comparison",
            "NOT ({{PetKind}} = 2) AND NOT ({{PetKind}} = 3)",
        ),
        ('PetAge <= "old"', "compares text with <=", '{{PetAge}} <= "old"'),
        ("PetAge + 1 > 3", "calculates", "{{PetAge}} + 1 > 3"),
        ("VisitDate <= today()", "compares dates", "{{VisitDate}} <= SYSDATE"),
        (
            "VisitDate > 2024-02-29",
            "compares dates",
            "{{VisitDate}} > TODATE(2024, 2, 29)",
        ),
        ("PetAge = OwnerAge", "compares two questions", "{{PetAge}} = {{OwnerAge}}"),
        ('PetAge > "old"', "compares text with >", '{{PetAge}} > "old"'),
        ("PetAge", "is not a comparison", "{{PetAge}}"),
        ('"a" = "b"', "does not compare a question with a value", '"a" = "b"'),
        (
            "(PetCount = 1 or (PetAge = 2 and OwnerAge = 3)) and PetCount = 4",
            "and and or are mixed inside a group",
            "(({{PetCount}} = 1) OR (({{PetAge}} = 2) AND ({{OwnerAge}} = 3)))"
            " AND ({{PetCount}} = 4)",
        ),
        (
            # PetAge has no codes, so its choice is two statements, not one.
            "PetCount = 1 and (PetAge = 2 or PetAge = 3) or PetCount = 4",
            "and and or are mixed inside a group",
            "(({{PetCount}} = 1) AND (({{PetAge}} = 2) OR ({{PetAge}} = 3)))"
            " OR ({{PetCount}} = 4)",
        ),
        (
            "PetCount = 1 and (PetKind = 2 or PetKind > 2) or PetCount = 4",
            "and and or are mixed inside a group",
            "(({{PetCount}} = 1) AND (({{PetKind}} = 2) OR ({{PetKind}} > 2)))"
            " OR ({{PetCount}} = 4)",
        ),
        (
            # Only = and != select codes.
            "PetCount = 1 and (PetKind > 2 or PetKind > 3) or PetCount = 4",
            "and and or are mixed inside a group",
            "(({{PetCount}} = 1) AND (({{PetKind}} > 2) OR ({{PetKind}} > 3)))"
            " OR ({{PetCount}} = 4)",
        ),
        (
            "PetCount = 1 and (empty(PetKind) or PetKind = 2) or PetCount = 4",
            "and and or are mixed inside a group",
            "(({{PetCount}} = 1) AND (({{PetKind}} = EMPTY) OR ({{PetKind}} = 2)))"
            " OR ({{PetCount}} = 4)",
        ),
        (
            "PetAge * (PetCount + 1) > 3",
            "calculates",
            "{{PetAge}} * ({{PetCount}} + 1) > 3",
        ),
        (
            # No one statement says "not 2 or not 3", so it cannot nest.
            "PetCount = 1 or PetAge > 3 and (PetKind != 2 or PetKind != 3)",
            "and and or are mixed inside a group",
            "({{PetCount}} = 1) OR (({{PetAge}} > 3) AND (({{PetKind}} <> 2)"
            " OR ({{PetKind}} <> 3)))",
        ),
    ],
)
def test_what_neutral_cannot_hold_falls_back_to_blaise(
    text: str, reason: str, blaise: str
) -> None:
    compiled = _compile(text)
    assert compiled.fallback_reason is not None and reason in compiled.fallback_reason
    assert isinstance(compiled.condition, NativeCondition)
    assert compiled.condition.language == "Blaise"
    assert compiled.condition.text == blaise
    assert compiled.missing_settings == ()
    assert equivalent(parse_blaise(compiled.condition.text, DIALECT), text)


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        (
            "not (PetCount = 1)",
            "'not PetCount = 1' negates a comparison: it holds when the question "
            "has no answer, and whether NotEqual does is not known",
        ),
        ("PetAge + 1 > 3", "'PetAge + 1 > 3' calculates, which Neutral cannot"),
        (
            "PetCount = 1 and (PetAge = 2 or PetAge = 3) or PetCount = 4",
            "and and or are mixed inside a group, and in what order Colectica "
            "evaluates them is not known",
        ),
    ],
)
def test_the_fallback_reason_is_the_whole_sentence(text: str, reason: str) -> None:
    assert _compile(text).fallback_reason == reason


def test_inputs_list_every_name_in_order() -> None:
    compiled = _compile("PetAge + PetCount > OwnerAge or empty(PetAge)")
    assert compiled.inputs == ("PetAge", "PetCount", "OwnerAge")
    assert _compile("PetCount > 1 and PetAge < 3").inputs == ("PetCount", "PetAge")
    unset = _compile("VisitDate < today() and PetAge > 1", dialect=None)
    assert unset.inputs == ("VisitDate", "PetAge")


@pytest.mark.parametrize(
    ("text", "missing", "named"),
    [
        (
            "missing(PetAge) or PetAge + 1 > 3",
            ("empty", "refused"),
            "blaise.empty and blaise.refused, which are",
        ),
        ("VisitDate < today()", ("today",), "blaise.today, which is"),
        ("VisitDate = 2024-01-02", ("date",), "blaise.date, which is"),
    ],
)
def test_without_the_blaise_words_nothing_is_compiled(
    text: str, missing: tuple[str, ...], named: str
) -> None:
    compiled = _compile(text, dialect=None)
    assert compiled.condition is None
    assert compiled.missing_settings == missing
    assert compiled.fallback_reason is not None
    assert f"the Blaise form needs {named} not set" in compiled.fallback_reason


def test_a_dialect_sets_only_what_it_is_given() -> None:
    compiled = _compile(
        "refused(PetAge) or PetAge + 1 < 2", dialect=BlaiseDialect(refused="RF")
    )
    assert isinstance(compiled.condition, NativeCondition)
    assert compiled.condition.text == "({{PetAge}} = RF) OR ({{PetAge}} + 1 < 2)"


# ---- Reading Blaise -------------------------------------------------------------------


def test_reads_the_native_condition_of_the_sample() -> None:
    fragment = ddi_l.open_fragment(FIXTURES / "pets_conditions.ddi33.xml")
    item = fragment.get("22222222-2222-4222-8222-000000000060")
    assert item is not None
    native = parse_condition(item)
    assert isinstance(native, NativeCondition)
    assert equivalent(parse_blaise(native.text), "PetCount > 5")


def test_a_native_condition_with_statements_is_not_read() -> None:
    fragment = ddi_l.open_fragment(FIXTURES / "pets_defects.ddi33.xml")
    natives = [
        condition
        for item in fragment.items()
        if isinstance(condition := _safe_condition(item), NativeCondition)
    ]
    assert natives
    for native in natives:
        with pytest.raises(ExpressionError):
            parse_blaise(native.text, DIALECT)


def _safe_condition(item: object) -> object:
    try:
        return parse_condition(item)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None


@pytest.mark.parametrize(
    ("blaise", "expected"),
    [
        ("PetAge = empty", "empty(PetAge)"),
        ("Refusal = PetAge", "refused(PetAge)"),
        ("PetAge <> EMPTY", "not empty(PetAge)"),
        ("{{ PetAge }} > 3 and not (PetCount = 1)", "PetAge > 3 and not PetCount = 1"),
        ("VisitDate < todate( 2024 ,1, 2 )", "VisitDate < 2024-01-02"),
        ("VisitDate <= SysDate", "VisitDate <= today()"),
        ("Owner.Age > 17", "Owner.Age > 17"),
        ("2024-01-02 = x", "x = 2024 - 1 - 2"),
        ("PetAge >= 3", "PetAge >= 3"),
        # A keyword is a whole word: EMPTYSET is a name.
        ("PetAge = EMPTYSET", "PetAge = EMPTYSET"),
    ],
)
def test_parse_blaise(blaise: str, expected: str) -> None:
    assert equivalent(parse_blaise(blaise, DIALECT), expected)


@pytest.mark.parametrize(
    ("blaise", "reason"),
    [
        ("PetAge != 1", "Unexpected '!='"),
        ("PetAge > EMPTY", "Compare EMPTY with = or <>"),
        ("1 = EMPTY", "EMPTY is compared with a name"),
        ("EMPTY", "EMPTY is compared with a name"),
        ("PetAge + EMPTY = 1", "EMPTY is compared with a name"),
        ("PetAge IN [1, 2]", "Unexpected character '['"),
        ("PetAge IN Codes", "Unexpected 'IN'"),
        ("ABS(PetAge) > 1", "Unknown function 'ABS'"),
        ("{{PetAge > 1", "This {{name}} is not closed"),
    ],
)
def test_parse_blaise_errors(blaise: str, reason: str) -> None:
    with pytest.raises(ExpressionError) as caught:
        parse_blaise(blaise, DIALECT)
    assert caught.value.reason == reason


def test_parse_blaise_reads_the_dialect_words_as_written() -> None:
    dialect = BlaiseDialect(empty="NO ANSWER", refused="REFUSAL", today="TODAY()")

    # Any spacing between the words of a keyword.
    assert equivalent(parse_blaise("PetAge = NO   ANSWER", dialect), "empty(PetAge)")
    # A keyword that ends in a bracket may touch the next word.
    assert equivalent(
        parse_blaise("VisitDate < TODAY()AND PetAge > 1", dialect),
        "VisitDate < today() and PetAge > 1",
    )


def test_a_date_template_names_only_year_month_and_day() -> None:
    with pytest.raises(ValueError, match="names {hour}"):
        parse_blaise("x = 1", BlaiseDialect(date="DT({year}, {hour})"))


# ---- Reading Neutral --------------------------------------------------------------------


def test_reads_the_neutral_condition_of_the_sample() -> None:
    fragment = ddi_l.open_fragment(FIXTURES / "pets_conditions.ddi33.xml")
    gates = [
        condition
        for item in fragment.items()
        if isinstance(condition := _safe_condition(item), Condition)
        and len(condition.logic_groups) == 2
    ]
    (gate,) = gates
    names = {
        "urn:ddi:int.example:22222222-2222-4222-8222-000000000031:1": "PetKind",
        "urn:ddi:int.example:22222222-2222-4222-8222-000000000032:1": "PetCount",
    }
    codes = {"urn:ddi:int.example:22222222-2222-4222-8222-000000000006:1": "3"}
    expression = condition_to_expression(
        gate, subject_name=names.get, code_value=codes.get
    )
    assert equivalent(expression, "PetKind = 3 and (PetCount > 2 or refused(PetCount))")


def _statement(
    operator: int,
    *,
    value: str | None = "1",
    codes: list[str] | None = None,
    join: int = 0,
) -> Statement:
    return Statement(
        stmt_bool=StmtBool(join),
        subject=SUBJECTS["PetAge"],
        operator=Operator(operator),
        value=value,
        selected_codes=codes or [],
    )


@pytest.mark.parametrize(
    ("groups", "reason"),
    [
        ([], "the condition is empty$"),
        ([LogicGroup(GroupBool.FIRST, [])], "the condition is empty"),
        (
            [LogicGroup(GroupBool.FIRST, [_statement(99)])],
            "operator code 99 is not known",
        ),
        (
            [
                LogicGroup(
                    GroupBool.FIRST,
                    [_statement(1), _statement(3, join=1), _statement(1, join=2)],
                )
            ],
            "group 1 mixes And and Or, and in what order Colectica evaluates them "
            "is not known$",
        ),
        (
            [
                LogicGroup(GroupBool.FIRST, [_statement(1)]),
                LogicGroup(GroupBool.AND, [_statement(1)]),
                LogicGroup(GroupBool.OR, [_statement(1)]),
            ],
            "the condition mixes And and Or, and in what order Colectica evaluates "
            "them is not known$",
        ),
        (
            [LogicGroup(GroupBool.FIRST, [_statement(1), _statement(1, join=5)])],
            "group 1 joins with code 5",
        ),
        (
            [LogicGroup(GroupBool.FIRST, [_statement(1), _statement(1, join=0)])],
            "group 1 joins with code 0",
        ),
        (
            [LogicGroup(GroupBool.FIRST, [_statement(1, value=None)])],
            "EQUAL_TO has no value",
        ),
        (
            [
                LogicGroup(
                    GroupBool.FIRST, [_statement(3, codes=[CODES["PetKind"]["2"]])]
                )
            ],
            "GREATER_THAN compares with codes",
        ),
        (
            [
                LogicGroup(
                    GroupBool.FIRST, [_statement(4, codes=[CODES["PetKind"]["2"]])]
                )
            ],
            "GREATER_THAN_OR_EQUAL compares with codes",
        ),
        (
            [LogicGroup(GroupBool.FIRST, [_statement(0)])],
            r"a statement has no operator \(None\)$",
        ),
        (
            [LogicGroup(GroupBool.FIRST, [_statement(16, value=None)])],
            "DONT_KNOW tests for a don't-know answer",
        ),
        (
            [LogicGroup(GroupBool.FIRST, [_statement(17, value=None)])],
            "NOT_DONT_KNOW tests for a don't-know answer",
        ),
        (
            [
                LogicGroup(
                    GroupBool.FIRST,
                    [_statement(9, codes=list(CODES["PetKind"].values())[:2])],
                )
            ],
            "CONTAINS selects 2 codes, and how it reads several is not known$",
        ),
        (
            [LogicGroup(GroupBool.FIRST, [_statement(11)])],
            "CONTAINS_ANY selects no code",
        ),
        (
            [LogicGroup(GroupBool.FIRST, [_statement(11, codes=["urn:ddi:x:gone:1"])])],
            "the code urn:ddi:x:gone:1 is not in the file",
        ),
    ],
)
def test_what_cannot_be_read_back(groups: list[LogicGroup], reason: str) -> None:
    with pytest.raises(UnverifiableConditionError, match=f"^{reason}"):
        condition_to_expression(
            Condition(logic_groups=groups),
            subject_name=BY_SUBJECT.get,
            code_value=CODE_VALUES.get,
        )


def test_an_unbound_subject_cannot_be_read_back() -> None:
    condition = Condition(logic_groups=[LogicGroup(GroupBool.FIRST, [_statement(7)])])
    with pytest.raises(UnverifiableConditionError, match="bound to no known question"):
        condition_to_expression(
            condition, subject_name=lambda urn: None, code_value=CODE_VALUES.get
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2", "PetAge = 2"),
        ("2.50", "PetAge = 2.5"),
        ("-1", "PetAge = -1"),
        ("01", 'PetAge = "01"'),
        ("abc", 'PetAge = "abc"'),
    ],
)
def test_a_stored_value_is_a_number_unless_written_as_text(
    value: str, expected: str
) -> None:
    condition = Condition(
        logic_groups=[LogicGroup(GroupBool.FIRST, [_statement(1, value=value)])]
    )
    expression = condition_to_expression(
        condition, subject_name=BY_SUBJECT.get, code_value=CODE_VALUES.get
    )
    assert format_expression(expression) == expected


def test_equal_to_with_codes_reads_as_any_of_them() -> None:
    codes = [CODES["PetKind"]["2"], CODES["PetKind"]["3"]]
    condition = Condition(
        logic_groups=[LogicGroup(GroupBool.FIRST, [_statement(1, codes=codes)])]
    )
    expression = condition_to_expression(
        condition, subject_name=BY_SUBJECT.get, code_value=CODE_VALUES.get
    )
    assert format_expression(expression) == "PetAge = 2 or PetAge = 3"


@pytest.mark.parametrize(
    ("operator", "codes", "expected"),
    [
        (Operator.CONTAINS, ["2"], "PetAge = 2"),
        (Operator.DOES_NOT_CONTAIN, ["2"], "PetAge != 2"),
        (Operator.NOT_EQUAL, ["2"], "PetAge != 2"),
        (Operator.CONTAINS_NONE, ["2", "3"], "PetAge != 2 and PetAge != 3"),
        (Operator.CONTAINS_ALL, ["2", "3"], "PetAge = 2 and PetAge = 3"),
    ],
)
def test_each_statement_that_selects_codes_reads_back(
    operator: Operator, codes: list[str], expected: str
) -> None:
    statement = _statement(
        int(operator), value=None, codes=[CODES["PetKind"][code] for code in codes]
    )
    condition = Condition(logic_groups=[LogicGroup(GroupBool.FIRST, [statement])])
    expression = condition_to_expression(
        condition, subject_name=BY_SUBJECT.get, code_value=CODE_VALUES.get
    )
    assert format_expression(expression) == expected


# ---- Review fixes -----------------------------------------------------------------------


def test_a_quoted_plain_number_compares_as_that_number() -> None:
    from ddi_l.spec.compile import comparable

    compiled = _compile('PetAge = "3"')
    assert isinstance(compiled.condition, Condition)
    read = condition_to_expression(
        compiled.condition, subject_name=BY_SUBJECT.get, code_value=CODE_VALUES.get
    )
    assert format_expression(read) == "PetAge = 3"
    assert not equivalent(read, 'PetAge = "3"')
    assert equivalent(comparable(read), comparable(parse_expression('PetAge = "3"')))
    coded = _compile('PetKind = "2"')
    assert isinstance(coded.condition, Condition)
    read = condition_to_expression(
        coded.condition, subject_name=BY_SUBJECT.get, code_value=CODE_VALUES.get
    )
    assert equivalent(comparable(read), comparable(parse_expression('PetKind = "2"')))
    # Inside and, or, not, a sign and a calculation, on either side.
    assert comparable(
        parse_expression('"3" = PetAge or not (-PetCount + "1" > "2") and PetAge')
    ) == parse_expression("3 = PetAge or not (-PetCount + 1 > 2) and PetAge")
    # A leading zero, a sign or a space keeps a string a string.
    for text in ('"01"', '"+3"', '" 3"', '"3."'):
        kept = parse_expression(f"PetAge = {text}")
        assert comparable(kept) == kept


@pytest.mark.parametrize(
    "text",
    [
        "PetKind = 9 or PetCount != 1",
        "PetCount != 1 or PetKind = 9",
        # Also when the condition ends up Blaise.
        "PetAge + 1 > 3 or PetKind = 9",
        "PetAge + 1 > 3 or PetKind != 9",
    ],
)
def test_a_missing_code_is_an_error_in_any_order(text: str) -> None:
    with pytest.raises(ValueError, match=r"^PetKind has no code '9'\.$"):
        _compile(text)


EACH_ONCE = "The date template needs {year}, {month} and {day}, each once."
TEXT_BEFORE = (
    "The date template needs text before its first field that does not end with "
    "a digit, so a number is never read as a date."
)
DIGITS_BETWEEN = "The date template has nothing but digits between two fields."
DIGIT_AFTER = (
    "The date template has a digit right after a field, which reads as part of it."
)


@pytest.mark.parametrize(
    ("template", "reason"),
    [
        ("TODATE({year}, {month})", EACH_ONCE),
        ("D({year}, {month}, {day}, {day})", EACH_ONCE),
        ("{year}{month:02d}{day:02d}", TEXT_BEFORE),
        ("D(1{year}, {month}, {day})", TEXT_BEFORE),
        ("D(1 {year}, {month}, {day})", TEXT_BEFORE),
        ("D{year}{month}-{day}", DIGITS_BETWEEN),
        ("D{year}1{month}-{day}", DIGITS_BETWEEN),
        ("D({year}, {hour}, {day})", "The date template names {hour}."),
        ("D({year:>4}, {month}, {day})", "The date template's format {year:>4} is"),
        ("D({year}, {month}, {day}}", "The date template 'D({year}, {month}, {day}}'"),
        ("D({year}, {month}, {day!r})", "The date template's format {day!r} is"),
        ("D{year}-{month}-{day}0", DIGIT_AFTER),
        ("D{year}-{month}1x{day}", DIGIT_AFTER),
    ],
)
def test_a_date_template_must_read_back_unambiguously(
    template: str, reason: str
) -> None:
    with pytest.raises(ValueError, match=f"^{re.escape(reason)}"):
        BlaiseDialect(date=template)


def test_a_date_template_with_widths() -> None:
    dialect = BlaiseDialect(
        empty="EMPTY", refused="REFUSAL", date="D{year:04d}-{month:02d}-{day:02d}"
    )
    compiled = _compile("VisitDate > 2024-02-09", dialect=dialect)
    assert isinstance(compiled.condition, NativeCondition)
    assert compiled.condition.text == "{{VisitDate}} > D2024-02-09"
    assert equivalent(
        parse_blaise(compiled.condition.text, dialect), "VisitDate > 2024-02-09"
    )
    # A number is never read as a date.
    assert (
        format_expression(parse_blaise("{{PetAge}} > 2024", DIALECT)) == "PetAge > 2024"
    )
    assert format_expression(parse_blaise("{{PetAge}} > D20240", dialect)) != (
        "PetAge > 2024-01-01"
    )
    # A value narrower than its width is not a date.
    assert format_expression(parse_blaise("{{VisitDate}} > D2024-2-09", dialect)) == (
        "VisitDate > D2024 - 2 - 9"
    )


@pytest.mark.parametrize(
    "template", ["D{year:02d}-{month:02d}-{day:02d}", "D{year}-{month:01d}-{day:01d}"]
)
def test_a_width_pads_and_the_value_may_be_wider(template: str) -> None:
    dialect = BlaiseDialect(empty="EMPTY", refused="REFUSAL", date=template)
    compiled = _compile("VisitDate > 2024-12-31", dialect=dialect)
    assert isinstance(compiled.condition, NativeCondition)
    assert equivalent(
        parse_blaise(compiled.condition.text, dialect), "VisitDate > 2024-12-31"
    )


# ---- Translation validation -------------------------------------------------------

_NUMERIC = st.sampled_from(["PetCount", "PetAge", "OwnerAge"]).map(Identifier)
_VALUES = st.sampled_from(["0", "1", "2", "2.5"]).map(
    lambda text: Number(Decimal(text))
)
_OPERATORS = st.sampled_from(["=", "!=", "<", "<=", ">", ">="])
_GATES = st.recursive(
    st.one_of(
        st.builds(Comparison, _OPERATORS, _NUMERIC, _VALUES),
        st.builds(Comparison, _OPERATORS, _NUMERIC, st.just(String("2"))),
        st.builds(Comparison, _OPERATORS, _NUMERIC, _NUMERIC),
        st.builds(
            Comparison,
            _OPERATORS,
            st.builds(Arithmetic, st.sampled_from(["+", "*"]), _NUMERIC, _VALUES),
            _NUMERIC,
        ),
        st.builds(
            Comparison,
            st.sampled_from(["=", "!="]),
            st.just(Identifier("PetKind")),
            st.sampled_from([Number(Decimal("2")), Number(Decimal("3")), String("01")]),
        ),
        st.builds(
            Comparison,
            _OPERATORS,
            st.just(Identifier("VisitDate")),
            st.one_of(st.just(Today()), st.dates().map(Date)),
        ),
        st.builds(
            Predicate,
            st.sampled_from(["answered", "missing", "empty", "refused"]),
            st.sampled_from(NAMES).map(Identifier),
        ),
    ),
    lambda children: st.one_of(
        children.map(Not),
        st.lists(children, min_size=2, max_size=3).map(lambda parts: And(tuple(parts))),
        st.lists(children, min_size=2, max_size=3).map(lambda parts: Or(tuple(parts))),
    ),
    max_leaves=6,
)


@examples(300)
@given(_GATES)
def test_every_compiled_condition_reads_back_as_its_expression(
    expression: Expression,
) -> None:
    compiled = compile_condition(
        expression, subjects=SUBJECTS, codes=CODES, dialect=DIALECT, validate=True
    )

    assert compiled.verified is True


def _off_by_one(compiled: CompiledCondition) -> CompiledCondition:
    """A compiler fault: ``>`` written as ``>=``."""
    condition = compiled.condition
    assert isinstance(condition, Condition)
    groups = [
        replace(
            group,
            statements=[
                replace(statement, operator=Operator.GREATER_THAN_OR_EQUAL)
                if statement.operator is Operator.GREATER_THAN
                else statement
                for statement in group.statements
            ],
        )
        for group in condition.logic_groups
    ]
    return replace(compiled, condition=replace(condition, logic_groups=groups))


@pytest.fixture
def faulty_compiler(monkeypatch: pytest.MonkeyPatch) -> None:
    from ddi_l.spec import compile as compiling

    compiled = compiling._compiled
    monkeypatch.setattr(
        compiling, "_compiled", lambda *args: _off_by_one(compiled(*args))
    )


@pytest.mark.skipif(not logic_available(), reason="requires the 'logic' extra")
@pytest.mark.usefixtures("faulty_compiler")
def test_a_condition_that_reads_back_differently_is_caught() -> None:
    assert _compile("PetCount > 3").verified is False
    with pytest.raises(ValueError) as caught:
        compile_condition("PetCount > 3", subjects=SUBJECTS, codes=CODES, validate=True)
    assert str(caught.value) == (
        "The compiled condition reads back as PetCount >= 3, which differs from "
        "PetCount > 3 when PetCount is 3."
    )


@pytest.mark.usefixtures("faulty_compiler")
def test_without_the_logic_extra_a_difference_is_not_decided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("ddi_l.spec.semantics.logic_available", lambda: False)
    monkeypatch.setattr(
        "ddi_l.spec.semantics._smt",
        lambda: (_ for _ in ()).throw(LogicDependencyError()),
    )

    assert _compile("PetCount > 3").verified is None
    # What normal forms settle needs no solver.
    assert _compile("PetCount = 3").verified is True
    with pytest.raises(LogicDependencyError):
        compile_condition("PetCount > 3", subjects=SUBJECTS, codes=CODES, validate=True)


def test_what_is_not_checked_is_not_verified() -> None:
    assert (
        compile_condition("PetCount > 3", subjects=SUBJECTS, validate=False).verified
        is None
    )
    # No condition was compiled: the Blaise form needs a word.
    assert _compile("not PetCount = 3 or empty(PetAge)", dialect=None).verified is None
    # Two names on one subject: what it reads back as cannot tell them apart.
    shared = {"PetCount": SUBJECTS["PetCount"], "PetAge": SUBJECTS["PetCount"]}
    assert (
        compile_condition("PetCount = 1 and PetAge = 2", subjects=shared).verified
        is None
    )


def test_a_condition_that_does_not_read_back_is_not_verified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ddi_l.spec import compile as compiling

    def unreadable(text: str, dialect: BlaiseDialect | None = None) -> Expression:
        raise ExpressionError("unexpected input", text, 1)

    monkeypatch.setattr(compiling, "parse_blaise", unreadable)
    assert _compile("not PetCount = 3").verified is False

    monkeypatch.setattr(
        compiling,
        "condition_to_expression",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            UnverifiableConditionError("the condition is empty")
        ),
    )
    compiled = _compile("PetCount = 3")
    assert compiled.verified is False
    with pytest.raises(ValueError, match="does not read back: the condition is empty"):
        compile_condition("PetCount = 3", subjects=SUBJECTS, validate=True)
