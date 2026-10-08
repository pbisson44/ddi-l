"""Shared schema release metadata for version-aware helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from types import MappingProxyType
from typing import TypedDict

# Recorded release archive checksums are used to validate downloads performed by
# :func:`ddi_l.schema_sync.update_schema_package`. Maintainers should refresh
# these values whenever a schema bundle is updated.
SCHEMA_ARCHIVE_CHECKSUMS: Mapping[str, str] = MappingProxyType(
    {
        # Populate with the SHA-256 digest of the official release archive.
        "3.1": "30f49976d2c16477733b3150aae8932ad9a6bee335408274662c0db2afd86732",
        "3.2": "1042769ddbdf7023e03347443ca203d13bf5ad33771ed9286f02ba210a4b0fc4",
        "3.3": "42712412d8309a08c6292c4bb7d178f3176b58070249866da2e2637a3fce8771",
    }
)


class SchemaRelease(TypedDict, total=False):
    """Structured details describing a bundled schema release."""

    version: str
    suffix: str
    schema_resource: tuple[str, ...]
    schema_filename: str
    namespaces: Mapping[str, str]
    archive_checksum: str


DEFAULT_SCHEMA_VERSION = "3.3"
SUPPORTED_SCHEMA_VERSIONS: tuple[str, ...] = ("3.1", "3.2", "3.3")

# The 17 namespaces the DDI 3.3 XSDs declare as a targetNamespace (checked
# against the bundled schemas by tests/test_schema_versions.py).
_SCHEMA_NAMESPACE_TEMPLATES: Mapping[str, str] = MappingProxyType(
    {
        "instance": "ddi:instance:{suffix}",
        "reusable": "ddi:reusable:{suffix}",
        "studyunit": "ddi:studyunit:{suffix}",
        "datacollection": "ddi:datacollection:{suffix}",
        "logicalproduct": "ddi:logicalproduct:{suffix}",
        "physicaldataproduct": "ddi:physicaldataproduct:{suffix}",
        "physicaldataproduct_ncube_inline": (
            "ddi:physicaldataproduct_ncube_inline:{suffix}"
        ),
        "physicaldataproduct_ncube_normal": (
            "ddi:physicaldataproduct_ncube_normal:{suffix}"
        ),
        "physicaldataproduct_ncube_tabular": (
            "ddi:physicaldataproduct_ncube_tabular:{suffix}"
        ),
        "physicaldataproduct_proprietary": (
            "ddi:physicaldataproduct_proprietary:{suffix}"
        ),
        "physicalinstance": "ddi:physicalinstance:{suffix}",
        "archive": "ddi:archive:{suffix}",
        "group": "ddi:group:{suffix}",
        "conceptualcomponent": "ddi:conceptualcomponent:{suffix}",
        "comparative": "ddi:comparative:{suffix}",
        "ddiprofile": "ddi:ddiprofile:{suffix}",
        "dataset": "ddi:dataset:{suffix}",
    }
)

# Synthetic namespaces for model types that no DDI Lifecycle schema defines
# (Process*, MethodologyItem/MethodologyScheme, ReviewEvent). They are spelled
# ``urn:ddi-l:extension:...`` so nobody mistakes them for DDI Alliance
# namespaces, and carry no DDI version. See docs/DEVELOPMENT.en.md.
_SYNTHETIC_NAMESPACE_TEMPLATES: Mapping[str, str] = MappingProxyType(
    {
        "process": "urn:ddi-l:extension:process:1",
        "methodology": "urn:ddi-l:extension:methodology:1",
    }
)

_NAMESPACE_TEMPLATES: Mapping[str, str] = MappingProxyType(
    {**_SCHEMA_NAMESPACE_TEMPLATES, **_SYNTHETIC_NAMESPACE_TEMPLATES}
)


def _build_release(version: str) -> SchemaRelease:
    suffix = version.replace(".", "_")
    namespaces: MutableMapping[str, str] = {}
    for key, template in _NAMESPACE_TEMPLATES.items():
        namespaces[key] = template.format(suffix=suffix)

    schema_filename = f"instance_{suffix}.xsd"
    return SchemaRelease(
        version=version,
        suffix=suffix,
        schema_resource=("ddi", f"v{suffix}", schema_filename),
        schema_filename=schema_filename,
        namespaces=MappingProxyType(dict(namespaces)),
        archive_checksum=SCHEMA_ARCHIVE_CHECKSUMS.get(version, ""),
    )


SCHEMA_RELEASES: Mapping[str, SchemaRelease] = MappingProxyType(
    {version: _build_release(version) for version in SUPPORTED_SCHEMA_VERSIONS}
)


def get_schema_release(version: str | None = None) -> SchemaRelease:
    """Return the schema release metadata for ``version``.

    Args:
        version: Semantic version string for the desired DDI release. When
            ``None`` the bundled default version is returned.

    Raises:
        KeyError: If ``version`` is not part of :data:`SUPPORTED_SCHEMA_VERSIONS`.
    """
    target_version = version or DEFAULT_SCHEMA_VERSION
    try:
        return SCHEMA_RELEASES[target_version]
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise KeyError(f"Unsupported DDI schema version: {target_version!r}") from exc


def iter_schema_versions() -> Iterable[str]:
    """Return the supported schema versions in ascending order."""
    return SUPPORTED_SCHEMA_VERSIONS


INSTANCE_NAMESPACE_TO_VERSION: Mapping[str, str] = MappingProxyType(
    {
        release["namespaces"]["instance"]: version
        for version, release in SCHEMA_RELEASES.items()
    }
)


__all__ = [
    "DEFAULT_SCHEMA_VERSION",
    "INSTANCE_NAMESPACE_TO_VERSION",
    "SCHEMA_ARCHIVE_CHECKSUMS",
    "SCHEMA_RELEASES",
    "SUPPORTED_SCHEMA_VERSIONS",
    "SchemaRelease",
    "get_schema_release",
    "iter_schema_versions",
]
