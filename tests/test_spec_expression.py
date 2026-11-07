"""The spec expression language: parsing, writing, normal form."""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ddi_l.spec.expression import (
    And,
    Arithmetic,
    Comparison,
    Date,
    Expression,
    ExpressionError,
    Identifier,
    Negate,
    Not,
    Number,
    Or,
    Predicate,
    String,
    Today,
    equivalent,
    format_expression,
    identifiers,
    normalise,
    parse_expression,
)
from tests.helpers.examples import examples

X = Identifier("x")
Y = Identifier("y")


def _n(value: str) -> Number:
    return Number(Decimal(value))


# ---- Parsing ---------------------------------------------------------------------


def test_or_binds_looser_than_and_and_not() -> None:
    assert parse_expression("not a and b or c") == Or(
        (And((Not(Identifier("a")), Identifier("b"))), Identifier("c"))
    )


def test_comparison_binds_tighter_than_not() -> None:
    assert parse_expression("not x = 1") == Not(Comparison("=", X, _n("1")))


def test_arithmetic_precedence_and_left_associativity() -> None:
    assert parse_expression("x - 1 - 2 * y") == Arithmetic(
        "-",
        Arithmetic("-", X, _n("1")),
        Arithmetic("*", _n("2"), Y),
    )
    assert parse_expression("-x * -2") == Arithmetic("*", Negate(X), _n("-2"))


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("x == 1", Comparison("=", X, _n("1"))),
        ("x AND y", And((X, Y))),
        ("x && y || x", Or((And((X, Y)), X))),
        ("ANSWERED(x)", Predicate("answered", X)),
        ("Today()", Today()),
        (
            "d >= 2024-02-29",
            Comparison(">=", Identifier("d"), Date(datetime.date(2024, 2, 29))),
        ),
        ("x = 'it''s'", Comparison("=", X, String("it's"))),
        ('x = "say ""hi"""', Comparison("=", X, String('say "hi"'))),
        ("Owner.Age > 17", Comparison(">", Identifier("Owner.Age"), _n("17"))),
        ("x = 2024 - 1", Comparison("=", X, Arithmetic("-", _n("2024"), _n("1")))),
    ],
)
def test_parses(text: str, expected: Expression) -> None:
    assert parse_expression(text) == expected


@pytest.mark.parametrize(
    ("text", "reason", "column"),
    [
        ("", "The expression is empty", 1),
        ("   ", "The expression is empty", 4),
        ("1 < x < 3", "Comparisons do not chain: join them with 'and'", 7),
        ("x <> 1", "Write != for not equal", 3),
        ("answered(1)", "answered() takes the name of a question", 10),
        ("refused(x, y)", "refused() takes one name, then ')'", 10),
        ("today(x)", "today() takes no argument", 7),
        ("lookup(x)", "Unknown function 'lookup'", 1),
        ("x = 'abc", "This string is not closed", 5),
        ("(a and b", "Expected ')', found end of the expression", 9),
        ("a and", "Expected a value, found end of the expression", 6),
        ("a b", "Unexpected 'b'", 3),
        ("x # 1", "Unexpected character '#'", 3),
        ("d = 2024-13-01", "This is not a valid date", 5),
        ("x = 3.x", "This is not a number", 5),
        ("and", "Expected a value, found 'and'", 1),
    ],
)
def test_errors_point_at_the_column(text: str, reason: str, column: int) -> None:
    with pytest.raises(ExpressionError) as caught:
        parse_expression(text)
    assert (caught.value.reason, caught.value.column) == (reason, column)
    lines = str(caught.value).splitlines()
    assert lines[0] == f"{reason} (column {column})"
    assert lines[1] == f"  {text}"
    assert lines[2] == "  " + " " * (column - 1) + "^"


def test_identifiers_in_order_of_first_use() -> None:
    expression = parse_expression("b > 1 and answered(a) or b = c")
    assert identifiers(expression) == ["b", "a", "c"]


# ---- Writing ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "written"),
    [
        ("a and (b or c)", "a and (b or c)"),
        ("(a and b) or c", "a and b or c"),
        ("a and (b and c)", "a and (b and c)"),
        ("not (a or b)", "not (a or b)"),
        ("a - (b - c)", "a - (b - c)"),
        ("(a - b) - c", "a - b - c"),
        ("(a + b) * c", "(a + b) * c"),
        ("-(a + b)", "-(a + b)"),
        ("x == 2.50", "x = 2.5"),
        ("x = 1.0", "x = 1"),
        ("x = 'q'", 'x = "q"'),
        ("(x = 1) = (y = 2)", "(x = 1) = (y = 2)"),
        ("NOT a OR b", "not a or b"),
    ],
)
def test_writes_only_the_parentheses_needed(text: str, written: str) -> None:
    assert format_expression(parse_expression(text)) == written


# ---- Normal form ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("answered(x)", "not missing(x)"),
        ("answered(x)", "not empty(x) and not refused(x)"),
        ("missing(x)", "refused(x) or empty(x)"),
        ("3 < x", "x > 3"),
        ("2 >= x", "x <= 2"),
        ("x = y", "y = x"),
        ("x = 3", "x = 3.00"),
        ("a and b", "b and a"),
        ("a and (b and c)", "(c and a) and b"),
        ("a or a", "a"),
        ("not (a and b)", "not a or not b"),
        ("not (a or b)", "not a and not b"),
        ("not not a", "a"),
        ("not answered(x)", "missing(x)"),
        ("x = 1 and (y = 2 or y = 3)", "(y = 3 or 2 = y) and 1 = x"),
        # A comparison of x already needs an answer: answered(x) beside it goes.
        ("answered(x) and x > 3", "x > 3"),
        ("not missing(x) and (x = 1 or x = 2)", "x = 1 or x = 2"),
        ("not refused(x) and x = y", "x = y"),
        ("answered(x) and x = 1 or answered(x) and x = 2", "x = 1 or x = 2"),
        ("not (missing(x) or not x > 3)", "x > 3"),
    ],
)
def test_equivalent(left: str, right: str) -> None:
    assert equivalent(left, right)


