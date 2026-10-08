"""Base classes and utilities for DDI model objects.

This module provides the foundational types used throughout the DDI models:

- MaintainableBase: Base dataclass for all maintainable DDI objects
- Reference: Lightweight representation of DDI references
- InternationalString: Multi-language text content
- Supporting types: CodeValue, UserID, UserAttributePair, VersionRationale

Example:
    >>> from ddi_l.models.base import MaintainableBase, InternationalString
    >>>
    >>> @dataclass
    ... class MyType(MaintainableBase):
    ...     TAG = "{http://example.org}MyType"
    ...     custom_field: str = ""
"""

from __future__ import annotations

import copy
import re
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import (
    ClassVar,
    TypedDict,
    TypeVar,
    cast,
)

from .._etree import Element, create_element
from ..constants import REUSABLE_NS, XML_NS
from ..exceptions import DDIParseError, ModelValidationError
from ..namespaces import canonicalize_prefixes
from ..registry import MaintainableRegistry
from ._generated.label_slots import SCHEMA_NAMESPACES, TAGS_ALLOWING_LABEL

_SERIALIZE_VALIDATION_SUPPRESSED: ContextVar[bool] = ContextVar(
    "_SERIALIZE_VALIDATION_SUPPRESSED", default=False
)


@contextmanager
def suppress_serialize_validation() -> Iterator[None]:
    """Skip model validation in ``to_xml`` for the current context.

    Used by the document facade, which serializes partially built models
    and validates the whole document separately. Context-local, so other
    threads and tasks are unaffected.
    """
    token = _SERIALIZE_VALIDATION_SUPPRESSED.set(True)
    try:
        yield
    finally:
        _SERIALIZE_VALIDATION_SUPPRESSED.reset(token)


def warn_at_caller(warning: Warning) -> None:
    """Issue ``warning`` attributed to the first frame outside ``ddi_l``."""
    import sys
    import warnings
    from types import FrameType

    # stacklevel=1 is this function; 2 is its caller, where the walk starts.
    level = 2
    frame: FrameType | None = sys._getframe(1)
    while frame is not None and frame.f_globals.get("__name__", "").startswith(
        "ddi_l."
    ):
        frame = frame.f_back
        level += 1
    warnings.warn(warning, stacklevel=level)


def should_validate_on_serialize(obj: object) -> bool:
    """Return whether ``obj.to_xml`` should validate the model first."""
    return bool(getattr(obj, "VALIDATE_ON_SERIALIZE", False)) and not (
        _SERIALIZE_VALIDATION_SUPPRESSED.get()
    )


def _reusable_children(container: Element, local_name: str) -> list[Element]:
    """Return ``container``'s ``r:<local_name>`` children in any DDI 3.x version."""
    matches = []
    for child in container:
        tag = child.tag
        if not isinstance(tag, str) or not tag.startswith("{ddi:reusable:"):
            continue
        if tag.rsplit("}", 1)[1] == local_name:
            matches.append(child)
    return matches


def _collect_scheme_labels(element: Element) -> dict[str, list[InternationalString]]:
    """Return the ``r:Label`` text of scheme wrappers directly under ``element``.

    Scheme wrappers are regenerated on serialization, so their labels are
    kept in ``scheme_labels`` to survive a parse and re-serialize.
    """
    label_tag = qn(REUSABLE_NS, "Label")
    labels: dict[str, list[InternationalString]] = {}
    for child in element:
        tag = child.tag
        if not isinstance(tag, str) or tag not in TAGS_ALLOWING_LABEL:
            continue
        local = tag.rsplit("}", 1)[-1]
        if not local.endswith("Scheme"):
            continue
        for container in child.findall(label_tag):
            labels.setdefault(local, []).extend(
                InternationalString.from_container(container)
            )
    return labels


def _first_text(values: object) -> str | None:
    """Return the text of the first InternationalString in ``values``."""
    if isinstance(values, list) and values:
        text = getattr(values[0], "text", None)
        if isinstance(text, str):
            return text
    return None


def _maintainable_repr(self: object) -> str:
    """Concise repr: identification plus the first name and label."""
    parts = [
        f"{field}={getattr(self, field, None)!r}"
        for field in ("agency", "identifier", "version")
        if getattr(self, field, None) is not None
    ]
    name = _first_text(getattr(self, "names", None))
    if name is not None:
        parts.append(f"name={name!r}")
    label = _first_text(getattr(self, "labels", None))
    if label is not None:
        parts.append(f"label={label!r}")
    return f"{type(self).__name__}({', '.join(parts)})"


def _namespace_of(tag: str) -> str | None:
    """Return the namespace URI in a Clark-notation ``tag``, or ``None``."""
    if not tag.startswith("{"):
        return None
    namespace, sep, _ = tag[1:].partition("}")
    return namespace if sep else None


__all__ = [
    "CodeValue",
    "InternationalString",
    "MaintainableBase",
    "MaintainableInitData",
    "Reference",
    "ReferenceWarning",
    "UserAttributePair",
    "UserID",
    "ValidationContext",
    "VersionRationale",
    "apply_other_attributes",
    "build_identification_elements",
    "clone_element",
    "collect_other_attributes",
    "preserve_unrecognized_children",
    "qn",
]

# ============================================================================
# Constants and Patterns
# ============================================================================

_AGENCY_SEGMENT_PATTERN = r"[A-Za-z0-9-]{1,63}"
_ID_SEGMENT_PATTERN = r"[A-Za-z0-9*@$_-]+"
_VERSION_PATTERN = r"[0-9]+(?:\.[0-9]+)*"

_ID_RE = re.compile(rf"^{_ID_SEGMENT_PATTERN}(?:\.{_ID_SEGMENT_PATTERN})*$")
# Mirrors DDI 3.3's ``r:VersionType``, whose XSD restriction is
# ``[0-9]+(\.[0-9]+)*`` -- digits with optional dot-separated levels, any depth.
_VERSION_RE = re.compile(rf"^{_VERSION_PATTERN}$")
_CANONICAL_URN_RE = re.compile(
    rf"^[Uu][Rr][Nn]:[Dd][Dd][Ii]:{_AGENCY_SEGMENT_PATTERN}(?:\.{_AGENCY_SEGMENT_PATTERN})*"
    rf":{_ID_SEGMENT_PATTERN}(?:\.{_ID_SEGMENT_PATTERN})*:{_VERSION_PATTERN}$"
)


# ============================================================================
# Utility Functions
# ============================================================================


def qn(namespace: str, local: str) -> str:
    """Create a Clark-notation qualified name.

    Args:
        namespace: The namespace URI.
        local: The local element/attribute name.

    Returns:
        String in Clark notation: "{namespace}local"
    """
    return f"{{{namespace}}}{local}"


def _get_text(parent: Element, tag: str) -> str | None:
    """Get text content of a child element."""
    child = parent.find(tag)
    return None if child is None else child.text


def _should_copy_nsmap(element: Element) -> dict[str | None, str] | None:
    """Determine if namespace map should be copied during cloning."""
    nsmap = getattr(element, "nsmap", None) or None
    if not nsmap:
        return None

    getparent = getattr(element, "getparent", None)
    if callable(getparent):
        parent = getparent()
        if parent is not None:
            parent_nsmap = getattr(parent, "nsmap", None) or {}
            filtered = {
                prefix: uri
                for prefix, uri in nsmap.items()
                if parent_nsmap.get(prefix) != uri
            }
            return filtered if filtered else None

    return dict(nsmap)


def clone_element(element: Element, *, deep: bool = True) -> Element:
    """Create a copy of an XML element.

    Args:
        element: The XML element to clone.
        deep: If True, recursively clone all children.

    Returns:
        A new Element that is a copy of the input.
    """
    if deep:
        return copy.deepcopy(element)

    attrib: dict[str, str] = dict(element.attrib)
    nsmap = _should_copy_nsmap(element)

    makeelement = getattr(element, "makeelement", None)
    if callable(makeelement):
        if nsmap is not None:
            try:
                clone = makeelement(element.tag, attrib=attrib, nsmap=nsmap)
            except TypeError:
                clone = makeelement(element.tag, attrib)
        else:
            try:
                clone = makeelement(element.tag, attrib=attrib)
            except TypeError:
                clone = makeelement(element.tag, attrib)
    else:
        clone = create_element(element.tag, nsmap=nsmap)
        if attrib:
            clone.attrib.update(attrib)

    clone.text = element.text
    clone.tail = element.tail
    return clone


def preserve_unrecognized_children(
    element: Element, recognized: Iterable[str]
) -> list[Element]:
    """Collect child elements not in the recognized set."""
    recognized_set = set(recognized)
    return [child for child in element if child.tag not in recognized_set]


def collect_other_attributes(element: Element) -> dict[str, str]:
    """Capture an element's attributes for round-trip preservation.

    Value-type wrappers (which are not ``MaintainableBase`` subclasses) call
    this in ``from_xml`` and pair it with :func:`apply_other_attributes` in
    ``to_xml``. Every attribute is captured; :func:`apply_other_attributes`
    re-applies only those the wrapper did not already emit, so mapped
    attributes are never duplicated or clobbered.
    """
    return dict(element.attrib)


