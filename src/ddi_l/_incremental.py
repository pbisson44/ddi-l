"""What is read from an unchanged element is not read again.

On the native backend each element's content digest is cached on the tree
and cleared by any change below it. So what a document's reader worked out
from one element can be kept under that element's digest and reused while
the digest is the same: an edit costs a re-read of what it changed.

`findings` does this for a lint rule registered with ``per_item=True``,
which reports about each item from that item alone: a later run of the rule
re-runs it for the items whose digest is new only. The first run is the
rule's ordinary run, each finding filed under the item it is about; if that
cannot be done, the rule runs in full every time. A finding reports an item
by its tag on the native backend, not its position, so moving an item
changes nothing. `per_element` and `per_chunk` do it for any reader: the
other lint rules' facts, and who refers to what for `revise`.

The kept results live in the document's ``_incremental_cache``. Other
backends read everything every time.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from ._etree import NATIVE
from ._facts import limited_to, record_findings

if TYPE_CHECKING:  # pragma: no cover - for annotations only
    from .lint import LintFinding, LintTarget, _LintRule

__all__ = ["findings", "per_chunk", "per_element"]


def findings(document: LintTarget, rule: _LintRule) -> list[LintFinding]:
    """``rule``'s findings on ``document``, re-run for changed items only."""
    store = getattr(document, "__dict__", None)
    if not NATIVE or store is None:
        return list(rule.run(document))
    import ddi_l_native

    from .colectica_lint import _Context
    from .lint import get_lint_configuration

    items = _Context(document).items
    if not all(isinstance(item, ddi_l_native.Element) for item in items):
        return list(rule.run(document))
    digests = [ddi_l_native.digest(item) for item in items]
    caches: dict[Any, dict[bytes, Sequence[LintFinding]]] = store.setdefault(
        "_incremental_cache", {}
    )
    key = (rule.rule_id, get_lint_configuration())
    known = caches.get(key)
    fresh: dict[bytes, Sequence[LintFinding]]
    if known is None:
        by_item = _sorted_out(document, rule, items)
        if by_item is None:
            return list(rule.run(document))
        # Most items have no finding: they share one empty tuple.
        fresh = {digest: by_item.get(at, ()) for at, digest in enumerate(digests)}
    else:
        fresh = {}
        for item, digest in zip(items, digests, strict=True):
            if digest in fresh:
                continue
            if digest in known:
                fresh[digest] = known[digest]
                continue
            found = _about(document, rule, item)
            if found is None:
                del caches[key]
                return list(rule.run(document))
            fresh[digest] = found
    caches[key] = fresh
    return [finding for digest in digests for finding in fresh[digest]]


def _about(document: LintTarget, rule: _LintRule, item: Any) -> list[Any] | None:
    """``rule``'s findings about ``item``; ``None`` if some are about others."""
    import ddi_l_native

    with limited_to((item,)), record_findings() as recorded:
        produced = list(rule.run(document))
    if len(recorded) != len(produced):
        return None
    for _, element in recorded:
        node = element
        while node is not None and node is not item:
            node = ddi_l_native.parent(node)
        if node is None:
            return None
    return produced


def per_chunk(document: LintTarget, kind: str, read: Any) -> list[Any]:
    """``read(child)`` for each child of ``document``'s root, in order.

    See `per_element`.
    """
    return per_element(document, kind, list(document.root), read)


def per_element(
    document: LintTarget, kind: str, elements: list[Any], read: Any
) -> list[Any]:
    """``read(element)`` for each of ``elements``, in order.

    On the native backend each result is kept under the element's digest,
    so an element unchanged since the last call is not read again. What
    ``read`` returns must depend on the element alone.
    """
    store = getattr(document, "__dict__", None)
    if not NATIVE or store is None:
        return [read(element) for element in elements]
    import ddi_l_native

    if not all(isinstance(element, ddi_l_native.Element) for element in elements):
        return [read(element) for element in elements]
    caches: dict[Any, dict[bytes, Any]] = store.setdefault("_incremental_cache", {})
    known = caches.get(("read", kind), {})
    fresh: dict[bytes, Any] = {}
    results = []
    for element in elements:
        digest = ddi_l_native.digest(element)
        if digest not in fresh:
            fresh[digest] = known[digest] if digest in known else read(element)
        results.append(fresh[digest])
    caches[("read", kind)] = fresh
    return results


def _sorted_out(
    document: LintTarget, rule: _LintRule, items: list[Any]
) -> dict[int, list[LintFinding]] | None:
    """``rule``'s findings on ``document``, by the position of their item.

    ``None`` if they cannot all be filed under an item in item order.
    """
    import ddi_l_native

    position = {id(item): at for at, item in enumerate(items)}
    by_item: dict[int, list[LintFinding]] = {}
    with record_findings() as recorded:
        produced = list(rule.run(document))
    if len(recorded) != len(produced):
        return None
    for (_, element), finding in zip(recorded, produced, strict=True):
        node = element
        while node is not None and id(node) not in position:
            node = ddi_l_native.parent(node)
        if node is None:
            return None
        by_item.setdefault(position[id(node)], []).append(finding)
    if [finding for _, found in sorted(by_item.items()) for finding in found] != (
        produced
    ):
        return None
    return by_item
