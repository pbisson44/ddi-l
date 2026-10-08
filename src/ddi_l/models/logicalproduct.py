"""Wrappers for LogicalProduct content (variables and managed representations).

Hand-written classes inherit field definitions from the generated base
classes in ``_generated.logicalproduct`` and add serialization
(``from_xml`` / ``to_xml``), validation and helpers.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import ClassVar, Generic, TypeVar
from uuid import uuid5

from .._etree import Element, create_element
from ..constants import IDENTIFIER_NAMESPACE, LOGICAL_PRODUCT_NS, REUSABLE_NS
from ..exceptions import ModelValidationError
from ..namespaces import NamespaceBindings, build_namespace_map

# Generated field-only base classes (from XSD introspection)
from ._generated.logicalproduct import (
    CategoryFields,
    CategorySchemeFields,
    CodeListFields,
    CodeListSchemeFields,
    DataRelationshipFields,
    LogicalProductFields,
    LogicalRecordFields,
    NCubeFields,
    RepresentedVariableFields,
    RepresentedVariableSchemeFields,
    VariableFields,
    VariableGroupFields,
    VariableSchemeFields,
)
from .base import (
    CodeValue,
    InternationalString,
    MaintainableBase,
    Reference,
    UserAttributePair,
    UserID,
    VersionRationale,
    apply_other_attributes,
    build_identification_elements,
    clone_element,
    collect_other_attributes,
    preserve_unrecognized_children,
    qn,
    should_validate_on_serialize,
)

# Shared tag constants for reusable version metadata captured by maintainables.
_VERSION_METADATA_TAGS = {
    qn(REUSABLE_NS, "VersionResponsibility"),
    qn(REUSABLE_NS, "VersionResponsibilityReference"),
    qn(REUSABLE_NS, "VersionRationale"),
}


TMaintainable = TypeVar("TMaintainable", bound=MaintainableBase)


@dataclass
class _InlineScheme(Generic[TMaintainable]):
    """Metadata describing inline schemes emitted within a logical product."""

    identifier: str | None
    agency: str | None
    version: str | None
    urn: str | None
    members: list[TMaintainable]


def _find_text(parent: Element, tag: str) -> str | None:
    """Return the text content of ``tag`` if available on ``parent``."""
    node = parent.find(tag)
    return None if node is None else node.text


__all__ = [
    "Category",
    "CategoryScheme",
    "CodeItem",
    "CodeList",
    "CodeListScheme",
    "CodeRepresentation",
    "DataRelationship",
    "DateTimeRepresentation",
    "LogicalProduct",
    "LogicalRecord",
    "NCube",
    "NumberRange",
    "NumericRepresentation",
    "RepresentedVariable",
    "RepresentedVariableScheme",
    "TextRepresentation",
    "Variable",
    "VariableGroup",
    "VariableRepresentation",
    "VariableScheme",
]


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() == "true"


def _format_bool(value: bool) -> str:
    return "true" if value else "false"


def _collect_version_metadata(
    element: Element,
) -> tuple[str | None, list[Reference], list[VersionRationale]]:
    """Extract reusable version metadata children from ``element``."""
    version_responsibility_el = element.find(qn(REUSABLE_NS, "VersionResponsibility"))
    version_responsibility = (
        version_responsibility_el.text
        if version_responsibility_el is not None
        else None
    )
    version_responsibility_references = [
        Reference.from_xml(node)
        for node in element.findall(qn(REUSABLE_NS, "VersionResponsibilityReference"))
    ]
    version_rationales = [
        VersionRationale.from_xml(node)
        for node in element.findall(qn(REUSABLE_NS, "VersionRationale"))
    ]
    return version_responsibility, version_responsibility_references, version_rationales


def _append_version_metadata(
    element: Element,
    *,
    version_responsibility: str | None,
    version_responsibility_references: Iterable[Reference],
    version_rationales: Iterable[VersionRationale],
) -> None:
    """Emit reusable version metadata in schema order for ``element``."""
    if version_responsibility:
        responsibility_el = create_element(qn(REUSABLE_NS, "VersionResponsibility"))
        responsibility_el.text = version_responsibility
        element.append(responsibility_el)
    for reference in version_responsibility_references:
        element.append(reference.to_xml("VersionResponsibilityReference"))
    for rationale in version_rationales:
        element.append(rationale.to_xml())


@dataclass
class NumberRange:
    """Lightweight representation of ``r:NumberRange`` structures."""

    low: str | None = None
    high: str | None = None
    low_is_inclusive: bool | None = None
    high_is_inclusive: bool | None = None
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "NumberRange")

    @classmethod
    def from_xml(cls, element: Element) -> NumberRange:
        if element.tag != cls.TAG:
            raise ValueError("Expected a reusable:NumberRange element.")

        def _collect_limit(tag: str) -> tuple[str | None, bool | None]:
            limit_el = element.find(qn(REUSABLE_NS, tag))
            if limit_el is None:
                return None, None
            value = limit_el.text or None
            inclusive = _parse_bool(limit_el.get("isInclusive"))
            return value, inclusive

        low, low_is_inclusive = _collect_limit("Low")
        high, high_is_inclusive = _collect_limit("High")
        return cls(
            low=low,
            high=high,
            low_is_inclusive=low_is_inclusive,
            high_is_inclusive=high_is_inclusive,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.low is not None or self.low_is_inclusive is not None:
            low_el = create_element(qn(REUSABLE_NS, "Low"))
            if self.low_is_inclusive is not None:
                low_el.set("isInclusive", _format_bool(self.low_is_inclusive))
            if self.low is not None:
                low_el.text = self.low
            element.append(low_el)
        if self.high is not None or self.high_is_inclusive is not None:
            high_el = create_element(qn(REUSABLE_NS, "High"))
            if self.high_is_inclusive is not None:
                high_el.set("isInclusive", _format_bool(self.high_is_inclusive))
            if self.high is not None:
                high_el.text = self.high
            element.append(high_el)
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class CodeRepresentation:
    """Wrapper for ``r:CodeRepresentation`` nodes."""

    blank_is_missing_value: bool | None = None
    code_list_reference: Reference | None = None
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "CodeRepresentation")

    @classmethod
    def from_xml(cls, element: Element) -> CodeRepresentation:
        if element.tag != cls.TAG:
            raise ValueError("Expected a reusable:CodeRepresentation element.")
        blank_is_missing_value = _parse_bool(element.get("blankIsMissingValue"))
        other_attributes = {
            k: v for k, v in element.attrib.items() if k != "blankIsMissingValue"
        }
        code_list_el = element.find(qn(REUSABLE_NS, "CodeListReference"))
        code_list_reference = (
            Reference.from_xml(code_list_el) if code_list_el is not None else None
        )
        recognized = {qn(REUSABLE_NS, "CodeListReference")}
        other_elements = preserve_unrecognized_children(element, recognized)
        return cls(
            blank_is_missing_value=blank_is_missing_value,
            code_list_reference=code_list_reference,
            other_elements=other_elements,
            other_attributes=other_attributes,
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.blank_is_missing_value is not None:
            element.set(
                "blankIsMissingValue", _format_bool(self.blank_is_missing_value)
            )
        for key, value in self.other_attributes.items():
            element.set(key, value)
        if self.code_list_reference is not None:
            element.append(self.code_list_reference.to_xml("CodeListReference"))
        for child in self.other_elements:
            element.append(clone_element(child))
        return element


@dataclass
class NumericRepresentation:
    """Wrapper for ``r:NumericRepresentation`` nodes."""

    blank_is_missing_value: bool | None = None
    number_range: NumberRange | None = None
    numeric_type_code: str | None = None
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "NumericRepresentation")

    @classmethod
    def from_xml(cls, element: Element) -> NumericRepresentation:
        if element.tag != cls.TAG:
            raise ValueError("Expected a reusable:NumericRepresentation element.")
        blank_is_missing_value = _parse_bool(element.get("blankIsMissingValue"))
        other_attributes = {
            k: v for k, v in element.attrib.items() if k != "blankIsMissingValue"
        }
        range_el = element.find(qn(REUSABLE_NS, "NumberRange"))
        number_range = NumberRange.from_xml(range_el) if range_el is not None else None
        numeric_type_el = element.find(qn(REUSABLE_NS, "NumericTypeCode"))
        numeric_type_code = (
            numeric_type_el.text if numeric_type_el is not None else None
        )
        recognized = {
            qn(REUSABLE_NS, "NumberRange"),
            qn(REUSABLE_NS, "NumericTypeCode"),
        }
        other_elements = preserve_unrecognized_children(element, recognized)
        return cls(
            blank_is_missing_value=blank_is_missing_value,
            number_range=number_range,
            numeric_type_code=numeric_type_code,
            other_elements=other_elements,
            other_attributes=other_attributes,
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.blank_is_missing_value is not None:
            element.set(
                "blankIsMissingValue", _format_bool(self.blank_is_missing_value)
            )
        for key, value in self.other_attributes.items():
            element.set(key, value)
        if self.number_range is not None:
            element.append(self.number_range.to_xml())
        if self.numeric_type_code is not None:
            numeric_type_el = create_element(qn(REUSABLE_NS, "NumericTypeCode"))
            numeric_type_el.text = self.numeric_type_code
            element.append(numeric_type_el)
        for child in self.other_elements:
            element.append(clone_element(child))
        return element


@dataclass
class DateTimeRepresentation:
    """Wrapper for ``r:DateTimeRepresentation`` nodes."""

    blank_is_missing_value: bool | None = None
    date_type_code: str | None = None
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "DateTimeRepresentation")

    @classmethod
    def from_xml(cls, element: Element) -> DateTimeRepresentation:
        if element.tag != cls.TAG:
            raise ValueError("Expected a reusable:DateTimeRepresentation element.")
        blank_is_missing_value = _parse_bool(element.get("blankIsMissingValue"))
        other_attributes = {
            k: v for k, v in element.attrib.items() if k != "blankIsMissingValue"
        }
        date_type_el = element.find(qn(REUSABLE_NS, "DateTypeCode"))
        date_type_code = date_type_el.text if date_type_el is not None else None
        recognized = {qn(REUSABLE_NS, "DateTypeCode")}
        other_elements = preserve_unrecognized_children(element, recognized)
        return cls(
            blank_is_missing_value=blank_is_missing_value,
            date_type_code=date_type_code,
            other_elements=other_elements,
            other_attributes=other_attributes,
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.blank_is_missing_value is not None:
            element.set(
                "blankIsMissingValue", _format_bool(self.blank_is_missing_value)
            )
        for key, value in self.other_attributes.items():
            element.set(key, value)
        if self.date_type_code is not None:
            date_type_el = create_element(qn(REUSABLE_NS, "DateTypeCode"))
            date_type_el.text = self.date_type_code
            element.append(date_type_el)
        for child in self.other_elements:
            element.append(clone_element(child))
        return element


@dataclass
class TextRepresentation:
    """Wrapper for ``r:TextRepresentation`` nodes."""

    blank_is_missing_value: bool | None = None
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "TextRepresentation")

    @classmethod
    def from_xml(cls, element: Element) -> TextRepresentation:
        if element.tag != cls.TAG:
            raise ValueError("Expected a reusable:TextRepresentation element.")
        blank_is_missing_value = _parse_bool(element.get("blankIsMissingValue"))
        other_attributes = {
            k: v for k, v in element.attrib.items() if k != "blankIsMissingValue"
        }
        other_elements = list(element)
        return cls(
            blank_is_missing_value=blank_is_missing_value,
            other_elements=other_elements,
            other_attributes=other_attributes,
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.blank_is_missing_value is not None:
            element.set(
                "blankIsMissingValue", _format_bool(self.blank_is_missing_value)
            )
        for key, value in self.other_attributes.items():
            element.set(key, value)
        for child in self.other_elements:
            element.append(clone_element(child))
        return element


@dataclass
class VariableRepresentation:
    """Wrapper for ``l:VariableRepresentation`` containers."""

    variable_role: CodeValue | None = None
    code_representation: CodeRepresentation | None = None
    numeric_representation: NumericRepresentation | None = None
    date_time_representation: DateTimeRepresentation | None = None
    text_representation: TextRepresentation | None = None
    missing_values_reference: Reference | None = None
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "VariableRepresentation")

    @classmethod
    def from_xml(cls, element: Element) -> VariableRepresentation:
        if element.tag != cls.TAG:
            raise ValueError(
                "Expected a logicalproduct:VariableRepresentation element."
            )
        other_attributes = {
            k: v for k, v in element.attrib.items() if k != "variableRole"
        }
        variable_role_el = element.find(qn(LOGICAL_PRODUCT_NS, "VariableRole"))
        variable_role = (
            CodeValue.from_xml(variable_role_el)
            if variable_role_el is not None
            else None
        )
        code_rep_el = element.find(CodeRepresentation.TAG)
        code_representation = (
            CodeRepresentation.from_xml(code_rep_el)
            if code_rep_el is not None
            else None
        )
        numeric_rep_el = element.find(NumericRepresentation.TAG)
        numeric_representation = (
            NumericRepresentation.from_xml(numeric_rep_el)
            if numeric_rep_el is not None
            else None
        )
        date_rep_el = element.find(DateTimeRepresentation.TAG)
        date_time_representation = (
            DateTimeRepresentation.from_xml(date_rep_el)
            if date_rep_el is not None
            else None
        )
        text_rep_el = element.find(TextRepresentation.TAG)
        text_representation = (
            TextRepresentation.from_xml(text_rep_el)
            if text_rep_el is not None
            else None
        )
        missing_values_el = element.find(
            qn(LOGICAL_PRODUCT_NS, "MissingValuesReference")
        )
        missing_values_reference = (
            Reference.from_xml(missing_values_el)
            if missing_values_el is not None
            else None
        )
        recognized = {
            CodeRepresentation.TAG,
            NumericRepresentation.TAG,
            DateTimeRepresentation.TAG,
            TextRepresentation.TAG,
            qn(LOGICAL_PRODUCT_NS, "MissingValuesReference"),
            qn(LOGICAL_PRODUCT_NS, "VariableRole"),
        }
        other_elements = preserve_unrecognized_children(element, recognized)
        return cls(
            variable_role=variable_role,
            code_representation=code_representation,
            numeric_representation=numeric_representation,
            date_time_representation=date_time_representation,
            text_representation=text_representation,
            missing_values_reference=missing_values_reference,
            other_elements=other_elements,
            other_attributes=other_attributes,
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        for key, value in self.other_attributes.items():
            element.set(key, value)
        if self.variable_role is not None:
            element.append(
                self.variable_role.to_xml("VariableRole", namespace=LOGICAL_PRODUCT_NS)
            )
        if self.code_representation is not None:
            element.append(self.code_representation.to_xml())
        if self.numeric_representation is not None:
            element.append(self.numeric_representation.to_xml())
        if self.date_time_representation is not None:
            element.append(self.date_time_representation.to_xml())
        if self.text_representation is not None:
            element.append(self.text_representation.to_xml())
        if self.missing_values_reference is not None:
            element.append(
                self.missing_values_reference.to_xml(
                    "MissingValuesReference", namespace=LOGICAL_PRODUCT_NS
                )
            )
        for child in self.other_elements:
            element.append(clone_element(child))
        return element


@dataclass
class CodeItem:
    """Representation of a ``l:Code`` entry within a code list."""

    agency: str | None = None
    identifier: str | None = None
    version: str | None = None
    urn: str | None = None
    value: str | None = None
    category: Reference | None = None
    children: list[CodeItem] = field(default_factory=list)
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Code")

    @classmethod
    def from_xml(cls, element: Element) -> CodeItem:
        category_el = element.find(qn(REUSABLE_NS, "CategoryReference"))
        category = Reference.from_xml(category_el) if category_el is not None else None
        value_el = element.find(qn(REUSABLE_NS, "Value"))
        value = value_el.text if value_el is not None else None
        children = [
            cls.from_xml(child)
            for child in element.findall(qn(LOGICAL_PRODUCT_NS, "Code"))
        ]
        urn_el = element.find(qn(REUSABLE_NS, "URN"))
        agency_el = element.find(qn(REUSABLE_NS, "Agency"))
        identifier_el = element.find(qn(REUSABLE_NS, "ID"))
        version_el = element.find(qn(REUSABLE_NS, "Version"))
        recognized = {
            qn(REUSABLE_NS, "URN"),
            qn(REUSABLE_NS, "Agency"),
            qn(REUSABLE_NS, "ID"),
            qn(REUSABLE_NS, "Version"),
            qn(REUSABLE_NS, "CategoryReference"),
            qn(REUSABLE_NS, "Value"),
            qn(LOGICAL_PRODUCT_NS, "Code"),
        }
        extras = preserve_unrecognized_children(element, recognized)
        return cls(
            agency=agency_el.text if agency_el is not None else None,
            identifier=identifier_el.text if identifier_el is not None else None,
            version=version_el.text if version_el is not None else None,
            urn=urn_el.text if urn_el is not None else None,
            value=value,
            category=category,
            children=children,
            other_elements=extras,
            other_attributes=collect_other_attributes(element),
        )

    def _append_identification(self, element: Element) -> None:
        if self.urn:
            urn_el = create_element(qn(REUSABLE_NS, "URN"))
            urn_el.text = self.urn
            element.append(urn_el)
        if self.agency and self.identifier and self.version:
            agency_el = create_element(qn(REUSABLE_NS, "Agency"))
            agency_el.text = self.agency
            element.append(agency_el)
            id_el = create_element(qn(REUSABLE_NS, "ID"))
            id_el.text = self.identifier
            element.append(id_el)
            version_el = create_element(qn(REUSABLE_NS, "Version"))
            version_el.text = self.version
            element.append(version_el)

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        self._append_identification(element)
        if self.category is not None:
            element.append(self.category.to_xml("CategoryReference"))
        if self.value is not None:
            value_el = create_element(qn(REUSABLE_NS, "Value"))
            value_el.text = self.value
            element.append(value_el)
        for child in self.children:
            element.append(child.to_xml())
        for extra in self.other_elements:
            element.append(clone_element(extra))
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class CodeList(CodeListFields):
    """Wrapper around ``l:CodeList`` content."""

    names: list[InternationalString] = field(default_factory=list)
    recommended_datatype: str | None = None
    code_list_references: list[Reference] = field(default_factory=list)
    category_scheme_reference: Reference | None = None
    hierarchy_type: str | None = None  # type: ignore[assignment]
    levels: list[Element] = field(default_factory=list)
    codes: list[CodeItem] = field(default_factory=list)  # type: ignore[assignment]

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CodeList")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")

    @classmethod
    def from_xml(cls, element: Element) -> CodeList:
        recognized = {
            qn(LOGICAL_PRODUCT_NS, "CodeListName"),
            qn(REUSABLE_NS, "RecommendedDataType"),
            qn(REUSABLE_NS, "CodeListReference"),
            qn(REUSABLE_NS, "CategorySchemeReference"),
            qn(LOGICAL_PRODUCT_NS, "HierarchyType"),
            qn(LOGICAL_PRODUCT_NS, "Level"),
            qn(LOGICAL_PRODUCT_NS, "Code"),
        }
        names: list[InternationalString] = []
        for container in element.findall(qn(LOGICAL_PRODUCT_NS, "CodeListName")):
            names.extend(InternationalString.from_container(container))
        recommended_datatype: str | None = None
        datatype_el = element.find(qn(REUSABLE_NS, "RecommendedDataType"))
        if datatype_el is not None:
            recommended_datatype = datatype_el.text or None
        code_list_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "CodeListReference"))
        ]
        cat_scheme_el = element.find(qn(REUSABLE_NS, "CategorySchemeReference"))
        category_scheme_reference = (
            Reference.from_xml(cat_scheme_el) if cat_scheme_el is not None else None
        )
        hierarchy_el = element.find(qn(LOGICAL_PRODUCT_NS, "HierarchyType"))
        hierarchy_type = hierarchy_el.text if hierarchy_el is not None else None
        levels = [
            clone_element(lev)
            for lev in element.findall(qn(LOGICAL_PRODUCT_NS, "Level"))
        ]
        codes = [
            CodeItem.from_xml(code_el)
            for code_el in element.findall(qn(LOGICAL_PRODUCT_NS, "Code"))
        ]
        data = cls._collect_common(element, recognized_children=recognized)
        return cls(
            names=names,
            recommended_datatype=recommended_datatype,
            code_list_references=code_list_references,
            category_scheme_reference=category_scheme_reference,
            hierarchy_type=hierarchy_type,
            levels=levels,
            codes=codes,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        for name in self.names:
            name_el = create_element(qn(LOGICAL_PRODUCT_NS, "CodeListName"))
            name_el.append(name.to_child(child_tag="String"))
            element.append(name_el)
        if self.recommended_datatype:
            datatype_el = create_element(qn(REUSABLE_NS, "RecommendedDataType"))
            datatype_el.text = self.recommended_datatype
            element.append(datatype_el)
        for ref in self.code_list_references:
            element.append(ref.to_xml("CodeListReference", namespace=REUSABLE_NS))
        if self.category_scheme_reference is not None:
            element.append(
                self.category_scheme_reference.to_xml("CategorySchemeReference")
            )
        if self.hierarchy_type is not None:
            ht_el = create_element(qn(LOGICAL_PRODUCT_NS, "HierarchyType"))
            ht_el.text = self.hierarchy_type
            element.append(ht_el)
        for level in self.levels:
            element.append(clone_element(level))
        for code in self.codes:
            element.append(code.to_xml())
        self._append_other_elements(element)
        # CodeListType declares CodeListName before r:Label, but the label
        # comes from _build_base_element and is therefore appended first.
        self._reorder_children_by_element_order(element)
        return element


@dataclass
class Variable(VariableFields):
    """Representation of ``l:Variable`` entries."""

    names: list[InternationalString] = field(default_factory=list)
    out_parameter: Element | None = None
    source_parameter_reference: Reference | None = None
    concept_references: list[Reference] = field(default_factory=list)
    question_references: list[Reference] = field(default_factory=list)
    measurement_references: list[Reference] = field(default_factory=list)
    conceptual_variable_references: list[Reference] = field(default_factory=list)
    universe_references: list[Reference] = field(default_factory=list)
    source_variable_references: list[Reference] = field(default_factory=list)
    represented_variable_reference: Reference | None = None
    weighting_process_reference: Reference | None = None
    embargo_reference: Reference | None = None
    source_unit: CodeValue | None = None
    analysis_unit: CodeValue | None = None
    unit_type_reference: Reference | None = None
    variable_representation: VariableRepresentation | None = None  # type: ignore[assignment]
    user_ids: list[UserID] = field(default_factory=list)
    user_attribute_pairs: list[UserAttributePair] = field(default_factory=list)
    version_responsibility: str | None = None
    version_responsibility_references: list[Reference] = field(default_factory=list)  # type: ignore[assignment]
    version_rationales: list[VersionRationale] = field(default_factory=list)

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Variable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")

    def set_numeric(
        self,
        numeric_type: str = "Decimal",
        *,
        low: str | int | None = None,
        high: str | int | None = None,
        low_inclusive: bool | None = None,
        high_inclusive: bool | None = None,
        missing_values: list[str] | None = None,
        blank_is_missing_value: bool | None = None,
    ) -> Variable:
        """Mark this variable as numeric (``"Integer"``, ``"Decimal"``, ...).

        Pass ``low``/``high`` to record a valid range, and
        ``low_inclusive``/``high_inclusive`` to say whether each bound is
        included (defaults to the DDI default of inclusive). ``missing_values``
        lists sentinel values that denote missing data, and
        ``blank_is_missing_value`` marks blanks as missing. Returns ``self``.
        """
        number_range = None
        if (
            low is not None
            or high is not None
            or low_inclusive is not None
            or high_inclusive is not None
        ):
            number_range = NumberRange(
                low=None if low is None else str(low),
                high=None if high is None else str(high),
                low_is_inclusive=low_inclusive,
                high_is_inclusive=high_inclusive,
            )
        other_attributes: dict[str, str] = {}
        if missing_values:
            other_attributes["missingValue"] = " ".join(missing_values)
        self.variable_representation = VariableRepresentation(
            numeric_representation=NumericRepresentation(
                numeric_type_code=numeric_type,
                number_range=number_range,
                blank_is_missing_value=blank_is_missing_value,
                other_attributes=other_attributes,
            )
        )
        return self

    def set_coded(self, code_list: CodeList | Reference) -> Variable:
        """Mark this variable as coded by a code list. Returns ``self``.

        Accepts a :class:`CodeList` (its reference is taken) or a
        :class:`~ddi_l.models.base.Reference`.
        """
        reference = (
            code_list if isinstance(code_list, Reference) else code_list.to_reference()
        )
        self.variable_representation = VariableRepresentation(
            code_representation=CodeRepresentation(code_list_reference=reference)
        )
        return self

    def set_text(self) -> Variable:
        """Mark this variable as free text. Returns ``self``."""
        self.variable_representation = VariableRepresentation(
            text_representation=TextRepresentation()
        )
        return self

    def set_datetime(self, date_type: str = "DateTime") -> Variable:
        """Mark this variable as a date/time (``"Date"``, ``"DateTime"``, ...).

        Returns ``self``.
        """
        self.variable_representation = VariableRepresentation(
            date_time_representation=DateTimeRepresentation(date_type_code=date_type)
        )
        return self

    @classmethod
    def from_xml(cls, element: Element) -> Variable:
        recognized = {
            qn(LOGICAL_PRODUCT_NS, "VariableName"),
            qn(REUSABLE_NS, "OutParameter"),
            qn(REUSABLE_NS, "SourceParameterReference"),
            qn(REUSABLE_NS, "ConceptReference"),
            qn(REUSABLE_NS, "QuestionReference"),
            qn(REUSABLE_NS, "MeasurementReference"),
            qn(REUSABLE_NS, "ConceptualVariableReference"),
            qn(REUSABLE_NS, "UniverseReference"),
            qn(REUSABLE_NS, "SourceVariableReference"),
            qn(REUSABLE_NS, "RepresentedVariableReference"),
            qn(LOGICAL_PRODUCT_NS, "WeightingProcessReference"),
            qn(LOGICAL_PRODUCT_NS, "EmbargoReference"),
            qn(LOGICAL_PRODUCT_NS, "SourceUnit"),
            qn(REUSABLE_NS, "AnalysisUnit"),
            qn(REUSABLE_NS, "UnitTypeReference"),
            qn(REUSABLE_NS, "UserID"),
            qn(REUSABLE_NS, "UserAttributePair"),
            VariableRepresentation.TAG,
        }
        recognized.update(_VERSION_METADATA_TAGS)
        names: list[InternationalString] = []
        for container in element.findall(qn(LOGICAL_PRODUCT_NS, "VariableName")):
            names.extend(InternationalString.from_container(container))
        out_parameter_el = element.find(qn(REUSABLE_NS, "OutParameter"))
        out_parameter = (
            clone_element(out_parameter_el) if out_parameter_el is not None else None
        )
        source_param_el = element.find(qn(REUSABLE_NS, "SourceParameterReference"))
        source_parameter_reference = (
            Reference.from_xml(source_param_el) if source_param_el is not None else None
        )
        concept_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "ConceptReference"))
        ]
        question_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "QuestionReference"))
        ]
        measurement_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "MeasurementReference"))
        ]
        conceptual_variable_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "ConceptualVariableReference"))
        ]
        universe_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "UniverseReference"))
        ]
        source_variable_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "SourceVariableReference"))
        ]
        represented_variable_el = element.find(
            qn(REUSABLE_NS, "RepresentedVariableReference")
        )
        represented_variable_reference = (
            Reference.from_xml(represented_variable_el)
            if represented_variable_el is not None
            else None
        )
        weighting_el = element.find(qn(LOGICAL_PRODUCT_NS, "WeightingProcessReference"))
        weighting_process_reference = (
            Reference.from_xml(weighting_el) if weighting_el is not None else None
        )
        embargo_el = element.find(qn(LOGICAL_PRODUCT_NS, "EmbargoReference"))
        embargo_reference = (
            Reference.from_xml(embargo_el) if embargo_el is not None else None
        )
        source_unit_el = element.find(qn(LOGICAL_PRODUCT_NS, "SourceUnit"))
        source_unit = (
            CodeValue.from_xml(source_unit_el) if source_unit_el is not None else None
        )
        analysis_unit_el = element.find(qn(REUSABLE_NS, "AnalysisUnit"))
        analysis_unit = (
            CodeValue.from_xml(analysis_unit_el)
            if analysis_unit_el is not None
            else None
        )
        unit_type_el = element.find(qn(REUSABLE_NS, "UnitTypeReference"))
        unit_type_reference = (
            Reference.from_xml(unit_type_el) if unit_type_el is not None else None
        )
        variable_rep_el = element.find(VariableRepresentation.TAG)
        variable_representation = (
            VariableRepresentation.from_xml(variable_rep_el)
            if variable_rep_el is not None
            else None
        )
        user_ids = [
            UserID.from_xml(node) for node in element.findall(qn(REUSABLE_NS, "UserID"))
        ]
        user_attribute_pairs = [
            UserAttributePair.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "UserAttributePair"))
        ]
        data = cls._collect_common(element, recognized_children=recognized)
        (
            version_responsibility,
            version_responsibility_references,
            version_rationales,
        ) = _collect_version_metadata(element)
        return cls(  # type: ignore[misc]
            names=names,
            out_parameter=out_parameter,
            source_parameter_reference=source_parameter_reference,
            concept_references=concept_references,
            question_references=question_references,
            measurement_references=measurement_references,
            conceptual_variable_references=conceptual_variable_references,
            universe_references=universe_references,
            source_variable_references=source_variable_references,
            represented_variable_reference=represented_variable_reference,
            weighting_process_reference=weighting_process_reference,
            embargo_reference=embargo_reference,
            source_unit=source_unit,
            analysis_unit=analysis_unit,
            unit_type_reference=unit_type_reference,
            variable_representation=variable_representation,
            user_ids=user_ids,
            user_attribute_pairs=user_attribute_pairs,
            version_responsibility=version_responsibility,
            version_responsibility_references=version_responsibility_references,
            version_rationales=version_rationales,
            **data,  # type: ignore[arg-type]
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        for user_id in self.user_ids:
            element.append(user_id.to_xml())
        for pair in self.user_attribute_pairs:
            element.append(pair.to_xml())
        _append_version_metadata(
            element,
            version_responsibility=self.version_responsibility,
            version_responsibility_references=self.version_responsibility_references,
            version_rationales=self.version_rationales,
        )
        label_description_tags = {
            qn(REUSABLE_NS, "Label"),
            qn(REUSABLE_NS, "Description"),
        }
        trailing_children = [
            child for child in list(element) if child.tag in label_description_tags
        ]
        for child in trailing_children:
            element.remove(child)
        for name in self.names:
            name_el = create_element(qn(LOGICAL_PRODUCT_NS, "VariableName"))
            name_el.append(name.to_child(child_tag="String"))
            element.append(name_el)
        for child in trailing_children:
            element.append(child)
        if self.out_parameter is not None:
            element.append(clone_element(self.out_parameter))
        if self.source_parameter_reference is not None:
            element.append(
                self.source_parameter_reference.to_xml("SourceParameterReference")
            )
        for reference in self.source_variable_references:
            element.append(reference.to_xml("SourceVariableReference"))
        if self.represented_variable_reference is not None:
            element.append(
                self.represented_variable_reference.to_xml(
                    "RepresentedVariableReference"
                )
            )
        for reference in self.conceptual_variable_references:
            element.append(reference.to_xml("ConceptualVariableReference"))
        if self.weighting_process_reference is not None:
            element.append(
                self.weighting_process_reference.to_xml(
                    "WeightingProcessReference", namespace=LOGICAL_PRODUCT_NS
                )
            )
        for reference in self.universe_references:
            element.append(reference.to_xml("UniverseReference"))
        for reference in self.concept_references:
            element.append(reference.to_xml("ConceptReference"))
        for reference in self.question_references:
            element.append(reference.to_xml("QuestionReference"))
        for reference in self.measurement_references:
            element.append(reference.to_xml("MeasurementReference"))
        if self.embargo_reference is not None:
            element.append(
                self.embargo_reference.to_xml(
                    "EmbargoReference", namespace=LOGICAL_PRODUCT_NS
                )
            )
        if self.source_unit is not None:
            element.append(
                self.source_unit.to_xml("SourceUnit", namespace=LOGICAL_PRODUCT_NS)
            )
        if self.analysis_unit is not None:
            element.append(
                self.analysis_unit.to_xml("AnalysisUnit", namespace=REUSABLE_NS)
            )
        if self.unit_type_reference is not None:
            element.append(self.unit_type_reference.to_xml("UnitTypeReference"))
        if self.variable_representation is not None:
            element.append(self.variable_representation.to_xml())
        self._append_other_elements(element)
        return element


@dataclass
class Category(CategoryFields):
    """Maintainable wrapper for ``l:Category`` entries."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "Category")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")


