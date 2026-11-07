"""Write a document read from a file with its unchanged parts as they were read.

A document keeps the bytes it was read from. When it is written, each
element whose content is unchanged (same tag, attributes, text and children,
however they were reached) is copied from those bytes: its quotes,
character references, CDATA, comments, line ends and indentation stay as
read. Only new or changed elements are formatted, by a layout profile that
matches the file: Colectica's for a ``FragmentInstance``, this library's
pretty-printing (with the file's own indentation) otherwise.

An element is matched by a digest of its content, not by identity, so a
model written back unchanged, a copied element and a moved construct all
come back as the bytes they were read as. A copied span must also mean the
same where it lands: every namespace prefix it relies on has to be bound to
the same URI there, or it is formatted afresh.
"""

from __future__ import annotations

import hashlib
import io
import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from ._etree import NATIVE, PARSER_ERRORS, Element, parse_xml

if NATIVE:
    import ddi_l_native as _native

    from ._etree import parse_indexed
from ._whitespace import is_mixed_content
from .constants import DEFAULT_NSMAP, XML_NS
from .xml_utils import resolve_xml_source

__all__ = ["Source", "write"]

_UTF8_BOM = b"\xef\xbb\xbf"
_DECLARED_ENCODING = re.compile(rb"""^<\?xml[^>]*?encoding\s*=\s*["']([^"']+)["']""")
# One piece of markup: a comment, CDATA, a processing instruction or
# declaration, an end tag, or a start tag with its attributes.
_MARKUP = re.compile(
    rb"""<!--.*?-->"""
    rb"""|<!\[CDATA\[.*?\]\]>"""
    rb"""|<\?.*?\?>"""
    rb"""|<!(?:[^>"']|"[^"]*"|'[^']*')*>"""
    rb"""|</(?P<end>[^\s>]+)\s*>"""
    rb"""|<(?P<start>[^\s/>!?]+)(?P<attrs>(?:\s+[^\s=/>]+\s*=\s*(?:"[^"]*"|'[^']*'))*)"""
    rb"""\s*(?P<empty>/?)>""",
    re.DOTALL,
)
_ATTRIBUTE = re.compile(rb"""([^\s=]+)\s*=\s*(?:"([^"]*)"|'([^']*)')""")


@dataclass
class _Span:
    """Where one element of the source is, and what its markup relies on."""

    start: int
    open_end: int
    close_start: int = -1
    end: int = -1
    depth: int = 0
    children: list[int] = field(default_factory=list)
    # The prefixes its own start tag declares, and the in-scope bindings of
    # the prefixes its markup uses but does not declare ("" is the default
    # namespace).
    declares: dict[str, str] = field(default_factory=dict)
    needs: dict[str, str] = field(default_factory=dict)
    tag_needs: dict[str, str] = field(default_factory=dict)

    @property
    def self_closing(self) -> bool:
        return self.close_start == self.open_end == self.end


@dataclass
class _Table:
    """The index of a source; ``ddi_l_native.Table`` has the same methods."""

    data: bytes
    spans: list[_Span]
    # The source parsed as the document was, its elements in document
    # order, and each one's digest.
    elements: list[Element]
    digests: list[bytes]
    by_digest: dict[bytes, list[int]]
    indent: str
    newline: str

    def span(self, index: int) -> _Span:
        return self.spans[index]

    def element(self, index: int) -> Element:
        return self.elements[index]

    def digest(self, index: int) -> bytes:
        return self.digests[index]

    def candidates(self, digest: bytes) -> list[int] | None:
        return self.by_digest.get(digest)

    def canonical_prefixes(self, canonical: dict[str, str]) -> bool:
        """Whether each prefix declared is the one ``canonical`` gives its URI."""
        return all(
            canonical.get(uri, prefix) == prefix
            for span in self.spans
            for prefix, uri in span.declares.items()
            if prefix
        )


