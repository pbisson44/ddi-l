"""Which constructs of a flow a respondent can reach: the ``logic`` extra.

A construct is asked when what leads to it is asked and the gate on the way,
if any, holds. Its ask-condition is the disjunction, over the ways to it, of
the gates' conjunction. Each construct reached from the root is one solver
variable, defined from the constructs leading to it, so a part of the flow
shared by many paths is encoded once, however many paths there are. In a
flow that loops back on itself, a construct only the loop would reach may
count as reached (nothing is reported for it), and no read is said to be
met by no respondent.

A gate's condition is read without a spec: a subject is named by the
parameter its bindings end at, a code by its value. A condition that cannot
be read (a data lookup, code in another language) is a fact of its own that
may hold or not, so the branches of one gate still exclude each other. A
loop's body counts as reached once.

Every respondent the solver finds is checked by walking the flow with
`ddi_l.spec.semantics.evaluate`; one that does not pass is not given.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .._etree import Element
from ..colectica_lint import _Context, _local
from ..colectica_logic import (
    Condition,
    ConditionFormatError,
    NativeCondition,
    _parse_urn,
    parse_condition,
)
from ._instrument import GateTerm, leads
from .compile import (
    BlaiseDialect,
    UnverifiableConditionError,
    comparable,
    condition_to_expression,
    parse_blaise,
)
from .conform import _renamed
from .expression import (
    Expression,
    ExpressionError,
    Identifier,
    Predicate,
    Today,
    identifiers,
    walk,
)
from .semantics import Example, _smt, _typing, _UnmodelledError, evaluate

__all__: list[str] = []

# What an opaque condition is named: no subject name starts with it.
_OPAQUE = "#"

_Edges = list[tuple[Element, GateTerm | None]]
# A way into a construct: the construct before it, the position among what
# that one leads to, and the gate.
_Way = tuple[Element, int, GateTerm | None]


class Routing:
    """One flow, from ``root``, as formulas over one respondent.

    Raises:
        LogicDependencyError: Without the ``logic`` extra.
    """

    def __init__(self, context: _Context, root: Element) -> None:
        smt = _smt()
        self.context = context
        self.root = root
        # What each construct reached leads to, and the constructs in walk
        # order (the root first), then each after every one leading to it.
        self._below: dict[int, _Edges] = {}
        self._order: list[Element] = []
        self._read_graph()
        self._cyclic = False
        self._settling = self._parents_first()
        self._ways: dict[int, list[_Way]] = {}
        for above in self._order:
            for position, (element, term) in enumerate(self._below[id(above)]):
                self._ways.setdefault(id(element), []).append((above, position, term))
        reader = _GateReader(context)
        # Each condition of each gate reached, read once.
        self._conditions: dict[int, list[Expression]] = {
            id(gate): reader.conditions(gate)
            for gate in self._order
            if _local(gate.tag) == "IfThenElse"
        }
        self._opaque_unmodelled()
        expressions = [e for found in self._conditions.values() for e in found]
        self.flow = smt.Flow(_typing(expressions, {}))
        self._formulas: dict[int, list[Any]] = {}
        self._reach: dict[int, Any] = {}
        self._undefined: dict[tuple[int, int], Any] = {}
        self._inside: dict[tuple[int, int], Any] = {}

    def _read_graph(self) -> None:
        """Read what each construct reached leads to, depth first."""
        seen = {id(self.root)}
        stack = [self.root]
        while stack:
            element = stack.pop()
            self._order.append(element)
            edges = [
                (target, term)
                for reference, term in leads(element)
                if (target := self.context.resolve(reference)) is not None
            ]
            self._below[id(element)] = edges
            for target, _ in reversed(edges):
                if id(target) not in seen:
                    seen.add(id(target))
                    stack.append(target)

    def _parents_first(self) -> list[Element]:
        """The constructs, each after every one leading to it but by a loop."""
        finished: list[Element] = []
        seen = {id(self.root)}
        open_ = {id(self.root)}
        stack = [(self.root, iter(self._below[id(self.root)]))]
        while stack:
            element, pending = stack[-1]
            step = next(pending, None)
            if step is None:
                stack.pop()
                open_.discard(id(element))
                finished.append(element)
            elif id(step[0]) in open_:
                self._cyclic = True
            elif id(step[0]) not in seen:
                seen.add(id(step[0]))
                open_.add(id(step[0]))
                stack.append((step[0], iter(self._below[id(step[0])])))
        return finished[::-1]

    def _opaque_unmodelled(self) -> None:
        """Make opaque each condition the solver cannot read with the others."""
        expressions = [e for found in self._conditions.values() for e in found]
        try:
            _typing(expressions, {})
            return
        except _UnmodelledError:
            pass
        kept: list[Expression] = []
        for gate, found in self._conditions.items():
            for number, expression in enumerate(found):
                try:
                    _typing([*kept, expression], {})
                except _UnmodelledError:
                    found[number] = _opaque(gate, number)
                else:
                    kept.append(expression)

    # ---- Formulas -----------------------------------------------------------------

    def _term(self, term: GateTerm | None) -> Any:
        flow = self.flow
        if term is None:
            return flow.true()
        conditions = self._formulas.get(id(term.gate))
        if conditions is None:
            conditions = self._formulas[id(term.gate)] = [
                flow.condition(c) for c in self._conditions[id(term.gate)]
            ]
        if term.branch == 0:
            return conditions[0]
        if term.branch > 0:
            before = [flow.negation(c) for c in conditions[: term.branch]]
            return flow.all_of([*before, conditions[term.branch]])
        return flow.negation(flow.any_of(conditions))

    def reached(self, element: Element) -> Any:
        """Whether a respondent reaches ``element``: its ask-condition."""
        if element is self.root:
            return self.flow.true()
        found = self._reach.get(id(element))
        if found is None:
            # The variable first: a loop leads back to it.
            found = self._reach[id(element)] = self.flow.variable()
            ways = [
                self.flow.all_of([self._term(term), self.reached(above)])
                for above, _, term in self._ways.get(id(element), ())
            ]
            self.flow.define(found, self.flow.any_of(ways))
        return found

    def _inside_of(self, element: Element, producer: Element) -> Any:
        """Whether ``producer`` is asked while ``element`` runs, once entered."""
        key = (id(element), id(producer))
        found = self._inside.get(key)
        if found is None:
            found = self._inside[key] = self.flow.variable()
            parts = [self.flow.true()] if element is producer else []
            parts += [
                self.flow.all_of([self._term(term), self._inside_of(below, producer)])
                for below, term in self._below[id(element)]
            ]
            self.flow.define(found, self.flow.any_of(parts))
        return found

    def _before(self, above: Element, position: int, producer: Element) -> list[Any]:
        """Whether ``producer`` ran in what ``above`` led to before ``position``.

        Nothing comes before a branch of a gate but the gate.
        """
        if _local(above.tag) == "IfThenElse":
            return []
        return [
            self.flow.all_of([self._term(term), self._inside_of(element, producer)])
            for element, term in self._below[id(above)][:position]
        ]

    def undefined(self, element: Element, producer: Element) -> Any:
        """Whether a respondent enters ``element`` before ``producer`` is asked."""
        if element is self.root:
            return self.flow.true()
        key = (id(element), id(producer))
        found = self._undefined.get(key)
        if found is None:
            flow = self.flow
            found = self._undefined[key] = flow.variable()
            ways = []
            for above, position, term in self._ways.get(id(element), ()):
                parts = [self._term(term), self.undefined(above, producer)]
                ran = self._before(above, position, producer)
                parts += [flow.negation(part) for part in ran]
                ways.append(flow.all_of(parts))
            flow.define(found, flow.any_of(ways))
        return found

    # ---- Questions ----------------------------------------------------------------

    def unreachable(self) -> list[Element]:
        """The constructs no respondent reaches, each the first on its way.

        A construct is reported when it is not reached but one leading to it
        is: the gate on that way rules it out. Constructs below it are not
        reported.

        The constructs are settled from the top: one is reached when a way
        with no gate leads to it from one that is, and is not when every way
        to it comes from one that is not. The solver settles the rest; each
        respondent it finds settles every construct they reach.
        """
        reached: set[int] = {id(self.root)}
        unreached: set[int] = set()
        for element in self._settling[1:]:
            if id(element) in reached:
                continue
            ways = self._ways.get(id(element), [])
            if any(term is None and id(above) in reached for above, _, term in ways):
                reached.add(id(element))
                continue
            if ways and all(id(above) in unreached for above, _, _ in ways):
                unreached.add(id(element))
                continue
            found = self.flow.example(self.reached(element))
            if found is False:
                unreached.add(id(element))
                continue
            # What the respondent found reaches is reached. Undecided, or not
            # reached by that respondent's walk: counted as reached all the
            # same, so nothing is reported for it.
            if isinstance(found, Example):
                reached.update(id(e) for e in self._walk(found, []))
            reached.add(id(element))
        return [
            element
            for element in self._order
            if id(element) in unreached
            and any(
                id(above) not in unreached for above, _, _ in self._ways[id(element)]
            )
        ]

    def respondent_before(
        self, reader: Element, producer: Element
    ) -> Example | bool | None:
        """A respondent who reaches ``reader`` before ``producer`` is asked.

        ``False`` if there is none. ``None`` if it cannot be decided, if the
        respondent found does not pass the check, if a condition this module
        cannot read decides their way, or if there is none but the flow
        loops. The respondent's answers are those the gates before
        ``reader`` read.
        """
        if id(reader) not in self._below or reader is self.root:
            return None
        found = self.flow.example(self.undefined(reader, producer))
        if found is False and self._cyclic:
            return None
        if not isinstance(found, Example):
            return found
        read: list[Expression] = []
        for element in self._walk(found, read):
            if element is producer:
                return None
            if element is reader:
                break
        else:
            return None
        names = {name for condition in read for name in identifiers(condition)}
        if any(name.startswith(_OPAQUE) for name in names):
            return None
        today = any(isinstance(n, Today) for c in read for n in walk(c))
        return Example(
            {name: answer for name, answer in found.answers.items() if name in names},
            found.today if today else None,
        )

    def _walk(self, example: Example, read: list[Expression]) -> Iterator[Element]:
        """The constructs ``example``'s interview reaches, in order.

        The conditions it reads on the way go to ``read``. A construct that
        leads back to one it is under is not followed again, and the walk
        stops at a condition `evaluate` cannot evaluate for them.
        """

        def taken(element: Element) -> Iterator[Element]:
            edges = self._below[id(element)]
            if _local(element.tag) != "IfThenElse":
                yield from (target for target, _ in edges)
                return
            branch = -1
            for number, condition in enumerate(self._conditions[id(element)]):
                read.append(condition)
                try:
                    holds = evaluate(condition, example.answers, example.today)
                except ValueError:
                    raise _UndecidedError from None
                if holds:
                    branch = number
                    break
            for target, term in edges:
                if term is not None and term.branch == branch:
                    yield target

        def visit(element: Element, path: frozenset[int]) -> Iterator[Element]:
            yield element
            for below in taken(element):
                if id(below) not in path:
                    yield from visit(below, path | {id(below)})

        try:
            for element in taken(self.root):
                yield from visit(element, frozenset({id(self.root), id(element)}))
        except _UndecidedError:
            return


class _UndecidedError(Exception):
    """A condition `evaluate` cannot evaluate for a respondent."""


def _opaque(gate: int, number: int) -> Expression:
    """A condition the solver reads as a fact of its own."""
    return Predicate("answered", Identifier(f"{_OPAQUE}{gate}.{number}"))


class _GateReader:
    """A gate's conditions as expressions, without a spec."""

    def __init__(self, context: _Context) -> None:
        self.context = context
        self.lookup = context.lookup()
        self._names: dict[tuple[str, str], str] = {}
        self._taken: set[str] = set()

    def conditions(self, gate: Element) -> list[Expression]:
        """The gate's own condition, then each ``ElseIf``'s."""
        holders = [gate] + [child for child in gate if _local(child.tag) == "ElseIf"]
        return [
            self._condition(holder, gate, number)
            for number, holder in enumerate(holders)
        ]

    def _condition(self, holder: Element, gate: Element, number: int) -> Expression:
        try:
            stored = parse_condition(holder)
        except ConditionFormatError:
            stored = None
        if isinstance(stored, Condition):
            try:
                return comparable(
                    condition_to_expression(
                        stored,
                        subject_name=lambda urn: self.subject(_parse_urn(urn)),
                        code_value=self.code_value,
                    )
                )
            except UnverifiableConditionError:
                pass
        elif isinstance(stored, NativeCondition) and stored.language.lower().startswith(
            "blaise"
        ):
            try:
                native = parse_blaise(stored.text, BlaiseDialect())
            except ExpressionError:
                pass
            else:
                aliases = {}
                for parameter in gate.findall(self.context.r("InParameter")):
                    alias = (parameter.findtext(self.context.r("Alias")) or "").strip()
                    name = self.subject(self._key(parameter))
                    if alias and name:
                        aliases[alias] = name
                return _renamed(native, lambda name: aliases.get(name, name))
        # A data lookup, code in another language or what does not read.
        return _opaque(id(gate), number)

    def _key(self, element: Element) -> tuple[str, str] | None:
        agency = element.findtext(self.context.r("Agency"))
        identifier = element.findtext(self.context.r("ID"))
        return (agency, identifier) if agency and identifier else None

    def subject(self, key: tuple[str, str] | None) -> str | None:
        """A name for the parameter the bindings from ``key`` end at.

        Its alias, made unique; else the start of its ID.
        """
        if key is None:
            return None
        seen = {key}
        while (source := self.lookup.bound_from.get(key)) is not None:
            if source in seen:
                break
            seen.add(source)
            key = source
        name = self._names.get(key)
        if name is None:
            parameter = self.lookup.items.get(key)
            alias = ""
            if parameter is not None:
                alias = (parameter.findtext(self.context.r("Alias")) or "").strip()
            base = alias or key[1][:8]
            name, count = base, 1
            while name in self._taken:
                count += 1
                name = f"{base} ({count})"
            self._taken.add(name)
            self._names[key] = name
        return name

    def code_value(self, urn: str) -> str | None:
        key = _parse_urn(urn)
        code = None if key is None else self.lookup.items.get(key)
        if code is None:
            return None
        value = code.findtext(self.context.r("Value"))
        return None if value is None else value.strip()
