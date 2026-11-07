"""Edit a Colectica questionnaire in place: versions, sequences, copies.

The functions behind `DDIFragment.revise`,
`move_construct`, `wrap_in_condition`,
`duplicate` and
`repair_shared_identifiables`. They edit the fragment's XML
directly (an item's typed model is a copy), and work on DDI 3.3 fragments
only.

Colectica identifies a reference by Agency, ID and Version. A reference that
is not late-bound names one version, so changing an item and giving it a new
version leaves every item pointing at the old one stale: they need their
reference updated, which changes them in turn, up to the instrument.
`revise` does that walk.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from functools import partial
from typing import TYPE_CHECKING

from . import _incremental
from ._etree import Element, create_element
from .colectica import apply_colectica_conventions, colectica_timestamp
from .colectica_logic import AnyCondition, serialize_condition
from .colectica_logic import _version_rank as _rank
from .exceptions import DDIModelError
from .models.base import MaintainableBase, clone_element, qn

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from .document import DDIFragment

__all__ = [
    "EditResult",
    "RepairPlan",
    "RepairStep",
    "RevisionPlan",
    "RevisionStep",
]

DATA_COLLECTION_NS = "ddi:datacollection:3_3"
_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
_LATE_BOUND = ("true", "1")
# Children that come before r:VersionResponsibility / r:BasedOnObject in a
# versionable item, in schema order.
_IDENTIFICATION = ("URN", "Agency", "ID", "Version", "UserID", "UserAttributePair")
_VERSIONING = (
    *_IDENTIFICATION,
    "VersionResponsibility",
    "VersionResponsibilityReference",
    "VersionRationale",
)


def _local(tag: object) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


class _Items:
    """The fragment's items by ``(agency, id)``, highest version first."""

    def __init__(self, fragment: DDIFragment) -> None:
        fragment._require_typed_models()
        self.fragment = fragment
        self.r = fragment._reusable_ns
        self.versions: dict[tuple[str, str], list[Element]] = {}
        for payload in fragment.iter_fragment_payloads():
            key = self.key(payload)
            if key is not None:
                self.versions.setdefault(key, []).append(payload)
        for payloads in self.versions.values():
            payloads.sort(key=lambda p: _rank(self.version(p)), reverse=True)

    def tag(self, name: str) -> str:
        return qn(self.r, name)

    def key(self, element: Element) -> tuple[str, str] | None:
        agency = element.findtext(self.tag("Agency"))
        identifier = element.findtext(self.tag("ID"))
        return (agency, identifier) if agency and identifier else None

    def version(self, element: Element) -> str:
        return element.findtext(self.tag("Version")) or ""

    def latest(self) -> Iterator[Element]:
        for payloads in self.versions.values():
            yield payloads[0]

    def find(self, item: str | MaintainableBase | Element) -> Element:
        """The highest version of ``item`` (an ID, a typed model or an element)."""
        if isinstance(item, MaintainableBase):
            identifier, agency = item.identifier, item.agency
        elif isinstance(item, str):
            identifier, agency = item, None
        else:
            identifier = item.findtext(self.tag("ID"))
            agency = item.findtext(self.tag("Agency"))
        for (item_agency, item_id), payloads in self.versions.items():
            if item_id == identifier and agency in (None, item_agency):
                return payloads[0]
        raise KeyError(f"No item with ID {identifier!r} in the fragment.")

    def references(self, element: Element) -> Iterator[Element]:
        """Typed references under ``element``."""
        type_tag = self.tag("TypeOfObject")
        for node in element.iter():
            if (
                isinstance(node.tag, str)
                and node.tag.endswith("Reference")
                and node.find(type_tag) is not None
            ):
                yield node

    # Each change made through these is undone by `undo` while ``journal``
    # is a list: a dry run makes its changes, then takes them back.
    journal: list[Callable[[], object]] | None = None

    def set_text(self, node: Element, text: str | None) -> None:
        if self.journal is not None:
            self.journal.append(partial(setattr, node, "text", node.text))
        node.text = text

    def set_attribute(self, node: Element, name: str, value: str) -> None:
        if self.journal is not None:
            old = node.get(name)
            if old is None:
                self.journal.append(partial(node.attrib.__delitem__, name))
            else:
                self.journal.append(partial(node.set, name, old))
        node.set(name, value)

    def insert(self, parent: Element, at: int, child: Element) -> None:
        parent.insert(at, child)
        if self.journal is not None:
            self.journal.append(partial(parent.remove, child))

    def remove(self, parent: Element, child: Element) -> None:
        if self.journal is not None:
            at = next(n for n, node in enumerate(parent) if node is child)
            self.journal.append(partial(parent.insert, at, child))
        parent.remove(child)

    def undo(self) -> None:
        """Take back every change in ``journal``, last first."""
        while self.journal:
            self.journal.pop()()


