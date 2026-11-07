"""Lint rules for questionnaires designed in Colectica.

The rules of the ``colectica-questionnaire`` profile: problems in the design
of questionnaires exported from Colectica (shared identifiers, empty or
impossible conditions, unresolved template text, compounded alias escaping
and so on).
They run on any DDI 3.3 document but read Colectica's conventions, notably
the condition JSON `ddi_l.colectica_logic` parses.

Rules marked *heuristic* in their docstrings guess at intent from wording or
layout; they report at most a warning. Anything specific to one organisation
comes from `LintConfiguration` and is empty by default,
so the rule needing it does nothing until it is configured.

Importing `ddi_l.lint` registers these rules; none joins the default
profile.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from functools import partial
from itertools import groupby
from typing import Any, NamedTuple

from . import _incremental
from ._etree import Element
from ._facts import only_items, recorder, shared, shared_by_value
from .colectica_logic import (
    Condition,
    ConditionFormatError,
    DataLookup,
    NativeCondition,
    Operator,
    Statement,
    StmtBool,
    _command_holder,
    _Lookup,
    _parse_urn,
    _subject_names,
    _used_inputs,
    parse_command,
    render_synopsis,
)
from .colectica_logic import (
    _version_rank as _rank,
)
from .lint import (
    _REGISTRY,
    COLECTICA_QUESTIONNAIRE_PROFILE,
    LintFinding,
    LintTarget,
    _element_path,
    _is_fragment_instance,
    _language_range_matches,
    _namespaces,
    get_lint_configuration,
    register_profile,
    register_rule,
)
from .models import qn
from .models._generated.fragment_items import FRAGMENT_ITEM_TYPES

__all__: list[str] = []

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
_ITEM_TYPES = frozenset(tag.rsplit("}", 1)[-1] for tag in FRAGMENT_ITEM_TYPES)
_MAX_ALIAS_LENGTH = 64
# A run of lower-case letters this long in an alias is question text that
# was concatenated into the name ("numberofpayrollsforworking...").
_CONCATENATED_TEXT = re.compile(r"[a-z]{20,}")
_XML_ESCAPE = re.compile(r"_x[0-9A-Fa-f]{4}_")
_COMPOUNDED_ESCAPE = re.compile(r"_((?:x005F_)+)")
_PIPE = re.compile(r"#\{([^{}]*)\}")
_TYPOGRAPHIC_QUOTES = re.compile("[\u2018\u2019\u201c\u201d]")
_NATIVE_INPUT = re.compile(r"\{\{\s*([^{}\s]+)\s*\}\}")
# A string literal, or a Blaise comment ({ ... }, not a {{name}} input),
# whichever starts first: text inside either is not code.
_STRING_OR_COMMENT = re.compile(
    r"\"(?:[^\"]|\"\")*\"|'(?:[^']|'')*'|(?<!\{)\{(?!\{)[^{}]*\}(?!\})"
)


def _code_only(text: str, *, keep_strings: bool = False) -> str:
    """``text`` with its comments blanked and, unless kept, its strings emptied."""

    def blank(match: re.Match[str]) -> str:
        found = match.group(0)
        if found[0] in "\"'":
            return found if keep_strings else '""'
        return " "

    return _STRING_OR_COMMENT.sub(blank, text)


def _local(tag: object) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _attribute(item: Element, key: str) -> str | None:
    """The value of the item's ``r:UserAttributePair`` with ``key``, if any."""
    for pair in item:
        if _local(pair.tag) != "UserAttributePair":
            continue
        parts = {_local(child.tag): (child.text or "").strip() for child in pair}
        if parts.get("AttributeKey") == key:
            return parts.get("AttributeValue")
    return None


def _text_of(element: Element) -> str:
    return " ".join(
        (node.text or "").strip()
        for node in element.iter()
        if isinstance(node.tag, str) and (node.text or "").strip()
    )


def _first(text: str, limit: int = 120) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _language_of(node: Element, inherited: str | None) -> str | None:
    # Colectica writes one QuestionText per language, marked with
    # audienceLanguage, around a Text without xml:lang.
    return node.get(XML_LANG) or node.get("audienceLanguage") or inherited


def _texts(element: Element) -> Iterator[tuple[Element, str, str]]:
    """Text in a language under ``element``: (node, text, language).

    A node's language is its ``xml:lang``, else an ``audienceLanguage``, else
    the nearest ancestor's. Text with no language anywhere above it
    (identifiers, aliases, codes) is not content and is left out.
    """
    stack: list[tuple[Element, str | None]] = [(element, _language_of(element, None))]
    while stack:
        node, language = stack.pop()
        if not isinstance(node.tag, str):
            continue
        if language and (node.text or "").strip():
            yield node, node.text, language  # type: ignore[misc]
        stack.extend(
            (child, _language_of(child, language)) for child in reversed(list(node))
        )


@dataclass
class _Context:
    """One pass over a document: its items, their latest versions and names."""

    document: LintTarget
    reusable: str = ""
    items: list[Element] = field(default_factory=list)
    by_key: dict[tuple[str, str], Element] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Every rule of a run reads the same items: build them once.
        self.reusable, self.items, self.by_key = shared(
            "context", self.document.root, lambda: _context_items(self.document)
        )
        # A rule run for some items only (incremental lint) reads only them;
        # it still resolves references against every item.
        only = only_items()
        if only is not None:
            self.items = list(only)

    def r(self, name: str) -> str:
        return qn(self.reusable, name)

    def short_id(self, element: Element) -> str:
        return (element.findtext(self.r("ID")) or "")[:8]

    def name(self, element: Element) -> str | None:
        """An item's name: a *Name, its label, or a parameter's alias."""
        for child in element:
            if _local(child.tag).endswith("Name"):
                text = next(
                    (
                        (node.text or "").strip()
                        for node in child.iter()
                        if (node.text or "").strip()
                    ),
                    "",
                )
                if text:
                    return _first(text, 60)
        label = element.find(self.r("Label"))
        first_label = (
            next((text for _, text, _ in _texts(label)), "")
            if label is not None
            else ""
        )
        if not first_label and label is not None:
            first_label = _text_of(label)
        if first_label.strip():
            return _first(first_label.strip(), 60)
        alias = element.findtext(self.r("Alias"))
        return alias.strip() if alias and alias.strip() else None

    def describe(self, element: Element) -> str:
        """``Type shortid (name)``, the way findings name an item."""
        name = self.name(element)
        text = f"{_local(element.tag)} {self.short_id(element)}".rstrip()
        return f"{text} ({name})" if name else text

    def lookup(self) -> _Lookup:
        root = self.document.root
        return shared("lookup", root, lambda: _Lookup(root))

    def resolve(self, reference: Element) -> Element | None:
        agency = reference.findtext(self.r("Agency"))
        identifier = reference.findtext(self.r("ID"))
        if not agency or not identifier:
            return None
        return self.by_key.get((agency, identifier))

    def items_of_type(self, *local_names: str) -> Iterator[Element]:
        for item in self.items:
            if _local(item.tag) in local_names:
                yield item

    def texts(self) -> Iterator[tuple[Element, Element, str, str]]:
        """Each piece of text in a language: item, element, text, language."""
        if only_items() is not None:
            yield from self._texts()
            return
        yield from shared("texts", self.document.root, self._texts)

    def _texts(self) -> list[tuple[Element, Element, str, str]]:
        return [
            (item, node, text, language)
            for item in self.items
            for node, text, language in _texts(item)
        ]

    def finding(
        self, rule_id: str, severity: str, element: Element, message: str
    ) -> LintFinding:
        found = LintFinding(
            rule_id=rule_id,
            message=message,
            severity=severity,
            location=_element_path(element),
        )
        record = recorder()
        if record is not None:
            record.append((found, element))
        return found


def _context_items(
    document: LintTarget,
) -> tuple[str, list[Element], dict[tuple[str, str], Element]]:
    """The reusable namespace, the items to lint, and the latest of each key."""
    root = document.root
    reusable = _namespaces(root)["REUSABLE_NS"]
    agency_tag = qn(reusable, "Agency")
    id_tag = qn(reusable, "ID")
    version_tag = qn(reusable, "Version")
    items: list[Element]
    if _is_fragment_instance(document):
        items = list(document.iter_fragment_payloads())  # type: ignore[union-attr]
    else:
        # In a DDIInstance, items nest inside schemes and studies: lint the
        # innermost ones, the types a Colectica fragment would carry one per
        # <Fragment>, so a finding names the item and not its scheme.
        items = _innermost_items(root)
    by_key: dict[tuple[str, str], Element] = {}
    ranks: dict[tuple[str, str], tuple[int, ...]] = {}
    for item in items:
        agency, identifier = item.findtext(agency_tag), item.findtext(id_tag)
        if agency and identifier:
            rank = _rank(item.findtext(version_tag) or "")
            key = (agency, identifier)
            if key not in ranks or rank > ranks[key]:
                ranks[key], by_key[key] = rank, item
    # A Colectica export can carry several versions of an item; the older
    # ones are history, so only the highest version of each is linted.
    latest = {id(item) for item in by_key.values()}
    items = [
        item
        for item in items
        if id(item) in latest
        or not (item.findtext(agency_tag) and item.findtext(id_tag))
    ]
    return reusable, items, by_key