@dataclass
class CategoryScheme(CategorySchemeFields):
    """Maintainable wrapper for ``l:CategoryScheme`` elements."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CategoryScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")


@dataclass
class CodeListScheme(CodeListSchemeFields):
    """Maintainable wrapper for ``l:CodeListScheme`` elements."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "CodeListScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")


@dataclass
class VariableScheme(VariableSchemeFields):
    """Maintainable wrapper for ``l:VariableScheme`` elements."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "VariableScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")


@dataclass
class RepresentedVariableScheme(RepresentedVariableSchemeFields):
    """Maintainable wrapper for ``l:RepresentedVariableScheme`` elements."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")


@dataclass
class RepresentedVariable(RepresentedVariableFields):
    """Maintainable wrapper for ``l:RepresentedVariable`` entries."""

    names: list[InternationalString] = field(default_factory=list)
    is_missing: bool | None = None
    unit_type_reference: Reference | None = None
    concept_reference: Reference | None = None
    conceptual_variable_reference: Reference | None = None
    code_representation: CodeRepresentation | None = None
    numeric_representation: NumericRepresentation | None = None
    date_time_representation: DateTimeRepresentation | None = None
    text_representation: TextRepresentation | None = None
    version_responsibility: str | None = None
    version_responsibility_references: list[Reference] = field(default_factory=list)  # type: ignore[assignment]
    version_rationales: list[VersionRationale] = field(default_factory=list)

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "RepresentedVariable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")

    @classmethod
    def from_xml(cls, element: Element) -> RepresentedVariable:
        recognized = {
            qn(LOGICAL_PRODUCT_NS, "RepresentedVariableName"),
            qn(REUSABLE_NS, "UnitTypeReference"),
            qn(REUSABLE_NS, "ConceptReference"),
            qn(REUSABLE_NS, "ConceptualVariableReference"),
            CodeRepresentation.TAG,
            NumericRepresentation.TAG,
            DateTimeRepresentation.TAG,
            TextRepresentation.TAG,
        }
        recognized.update(_VERSION_METADATA_TAGS)
        names: list[InternationalString] = []
        for container in element.findall(
            qn(LOGICAL_PRODUCT_NS, "RepresentedVariableName")
        ):
            names.extend(InternationalString.from_container(container))
        unit_type_nodes = element.findall(qn(REUSABLE_NS, "UnitTypeReference"))
        concept_nodes = element.findall(qn(REUSABLE_NS, "ConceptReference"))
        conceptual_nodes = element.findall(
            qn(REUSABLE_NS, "ConceptualVariableReference")
        )

        extras: list[Element] = []
        conceptual_variable_reference: Reference | None = None
        unit_type_reference: Reference | None = None
        concept_reference: Reference | None = None

        if conceptual_nodes:
            conceptual_variable_reference = Reference.from_xml(conceptual_nodes[0])
            extras.extend(clone_element(node) for node in conceptual_nodes[1:])
            extras.extend(clone_element(node) for node in unit_type_nodes)
            extras.extend(clone_element(node) for node in concept_nodes)
        else:
            if unit_type_nodes:
                unit_type_reference = Reference.from_xml(unit_type_nodes[0])
                extras.extend(clone_element(node) for node in unit_type_nodes[1:])
            if concept_nodes:
                concept_reference = Reference.from_xml(concept_nodes[0])
                extras.extend(clone_element(node) for node in concept_nodes[1:])
        code_rep_el = element.find(CodeRepresentation.TAG)
        code_representation = (
            CodeRepresentation.from_xml(code_rep_el)
            if code_rep_el is not None
            else None
        )
        numeric_rep_el = element.find(NumericRepresentation.TAG)
        numeric_representation = (
            NumericRepresentation.from_xml(numeric_rep_el)
            if numeric_rep_el is not None
            else None
        )
        date_rep_el = element.find(DateTimeRepresentation.TAG)
        date_time_representation = (
            DateTimeRepresentation.from_xml(date_rep_el)
            if date_rep_el is not None
            else None
        )
        text_rep_el = element.find(TextRepresentation.TAG)
        text_representation = (
            TextRepresentation.from_xml(text_rep_el)
            if text_rep_el is not None
            else None
        )
        data = cls._collect_common(element, recognized_children=recognized)
        data["other_elements"].extend(extras)
        (
            version_responsibility,
            version_responsibility_references,
            version_rationales,
        ) = _collect_version_metadata(element)
        is_missing = _parse_bool(element.get("isMissing"))
        return cls(  # type: ignore[misc]
            names=names,
            is_missing=is_missing,
            unit_type_reference=unit_type_reference,
            concept_reference=concept_reference,
            conceptual_variable_reference=conceptual_variable_reference,
            code_representation=code_representation,
            numeric_representation=numeric_representation,
            date_time_representation=date_time_representation,
            text_representation=text_representation,
            version_responsibility=version_responsibility,
            version_responsibility_references=version_responsibility_references,
            version_rationales=version_rationales,
            **data,  # type: ignore[arg-type]
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        if self.is_missing is not None:
            element.set("isMissing", _format_bool(self.is_missing))
        label_description_tags = {
            qn(REUSABLE_NS, "Label"),
            qn(REUSABLE_NS, "Description"),
        }
        trailing_children = [
            child for child in list(element) if child.tag in label_description_tags
        ]
        for child in trailing_children:
            element.remove(child)
        _append_version_metadata(
            element,
            version_responsibility=self.version_responsibility,
            version_responsibility_references=self.version_responsibility_references,
            version_rationales=self.version_rationales,
        )
        for name in self.names:
            name_el = create_element(qn(LOGICAL_PRODUCT_NS, "RepresentedVariableName"))
            name_el.append(name.to_child(child_tag="String"))
            element.append(name_el)
        for child in trailing_children:
            element.append(child)
        if self.conceptual_variable_reference is not None:
            element.append(
                self.conceptual_variable_reference.to_xml("ConceptualVariableReference")
            )
        else:
            if self.unit_type_reference is not None:
                element.append(self.unit_type_reference.to_xml("UnitTypeReference"))
            if self.concept_reference is not None:
                element.append(self.concept_reference.to_xml("ConceptReference"))
        if self.code_representation is not None:
            element.append(self.code_representation.to_xml())
        if self.numeric_representation is not None:
            element.append(self.numeric_representation.to_xml())
        if self.date_time_representation is not None:
            element.append(self.date_time_representation.to_xml())
        if self.text_representation is not None:
            element.append(self.text_representation.to_xml())
        suppressed = {
            qn(REUSABLE_NS, "UnitTypeReference"),
            qn(REUSABLE_NS, "ConceptReference"),
            qn(REUSABLE_NS, "ConceptualVariableReference"),
        }
        for child in self.other_elements:
            if child.tag in suppressed:
                continue
            element.append(clone_element(child))
        return element


@dataclass
class VariableGroup(VariableGroupFields):
    """Maintainable representation of ``l:VariableGroup`` aggregates."""

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "VariableGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")


