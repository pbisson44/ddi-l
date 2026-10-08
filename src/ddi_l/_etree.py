"""Compatibility helpers for working with XML trees with or without lxml."""

from __future__ import annotations

import re
from typing import Any, cast

XMLNS = "http://www.w3.org/2000/xmlns/"

# ``ElementTree`` writes empty elements as ``<tag />``, lxml as ``<tag/>``;
# normalize so both backends produce identical bytes. The pattern anchors at
# ``<`` (so text content never matches) and consumes quoted attribute values
# whole, so a `` />`` inside an attribute value is never rewritten.
_EMPTY_ELEMENT_SPACING = re.compile(r"""(<(?:[^<>"']|"[^"]*"|'[^']*')*?)\s+/>""")


def _normalize_empty_elements(xml: str) -> str:
    """Render empty elements as ``<tag/>``, matching lxml's output."""
    return _EMPTY_ELEMENT_SPACING.sub(r"\1/>", xml)


_lxml_etree: Any
try:  # pragma: no cover - exercised indirectly
    from lxml import etree as _lxml_etree  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback used when lxml is unavailable
    _lxml_etree = None

USING_LXML = _lxml_etree is not None

if USING_LXML:  # pragma: no cover - behaviour validated through higher-level tests
    assert _lxml_etree is not None
    etree = _lxml_etree
    Element = etree._Element  # type: ignore[attr-defined]
    import xml.etree.ElementTree as _StdlibEtree

    def _lxml_generates_anonymous_prefixes() -> bool:
        try:
            probe = etree.Element("{urn:ddi:probe}Probe", nsmap={None: "urn:ddi:probe"})
        except Exception:  # pragma: no cover - defensive guard
            return False
        rendered = etree.tostring(probe, encoding="unicode")
        return rendered.startswith("<ns0:") or "xmlns:ns0" in rendered

    _LXML_NEEDS_STDLIB_SERIALIZATION = _lxml_generates_anonymous_prefixes()

    def _collect_namespace_bindings(element: Any) -> dict[str, str]:
        namespaces: dict[str, str] = {}
        for node in element.iter():
            nsmap = getattr(node, "nsmap", None)
            if not nsmap:
                nsmap = {}
            for prefix, uri in nsmap.items():
                if not uri:
                    continue
                key = "" if prefix in (None, "") else str(prefix)
                if key in {"xmlns", "xml"}:
                    continue
                namespaces.setdefault(key, uri)
            attribs = getattr(node, "attrib", {})
            default_uri = attribs.get("xmlns")
            if default_uri:
                namespaces.setdefault("", default_uri)
            for attr_name, attr_value in attribs.items():
                if attr_name.startswith("xmlns:"):
                    prefix = attr_name.split(":", 1)[1]
                    namespaces.setdefault(prefix, attr_value)
        return namespaces

    def _convert_to_stdlib_element(element: Any) -> _StdlibEtree.Element:
        clone = _StdlibEtree.Element(element.tag)
        for attr_name, attr_value in element.attrib.items():
            clone.set(attr_name, attr_value)
        clone.text = element.text
        clone.tail = element.tail
        for child in list(element):
            clone.append(_convert_to_stdlib_element(child))
        return clone

    def _indent_stdlib_element(elem: _StdlibEtree.Element, level: int = 0) -> None:
        indent_text = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent_text + "  "
            for child in list(elem):
                _indent_stdlib_element(child, level + 1)
            last_child = elem[-1]
            if last_child is not None and (
                not last_child.tail or not last_child.tail.strip()
            ):
                last_child.tail = indent_text
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent_text

    def _serialize_with_stdlib(
        element: Any,
        *,
        pretty_print: bool,
        xml_declaration: bool,
        encoding: str,
    ) -> str | bytes:
        namespaces = _collect_namespace_bindings(element)
        xml_namespace = "http://www.w3.org/XML/1998/namespace"
        used_uris: set[str] = set()
        for node in element.iter():
            tag = getattr(node, "tag", "")
            if isinstance(tag, str) and tag.startswith("{"):
                uri, _ = tag[1:].split("}", 1)
                used_uris.add(uri)
            for attr_name in getattr(node, "attrib", {}):
                if attr_name.startswith(f"{{{xml_namespace}}}"):
                    namespaces.setdefault("xml", xml_namespace)
                    continue
                if attr_name.startswith("{"):
                    uri, _ = attr_name[1:].split("}", 1)
                    if uri != XMLNS:
                        used_uris.add(uri)
        for prefix, uri in namespaces.items():
            if prefix in {"xmlns", "xml"}:
                continue
            _StdlibEtree.register_namespace("" if prefix == "" else prefix, uri)

        converted = _convert_to_stdlib_element(element)
        for prefix, uri in namespaces.items():
            if prefix in {"xmlns", "xml"}:
                continue
            if prefix == "" or uri in used_uris:
                continue
            converted.set(f"xmlns:{prefix}", uri)
        if pretty_print:
            _indent_stdlib_element(converted)

        serialized = _StdlibEtree.tostring(converted, encoding="unicode")
        if xml_declaration:
            encoding_label = encoding if encoding != "unicode" else "utf-8"
            declaration = f'<?xml version="1.0" encoding="{encoding_label.upper()}"?>\n'
        else:
            declaration = ""
        payload = declaration + serialized
        if encoding == "unicode":
            return payload
        return payload.encode(encoding)

    def create_element(tag: str, nsmap: dict[str | None, str] | None = None):
        """Return a new lxml element with optional namespace bindings.

        Args:
            tag: Qualified tag name for the element.
            nsmap: Mapping of prefixes to namespace URIs to attach to the root.

        Returns:
            Element: The created lxml element.
        """
        return etree.Element(tag, nsmap=nsmap)

    def tostring(element: Any, *, pretty_print: bool = True) -> str:
        """Serialize an lxml element to Unicode text.

        Args:
            element: Any to serialize.
            pretty_print: Whether to include human-readable indentation.

        Returns:
            str: The serialized XML string.
        """
        if _LXML_NEEDS_STDLIB_SERIALIZATION:
            return cast(
                str,
                _serialize_with_stdlib(
                    element,
                    pretty_print=pretty_print,
                    xml_declaration=False,
                    encoding="unicode",
                ),
            )
        return etree.tostring(element, encoding="unicode", pretty_print=pretty_print)

    def cleanup_namespaces(
        element: Any, nsmap: dict[str | None, str] | None = None
    ) -> None:
        """Remove unused namespace declarations from an lxml tree.

        Args:
            element: Root element whose namespace declarations should be normalized.
            nsmap: Explicit namespace mapping to retain at the top level.

        Side Effects:
            Mutates ``element`` in-place by adjusting ``xmlns`` declarations.
        """
        if nsmap is None:
            etree.cleanup_namespaces(element)
        else:
            etree.cleanup_namespaces(element, top_nsmap=nsmap)

    _DEFAULT_PARSER_KWARGS = {
        "remove_blank_text": True,
        "resolve_entities": False,
        "load_dtd": False,
        "no_network": True,
    }

    def _build_secure_parser() -> Any:
        """Return a hardened XML parser suitable for untrusted documents."""
        return etree.XMLParser(**_DEFAULT_PARSER_KWARGS)

    def _reject_doctype(tree: Any) -> None:
        """Raise when a parsed document carries a DTD.

        The parser options already neutralize entities and network access; this
        rejects the DTD outright, as ``defusedxml`` does on the stdlib backend,
        so both backends accept the same input. DDI instances never need a DTD.
        """
        docinfo = getattr(tree, "docinfo", None)
        if docinfo is None:
            return
        if docinfo.internalDTD is not None or docinfo.externalDTD is not None:
            raise etree.XMLSyntaxError(
                "Document type declarations are not permitted in DDI documents.",
                None,
                0,
                0,
            )

    def parse_xml(source) -> Any:
        """Parse XML from a path or file-like object using lxml.

        Args:
            source: Path, string, bytes, or file-like object containing XML.

        Returns:
            Element: Root element of the parsed document.

        Raises:
            lxml.etree.XMLSyntaxError: If the document cannot be parsed or
                declares a DTD.
        """
        parser = _build_secure_parser()
        if hasattr(source, "read") and not isinstance(source, (str, bytes, bytearray)):
            tree = etree.parse(source, parser=parser)
        else:
            tree = etree.parse(str(source), parser=parser)
        _reject_doctype(tree)
        return tree.getroot()

    def fromstring(data: str | bytes | bytearray) -> Any:
        """Create an lxml element from raw XML text.

        Args:
            data: XML payload as ``str`` or bytes.

        Returns:
            Element: Root element parsed from the payload.

        Raises:
            lxml.etree.XMLSyntaxError: If the payload is not well-formed or
                declares a DTD.
        """
        parser = _build_secure_parser()
        if isinstance(data, str):
            data = data.encode("utf-8")
        root = etree.fromstring(data, parser=parser)
        _reject_doctype(root.getroottree())
        return root