def _innermost_items(root: Element) -> list[Element]:
    """The item-type elements below ``root`` with no item-type element in them.

    In document order. One pass down and one back up, rather than a search
    of every item's subtree.
    """
    order = list(root.iter())
    parent_of = {id(child): parent for parent in order for child in parent}
    holds_item: set[int] = set()
    # Reversed document order reaches every element after all it contains.
    for element in reversed(order):
        if id(element) in holds_item or _local(element.tag) in _ITEM_TYPES:
            parent = parent_of.get(id(element))
            if parent is not None:
                holds_item.add(id(parent))
    return [
        element
        for element in order
        if element is not root
        and _local(element.tag) in _ITEM_TYPES
        and id(element) not in holds_item
    ]


_CONDITIONAL = ("IfThenElse", "ComputationItem", "Loop", "RepeatUntil", "RepeatWhile")


class _Command(NamedTuple):
    """One condition of an item, as read.

    ``holder`` is the element holding it (``IfCondition``, ``CommandCode``,
    ``LoopWhile``...). ``condition`` is ``None`` when the content does not
    parse, and ``error`` then says why. ``branch`` is ``""`` for the item's
    own condition and ``"ElseIf 2"`` for a branch's.
    """

    item: Element
    holder: Element
    command: Element
    condition: Condition | DataLookup | NativeCondition | None
    error: str | None
    branch: str

    def where(self, context: _Context) -> str:
        """The item, and the branch when the condition is an ``ElseIf``'s."""
        described = context.describe(self.item)
        return f"{described}, {self.branch}" if self.branch else described


def _conditions(context: _Context, *local_names: str) -> Iterator[_Command]:
    """Each condition of the items: their own, then each ``ElseIf``'s in turn.

    A ``Loop``'s condition is its ``LoopWhile``; its ``InitialValue`` and
    ``StepValue`` are assignments, not conditions.
    """
    for item in context.items_of_type(*local_names):
        yield from _item_conditions(context, item)


def _item_conditions(context: _Context, item: Element) -> Iterator[_Command]:
    """`_conditions` of one item."""
    command_tag = context.r("Command")
    holders = [("", _command_holder(item))]
    branches = [child for child in item if _local(child.tag) == "ElseIf"]
    for number, branch in enumerate(branches, 1):
        holders.append((f"ElseIf {number}", _command_holder(branch)))
    for label, holder in holders:
        command = None if holder is None else holder.find(command_tag)
        if holder is None or command is None:
            continue
        language = command.findtext(context.r("ProgramLanguage"))
        text = command.findtext(context.r("CommandContent"))
        condition, error = shared_by_value(
            "command", (language, text), partial(_parsed, language, text)
        )
        yield _Command(item, holder, command, condition, error, label)


def _parsed(
    language: str | None, text: str | None
) -> tuple[Condition | DataLookup | NativeCondition | None, str | None]:
    """A command's condition, or ``None`` and why it does not parse."""
    try:
        return parse_command(language, text), None
    except ConditionFormatError as error:
        return None, str(error)


def _description(
    context: _Context, item: Element, holder: Element | None = None
) -> str:
    """The text of a condition's description, else the item's own description.

    ``holder`` is the element holding the condition; by default the item's.
    """
    for element in (holder if holder is not None else _command_holder(item), item):
        if element is None:
            continue
        description = element.find(context.r("Description"))
        if description is not None and _text_of(description):
            return _text_of(description)
    return ""


def _inputs(
    context: _Context, item: Element
) -> list[tuple[tuple[str, str] | None, str]]:
    return _parameters(context, item, "InParameter")


def _parameters(
    context: _Context, item: Element, kind: str
) -> list[tuple[tuple[str, str] | None, str]]:
    """Each ``kind`` parameter the item declares: its key and its alias."""
    found = []
    for parameter in item.findall(context.r(kind)):
        agency = parameter.findtext(context.r("Agency"))
        identifier = parameter.findtext(context.r("ID"))
        key = (agency, identifier) if agency and identifier else None
        alias = (parameter.findtext(context.r("Alias")) or "").strip()
        found.append((key, alias or (identifier or "")[:8]))
    return found


# ---- Identifiers and bindings ----------------------------------------------


def _check_shared_ids(document: LintTarget) -> Iterable[LintFinding]:
    """Report an identifiable declared inside two or more different items.

    Colectica's copy of a question can keep the source's ``OutParameter`` IDs,
    so two items declare the same parameter; a binding to it is ambiguous.
    Versions of one item sharing their children is expected and not reported.
    """
    context = _Context(document)
    parents: dict[tuple[str, str], dict[tuple[str, str], Element]] = {}
    first: dict[tuple[str, str], Element] = {}
    # What each item declares is read once while the item is unchanged.
    reads = _incremental.per_element(
        document,
        "item-identifiables",
        context.items,
        partial(_declared_identifiables, context),
    )
    for item, (item_key, declared) in zip(context.items, reads, strict=True):
        for key in declared:
            parents.setdefault(key, {}).setdefault(item_key, item)
            first.setdefault(key, item)
    for key, owners in parents.items():
        if len(owners) < 2:
            continue
        node = _first_declaration(context, first[key], key)
        names = ", ".join(context.describe(owner) for owner in owners.values())
        yield context.finding(
            "colectica.identifiable.shared-id",
            "error",
            node,
            f"{_local(node.tag)} {key[1][:8]} is declared in {len(owners)} "
            f"items: {names}.",
        )


def _declarations(
    context: _Context, item: Element
) -> Iterator[tuple[tuple[str, str], Element]]:
    """Each identifiable declared inside ``item``, with its key."""
    agency_tag, id_tag = context.r("Agency"), context.r("ID")
    stack = [child for child in item]
    while stack:
        node = stack.pop()
        if not isinstance(node.tag, str) or node.tag.endswith("Reference"):
            continue
        agency, identifier = node.findtext(agency_tag), node.findtext(id_tag)
        if agency and identifier:
            yield (agency, identifier), node
        stack.extend(node)


def _declared_identifiables(
    context: _Context, item: Element
) -> tuple[tuple[str, str], list[tuple[str, str]]]:
    """``item``'s key and the key of each identifiable declared inside it."""
    agency_tag, id_tag = context.r("Agency"), context.r("ID")
    item_key = (item.findtext(agency_tag) or "", item.findtext(id_tag) or "")
    return item_key, [key for key, _ in _declarations(context, item)]


def _first_declaration(
    context: _Context, item: Element, key: tuple[str, str]
) -> Element:
    """The first identifiable inside ``item`` with ``key``."""
    return next(node for found, node in _declarations(context, item) if found == key)


def _check_dangling_bindings(document: LintTarget) -> Iterable[LintFinding]:
    """Report a binding whose source or target parameter is not in the file.

    Late-bound references resolve to any version, so only a parameter
    missing at every version is reported.
    """
    from .lint import _index_identifiable_items

    context = _Context(document)
    known = _index_identifiable_items(document).versions
    for item in context.items:
        for binding in item.iter(context.r("Binding")):
            for end in ("Source", "Target"):
                reference = binding.find(context.r(f"{end}ParameterReference"))
                if reference is None:
                    continue
                agency = reference.findtext(context.r("Agency"))
                identifier = reference.findtext(context.r("ID"))
                if not agency or not identifier or (agency, identifier) in known:
                    continue
                kind = reference.findtext(context.r("TypeOfObject")) or "parameter"
                yield context.finding(
                    "colectica.binding.dangling",
                    "error",
                    reference,
                    f"A binding in {context.describe(item)} has a {end.lower()} "
                    f"{kind} {identifier[:8]} that is not declared in this file.",
                )


# ---- Conditions --------------------------------------------------------------


def _check_malformed_conditions(document: LintTarget) -> Iterable[LintFinding]:
    """Report a JSON condition that does not parse.

    ``Neutral`` and ``Blaise5DataLookup`` commands must hold valid JSON.
    """
    context = _Context(document)
    for entry in _conditions(context, *_CONDITIONAL):
        if entry.error:
            yield context.finding(
                "colectica.condition.malformed",
                "error",
                entry.command,
                f"{entry.where(context)}: {entry.error}",
            )


def _check_empty_conditions(document: LintTarget) -> Iterable[LintFinding]:
    """Report a ``Neutral`` condition with no statement at all.

    An empty condition is always true, so the branch always shows. A loop's
    empty condition tests nothing either, so whether the loop repeats no
    longer depends on the answers. The intended logic is often in the
    condition's description, quoted in the message.
    """
    context = _Context(document)
    for entry in _conditions(context, *_CONDITIONAL):
        condition = entry.condition
        if isinstance(condition, Condition) and condition.is_empty:
            description = _description(context, entry.item, entry.holder)
            detail = (
                f'; its description reads "{_first(description)}"'
                if description
                else ""
            )
            yield context.finding(
                "colectica.condition.empty",
                "error",
                entry.command,
                f"{entry.where(context)} has an empty condition{detail}.",
            )


def _statement_kind(statement: Statement) -> tuple[str, object] | None:
    operator = statement.operator
    if operator is Operator.EMPTY:
        return ("empty", None)
    if operator is Operator.REFUSED:
        return ("refused", None)
    if operator is Operator.EQUAL_TO:
        return ("equal", frozenset(statement.selected_codes) or statement.value)
    if operator in (
        Operator.CONTAINS_ANY,
        Operator.CONTAINS_ALL,
        Operator.GREATER_THAN,
    ):
        return ("value", None)
    return None