@dataclass
class LogicalRecord(LogicalRecordFields):
    """A logical record: the set of variables describing one case/unit.

    Use :meth:`include_all_variables` for the common rectangular case, where
    every variable in the logical product belongs to the record.
    """

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "LogicalRecord")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")

    def include_all_variables(self) -> LogicalRecord:
        """Mark every variable in the logical product as part of this record."""
        variables_in_record = create_element(
            qn(LOGICAL_PRODUCT_NS, "VariablesInRecord")
        )
        variables_in_record.set("allVariablesInLogicalProduct", "true")
        self.variables_in_record = variables_in_record
        return self


@dataclass
class DataRelationship(DataRelationshipFields):
    """Describes the logical records in a dataset and how they relate.

    Add records with :meth:`add_logical_record`. Created at the high level
    with :meth:`ddi_l.document.Document.add_data_relationship`.
    """

    logical_records: list[LogicalRecord] = field(  # type: ignore[assignment]
        default_factory=list
    )

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "DataRelationship")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")

    def add_logical_record(
        self, *, identifier: str | None = None, all_variables: bool = True
    ) -> LogicalRecord:
        """Append a logical record and return it.

        With ``all_variables`` (the default) the record contains every
        variable in the logical product, the usual rectangular-file case.
        """
        from uuid import uuid4

        record = LogicalRecord(
            agency=self.agency,
            identifier=identifier or str(uuid4()),
            version=self.version,
        )
        if all_variables:
            record.include_all_variables()
        self.logical_records.append(record)
        return record

    def to_xml(self) -> Element:
        element = self._build_base_element()
        # DataRelationshipName precedes r:Label in the content model.
        with self._labels_last(element):
            for name in self.names:
                name_el = create_element(qn(LOGICAL_PRODUCT_NS, "DataRelationshipName"))
                name_el.append(name.to_child(child_tag="String"))
                element.append(name_el)
        for record in self.logical_records:
            element.append(record.to_xml())
        for relationship in self.record_relationships:
            element.append(clone_element(relationship))
        self._append_other_elements(element)
        return element

    @classmethod
    def from_xml(cls, element: Element) -> DataRelationship:
        recognized = {
            qn(LOGICAL_PRODUCT_NS, "DataRelationshipName"),
            qn(LOGICAL_PRODUCT_NS, "LogicalRecord"),
            qn(LOGICAL_PRODUCT_NS, "RecordRelationship"),
        }
        data = cls._collect_common(element, recognized_children=recognized)
        names = [
            name
            for container in element.findall(
                qn(LOGICAL_PRODUCT_NS, "DataRelationshipName")
            )
            for name in InternationalString.from_container(container)
        ]
        logical_records = [
            LogicalRecord.from_xml(node)
            for node in element.findall(qn(LOGICAL_PRODUCT_NS, "LogicalRecord"))
        ]
        record_relationships = [
            clone_element(node)
            for node in element.findall(qn(LOGICAL_PRODUCT_NS, "RecordRelationship"))
        ]
        return cls(
            names=names,
            logical_records=logical_records,
            record_relationships=record_relationships,
            **data,
        )