class Source:
    """The bytes a document was read from, with a lazily built index."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        self._table: _Table | None = None
        self._built = False

    @classmethod
    def capture(cls, source: Any) -> tuple[Source | None, Any]:
        """``(Source, what to parse)`` for a path or bytes in UTF-8.

        Text, streams and other encodings give ``(None, source)``: they are
        parsed as before and written with a layout.
        """
        try:
            kind, payload = resolve_xml_source(source, require_existing_path=True)
        except (TypeError, OSError):
            return None, source
        if kind == "path":
            data = Path(payload).read_bytes()
            if data.startswith(b"\x1f\x8b"):  # gzip: the parser inflates it
                return None, source
        elif kind == "bytes":
            data = bytes(payload)
        else:
            return None, source
        body = data[len(_UTF8_BOM) :] if data.startswith(_UTF8_BOM) else data
        declared = _DECLARED_ENCODING.match(body)
        if declared and declared.group(1).lower() not in (b"utf-8", b"utf8", b"ascii"):
            return None, source
        return cls(data), data

    def table(self) -> _Table | None:
        """The index of the source, or ``None`` if it cannot be matched."""
        if not self._built:
            self._table = _build_table(self.data)
            self._built = True
        return self._table


# ---- Reading the source ------------------------------------------------------


def _qname_prefix(name: bytes) -> str:
    prefix, colon, _ = name.partition(b":")
    return prefix.decode() if colon else ""


def _scan(data: bytes) -> list[_Span] | None:
    """Every element's span, in document order; ``None`` if unreadable."""
    spans: list[_Span] = []
    open_stack: list[int] = []
    scopes: list[dict[str, str]] = [{"xml": XML_NS}]
    position = data.find(b"<")
    while position != -1:
        match = _MARKUP.match(data, position)
        if match is None:
            return None
        if match.group("end") is not None:
            if not open_stack:
                return None
            span = spans[open_stack.pop()]
            span.close_start, span.end = position, match.end()
            scopes.pop()
        elif match.group("start") is not None:
            span = _Span(start=position, open_end=match.end(), depth=len(open_stack))
            used = [_qname_prefix(match.group("start"))]
            for attribute in _ATTRIBUTE.finditer(match.group("attrs")):
                name = attribute.group(1)
                value = (
                    attribute.group(2)
                    if attribute.group(2) is not None
                    else (attribute.group(3))
                )
                if name == b"xmlns":
                    span.declares[""] = _unescape(value)
                elif name.startswith(b"xmlns:"):
                    span.declares[name[6:].decode()] = _unescape(value)
                elif b":" in name:
                    used.append(_qname_prefix(name))
            scope = {**scopes[-1], **span.declares}
            span.tag_needs = {
                prefix: scope.get(prefix, "")
                for prefix in used
                if prefix not in span.declares and prefix != "xml"
            }
            if open_stack:
                spans[open_stack[-1]].children.append(len(spans))
            spans.append(span)
            if match.group("empty"):
                span.close_start = span.end = match.end()
            else:
                open_stack.append(len(spans) - 1)
                scopes.append(scope)
        position = data.find(b"<", match.end())
    if open_stack or not spans:
        return None
    # What a subtree relies on: its own tags' needs plus its children's,
    # less what it declares itself.
    for span in reversed(spans):
        needs = dict(span.tag_needs)
        for child in span.children:
            for prefix, uri in spans[child].needs.items():
                if prefix not in span.declares:
                    needs.setdefault(prefix, uri)
        span.needs = needs
    return spans


def _unescape(value: bytes) -> str:
    text = value.decode("utf-8")
    if "&" not in text:
        return text
    from html import unescape

    return unescape(text)


def _layout(data: bytes, spans: list[_Span]) -> tuple[str, str]:
    """The file's newline and indentation unit, from its first nested child."""
    for span in spans:
        if span.depth == 1:
            parent_open = spans[0].open_end
            gap = data[parent_open : span.start].decode("utf-8", "replace")
            newline = "\r\n" if "\r\n" in gap else "\n"
            indent = gap.rpartition("\n")[2]
            if indent and not indent.strip():
                return newline, indent
            return newline, "  "
    return "\n", "  "


