"""Shared helpers for normalising namespace declarations on XML elements."""

from __future__ import annotations

import re
from collections.abc import Mapping, MutableMapping
from typing import Protocol, cast

from ._etree import USING_LXML, XMLNS, Element, cleanup_namespaces, create_element
from .constants import DEFAULT_NSMAP
from .namespaces import (
    NamespaceBindings,
    NamespaceProfileLike,
    merge_namespace_profiles,
)

_DEFAULT_NS_MAP: Mapping[str | None, str] = DEFAULT_NSMAP


class SupportsNsMap(Protocol):
    """Structural type for XML elements exposing ``nsmap`` metadata."""

    nsmap: Mapping[str | None, str] | None


def build_namespace_map(
    profile_or_map: NamespaceProfileLike | Mapping[str | None, str] | None = None,
    *,
    extra_namespaces: Mapping[str | None, str] | None = None,
    base: Mapping[str | None, str] | None = None,
) -> NamespaceBindings:
    """Merge namespace declarations into a single mapping.

    Args:
        profile_or_map: A namespace profile identifier or explicit mapping that
            should be merged into the resulting mapping.
        extra_namespaces: Optional mapping applied after ``profile_or_map``.
        base: Optional starting mapping. When omitted the default namespace
            bindings for DDI are used.

    Returns:
        A dictionary containing the merged namespace bindings.
    """
    initial: Mapping[str | None, str]
    initial = base if base is not None else _DEFAULT_NS_MAP

    merged: NamespaceBindings = dict(initial)

    if profile_or_map is not None:
        if isinstance(profile_or_map, Mapping):
            merged.update(profile_or_map)
        else:
            merged.update(merge_namespace_profiles(profile_or_map))

    if extra_namespaces is not None:
        merged.update(extra_namespaces)

    return merged


def extract_namespace_declarations(element: Element) -> NamespaceBindings:
    """Return namespace declarations present on ``element``.

    Args:
        element: The XML element whose namespace declarations should be
            inspected.

    Returns:
        Mapping of prefixes (``None`` for the default namespace) to namespace
        URIs currently declared on the element.
    """
    if USING_LXML:
        lxml_element = cast(SupportsNsMap, element)
        return dict(lxml_element.nsmap or {})

    declarations: NamespaceBindings = {}
    for attr, value in element.attrib.items():
        if attr == "xmlns":
            declarations[None] = value
        elif attr.startswith("xmlns:"):
            declarations[attr.split(":", 1)[1]] = value
    return declarations


_GENERATED_PREFIX = re.compile(r"^(?:ns|p)\d+$")


def _is_generated_prefix(prefix: str | None) -> bool:
    """Return whether ``prefix`` was invented by a serializer.

    ``ns0``/``p1`` and friends carry no authorial intent: they are what a
    backend emits when nothing told it a better name. An authored prefix like
    ``ddi`` must be preserved against a competing default binding; a generated
    one must not, or a caller asking for a default namespace never gets one.
    """
    return isinstance(prefix, str) and bool(_GENERATED_PREFIX.match(prefix))


def _ordered_nsmap(bindings: Mapping[str | None, str]) -> NamespaceBindings:
    """Order namespace bindings deterministically, without changing meaning.

    lxml uses nsmap order both for writing declarations and for choosing an
    element's prefix (the first matching binding wins), so plain alphabetical
    order could change a ``<ddi:FragmentInstance>`` root into an unprefixed
    one. Prefixed bindings are sorted, and the default binding goes just after
    any prefixed binding that shares its URI (first when none does), which
    matches the stdlib backend's output in the common case.
    """
    prefixed = sorted(
        (prefix, uri) for prefix, uri in bindings.items() if prefix not in (None, "")
    )
    if None not in bindings:
        return dict(prefixed)

    default_uri = bindings[None]
    ordered: NamespaceBindings = {}
    inserted = False
    for index, (prefix, uri) in enumerate(prefixed):
        ordered[prefix] = uri
        shares_uri = uri == default_uri
        next_shares = (
            index + 1 < len(prefixed) and prefixed[index + 1][1] == default_uri
        )
        if shares_uri and not next_shares and not inserted:
            ordered[None] = default_uri
            inserted = True
    if not inserted:
        # Nothing else claims the URI, so the default leads, as it reads best
        # and as the stdlib backend writes it.
        ordered = {None: default_uri, **dict(prefixed)}
    return ordered