def _reference_keys(items: _Items, element: Element) -> list[tuple[str, str]]:
    """The key of each of ``items.references(element)`` that has one."""
    keys = (items.key(reference) for reference in items.references(element))
    return [key for key in keys if key is not None]


class _Referrers:
    """Who refers to each key among the latest items.

    Built once per `revise` call, so the cascade costs what it revises and
    their referrers, not a scan of every item per revised item. On the
    native backend, what an item refers to is read again only once the item
    has changed (`ddi_l._incremental.per_element`).
    """

    def __init__(self, items: _Items) -> None:
        self.items = items
        latest = list(items.latest())
        reads = _incremental.per_element(
            items.fragment, "reference-keys", latest, partial(_reference_keys, items)
        )
        # Per key: the item's position, the reference's among its own, the item.
        self.by_key: dict[tuple[str, str], list[tuple[int, int, Element]]] = {}
        for at, (item, keys) in enumerate(zip(latest, reads, strict=True)):
            for number, key in enumerate(keys):
                self.by_key.setdefault(key, []).append((at, number, item))
        self.resolved: dict[int, list[Element]] = {}

    def of(self, keys: Iterable[tuple[str, str]]) -> list[tuple[Element, Element]]:
        """Each (item, reference) to one of ``keys``, items first, in order."""
        entries = sorted(
            (entry for key in keys for entry in self.by_key.get(key, ())),
            key=lambda entry: entry[:2],
        )
        found = []
        for _, number, item in entries:
            references = self.resolved.get(id(item))
            if references is None:
                references = self.resolved[id(item)] = [
                    reference
                    for reference in self.items.references(item)
                    if self.items.key(reference) is not None
                ]
            found.append((item, references[number]))
        return found


def _child_index(element: Element, after: Sequence[str]) -> int:
    """The position just after the last child named in ``after``."""
    position = 0
    for index, child in enumerate(element):
        if _local(child.tag) in after:
            position = index + 1
    return position


# ---- B2: revise ---------------------------------------------------------------


@dataclass(frozen=True)
class RevisionStep:
    """One item `revise` gave a new version.

    Attributes:
        item_type: The item's element name (``Sequence``, ...).
        identifier: Its ``r:ID``.
        old_version: The version it had.
        new_version: The version it has now.
        changed_references: The references in it that now name a revised
            item's new version, as ``"Type id"``.
    """

    item_type: str
    identifier: str
    old_version: str
    new_version: str
    changed_references: tuple[str, ...] = ()


@dataclass(frozen=True)
class RevisionPlan:
    """What `DDIFragment.revise` changed, or would change on a dry run.

    Attributes:
        steps: One step per revised item, the edited items first, then their
            parents in the order reached.
        top_level_reference_updated: Whether the fragment's
            ``TopLevelReference`` was re-pointed at a new version.
        dry_run: Whether nothing was changed.
    """

    steps: tuple[RevisionStep, ...]
    top_level_reference_updated: bool = False
    dry_run: bool = False

    def __len__(self) -> int:
        return len(self.steps)

    def __iter__(self) -> Iterator[RevisionStep]:
        return iter(self.steps)


def _next_major(version: str) -> str:
    parts = version.split(".")
    if not parts or not all(part.isdigit() for part in parts):
        raise DDIModelError(f"Cannot increment the non-numeric version {version!r}.")
    return ".".join([str(int(parts[0]) + 1), *("0" for _ in parts[1:])])


def _set_responsibility(items: _Items, element: Element, responsibility: str) -> None:
    tag = items.tag("VersionResponsibility")
    existing = element.find(tag)
    if existing is None:
        existing = create_element(tag)
        existing.text = responsibility
        items.insert(element, _child_index(element, _IDENTIFICATION), existing)
    else:
        items.set_text(existing, responsibility)


def _set_rationale(
    items: _Items, element: Element, rationale: str | Mapping[str, str] | None
) -> None:
    """Drop the rationale of the previous version; record ``rationale``, if any.

    A string is one ``r:String``; a mapping gives one per language.
    """
    tag = items.tag("VersionRationale")
    for old in element.findall(tag):
        items.remove(element, old)
    texts = {"": rationale} if isinstance(rationale, str) else dict(rationale or {})
    texts = {language: text for language, text in texts.items() if text}
    if not texts:
        return
    holder = create_element(tag)
    description = create_element(items.tag("RationaleDescription"))
    for language, text in texts.items():
        string = create_element(items.tag("String"))
        if language:
            string.set(_XML_LANG, language)
        string.text = text
        description.append(string)
    holder.append(description)
    after = (
        *_IDENTIFICATION,
        "VersionResponsibility",
        "VersionResponsibilityReference",
    )
    items.insert(element, _child_index(element, after), holder)


