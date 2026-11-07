"""Compile spec expressions into Colectica conditions, and read them back.

`compile_condition` turns a gate or an edit into what Colectica stores
in an ``r:Command``: a ``Neutral`` `Condition`
(the condition editor's JSON) when the expression fits it, else native
``Blaise`` code. `condition_to_expression` and `parse_blaise`
read either back into an expression, so a spec's gate can be compared with
the one an instrument holds.

``Neutral`` holds what Colectica's operator codes (`Operator`) can say:

================================================  ================================
Expression                                        Statement
================================================  ================================
``x = 3``, ``x != 3`` (``x`` has no codes)        ``Equal``, ``NotEqual`` 3
``x > 3``, ``x >= 3``, ``x < 3``, ``x <= 3``      ``GreaterThan``,
                                                  ``GreaterThanOrEqual``,
                                                  ``LessThan``,
                                                  ``LessThanOrEqual`` 3
``empty(x)``, ``not empty(x)``                    ``Empty``, ``NotEmpty``
``refused(x)``, ``not refused(x)``                ``Refused``, ``NotRefused``
``x = 2``, ``x = 2 or x = 3`` (``x`` coded)       ``ContainsAny`` the codes
``x = 2 and x = 3`` (``x`` coded)                 ``ContainsAll`` the codes
``x != 2``, ``x != 2 and x != 3`` (``x`` coded)   ``ContainsNone`` the codes
================================================  ================================

``answered(x)`` is ``not empty(x) and not refused(x)``, and ``missing(x)``
``empty(x) or refused(x)``. Statements are joined into one group by ``and``
or ``or``, or into groups joined by one ``and`` or ``or`` (``(a or b) and
c``). A choice among one coded question's codes is one statement wherever it
sits, so ``a and (x = 2 or x = 3) or b`` fits too. Anything else is compiled
to Blaise, and `CompiledCondition.fallback_reason` says why: a ``not``
in front of a comparison (``not (x = 3)`` holds when ``x`` has no answer,
and whether ``NotEqual`` does is not known),
arithmetic, dates or ``today()``, one question compared with another, or
``and`` and ``or`` mixed inside a group (in what order Colectica evaluates
them is not known).

Every comparison statement is read, as the expression language reads a
comparison, as false when the question has no answer. Whether Colectica
does is not known; it matters most for ``NotEqual`` and ``ContainsNone``.

Blaise writes inputs as ``{{name}}``, and ``empty``, ``refused``, today and
date literals with words this module does not assume: set them in a
`BlaiseDialect`. Without the word a condition needs, no condition is
compiled, and the reason names the setting.
"""

from __future__ import annotations

import datetime
import itertools
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from decimal import Decimal
from string import Formatter

from ..colectica_logic import (
    Condition,
    GroupBool,
    LogicGroup,
    NativeCondition,
    Operator,
    Statement,
    StmtBool,
)
from .expression import (
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
    _format,
    _normal,
    _parse,
    _Syntax,
    _Writer,
    format_expression,
    format_number,
    identifiers,
    normalise,
    parse_expression,
    walk,
)

__all__ = [
    "BlaiseDialect",
    "CompiledCondition",
    "UnverifiableConditionError",
    "comparable",
    "compile_condition",
    "condition_to_expression",
    "parse_blaise",
]

BLAISE = "Blaise"


class UnverifiableConditionError(ValueError):
    """A stored condition that cannot be read back into an expression."""


@dataclass(frozen=True)
class BlaiseDialect:
    """The Blaise words for what the expression language writes as functions.

    None has a default: the words depend on the Blaise version and the
    organisation's conventions. A spec sets them in its ``blaise:`` block.

    Attributes:
        empty: The value an unanswered question equals (``x = <empty>``).
        refused: The value a refused question equals.
        today: The expression for the interview date.
        date: How to write a date: a template with ``{year}``, ``{month}``
            and ``{day}``.
    """

    empty: str | None = None
    refused: str | None = None
    today: str | None = None
    date: str | None = None

    def __post_init__(self) -> None:
        if self.date is not None:
            _date_fields(self.date)


