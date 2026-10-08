"""Maintainable wrappers for reusable module content."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import ClassVar

from .._etree import Element, create_element
from ..constants import REUSABLE_NS, XML_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.reusable import (
    InformationClassificationFields,
    ManagedMissingValuesRepresentationFields,
)
from .base import (
    InternationalString,
    Reference,
    clone_element,
    preserve_unrecognized_children,
    qn,
)
from .logicalproduct import (
    CodeRepresentation,
    NumericRepresentation,
    TextRepresentation,
)

__all__ = [
    "InformationClassification",
    "ManagedMissingValuesRepresentation",
]


@contextmanager
def _retagged(element: Element, tag: str) -> Iterator[Element]:
    original = element.tag
    element.tag = tag
    try:
        yield element
    finally:
        element.tag = original


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() == "true"


def _format_bool(value: bool) -> str:
    return "true" if value else "false"


_REFERENCE_CHILDREN = {
    qn(REUSABLE_NS, "URN"),
    qn(REUSABLE_NS, "Agency"),
    qn(REUSABLE_NS, "ID"),
    qn(REUSABLE_NS, "Version"),
    qn(REUSABLE_NS, "TypeOfObject"),
}


def _parse_code_representation(element: Element) -> CodeRepresentation:
    with _retagged(element, CodeRepresentation.TAG) as working:
        return CodeRepresentation.from_xml(working)


def _serialize_code_representation(
    representation: CodeRepresentation, tag: str
) -> Element:
    element = representation.to_xml()
    element.tag = qn(REUSABLE_NS, tag)
    return element


def _parse_numeric_representation(element: Element) -> NumericRepresentation:
    with _retagged(element, NumericRepresentation.TAG) as working:
        return NumericRepresentation.from_xml(working)


def _serialize_numeric_representation(
    representation: NumericRepresentation, tag: str
) -> Element:
    element = representation.to_xml()
    element.tag = qn(REUSABLE_NS, tag)
    return element


def _parse_text_representation(element: Element) -> TextRepresentation:
    with _retagged(element, TextRepresentation.TAG) as working:
        return TextRepresentation.from_xml(working)


def _serialize_text_representation(
    representation: TextRepresentation, tag: str
) -> Element:
    element = representation.to_xml()
    element.tag = qn(REUSABLE_NS, tag)
    return element


@dataclass
class InformationClassification(InformationClassificationFields):
    """Representation of ``r:InformationClassification`` fragments."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "InformationClassification")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")