def _elements(root: Element) -> list[Element]:
    return [node for node in root.iter() if isinstance(node.tag, str)]


def _build_table(data: bytes) -> Any:
    if NATIVE:
        return _native_table(data)
    spans = _scan(data)
    if spans is None:
        return None
    root = parse_xml(io.BytesIO(data))
    elements = _elements(root)
    if len(elements) != len(spans):
        return None
    found = _digests(root)
    digests = [found[id(element)] for element in elements]
    by_digest: dict[bytes, list[int]] = {}
    for index, digest in enumerate(digests):
        by_digest.setdefault(digest, []).append(index)
    newline, indent = _layout(data, spans)
    return _Table(data, spans, elements, digests, by_digest, indent, newline)


def _native_table(data: bytes) -> Any:
    """The native index: spans from the parser, digests cached on the tree."""
    try:
        _root, index = parse_indexed(data)
    except PARSER_ERRORS:
        return None
    return _native.Table(index)


# ---- Content digests ---------------------------------------------------------


def _digests(root: Element) -> dict[int, bytes]:
    """A digest of each element's content, keyed by ``id``.

    The content is the tag, the attributes, the text, and each child with its
    tail; an element's own tail is its parent's. Every element stays in the
    list until the end, so its ``id`` stays its own (lxml makes a new Python
    object for an element nothing refers to).
    """
    elements = list(root.iter())
    found: dict[int, bytes] = {}
    # In reverse document order every child comes before its parent.
    for node in reversed(elements):
        if not isinstance(node.tag, str):
            continue
        digest = hashlib.blake2b(digest_size=16)
        digest.update(node.tag.encode())
        for name, value in sorted(node.attrib.items()):
            digest.update(b"\x01" + name.encode() + b"\x02" + value.encode())
        digest.update(b"\x03" + _text_bytes(node.text))
        for child in node:
            if isinstance(child.tag, str):
                digest.update(b"\x04" + found[id(child)])
            else:  # a comment or processing instruction (lxml only)
                digest.update(b"\x05" + _text_bytes(child.text))
            digest.update(b"\x06" + _text_bytes(child.tail))
        found[id(node)] = digest.digest()
    return found


def _text_bytes(text: str | None) -> bytes:
    return b"\x00" if text is None else text.encode()


# ---- Layout profiles ------------------------------------------------------------


def _escape_text(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\r", "&#13;")
    )


def _escape_attribute(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("\t", "&#9;")
        .replace("\n", "&#10;")
        .replace("\r", "&#13;")
    )


_CANONICAL_PREFIXES = {uri: prefix for prefix, uri in DEFAULT_NSMAP.items() if prefix}