@dataclass(frozen=True)
class CompiledCondition:
    """What `compile_condition` made of an expression.

    Attributes:
        condition: A ``Neutral`` condition, a ``Blaise`` one, or ``None``
            when Blaise was needed and lacks a word (``missing_settings``).
        inputs: The names the condition uses, in order: the item needs an
            ``r:InParameter`` for each (its alias, for Blaise).
        fallback_reason: Why the condition is not ``Neutral``; ``None`` when
            it is.
        missing_settings: The `BlaiseDialect` settings the Blaise
            form needed and did not have.
        verified: Whether the condition, read back, holds for the same
            respondents as the expression: ``True``; ``False`` when it does
            not or does not read back; ``None`` when it was not checked or
            could not be decided (see `compile_condition`).
    """

    condition: Condition | NativeCondition | None
    inputs: tuple[str, ...]
    fallback_reason: str | None = None
    missing_settings: tuple[str, ...] = ()
    verified: bool | None = None


# ---- Neutral ----------------------------------------------------------------------


class _NotNeutralError(Exception):
    """Why an expression has no ``Neutral`` form."""


_COMPARISONS = {
    "=": Operator.EQUAL_TO,
    "!=": Operator.NOT_EQUAL,
    ">": Operator.GREATER_THAN,
    ">=": Operator.GREATER_THAN_OR_EQUAL,
    "<": Operator.LESS_THAN,
    "<=": Operator.LESS_THAN_OR_EQUAL,
}
_PREDICATE_OPERATORS = {"empty": Operator.EMPTY, "refused": Operator.REFUSED}
_NEGATED_PREDICATE_OPERATORS = {
    "empty": Operator.NOT_EMPTY,
    "refused": Operator.NOT_REFUSED,
}
# The statements that test for an answer and take no value.
_NO_VALUE = frozenset(
    (Operator.EMPTY, Operator.NOT_EMPTY, Operator.REFUSED, Operator.NOT_REFUSED)
)


@dataclass
class _Atom:
    subject: str
    operator: Operator
    value: str | None = None
    codes: list[str] | None = None


def _literal_text(node: Expression) -> str | None:
    if isinstance(node, Number):
        return format_number(node.value)
    if isinstance(node, String):
        return node.value
    return None


def _atom(node: Expression, codes: Mapping[str, Mapping[str, str]]) -> _Atom:
    """One statement, or why ``node`` is not one."""
    if isinstance(node, Predicate):
        return _Atom(node.subject.name, _PREDICATE_OPERATORS[node.name])
    if isinstance(node, Not):
        if isinstance(node.operand, Predicate):
            operand = node.operand
            return _Atom(
                operand.subject.name, _NEGATED_PREDICATE_OPERATORS[operand.name]
            )
        raise _NotNeutralError(
            f"'{format_expression(node)}' negates a comparison: it holds when the "
            "question has no answer, and whether NotEqual does "
            "is not known"
        )
    if not isinstance(node, Comparison):
        raise _NotNeutralError(f"'{format_expression(node)}' is not a comparison")
    text = format_expression(node)
    if any(isinstance(part, (Arithmetic, Negate)) for part in walk(node)):
        raise _NotNeutralError(f"'{text}' calculates, which Neutral cannot")
    if any(isinstance(part, (Date, Today)) for part in walk(node)):
        raise _NotNeutralError(f"'{text}' compares dates, which Neutral cannot")
    if not isinstance(node.left, Identifier):
        raise _NotNeutralError(f"'{text}' does not compare a question with a value")
    value = _literal_text(node.right)
    if value is None:
        raise _NotNeutralError(f"'{text}' compares two questions")
    subject = node.left.name
    operator = _COMPARISONS[node.operator]
    if node.operator not in ("=", "!="):
        if not isinstance(node.right, Number):
            raise _NotNeutralError(f"'{text}' compares text with {node.operator}")
        return _Atom(subject, operator, value=value)
    subject_codes = codes.get(subject)
    if subject_codes is None:
        return _Atom(subject, operator, value=value)
    if value not in subject_codes:
        raise ValueError(f"{subject} has no code {value!r}.")
    # A coded question's statements select codes, as Colectica's editor writes them.
    selects = Operator.CONTAINS_ANY if node.operator == "=" else Operator.CONTAINS_NONE
    return _Atom(subject, selects, codes=[subject_codes[value]])


