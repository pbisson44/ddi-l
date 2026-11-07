"""The expression language of a questionnaire spec: gates and edit checks.

A spec writes a module's or a question's gate, and an edit's condition, as a
small expression::

    PetCount > 0 and answered(PetKind)
    not refused(OwnerAge) or OwnerAge >= 18
    VisitDate <= today()

From the loosest binding to the tightest:

========================  ==================================================
``or``, ``||``            either side
``and``, ``&&``           both sides
``not``                   negation
``= == != < <= > >=``     one comparison; they do not chain (``1 < x < 3``
                          is an error: write ``1 < x and x < 3``)
``+ -``                   addition, subtraction
``* /``                   multiplication, division
``-``                     negation of a number
========================  ==================================================

Operands are numbers (``3``, ``2.5``), strings (``"text"`` or ``'text'``, a
quote doubled inside), ISO dates (``2024-05-31``: write spaces around a minus
to subtract), identifiers (``PetCount``, ``Owner.Age``), parentheses, and five
functions:

``answered(x)``
    ``x`` has an answer: neither empty nor refused.
``missing(x)``
    ``x`` has no answer: empty or refused.
``empty(x)``
    ``x`` was not answered.
``refused(x)``
    ``x`` was refused.
``today()``
    The date of the interview.

Keywords and function names are case-insensitive; identifiers are not. A
number is compared as a number, so ``01`` and ``1`` are the same value; write
a code whose leading zero matters as a string (``"01"``).

`normalise` rewrites an expression into a canonical form. Two expressions
with the same normal form are equivalent; two with different forms may still
be, because normalising calculates nothing: ``x > 3`` and ``x >= 4`` stay
different, and so do ``not (x > 3)`` and ``x <= 3`` (they differ when ``x``
has no answer). With the ``logic`` extra, `equivalent` decides the rest (see
`ddi_l.spec.semantics`): ``x > 3`` and ``x >= 4`` agree for whole numbers.
"""

from __future__ import annotations

import datetime
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, replace
from decimal import Decimal, localcontext
from typing import TypeAlias

__all__ = [
    "PREDICATES",
    "And",
    "Arithmetic",
    "Comparison",
    "Date",
    "Expression",
    "ExpressionError",
    "Identifier",
    "Negate",
    "Not",
    "Number",
    "Or",
    "Predicate",
    "String",
    "Today",
    "equivalent",
    "format_expression",
    "identifiers",
    "normalise",
    "parse_expression",
    "walk",
]

# The functions taking one identifier.
PREDICATES = ("answered", "missing", "empty", "refused")


# ---- The tree -----------------------------------------------------------------


@dataclass(frozen=True)
class Number:
    """A number. ``Number(Decimal("3")) == Number(Decimal("3.0"))``."""

    value: Decimal


@dataclass(frozen=True)
class String:
    """A string."""

    value: str


@dataclass(frozen=True)
class Date:
    """An ISO date (``2024-05-31``)."""

    value: datetime.date


@dataclass(frozen=True)
class Identifier:
    """A question or variable, by its spec identifier."""

    name: str


@dataclass(frozen=True)
class Today:
    """``today()``: the date of the interview."""


@dataclass(frozen=True)
class Predicate:
    """``answered(x)``, ``missing(x)``, ``empty(x)`` or ``refused(x)``."""

    name: str
    subject: Identifier


@dataclass(frozen=True)
class Negate:
    """``-x`` for an operand that is not a number literal."""

    operand: Expression


@dataclass(frozen=True)
class Arithmetic:
    """``left + right``, ``-``, ``*`` or ``/``."""

    operator: str
    left: Expression
    right: Expression


@dataclass(frozen=True)
class Comparison:
    """``left operator right``: ``=``, ``!=``, ``<``, ``<=``, ``>`` or ``>=``."""

    operator: str
    left: Expression
    right: Expression


@dataclass(frozen=True)
class Not:
    """``not operand``."""

    operand: Expression


