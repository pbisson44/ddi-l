"""The XML backend: the native core, lxml or the standard library.

The first installed of ``ddi_l_native`` (the ``native`` extra), lxml and the
standard library is used, chosen once at import. The ``DDI_L_XML_BACKEND``
environment variable (``native``, ``lxml`` or ``stdlib``) picks one instead;
the tests use it to run on each.

Native elements behave like the standard library's, so the native backend
shares the standard library's helpers and only parses differently.
"""

from __future__ import annotations

import io
import os
import re
import types
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from types import MappingProxyType
from typing import Any, cast
from xml.etree import ElementTree as _ElementTree

from ._whitespace import (
    XHTML_NS,
    is_inline_xhtml,
    is_mixed_content,
    may_lose_mixed_space,
    without_indentation,
)

XMLNS = "http://www.w3.org/2000/xmlns/"
_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
_DOCTYPE_REFUSED = "Document type declarations are not permitted in DDI documents."

# The encoding an XML declaration names, to rewrite in text encoded to UTF-8.
_DECLARED_ENCODING = re.compile(
    r"""\A(\ufeff?\s*<\?xml\b[^>]*?\bencoding\s*=\s*)(["'])[^"']*\2"""
)


def text_as_utf8(text: str) -> bytes:
    """``text`` as UTF-8 bytes, its XML declaration naming UTF-8 too.

    A ``str`` is already decoded: the encoding its declaration names is the
    one it was read from, not the one its bytes are now in.
    """
    utf8 = _DECLARED_ENCODING.sub(
        lambda match: f"{match.group(1)}{match.group(2)}utf-8{match.group(2)}",
        text,
        count=1,
    )
    return utf8.encode("utf-8")


# ``ElementTree`` writes empty elements as ``<tag />``, lxml as ``<tag/>``;
# normalize so both backends produce identical bytes. The pattern anchors at
# ``<`` (so text content never matches) and consumes quoted attribute values
# whole, so a `` />`` inside an attribute value is never rewritten.
_EMPTY_ELEMENT_SPACING = re.compile(r"""(<(?:[^<>"']|"[^"]*"|'[^']*')*?)\s+/>""")


def _normalize_empty_elements(xml: str) -> str:
    """Render empty elements as ``<tag/>``, matching lxml's output."""
    return _EMPTY_ELEMENT_SPACING.sub(r"\1/>", xml)


# ---- Namespace prefixes for the standard library's writer ----------------------
#
# ElementTree names namespaces from a registry it keeps for the whole
# process. ddi-l never changes it: it serialises with prefixes of its own.

# ElementTree's built-in prefixes.
_BUILT_IN_PREFIXES: Mapping[str, str] = MappingProxyType(
    {
        "http://www.w3.org/XML/1998/namespace": "xml",
        "http://www.w3.org/1999/xhtml": "html",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
        "http://schemas.xmlsoap.org/wsdl/": "wsdl",
        "http://www.w3.org/2001/XMLSchema": "xs",
        "http://www.w3.org/2001/XMLSchema-instance": "xsi",
        "http://purl.org/dc/elements/1.1/": "dc",
    }
)


def _with_prefixes(
    prefixes: Mapping[str, str], nsmap: Mapping[str | None, str]
) -> dict[str, str]:
    """``prefixes`` (URI to prefix) with ``nsmap`` added in order.

    Each binding replaces what it clashes with, as
    ``ElementTree.register_namespace`` would.
    """
    found = dict(prefixes)
    for given, uri in nsmap.items():
        prefix = given or ""
        if re.match(r"ns\d+$", prefix):
            raise ValueError("Prefix format reserved for internal use")
        for known_uri, known_prefix in list(found.items()):
            if known_uri == uri or known_prefix == prefix:
                del found[known_uri]
        found[uri] = prefix
    return found