def _check_codes(node: Expression, codes: Mapping[str, Mapping[str, str]]) -> None:
    """Raise if ``node`` compares a coded question with a code it lacks.

    Checked before any form is tried, so the error does not depend on where
    the comparison sits or on whether the condition ends up Blaise.
    """
    for part in walk(node):
        if (
            isinstance(part, Comparison)
            and part.operator in ("=", "!=")
            and isinstance(part.left, Identifier)
            and part.left.name in codes
        ):
            value = _literal_text(part.right)
            if value is not None and value not in codes[part.left.name]:
                raise ValueError(f"{part.left.name} has no code {value!r}.")


def _code_set(node: And | Or, codes: Mapping[str, Mapping[str, str]]) -> _Atom | None:
    """``x = 2 or x = 3`` (``x`` coded) as one statement, else ``None``.

    One ``ContainsAny`` (for ``and``, ``ContainsAll``; for ``x != 2 and x !=
    3``, ``ContainsNone``) statement says the whole choice and reads back as
    the same ``or`` (``and``) whatever group it sits in, so the choice can sit
    in a group joined the other way.
    """
    names: set[str] = set()
    symbols: set[str] = set()
    for part in node.operands:
        if not (
            isinstance(part, Comparison)
            and part.operator in ("=", "!=")
            and isinstance(part.left, Identifier)
            and _literal_text(part.right) is not None
        ):
            return None
        names.add(part.left.name)
        symbols.add(part.operator)
    if len(names) != 1 or names.pop() not in codes or len(symbols) != 1:
        return None
    if symbols == {"!="}:
        if isinstance(node, Or):
            return None  # x != 2 or x != 3: no one statement says it.
        operator = Operator.CONTAINS_NONE
    else:
        operator = (
            Operator.CONTAINS_ANY if isinstance(node, Or) else Operator.CONTAINS_ALL
        )
    atoms = [_atom(part, codes) for part in node.operands]
    return _Atom(
        atoms[0].subject,
        operator,
        codes=[code for atom in atoms for code in atom.codes or ()],
    )


def _group(
    nodes: tuple[Expression, ...],
    joined_by: type[And] | type[Or],
    codes: Mapping[str, Mapping[str, str]],
) -> list[_Atom]:
    """The statements of one group, merging the codes of one coded question.

    ``x = 2`` and ``x = 3`` merge into one statement (``ContainsAny`` in an
    ``or`` group, ``ContainsAll`` in an ``and`` one); ``x != 2`` and ``x !=
    3`` into one ``ContainsNone``, in an ``and`` group only.
    """
    atoms: list[_Atom] = []
    merged: dict[tuple[str, bool], _Atom] = {}
    for node in nodes:
        if isinstance(node, (And, Or)):
            choice = _code_set(node, codes)
            if choice is None:
                raise _NotNeutralError(
                    "and and or are mixed inside a group, and in what order "
                    "Colectica evaluates them is not known"
                )
            # Kept apart: merged with x = 4 beside it, it would say all of them.
            atoms.append(choice)
            continue
        atom = _atom(node, codes)
        excludes = atom.operator is Operator.CONTAINS_NONE
        if atom.codes is not None and (joined_by is And or not excludes):
            key = (atom.subject, excludes)
            if key in merged:
                merged[key].codes.extend(atom.codes)  # type: ignore[union-attr]
                continue
            merged[key] = atom
        atoms.append(atom)
    for (_, excludes), atom in merged.items():
        if joined_by is And and not excludes and len(atom.codes or ()) > 1:
            atom.operator = Operator.CONTAINS_ALL
    return atoms


