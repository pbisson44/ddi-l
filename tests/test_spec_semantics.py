"""What an expression means (`evaluate`) and whether two agree (`decide`)."""

from __future__ import annotations

import datetime
import gc
import sys
import threading
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

import ddi_l.spec
from ddi_l.spec import (
    Answer,
    Example,
    LogicDependencyError,
    Verdict,
    decide,
    equivalent,
    evaluate,
    normalise,
    parse_expression,
)
from ddi_l.spec.expression import (
    PREDICATES,
    And,
    Arithmetic,
    Comparison,
    Date,
    Expression,
    Identifier,
    Not,
    Number,
    Or,
    Predicate,
    Today,
)
from ddi_l.spec.semantics import (
    ANSWERED,
    EMPTY,
    OTHER,
    REFUSED,
    _typing,
    logic_available,
)
from tests.helpers.examples import examples

needs_logic = pytest.mark.skipif(
    not logic_available(), reason="requires the 'logic' extra"
)
DAY = datetime.date(2024, 5, 31)


def _answered(*values: object) -> Answer:
    return Answer(ANSWERED, frozenset(values))  # type: ignore[arg-type]


# ---- One respondent ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "answers", "holds"),
    [
        ("empty(x)", {}, True),
        ("missing(x)", {"x": Answer(REFUSED)}, True),
        ("answered(x)", {"x": Answer(ANSWERED)}, True),
        ("refused(x)", {"x": _answered(Fraction(1))}, False),
        # A comparison needs a value; under not, it holds without one.
        ("x > 3", {"x": Answer(ANSWERED)}, False),
        ("not x > 3", {}, True),
        ("x <= 3", {}, False),
        ("x > 3", {"x": _answered(Fraction(7, 2))}, True),
        # Several answers: = is "among them", != "not among them".
        ("x = 1", {"x": _answered(Fraction(1), Fraction(2))}, True),
        ("x != 1", {"x": _answered(Fraction(1), Fraction(2))}, False),
        ("x != 3", {"x": _answered(Fraction(1), OTHER)}, True),
        ("x != 3", {"x": Answer(ANSWERED)}, False),
        ('x = "1"', {"x": _answered(Fraction(1))}, False),
        ("x > 1", {"x": _answered(Fraction(2), Fraction(3))}, False),
        # Dividing by zero makes a comparison false.
        (
            "x / y > 1",
            {"x": _answered(Fraction(1)), "y": _answered(Fraction(0))},
            False,
        ),
        (
            "x - y = -1",
            {"x": _answered(Fraction(1)), "y": _answered(Fraction(2))},
            True,
        ),
        ("-x = -1", {"x": _answered(Fraction(1))}, True),
        ("x * 2 = 3", {"x": _answered(Fraction(3, 2))}, True),
        ("d <= today()", {"d": _answered(DAY)}, True),
        ("d + 1 > today()", {"d": _answered(DAY)}, True),
        ("d = 2024-05-31", {"d": _answered(DAY)}, True),
        ('t = "yes"', {"t": _answered("yes")}, True),
        ('t != "yes"', {"t": _answered("no")}, True),
        ('"a" = "a"', {}, True),
        ("x > 1 and (empty(y) or y = 2)", {"x": _answered(Fraction(2))}, True),
        ("x = 1", {}, False),
        ("x > 1", {"x": _answered(OTHER)}, False),
        ("-x < 0", {}, False),
        ("x != y", {"x": _answered(Fraction(1)), "y": _answered(Fraction(2))}, True),
        ("x / 2 = 1", {"x": _answered(Fraction(2))}, True),
        # Text compared with text, and with a number.
        ("t = u", {"t": _answered("a"), "u": _answered("a")}, True),
        ("t != u", {"t": _answered("a"), "u": _answered("a")}, False),
        ("t = u", {"t": _answered("a"), "u": _answered(Fraction(1))}, False),
        # today() on either side, under a minus, in arithmetic.
        ("today() >= d", {"d": _answered(DAY)}, True),
        ("-today() < 0", {}, True),
        ("today() - 1 < today()", {}, True),
        ("1 + today() > today()", {}, True),
    ],
)
def test_evaluate(text: str, answers: dict[str, Answer], holds: bool) -> None:
    assert evaluate(text, answers, DAY) is holds


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ("d <= today()", "today() needs the interview date"),
        ('x < "b"', "text is not compared by order"),
        ('x + "b" > 1', "text is not calculated with"),
        ("x and y > 1", "Identifier is not a condition"),
        ("(x > 1) + 1 > 2", "a condition (Comparison) is not a value"),
    ],
)
def test_what_cannot_be_evaluated(text: str, reason: str) -> None:
    answers = {name: _answered("a") for name in ("x", "y")}
    answers["d"] = _answered(DAY)
    with pytest.raises(ValueError) as caught:
        evaluate(parse_expression(text), answers)
    assert str(caught.value) == reason


