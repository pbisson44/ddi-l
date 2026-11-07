"""What a gate or an edit condition means: the respondents it holds for.

A respondent leaves each question empty, refuses it or answers it. An answer
may have no value to compare (a don't-know); a question that takes several
answers has several values. A comparison holds only when every question it
reads has a value and nothing in it divides by zero, so ``not (x > 3)``
holds when ``x`` has no answer and ``x <= 3`` does not. ``x = 1`` holds when
1 is among the values of ``x``; ``x != 1`` when ``x`` has values and 1 is
not among them.

`evaluate` tells whether an expression holds for one respondent. `decide`
tells whether two expressions hold for the same respondents, and when they
do not, finds a respondent they disagree on. It needs the ``logic`` extra
(``pip install "ddi-l[logic]"``, the Z3 solver).

How each name is read:

* a name compared only by ``=`` and ``!=`` with literals may take several
  answers (a code list allowing several), unless ``types`` says otherwise;
* a name ordered (``<``...), used in arithmetic, or compared with a date or
  ``today()`` takes one value: a number, or a date;
* numbers are rational, and whole only when ``types`` says ``integer``;
  dates are whole days.

`decide` answers ``unknown`` when it cannot model the expressions: text
compared by order, a condition compared as a value or a value used as a
condition, a name compared with numbers and with text, or two names compared
when either may take several answers.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from fractions import Fraction
from typing import TYPE_CHECKING

from .expression import (
    And,
    Arithmetic,
    Comparison,
    Date,
    Expression,
    Identifier,
    Negate,
    Not,
    Number,
    Or,
    Predicate,
    String,
    Today,
    format_expression,
    normalise,
    parse_expression,
    walk,
)

if TYPE_CHECKING:
    from types import ModuleType

__all__ = [
    "ANSWERED",
    "EMPTY",
    "OTHER",
    "REFUSED",
    "TYPES",
    "Answer",
    "Example",
    "LogicDependencyError",
    "Verdict",
    "decide",
    "evaluate",
    "logic_available",
]

EMPTY = "empty"
REFUSED = "refused"
ANSWERED = "answered"

# What `types` can say a name is.
TYPES = ("numeric", "integer", "date", "text", "code")

_NUMBER, _TEXT, _DATE = "number", "text", "date"
_DECLARED = {
    "numeric": _NUMBER,
    "integer": _NUMBER,
    "date": _DATE,
    "text": _TEXT,
    "code": None,
}
_ORDERED = ("<", "<=", ">", ">=")
_LITERALS = (Number, String, Date)
# The dates `datetime.date` can hold, as day numbers.
FIRST_DAY, LAST_DAY = datetime.date.min.toordinal(), datetime.date.max.toordinal()


class _Other:
    """A value none of the expressions names."""

    def __repr__(self) -> str:
        return "OTHER"


OTHER = _Other()

Value = Fraction | str | datetime.date | _Other


@dataclass(frozen=True)
class Answer:
    """How a respondent answered one question.

    Attributes:
        state: `EMPTY`, `REFUSED` or `ANSWERED`.
        values: What the answer compares as: one value; several for a
            question that takes several answers; none for an answer with no
            value to compare (a don't-know). Numbers are `Fraction`, text
            `str`, dates `datetime.date`; `OTHER` is a value no expression
            names.
    """

    state: str
    values: frozenset[Value] = frozenset()


@dataclass(frozen=True)
class Example:
    """A respondent: their answers, by spec name, and the interview date.

    A name with no answer here left its question empty.
    """

    answers: Mapping[str, Answer] = field(default_factory=dict)
    today: datetime.date | None = None

    def describe(self) -> str:
        """The answers in words: ``PetCount is 1 and PetKind is refused``."""
        parts = [
            f"{name} {_answer_text(self.answers[name])}"
            for name in sorted(self.answers)
        ]
        if self.today is not None:
            parts.append(f"today is {self.today.isoformat()}")
        if len(parts) < 2:
            return "".join(parts)
        return ", ".join(parts[:-1]) + " and " + parts[-1]


def _answer_text(answer: Answer) -> str:
    if answer.state != ANSWERED:
        return f"is {answer.state}"
    if not answer.values:
        return "is answered with no value"
    named = sorted(
        (_value_text(value) for value in answer.values if value is not OTHER),
    )
    if OTHER in answer.values:
        named.append("another value")
    return "is " + (
        named[0] if len(named) == 1 else ", ".join(named[:-1]) + " and " + named[-1]
    )


def _value_text(value: Value) -> str:
    if isinstance(value, Fraction):
        # A decimal when it has one (up to 30 places), else a fraction.
        places = 0
        while (value * 10**places).denominator != 1 and places < 30:
            places += 1
        scaled = value * 10**places
        if scaled.denominator != 1:
            return f"{value.numerator}/{value.denominator}"
        if places == 0:
            return str(scaled.numerator)
        digits = str(abs(scaled.numerator)).rjust(places + 1, "0")
        sign = "-" if value < 0 else ""
        return f"{sign}{digits[:-places]}.{digits[-places:]}"
    if isinstance(value, datetime.date):
        return value.isoformat()
    return repr(value)  # text: OTHER is never named


@dataclass(frozen=True)
class Verdict:
    """Whether two expressions hold for the same respondents.

    Attributes:
        outcome: ``"equivalent"``, ``"different"`` or ``"unknown"``.
        example: For ``"different"``, a respondent one holds for and the
            other does not.
        reason: For ``"unknown"``, why it could not be decided.
    """

    outcome: str
    example: Example | None = None
    reason: str | None = None


class LogicDependencyError(ImportError):
    """The ``logic`` extra (the Z3 solver) is not installed."""

    def __init__(self) -> None:
        super().__init__(
            'Deciding expressions needs z3-solver: pip install "ddi-l[logic]"'
        )


# ---- One respondent ------------------------------------------------------------


def evaluate(
    expression: Expression | str,
    answers: Mapping[str, Answer],
    today: datetime.date | None = None,
) -> bool:
    """Whether ``expression`` holds for a respondent.

    Args:
        expression: The expression, or its text.
        answers: The respondent's answers by name; a name not given left its
            question empty.
        today: The interview date, for ``today()``.

    Raises:
        ValueError: If the expression compares text by order, mixes text
            and numbers in arithmetic, or reads ``today()`` without a date.
        ExpressionError: If a string does not parse.
    """
    if isinstance(expression, str):
        expression = parse_expression(expression)
    return _holds(expression, answers, today)


def _holds(
    node: Expression, answers: Mapping[str, Answer], today: datetime.date | None
) -> bool:
    if isinstance(node, Predicate):
        state = answers.get(node.subject.name, Answer(EMPTY)).state
        if node.name == "answered":
            return state == ANSWERED
        if node.name == "missing":
            return state != ANSWERED
        return state == node.name
    if isinstance(node, Not):
        return not _holds(node.operand, answers, today)
    if isinstance(node, And):
        return all(_holds(child, answers, today) for child in node.operands)
    if isinstance(node, Or):
        return any(_holds(child, answers, today) for child in node.operands)
    if isinstance(node, Comparison):
        return _compares(node, answers, today)
    raise ValueError(f"{type(node).__name__} is not a condition")


def _membership(node: Comparison) -> tuple[str, Expression] | None:
    """``(name, literal)`` for ``name = literal`` or ``name != literal``."""
    if node.operator not in ("=", "!="):
        return None
    for name, other in ((node.left, node.right), (node.right, node.left)):
        if isinstance(name, Identifier) and isinstance(other, _LITERALS):
            return name.name, other
    return None


def _compares(
    node: Comparison, answers: Mapping[str, Answer], today: datetime.date | None
) -> bool:
    member = _membership(node)
    if member is not None:
        name, literal = member
        answer = answers.get(name, Answer(EMPTY))
        if answer.state != ANSWERED or not answer.values:
            return False
        value = _literal(literal)
        return (value in answer.values) == (node.operator == "=")
    left = _value(node.left, answers, today)
    right = _value(node.right, answers, today)
    if left is None or right is None:
        return False
    if isinstance(left, str) or isinstance(right, str):
        if node.operator in _ORDERED:
            raise ValueError("text is not compared by order")
        same = left == right
        return same if node.operator == "=" else not same
    return {
        "=": left == right,
        "!=": left != right,
        "<": left < right,
        "<=": left <= right,
        ">": left > right,
        ">=": left >= right,
    }[node.operator]


def _literal(node: Expression) -> Value:
    if isinstance(node, Number):
        return Fraction(node.value)
    if isinstance(node, Date):
        return node.value
    assert isinstance(node, String)
    return node.value


def _value(
    node: Expression, answers: Mapping[str, Answer], today: datetime.date | None
) -> Fraction | str | None:
    """The value of a term: a number, a date as its day number, or text.

    ``None`` when a name it reads has no single value, or it divides by zero.
    """
    if isinstance(node, (Number, String, Date)):
        return _scalar(_literal(node))
    if isinstance(node, Today):
        if today is None:
            raise ValueError("today() needs the interview date")
        return Fraction(today.toordinal())
    if isinstance(node, Identifier):
        answer = answers.get(node.name, Answer(EMPTY))
        if answer.state != ANSWERED or len(answer.values) != 1:
            return None
        (value,) = answer.values
        return None if value is OTHER else _scalar(value)
    if isinstance(node, Negate):
        operand = _value(node.operand, answers, today)
        return None if operand is None else -_number(operand)
    if isinstance(node, Arithmetic):
        left = _value(node.left, answers, today)
        right = _value(node.right, answers, today)
        if left is None or right is None:
            return None
        left, right = _number(left), _number(right)
        if node.operator == "/":
            return None if right == 0 else left / right
        return {"+": left + right, "-": left - right, "*": left * right}[node.operator]
    raise ValueError(f"a condition ({type(node).__name__}) is not a value")


def _scalar(value: Value) -> Fraction | str:
    if isinstance(value, datetime.date):
        return Fraction(value.toordinal())
    assert not isinstance(value, _Other)
    return value


def _number(value: Fraction | str) -> Fraction:
    if isinstance(value, str):
        raise ValueError("text is not calculated with")
    return value


# ---- How names are read --------------------------------------------------------


class _UnmodelledError(Exception):
    """Two expressions `decide` cannot model; the message says why."""


@dataclass
class _Typing:
    """How the names of two expressions are read.

    Attributes:
        types: Each name's type: number, text or date.
        scalar: The names with one value, a number or a day number; the
            others are read by the literals they are compared with.
        integer: The scalar names that are whole numbers (dates included).
        single: The other names that take at most one answer.
        literals: For each name compared with literals, those literals.
    """

    types: dict[str, str] = field(default_factory=dict)
    scalar: set[str] = field(default_factory=set)
    integer: set[str] = field(default_factory=set)
    single: set[str] = field(default_factory=set)
    literals: dict[str, list[Value]] = field(default_factory=dict)


def _typing(expressions: Iterable[Expression], declared: Mapping[str, str]) -> _Typing:
    """Read the names of ``expressions`` together (see the module notes).

    Raises:
        _UnmodelledError: If they cannot be modelled.
    """
    typing = _Typing()
    comparisons: list[Comparison] = []
    names: set[str] = set()
    ordered: set[str] = set()  # names ordered, or in arithmetic
    related: list[set[str]] = []  # names compared with more than a literal
    for expression in expressions:
        _check_condition(expression)
        for node in walk(expression):
            if isinstance(node, (Identifier, Predicate)):
                names.add(
                    node.name if isinstance(node, Identifier) else node.subject.name
                )
            elif isinstance(node, Comparison):
                comparisons.append(node)
                for side in (node.left, node.right):
                    _check_value(side)
                    for inner in walk(side):
                        if isinstance(inner, (Arithmetic, Negate)):
                            ordered.update(_names(inner))
                if node.operator in _ORDERED:
                    ordered.update(_names(node))
                elif _membership(node) is None:
                    related.append(_names(node))
    types = typing.types
    for name, kind in declared.items():
        given = _DECLARED[kind]
        if given is not None:
            types[name] = given
    # A name compared with a side of known type has that type.
    changed = True
    while changed:
        changed = False
        for node in comparisons:
            for side, other in ((node.left, node.right), (node.right, node.left)):
                if isinstance(side, Identifier) and side.name not in types:
                    found = _type(other, types)
                    if found is not None:
                        types[side.name] = found
                        changed = True
    for name in names:
        types.setdefault(name, _NUMBER)
    for node in comparisons:
        left, right = _type(node.left, types), _type(node.right, types)
        if left != right:
            raise _UnmodelledError(f"{_described(node)} compares {left} with {right}")
        if left == _TEXT and node.operator in _ORDERED:
            raise _UnmodelledError(f"{_described(node)} compares text by order")
    for name in sorted(names):
        said = declared.get(name)
        if said == "code" and name in ordered:
            raise _UnmodelledError(
                f"{name} is a code, so it is not ordered or calculated"
            )
        # Ordered text has already failed the type check above.
        if said in ("numeric", "integer") or types[name] == _DATE or name in ordered:
            typing.scalar.add(name)
            if said == "integer" or types[name] == _DATE:
                typing.integer.add(name)
        elif said == "text":
            typing.single.add(name)
    for group in related:
        loose = sorted(group - typing.scalar)
        if loose:
            raise _UnmodelledError(
                f"{loose[0]} may take several answers, so it is not compared "
                "with another name"
            )
    for node in comparisons:
        member = _membership(node)
        if member is not None:
            values = typing.literals.setdefault(member[0], [])
            value = _literal(member[1])
            if value not in values:
                values.append(value)
    return typing


def _check_condition(node: Expression) -> None:
    if isinstance(node, (Not, And, Or)):
        for child in node.operands if isinstance(node, (And, Or)) else (node.operand,):
            _check_condition(child)
    elif not isinstance(node, (Comparison, Predicate)):
        raise _UnmodelledError(f"{_described(node)} is used as a condition")


def _check_value(node: Expression) -> None:
    for inner in walk(node):
        if isinstance(inner, (Comparison, Predicate, Not, And, Or)):
            raise _UnmodelledError(f"the condition {_described(inner)} is compared")


def _names(node: Expression) -> set[str]:
    return {inner.name for inner in walk(node) if isinstance(inner, Identifier)}


def _type(node: Expression, types: Mapping[str, str]) -> str | None:
    """The type of a value term; ``None`` while a name in it has none."""
    if isinstance(node, Number):
        return _NUMBER
    if isinstance(node, String):
        return _TEXT
    if isinstance(node, (Date, Today)):
        return _DATE
    if isinstance(node, Identifier):
        return types.get(node.name)
    if isinstance(node, Negate):
        operand = _type(node.operand, types)
        if operand not in (None, _NUMBER):
            raise _UnmodelledError(f"{_described(node)} negates {operand}")
        return None if operand is None else _NUMBER
    assert isinstance(node, Arithmetic)
    left, right = _type(node.left, types), _type(node.right, types)
    if left is None or right is None:
        return None
    found = {
        ("+", _NUMBER, _NUMBER): _NUMBER,
        ("+", _DATE, _NUMBER): _DATE,
        ("+", _NUMBER, _DATE): _DATE,
        ("-", _NUMBER, _NUMBER): _NUMBER,
        ("-", _DATE, _NUMBER): _DATE,
        ("-", _DATE, _DATE): _NUMBER,
        ("*", _NUMBER, _NUMBER): _NUMBER,
        ("/", _NUMBER, _NUMBER): _NUMBER,
    }.get((node.operator, left, right))
    if found is None:
        raise _UnmodelledError(f"{_described(node)} calculates with {left} and {right}")
    return found


def _described(node: Expression) -> str:
    return format_expression(node)


# ---- Two expressions -------------------------------------------------------------


def _smt() -> ModuleType:
    """`ddi_l.spec._smt`, which imports Z3."""
    try:
        from . import _smt
    except ImportError as error:
        if error.name != "z3":
            raise
        raise LogicDependencyError from error
    return _smt


def logic_available() -> bool:
    """Whether the ``logic`` extra is installed, so `decide` can run."""
    try:
        _smt()
    except LogicDependencyError:
        return False
    return True


def decide(
    left: Expression | str,
    right: Expression | str,
    *,
    types: Mapping[str, str] | None = None,
) -> Verdict:
    """Whether ``left`` and ``right`` hold for the same respondents.

    Expressions with the same `normalise` form are equivalent without
    calculating. Otherwise the solver looks for a respondent they disagree
    on; ``"different"`` comes with one, checked with `evaluate`.

    Args:
        left: An expression, or its text.
        right: Another.
        types: What some names are, by name: one of `TYPES`. A ``code``
            may take several answers; ``integer`` is a whole number.

    Raises:
        LogicDependencyError: Without the ``logic`` extra.
        ExpressionError: If a string does not parse.
        ValueError: If ``types`` gives a type not in `TYPES`.
    """
    for name, kind in (types or {}).items():
        if kind not in _DECLARED:
            raise ValueError(f"{name}: {kind!r} is not one of {', '.join(TYPES)}")
    if isinstance(left, str):
        left = parse_expression(left)
    if isinstance(right, str):
        right = parse_expression(right)
    if normalise(left) == normalise(right):
        return Verdict("equivalent")
    try:
        typing = _typing((left, right), types or {})
    except _UnmodelledError as reason:
        return Verdict("unknown", reason=str(reason))
    verdict: Verdict = _smt().decide(left, right, typing)
    return verdict