def _set_version(items: _Items, element: Element, new: str) -> str:
    """Give ``element`` version ``new``, its ``r:URN`` included; return the old."""
    version_el = element.find(items.tag("Version"))
    assert version_el is not None
    old = version_el.text or ""
    items.set_text(version_el, new)
    urn = element.find(items.tag("URN"))
    if urn is not None and urn.text and urn.text.endswith(f":{old}"):
        items.set_text(urn, f"{urn.text[: -len(old)]}{new}")
    return old


def _declared_versions(
    items: _Items, element: Element, new: str
) -> dict[tuple[str, str], str]:
    """Give what ``element`` declares its version; return their old versions.

    Colectica gives an item's parameters and codes the item's own version.
    """
    old: dict[tuple[str, str], str] = {}
    for node in _identifiables(items, element):
        key = items.key(node)
        if key is not None and node.find(items.tag("Version")) is not None:
            old[key] = _set_version(items, node, new)
    return old


def _bump(
    items: _Items,
    element: Element,
    responsibility: str | None,
    stamp: str,
    rationale: str | Mapping[str, str] | None = None,
) -> tuple[str, str, dict[tuple[str, str], str]]:
    """Give ``element`` the next major version, as Colectica numbers them.

    Returns its old and new version, and the old version of each identifiable
    it declares, which now has the new one.
    """
    version_el = element.find(items.tag("Version"))
    if version_el is None:
        raise DDIModelError(f"{_describe(items, element)} has no r:Version.")
    new = _next_major(version_el.text or "")
    old = _set_version(items, element, new)
    declared = _declared_versions(items, element, new)
    if element.get("versionDate") is not None:
        items.set_attribute(element, "versionDate", stamp)
    if responsibility:
        _set_responsibility(items, element, responsibility)
    _set_rationale(items, element, rationale)
    return old, new, declared


def _repoint(items: _Items, reference: Element, old: str, new: str) -> None:
    version = reference.find(items.tag("Version"))
    if version is not None:
        items.set_text(version, new)
    urn = reference.find(items.tag("URN"))
    if urn is not None and urn.text and urn.text.endswith(f":{old}"):
        items.set_text(urn, f"{urn.text[: -len(old)]}{new}")


def revise(
    fragment: DDIFragment,
    items: Iterable[str | MaintainableBase | Element],
    *,
    cascade: bool = True,
    dry_run: bool = False,
    responsibility: str | None = None,
    version_date: str | None = None,
    rationale: str | Mapping[str, str] | None = None,
) -> RevisionPlan:
    """Give items a new version and, with ``cascade``, every item that pins them.

    See `DDIFragment.revise`.
    """
    from .config import get_configuration

    if responsibility is None:
        responsibility = get_configuration().version_responsibility
    # One revision is one moment, as when Colectica saves several items.
    stamp = version_date or colectica_timestamp()
    index = _Items(fragment)
    if dry_run:
        # The changes are made, then taken back: no copy of the fragment.
        index.journal = []
    try:
        steps, top_updated = _revised(
            fragment, index, items, cascade, responsibility, stamp, rationale
        )
    finally:
        index.undo()
    return RevisionPlan(steps, top_updated, dry_run=dry_run)