@pytest.mark.parametrize(
    ("example", "text"),
    [
        (
            Example(
                {"PetCount": _answered(Fraction(1)), "PetKind": Answer(REFUSED)}, DAY
            ),
            "PetCount is 1, PetKind is refused and today is 2024-05-31",
        ),
        (Example({"x": _answered(Fraction(13, 4))}), "x is 3.25"),
        (Example({"x": _answered(Fraction(-5, 2))}), "x is -2.5"),
        (Example({"x": _answered(Fraction(1, 3))}), "x is 1/3"),
        (Example({"x": _answered(Fraction(1), Fraction(2))}), "x is 1 and 2"),
        (Example({"x": _answered(Fraction(1), OTHER)}), "x is 1 and another value"),
        (Example({"x": _answered("yes")}), "x is 'yes'"),
        (Example({"x": _answered(DAY)}), "x is 2024-05-31"),
        (Example({"x": Answer(ANSWERED)}), "x is answered with no value"),
        (Example({"x": Answer(EMPTY)}), "x is empty"),
        (
            Example({"x": _answered(Fraction(1), Fraction(2), Fraction(3))}),
            "x is 1, 2 and 3",
        ),
        (Example({"x": _answered(Fraction(1, 4))}), "x is 0.25"),
        # Past 30 decimal places, a fraction.
        (Example({"x": _answered(Fraction(1, 2**31))}), "x is 1/2147483648"),
        (Example(), ""),
    ],
)
def test_an_example_in_words(example: Example, text: str) -> None:
    assert example.describe() == text


def test_another_value_shows_as_other() -> None:
    assert repr(OTHER) == "OTHER"


# ---- Two expressions -------------------------------------------------------------