def _qualified_names(
    root: Any, prefixes: Mapping[str, str]
) -> tuple[dict[Any, Any], dict[str, str]]:
    """``ElementTree._namespaces``, reading ``prefixes`` for its registry."""
    qnames: dict[Any, Any] = {None: None}
    namespaces: dict[str, str] = {}

    def add(qname: str) -> None:
        if qname[:1] != "{":
            qnames[qname] = qname
            return
        uri, local = qname[1:].rsplit("}", 1)
        prefix = namespaces.get(uri)
        if prefix is None:
            prefix = prefixes.get(uri)
            if prefix is None:
                prefix = f"ns{len(namespaces)}"
            if prefix != "xml":
                namespaces[uri] = prefix
        qnames[qname] = f"{prefix}:{local}" if prefix else local

    for node in root.iter():
        tag = node.tag
        if isinstance(tag, _ElementTree.QName):
            tag = tag.text
        if isinstance(tag, str):
            if tag not in qnames:
                add(tag)
        elif tag not in (None, _ElementTree.Comment, _ElementTree.PI):
            _ElementTree._raise_serialization_error(tag)  # type: ignore[attr-defined]
        for key, value in node.items():
            if isinstance(key, _ElementTree.QName):
                key = key.text
            if key not in qnames:
                add(key)
            if isinstance(value, _ElementTree.QName) and value.text not in qnames:
                add(value.text)
        text = node.text
        if isinstance(text, _ElementTree.QName) and text.text not in qnames:
            add(text.text)
    return qnames, namespaces


def _stdlib_tostring(element: Any, prefixes: Mapping[str, str]) -> str:
    """``ElementTree.tostring(element, encoding="unicode")``, with prefixes.

    Each namespace is named from ``prefixes`` (URI to prefix).
    """
    qnames, namespaces = _qualified_names(element, prefixes)
    out = io.StringIO()
    _ElementTree._serialize_xml(  # type: ignore[attr-defined]
        out.write, element, qnames, namespaces, short_empty_elements=True
    )
    return out.getvalue()


_lxml_etree: Any
_BACKENDS = ("native", "lxml", "stdlib")
_REQUESTED = os.environ.get("DDI_L_XML_BACKEND", "").strip().lower() or None
if _REQUESTED not in (None, *_BACKENDS):  # pragma: no cover - a setup mistake
    raise ImportError(
        f"DDI_L_XML_BACKEND={_REQUESTED!r}: expected one of {', '.join(_BACKENDS)}"
    )

_native: Any = None
if _REQUESTED in (None, "native"):
    try:  # pragma: no cover - depends on the platform's ddi-l-native wheel
        import ddi_l_native as _native
    except ModuleNotFoundError:  # pragma: no cover - the stand-in, or not installed
        if _REQUESTED == "native":
            raise

_lxml_etree = None
if _native is None and _REQUESTED in (None, "lxml"):
    try:  # pragma: no cover - exercised indirectly
        from lxml import etree as _lxml_etree  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover - fallback without lxml
        if _REQUESTED == "lxml":
            raise

