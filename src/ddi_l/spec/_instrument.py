"""An instrument as `ddi_l.spec.conform` reads it.

The walk starts at an ``Instrument`` and follows its control constructs:
sequences, the Then, ElseIf and Else branches of each ``IfThenElse``, and
the bodies of loops. For each construct reached it records the ordinary
sequences above it and the gates on the way (an ``IfThenElse`` branch).

A sequence typed ``ConditionalChildContainer`` is the body of a branch, not
a module or a page: it is passed through. A construct that refers back to
one above it is not followed again.

A construct is one node for each run of sequences above it, however many
paths lead there: the node keeps the gates of the first path, in walk
order, and counts the paths. `InstrumentIndex.first_path` asks about every
path without walking them one by one. When a path can meet one construct
(agency and ID) twice, each path is its own node.
"""

from __future__ import annotations

import graphlib
from collections.abc import Callable, Collection, Hashable, Iterator
from dataclasses import dataclass, field
from typing import TypeVar

from .._etree import Element
from ..colectica_lint import _Context, _local

__all__: list[str] = []

CONDITIONAL_CHILD_CONTAINER = "ConditionalChildContainer"

_V = TypeVar("_V", bound=Hashable)


@dataclass(frozen=True)
class GateTerm:
    """One gate on the path to a construct.

    Attributes:
        gate: The ``IfThenElse``.
        branch: ``0`` for its Then branch, ``n`` for its n-th ``ElseIf``,
            ``-1`` for its Else branch.
    """

    gate: Element
    branch: int


@dataclass
class Node:
    """A construct reached from the instrument, under one run of sequences.

    Attributes:
        element: The construct.
        kind: Its element name (``QuestionConstruct``, ``Sequence``...).
        sequences: The ordinary sequences above it, outermost first.
        gates: The gates on the first path to it, outermost first.
        entered: For each of ``sequences``, how many of ``gates`` were on the
            way to it.
        paths: How many paths from the instrument lead to it.
    """

    element: Element
    kind: str
    sequences: tuple[Element, ...] = ()
    gates: tuple[GateTerm, ...] = ()
    entered: tuple[int, ...] = ()
    paths: int = 0

    def gates_inside(self, sequence: Element) -> tuple[GateTerm, ...]:
        """The gates on the first path between ``sequence`` and the construct.

        ``sequence`` is one of `sequences` or the construct itself.
        """
        if sequence is self.element:
            return ()
        for above, depth in zip(self.sequences, self.entered, strict=True):
            if above is sequence:
                return self.gates[depth:]
        return self.gates

    @property
    def is_page_or_module(self) -> bool:
        """Whether it is an ordinary sequence: a module or a page."""
        return self.kind == "Sequence" and not _is_branch_body(self.element)

    @property
    def depth(self) -> int:
        """Its depth: the instrument's own sequence is 1, its children 2."""
        return len(self.sequences) + (1 if self.is_page_or_module else 0)


def _is_branch_body(sequence: Element) -> bool:
    return any(
        _local(child.tag) == "TypeOfSequence"
        and (child.text or "").strip() == CONDITIONAL_CHILD_CONTAINER
        for child in sequence
    )


def _texts(element: Element) -> list[str]:
    """The distinct non-empty texts in ``element`` (every language)."""
    found: dict[str, None] = {}
    for node in element.iter():
        if isinstance(node.tag, str) and (node.text or "").strip():
            found.setdefault(node.text.strip(), None)  # type: ignore[union-attr]
    return list(found)


_Edges = list[tuple[Node, GateTerm | None]]


def leads(element: Element) -> Iterator[tuple[Element, GateTerm | None]]:
    """The references to the constructs ``element`` leads to, with their gates."""
    kind = _local(element.tag)
    if kind == "IfThenElse":
        branch = 0
        for child in element:
            local = _local(child.tag)
            if local == "ThenConstructReference":
                yield child, GateTerm(element, 0)
            elif local == "ElseIf":
                branch += 1
                for grandchild in child:
                    if _local(grandchild.tag) == "ThenConstructReference":
                        yield grandchild, GateTerm(element, branch)
            elif local == "ElseConstructReference":
                yield child, GateTerm(element, -1)
        return
    for child in element:
        local = _local(child.tag)
        if local in (
            "ControlConstructReference",
            "UntilConstructReference",
            "WhileConstructReference",
        ):
            yield child, None


