"""Flow walks as they were before they stopped enumerating paths.

Frozen copies, kept as oracles: the walks that replaced them must report
exactly what these do wherever these finish. Do not change them.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from ddi_l._etree import Element
from ddi_l.colectica_lint import (
    _Context,
    _flow_children,
    _flow_roots,
    _local,
    _reads,
    _Wiring,
)
from ddi_l.lint import LintFinding, LintTarget


def legacy_read_before_computed(document: LintTarget) -> Iterable[LintFinding]:
    """`colectica.flow.read-before-computed` as of commit c4b385e."""
    context = _Context(document)
    wiring = _Wiring.of(context)
    reads = _reads(context)
    parents = Counter(
        id(child) for item in context.items for child in _flow_children(context, item)
    )
    for root in _flow_roots(context):
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
                verb = (
                    "asks"
                    if _local(producer.tag) == "QuestionConstruct"
                    else "computes"
                )
                yield context.finding(
                    "colectica.flow.read-before-computed",
                    "warning",
                    element,
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