def apply_other_attributes(element: Element, other_attributes: dict[str, str]) -> None:
    """Re-apply preserved attributes that the caller has not already set."""
    for name, value in other_attributes.items():
        if element.get(name) is None:
            element.set(name, value)


# ---------------------------------------------------------------------------
# Generic field parsing / emitting helpers for _FIELD_XML_MAP
# ---------------------------------------------------------------------------


def _parse_field_value(
    element: Element,
    xml_tag: str,
    kind: str,
    is_list: bool,
    *,
    typed_class: type | None = None,
) -> object:
    """Parse a field value from *element* using *xml_tag* and *kind*.

    When *typed_class* is provided, children are parsed via
    ``typed_class.from_xml`` regardless of *kind*.
    """
    if typed_class is not None:
        matches = element.findall(xml_tag)
        if is_list:
            return [typed_class.from_xml(m) for m in matches]  # type: ignore[attr-defined]
        return typed_class.from_xml(matches[0]) if matches else None  # type: ignore[attr-defined]

    if kind == "reference":
        matches = element.findall(xml_tag)
        if is_list:
            return [Reference.from_xml(m) for m in matches]
        return Reference.from_xml(matches[0]) if matches else None

    if kind == "intl_string":
        results: list[InternationalString] = []
        for container in element.findall(xml_tag):
            results.extend(InternationalString.from_container(container))
        if is_list:
            return results
        return results[0] if results else None

    if kind == "code_value":
        matches = element.findall(xml_tag)
        if is_list:
            return [CodeValue.from_xml(m) for m in matches]
        return CodeValue.from_xml(matches[0]) if matches else None

    if kind in ("str", "bool", "int", "float"):
        matches = element.findall(xml_tag)
        if is_list:
            return [_convert_text(m.text, kind) for m in matches]
        if matches:
            return _convert_text(matches[0].text, kind)
        return None

    # "element" — raw XML
    matches = element.findall(xml_tag)
    if is_list:
        return [clone_element(m) for m in matches]
    return clone_element(matches[0]) if matches else None


def _emit_typed_or_raw(item: object) -> Element:
    """Emit an item that may be a typed object (with to_xml) or a raw Element."""
    if hasattr(item, "to_xml"):
        return item.to_xml()
    return clone_element(cast(Element, item))


def _emit_field_value(
    parent: Element,
    value: object,
    xml_tag: str,
    kind: str,
    is_list: bool,
    *,
    is_typed: bool = False,
) -> None:
    """Append serialised XML children to *parent* for a field value.

    When *is_typed* is True and *kind* is ``"element"``, items are serialized
    via their ``to_xml()`` method instead of raw Element cloning.
    """
    if value is None:
        return
    if is_list and not value:
        return

    items = value if is_list else [value]

    # Extract local name (strip namespace) for to_xml calls that need it
    local_name = xml_tag.split("}")[-1] if "}" in xml_tag else xml_tag
    # Extract namespace
    ns = xml_tag[1 : xml_tag.index("}")] if xml_tag.startswith("{") else None

    for item in items:  # type: ignore[attr-defined]
        if is_typed:
            parent.append(item.to_xml())
        elif kind == "reference":
            parent.append(item.to_xml(local_name, namespace=ns))
        elif kind == "intl_string":
            container = create_element(xml_tag)
            container.append(item.to_child())
            parent.append(container)
        elif kind == "code_value":
            # Accept a plain string for a coded field (``file_format="text/csv"``)
            # and use it as the code's text.
            if isinstance(item, str):
                item = CodeValue(text=item)
            parent.append(item.to_xml(local_name, namespace=ns))
        elif kind in ("str", "bool", "int", "float"):
            el = create_element(xml_tag)
            el.text = _format_text(item, kind)
            parent.append(el)
        else:
            # "element" -- raw XML. Simple-content types (``DelimiterType``,
            # ``OneCharStringType``) also accept a plain string, written as the
            # element's text; parsing it back yields an Element.
            if isinstance(item, str):
                el = create_element(xml_tag)
                el.text = item
                parent.append(el)
            else:
                parent.append(clone_element(item))


def _convert_text(text: str | None, kind: str) -> object:
    """Convert XML text content to a Python value."""
    if text is None:
        return None
    if kind == "bool":
        return text.strip().lower() in ("true", "1")
    if kind == "int":
        return int(text.strip())
    if kind == "float":
        return float(text.strip())
    return text.strip() if text else ""


def _format_text(value: object, kind: str) -> str:
    """Format a Python value as XML text content."""
    if kind == "bool":
        return "true" if value else "false"
    if kind == "float" and isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def build_identification_elements(
    *,
    agency: str | None = None,
    identifier: str | None = None,
    version: str | None = None,
    namespace: str = REUSABLE_NS,
) -> list[Element]:
    """Create standard DDI identification child elements in ``namespace``."""
    elements: list[Element] = []

    if agency:
        agency_el = create_element(qn(namespace, "Agency"))
        agency_el.text = agency
        elements.append(agency_el)

    if identifier:
        id_el = create_element(qn(namespace, "ID"))
        id_el.text = identifier
        elements.append(id_el)

    if version:
        version_el = create_element(qn(namespace, "Version"))
        version_el.text = version
        elements.append(version_el)

    return elements


# ============================================================================
# Supporting Data Classes
# ============================================================================


@dataclass
class InternationalString:
    """Multi-language text content for DDI elements.

    Attributes:
        text: The string content.
        lang: ISO 639 language code (e.g., "en", "fr").
        is_translated: Whether this is a translation.
        child_tag: XML tag name when serializing.
    """

    text: str = ""
    lang: str | None = None
    is_translated: bool | None = None
    is_plain_text: bool | None = None
    translation_source_language: str | None = None
    translation_date: str | None = None
    child_tag: str = "Content"

    def __repr__(self) -> str:
        if self.lang is None:
            return f"InternationalString({self.text!r})"
        return f"InternationalString({self.text!r}, lang={self.lang!r})"

    @classmethod
    def from_container(cls, container: Element) -> list[InternationalString]:
        """Parse InternationalStrings from a container element."""
        results: list[InternationalString] = []

        if container.text and container.text.strip():
            lang = container.get(qn(XML_NS, "lang"))
            is_plain_text = None
            is_plain_raw = container.get("isPlainText")
            if is_plain_raw is not None:
                is_plain_text = is_plain_raw.lower() == "true"
            results.append(
                cls(text=container.text.strip(), lang=lang, is_plain_text=is_plain_text)
            )

        for child in _reusable_children(container, "Content"):
            text = child.text or ""
            lang = child.get(qn(XML_NS, "lang"))
            is_translated = None
            translated_attr = child.get("isTranslated")
            if translated_attr is not None:
                is_translated = translated_attr.lower() == "true"
            results.append(
                cls(
                    text=text,
                    lang=lang,
                    is_translated=is_translated,
                    translation_source_language=child.get("translationSourceLanguage"),
                    translation_date=child.get("translationDate"),
                    child_tag="Content",
                )
            )

        for child in _reusable_children(container, "String"):
            text = child.text or ""
            lang = child.get(qn(XML_NS, "lang"))
            results.append(cls(text=text, lang=lang, child_tag="String"))

        return results

    def to_child(self, child_tag: str | None = None) -> Element:
        """Create a child element containing this text."""
        tag = child_tag or self.child_tag
        element = create_element(qn(REUSABLE_NS, tag))
        element.text = self.text

        if self.lang:
            element.set(qn(XML_NS, "lang"), self.lang)
        if self.is_translated is not None:
            element.set("isTranslated", "true" if self.is_translated else "false")
        if self.translation_source_language:
            element.set("translationSourceLanguage", self.translation_source_language)
        if self.translation_date:
            element.set("translationDate", self.translation_date)

        return element

    def to_element(self, tag: str) -> Element:
        """Create a container element with this text as child."""
        container = create_element(tag)
        container.append(self.to_child())
        return container