def _statements(
    atoms: list[_Atom], joined_by: StmtBool, subjects: Mapping[str, str]
) -> list[Statement]:
    statements = []
    for position, atom in enumerate(atoms):
        if atom.subject not in subjects:
            raise ValueError(f"No subject for {atom.subject}.")
        no_value = atom.operator in _NO_VALUE
        statements.append(
            Statement(
                stmt_bool=StmtBool.FIRST if position == 0 else joined_by,
                subject=subjects[atom.subject],
                operator=atom.operator,
                value=atom.value,
                value_not_needed=no_value,
                selected_codes=list(atom.codes or ()),
            )
        )
    return statements


def _bool(kind: type[And] | type[Or]) -> StmtBool:
    return StmtBool.AND if kind is And else StmtBool.OR


def _groups(
    node: Expression, codes: Mapping[str, Mapping[str, str]]
) -> tuple[list[list[_Atom]], list[StmtBool], GroupBool]:
    """Each group's statements and joins, and how the groups join.

    ``node`` is in the normal form that keeps the written order.
    """
    if not isinstance(node, (And, Or)):
        return [[_atom(node, codes)]], [StmtBool.FIRST], GroupBool.FIRST
    kind = type(node)
    if not any(isinstance(child, (And, Or)) for child in node.operands):
        return [_group(node.operands, kind, codes)], [_bool(kind)], GroupBool.FIRST
    inner: type[And] | type[Or] = Or if kind is And else And
    groups: list[list[_Atom]] = []
    joins: list[StmtBool] = []
    run: list[Expression] = []
    for child in [*node.operands, None]:
        if child is not None and not isinstance(child, inner):
            run.append(child)
            continue
        if run:
            groups.append(_group(tuple(run), kind, codes))
            joins.append(_bool(kind))
            run = []
        if child is not None:
            groups.append(_group(child.operands, inner, codes))
            joins.append(_bool(inner))
    return groups, joins, GroupBool.AND if kind is And else GroupBool.OR


def _neutral(
    node: Expression,
    subjects: Mapping[str, str],
    codes: Mapping[str, Mapping[str, str]],
    synopsis: str,
) -> Condition:
    groups, joins, joined_by = _groups(node, codes)
    return Condition(
        logic_groups=[
            LogicGroup(
                group_bool=GroupBool.FIRST if index == 0 else joined_by,
                statements=_statements(atoms, join, subjects),
            )
            for index, (atoms, join) in enumerate(zip(groups, joins, strict=True))
        ],
        synopsis=synopsis,
        version=1,
    )


# ---- Blaise -----------------------------------------------------------------------


class _BlaiseWriter(_Writer):
    and_word = "AND"
    or_word = "OR"
    not_word = "NOT"
    not_equal = "<>"

    def __init__(self, dialect: BlaiseDialect) -> None:
        self.dialect = dialect
        self.missing: list[str] = []

    def setting(self, name: str) -> str:
        value = getattr(self.dialect, name)
        if value is None:
            if name not in self.missing:
                self.missing.append(name)
            return f"<{name}>"
        return str(value)

    def name(self, name: str) -> str:
        return "{{" + name + "}}"

    def date(self, value: datetime.date) -> str:
        template = self.setting("date")
        if self.dialect.date is None:
            return template
        return template.format(year=value.year, month=value.month, day=value.day)

    def predicate(self, name: str, subject: str) -> str:
        # Only empty and refused are left once answered and missing expand.
        return f"{subject} = {self.setting(name)}"

    def today(self) -> str:
        return self.setting("today")

    def parenthesise(self, child: Expression, minimum: int) -> bool:
        # Blaise's precedence may follow Pascal's, where = binds looser than
        # AND: put every comparison and junction inside parentheses.
        if isinstance(child, Predicate):
            return True
        if minimum <= 3:
            # NOT binds tightest in either reading, so it needs none.
            atoms = (Identifier, Number, String, Date, Today, Not)
            return not isinstance(child, atoms)
        return super().parenthesise(child, minimum)