class _DefaultProfile:
    """This library's pretty-printing, with the file's newline and indent."""

    def __init__(self, newline: str, indent: str) -> None:
        self.newline = newline
        self.indent = indent

    def gap(self, depth: int, element: Element | None = None) -> str:
        """What goes before child ``element`` at ``depth``.

        With no ``element``, what goes before an end tag at ``depth``.
        """
        return self.newline + self.indent * depth

    def text(self, value: str) -> str:
        return _escape_text(value)

    def empty(self, name: str, open_tag: str, element: Element) -> str:
        return open_tag + "/>"

    def _name(
        self,
        tag: str,
        element: Element | None,
        scope: dict[str, str],
        declared: dict[str, str],
        *,
        attribute: bool = False,
    ) -> str:
        if not tag.startswith("{"):
            return tag
        uri, _, local = tag[1:].partition("}")
        if uri == XML_NS:
            return f"xml:{local}"
        if not attribute and scope.get("") == uri:
            return local
        for prefix, bound in scope.items():
            if prefix and bound == uri:
                return f"{prefix}:{local}"
        preferred = getattr(element, "prefix", None) if element is not None else None
        prefix = preferred or _CANONICAL_PREFIXES.get(uri) or "ns0"
        index = 0
        while prefix in scope or prefix == "xml":
            prefix = f"ns{index}"
            index += 1
        scope[prefix] = uri
        declared[prefix] = uri
        return f"{prefix}:{local}"

    def open_tag(
        self, element: Element, scope: dict[str, str]
    ) -> tuple[str, str, dict[str, str]]:
        """``(name, "<name attributes", inner scope)`` without the ``>``."""
        inner = dict(scope)
        declared: dict[str, str] = {}
        name = self._name(element.tag, element, inner, declared)
        attributes = [
            f"{self._name(key, None, inner, declared, attribute=True)}"
            f'="{_escape_attribute(value)}"'
            for key, value in element.attrib.items()
        ]
        declarations = [
            f'xmlns:{prefix}="{_escape_attribute(uri)}"'
            for prefix, uri in declared.items()
        ]
        parts = [name, *declarations, *attributes]
        return name, "<" + " ".join(parts), inner

    def subtree(self, element: Element, depth: int, scope: dict[str, str]) -> str:
        out: list[str] = []
        self._write(element, depth, scope, out, inline=False)
        return "".join(out)

    def _write(
        self,
        element: Element,
        depth: int,
        scope: dict[str, str],
        out: list[str],
        *,
        inline: bool,
    ) -> None:
        name, open_tag, inner = self.open_tag(element, scope)
        children = list(element)
        if not children:
            if element.text:
                out.append(f"{open_tag}>{_escape_text(element.text)}</{name}>")
            else:
                out.append(self.empty(name, open_tag, element))
            return
        out.append(f"{open_tag}>")
        elements = [child for child in children if isinstance(child.tag, str)]
        mixed = inline or is_mixed_content(element, elements)
        if mixed:
            out.append(_escape_text(element.text or ""))
        for child in children:
            if not mixed:
                out.append(self.gap(depth + 1))
            if isinstance(child.tag, str):
                self._write(child, depth + 1, inner, out, inline=mixed)
            else:
                out.append(_markup(child))
            if mixed:
                out.append(_escape_text(child.tail or ""))
        if not mixed:
            out.append(self.gap(depth))
        out.append(f"</{name}>")


def _markup(node: Element) -> str:
    """A comment or processing instruction as written (lxml only)."""
    target = getattr(node, "target", None)
    if target is not None:
        return f"<?{target} {node.text or ''}?>".replace(" ?>", "?>")
    return f"<!--{node.text or ''}-->"


class _ColecticaProfile(_DefaultProfile):
    """Colectica's layout, for new elements in a ``FragmentInstance``."""

    def __init__(self, root: Element) -> None:
        from .colectica import _INDENT, _Writer
        from .constants import get_namespace_set
        from .schema_loader._versions import (
            detect_version_from_element,
            normalize_version,
        )

        super().__init__("\n", _INDENT)
        version = normalize_version(detect_version_from_element(root))
        namespaces = get_namespace_set(version)
        self._reusable = namespaces["REUSABLE_NS"]
        self._fragment = f"{{{namespaces['INSTANCE_NS']}}}Fragment"
        self._writer = _Writer(
            instance_ns=namespaces["INSTANCE_NS"],
            reusable_ns=self._reusable,
            version=version,
        )

    def _fits(self, scope: dict[str, str]) -> bool:
        return scope.get("r") == self._reusable

    @staticmethod
    def _level(depth: int) -> int:
        """Colectica's indentation level for ``depth``.

        A ``<Fragment>`` is at column 0, so what is inside one sits a level
        lower than its depth.
        """
        return depth - 1 if depth >= 2 else depth

    def gap(self, depth: int, element: Element | None = None) -> str:
        if element is not None and element.tag == self._fragment:
            return "\n"
        return "\n" + self.indent * self._level(depth)

    def text(self, value: str) -> str:
        from .colectica import _escape_text as colectica_text

        return colectica_text(value)

    def empty(self, name: str, open_tag: str, element: Element) -> str:
        return self._writer.empty(name, open_tag[1:], element)

    def open_tag(
        self, element: Element, scope: dict[str, str]
    ) -> tuple[str, str, dict[str, str]]:
        if not self._fits(scope):
            return super().open_tag(element, scope)
        name, open_tag, default = self._writer.open_tag(element, scope.get(""))
        inner = dict(scope)
        if default is not None:
            inner[""] = default
        return name, "<" + open_tag, inner

    def subtree(self, element: Element, depth: int, scope: dict[str, str]) -> str:
        if not self._fits(scope):
            return super().subtree(element, depth, scope)
        if element.tag == self._fragment:
            return self._writer.fragment(element)
        level = self._level(depth)
        out: list[str] = []
        self._writer.write(element, depth=level, default_ns=scope.get(""), out=out)
        return "".join(out)[len(self.indent * level) :]