@dataclass
class CodeValue:
    """Representation of coded values from controlled vocabularies."""

    text: str = ""
    controlled_vocabulary_id: str | None = None
    controlled_vocabulary_name: str | None = None
    controlled_vocabulary_agency_name: str | None = None
    controlled_vocabulary_version_id: str | None = None
    other_value: str | None = None
    controlled_vocabulary_urn: str | None = None
    controlled_vocabulary_scheme_urn: str | None = None

    @classmethod
    def from_xml(cls, element: Element) -> CodeValue:
        """Parse a CodeValue from XML."""
        return cls(
            text=element.text or "",
            controlled_vocabulary_id=element.get("controlledVocabularyID"),
            controlled_vocabulary_name=element.get("controlledVocabularyName"),
            controlled_vocabulary_agency_name=element.get(
                "controlledVocabularyAgencyName"
            ),
            controlled_vocabulary_version_id=element.get(
                "controlledVocabularyVersionID"
            ),
            other_value=element.get("otherValue"),
            controlled_vocabulary_urn=element.get("controlledVocabularyURN"),
            controlled_vocabulary_scheme_urn=element.get(
                "controlledVocabularySchemeURN"
            ),
        )

    def to_xml(self, tag: str, *, namespace: str | None = None) -> Element:
        """Serialize to XML element."""
        full_tag = qn(namespace or REUSABLE_NS, tag)
        element = create_element(full_tag)
        element.text = self.text

        if self.controlled_vocabulary_id:
            element.set("controlledVocabularyID", self.controlled_vocabulary_id)
        if self.controlled_vocabulary_name:
            element.set("controlledVocabularyName", self.controlled_vocabulary_name)
        if self.controlled_vocabulary_agency_name:
            element.set(
                "controlledVocabularyAgencyName", self.controlled_vocabulary_agency_name
            )
        if self.controlled_vocabulary_version_id:
            element.set(
                "controlledVocabularyVersionID", self.controlled_vocabulary_version_id
            )
        if self.other_value:
            element.set("otherValue", self.other_value)
        if self.controlled_vocabulary_urn:
            element.set("controlledVocabularyURN", self.controlled_vocabulary_urn)
        if self.controlled_vocabulary_scheme_urn:
            element.set(
                "controlledVocabularySchemeURN", self.controlled_vocabulary_scheme_urn
            )

        return element


@dataclass
class Reference:
    """Lightweight representation of DDI reference elements."""

    type_of_object: str | None = None
    urn: str | None = None
    agency: str | None = None
    identifier: str | None = None
    version: str | None = None
    _auto_identifier: str | None = field(default=None, repr=False, compare=False)

    @staticmethod
    def _is_allowed_urn(urn: str) -> bool:
        return bool(_CANONICAL_URN_RE.fullmatch(urn))

    def _canonical_urn(self) -> str | None:
        if self.agency and self.identifier and self.version:
            return f"urn:ddi:{self.agency}:{self.identifier}:{self.version}"
        return None

    @classmethod
    def from_xml(cls, element: Element) -> Reference:
        """Parse a Reference from XML."""
        return cls(
            urn=_get_text(element, qn(REUSABLE_NS, "URN")),
            agency=_get_text(element, qn(REUSABLE_NS, "Agency")),
            identifier=_get_text(element, qn(REUSABLE_NS, "ID")),
            version=_get_text(element, qn(REUSABLE_NS, "Version")),
            type_of_object=_get_text(element, qn(REUSABLE_NS, "TypeOfObject")),
        )

    def to_xml(self, tag: str, *, namespace: str | None = None) -> Element:
        """Serialize to XML element."""
        element = create_element(qn(namespace or REUSABLE_NS, tag))

        urn_value: str | None = None
        canonical_urn = self._canonical_urn()
        if canonical_urn:
            if self.urn and self._is_allowed_urn(self.urn):
                urn_value = self.urn
            else:
                urn_value = canonical_urn
        elif self.urn and self._is_allowed_urn(self.urn):
            urn_value = self.urn

        if urn_value:
            urn_el = create_element(qn(REUSABLE_NS, "URN"))
            urn_el.text = urn_value
            element.append(urn_el)

        for child in build_identification_elements(
            agency=self.agency,
            identifier=self.identifier,
            version=self.version,
        ):
            element.append(child)

        if self.type_of_object:
            type_el = create_element(qn(REUSABLE_NS, "TypeOfObject"))
            type_el.text = self.type_of_object
            element.append(type_el)

        return element

    def matches(self, other: Reference) -> bool:
        """Check if this reference points to the same target as another."""
        if self.urn and other.urn:
            return self.urn.lower() == other.urn.lower()
        return (
            self.agency == other.agency
            and self.identifier == other.identifier
            and self.version == other.version
        )


