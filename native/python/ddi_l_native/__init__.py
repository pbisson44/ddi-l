"""Native XML core for ddi-l.

``pip install ddi-l`` installs it wherever a compiled wheel exists, and ddi-l
uses it: a hardened parser that builds a tree whose elements behave like
``xml.etree.ElementTree``'s and keep the bytes they were read from.
"""

from collections.abc import MutableMapping

from ._core import (
    Attrib,
    Element,
    Index,
    Schema,
    Span,
    SubElement,
    Table,
    digest,
    parent,
    parse,
    source_position,
    uses_namespace,
)

# An element's attributes are a live mapping, as ``Element.attrib`` is.
MutableMapping.register(Attrib)

__all__ = [
    "Attrib",
    "Element",
    "Index",
    "Schema",
    "Span",
    "SubElement",
    "Table",
    "digest",
    "parent",
    "parse",
    "source_position",
    "uses_namespace",
]