@dataclass
class NCube(NCubeFields):
    """Maintainable representation of an ``l:NCube`` (multidimensional data).

    An NCube relates measures to a set of dimensions (axes). Add axes with
    :meth:`add_dimension` and measured values with :meth:`add_measure`.
    Created at the high level with :meth:`ddi_l.document.Document.add_ncube`.
    """

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "NCube")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")

    def add_dimension(
        self, variable_reference: Reference, *, rank: int | None = None
    ) -> Element:
        """Add a dimension (axis) backed by a variable. Returns the element.

        ``rank`` defaults to the next axis number (1, 2, 3, ...).
        """
        dimension = create_element(qn(LOGICAL_PRODUCT_NS, "Dimension"))
        next_rank = rank if rank is not None else len(self.dimensions) + 1
        dimension.set("rank", str(next_rank))
        dimension.append(
            variable_reference.to_xml("VariableReference", namespace=REUSABLE_NS)
        )
        self.dimensions.append(dimension)
        return dimension

    def add_measure(self, variable_reference: Reference) -> Element:
        """Add a measured value backed by a variable. Returns the element."""
        measure = create_element(qn(LOGICAL_PRODUCT_NS, "MeasureDefinition"))
        # MeasureDefinition is an IdentifiableType: needs Agency/ID/Version.
        self._append_child_identification(
            measure, suffix=f"measure-{len(self.measure_definitions) + 1}"
        )
        measure.append(
            variable_reference.to_xml("VariableReference", namespace=REUSABLE_NS)
        )
        self.measure_definitions.append(measure)
        return measure

    def add_attribute(
        self,
        variable_reference: Reference,
        *,
        attachment_level: str = "Cube",
        attachment_region: Element | None = None,
    ) -> Element:
        """Add a cube attribute backed by a variable. Returns the element.

        ``attachment_level`` says what the attribute qualifies (``"Cube"`` by
        default; also ``"Dimension"``, ``"Measure"``, ``"Cell"``, ...). Pass
        ``attachment_region`` (from :meth:`add_coordinate_region`) to attach the
        attribute to a specific region of the cube; the attachment level is set
        to ``"CoordinateRegion"`` automatically.
        """
        attribute = create_element(qn(LOGICAL_PRODUCT_NS, "Attribute"))
        if attachment_region is not None:
            attachment_level = "CoordinateRegion"
        attribute.set("attachmentLevel", attachment_level)
        # Attribute is an IdentifiableType: needs Agency/ID/Version.
        self._append_child_identification(
            attribute, suffix=f"attribute-{len(self.attributes) + 1}"
        )
        attribute.append(
            variable_reference.to_xml("VariableReference", namespace=REUSABLE_NS)
        )
        if attachment_region is not None:
            region_id = attachment_region.find(qn(REUSABLE_NS, "ID"))
            reference = Reference(
                agency=self.agency,
                identifier=region_id.text if region_id is not None else None,
                version=self.version or "1",
                type_of_object="CoordinateRegion",
            )
            attribute.append(
                reference.to_xml(
                    "AttachmentRegionReference", namespace=LOGICAL_PRODUCT_NS
                )
            )
        self.attributes.append(attribute)
        return attribute

    def add_coordinate_region(
        self,
        *,
        identifier: str | None = None,
        universe_reference: Reference | None = None,
    ) -> Element:
        """Add a ``CoordinateRegion`` (a subset of the cube). Returns the element.

        Select the included values on each dimension with
        :meth:`add_dimension_value`, then attach an attribute to the region via
        ``add_attribute(variable_ref, attachment_region=region)``.
        """
        region = create_element(qn(LOGICAL_PRODUCT_NS, "CoordinateRegion"))
        # CoordinateRegion is an IdentifiableType: needs Agency/ID/Version.
        self._append_child_identification(
            region,
            suffix=identifier or f"region-{len(self.coordinate_regions) + 1}",
        )
        if universe_reference is not None:
            region.append(
                universe_reference.to_xml("UniverseReference", namespace=REUSABLE_NS)
            )
        self.coordinate_regions.append(region)
        return region

    @staticmethod
    def add_dimension_value(
        region: Element,
        *,
        rank: int,
        category_references: list[Reference] | None = None,
        code_references: list[Reference] | None = None,
    ) -> Element:
        """Add a ``DimensionValue`` selecting values on one dimension of ``region``.

        ``rank`` identifies the dimension (matching :meth:`add_dimension`).
        Provide category and/or code references for the included values. Returns
        the dimension-value element.
        """
        dimension_value = create_element(qn(LOGICAL_PRODUCT_NS, "DimensionValue"))
        dimension_value.set("rank", str(rank))
        for reference in category_references or []:
            dimension_value.append(
                reference.to_xml("CategoryReference", namespace=REUSABLE_NS)
            )
        for reference in code_references or []:
            dimension_value.append(
                reference.to_xml("CodeReference", namespace=REUSABLE_NS)
            )
        region.append(dimension_value)
        return dimension_value


