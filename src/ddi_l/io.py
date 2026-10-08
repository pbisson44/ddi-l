"""Convenience helpers for reading and writing DDI instance documents."""

from __future__ import annotations

import io
from collections.abc import Iterator, Mapping, MutableMapping
from collections.abc import Sequence as TypingSequence
from dataclasses import is_dataclass
from pathlib import Path
from typing import (
    BinaryIO,
    TextIO,
    cast,
)

from . import schema_loader
from ._etree import (
    _LXML_NEEDS_STDLIB_SERIALIZATION,
    PARSER_ERRORS,
    USING_LXML,
    Element,
    _serialize_with_stdlib,
    etree,
    parse_xml,
    tostring,
)
from .constants import DEFAULT_NSMAP, XSI_NS, get_namespace_set
from .document import DDIDocument, DDIFragment, Document
from .exceptions import (
    DDIParseError,
    DDIReadError,
    DDIWriteError,
    build_error_location,
)
from .models import MaintainableBase, QuestionItem, Variable, clone_element
from .models.base import qn
from .namespace_utils import apply_namespace_map
from .schema_loader._versions import detect_version_from_element, normalize_version
from .xml_utils import coerce_element as _coerce_xml_input
from .xml_utils import resolve_xml_source

__all__ = [
    "iter_questions",
    "iter_variables",
    "iterparse_ddi",
    "read",
    "read_ddi",
    "validate",
    "write",
    "write_ddi",
]

SourceType = str | Path | bytes | bytearray | BinaryIO | TextIO
DocumentLike = (
    Document
    | DDIDocument
    | DDIFragment
    | Element
    | MaintainableBase
    | str
    | bytes
    | bytearray
)
DDIWrapper = DDIDocument | DDIFragment

_DEFAULT_NS_MAP: Mapping[str | None, str] = DEFAULT_NSMAP

_DEFAULT_MAINTAINABLES: TypingSequence[type[MaintainableBase]] = (
    MaintainableBase.maintainable_types()
)


def _coerce_source(source: SourceType) -> tuple[str | BinaryIO | TextIO, bool]:
    """Normalize different source types into a path or file-like handle.

    Args:
        source: The input to parse, which may be a filesystem path, textual or
            binary XML content, or an open file-like object.

    Returns:
        A tuple ``(handle, should_close)`` where ``handle`` is either a string
        path or a file-like object suitable for XML parsing, and
        ``should_close`` indicates whether the caller must close the handle
        after use.

    Raises:
        FileNotFoundError: Raised when ``source`` is a :class:`~pathlib.Path`
            instance that does not exist on disk.
        TypeError: Raised when ``source`` is not one of the supported
            types.
    """
    try:
        kind, payload = resolve_xml_source(source, require_existing_path=True)
    except TypeError as exc:  # pragma: no cover - defensive guard
        raise TypeError("Unsupported source type for DDI parsing.") from exc

    if kind == "path":
        return str(payload), False
    if kind == "text":
        text_payload = cast(str, payload)
        return io.BytesIO(text_payload.encode("utf-8")), True
    if kind == "bytes":
        byte_payload = cast(bytes, payload)
        return io.BytesIO(byte_payload), True
    if kind == "file":
        return cast(BinaryIO | TextIO, payload), False
    raise TypeError("Unsupported source type for DDI parsing.")


def _coerce_element(document_or_element: DocumentLike) -> Element:
    """Convert a supported document representation into an XML element.

    Args:
        document_or_element: A DDI document wrapper, maintainable instance,
            XML element, serialized XML string or bytes, or dataclass with a
            ``to_xml`` method that can be transformed into an
            :class:`~ddi_l._etree.Element` instance.

    Returns:
        The XML :class:`~ddi_l._etree.Element` representing the provided
        document or maintainable object.

    Raises:
        TypeError: Raised when ``document_or_element`` cannot be coerced into
            an XML element via the supported interfaces.
    """
    if isinstance(document_or_element, (DDIDocument, DDIFragment)):
        return document_or_element.root
    if isinstance(document_or_element, Document):
        document_or_element._flush()
        return document_or_element._inner.root
    if isinstance(document_or_element, Element):
        return document_or_element
    if isinstance(document_or_element, MaintainableBase):
        return document_or_element.to_xml()
    if is_dataclass(document_or_element) and hasattr(document_or_element, "to_xml"):
        return document_or_element.to_xml()

    try:
        return _coerce_xml_input(document_or_element)
    except TypeError as exc:  # pragma: no cover - defensive guard
        raise TypeError("Unsupported document type for DDI serialization.") from exc


