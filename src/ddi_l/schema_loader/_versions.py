"""Utilities for resolving and detecting DDI schema versions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .._etree import Element
from .._schema_versions import (
    DEFAULT_SCHEMA_VERSION,
    INSTANCE_NAMESPACE_TO_VERSION,
    SCHEMA_RELEASES,
)
from ..constants import XSI_NS


def normalize_version(version: str | None) -> str:
    """Return a supported schema version, defaulting when ``None``."""
    if version is None:
        return DEFAULT_SCHEMA_VERSION

    if version in SCHEMA_RELEASES:
        return version
    raise ValueError(f"Unsupported DDI schema version: {version!r}")


def _extract_namespace(tag: str) -> str | None:
    if tag.startswith("{") and "}" in tag:
        return tag[1:].split("}", 1)[0]
    return None


def _detect_from_namespace(namespace: str | None) -> str | None:
    if namespace is None:
        return None
    return INSTANCE_NAMESPACE_TO_VERSION.get(namespace)


def _detect_from_schema_location(value: str) -> str | None:
    for version, release in SCHEMA_RELEASES.items():
        if release["schema_filename"] in value:
            return version
        namespace = release["namespaces"]["instance"]
        if namespace in value:
            return version
    return None


def detect_version_from_element(element: Element) -> str | None:
    """Infer the schema version from ``element`` when possible."""
    namespace = _extract_namespace(getattr(element, "tag", ""))
    version = _detect_from_namespace(namespace)
    if version is not None:
        return version

    for attr in (
        f"{{{XSI_NS}}}schemaLocation",
        f"{{{XSI_NS}}}noNamespaceSchemaLocation",
        "schemaLocation",
    ):
        location = element.get(attr)
        if isinstance(location, str):
            version = _detect_from_schema_location(location)
            if version is not None:
                return version

    # Fall back to inspecting explicit xmlns declarations.
    for attr_name, attr_value in element.attrib.items():
        if not isinstance(attr_value, str):
            continue
        if attr_name == "xmlns" or attr_name.endswith(":xmlns"):
            version = _detect_from_namespace(attr_value)
            if version is not None:
                return version
        if attr_name.startswith("xmlns:") and attr_value:
            version = _detect_from_namespace(attr_value)
            if version is not None:
                return version
        if attr_name.startswith("{http://www.w3.org/2000/xmlns/}"):
            version = _detect_from_namespace(attr_value)
            if version is not None:
                return version

    return None


def detect_version_from_mapping(data: Mapping[str, Any]) -> str | None:
    """Infer the schema version from a mapping representation."""
    if not data:
        return None

    if len(data) == 1:
        root_tag, payload = next(iter(data.items()))
        version = _detect_from_namespace(_extract_namespace(root_tag))
        if version is not None:
            return version
        if isinstance(payload, Mapping):
            schema_location_keys = [
                f"@{{{XSI_NS}}}schemaLocation",
                f"@{{{XSI_NS}}}noNamespaceSchemaLocation",
                "@schemaLocation",
            ]
            for key in schema_location_keys:
                location = payload.get(key)
                if isinstance(location, str):
                    version = _detect_from_schema_location(location)
                    if version is not None:
                        return version

            for key, value in payload.items():
                if not isinstance(key, str) or not key.startswith("@"):
                    continue
                if not isinstance(value, str):
                    continue
                if key.startswith("@xmlns") or "xmlns" in key:
                    version = _detect_from_namespace(value)
                    if version is not None:
                        return version

    return None


__all__ = [
    "detect_version_from_element",
    "detect_version_from_mapping",
    "normalize_version",
]
