"""Compatibility shims for optional ``xmlschema`` dependency."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

xmlschema: Any
XMLSchemaConverter: Any
qname_to_clark_notation: Callable[[str, Mapping[str | None, str] | None], str] | None
XMLSchemaValidationError: type[Exception]

try:  # pragma: no cover - xmlschema is optional
    import xmlschema
    from xmlschema.converters import (
        XMLSchemaConverter as _XMLSchemaConverter,
    )

    try:  # pragma: no cover - symbol removed in xmlschema>=2.3.0
        from xmlschema.helpers import (  # type: ignore[import-not-found]
            qname_to_clark_notation as _qname_to_clark_notation,
        )
    except (ImportError, AttributeError):  # pragma: no cover - fallback path
        _qname_to_clark_notation = None

    from xmlschema.validators.exceptions import (
        XMLSchemaValidationError as _XMLSchemaValidationError,
    )

    XMLSchemaConverter = _XMLSchemaConverter
    qname_to_clark_notation = _qname_to_clark_notation
    XMLSchemaValidationError = _XMLSchemaValidationError
except ModuleNotFoundError:  # pragma: no cover - fallback path
    xmlschema = None
    XMLSchemaConverter = None
    qname_to_clark_notation = None

    class _FallbackXMLSchemaValidationError(ValueError):
        """Fallback validation error raised when xmlschema is unavailable."""

        def __init__(
            self,
            message: str,
            elem: Any = None,
            xpath: str | None = None,
            *,
            line: int | None = None,
            column: int | None = None,
        ) -> None:
            super().__init__(message)
            self.reason = message
            self.message = message
            self.elem = elem
            self.obj = elem
            self.path = xpath

            node_line = getattr(elem, "sourceline", None) if elem is not None else None
            node_column = (
                getattr(elem, "sourcecolumn", None) if elem is not None else None
            )

            self.line = line if line is not None else node_line
            self.column = column if column is not None else node_column
            self.position: tuple[int | None, int | None] | None
            if self.line is not None and self.column is not None:
                self.position = (self.line, self.column)
            elif self.line is not None:
                self.position = (self.line, None)
            else:
                self.position = None

    XMLSchemaValidationError = _FallbackXMLSchemaValidationError


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