@pytest.mark.parametrize(
    ("left", "right"),
    [
        # Normalising calculates nothing: these agree on whole numbers, but
        # their normal forms differ (the logic extra decides them).
        ("x > 3", "x >= 4"),
        ("x + 1 > 3", "x > 2"),
        ("x * 2", "2 * x"),
        # A comparison under not is kept: they differ when x has no answer.
        ("not x > 3", "x <= 3"),
        ("a and b", "a or b"),
        ("empty(x)", "missing(x)"),
        # answered(x) stays where nothing beside it needs x answered.
        ("answered(x) and (x = 1 or y = 2)", "x = 1 or y = 2"),
        ("answered(x) and not x = 1", "not x = 1"),
        ("answered(x) and y > 3", "y > 3"),
        ("answered(x) or x > 3", "x > 3"),
    ],
)
def test_not_recognised_as_equivalent(left: str, right: str) -> None:
    assert not equivalent(left, right, exact=False)


def test_normal_form_reads_back() -> None:
    normal = normalise(parse_expression("not (answered(PetKind) and 3 < PetCount)"))
    assert format_expression(normal) == (
        "empty(PetKind) or not PetCount > 3 or refused(PetKind)"
    )


def test_equivalent_takes_trees_or_text() -> None:
    assert equivalent(Comparison("<", _n("3"), X), "x > 3")
    with pytest.raises(ExpressionError):
        equivalent("x >", "x > 1")


# ---- Properties ----------------------------------------------------------------------

_NAMES = st.from_regex(
    r"[A-Za-z_][A-Za-z0-9_]{0,6}(\.[A-Za-z_][A-Za-z0-9_]{0,4})?", fullmatch=True
).filter(lambda name: name.lower() not in ("and", "or", "not"))
_IDENTIFIERS = _NAMES.map(Identifier)
_LEAVES: st.SearchStrategy[Expression] = st.one_of(
    st.decimals(min_value=-(10**6), max_value=10**6, places=3, allow_nan=False).map(
        Number
    ),
    st.text(max_size=8).map(String),
    st.dates().map(Date),
    _IDENTIFIERS,
    st.just(Today()),
    st.builds(
        Predicate,
        st.sampled_from(["answered", "missing", "empty", "refused"]),
        _IDENTIFIERS,
    ),
)


def _extend(children: st.SearchStrategy[Expression]) -> st.SearchStrategy[Expression]:
    several = st.lists(children, min_size=2, max_size=3).map(tuple)
    return st.one_of(
        # The parser folds a minus into a number literal.
        children.filter(lambda node: not isinstance(node, Number)).map(Negate),
        st.builds(
            Arithmetic, st.sampled_from(["+", "-", "*", "/"]), children, children
        ),
        st.builds(
            Comparison,
            st.sampled_from(["=", "!=", "<", "<=", ">", ">="]),
            children,
            children,
        ),
        children.map(Not),
        several.map(And),
        several.map(Or),
    )


_EXPRESSIONS = st.recursive(_LEAVES, _extend, max_leaves=12)


@examples(300)
@given(_EXPRESSIONS)
def test_what_is_written_parses_back(expression: Expression) -> None:
    assert parse_expression(format_expression(expression)) == expression


@examples(300)
@given(_EXPRESSIONS)
def test_normalising_twice_changes_nothing(expression: Expression) -> None:
    normal = normalise(expression)
    assert normalise(normal) == normal
    assert equivalent(expression, normal)


def test_walk_reaches_every_operand() -> None:
    expression = parse_expression("-a > 1 and not b or c * d = 2")
    assert identifiers(expression) == ["a", "b", "c", "d"]


def test_format_rejects_what_is_not_an_expression() -> None:
    with pytest.raises(TypeError, match="Not an expression"):
        format_expression(object())  # type: ignore[arg-type]


# ---- Numbers keep every digit -----------------------------------------------------


def test_a_long_number_keeps_every_digit() -> None:
    long = "1.00000000000000000000000000001"  # 30 significant digits
    assert not equivalent(f"x = {long}", "x = 1")
    assert format_expression(normalise(parse_expression(f"x = {long}0"))) == (
        f"x = {long}"
    )
    tree = parse_expression(f"x = -{long}")
    assert format_expression(tree) == f"x = -{long}"
    assert parse_expression(format_expression(tree)) == tree
    big = "123456789012345678901234567890123"
    assert format_expression(normalise(parse_expression(f"x = {big}.000"))) == (
        f"x = {big}"
    )
    assert not equivalent(f"x = {big}", f"x = {big[:-1]}0")


def test_the_expression_helpers_are_public() -> None:
    import ddi_l.spec as spec

    tree = spec.parse_expression("PetAge > 1 and PetKind = PetAge")
    assert spec.identifiers(tree) == ["PetAge", "PetKind"]
    assert next(spec.walk(tree)) is tree
    assert spec.comparable(spec.parse_expression('PetKind = "2"')) == (
        spec.parse_expression("PetKind = 2")
    )
