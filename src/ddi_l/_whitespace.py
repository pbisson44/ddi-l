"""Whitespace that is text and whitespace that is layout.

DDI documents are indented, and the indentation between elements is not
content. Mixed content is different: in an ``r:Content`` holding XHTML,
``Kind <b>of</b> <i>pet</i>`` and ``<b>Kind</b> <i>of</i> pet`` each have a
space that is part of the text. Between XHTML blocks (``<p>``, ``<ul>``...)
whitespace is layout again.

A leaf module: the parsers in `ddi_l._etree` and the models both use it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - the annotations are the only use
    from ._etree import Element

XHTML_NS = "http://www.w3.org/1999/xhtml"
_XHTML_PREFIX = f"{{{XHTML_NS}}}"
_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
_XHTML_BREAK = f"{_XHTML_PREFIX}br"

# XHTML elements laid out as blocks: the whitespace between them is layout.
XHTML_BLOCKS = frozenset(
    f"{_XHTML_PREFIX}{name}"
    for name in (
        "address",
        "blockquote",
        "caption",
        "dd",
        "div",
        "dl",
        "dt",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "li",
        "ol",
        "p",
        "pre",
        "table",
        "tbody",
        "td",
        "tfoot",
        "th",
        "thead",
        "tr",
        "ul",
    )
)


def is_inline_xhtml(tag: object) -> bool:
    """Whether ``tag`` is an XHTML element laid out inline (``<b>``, ``<span>``)."""
    return (
        isinstance(tag, str)
        and tag.startswith(_XHTML_PREFIX)
        and tag not in XHTML_BLOCKS
    )


def is_mixed_content(node: Element, children: list[Element]) -> bool:
    """Text beside the children, or inline XHTML: whitespace there is text."""
    if node.text is not None and node.text.strip():
        return True
    for child in children:
        if child.tail is not None and child.tail.strip():
            return True
        if is_inline_xhtml(child.tag):
            return True
    return False


def without_indentation(element: Element) -> Element:
    """Drop whitespace-only text around child elements (pretty-printing).

    Text of a leaf is content and is kept, even when it is only spaces. So is
    the whitespace of mixed content (text beside the children, or inline
    XHTML), where the space in ``Kind <b>of</b> <i>pet</i>`` is part of the
    text, and of everything under ``xml:space="preserve"``; between XHTML
    blocks (``<p>``, ``<ul>``...) it is layout.
    """
    stack = [(element, False)]
    while stack:
        node, preserve = stack.pop()
        space = node.get(_XML_SPACE) if isinstance(node.tag, str) else None
        if space is not None:
            preserve = space == "preserve"
        children = list(node)
        stack.extend((child, preserve) for child in children)
        if preserve or not children or is_mixed_content(node, children):
            continue
        if node.text is not None and not node.text.strip():
            node.text = None
        for child in children:
            if child.tail is not None and not child.tail.strip():
                child.tail = None
    return element


def may_lose_mixed_space(root: Element) -> bool:
    """Whether a parser dropping blank text could have dropped text here.

    lxml's ``remove_blank_text`` keeps blank text only after text, so a blank
    in an element whose content starts with an XHTML element is dropped, and
    in mixed content (inline XHTML, or text after a block) that blank was
    text: the ``" "`` in ``<b>Kind</b> <i>of</i> pet`` or in
    ``<p>Kind</p> <p>of</p> pet``.
    """
    for node in root.iter():
        if node.text is not None and node.text.strip():
            continue
        children = list(node)
        if any(
            isinstance(child.tag, str) and child.tag.startswith(_XHTML_PREFIX)
            for child in children
        ) and is_mixed_content(node, children):
            return True
    return False


def xhtml_text(element: Element) -> str:
    """The text of ``element``, with XHTML blocks kept apart.

    Inline elements join their text (``<b>Kind</b> of pet`` reads "Kind of
    pet"); a block (``<p>``, ``<li>``...) is separated from the text around it
    (or a ``<br/>``) by a space unless whitespace already does it, so
    ``<p>Dog</p><ul><li>Large</li></ul>`` reads "Dog Large". Comments and
    processing instructions add nothing.
    """
    parts: list[str] = []
    pending = False  # a block ended or began: the next text needs a gap

    def add(text: str | None) -> None:
        nonlocal pending
        if not text:
            return
        if (
            pending
            and parts
            and not parts[-1][-1:].isspace()
            and not text[:1].isspace()
        ):
            parts.append(" ")
        pending = False
        parts.append(text)

    def walk(node: Element, top: bool) -> None:
        nonlocal pending
        block = not top and (node.tag in XHTML_BLOCKS or node.tag == _XHTML_BREAK)
        if block:
            pending = True
        add(node.text)
        for child in node:
            if isinstance(child.tag, str):
                walk(child, False)
            add(child.tail)
        if block:
            pending = True

    walk(element, True)
    return "".join(parts)