@dataclass(frozen=True)
class And:
    """All of ``operands`` (two or more)."""

    operands: tuple[Expression, ...]


@dataclass(frozen=True)
class Or:
    """Any of ``operands`` (two or more)."""

    operands: tuple[Expression, ...]


Expression: TypeAlias = (
    Number
    | String
    | Date
    | Identifier
    | Today
    | Predicate
    | Negate
    | Arithmetic
    | Comparison
    | Not
    | And
    | Or
)
Literal: TypeAlias = Number | String | Date | Today
_LITERALS = (Number, String, Date, Today)


class ExpressionError(ValueError):
    """An expression that does not parse.

    Attributes:
        text: The expression.
        column: Where the problem is, counted from 1.
        reason: What the problem is, without the position.
    """

    def __init__(self, reason: str, text: str, column: int) -> None:
        self.reason = reason
        self.text = text
        self.column = column
        caret = " " * (column - 1) + "^"
        super().__init__(f"{reason} (column {column})\n  {text}\n  {caret}")


# ---- Tokens -------------------------------------------------------------------


@dataclass(frozen=True)
class _Token:
    kind: str  # number, string, date, name, keyword, op, end
    text: str
    column: int
    value: object = None


@dataclass(frozen=True)
class _Syntax:
    """What a dialect writes differently: the spec's own, or native code's.

    ``keywords`` pairs a pattern with the predicate it stands for when
    compared with ``=`` (``x = EMPTY``), or with ``"today"``. ``date``
    matches a date written as a function, with groups named ``year``,
    ``month`` and ``day``.
    """

    comparisons: dict[str, str]
    functions: frozenset[str]
    braced_names: bool = False
    keywords: tuple[tuple[re.Pattern[str], str], ...] = ()
    date: re.Pattern[str] | None = None
    iso_dates: bool = True


SPEC_SYNTAX = _Syntax(
    comparisons={
        "=": "=",
        "==": "=",
        "!=": "!=",
        "<": "<",
        "<=": "<=",
        ">": ">",
        ">=": ">=",
    },
    functions=frozenset((*PREDICATES, "today")),
)

_SPACE = re.compile(r"\s+")
_ISO_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})(?![\w.])")
_NUMBER = re.compile(r"\d+(?:\.\d+)?(?![\w.])")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*")
_BRACED = re.compile(r"\{\{\s*([^{}\s]+)\s*\}\}")
# Longest first, so "<=" is not read as "<" then "=".
_OPERATORS: tuple[str, ...] = (
    *("&&", "||", "==", "!=", "<>", "<=", ">=", "<", ">", "="),
    *("+", "-", "*", "/", "(", ")", ","),
)
_WORDS = {"and": "and", "or": "or", "not": "not"}


def _tokens(text: str, syntax: _Syntax) -> list[_Token]:
    found: list[_Token] = []
    position = 0
    while position < len(text):
        space = _SPACE.match(text, position)
        if space:
            position = space.end()
            continue
        column = position + 1
        char = text[position]
        keyword = next(
            (
                (match, value)
                for pattern, value in syntax.keywords
                if (match := pattern.match(text, position))
            ),
            None,
        )
        if keyword is not None:
            match, word = keyword
            found.append(_Token("keyword", match.group(0), column, word))
            position = match.end()
            continue
        if syntax.date is not None:
            match = syntax.date.match(text, position)
            if match:
                parts = match.group("year", "month", "day")
                value = _date(text, column, *parts)
                found.append(_Token("date", match.group(0), column, value))
                position = match.end()
                continue
        if syntax.iso_dates:
            match = _ISO_DATE.match(text, position)
            if match:
                value = _date(text, column, *match.groups())
                found.append(_Token("date", match.group(0), column, value))
                position = match.end()
                continue
        if char.isdigit():
            match = _NUMBER.match(text, position)
            if match is None:
                raise ExpressionError("This is not a number", text, column)
            found.append(_Token("number", match.group(0), column))
            position = match.end()
            continue
        if char in "\"'":
            string, end = _string(text, position)
            found.append(_Token("string", text[position:end], column, string))
            position = end
            continue
        if syntax.braced_names and text.startswith("{{", position):
            match = _BRACED.match(text, position)
            if match is None:
                raise ExpressionError("This {{name}} is not closed", text, column)
            found.append(_Token("name", match.group(0), column, match.group(1)))
            position = match.end()
            continue
        match = _NAME.match(text, position)
        if match:
            word = match.group(0)
            if word.lower() in _WORDS:
                found.append(_Token("keyword", word, column, _WORDS[word.lower()]))
            else:
                found.append(_Token("name", word, column, word))
            position = match.end()
            continue
        operator = next(
            (op for op in _OPERATORS if text.startswith(op, position)), None
        )
        if operator is None or (operator == "<>" and "<>" not in syntax.comparisons):
            if operator == "<>":
                raise ExpressionError("Write != for not equal", text, column)
            raise ExpressionError(f"Unexpected character {char!r}", text, column)
        found.append(_Token("op", operator, column))
        position += len(operator)
    found.append(_Token("end", "", len(text) + 1))
    return found