def read_ddi(
    source: SourceType,
    *,
    validate: bool = False,
    build_index: bool = False,
    version: str | None = None,
) -> DDIWrapper:
    """Parse ``source`` into a :class:`DDIDocument` or :class:`DDIFragment`.

    Args:
        source: The DDI instance XML to parse. Accepts filesystem paths,
            strings, bytes, or file-like objects.
        validate: Whether to validate the parsed document against the DDI XML
            schema.
        build_index: Build the resolver index now. By default it is built on
            first use of :attr:`DDIDocument.resolver`.
        version: Optional DDI schema version override used when validating the
            parsed document.

    Returns:
        A :class:`DDIDocument` when the root element is ``DDIInstance`` or a
        :class:`DDIFragment` when the root element is ``FragmentInstance``.

    Raises:
        FileNotFoundError: Propagated when ``source`` is a :class:`~pathlib.Path`
            that does not exist.
        TypeError: Raised when ``source`` is not a supported input type.
        ValueError: Raised when the parsed XML root is not a valid DDI
            instance or fragment tag.
        DDIReadError: Raised when XML parsing fails because the input is
            malformed or cannot be read.
    """
    root: Element

    try:
        handle, should_close = _coerce_source(source)
    except (FileNotFoundError, TypeError):
        raise
    except Exception as exc:  # pragma: no cover - defensive guard
        location = build_error_location(sources=[source])
        raise DDIReadError(
            "Failed to prepare DDI source for parsing.",
            cause=exc,
            location=location,
        ) from exc
    try:
        try:
            root = parse_xml(handle)
        except PARSER_ERRORS as exc:
            raise DDIParseError.from_parser_error(exc, sources=[source]) from exc
        except OSError as exc:
            location = build_error_location(sources=[source])
            raise DDIReadError(
                "Failed to read DDI XML content.",
                cause=exc,
                location=location,
            ) from exc
        except Exception as exc:  # pragma: no cover - defensive guard
            location = build_error_location(sources=[source])
            raise DDIReadError(
                "Unexpected failure while reading DDI XML.",
                cause=exc,
                location=location,
            ) from exc
    finally:
        if should_close and hasattr(handle, "close"):
            handle.close()

    version_override = normalize_version(version) if version is not None else None

    # The root's own namespace decides the wrapper type; ``version`` only
    # selects the schema used for validation.
    namespace_set = get_namespace_set(
        detect_version_from_element(root) or version_override
    )

    if validate:
        schema_loader.validate(root, version=version_override)

    instance_namespace = namespace_set["INSTANCE_NS"]
    document_tag = qn(instance_namespace, "DDIInstance")
    fragment_tag = qn(instance_namespace, "FragmentInstance")
    if root.tag == document_tag:
        document = DDIDocument(root)
        if build_index:
            document.build_index()
        return document
    if root.tag == fragment_tag:
        return DDIFragment(root)
    location = build_error_location(sources=[source], element=root)
    raise DDIReadError(
        "Document root must be DDIInstance or FragmentInstance"
        " in the DDI instance namespace.",
        location=location,
    )


class _WriteBackend:
    """Strategy object encapsulating backend-specific serialization behaviour."""

    def prepare(self, element: Element) -> Element:
        """Return the element that should be serialised for this backend."""
        raise NotImplementedError

    def serialize(
        self,
        element: Element,
        *,
        pretty_print: bool,
        xml_declaration: bool,
        encoding: str,
    ) -> bytes:
        """Serialize ``element`` into bytes for the configured backend."""
        raise NotImplementedError


