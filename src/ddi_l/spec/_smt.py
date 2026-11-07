"""Deciding two expressions with the Z3 solver: the ``logic`` extra.

Each name is three facts: whether its question is empty, whether it is
refused, and whether its answer has a value. The value is a number (a day
number for a date) or, for a name read by the literals it is compared with,
which of them it equals. A comparison holds when every name it reads has a
value and no divisor is zero, as `ddi_l.spec.semantics` says.

The solver looks for a respondent the two expressions disagree on. A
resource limit, not a clock, bounds its work, so a verdict is the same on
every run and every machine. Each pair is decided in a Z3 context of its
own: Z3 is thread-safe only across contexts, and Python may free a Z3 object
on any thread.
"""

from __future__ import annotations

import datetime
from fractions import Fraction

import z3

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
)
from .semantics import (
    ANSWERED,
    EMPTY,
    FIRST_DAY,
    LAST_DAY,
    OTHER,
    REFUSED,
    Answer,
    Example,
    Value,
    Verdict,
    _literal,
    _membership,
    _Typing,
    evaluate,
)

# The work the solver may do on one pair of expressions before it gives up.
RESOURCE_LIMIT = 5_000_000


class _Encoding:
    """Two expressions as Z3 formulas over one respondent."""

    def __init__(self, typing: _Typing) -> None:
        self.typing = typing
        self.context = z3.Context()
        self.facts: list[z3.BoolRef] = []
        # Each name's empty, refused and has-a-value facts.
        self.states: dict[str, tuple[z3.BoolRef, z3.BoolRef, z3.BoolRef]] = {}
        self.values: dict[str, z3.ArithRef] = {}
        self.atoms: dict[str, dict[Value, z3.BoolRef]] = {}
        self.today: z3.ArithRef | None = None

    def state(self, name: str) -> tuple[z3.BoolRef, z3.BoolRef, z3.BoolRef]:
        found = self.states.get(name)
        if found is not None:
            return found
        index = len(self.states)
        empty, refused, valued = z3.Bools(
            f"empty{index} refused{index} value{index}", self.context
        )
        self.facts.append(z3.Not(z3.And(empty, refused)))
        self.facts.append(z3.Implies(valued, z3.Not(z3.Or(empty, refused))))
        if name in self.typing.scalar:
            make = z3.Int if name in self.typing.integer else z3.Real
            value = self.values[name] = make(f"x{index}", self.context)
            if self.typing.types[name] == "date":
                self.facts.append(z3.And(value >= FIRST_DAY, value <= LAST_DAY))
        else:
            atoms = self.atoms[name] = {
                literal: z3.Bool(f"is{index}_{n}", self.context)
                for n, literal in enumerate(self.typing.literals.get(name, ()))
            }
            if name in self.typing.single and len(atoms) > 1:
                self.facts.append(z3.AtMost(*atoms.values(), 1))
        found = self.states[name] = (empty, refused, valued)
        return found

    def formula(self, node: Expression) -> z3.BoolRef:
        if isinstance(node, Predicate):
            empty, refused, _ = self.state(node.subject.name)
            return {
                "empty": empty,
                "refused": refused,
                "missing": z3.Or(empty, refused),
                "answered": z3.Not(z3.Or(empty, refused)),
            }[node.name]
        if isinstance(node, Not):
            return z3.Not(self.formula(node.operand))
        if isinstance(node, And):
            return z3.And(*(self.formula(child) for child in node.operands))
        if isinstance(node, Or):
            return z3.Or(*(self.formula(child) for child in node.operands))
        assert isinstance(node, Comparison)
        member = _membership(node)
        if member is not None and member[0] not in self.typing.scalar:
            name, literal = member
            _, _, valued = self.state(name)
            atom = self.atoms[name][_literal(literal)]
            return z3.And(valued, atom if node.operator == "=" else z3.Not(atom))
        guards: list[z3.BoolRef] = []
        left = self.term(node.left, guards)
        right = self.term(node.right, guards)
        if left is None or right is None:
            # Text literals only: names compared with text are read by them.
            return z3.BoolVal(evaluate(node, {}), self.context)
        left, right = _alike(left, right)
        relation = {
            "=": lambda: left == right,
            "!=": lambda: left != right,
            "<": lambda: left < right,
            "<=": lambda: left <= right,
            ">": lambda: left > right,
            ">=": lambda: left >= right,
        }[node.operator]()
        return z3.And(*guards, relation)

    def term(self, node: Expression, guards: list[z3.BoolRef]) -> z3.ArithRef | None:
        """A number or day-number term; ``None`` for text.

        Whole numbers stay integers until they meet a fraction or a
        division: Z3 decides integer and rational arithmetic quickly, and
        the two mixed much more slowly.
        """
        if isinstance(node, Number):
            value = Fraction(node.value)
            if value.denominator == 1:
                return z3.IntVal(value.numerator, self.context)
            return z3.Q(value.numerator, value.denominator, self.context)
        if isinstance(node, Date):
            return z3.IntVal(node.value.toordinal(), self.context)
        if isinstance(node, String):
            return None
        if isinstance(node, Today):
            if self.today is None:
                self.today = z3.Int("today", self.context)
                self.facts.append(
                    z3.And(self.today >= FIRST_DAY, self.today <= LAST_DAY)
                )
            return self.today
        if isinstance(node, Identifier):
            _, _, valued = self.state(node.name)
            guards.append(valued)
            return self.values[node.name]
        if isinstance(node, Negate):
            operand = self.term(node.operand, guards)
            assert operand is not None
            return -operand
        assert isinstance(node, Arithmetic)
        left = self.term(node.left, guards)
        right = self.term(node.right, guards)
        assert left is not None and right is not None
        if node.operator == "/":
            guards.append(right != 0)
            return _real(left) / _real(right)
        left, right = _alike(left, right)
        return {"+": left + right, "-": left - right, "*": left * right}[node.operator]

    def example(self, model: z3.ModelRef) -> Example | None:
        """The respondent ``model`` describes; ``None`` if a value is irrational."""

        def true(fact: z3.BoolRef) -> bool:
            return z3.is_true(model.eval(fact, model_completion=True))

        answers = {}
        for name, (empty, refused, valued) in self.states.items():
            if true(empty):
                answers[name] = Answer(EMPTY)
            elif true(refused):
                answers[name] = Answer(REFUSED)
            elif not true(valued):
                answers[name] = Answer(ANSWERED)
            elif name in self.values:
                number = _fraction(model.eval(self.values[name], model_completion=True))
                if number is None:
                    return None
                value: Value = number
                if self.typing.types[name] == "date":
                    value = datetime.date.fromordinal(int(number))
                answers[name] = Answer(ANSWERED, frozenset({value}))
            else:
                values = frozenset(
                    literal for literal, atom in self.atoms[name].items() if true(atom)
                )
                answers[name] = Answer(ANSWERED, values or frozenset({OTHER}))
        today = None
        if self.today is not None:
            day = _fraction(model.eval(self.today, model_completion=True))
            assert day is not None
            today = datetime.date.fromordinal(int(day))
        return Example(answers, today)