def _date(text: str, column: int, year: str, month: str, day: str) -> datetime.date:
    try:
        return datetime.date(int(year), int(month), int(day))
    except ValueError:
        raise ExpressionError("This is not a valid date", text, column) from None


def _string(text: str, start: int) -> tuple[str, int]:
    quote = text[start]
    parts: list[str] = []
    position = start + 1
    while True:
        end = text.find(quote, position)
        if end < 0:
            raise ExpressionError("This string is not closed", text, start + 1)
        parts.append(text[position:end])
        if text.startswith(quote, end + 1):
            parts.append(quote)
            position = end + 2
            continue
        return "".join(parts), end + 1


# ---- Parsing ------------------------------------------------------------------


@dataclass(frozen=True)
class _Keyword:
    """A native keyword (``EMPTY``) waiting for the comparison it is part of."""

    predicate: str


_Node: TypeAlias = Expression | _Keyword


# Deeper than this, a parse would exhaust Python's recursion limit.
_MAX_NESTING = 50


class _Parser:
    def __init__(self, text: str, syntax: _Syntax) -> None:
        self.text = text
        self.syntax = syntax
        self.tokens = _tokens(text, syntax)
        self.index = 0
        self.depth = 0

    def nest(self) -> None:
        """Count one more level of parentheses, ``not`` or minus."""
        self.depth += 1
        if self.depth > _MAX_NESTING:
            raise self.error(
                f"The expression is nested too deeply (more than {_MAX_NESTING} "
                "levels of parentheses, not or minus)"
            )

    @property
    def token(self) -> _Token:
        return self.tokens[self.index]

    def advance(self) -> _Token:
        token = self.tokens[self.index]
        self.index += 1
        return token

    def error(self, reason: str, token: _Token | None = None) -> ExpressionError:
        return ExpressionError(reason, self.text, (token or self.token).column)

    def is_keyword(self, *values: str) -> bool:
        return self.token.kind == "keyword" and self.token.value in values

    def is_op(self, *values: str) -> bool:
        return self.token.kind == "op" and self.token.text in values

    def parse(self) -> Expression:
        if self.token.kind == "end":
            raise self.error("The expression is empty")
        node = self.or_expression()
        if self.token.kind != "end":
            raise self.error(f"Unexpected {self.describe(self.token)}")
        return node

    def describe(self, token: _Token) -> str:
        return "end of the expression" if token.kind == "end" else repr(token.text)

    def or_expression(self) -> Expression:
        operands = [self.and_expression()]
        while self.is_keyword("or") or self.is_op("||"):
            self.advance()
            operands.append(self.and_expression())
        return operands[0] if len(operands) == 1 else Or(tuple(operands))

    def and_expression(self) -> Expression:
        operands = [self.not_expression()]
        while self.is_keyword("and") or self.is_op("&&"):
            self.advance()
            operands.append(self.not_expression())
        return operands[0] if len(operands) == 1 else And(tuple(operands))

    def not_expression(self) -> Expression:
        if self.is_keyword("not"):
            self.advance()
            self.nest()
            node = Not(self.not_expression())
            self.depth -= 1
            return node
        return self.comparison()

    def comparison(self) -> Expression:
        start = self.token
        left = self.additive()
        if not (self.token.kind == "op" and self.token.text in self.syntax.comparisons):
            return self.operand(left, start)
        operator_token = self.advance()
        operator = self.syntax.comparisons[operator_token.text]
        right_start = self.token
        right = self.additive()
        if self.token.kind == "op" and self.token.text in self.syntax.comparisons:
            raise self.error("Comparisons do not chain: join them with 'and'")
        return self.keyword_comparison(left, operator, right, start, right_start)

    def keyword_comparison(
        self,
        left: _Node,
        operator: str,
        right: _Node,
        start: _Token,
        right_start: _Token,
    ) -> Expression:
        """``x = EMPTY`` in native code: a predicate."""
        if isinstance(left, _Keyword):
            left, right, start, right_start = right, left, right_start, start
        if not isinstance(right, _Keyword):
            return Comparison(
                operator, self.operand(left, start), self.operand(right, right_start)
            )
        if operator not in ("=", "!="):
            raise self.error(f"Compare {right_start.text} with = or <>", right_start)
        if not isinstance(left, Identifier):
            raise self.error(f"{right_start.text} is compared with a name", start)
        predicate = Predicate(right.predicate, left)
        return predicate if operator == "=" else Not(predicate)

    def operand(self, node: _Node, token: _Token) -> Expression:
        """``node``, which must not be a keyword standing alone."""
        if isinstance(node, _Keyword):
            raise self.error(f"{token.text} is compared with a name", token)
        return node

    def additive(self) -> _Node:
        start = self.token
        node = self.term()
        while self.is_op("+", "-"):
            operator = self.advance().text
            right_start = self.token
            right = self.operand(self.term(), right_start)
            node = Arithmetic(operator, self.operand(node, start), right)
        return node

    def term(self) -> _Node:
        start = self.token
        node = self.unary()
        while self.is_op("*", "/"):
            operator = self.advance().text
            right_start = self.token
            right = self.operand(self.unary(), right_start)
            node = Arithmetic(operator, self.operand(node, start), right)
        return node

    def unary(self) -> _Node:
        if self.is_op("-"):
            self.advance()
            start = self.token
            self.nest()
            operand = self.operand(self.unary(), start)
            self.depth -= 1
            if isinstance(operand, Number):
                # copy_negate, not unary minus: that rounds to the context.
                return Number(operand.value.copy_negate())
            return Negate(operand)
        return self.primary()

    def primary(self) -> _Node:
        token = self.token
        if token.kind == "number":
            self.advance()
            return Number(Decimal(token.text))
        if token.kind == "string":
            self.advance()
            return String(str(token.value))
        if token.kind == "date":
            self.advance()
            assert isinstance(token.value, datetime.date)
            return Date(token.value)
        if self.is_op("("):
            self.advance()
            self.nest()
            node = self.or_expression()
            if not self.is_op(")"):
                raise self.error(f"Expected ')', found {self.describe(self.token)}")
            self.advance()
            self.depth -= 1
            return node
        if token.kind == "keyword" and token.value not in _WORDS.values():
            self.advance()
            if token.value == "today":
                return Today()
            return _Keyword(str(token.value))
        if token.kind == "name":
            self.advance()
            if self.is_op("("):
                return self.call(token)
            return Identifier(str(token.value))
        raise self.error(f"Expected a value, found {self.describe(token)}")

    def call(self, name: _Token) -> Expression:
        function = name.text.lower()
        if name.text.startswith("{{") or function not in self.syntax.functions:
            raise self.error(f"Unknown function {name.text!r}", name)
        self.advance()  # (
        if function == "today":
            if not self.is_op(")"):
                raise self.error("today() takes no argument")
            self.advance()
            return Today()
        argument = self.token
        if argument.kind != "name":
            raise self.error(f"{function}() takes the name of a question")
        self.advance()
        if not self.is_op(")"):
            raise self.error(f"{function}() takes one name, then ')'")
        self.advance()
        return Predicate(function, Identifier(str(argument.value)))