def _blaise(node: Expression, dialect: BlaiseDialect) -> tuple[str, list[str]]:
    writer = _BlaiseWriter(dialect)
    return _format(node, writer), writer.missing


# ---- Compiling ----------------------------------------------------------------------


def compile_condition(
    expression: Expression | str,
    *,
    subjects: Mapping[str, str],
    codes: Mapping[str, Mapping[str, str]] | None = None,
    dialect: BlaiseDialect | None = None,
    validate: bool | None = None,
) -> CompiledCondition:
    """Compile a gate or edit condition for an ``r:Command``.

    The condition is read back (`condition_to_expression`, `parse_blaise`)
    and compared with the expression, so a fault in the compiler shows in
    `CompiledCondition.verified` rather than in an instrument.

    Args:
        expression: The expression, or its text.
        subjects: For each name the expression uses, the URN of the item's
            ``r:InParameter`` bound to it (a ``Neutral`` statement's
            ``Subject``).
        codes: For each coded question, its code values and their
            ``l:Code`` URNs (``{"PetKind": {"2": "urn:ddi:..."}}``): an
            equality on it selects codes.
        dialect: The Blaise words, for an expression ``Neutral`` cannot
            hold.
        validate: Whether to read the condition back and compare: ``None``
            compares normal forms, then decides with the ``logic`` extra
            when it is installed, and records the result; ``True`` also
            raises when the two differ, and needs the extra when normal
            forms do not settle it; ``False`` does not compare.

    Raises:
        ExpressionError: If the text does not parse.
        ValueError: If a name the ``Neutral`` form needs has no subject, or
            a coded question has no such code; with ``validate=True``, if the
            condition read back differs from the expression.
        LogicDependencyError: With ``validate=True``, when normal forms
            differ and the ``logic`` extra is not installed.
    """
    if isinstance(expression, str):
        expression = parse_expression(expression)
    compiled = _compiled(expression, subjects, codes or {}, dialect or BlaiseDialect())
    if validate is False or compiled.condition is None:
        return compiled
    verified, why = _verified(
        expression,
        compiled.condition,
        subjects,
        codes or {},
        dialect or BlaiseDialect(),
        exact=validate is True,
    )
    if verified is False and validate:
        raise ValueError(f"The compiled condition {why}.")
    return replace(compiled, verified=verified)


def _compiled(
    expression: Expression,
    subjects: Mapping[str, str],
    codes: Mapping[str, Mapping[str, str]],
    dialect: BlaiseDialect,
) -> CompiledCondition:
    names = tuple(identifiers(expression))
    prepared = _normal(expression, negated=False, canonical=False)
    _check_codes(prepared, codes)
    try:
        condition = _neutral(prepared, subjects, codes, format_expression(expression))
    except _NotNeutralError as reason:
        fallback = str(reason)
    else:
        return CompiledCondition(condition=condition, inputs=names)
    text, unset = _blaise(prepared, dialect)
    if unset:
        settings = " and ".join(f"blaise.{name}" for name in unset)
        verb = "is" if len(unset) == 1 else "are"
        return CompiledCondition(
            condition=None,
            inputs=names,
            fallback_reason=f"{fallback}; the Blaise form needs {settings}, "
            f"which {verb} not set",
            missing_settings=tuple(unset),
        )
    return CompiledCondition(
        condition=NativeCondition(text=text, language=BLAISE),
        inputs=names,
        fallback_reason=fallback,
    )


