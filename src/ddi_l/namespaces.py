"""Helpers for working with reusable namespace bindings and profiles."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from types import MappingProxyType

from .constants import (
    ARCHIVE_NS,
    COMPARATIVE_NS,
    CONCEPTUAL_COMPONENT_NS,
    DATA_COLLECTION_NS,
    DDI_PROFILE_NS,
    DEFAULT_NSMAP,
    GROUP_NS,
    LOGICAL_PRODUCT_NS,
    METHODOLOGY_NS,
    PHYSICAL_DATA_PRODUCT_NS,
    PHYSICAL_INSTANCE_NS,
    PROCESS_NS,
    REUSABLE_NS,
    STUDY_UNIT_NS,
    XSI_NS,
)

NamespaceBindings = dict[str | None, str]
NamespaceProfile = Mapping[str | None, str]
NamespaceProfileLike = str | NamespaceProfile

DDI_DEFAULT_PROFILE = "ddi-default"
DDI_REUSABLE_PROFILE = "ddi-reusable"
DDI_STUDY_UNIT_PROFILE = "ddi-study-unit"
DDI_DATA_COLLECTION_PROFILE = "ddi-data-collection"
DDI_LOGICAL_PRODUCT_PROFILE = "ddi-logical-product"
DDI_PHYSICAL_DATA_PROFILE = "ddi-physical-data"
DDI_ARCHIVE_PROFILE = "ddi-archive"
DDI_CONCEPTUAL_COMPONENT_PROFILE = "ddi-conceptual-component"
DDI_COMPARATIVE_PROFILE = "ddi-comparative"
DDI_PROFILE_PROFILE = "ddi-profile"

_DDI_PROFILE_NAMESPACE = DDI_PROFILE_NS

# ``pr`` is bound to the ddiprofile namespace to match the canonical DDI 3.3
# instance schema (``instance_3_3.xsd`` declares ``xmlns:pr="ddi:ddiprofile:3_3"``).
# The process module — which is not part of the instance schema set — uses the
# distinct ``prc`` prefix so the two never collide.
NAMESPACE_PREFIXES: Mapping[str, str] = MappingProxyType(
    {
        "a": ARCHIVE_NS,
        "c": CONCEPTUAL_COMPONENT_NS,
        "cmp": COMPARATIVE_NS,
        "d": DATA_COLLECTION_NS,
        "g": GROUP_NS,
        "l": LOGICAL_PRODUCT_NS,
        "m": METHODOLOGY_NS,
        "p": PHYSICAL_DATA_PRODUCT_NS,
        "pi": PHYSICAL_INSTANCE_NS,
        "pr": DDI_PROFILE_NS,
        "prc": PROCESS_NS,
        "r": REUSABLE_NS,
        "s": STUDY_UNIT_NS,
        "xsi": XSI_NS,
    }
)

_DEFAULT_PROFILE_BINDINGS: Mapping[str | None, str] = DEFAULT_NSMAP

NAMESPACE_PROFILES: dict[str, NamespaceProfile] = {
    DDI_DEFAULT_PROFILE: _DEFAULT_PROFILE_BINDINGS,
    DDI_REUSABLE_PROFILE: {"r": REUSABLE_NS},
    DDI_STUDY_UNIT_PROFILE: {"s": STUDY_UNIT_NS, "c": CONCEPTUAL_COMPONENT_NS},
    DDI_DATA_COLLECTION_PROFILE: {"d": DATA_COLLECTION_NS},
    DDI_LOGICAL_PRODUCT_PROFILE: {"l": LOGICAL_PRODUCT_NS},
    DDI_PHYSICAL_DATA_PROFILE: {"p": PHYSICAL_DATA_PRODUCT_NS},
    DDI_ARCHIVE_PROFILE: {"a": ARCHIVE_NS},
    DDI_CONCEPTUAL_COMPONENT_PROFILE: {"cc": CONCEPTUAL_COMPONENT_NS},
    DDI_COMPARATIVE_PROFILE: {"cmp": COMPARATIVE_NS},
    DDI_PROFILE_PROFILE: {"pr": _DDI_PROFILE_NAMESPACE},
}


def get_namespace_profile(name: str) -> NamespaceBindings:
    """Return a copy of the bindings stored under ``name``.

    Args:
        name: The profile identifier to look up.

    Raises:
        KeyError: If the requested profile has not been registered.
    """
    try:
        profile = NAMESPACE_PROFILES[name]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise KeyError(f"Unknown namespace profile: {name}") from exc
    return dict(profile)


def merge_namespace_profiles(
    *profiles: NamespaceProfileLike,
    overrides: NamespaceProfile | None = None,
    allow_override: bool = False,
) -> NamespaceBindings:
    """Merge named and ad-hoc namespace bindings into a single dictionary.

    Args:
        profiles: Sequence of named profiles or explicit prefix-to-URI
            mappings. Later profiles are processed after earlier ones.
        overrides: Optional explicit mapping that is always applied last.
        allow_override: When ``False`` (the default) conflicting bindings raise
            a :class:`ValueError`. When ``True`` later values replace earlier
            bindings.
    """
    merged: NamespaceBindings = {}
    for profile in profiles:
        mapping = _coerce_profile(profile)
        _merge_bindings(merged, mapping, allow_override=allow_override)
    if overrides is not None:
        _merge_bindings(merged, overrides, allow_override=True)
    return merged


def canonicalize_prefixes(
    bindings: Mapping[str | None, str],
) -> dict[str | None, str]:
    """Re-key namespace bindings onto their canonical DDI prefixes.

    Another tool may bind the studyunit namespace to ``p4`` rather than ``s``.
    Bindings whose URI has a registered prefix in :data:`NAMESPACE_PREFIXES`
    are moved onto it, so output is canonical and identical on both XML
    backends. The default (``None``) binding and unknown namespaces are
    preserved as given.

    Args:
        bindings: Prefix-to-URI mapping read from a source document.

    Returns:
        A new mapping with canonical prefixes substituted where known.
    """
    canonical_for_uri = {uri: prefix for prefix, uri in NAMESPACE_PREFIXES.items()}
    result: dict[str | None, str] = {}
    for prefix, uri in bindings.items():
        if prefix in (None, "") or not uri:
            result[prefix] = uri
            continue
        result[canonical_for_uri.get(uri, prefix)] = uri
    return result


def build_namespace_map(
    *prefixes: str,
    default_namespace: str | None = None,
    extra: Mapping[str | None, str] | None = None,
) -> NamespaceBindings:
    """Construct a namespace mapping using :data:`NAMESPACE_PREFIXES`.

    Args:
        *prefixes: Namespace prefixes to include in the resulting mapping.
            Each prefix must be registered in :data:`NAMESPACE_PREFIXES`.
        default_namespace: Optional namespace URI bound to the default
            (``None``) prefix.
        extra: Optional explicit bindings merged into the result after the
            registered prefixes have been processed.

    Returns:
        NamespaceBindings: A mutable dictionary suitable for assigning to
            ``NSMAP`` class attributes.
    """
    mapping: NamespaceBindings = {}
    if default_namespace is not None:
        mapping[None] = default_namespace
    for prefix in prefixes:
        try:
            mapping[prefix] = NAMESPACE_PREFIXES[prefix]
        except KeyError as exc:  # pragma: no cover - defensive branch
            raise KeyError(f"Unknown namespace prefix: {prefix!r}") from exc
    if extra is not None:
        mapping.update(extra)
    return mapping


def _coerce_profile(profile: NamespaceProfileLike) -> NamespaceProfile:
    """Normalise a namespace profile reference to a mapping.

    Args:
        profile: A profile identifier or an explicit prefix-to-URI mapping.

    Returns:
        A mapping of namespace prefixes to their associated URIs.

    Raises:
        KeyError: If ``profile`` is a string that does not match a registered
            namespace profile name.
    """
    if isinstance(profile, str):
        return get_namespace_profile(profile)
    return profile


def _merge_bindings(
    target: MutableMapping[str | None, str],
    source: NamespaceProfile,
    *,
    allow_override: bool,
) -> None:
    """Update ``target`` with bindings from ``source``.

    Args:
        target: The mapping being mutated.
        source: Namespace bindings to merge into ``target``.
        allow_override: When ``True`` existing prefixes in ``target`` are
            replaced by the bindings from ``source``. When ``False`` the
            function enforces that any pre-existing prefix is associated with
            the same URI and otherwise raises an error.

    Raises:
        ValueError: If ``allow_override`` is ``False`` and ``source`` contains
            a prefix already bound to a different URI in ``target``.
    """
    for prefix, uri in source.items():
        if not allow_override and prefix in target and target[prefix] != uri:
            raise ValueError(
                f"Namespace prefix {prefix!r} is already bound"
                f" to {target[prefix]!r} and cannot be"
                f" rebound to {uri!r}."
            )
        target[prefix] = uri


__all__ = [
    "DDI_ARCHIVE_PROFILE",
    "DDI_COMPARATIVE_PROFILE",
    "DDI_CONCEPTUAL_COMPONENT_PROFILE",
    "DDI_DATA_COLLECTION_PROFILE",
    "DDI_DEFAULT_PROFILE",
    "DDI_LOGICAL_PRODUCT_PROFILE",
    "DDI_PHYSICAL_DATA_PROFILE",
    "DDI_PROFILE_PROFILE",
    "DDI_REUSABLE_PROFILE",
    "DDI_STUDY_UNIT_PROFILE",
    "NAMESPACE_PREFIXES",
    "NAMESPACE_PROFILES",
    "NamespaceBindings",
    "NamespaceProfile",
    "NamespaceProfileLike",
    "build_namespace_map",
    "canonicalize_prefixes",
    "get_namespace_profile",
    "merge_namespace_profiles",
]