class Flow:
    """Formulas over one respondent, built up for a whole flow, and a solver.

    `ddi_l.spec._routing` names a formula for each construct it asks
    about, so what many ways to a construct share is encoded once.
    """

    def __init__(self, typing: _Typing) -> None:
        self.encoding = _Encoding(typing)
        self.context = self.encoding.context
        self.solver = z3.Solver(ctx=self.context)
        self._facts = 0
        self._named = 0
        self._model: z3.ModelRef | None = None

    def condition(self, expression: Expression) -> z3.BoolRef:
        return self.encoding.formula(expression)

    def true(self) -> z3.BoolRef:
        return z3.BoolVal(True, self.context)

    def all_of(self, parts: list[z3.BoolRef]) -> z3.BoolRef:
        return z3.And(*parts) if len(parts) != 1 else parts[0]

    def any_of(self, parts: list[z3.BoolRef]) -> z3.BoolRef:
        if not parts:
            return z3.BoolVal(False, self.context)
        return z3.Or(*parts) if len(parts) > 1 else parts[0]

    def negation(self, part: z3.BoolRef) -> z3.BoolRef:
        return z3.Not(part)

    def variable(self) -> z3.BoolRef:
        """A new variable, for `define` to give a meaning."""
        variable = z3.Bool(f"n{self._named}", self.context)
        self._named += 1
        return variable

    def define(self, variable: z3.BoolRef, formula: z3.BoolRef) -> None:
        """Make ``variable`` hold exactly when ``formula`` does."""
        self.solver.add(variable == formula)

    def check(self, goal: z3.BoolRef) -> bool | None:
        """Whether a respondent makes ``goal`` hold; ``None`` if undecided.

        After ``True``, `holds` reads that respondent.
        """
        facts = self.encoding.facts
        self.solver.add(*facts[self._facts :])
        self._facts = len(facts)
        # A limit on the work of this check alone, as `decide` has.
        self.solver.set("rlimit", RESOURCE_LIMIT)
        outcome = self.solver.check(goal)
        self._model = self.solver.model() if outcome == z3.sat else None
        if outcome == z3.unsat:
            return False
        return True if outcome == z3.sat else None

    def holds(self, formula: z3.BoolRef) -> bool:
        """Whether ``formula`` holds for the respondent the last check found."""
        assert self._model is not None
        return z3.is_true(self._model.eval(formula, model_completion=True))

    def example(self, goal: z3.BoolRef) -> Example | bool | None:
        """A respondent who makes ``goal`` hold.

        ``False`` if there is none; ``None`` if it is undecided or a value
        the respondent needs is irrational.
        """
        found = self.check(goal)
        if found is not True:
            return found
        assert self._model is not None
        return self.encoding.example(self._model)


