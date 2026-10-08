"""Public API for schema loading, conversion, and validation helpers."""

from __future__ import annotations

from .._etree import Element, create_element
from .._etree import fromstring as _etree_fromstring
from ._cache import clear_schema_cache, get_schema
from ._compat import (
    XMLSchemaConverter,
    XMLSchemaValidationError,
    qname_to_clark_notation,
    xmlschema,
)
from ._constants import (
    INSTANCE_NAMESPACE,
    REUSABLE_NAMESPACE,
    SCHEMA_VERSION,
    XMLNS_NAMESPACE,
    SchemaInput,
)
from ._conversion_runtime import (
    IMPLEMENTATION as CONVERSION_IMPLEMENTATION,
)
from ._conversion_runtime import (  # type: ignore[attr-defined]
    from_dict,
    get_available_conversion_backends,
    set_conversion_backend,
    to_dict,
)
from ._fallback import _FallbackSchema  # noqa: F401  # re-exported for consumers/tests
from ._validation import (
    IMPLEMENTATION as VALIDATION_IMPLEMENTATION,
)
from ._validation import (
    SchemaValidationError,
    SchemaValidationIssue,
    _clear_known_type_name_cache,
    get_available_validation_backends,
    set_validation_backend,
    validate,
)


def clear_known_type_name_cache() -> None:
    """Reset the cached maintainable type names used during validation."""
    _clear_known_type_name_cache()


def _invalidate_cache_on_register(_cls: type) -> None:
    """Callback to clear the known type name cache when new types are registered."""
    _clear_known_type_name_cache()


try:
    from ..registry import MaintainableRegistry as _Registry

    _Registry.on_register(_invalidate_cache_on_register)
except Exception:
    pass  # Registry may not be available during early initialization


fromstring = _etree_fromstring

__all__ = [
    "CONVERSION_IMPLEMENTATION",
    "INSTANCE_NAMESPACE",
    "REUSABLE_NAMESPACE",
    "SCHEMA_VERSION",
    "VALIDATION_IMPLEMENTATION",
    "XMLNS_NAMESPACE",
    "Element",
    "SchemaInput",
    "SchemaValidationError",
    "SchemaValidationIssue",
    "XMLSchemaConverter",
    "XMLSchemaValidationError",
    "clear_known_type_name_cache",
    "clear_schema_cache",
    "create_element",
    "from_dict",
    "fromstring",
    "get_available_conversion_backends",
    "get_available_validation_backends",
    "get_schema",
    "qname_to_clark_notation",
    "set_conversion_backend",
    "set_validation_backend",
    "to_dict",
    "validate",
    "xmlschema",
]
