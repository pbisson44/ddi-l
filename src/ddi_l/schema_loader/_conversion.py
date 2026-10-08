"""Conversion helpers between XML elements and mapping representations."""

from __future__ import annotations

import logging
from collections import deque
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any

from .._etree import Element, create_element
from ..constants import DEFAULT_NSMAP, XML_NS
from ..xml_utils import coerce_element as _coerce_xml_input
from ._compat import _resolve_qname_converter
from ._constants import XMLNS_NAMESPACE, SchemaInput
from ._namespaces import (
    _denormalize_clark_notation as _denormalize_clark_notation_py,
)
from ._namespaces import (
    _gather_namespaces,
    _local_name,
)
from ._namespaces import (
    _normalize_prefixed_qnames as _normalize_prefixed_qnames_py,
)
from ._versions import (
    detect_version_from_element,
    detect_version_from_mapping,
    normalize_version,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from types import ModuleType

    from . import XMLSchemaConverter as _XMLSchemaConverterType


def _xmlschema_module() -> ModuleType | None:
    from . import xmlschema as xmlschema_module

    return xmlschema_module


def _xmlschema_converter() -> _XMLSchemaConverterType | None:
    from . import XMLSchemaConverter as converter  # noqa: N813

    return converter


def _coerce_element(document: SchemaInput) -> Element:
    """Return an :class:`~xml.etree.ElementTree.Element` for ``document``."""
    try:
        return _coerce_xml_input(document)
    except TypeError as exc:  # pragma: no cover - defensive guard
        raise TypeError(
            "Unsupported document type. Expected str, Path, "
            "XML element, or file-like object."
        ) from exc


def _element_to_dict(
    element: Element, *, process_namespaces: bool = True
) -> dict[str, Any] | str:
    """Convert ``element`` into a nested mapping representation."""

    def _normalize(name: str) -> str:
        if process_namespaces and name.startswith("{"):
            namespace, local = name[1:].split("}", 1)
            return f"{{{namespace}}}{local}"
        return name

    result: dict = {}

    for attr_name, attr_value in element.attrib.items():
        normalized_name = _normalize(attr_name)
        result[f"@{normalized_name}"] = attr_value

    children = list(element)
    for child in children:
        key = _normalize(child.tag)
        value = _element_to_dict(child, process_namespaces=process_namespaces)
        if key in result:
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(value)
        else:
            result[key] = value

    if result:
        if element.text is not None:
            result["#text"] = element.text
        return result

    return element.text or ""


def _normalize_prefixed_qnames(data: Any, namespaces: Mapping[str | None, str]) -> Any:
    """Delegate to the Python implementation for prefixed QName normalization."""
    return _normalize_prefixed_qnames_py(data, namespaces)


def _denormalize_clark_notation(data: Any, namespaces: Mapping[str | None, str]) -> Any:
    """Delegate to the Python implementation for converting from Clark notation."""
    return _denormalize_clark_notation_py(data, namespaces)


def _normalize_result_namespaces(
    data: Any,
    element: Element,
    schema: Any,
    *,
    process_namespaces: bool,
) -> Any:
    if not process_namespaces:
        return data

    namespaces = _gather_namespaces(element, schema)
    normalized = _normalize_prefixed_qnames(data, namespaces)
    aligned = _align_mapping_with_element(normalized, element)
    cleaned = _remove_namespace_declarations(aligned)
    boolean_normalized = _normalize_boolean_attributes(cleaned)
    collapsed = _collapse_text_nodes(boolean_normalized)
    return _collapse_single_item_lists(collapsed)


def _is_namespace_declaration_key(key: str) -> bool:
    """Return whether ``key`` is a namespace declaration rather than an attribute.

    Both spellings have to be recognised. A stdlib tree yields the Clark form
    ``@{http://www.w3.org/2000/xmlns/}prefix``, while an lxml tree yields the
    plain ``@xmlns`` / ``@xmlns:prefix``. Matching only the Clark form left
    ``@xmlns`` in the mapping under lxml, and ``from_dict`` then rebuilt it as
    a literal attribute, which the schema rejects with "'xmlns' attribute not
    allowed for element".
    """
    if key.startswith(f"@{{{XMLNS_NAMESPACE}}}"):
        return True
    return key == "@xmlns" or key.startswith("@xmlns:")


def _remove_namespace_declarations(data: Any) -> Any:
    if isinstance(data, dict):
        filtered: dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(key, str) and _is_namespace_declaration_key(key):
                continue
            filtered[key] = _remove_namespace_declarations(value)
        return filtered
    if isinstance(data, list):
        return [_remove_namespace_declarations(item) for item in data]
    return data


def _normalize_boolean_attributes(data: Any) -> Any:
    if isinstance(data, dict):
        normalized: dict[str, Any] = {}
        for key, value in data.items():
            normalized_value = _normalize_boolean_attributes(value)
            if key.startswith("@") and isinstance(normalized_value, str):
                lowered = normalized_value.lower()
                if lowered == "true":
                    normalized_value = True
                elif lowered == "false":
                    normalized_value = False
            normalized[key] = normalized_value
        return normalized
    if isinstance(data, list):
        return [_normalize_boolean_attributes(item) for item in data]
    return data


def _collapse_text_nodes(data: Any) -> Any:
    if isinstance(data, dict):
        collapsed: dict[str, Any] = {
            key: _collapse_text_nodes(value) for key, value in data.items()
        }
        if set(collapsed.keys()) == {"#text"}:
            return collapsed["#text"]
        return collapsed
    if isinstance(data, list):
        return [_collapse_text_nodes(item) for item in data]
    return data


def _attribute_lookup(element: Element) -> dict[str, str]:
    lookup: dict[str, str] = {}
    nsmap = getattr(element, "nsmap", {}) or {}
    for attr_name in element.attrib:
        lookup[attr_name] = attr_name
        local = _local_name(attr_name)
        lookup.setdefault(local, attr_name)
        if attr_name.startswith("{"):
            namespace = attr_name[1:].split("}", 1)[0]
            for prefix, uri in nsmap.items():
                if not prefix:
                    continue
                if uri == namespace:
                    lookup.setdefault(f"{prefix}:{local}", attr_name)
        elif ":" in attr_name:
            lookup.setdefault(attr_name, attr_name)
    return lookup


def _append_child(result: dict[str, Any], key: str, value: Any) -> None:
    if key in result:
        if not isinstance(result[key], list):
            result[key] = [result[key]]
        result[key].append(value)
    else:
        result[key] = value


def _collapse_single_item_lists(data: Any) -> Any:
    if isinstance(data, list):
        collapsed = [_collapse_single_item_lists(item) for item in data]
        if len(collapsed) == 1:
            return collapsed[0]
        return collapsed

    if isinstance(data, dict):
        return {key: _collapse_single_item_lists(value) for key, value in data.items()}

    return data


def _element_has_content(element: Element) -> bool:
    """Return ``True`` when ``element`` carries meaningful payload."""
    if element.attrib:
        return True
    if any(True for _ in element):
        return True
    return bool(element.text and element.text.strip())


def _has_payload(data: Any) -> bool:
    """Return ``True`` when ``data`` contains non-empty content."""
    if isinstance(data, bool):
        return True
    if isinstance(data, (int, float)):
        return True
    if isinstance(data, str):
        return bool(data.strip())
    if isinstance(data, Mapping):
        for key, value in data.items():
            if key == "#text" and isinstance(value, str) and not value.strip():
                continue
            if _has_payload(value):
                return True
        return False
    if isinstance(data, Iterable) and not isinstance(data, (str, bytes, bytearray)):
        return any(_has_payload(item) for item in data)
    return bool(data)


def _align_mapping_with_element(data: Any, element: Element | None) -> Any:
    """Align mapping keys with the namespaces and ordering of ``element``."""
    if element is None:
        if isinstance(data, dict):
            return {k: _align_mapping_with_element(v, None) for k, v in data.items()}
        if isinstance(data, list):
            return [_align_mapping_with_element(item, None) for item in data]
        return data

    if isinstance(data, list):
        return [_align_mapping_with_element(item, element) for item in data]

    if not isinstance(data, dict):
        return data

    result: dict[str, Any] = {}
    attr_lookup = _attribute_lookup(element)
    child_map: dict[str, deque[Element]] = {}
    for child in list(element):
        local = _local_name(child.tag)
        child_map.setdefault(local, deque()).append(child)

    for key, value in data.items():
        if key.startswith("@"):
            raw_attr = key[1:]
            attr_name = attr_lookup.get(raw_attr)
            if attr_name is None and ":" in raw_attr:
                attr_name = attr_lookup.get(raw_attr.split(":", 1)[1])
            if attr_name is not None and attr_name in element.attrib:
                result[f"@{attr_name}"] = element.attrib[attr_name]
            else:
                result[key] = _align_mapping_with_element(value, element)
            continue

        if key == "#text":
            result[key] = (
                element.text
                if element.text is not None
                else _align_mapping_with_element(value, element)
            )
            continue

        if key.startswith("#"):
            result[key] = _align_mapping_with_element(value, element)
            continue

        local = _local_name(key)
        candidates = child_map.get(local)
        if not candidates:
            result[key] = _align_mapping_with_element(value, element)
            continue

        if isinstance(value, list):
            for item in value:
                child_element = candidates.popleft() if candidates else None
                remapped = _align_mapping_with_element(item, child_element)
                child_tag = child_element.tag if child_element is not None else key
                _append_child(result, child_tag, remapped)
        else:
            child_element = candidates.popleft() if candidates else None
            remapped = _align_mapping_with_element(value, child_element)
            child_tag = child_element.tag if child_element is not None else key
            _append_child(result, child_tag, remapped)

    return result


def _prune_schema_defaults_from_element(element: Element, payload: Any) -> None:
    """Trim schema-supplied defaults that were absent from ``payload``."""
    if not isinstance(payload, Mapping):
        return

    allowed_attributes: set[str] = set()
    for key in payload:
        if not isinstance(key, str) or not key.startswith("@"):
            continue
        allowed_attributes.add(key[1:])

    for attr_name in list(element.attrib):
        if attr_name == "xmlns" or attr_name.startswith("xmlns:"):
            continue
        if attr_name.startswith(f"{{{XMLNS_NAMESPACE}}}"):
            continue
        local = attr_name.split("}", 1)[1] if attr_name.startswith("{") else attr_name
        if attr_name not in allowed_attributes and local not in allowed_attributes:
            element.attrib.pop(attr_name, None)

    child_payloads: dict[str, deque[Any]] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or key.startswith("@") or key == "#text":
            continue
        items = value if isinstance(value, list) else [value]
        child_payloads.setdefault(key, deque()).extend(items)

    for child in list(element):
        candidates = child_payloads.get(child.tag)
        if not candidates:
            element.remove(child)
            continue
        payload_item = candidates.popleft() if candidates else None
        _prune_schema_defaults_from_element(child, payload_item)


def _collect_used_namespace_uris(data: Any, found: set[str]) -> None:
    """Collect the namespace URIs named by Clark-notation keys in ``data``."""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(key, str) and key.startswith(("{", "@{")):
                uri = key.lstrip("@")[1:].partition("}")[0]
                if uri and uri != XMLNS_NAMESPACE:
                    found.add(uri)
            _collect_used_namespace_uris(value, found)
    elif isinstance(data, list):
        for item in data:
            _collect_used_namespace_uris(item, found)


def _seed_canonical_namespaces(
    declared: Mapping[str | None, str] | None, normalized: Any
) -> dict[str | None, str]:
    """Add canonical prefixes for every DDI namespace the payload uses.

    A mapping produced by ``to_dict`` carries no namespace declarations, so
    the rebuilt tree needs them added, or lxml invents an ``ns0`` prefix per
    element. The root's own namespace becomes the default namespace.
    Declarations already present in the payload win; this only fills gaps.
    """
    from ..namespaces import NAMESPACE_PREFIXES

    seeded: dict[str | None, str] = dict(declared or {})

    if None not in seeded:
        root_namespace = _root_namespace_of(normalized)
        if root_namespace:
            seeded[None] = root_namespace

    already_bound = {uri for uri in seeded.values() if uri}

    used: set[str] = set()
    _collect_used_namespace_uris(normalized, used)

    for prefix, uri in NAMESPACE_PREFIXES.items():
        if uri in used and uri not in already_bound and prefix not in seeded:
            seeded[prefix] = uri
    return seeded


def _root_namespace_of(normalized: Any) -> str | None:
    """Return the namespace of the single root tag in ``normalized``."""
    if not isinstance(normalized, Mapping):
        return None
    keys = [key for key in normalized if isinstance(key, str) and key.startswith("{")]
    if len(keys) != 1:
        return None
    namespace, _, _ = keys[0][1:].partition("}")
    return namespace or None


def _collect_declared_namespaces(data: Any) -> dict[str | None, str]:
    """Gather namespace declarations embedded within mapping structures."""
    collected: dict[str | None, str] = {}

    if isinstance(data, dict):
        for key, value in data.items():
            if key.startswith("@"):
                attr_name = key[1:]
                if attr_name == "xmlns":
                    collected[None] = str(value)
                elif attr_name.startswith("xmlns:"):
                    prefix = attr_name.split(":", 1)[1]
                    collected[prefix] = str(value)
                elif attr_name.startswith(f"{{{XMLNS_NAMESPACE}}}"):
                    prefix = attr_name.split("}", 1)[1]
                    if prefix:
                        collected[prefix] = str(value)
                    else:
                        collected[None] = str(value)
            if isinstance(value, (dict, list)):
                nested = _collect_declared_namespaces(value)
                for prefix, uri in nested.items():
                    collected.setdefault(prefix, uri)
    elif isinstance(data, list):
        for item in data:
            nested = _collect_declared_namespaces(item)
            for prefix, uri in nested.items():
                collected.setdefault(prefix, uri)

    return collected


def _schema_namespace_defaults(schema: Any) -> dict[str | None, str]:
    """Build a namespace map combining schema and library defaults."""
    defaults: dict[str | None, str] = {}

    schema_namespaces = getattr(schema, "namespaces", None)
    if schema_namespaces:
        items: Iterable[tuple[str | None, str]]
        if hasattr(schema_namespaces, "items"):
            items = schema_namespaces.items()
        else:
            items = schema_namespaces
        for prefix, uri in items:
            if not uri:
                continue
            key = None if prefix in (None, "") else prefix
            defaults.setdefault(key, uri)

    default_map: Mapping[str | None, str] = DEFAULT_NSMAP
    for prefix, uri in default_map.items():
        key = None if prefix in (None, "") else prefix
        defaults.setdefault(key, uri)

    defaults.setdefault("xml", XML_NS)
    defaults.setdefault("xmlns", XMLNS_NAMESPACE)

    return defaults


def _normalize_input_mapping(
    data: Mapping[str, Any],
    schema: Any,
    *,
    process_namespaces: bool,
) -> Mapping[str, Any]:
    """Normalize prefixed keys in ``data`` using schema-aware namespace maps."""
    if not process_namespaces:
        return data

    namespaces = _schema_namespace_defaults(schema)
    declared = _collect_declared_namespaces(data)
    namespaces.update(declared)
    return _normalize_prefixed_qnames(data, namespaces)


def _prepare_nsmap(
    nsmap: Mapping[str | None, str] | None,
) -> dict[str | None, str] | None:
    """Normalize namespace declarations for use with :func:`create_element`."""
    if not nsmap:
        return None

    prepared: dict[str | None, str] = {}
    for prefix, uri in nsmap.items():
        if not uri:
            continue
        if prefix == "xmlns":
            continue
        if prefix in ("", None):
            prepared.setdefault(None, uri)
        else:
            prepared.setdefault(prefix, uri)
    return prepared or None


def _build_element_from_mapping(
    tag: str,
    content: Any,
    *,
    process_namespaces: bool,
    nsmap: Mapping[str | None, str] | None = None,
    prepared_nsmap: Mapping[str | None, str] | None = None,
) -> Element:
    """Construct an XML element using the provided mapping representation."""
    namespace_sentinel = object()

    def _resolve_namespace_declaration(attr_name: str):
        if attr_name == "xmlns":
            return None
        if attr_name.startswith("xmlns:"):
            return attr_name.split(":", 1)[1] or None
        if attr_name.startswith(f"{{{XMLNS_NAMESPACE}}}"):
            prefix = attr_name.split("}", 1)[1]
            return prefix or None
        return namespace_sentinel

    element_nsmap = (
        prepared_nsmap if prepared_nsmap is not None else _prepare_nsmap(nsmap)
    )

    nsmap_dict = dict(element_nsmap) if element_nsmap is not None else None

    if not isinstance(content, dict):
        element = create_element(tag, nsmap=nsmap_dict)
        element.text = str(content)
        return element

    attributes: dict[str, str] = {}
    text: str | None = None
    children: list[Element] = []

    for key, value in content.items():
        if key.startswith("@"):
            attr_name = key[1:]
            if attr_name.startswith("{"):
                attributes[attr_name] = str(value)
                continue
            if process_namespaces and nsmap is not None:
                namespace = _resolve_namespace_declaration(attr_name)
                if namespace is namespace_sentinel and ":" in attr_name:
                    prefix, local = attr_name.split(":", 1)
                    resolved = nsmap.get(prefix)
                    if resolved:
                        attr_name = f"{{{resolved}}}{local}"
            attributes[attr_name] = str(value)
            continue

        if key == "#text":
            text = str(value) if value is not None else None
            continue

        child_nsmap = nsmap
        if isinstance(value, list):
            for item in value:
                child = _build_element_from_mapping(
                    key,
                    item,
                    process_namespaces=process_namespaces,
                    nsmap=child_nsmap,
                    prepared_nsmap=prepared_nsmap,
                )
                children.append(child)
            continue

        child = _build_element_from_mapping(
            key,
            value,
            process_namespaces=process_namespaces,
            nsmap=child_nsmap,
            prepared_nsmap=prepared_nsmap,
        )
        children.append(child)

    element = create_element(tag, nsmap=nsmap_dict)

    for attr_name, attr_value in attributes.items():
        element.set(attr_name, attr_value)

    if text is not None:
        element.text = text

    for child in children:
        element.append(child)

    return element


def _dict_to_element(
    data: Mapping[str, Any],
    *,
    process_namespaces: bool,
    nsmap: Mapping[str | None, str] | None = None,
) -> Element:
    if len(data) != 1:
        raise ValueError("Expected mapping to describe a single XML element.")

    tag, content = next(iter(data.items()))

    prepared_nsmap = _prepare_nsmap(nsmap)
    element = _build_element_from_mapping(
        tag,
        content,
        process_namespaces=process_namespaces,
        nsmap=nsmap,
        prepared_nsmap=prepared_nsmap,
    )

    if isinstance(content, Mapping):
        _prune_schema_defaults_from_element(element, content)

    return element


def from_dict(
    data: Mapping[str, Any],
    *,
    process_namespaces: bool = True,
    version: str | None = None,
) -> Element:
    """Build an XML element tree from ``data``."""
    from . import get_schema as _get_schema

    target_version = normalize_version(version or detect_version_from_mapping(data))
    schema = _get_schema(version=target_version)
    normalized = _normalize_input_mapping(
        data, schema, process_namespaces=process_namespaces
    )

    namespace_map: Mapping[str | None, str] | None = None
    if process_namespaces:
        namespace_map = _collect_declared_namespaces(data)
        namespace_map = _seed_canonical_namespaces(namespace_map, normalized)

    xmlschema_module = _xmlschema_module()

    if xmlschema_module is None:
        return _dict_to_element(
            normalized,
            process_namespaces=process_namespaces,
            nsmap=namespace_map,
        )

    if hasattr(schema, "from_dict"):
        try:
            element = schema.from_dict(
                normalized,
                process_namespaces=process_namespaces,
            )
        except AttributeError:
            element = None
        else:
            if element is not None:
                if isinstance(element, list):
                    if len(element) != 1:
                        raise ValueError(
                            "Expected mapping to describe a single XML element."
                        )
                    element = element[0]
                payload_view: Any = normalized
                if isinstance(payload_view, Mapping) and len(payload_view) == 1:
                    payload_view = next(iter(payload_view.values()))
                _prune_schema_defaults_from_element(element, payload_view)
                return element

    if hasattr(schema, "fromdict"):
        return schema.fromdict(normalized)

    return _dict_to_element(
        normalized,
        process_namespaces=process_namespaces,
        nsmap=namespace_map,
    )


def to_dict(
    element: Element, *, process_namespaces: bool = True, version: str | None = None
) -> dict:
    """Return a mapping representation of an XML element."""
    from . import get_schema as _get_schema

    target_version = normalize_version(version or detect_version_from_element(element))
    schema = _get_schema(version=target_version)

    xmlschema_module = _xmlschema_module()
    converter_cls = _xmlschema_converter()

    if (
        xmlschema_module is None
        or converter_cls is None
        or not hasattr(schema, "to_dict")
    ):
        result = _element_to_dict(element, process_namespaces=process_namespaces)
        return _normalize_result_namespaces(
            result,
            element,
            schema,
            process_namespaces=process_namespaces,
        )

    converter = converter_cls(
        map_qnames=process_namespaces,
        attr_prefix="@",
        text_key="#text",
        qname_converter=_resolve_qname_converter(),
    )

    def _fallback_result() -> tuple[Any, Any]:
        fallback_raw = _element_to_dict(element, process_namespaces=process_namespaces)
        normalized = _normalize_result_namespaces(
            fallback_raw,
            element,
            schema,
            process_namespaces=process_namespaces,
        )
        if _has_payload(normalized):
            return normalized, fallback_raw
        if _has_payload(fallback_raw):
            return fallback_raw, fallback_raw
        if _element_has_content(element):
            return fallback_raw, fallback_raw
        return normalized, fallback_raw

    missing_namespace_errors: tuple[type[Exception], ...] = ()
    if xmlschema_module is not None:
        exceptions_module = getattr(xmlschema_module, "exceptions", None)
        candidates = []
        for name in ("XMLSchemaKeyError", "XMLSchemaValueError"):
            candidate = (
                getattr(exceptions_module, name, None) if exceptions_module else None
            )
            if candidate is not None:
                candidates.append(candidate)
        if candidates:
            missing_namespace_errors = tuple(candidates)

    def _should_handle_missing_namespace(error: BaseException) -> bool:
        message = str(error)
        return "namespace" in message and "not loaded" in message

    if missing_namespace_errors:
        try:
            raw_result = schema.to_dict(
                element,
                process_namespaces=process_namespaces,
                converter=converter,
                validation="lax",
                use_defaults=False,
            )
        except missing_namespace_errors as exc:
            if _should_handle_missing_namespace(exc):
                fallback, fallback_raw = _fallback_result()
                if _has_payload(fallback):
                    return fallback
                if _has_payload(fallback_raw) or _element_has_content(element):
                    return fallback_raw
                return fallback
            raise
    else:
        raw_result = schema.to_dict(
            element,
            process_namespaces=process_namespaces,
            converter=converter,
            validation="lax",
            use_defaults=False,
        )

    errors: Iterable[Exception] | None = None
    if isinstance(raw_result, tuple):
        payload = raw_result[0]
        if len(raw_result) > 1:
            errors = raw_result[1]
    else:
        payload = raw_result

    if errors:
        errors_list = list(errors)
        logger.debug(
            "xmlschema returned validation errors during "  # pragma: no cover
            "to_dict conversion",
            exc_info=False,
            extra={"errors": errors_list},
        )

    result = _normalize_result_namespaces(
        payload,
        element,
        schema,
        process_namespaces=process_namespaces,
    )

    if isinstance(result, dict) and list(result.keys()) == [element.tag]:
        collapsed = result[element.tag]
        if not _has_payload(collapsed):
            fallback, fallback_raw = _fallback_result()
            if _has_payload(fallback):
                return fallback
            if _has_payload(fallback_raw) or _element_has_content(element):
                return fallback_raw
        return collapsed

    if not _has_payload(result):
        fallback, fallback_raw = _fallback_result()
        if _has_payload(fallback):
            return fallback
        if _has_payload(fallback_raw) or _element_has_content(element):
            return fallback_raw

    return result


__all__ = [
    "_align_mapping_with_element",
    "_coerce_element",
    "_collect_declared_namespaces",
    "_denormalize_clark_notation",
    "_dict_to_element",
    "_element_to_dict",
    "_normalize_input_mapping",
    "_normalize_prefixed_qnames",
    "_normalize_result_namespaces",
    "_prepare_nsmap",
    "from_dict",
    "to_dict",
]
