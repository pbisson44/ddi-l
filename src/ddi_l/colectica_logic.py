"""Read, edit and explain the conditions Colectica stores in ``r:Command``.

Colectica keeps the logic of an ``IfThenElse`` (in ``d:IfCondition``, and in
the ``d:IfCondition`` of each ``d:ElseIf``) and of a ``ComputationItem`` (in
``r:CommandCode``) as an ``r:Command`` whose ``r:ProgramLanguage`` says how to
read its ``r:CommandContent``. DDI keeps a loop's condition the same way: a
``Loop``'s in ``d:LoopWhile`` (with ``d:InitialValue`` and ``d:StepValue``), a
``RepeatUntil``'s in ``d:UntilCondition`` and a ``RepeatWhile``'s in
``d:WhileCondition``.

The content can be:

``Neutral``
    JSON built by Colectica's condition editor::

        {"LogicGroups":[{"GroupBooleanType":0,"Statements":[
            {"StatementBooleanType":0,
             "Subject":"urn:ddi:example.org:<in-parameter id>:1",
             "Operator":7,
             "Value":{"ValueNotNeeded":true,"SelectedCodes":[]}}]}],
         "Synopsis":"Q1 Empty","Version":1}

    Parsed into a `Condition`.
``Blaise5DataLookup``
    JSON listing the fields a data lookup reads
    (``{"DataLookupFields":[{"Name":..,"Type":..,"IsAssigned":..,
    "Identifier":..}]}``). Parsed into a `DataLookup`.
anything else (``Blaise``, ...)
    Native code, kept as text in a `NativeCondition`.

A statement's ``Subject`` names an ``r:InParameter`` of the item holding the
command, by URN; a parent sequence binds that parameter to a question's
``r:OutParameter``. ``SelectedCodes`` name ``l:Code`` items by URN.

The integer codes are Colectica's: `Operator` for a statement's comparison,
`GroupBool` and `StmtBool` for how groups and statements join.
A value the enum does not list is kept as-is
(``Operator(99).name == "UNKNOWN_99"``) and written back unchanged.

Only the codes' names are known: not how a statement treats a question
with no answer, nor in what order ``And`` and ``Or`` mixed in one group are
evaluated.

Writing a condition back reproduces the original text byte for byte when
nothing was changed; an edited one is re-encoded the way Colectica writes JSON
(compact separators, keys in their original order, non-ASCII written as is
unless the source escaped it).
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, TypeAlias

from ._etree import Element
from .constants import get_namespace_set
from .models.base import MaintainableBase, qn
from .schema_loader._versions import detect_version_from_element

__all__ = [
    "AnyCondition",
    "Condition",
    "ConditionExplanation",
    "ConditionFormatError",
    "DataLookup",
    "DataLookupField",
    "GroupBool",
    "LogicGroup",
    "NativeCondition",
    "Operator",
    "Statement",
    "StmtBool",
    "explain_condition",
    "parse_command",
    "parse_condition",
    "render_synopsis",
    "serialize_condition",
    "write_condition",
]

NEUTRAL = "Neutral"
DATA_LOOKUP = "Blaise5DataLookup"


class _OpenIntEnum(IntEnum):
    """An ``IntEnum`` that keeps values it does not list.

    An unlisted value becomes a member named ``UNKNOWN_<n>``, so a condition
    using an operator not yet seen still parses and writes back unchanged.
    """

    @classmethod
    def _missing_(cls, value: object) -> Any:
        if isinstance(value, int) and not isinstance(value, bool):
            member = int.__new__(cls, value)
            member._name_ = f"UNKNOWN_{value}"
            member._value_ = value
            return member
        return None

    @property
    def known(self) -> bool:
        """Whether this value is one the enum lists."""
        return self._name_ in type(self).__members__


class GroupBool(_OpenIntEnum):
    """How a logic group joins the groups before it.

    ``FIRST`` (Colectica's ``None``, also ``NONE`` here) marks the first
    group, which joins nothing.
    """

    FIRST = 0
    NONE = 0
    AND = 1
    OR = 2


class StmtBool(_OpenIntEnum):
    """How a statement joins the statements before it.

    ``FIRST`` (Colectica's ``None``, also ``NONE`` here) marks the first
    statement of a group.
    """

    FIRST = 0
    NONE = 0
    AND = 1
    OR = 2


class Operator(_OpenIntEnum):
    """A statement's comparison, by Colectica's code.

    ``EQUAL_TO`` is Colectica's ``Equal`` (also ``EQUAL`` here).
    ``Contains...`` statements compare a coded question with the codes they
    select; ``DontKnow`` tests for a don't-know answer.
    """

    NONE = 0
    EQUAL_TO = 1
    EQUAL = 1
    NOT_EQUAL = 2
    GREATER_THAN = 3
    GREATER_THAN_OR_EQUAL = 4
    LESS_THAN = 5
    LESS_THAN_OR_EQUAL = 6
    EMPTY = 7
    NOT_EMPTY = 8
    CONTAINS = 9
    DOES_NOT_CONTAIN = 10
    CONTAINS_ANY = 11
    CONTAINS_ALL = 12
    CONTAINS_NONE = 13
    REFUSED = 14
    NOT_REFUSED = 15
    DONT_KNOW = 16
    NOT_DONT_KNOW = 17


class ConditionFormatError(ValueError):
    """A command's content is not the JSON its ``ProgramLanguage`` promises."""


# ---- JSON objects that remember their layout ------------------------------


@dataclass
class _Layout:
    """The key order and unmodelled keys of one JSON object, as read."""

    keys: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)


def _ordered(layout: _Layout, values: dict[str, Any]) -> dict[str, Any]:
    """``values`` (``None`` = absent) in the key order read, new keys last.

    A model built in code has an empty layout, so its keys come out in the
    order ``values`` lists them, which is the order Colectica writes.
    """
    merged = {**layout.extra, **values}
    order = [key for key in layout.keys if key in merged]
    order += [key for key in merged if key not in order]
    return {key: merged[key] for key in order if merged[key] is not None}


def _layout(obj: dict[str, Any], modelled: tuple[str, ...]) -> _Layout:
    return _Layout(
        keys=tuple(obj),
        extra={key: value for key, value in obj.items() if key not in modelled},
    )


def _expect(obj: Any, kind: type, where: str) -> Any:
    if not isinstance(obj, kind):
        raise ConditionFormatError(
            f"{where}: expected a JSON {kind.__name__}, got {type(obj).__name__}."
        )
    return obj


def _selected_codes(value: dict[str, Any]) -> list[Any]:
    """A statement's ``SelectedCodes``: a list, or ``null`` for none."""
    codes = value.get("SelectedCodes")
    if codes is None:
        return []
    return list(_expect(codes, list, "Statement SelectedCodes"))


def _code(obj: dict[str, Any], key: str) -> int:
    """The integer code ``obj[key]`` (default 0); a code is never a bool or float."""
    value = obj.get(key, 0)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConditionFormatError(
            f"{key}: expected an integer code, got {json.dumps(value)}."
        )
    return value


@dataclass
class Statement:
    """One comparison: ``subject operator value``.

    Attributes:
        stmt_bool: How it joins the statements before it in its group.
        subject: URN of the ``r:InParameter`` compared.
        operator: The comparison.
        value: The literal compared against, for operators that take one.
        value_not_needed: Colectica's flag for operators that take no value
            (``Empty``, ``Refused``).
        selected_codes: URNs of the ``l:Code`` items compared against.
    """

    stmt_bool: StmtBool
    subject: str
    operator: Operator
    value: str | None = None
    value_not_needed: bool = False
    selected_codes: list[str] = field(default_factory=list)
    _layout: _Layout = field(default_factory=_Layout, repr=False, compare=False)
    _value_layout: _Layout = field(default_factory=_Layout, repr=False, compare=False)

    @classmethod
    def _from_json(cls, obj: Any) -> Statement:
        obj = _expect(obj, dict, "Statement")
        value = _expect(obj.get("Value", {}), dict, "Statement Value")
        return cls(
            stmt_bool=StmtBool(_code(obj, "StatementBooleanType")),
            subject=str(obj.get("Subject", "")),
            operator=Operator(_code(obj, "Operator")),
            value=None if value.get("Value") is None else str(value["Value"]),
            value_not_needed=bool(value.get("ValueNotNeeded", False)),
            selected_codes=[str(code) for code in _selected_codes(value)],
            _layout=_layout(
                obj, ("StatementBooleanType", "Subject", "Operator", "Value")
            ),
            _value_layout=_layout(value, ("Value", "ValueNotNeeded", "SelectedCodes")),
        )

    def _to_json(self) -> dict[str, Any]:
        value = _ordered(
            self._value_layout,
            {
                "Value": self.value,
                "ValueNotNeeded": self.value_not_needed,
                "SelectedCodes": list(self.selected_codes),
            },
        )
        return _ordered(
            self._layout,
            {
                "StatementBooleanType": int(self.stmt_bool),
                "Subject": self.subject,
                "Operator": int(self.operator),
                "Value": value,
            },
        )


@dataclass
class LogicGroup:
    """Statements evaluated together, joined to the groups before them.

    Attributes:
        group_bool: How the group joins the groups before it.
        statements: The group's statements, in order.
    """

    group_bool: GroupBool
    statements: list[Statement] = field(default_factory=list)
    _layout: _Layout = field(default_factory=_Layout, repr=False, compare=False)

    @classmethod
    def _from_json(cls, obj: Any) -> LogicGroup:
        obj = _expect(obj, dict, "LogicGroup")
        statements = _expect(obj.get("Statements", []), list, "Statements")
        return cls(
            group_bool=GroupBool(_code(obj, "GroupBooleanType")),
            statements=[Statement._from_json(item) for item in statements],
            _layout=_layout(obj, ("GroupBooleanType", "Statements")),
        )

    def _to_json(self) -> dict[str, Any]:
        return _ordered(
            self._layout,
            {
                "GroupBooleanType": int(self.group_bool),
                "Statements": [statement._to_json() for statement in self.statements],
            },
        )


@dataclass
class _Encoded:
    """What a command looked like when read, to write it back unchanged."""

    raw: str | None = None
    snapshot: Any = None
    ensure_ascii: bool = False


@dataclass
class Condition:
    """A ``Neutral`` condition from Colectica's condition editor.

    Attributes:
        logic_groups: The groups, in order. Empty means no logic at all, which
            Colectica evaluates as always true.
        synopsis: The text Colectica stored alongside the logic. It is what
            the editor last displayed, not derived from ``logic_groups`` when
            read, and can be stale; compare it with `render_synopsis`.
        version: The format version Colectica wrote (``1`` so far).
        language: The ``r:ProgramLanguage`` (``"Neutral"``).
    """

    logic_groups: list[LogicGroup] = field(default_factory=list)
    synopsis: str | None = None
    version: int | None = 1
    language: str = NEUTRAL
    _layout: _Layout = field(default_factory=_Layout, repr=False, compare=False)
    _encoded: _Encoded = field(default_factory=_Encoded, repr=False, compare=False)

    @property
    def statements(self) -> Iterator[Statement]:
        """Every statement, group by group."""
        for group in self.logic_groups:
            yield from group.statements

    @property
    def is_empty(self) -> bool:
        """Whether the condition has no statement at all."""
        return not any(group.statements for group in self.logic_groups)

    def _to_json(self) -> dict[str, Any]:
        return _ordered(
            self._layout,
            {
                "LogicGroups": [group._to_json() for group in self.logic_groups],
                "Synopsis": self.synopsis,
                "Version": self.version,
            },
        )


@dataclass
class DataLookupField:
    """A field a ``Blaise5DataLookup`` reads.

    Attributes:
        name: The field's name, as text pipes it (``#{name}``).
        type: Its type, as Colectica wrote it.
        is_assigned: Whether the lookup assigns it.
        identifier: Colectica's identifier for the field, if any.
    """

    name: str
    type: Any = None
    is_assigned: bool | None = None
    identifier: Any = None
    _layout: _Layout = field(default_factory=_Layout, repr=False, compare=False)

    @classmethod
    def _from_json(cls, obj: Any) -> DataLookupField:
        obj = _expect(obj, dict, "DataLookupField")
        assigned = obj.get("IsAssigned")
        return cls(
            name=str(obj.get("Name", "")),
            type=obj.get("Type"),
            is_assigned=None if assigned is None else bool(assigned),
            identifier=obj.get("Identifier"),
            _layout=_layout(obj, ("Name", "Type", "IsAssigned", "Identifier")),
        )

    def _to_json(self) -> dict[str, Any]:
        return _ordered(
            self._layout,
            {
                "Name": self.name,
                "Type": self.type,
                "IsAssigned": self.is_assigned,
                "Identifier": self.identifier,
            },
        )


@dataclass
class DataLookup:
    """A ``Blaise5DataLookup`` command: the fields a data lookup reads."""

    fields: list[DataLookupField] = field(default_factory=list)
    language: str = DATA_LOOKUP
    _layout: _Layout = field(default_factory=_Layout, repr=False, compare=False)
    _encoded: _Encoded = field(default_factory=_Encoded, repr=False, compare=False)

    def _to_json(self) -> dict[str, Any]:
        return _ordered(
            self._layout,
            {"DataLookupFields": [item._to_json() for item in self.fields]},
        )


@dataclass
class NativeCondition:
    """Native code (``Blaise`` and others), kept as written."""

    text: str
    language: str


AnyCondition: TypeAlias = Condition | DataLookup | NativeCondition


# ---- Parsing and writing --------------------------------------------------

_NON_ASCII_ESCAPE = re.compile(
    r"\\u(?:00[89a-fA-F][0-9a-fA-F]|0[1-9a-fA-F]|[1-9a-fA-F])"
)


def _load(text: str, language: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ConditionFormatError(
            f"{language} command is not valid JSON: {error.msg} "
            f"(line {error.lineno}, column {error.colno})."
        ) from error


def _encoded(text: str, model: Condition | DataLookup) -> _Encoded:
    return _Encoded(
        raw=text,
        snapshot=model._to_json(),
        ensure_ascii=bool(_NON_ASCII_ESCAPE.search(text)),
    )


def parse_command(language: str | None, text: str | None) -> AnyCondition:
    """Parse one command's content according to its program language.

    Args:
        language: The ``r:ProgramLanguage`` text.
        text: The ``r:CommandContent`` text.

    Raises:
        ConditionFormatError: If a ``Neutral`` or ``Blaise5DataLookup``
            command is not the JSON that language promises.
    """
    language = (language or "").strip()
    text = text or ""
    if language == NEUTRAL:
        obj = _expect(_load(text, language), dict, "Neutral command")
        groups = _expect(obj.get("LogicGroups", []), list, "LogicGroups")
        condition = Condition(
            logic_groups=[LogicGroup._from_json(group) for group in groups],
            synopsis=None if obj.get("Synopsis") is None else str(obj["Synopsis"]),
            version=obj.get("Version"),
            _layout=_layout(obj, ("LogicGroups", "Synopsis", "Version")),
        )
        condition._encoded = _encoded(text, condition)
        return condition
    if language == DATA_LOOKUP:
        obj = _expect(_load(text, language), dict, "data lookup command")
        items = _expect(obj.get("DataLookupFields", []), list, "DataLookupFields")
        lookup = DataLookup(
            fields=[DataLookupField._from_json(item) for item in items],
            _layout=_layout(obj, ("DataLookupFields",)),
        )
        lookup._encoded = _encoded(text, lookup)
        return lookup
    return NativeCondition(text=text, language=language)


def serialize_condition(condition: AnyCondition) -> str:
    """The ``r:CommandContent`` text for ``condition``.

    An unchanged condition comes back exactly as read. An edited one is
    re-encoded as Colectica writes JSON: no spaces, keys in the order read
    (new keys last), and non-ASCII characters written as is unless the
    source escaped them.
    """
    if isinstance(condition, NativeCondition):
        return condition.text
    current = condition._to_json()
    encoded = condition._encoded
    if encoded.raw is not None and current == encoded.snapshot:
        return encoded.raw
    return json.dumps(current, separators=(",", ":"), ensure_ascii=encoded.ensure_ascii)


def _reusable(element: Element) -> str:
    return get_namespace_set(detect_version_from_element(element))["REUSABLE_NS"]


def _element_of(item: Element | MaintainableBase) -> Element:
    return item.to_xml() if isinstance(item, MaintainableBase) else item


def _child(element: Element, *local_names: str) -> Element | None:
    """The first child element whose local name is one of ``local_names``."""
    for child in element:
        if isinstance(child.tag, str) and child.tag.rsplit("}", 1)[-1] in local_names:
            return child
    return None


# The elements of type r:CommandCodeType a control construct keeps a command in.
_COMMAND_HOLDERS = (
    "IfCondition",
    "CommandCode",
    "LoopWhile",
    "UntilCondition",
    "WhileCondition",
    "InitialValue",
    "StepValue",
)
# Those that hold an item's condition (or computation), in the order they are
# looked for: a Loop's InitialValue and StepValue are read only when asked for.
_CONDITION_HOLDERS = _COMMAND_HOLDERS[:5]


def _check_which(which: str | None) -> None:
    if which is not None and which not in _COMMAND_HOLDERS:
        raise ValueError(
            f"which must be one of {', '.join(_COMMAND_HOLDERS)}, not {which!r}."
        )


def _command_holder(element: Element, which: str | None = None) -> Element | None:
    """The child of ``element`` holding its command (``which`` names it).

    Raises:
        ValueError: If ``which`` is not a command holder.
    """
    _check_which(which)
    for name in (which,) if which is not None else _CONDITION_HOLDERS:
        holder = _child(element, name)
        if holder is not None:
            return holder
    return None


def _first_command(element: Element, which: str | None = None) -> Element | None:
    """The ``r:Command`` of an item, of a command holder, or the command itself.

    For an ``IfThenElse`` or ``ElseIf``, that of its ``IfCondition``; for a
    ``ComputationItem`` (or any item with one), that of its ``r:CommandCode``;
    for a ``Loop``, that of its ``LoopWhile`` (``which="InitialValue"`` or
    ``"StepValue"`` for the others); for a ``RepeatUntil`` or ``RepeatWhile``,
    that of its ``UntilCondition`` or ``WhileCondition``.

    Raises:
        ValueError: If ``which`` is not a command holder, or ``element`` is a
            holder other than ``which``.
    """
    _check_which(which)
    command_tag = qn(_reusable(element), "Command")
    if element.tag == command_tag:
        return element
    local = element.tag.rsplit("}", 1)[-1]
    if local in _COMMAND_HOLDERS:
        if which is not None and which != local:
            raise ValueError(f"which={which!r} names another holder than this {local}.")
        return element.find(command_tag)
    holder = _command_holder(element, which)
    return None if holder is None else holder.find(command_tag)


def _else_if_commands(element: Element) -> list[Element]:
    """The ``r:Command`` of each ``d:ElseIf`` of an ``IfThenElse``, in order."""
    commands = []
    for child in element:
        if isinstance(child.tag, str) and child.tag.rsplit("}", 1)[-1] == "ElseIf":
            command = _first_command(child)
            if command is not None:
                commands.append(command)
    return commands


def parse_condition(
    item: Element | MaintainableBase, *, which: str | None = None
) -> AnyCondition | None:
    """Parse the condition of an ``IfThenElse``, loop, ``ComputationItem`` or command.

    Args:
        item: An item element or typed model, a command holder
            (``IfCondition``, ``CommandCode``, ``LoopWhile``...), an ``ElseIf``
            element, or an ``r:Command``.
        which: The holder to read when ``item`` has several, such as a
            ``Loop``'s ``"InitialValue"`` or ``"StepValue"``. By default an
            item's condition: a ``Loop``'s is in its ``LoopWhile``. Given an
            ``r:Command`` itself, it has nothing to choose from.

    Returns:
        The parsed condition, or ``None`` when ``item`` holds no command.

    Raises:
        ConditionFormatError: If a JSON command is malformed.
        ValueError: If ``which`` names no command holder, or ``item`` is a
            holder other than ``which``.
    """
    command = _first_command(_element_of(item), which)
    if command is None:
        return None
    reusable = _reusable(command)
    return parse_command(
        command.findtext(qn(reusable, "ProgramLanguage")),
        command.findtext(qn(reusable, "CommandContent")),
    )


def write_condition(
    command_holder: Element, condition: AnyCondition, *, which: str | None = None
) -> Element:
    """Write ``condition`` into an item's (or an ``r:Command``'s) content.

    Only ``r:CommandContent`` and ``r:ProgramLanguage`` change, so the rest
    of the element round-trips as read.

    Args:
        command_holder: An item, a command holder, or an ``r:Command``.
        condition: The condition to write.
        which: The holder to write when the item has several, as for
            `parse_condition`.

    Returns:
        The ``r:Command`` written.

    Raises:
        ValueError: If ``command_holder`` holds no ``r:Command``, if ``which``
            names no command holder, or if ``command_holder`` is a holder
            other than ``which``.
    """
    command = _first_command(command_holder, which)
    if command is None:
        raise ValueError("The element holds no r:Command to write the condition to.")
    reusable = _reusable(command)
    language = command.find(qn(reusable, "ProgramLanguage"))
    content = command.find(qn(reusable, "CommandContent"))
    if language is None or content is None:
        raise ValueError("The r:Command has no ProgramLanguage or CommandContent.")
    language.text = condition.language
    content.text = serialize_condition(condition)
    return command


# ---- Rendering against a document -------------------------------------------


def _parse_urn(urn: str) -> tuple[str, str] | None:
    """``(agency, id)`` from ``urn:ddi:agency:id:version``."""
    parts = urn.split(":")
    if len(parts) >= 5 and parts[0].lower() == "urn" and parts[1].lower() == "ddi":
        return parts[2], parts[3]
    return None


def _version_rank(version: str) -> tuple[int, ...]:
    """Sort key for a DDI version string (``"1.10"`` after ``"1.9"``)."""
    return tuple(int(part) if part.isdigit() else -1 for part in version.split("."))


class _Lookup:
    """Identifiables, their owners and the bindings of one document."""

    def __init__(self, root: Element) -> None:
        reusable = _reusable(root)
        self._reusable = reusable
        agency_tag, id_tag = qn(reusable, "Agency"), qn(reusable, "ID")
        version_tag = qn(reusable, "Version")
        binding_tag = qn(reusable, "Binding")
        self.items: dict[tuple[str, str], Element] = {}
        self.owner: dict[int, Element] = {}
        self.bound_from: dict[tuple[str, str], tuple[str, str]] = {}
        ranks: dict[tuple[str, str], tuple[int, ...]] = {}
        parameters = {qn(reusable, "InParameter"), qn(reusable, "OutParameter")}
        # Each binding with the item holding it and that item's version: only
        # the latest version of an item binds (an export can hold several).
        bindings: list[tuple[tuple[str, str] | None, tuple[int, ...], Any, Any]] = []

        # In document order, so of two copies of one version the first wins,
        # as in every other index.
        stack: list[tuple[Element, Element | None]] = [(root, None)]
        while stack:
            element, owner = stack.pop()
            tag = element.tag
            if not isinstance(tag, str):
                continue
            child_owner = owner
            if not tag.endswith("Reference"):
                agency = element.findtext(agency_tag)
                identifier = element.findtext(id_tag)
                if agency and identifier:
                    key = (agency, identifier)
                    rank = _version_rank(element.findtext(version_tag) or "")
                    if key not in ranks or rank > ranks[key]:
                        ranks[key] = rank
                        self.items[key] = element
                    if tag in parameters and owner is not None:
                        self.owner[id(element)] = owner
                    elif tag not in parameters:
                        child_owner = element
            if tag == binding_tag:
                source = element.find(qn(reusable, "SourceParameterReference"))
                target = element.find(qn(reusable, "TargetParameterReference"))
                if source is not None and target is not None:
                    source_key = self._key(source)
                    target_key = self._key(target)
                    if source_key and target_key:
                        holder = None if owner is None else self._key(owner)
                        rank = _version_rank(
                            "" if owner is None else owner.findtext(version_tag) or ""
                        )
                        bindings.append((holder, rank, target_key, source_key))
            stack.extend((child, child_owner) for child in reversed(list(element)))
        # Only the latest version of each holder binds: the bindings of an
        # older version (or none at all, if the latest has none) are history.
        # Of several bindings of one target, the first in the document wins.
        for holder, rank, target_key, source_key in bindings:
            if holder is None or rank == ranks.get(holder, rank):
                self.bound_from.setdefault(target_key, source_key)

    def _key(self, reference: Element) -> tuple[str, str] | None:
        agency = reference.findtext(qn(self._reusable, "Agency"))
        identifier = reference.findtext(qn(self._reusable, "ID"))
        return (agency, identifier) if agency and identifier else None

    def text_of(self, element: Element, *local_names: str) -> str | None:
        for child in element:
            if (
                isinstance(child.tag, str)
                and child.tag.rsplit("}", 1)[-1] in local_names
            ):
                for node in child.iter():
                    if (node.text or "").strip():
                        return node.text.strip()  # type: ignore[union-attr]
        return None

    def alias(self, key: tuple[str, str]) -> str | None:
        parameter = self.items.get(key)
        if parameter is None:
            return None
        return self.text_of(parameter, "Alias", "ParameterName")

    def question_name(self, key: tuple[str, str]) -> str | None:
        """The name of the question whose answer feeds parameter ``key``."""
        seen: set[tuple[str, str]] = set()
        current: tuple[str, str] | None = key
        while current is not None and current not in seen:
            seen.add(current)
            parameter = self.items.get(current)
            owner = None if parameter is None else self.owner.get(id(parameter))
            if owner is not None:
                name = self._question_of(owner)
                if name:
                    return name
            current = self.bound_from.get(current)
        return None

    def _question_of(self, owner: Element) -> str | None:
        local = owner.tag.rsplit("}", 1)[-1]
        if local in ("QuestionItem", "QuestionGrid", "QuestionBlock"):
            return self.text_of(owner, f"{local}Name", "Name")
        if local == "QuestionConstruct":
            reference = owner.find(qn(self._reusable, "QuestionReference"))
            key = None if reference is None else self._key(reference)
            question = None if key is None else self.items.get(key)
            if question is not None:
                return self._question_of(question)
        return None

    def code(self, urn: str) -> tuple[str, str | None]:
        """A code's value and its category's label, for a code URN."""
        key = _parse_urn(urn)
        code = None if key is None else self.items.get(key)
        if code is None:
            return urn, None
        value = code.findtext(qn(self._reusable, "Value")) or urn
        reference = code.find(qn(self._reusable, "CategoryReference"))
        category_key = None if reference is None else self._key(reference)
        category = None if category_key is None else self.items.get(category_key)
        label = None if category is None else self.text_of(category, "Label")
        return value.strip(), label


_OPERATOR_TEXT = {
    Operator.EQUAL_TO: "=",
    Operator.NOT_EQUAL: "!=",
    Operator.GREATER_THAN: ">",
    Operator.GREATER_THAN_OR_EQUAL: ">=",
    Operator.LESS_THAN: "<",
    Operator.LESS_THAN_OR_EQUAL: "<=",
    Operator.EMPTY: "is empty",
    Operator.NOT_EMPTY: "is not empty",
    Operator.CONTAINS: "contains",
    Operator.DOES_NOT_CONTAIN: "does not contain",
    Operator.CONTAINS_ANY: "contains any of",
    Operator.CONTAINS_ALL: "contains all of",
    Operator.CONTAINS_NONE: "contains none of",
    Operator.REFUSED: "is refused",
    Operator.NOT_REFUSED: "is not refused",
    Operator.DONT_KNOW: "is don't know",
    Operator.NOT_DONT_KNOW: "is not don't know",
}


def _bool_text(value: GroupBool | StmtBool) -> str:
    if value.known and value._name_ in ("AND", "OR"):
        return value._name_.lower()
    return f"<{value._name_.lower()}>"


def _root_of(doc: Any) -> Element:
    return doc.root if hasattr(doc, "root") else doc


def _subject_names(statement: Statement, doc: Any) -> tuple[str | None, str | None]:
    """The bound question's name and the parameter alias for a subject."""
    lookup = doc if isinstance(doc, _Lookup) else _Lookup(_root_of(doc))
    key = _parse_urn(statement.subject)
    if key is None:
        return None, None
    return lookup.question_name(key), lookup.alias(key)


def _render_statement(statement: Statement, lookup: _Lookup) -> str:
    question, alias = _subject_names(statement, lookup)
    key = _parse_urn(statement.subject)
    subject = question or alias or (key[1][:8] if key else statement.subject)
    operator = _OPERATOR_TEXT.get(
        statement.operator, f"<operator {int(statement.operator)}>"
    )
    if statement.selected_codes:
        codes = []
        for urn in statement.selected_codes:
            value, label = lookup.code(urn)
            codes.append(f'{value} "{label}"' if label else value)
        return f"{subject} {operator} {', '.join(codes)}"
    if statement.value_not_needed or statement.value is None:
        return f"{subject} {operator}"
    return f"{subject} {operator} {statement.value}"


def render_synopsis(condition: Condition, doc: Any) -> str:
    """A readable synopsis of ``condition``, resolved against ``doc``.

    Unlike the synopsis Colectica stores, subjects are named after the
    question bound to them (else the parameter's alias) and codes by their
    **value** and label. The stored synopsis numbers codes by their position
    in the list, so it reads ``1`` for the first code even when that code's
    value is ``2``.

    Args:
        condition: A ``Neutral`` condition.
        doc: The fragment or document holding the condition's subjects and
            codes (anything with a ``root``, or a root element).
    """
    lookup = doc if isinstance(doc, _Lookup) else _Lookup(_root_of(doc))
    parts: list[str] = []
    groups = [group for group in condition.logic_groups]
    for index, group in enumerate(groups):
        statements = []
        for position, statement in enumerate(group.statements):
            text = _render_statement(statement, lookup)
            if position:
                text = f"{_bool_text(statement.stmt_bool)} {text}"
            statements.append(text)
        # An empty group reads "()", as in Colectica's own synopsis.
        body = " ".join(statements)
        if len(groups) > 1 or not body:
            body = f"({body})"
        if index:
            body = f"{_bool_text(group.group_bool)} {body}"
        parts.append(body)
    return " ".join(parts) if parts else "(no condition)"


@dataclass(frozen=True)
class ConditionExplanation:
    r"""Everything `explain_condition` found about one item's condition.

    Attributes:
        item_type: The item's element name (``IfThenElse``, ...).
        identifier: The item's ``r:ID``.
        version: The item's ``r:Version``.
        language: The command's program language, or ``None`` without one.
        stored_synopsis: The synopsis Colectica stored, for a ``Neutral``
            condition.
        rendered_synopsis: `render_synopsis` for a ``Neutral``
            condition, else the native text or the lookup fields.
        unnamed_subjects: Subjects whose question name and alias both are
            missing from the stored synopsis: a sign it names the wrong
            variable.
        descriptions: The condition's ``r:Description`` text, by language.
        used_inputs: Aliases of the item's ``r:InParameter``\s the condition
            uses, or the condition of any ``ElseIf`` branch, or a ``Loop``'s
            ``InitialValue`` or ``StepValue``.
        unused_inputs: Aliases of those none of them uses, or ``None`` when
            that cannot be told: a command does not parse, or is a data
            lookup.
        error: Why the command (or, prefixed with where it is, an ``ElseIf``
            branch's or a ``Loop``'s other command) could not be parsed.
    """

    item_type: str
    identifier: str
    version: str | None
    language: str | None
    stored_synopsis: str | None
    rendered_synopsis: str | None
    unnamed_subjects: tuple[str, ...]
    descriptions: dict[str, str]
    used_inputs: tuple[str, ...]
    unused_inputs: tuple[str, ...] | None
    error: str | None = None


def _find_item(root: Element, identifier: str) -> Element | None:
    reusable = _reusable(root)
    id_tag, version_tag = qn(reusable, "ID"), qn(reusable, "Version")
    best: Element | None = None
    best_rank: tuple[int, ...] = ()
    for element in root.iter():
        if not isinstance(element.tag, str) or element.tag.endswith("Reference"):
            continue
        if element.findtext(id_tag) == identifier:
            rank = _version_rank(element.findtext(version_tag) or "")
            if best is None or rank > best_rank:
                best, best_rank = element, rank
    return best


def _descriptions(item: Element) -> dict[str, str]:
    """The ``r:Description`` of the element holding an item's condition."""
    reusable = _reusable(item)
    holder = _command_holder(item)
    description = None if holder is None else holder.find(qn(reusable, "Description"))
    if description is None:
        return {}
    found: dict[str, str] = {}
    xml_lang = "{http://www.w3.org/XML/1998/namespace}lang"
    for node in description.iter():
        text = (node.text or "").strip()
        if text and node is not description:
            found.setdefault(node.get(xml_lang) or "", text)
    return found


def _used_inputs(
    condition: AnyCondition | None,
    inputs: list[tuple[tuple[str, str] | None, str]],
) -> set[tuple[str, str] | None]:
    """The inputs (keys) a condition tests: its subjects, or aliases it names."""
    if isinstance(condition, Condition):
        return {_parse_urn(statement.subject) for statement in condition.statements}
    if isinstance(condition, NativeCondition):
        return {
            key
            for key, alias in inputs
            if re.search(rf"(?<![\w.]){re.escape(alias)}(?![\w.])", condition.text)
        }
    return set()


def explain_condition(doc: Any, identifier: str) -> ConditionExplanation:
    """Explain the condition of the item with ``identifier`` in ``doc``.

    Args:
        doc: A fragment or document (anything with a ``root``), or a root.
        identifier: The ``r:ID`` of an ``IfThenElse``, a loop, a
            ``ComputationItem`` or another item holding a command; the
            highest version is used.

    Raises:
        KeyError: If no item has that identifier.
    """
    root = _root_of(doc)
    item = _find_item(root, identifier)
    if item is None:
        raise KeyError(f"No item with ID {identifier!r}.")
    reusable = _reusable(item)
    lookup = _Lookup(root)
    item_type = item.tag.rsplit("}", 1)[-1]
    inputs: list[tuple[tuple[str, str] | None, str]] = []
    for parameter in item.findall(qn(reusable, "InParameter")):
        agency = parameter.findtext(qn(reusable, "Agency"))
        ident = parameter.findtext(qn(reusable, "ID"))
        key = (agency, ident) if agency and ident else None
        alias = lookup.text_of(parameter, "Alias", "ParameterName") or (ident or "")[:8]
        inputs.append((key, alias))

    language: str | None = None
    stored: str | None = None
    rendered: str | None = None
    error: str | None = None
    unnamed: list[str] = []
    used: set[tuple[str, str] | None] = set()
    # Whether some command may use inputs that cannot be told: one that does
    # not parse, or a data lookup (its JSON names fields, not inputs).
    unknown = False
    try:
        condition = parse_condition(item)
    except ConditionFormatError as failure:
        condition, error, unknown = None, str(failure), True
        command = _first_command(item)
        if command is not None:
            language = command.findtext(qn(reusable, "ProgramLanguage"))
    if isinstance(condition, Condition):
        language, stored = condition.language, condition.synopsis
        rendered = render_synopsis(condition, lookup)
        for statement in condition.statements:
            question, subject_alias = _subject_names(statement, lookup)
            names = [name for name in (question, subject_alias) if name]
            if (
                stored is not None
                and names
                and not any(
                    re.search(rf"(?<![\w.]){re.escape(name)}(?![\w.])", stored)
                    for name in names
                )
            ):
                unnamed.append(names[0])
    elif isinstance(condition, DataLookup):
        language, unknown = condition.language, True
        rendered = ", ".join(entry.name for entry in condition.fields)
    elif isinstance(condition, NativeCondition):
        language, rendered = condition.language, condition.text
    used |= _used_inputs(condition, inputs)
    # An ElseIf declares no inputs of its own: it tests the IfThenElse's. A
    # Loop's InitialValue and StepValue may use its inputs too.
    others = [
        (f"ElseIf {number}", command)
        for number, command in enumerate(_else_if_commands(item), 1)
    ]
    for which in ("InitialValue", "StepValue"):
        holder = _command_holder(item, which)
        command = None if holder is None else holder.find(qn(reusable, "Command"))
        if command is not None:
            others.append((which, command))
    for where, command in others:
        try:
            other = parse_command(
                command.findtext(qn(reusable, "ProgramLanguage")),
                command.findtext(qn(reusable, "CommandContent")),
            )
        except ConditionFormatError as failure:
            unknown = True
            error = error or f"{where}: {failure}"
            continue
        unknown = unknown or isinstance(other, DataLookup)
        used |= _used_inputs(other, inputs)

    return ConditionExplanation(
        item_type=item_type,
        identifier=identifier,
        version=item.findtext(qn(reusable, "Version")),
        language=language,
        stored_synopsis=stored,
        rendered_synopsis=rendered,
        unnamed_subjects=tuple(dict.fromkeys(unnamed)),
        descriptions=_descriptions(item),
        used_inputs=tuple(alias for key, alias in inputs if key in used),
        unused_inputs=None
        if unknown
        else tuple(alias for key, alias in inputs if key not in used),
        error=error,
    )