def _contradicts(left: tuple[str, object], right: tuple[str, object]) -> bool:
    kinds = {left[0], right[0]}
    if kinds == {"empty"} or kinds == {"refused"}:
        return False
    if "empty" in kinds or "refused" in kinds:
        # No answer cannot also be a given answer, and empty is not refused.
        return True
    if kinds == {"equal"}:
        return left[1] != right[1]
    return False


def _and_runs(statements: list[Statement]) -> Iterator[list[Statement]]:
    """Split a group's statements where ``Or`` joins them."""
    run: list[Statement] = []
    for statement in statements:
        if run and statement.stmt_bool is StmtBool.OR:
            yield run
            run = []
        run.append(statement)
    if run:
        yield run


def _check_unsatisfiable_conditions(document: LintTarget) -> Iterable[LintFinding]:
    """Report a logic group whose ``And``-joined statements contradict each other.

    On one subject: a value and ``Empty``, ``Empty`` and ``Refused``, a
    value and ``Refused``, or two different ``EqualTo`` values. Such a group
    can never be true.
    """
    context = _Context(document)
    lookup = None
    for entry in _conditions(context, *_CONDITIONAL):
        condition = entry.condition
        if not isinstance(condition, Condition):
            continue
        impossible: list[str] = []
        for number, group in enumerate(condition.logic_groups, 1):
            for run in _and_runs(group.statements):
                seen: dict[str, tuple[str, object]] = {}
                clash = None
                for statement in run:
                    kind = _statement_kind(statement)
                    if kind is None:
                        continue
                    previous = seen.get(statement.subject)
                    if previous is not None and _contradicts(previous, kind):
                        clash = statement
                        break
                    seen.setdefault(statement.subject, kind)
                if clash is not None:
                    lookup = lookup or context.lookup()
                    question, alias = _subject_names(clash, lookup)
                    key = _parse_urn(clash.subject)
                    subject = (
                        question or alias or (key[1][:8] if key else clash.subject)
                    )
                    impossible.append(f"group {number} ({subject})")
                    break
        if impossible:
            yield context.finding(
                "colectica.condition.unsatisfiable",
                "error",
                entry.command,
                f"{entry.where(context)} can never be true in "
                f"{', '.join(impossible)}: the statements joined by And "
                "contradict each other on one subject.",
            )


def _check_native_conditions(document: LintTarget) -> Iterable[LintFinding]:
    """Report native ``Blaise`` content that is not a valid condition or program.

    A condition (an ``IfThenElse``'s, a loop's, or that of a ``ComputationItem``
    with no output parameters, such as an edit check) should be one expression
    over the item's inputs: not statements (``goto``, ``set``, several lines).
    A ``ComputationItem`` with output parameters holds a program, which may
    span lines and assign its outputs. Neither should use typographic quotes
    outside a string or a ``{ comment }``, nor name in ``{{name}}`` anything
    but the item's parameters.
    """
    context = _Context(document)
    for entry in _conditions(context, *_CONDITIONAL):
        condition = entry.condition
        if not isinstance(condition, NativeCondition):
            continue
        if not condition.language.lower().startswith("blaise"):
            continue
        text = condition.text
        code = _code_only(text)
        outputs: set[str] = set()
        if _local(entry.item.tag) == "ComputationItem":
            parameters = _parameters(context, entry.item, "OutParameter")
            outputs = {alias for _, alias in parameters}
        problems: list[str] = []
        lines = [
            line
            for line in _code_only(text, keep_strings=True).splitlines()
            if line.strip()
        ]
        statements = re.search(r"(?i)\bgoto\b", code) or re.search(
            r"(?im)^\s*set\s", code
        )
        if outputs:
            what = "a valid program"
            if statements:
                problems.append("it contains goto or set, which Blaise does not have")
        else:
            what = "a single valid expression"
            if len(lines) > 1:
                problems.append(f"it spans {len(lines)} lines")
            if statements:
                problems.append("it contains statements (goto/set), not an expression")
        if _TYPOGRAPHIC_QUOTES.search(code):
            problems.append("it uses typographic quotes")
        known = {alias for _, alias in _inputs(context, entry.item)} | outputs
        undeclared = sorted(
            {name for name in _NATIVE_INPUT.findall(text) if name not in known}
        )
        if undeclared:
            whose = "inputs or outputs" if outputs else "inputs"
            problems.append(
                f"it names {', '.join(undeclared)}, not {whose} of the item"
            )
        if problems:
            yield context.finding(
                "colectica.condition.native-invalid",
                "error",
                entry.command,
                f"{entry.where(context)} has {condition.language} code that is not "
                f"{what}: {'; '.join(problems)}.",
            )


def _check_unused_inputs(document: LintTarget) -> Iterable[LintFinding]:
    """Report input parameters of an ``IfThenElse`` its conditions never use.

    The inputs are the ``IfThenElse``'s, and its ``ElseIf`` branches test
    them too: an input only a branch uses is used, and so is one the item
    binds onward, to what its branches hold. An item with an empty,
    unreadable or data-lookup condition in any branch is left alone.
    """
    context = _Context(document)
    entries_by_item = groupby(
        _conditions(context, "IfThenElse"), key=lambda entry: id(entry.item)
    )
    for _, group in entries_by_item:
        entries = list(group)
        main = entries[0]
        inputs = _inputs(context, main.item)
        conditions = [entry.condition for entry in entries]
        if not inputs or main.branch or any(c is None for c in conditions):
            continue
        if not isinstance(main.condition, (Condition, NativeCondition)):
            continue
        # An empty branch is reported by its own rule, and a lookup names
        # fields rather than inputs: what either tests is unknown, so no input
        # can be called unused.
        if any(
            isinstance(c, DataLookup) or (isinstance(c, Condition) and c.is_empty)
            for c in conditions
        ):
            continue
        used: set[tuple[str, str] | None] = set()
        for condition in conditions:
            used |= _used_inputs(condition, inputs)
        used |= _passed_on(context, main.item)
        unused = [alias for key, alias in inputs if key not in used]
        if unused:
            whose = "its condition never uses"
            if len(entries) > 1:
                whose = "its conditions never use"
            yield context.finding(
                "colectica.condition.unused-inputs",
                "warning",
                main.command,
                f"{context.describe(main.item)} has {len(unused)} input(s) "
                f"{whose}: {', '.join(unused)}.",
            )


def _passed_on(context: _Context, item: Element) -> set[tuple[str, str] | None]:
    """Keys of the parameters ``item``'s own bindings take their value from."""
    keys: set[tuple[str, str] | None] = set()
    for binding in item.findall(context.r("Binding")):
        source = binding.find(context.r("SourceParameterReference"))
        if source is None:
            continue
        agency = source.findtext(context.r("Agency"))
        identifier = source.findtext(context.r("ID"))
        if agency and identifier:
            keys.add((agency, identifier))
    return keys


def _check_stale_synopses(document: LintTarget) -> Iterable[LintFinding]:
    """Report a stored synopsis that does not name a subject the logic tests.

    Colectica stores the synopsis its editor last showed; a synopsis naming
    another variable, or missing while the condition has statements, no
    longer describes the logic. The message gives the synopsis rendered from
    the logic (see `ddi_l.colectica_logic.render_synopsis`).
    """
    context = _Context(document)
    lookup = None
    for entry in _conditions(context, *_CONDITIONAL):
        condition = entry.condition
        if not isinstance(condition, Condition) or condition.is_empty:
            continue
        lookup = lookup or context.lookup()
        stored = condition.synopsis or ""
        missing: list[str] = []
        for statement in condition.statements:
            names = [name for name in _subject_names(statement, lookup) if name]
            if names and not any(
                re.search(rf"(?<![\w.]){re.escape(name)}(?![\w.])", stored)
                for name in names
            ):
                missing.append(names[0])
        if not stored.strip() or missing:
            reason = (
                "there is no stored synopsis"
                if not stored.strip()
                else "the stored synopsis does not name "
                + ", ".join(dict.fromkeys(missing))
            )
            yield context.finding(
                "colectica.condition.synopsis-stale",
                "info",
                entry.command,
                f"{entry.where(context)}: {reason}; the logic reads "
                f'"{_first(render_synopsis(condition, lookup), 200)}".',
            )


def _children(context: _Context, sequence: Element) -> list[Element]:
    found = []
    for reference in sequence:
        if _local(reference.tag) == "ControlConstructReference":
            target = context.resolve(reference)
            if target is not None:
                found.append(target)
    return found