def _verified(
    expression: Expression,
    condition: Condition | NativeCondition,
    subjects: Mapping[str, str],
    codes: Mapping[str, Mapping[str, str]],
    dialect: BlaiseDialect,
    *,
    exact: bool,
) -> tuple[bool | None, str]:
    """Whether ``condition`` reads back as ``expression``, and if not, why.

    A ``Neutral`` condition stores ``"2"`` and ``2`` alike, so it is
    compared with `comparable` ``expression``. ``None`` when it cannot be
    decided, or needs the ``logic`` extra and ``exact`` is not set.
    """
    from .semantics import decide, logic_available

    used = {
        name: subjects[name] for name in identifiers(expression) if name in subjects
    }
    if isinstance(condition, NativeCondition):
        source = expression
        try:
            read = parse_blaise(condition.text, dialect)
        except ExpressionError as error:
            return False, f"does not read back: {error.reason}"
    else:
        if len(set(used.values())) < len(used):
            return None, ""  # two names share a subject: it cannot tell which
        source = comparable(expression)
        names = {urn: name for name, urn in used.items()}
        values = {
            urn: value for listed in codes.values() for value, urn in listed.items()
        }
        try:
            read = condition_to_expression(
                condition, subject_name=names.get, code_value=values.get
            )
        except UnverifiableConditionError as error:
            return False, f"does not read back: {error}"
    if normalise(read) == normalise(source):
        return True, ""
    if not exact and not logic_available():
        return None, ""
    verdict = decide(read, source, types={name: "code" for name in codes})
    if verdict.outcome == "equivalent":
        return True, ""
    if verdict.outcome == "unknown":
        return None, ""
    assert verdict.example is not None
    return False, (
        f"reads back as {format_expression(read)}, which differs from "
        f"{format_expression(source)} when {verdict.example.describe()}"
    )


# ---- Reading back -------------------------------------------------------------------


def _word(text: str) -> re.Pattern[str]:
    escaped = r"\s*".join(re.escape(part) for part in text.split())
    tail = r"(?![\w.])" if re.search(r"\w$", text) else ""
    return re.compile(escaped + tail, re.IGNORECASE)


_DATE_FIELDS = ("year", "month", "day")
_WIDTH = re.compile(r"0(\d+)d")


def _date_fields(template: str) -> list[tuple[str, str | None, int | None]]:
    """The literal before each field, the field and its width; raise if unusable.

    A template is usable when a date written with it reads back as that date
    and a number never reads as one: ``{year}``, ``{month}`` and ``{day}``
    each once and nothing else, text before the first field that does not
    end with a digit, something other than digits between two fields, no
    digit right after a field, and format specs only of the form ``0Nd`` (a
    width pads, so the value read can be wider).
    """
    try:
        pieces = list(Formatter().parse(template))
    except ValueError as exc:
        raise ValueError(
            f"The date template {template!r} is not a valid template: {exc}."
        ) from exc
    fields: list[tuple[str, str | None, int | None]] = []
    for literal, name, spec, conversion in pieces:
        if name is None:
            fields.append((literal, None, None))
            continue
        if name not in _DATE_FIELDS:
            raise ValueError(f"The date template names {{{name}}}.")
        if conversion:
            raise ValueError(
                f"The date template's format {{{name}!{conversion}}} is not 0Nd."
            )
        width = None
        if spec:
            match = _WIDTH.fullmatch(spec)
            if match is None:
                raise ValueError(
                    f"The date template's format {{{name}:{spec}}} is not 0Nd."
                )
            width = int(match.group(1))
        fields.append((literal, name, width))
    named = [name for _, name, _ in fields if name]
    if sorted(named) != sorted(_DATE_FIELDS):
        raise ValueError(
            "The date template needs {year}, {month} and {day}, each once."
        )
    first = fields[0][0]
    if not first.strip() or first.rstrip()[-1].isdigit():
        raise ValueError(
            "The date template needs text before its first field that does not "
            "end with a digit, so a number is never read as a date."
        )
    for (_, before, _), (literal, name, _) in itertools.pairwise(fields):
        if name and not re.search(r"\D", literal.strip() or "0"):
            raise ValueError(
                "The date template has nothing but digits between two fields."
            )
        if before and literal[:1].isdigit():
            raise ValueError(
                "The date template has a digit right after a field, which reads "
                "as part of it."
            )
    return fields