NATIVE = _native is not None
USING_LXML = _lxml_etree is not None
BACKEND = "native" if NATIVE else "lxml" if USING_LXML else "stdlib"

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

    def _indent_stdlib_element(
        elem: _StdlibEtree.Element, level: int = 0, preserve: bool = False
    ) -> None:
        space = elem.get(_XML_SPACE)
        if space is not None:
            preserve = space == "preserve"
        indent_text = "\n" + "  " * level
        if len(elem) and not _written_as_it_stands(elem, preserve):
            if not elem.text or not elem.text.strip():
                elem.text = indent_text + "  "
            for child in list(elem):
                _indent_stdlib_element(child, level + 1, preserve)
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
        prefixes = _with_prefixes(
            _BUILT_IN_PREFIXES,
            {
                prefix: uri
                for prefix, uri in namespaces.items()
                if prefix not in {"xmlns", "xml"}
            },
        )

        converted = _convert_to_stdlib_element(element)
        for prefix, uri in namespaces.items():
            if prefix in {"xmlns", "xml"}:
                continue
            if prefix == "" or uri in used_uris:
                continue
            converted.set(f"xmlns:{prefix}", uri)
        if pretty_print:
            _indent_stdlib_element(converted)

        serialized = _stdlib_tostring(converted, prefixes)
        if xml_declaration:
            encoding_label = encoding if encoding != "unicode" else "utf-8"
            declaration = f'<?xml version="1.0" encoding="{encoding_label.upper()}"?>\n'
        else:
            declaration = ""
        payload = declaration + serialized
        if encoding == "unicode":
            return payload
        return payload.encode(encoding)

    def unicode_text(element: Any) -> str:
        """``element`` serialised as lxml writes it."""
        return etree.tostring(element, encoding="unicode")

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
        if not pretty_print:
            return etree.tostring(element, encoding="unicode")
        with inline_layout_kept(element):
            return etree.tostring(element, encoding="unicode", pretty_print=True)

    @contextmanager
    def inline_layout_kept(element: Any) -> Iterator[Any]:
        """While inside, libxml2 does not indent inside ``element``'s inline XHTML.

        libxml2 indents the children of an element with no text of its own,
        which in ``<p><b>Pet</b><i>s</i></p>`` would put a line break inside
        "Pets". An empty text keeps it from doing so; it is set for the
        duration only. Only XHTML elements are visited.
        """
        parents = _bare_inline_parents(element)
        for parent in parents:
            parent.text = ""
        try:
            yield element
        finally:
            for parent in parents:
                parent.text = None

    def _bare_inline_parents(element: Any) -> list[Any]:
        """Elements holding inline XHTML with no text at all beside it."""
        found: dict[Any, None] = {}
        for node in element.iter(f"{{{XHTML_NS}}}*"):
            if not is_inline_xhtml(node.tag):
                continue
            parent = node.getparent()
            if parent is None or parent in found:
                continue
            if not parent.text and not any(child.tail for child in parent):
                found[parent] = None
        return list(found)

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

    def _build_secure_parser(
        *, keep_blank_text: bool = False, encoding: str | None = None
    ) -> Any:
        """Return a hardened XML parser suitable for untrusted documents.

        ``encoding`` overrides the document's own declaration: text that was
        a ``str`` is parsed as the UTF-8 it was encoded to.
        """
        kwargs: dict[str, Any] = dict(_DEFAULT_PARSER_KWARGS)
        if keep_blank_text:
            kwargs["remove_blank_text"] = False
        if encoding is not None:
            kwargs["encoding"] = encoding
        return etree.XMLParser(**kwargs)

    def _loses_mixed_space(root: Any) -> bool:
        """Whether ``remove_blank_text`` may have dropped text of mixed XHTML.

        See `ddi_l._whitespace.may_lose_mixed_space`; only the parents of
        XHTML elements are looked at, so a file without XHTML costs one pass
        in C.
        """
        # The parents themselves, not their id(): a proxy let go is freed and
        # its address reused by the next one.
        seen: set[Any] = set()
        for node in root.iter(f"{{{XHTML_NS}}}*"):
            parent = node.getparent()
            if parent is None or parent in seen:
                continue
            seen.add(parent)
            if (parent.text or "").strip():
                continue
            if is_mixed_content(parent, list(parent)):
                return True
        return False

    def _parse(
        source: Any, *, keep_blank_text: bool = False, text: bool = False
    ) -> Any:
        parser = _build_secure_parser(
            keep_blank_text=keep_blank_text, encoding="utf-8" if text else None
        )
        tree = etree.parse(source, parser=parser)
        _reject_doctype(tree)
        return tree.getroot()

    def _parse_data(data: bytes, *, text: bool = False) -> Any:
        """Parse ``data``, a second time keeping blanks if mixed XHTML needs it.

        The second reading keeps every blank, then drops the ones that are
        layout, as the stdlib backend does, so both read the same tree.
        """
        root = _parse(io.BytesIO(data), text=text)
        if not _loses_mixed_space(root):
            return root
        return without_indentation(
            _parse(io.BytesIO(data), keep_blank_text=True, text=text)
        )

    def _reject_doctype(tree: Any) -> None:
        """Raise when a parsed document carries a DTD.

        The parser options already neutralize entities and network access; this
        rejects the DTD outright, as ``defusedxml`` does on the stdlib backend
        with ``forbid_dtd``, so both backends accept the same input. DDI
        instances never need a DTD.
        """
        docinfo = getattr(tree, "docinfo", None)
        if docinfo is None:
            return
        if docinfo.internalDTD is not None or docinfo.externalDTD is not None:
            raise etree.XMLSyntaxError(_DOCTYPE_REFUSED, None, 0, 0)

    # What `iterparse_ddi` passes to `etree.iterparse`, as `_parse` does.
    HARDENED_ITERPARSE: dict[str, bool] = {
        "resolve_entities": False,
        "load_dtd": False,
        "no_network": True,
    }

    def refuse_doctype(element: Any) -> None:
        """Raise when the document ``element`` was read from declares a DTD."""
        _reject_doctype(element.getroottree())

    @contextmanager
    def doctype_refused() -> Iterator[None]:
        """Nothing to do: lxml reads a DTD, and `refuse_doctype` refuses it."""
        yield

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
        if hasattr(source, "read") and not isinstance(source, (str, bytes, bytearray)):
            return _parse_stream(source)
        root = _parse(str(source))
        if not _loses_mixed_space(root):
            return root
        # By path again, so a compressed file is read as lxml read it.
        return without_indentation(_parse(str(source), keep_blank_text=True))

    def _parse_stream(stream: Any) -> Any:
        """Parse a stream incrementally, rewinding it for a second reading.

        A stream that cannot be rewound (stdin) is read whole first, and
        text is parsed as the UTF-8 it is encoded to.
        """
        start = None
        try:
            if stream.seekable():
                start = stream.tell()
                stream.seek(start)  # a stream that cannot, says so here
        except (AttributeError, OSError, ValueError):
            start = None
        text = isinstance(stream.read(0), str)
        if start is None or text:
            data = stream.read()
            if isinstance(data, str):
                return _parse_data(text_as_utf8(data))
            return _parse_data(data)
        root = _parse(stream)
        if not _loses_mixed_space(root):
            return root
        stream.seek(start)
        return without_indentation(_parse(stream, keep_blank_text=True))

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
        text = isinstance(data, str)
        if isinstance(data, str):
            data = data.encode("utf-8")
        parser = _build_secure_parser(encoding="utf-8" if text else None)
        root = etree.fromstring(data, parser=parser)
        _reject_doctype(root.getroottree())
        if not _loses_mixed_space(root):
            return root
        parser = _build_secure_parser(
            keep_blank_text=True, encoding="utf-8" if text else None
        )
        root = etree.fromstring(bytes(data), parser=parser)
        return without_indentation(root)