def _check_partial_gates(document: LintTarget) -> Iterable[LintFinding]:
    """Report a gate that wraps only the first construct of a page.

    *Heuristic.*

    The ``IfThenElse`` holds a single construct in its Then branch, more
    constructs follow it unconditionally in the same sequence, it has no
    Else branch, and its description says it routes to a page (see
    ``gate_description_patterns``): the gate probably should wrap the whole
    page.
    """
    context = _Context(document)
    patterns = [
        re.compile(p) for p in get_lint_configuration().gate_description_patterns
    ]
    if not patterns:
        return
    for sequence in context.items_of_type("Sequence"):
        children = _children(context, sequence)
        for index, child in enumerate(children):
            if _local(child.tag) != "IfThenElse" or index == len(children) - 1:
                continue
            if any(
                _local(c.tag) in ("ElseConstructReference", "ElseIf") for c in child
            ):
                continue
            then = next(
                (c for c in child if _local(c.tag) == "ThenConstructReference"), None
            )
            branch = None if then is None else context.resolve(then)
            if branch is None:
                continue
            inside = (
                _children(context, branch)
                if _local(branch.tag) == "Sequence"
                else [branch]
            )
            if len(inside) != 1:
                continue
            description = _description(context, child)
            if not any(pattern.search(description) for pattern in patterns):
                continue
            after = len(children) - index - 1
            yield context.finding(
                "colectica.ifthenelse.partial-gate",
                "warning",
                child,
                f"{context.describe(child)} gates only {context.describe(inside[0])}, "
                f"while the {after} construct(s) after it in "
                f"{context.describe(sequence)} show unconditionally; its "
                f'description reads "{_first(description)}". The gate probably '
                "should wrap the whole page.",
            )


# ---- Domains -----------------------------------------------------------------


def _check_codedomain_without_codelist(document: LintTarget) -> Iterable[LintFinding]:
    """Report a ``CodeDomain`` without an ``r:CodeListReference``.

    Grid cell domains included.
    """
    context = _Context(document)
    for item in context.items:
        for domain in item.iter():
            if _local(domain.tag) != "CodeDomain":
                continue
            if domain.find(context.r("CodeListReference")) is None:
                yield context.finding(
                    "colectica.codedomain.no-codelist",
                    "error",
                    domain,
                    f"{context.describe(item)} has a code domain with no code list.",
                )


def _domains(item: Element) -> Iterator[Element]:
    for node in item.iter():
        local = _local(node.tag)
        if local.endswith("Domain") or local.endswith("DomainReference"):
            yield node


def _check_domain_label_mismatch(document: LintTarget) -> Iterable[LintFinding]:
    """Report a domain label or item name naming another variable code.

    *Heuristic.*

    With ``variable_code_pattern`` set, the codes it matches in the item's
    output parameter alias are compared with those in its response domain
    labels and its names: a label naming only other codes was probably
    copied from another question.
    """
    pattern_text = get_lint_configuration().variable_code_pattern
    if not pattern_text:
        return
    pattern = re.compile(pattern_text)
    context = _Context(document)
    for item in context.items_of_type("QuestionItem", "QuestionGrid"):
        aliases = " ".join(
            (p.findtext(context.r("Alias")) or "")
            for p in item.findall(context.r("OutParameter"))
        )
        expected = set(pattern.findall(aliases))
        if not expected:
            continue
        texts: list[tuple[Element, str]] = []
        for domain in _domains(item):
            label = domain.find(context.r("Label"))
            if label is not None:
                texts.extend(
                    (node, node.text or "")
                    for node in label.iter()
                    if (node.text or "").strip()
                )
        for child in item:
            if _local(child.tag).endswith("Name"):
                texts.extend(
                    (node, node.text or "")
                    for node in child.iter()
                    if (node.text or "").strip()
                )
        seen: set[str] = set()
        for node, text in texts:
            found = set(pattern.findall(text))
            if text in seen:
                continue
            seen.add(text)
            if found and not found & expected:
                yield context.finding(
                    "colectica.domain.label-mismatch",
                    "warning",
                    node,
                    f'{context.describe(item)}: "{_first(text, 60)}" names '
                    f"{', '.join(sorted(found))}, but its output is "
                    f"{', '.join(sorted(expected))}.",
                )


# Interrogatives, by language: generic language data.
_NOT_A_DATE = {"en": {"why"}, "fr": {"pourquoi"}}
_NOT_A_DATE_UNLESS_DATED = {
    "en": {"what", "which"},
    "fr": {"quel", "quelle", "quels", "quelles"},
}
_A_DATE = {"en": {"when"}, "fr": {"quand"}}
_DATE_WORDS = {
    "en": re.compile(r"(?i)\b(date|day|month|year|birth|time)\b"),
    "fr": re.compile(r"(?i)\b(date|jour|mois|année|an|naissance|heure)\b"),
}


def _first_word(text: str) -> str:
    match = re.search(r"[^\W\d_]+", text)
    return match.group(0).casefold() if match else ""


def _check_domain_type_mismatch(document: LintTarget) -> Iterable[LintFinding]:
    """Report a question whose wording does not fit its domain type.

    *Heuristic.*

    A question opening with *Why* (*Pourquoi*), or *What*/*Which*
    (*Quel*...) without a date word, whose answer is a date; or one opening
    with *When* (*Quand*) whose answer is a code or text.
    """
    context = _Context(document)
    for item in context.items_of_type("QuestionItem"):
        kinds = {
            _local(domain.tag).removesuffix("Reference") for domain in _domains(item)
        }
        is_date = bool(kinds & {"DateTimeDomain"})
        is_code_or_text = bool(kinds & {"CodeDomain", "TextDomain"}) and not is_date
        if not (is_date or is_code_or_text):
            continue
        questions = [c for c in item if _local(c.tag) == "QuestionText"]
        texts = [entry for question in questions for entry in _texts(question)]
        for node, raw, tag in texts:
            language = tag.split("-")[0].casefold()
            text = raw.strip()
            if language not in _A_DATE:
                continue
            word = _first_word(text)
            mismatch = None
            if is_date and (
                word in _NOT_A_DATE[language]
                or (
                    word in _NOT_A_DATE_UNLESS_DATED[language]
                    and not _DATE_WORDS[language].search(text)
                )
            ):
                mismatch = "a date"
            elif is_code_or_text and word in _A_DATE[language]:
                mismatch = "a code or text, not a date"
            if mismatch:
                yield context.finding(
                    "colectica.domain.type-mismatch",
                    "warning",
                    node,
                    f'{context.describe(item)} asks "{_first(text, 60)}" but its '
                    f"answer is {mismatch}.",
                )
                break


# ---- Languages and text ---------------------------------------------------------


def _languages(elements: Iterable[Element]) -> set[str]:
    return {language for element in elements for _, _, language in _texts(element)}


def _check_missing_languages(document: LintTarget) -> Iterable[LintFinding]:
    """Report text missing a language listed in ``required_languages``.

    Question texts, statement display texts, category labels and numeric or
    text domain labels are errors; a condition's description is info.
    Nothing runs until ``required_languages`` is configured.
    """
    required = get_lint_configuration().required_languages
    if not required:
        return
    context = _Context(document)

    def check(
        item: Element, elements: list[Element], what: str, severity: str
    ) -> Iterator[LintFinding]:
        if not elements:
            return
        present = _languages(elements)
        absent = [
            language
            for language in required
            if not any(_language_range_matches(language, tag) for tag in present)
        ]
        # Text without a letter ("1914", "0-99") reads the same in every
        # language, so a missing translation of it is no defect.
        letters = any(
            re.search(r"[^\W\d_]", text)
            for element in elements
            for _, text, _ in _texts(element)
        )
        if absent and letters:
            yield context.finding(
                "i18n.missing-language",
                severity,
                elements[0],
                f"{context.describe(item)}: {what} has no {', '.join(absent)}.",
            )

    for item in context.items:
        local = _local(item.tag)
        children = [child for child in item if isinstance(child.tag, str)]

        def named(name: str, among: list[Element] = children) -> list[Element]:
            return [child for child in among if _local(child.tag) == name]

        yield from check(item, named("QuestionText"), "the question text", "error")
        if local == "StatementItem":
            yield from check(item, named("DisplayText"), "the display text", "error")
        if local == "Category":
            yield from check(item, named("Label"), "the label", "error")
        for condition in named("IfCondition"):
            description = condition.find(context.r("Description"))
            if description is not None:
                yield from check(
                    item, [description], "the condition description", "info"
                )
        for domain in _domains(item):
            if _local(domain.tag) in ("NumericDomain", "TextDomain"):
                yield from check(
                    item, named("Label", list(domain)), "the domain label", "error"
                )


def _check_placeholders(document: LintTarget) -> Iterable[LintFinding]:
    """Report template placeholders left in text (``placeholder_patterns``)."""
    patterns = [re.compile(p) for p in get_lint_configuration().placeholder_patterns]
    if not patterns:
        return
    context = _Context(document)
    for item, node, text, language in context.texts():
        for pattern in patterns:
            for match in pattern.finditer(text):
                yield context.finding(
                    "text.placeholder-unresolved",
                    "warning",
                    node,
                    f"{context.describe(item)}: unresolved placeholder "
                    f'"{_first(match.group(0), 60)}" in {language} text.',
                )


def _check_ui_chrome(document: LintTarget) -> Iterable[LintFinding]:
    """Report user-interface words pasted into content (``ui_chrome_tokens``).

    Tokens match whole, case-insensitively. The default list is empty: the
    words depend on the application the mock-ups came from.
    """
    tokens = get_lint_configuration().ui_chrome_tokens
    if not tokens:
        return
    pattern = re.compile(
        "|".join(rf"(?<!\w){re.escape(token)}(?!\w)" for token in tokens), re.IGNORECASE
    )
    context = _Context(document)
    for item, node, text, language in context.texts():
        found = sorted({match.group(0) for match in pattern.finditer(text)})
        if found:
            yield context.finding(
                "text.ui-chrome",
                "warning",
                node,
                f"{context.describe(item)}: user-interface text "
                f"{', '.join(repr(token) for token in found)} in "
                f"{language} content.",
            )


