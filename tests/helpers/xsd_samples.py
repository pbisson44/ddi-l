"""Build schema-valid sample instances of any DDI 3.3 element from the XSDs.

Real exports exist for a handful of item types; the DDI 3.3 ``Fragment`` can
carry 161. :func:`build_sample` walks an element's content model and fills
every optional child and attribute (to a depth limit), so one call exercises
fields a hand-made fixture would skip. ``variant`` rotates which branch of
each ``xs:choice`` is taken and which value an enumeration gets, so a few
variants between them reach every branch near the top of the tree.

Values come from a list of candidates tried against each simple type's own
validator, which satisfies patterns (``r:ID``, ``r:URN``, version numbers)
without knowing them in advance.
"""

from __future__ import annotations

import itertools
from functools import lru_cache
from typing import Any

import xmlschema
from codegen.xsd_introspect import ENTRY_SCHEMA
from xmlschema.validators import (
    XsdAnyElement,
    XsdComplexType,
    XsdElement,
    XsdGroup,
)

from ddi_l._etree import Element, create_element
from ddi_l.constants import XML_NS

# Optional content is filled down to this depth; below it only what the
# schema requires is built, which keeps recursive types (a Sequence inside a
# Sequence) finite.
_OPTIONAL_DEPTH = 4
_REPEAT_DEPTH = 2
_MAX_DEPTH = 12

_XHTML_NS = "http://www.w3.org/1999/xhtml"

_CANDIDATES = (
    "true",
    "x",
    "1",
    "en",
    "2024-01-01",
    "2024-01-01T00:00:00",
    "2024",
    "2024-01",
    "00:00:00",
    "P1D",
    "1.5",
    "http://example.org/x",
    "urn:ddi:example.org:sample-1:1",
    "example.org",
    "AA==",
    "00",
    "1 2",
    "x y",
)


@lru_cache(maxsize=1)
def schema() -> Any:
    """The bundled DDI 3.3 schema set, loaded once."""
    return xmlschema.XMLSchema(str(ENTRY_SCHEMA))


class _Builder:
    def __init__(self, variant: int) -> None:
        self._variant = variant
        self._ids = itertools.count(1)
        self._value_cache: dict[int, list[str]] = {}

    def _pick(self, options: list[Any]) -> Any:
        return options[self._variant % len(options)]

    def _values(self, simple_type: Any) -> list[str]:
        key = id(simple_type)
        if key not in self._value_cache:
            enumeration = getattr(simple_type, "enumeration", None)
            if enumeration:
                values = [str(value) for value in enumeration]
            else:
                values = [v for v in _CANDIDATES if _is_valid(simple_type, v)]
            self._value_cache[key] = values
        return self._value_cache[key]

    def _value(self, simple_type: Any, name: str) -> str | None:
        values = self._values(simple_type)
        if not values:
            return None
        primitive = getattr(
            getattr(simple_type, "primitive_type", None), "local_name", ""
        )
        if name in {"ID", "Alias"} or primitive == "ID":
            candidate = f"sample-{next(self._ids)}"
            if _is_valid(simple_type, candidate):
                return candidate
        return str(self._pick(values))

    def element(self, declaration: XsdElement, depth: int) -> Element | None:
        if declaration.abstract:
            substitutes = sorted(
                (
                    candidate
                    for candidate in schema().maps.substitution_groups.get(
                        declaration.name, ()
                    )
                    if not candidate.abstract
                ),
                key=lambda candidate: candidate.name,
            )
            if not substitutes:
                return None
            declaration = self._pick(substitutes)
        if depth > _MAX_DEPTH:
            return None
        element_type = declaration.type
        if getattr(element_type, "abstract", False):
            # An abstract type needs an xsi:type naming a concrete one; leave
            # such elements out (callers drop them when optional).
            return None
        element = create_element(declaration.name)
        if not isinstance(element_type, XsdComplexType):
            value = self._value(element_type, declaration.local_name)
            if value is None:
                return None
            element.text = value
            return element

        for name, attribute in element_type.attributes.items():
            if not name or attribute.use == "prohibited":
                continue
            if attribute.use != "required" and depth > _OPTIONAL_DEPTH:
                continue
            if attribute.fixed is not None:
                value = str(attribute.fixed)
            else:
                value = self._value(attribute.type, name)
            if value is None:
                if attribute.use == "required":
                    return None
                continue
            element.set(name, value)

        if element_type.has_simple_content():
            value = self._value(element_type.content, declaration.local_name)
            if value is None:
                return None
            element.text = value
            return element
        content = element_type.content
        if isinstance(content, XsdGroup):
            children = self.group(content, depth + 1)
            if children is None:
                return None
            for child in children:
                element.append(child)
        if element_type.mixed and not len(element):
            element.text = "x"
        return element

    def group(self, group: XsdGroup, depth: int) -> list[Element] | None:
        if group.model == "choice":
            options = [p for p in group if not isinstance(p, XsdAnyElement)]
            if not options:
                return []
            start = self._variant % len(options)
            for offset in range(len(options)):
                built = self.particle(options[(start + offset) % len(options)], depth)
                if built is not None:
                    return built
            return None if group.min_occurs else []
        built_all: list[Element] = []
        for particle in group:
            built = self.particle(particle, depth)
            if built is None:
                return None
            built_all.extend(built)
        return built_all

    def particle(self, particle: Any, depth: int) -> list[Element] | None:
        if isinstance(particle, XsdAnyElement):
            return []
        name = getattr(particle, "name", None) or ""
        if name.startswith(f"{{{_XHTML_NS}}}"):
            # Embedded XHTML is opaque markup to every model; text stands in.
            return []
        required = particle.min_occurs
        optional = depth <= _OPTIONAL_DEPTH
        count = max(required, 1 if optional else 0)
        if (
            count
            and depth <= _REPEAT_DEPTH
            and not isinstance(particle, XsdGroup)
            and (particle.max_occurs is None or particle.max_occurs > 1)
        ):
            count = max(count, 2)
        if not count:
            return []
        built: list[Element] = []
        for _ in range(count):
            if isinstance(particle, XsdGroup):
                part = self.group(particle, depth)
                if part is None:
                    return None if required else built
                built.extend(part)
            else:
                node = self.element(particle, depth)
                if node is None:
                    return None if required else built
                built.append(node)
        return built


def _is_valid(simple_type: Any, value: str) -> bool:
    try:
        return bool(simple_type.is_valid(value))
    except (TypeError, ValueError, AttributeError):
        return False


def build_sample(tag: str, *, variant: int = 0) -> Element | None:
    """Return a sample ``tag`` element, or ``None`` if none could be built.

    Args:
        tag: Clark-notation tag of a global DDI 3.3 element.
        variant: Rotates choice branches and enumeration values.
    """
    declaration = schema().maps.elements[tag]
    element = _Builder(variant).element(declaration, 0)
    if element is not None:
        _label_languages(element)
    return element


def _label_languages(element: Element) -> None:
    """Give repeated strings in one container distinct languages.

    Two ``r:Content`` children of one ``r:Label`` that share a language are
    legal but meaningless; distinct languages make the bilingual-container
    case the sample is there to exercise.
    """
    lang = f"{{{XML_NS}}}lang"
    for container in element.iter():
        langs = itertools.cycle(("en", "fr", "de"))
        for child in container:
            if child.get(lang) is not None:
                child.set(lang, next(langs))
