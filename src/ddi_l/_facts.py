"""What the checks of one run know about a document, built once.

Lint rules, conformance and condition explanation each walk a document for
the same things: its identifiable items, the latest version of each, its
bindings, its parsed conditions. Inside `run_scope`, each of those is built
once per document and shared by every check of the run; outside one, each
call builds its own, as before. A run must not change the document it reads.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, TypeVar

_T = TypeVar("_T")

# What the run under way has built, by kind and key; each thread and task has
# its own. The key's first object is held too, so an id() cannot be reused.
_BUILT: ContextVar[dict[tuple[str, Hashable], tuple[Any, Any]] | None] = ContextVar(
    "ddi_l_facts", default=None
)


# The items a rule run is limited to, for incremental lint; None for all.
_ONLY: ContextVar[tuple[Any, ...] | None] = ContextVar("ddi_l_only_items", default=None)


def only_items() -> tuple[Any, ...] | None:
    """The items the rule under way is limited to, or ``None`` for all."""
    return _ONLY.get()


@contextmanager
def limited_to(items: tuple[Any, ...]) -> Iterator[None]:
    """Limit the rules run inside the ``with`` block to ``items``."""
    token = _ONLY.set(items)
    try:
        yield
    finally:
        _ONLY.reset(token)


# Where `record_findings` collects (finding, element) pairs; None when off.
_RECORD: ContextVar[list[tuple[Any, Any]] | None] = ContextVar(
    "ddi_l_recorded_findings", default=None
)


def recorder() -> list[tuple[Any, Any]] | None:
    """The list a rule's findings and their elements go to, if any."""
    return _RECORD.get()


@contextmanager
def record_findings() -> Iterator[list[tuple[Any, Any]]]:
    """Collect each finding made inside the block with the element it is about."""
    found: list[tuple[Any, Any]] = []
    token = _RECORD.set(found)
    try:
        yield found
    finally:
        _RECORD.reset(token)


@contextmanager
def run_scope() -> Iterator[None]:
    """Share what the checks inside the ``with`` block build. Re-entrant."""
    if _BUILT.get() is not None:
        yield
        return
    token = _BUILT.set({})
    try:
        yield
    finally:
        _BUILT.reset(token)


def shared(kind: str, owner: object, build: Callable[[], _T]) -> _T:
    """``build()``, made once per ``kind`` and ``owner`` inside a run scope.

    ``owner`` is the object the result describes, usually a document root;
    it is compared by identity.
    """
    return _built(kind, id(owner), owner, build)


def shared_by_value(kind: str, key: Hashable, build: Callable[[], _T]) -> _T:
    """``build()``, made once per ``kind`` and equal ``key`` inside a run scope."""
    return _built(kind, key, None, build)


def _built(kind: str, key: Hashable, owner: object, build: Callable[[], _T]) -> _T:
    """The cached ``build()``; an ``owner`` must be the very object cached."""
    cache = _BUILT.get()
    if cache is None:
        return build()
    entry = cache.get((kind, key))
    if entry is not None and entry[0] is owner:
        return entry[1]
    value = build()
    cache[(kind, key)] = (owner, value)
    return value