@dataclass
class ManagedMissingValuesRepresentation(ManagedMissingValuesRepresentationFields):
    """Representation of ``r:ManagedMissingValuesRepresentation`` entries."""

    names: list[InternationalString] = field(default_factory=list)
    missing_code_representations: list[CodeRepresentation] = field(default_factory=list)  # type: ignore[assignment]
    missing_numeric_representations: list[NumericRepresentation] = field(  # type: ignore[assignment]
        default_factory=list
    )
    missing_text_representations: list[TextRepresentation] = field(default_factory=list)  # type: ignore[assignment]
    processing_instruction_reference: Reference | None = None
    processing_instruction_reference_extras: list[Element] = field(default_factory=list)
    blank_is_missing_value: bool | None = None
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ManagedMissingValuesRepresentation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    _ALLOWED_OTHER_ATTRIBUTES: ClassVar[set[str]] = {
        "inheritanceAction",
        "objectSource",
        "scopeOfUniqueness",
        "isUniversallyUnique",
        "versionDate",
        "isPublished",
        "externalReferenceDefaultURI",
        qn(XML_NS, "lang"),
        "isMaintainable",
        "isVersionable",
    }
    _SCOPE_OF_UNIQUENESS_VALUES: ClassVar[set[str]] = {"Agency", "Maintainable"}

    @classmethod
    def from_xml(cls, element: Element) -> ManagedMissingValuesRepresentation:
        recognized = {
            qn(REUSABLE_NS, "ManagedMissingValuesRepresentationName"),
            qn(REUSABLE_NS, "MissingCodeRepresentation"),
            qn(REUSABLE_NS, "MissingNumericRepresentation"),
            qn(REUSABLE_NS, "MissingTextRepresentation"),
            qn(REUSABLE_NS, "ProcessingInstructionReference"),
        }
        data = cls._collect_common(element, recognized_children=recognized)

        names: list[InternationalString] = []
        for container in element.findall(
            qn(REUSABLE_NS, "ManagedMissingValuesRepresentationName")
        ):
            names.extend(InternationalString.from_container(container))

        missing_code_representations = [
            _parse_code_representation(node)
            for node in element.findall(qn(REUSABLE_NS, "MissingCodeRepresentation"))
        ]
        missing_numeric_representations = [
            _parse_numeric_representation(node)
            for node in element.findall(qn(REUSABLE_NS, "MissingNumericRepresentation"))
        ]
        missing_text_representations = [
            _parse_text_representation(node)
            for node in element.findall(qn(REUSABLE_NS, "MissingTextRepresentation"))
        ]

        processing_instruction_reference: Reference | None = None
        processing_instruction_reference_extras: list[Element] = []
        pir_el = element.find(qn(REUSABLE_NS, "ProcessingInstructionReference"))
        if pir_el is not None:
            processing_instruction_reference = Reference.from_xml(pir_el)
            processing_instruction_reference_extras = preserve_unrecognized_children(
                pir_el, _REFERENCE_CHILDREN
            )

        blank_is_missing_value = _parse_bool(element.get("isBlankMissingValue"))

        # ``other_attributes`` (unrecognized attributes) is supplied by
        # ``_collect_common`` via ``**data``; ``isBlankMissingValue`` is captured
        # into ``blank_is_missing_value`` and re-emitted explicitly, so the
        # passthrough's is-absent guard leaves it untouched.
        return cls(
            names=names,
            missing_code_representations=missing_code_representations,
            missing_numeric_representations=missing_numeric_representations,
            missing_text_representations=missing_text_representations,
            processing_instruction_reference=processing_instruction_reference,
            processing_instruction_reference_extras=processing_instruction_reference_extras,
            blank_is_missing_value=blank_is_missing_value,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()

        label_tag = qn(REUSABLE_NS, "Label")
        description_tag = qn(REUSABLE_NS, "Description")
        label_children: list[Element] = []
        description_children: list[Element] = []
        for child in list(element):
            if child.tag == label_tag:
                label_children.append(child)
                element.remove(child)
            elif child.tag == description_tag:
                description_children.append(child)
                element.remove(child)

        if self.blank_is_missing_value is not None:
            element.set(
                "isBlankMissingValue", _format_bool(self.blank_is_missing_value)
            )
        for key, value in self.other_attributes.items():
            if (
                key == "scopeOfUniqueness"
                and value not in self._SCOPE_OF_UNIQUENESS_VALUES
            ):
                continue
            if key in self._ALLOWED_OTHER_ATTRIBUTES:
                element.set(key, value)

        for name in self.names:
            container = create_element(
                qn(REUSABLE_NS, "ManagedMissingValuesRepresentationName")
            )
            container.append(name.to_child(child_tag="String"))
            element.append(container)

        for child in label_children:
            element.append(child)
        for child in description_children:
            element.append(child)

        for code_representation in self.missing_code_representations:
            element.append(
                _serialize_code_representation(
                    code_representation, "MissingCodeRepresentation"
                )
            )
        for numeric_representation in self.missing_numeric_representations:
            element.append(
                _serialize_numeric_representation(
                    numeric_representation, "MissingNumericRepresentation"
                )
            )
        for text_representation in self.missing_text_representations:
            element.append(
                _serialize_text_representation(
                    text_representation, "MissingTextRepresentation"
                )
            )

        if self.processing_instruction_reference is not None:
            reference_el = self.processing_instruction_reference.to_xml(
                "ProcessingInstructionReference"
            )
            for child in self.processing_instruction_reference_extras:
                reference_el.append(clone_element(child))
            element.append(reference_el)

        self._append_other_elements(element)
        return element