# ---- Writing ------------------------------------------------------------------


class _Writer:
    def __init__(
        self,
        table: _Table,
        profile: _DefaultProfile,
        digest: Callable[[Element], bytes],
    ) -> None:
        self.table = table
        self.data = table.data
        self.profile = profile
        self.digest = digest

    def _copyable(
        self, element: Element, hint: int | None, scope: dict[str, str]
    ) -> int | None:
        candidates = self.table.candidates(self.digest(element))
        if not candidates:
            return None
        ordered: Iterator[int] = iter(candidates)
        if hint is not None and hint in candidates:
            ordered = iter([hint, *candidates])
        for index in ordered:
            needs = self.table.span(index).needs
            if all(scope.get(prefix) == uri for prefix, uri in needs.items()):
                return index
        return None

    def write(
        self,
        element: Element,
        hint: int | None,
        depth: int,
        scope: dict[str, str],
        out: list[str | bytes],
    ) -> None:
        copied = self._copyable(element, hint, scope)
        if copied is not None:
            span = self.table.span(copied)
            out.append(self.data[span.start : span.end])
            return
        original = None
        if hint is not None and self.table.element(hint).tag == element.tag:
            original = hint
        children = [child for child in element if isinstance(child.tag, str)]
        others = len(children) != len(element)  # comments or instructions
        if (
            original is None
            or others
            or is_mixed_content(element, children)
            or self._space_preserved(element)
        ):
            out.append(self.profile.subtree(element, depth, scope))
            return
        self._write_changed(element, original, children, depth, scope, out)

    @staticmethod
    def _space_preserved(element: Element) -> bool:
        return element.get(f"{{{XML_NS}}}space") == "preserve"

    def _write_changed(
        self,
        element: Element,
        original: int,
        children: list[Element],
        depth: int,
        scope: dict[str, str],
        out: list[str | bytes],
    ) -> None:
        span = self.table.span(original)
        before = self.table.element(original)
        kept_open = (
            dict(element.attrib) == dict(before.attrib)
            and not span.self_closing
            and all(scope.get(prefix) == uri for prefix, uri in span.tag_needs.items())
        )
        if kept_open:
            out.append(self.data[span.start : span.open_end])
            inner = {**scope, **span.declares}
            name = None
        else:
            name, open_tag, inner = self.profile.open_tag(element, scope)
            if not children and not element.text:
                out.append(self.profile.empty(name, open_tag, element))
                return
            out.append(open_tag + ">")

        old_children = [child for child in before if isinstance(child.tag, str)]
        if not children:
            if kept_open and element.text == before.text and not old_children:
                out.append(self.data[span.open_end : span.close_start])
            else:
                out.append(self.profile.text(element.text or ""))
        else:
            self._write_children(
                element, before, span, children, old_children, depth, inner, out
            )
        if kept_open:
            out.append(self.data[span.close_start : span.end])
        else:
            out.append(f"</{name}>")

    def _write_children(
        self,
        element: Element,
        before: Element,
        span: _Span,
        children: list[Element],
        old_children: list[Element],
        depth: int,
        scope: dict[str, str],
        out: list[str | bytes],
    ) -> None:
        old_spans = span.children
        table_digests = [self.table.digest(index) for index in old_spans]
        current = [self.digest(child) for child in children]
        aligned: list[int | None] = [None] * len(children)
        matcher = SequenceMatcher(None, current, table_digests, autojunk=False)
        for kind, i1, i2, j1, j2 in matcher.get_opcodes():
            if kind == "equal":
                for offset in range(i2 - i1):
                    aligned[i1 + offset] = j1 + offset
            elif kind == "replace":
                for new, old in zip(range(i1, i2), range(j1, j2), strict=False):
                    if children[new].tag == old_children[old].tag:
                        aligned[new] = old
        data = self.data
        span_at = self.table.span
        for k, child in enumerate(children):
            j = aligned[k]
            # The gap before the child is kept when it sits after the same
            # neighbour (or opening) as in the source, with the same text.
            if j is None:
                same_gap = False
            elif k == 0:
                same_gap = j == 0 and element.text == before.text
            else:
                previous = aligned[k - 1]
                same_gap = (
                    previous is not None
                    and j == previous + 1
                    and children[k - 1].tail == old_children[previous].tail
                )
            if same_gap:
                assert j is not None
                gap_start = span_at(old_spans[j - 1]).end if j else span.open_end
                out.append(data[gap_start : span_at(old_spans[j]).start])
            else:
                out.append(self.profile.gap(depth + 1, child))
            hint = old_spans[j] if j is not None else None
            self.write(child, hint, depth + 1, scope, out)
        last = aligned[-1]
        if (
            last is not None
            and last == len(old_children) - 1
            and children[-1].tail == old_children[-1].tail
        ):
            out.append(data[span_at(old_spans[-1]).end : span.close_start])
        else:
            out.append(self.profile.gap(depth))


