"""Schema resource helpers and caching utilities."""

from __future__ import annotations

import threading
from importlib import resources
from importlib.resources.abc import Traversable
from types import SimpleNamespace

import xmlschema

from ._constants import _SCHEMA_PACKAGE, SCHEMA_VERSION, get_schema_release

_SCHEMA_CACHE: dict[str, object] = {}
# Loading a schema takes seconds; the lock stops concurrent first requests
# from each loading the same version.
_SCHEMA_LOCK = threading.Lock()


def _schema_resource(version: str) -> Traversable:
    """Return the packaged schema resource for ``version``."""
    release = get_schema_release(version)
    resource = resources.files(_SCHEMA_PACKAGE)
    for part in release["schema_resource"]:
        resource = resource / part
    return resource


def _load_schema(version: str) -> object:
    resource = _schema_resource(version)
    if not resource.is_file():
        raise FileNotFoundError(
            f"The DDI {version} schema is missing from the ddi-l install "
            f"({resource}). Reinstall ddi-l."
        )
    with resources.as_file(resource) as schema_path:
        return xmlschema.XMLSchema(schema_path)


def get_schema(version: str | None = None):
    """Return a cached schema instance for ``version``."""
    target_version = version or SCHEMA_VERSION
    schema = _SCHEMA_CACHE.get(target_version)
    if schema is not None:
        return schema
    with _SCHEMA_LOCK:
        schema = _SCHEMA_CACHE.get(target_version)
        if schema is None:
            schema = _load_schema(target_version)
            _SCHEMA_CACHE[target_version] = schema
        return schema


def clear_schema_cache(version: str | None = None) -> None:
    """Clear the cached schema for ``version`` or all versions when ``None``."""
    from . import _libxml2

    _libxml2.clear()
    with _SCHEMA_LOCK:
        if version is None:
            _SCHEMA_CACHE.clear()
            return
        _SCHEMA_CACHE.pop(version, None)


def _cache_info() -> SimpleNamespace:
    return SimpleNamespace(currsize=len(_SCHEMA_CACHE), maxsize=None)


get_schema.cache_clear = clear_schema_cache  # type: ignore[attr-defined]
get_schema.cache_info = _cache_info  # type: ignore[attr-defined]


__all__ = ["clear_schema_cache", "get_schema"]