@dataclass
class UserID:
    """External identifier for a DDI object."""

    value: str | None = None
    type_of_user_id: str | None = None
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "UserID")

    @classmethod
    def from_xml(cls, element: Element) -> UserID:
        if element.tag != cls.TAG:
            raise DDIParseError.tag_mismatch(cls.TAG, element.tag, element)
        return cls(
            value=element.text or None,
            type_of_user_id=element.get("typeOfUserID"),
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.type_of_user_id:
            element.set("typeOfUserID", self.type_of_user_id)
        if self.value is not None:
            element.text = self.value
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class UserAttributePair:
    """Custom key-value metadata for DDI objects."""

    key: str | None = None
    value: str | None = None
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "UserAttributePair")

    @classmethod
    def from_xml(cls, element: Element) -> UserAttributePair:
        if element.tag != cls.TAG:
            raise DDIParseError.tag_mismatch(cls.TAG, element.tag, element)
        key_el = element.find(qn(REUSABLE_NS, "AttributeKey"))
        value_el = element.find(qn(REUSABLE_NS, "AttributeValue"))
        return cls(
            key=key_el.text if key_el is not None else None,
            value=value_el.text if value_el is not None else None,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.key is not None:
            key_el = create_element(qn(REUSABLE_NS, "AttributeKey"))
            key_el.text = self.key
            element.append(key_el)
        if self.value is not None:
            value_el = create_element(qn(REUSABLE_NS, "AttributeValue"))
            value_el.text = self.value
            element.append(value_el)
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class VersionRationale:
    """Explanation for version changes."""

    descriptions: list[InternationalString] = field(default_factory=list)
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "VersionRationale")

    @classmethod
    def from_xml(cls, element: Element) -> VersionRationale:
        if element.tag != cls.TAG:
            raise DDIParseError.tag_mismatch(cls.TAG, element.tag, element)
        recognized = {qn(REUSABLE_NS, "RationaleDescription")}
        descriptions: list[InternationalString] = []
        for container in element.findall(qn(REUSABLE_NS, "RationaleDescription")):
            descriptions.extend(InternationalString.from_container(container))
        extras = preserve_unrecognized_children(element, recognized)
        return cls(
            descriptions=descriptions,
            other_elements=extras,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        for description in self.descriptions:
            container = create_element(qn(REUSABLE_NS, "RationaleDescription"))
            # RationaleDescription is an InternationalStringType in every
            # supported schema, so its children are r:String, never the
            # r:Content that InternationalString defaults to.
            container.append(description.to_child("String"))
            element.append(container)
        for child in self.other_elements:
            element.append(clone_element(child))
        apply_other_attributes(element, self.other_attributes)
        return element


# ============================================================================
# Type Definitions
# ============================================================================


class MaintainableInitData(TypedDict, total=False):
    """Initialization data extracted from a maintainable XML fragment."""

    urn: str | None
    agency: str | None
    identifier: str | None
    version: str | None
    labels: list[InternationalString]
    descriptions: list[InternationalString]
    user_ids: list[UserID]
    user_attribute_pairs: list[UserAttributePair]
    version_responsibility: str | None
    version_responsibility_references: list[Element]
    version_rationales: list[VersionRationale]
    based_on_object: Element | None
    related_other_material_references: list[Element]
    notes: list[Element]
    software_elements: list[Element]
    metadata_quality_elements: list[Element]
    other_elements: list[Element]
    other_attributes: dict[str, str]
    scheme_labels: dict[str, list[InternationalString]]
    _nsmap_override: dict[str | None, str] | None


# ============================================================================
# MaintainableBase
# ============================================================================

T = TypeVar("T", bound="MaintainableBase")


@dataclass
class MaintainableBase:
    """Base dataclass for all maintainable DDI structures.

    MaintainableBase provides the common foundation for all DDI maintainable
    types, including identification, labeling, and XML serialization.

    Subclasses must define a TAG class variable with the Clark-notation
    tag name for the element type.

    Attributes:
        urn: Full URN identifier (alternative to agency/id/version).
        agency: Agency responsible for this object.
        identifier: Unique identifier within the agency.
        version: Version string (e.g., "1.0", "2.1.3").
        labels: Human-readable labels in multiple languages.
        descriptions: Detailed descriptions in multiple languages.
        other_elements: Unrecognized XML preserved for round-tripping.

    Class Attributes:
        TAG: Clark-notation tag for this element type (required).
        NSMAP: Default namespace bindings for serialization.
        ALLOW_LABELS: Whether this type supports labels.
        VALIDATE_ON_SERIALIZE: Whether to validate before serialization.

    Example:
        >>> @dataclass
        ... class Concept(MaintainableBase):
        ...     TAG = "{http://ddi.../conceptualcomponent}Concept"
        ...     names: list[InternationalString] = field(default_factory=list)
        ...
        >>> c = Concept(
        ...     agency="example.org",
        ...     identifier="age",
        ...     version="1.0",
        ...     labels=[InternationalString("Age", lang="en")],
        ... )
        >>> xml = c.to_xml()
    """

    urn: str | None = None
    agency: str | None = None
    identifier: str | None = None
    version: str | None = None
    labels: list[InternationalString] = field(default_factory=list)
    descriptions: list[InternationalString] = field(default_factory=list)
    scheme_labels: dict[str, list[InternationalString]] = field(default_factory=dict)
    user_ids: list[UserID] = field(default_factory=list)
    user_attribute_pairs: list[UserAttributePair] = field(default_factory=list)
    version_responsibility: str | None = None
    version_responsibility_references: list[Element] = field(default_factory=list)
    version_rationales: list[VersionRationale] = field(default_factory=list)
    based_on_object: Element | None = None
    related_other_material_references: list[Element] = field(default_factory=list)
    notes: list[Element] = field(default_factory=list)
    software_elements: list[Element] = field(default_factory=list)
    metadata_quality_elements: list[Element] = field(default_factory=list)
    other_elements: list[Element] = field(default_factory=list)
    # Unrecognized XML attributes preserved verbatim for round-tripping (mirrors
    # ``other_elements`` for child elements). Keyed by the attribute's qualified
    # name as it appears in ``element.attrib``.
    other_attributes: dict[str, str] = field(default_factory=dict)
    _nsmap_override: dict[str | None, str] | None = field(
        default=None, repr=False, compare=False
    )
    _auto_identifier: str | None = field(default=None, repr=False, compare=False)
    _inherited_identifier_suffixes: tuple[str, ...] = field(
        default=(), repr=False, compare=False
    )

    # Class-level configuration
    TAG: ClassVar[str]
    NSMAP: ClassVar[dict[str | None, str] | None] = None
    ALLOW_LABELS: ClassVar[bool] = True
    VALIDATE_ON_SERIALIZE: ClassVar[bool] = True
    AUTO_GENERATE_URN: ClassVar[bool] = True

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Register subclass in the maintainable registry."""
        super().__init_subclass__(**kwargs)
        # Set before @dataclass runs, which then keeps it: dataclass never
        # replaces a __repr__ the class defines itself.
        if "__repr__" not in cls.__dict__:
            cls.__repr__ = _maintainable_repr  # type: ignore[method-assign]
        # Skip generated base classes — they exist only to provide field
        # definitions and should never be instantiated directly by the
        # registry.  Hand-written subclasses will register themselves.
        if "._generated." in cls.__module__:
            return
        tag = getattr(cls, "TAG", None)
        if isinstance(tag, str):
            MaintainableRegistry.register_class(tag, cls)
            # Derive label support from the XSD-generated table, so a model
            # never emits an r:Label its content model forbids. Tags outside the
            # DDI 3.3 namespaces (downstream subclasses) keep their own flag.
            if _namespace_of(tag) in SCHEMA_NAMESPACES:
                cls.ALLOW_LABELS = tag in TAGS_ALLOWING_LABEL

    # ========== Class Methods ==========

    @classmethod
    def for_tag(cls, tag: str) -> type[MaintainableBase] | None:
        """Return the registered maintainable type for a given tag."""
        return MaintainableRegistry.get(tag)

    @classmethod
    def maintainable_types(cls) -> tuple[type[MaintainableBase], ...]:
        """Return all registered maintainable subclasses."""
        types = MaintainableRegistry.get_all()
        if not types:
            # Ensure models are imported
            import importlib

            importlib.import_module("ddi_l.models")
            types = MaintainableRegistry.get_all()
        return types

    @classmethod
    def _collect_common(
        cls,
        element: Element,
        *,
        recognized_children: Iterable[str] | None = None,
    ) -> MaintainableInitData:
        """Extract common maintainable data from an XML element.

        Args:
            element: XML element to parse.
            recognized_children: Additional tags handled by the subclass.

        Returns:
            Dictionary suitable for passing to __init__.

        Raises:
            DDIParseError: If element tag doesn't match expected.
        """
        if element.tag != cls.TAG:
            raise DDIParseError.tag_mismatch(cls.TAG, element.tag, element)

        _inherited_tags = {
            qn(REUSABLE_NS, "URN"),
            qn(REUSABLE_NS, "Agency"),
            qn(REUSABLE_NS, "ID"),
            qn(REUSABLE_NS, "Version"),
            qn(REUSABLE_NS, "Label"),
            qn(REUSABLE_NS, "Description"),
            qn(REUSABLE_NS, "UserID"),
            qn(REUSABLE_NS, "UserAttributePair"),
            qn(REUSABLE_NS, "VersionResponsibility"),
            qn(REUSABLE_NS, "VersionResponsibilityReference"),
            qn(REUSABLE_NS, "VersionRationale"),
            qn(REUSABLE_NS, "BasedOnObject"),
            qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
            qn(REUSABLE_NS, "Note"),
            qn(REUSABLE_NS, "Software"),
            qn(REUSABLE_NS, "MetadataQuality"),
            qn(REUSABLE_NS, "MaintainableObject"),
        }

        recognized: set[str] = set(_inherited_tags)
        if recognized_children:
            recognized.update(recognized_children)

        labels: list[InternationalString] = []
        if cls.ALLOW_LABELS:
            for container in element.findall(qn(REUSABLE_NS, "Label")):
                labels.extend(InternationalString.from_container(container))

        descriptions: list[InternationalString] = []
        for container in element.findall(qn(REUSABLE_NS, "Description")):
            descriptions.extend(InternationalString.from_container(container))

        extras = preserve_unrecognized_children(element, recognized)

        # Preserve unrecognized attributes verbatim for round-tripping (mirrors
        # ``extras`` for child elements). Covers both the generic engine and
        # hand-written wrappers, which all funnel through ``_collect_common``.
        known_attr_names = {
            attr_name for attr_name, _kind in getattr(cls, "_ATTR_XML_MAP", {}).values()
        }
        other_attributes = {
            name: value
            for name, value in element.attrib.items()
            if name not in known_attr_names
        }

        nsmap_override: dict[str | None, str] | None = None
        if hasattr(element, "nsmap"):
            raw_nsmap = element.nsmap or {}
            nsmap_override = canonicalize_prefixes(raw_nsmap)

        return {
            "urn": _get_text(element, qn(REUSABLE_NS, "URN")),
            "agency": _get_text(element, qn(REUSABLE_NS, "Agency")),
            "identifier": _get_text(element, qn(REUSABLE_NS, "ID")),
            "version": _get_text(element, qn(REUSABLE_NS, "Version")),
            "labels": labels,
            "descriptions": descriptions,
            "other_elements": extras,
            "other_attributes": other_attributes,
            "scheme_labels": _collect_scheme_labels(element),
            "_nsmap_override": nsmap_override,
        }

    @classmethod
    def _parse_inherited_metadata(
        cls,
        element: Element,
    ) -> dict[str, object]:
        """Parse inherited version/identification metadata from XML.

        These elements are defined on the XSD base types
        (IdentifiableType, VersionableType, MaintainableType) and are
        common to all DDI types.
        """
        result: dict[str, object] = {}

        result["user_ids"] = [
            UserID.from_xml(el) for el in element.findall(qn(REUSABLE_NS, "UserID"))
        ]
        result["user_attribute_pairs"] = [
            UserAttributePair.from_xml(el)
            for el in element.findall(qn(REUSABLE_NS, "UserAttributePair"))
        ]
        vr_el = element.find(qn(REUSABLE_NS, "VersionResponsibility"))
        result["version_responsibility"] = vr_el.text if vr_el is not None else None
        result["version_responsibility_references"] = [
            clone_element(el)
            for el in element.findall(qn(REUSABLE_NS, "VersionResponsibilityReference"))
        ]
        result["version_rationales"] = [
            VersionRationale.from_xml(el)
            for el in element.findall(qn(REUSABLE_NS, "VersionRationale"))
        ]
        based_on_el = element.find(qn(REUSABLE_NS, "BasedOnObject"))
        result["based_on_object"] = (
            clone_element(based_on_el) if based_on_el is not None else None
        )
        result["related_other_material_references"] = [
            clone_element(el)
            for el in element.findall(qn(REUSABLE_NS, "RelatedOtherMaterialReference"))
        ]
        result["notes"] = [
            clone_element(el) for el in element.findall(qn(REUSABLE_NS, "Note"))
        ]
        result["software_elements"] = [
            clone_element(el) for el in element.findall(qn(REUSABLE_NS, "Software"))
        ]
        result["metadata_quality_elements"] = [
            clone_element(el)
            for el in element.findall(qn(REUSABLE_NS, "MetadataQuality"))
        ]
        return result

    @classmethod
    def from_xml(cls: type[T], element: Element) -> T:
        """Parse a maintainable from XML.

        When the class defines a ``_FIELD_XML_MAP`` (generated bases),
        fields are parsed automatically.  Hand-written subclasses that
        override this method bypass the generic path entirely.

        Args:
            element: XML element to parse.

        Returns:
            Instance of this maintainable type.
        """
        field_map: dict[str, tuple] = getattr(cls, "_FIELD_XML_MAP", {})
        attr_map: dict[str, tuple] = getattr(cls, "_ATTR_XML_MAP", {})
        typed_children: dict[str, type] = getattr(cls, "_TYPED_CHILDREN", {})

        # Build recognized set from field map tags
        recognized_tags = {entry[0] for entry in field_map.values()}

        kwargs: dict[str, object] = {}
        for field_name, (xml_tag, kind, is_list) in field_map.items():
            kwargs[field_name] = _parse_field_value(
                element,
                xml_tag,
                kind,
                is_list,
                typed_class=typed_children.get(field_name),
            )

        # Parse XML attributes (unrecognized attributes are preserved via
        # ``_collect_common`` below, which populates ``other_attributes``).
        for field_name, (attr_name, attr_kind) in attr_map.items():
            raw = element.get(attr_name)
            if raw is not None:
                kwargs[field_name] = _convert_text(raw, attr_kind)

        data = cls._collect_common(
            element,
            recognized_children=recognized_tags if recognized_tags else None,
        )

        # Parse inherited version/identification metadata
        inherited = cls._parse_inherited_metadata(element)
        kwargs.update(inherited)

        return cls(**kwargs, **data)  # type: ignore[arg-type]

    # ========== Validation ==========

    def validate(self) -> None:
        """Ensure the maintainable is ready for serialization.

        Raises:
            ModelValidationError: If validation fails.
        """
        self._validate_identification()

    def _assert_unique_children(
        self,
        children: Iterable[MaintainableBase],
        *,
        child_label: str = "child",
    ) -> None:
        """Raise if any two children share the same identifier and version.

        Different versions of the same identifier are permitted.

        Args:
            children: Iterable of maintainable children to check.
            child_label: Human-readable label for error messages.

        Raises:
            ModelValidationError: When duplicate identifier/version pairs
                are found.
        """
        seen: dict[tuple, MaintainableBase] = {}
        for child in children:
            ident = child.identifier
            if not ident:
                continue
            key = (ident, child.version)
            if key in seen:
                raise ModelValidationError(
                    f"{type(self).__name__} contains duplicate {child_label} "
                    f"with identifier {ident!r}.",
                    model_type=type(self),
                )
            seen[key] = child

    def validate_references(
        self,
        context: ValidationContext,
    ) -> list[ReferenceWarning]:
        """Check that Reference fields point to objects in *context*.

        Inspects all dataclass fields holding :class:`Reference` values
        (including lists of references).  Subclasses may override to add
        domain-specific checks.

        Args:
            context: The validation context containing known objects.

        Returns:
            List of reference warnings (non-fatal by default).
        """
        import dataclasses as _dc

        warnings: list[ReferenceWarning] = []
        if not _dc.is_dataclass(self):
            return warnings

        for f in _dc.fields(self):
            value = getattr(self, f.name, None)
            if value is None:
                continue
            refs: list[Reference] = []
            if isinstance(value, Reference):
                refs = [value]
            elif isinstance(value, list):
                refs = [v for v in value if isinstance(v, Reference)]
            if not refs:
                continue
            for ref in refs:
                if not context.can_resolve(ref):
                    warnings.append(
                        ReferenceWarning(
                            source_type=type(self).__name__,
                            source_identifier=self.identifier,
                            field_name=f.name,
                            reference=ref,
                            message=(
                                f"{type(self).__name__}.{f.name} references "
                                f"{ref.identifier or ref.urn!r} which is not present "
                                f"in the current document."
                            ),
                        )
                    )
        return warnings

    def validate_tree(
        self,
        context: ValidationContext | None = None,
    ) -> list[ReferenceWarning]:
        """Recursively validate references across the entire object tree.

        Builds a :class:`ValidationContext` from this object (unless one is
        supplied), then walks every :class:`MaintainableBase` descendant and
        collects reference warnings.

        Args:
            context: Pre-built context, or ``None`` to auto-build one.

        Returns:
            Aggregated list of :class:`ReferenceWarning` from all descendants.
        """
        import dataclasses as _dc

        if context is None:
            context = ValidationContext.from_maintainable(self)

        warnings = self.validate_references(context)
        if not _dc.is_dataclass(self):
            return warnings

        for f in _dc.fields(self):
            value = getattr(self, f.name, None)
            if value is None:
                continue
            if isinstance(value, MaintainableBase):
                warnings.extend(value.validate_tree(context))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, MaintainableBase):
                        warnings.extend(item.validate_tree(context))
        return warnings

    @staticmethod
    @contextmanager
    def _labels_last(element: Element) -> Iterator[None]:
        """Re-append ``r:Label`` and ``r:Description`` after the block runs.

        ``_build_base_element`` emits identification, then labels, then
        descriptions, but several DDI types declare their own Name element
        *before* the label (``d:ConstructName`` precedes ``r:Label`` in
        ``SequenceType``, for one). Moving the label and description to the end
        of the block keeps the schema order.
        """
        label_nodes = element.findall(qn(REUSABLE_NS, "Label"))
        description_nodes = element.findall(qn(REUSABLE_NS, "Description"))
        for node in (*label_nodes, *description_nodes):
            element.remove(node)
        try:
            yield
        finally:
            for node in (*label_nodes, *description_nodes):
                element.append(node)

    def _validate_identification(self) -> None:
        """Verify required identification metadata is present."""
        identifier_value = self.identifier

        if identifier_value and not _ID_RE.fullmatch(identifier_value):
            raise ModelValidationError.invalid_value(
                type(self),
                "identifier",
                identifier_value,
                "does not match DDI identifier pattern",
            )

        # DDI 3.3 restricts `r:Version` to ``[0-9]+(\.[0-9]+)*``; check it here
        # rather than at schema validation.
        if self.version and not _VERSION_RE.fullmatch(self.version):
            raise ModelValidationError.invalid_value(
                type(self),
                "version",
                self.version,
                "does not match DDI version pattern (digits separated by dots)",
            )

        if self.urn:
            if not _CANONICAL_URN_RE.fullmatch(self.urn):
                raise ModelValidationError.invalid_value(
                    type(self), "urn", self.urn, "does not match DDI URN pattern"
                )
            return

        missing: list[str] = []
        if not self.agency:
            missing.append("agency")
        if not identifier_value:
            missing.append("identifier")
        if not self.version:
            missing.append("version")

        if missing:
            raise ModelValidationError(
                f"{type(self).__name__} requires "
                f"{', '.join(missing)} when URN is not provided.",
                model_type=type(self),
            )

    # ========== Version Management ==========

    def _increment_version_component(self, component_index: int) -> None:
        """Increment a specific version component."""
        if not self.version:
            raise ModelValidationError(
                f"{type(self).__name__} does not have a version set.",
                model_type=type(self),
            )

        segments = self.version.split(".")
        int_segments: list[int] = []

        for raw in segments:
            if not raw.isdigit():
                raise ModelValidationError.invalid_value(
                    type(self), "version", self.version, f"non-numeric segment '{raw}'"
                )
            int_segments.append(int(raw))

        while len(int_segments) <= component_index:
            int_segments.append(0)

        int_segments[component_index] += 1
        for index in range(component_index + 1, len(int_segments)):
            int_segments[index] = 0

        old_version = self.version
        self.version = ".".join(str(part) for part in int_segments)
        # A DDI URN ends with the version (urn:ddi:agency:id:version). An
        # explicit one read from a file would otherwise keep naming the old
        # version, both in this item's r:URN and in every to_reference().
        if self.urn and self.urn.endswith(f":{old_version}"):
            self.urn = f"{self.urn[: -len(old_version)]}{self.version}"

    def increment_major_version(self) -> None:
        """Increment the major (first) version component."""
        self._increment_version_component(0)

    def increment_minor_version(self) -> None:
        """Increment the minor (second) version component."""
        self._increment_version_component(1)

    def increment_subversion(self) -> None:
        """Increment the patch (third) version component."""
        self._increment_version_component(2)

    # ========== Child Identification Propagation ==========

    def _default_child_suffix(self, base: str, index: int) -> str:
        """Generate a default identifier suffix for a child element.

        The first child (index 0) gets just ``base``; subsequent children
        get ``base-N`` with 1-based numbering starting at 2.

        Args:
            base: Base suffix string (e.g., "question-item").
            index: Zero-based index of the child.

        Returns:
            Suffix string like "question-item" or "question-item-2".
        """
        if index == 0:
            return base
        return f"{base}-{index + 1}"

    def _propagate_child_identification(
        self,
        children: Iterable[MaintainableBase],
        *,
        identifier_suffix_factory: Callable[[int, MaintainableBase], str | None]
        | None = None,
    ) -> None:
        """Propagate this object's identification to child objects lacking their own.

        For children that don't have agency, identifier, or version set,
        this method copies the parent's values and optionally appends a
        generated suffix to make the identifier unique.  Also computes a
        deterministic ``_auto_identifier`` (UUID5) and records the applied
        suffixes in ``_inherited_identifier_suffixes``.

        Args:
            children: Iterable of child maintainable objects.
            identifier_suffix_factory: Optional callable that takes (index, child)
                and returns a suffix string to append to the identifier,
                or None to use the parent's identifier directly.
        """
        from uuid import uuid5

        from ..constants import IDENTIFIER_NAMESPACE

        for index, child in enumerate(children):
            if not isinstance(child, MaintainableBase):
                continue
            if not child.agency and self.agency:
                child.agency = self.agency
            if not child.version and self.version:
                child.version = self.version
            suffix = None
            if not child.identifier and self.identifier:
                if identifier_suffix_factory is not None:
                    suffix = identifier_suffix_factory(index, child)
                if suffix:
                    child.identifier = f"{self.identifier}-{suffix}"
                else:
                    child.identifier = self.identifier

            # Compute deterministic auto-identifier and record suffixes
            if suffix and child.agency and self.identifier:
                seed = f"{child.agency}:{self.identifier}:{suffix}"
                child._auto_identifier = str(uuid5(IDENTIFIER_NAMESPACE, seed))
                child._inherited_identifier_suffixes = (suffix,)

    def _append_child_identification(
        self,
        element: Element,
        *,
        suffix: str | None = None,
    ) -> None:
        """Append identification elements to a child element.

        When a suffix is provided, the resulting identifier is a
        deterministic UUID5 derived from ``agency:base_identifier-suffix``
        so that wrapper scheme elements receive stable unique IDs.

        Args:
            element: The element to append identification elements to.
            suffix: Optional suffix to append to the identifier.
        """
        identifier = getattr(self, "_auto_identifier", None) or self.identifier
        if suffix and identifier:
            from uuid import uuid5

            from ..constants import IDENTIFIER_NAMESPACE

            seed = f"{self.agency}:{identifier}:{suffix}"
            identifier = str(uuid5(IDENTIFIER_NAMESPACE, seed))

        for child in build_identification_elements(
            agency=self.agency,
            identifier=identifier,
            version=self.version,
        ):
            element.append(child)

        self._append_scheme_label(element)

    def _append_scheme_label(self, element: Element) -> None:
        """Append a caller-supplied ``r:Label`` to a generated scheme wrapper.

        Scheme wrappers (``ConceptScheme``, ``QuestionScheme``,
        ``CategoryScheme`` and so on) are created when the containing model is
        serialized; :meth:`set_scheme_label` is how they get a label. Nothing is
        emitted for a scheme the schema gives no ``r:Label`` slot.
        """
        if not self.scheme_labels:
            return
        tag = element.tag
        if not isinstance(tag, str) or tag not in TAGS_ALLOWING_LABEL:
            return
        for label in self.scheme_labels.get(tag.split("}")[-1], ()):
            label_element = create_element(qn(REUSABLE_NS, "Label"))
            label_element.append(label.to_child(child_tag="Content"))
            element.append(label_element)

    def set_scheme_label(
        self,
        scheme: str,
        text: str,
        *,
        lang: str = "en",
    ) -> None:
        """Label a scheme wrapper this model generates when it serializes.

        Args:
            scheme: Local name of the wrapper, e.g. ``"ConceptScheme"`` or
                ``"QuestionScheme"``.
            text: The label text.
            lang: Language code for the label.

        Raises:
            ValueError: If the DDI schema gives ``scheme`` no ``r:Label`` slot,
                which would make the serialized document invalid.
        """
        candidates = {
            candidate
            for candidate in TAGS_ALLOWING_LABEL
            if candidate.split("}")[-1] == scheme
        }
        if not candidates:
            raise ValueError(
                f"DDI 3.3 defines no element named {scheme!r} that accepts an "
                "r:Label, so labelling it would produce an invalid document."
            )
        self.scheme_labels.setdefault(scheme, []).append(
            InternationalString(text=text, lang=lang, child_tag="Content")
        )

    # ========== Serialization ==========

    def _build_base_element(self) -> Element:
        """Create the XML element with identification and metadata."""
        nsmap = self._nsmap_override or self.NSMAP
        element = create_element(self.TAG, nsmap=nsmap)

        # Add identification elements
        if self.urn:
            urn_el = create_element(qn(REUSABLE_NS, "URN"))
            urn_el.text = self.urn
            element.append(urn_el)

        effective_identifier = (
            getattr(self, "_auto_identifier", None) or self.identifier
        )
        for child in build_identification_elements(
            agency=self.agency,
            identifier=effective_identifier,
            version=self.version,
        ):
            element.append(child)

        # Add labels
        if self.ALLOW_LABELS:
            for label in self.labels:
                label_el = create_element(qn(REUSABLE_NS, "Label"))
                label_el.append(label.to_child())
                element.append(label_el)
        elif self.labels:
            # This type's content model has no r:Label slot: warn instead of
            # dropping the caller's labels without notice.
            import warnings as _warnings

            _warnings.warn(
                f"DDI defines no r:Label slot on {type(self).__name__}; the "
                f"{len(self.labels)} label(s) set on it were not serialized. "
                "A StudyUnit, for instance, carries its title in r:Citation.",
                stacklevel=2,
            )

        # Add descriptions (grouped into a single container)
        if self.descriptions:
            desc_el = create_element(qn(REUSABLE_NS, "Description"))
            for desc in self.descriptions:
                desc_el.append(desc.to_child())
            element.append(desc_el)

        # Re-apply preserved unrecognized attributes (mapped attributes are set
        # by the caller afterwards; _set_other_attributes never clobbers them).
        self._set_other_attributes(element)

        return element

    def _reorder_children_by_element_order(self, element: Element) -> None:
        """Sort *element*'s children into the sequence the XSD declares.

        Hand-written ``to_xml`` overrides append children in source order, but
        several DDI types (``CodeListType`` among them) declare their own name
        element *before* ``r:Label``. ``_ELEMENT_ORDER`` records the required
        sequence; the sort is stable, and tags it does not name keep their
        relative order at the end, where preserved unrecognized content belongs.
        """
        order: list[str] = getattr(self, "_ELEMENT_ORDER", [])
        if not order:
            return
        rank = {tag: index for index, tag in enumerate(order)}
        unranked = len(rank)
        children = sorted(element, key=lambda child: rank.get(child.tag, unranked))
        # ElementTree's ``append`` on a child that is already present appends a
        # second reference rather than moving it, so detach everything first.
        for child in list(element):
            element.remove(child)
        for child in children:
            element.append(child)

    def _emit_version_metadata(self, element: Element) -> None:
        """Emit inherited version/identification metadata elements."""
        for uid in self.user_ids:
            element.append(_emit_typed_or_raw(uid))
        for uap in self.user_attribute_pairs:
            element.append(_emit_typed_or_raw(uap))
        if self.version_responsibility:
            vr_el = create_element(qn(REUSABLE_NS, "VersionResponsibility"))
            vr_el.text = self.version_responsibility
            element.append(vr_el)
        for vrr in self.version_responsibility_references:
            element.append(clone_element(vrr))
        for vrat in self.version_rationales:
            element.append(_emit_typed_or_raw(vrat))
        if self.based_on_object is not None:
            element.append(clone_element(self.based_on_object))
        for rom in self.related_other_material_references:
            element.append(clone_element(rom))
        for note in self.notes:
            element.append(clone_element(note))
        for sw in self.software_elements:
            element.append(clone_element(sw))
        for mq in self.metadata_quality_elements:
            element.append(clone_element(mq))

    def _append_other_elements(self, element: Element) -> None:
        """Append preserved unrecognized elements."""
        for child in self.other_elements:
            element.append(clone_element(child))

    def _set_other_attributes(self, element: Element) -> None:
        """Re-apply preserved unrecognized attributes (without clobbering set ones)."""
        for name, value in self.other_attributes.items():
            if element.get(name) is None:
                element.set(name, value)

    def _emit_inherited_tag(self, element: Element, tag: str) -> None:
        """Emit a single inherited element identified by its tag."""
        urn_tag = qn(REUSABLE_NS, "URN")
        agency_tag = qn(REUSABLE_NS, "Agency")
        id_tag = qn(REUSABLE_NS, "ID")
        version_tag = qn(REUSABLE_NS, "Version")
        label_tag = qn(REUSABLE_NS, "Label")
        desc_tag = qn(REUSABLE_NS, "Description")

        if tag == urn_tag:
            if self.urn:
                urn_el = create_element(urn_tag)
                urn_el.text = self.urn
                element.append(urn_el)
        elif tag == agency_tag:
            effective_id = getattr(self, "_auto_identifier", None) or self.identifier
            if self.agency:
                el = create_element(agency_tag)
                el.text = self.agency
                element.append(el)
            if effective_id:
                el = create_element(id_tag)
                el.text = effective_id
                element.append(el)
            if self.version:
                el = create_element(version_tag)
                el.text = self.version
                element.append(el)
        elif tag in (id_tag, version_tag):
            pass
        elif tag == label_tag:
            if self.ALLOW_LABELS:
                for label in self.labels:
                    label_el = create_element(label_tag)
                    label_el.append(label.to_child())
                    element.append(label_el)
        elif tag == desc_tag:
            if self.descriptions:
                desc_el = create_element(desc_tag)
                for desc in self.descriptions:
                    desc_el.append(desc.to_child())
                element.append(desc_el)
        elif tag == qn(REUSABLE_NS, "UserID"):
            for uid in self.user_ids:
                element.append(_emit_typed_or_raw(uid))
        elif tag == qn(REUSABLE_NS, "UserAttributePair"):
            for uap in self.user_attribute_pairs:
                element.append(_emit_typed_or_raw(uap))
        elif tag == qn(REUSABLE_NS, "VersionResponsibility"):
            if self.version_responsibility:
                el = create_element(tag)
                el.text = self.version_responsibility
                element.append(el)
        elif tag == qn(REUSABLE_NS, "VersionResponsibilityReference"):
            for vrr in self.version_responsibility_references:
                element.append(_emit_typed_or_raw(vrr))
        elif tag == qn(REUSABLE_NS, "VersionRationale"):
            for vrat in self.version_rationales:
                element.append(_emit_typed_or_raw(vrat))
        elif tag == qn(REUSABLE_NS, "BasedOnObject"):
            if self.based_on_object is not None:
                element.append(_emit_typed_or_raw(self.based_on_object))
        elif tag == qn(REUSABLE_NS, "RelatedOtherMaterialReference"):
            for rom in self.related_other_material_references:
                element.append(_emit_typed_or_raw(rom))
        elif tag == qn(REUSABLE_NS, "Note"):
            for note in self.notes:
                element.append(_emit_typed_or_raw(note))
        elif tag == qn(REUSABLE_NS, "Software"):
            for sw in self.software_elements:
                element.append(_emit_typed_or_raw(sw))
        elif tag == qn(REUSABLE_NS, "MetadataQuality"):
            for mq in self.metadata_quality_elements:
                element.append(_emit_typed_or_raw(mq))

    def to_xml(self) -> Element:
        """Serialize this maintainable to XML.

        When the class defines ``_ELEMENT_ORDER`` (generated bases), elements
        are emitted in the XSD-declared sequence.  Hand-written subclasses
        that override this method bypass the generic path entirely.

        Returns:
            XML Element representation.

        Raises:
            ModelValidationError: If VALIDATE_ON_SERIALIZE is True and
                validation fails.
        """
        if should_validate_on_serialize(self):
            self.validate()

        element_order: list[str] = getattr(self, "_ELEMENT_ORDER", [])
        field_map: dict[str, tuple] = getattr(self, "_FIELD_XML_MAP", {})
        attr_map: dict[str, tuple] = getattr(self, "_ATTR_XML_MAP", {})
        typed_children: dict[str, type] = getattr(self, "_TYPED_CHILDREN", {})

        if element_order:
            # Order-aware serialization using _ELEMENT_ORDER
            nsmap = self._nsmap_override or self.NSMAP
            element = create_element(self.TAG, nsmap=nsmap)

            # Build reverse map: xml_tag → (field_name, kind, is_list)
            tag_to_field: dict[str, tuple[str, str, bool]] = {}
            for field_name, (xml_tag, kind, is_list) in field_map.items():
                tag_to_field[xml_tag] = (field_name, kind, is_list)

            # Tags handled by the base class
            inherited_tags = {
                qn(REUSABLE_NS, "URN"),
                qn(REUSABLE_NS, "Agency"),
                qn(REUSABLE_NS, "ID"),
                qn(REUSABLE_NS, "Version"),
                qn(REUSABLE_NS, "Label"),
                qn(REUSABLE_NS, "Description"),
                qn(REUSABLE_NS, "UserID"),
                qn(REUSABLE_NS, "UserAttributePair"),
                qn(REUSABLE_NS, "VersionResponsibility"),
                qn(REUSABLE_NS, "VersionResponsibilityReference"),
                qn(REUSABLE_NS, "VersionRationale"),
                qn(REUSABLE_NS, "BasedOnObject"),
                qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
                qn(REUSABLE_NS, "Note"),
                qn(REUSABLE_NS, "Software"),
                qn(REUSABLE_NS, "MetadataQuality"),
                qn(REUSABLE_NS, "MaintainableObject"),
            }

            for tag in element_order:
                if tag in inherited_tags:
                    self._emit_inherited_tag(element, tag)
                elif tag in tag_to_field:
                    field_name, kind, is_list = tag_to_field[tag]
                    value = getattr(self, field_name, None)
                    _emit_field_value(
                        element,
                        value,
                        tag,
                        kind,
                        is_list,
                        is_typed=field_name in typed_children,
                    )

            # Emit attributes
            for field_name, (attr_name, attr_kind) in attr_map.items():
                value = getattr(self, field_name, None)
                if value is not None:
                    element.set(attr_name, _format_text(value, attr_kind))

            self._set_other_attributes(element)
            self._append_other_elements(element)
            return element

        # Models without _ELEMENT_ORDER: emit identification, version metadata,
        # labels, descriptions, the field map, then other_elements.
        nsmap = self._nsmap_override or self.NSMAP
        element = create_element(self.TAG, nsmap=nsmap)

        if self.urn:
            urn_el = create_element(qn(REUSABLE_NS, "URN"))
            urn_el.text = self.urn
            element.append(urn_el)

        effective_identifier = (
            getattr(self, "_auto_identifier", None) or self.identifier
        )
        for child in build_identification_elements(
            agency=self.agency,
            identifier=effective_identifier,
            version=self.version,
        ):
            element.append(child)

        self._emit_version_metadata(element)

        if self.ALLOW_LABELS:
            for label in self.labels:
                label_el = create_element(qn(REUSABLE_NS, "Label"))
                label_el.append(label.to_child())
                element.append(label_el)

        if self.descriptions:
            desc_el = create_element(qn(REUSABLE_NS, "Description"))
            for desc in self.descriptions:
                desc_el.append(desc.to_child())
            element.append(desc_el)

        for field_name, (xml_tag, kind, is_list) in field_map.items():
            value = getattr(self, field_name, None)
            _emit_field_value(
                element,
                value,
                xml_tag,
                kind,
                is_list,
                is_typed=field_name in typed_children,
            )

        for field_name, (attr_name, attr_kind) in attr_map.items():
            value = getattr(self, field_name, None)
            if value is not None:
                element.set(attr_name, _format_text(value, attr_kind))

        self._set_other_attributes(element)
        self._append_other_elements(element)
        return element

    # ========== Utility Methods ==========

    def get_label(self, lang: str = "en") -> str | None:
        """Get label text in the specified language.

        Args:
            lang: Language code to retrieve.

        Returns:
            Label text, or None if not found.
        """
        for label in self.labels:
            if label.lang == lang:
                return label.text
        return self.labels[0].text if self.labels else None

    def get_description(self, lang: str = "en") -> str | None:
        """Get description text in the specified language."""
        for desc in self.descriptions:
            if desc.lang == lang:
                return desc.text
        return self.descriptions[0].text if self.descriptions else None

    def _format_urn(self) -> str | None:
        """Return the canonical URN for this object.

        Prefers the explicit ``urn`` attribute when set; otherwise computes
        the canonical ``urn:ddi:{agency}:{identifier}:{version}`` form.
        """
        if self.urn:
            return self.urn
        if self.agency and self.identifier and self.version:
            return f"urn:ddi:{self.agency}:{self.identifier}:{self.version}"
        return None

    def canonical_urn(self) -> str | None:
        """Compute the canonical URN from identification components."""
        return self._format_urn()

    def to_reference(self) -> Reference:
        """Create a Reference pointing to this maintainable.

        Returns:
            Reference with identification from this object.
        """
        return Reference(
            urn=self.urn or self.canonical_urn(),
            agency=self.agency,
            identifier=self.identifier,
            version=self.version,
            type_of_object=type(self).__name__,
        )

    # ========== Custom Properties ==========

    @property
    def properties(self) -> dict[str, str]:
        """Return custom properties as a key-value mapping.

        Returns:
            dict mapping each ``UserAttributePair`` key to its value.
            Pairs with ``None`` keys are skipped; ``None`` values become
            empty strings.
        """
        return {
            pair.key: (pair.value or "")
            for pair in self.user_attribute_pairs
            if pair.key is not None
        }

    def get_property(self, key: str) -> str | None:
        """Return the value of a custom property.

        Args:
            key: The property key to look up.

        Returns:
            The property value, or ``None`` if not found.
        """
        for pair in self.user_attribute_pairs:
            if pair.key == key:
                return pair.value
        return None

    def set_property(
        self,
        key: str,
        value: str | MaintainableBase | Reference,
    ) -> None:
        """Set a custom property on this item.

        If ``value`` is a :class:`MaintainableBase` or :class:`Reference`,
        the stored value is its URN (useful for linking to a code list or
        other controlled vocabulary).

        Args:
            key: The property key.
            value: A plain string, a maintainable object, or a reference.
        """
        if isinstance(value, MaintainableBase):
            str_value = value._format_urn() or value.identifier or ""
        elif isinstance(value, Reference):
            str_value = value.urn or value._canonical_urn() or value.identifier or ""
        else:
            str_value = value

        for pair in self.user_attribute_pairs:
            if pair.key == key:
                pair.value = str_value
                return
        self.user_attribute_pairs.append(UserAttributePair(key=key, value=str_value))

    def remove_property(self, key: str) -> bool:
        """Remove a custom property by key.

        Args:
            key: The property key to remove.

        Returns:
            True if a property was removed, False if the key was not found.
        """
        for i, pair in enumerate(self.user_attribute_pairs):
            if pair.key == key:
                self.user_attribute_pairs.pop(i)
                return True
        return False

    # ========== Dict Serialization ==========

    def to_dict(self) -> dict:
        """Convert this maintainable to a nested mapping via XML.

        The returned dict is keyed by the Clark-notation tag of this object
        so that :meth:`from_dict` can reconstruct it unambiguously.

        Returns:
            dict: Mapping suitable for JSON serialisation.
        """
        from .. import schema_loader

        xml = self.to_xml()
        inner = schema_loader.to_dict(xml, process_namespaces=True)
        return {self.TAG: inner}

    @classmethod
    def from_dict(cls, data: dict) -> MaintainableBase:
        """Create an instance from its mapping representation.

        Args:
            data: Mapping previously produced by :meth:`to_dict`.  May be
                a tag-wrapped ``{TAG: {...}}`` dict or a flat inner dict.

        Returns:
            A new instance of this class.
        """
        from .. import schema_loader

        element = schema_loader.from_dict(data, process_namespaces=True)
        return cls.from_xml(element)

    # ========== Comparison Helpers ==========

    def equals(
        self,
        other: MaintainableBase,
        *,
        ignore_label_order: bool = False,
        ignore_other_elements_order: bool = False,
    ) -> bool:
        """Compare this maintainable against *other* for structural equality.

        Args:
            other: The maintainable to compare against.
            ignore_label_order: Treat labels as order-independent.
            ignore_other_elements_order: Treat ``other_elements`` as
                order-independent.

        Returns:
            ``True`` when the two instances are structurally identical.
        """
        return not self.diff(
            other,
            ignore_label_order=ignore_label_order,
            ignore_other_elements_order=ignore_other_elements_order,
        )

    def diff(
        self,
        other: MaintainableBase,
        *,
        ignore_label_order: bool = False,
        ignore_other_elements_order: bool = False,
        _prefix: str = "",
    ) -> list[str]:
        """Return a list of human-readable differences against *other*.

        Args:
            other: The maintainable to compare against.
            ignore_label_order: Treat labels as order-independent.
            ignore_other_elements_order: Treat ``other_elements`` as
                order-independent.

        Returns:
            List of difference descriptions; empty when instances are equal.
        """
        import dataclasses as _dc

        if type(self) is not type(other):
            return [
                f"{_prefix}type mismatch: "
                f"{type(self).__name__} vs {type(other).__name__}"
            ]

        if not _dc.is_dataclass(self):
            return [] if self == other else [f"{_prefix}values differ"]

        diffs: list[str] = []
        for f in _dc.fields(self):
            if f.name.startswith("_") or f.name in ("TAG", "NSMAP"):
                continue
            if not f.repr:
                continue
            self_val = getattr(self, f.name, None)
            other_val = getattr(other, f.name, None)

            if (
                ignore_label_order
                and f.name == "labels"
                and isinstance(self_val, list)
                and isinstance(other_val, list)
                and sorted(self_val, key=repr) == sorted(other_val, key=repr)
            ):
                continue

            if (
                ignore_other_elements_order
                and f.name == "other_elements"
                and isinstance(self_val, list)
                and isinstance(other_val, list)
            ):
                self_reprs = sorted(_element_repr(e) for e in self_val)
                other_reprs = sorted(_element_repr(e) for e in other_val)
                if self_reprs == other_reprs:
                    continue

            field_prefix = (
                f"{_prefix}{f.name}" if not _prefix else f"{_prefix}.{f.name}"
            )

            if isinstance(self_val, list) and isinstance(other_val, list):
                if len(self_val) != len(other_val):
                    diffs.append(
                        f"{field_prefix}: length {len(self_val)} vs {len(other_val)}"
                    )
                    continue
                for i, (a, b) in enumerate(zip(self_val, other_val, strict=False)):
                    item_prefix = f"{field_prefix}[{i}]"
                    if isinstance(a, MaintainableBase) and isinstance(
                        b, MaintainableBase
                    ):
                        diffs.extend(
                            a.diff(
                                b,
                                ignore_label_order=ignore_label_order,
                                ignore_other_elements_order=ignore_other_elements_order,
                                _prefix=item_prefix,
                            )
                        )
                    elif a != b:
                        diffs.append(f"{item_prefix}: {a!r} != {b!r}")
            elif isinstance(self_val, MaintainableBase) and isinstance(
                other_val, MaintainableBase
            ):
                diffs.extend(
                    self_val.diff(
                        other_val,
                        ignore_label_order=ignore_label_order,
                        ignore_other_elements_order=ignore_other_elements_order,
                        _prefix=field_prefix,
                    )
                )
            elif self_val != other_val:
                diffs.append(f"{field_prefix}: {self_val!r} != {other_val!r}")

        return diffs

    # Live views of MaintainableRegistry for code that inspects the class.
    _TAG_REGISTRY: ClassVar[dict] = MaintainableRegistry._tag_to_class
    _REGISTERED_TYPES: ClassVar[list] = MaintainableRegistry._registered_types


def _element_repr(el: Element) -> str:
    """Return a sortable string representation of an XML element."""
    from .._etree import tostring

    try:
        return tostring(el)
    except Exception:
        return repr(el)


# ============================================================================
# Validation Context -- cross-reference validation
# ============================================================================


@dataclass
class ReferenceWarning:
    """A non-fatal warning about an unresolvable reference.

    Attributes:
        source_type: Class name of the object containing the reference.
        source_identifier: Identifier of that object.
        field_name: The Python field holding the reference.
        reference: The unresolved :class:`Reference`.
        message: Human-readable description.
    """

    source_type: str
    source_identifier: str | None
    field_name: str
    reference: Reference
    message: str


class ValidationContext:
    """Registry of known objects used to validate references at serialization time.

    Build a context from a top-level maintainable (e.g. ``StudyUnit``)
    and pass it to :meth:`MaintainableBase.validate_references` to
    check that all ``Reference`` fields point to objects that exist
    within the document.

    Example::

        ctx = ValidationContext.from_maintainable(study)
        warnings = study.validate_references(ctx)
        for w in warnings:
            print(w.message)
    """

    def __init__(self) -> None:
        self._by_urn: dict[str, MaintainableBase] = {}
        self._by_key: dict[tuple[str | None, str, str | None], MaintainableBase] = {}
        self._identifiers: set[str] = set()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, obj: MaintainableBase) -> None:
        """Add *obj* to the context so references to it can be resolved."""
        urn = obj._format_urn()
        if urn:
            self._by_urn[urn] = obj
        ident = obj.identifier
        if ident:
            self._by_key[(obj.agency, ident, obj.version)] = obj
            self._identifiers.add(ident)

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def can_resolve(self, ref: Reference) -> bool:
        """Return ``True`` if *ref* can be resolved to a registered object."""
        if ref.urn and ref.urn in self._by_urn:
            return True
        if ref.identifier:
            # Exact match
            key = (ref.agency, ref.identifier, ref.version)
            if key in self._by_key:
                return True
            # Relaxed: identifier-only match (common in DDI fragments)
            if ref.identifier in self._identifiers:
                return True
        return False

    def resolve(self, ref: Reference) -> MaintainableBase | None:
        """Resolve *ref* to a registered object, or ``None``."""
        if ref.urn:
            hit = self._by_urn.get(ref.urn)
            if hit is not None:
                return hit
        if ref.identifier:
            key = (ref.agency, ref.identifier, ref.version)
            hit = self._by_key.get(key)
            if hit is not None:
                return hit
            # Relaxed match by identifier alone
            for k, v in self._by_key.items():
                if k[1] == ref.identifier:
                    return v
        return None

    # ------------------------------------------------------------------
    # Tree walking
    # ------------------------------------------------------------------

    @classmethod
    def from_maintainable(cls, root: MaintainableBase) -> ValidationContext:
        """Build a context by recursively walking *root*.

        Registers every :class:`MaintainableBase` descendant.
        """
        ctx = cls()
        cls._walk(root, ctx)
        return ctx

    @classmethod
    def _walk(cls, obj: MaintainableBase, ctx: ValidationContext) -> None:
        """Recursively register *obj* and all its MaintainableBase children."""
        ctx.register(obj)
        # Walk dataclass fields looking for MaintainableBase children
        import dataclasses as _dc

        if not _dc.is_dataclass(obj):
            return
        for f in _dc.fields(obj):
            value = getattr(obj, f.name, None)
            if value is None:
                continue
            if isinstance(value, MaintainableBase):
                cls._walk(value, ctx)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, MaintainableBase):
                        cls._walk(item, ctx)