def _pipe_problem(name: str, prefixes: tuple[str, ...]) -> str | None:
    if not name.strip():
        return "is empty"
    if re.search(r"\s", name):
        return "contains white space"
    if any(name == prefix or f"{name}_" == prefix for prefix in prefixes):
        return "is only a prefix"
    return None


def _check_malformed_pipes(document: LintTarget) -> Iterable[LintFinding]:
    """Report a ``#{...}`` pipe that is empty, holds white space, or is a prefix."""
    prefixes = get_lint_configuration().pipe_prefixes
    context = _Context(document)
    for item, node, text, _ in context.texts():
        for match in _PIPE.finditer(text):
            problem = _pipe_problem(match.group(1), prefixes)
            if problem:
                yield context.finding(
                    "text.pipe-malformed",
                    "error",
                    node,
                    f"{context.describe(item)}: the pipe {match.group(0)!r} {problem}.",
                )


def _names_and_pipes(
    context: _Context, item: Element
) -> tuple[set[str], list[tuple[Element, str]]]:
    """The names ``item`` declares, and the names it pipes.

    A name is declared by a parameter alias or a data lookup field.
    """
    names = set()
    for alias in item.iter(context.r("Alias")):
        if (alias.text or "").strip():
            names.add(alias.text.strip())  # type: ignore[union-attr]
    if _local(item.tag) in _CONDITIONAL:
        for entry in _item_conditions(context, item):
            if isinstance(entry.condition, DataLookup):
                names.update(field.name for field in entry.condition.fields)
    pipes = [
        (node, match.group(1))
        for node, text, _ in _texts(item)
        for match in _PIPE.finditer(text)
    ]
    return names, pipes


def _check_undeclared_pipes(document: LintTarget) -> Iterable[LintFinding]:
    """Report a piped ``#{name}`` that nothing in the file declares.

    A name is declared by a data lookup field, a parameter alias, or
    ``known_names`` (what the run-time system supplies; ``--known-names
    FILE``). ``pipe_suffixes`` are stripped first.
    """
    configuration = get_lint_configuration()
    context = _Context(document)
    # What each item declares and pipes is read once while it is unchanged.
    read = _incremental.per_element(
        document, "names-and-pipes", context.items, partial(_names_and_pipes, context)
    )
    declared = set(configuration.known_names).union(*(names for names, _ in read))
    for item, (_, pipes) in zip(context.items, read, strict=True):
        reported: set[str] = set()
        for node, name in pipes:
            if _pipe_problem(name, configuration.pipe_prefixes) or name in reported:
                continue
            suffixes = configuration.pipe_suffixes
            bare = next((name[: -len(s)] for s in suffixes if name.endswith(s)), name)
            if name in declared or bare in declared:
                continue
            reported.add(name)
            yield context.finding(
                "text.pipe-undeclared",
                "warning",
                node,
                f"{context.describe(item)} pipes #{{{name}}}, which no lookup "
                "field, parameter or known name declares.",
            )


# ---- Data lookups and aliases ------------------------------------------------------


def _lookups(context: _Context) -> Iterator[tuple[Element, Element, DataLookup]]:
    for entry in _conditions(context, *_CONDITIONAL):
        if isinstance(entry.condition, DataLookup):
            yield entry.item, entry.command, entry.condition


def _check_duplicate_lookup_fields(document: LintTarget) -> Iterable[LintFinding]:
    """Report a name listed twice in one data lookup's fields."""
    context = _Context(document)
    for item, command, lookup in _lookups(context):
        counts = Counter(entry.name for entry in lookup.fields)
        for name, count in counts.items():
            if count > 1:
                yield context.finding(
                    "colectica.lookup.duplicate-field",
                    "error",
                    command,
                    f"{context.describe(item)} lists the lookup field {name!r} "
                    f"{count} times.",
                )


def _check_suspicious_lookup_fields(document: LintTarget) -> Iterable[LintFinding]:
    """Report a lookup field never assigned, or named like a value.

    *Heuristic.*

    A field whose name starts with a digit is more likely a value typed into
    the wrong place than a field.
    """
    context = _Context(document)
    for item, command, lookup in _lookups(context):
        for entry in lookup.fields:
            reasons = []
            if entry.is_assigned is False:
                reasons.append("is not assigned")
            if entry.name[:1].isdigit():
                reasons.append("is named like a value")
            if reasons:
                yield context.finding(
                    "colectica.lookup.suspicious-field",
                    "warning",
                    command,
                    f"{context.describe(item)}: the lookup field {entry.name!r} "
                    f"{' and '.join(reasons)}.",
                )


def _check_unlisted_lookup_outputs(document: LintTarget) -> Iterable[LintFinding]:
    """Report a data lookup output its field list does not hold.

    Colectica gives a data lookup one ``r:OutParameter`` per field, whose ID
    is the field's ``Identifier`` and whose alias is the field's ``Name``. An
    output no field lists carries no value, and one named otherwise hands its
    field on under another name, so whatever binds it reads the wrong thing.
    A field written without an ``Identifier`` is matched by its name.
    """
    context = _Context(document)
    for item, _command, lookup in _lookups(context):
        by_id = {
            str(entry.identifier): entry.name
            for entry in lookup.fields
            if entry.identifier not in (None, "")
        }
        by_name = {
            entry.name for entry in lookup.fields if entry.identifier in (None, "")
        }
        for parameter in item.findall(context.r("OutParameter")):
            identifier = (parameter.findtext(context.r("ID")) or "").strip()
            alias = (parameter.findtext(context.r("Alias")) or "").strip()
            if identifier in by_id:
                if by_id[identifier] == alias:
                    continue
                message = (
                    f"the output {alias!r} is the lookup field "
                    f"{by_id[identifier]!r} under another name."
                )
            elif alias in by_name:
                continue
            else:
                message = f"the output {alias!r} is not one of its lookup fields."
            yield context.finding(
                "colectica.lookup.unlisted-output",
                "error",
                parameter,
                f"{context.describe(item)}: {message}",
            )


def _aliases(context: _Context) -> Iterator[tuple[Element, Element, str]]:
    for item in context.items:
        for parameter in item.iter():
            if _local(parameter.tag) not in ("InParameter", "OutParameter"):
                continue
            alias = (parameter.findtext(context.r("Alias")) or "").strip()
            if alias:
                yield item, parameter, alias


def _check_compounded_escapes(document: LintTarget) -> Iterable[LintFinding]:
    """Report an alias whose XML escape was escaped again (``_x005F_``).

    Escaping a name that already holds an escape turns its underscore into
    ``_x005F_``, and each further pass doubles it: the alias grows on every
    propagation and becomes an unusable variable name.
    """
    context = _Context(document)
    for item, parameter, alias in _aliases(context):
        runs = [
            len(match.group(1)) // len("x005F_")
            for match in _COMPOUNDED_ESCAPE.finditer(alias)
        ]
        if runs:
            yield context.finding(
                "colectica.alias.escape-compounded",
                "error",
                parameter,
                f"{_local(parameter.tag)} {context.short_id(parameter)} of "
                f"{context.describe(item)} has an alias escaped {max(runs) + 1} "
                f"times over ({len(alias)} characters): {_first(alias, 60)!r}.",
            )


def _check_malformed_aliases(document: LintTarget) -> Iterable[LintFinding]:
    """Report an alias with an XML escape, too long, or made of text.

    *Heuristic.*

    Compounded escapes are reported by ``colectica.alias.escape-compounded``.
    """
    context = _Context(document)
    for item, parameter, alias in _aliases(context):
        if _COMPOUNDED_ESCAPE.search(alias):
            continue
        reasons = []
        if _XML_ESCAPE.search(alias):
            reasons.append("holds an XML escape")
        if len(alias) > _MAX_ALIAS_LENGTH:
            reasons.append(f"is {len(alias)} characters long")
        if _CONCATENATED_TEXT.search(alias):
            reasons.append("looks like concatenated question text")
        if reasons:
            yield context.finding(
                "colectica.alias.malformed",
                "warning",
                parameter,
                f"{_local(parameter.tag)} {context.short_id(parameter)} of "
                f"{context.describe(item)}: the alias {_first(alias, 60)!r} "
                f"{' and '.join(reasons)}.",
            )


def _check_logic_notes(document: LintTarget) -> Iterable[LintFinding]:
    """Report a statement that is a design note shown as content.

    *Heuristic.*

    Its name or display text matches ``logic_note_patterns`` ("Flow
    condition: ...", "Display condition", ...). A statement Colectica types as
    a Note (``extension:TypeOfStatement`` = ``Note``) is not shown, so it is
    where such a note belongs and is not reported.
    """
    patterns = [re.compile(p) for p in get_lint_configuration().logic_note_patterns]
    if not patterns:
        return
    context = _Context(document)
    for item in context.items_of_type("StatementItem"):
        if _attribute(item, "extension:TypeOfStatement") == "Note":
            continue
        for child in item:
            if _local(child.tag) not in ("ConstructName", "DisplayText"):
                continue
            for node in child.iter():
                text = (node.text or "").strip()
                if text and any(pattern.search(text) for pattern in patterns):
                    yield context.finding(
                        "colectica.statement.logic-note",
                        "warning",
                        node,
                        f'{context.describe(item)} reads "{_first(text, 60)}": a '
                        "design note shown to respondents as content.",
                    )
                    break
            else:
                continue
            break