def apply_namespace_map(
    element: Element,
    nsmap: Mapping[str | None, str],
    *,
    preserve_existing: bool,
) -> Element:
    """Synchronise namespace declarations on ``element``.

    Args:
        element: The element to normalise.
        nsmap: Mapping of prefixes to namespace URIs that should be declared on
            the element. When ``preserve_existing`` is ``True`` existing
            declarations take precedence unless explicitly overridden.
        preserve_existing: When ``True`` namespace declarations already present
            on ``element`` are preserved unless explicitly overridden by
            ``nsmap``.

    Returns:
        The element whose namespace declarations were normalised. When using
        ``lxml`` a new root element may be returned if additional namespace
        bindings needed to be introduced.
    """
    effective_map: MutableMapping[str | None, str] = dict(nsmap)

    if preserve_existing:
        existing = extract_namespace_declarations(element)
        # Only a competing *prefixed* binding supersedes an existing one. A
        # default binding for the same URI does not: a document may declare
        # both ``xmlns="…instance…"`` and ``xmlns:ddi="…instance…"``, and
        # dropping the prefixed form silently rewrites its root element.
        already_bound = {
            uri
            for prefix, uri in effective_map.items()
            if uri and prefix not in (None, "")
        }
        requested_uris = {uri for uri in effective_map.values() if uri}
        for prefix, uri in existing.items():
            if _is_generated_prefix(prefix) and uri in requested_uris:
                continue
            # Never add a second prefix for a URI ``nsmap`` already binds: lxml
            # would resolve to the leftover prefix instead of the canonical one.
            if prefix not in (None, "") and uri in already_bound:
                continue
            effective_map.setdefault(prefix, uri)

    cleanup_namespaces(element, dict(effective_map) if effective_map else None)

    if not effective_map:
        return element

    if USING_LXML:
        lxml_element = cast(SupportsNsMap, element)
        current_nsmap = dict(lxml_element.nsmap or {})
        # Carry over only bindings whose URI ``effective_map`` does not already
        # bind, so a superseded prefix is not reinstated. When not preserving,
        # the caller's map is authoritative, including its default binding.
        target_uris = {
            uri
            for prefix, uri in effective_map.items()
            if uri and (not preserve_existing or prefix not in (None, ""))
        }
        carried = {
            prefix: uri
            for prefix, uri in current_nsmap.items()
            if prefix in (None, "")
            or (uri not in target_uris and not _is_generated_prefix(prefix))
        }
        combined_nsmap = _ordered_nsmap({**carried, **effective_map})
        # Rebuild when a binding is missing or out of order: lxml writes
        # declarations in insertion order, so ordering must be canonical for
        # identical output across build paths and backends.
        if list(current_nsmap.items()) != list(combined_nsmap.items()):
            new_root = create_element(element.tag, nsmap=combined_nsmap)

            new_root.text = element.text
            new_root.tail = element.tail

            for attr_name, attr_value in element.attrib.items():
                new_root.set(attr_name, attr_value)

            for child in list(element):
                new_root.append(child)

            element.clear()
            return new_root
        return element

    _apply_namespace_attributes(element, effective_map)
    return element


def _apply_namespace_attributes(
    element: Element, nsmap: Mapping[str | None, str]
) -> None:
    """Synchronise ``xmlns`` attributes on ``element`` when using stdlib XML."""
    namespace_attrs = [
        attr for attr in element.attrib if attr == "xmlns" or attr.startswith("xmlns:")
    ]
    for attr in namespace_attrs:
        element.attrib.pop(attr, None)

    used_uris: set[str] = set()
    for node in element.iter():
        tag = getattr(node, "tag", "")
        if isinstance(tag, str) and tag.startswith("{"):
            uri, _ = tag[1:].split("}", 1)
            used_uris.add(uri)
        for attr in node.attrib:
            if not attr.startswith("{"):
                continue
            uri, _ = attr[1:].split("}", 1)
            if uri != XMLNS:
                used_uris.add(uri)

    for prefix, uri in nsmap.items():
        if prefix in (None, "", "xml"):
            continue

        if uri in used_uris:
            continue

        attr = f"xmlns:{prefix}"
        element.set(attr, uri)


__all__ = [
    "apply_namespace_map",
    "build_namespace_map",
    "extract_namespace_declarations",
]
