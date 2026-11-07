"""The instrument walk as it was before nodes stood for more than one path.

A frozen copy, kept as an oracle: the index that replaced it must give
`ddi_l.spec.conform` exactly what this one does. Every path is its own node,
and `first_path` tries them one by one. Do not change the walk.
"""

from __future__ import annotations

from collections.abc import Callable, Collection
from typing import TypeVar

from ddi_l._etree import Element
from ddi_l.colectica_lint import _local
from ddi_l.spec._instrument import GateTerm, InstrumentIndex, Node

V = TypeVar("V")


class LegacyInstrumentIndex(InstrumentIndex):
    """`InstrumentIndex` as of commit c4b385e: one node per path."""

    def __post_init__(self) -> None:
        self._walk_paths(self.instrument, (), (), (), ())

    def _walk_paths(
        self,
        element: Element,
        sequences: tuple[Element, ...],
        entered: tuple[int, ...],
        gates: tuple[GateTerm, ...],
        path: tuple[tuple[str, str], ...],
    ) -> None:
        for reference, term in self._references(element):
            target = self.context.resolve(reference)
            if target is None:
                continue
            key = self._key(target)
            if key in path:
                continue
            node = Node(
                target,
                _local(target.tag),
                sequences,
                gates if term is None else (*gates, term),
                entered,
                paths=1,
            )
            self.nodes.append(node)
            below, below_entered = sequences, entered
            if node.is_page_or_module:
                below = (*sequences, target)
                below_entered = (*entered, len(node.gates))
            self._walk_paths(target, below, below_entered, node.gates, (*path, key))

    def nodes_of(self, element: Element) -> list[Node]:
        return [node for node in self.nodes if node.element is element]

    def first_path(
        self,
        targets: Collection[Node],
        below: Element,
        fold: Callable[[V, GateTerm], V],
        start: V,
        accept: Callable[[V], bool],
    ) -> tuple[Node, tuple[GateTerm, ...]] | None:
        wanted = {id(node) for node in targets}
        for node in self.nodes:
            if id(node) not in wanted:
                continue
            gates = node.gates_inside(below)
            value = start
            for term in gates:
                value = fold(value, term)
            if accept(value):
                return node, gates
        return None