def _revised(
    fragment: DDIFragment,
    index: _Items,
    items: Iterable[str | MaintainableBase | Element],
    cascade: bool,
    responsibility: str | None,
    stamp: str,
    rationale: str | Mapping[str, str] | None,
) -> tuple[tuple[RevisionStep, ...], bool]:
    """`revise`'s changes, made through ``index``; its steps and top update."""
    queue = [index.find(item) for item in items]
    revised: dict[int, RevisionStep] = {}
    order: list[int] = []
    changed: dict[int, list[str]] = {}
    referrers = _Referrers(index) if cascade else None

    while queue:
        element = queue.pop(0)
        if id(element) in revised:
            continue
        key = index.key(element)
        old, new, declared = _bump(index, element, responsibility, stamp, rationale)
        revised[id(element)] = RevisionStep(
            _local(element.tag), key[1] if key else "", old, new
        )
        order.append(id(element))
        if referrers is None or key is None:
            continue
        # The item and what it declares, by their old versions.
        superseded = {key: old, **declared}
        for parent, reference in referrers.of(superseded):
            target = index.key(reference)
            assert target is not None
            if (
                (parent is not element or target != key)
                and reference.findtext(index.tag("Version")) == superseded[target]
                and reference.get("lateBound") not in _LATE_BOUND
            ):
                _repoint(index, reference, superseded[target], new)
                changed.setdefault(id(parent), []).append(
                    f"{reference.findtext(index.tag('TypeOfObject'))} {target[1]}"
                )
                if (
                    parent is not element
                    and id(parent) not in revised
                    and parent not in queue
                ):
                    queue.append(parent)

    top_updated = False
    top = fragment.root.find(qn(fragment._instance_ns, "TopLevelReference"))
    if top is not None:
        top_key = index.key(top)
        for step_id in order:
            step = revised[step_id]
            if (
                top_key
                and top_key[1] == step.identifier
                and (top.findtext(index.tag("Version")) == step.old_version)
            ):
                _repoint(index, top, step.old_version, step.new_version)
                top_updated = True

    steps = tuple(
        RevisionStep(
            revised[step_id].item_type,
            revised[step_id].identifier,
            revised[step_id].old_version,
            revised[step_id].new_version,
            tuple(changed.get(step_id, ())),
        )
        for step_id in order
    )
    return steps, top_updated


# ---- B3: sequence editing -------------------------------------------------------


@dataclass(frozen=True)
class EditResult:
    """The items an edit created or changed, by ``r:ID``.

    Pass ``touched`` to `DDIFragment.revise` to version the change;
    ``created`` items are new, at version 1.
    """

    touched: tuple[str, ...] = ()
    created: tuple[str, ...] = ()


def _construct_refs(sequence: Element) -> list[Element]:
    return [c for c in sequence if _local(c.tag) == "ControlConstructReference"]


def _insert_construct_ref(
    sequence: Element, reference: Element, index: int | None
) -> None:
    refs = _construct_refs(sequence)
    if refs:
        if index is not None and index < 0:
            # Counted from the end, as list.insert() does.
            index = max(index + len(refs), 0)
        if index is None or index >= len(refs):
            position = list(sequence).index(refs[-1]) + 1
        else:
            position = list(sequence).index(refs[max(index, 0)])
    else:
        after = [c for c in sequence if _local(c.tag) == "ConstructSequence"]
        position = list(sequence).index(after[0]) if after else len(sequence)
    sequence.insert(position, reference)


def _reference_to(items: _Items, target: Element, tag: str) -> Element:
    reference = create_element(tag)
    for name in ("Agency", "ID", "Version"):
        child = create_element(items.tag(name))
        child.text = target.findtext(items.tag(name))
        reference.append(child)
    kind = create_element(items.tag("TypeOfObject"))
    kind.text = _local(target.tag)
    reference.append(kind)
    return reference


def move_construct(
    fragment: DDIFragment,
    construct: str | MaintainableBase | Element,
    from_sequence: str | MaintainableBase | Element,
    to_sequence: str | MaintainableBase | Element,
    *,
    index: int | None = None,
) -> EditResult:
    """Move a construct's reference from one sequence to another.

    See `DDIFragment.move_construct`.
    """
    items = _Items(fragment)
    target = items.find(construct)
    source = items.find(from_sequence)
    destination = items.find(to_sequence)
    key = items.key(target)
    reference = next(
        (ref for ref in _construct_refs(source) if items.key(ref) == key), None
    )
    if reference is None:
        raise KeyError(
            f"{_local(source.tag)} {source.findtext(items.tag('ID'))} does not "
            f"contain {_local(target.tag)} {key[1] if key else ''}."
        )
    # What moves is the version the reference pins.
    pinned = _pinned(items, reference)
    _refuse_cycle(items, destination, target if pinned is None else pinned, key)
    source.remove(reference)
    _insert_construct_ref(destination, reference, index)
    touched = [source.findtext(items.tag("ID")) or ""]
    if destination is not source:
        touched.append(destination.findtext(items.tag("ID")) or "")
    return EditResult(touched=tuple(touched))


# The members of DDI 3.3's ControlConstruct substitution group: what a
# sequence's ControlConstructReference may point at.
_CONTROL_CONSTRUCTS = frozenset(
    {
        "ComputationItem",
        "DevelopmentStep",
        "IfThenElse",
        "Loop",
        "MeasurementConstruct",
        "QuestionConstruct",
        "RepeatUntil",
        "RepeatWhile",
        "SampleStep",
        "SamplingStage",
        "Sequence",
        "Split",
        "SplitJoin",
        "StatementItem",
    }
)