@dataclass
class InstrumentIndex:
    """Every construct one instrument reaches, in walk order.

    One node per construct and run of sequences above it (see `Node`).
    """

    context: _Context
    instrument: Element
    nodes: list[Node] = field(default_factory=list)
    _leads: dict[int, list[tuple[Element, GateTerm | None]]] = field(
        default_factory=dict, init=False, repr=False
    )
    # What each node leads to, by id(node), and what the instrument does.
    _below: dict[int, _Edges] = field(default_factory=dict, init=False, repr=False)
    _top: _Edges = field(default_factory=list, init=False, repr=False)
    # Each node after every node it leads to.
    _finished: list[Node] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self._top = self._walk(
            self.instrument, (), (), (), (), {}, by_path=self._meets_a_key_twice()
        )
        for node, _ in self._top:
            node.paths += 1
        for node in reversed(self._finished):
            for below, _ in self._below[id(node)]:
                below.paths += node.paths

    def _references(
        self, element: Element
    ) -> Iterator[tuple[Element, GateTerm | None]]:
        """The constructs ``element`` leads to, and the gate on each way."""
        return leads(element)

    def _targets(self, element: Element) -> list[tuple[Element, GateTerm | None]]:
        """The constructs ``element`` leads to that resolve, with their gates."""
        found = self._leads.get(id(element))
        if found is None:
            found = self._leads[id(element)] = [
                (target, term)
                for reference, term in self._references(element)
                if (target := self.context.resolve(reference)) is not None
            ]
        return found

    def _meets_a_key_twice(self) -> bool:
        """Whether a path from the instrument can meet one agency and ID twice."""
        graph: dict[tuple[str, str], set[tuple[str, str]]] = {}
        seen = {id(self.instrument)}
        stack = [self.instrument]
        while stack:
            element = stack.pop()
            after = graph.setdefault(self._key(element), set())
            for target, _ in self._targets(element):
                after.add(self._key(target))
                if id(target) not in seen:
                    seen.add(id(target))
                    stack.append(target)
        try:
            tuple(graphlib.TopologicalSorter(graph).static_order())
        except graphlib.CycleError:
            return True
        return False

    def _walk(
        self,
        element: Element,
        sequences: tuple[Element, ...],
        entered: tuple[int, ...],
        gates: tuple[GateTerm, ...],
        path: tuple[tuple[str, str], ...],
        seen: dict[Hashable, Node],
        *,
        by_path: bool,
    ) -> _Edges:
        """The nodes ``element`` leads to, walking each new one.

        Two ways to one construct under the same sequences reach one node,
        walked once: what is below a node depends on nothing else. With
        ``by_path``, the path is part of the node too, so a construct met
        again on it is not followed.
        """
        edges: _Edges = []
        for target, term in self._targets(element):
            key = self._key(target)
            if key in path:
                continue
            state = (id(target), tuple(map(id, sequences)), path)
            node = seen.get(state)
            if node is None:
                node = seen[state] = Node(
                    target,
                    _local(target.tag),
                    sequences,
                    gates if term is None else (*gates, term),
                    entered,
                )
                self.nodes.append(node)
                below, below_entered = sequences, entered
                if node.is_page_or_module:
                    below = (*sequences, target)
                    below_entered = (*entered, len(node.gates))
                self._below[id(node)] = self._walk(
                    target,
                    below,
                    below_entered,
                    node.gates,
                    (*path, key) if by_path else (),
                    seen,
                    by_path=by_path,
                )
                self._finished.append(node)
            edges.append((node, term))
        return edges

    def _key(self, element: Element) -> tuple[str, str]:
        return (
            element.findtext(self.context.r("Agency")) or "",
            element.findtext(self.context.r("ID")) or "",
        )

    def of_kind(self, *kinds: str) -> list[Node]:
        """The nodes of these element names, in walk order."""
        return [node for node in self.nodes if node.kind in kinds]

    def nodes_of(self, element: Element) -> list[Node]:
        """The nodes of ``element``, in walk order."""
        return [node for node in self.nodes if node.element is element]

    # ---- Every path -------------------------------------------------------------

    def first_path(
        self,
        targets: Collection[Node],
        below: Element,
        fold: Callable[[_V, GateTerm], _V],
        start: _V,
        accept: Callable[[_V], bool],
    ) -> tuple[Node, tuple[GateTerm, ...]] | None:
        """The first path, in walk order, to one of ``targets`` that ``accept`` takes.

        ``below`` is one of the `Node.sequences` of every target. The gates on
        a path below it are folded with ``fold``, from ``start``, and
        ``accept`` takes or leaves the result. Returns the path's target
        and those gates, or ``None`` when ``accept`` takes no path.

        A node is searched once for each value the fold reaches it with, so
        the paths are not walked one by one.
        """
        wanted = {id(node) for node in targets}
        leading = set(wanted)
        for node in self._finished:
            if any(id(child) in leading for child, _ in self._below[id(node)]):
                leading.add(id(node))
        exhausted: set[tuple[int, bool, _V]] = set()
        gates: list[GateTerm] = []

        def search(edges: _Edges, inside: bool, value: _V) -> Node | None:
            for node, term in edges:
                if id(node) not in leading:
                    continue
                folded = value
                if inside and term is not None:
                    folded = fold(value, term)
                    gates.append(term)
                now_inside = inside or node.element is below
                if now_inside and id(node) in wanted and accept(folded):
                    return node
                if (id(node), now_inside, folded) not in exhausted:
                    found = search(self._below[id(node)], now_inside, folded)
                    if found is not None:
                        return found
                    exhausted.add((id(node), now_inside, folded))
                if inside and term is not None:
                    gates.pop()
            return None

        found = search(self._top, False, start)
        return None if found is None else (found, tuple(gates))

    # ---- Where an id can be ----------------------------------------------------

    def question_item(self, construct: Element) -> Element | None:
        """The question a ``QuestionConstruct`` asks."""
        reference = construct.find(self.context.r("QuestionReference"))
        return None if reference is None else self.context.resolve(reference)

    def ids(self, element: Element, source: str) -> list[str]:
        """The values ``source`` gives for ``element``.

        ``construct_name``, ``label`` and ``user_id`` read the element's own
        ``ConstructName``, ``r:Label`` and ``r:UserID``; ``construct_alias``
        the alias of its ``r:OutParameter``; ``item_name`` and ``item_alias``
        the name and output alias of the question a ``QuestionConstruct``
        asks.
        """
        if source in ("item_name", "item_alias"):
            if _local(element.tag) != "QuestionConstruct":
                return []
            item = self.question_item(element)
            if item is None:
                return []
            if source == "item_alias":
                return self._aliases(item)
            return [
                text
                for child in item
                if _local(child.tag).startswith("Question")
                and _local(child.tag).endswith("Name")
                for text in _texts(child)
            ]
        if source == "construct_alias":
            return self._aliases(element)
        local = {
            "construct_name": "ConstructName",
            "label": "Label",
            "user_id": "UserID",
        }[source]
        found: dict[str, None] = {}
        for child in element:
            if _local(child.tag) == local:
                for text in _texts(child):
                    found.setdefault(text, None)
        return list(found)

    def _aliases(self, element: Element) -> list[str]:
        found: dict[str, None] = {}
        for parameter in element.findall(self.context.r("OutParameter")):
            alias = (parameter.findtext(self.context.r("Alias")) or "").strip()
            if alias:
                found.setdefault(alias, None)
        return list(found)