def parse_expression(text: str) -> Expression:
    """Parse ``text`` into an expression tree.

    Raises:
        ExpressionError: If ``text`` is not a valid expression; its message
            points at the column.
    """
    return _parse(text, SPEC_SYNTAX)


def _parse(text: str, syntax: _Syntax) -> Expression:
    return _Parser(text, syntax).parse()


# ---- Writing --------------------------------------------------------------------

_PRECEDENCE = {Or: 1, And: 2, Not: 3, Comparison: 4, Negate: 7}
_ARITHMETIC = {"+": 5, "-": 5, "*": 6, "/": 6}


def _precedence(node: Expression) -> int:
    if isinstance(node, Arithmetic):
        return _ARITHMETIC[node.operator]
    if isinstance(node, Number) and node.value < 0:
        return 7
    return _PRECEDENCE.get(type(node), 8)


def _exact(value: Decimal) -> Decimal:
    """``value`` without trailing zeros, every digit kept.

    ``Decimal.normalize`` rounds to the context's precision (28 digits): a
    longer number would come out as a different one.
    """
    if not value:
        return Decimal(0)
    with localcontext() as context:
        context.prec = max(context.prec, len(value.as_tuple().digits))
        return value.normalize()


def format_number(value: Decimal) -> str:
    """``value`` as the expression language writes it: ``3``, ``2.5``, ``-1``."""
    if value == value.to_integral_value():
        return str(int(value))
    return format(_exact(value), "f")