# ---- Flow -------------------------------------------------------------------------

_FLOW_REFERENCES = (
    "ControlConstructReference",
    "ThenConstructReference",
    "ElseConstructReference",
    "UntilConstructReference",
    "WhileConstructReference",
)
_LOOPS = ("Loop", "RepeatUntil", "RepeatWhile")


def _flow_children(context: _Context, construct: Element) -> list[Element]:
    """The constructs ``construct`` leads to, in document order."""
    return shared(
        "flow-children", construct, lambda: _resolved_children(context, construct)
    )


def _resolved_children(context: _Context, construct: Element) -> list[Element]:
    found = []
    for child in construct:
        local = _local(child.tag)
        if local == "ElseIf":
            references = [
                node for node in child if _local(node.tag) == "ThenConstructReference"
            ]
        else:
            references = [child] if local in _FLOW_REFERENCES else []
        for reference in references:
            target = context.resolve(reference)
            if target is not None:
                found.append(target)
    return found


def _reference_key(
    context: _Context, reference: Element | None
) -> tuple[str, str] | None:
    if reference is None:
        return None
    agency = reference.findtext(context.r("Agency"))
    identifier = reference.findtext(context.r("ID"))
    return (agency, identifier) if agency and identifier else None


@dataclass
class _Wiring:
    """Who declares each parameter, and the bindings, target to sources.

    ``bound`` is each holder's own bindings; ``sources`` is all of them.
    """

    owner: dict[tuple[str, str], Element] = field(default_factory=dict)
    bound: dict[int, dict[tuple[str, str], list[tuple[str, str]]]] = field(
        default_factory=dict
    )
    sources: dict[tuple[str, str], list[tuple[str, str]]] = field(default_factory=dict)

    @classmethod
    def of(cls, context: _Context) -> _Wiring:
        return shared("wiring", context.document.root, lambda: cls._built(context))

    @classmethod
    def _built(cls, context: _Context) -> _Wiring:
        wiring = cls()
        for item in context.items:
            for kind in ("InParameter", "OutParameter"):
                for key, _ in _parameters(context, item, kind):
                    if key is not None:
                        wiring.owner.setdefault(key, item)
            own = wiring.bound.setdefault(id(item), {})
            for binding in item.findall(context.r("Binding")):
                source = _reference_key(
                    context, binding.find(context.r("SourceParameterReference"))
                )
                target = _reference_key(
                    context, binding.find(context.r("TargetParameterReference"))
                )
                if source and target:
                    own.setdefault(target, []).append(source)
                    wiring.sources.setdefault(target, []).append(source)
        return wiring

    def producer(
        self, key: tuple[str, str], seen: frozenset[tuple[str, str]] = frozenset()
    ) -> Element | None:
        """The question construct or computation whose output ``key`` carries."""
        owner = self.owner.get(key)
        if owner is None or key in seen:
            return None
        if _local(owner.tag) in ("QuestionConstruct", "ComputationItem"):
            return owner
        # A container re-exporting the output of one of its children.
        for source in self.bound.get(id(owner), {}).get(key, []):
            if self.owner.get(source) is not owner:
                found = self.producer(source, seen | {key})
                if found is not None:
                    return found
        return None

    def source_on(
        self, key: tuple[str, str], path: tuple[Element, ...]
    ) -> Element | None:
        """What produces the input ``key`` of ``path[-1]``'s child, on ``path``.

        Each container's binding of the input is followed up the path, to the
        output of an earlier sibling that carries it.
        """
        for holder in reversed(path):
            sources = self.bound.get(id(holder), {}).get(key, [])
            if not sources:
                return None
            source = sources[0]
            if self.owner.get(source) is not holder:
                return self.producer(source)
            key = source
        return None

    def answer(
        self, key: tuple[str, str]
    ) -> tuple[Element, tuple[str, str]] | tuple[None, None]:
        """The question item, and its output, that a parameter's value comes from."""
        seen: set[tuple[str, str]] = set()
        queue = [key]
        while queue:
            current = queue.pop(0)
            if current in seen:
                continue
            seen.add(current)
            owner = self.owner.get(current)
            if owner is not None and _local(owner.tag) in (
                "QuestionItem",
                "QuestionGrid",
            ):
                return owner, current
            queue.extend(self.sources.get(current, []))
        return None, None


def _flow_roots(context: _Context) -> list[Element]:
    """Where the flow starts: each instrument, or each construct nothing leads to."""
    instruments = list(context.items_of_type("Instrument"))
    if instruments:
        return instruments
    reached = {
        id(child) for item in context.items for child in _flow_children(context, item)
    }
    return [
        item
        for item in context.items
        if _local(item.tag) in ("Sequence", "IfThenElse", *_LOOPS)
        and id(item) not in reached
    ]


def _reads(context: _Context) -> dict[int, list[tuple[tuple[str, str], str]]]:
    """The inputs each item reads (not those it only passes on), by item."""
    return shared("reads", context.document.root, lambda: _read_inputs(context))


def _read_inputs(context: _Context) -> dict[int, list[tuple[tuple[str, str], str]]]:
    used: dict[int, set[tuple[str, str] | None]] = {}
    for entry in _conditions(context, "IfThenElse", *_LOOPS):
        used.setdefault(id(entry.item), set()).update(
            _used_inputs(entry.condition, _inputs(context, entry.item))
        )
    reads: dict[int, list[tuple[tuple[str, str], str]]] = {}
    for item in context.items:
        kind = _local(item.tag)
        inputs = [(key, alias) for key, alias in _inputs(context, item) if key]
        if kind == "IfThenElse" or kind in _LOOPS:
            tested = used.get(id(item), set())
            count = _attribute(
                item, "extension:DynamicIterationCountParameterIdentifier"
            )
            reads[id(item)] = [
                (key, alias)
                for key, alias in inputs
                if key in tested or key[1] == count
            ]
        elif kind in ("ComputationItem", "QuestionConstruct", "StatementItem"):
            reads[id(item)] = inputs
    return reads


def _check_read_before_computed(document: LintTarget) -> Iterable[LintFinding]:
    """Report an item that reads a value asked or computed later in the flow.

    A condition, a fill or a computation can only read what an earlier
    question or computation produced: Colectica Designer's routing view
    reports a later source as broken. The flow is walked in document order,
    an item reached by several paths (a page reused by several exits, say)
    once on each, and each input is followed through the bindings of the
    containers on that path to the question construct or computation that
    produces it. An input with no binding is left to other rules.

    With the ``logic`` extra, the solver also asks whether a respondent can
    reach the item before the question or computation: if so, the finding
    gives one; if not, it is ``info``, since only the routing view is
    affected.
    """
    context = _Context(document)
    wiring = _Wiring.of(context)
    reads = _reads(context)
    parents = Counter(
        id(child) for item in context.items for child in _flow_children(context, item)
    )
    for root in _flow_roots(context):
        report = partial(_read_before_finding, context, _routing(context, root))
        walk = _ReadWalk(context, wiring, reads, parents, report)
        try:
            if walk.cyclic(root):
                raise RecursionError
            found = list(walk.first(root, (), None))
        except RecursionError:
            # A cycle, or a flow too deep to recurse: walk every path.
            found = list(
                _read_before_computed_by_path(
                    context, wiring, reads, parents, root, report
                )
            )
        yield from found


def _routing(context: _Context, root: Element) -> Any | None:
    """The flow from ``root`` for the solver (`ddi_l.spec._routing`).

    ``None`` without the ``logic`` extra, or when the document has no gate.
    """
    from .spec.semantics import logic_available

    if not logic_available() or next(context.items_of_type("IfThenElse"), None) is None:
        return None
    from .spec._routing import Routing

    return shared("routing", root, lambda: Routing(context, root))


def _read_before_finding(
    context: _Context,
    routing: Any | None,
    element: Element,
    producer: Element,
    message: str,
) -> LintFinding:
    """A ``colectica.flow.read-before-computed`` finding, with a respondent."""
    severity = "warning"
    if routing is not None:
        found = routing.respondent_before(element, producer)
        if found is False:
            severity = "info"
            message += (
                " No respondent reaches it before then, so only Designer's "
                "routing view reports it."
            )
        elif found is not None and found.answers:
            message += f" For example, when {found.describe()}."
    return context.finding(
        "colectica.flow.read-before-computed", severity, element, message
    )


