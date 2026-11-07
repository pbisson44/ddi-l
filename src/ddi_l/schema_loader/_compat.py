"""Compatibility shims for the ``xmlschema`` dependency."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

import xmlschema
from xmlschema.converters import XMLSchemaConverter as _XMLSchemaConverter
from xmlschema.validators.exceptions import (
    XMLSchemaValidationError as _XMLSchemaValidationError,
)

XMLSchemaConverter: Any = _XMLSchemaConverter
XMLSchemaValidationError: type[Exception] = _XMLSchemaValidationError
qname_to_clark_notation: Callable[[str, Mapping[str | None, str] | None], str] | None

try:  # pragma: no cover - symbol removed in xmlschema>=2.3.0
    from xmlschema.helpers import (  # type: ignore[import-not-found]
        qname_to_clark_notation as _qname_to_clark_notation,
    )
except (ImportError, AttributeError):  # pragma: no cover - fallback path
    _qname_to_clark_notation = None
qname_to_clark_notation = _qname_to_clark_notation


def _fallback_qname_converter(
    qname: str, namespaces: Mapping[str | None, str] | None = None
) -> str:
    """Return Clark-notation for prefixed QNames when possible."""
    if qname.startswith("{"):
        return qname

    if namespaces:
        if ":" in qname:
            prefix, local = qname.split(":", 1)
            namespace = namespaces.get(prefix)
            if namespace:
                return f"{{{namespace}}}{local}"
        else:
            for candidate in ("", None):
                namespace = namespaces.get(candidate)
                if namespace:
                    return f"{{{namespace}}}{qname}"

    return qname


def _resolve_qname_converter():
    if qname_to_clark_notation is not None:
        return qname_to_clark_notation
    return _fallback_qname_converter


__all__ = [
    "XMLSchemaConverter",
    "XMLSchemaValidationError",
    "_fallback_qname_converter",
    "_resolve_qname_converter",
    "qname_to_clark_notation",
    "xmlschema",
]