def _finalize_document(
    body: str,
    *,
    pretty_print: bool,
    xml_declaration: bool,
    encoding: str,
) -> bytes:
    """Attach the XML declaration and trailing newline, identically per backend.

    The backends spell the declaration differently and disagree on the
    trailing newline; this is the one place that decides both.
    """
    declaration = (
        f'<?xml version="1.0" encoding="{encoding.upper()}"?>\n'
        if xml_declaration
        else ""
    )
    if pretty_print and not body.endswith("\n"):
        body += "\n"
    return (declaration + body).encode(encoding)


class _LXMLWriteBackend(_WriteBackend):
    """Implementation of :class:`_WriteBackend` for the lxml backend."""

    def prepare(self, element: Element) -> Element:
        return element

    def serialize(
        self,
        element: Element,
        *,
        pretty_print: bool,
        xml_declaration: bool,
        encoding: str,
    ) -> bytes:
        if _LXML_NEEDS_STDLIB_SERIALIZATION:
            serialized = _serialize_with_stdlib(
                element,
                pretty_print=pretty_print,
                xml_declaration=False,
                encoding="unicode",
            )
            body = (
                serialized.decode(encoding)
                if isinstance(serialized, bytes)
                else serialized
            )
            return _finalize_document(
                body,
                pretty_print=pretty_print,
                xml_declaration=xml_declaration,
                encoding=encoding,
            )

        # Serialize without a declaration and add our own, so the two backends
        # agree on its spelling.
        xml_bytes = etree.tostring(
            element,
            encoding="unicode",
            pretty_print=pretty_print,
        )
        body = xml_bytes.decode(encoding) if isinstance(xml_bytes, bytes) else xml_bytes
        return _finalize_document(
            body,
            pretty_print=pretty_print,
            xml_declaration=xml_declaration,
            encoding=encoding,
        )


class _StdlibWriteBackend(_WriteBackend):
    """Implementation of :class:`_WriteBackend` for the stdlib backend."""

    def prepare(self, element: Element) -> Element:
        return clone_element(element)

    def serialize(
        self,
        element: Element,
        *,
        pretty_print: bool,
        xml_declaration: bool,
        encoding: str,
    ) -> bytes:
        serialized = (
            tostring(element, pretty_print=pretty_print)
            if pretty_print
            else etree.tostring(element, encoding="unicode")
        )
        if isinstance(serialized, bytes):
            serialized = serialized.decode(encoding)
        return _finalize_document(
            serialized,
            pretty_print=pretty_print,
            xml_declaration=xml_declaration,
            encoding=encoding,
        )


_WRITE_BACKEND: _WriteBackend = (
    _LXMLWriteBackend() if USING_LXML else _StdlibWriteBackend()
)


def _root_nsmap_for_tree(element: Element) -> Mapping[str | None, str]:
    """Return the bindings the root should declare so children need not.

    Hoisting every binding to the root stops lxml repeating declarations on
    nested elements and matches the stdlib backend's output. A prefix
    already bound to a different URI is left alone, and ``xsi`` is declared
    only when the tree uses it.
    """
    merged: dict[str | None, str] = {
        prefix: uri
        for prefix, uri in _DEFAULT_NS_MAP.items()
        if uri != XSI_NS or _tree_uses_namespace(element, XSI_NS)
    }
    if not USING_LXML:
        return merged

    for node in element.iter():
        for prefix, uri in (getattr(node, "nsmap", None) or {}).items():
            merged.setdefault(prefix, uri)
    return merged


def _tree_uses_namespace(element: Element, uri: str) -> bool:
    """Return whether any tag or attribute in the tree is in ``uri``.

    A namespace is "used" when a tag or attribute names it, not merely when
    it is declared.
    """
    marker = f"{{{uri}}}"
    for node in element.iter():
        tag = node.tag
        if isinstance(tag, str) and tag.startswith(marker):
            return True
        if any(name.startswith(marker) for name in node.attrib):
            return True
    return False


def _emit_xml(
    element: Element,
    *,
    pretty_print: bool,
    xml_declaration: bool,
    encoding: str,
) -> bytes:
    """Serialize ``element`` using the active XML backend."""
    target = _WRITE_BACKEND.prepare(element)
    if USING_LXML:
        target = clone_element(target)
    target = apply_namespace_map(
        target, _root_nsmap_for_tree(target), preserve_existing=True
    )
    return _WRITE_BACKEND.serialize(
        target,
        pretty_print=pretty_print,
        xml_declaration=xml_declaration,
        encoding=encoding,
    )