else:  # pragma: no cover - fallback validated via high level tests
    _DefusedEtree: Any
    try:  # pragma: no cover - exercised indirectly
        from defusedxml import ElementTree as _DefusedEtree  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover - fall back to stdlib parser
        _DefusedEtree = None

    from xml.etree import ElementTree as _StdlibEtree

    etree = _DefusedEtree or _StdlibEtree
    _LXML_NEEDS_STDLIB_SERIALIZATION = False

    # ``defusedxml.ElementTree`` mirrors most of the stdlib API but deliberately
    # omits helpers for constructing elements.  Fall back to the safe stdlib
    # implementations for those utilities while continuing to use ``defusedxml``
    # for parsing untrusted XML content whenever it is available.

    Element = getattr(etree, "Element", _StdlibEtree.Element)  # type: ignore[attr-defined]
    # ``defusedxml.ElementTree`` omits constructors such as :func:`Element`;
    # expose the stdlib ones so ``etree.Element`` works on either backend.
    if not hasattr(etree, "Element"):
        etree.Element = Element
    _register_namespace = getattr(
        etree, "register_namespace", _StdlibEtree.register_namespace
    )
    _tostring = getattr(etree, "tostring", _StdlibEtree.tostring)

    def _serialize_with_stdlib(
        element: Any,
        *,
        pretty_print: bool,
        xml_declaration: bool,
        encoding: str,
    ) -> str | bytes:
        target = element
        if pretty_print:
            _indent(target)
        serialized = _tostring(target, encoding="unicode")
        enc_label = encoding if encoding != "unicode" else "utf-8"
        declaration = (
            f'<?xml version="1.0" encoding="{enc_label.upper()}"?>\n'
            if xml_declaration
            else ""
        )
        payload = declaration + serialized
        if encoding == "unicode":
            return payload
        return payload.encode(encoding)

    def _register_namespaces(nsmap: dict[str | None, str]) -> None:
        """Register namespaces for subsequent stdlib element creation.

        Args:
            nsmap: Mapping of prefixes (or ``None`` for default) to namespace URIs.

        Side Effects:
            Updates the global namespace registry maintained by ``ElementTree``.
        """
        for prefix, uri in nsmap.items():
            if prefix in (None, ""):
                _register_namespace("", uri)
            else:
                assert prefix is not None
                _register_namespace(prefix, uri)

    def create_element(tag: str, nsmap: dict[str | None, str] | None = None):
        """Return a stdlib element, registering namespaces when provided.

        Args:
            tag: Qualified tag name for the element.
            nsmap: Namespace mapping to register globally before creation.

        Returns:
            Element: The created stdlib element.

        Side Effects:
            Calls :func:`_register_namespaces` when ``nsmap`` is supplied.
        """
        if nsmap:
            _register_namespaces(nsmap)
        return cast(Any, Element)(tag)

    def tostring(element: Any, *, pretty_print: bool = True) -> str:
        """Serialize an element to Unicode text, optionally indenting it.

        Args:
            element: Any to serialize.
            pretty_print: Whether to modify ``element`` with indentation before output.

        Returns:
            str: The serialized XML string.

        Side Effects:
            Mutates ``element`` in-place when ``pretty_print`` is ``True``.
        """
        if pretty_print:
            _indent(element)
        return _normalize_empty_elements(_tostring(element, encoding="unicode"))

    def cleanup_namespaces(
        element: Any, nsmap: dict[str | None, str] | None = None
    ) -> None:
        """Normalize namespace declarations when using the stdlib backend.

        Args:
            element: Root element whose namespaces should be cleaned up.
            nsmap: Namespace mapping that should remain registered.

        Side Effects:
            Mutates ``element`` and registers additional prefixes as needed.
        """
        if nsmap is None:
            nsmap = {}

        nsmap = dict(nsmap)
        _register_namespaces(nsmap)

        uri_to_prefix = {
            uri: (None if prefix in (None, "") else prefix)
            for prefix, uri in nsmap.items()
        }

        seen_uris = set()

        for node in element.iter():
            for attr in list(node.attrib):
                if attr.startswith(f"{{{XMLNS}}}"):
                    del node.attrib[attr]

            if node.tag.startswith("{"):
                uri, _ = node.tag[1:].split("}", 1)
                seen_uris.add(uri)

            for attr in node.attrib:
                if attr.startswith("{"):
                    uri, _ = attr[1:].split("}", 1)
                    if uri != XMLNS:
                        seen_uris.add(uri)

        counter = 0
        reserved = set(filter(None, uri_to_prefix.values()))

        def _next_prefix() -> str:
            nonlocal counter
            while True:
                candidate = f"p{counter}"
                counter += 1
                if candidate not in reserved and candidate != "xml":
                    reserved.add(candidate)
                    return candidate

        def _canonical_prefix(uri: str) -> str | None:
            """Return the registered DDI prefix for ``uri``, if there is one."""
            from .namespaces import NAMESPACE_PREFIXES

            for prefix, known_uri in NAMESPACE_PREFIXES.items():
                if known_uri == uri and prefix not in reserved:
                    return prefix
            return None

        def _assign_prefix(uri: str) -> None:
            if uri in uri_to_prefix or uri in (
                XMLNS,
                "http://www.w3.org/XML/1998/namespace",
            ):
                return
            # Prefer the namespace's canonical DDI prefix (``c:``, ``d:``) over a
            # generated ``p0:`` so both backends agree.
            prefix = _canonical_prefix(uri)
            if prefix is None:
                prefix = _next_prefix()
            else:
                reserved.add(prefix)
            uri_to_prefix[uri] = prefix
            _register_namespaces({prefix: uri})

        for uri in sorted(seen_uris):
            _assign_prefix(uri)

    def parse_xml(source) -> Any:
        """Parse XML from a path or file-like object using the stdlib parser.

        Args:
            source: Path, string, bytes, or file-like object containing XML.

        Returns:
            Element: Root element of the parsed document.

        Raises:
            xml.etree.ElementTree.ParseError: If the document cannot be parsed.
        """
        if hasattr(source, "read") and not isinstance(source, (str, bytes, bytearray)):
            tree = etree.parse(source)
        else:
            tree = etree.parse(str(source))
        return tree.getroot()

    def fromstring(data: str | bytes | bytearray) -> Any:
        """Build an element tree from raw XML text using the stdlib parser.

        Args:
            data: XML payload as ``str`` or bytes.

        Returns:
            Element: Root element parsed from the payload.

        Raises:
            xml.etree.ElementTree.ParseError: If the payload is not well-formed.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        return etree.fromstring(data)

    def _indent(elem: Any, level: int = 0) -> None:
        """Indent elements recursively to emulate ``pretty_print=True``.

        Args:
            elem: Any to indent, modified in-place.
            level: Current indentation depth.

        Side Effects:
            Mutates ``elem`` and its descendants by adjusting ``text`` and ``tail``.
        """
        indent_text = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent_text + "  "
            for child in elem:
                _indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent_text
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent_text


def _parser_errors() -> tuple[type[BaseException], ...]:
    """Exception types raised for malformed or rejected XML input."""
    candidates: list[type[BaseException]] = []
    for name in ("XMLSyntaxError", "ParseError"):
        candidate = getattr(etree, name, None)
        if isinstance(candidate, type):
            candidates.append(candidate)
    try:
        from defusedxml import DefusedXmlException
    except ModuleNotFoundError:  # pragma: no cover - defusedxml is a dependency
        pass
    else:
        candidates.append(DefusedXmlException)
    return tuple(candidates) or (Exception,)


PARSER_ERRORS: tuple[type[BaseException], ...] = _parser_errors()


__all__ = [
    "PARSER_ERRORS",
    "USING_LXML",
    "_LXML_NEEDS_STDLIB_SERIALIZATION",
    "Element",
    "_serialize_with_stdlib",
    "cleanup_namespaces",
    "create_element",
    "etree",
    "fromstring",
    "parse_xml",
    "tostring",
]