def _canonical_prefixes(table: _Table) -> bool:
    """Whether the source binds each DDI namespace it declares to its own prefix."""
    from .namespaces import NAMESPACE_PREFIXES

    return table.canonical_prefixes(
        {uri: prefix for prefix, uri in NAMESPACE_PREFIXES.items()}
    )


def write(
    root: Element,
    source: Source,
    *,
    colectica: bool,
    whole: bool = True,
    canonical_prefixes: bool = False,
) -> bytes | None:
    """``root`` written with its unchanged parts as ``source`` has them.

    With ``whole``, the file: what comes before and after the root (byte-order
    mark, declaration, comments) as read. Otherwise the root element alone.
    Returns ``None`` when the source cannot be indexed, or, with
    ``canonical_prefixes``, when it binds a DDI namespace to another prefix
    (``p0``, ``ns1``): the caller then writes the whole document with a
    layout, which renames them.
    """
    table = source.table()
    if table is None:
        return None
    if canonical_prefixes and not _canonical_prefixes(table):
        return None
    profile: _DefaultProfile = (
        _ColecticaProfile(root)
        if colectica
        else _DefaultProfile(table.newline, table.indent)
    )
    elements: list[Element] = []
    if NATIVE:  # the tree caches each element's digest
        digest = _native.digest
    else:
        # Keep every element alive while the digests are keyed by ``id``.
        elements = list(root.iter())
        found = _digests(root)
        digest = lambda element: found[id(element)]  # noqa: E731
    writer = _Writer(table, profile, digest)
    out: list[str | bytes] = []
    hint = 0 if table.element(0).tag == root.tag else None
    writer.write(root, hint, 0, {"xml": XML_NS}, out)
    data = table.data
    first, last = table.span(0).start, table.span(0).end
    body = b"".join(part if isinstance(part, bytes) else part.encode() for part in out)
    del elements
    return data[:first] + body + data[last:] if whole else body
