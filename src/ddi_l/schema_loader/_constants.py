"""Shared constants and type definitions for schema loading helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import IO

from .._etree import Element
from .._schema_versions import (
    DEFAULT_SCHEMA_VERSION,
    INSTANCE_NAMESPACE_TO_VERSION,
    SCHEMA_RELEASES,
    SUPPORTED_SCHEMA_VERSIONS,
    get_schema_release,
)

XMLNS_NAMESPACE = "http://www.w3.org/2000/xmlns/"
_SCHEMA_PACKAGE = "ddi_l.schemas"


def _schema_resource_for_version(version: str | None = None) -> tuple[str, ...]:
    release = get_schema_release(version)
    return release["schema_resource"]


def _namespaces_for_version(version: str | None = None) -> Mapping[str, str]:
    release = get_schema_release(version)
    return release["namespaces"]


def get_instance_namespace(version: str | None = None) -> str:
    return _namespaces_for_version(version)["instance"]


def get_reusable_namespace(version: str | None = None) -> str:
    return _namespaces_for_version(version)["reusable"]


def get_namespaces(version: str | None = None) -> Mapping[str, str]:
    return _namespaces_for_version(version)


SCHEMA_VERSION = DEFAULT_SCHEMA_VERSION
INSTANCE_NAMESPACE = get_instance_namespace()
REUSABLE_NAMESPACE = get_reusable_namespace()
_SCHEMA_RESOURCE = _schema_resource_for_version()

SchemaInput = str | Path | Element | bytes | IO[bytes] | IO[str]

__all__ = [
    "INSTANCE_NAMESPACE",
    "INSTANCE_NAMESPACE_TO_VERSION",
    "REUSABLE_NAMESPACE",
    "SCHEMA_RELEASES",
    "SCHEMA_VERSION",
    "SUPPORTED_SCHEMA_VERSIONS",
    "XMLNS_NAMESPACE",
    "_SCHEMA_PACKAGE",
    "_SCHEMA_RESOURCE",
    "SchemaInput",
    "get_instance_namespace",
    "get_namespaces",
    "get_reusable_namespace",
    "get_schema_release",
]