def _write_to_destination(
    payload: bytes,
    destination: str | Path | BinaryIO | TextIO | None,
    *,
    encoding: str,
) -> bytes:
    """Write ``payload`` to ``destination``.

    Handles text and binary streams uniformly.
    """
    if destination is None:
        return payload
    if isinstance(destination, (str, Path)):
        Path(destination).write_bytes(payload)
        return payload
    if hasattr(destination, "write"):
        if isinstance(destination, io.TextIOBase):
            destination.write(payload.decode(encoding))
        else:
            cast(BinaryIO, destination).write(payload)
        return payload
    raise TypeError("Unsupported destination type for DDI serialization.")


def write_ddi(
    document_or_element: DocumentLike,
    destination: str | Path | BinaryIO | TextIO | None = None,
    *,
    pretty_print: bool = True,
    xml_declaration: bool = True,
    encoding: str = "utf-8",
    version: str | None = None,
) -> bytes:
    """Serialize a document to ``destination`` (or return bytes when omitted).

    Args:
        document_or_element: A DDI document wrapper, maintainable object,
            element, or serialized XML that should be emitted as XML.
        destination: Optional output location. When ``None``, bytes are
            returned. When a path-like object, bytes are written to disk. When
            a writable binary or text stream, the serialized XML is written to
            the stream.
        pretty_print: Whether to format the XML output with indentation when
            supported by the underlying XML backend.
        xml_declaration: Whether to include the XML declaration at the start of
            the serialized output.
        encoding: Text encoding used when writing XML bytes or decoding to
            text streams.
        version: Optional DDI schema version override used to assert the target
            release is supported when specified.

    Returns:
        The serialized XML bytes regardless of ``destination``.

    Raises:
        DDIWriteError: Raised when serialization or writing to the destination
            fails.
    """
    if version is not None:
        normalize_version(version)

    location_sources = [document_or_element]
    element: Element | None = None
    try:
        element = _coerce_element(document_or_element)
    except DDIWriteError:
        raise
    except TypeError as exc:
        location = build_error_location(sources=location_sources)
        raise DDIWriteError(
            "Failed to prepare DDI XML for serialisation.",
            cause=exc,
            location=location,
        ) from exc
    except ValueError as exc:
        element_hint = None
        if isinstance(document_or_element, (DDIDocument, DDIFragment)):
            element_hint = document_or_element.root
        elif isinstance(document_or_element, Element):
            element_hint = document_or_element
        location = build_error_location(
            sources=location_sources,
            element=element_hint,
        )
        raise DDIWriteError(
            "Failed to serialise DDI XML content.",
            cause=exc,
            location=location,
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        element_hint = element
        location = build_error_location(sources=location_sources, element=element_hint)
        raise DDIWriteError(
            "Unexpected failure while writing DDI XML.",
            cause=exc,
            location=location,
        ) from exc

    try:
        xml_bytes = _emit_xml(
            element,
            pretty_print=pretty_print,
            xml_declaration=xml_declaration,
            encoding=encoding,
        )
        return _write_to_destination(xml_bytes, destination, encoding=encoding)
    except DDIWriteError:
        raise
    except ValueError as exc:
        location = build_error_location(element=element, sources=location_sources)
        raise DDIWriteError(
            "Failed to serialise DDI XML content.",
            cause=exc,
            location=location,
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        location = build_error_location(element=element, sources=location_sources)
        raise DDIWriteError(
            "Unexpected failure while writing DDI XML.",
            cause=exc,
            location=location,
        ) from exc


_LXML_ITERPARSE_DEFAULTS = {
    "resolve_entities": False,
    "load_dtd": False,
    "no_network": True,
}


def _prune_element(element: Element, parent: Element | None) -> None:
    """Clear ``element`` and detach it from ``parent`` to free memory."""
    element.clear()
    if parent is not None:
        parent.remove(element)


def iterparse_ddi(
    source: SourceType,
    *,
    maintainable_types: TypingSequence[type[MaintainableBase]] | None = None,
    **kwargs: object,
) -> Iterator[MaintainableBase]:
    """Stream maintainable objects from a DDI instance document.

    Every element whose tag matches a requested type is yielded, fully
    populated, when its end tag is reached. Maintainables nested inside
    another requested maintainable are yielded as well and kept in the tree
    until the enclosing one is built. Once an element is no longer inside a
    requested match it is cleared, so memory is bounded by the largest
    outermost match. Request only the types you need, as :func:`iter_variables`
    does, to keep that bound small.

    Args:
        source: The XML content to parse, provided as a path, serialized XML,
            or file-like object.
        maintainable_types: Classes to instantiate when their XML tags are
            encountered. Defaults to every registered maintainable type.
        **kwargs: Additional keyword arguments forwarded to
            :func:`etree.iterparse`.

    Yields:
        Instances of the requested maintainable classes, innermost first.
    """
    registered_maintainables = MaintainableBase.maintainable_types()
    maintainable_types = (
        tuple(maintainable_types)
        if maintainable_types is not None
        else registered_maintainables
    )
    tag_to_type: MutableMapping[str, type[MaintainableBase]] = {
        maintainable.TAG: maintainable for maintainable in maintainable_types
    }
    prunable_tags = {maintainable.TAG for maintainable in registered_maintainables}
    prunable_tags.update(tag_to_type)
    if USING_LXML:
        for key, value in _LXML_ITERPARSE_DEFAULTS.items():
            kwargs.setdefault(key, value)
    handle, should_close = _coerce_source(source)
    stack: list[Element] = []
    root: Element | None = None
    open_matches = 0
    try:
        context = etree.iterparse(handle, events=("start", "end"), **kwargs)
        for event, element in context:
            if event == "start":
                if root is None:
                    root = element
                stack.append(element)
                if element.tag in tag_to_type:
                    open_matches += 1
                continue
            stack.pop()
            cls = tag_to_type.get(element.tag)
            if cls is not None:
                open_matches -= 1
                yield cls.from_xml(element)
            if open_matches == 0 and element.tag in prunable_tags and stack:
                _prune_element(element, stack[-1])
    finally:
        if root is not None:
            root.clear()
        if should_close and hasattr(handle, "close"):
            handle.close()


def iter_variables(source: SourceType, **kwargs: object) -> Iterator[Variable]:
    """Iterate over :class:`Variable` maintainables in a DDI instance.

    Args:
        source: The XML content to parse for ``Variable`` maintainables.
        **kwargs: Additional keyword arguments forwarded to
            :func:`iterparse_ddi`.

    Returns:
        An iterator yielding :class:`Variable` objects as they are parsed from
        ``source``.

    Side Effects:
        Consumes the input stream and prunes processed XML elements via
        :func:`iterparse_ddi` to minimize memory usage.
    """
    if isinstance(source, DDIDocument):
        yield from source.resolver.iter_resources(Variable)
        return

    for maintainable in iterparse_ddi(source, maintainable_types=(Variable,), **kwargs):
        yield cast(Variable, maintainable)


def iter_questions(source: SourceType, **kwargs: object) -> Iterator[QuestionItem]:
    """Iterate over :class:`QuestionItem` maintainables in a DDI instance.

    Args:
        source: The XML content to parse for ``QuestionItem`` maintainables.
        **kwargs: Additional keyword arguments forwarded to
            :func:`iterparse_ddi`.

    Returns:
        An iterator yielding :class:`QuestionItem` objects as they are parsed
        from ``source``.

    Side Effects:
        Consumes the input stream and prunes processed XML elements via
        :func:`iterparse_ddi` to minimize memory usage.
    """
    if isinstance(source, DDIDocument):
        yield from source.resolver.iter_resources(QuestionItem)
        return

    for maintainable in iterparse_ddi(
        source,
        maintainable_types=(QuestionItem,),
        **kwargs,
    ):
        yield cast(QuestionItem, maintainable)


read = read_ddi
write = write_ddi
validate = schema_loader.validate
