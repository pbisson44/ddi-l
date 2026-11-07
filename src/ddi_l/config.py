"""Library-wide defaults that callers can set once instead of on every call.

Every setting here is a *default* for a keyword the library's functions also
accept directly, and the keyword always wins. Prefer the keyword in library
code; use `configure` for an application-wide policy, and `configured` to
scope a change to a block. A `configured` block changes the defaults for its
own thread or task only::

    import ddi_l as ddi

    ddi.configure(version_responsibility="Questionnaire design team")
    item.increment_major_version()  # records that responsibility

    with ddi.configured(version_responsibility=None):
        item.increment_major_version()  # records none
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, replace
from typing import Any

__all__ = [
    "Configuration",
    "configure",
    "configured",
    "get_configuration",
    "reset_configuration",
]


@dataclass(frozen=True)
class Configuration:
    """The library-wide defaults.

    Attributes:
        version_responsibility: Recorded as ``r:VersionResponsibility`` when a
            version is incremented without an explicit ``responsibility=``,
            and on new items built for Colectica. ``None`` (default) records
            nothing; the library never invents one.
    """

    version_responsibility: str | None = None


_BUILT_IN = Configuration()
_lock = threading.Lock()
# The application default, which only `configure` changes. A `configured`
# block overrides it for its own thread or task only.
_default = _BUILT_IN
_scoped: ContextVar[Configuration | None] = ContextVar(
    "ddi_l_configuration", default=None
)
_UNSET: Any = object()


def get_configuration() -> Configuration:
    """Return the active `Configuration`.

    That is the one a `configured` block in this thread or task set, else
    the application default.
    """
    return _scoped.get() or _default


def _set_default(configuration: Configuration) -> Configuration:
    """Make ``configuration`` the application default; hold ``_lock``."""
    global _default
    _default = configuration
    return configuration


def _updated(version_responsibility: str | None) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    if version_responsibility is not _UNSET:
        updates["version_responsibility"] = version_responsibility
    return updates


def configure(*, version_responsibility: str | None = _UNSET) -> Configuration:
    """Change the application defaults; only the options passed are changed.

    The change reaches every thread and task, except inside a `configured`
    block, which keeps its own.

    Args:
        version_responsibility: The default ``r:VersionResponsibility`` for
            version increments, or ``None`` to record none.

    Returns:
        The new application default.
    """
    updates = _updated(version_responsibility)
    if not updates:
        return _default
    with _lock:
        return _set_default(replace(_default, **updates))


def reset_configuration() -> Configuration:
    """Restore the built-in defaults and return them."""
    with _lock:
        return _set_default(_BUILT_IN)


@contextmanager
def configured(
    *, version_responsibility: str | None = _UNSET
) -> Iterator[Configuration]:
    """Change the defaults for the ``with`` block, in this thread or task only.

    Other threads and tasks keep seeing the application default. The previous
    configuration is restored on exit, even if the block raises.

    Yields:
        The configuration in force inside the block.
    """
    inside = replace(get_configuration(), **_updated(version_responsibility))
    token = _scoped.set(inside)
    try:
        yield inside
    finally:
        _scoped.reset(token)