@needs_logic
@pytest.mark.parametrize(
    ("left", "right", "types", "outcome"),
    [
        ("x > 3", "x >= 4", None, "different"),
        ("x > 3", "x >= 4", {"x": "integer"}, "equivalent"),
        ("x + 1 > 3", "x > 2", None, "equivalent"),
        ("x / 2 > 1", "x > 2", None, "equivalent"),
        ("answered(x)", "x > 3 or x <= 3", None, "different"),
        ("not x > 3", "x <= 3", None, "different"),
        ("x = 1", "x = 1 and answered(x)", None, "equivalent"),
        ("x = 1 or x = 2", "not (x != 1 and x != 2)", None, "different"),
        ("x = 1 and x = 2", "x > 5 and x < 3", None, "equivalent"),
        ("x = y", "x - y = 0", None, "equivalent"),
        ("x = y and x > 0", "x = y and y > 0", None, "equivalent"),
        ("VisitDate <= today()", "VisitDate < today() + 1", None, "equivalent"),
        ("VisitDate <= today()", "VisitDate < today()", None, "different"),
        ("d > 2024-05-31", "d >= 2024-06-01", None, "equivalent"),
        ('t = "a" and t = "b"', 't = "a" and t = "c"', {"t": "text"}, "equivalent"),
        ("c = 1 and c = 2", "c = 1 and c = 3", {"c": "numeric"}, "equivalent"),
        # Two codes of one question may both be chosen.
        ("c = 1 and c = 2", "c = 1 and c = 3", None, "unknown"),
        ("c = 1 and c = 2", "c = 1 and c = 3", {"c": "code"}, "unknown"),
        ('PetCount > "00"', "PetCount > 0", None, "unknown"),
        ("x = y", "x = 1", None, "unknown"),
        ("c > 1", "c >= 2", {"c": "code"}, "unknown"),
        ('t > "a"', 't >= "b"', {"t": "text"}, "unknown"),
        ("t + 1 > 2", "t > 1", {"t": "text"}, "unknown"),
        ("x and y > 1", "y > 1", None, "unknown"),
        ("-d > 1", "d < -1", None, "equivalent"),
        ("-d > 1", "d < -1", {"d": "date"}, "unknown"),
        ("d - 2024-01-01 > 3", "d > 2024-01-04", None, "equivalent"),
        ("x * x = 2", "x * x = 2 and x > 0", None, "unknown"),
        ("missing(x)", "empty(x)", None, "different"),
        ("answered(x)", "not empty(x)", None, "different"),
        ("c != 1", "c = 1", None, "different"),
        ("x > y", "x < y", None, "different"),
        ("x != y", "x > y or x < y", None, "equivalent"),
        ("x * 2 > 4", "x > 2", None, "equivalent"),
        ("x / y > 0", "x * y > 0", None, "equivalent"),
        # A whole number divided is not divided as a whole number.
        ("x / 2 > 1", "x > 2", {"x": "integer"}, "equivalent"),
        ("y = x + 1", "y - x = 1", None, "equivalent"),
        ("d - 1 < today()", "d <= today()", None, "equivalent"),
        ("1 + d > today()", "d >= today()", None, "equivalent"),
        # y is a date, so x is one too.
        ("x < y and y < 2024-01-01", "x < y and y <= 2023-12-31", None, "equivalent"),
        # One text answer is one value; two codes may both be chosen.
        ('t = "a" and t = "b"', 't = "a" and t != "a"', {"t": "text"}, "equivalent"),
        ("c = 1 and c = 2", "c = 1 and c != 1", None, "unknown"),
        # The first and last dates there are.
        ("d < 0001-01-02", "d < 0001-01-01", None, "different"),
        ("d > 9999-12-30", "d > 9999-12-31", None, "different"),
        ("today() < 0001-01-02", "today() < 0001-01-01", None, "different"),
        ("today() > 9999-12-30", "today() > 9999-12-31", None, "different"),
        # No day comes before the first or after the last.
        ("d < 0001-01-01", "d < 0001-01-01 and e = 1", None, "equivalent"),
        ("d > 9999-12-31", "d > 9999-12-31 and e = 1", None, "equivalent"),
        ("today() < 0001-01-01", "today() < 0001-01-01 and e = 1", None, "equivalent"),
        ("today() > 9999-12-31", "today() > 9999-12-31 and e = 1", None, "equivalent"),
        # b is a date, so a is one too, though a is compared with b first.
        (
            "a < b and b < 2024-01-01",
            "b < 2024-01-01 and refused(a)",
            None,
            "different",
        ),
        ('"a" = "a"', "x = 1 or not x = 1", None, "equivalent"),
    ],
)
def test_decide(
    left: str, right: str, types: dict[str, str] | None, outcome: str
) -> None:
    verdict = decide(left, right, types=types)

    assert verdict.outcome == outcome, verdict
    if outcome == "different":
        assert verdict.example is not None
        example = verdict.example
        assert evaluate(left, example.answers, example.today) != evaluate(
            right, example.answers, example.today
        )
    if outcome == "unknown":
        assert verdict.reason


@needs_logic
def test_a_difference_comes_with_the_respondent_it_shows_in() -> None:
    verdict = decide("answered(x)", "x > 3 or x <= 3")

    assert verdict == Verdict(
        "different", Example({"x": Answer(ANSWERED)}), reason=None
    )
    assert verdict.example is not None
    assert verdict.example.describe() == "x is answered with no value"
    # The same question, the same answer.
    assert decide("answered(x)", "x > 3 or x <= 3") == verdict