def _require_construct(items: _Items, element: Element) -> None:
    local = _local(element.tag)
    if local in _CONTROL_CONSTRUCTS:
        return
    hint = (
        "; place the QuestionConstruct that asks it"
        if local in ("QuestionItem", "QuestionGrid", "QuestionBlock")
        else ""
    )
    raise DDIModelError(
        f"{local} {element.findtext(items.tag('ID'))} is not a control "
        f"construct, so a sequence cannot contain it{hint}."
    )


def _pinned(items: _Items, reference: Element) -> Element | None:
    """The version of its item a reference points at: latest when late-bound."""
    target = items.key(reference)
    payloads = items.versions.get(target) if target else None
    if not payloads:
        return None
    if (reference.get("lateBound") or "").strip() in ("true", "1"):
        return payloads[0]
    version = reference.findtext(items.tag("Version"))
    return next((p for p in payloads if items.version(p) == version), payloads[0])


def _flow_references(items: _Items, element: Element) -> Iterator[Element]:
    """The typed references under ``element``, lineage and user attributes aside."""
    type_tag = items.tag("TypeOfObject")
    stack = list(element)
    while stack:
        node = stack.pop()
        if not isinstance(node.tag, str):
            continue
        if _local(node.tag) in ("BasedOnObject", "UserAttributePair"):
            continue
        if node.tag.endswith("Reference") and node.find(type_tag) is not None:
            yield node
        else:
            stack.extend(node)


def _contains(items: _Items, start: Element, goal: tuple[str, str] | None) -> bool:
    """Whether ``goal`` is ``start`` or a construct in the flow under it.

    The flow is followed at the version each reference pins (the latest for
    a late-bound one); lineage (``r:BasedOnObject``) and user attributes are
    not flow.
    """
    seen: set[int] = set()
    stack = [start]
    while stack:
        element = stack.pop()
        if items.key(element) == goal:
            return True
        if id(element) in seen:
            continue
        seen.add(id(element))
        for reference in _flow_references(items, element):
            kind = reference.findtext(items.tag("TypeOfObject"))
            target = items.key(reference)
            if kind not in _CONTROL_CONSTRUCTS:
                continue
            if target == goal:
                return True
            pinned = _pinned(items, reference)
            if pinned is not None:
                stack.append(pinned)
    return False


def _refuse_cycle(
    items: _Items, sequence: Element, construct: Element, key: tuple[str, str] | None
) -> None:
    """Raise if placing ``construct`` in ``sequence`` would make a cycle."""
    sequence_id = sequence.findtext(items.tag("ID")) or ""
    if key == items.key(sequence):
        raise ValueError(f"{_local(sequence.tag)} {sequence_id} cannot contain itself.")
    if _contains(items, construct, items.key(sequence)):
        raise ValueError(
            f"{_local(sequence.tag)} {sequence_id} cannot contain "
            f"{_local(construct.tag)} {key[1] if key else ''}, which contains it."
        )


def insert_construct(
    fragment: DDIFragment,
    sequence: str | MaintainableBase | Element,
    construct: str | MaintainableBase | Element,
    *,
    index: int | None = None,
    before: str | MaintainableBase | Element | None = None,
    after: str | MaintainableBase | Element | None = None,
    colectica: bool = True,
) -> EditResult:
    """Place a construct, new or in the fragment, in a sequence.

    See `DDIFragment.insert_construct`.
    """
    from .document import _fragment_payload

    if sum(option is not None for option in (index, before, after)) > 1:
        raise ValueError("Pass at most one of index, before and after.")
    items = _Items(fragment)
    parent = items.find(sequence)
    parent_id = parent.findtext(items.tag("ID")) or ""
    if _local(parent.tag) != "Sequence":
        raise DDIModelError(f"{_local(parent.tag)} {parent_id} is not a Sequence.")

    # Every check comes before the fragment changes: a call that fails adds
    # nothing.
    new_element: Element | None = None
    if isinstance(construct, MaintainableBase):
        try:
            target = items.find(construct)
        except KeyError:
            missing = [
                name
                for name, value in (
                    ("agency", construct.agency),
                    ("identifier", construct.identifier),
                    ("version", construct.version),
                )
                if not value
            ]
            if missing:
                raise ValueError(
                    f"A new {type(construct).__name__} needs an agency, identifier "
                    f"and version to be placed; it has no {', '.join(missing)}."
                ) from None
            new_element = target = _fragment_payload(construct)
    else:
        target = items.find(construct)
    _require_construct(items, target)

    key = items.key(target)
    target_id = key[1] if key else ""
    described = f"{_local(target.tag)} {target_id}"
    _refuse_cycle(items, parent, target, key)
    refs = _construct_refs(parent)
    if any(items.key(ref) == key for ref in refs):
        raise ValueError(
            f"Sequence {parent_id} already contains {described}; move it with "
            "move_construct()."
        )
    position = index
    for anchor, offset in ((before, 0), (after, 1)):
        if anchor is None:
            continue
        anchor_key = items.key(items.find(anchor))
        found = [n for n, ref in enumerate(refs) if items.key(ref) == anchor_key]
        if not found:
            raise KeyError(
                f"Sequence {parent_id} does not contain "
                f"{anchor_key[1] if anchor_key else anchor!r}."
            )
        position = found[0] + offset

    if new_element is not None:
        if colectica:
            apply_colectica_conventions([new_element], reusable_ns=items.r)
        fragment.add_fragment(new_element)
    _insert_construct_ref(
        parent,
        _reference_to(
            items, target, qn(DATA_COLLECTION_NS, "ControlConstructReference")
        ),
        position,
    )
    return EditResult(
        touched=(parent_id,), created=(target_id,) if new_element is not None else ()
    )


