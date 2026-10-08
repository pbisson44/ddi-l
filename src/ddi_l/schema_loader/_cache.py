"""Schema resource helpers and caching utilities."""

from __future__ import annotations

import threading
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from types import SimpleNamespace

from ._constants import _SCHEMA_PACKAGE, SCHEMA_VERSION, get_schema_release
from ._fallback import _FallbackSchema

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
    release = get_schema_release(version)
    expected_filename = release["schema_filename"]
    if not resource.is_file():
        return _FallbackSchema(Path(expected_filename), version=version)

    with resources.as_file(resource) as schema_path:
        actual_filename = schema_path.name
        if actual_filename != expected_filename:
            return _FallbackSchema(Path(schema_path), version=version)
        from . import xmlschema as xmlschema_module

        if xmlschema_module is not None:  # pragma: no branch - dependency controlled
            try:
                return xmlschema_module.XMLSchema(schema_path)
            except OSError:
                pass

        return _FallbackSchema(Path(schema_path), version=version)


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