@needs_logic
@pytest.mark.parametrize(
    ("left", "right", "types", "reason"),
    [
        ('x = 1 and x = "a"', "x = 1", None, 'x = "a" compares number with text'),
        (
            "c > 1",
            "c >= 2",
            {"c": "code"},
            "c is a code, so it is not ordered or calculated",
        ),
        ("x and y > 1", "y > 1", None, "x is used as a condition"),
        ("(x > 1) + 1 > 2", "x > 1", None, "the condition x > 1 is compared"),
        ("-d > 1", "d < -1", {"d": "date"}, "-d negates date"),
        ("t + 1 > 2", "t > 1", {"t": "text"}, "t + 1 calculates with text and number"),
        (
            "a = -b and a = 2024-01-01",
            "a = 2024-01-01",
            None,
            "a = -b compares date with number",
        ),
    ],
)
def test_what_cannot_be_modelled_says_why(
    left: str, right: str, types: dict[str, str] | None, reason: str
) -> None:
    assert decide(left, right, types=types) == Verdict("unknown", reason=reason)


@needs_logic
def test_a_respondent_is_one_the_model_allows() -> None:
    verdict = decide("empty(x)", "refused(x)")
    assert verdict.example is not None
    assert verdict.example.answers["x"].state in (EMPTY, REFUSED)
    # c is neither 1 nor 2.
    assert decide("c != 1", "c = 2") == Verdict(
        "different", Example({"c": Answer(ANSWERED, frozenset({OTHER}))})
    )
    verdict = decide("VisitDate <= today()", "VisitDate < today()")
    assert verdict.example is not None
    (value,) = verdict.example.answers["VisitDate"].values
    assert isinstance(value, datetime.date)
    assert verdict.example.today == value
    assert decide("refused(x)", "refused(x) and empty(x)") == Verdict(
        "different", Example({"x": Answer(REFUSED)})
    )
    assert decide("c = 1", "c = 1 and c != 1") == Verdict(
        "different", Example({"c": Answer(ANSWERED, frozenset({Fraction(1)}))})
    )


@needs_logic
def test_why_a_pair_is_unknown() -> None:
    assert decide('PetCount > "00"', "PetCount > 0").reason == (
        'PetCount > "00" compares text by order'
    )
    assert decide("c = 1 and c = 2", "c = 1 and c = 3").reason == (
        "they differ only for a question answered with several codes"
    )
    assert decide("x = y", "x = 1").reason == (
        "x may take several answers, so it is not compared with another name"
    )
    assert decide("x * x = 2", "x * x = 2 and x > 0").reason == (
        "they differ only when a value is irrational"
    )


@needs_logic
def test_the_solver_gives_up_at_its_resource_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ddi_l.spec import _smt

    monkeypatch.setattr(_smt, "RESOURCE_LIMIT", 1)

    assert decide("x > 3", "x >= 4") == Verdict("unknown", reason="the solver gave up")


@needs_logic
def test_a_respondent_the_evaluator_does_not_separate_them_by_is_no_difference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ddi_l.spec import _smt

    monkeypatch.setattr(_smt, "evaluate", lambda *arguments: False)

    assert decide("x > 3", "x >= 4") == Verdict(
        "unknown", reason="the respondent found does not separate them"
    )


@pytest.mark.parametrize("right", ["x > 2", "x > 1"])
def test_types_must_be_known(right: str) -> None:
    with pytest.raises(ValueError) as caught:
        decide("x > 1", right, types={"x": "whole"})
    assert str(caught.value) == (
        "x: 'whole' is not one of numeric, integer, date, text, code"
    )


@needs_logic
def test_equivalent_decides_what_normalising_cannot() -> None:
    assert equivalent("x + 1 > 3", "x > 2")
    assert not equivalent("x + 1 > 3", "x > 2", exact=False)
    assert equivalent("x > 3", "x >= 4", types={"x": "integer"})
    assert not equivalent("x > 3", "x >= 4")