def _date_pattern(template: str) -> re.Pattern[str]:
    pattern = ""
    for literal, name, width in _date_fields(template):
        pattern += r"\s*".join(re.escape(part) for part in re.split(r"\s+", literal))
        if name:
            digits = rf"\d{{{width},}}" if width else r"\d{1,4}"
            pattern += rf"\s*(?P<{name}>{digits})(?!\d)\s*"
    return re.compile(pattern, re.IGNORECASE)


def _blaise_syntax(dialect: BlaiseDialect) -> _Syntax:
    keywords = tuple(
        (_word(text), name)
        for name, text in (
            ("empty", dialect.empty),
            ("refused", dialect.refused),
            ("today", dialect.today),
        )
        if text
    )
    return _Syntax(
        comparisons={
            "=": "=",
            "<>": "!=",
            "<": "<",
            "<=": "<=",
            ">": ">",
            ">=": ">=",
        },
        functions=frozenset(),
        braced_names=True,
        keywords=keywords,
        date=_date_pattern(dialect.date) if dialect.date else None,
        iso_dates=False,
    )


def parse_blaise(text: str, dialect: BlaiseDialect | None = None) -> Expression:
    """Read a ``Blaise`` condition back into an expression.

    Inputs are read from ``{{name}}`` and from bare names alike; ``x =
    <empty>`` and ``x = <refused>`` (with the dialect's words) become
    ``empty(x)`` and ``refused(x)``.

    Raises:
        ExpressionError: If the text is not one expression this reader knows
            (statements, functions and set membership are not read).
    """
    return _parse(text, _blaise_syntax(dialect or BlaiseDialect()))


_STORED_NUMBER = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?")


def comparable(expression: Expression) -> Expression:
    """``expression`` with every quoted plain number written as that number.

    A ``Neutral`` condition stores ``"2"`` and ``2`` alike, so a condition
    read back cannot tell them apart: compare a spec's expression and an
    instrument's through this. A string a number would not write the same
    way (``"01"``, ``"+3"``, ``" 3"``) stays a string.
    """
    if isinstance(expression, String):
        return _value(expression.value)
    if isinstance(expression, (And, Or)):
        return type(expression)(tuple(comparable(part) for part in expression.operands))
    if isinstance(expression, (Not, Negate)):
        return type(expression)(comparable(expression.operand))
    if isinstance(expression, (Comparison, Arithmetic)):
        return replace(
            expression,
            left=comparable(expression.left),
            right=comparable(expression.right),
        )
    return expression


def _value(text: str) -> Expression:
    """A stored value: a number when written as one, else text.

    A leading zero keeps a value text: ``"01"`` is a code, not ``1``.
    """
    if _STORED_NUMBER.fullmatch(text):
        return Number(Decimal(text))
    return String(text)


_SYMBOLS = {operator: symbol for symbol, operator in _COMPARISONS.items()}
_PREDICATES_READ = {
    Operator.EMPTY: ("empty", False),
    Operator.NOT_EMPTY: ("empty", True),
    Operator.REFUSED: ("refused", False),
    Operator.NOT_REFUSED: ("refused", True),
}
# How a statement that selects codes reads: each code compared with the
# symbol, joined by the junction; None where one code is all it can select.
_CODE_READINGS: dict[Operator, tuple[str, type[And] | type[Or] | None]] = {
    Operator.EQUAL_TO: ("=", Or),
    Operator.CONTAINS_ANY: ("=", Or),
    Operator.CONTAINS_ALL: ("=", And),
    Operator.CONTAINS_NONE: ("!=", And),
    Operator.CONTAINS: ("=", None),
    Operator.NOT_EQUAL: ("!=", None),
    Operator.DOES_NOT_CONTAIN: ("!=", None),
}