def format_expression(node: Expression) -> str:
    """``node`` as text, with only the parentheses its structure needs.

    ``parse_expression(format_expression(node)) == node`` for any tree the
    parser builds.
    """
    return _format(node, SPEC_WRITER)


class _Writer:
    """How a dialect writes each part; `ddi_l.spec.compile` adds Blaise."""

    and_word = "and"
    or_word = "or"
    not_word = "not"
    not_equal = "!="

    def name(self, name: str) -> str:
        return name

    def string(self, value: str) -> str:
        return '"' + value.replace('"', '""') + '"'

    def date(self, value: datetime.date) -> str:
        return value.isoformat()

    def predicate(self, name: str, subject: str) -> str:
        return f"{name}({subject})"

    def today(self) -> str:
        return "today()"

    def parenthesise(self, child: Expression, minimum: int) -> bool:
        """Whether ``child`` needs parentheses where ``minimum`` binds."""
        return _precedence(child) < minimum


SPEC_WRITER = _Writer()


def _format(node: Expression, writer: _Writer) -> str:
    def wrap(child: Expression, minimum: int) -> str:
        text = _format(child, writer)
        return f"({text})" if writer.parenthesise(child, minimum) else text

    if isinstance(node, Number):
        return format_number(node.value)
    if isinstance(node, String):
        return writer.string(node.value)
    if isinstance(node, Date):
        return writer.date(node.value)
    if isinstance(node, Identifier):
        return writer.name(node.name)
    if isinstance(node, Today):
        return writer.today()
    if isinstance(node, Predicate):
        return writer.predicate(node.name, writer.name(node.subject.name))
    if isinstance(node, Negate):
        return "-" + wrap(node.operand, 8)
    if isinstance(node, Arithmetic):
        own = _ARITHMETIC[node.operator]
        return f"{wrap(node.left, own)} {node.operator} {wrap(node.right, own + 1)}"
    if isinstance(node, Comparison):
        operator = writer.not_equal if node.operator == "!=" else node.operator
        return f"{wrap(node.left, 5)} {operator} {wrap(node.right, 5)}"
    if isinstance(node, Not):
        return f"{writer.not_word} {wrap(node.operand, 3)}"
    if isinstance(node, And):
        return f" {writer.and_word} ".join(wrap(child, 3) for child in node.operands)
    if isinstance(node, Or):
        return f" {writer.or_word} ".join(wrap(child, 2) for child in node.operands)
    raise TypeError(f"Not an expression: {node!r}")