@needs_logic
def test_pairs_are_decided_in_parallel_threads() -> None:
    pairs = [
        ("x > 3", "x >= 4", {"x": "integer"}),
        ("x > 3", "x >= 4", None),
        ("answered(x)", "x > 3 or x <= 3", None),
        ("d <= today()", "d < today() + 1", None),
    ]
    expected = [
        decide(left, right, types=types).outcome for left, right, types in pairs
    ]
    found: list[list[str]] = []

    def run() -> None:
        outcomes = []
        for _ in range(5):
            for left, right, types in pairs:
                outcomes.append(decide(left, right, types=types).outcome)
            # Free the Z3 objects of other threads on this one.
            gc.collect()
        found.append(outcomes)

    threads = [threading.Thread(target=run) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert found == [expected * 5] * 8


def test_without_the_logic_extra(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "z3", None)
    monkeypatch.delitem(sys.modules, "ddi_l.spec._smt", raising=False)
    monkeypatch.delattr(ddi_l.spec, "_smt", raising=False)

    assert not logic_available()
    # What normalising decides needs no solver.
    assert decide("answered(x)", "not missing(x)") == Verdict("equivalent")
    assert equivalent("answered(x)", "not missing(x)", exact=True)
    assert not equivalent("x + 1 > 3", "x > 2")
    with pytest.raises(LogicDependencyError) as caught:
        decide("x + 1 > 3", "x > 2")
    assert str(caught.value) == (
        'Deciding expressions needs z3-solver: pip install "ddi-l[logic]"'
    )
    with pytest.raises(LogicDependencyError):
        equivalent("x + 1 > 3", "x > 2", exact=True)


# ---- Properties ----------------------------------------------------------------------

TYPES = {"a": "integer", "b": "numeric", "c": "code", "d": "date"}
_NUMBERS = st.sampled_from(["-1", "0", "1", "2", "2.5"]).map(
    lambda text: Number(__import__("decimal").Decimal(text))
)
_SCALARS = st.sampled_from(["a", "b"]).map(Identifier)
_OPERATORS = st.sampled_from(["=", "!=", "<", "<=", ">", ">="])
_DATES = st.integers(min_value=-2, max_value=2).map(
    lambda days: Date(DAY + datetime.timedelta(days=days))
)
_COMPARISONS: st.SearchStrategy[Expression] = st.one_of(
    st.builds(Comparison, _OPERATORS, _SCALARS, _NUMBERS),
    st.builds(Comparison, _OPERATORS, _SCALARS, _SCALARS),
    st.builds(
        Comparison,
        _OPERATORS,
        st.builds(
            Arithmetic, st.sampled_from(["+", "-", "*", "/"]), _SCALARS, _NUMBERS
        ),
        _SCALARS,
    ),
    st.builds(
        Comparison,
        st.sampled_from(["=", "!="]),
        st.just(Identifier("c")),
        st.sampled_from(["1", "2", "3"]).map(
            lambda text: Number(__import__("decimal").Decimal(text))
        ),
    ),
    st.builds(
        Comparison,
        _OPERATORS,
        st.just(Identifier("d")),
        st.one_of(st.just(Today()), _DATES),
    ),
    st.builds(
        Predicate,
        st.sampled_from(PREDICATES),
        st.sampled_from(["a", "b", "c", "d"]).map(Identifier),
    ),
)


def _junctions(
    children: st.SearchStrategy[Expression],
) -> st.SearchStrategy[Expression]:
    several = st.lists(children, min_size=2, max_size=3).map(tuple)
    return st.one_of(children.map(Not), several.map(And), several.map(Or))


_CONDITIONS = st.recursive(_COMPARISONS, _junctions, max_leaves=5)


def _answers() -> st.SearchStrategy[dict[str, Answer]]:
    def answer(
        values: st.SearchStrategy[frozenset[object]],
    ) -> st.SearchStrategy[Answer]:
        return st.one_of(
            st.sampled_from([Answer(EMPTY), Answer(REFUSED), Answer(ANSWERED)]),
            values.map(lambda found: Answer(ANSWERED, found)),  # type: ignore[arg-type]
        )

    def one(values: st.SearchStrategy[object]) -> st.SearchStrategy[frozenset[object]]:
        return values.map(lambda value: frozenset({value}))

    return st.fixed_dictionaries(
        {
            "a": answer(one(st.integers(-2, 4).map(Fraction))),
            "b": answer(one(st.integers(-4, 10).map(lambda k: Fraction(k, 2)))),
            "c": answer(
                st.frozensets(
                    st.sampled_from([Fraction(1), Fraction(2), Fraction(3), OTHER]),
                    min_size=1,
                )
            ),
            "d": answer(
                one(st.integers(-3, 3).map(lambda days: DAY + datetime.timedelta(days)))
            ),
        }
    )


_TODAYS = st.integers(-3, 3).map(lambda days: DAY + datetime.timedelta(days))
EXAMPLES = examples(300)


@EXAMPLES
@given(_CONDITIONS, _answers(), _TODAYS)
def test_normalising_keeps_who_an_expression_holds_for(
    expression: Expression, answers: dict[str, Answer], today: datetime.date
) -> None:
    assert evaluate(expression, answers, today) == evaluate(
        normalise(expression), answers, today
    )


@needs_logic
@EXAMPLES
@given(_CONDITIONS)
def test_the_solver_never_separates_an_expression_from_its_normal_form(
    expression: Expression,
) -> None:
    from ddi_l.spec import _smt

    normal = normalise(expression)
    verdict = _smt.decide(expression, normal, _typing((expression, normal), TYPES))

    assert verdict.outcome != "different", verdict


@needs_logic
@EXAMPLES
@given(
    _CONDITIONS,
    _CONDITIONS,
    st.lists(st.tuples(_answers(), _TODAYS), min_size=1, max_size=20),
)
def test_a_verdict_agrees_with_evaluating(
    left: Expression,
    right: Expression,
    respondents: list[tuple[dict[str, Answer], datetime.date]],
) -> None:
    verdict = decide(left, right, types=TYPES)

    if verdict.outcome == "equivalent":
        for answers, today in respondents:
            assert evaluate(left, answers, today) == evaluate(right, answers, today)
    elif verdict.outcome == "different":
        example = verdict.example
        assert example is not None
        assert evaluate(left, example.answers, example.today) != evaluate(
            right, example.answers, example.today
        )
        # The respondent is one the types allow.
        for name, answer in example.answers.items():
            if answer.values and name != "c":
                assert len(answer.values) == 1
            if name == "a" and answer.values:
                (value,) = answer.values
                assert isinstance(value, Fraction) and value.denominator == 1


def _whole_steps(expression: Expression) -> Expression:
    """``a > k`` as ``a >= k + 1`` and the like: the same for whole ``a``."""
    if isinstance(expression, (And, Or)):
        return type(expression)(
            tuple(_whole_steps(child) for child in expression.operands)
        )
    if isinstance(expression, Not):
        return Not(_whole_steps(expression.operand))
    if (
        isinstance(expression, Comparison)
        and expression.left == Identifier("a")
        and isinstance(expression.right, Number)
        and expression.right.value == expression.right.value.to_integral_value()
    ):
        step = {">": (">=", 1), "<": ("<=", -1), ">=": (">", -1), "<=": ("<", 1)}
        if expression.operator in step:
            operator, by = step[expression.operator]
            return Comparison(
                operator, expression.left, Number(expression.right.value + by)
            )
    return expression


@needs_logic
@EXAMPLES
@given(
    _CONDITIONS,
    st.lists(st.tuples(_answers(), _TODAYS), min_size=1, max_size=20),
)
def test_whole_numbers_are_whole(
    expression: Expression,
    respondents: list[tuple[dict[str, Answer], datetime.date]],
) -> None:
    stepped = _whole_steps(expression)

    assert decide(expression, stepped, types=TYPES) == Verdict("equivalent")
    for answers, today in respondents:
        assert evaluate(expression, answers, today) == evaluate(stepped, answers, today)