def _real(term: z3.ArithRef) -> z3.ArithRef:
    return z3.ToReal(term) if z3.is_int(term) else term


def _alike(left: z3.ArithRef, right: z3.ArithRef) -> tuple[z3.ArithRef, z3.ArithRef]:
    """Both integers, or both rationals."""
    if z3.is_int(left) and z3.is_int(right):
        return left, right
    return _real(left), _real(right)


def _fraction(value: z3.ExprRef) -> Fraction | None:
    if z3.is_int_value(value):
        return Fraction(value.as_long())
    if z3.is_rational_value(value):
        return Fraction(value.numerator_as_long(), value.denominator_as_long())
    return None


def decide(left: Expression, right: Expression, typing: _Typing) -> Verdict:
    """`ddi_l.spec.semantics.decide` once the names are read."""
    encoding = _Encoding(typing)
    disagree = encoding.formula(left) != encoding.formula(right)
    solver = z3.Solver(ctx=encoding.context)
    solver.set("rlimit", RESOURCE_LIMIT)
    solver.add(*encoding.facts, disagree)
    outcome = solver.check()
    if outcome == z3.unsat:
        return Verdict("equivalent")
    # A respondent with one answer to each question, if they differ on one.
    several = [
        atoms
        for name, atoms in encoding.atoms.items()
        if name not in typing.single and len(atoms) > 1
    ]
    if outcome == z3.sat and several:
        solver.add(*(z3.AtMost(*atoms.values(), 1) for atoms in several))
        outcome = solver.check()
        if outcome == z3.unsat:
            return Verdict(
                "unknown",
                reason="they differ only for a question answered with several codes",
            )
    if outcome != z3.sat:
        return Verdict("unknown", reason="the solver gave up")
    example = encoding.example(solver.model())
    if example is None:
        return Verdict("unknown", reason="they differ only when a value is irrational")
    if evaluate(left, example.answers, example.today) == evaluate(
        right, example.answers, example.today
    ):
        # The solver and the evaluator read the expressions differently.
        return Verdict("unknown", reason="the respondent found does not separate them")
    return Verdict("different", example=example)