# ---- Reading a tree -------------------------------------------------------------


def walk(node: Expression) -> Iterator[Expression]:
    """``node`` and every node under it, depth first."""
    yield node
    if isinstance(node, Predicate):
        yield node.subject
    elif isinstance(node, (Negate, Not)):
        yield from walk(node.operand)
    elif isinstance(node, (Arithmetic, Comparison)):
        yield from walk(node.left)
        yield from walk(node.right)
    elif isinstance(node, (And, Or)):
        for child in node.operands:
            yield from walk(child)


def identifiers(node: Expression) -> list[str]:
    """The names an expression uses, in order of first use."""
    return list(
        dict.fromkeys(item.name for item in walk(node) if isinstance(item, Identifier))
    )


# ---- Normal form ------------------------------------------------------------------

_MIRROR = {"=": "=", "!=": "!=", "<": ">", "<=": ">=", ">": "<", ">=": "<="}


def normalise(node: Expression) -> Expression:
    """Rewrite ``node`` into the canonical form `equivalent` compares.

    * ``missing(x)`` becomes ``empty(x) or refused(x)``, and ``answered(x)``
      becomes ``not empty(x) and not refused(x)``;
    * a literal compared with something else goes on the right
      (``3 < x`` becomes ``x > 3``), and two other operands are put in a
      fixed order;
    * ``not`` is pushed inward over ``and`` and ``or``, and ``not not x``
      becomes ``x``; a comparison under ``not`` is kept as it is, since
      ``not (x > 3)`` holds when ``x`` has no answer and ``x <= 3`` does not;
    * in an ``and``, ``not empty(x)`` and ``not refused(x)`` go when another
      part compares ``x``, since a comparison is false without an answer
      (``answered(x) and x > 3`` is ``x > 3``);
    * nested ``and`` (``or``) are flattened, repeats dropped and the
      operands sorted;
    * numbers compare by value (``3.0`` is ``3``).

    Arithmetic is left as written: nothing is calculated.
    """
    return _normal(node, negated=False, canonical=True)


def _normal(node: Expression, *, negated: bool, canonical: bool) -> Expression:
    """`normalise`; with ``canonical=False``, keep the written order.

    Without it, operands keep their order, two non-literal operands of a
    comparison are not swapped, and only exact repeats are dropped: the form a
    compiler wants, where the order is the author's.
    """
    if isinstance(node, Predicate):
        subject = node.subject
        if node.name in ("missing", "answered"):
            expanded = Or((Predicate("empty", subject), Predicate("refused", subject)))
            flip = node.name == "answered"
            return _normal(expanded, negated=negated != flip, canonical=canonical)
        return Not(node) if negated else node
    if isinstance(node, Not):
        return _normal(node.operand, negated=not negated, canonical=canonical)
    if isinstance(node, (And, Or)):
        # De Morgan: under a negation, and becomes or and the reverse.
        kind: type[And] | type[Or] = type(node)
        if negated:
            kind = Or if isinstance(node, And) else And
        children = [
            _normal(child, negated=negated, canonical=canonical)
            for child in node.operands
        ]
        return _junction(kind, children, canonical=canonical)
    leaf = _normal_leaf(node, canonical=canonical)
    return Not(leaf) if negated else leaf


def _junction(
    kind: type[And] | type[Or], children: list[Expression], *, canonical: bool
) -> Expression:
    flat: list[Expression] = []
    for child in children:
        if isinstance(child, kind):
            flat.extend(child.operands)
        else:
            flat.append(child)
    if kind is And:
        flat = _without_implied_answers(flat)
    unique: dict[str, Expression] = {}
    for child in flat:
        unique.setdefault(format_expression(child), child)
    keys = sorted(unique) if canonical else list(unique)
    if len(keys) == 1:
        return unique[keys[0]]
    return kind(tuple(unique[key] for key in keys))