def _new_item(
    items: _Items, local: str, agency: str, name: str, language: str, stamp: str
) -> Element:
    from .config import get_configuration

    element = create_element(qn(DATA_COLLECTION_NS, local))
    identifier = str(uuid.uuid4())
    element.set("isUniversallyUnique", "true")
    element.set("versionDate", stamp)
    for tag, text in (
        ("URN", f"urn:ddi:{agency}:{identifier}:1"),
        ("Agency", agency),
        ("ID", identifier),
        ("Version", "1"),
        ("VersionResponsibility", get_configuration().version_responsibility),
    ):
        if text is None:
            continue
        child = create_element(items.tag(tag))
        child.text = text
        element.append(child)
    construct_name = create_element(qn(DATA_COLLECTION_NS, "ConstructName"))
    string = create_element(items.tag("String"))
    string.set(_XML_LANG, language)
    string.text = name
    construct_name.append(string)
    element.append(construct_name)
    return element


def wrap_in_condition(
    fragment: DDIFragment,
    sequence: str | MaintainableBase | Element,
    constructs: Sequence[str | MaintainableBase | Element],
    condition: AnyCondition,
    *,
    name: str | None = None,
) -> EditResult:
    """Put constructs of a sequence under a new ``IfThenElse``.

    See `DDIFragment.wrap_in_condition`.
    """
    items = _Items(fragment)
    parent = items.find(sequence)
    wanted = [items.key(items.find(construct)) for construct in constructs]
    refs = [ref for ref in _construct_refs(parent) if items.key(ref) in wanted]
    if len(refs) != len(wanted):
        raise KeyError(
            f"{_local(parent.tag)} {parent.findtext(items.tag('ID'))} does not "
            "contain every construct to wrap."
        )
    agency = parent.findtext(items.tag("Agency")) or ""
    label = name or "Condition"
    # Name the new items in the language the sequence is named in.
    parent_name = next((c for c in parent if _local(c.tag) == "ConstructName"), None)
    named = None if parent_name is None else parent_name.find(items.tag("String"))
    language = (named.get(_XML_LANG) if named is not None else None) or "en"

    # The two new items are saved together, so they share one moment.
    stamp = colectica_timestamp()
    then = _new_item(items, "Sequence", agency, f"{label} (then)", language, stamp)
    kind = create_element(qn(DATA_COLLECTION_NS, "TypeOfSequence"))
    kind.text = "ConditionalChildContainer"
    then.append(kind)
    position = list(parent).index(refs[0])
    for ref in refs:
        parent.remove(ref)
        then.append(ref)

    gate = _new_item(items, "IfThenElse", agency, label, language, stamp)
    if_condition = create_element(qn(DATA_COLLECTION_NS, "IfCondition"))
    command = create_element(items.tag("Command"))
    program = create_element(items.tag("ProgramLanguage"))
    program.text = condition.language
    content = create_element(items.tag("CommandContent"))
    content.text = serialize_condition(condition)
    command.append(program)
    command.append(content)
    if_condition.append(command)
    gate.append(if_condition)
    gate.append(
        _reference_to(items, then, qn(DATA_COLLECTION_NS, "ThenConstructReference"))
    )

    parent.insert(
        position,
        _reference_to(items, gate, qn(DATA_COLLECTION_NS, "ControlConstructReference")),
    )
    fragment.add_fragment(gate)
    fragment.add_fragment(then)
    return EditResult(
        touched=(parent.findtext(items.tag("ID")) or "",),
        created=(
            gate.findtext(items.tag("ID")) or "",
            then.findtext(items.tag("ID")) or "",
        ),
    )