@dataclass
class LogicalProduct(LogicalProductFields):
    """Maintainable wrapper for ``l:LogicalProduct`` elements."""

    names: list[InternationalString] = field(default_factory=list)
    categories: list[Category] = field(default_factory=list)
    variables: list[Variable] = field(default_factory=list)
    code_lists: list[CodeList] = field(default_factory=list)
    represented_variables: list[RepresentedVariable] = field(default_factory=list)
    category_scheme_references: list[Reference] = field(default_factory=list)
    code_list_scheme_references: list[Reference] = field(default_factory=list)
    variable_scheme_references: list[Reference] = field(default_factory=list)
    represented_variable_scheme_references: list[Reference] = field(
        default_factory=list
    )
    managed_representation_scheme_references: list[Reference] = field(
        default_factory=list
    )
    n_cube_scheme_references: list[Reference] = field(default_factory=list)
    data_relationship_references: list[Reference] = field(default_factory=list)
    data_relationships: list[DataRelationship] = field(  # type: ignore[assignment]
        default_factory=list
    )
    n_cubes: list[NCube] = field(default_factory=list)
    coverage: list[Element] = field(default_factory=list)  # type: ignore[assignment]
    _category_schemes: list[_InlineScheme[Category]] = field(
        default_factory=list, init=False, repr=False
    )
    _variable_schemes: list[_InlineScheme[Variable]] = field(
        default_factory=list, init=False, repr=False
    )
    _code_list_schemes: list[_InlineScheme[CodeList]] = field(
        default_factory=list, init=False, repr=False
    )
    _represented_variable_schemes: list[_InlineScheme[RepresentedVariable]] = field(
        default_factory=list, init=False, repr=False
    )

    TAG: ClassVar[str] = qn(LOGICAL_PRODUCT_NS, "LogicalProduct")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")

    def __post_init__(self) -> None:
        self._ensure_category_schemes()
        self._ensure_variable_schemes()
        self._ensure_code_list_schemes()
        self._ensure_represented_variable_schemes()
        self._propagate_child_identification(
            self.categories,
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "category", index
            ),
        )
        self._propagate_child_identification(
            self.variables,
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "variable", index
            ),
        )
        self._propagate_child_identification(
            self.code_lists,
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "code-list", index
            ),
        )
        self._propagate_child_identification(
            self.represented_variables,
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "represented-variable", index
            ),
        )

    def validate(self) -> None:
        super().validate()
        has_category_content = any(
            scheme.members for scheme in self._ensure_category_schemes()
        )
        has_variable_content = any(
            scheme.members for scheme in self._ensure_variable_schemes()
        )
        has_code_list_content = any(
            scheme.members for scheme in self._ensure_code_list_schemes()
        )
        has_represented_variable_content = any(
            scheme.members for scheme in self._ensure_represented_variable_schemes()
        )
        has_scheme_references = bool(
            self.category_scheme_references
            or self.code_list_scheme_references
            or self.variable_scheme_references
            or self.represented_variable_scheme_references
            or self.managed_representation_scheme_references
            or self.n_cube_scheme_references
        )
        has_references = has_scheme_references or any(
            child.tag.endswith("Reference") for child in self.other_elements
        )
        if not (
            has_category_content
            or has_variable_content
            or has_code_list_content
            or has_represented_variable_content
            or has_references
        ):
            raise ModelValidationError(
                "LogicalProduct requires categories, variables,"
                " code lists, or scheme references before"
                " serialization."
            )
        self._assert_unique_children(self.categories, child_label="Category")
        self._assert_unique_children(self.variables, child_label="Variable")
        self._assert_unique_children(self.code_lists, child_label="CodeList")
        self._assert_unique_children(
            self.represented_variables, child_label="RepresentedVariable"
        )

    @classmethod
    def from_xml(cls, element: Element) -> LogicalProduct:
        recognized = {
            qn(LOGICAL_PRODUCT_NS, "LogicalProductName"),
            qn(LOGICAL_PRODUCT_NS, "CategoryScheme"),
            qn(LOGICAL_PRODUCT_NS, "VariableScheme"),
            qn(LOGICAL_PRODUCT_NS, "CodeListScheme"),
            qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme"),
            qn(LOGICAL_PRODUCT_NS, "NCubeScheme"),
            qn(REUSABLE_NS, "CategorySchemeReference"),
            qn(REUSABLE_NS, "CodeListSchemeReference"),
            qn(REUSABLE_NS, "VariableSchemeReference"),
            qn(REUSABLE_NS, "RepresentedVariableSchemeReference"),
            qn(REUSABLE_NS, "ManagedRepresentationSchemeReference"),
            qn(REUSABLE_NS, "NCubeSchemeReference"),
            qn(REUSABLE_NS, "DataRelationshipReference"),
            qn(LOGICAL_PRODUCT_NS, "DataRelationship"),
            qn(REUSABLE_NS, "Coverage"),
        }
        # Parse names
        names: list[InternationalString] = []
        for container in element.findall(qn(LOGICAL_PRODUCT_NS, "LogicalProductName")):
            names.extend(InternationalString.from_container(container))
        # Parse CategorySchemes
        categories: list[Category] = []
        category_schemes: list[_InlineScheme[Category]] = []
        for scheme in element.findall(qn(LOGICAL_PRODUCT_NS, "CategoryScheme")):
            scheme_categories: list[Category] = []
            for cat_el in scheme.findall(qn(LOGICAL_PRODUCT_NS, "Category")):
                category = Category.from_xml(cat_el)
                categories.append(category)
                scheme_categories.append(category)
            category_schemes.append(
                _InlineScheme(
                    identifier=_find_text(scheme, qn(REUSABLE_NS, "ID")),
                    agency=_find_text(scheme, qn(REUSABLE_NS, "Agency")),
                    version=_find_text(scheme, qn(REUSABLE_NS, "Version")),
                    urn=_find_text(scheme, qn(REUSABLE_NS, "URN")),
                    members=scheme_categories,
                )
            )
        # Parse VariableSchemes
        variables: list[Variable] = []
        variable_schemes: list[_InlineScheme[Variable]] = []
        for scheme in element.findall(qn(LOGICAL_PRODUCT_NS, "VariableScheme")):
            scheme_variables: list[Variable] = []
            for variable_el in scheme.findall(qn(LOGICAL_PRODUCT_NS, "Variable")):
                variable = Variable.from_xml(variable_el)
                variables.append(variable)
                scheme_variables.append(variable)
            variable_schemes.append(
                _InlineScheme(
                    identifier=_find_text(scheme, qn(REUSABLE_NS, "ID")),
                    agency=_find_text(scheme, qn(REUSABLE_NS, "Agency")),
                    version=_find_text(scheme, qn(REUSABLE_NS, "Version")),
                    urn=_find_text(scheme, qn(REUSABLE_NS, "URN")),
                    members=scheme_variables,
                )
            )
        # Parse CodeListSchemes
        code_lists: list[CodeList] = []
        code_list_schemes: list[_InlineScheme[CodeList]] = []
        for scheme in element.findall(qn(LOGICAL_PRODUCT_NS, "CodeListScheme")):
            scheme_code_lists: list[CodeList] = []
            for code_list_el in scheme.findall(qn(LOGICAL_PRODUCT_NS, "CodeList")):
                code_list = CodeList.from_xml(code_list_el)
                code_lists.append(code_list)
                scheme_code_lists.append(code_list)
            code_list_schemes.append(
                _InlineScheme(
                    identifier=_find_text(scheme, qn(REUSABLE_NS, "ID")),
                    agency=_find_text(scheme, qn(REUSABLE_NS, "Agency")),
                    version=_find_text(scheme, qn(REUSABLE_NS, "Version")),
                    urn=_find_text(scheme, qn(REUSABLE_NS, "URN")),
                    members=scheme_code_lists,
                )
            )
        # Parse RepresentedVariableSchemes
        represented_variables: list[RepresentedVariable] = []
        represented_variable_schemes: list[_InlineScheme[RepresentedVariable]] = []
        for scheme in element.findall(
            qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme")
        ):
            scheme_repr_vars: list[RepresentedVariable] = []
            for rv_el in scheme.findall(qn(LOGICAL_PRODUCT_NS, "RepresentedVariable")):
                rv = RepresentedVariable.from_xml(rv_el)
                represented_variables.append(rv)
                scheme_repr_vars.append(rv)
            represented_variable_schemes.append(
                _InlineScheme(
                    identifier=_find_text(scheme, qn(REUSABLE_NS, "ID")),
                    agency=_find_text(scheme, qn(REUSABLE_NS, "Agency")),
                    version=_find_text(scheme, qn(REUSABLE_NS, "Version")),
                    urn=_find_text(scheme, qn(REUSABLE_NS, "URN")),
                    members=scheme_repr_vars,
                )
            )
        # Parse scheme references
        category_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "CategorySchemeReference"))
        ]
        code_list_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "CodeListSchemeReference"))
        ]
        variable_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "VariableSchemeReference"))
        ]
        represented_variable_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(
                qn(REUSABLE_NS, "RepresentedVariableSchemeReference")
            )
        ]
        managed_representation_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(
                qn(REUSABLE_NS, "ManagedRepresentationSchemeReference")
            )
        ]
        n_cube_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "NCubeSchemeReference"))
        ]
        data_relationship_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "DataRelationshipReference"))
        ]
        data_relationships = [
            DataRelationship.from_xml(node)
            for node in element.findall(qn(LOGICAL_PRODUCT_NS, "DataRelationship"))
        ]
        n_cubes = [
            NCube.from_xml(node)
            for scheme in element.findall(qn(LOGICAL_PRODUCT_NS, "NCubeScheme"))
            for node in scheme.findall(qn(LOGICAL_PRODUCT_NS, "NCube"))
        ]
        coverage = [
            clone_element(node) for node in element.findall(qn(REUSABLE_NS, "Coverage"))
        ]
        data = cls._collect_common(element, recognized_children=recognized)
        instance = cls(
            names=names,
            categories=categories,
            variables=variables,
            code_lists=code_lists,
            represented_variables=represented_variables,
            category_scheme_references=category_scheme_references,
            code_list_scheme_references=code_list_scheme_references,
            variable_scheme_references=variable_scheme_references,
            represented_variable_scheme_references=represented_variable_scheme_references,
            managed_representation_scheme_references=managed_representation_scheme_references,
            n_cube_scheme_references=n_cube_scheme_references,
            data_relationship_references=data_relationship_references,
            data_relationships=data_relationships,
            n_cubes=n_cubes,
            coverage=coverage,
            **data,
        )
        if category_schemes:
            instance._category_schemes = category_schemes
        if variable_schemes:
            instance._variable_schemes = variable_schemes
        if code_list_schemes:
            instance._code_list_schemes = code_list_schemes
        if represented_variable_schemes:
            instance._represented_variable_schemes = represented_variable_schemes
        return instance

    def to_xml(self) -> Element:
        if should_validate_on_serialize(self):
            self.validate()
        element = self._build_base_element()
        # LogicalProductName
        for name in self.names:
            name_el = create_element(qn(LOGICAL_PRODUCT_NS, "LogicalProductName"))
            name_el.append(name.to_child(child_tag="String"))
            element.append(name_el)
        # Coverage
        for coverage_el in self.coverage:
            element.append(clone_element(coverage_el))
        # DataRelationship (inline) and references — both precede the schemes.
        for data_relationship in self.data_relationships:
            element.append(data_relationship.to_xml())
        for ref in self.data_relationship_references:
            element.append(ref.to_xml("DataRelationshipReference"))
        # XSD order: CategoryScheme → CodeListScheme → ManagedRepresentationScheme →
        #            RepresentedVariableScheme → VariableScheme → NCubeScheme
        for index, cat_scheme in enumerate(self._ensure_category_schemes(), start=1):
            if not cat_scheme.members:
                continue
            scheme_el = create_element(qn(LOGICAL_PRODUCT_NS, "CategoryScheme"))
            self._append_inline_scheme_identification(
                scheme_el,
                cat_scheme,
                default_suffix="category-scheme",
                index=index,
            )
            for category in cat_scheme.members:
                scheme_el.append(category.to_xml())
            element.append(scheme_el)
        for ref in self.category_scheme_references:
            element.append(ref.to_xml("CategorySchemeReference"))
        for index, code_scheme in enumerate(self._ensure_code_list_schemes(), start=1):
            if not code_scheme.members:
                continue
            scheme_el = create_element(qn(LOGICAL_PRODUCT_NS, "CodeListScheme"))
            self._append_inline_scheme_identification(
                scheme_el,
                code_scheme,
                default_suffix="code-list-scheme",
                index=index,
            )
            for code_list in code_scheme.members:
                scheme_el.append(code_list.to_xml())
            element.append(scheme_el)
        for ref in self.code_list_scheme_references:
            element.append(ref.to_xml("CodeListSchemeReference"))
        for ref in self.managed_representation_scheme_references:
            element.append(ref.to_xml("ManagedRepresentationSchemeReference"))
        for index, rv_scheme in enumerate(
            self._ensure_represented_variable_schemes(), start=1
        ):
            if not rv_scheme.members:
                continue
            scheme_el = create_element(
                qn(LOGICAL_PRODUCT_NS, "RepresentedVariableScheme")
            )
            self._append_inline_scheme_identification(
                scheme_el,
                rv_scheme,
                default_suffix="represented-variable-scheme",
                index=index,
            )
            for rv in rv_scheme.members:
                scheme_el.append(rv.to_xml())
            element.append(scheme_el)
        for ref in self.represented_variable_scheme_references:
            element.append(ref.to_xml("RepresentedVariableSchemeReference"))
        for index, variable_scheme in enumerate(
            self._ensure_variable_schemes(), start=1
        ):
            if not variable_scheme.members:
                continue
            scheme_el = create_element(qn(LOGICAL_PRODUCT_NS, "VariableScheme"))
            self._append_inline_scheme_identification(
                scheme_el,
                variable_scheme,
                default_suffix="variable-scheme",
                index=index,
            )
            for variable in variable_scheme.members:
                scheme_el.append(variable.to_xml())
            element.append(scheme_el)
        for ref in self.variable_scheme_references:
            element.append(ref.to_xml("VariableSchemeReference"))
        if self.n_cubes:
            scheme_el = create_element(qn(LOGICAL_PRODUCT_NS, "NCubeScheme"))
            self._append_child_identification(scheme_el, suffix="ncube-scheme")
            for ncube in self.n_cubes:
                scheme_el.append(ncube.to_xml())
            element.append(scheme_el)
        for ref in self.n_cube_scheme_references:
            element.append(ref.to_xml("NCubeSchemeReference"))
        self._append_other_elements(element)
        return element

    def iter_categories(
        self,
        *,
        identifier: str | None = None,
        urn: str | None = None,
        scheme_identifier: str | None = None,
        scheme_urn: str | None = None,
    ) -> Iterator[Category]:
        """Yield categories with optional filtering by metadata."""
        for scheme in self._ensure_category_schemes():
            if scheme_identifier is not None and scheme.identifier != scheme_identifier:
                continue
            if scheme_urn is not None and scheme.urn != scheme_urn:
                continue
            for category in scheme.members:
                if identifier is not None and category.identifier != identifier:
                    continue
                if urn is not None and category.urn != urn:
                    continue
                yield category

    def iter_variables(
        self,
        *,
        identifier: str | None = None,
        urn: str | None = None,
        scheme_identifier: str | None = None,
        scheme_urn: str | None = None,
    ) -> Iterator[Variable]:
        """Yield variables with optional filtering by metadata."""
        for scheme in self._ensure_variable_schemes():
            if scheme_identifier is not None and scheme.identifier != scheme_identifier:
                continue
            if scheme_urn is not None and scheme.urn != scheme_urn:
                continue
            for variable in scheme.members:
                if identifier is not None and variable.identifier != identifier:
                    continue
                if urn is not None and variable.urn != urn:
                    continue
                yield variable

    def iter_code_lists(
        self,
        *,
        identifier: str | None = None,
        urn: str | None = None,
        scheme_identifier: str | None = None,
        scheme_urn: str | None = None,
    ) -> Iterator[CodeList]:
        """Yield code lists with optional filtering by metadata."""
        for scheme in self._ensure_code_list_schemes():
            if scheme_identifier is not None and scheme.identifier != scheme_identifier:
                continue
            if scheme_urn is not None and scheme.urn != scheme_urn:
                continue
            for code_list in scheme.members:
                if identifier is not None and code_list.identifier != identifier:
                    continue
                if urn is not None and code_list.urn != urn:
                    continue
                yield code_list

    def iter_represented_variables(
        self,
        *,
        identifier: str | None = None,
        urn: str | None = None,
        scheme_identifier: str | None = None,
        scheme_urn: str | None = None,
    ) -> Iterator[RepresentedVariable]:
        """Yield represented variables with optional filtering by metadata."""
        for scheme in self._ensure_represented_variable_schemes():
            if scheme_identifier is not None and scheme.identifier != scheme_identifier:
                continue
            if scheme_urn is not None and scheme.urn != scheme_urn:
                continue
            for rv in scheme.members:
                if identifier is not None and rv.identifier != identifier:
                    continue
                if urn is not None and rv.urn != urn:
                    continue
                yield rv

    def iter_derived_datasets(
        self,
        *,
        identifier: str | None = None,
        urn: str | None = None,
    ) -> Iterator[MaintainableBase]:
        """Yield derived dataset maintainables preserved in ``other_elements``."""
        for element in self.other_elements:
            if element.tag != qn(LOGICAL_PRODUCT_NS, "DerivedDataSet"):
                continue
            model = MaintainableBase.for_tag(element.tag)
            if model is None:
                continue
            dataset = model.from_xml(element)
            if identifier is not None and dataset.identifier != identifier:
                continue
            if urn is not None and dataset.urn != urn:
                continue
            yield dataset

    @staticmethod
    def _reconcile_scheme_members(
        schemes: list[_InlineScheme[TMaintainable]],
        members: list[TMaintainable],
    ) -> None:
        """Add flat-list ``members`` missing from existing inline ``schemes``.

        After parsing from XML, members live in ``schemes`` while the public
        list (``self.variables`` etc.) is a parallel view. Items appended to the
        public list must be merged back so they serialize. Matching is by
        identifier so already-present members are not duplicated.
        """
        if not schemes or not members:
            return
        present = {member.identifier for scheme in schemes for member in scheme.members}
        for member in list(members):
            if member.identifier not in present:
                schemes[0].members.append(member)
                present.add(member.identifier)

    def _ensure_category_schemes(self) -> list[_InlineScheme[Category]]:
        if not self._category_schemes:
            if self.categories:
                self._category_schemes = [
                    _InlineScheme(
                        identifier=None,
                        agency=self.agency,
                        version=self.version,
                        urn=None,
                        members=self.categories,
                    )
                ]
            else:
                self._category_schemes = []
        self._reconcile_scheme_members(self._category_schemes, self.categories)
        self._populate_scheme_defaults(
            self._category_schemes, base_suffix="category-scheme"
        )
        return self._category_schemes

    def _ensure_variable_schemes(self) -> list[_InlineScheme[Variable]]:
        if not self._variable_schemes:
            if self.variables:
                self._variable_schemes = [
                    _InlineScheme(
                        identifier=None,
                        agency=self.agency,
                        version=self.version,
                        urn=None,
                        members=self.variables,
                    )
                ]
            else:
                self._variable_schemes = []
        self._reconcile_scheme_members(self._variable_schemes, self.variables)
        self._populate_scheme_defaults(
            self._variable_schemes, base_suffix="variable-scheme"
        )
        return self._variable_schemes

    def _ensure_code_list_schemes(self) -> list[_InlineScheme[CodeList]]:
        if not self._code_list_schemes:
            if self.code_lists:
                self._code_list_schemes = [
                    _InlineScheme(
                        identifier=None,
                        agency=self.agency,
                        version=self.version,
                        urn=None,
                        members=self.code_lists,
                    )
                ]
            else:
                self._code_list_schemes = []
        self._reconcile_scheme_members(self._code_list_schemes, self.code_lists)
        self._populate_scheme_defaults(
            self._code_list_schemes, base_suffix="code-list-scheme"
        )
        return self._code_list_schemes

    def _ensure_represented_variable_schemes(
        self,
    ) -> list[_InlineScheme[RepresentedVariable]]:
        if not self._represented_variable_schemes:
            if self.represented_variables:
                self._represented_variable_schemes = [
                    _InlineScheme(
                        identifier=None,
                        agency=self.agency,
                        version=self.version,
                        urn=None,
                        members=self.represented_variables,
                    )
                ]
            else:
                self._represented_variable_schemes = []
        self._reconcile_scheme_members(
            self._represented_variable_schemes, self.represented_variables
        )
        self._populate_scheme_defaults(
            self._represented_variable_schemes,
            base_suffix="represented-variable-scheme",
        )
        return self._represented_variable_schemes

    def _populate_scheme_defaults(
        self,
        schemes: list[_InlineScheme[TMaintainable]],
        *,
        base_suffix: str,
        start_index: int = 1,
    ) -> None:
        for offset, scheme in enumerate(schemes, start=start_index):
            if scheme.identifier is None:
                scheme.identifier = self._default_inline_identifier(base_suffix, offset)
            if scheme.agency is None:
                scheme.agency = self.agency
            if scheme.version is None:
                scheme.version = self.version

    def _append_inline_scheme_identification(
        self,
        element: Element,
        scheme: _InlineScheme[TMaintainable],
        *,
        default_suffix: str,
        index: int,
    ) -> None:
        self._populate_scheme_defaults(
            [scheme], base_suffix=default_suffix, start_index=index
        )
        if scheme.urn is not None:
            urn_el = create_element(qn(REUSABLE_NS, "URN"))
            urn_el.text = scheme.urn
            element.append(urn_el)
        for child in build_identification_elements(
            agency=scheme.agency,
            identifier=scheme.identifier,
            version=scheme.version,
        ):
            element.append(child)
        # Inline schemes bypass _append_child_identification, so apply the
        # scheme-label hook here for set_scheme_label() to take effect.
        self._append_scheme_label(element)

    def _default_inline_identifier(self, suffix: str, index: int) -> str | None:
        prefix = self.identifier or getattr(self, "_auto_identifier", None)
        if prefix is None:
            return None
        parts = []
        if self.agency:
            parts.append(self.agency)
        parts.append(prefix)
        parts.append(suffix)
        if index != 1:
            parts.append(str(index))
        seed = ":".join(parts)
        return str(uuid5(IDENTIFIER_NAMESPACE, seed))

    # ``scheme.urn`` is preserved only when explicitly provided in the source
    # payload. No default URN is generated to keep round-tripped XML stable.
