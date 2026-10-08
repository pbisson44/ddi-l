"""Namespace constants shared across the DDI helpers and models."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from types import MappingProxyType
from typing import Literal, TypeAlias, TypedDict, cast
from uuid import UUID

from ._schema_versions import (
    DEFAULT_SCHEMA_VERSION,
    SCHEMA_RELEASES,
    SUPPORTED_SCHEMA_VERSIONS,
    get_schema_release,
)

XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
XML_NS = "http://www.w3.org/XML/1998/namespace"


class NamespaceSet(TypedDict):
    INSTANCE_NS: str
    REUSABLE_NS: str
    STUDY_UNIT_NS: str
    DATA_COLLECTION_NS: str
    LOGICAL_PRODUCT_NS: str
    PHYSICAL_DATA_PRODUCT_NS: str
    PHYSICAL_INSTANCE_NS: str
    ARCHIVE_NS: str
    GROUP_NS: str
    CONCEPTUAL_COMPONENT_NS: str
    COMPARATIVE_NS: str
    PROCESS_NS: str
    METHODOLOGY_NS: str
    DDI_PROFILE_NS: str
    DATASET_NS: str
    DEFAULT_NSMAP: Mapping[str | None, str]


NamespaceSetValue: TypeAlias = str | Mapping[str | None, str]
NamespaceKey = Literal[
    "INSTANCE_NS",
    "REUSABLE_NS",
    "STUDY_UNIT_NS",
    "DATA_COLLECTION_NS",
    "LOGICAL_PRODUCT_NS",
    "PHYSICAL_DATA_PRODUCT_NS",
    "PHYSICAL_INSTANCE_NS",
    "ARCHIVE_NS",
    "GROUP_NS",
    "CONCEPTUAL_COMPONENT_NS",
    "COMPARATIVE_NS",
    "PROCESS_NS",
    "METHODOLOGY_NS",
    "DDI_PROFILE_NS",
    "DATASET_NS",
    "DEFAULT_NSMAP",
]


def _build_namespace_constants(
    version: str,
) -> Mapping[NamespaceKey, NamespaceSetValue]:
    release = get_schema_release(version)
    namespaces = release["namespaces"]

    mapping: MutableMapping[NamespaceKey, NamespaceSetValue] = {
        "INSTANCE_NS": namespaces["instance"],
        "REUSABLE_NS": namespaces["reusable"],
        "STUDY_UNIT_NS": namespaces["studyunit"],
        "DATA_COLLECTION_NS": namespaces["datacollection"],
        "LOGICAL_PRODUCT_NS": namespaces["logicalproduct"],
        "PHYSICAL_DATA_PRODUCT_NS": namespaces["physicaldataproduct"],
        "PHYSICAL_INSTANCE_NS": namespaces["physicalinstance"],
        "ARCHIVE_NS": namespaces["archive"],
        "GROUP_NS": namespaces["group"],
        "CONCEPTUAL_COMPONENT_NS": namespaces["conceptualcomponent"],
        "COMPARATIVE_NS": namespaces["comparative"],
        "PROCESS_NS": namespaces["process"],
        "METHODOLOGY_NS": namespaces["methodology"],
        "DDI_PROFILE_NS": namespaces["ddiprofile"],
        "DATASET_NS": namespaces["dataset"],
    }

    mapping["DEFAULT_NSMAP"] = MappingProxyType(
        {None: namespaces["instance"], "r": namespaces["reusable"], "xsi": XSI_NS}
    )

    return MappingProxyType(dict(mapping))


NAMESPACE_SETS: Mapping[str, NamespaceSet] = MappingProxyType(
    {
        version: _build_namespace_constants(version)  # type: ignore[misc]
        for version in SUPPORTED_SCHEMA_VERSIONS
    }
)


def get_namespace_set(version: str | None = None) -> NamespaceSet:
    """Return the namespace constants for ``version``."""
    target = version or DEFAULT_SCHEMA_VERSION
    try:
        return NAMESPACE_SETS[target]
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise KeyError(f"Unsupported DDI schema version: {target!r}") from exc


def _namespace_value(
    name: NamespaceKey, version: str | None = None
) -> NamespaceSetValue:
    return get_namespace_set(version)[name]


def get_default_nsmap(version: str | None = None) -> Mapping[str | None, str]:
    """Return the default namespace map for ``version``."""
    return cast(Mapping[str | None, str], _namespace_value("DEFAULT_NSMAP", version))


def _export(name: str) -> NamespaceSetValue:
    return _namespace_value(name)  # type: ignore[arg-type]


INSTANCE_NS: str = cast(str, _export("INSTANCE_NS"))
REUSABLE_NS: str = cast(str, _export("REUSABLE_NS"))
STUDY_UNIT_NS: str = cast(str, _export("STUDY_UNIT_NS"))
DATA_COLLECTION_NS: str = cast(str, _export("DATA_COLLECTION_NS"))
LOGICAL_PRODUCT_NS: str = cast(str, _export("LOGICAL_PRODUCT_NS"))
PHYSICAL_DATA_PRODUCT_NS: str = cast(str, _export("PHYSICAL_DATA_PRODUCT_NS"))
PHYSICAL_INSTANCE_NS: str = cast(str, _export("PHYSICAL_INSTANCE_NS"))
ARCHIVE_NS: str = cast(str, _export("ARCHIVE_NS"))
GROUP_NS: str = cast(str, _export("GROUP_NS"))
CONCEPTUAL_COMPONENT_NS: str = cast(str, _export("CONCEPTUAL_COMPONENT_NS"))
COMPARATIVE_NS: str = cast(str, _export("COMPARATIVE_NS"))
PROCESS_NS: str = cast(str, _export("PROCESS_NS"))
METHODOLOGY_NS: str = cast(str, _export("METHODOLOGY_NS"))
DDI_PROFILE_NS: str = cast(str, _export("DDI_PROFILE_NS"))
DATASET_NS: str = cast(str, _export("DATASET_NS"))

# Namespace used to deterministically derive UUID identifiers from agency/id seeds.
IDENTIFIER_NAMESPACE: UUID = UUID("da543305-75a4-559f-b750-0ef55cc8ef52")
DEFAULT_NSMAP: Mapping[str | None, str] = cast(
    Mapping[str | None, str], _export("DEFAULT_NSMAP")
)

__all__ = [
    "ARCHIVE_NS",
    "COMPARATIVE_NS",
    "CONCEPTUAL_COMPONENT_NS",
    "DATASET_NS",
    "DATA_COLLECTION_NS",
    "DDI_PROFILE_NS",
    "DEFAULT_NSMAP",
    "GROUP_NS",
    "INSTANCE_NS",
    "LOGICAL_PRODUCT_NS",
    "METHODOLOGY_NS",
    "NAMESPACE_SETS",
    "PHYSICAL_DATA_PRODUCT_NS",
    "PHYSICAL_INSTANCE_NS",
    "PROCESS_NS",
    "REUSABLE_NS",
    "SCHEMA_RELEASES",
    "STUDY_UNIT_NS",
    "SUPPORTED_SCHEMA_VERSIONS",
    "XML_NS",
    "XSI_NS",
    "get_default_nsmap",
    "get_namespace_set",
]
