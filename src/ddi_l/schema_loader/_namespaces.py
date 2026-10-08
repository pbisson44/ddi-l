"""Namespace helpers shared by schema conversion and validation routines."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .._etree import Element
from ..constants import DEFAULT_NSMAP, XML_NS
from ._compat import _fallback_qname_converter
from ._constants import XMLNS_NAMESPACE


def _extract_xmlns_attributes(element: Element) -> dict[str | None, str]:
    """Collect namespace declarations visible from ``element``."""
    namespaces: dict[str | None, str] = {}
    current: Element | None = element

    while current is not None:
        for attr_name, attr_value in current.attrib.items():
            if attr_name == "xmlns":
                namespaces[None] = attr_value
            elif attr_name.startswith("xmlns:"):
                prefix = attr_name.split(":", 1)[1]
                namespaces[prefix] = attr_value
            elif attr_name.startswith("{http://www.w3.org/2000/xmlns/}"):
                prefix = attr_name.split("}", 1)[1]
                if prefix:
                    namespaces[prefix] = attr_value
                else:
                    namespaces[None] = attr_value

        current = current.getparent() if hasattr(current, "getparent") else None

    return namespaces


def _gather_namespaces(element: Element, schema: Any) -> dict[str | None, str]:
    """Build a namespace map covering schema, defaults, and in-scope prefixes."""
    namespaces: dict[str | None, str] = {}

    if hasattr(element, "nsmap") and element.nsmap:
        for prefix, uri in element.nsmap.items():
            if uri:
                key = None if prefix in (None, "") else prefix
                namespaces[key] = uri
    else:
        namespaces.update(_extract_xmlns_attributes(element))

    schema_namespaces = getattr(schema, "namespaces", None)
    if schema_namespaces:
        items = (
            schema_namespaces.items()
            if hasattr(schema_namespaces, "items")
            else schema_namespaces
        )
        for prefix, uri in items:
            if uri:
                key = None if prefix in (None, "") else prefix
                namespaces.setdefault(key, uri)

    fallback_map: dict[str | None, str] = {}
    default_map: Mapping[str | None, str] = DEFAULT_NSMAP
    for prefix, uri in default_map.items():
        key = None if prefix in (None, "") else prefix
        fallback_map[key] = uri

    fallback_map.setdefault("xml", XML_NS)
    fallback_map.setdefault("xmlns", XMLNS_NAMESPACE)

    merged = dict(fallback_map)
    merged.update(namespaces)
    return merged


def _local_name(qname: str) -> str:
    """Return the local part of a qualified XML name."""
    if qname.startswith("{"):
        return qname.split("}", 1)[1]
    if ":" in qname:
        return qname.split(":", 1)[1]
    return qname


def _format_tag(tag: str, namespaces: Mapping[str | None, str]) -> str:
    """Format ``tag`` using the most suitable prefix from ``namespaces``."""
    if not isinstance(tag, str):
        return str(tag)
    if tag.startswith("{"):
        namespace, local = tag[1:].split("}", 1)
        for prefix, uri in namespaces.items():
            if uri == namespace:
                if prefix in (None, ""):
                    return local
                return f"{prefix}:{local}"
        return f"{{{namespace}}}{local}"
    return tag


def _describe_node(
    node: Element | None, namespaces: Mapping[str | None, str]
) -> str | None:
    """Build a concise textual description for ``node``."""
    if node is None or not hasattr(node, "tag"):
        return None
    tag = _format_tag(node.tag, namespaces)
    text = (node.text or "").strip()
    if text:
        snippet = text.splitlines()[0]
        if len(snippet) > 60:
            snippet = f"{snippet[:57]}..."
        return f"<{tag}> {snippet}"
    return f"<{tag}>"


def _find_path(root: Element, target: Element) -> list[Element]:
    """Return the list of nodes from ``root`` to ``target``."""
    if root is target:
        return [root]
    for child in list(root):
        path = _find_path(child, target)
        if path:
            return [root, *path]
    return []


def _build_xpath_from_tree(
    root: Element,
    target: Element,
    namespaces: Mapping[str | None, str],
) -> str | None:
    """Compute an absolute XPath for ``target`` relative to ``root``."""
    path = _find_path(root, target)
    if not path:
        return None
    segments: list[str] = []
    for index, node in enumerate(path):
        tag = _format_tag(node.tag, namespaces)
        if index == 0:
            segments.append(tag)
            continue
        parent = path[index - 1]
        siblings = [child for child in list(parent) if child.tag == node.tag]
        if len(siblings) > 1:
            position = siblings.index(node) + 1
            segments.append(f"{tag}[{position}]")
        else:
            segments.append(tag)
    return "/" + "/".join(segments)


def _normalize_prefixed_qnames(data: Any, namespaces: Mapping[str | None, str]) -> Any:
    """Rewrite prefixed keys in ``data`` to Clark notation when possible."""
    if isinstance(data, dict):
        normalized: dict[str, Any] = {}
        for key, value in data.items():
            new_key = key
            if key.startswith("@"):
                attr_name = key[1:]
                if ":" in attr_name and not attr_name.startswith("{"):
                    converted = _fallback_qname_converter(attr_name, namespaces)
                    if converted != attr_name:
                        new_key = f"@{converted}"
            elif not key.startswith("#"):
                if ":" in key and not key.startswith("{"):
                    converted = _fallback_qname_converter(key, namespaces)
                    if converted != key:
                        new_key = converted
            normalized[new_key] = _normalize_prefixed_qnames(value, namespaces)
        return normalized
    if isinstance(data, list):
        return [_normalize_prefixed_qnames(item, namespaces) for item in data]
    return data


def _denormalize_clark_notation(data: Any, namespaces: Mapping[str | None, str]) -> Any:
    """Convert Clark-notation keys in ``data`` back to prefixed form when possible."""

    def _lookup_prefix(namespace: str) -> str | None:
        explicit: list[str] = []
        fallbacks: list[str] = []
        for candidate, uri in namespaces.items():
            if uri != namespace:
                continue
            if candidate in ("xmlns",):
                continue
            if candidate in (None, ""):
                fallbacks.append("")
            else:
                explicit.append(str(candidate))
        if explicit:
            return explicit[0]
        if fallbacks:
            return ""
        return None

    if isinstance(data, dict):
        rewritten: dict[str, Any] = {}
        for key, value in data.items():
            if key.startswith("@{"):
                namespace, local = key[2:].split("}", 1)
                prefix = _lookup_prefix(namespace)
                if prefix is None:
                    rewritten[key] = _denormalize_clark_notation(value, namespaces)
                    continue
                rewritten_key = f"@{local}" if prefix == "" else f"@{prefix}:{local}"
                rewritten[rewritten_key] = _denormalize_clark_notation(
                    value, namespaces
                )
                continue
            if key.startswith("{") and "}" in key:
                namespace, local = key[1:].split("}", 1)
                prefix = _lookup_prefix(namespace)
                if prefix is None:
                    rewritten[key] = _denormalize_clark_notation(value, namespaces)
                    continue
                rewritten_key = local if prefix == "" else f"{prefix}:{local}"
                rewritten[rewritten_key] = _denormalize_clark_notation(
                    value, namespaces
                )
                continue
            rewritten[key] = _denormalize_clark_notation(value, namespaces)
        return rewritten

    if isinstance(data, list):
        return [_denormalize_clark_notation(item, namespaces) for item in data]

    return data


__all__ = [
    "_build_xpath_from_tree",
    "_denormalize_clark_notation",
    "_describe_node",
    "_extract_xmlns_attributes",
    "_format_tag",
    "_gather_namespaces",
    "_local_name",
    "_normalize_prefixed_qnames",
]