# ---- B4: duplicate and repair ------------------------------------------------------


def _identifiables(items: _Items, element: Element) -> Iterator[Element]:
    """Elements with their own Agency and ID under ``element``, references aside."""
    stack = list(element)
    while stack:
        node = stack.pop()
        if not isinstance(node.tag, str) or node.tag.endswith("Reference"):
            continue
        if items.key(node) is not None:
            yield node
        stack.extend(node)


def _set_id(items: _Items, element: Element, new_id: str) -> None:
    id_el = element.find(items.tag("ID"))
    assert id_el is not None
    old = id_el.text or ""
    items.set_text(id_el, new_id)
    urn = element.find(items.tag("URN"))
    if urn is not None and urn.text and f":{old}:" in urn.text:
        items.set_text(urn, urn.text.replace(f":{old}:", f":{new_id}:"))


def _repoint_id(items: _Items, element: Element, id_map: dict[str, str]) -> int:
    """Point references under ``element`` at the new IDs of ``id_map``."""
    count = 0
    for reference in items.references(element):
        id_el = reference.find(items.tag("ID"))
        if id_el is not None and id_el.text in id_map:
            old = id_el.text
            items.set_text(id_el, id_map[old])
            urn = reference.find(items.tag("URN"))
            if urn is not None and urn.text:
                items.set_text(urn, urn.text.replace(f":{old}:", f":{id_map[old]}:"))
            count += 1
    return count


def duplicate(
    fragment: DDIFragment,
    item: str | MaintainableBase | Element,
    *,
    new_id: str | None = None,
) -> tuple[MaintainableBase, dict[str, str]]:
    """Copy an item with fresh IDs for it and everything it declares.

    See `DDIFragment.duplicate`.
    """
    from .config import get_configuration

    items = _Items(fragment)
    source = items.find(item)
    copy = clone_element(source)
    id_map: dict[str, str] = {}
    root_id = copy.findtext(items.tag("ID")) or ""
    id_map[root_id] = new_id or str(uuid.uuid4())
    for node in _identifiables(items, copy):
        old = node.findtext(items.tag("ID")) or ""
        id_map.setdefault(old, str(uuid.uuid4()))
    for node in [copy, *_identifiables(items, copy)]:
        _set_id(items, node, id_map[node.findtext(items.tag("ID")) or ""])
    # References inside the copy to what the copy declares (a binding to its
    # own parameter) follow the new IDs; references elsewhere are kept.
    _repoint_id(items, copy, id_map)

    version = copy.find(items.tag("Version"))
    old_version = version.text if version is not None else None
    if version is not None:
        version.text = "1"
    urn = copy.find(items.tag("URN"))
    if urn is not None and urn.text and old_version:
        urn.text = urn.text.rsplit(":", 1)[0] + ":1"
    # What the copy declares starts at its version too.
    _declared_versions(items, copy, "1")
    if copy.get("versionDate") is not None:
        copy.set("versionDate", colectica_timestamp())
    responsibility = get_configuration().version_responsibility
    if responsibility:
        _set_responsibility(items, copy, responsibility)

    for existing in copy.findall(items.tag("BasedOnObject")):
        copy.remove(existing)
    based_on = create_element(items.tag("BasedOnObject"))
    based_on.append(_reference_to(items, source, items.tag("BasedOnReference")))
    rationale = create_element(items.tag("BasedOnRationaleCode"))
    rationale.text = "DuplicateItem"
    based_on.append(rationale)
    copy.insert(_child_index(copy, _VERSIONING), based_on)

    fragment.add_fragment(copy)
    MaintainableBase.maintainable_types()
    model = MaintainableBase.for_tag(copy.tag)
    if model is None:  # pragma: no cover - every fragment item type has one
        raise DDIModelError(f"No model for {copy.tag}.")
    return model.from_xml(copy), id_map


@dataclass(frozen=True)
class RepairStep:
    """One shared identifiable `repair_shared_identifiables` re-identifies.

    Attributes:
        item_type: The shared element's name (``OutParameter``, ...).
        old_id: The ID the items shared.
        new_id: The ID the copy gets.
        kept_in: The item keeping ``old_id`` (``"Type id"``).
        copy: The item getting ``new_id``.
        rebound: References re-pointed in the copy's own question
            constructs.
        ambiguous: References to ``old_id`` elsewhere, left as they are: it
            cannot be told which item they mean.
    """

    item_type: str
    old_id: str
    new_id: str
    kept_in: str
    copy: str
    rebound: int = 0
    ambiguous: tuple[str, ...] = ()