def _check_unreachable(document: LintTarget) -> Iterable[LintFinding]:
    """Report a construct no respondent reaches.

    The gates on every way to it cannot all hold, for any answers: its
    ask-condition, the disjunction over the ways to it of the gates'
    conjunction, is unsatisfiable. Only the first construct on a way is
    reported, not those below it. A condition this rule cannot read (a data
    lookup, code in another language) may hold or not, and a loop's body
    counts as reached. Needs the ``logic`` extra: without it, a flow with a
    gate gets one ``info`` finding that it was not checked.
    """
    context = _Context(document)
    gate = next(context.items_of_type("IfThenElse"), None)
    if gate is None:
        return
    for root in _flow_roots(context):
        routing = _routing(context, root)
        if routing is None:
            yield context.finding(
                "colectica.flow.unreachable",
                "info",
                root,
                f"{context.describe(root)} was not checked for constructs no "
                "respondent reaches: that needs the logic extra (pip install "
                '"ddi-l[logic]").',
            )
            continue
        for element in routing.unreachable():
            yield context.finding(
                "colectica.flow.unreachable",
                "warning",
                element,
                f"{context.describe(element)} is never reached: no answers meet "
                "the gates on every way to it.",
            )


# How a finding replayed from a construct reached again names its path:
# through the construct it was reached from, or as the path above says.
_THROUGH_CALLER = "through the caller"
_AS_ABOVE = "as above"


class _ReadWalk:
    """`_check_read_before_computed` for one flow root, without enumerating paths.

    A construct is walked in full the first time it is reached. Reached
    again by another path, all below it is reached already, so what it
    reports depends only on where its own inputs come from above it and on
    the producers reached so far: worked out once for each of those, it is
    replayed rather than walked again. Findings and their order are those of
    walking every path (`_read_before_computed_by_path`).
    """

    def __init__(
        self,
        context: _Context,
        wiring: _Wiring,
        reads: dict[int, list[tuple[tuple[str, str], str]]],
        parents: Counter[int],
        report: Any,
    ) -> None:
        self.context, self.wiring, self.reads, self.parents = (
            context,
            wiring,
            reads,
            parents,
        )
        self.report = report
        self.owned: dict[int, list[tuple[str, str]]] = {}
        for key, owner in wiring.owner.items():
            self.owned.setdefault(id(owner), []).append(key)
        self.reached: set[int] = set()
        self.producers = 0
        self.reported: set[tuple[int, tuple[str, str]]] = set()
        self.memo: dict[tuple[Any, ...], list[tuple[Any, ...]]] = {}

    def children(self, element: Element) -> list[Element]:
        return [
            child
            for child in _flow_children(self.context, element)
            if child is not element
        ]

    def cyclic(self, root: Element) -> bool:
        """Whether the flow below ``root`` loops back on itself."""
        open_: set[int] = {id(root)}
        done: set[int] = set()
        stack = [(root, iter(self.children(root)))]
        while stack:
            element, pending = stack[-1]
            child = next(pending, None)
            if child is None:
                stack.pop()
                open_.discard(id(element))
                done.add(id(element))
            elif id(child) in open_:
                return True
            elif id(child) not in done:
                open_.add(id(child))
                stack.append((child, iter(self.children(child))))
        return False

    def first(
        self, element: Element, path: tuple[Element, ...], via: Element | None
    ) -> Iterator[LintFinding]:
        """Walk ``element``, reached for the first time, and all below it.

        ``via`` is the construct a finding at ``element`` names as the one it
        was reached through.
        """
        self.reached.add(id(element))
        if _local(element.tag) in ("QuestionConstruct", "ComputationItem"):
            self.producers += 1
        if path:
            for key, alias in self.reads.get(id(element), ()):
                producer = self.wiring.source_on(key, path)
                if self._unreached(producer, element):
                    yield from self._emit(element, key, alias, producer, via)
        chain = (*path, element)
        for child in self.children(element):
            child_via = element if self.parents[id(child)] > 1 else via
            if id(child) not in self.reached:
                yield from self.first(child, chain, child_via)
                continue
            above = {
                key: self.wiring.source_on(key, chain) for key in self._keys(child)
            }
            for found, key, alias, producer, named in self._again(child, above):
                if named == _THROUGH_CALLER:
                    named = element
                elif named == _AS_ABOVE:
                    named = via
                yield from self._emit(found, key, alias, producer, named)

    def _again(
        self, element: Element, above: dict[tuple[str, str], Element | None]
    ) -> list[tuple[Any, ...]]:
        """What ``element``, reached again, and all below it report.

        ``above`` is what each input ``element`` holds or reads is bound to
        above it. Each finding names its path as a construct, or as
        `_THROUGH_CALLER` or `_AS_ABOVE` for the caller to settle.
        """
        state = (
            id(element),
            tuple(
                sorted(
                    (key, None if producer is None else id(producer))
                    for key, producer in above.items()
                )
            ),
            self.producers,
        )
        cached = self.memo.get(state)
        if cached is not None:
            return cached
        found: dict[tuple[int, tuple[str, str]], tuple[Any, ...]] = {}

        def add(
            item: Element,
            key: tuple[str, str],
            alias: str,
            producer: Element | None,
            named: object,
        ) -> None:
            if self._unreached(producer, item):
                found.setdefault((id(item), key), (item, key, alias, producer, named))

        shared_here = self.parents[id(element)] > 1
        for key, alias in self.reads.get(id(element), ()):
            add(
                element,
                key,
                alias,
                above.get(key),
                _THROUGH_CALLER if shared_here else _AS_ABOVE,
            )
        for child in self.children(element):
            below = {key: self._bound(key, element, above) for key in self._keys(child)}
            for item, key, alias, producer, named in self._again(child, below):
                if named == _THROUGH_CALLER:
                    named = element
                elif named == _AS_ABOVE:
                    named = _THROUGH_CALLER if shared_here else _AS_ABOVE
                add(item, key, alias, producer, named)
        result = list(found.values())
        self.memo[state] = result
        return result

    def _keys(self, element: Element) -> set[tuple[str, str]]:
        """The inputs whose sources above ``element`` its subtree may need."""
        return {
            *self.owned.get(id(element), ()),
            *(k for k, _ in self.reads.get(id(element), ())),
        }

    def _bound(
        self,
        key: tuple[str, str],
        holder: Element,
        above: dict[tuple[str, str], Element | None],
    ) -> Element | None:
        """`_Wiring.source_on` for a child of ``holder``, given ``above``."""
        sources = self.wiring.bound.get(id(holder), {}).get(key, [])
        if not sources:
            return None
        source = sources[0]
        if self.wiring.owner.get(source) is not holder:
            return self.wiring.producer(source)
        return above.get(source)

    def _unreached(self, producer: Element | None, reader: Element) -> bool:
        return (
            producer is not None
            and producer is not reader
            and id(producer) not in self.reached
        )

    def _emit(
        self,
        element: Element,
        key: tuple[str, str],
        alias: str,
        producer: Element | None,
        via: object,
    ) -> Iterator[LintFinding]:
        if (id(element), key) in self.reported or producer is None:
            return
        self.reported.add((id(element), key))
        through = (
            f", reached through {self.context.describe(via)},"
            if isinstance(via, Element)
            else ""
        )
        verb = "asks" if _local(producer.tag) == "QuestionConstruct" else "computes"
        yield self.report(
            element,
            producer,
            f"{self.context.describe(element)}{through} reads {alias} before "
            f"{self.context.describe(producer)} {verb} it.",
        )


def _read_before_computed_by_path(
    context: _Context,
    wiring: _Wiring,
    reads: dict[int, list[tuple[tuple[str, str], str]]],
    parents: Counter[int],
    root: Element,
    report: Any,
) -> Iterator[LintFinding]:
    """Walk every path from ``root``: the walk a cyclic flow still needs."""
    reached: set[int] = set()
    reported: set[tuple[int, tuple[str, str]]] = set()
    stack: list[tuple[Element, tuple[Element, ...]]] = [(root, ())]
    while stack:
        element, path = stack.pop()
        reached.add(id(element))
        for key, alias in reads.get(id(element), ()):
            if not path or (id(element), key) in reported:
                continue
            producer = wiring.source_on(key, path)
            if producer is None or producer is element or id(producer) in reached:
                continue
            reported.add((id(element), key))
            chain = (*path, element)
            via = next(
                (
                    f", reached through {context.describe(chain[index - 1])},"
                    for index in range(len(chain) - 1, 0, -1)
                    if parents[id(chain[index])] > 1
                ),
                "",
            )
            verb = "asks" if _local(producer.tag) == "QuestionConstruct" else "computes"
            yield report(
                element,
                producer,
                f"{context.describe(element)}{via} reads {alias} before "
                f"{context.describe(producer)} {verb} it.",
            )
        children = [
            child
            for child in _flow_children(context, element)
            if child is not element and all(child is not node for node in path)
        ]
        # Depth first, in document order.
        stack.extend((child, (*path, element)) for child in reversed(children))


