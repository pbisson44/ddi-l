"""Optional HTTP API over the ddi-l operations.

Install with the ``server`` extra::

    pip install 'ddi-l[server]'

Nothing in this subpackage is imported by ``ddi_l/__init__.py``, so a plain
install neither pays for it nor needs Litestar present. Importing it without the
extra raises :class:`ImportError` with the install command.
"""

from __future__ import annotations

from .config import ServerConfig

__all__ = ["ServerConfig", "create_app"]


def create_app(config: ServerConfig | None = None):
    """Build the Litestar application.

    Imported lazily so that ``from ddi_l.server import ServerConfig`` (which
    the CLI does to describe defaults in ``--help``) does not require Litestar.
    """
    from .app import create_app as _create_app

    return _create_app(config)
