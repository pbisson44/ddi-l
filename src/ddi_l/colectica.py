r"""Write a ``FragmentInstance`` exactly as Colectica Designer writes one.

Colectica exports items as a DDI ``FragmentInstance``: one ``<Fragment>`` per
item, each item declaring its module's namespace as the default, the reusable
namespace bound to ``r:``, two-space indentation, and a UTF-8 byte-order mark.
A general-purpose serializer produces the same information laid out
differently -- prefixes on every element, namespaces hoisted to the root,
attributes in parse order -- so a file read from Colectica and saved back is a
different file, and a diff against the original is all noise.

:func:`to_colectica_bytes` writes the layout byte for byte. Reading a
Colectica export and writing it back yields the identical file; items built
or edited with the typed models come out as Colectica would have written them.

The conventions, all taken from Colectica's output:

- ``\ufeff<?xml version="1.0" encoding="utf-8"?>``, then ``\n`` line ends
  and no newline after the closing root tag.
- ``<ddi:FragmentInstance xmlns:r=... xmlns:ddi=...>`` and
  ``<ddi:TopLevelReference>`` use the ``ddi:`` prefix; each ``<Fragment>`` sits
  at column 0 and declares ``xmlns:r`` and the instance namespace as default.
- An element outside the namespace in force declares its own as the default,
  written after its other attributes.
- Attributes in schema declaration order, base type first.
- An empty element is ``<a></a>`` when its type holds text and ``<a ... />``
  otherwise.
- Text escapes ``&``, ``<`` and ``>``; attribute values also escape ``"`` and
  write tab, newline and carriage return as character references.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from ._etree import Element, create_element
from .constants import DEFAULT_NSMAP, XML_NS, get_namespace_set
from .models._generated.element_layout import ATTRIBUTE_ORDER, TEXT_CONTENT_TAGS
from .models.base import qn
from .schema_loader._versions import detect_version_from_element, normalize_version

__all__ = [
    "COLECTICA_DECLARATION",
    "apply_colectica_conventions",
    "colectica_timestamp",
    "to_colectica_bytes",
]

COLECTICA_DECLARATION = '﻿<?xml version="1.0" encoding="utf-8"?>\n'
_INDENT = "  "


def colectica_timestamp(moment: datetime | None = None) -> str:
    """Format ``moment`` (default: now) as Colectica writes ``versionDate``.

    .NET's round-trip format: UTC, seven fractional digits, a ``Z`` suffix,
    e.g. ``2025-09-23T18:27:42.3184877Z``.
    """
    value = (moment or datetime.now(UTC)).astimezone(UTC)
    return value.strftime("%Y-%m-%dT%H:%M:%S.%f") + "0Z"


def to_colectica_bytes(root: Element) -> bytes:
    """Serialize a ``FragmentInstance`` in Colectica's exact layout.

    Args:
        root: A ``FragmentInstance`` element (DDI 3.1, 3.2 or 3.3).

    Returns:
        The UTF-8 document, byte-order mark included.

    Raises:
        ValueError: If ``root`` is not a ``FragmentInstance``.
    """
    version = normalize_version(detect_version_from_element(root))
    namespaces = get_namespace_set(version)
    instance_ns = namespaces["INSTANCE_NS"]
    reusable_ns = namespaces["REUSABLE_NS"]
    if root.tag != qn(instance_ns, "FragmentInstance"):
        raise ValueError(
            "The Colectica layout is defined for a FragmentInstance; got "
            f"{root.tag!r}. Use write_ddi() for a DDIInstance."
        )
    writer = _Writer(instance_ns=instance_ns, reusable_ns=reusable_ns, version=version)
    parts: list[str] = [
        COLECTICA_DECLARATION,
        f'<ddi:FragmentInstance xmlns:r="{reusable_ns}" xmlns:ddi="{instance_ns}">',
    ]
    fragment_tag = qn(instance_ns, "Fragment")
    for child in root:
        if not isinstance(child.tag, str):
            continue
        parts.append("\n")
        if child.tag == fragment_tag:
            parts.append(f'<Fragment xmlns:r="{reusable_ns}" xmlns="{instance_ns}">')
            for payload in child:
                if isinstance(payload.tag, str):
                    parts.append("\n")
                    writer.write(payload, depth=1, default_ns=instance_ns, out=parts)
            parts.append("\n</Fragment>")
        else:
            # TopLevelReference and anything else directly under the root keep
            # the ddi: prefix, as the root itself does.
            writer.write(child, depth=1, default_ns=None, out=parts)
    parts.append("\n</ddi:FragmentInstance>")
    return "".join(parts).encode("utf-8")


class _Writer:
    def __init__(self, *, instance_ns: str, reusable_ns: str, version: str) -> None:
        self._instance_ns = instance_ns
        self._reusable_ns = reusable_ns
        # The layout tables are keyed by DDI 3.3 tags; earlier versions differ
        # only in the namespace suffix for the elements both define.
        self._suffix = "3_" + version.split(".")[1]
        self._prefixes = {
            uri: prefix for prefix, uri in DEFAULT_NSMAP.items() if prefix
        }

    def _layout_tag(self, tag: str) -> str:
        if self._suffix == "3_3":
            return tag
        return tag.replace(f":{self._suffix}}}", ":3_3}")

    def _name(self, tag: str, default_ns: str | None) -> tuple[str, str | None]:
        """Return the written name and the namespace to declare as default."""
        namespace, _, local = tag[1:].partition("}")
        if namespace == self._reusable_ns:
            return f"r:{local}", None
        if default_ns is None and namespace == self._instance_ns:
            return f"ddi:{local}", None
        if namespace == default_ns:
            return local, None
        return local, namespace

    def _attributes(self, element: Element, declared: dict[str, str]) -> list[str]:
        order = ATTRIBUTE_ORDER.get(self._layout_tag(element.tag), ())
        rank = {name: index for index, name in enumerate(order)}
        names = sorted(
            element.attrib.keys(), key=lambda name: rank.get(name, len(rank))
        )
        written: list[str] = []
        for name in names:
            value = _escape_attribute(element.attrib[name])
            if name.startswith("{"):
                namespace, _, local = name[1:].partition("}")
                if namespace == XML_NS:
                    written.append(f'xml:{local}="{value}"')
                    continue
                prefix = self._prefixes.get(namespace) or _unknown_prefix(
                    namespace, declared
                )
                if declared.get(prefix) != namespace:
                    declared[prefix] = namespace
                written.append(f'{prefix}:{local}="{value}"')
            else:
                written.append(f'{name}="{value}"')
        return written

    def write(
        self,
        element: Element,
        *,
        depth: int,
        default_ns: str | None,
        out: list[str],
        inline: bool = False,
    ) -> None:
        name, new_default = self._name(element.tag, default_ns)
        child_default = new_default or default_ns
        extra_declarations: dict[str, str] = {}
        attributes = self._attributes(element, extra_declarations)
        attributes.extend(
            f'xmlns:{prefix}="{uri}"' for prefix, uri in extra_declarations.items()
        )
        if new_default is not None:
            attributes.append(f'xmlns="{new_default}"')
        open_tag = name if not attributes else f"{name} {' '.join(attributes)}"
        if not inline:
            out.append(_INDENT * depth)

        children = [child for child in element if isinstance(child.tag, str)]
        text = element.text or ""
        if not children:
            if text:
                out.append(f"<{open_tag}>{_escape_text(text)}</{name}>")
            elif self._layout_tag(element.tag) in TEXT_CONTENT_TAGS:
                out.append(f"<{open_tag}></{name}>")
            else:
                out.append(f"<{open_tag} />")
            return

        out.append(f"<{open_tag}>")
        # Mixed content (text beside elements) is written as it stands, without
        # indentation, as an XmlWriter does once it has written text.
        mixed = (
            inline
            or bool(text.strip())
            or any((child.tail or "").strip() for child in children)
        )
        if mixed:
            out.append(_escape_text(text))
            for child in children:
                self.write(
                    child,
                    depth=depth + 1,
                    default_ns=child_default,
                    out=out,
                    inline=True,
                )
                out.append(_escape_text(child.tail or ""))
            out.append(f"</{name}>")
            return
        for child in children:
            out.append("\n")
            self.write(child, depth=depth + 1, default_ns=child_default, out=out)
        out.append(f"\n{_INDENT * depth}</{name}>")


def _unknown_prefix(namespace: str, declared: dict[str, str]) -> str:
    """A prefix for an attribute namespace outside DEFAULT_NSMAP.

    The one already declared for ``namespace`` on this element, else the
    first of ``ns0``, ``ns1``, ... not taken, so two foreign namespaces never
    share a prefix.
    """
    for prefix, uri in declared.items():
        if uri == namespace:
            return prefix
    index = 0
    while f"ns{index}" in declared:
        index += 1
    return f"ns{index}"


def _escape_text(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _escape_attribute(value: str) -> str:
    return (
        _escape_text(value)
        .replace('"', "&quot;")
        .replace("\t", "&#x9;")
        .replace("\n", "&#xA;")
        .replace("\r", "&#xD;")
    )


def apply_colectica_conventions(
    items: Iterable[Element],
    *,
    reusable_ns: str,
    version_date: str | None = None,
) -> None:
    """Give items built in code what Colectica writes on every item.

    Only what is missing is added; an item read from a Colectica export
    already has all of it and comes through unchanged.

    - ``isUniversallyUnique="true"`` and a ``versionDate`` (``version_date``,
      or now) on the item.
    - An ``r:URN`` built from its Agency, ID and Version, as its first child.
    - References lose an ``r:URN`` that only restates their Agency, ID and
      Version: Colectica identifies a reference by those three alone.

    Args:
        items: The item elements (the ``<Fragment>`` payloads).
        reusable_ns: The reusable namespace of the items' DDI version.
        version_date: ``versionDate`` for items that have none.
    """
    stamp = version_date or colectica_timestamp()
    urn_tag = qn(reusable_ns, "URN")
    agency_tag = qn(reusable_ns, "Agency")
    id_tag = qn(reusable_ns, "ID")
    version_tag = qn(reusable_ns, "Version")
    type_tag = qn(reusable_ns, "TypeOfObject")

    def canonical(element: Element) -> str | None:
        agency = element.findtext(agency_tag)
        identifier = element.findtext(id_tag)
        version = element.findtext(version_tag)
        if agency and identifier and version:
            return f"urn:ddi:{agency}:{identifier}:{version}"
        return None

    for item in items:
        if item.get("isUniversallyUnique") is None:
            item.set("isUniversallyUnique", "true")
        if item.get("versionDate") is None:
            item.set("versionDate", stamp)
        urn = canonical(item)
        if item.find(urn_tag) is None and urn is not None:
            urn_element = create_element(urn_tag)
            urn_element.text = urn
            item.insert(0, urn_element)
        # A list, not the live iterator: removing a node's child mid-walk
        # makes lxml skip what follows it.
        for node in list(item.iter()):
            if node is item or node.find(type_tag) is None:
                continue
            node_urn = node.find(urn_tag)
            if node_urn is not None and node_urn.text == canonical(node):
                node.remove(node_urn)