@dataclass(frozen=True)
class RepairPlan:
    """What `DDIFragment.repair_shared_identifiables` changed or would change."""

    steps: tuple[RepairStep, ...] = ()
    dry_run: bool = True
    touched: tuple[str, ...] = field(default=())

    def __len__(self) -> int:
        return len(self.steps)

    def __iter__(self) -> Iterator[RepairStep]:
        return iter(self.steps)


def _describe(items: _Items, element: Element) -> str:
    return f"{_local(element.tag)} {element.findtext(items.tag('ID')) or ''}"


def _keeper(items: _Items, owners: list[Element]) -> Element:
    """The original among items sharing an identifiable.

    The earliest ``versionDate``; then one with no ``r:BasedOnObject`` (a
    copy records its source there); then the first in the file.
    """

    def order(pair: tuple[int, Element]) -> tuple[str, int, int]:
        position, element = pair
        stamp = element.get("versionDate") or "9999"
        copied = 1 if element.find(items.tag("BasedOnObject")) is not None else 0
        return (stamp, copied, position)

    return min(enumerate(owners), key=order)[1]


def repair_shared_identifiables(
    fragment: DDIFragment, *, dry_run: bool = True
) -> RepairPlan:
    """Give each copy of a shared identifiable an ID of its own.

    See `DDIFragment.repair_shared_identifiables`.
    """
    items = _Items(fragment)
    if dry_run:
        # The changes are made, then taken back: no copy of the fragment.
        items.journal = []
    try:
        steps, touched = _repaired(items)
    finally:
        items.undo()
    return RepairPlan(
        tuple(steps), dry_run=dry_run, touched=tuple(dict.fromkeys(touched))
    )


def _repaired(items: _Items) -> tuple[list[RepairStep], list[str]]:
    """`repair_shared_identifiables`'s changes, made through ``items``."""
    owners: dict[tuple[str, str], dict[tuple[str, str], Element]] = {}
    kinds: dict[tuple[str, str], str] = {}
    for parent in items.latest():
        parent_key = items.key(parent)
        for node in _identifiables(items, parent):
            node_key = items.key(node)
            assert node_key is not None and parent_key is not None
            owners.setdefault(node_key, {}).setdefault(parent_key, parent)
            kinds.setdefault(node_key, _local(node.tag))

    steps: list[RepairStep] = []
    touched: list[str] = []
    for node_key, parents in owners.items():
        if len(parents) < 2:
            continue
        keeper = _keeper(items, list(parents.values()))
        constructs_of: dict[tuple[str, str], list[Element]] = {}
        for construct in items.latest():
            if _local(construct.tag) != "QuestionConstruct":
                continue
            reference = construct.find(items.tag("QuestionReference"))
            question = items.key(reference) if reference is not None else None
            if question is not None:
                constructs_of.setdefault(question, []).append(construct)
        handled: set[int] = set()
        pending: list[tuple[Element, str, int]] = []
        for parent_key, parent in parents.items():
            if parent is keeper:
                continue
            new_id = str(uuid.uuid4())
            for version in items.versions[parent_key]:
                for node in _identifiables(items, version):
                    if items.key(node) == node_key:
                        _set_id(items, node, new_id)
            rebound = 0
            for construct in constructs_of.get(parent_key, []):
                rebound += _repoint_id(items, construct, {node_key[1]: new_id})
                handled.add(id(construct))
                touched.append(construct.findtext(items.tag("ID")) or "")
            touched.append(parent_key[1])
            pending.append((parent, new_id, rebound))
        # The keeper's own constructs rightly bind the ID it keeps; any other
        # reference to it cannot be told apart and is reported, not guessed.
        keeper_constructs = {
            id(construct)
            for construct in constructs_of.get(items.key(keeper) or ("", ""), [])
        }
        ambiguous = tuple(
            _describe(items, element)
            for element in items.latest()
            if element is not keeper
            and id(element) not in handled | keeper_constructs
            and any(
                items.key(reference) == node_key
                for reference in items.references(element)
            )
        )
        for parent, new_id, rebound in pending:
            steps.append(
                RepairStep(
                    kinds[node_key],
                    node_key[1],
                    new_id,
                    _describe(items, keeper),
                    _describe(items, parent),
                    rebound,
                    ambiguous,
                )
            )
    return steps, touched
