"""libxml2 schema pre-check used by the ``lxml`` validation backend.

libxml2 validates DDI documents about 35 times faster than xmlschema. It is
used only to confirm that a document is valid: when it reports a problem,
validation falls through to xmlschema, which produces the detailed issues, so
the reported errors are identical on every backend.
"""

from __future__ import annotations

import threading
from importlib import resources
from typing import Any

from ._cache import _schema_resource

_SCHEMAS: dict[str, Any] = {}
_LOCK = threading.Lock()
_UNAVAILABLE = object()


def _compile(version: str) -> Any:
    try:
        from lxml import etree  # type: ignore[import-untyped]
    except ModuleNotFoundError:  # pragma: no cover - depends on the `full` extra
        return _UNAVAILABLE
    resource = _schema_resource(version)
    if not resource.is_file():
        return _UNAVAILABLE
    try:
        with resources.as_file(resource) as path:
            return etree.XMLSchema(etree.parse(str(path)))
    except (etree.XMLSchemaParseError, etree.XMLSyntaxError, OSError):
        return _UNAVAILABLE


def get_libxml2_schema(version: str) -> Any | None:
    """Return the compiled libxml2 schema for ``version``, or ``None``."""
    schema = _SCHEMAS.get(version)
    if schema is None:
        with _LOCK:
            schema = _SCHEMAS.get(version)
            if schema is None:
                schema = _compile(version)
                _SCHEMAS[version] = schema
    return None if schema is _UNAVAILABLE else schema


def is_valid(root: Any, version: str) -> bool:
    """Return ``True`` only when libxml2 confirms ``root`` is schema-valid.

    ``False`` means "not confirmed": the caller must run the full validator.
    """
    if not hasattr(root, "getroottree"):  # stdlib element: libxml2 cannot see it
        return False
    schema = get_libxml2_schema(version)
    if schema is None:
        return False
    try:
        return bool(schema.validate(root))
    except Exception:  # pragma: no cover - defer to the full validator
        return False


def clear() -> None:
    """Drop the compiled schemas."""
    with _LOCK:
        _SCHEMAS.clear()


def available() -> bool:
    """Return whether lxml is installed."""
    try:
        import lxml.etree  # type: ignore[import-untyped]  # noqa: F401
    except ModuleNotFoundError:  # pragma: no cover - depends on the `full` extra
        return False
    return True


__all__ = ["available", "clear", "get_libxml2_schema", "is_valid"]
