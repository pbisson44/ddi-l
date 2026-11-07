"""Compare an instrument with a questionnaire spec.

`conform` finds the spec's modules, questions and statements in an
instrument, and reports what is missing, extra, misplaced or different: code
lists, response domains, languages, gates, edit checks and the variables a
data lookup supplies. Each finding carries a rule id (the list is in
`ddi_l.spec.RULES`), its severity, and the module and item it is about.

How each id is found is the spec's ``match`` block. The first place that
holds an id anywhere in the instrument is the one used, and an id found on
several constructs there is reported as ambiguous rather than guessed.

Gates are compared after normalising (`ddi_l.spec.normalise`), which
does not calculate: a gate stored as ``x >= 4`` where the spec says ``x >
3`` is reported as different. A stored gate that cannot be read back (an
operator code that is not known, ``and`` and ``or`` mixed in one group,
native code this reader does not know) is reported as unverifiable.

Where edit checks are stored is not known in general: by default each edit
is reported as not verifiable. With ``edits="strict"`` and the spec's
``match.edits``, they are looked for and compared.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from .._etree import Element
from .._facts import run_scope
from ..colectica_lint import _Context, _local, _texts
from ..colectica_logic import (
    Condition,
    ConditionFormatError,
    DataLookup,
    NativeCondition,
    _parse_urn,
    parse_condition,
)
from ..lint import LintFinding, LintTarget, _element_path, _language_range_matches
from ._instrument import GateTerm, InstrumentIndex, Node
from .compile import (
    UnverifiableConditionError,
    comparable,
    condition_to_expression,
    parse_blaise,
)
from .expression import (
    And,
    Arithmetic,
    Comparison,
    Expression,
    ExpressionError,
    Identifier,
    Negate,
    Not,
    Or,
    Predicate,
    format_expression,
    format_number,
    normalise,
)
from .model import DomainSpec, EditSpec, ModuleSpec, QuestionSpec, Spec
from .semantics import Verdict, decide, logic_available

__all__ = [
    "EDIT_MODES",
    "SEMANTICS",
    "ConformError",
    "ConformFinding",
    "ConformReport",
    "ModuleResult",
    "conform",
]

EDIT_MODES = ("off", "info", "strict")
# How gates and edits are compared (`conform`'s ``semantics``).
SEMANTICS = ("syntactic", "smt")
NOT_VERIFIABLE = "not verifiable (edit storage unknown)"

_DOMAIN_KINDS = {
    "CodeDomain": "code",
    "NumericDomain": "numeric",
    "TextDomain": "text",
    "DateTimeDomain": "date",
    # What a *DomainReference refers to.
    "ManagedNumericRepresentation": "numeric",
    "ManagedTextRepresentation": "text",
    "ManagedDateTimeRepresentation": "date",
}
_MIXED = "StructuredMixedResponseDomain"
_QUESTIONS = ("QuestionConstruct", "QuestionItem", "QuestionGrid", "QuestionBlock")


class ConformError(ValueError):
    """The comparison cannot run as asked: a module or mode that is not."""


@dataclass(frozen=True)
class ConformFinding(LintFinding):
    """A difference between an instrument and its spec.

    Attributes:
        module: The spec module it is about, if any.
        item: The spec question, statement, edit or variable, if any.
        expected: What the spec says, when there is a value to show.
        actual: What the instrument holds.
        example: For a gate or an edit that differs, a respondent the two
            disagree on, in words (``PetCount is 1``); only when the solver
            found one.
    """

    module: str | None = None
    item: str | None = None
    expected: str | None = None
    actual: str | None = None
    example: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        """Return a JSON-serialisable representation of the finding.

        ``example`` is there only when it is set.
        """
        found = {
            **super().as_dict(),
            "module": self.module,
            "item": self.item,
            "expected": self.expected,
            "actual": self.actual,
        }
        if self.example is not None:
            found["example"] = self.example
        return found


@dataclass(frozen=True)
class ModuleResult:
    """How one spec module fared.

    Attributes:
        id: The module's id.
        found: Whether the instrument has it.
        required: Whether the spec requires it.
        counts: Its findings by severity.
    """

    id: str
    found: bool
    required: bool
    counts: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "id": self.id,
            "found": self.found,
            "required": self.required,
            "findings": dict(self.counts),
        }


@dataclass
class ConformReport:
    """Everything `conform` found.

    Attributes:
        spec: The spec's name.
        instrument: The instrument compared (``Instrument 1234abcd (name)``),
            or ``None`` when none was found.
        edits: The edits mode the comparison ran with.
        findings: Every finding, in spec order.
        modules: Each spec module compared, and how it fared.
    """

    spec: str
    instrument: str | None
    edits: str
    findings: list[ConformFinding] = field(default_factory=list)
    modules: list[ModuleResult] = field(default_factory=list)

    @property
    def summary(self) -> dict[str, int]:
        """The findings by severity."""
        counts = Counter(finding.severity for finding in self.findings)
        return {severity: counts[severity] for severity in ("error", "warning", "info")}

    def failed(self, fail_severity: str = "error") -> bool:
        """Whether a finding is at least as severe as ``fail_severity``."""
        order = ("info", "warning", "error")
        threshold = order.index(fail_severity)
        return any(order.index(f.severity) >= threshold for f in self.findings)

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "spec": self.spec,
            "instrument": self.instrument,
            "edits": self.edits,
            "summary": self.summary,
            "modules": [module.as_dict() for module in self.modules],
            "findings": [finding.as_dict() for finding in self.findings],
        }


class _UnverifiableError(Exception):
    """Why a stored condition cannot be compared."""


def _sentence(reason: object) -> str:
    """``reason`` to go inside a sentence: without its final full stop."""
    return str(reason).rstrip().rstrip(".")


def _renamed(node: Expression, rename: Callable[[str], str]) -> Expression:
    if isinstance(node, Identifier):
        return Identifier(rename(node.name))
    if isinstance(node, Predicate):
        return Predicate(node.name, Identifier(rename(node.subject.name)))
    if isinstance(node, Not):
        return Not(_renamed(node.operand, rename))
    if isinstance(node, Negate):
        return Negate(_renamed(node.operand, rename))
    if isinstance(node, (Arithmetic, Comparison)):
        return type(node)(
            node.operator, _renamed(node.left, rename), _renamed(node.right, rename)
        )
    if isinstance(node, (And, Or)):
        return type(node)(tuple(_renamed(child, rename) for child in node.operands))
    return node


def _all_of(terms: list[Expression]) -> Expression | None:
    if not terms:
        return None
    return terms[0] if len(terms) == 1 else And(tuple(terms))


def _when(verdict: Verdict) -> str:
    """`` (they differ when ...)`` for a verdict with a respondent, else ``""``."""
    if verdict.example is None:
        return ""
    return f" (they differ when {verdict.example.describe()})"


def _example(verdict: Verdict) -> str | None:
    return None if verdict.example is None else verdict.example.describe()


def _types(spec: Spec) -> dict[str, str]:
    """What the spec says each name is, for the solver (`decide`'s ``types``)."""
    types = {}
    for question in spec.questions:
        domain = question.domain
        if domain is None:
            continue
        if domain.kind == "numeric":
            types[question.id] = "integer" if domain.decimals == 0 else "numeric"
        else:
            types[question.id] = domain.kind
    for variable in (*spec.imported_variables, *spec.derived_variables):
        if variable.type is not None:
            types[variable.name] = variable.type
    return types


def _shown(expression: Expression | None) -> str | None:
    return None if expression is None else format_expression(normalise(expression))


def _same_text(left: str, right: str) -> bool:
    return " ".join(left.split()) == " ".join(right.split())


def _decimal(text: str | None) -> Decimal | None:
    try:
        return None if text is None else Decimal(text.strip())
    except InvalidOperation:
        return None


class _Checker:
    def __init__(
        self,
        document: LintTarget,
        spec: Spec,
        *,
        modules: list[ModuleSpec],
        whole: bool,
        edits: str,
        instrument: str | None,
        exact: bool,
    ) -> None:
        self.document = document
        self.spec = spec
        self.selected = modules
        # The whole spec, not one module: then modules the spec does not list
        # and variables are checked too.
        self.whole = whole
        self.edits = edits
        self.instrument_name = instrument or spec.instrument
        self.context = _Context(document)
        self.lookup = self.context.lookup()
        self.findings: list[ConformFinding] = []
        self.index: InstrumentIndex | None = None
        self.variable_names = {
            variable.name
            for variable in (*spec.imported_variables, *spec.derived_variables)
        }
        self.spec_names = {question.id for question in spec.questions}
        self.spec_names |= self.variable_names
        # (agency, id) of each matched construct and its question: spec id.
        self.spec_id_of: dict[tuple[str, str], str] = {}
        # Every id the spec matches to a construct: a question in parts can
        # be several spec questions, one per part.
        self.spec_ids_of: dict[tuple[str, str], set[str]] = {}
        self.module_nodes: dict[str, Node] = {}
        # The candidate sequences of each module that matches several.
        self.ambiguous_modules: dict[str, list[Node]] = {}
        self.item_nodes: dict[str, Node] = {}
        # The module the spec lists each question and statement in.
        self.listed_in: dict[str, str] = {}
        # What the conditions read since the last reset were stored as: a
        # Neutral condition may have quoted its numbers (see same).
        self.neutral_read = self.native_read = False
        # Whether gates are decided with the solver, what the spec says each
        # name is, and each pair decided, by normal forms.
        self.exact = exact
        self.types = _types(spec)
        self.decided: dict[tuple[Expression, Expression], Verdict] = {}
        # Each gate term read: its condition or why it cannot be read, and
        # whether that read Neutral and native code.
        self.terms_read: dict[GateTerm, tuple[Expression | str, bool, bool]] = {}

    # ---- Reporting -------------------------------------------------------------------

    def report(
        self,
        rule_id: str,
        message: str,
        *,
        element: Element | None = None,
        module: str | None = None,
        item: str | None = None,
        expected: str | None = None,
        actual: str | None = None,
        example: str | None = None,
    ) -> None:
        self.findings.append(
            ConformFinding(
                rule_id=rule_id,
                message=message,
                severity=self.spec.severity(rule_id),
                location=None if element is None else _element_path(element),
                module=module,
                item=item,
                expected=expected,
                actual=actual,
                example=example,
            )
        )

    def describe(self, element: Element) -> str:
        return self.context.describe(element)

    # ---- The instrument --------------------------------------------------------------

    def find_instrument(self) -> Element | None:
        instruments = list(self.context.items_of_type("Instrument"))
        wanted = self.instrument_name
        if wanted is not None:
            instruments = [
                element
                for element in instruments
                if wanted in self._instrument_ids(element)
            ]
        if not instruments:
            named = f" named {wanted!r}" if wanted is not None else ""
            self.report(
                "spec.instrument.missing", f"The file has no instrument{named}."
            )
            return None
        if len(instruments) > 1:
            listed = ", ".join(self.describe(element) for element in instruments)
            self.report(
                "spec.instrument.ambiguous",
                f"{len(instruments)} instruments match: {listed}; name one with "
                "the spec's instrument or --instrument.",
                element=instruments[0],
            )
            return None
        return instruments[0]

    def _instrument_ids(self, element: Element) -> set[str]:
        found = {element.findtext(self.context.r("ID")) or ""}
        for child in element:
            if _local(child.tag) in ("InstrumentName", "Label", "UserID"):
                found.update(
                    (node.text or "").strip()
                    for node in child.iter()
                    if (node.text or "").strip()
                )
        return found

    # ---- Matching ------------------------------------------------------------------

    def match(
        self, wanted: str, nodes: list[Node], sources: Iterable[str]
    ) -> tuple[list[Node], str | None]:
        """The nodes the first source holding ``wanted`` gives, and that source."""
        assert self.index is not None
        for source in sources:
            hits: dict[int, Node] = {}
            for node in nodes:
                if wanted in self.index.ids(node.element, source):
                    hits.setdefault(id(node.element), node)
            if hits:
                return list(hits.values()), source
        return [], None

    def key(self, element: Element) -> tuple[str, str]:
        return (
            element.findtext(self.context.r("Agency")) or "",
            element.findtext(self.context.r("ID")) or "",
        )

    def module_of(self, node: Node) -> str | None:
        """The spec module whose sequence holds ``node``, innermost first."""
        for sequence in reversed(node.sequences):
            for module_id, module_node in self.module_nodes.items():
                if module_node.element is sequence:
                    return module_id
        return None

    # ---- Running --------------------------------------------------------------------

    def run(self) -> tuple[Element | None, list[ModuleResult]]:
        instrument = self.find_instrument()
        if instrument is None:
            return None, [
                ModuleResult(module.id, False, module.required, {})
                for module in self.selected
            ]
        self.index = InstrumentIndex(self.context, instrument)
        self.match_modules()
        self.match_items()
        for module in self.selected:
            self.check_module(module)
        if self.whole:
            self.check_extra_modules()
            self.check_variables()
        self.check_edits()
        results = []
        for module in self.selected:
            counts = Counter(
                finding.severity
                for finding in self.findings
                if finding.module == module.id
            )
            results.append(
                ModuleResult(
                    module.id,
                    module.id in self.module_nodes,
                    module.required,
                    {
                        severity: counts[severity]
                        for severity in ("error", "warning", "info")
                    },
                )
            )
        return instrument, results

    def match_modules(self) -> None:
        assert self.index is not None
        candidates = [node for node in self.index.nodes if node.is_page_or_module]
        depth = self.spec.match.module_depth
        if depth is not None:
            candidates = [node for node in candidates if node.depth == depth]
        selected = {module.id for module in self.selected}
        for module in self.spec.modules:
            hits, _ = self.match(module.id, candidates, self.spec.match.module_id)
            if len(hits) == 1:
                self.module_nodes[module.id] = hits[0]
            elif hits:
                # Recorded even when not checked: what is inside cannot be
                # placed by the modules that are.
                self.ambiguous_modules[module.id] = hits
                if module.id not in selected:
                    continue
                listed = ", ".join(self.describe(node.element) for node in hits)
                self.report(
                    "spec.module.ambiguous",
                    f"The module {module.id} matches {len(hits)} sequences: {listed}.",
                    element=hits[0].element,
                    module=module.id,
                )
            elif module.required and module.id in selected:
                self.report(
                    "spec.module.missing",
                    f"The module {module.id} is not in the instrument.",
                    module=module.id,
                )

    def match_items(self) -> None:
        assert self.index is not None
        for module in self.spec.modules:
            for item_id in [*module.statements, *(q.id for q in module.questions)]:
                self.listed_in.setdefault(item_id, module.id)
        questions = self.index.of_kind("QuestionConstruct")
        statements = self.index.of_kind("StatementItem")
        for question in self.spec.questions:
            hits, _ = self.match(question.id, questions, self.spec.match.question_id)
            if len(hits) == 1:
                node = self.item_nodes[question.id] = hits[0]
                self.spec_id_of[self.key(node.element)] = question.id
                self.spec_ids_of.setdefault(self.key(node.element), set()).add(
                    question.id
                )
                item = self.index.question_item(node.element)
                if item is not None:
                    self.spec_id_of[self.key(item)] = question.id
        for module in self.spec.modules:
            for statement in module.statements:
                hits, _ = self.match(
                    statement, statements, self.spec.match.statement_id
                )
                if len(hits) == 1:
                    self.item_nodes[statement] = hits[0]

    # ---- One module ------------------------------------------------------------------

    def check_module(self, module: ModuleSpec) -> None:
        assert self.index is not None
        module_node = self.module_nodes.get(module.id)
        listed: list[tuple[str, QuestionSpec | None]] = [
            (statement, None) for statement in module.statements
        ] + [(question.id, question) for question in module.questions]
        scope_term = None
        if module_node is not None:
            scope_term = self.check_module_gate(module, module_node)
        for item_id, question in listed:
            self.check_item(module, item_id, question, scope_term)
        if module_node is not None:
            self.check_extra_items(module, module_node)

    def check_item(
        self,
        module: ModuleSpec,
        item_id: str,
        question: QuestionSpec | None,
        scope_term: Expression | None,
    ) -> None:
        assert self.index is not None
        kind = "question" if question is not None else "statement"
        nodes = self.index.of_kind(
            "QuestionConstruct" if question is not None else "StatementItem"
        )
        sources = (
            self.spec.match.question_id
            if question is not None
            else self.spec.match.statement_id
        )
        hits, source = self.match(item_id, nodes, sources)
        if not hits:
            self.report(
                "spec.item.missing",
                f"The {kind} {item_id} of module {module.id} is not in the instrument.",
                module=module.id,
                item=item_id,
            )
            return
        if len(hits) > 1:
            listed = ", ".join(self.describe(node.element) for node in hits)
            self.report(
                "spec.item.ambiguous",
                f"The {kind} {item_id} matches {len(hits)} constructs by {source}: "
                f"{listed}.",
                element=hits[0].element,
                module=module.id,
                item=item_id,
            )
            return
        # Every place the construct is: it can be asked in several.
        places = self.index.nodes_of(hits[0].element)
        inside = [place for place in places if self.module_of(place) == module.id]
        ambiguous = [
            candidate
            for candidates in self.ambiguous_modules.values()
            for candidate in candidates
        ]
        if not inside and any(self.inside(place, ambiguous) for place in places):
            # It is in a module that cannot be told apart (its own, or one the
            # spec lists elsewhere): where it is and its gate are not compared.
            node, found_in, compare_gates = places[0], None, False
        else:
            node = inside[0] if inside else places[0]
            found_in = module.id if inside else self.module_of(node)
            compare_gates = True
            self.check_paths(module, item_id, kind, places, found_in)
            if found_in != module.id:
                where = f"module {found_in}" if found_in else "no module of the spec"
                self.report(
                    "spec.item.misplaced",
                    f"The {kind} {item_id} belongs in module {module.id}, but is in "
                    f"{where}.",
                    element=node.element,
                    module=module.id,
                    item=item_id,
                    expected=module.id,
                    actual=found_in,
                )
        if question is None:
            self.check_languages(
                node.element, "DisplayText", "display text", module, item_id
            )
            if compare_gates and scope_term is not None and found_in == module.id:
                self.check_statement_gate(inside, item_id, module, scope_term)
            return
        assert source is not None
        self.check_id_sources(node, item_id, source, module)
        self.check_question(node, question, module)
        if not compare_gates:
            return
        inside = [place for place in places if self.module_of(place) == found_in]
        paths = sum(place.paths for place in inside)
        if paths > 1 and found_in is not None:
            reason = self.paths_disagree(inside, self.module_nodes[found_in])
            if reason is not None:
                self.report(
                    "spec.gate.unverifiable",
                    f"The gate of question {question.id} cannot be compared: it is "
                    f"reached by {paths} paths {reason}.",
                    element=node.element,
                    module=module.id,
                    item=question.id,
                    expected=_shown(question.gate),
                )
                return
        self.check_item_gate(node, question, module, found_in, scope_term)

    @staticmethod
    def inside(node: Node, sequences: list[Node]) -> bool:
        """Whether ``node`` is one of ``sequences`` or under one of them."""
        return any(
            sequence.element is node.element or sequence.element in node.sequences
            for sequence in sequences
        )

    def check_paths(
        self,
        module: ModuleSpec,
        item_id: str,
        kind: str,
        places: list[Node],
        found_in: str | None,
    ) -> None:
        """Report the item in each other spec module that also holds it."""
        reported = {module.id, found_in}
        selected = {checked.id for checked in self.selected}
        for place in places:
            other = self.module_of(place)
            if other is None or other in reported or other not in selected:
                continue
            reported.add(other)
            self.report(
                "spec.item.extra",
                f"Module {other} has the {kind} {self.describe(place.element)}, which "
                f"the spec lists in module {module.id}.",
                element=place.element,
                module=other,
                item=item_id,
            )

    def paths_disagree(self, places: list[Node], holder: Node) -> str | None:
        """Why the paths to an item cannot give it one gate, if they cannot.

        ``places`` are the item's nodes in ``holder``. ``None`` when every
        path carries an equivalent gate (or none).
        """
        assert self.index is not None
        below = holder.element
        unreadable = self.index.first_path(
            places,
            below,
            lambda found, term: found or not self.readable(term),
            False,
            bool,
        )
        if unreadable is not None:
            try:
                self.terms(unreadable[1])
            except _UnverifiableError as error:
                return f"and the gate on one cannot be read ({_sentence(error)})"
        first = _all_of(self.terms(places[0].gates_inside(below)))

        def differs(terms: frozenset[Expression]) -> bool:
            other = _all_of(sorted(terms, key=format_expression))
            if first is None or other is None:
                return (first is None) != (other is None)
            return self.decide(first, other).outcome != "equivalent"

        none: frozenset[Expression] = frozenset()
        differing = self.index.first_path(
            places, below, lambda terms, term: terms | {self.term(term)}, none, differs
        )
        return None if differing is None else "with different gates"

    def check_id_sources(
        self, node: Node, item_id: str, source: str, module: ModuleSpec
    ) -> None:
        assert self.index is not None
        others = []
        for other in self.spec.match.question_id:
            values = self.index.ids(node.element, other)
            if other != source and values and item_id not in values:
                others.append(f"its {other} is {values[0]!r}")
        if others:
            self.report(
                "spec.item.id-sources-differ",
                f"The question {item_id} is found by its {source}; "
                f"{'; '.join(others)}.",
                element=node.element,
                module=module.id,
                item=item_id,
            )

    def check_extra_items(self, module: ModuleSpec, module_node: Node) -> None:
        assert self.index is not None
        listed = {question.id for question in module.questions} | set(module.statements)
        known = {id(node.element): item for item, node in self.item_nodes.items()}
        selected = {checked.id for checked in self.selected}
        seen: set[int] = set()
        for node in self.index.of_kind("QuestionConstruct", "StatementItem"):
            if module_node.element not in node.sequences:
                continue
            if id(node.element) in seen:
                continue
            seen.add(id(node.element))
            kind = "question" if node.kind == "QuestionConstruct" else "statement"
            if id(node.element) in known:
                # Listed in another module: that module's check reports it
                # here, unless it is not being checked.
                item = known[id(node.element)]
                home = self.listed_in.get(item)
                if home is not None and home != module.id and home not in selected:
                    self.report(
                        "spec.item.extra",
                        f"Module {module.id} has the {kind} "
                        f"{self.describe(node.element)}, which the spec lists in "
                        f"module {home}.",
                        element=node.element,
                        module=module.id,
                        item=item,
                    )
                continue
            sources = (
                self.spec.match.question_id
                if node.kind == "QuestionConstruct"
                else self.spec.match.statement_id
            )
            names = [
                name
                for source in sources
                for name in self.index.ids(node.element, source)
            ]
            # A listed id the spec could not match (ambiguous) may be this
            # construct; a listed id matched elsewhere makes this one extra.
            if any(name in listed and name not in self.item_nodes for name in names):
                continue
            name = names[0] if names else None
            self.report(
                "spec.item.extra",
                f"Module {module.id} has the {kind} {self.describe(node.element)}, "
                "which the spec does not list.",
                element=node.element,
                module=module.id,
                item=name,
            )

    # ---- Questions -------------------------------------------------------------------

    def check_question(
        self, node: Node, question: QuestionSpec, module: ModuleSpec
    ) -> None:
        assert self.index is not None
        item = self.index.question_item(node.element)
        if item is None:
            if question.domain is not None:
                self.report(
                    "spec.domain.unverifiable",
                    f"The question {question.id} asks no question in the file.",
                    element=node.element,
                    module=module.id,
                    item=question.id,
                )
            return
        self.check_languages(item, "QuestionText", "question text", module, question.id)
        if question.domain is not None:
            self.check_domain(item, question, module)

    def check_languages(
        self, element: Element, local: str, what: str, module: ModuleSpec, item_id: str
    ) -> None:
        if not self.spec.languages:
            return
        holders = [child for child in element if _local(child.tag) == local]
        if not holders:
            return
        present = {language for holder in holders for _, _, language in _texts(holder)}
        absent = [
            language
            for language in self.spec.languages
            if not any(_language_range_matches(language, tag) for tag in present)
        ]
        if absent:
            self.report(
                "spec.language.missing",
                f"The {what} of {item_id} has no {', '.join(absent)}.",
                element=holders[0],
                module=module.id,
                item=item_id,
                expected=", ".join(self.spec.languages),
                actual=", ".join(sorted(present)),
            )

    def check_domain(
        self, item: Element, question: QuestionSpec, module: ModuleSpec
    ) -> None:
        spec = question.domain
        assert spec is not None
        if _local(item.tag) != "QuestionItem":
            self.unverifiable_domain(item, question, module, f"is a {_local(item.tag)}")
            return
        domains = [
            child
            for child in item
            if _local(child.tag).endswith(("Domain", "DomainReference"))
        ]
        if not domains:
            self.report(
                "spec.domain.type",
                f"The question {question.id} has no response domain; the spec says "
                f"{spec.kind}.",
                element=item,
                module=module.id,
                item=question.id,
                expected=spec.kind,
            )
            return
        if len(domains) > 1:
            self.unverifiable_domain(item, question, module, "has several domains")
            return
        domain = domains[0]
        local = _local(domain.tag)
        if local == _MIXED:
            # A container: compare its one domain of the spec's kind.
            inner = [
                child
                for holder in domain
                if _local(holder.tag) == "ResponseDomainInMixed"
                for child in holder
                if _local(child.tag).endswith(("Domain", "DomainReference"))
            ]
            kinds = [self.domain_kind(child) for child in inner]
            of_kind = [
                child
                for child, kind in zip(inner, kinds, strict=True)
                if kind == spec.kind
            ]
            unresolved = [kind for kind in kinds if kind.endswith("Reference")]
            if not of_kind and not unresolved:
                found = ", ".join(sorted(set(kinds))) or "no"
                self.report(
                    "spec.domain.type",
                    f"The question {question.id} has a mixed domain of {found} "
                    f"domains; the spec says {spec.kind}.",
                    element=domain,
                    module=module.id,
                    item=question.id,
                    expected=spec.kind,
                    actual=f"mixed({', '.join(kinds)})",
                )
                return
            if len(of_kind) != 1:
                why = (
                    f"has a mixed domain with {len(of_kind)} {spec.kind} domains"
                    if len(of_kind) > 1
                    else "has a mixed domain that refers to a domain not in the "
                    f"file ({unresolved[0]})"
                )
                self.unverifiable_domain(item, question, module, why)
                return
            domain = of_kind[0]
            local = _local(domain.tag)
        if local.endswith("Reference"):
            target = self.context.resolve(domain)
            if target is None:
                self.unverifiable_domain(
                    item,
                    question,
                    module,
                    f"refers to its domain ({local}), which is not in the file",
                )
                return
            domain = target
            local = _local(domain.tag)
        kind = _DOMAIN_KINDS.get(local, local)
        if kind != spec.kind:
            self.report(
                "spec.domain.type",
                f"The question {question.id} has a {kind} domain; the spec says "
                f"{spec.kind}.",
                element=domain,
                module=module.id,
                item=question.id,
                expected=spec.kind,
                actual=kind,
            )
            return
        check = {
            "code": self.check_codes,
            "numeric": self.check_numeric,
            "text": self.check_text,
            "date": self.check_date,
        }[kind]
        check(domain, spec, question, module)

    def domain_kind(self, domain: Element) -> str:
        """The kind of a domain, following a reference to it."""
        local = _local(domain.tag)
        if local.endswith("Reference"):
            target = self.context.resolve(domain)
            if target is None:
                return local
            local = _local(target.tag)
        return _DOMAIN_KINDS.get(local, local)

    def unverifiable_domain(
        self, element: Element, question: QuestionSpec, module: ModuleSpec, why: str
    ) -> None:
        self.report(
            "spec.domain.unverifiable",
            f"The domain of {question.id} is not compared: the question {why}.",
            element=element,
            module=module.id,
            item=question.id,
        )

    def check_codes(
        self,
        domain: Element,
        spec: DomainSpec,
        question: QuestionSpec,
        module: ModuleSpec,
    ) -> None:
        reference = domain.find(self.context.r("CodeListReference"))
        code_list = None if reference is None else self.context.resolve(reference)
        if code_list is None:
            self.unverifiable_domain(
                domain, question, module, "has a code list that is not in the file"
            )
            return
        found: dict[str, Element | None] = {}
        for code in code_list.iter():
            if _local(code.tag) != "Code":
                continue
            value = (code.findtext(self.context.r("Value")) or "").strip()
            category_reference = code.find(self.context.r("CategoryReference"))
            category = (
                None
                if category_reference is None
                else self.context.resolve(category_reference)
            )
            found.setdefault(value, category)
        expected = spec.codes or {}
        missing = [value for value in expected if value not in found]
        extra = [value for value in found if value not in expected]
        if missing:
            self.report(
                "spec.code.missing",
                f"The question {question.id} does not offer the code(s) "
                f"{', '.join(missing)}.",
                element=code_list,
                module=module.id,
                item=question.id,
                expected=", ".join(expected),
                actual=", ".join(found),
            )
        if extra:
            self.report(
                "spec.code.extra",
                f"The question {question.id} offers the code(s) {', '.join(extra)}, "
                "which the spec does not list.",
                element=code_list,
                module=module.id,
                item=question.id,
                expected=", ".join(expected),
                actual=", ".join(found),
            )
        for value, labels in expected.items():
            category = found.get(value)
            if category is None:
                continue
            self.check_label(category, value, labels, question, module)

    def check_label(
        self,
        category: Element,
        value: str,
        labels: dict[str, str],
        question: QuestionSpec,
        module: ModuleSpec,
    ) -> None:
        holders = [child for child in category if _local(child.tag) == "Label"]
        written = [
            (language, text.strip())
            for holder in holders
            for _, text, language in _texts(holder)
        ]
        for language in self.spec.languages:
            if not any(_language_range_matches(language, tag) for tag, _ in written):
                self.report(
                    "spec.language.missing",
                    f"The label of code {value} of {question.id} has no {language}.",
                    element=category,
                    module=module.id,
                    item=question.id,
                    expected=language,
                )
        for language, text in labels.items():
            actual = [
                label
                for tag, label in written
                if not language or _language_range_matches(language, tag)
            ]
            if actual and not any(_same_text(label, text) for label in actual):
                where = f" in {language}" if language else ""
                self.report(
                    "spec.code.label",
                    f"Code {value} of {question.id} is labelled {actual[0]!r}{where}; "
                    f"the spec says {text!r}.",
                    element=category,
                    module=module.id,
                    item=question.id,
                    expected=text,
                    actual=actual[0],
                )

    def check_numeric(
        self,
        domain: Element,
        spec: DomainSpec,
        question: QuestionSpec,
        module: ModuleSpec,
    ) -> None:
        number_range = domain.find(self.context.r("NumberRange"))
        low = high = None
        low_inclusive = high_inclusive = True
        if number_range is not None:
            for child in number_range:
                local = _local(child.tag)
                # xs:boolean: "false" and "0" are false.
                inclusive = (child.get("isInclusive") or "true").strip() not in (
                    "false",
                    "0",
                )
                if local in ("Low", "LowDouble"):
                    low, low_inclusive = _decimal(child.text), inclusive
                elif local in ("High", "HighDouble"):
                    high, high_inclusive = _decimal(child.text), inclusive
        problems = []
        if spec.minimum is not None and (
            low != spec.minimum or low_inclusive != spec.min_inclusive
        ):
            problems.append("minimum")
        if spec.maximum is not None and (
            high != spec.maximum or high_inclusive != spec.max_inclusive
        ):
            problems.append("maximum")
        if problems:
            expected = _range_text(
                spec.minimum, spec.min_inclusive, spec.maximum, spec.max_inclusive
            )
            actual = _range_text(low, low_inclusive, high, high_inclusive)
            self.report(
                "spec.domain.range",
                f"The range of {question.id} is {actual}; the spec says {expected}.",
                element=domain,
                module=module.id,
                item=question.id,
                expected=expected,
                actual=actual,
            )
        decimals = domain.get("decimalPositions")
        if spec.decimals is not None and decimals != str(spec.decimals):
            self.report(
                "spec.domain.decimals",
                f"{question.id} allows {decimals or 'unspecified'} decimal(s); the "
                f"spec says {spec.decimals}.",
                element=domain,
                module=module.id,
                item=question.id,
                expected=str(spec.decimals),
                actual=decimals,
            )

    def check_text(
        self,
        domain: Element,
        spec: DomainSpec,
        question: QuestionSpec,
        module: ModuleSpec,
    ) -> None:
        for name, attribute, wanted in (
            ("maximum length", "maxLength", spec.max_length),
            ("minimum length", "minLength", spec.min_length),
        ):
            actual = domain.get(attribute)
            if wanted is not None and actual != str(wanted):
                self.report(
                    "spec.domain.length",
                    f"The {name} of {question.id} is {actual or 'unspecified'}; the "
                    f"spec says {wanted}.",
                    element=domain,
                    module=module.id,
                    item=question.id,
                    expected=str(wanted),
                    actual=actual,
                )

    def check_date(
        self,
        domain: Element,
        spec: DomainSpec,
        question: QuestionSpec,
        module: ModuleSpec,
    ) -> None:
        actual = (domain.findtext(self.context.r("DateTypeCode")) or "").strip()
        if spec.date_type is not None and actual != spec.date_type:
            self.report(
                "spec.domain.type",
                f"{question.id} is a {actual or 'date'}; the spec says "
                f"{spec.date_type}.",
                element=domain,
                module=module.id,
                item=question.id,
                expected=spec.date_type,
                actual=actual or None,
            )

    # ---- Gates -------------------------------------------------------------------

    def subject(self, key: tuple[str, str] | None) -> str | None:
        """The spec name a parameter is bound to, following bindings.

        The question the bindings reach names it: its spec id, or, for a
        question the spec does not list, its own id, so a gate bound to the
        wrong question reads as that question. A question with several
        outputs (a grid's cells) is named by the output: its alias when the
        spec names it, else the variable of the spec an alias on the way names
        (the cell is that variable), else the question's id and the alias.
        When no question is reached, the output the bindings end at (a data
        lookup's field, a computation's result) names it, else the farthest
        alias on the way that the spec names. An alias naming a question
        never hides which question, or which output, a gate is bound to.
        """
        seen: set[tuple[str, str]] = set()
        farthest = source = variable = None
        while key is not None and key not in seen:
            seen.add(key)
            parameter = self.lookup.items.get(key)
            source = None
            if parameter is not None:
                alias = (parameter.findtext(self.context.r("Alias")) or "").strip()
                owner = self.lookup.owner.get(id(parameter))
                if owner is not None and _local(owner.tag) in _QUESTIONS:
                    return self.question_subject(owner, alias, variable)
                if alias in self.spec_names:
                    farthest = alias
                if alias in self.variable_names:
                    variable = alias
                if _local(parameter.tag) == "OutParameter" and alias:
                    source = alias
            key = self.lookup.bound_from.get(key)
        return source or farthest

    def question_subject(
        self, owner: Element, alias: str, variable: str | None
    ) -> str | None:
        question_id = self.spec_id_of.get(self.key(owner))
        if question_id is None:
            return self.question_name(owner)
        outputs = owner.findall(self.context.r("OutParameter"))
        if len(outputs) > 1:
            parts = self.spec_ids_of.get(self.key(owner), set())
            if alias in self.variable_names or alias == question_id or alias in parts:
                return alias
            return variable or f"{question_id}.{alias}"
        return question_id

    def question_name(self, question: Element) -> str | None:
        """The first id the spec's id sources give a question it does not list."""
        assert self.index is not None
        for source in self.spec.match.question_id:
            names = self.index.ids(question, source)
            if names:
                return names[0]
        return self.lookup._question_of(question) or self.key(question)[1]

    def code_value(self, urn: str) -> str | None:
        key = _parse_urn(urn)
        code = None if key is None else self.lookup.items.get(key)
        if code is None:
            return None
        value = code.findtext(self.context.r("Value"))
        return None if value is None else value.strip()

    def condition(self, holder: Element, owner: Element) -> Expression:
        """The condition ``holder`` stores, in spec names.

        Raises:
            _UnverifiableError: If it cannot be read back.
        """
        try:
            stored = parse_condition(holder)
        except ConditionFormatError as error:
            raise _UnverifiableError(str(error)) from None
        if stored is None:
            raise _UnverifiableError("it holds no condition")
        if isinstance(stored, DataLookup):
            raise _UnverifiableError("it is a data lookup")
        if isinstance(stored, Condition):
            self.neutral_read = True
            try:
                return comparable(
                    condition_to_expression(
                        stored,
                        subject_name=lambda urn: self.subject(_parse_urn(urn)),
                        code_value=self.code_value,
                    )
                )
            except UnverifiableConditionError as error:
                raise _UnverifiableError(str(error)) from None
        assert isinstance(stored, NativeCondition)
        self.native_read = True
        if not stored.language.lower().startswith("blaise"):
            raise _UnverifiableError(f"it is {stored.language} code")
        try:
            native = parse_blaise(stored.text, self.spec.blaise)
        except ExpressionError as error:
            raise _UnverifiableError(
                f"its Blaise code does not read: {error.reason}"
            ) from None
        aliases = {}
        for parameter in owner.findall(self.context.r("InParameter")):
            alias = (parameter.findtext(self.context.r("Alias")) or "").strip()
            name = self.subject(self.key(parameter))
            if alias and name:
                aliases[alias] = name
        return _renamed(native, lambda name: aliases.get(name, name))

    def decide(self, found: Expression, expected: Expression) -> Verdict:
        """Whether two conditions hold for the same respondents.

        By normal form; then, with ``exact``, by the solver. Each pair is
        decided once a run.
        """
        key = (normalise(found), normalise(expected))
        verdict = self.decided.get(key)
        if verdict is None:
            if key[0] == key[1]:
                verdict = Verdict("equivalent")
            elif not self.exact:
                verdict = Verdict("unknown", reason="their normal forms differ")
            else:
                verdict = decide(found, expected, types=self.types)
            self.decided[key] = verdict
        return verdict

    def same(
        self, found: Expression, expected: Expression, all_neutral: bool
    ) -> Verdict:
        """Whether a stored condition matches the spec's.

        What is read from a ``Neutral`` condition, which stores ``"2"`` and
        ``2`` alike, already has its quoted plain numbers as numbers (see
        `comparable`); Blaise keeps them apart. The spec's are taken as
        numbers too only when everything was read from ``Neutral``, and that
        reading is preferred for the respondent shown.
        """
        verdicts = [self.decide(found, expected)]
        if all_neutral:
            verdicts.insert(0, self.decide(found, comparable(expected)))
        for outcome in ("equivalent", "different"):
            for verdict in verdicts:
                if verdict.outcome == outcome:
                    return verdict
        return verdicts[0]

    def read_only_neutral(self) -> bool:
        """Whether every condition read since the last reset was ``Neutral``."""
        return self.neutral_read and not self.native_read

    def term(self, term: GateTerm) -> Expression:
        """The condition one gate term puts on the constructs under it.

        Only the conditions the branch depends on are read: a Then branch its
        own, the n-th ElseIf the first n + 1, an Else all of them. A term is
        read once; reading it again marks again what it was stored as.
        """
        read = self.terms_read.get(term)
        if read is None:
            marks = self.neutral_read, self.native_read
            self.neutral_read = self.native_read = False
            try:
                found: Expression | str = self.read_term(term)
            except _UnverifiableError as reason:
                found = str(reason)
            read = self.terms_read[term] = (found, self.neutral_read, self.native_read)
            self.neutral_read, self.native_read = marks
        found, neutral, native = read
        self.neutral_read |= neutral
        self.native_read |= native
        if isinstance(found, str):
            raise _UnverifiableError(found)
        return found

    def read_term(self, term: GateTerm) -> Expression:
        conditions = [self.condition(term.gate, term.gate)]
        if term.branch == 0:
            return conditions[0]
        else_ifs = [child for child in term.gate if _local(child.tag) == "ElseIf"]
        needed = else_ifs if term.branch < 0 else else_ifs[: term.branch]
        for child in needed:
            conditions.append(self.condition(child, term.gate))
        if term.branch > 0:
            parts = [Not(condition) for condition in conditions[: term.branch]]
            return And((*parts, conditions[term.branch]))
        return Not(Or(tuple(conditions)) if len(conditions) > 1 else conditions[0])

    def terms(self, terms: Iterable[GateTerm]) -> list[Expression]:
        return [self.term(term) for term in terms]

    def compare_gate(
        self,
        what: str,
        expected: Expression | None,
        actual: list[GateTerm],
        *,
        element: Element,
        module: str,
        item: str | None,
    ) -> None:
        self.neutral_read = self.native_read = False
        try:
            terms = self.terms(actual)
        except _UnverifiableError as reason:
            self.report(
                "spec.gate.unverifiable",
                f"The gate of {what} cannot be compared: {_sentence(reason)}.",
                element=element,
                module=module,
                item=item,
                expected=_shown(expected),
            )
            return
        found = _all_of(terms)
        neutral = self.read_only_neutral()
        if expected is None and found is None:
            return
        if expected is None:
            self.report(
                "spec.gate.extra",
                f"{what[0].upper()}{what[1:]} is gated by {_shown(found)}; the spec "
                "gates it with nothing.",
                element=element,
                module=module,
                item=item,
                actual=_shown(found),
            )
        elif found is None:
            self.report(
                "spec.gate.missing",
                f"{what[0].upper()}{what[1:]} is not gated; the spec says "
                f"{_shown(expected)}.",
                element=element,
                module=module,
                item=item,
                expected=_shown(expected),
            )
        elif (verdict := self.same(found, expected, neutral)).outcome != "equivalent":
            self.report(
                "spec.gate.different",
                f"{what[0].upper()}{what[1:]} is gated by {_shown(found)}; the spec "
                f"says {_shown(expected)}{_when(verdict)}.",
                element=element,
                module=module,
                item=item,
                expected=_shown(expected),
                actual=_shown(found),
                example=_example(verdict),
            )

    def check_module_gate(self, module: ModuleSpec, node: Node) -> Expression | None:
        """Compare the module's gate; return the gate expected on each page."""
        gate = module.gate
        if gate is not None:
            self.neutral_read = self.native_read = False
            try:
                own: list[Expression] | None = self.terms(node.gates)
            except _UnverifiableError:
                own = None  # compare_gate reports why
            if own is not None:
                neutral = self.read_only_neutral()
                at_module = any(
                    self.same(term, gate, neutral).outcome == "equivalent"
                    for term in own
                )
                if module.gate_scope == "page" and at_module:
                    self.report(
                        "spec.gate.scope",
                        f"The gate of module {module.id} wraps the module; the "
                        "spec says each page.",
                        element=node.element,
                        module=module.id,
                        expected="page",
                        actual="module",
                    )
                    return None
                if (
                    module.gate_scope == "module"
                    and not at_module
                    and self.gated_per_page(gate, node)
                ):
                    self.report(
                        "spec.gate.scope",
                        f"The gate of module {module.id} wraps each page; the spec "
                        "says the module.",
                        element=node.element,
                        module=module.id,
                        expected="module",
                        actual="page",
                    )
                    # The module's own gates are still compared, with nothing.
                    self.compare_gate(
                        f"module {module.id}",
                        None,
                        list(node.gates),
                        element=node.element,
                        module=module.id,
                        item=None,
                    )
                    return gate
        page_gate = gate if module.gate_scope == "page" else None
        self.compare_gate(
            f"module {module.id}",
            None if page_gate is not None else gate,
            list(node.gates),
            element=node.element,
            module=module.id,
            item=None,
        )
        return page_gate

    def gated_per_page(self, gate: Expression, module_node: Node) -> bool:
        """Whether every construct in the module carries ``gate`` below it.

        On every path to it.
        """
        assert self.index is not None
        inside = [
            node
            for node in self.index.of_kind("QuestionConstruct", "StatementItem")
            if module_node.element in node.sequences
        ]
        if not inside:
            return False
        ungated = self.index.first_path(
            inside,
            module_node.element,
            lambda gated, term: gated or self.term_is(term, gate),
            False,
            lambda gated: not gated,
        )
        return ungated is None

    def readable(self, term: GateTerm) -> bool:
        """Whether ``term`` can be read."""
        try:
            self.term(term)
        except _UnverifiableError:
            return False
        return True

    def term_is(self, term: GateTerm, gate: Expression) -> bool:
        """Whether ``term`` is ``gate``; a term that cannot be read is not."""
        try:
            self.neutral_read = self.native_read = False
            found = self.term(term)
            return self.same(found, gate, self.read_only_neutral()).outcome == (
                "equivalent"
            )
        except _UnverifiableError:
            return False

    def check_item_gate(
        self,
        node: Node,
        question: QuestionSpec,
        module: ModuleSpec,
        found_in: str | None,
        scope_term: Expression | None,
    ) -> None:
        holder = self.module_nodes.get(found_in) if found_in else None
        below = node.gates_inside(holder.element) if holder is not None else node.gates
        # A page gate is the spec module's: it applies where the module is.
        page_gate = scope_term if found_in == module.id else None
        expected = _all_of(
            [term for term in (page_gate, question.gate) if term is not None]
        )
        self.compare_gate(
            f"question {question.id}",
            expected,
            list(below),
            element=node.element,
            module=module.id,
            item=question.id,
        )

    def check_statement_gate(
        self,
        places: list[Node],
        item_id: str,
        module: ModuleSpec,
        page_gate: Expression,
    ) -> None:
        """The module's page gate must wrap the statement, on every path to it.

        ``places`` are the statement's nodes in the module. The spec gives a
        statement no gate of its own, so one it carries besides the page
        gate is not reported; the first path without the page gate is.
        """
        assert self.index is not None
        holder = self.module_nodes[module.id]
        ungated = self.index.first_path(
            places,
            holder.element,
            lambda gated, term: gated or self.term_is(term, page_gate),
            False,
            lambda gated: not gated,
        )
        if ungated is None:
            return
        node, gates = ungated
        below = list(gates)
        what = f"statement {item_id}"
        if not below:
            self.compare_gate(
                what,
                page_gate,
                below,
                element=node.element,
                module=module.id,
                item=item_id,
            )
            return
        self.neutral_read = self.native_read = False
        try:
            found = _all_of(self.terms(below))
        except _UnverifiableError as reason:
            self.report(
                "spec.gate.unverifiable",
                f"The gate of {what} cannot be compared: {_sentence(reason)}.",
                element=node.element,
                module=module.id,
                item=item_id,
                expected=_shown(page_gate),
            )
            return
        assert found is not None  # below holds a gate
        verdict = self.same(found, page_gate, self.read_only_neutral())
        self.report(
            "spec.gate.different",
            f"Statement {item_id} is gated by {_shown(found)}; the spec puts it "
            f"under its page gate, {_shown(page_gate)}{_when(verdict)}.",
            element=node.element,
            module=module.id,
            item=item_id,
            expected=_shown(page_gate),
            actual=_shown(found),
            example=_example(verdict),
        )

    # ---- Modules the spec does not list --------------------------------------------

    def check_extra_modules(self) -> None:
        assert self.index is not None
        depth = self.spec.match.module_depth
        if depth is None:
            depths = {node.depth for node in self.module_nodes.values()}
            if len(depths) != 1:
                return
            (depth,) = depths
        matched = {id(node.element) for node in self.module_nodes.values()}
        matched.update(
            id(node.element)
            for candidates in self.ambiguous_modules.values()
            for node in candidates
        )
        seen: set[int] = set()
        for node in self.index.nodes:
            if not node.is_page_or_module or node.depth != depth:
                continue
            if id(node.element) in matched or id(node.element) in seen:
                continue
            seen.add(id(node.element))
            names = [
                name
                for source in self.spec.match.module_id
                for name in self.index.ids(node.element, source)
            ]
            self.report(
                "spec.module.extra",
                f"The instrument has the module {self.describe(node.element)}, which "
                "the spec does not list.",
                element=node.element,
                item=names[0] if names else None,
            )

    # ---- Variables ------------------------------------------------------------------

    def lookup_fields(self) -> dict[str, Any]:
        assert self.index is not None
        fields: dict[str, Any] = {}
        for node in self.index.of_kind("ComputationItem"):
            try:
                stored = parse_condition(node.element)
            except ConditionFormatError:
                continue
            if isinstance(stored, DataLookup):
                for entry in stored.fields:
                    fields.setdefault(entry.name, entry.type)
        return fields

    def check_variables(self) -> None:
        fields = self.lookup_fields()
        types = self.spec.match.lookup_types
        for variable in self.spec.imported_variables:
            if variable.name not in fields:
                self.report(
                    "spec.variable.import-undeclared",
                    f"The imported variable {variable.name} is not a field of any "
                    "data lookup of the instrument.",
                    item=variable.name,
                )
                continue
            stored = fields[variable.name]
            mapped = types.get(str(stored)) if stored is not None else None
            if (
                variable.type is not None
                and mapped is not None
                and mapped != variable.type
            ):
                self.report(
                    "spec.variable.import-type",
                    f"The lookup field {variable.name} is {stored} ({mapped}); the "
                    f"spec says {variable.type}.",
                    item=variable.name,
                    expected=variable.type,
                    actual=mapped,
                )
        for variable in self.spec.derived_variables:
            if variable.name in fields:
                self.report(
                    "spec.variable.derived-is-lookup",
                    f"The derived variable {variable.name} is a data lookup field: it "
                    "is imported, not computed.",
                    item=variable.name,
                )

    # ---- Edits ----------------------------------------------------------------------

    def edits_to_check(self) -> list[EditSpec]:
        modules = {module.id for module in self.selected}
        return [
            edit for edit in self.spec.edits if self.whole or edit.module in modules
        ]

    def check_edits(self) -> None:
        edits = self.edits_to_check()
        if self.edits == "off":
            return
        if self.edits == "info":
            for edit in edits:
                self.report(
                    "spec.edit.unverifiable",
                    f"The edit {edit.id}: {NOT_VERIFIABLE}.",
                    module=edit.module,
                    item=edit.id,
                    expected=_shown(edit.when),
                )
            return
        match = self.spec.match.edits
        assert match is not None
        stored: dict[str, list[Element]] = {}
        # The edit checks this instrument reaches, not every one in the file.
        reached: dict[int, Element] = {}
        if self.index is not None:
            for node in self.index.of_kind("ComputationItem"):
                reached.setdefault(id(node.element), node.element)
        for element in reached.values():
            if not self.is_edit(element, match.attribute, match.value):
                continue
            assert self.index is not None
            for name in self.index.ids(element, match.id):
                stored.setdefault(name, []).append(element)
        for edit in edits:
            found = stored.get(edit.id, [])
            if not found:
                self.report(
                    "spec.edit.missing",
                    f"No edit check is {edit.id}.",
                    module=edit.module,
                    item=edit.id,
                    expected=_shown(edit.when),
                )
                continue
            if len(found) > 1:
                listed = ", ".join(self.describe(element) for element in found)
                self.report(
                    "spec.item.ambiguous",
                    f"The edit {edit.id} matches {len(found)} edit checks: {listed}.",
                    element=found[0],
                    module=edit.module,
                    item=edit.id,
                )
                continue
            element = found[0]
            self.neutral_read = self.native_read = False
            try:
                condition = self.condition(element, element)
            except _UnverifiableError as reason:
                self.report(
                    "spec.edit.unverifiable",
                    f"The edit {edit.id} cannot be compared: {_sentence(reason)}.",
                    element=element,
                    module=edit.module,
                    item=edit.id,
                    expected=_shown(edit.when),
                )
                continue
            verdict = self.same(condition, edit.when, self.read_only_neutral())
            if verdict.outcome != "equivalent":
                self.report(
                    "spec.edit.different",
                    f"The edit {edit.id} fires on {_shown(condition)}; the spec says "
                    f"{_shown(edit.when)}{_when(verdict)}.",
                    element=element,
                    module=edit.module,
                    item=edit.id,
                    expected=_shown(edit.when),
                    actual=_shown(condition),
                    example=_example(verdict),
                )

    def is_edit(self, element: Element, attribute: str, value: str) -> bool:
        for pair in element.findall(self.context.r("UserAttributePair")):
            key = (pair.findtext(self.context.r("AttributeKey")) or "").strip()
            stored = (pair.findtext(self.context.r("AttributeValue")) or "").strip()
            if key == attribute and stored == value:
                return True
        return False


def _range_text(
    low: Decimal | None, low_inclusive: bool, high: Decimal | None, high_inclusive: bool
) -> str:
    left = "[" if low_inclusive else "("
    right = "]" if high_inclusive else ")"
    low_text = "" if low is None else _number(low)
    high_text = "" if high is None else _number(high)
    return f"{left}{low_text}, {high_text}{right}"


def _number(value: Decimal) -> str:
    if value.is_nan():
        return "NaN"
    if value.is_infinite():
        return "-INF" if value.is_signed() else "INF"
    return format_number(value)


def conform(
    document: LintTarget,
    spec: Spec,
    *,
    module: str | None = None,
    edits: str = "info",
    instrument: str | None = None,
    semantics: str | None = None,
) -> ConformReport:
    """Compare the instrument in ``document`` with ``spec``.

    Args:
        document: A fragment or document (as `ddi_l.read_ddi` gives).
        spec: The spec (`ddi_l.spec.load_spec`).
        module: Compare only this spec module. Modules the spec does not
            list and variables are then not checked.
        edits: ``info`` (the default) reports each edit as not verifiable;
            ``strict`` looks for edit checks as the spec's ``match.edits``
            says; ``off`` leaves edits out.
        instrument: The instrument to compare when the file has several: its
            name, label, user ID or ID. Overrides the spec's ``instrument``.
        semantics: How gates and edits are compared: ``"syntactic"`` by
            normal form (`normalise`); ``"smt"`` also decides what normal
            forms leave open, with the ``logic`` extra, and a difference
            comes with a respondent it shows in; ``None`` (the default) is
            ``"smt"`` when the extra is installed. The spec's response
            domains and variable types say what each name is.

    Raises:
        ConformError: If ``module`` is not one of the spec's, ``edits`` or
            ``semantics`` is not a mode, ``edits="strict"`` and the spec has
            no ``match.edits``, or ``semantics="smt"`` without the ``logic``
            extra.
    """
    if edits not in EDIT_MODES:
        raise ConformError(
            f"edits must be one of {', '.join(EDIT_MODES)}, not {edits!r}."
        )
    if semantics is not None and semantics not in SEMANTICS:
        raise ConformError(
            f"semantics must be one of {', '.join(SEMANTICS)}, not {semantics!r}."
        )
    solver = logic_available()
    if semantics == "smt" and not solver:
        raise ConformError(
            "semantics='smt' needs the logic extra: pip install 'ddi-l[logic]'."
        )
    if edits == "strict" and spec.match.edits is None:
        raise ConformError(
            "edits='strict' needs the spec's match.edits: the user attribute that "
            "marks an edit check, and where its id is."
        )
    if module is None:
        modules = list(spec.modules)
    else:
        try:
            modules = [spec.module(module)]
        except KeyError:
            listed = ", ".join(item.id for item in spec.modules)
            raise ConformError(
                f"The spec has no module {module!r}; it has {listed}."
            ) from None
    # The checks share what they build from the document (`ddi_l._facts`).
    with run_scope():
        checker = _Checker(
            document,
            spec,
            modules=modules,
            whole=module is None,
            edits=edits,
            instrument=instrument,
            exact=solver if semantics is None else semantics == "smt",
        )
        element, results = checker.run()
    return ConformReport(
        spec=spec.name,
        instrument=None if element is None else checker.describe(element),
        edits=edits,
        findings=checker.findings,
        modules=results,
    )