def _statement(
    statement: Statement,
    subject_name: Callable[[str], str | None],
    code_value: Callable[[str], str | None],
) -> Expression:
    operator = statement.operator
    if not operator.known:
        raise UnverifiableConditionError(f"operator code {int(operator)} is not known")
    if operator is Operator.NONE:
        raise UnverifiableConditionError("a statement has no operator (None)")
    if operator in (Operator.DONT_KNOW, Operator.NOT_DONT_KNOW):
        raise UnverifiableConditionError(
            f"{operator.name} tests for a don't-know answer, which the expression "
            "language has no word for"
        )
    name = subject_name(statement.subject)
    if name is None:
        raise UnverifiableConditionError(
            f"the subject {statement.subject} is bound to no known question"
        )
    subject = Identifier(name)
    if operator in _PREDICATES_READ:
        predicate, negated = _PREDICATES_READ[operator]
        test = Predicate(predicate, subject)
        return Not(test) if negated else test
    if statement.selected_codes:
        if operator not in _CODE_READINGS:
            raise UnverifiableConditionError(f"{operator.name} compares with codes")
        symbol, junction = _CODE_READINGS[operator]
        if junction is None and len(statement.selected_codes) > 1:
            raise UnverifiableConditionError(
                f"{operator.name} selects {len(statement.selected_codes)} codes, "
                "and how it reads several is not known"
            )
        values = []
        for urn in statement.selected_codes:
            value = code_value(urn)
            if value is None:
                raise UnverifiableConditionError(f"the code {urn} is not in the file")
            values.append(Comparison(symbol, subject, _value(value)))
        if len(values) == 1:
            return values[0]
        assert junction is not None
        return junction(tuple(values))
    if operator not in _SYMBOLS:
        raise UnverifiableConditionError(f"{operator.name} selects no code")
    if statement.value is None:
        raise UnverifiableConditionError(
            f"{operator.name} has no value to compare with"
        )
    return Comparison(_SYMBOLS[operator], subject, _value(statement.value))


def _uniform(
    values: list[StmtBool] | list[GroupBool], where: str
) -> type[And] | type[Or]:
    """How every value after the first joins: all by and, or all by or."""
    names = set()
    for value in values[1:]:
        if not value.known or value.name == "FIRST":
            raise UnverifiableConditionError(f"{where} joins with code {int(value)}")
        names.add(value.name)
    if len(names) > 1:
        raise UnverifiableConditionError(
            f"{where} mixes And and Or, and in what order Colectica evaluates "
            "them is not known"
        )
    return Or if names == {"OR"} else And


def _joined(kind: type[And] | type[Or], parts: list[Expression]) -> Expression:
    return parts[0] if len(parts) == 1 else kind(tuple(parts))


def condition_to_expression(
    condition: Condition,
    *,
    subject_name: Callable[[str], str | None],
    code_value: Callable[[str], str | None],
) -> Expression:
    """Read a ``Neutral`` condition back into an expression.

    Args:
        condition: The condition.
        subject_name: The spec name of the question a subject (an
            ``r:InParameter`` URN) is bound to, or ``None``.
        code_value: The value of a selected code (an ``l:Code`` URN), or
            ``None``.

    Raises:
        UnverifiableConditionError: For an operator or join code that is not
            known, ``and`` and ``or`` mixed in one group or across groups, a
            subject or code that cannot be resolved, or an empty condition.
    """
    groups = [group for group in condition.logic_groups if group.statements]
    if not groups:
        raise UnverifiableConditionError("the condition is empty")
    parts = []
    for number, group in enumerate(groups, 1):
        kind = _uniform([s.stmt_bool for s in group.statements], f"group {number}")
        statements = [
            _statement(statement, subject_name, code_value)
            for statement in group.statements
        ]
        parts.append(_joined(kind, statements))
    kind = _uniform([group.group_bool for group in groups], "the condition")
    return _joined(kind, parts)