def _answer_test(node: Expression) -> str | None:
    """The name ``node`` tests for an answer (``not empty(x)``, ``not refused(x)``)."""
    if (
        isinstance(node, Not)
        and isinstance(node.operand, Predicate)
        and node.operand.name in ("empty", "refused")
    ):
        return node.operand.subject.name
    return None


def _needs_answers(node: Expression) -> set[str]:
    """The names ``node`` is false without an answer for.

    A comparison is false when a question it compares has no answer; an
    ``and`` needs what any part needs, an ``or`` what every part needs.
    """
    if isinstance(node, Comparison):
        return {
            side.name
            for side in (node.left, node.right)
            if isinstance(side, Identifier)
        }
    if isinstance(node, And):
        return set().union(*(_needs_answers(child) for child in node.operands))
    if isinstance(node, Or):
        return set.intersection(*(_needs_answers(child) for child in node.operands))
    return set()


def _without_implied_answers(operands: list[Expression]) -> list[Expression]:
    """Drop the answer tests of an ``and`` that another part already implies."""
    implied: set[str] = set()
    for operand in operands:
        if _answer_test(operand) is None:
            implied |= _needs_answers(operand)
    return [operand for operand in operands if _answer_test(operand) not in implied]


def _normal_leaf(node: Expression, *, canonical: bool) -> Expression:
    if isinstance(node, Comparison):
        left = _normal_leaf(node.left, canonical=canonical)
        right = _normal_leaf(node.right, canonical=canonical)
        operator = node.operator
        left_literal = isinstance(left, _LITERALS)
        right_literal = isinstance(right, _LITERALS)
        swap = (left_literal and not right_literal) or (
            canonical
            and left_literal == right_literal
            and format_expression(left) > format_expression(right)
        )
        if swap:
            left, right, operator = right, left, _MIRROR[operator]
        return Comparison(operator, left, right)
    if isinstance(node, Arithmetic):
        return replace(
            node,
            left=_normal_leaf(node.left, canonical=canonical),
            right=_normal_leaf(node.right, canonical=canonical),
        )
    if isinstance(node, Negate):
        return Negate(_normal_leaf(node.operand, canonical=canonical))
    if isinstance(node, (Not, And, Or, Predicate)):
        # A boolean inside a comparison or arithmetic: normalise it as such.
        return _normal(node, negated=False, canonical=canonical)
    if isinstance(node, Number):
        return Number(_exact(node.value))
    return node


def equivalent(
    left: Expression | str,
    right: Expression | str,
    *,
    exact: bool | None = None,
    types: Mapping[str, str] | None = None,
) -> bool:
    """Whether two expressions hold for the same respondents.

    Two expressions with the same `normalise` form are. Others are decided
    by `ddi_l.spec.semantics.decide` when the ``logic`` extra is installed;
    without it, ``False`` means only that they are written differently in a
    way normalising does not undo, and they may still always agree (``x > 3``
    and ``x >= 4`` for whole numbers).

    Args:
        left: An expression, or its text.
        right: Another.
        exact: ``False`` compares normal forms only; ``True`` needs the
            ``logic`` extra; ``None`` uses it when it is installed.
        types: What some names are, for the solver (see `decide`).

    Raises:
        ExpressionError: If a string does not parse.
        LogicDependencyError: With ``exact=True`` and no ``logic`` extra.
    """
    if isinstance(left, str):
        left = parse_expression(left)
    if isinstance(right, str):
        right = parse_expression(right)
    if normalise(left) == normalise(right):
        return True
    if exact is False:
        return False
    from .semantics import decide, logic_available

    if exact is None and not logic_available():
        return False
    return decide(left, right, types=types).outcome == "equivalent"