else:  # pragma: no cover - fallback validated via high level tests
    _DefusedEtree: Any
    try:  # pragma: no cover - exercised indirectly
        from defusedxml import ElementTree as _DefusedEtree  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover - fall back to stdlib parser
        _DefusedEtree = None

    from xml.etree import ElementTree as _StdlibEtree

    etree = _DefusedEtree or _StdlibEtree
    _LXML_NEEDS_STDLIB_SERIALIZATION = False

    # What defusedxml raises for a DTD; nothing without it.
    _DTD_REFUSALS: tuple[type[BaseException], ...] = ()
    if _DefusedEtree is not None:
        from defusedxml.common import DTDForbidden

        _DTD_REFUSALS = (DTDForbidden,)
        # defusedxml refuses a DTD only when asked; lxml's `_reject_doctype`
        # refuses it always.
        _DEFUSED_OPTIONS: dict[str, bool] = {"forbid_dtd": True}
        # What `iterparse_ddi` passes to `etree.iterparse`.
        HARDENED_ITERPARSE: dict[str, bool] = {
            "forbid_dtd": True,
            "forbid_entities": True,
            "forbid_external": True,
        }
    else:  # pragma: no cover - defusedxml is a dependency
        _DEFUSED_OPTIONS = {}
        HARDENED_ITERPARSE = {}

    def refuse_doctype(element: Any) -> None:
        """Nothing to do: defusedxml refuses a DTD while it parses."""

    @contextmanager
    def doctype_refused() -> Iterator[None]:
        """Report defusedxml's refusal of a DTD in lxml's words."""
        try:
            yield
        except _DTD_REFUSALS as error:
            raise etree.ParseError(_DOCTYPE_REFUSED) from error

    # ``defusedxml.ElementTree`` mirrors most of the stdlib API but deliberately
    # omits helpers for constructing elements.  Fall back to the safe stdlib
    # implementations for those utilities while continuing to use ``defusedxml``
    # for parsing untrusted XML content whenever it is available.

    Element = getattr(etree, "Element", _StdlibEtree.Element)  # type: ignore[attr-defined]
    # ``defusedxml.ElementTree`` omits constructors such as `Element`;
    # expose the stdlib ones so ``etree.Element`` works on either backend.
    if not hasattr(etree, "Element"):
        etree.Element = Element
    # The prefixes `create_element` and `cleanup_namespaces` register, kept
    # for the current context (thread or task) only.
    _PREFIXES: ContextVar[Mapping[str, str]] = ContextVar(
        "ddi_l_namespace_prefixes", default=_BUILT_IN_PREFIXES
    )

    def _register_namespaces(nsmap: dict[str | None, str]) -> None:
        """Register namespaces for this context's serialisation.

        Args:
            nsmap: Mapping of prefixes (or ``None`` for default) to namespace URIs.

        Side Effects:
            Updates the current context's prefixes; ElementTree's own
            registry is left alone.
        """
        _PREFIXES.set(MappingProxyType(_with_prefixes(_PREFIXES.get(), nsmap)))

    def unicode_text(element: Any) -> str:
        """``element`` serialised as ElementTree writes it.

        Its namespaces are named with this context's prefixes.
        """
        return _stdlib_tostring(element, _PREFIXES.get())

    def create_element(tag: str, nsmap: dict[str | None, str] | None = None):
        """Return a stdlib element, registering namespaces when provided.

        Args:
            tag: Qualified tag name for the element.
            nsmap: Namespace mapping to register globally before creation.

        Returns:
            Element: The created stdlib element.

        Side Effects:
            Calls `_register_namespaces` when ``nsmap`` is supplied.
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
        return _normalize_empty_elements(unicode_text(element))

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
        if not hasattr(source, "read") or isinstance(source, (str, bytes, bytearray)):
            source = str(source)
        with doctype_refused():
            tree = etree.parse(source, **_DEFUSED_OPTIONS)
        return _as_lxml_reads(tree.getroot())

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
            data = text_as_utf8(data)
        with doctype_refused():
            root = etree.fromstring(data, **_DEFUSED_OPTIONS)
        return _as_lxml_reads(root)

    @contextmanager
    def inline_layout_kept(element: Any) -> Iterator[Any]:
        """``element``: the stdlib pretty-printer leaves mixed content alone."""
        yield element

    def _as_lxml_reads(root: Any) -> Any:
        """``root``, without its layout where inline XHTML starts some content.

        There the lxml backend reads the file again keeping its blanks and
        drops the layout; doing the same gives both backends one tree.
        """
        if may_lose_mixed_space(root):
            return without_indentation(root)
        return root

    def _indent(elem: Any, level: int = 0, preserve: bool = False) -> None:
        """Indent elements recursively to emulate ``pretty_print=True``.

        Args:
            elem: Any to indent, modified in-place.
            level: Current indentation depth.
            preserve: Whether ``xml:space="preserve"`` applies, from above.

        Side Effects:
            Mutates ``elem`` and its descendants by adjusting ``text`` and ``tail``.
        """
        space = elem.get(_XML_SPACE)
        if space is not None:
            preserve = space == "preserve"
        indent_text = "\n" + "  " * level
        if len(elem) and not _written_as_it_stands(elem, preserve):
            if not elem.text or not elem.text.strip():
                elem.text = indent_text + "  "
            for child in elem:
                _indent(child, level + 1, preserve)
            if not child.tail or not child.tail.strip():
                child.tail = indent_text
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent_text


if NATIVE:  # pragma: no cover - depends on the platform's ddi-l-native wheel
    # The standard library's helpers above work on native elements; only
    # making and parsing them differ.
    Element = _native.Element

    def create_element(tag: str, nsmap: dict[str | None, str] | None = None):
        """A native element, registering namespaces as the stdlib backend does."""
        if nsmap:
            _register_namespaces(nsmap)
        return Element(tag)

    _DECLARED_BYTES = re.compile(
        rb"""\A(?:\xef\xbb\xbf)?\s*<\?xml\b[^>]*?\bencoding\s*=\s*["']([^"']*)["']"""
    )
    _UTF8_NAMES = frozenset({"utf-8", "utf8", "us-ascii", "ascii"})

    def _as_utf8(data: bytes) -> bytes:
        """``data`` in UTF-8: the native parser reads nothing else."""
        if data.startswith((b"\xff\xfe", b"\xfe\xff")):
            return text_as_utf8(data.decode("utf-16"))
        declared = _DECLARED_BYTES.match(data)
        if declared is None:
            return data
        encoding = declared.group(1).decode("ascii", "replace").lower()
        if encoding in _UTF8_NAMES:
            return data
        try:
            return text_as_utf8(data.decode(encoding))
        except (LookupError, UnicodeDecodeError) as error:
            raise _StdlibEtree.ParseError(f"unknown encoding: {encoding}") from error

    def _read_bytes(source: Any) -> bytes:
        if hasattr(source, "read"):
            data = source.read()
        else:
            with open(os.fspath(source), "rb") as handle:
                data = handle.read()
        if isinstance(data, str):
            return text_as_utf8(data)
        return _as_utf8(bytes(data))

    def _native_reads(root: Any) -> Any:
        """``root``, without its layout where the stdlib backend drops it."""
        if _native.uses_namespace(root, XHTML_NS):
            return _as_lxml_reads(root)
        return root

    def parse_xml(source) -> Any:
        """Parse XML from a path or file-like object with the native parser."""
        return _native_reads(_native.parse(_read_bytes(source)))

    def fromstring(data: str | bytes | bytearray) -> Any:
        """Build a native tree from XML text or bytes."""
        if isinstance(data, str):
            return _native_reads(_native.parse(text_as_utf8(data)))
        return _native_reads(_native.parse(_as_utf8(bytes(data))))

    def parse_indexed(data: bytes) -> tuple[Any, Any]:
        """``data`` parsed as `parse_xml` does, with each element's source span."""
        root, index = _native.parse(data, index=True)
        return _native_reads(root), index

    # ``etree`` for the native backend: the standard library's module with
    # native elements, parsed by the native parser. Streaming (`iterparse`)
    # stays defusedxml's, with standard library elements.
    etree = types.ModuleType("ddi_l._etree.native")
    etree.__dict__.update(vars(_StdlibEtree))
    etree.Element = Element
    etree.SubElement = _native.SubElement
    etree.fromstring = etree.XML = fromstring
    etree.parse = lambda source, parser=None: _StdlibEtree.ElementTree(
        parse_xml(source)
    )
    if _DefusedEtree is not None:
        etree.iterparse = _DefusedEtree.iterparse
        etree.DefusedXmlException = getattr(_DefusedEtree, "DefusedXmlException", None)

    def adopt(element: Any) -> Any:
        """A native copy of ``element``, so it can join native trees.

        `etree.iterparse` gives standard library elements.
        """
        if isinstance(element, Element):
            return element
        root = Element(element.tag, dict(element.attrib))
        root.text, root.tail = element.text, element.tail
        pending = [(element, root)]
        while pending:
            source, target = pending.pop()
            for child in source:
                copy = _native.SubElement(target, child.tag, dict(child.attrib))
                copy.text, copy.tail = child.text, child.tail
                pending.append((child, copy))
        return root

else:

    def adopt(element: Any) -> Any:
        """``element``: `etree.iterparse` gives this backend's own elements."""
        return element


def _written_as_it_stands(elem: Any, preserve: bool = False) -> bool:
    """Whether pretty-printing leaves ``elem``'s content alone.

    Mixed content (text beside the children, or inline XHTML) is written as it
    stands: its whitespace is text. So is any text under
    ``xml:space="preserve"``. libxml2 does the same for text beside the
    children, and `inline_layout_kept` makes it do so for inline XHTML.
    """
    if is_mixed_content(elem, list(elem)):
        return True
    return preserve and (bool(elem.text) or any(child.tail for child in elem))


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
    "BACKEND",
    "HARDENED_ITERPARSE",
    "NATIVE",
    "PARSER_ERRORS",
    "USING_LXML",
    "_LXML_NEEDS_STDLIB_SERIALIZATION",
    "Element",
    "adopt",
    "cleanup_namespaces",
    "create_element",
    "doctype_refused",
    "etree",
    "fromstring",
    "parse_xml",
    "refuse_doctype",
    "tostring",
    "unicode_text",
]