def _check_multi_answer_subjects(document: LintTarget) -> Iterable[LintFinding]:
    """Report a gate whose condition tests one answer of a multi-answer question.

    Colectica Designer's routing view reports a condition on one answer of a
    question with several (a ``StructuredMixedResponseDomain``) as broken,
    even when the answer's output is restated in its domain; a condition on a
    question with one answer resolves. Ask that answer as a question of its
    own.
    """
    context = _Context(document)
    wiring = _Wiring.of(context)
    for entry in _conditions(context, "IfThenElse", *_LOOPS):
        if not isinstance(entry.condition, Condition):
            continue
        inputs = _inputs(context, entry.item)
        for key in sorted(
            (key for key in _used_inputs(entry.condition, inputs) if key), key=str
        ):
            question, answer = wiring.answer(key)
            if question is None or answer is None:
                continue
            mixed = next(
                (
                    child
                    for child in question
                    if _local(child.tag) == "StructuredMixedResponseDomain"
                ),
                None,
            )
            domains = (
                [c for c in mixed if _local(c.tag) == "ResponseDomainInMixed"]
                if mixed is not None
                else []
            )
            if len(domains) < 2:
                continue
            outputs = [k for k, _ in _parameters(context, question, "OutParameter")]
            aliases = dict(_parameters(context, question, "OutParameter"))
            position = outputs.index(answer) + 1 if answer in outputs else None
            which = f"answer {position} of {len(domains)}" if position else "an answer"
            yield context.finding(
                "colectica.condition.multi-answer-question",
                "warning",
                entry.command,
                f"{entry.where(context)} tests {aliases.get(answer, answer[1][:8])}, "
                f"{which} of {context.describe(question)}: Designer's routing view "
                "reports a condition on one answer of a question with several as "
                "broken. Ask it as a question of its own.",
            )


# ---- Registration ---------------------------------------------------------------

_RULES = (
    (
        "colectica.identifiable.shared-id",
        _check_shared_ids,
        "error",
        (
            "OutParameter 33333333 is declared in 2 items: QuestionItem "
            "11111111 (PetKind), QuestionItem 22222222 (PetKind)."
        ),
    ),
    (
        "colectica.binding.dangling",
        _check_dangling_bindings,
        "error",
        (
            "A binding in Sequence 77777777 (Pet survey) has a source "
            "OutParameter 99999999 that is not declared in this file."
        ),
    ),
    (
        "colectica.condition.malformed",
        _check_malformed_conditions,
        "error",
        (
            "IfThenElse 33333333 (Cat owners): Neutral command is not valid "
            "JSON: Expecting value (line 1, column 1)."
        ),
    ),
    (
        "colectica.condition.empty",
        _check_empty_conditions,
        "error",
        (
            "IfThenElse 33333333 (Cat owners) has an empty condition; its "
            'description reads "Show when a cat lives here.".'
        ),
    ),
    (
        "colectica.condition.unsatisfiable",
        _check_unsatisfiable_conditions,
        "error",
        (
            "IfThenElse 33333333 (No pets) can never be true in group 1 "
            "(PetCount): the statements joined by And contradict each other on "
            "one subject."
        ),
    ),
    (
        "colectica.condition.native-invalid",
        _check_native_conditions,
        "error",
        (
            "ComputationItem 66666666 (Many pets) has Blaise code that is not a"
            " single valid expression: it uses typographic quotes."
        ),
    ),
    (
        "colectica.condition.unused-inputs",
        _check_unused_inputs,
        "warning",
        (
            "IfThenElse 33333333 (Cat owners) has 1 input(s) its condition "
            "never uses: PetAge."
        ),
    ),
    (
        "colectica.condition.synopsis-stale",
        _check_stale_synopses,
        "info",
        (
            "IfThenElse 33333333 (Cat owners): the stored synopsis does not "
            'name PetKind; the logic reads "(PetKind contains all of 3 "Cat") '
            'and (PetCount > 2)".'
        ),
    ),
    (
        "colectica.ifthenelse.partial-gate",
        _check_partial_gates,
        "warning",
        (
            "IfThenElse 33333333 (Owner gate) gates only StatementItem 44444444"
            " (Welcome), while the 2 construct(s) after it in Sequence 55555555"
            ' (Owner page) show unconditionally; its description reads "If an '
            'owner, go to the owner page". The gate probably should wrap the '
            "whole page."
        ),
    ),
    (
        "colectica.codedomain.no-codelist",
        _check_codedomain_without_codelist,
        "error",
        ("QuestionGrid 11111111 (PetHours) has a code domain with no code list."),
    ),
    (
        "colectica.domain.label-mismatch",
        _check_domain_label_mismatch,
        "warning",
        (
            'QuestionItem 11111111 (P0012): "P0016" names P0016, but its output'
            " is P0012."
        ),
    ),
    (
        "colectica.domain.type-mismatch",
        _check_domain_type_mismatch,
        "warning",
        (
            'QuestionItem 11111111 (PetLeft) asks "Why did the pet leave?" but '
            "its answer is a date."
        ),
    ),
    (
        "i18n.missing-language",
        _check_missing_languages,
        "error (info for descriptions)",
        ("Category 22222222 (Bird): the label has no fr-CA."),
    ),
    (
        "text.placeholder-unresolved",
        _check_placeholders,
        "warning",
        (
            'StatementItem 44444444 (Welcome): unresolved placeholder "<<insert'
            ' pet name>>" in en-CA text.'
        ),
    ),
    (
        "text.ui-chrome",
        _check_ui_chrome,
        "warning",
        (
            "StatementItem 44444444 (Goodbye): user-interface text 'Previous', "
            "'Next' in en-CA content."
        ),
    ),
    (
        "text.pipe-malformed",
        _check_malformed_pipes,
        "error",
        (
            "StatementItem 44444444 (Welcome): the pipe '#{Owner Name}' "
            "contains white space."
        ),
    ),
    (
        "text.pipe-undeclared",
        _check_undeclared_pipes,
        "warning",
        (
            "StatementItem 44444444 (Welcome) pipes #{VetName}, which no lookup"
            " field, parameter or known name declares."
        ),
    ),
    (
        "colectica.lookup.duplicate-field",
        _check_duplicate_lookup_fields,
        "error",
        (
            "ComputationItem 55555555 (Owner lookup) lists the lookup field "
            "'OwnerName' 2 times."
        ),
    ),
    (
        "colectica.lookup.unlisted-output",
        _check_unlisted_lookup_outputs,
        "error",
        (
            "ComputationItem 55555555 (Owner lookup): the output 'OwnerPhone' is "
            "not one of its lookup fields."
        ),
    ),
    (
        "colectica.lookup.suspicious-field",
        _check_suspicious_lookup_fields,
        "warning",
        (
            "ComputationItem 55555555 (Owner lookup): the lookup field '01' is "
            "named like a value."
        ),
    ),
    (
        "colectica.alias.escape-compounded",
        _check_compounded_escapes,
        "error",
        (
            "OutParameter 88888888 of Sequence 77777777 (Pet survey) has an "
            "alias escaped 3 times over (44 characters): "
            "'Pets_x005F_x005F_x002F_Count'."
        ),
    ),
    (
        "colectica.alias.malformed",
        _check_malformed_aliases,
        "warning",
        (
            "OutParameter 88888888 of Sequence 77777777 (Pet survey): the alias"
            " 'Pets_x002F_Count' holds an XML escape."
        ),
    ),
    (
        "colectica.statement.logic-note",
        _check_logic_notes,
        "warning",
        (
            'StatementItem 44444444 (Flow condition) reads "Flow condition: '
            'owners only": a design note shown to respondents as content.'
        ),
    ),
    (
        "colectica.flow.read-before-computed",
        _check_read_before_computed,
        "warning/info",
        (
            "IfThenElse 44444444 (Vet gate), reached through IfThenElse 55555555 "
            "(Early exit), reads PetAge before QuestionConstruct 66666666 (PetAge) "
            "asks it. For example, when PetCount is 2."
        ),
    ),
    (
        "colectica.flow.unreachable",
        _check_unreachable,
        "warning/info",
        (
            "QuestionConstruct 77777777 (PetFood) is never reached: no answers "
            "meet the gates on every way to it."
        ),
    ),
    (
        "colectica.condition.multi-answer-question",
        _check_multi_answer_subjects,
        "warning",
        (
            "IfThenElse 44444444 (Food gate) tests FoodGrams, answer 2 of 2 of "
            "QuestionItem 66666666 (PetFood): Designer's routing view reports a "
            "condition on one answer of a question with several as broken. Ask it "
            "as a question of its own."
        ),
    ),
)

# The rules whose findings about an item depend on that item alone (and the
# lint configuration): incremental lint re-runs them for changed items only.
_PER_ITEM = frozenset(
    {
        "colectica.condition.malformed",
        "colectica.condition.empty",
        "colectica.codedomain.no-codelist",
        "colectica.domain.label-mismatch",
        "colectica.domain.type-mismatch",
        "text.placeholder-unresolved",
        "text.ui-chrome",
        "text.pipe-malformed",
        "colectica.lookup.duplicate-field",
        "colectica.lookup.unlisted-output",
        "colectica.lookup.suspicious-field",
        "colectica.alias.escape-compounded",
        "colectica.alias.malformed",
        "colectica.statement.logic-note",
    }
)

for _rule_id, _callback, _severity, _example in _RULES:
    register_rule(
        _rule_id,
        _callback,
        default=False,
        severity=_severity,
        example=_example,
    )
for _rule_id in _PER_ITEM:
    _REGISTRY[_rule_id].per_item = True

register_profile(
    COLECTICA_QUESTIONNAIRE_PROFILE,
    (
        "colectica.maintainable.labels",
        "ddi.reference.integrity",
        "ddi.reference.version",
        "ddi.reference.provenance-external",
        *(rule_id for rule_id, *_ in _RULES),
    ),
)
