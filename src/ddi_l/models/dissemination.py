"""Wrappers for dissemination and harmonisation-related modules."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, ClassVar, cast

from .._etree import Element, cleanup_namespaces, create_element
from ..constants import (
    COMPARATIVE_NS,
    DATA_COLLECTION_NS,
    PHYSICAL_INSTANCE_NS,
    REUSABLE_NS,
)
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.datacollection import WeightingMethodologyFields
from ._generated.physicalinstance import PhysicalInstanceGroupFields
from .base import (
    CodeValue,
    InternationalString,
    Reference,
    UserAttributePair,
    UserID,
    VersionRationale,
    apply_other_attributes,
    build_identification_elements,
    clone_element,
    collect_other_attributes,
    qn,
)
from .datacollection import VersionableMaintainableBase

__all__ = [
    "ConceptMap",
    "PhysicalInstanceGroup",
    "QuestionMap",
    "VariableMap",
    "Weighting",
    "WeightingMethodology",
]


def _iter_children(element: Element, tag: str, *, namespace: str) -> Iterable[Element]:
    return element.findall(qn(namespace, tag))


@dataclass
class _CorrespondenceProperty:
    """Representation of ``r:UserDefinedCorrespondenceProperty`` entries."""

    key: str | None = None
    value: str | None = None
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "UserDefinedCorrespondenceProperty")

    @classmethod
    def from_xml(cls, element: Element) -> _CorrespondenceProperty:
        if element.tag != cls.TAG:
            raise ValueError(
                "Expected a reusable:UserDefinedCorrespondenceProperty element."
            )
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
class Correspondence:
    """Representation of ``cm:Correspondence`` structures."""

    commonalities: list[InternationalString] = field(default_factory=list)
    differences: list[InternationalString] = field(default_factory=list)
    commonality_type: CodeValue | None = None
    commonality_weight: float | None = None
    properties: list[_CorrespondenceProperty] = field(default_factory=list)
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "Correspondence")

    @classmethod
    def from_xml(cls, element: Element) -> Correspondence:
        if element.tag != cls.TAG:
            raise ValueError("Expected a comparative:Correspondence element.")
        recognized = {
            qn(COMPARATIVE_NS, "Commonality"),
            qn(REUSABLE_NS, "Difference"),
            qn(COMPARATIVE_NS, "CommonalityTypeCoded"),
            qn(COMPARATIVE_NS, "CommonalityWeight"),
            qn(REUSABLE_NS, "UserDefinedCorrespondenceProperty"),
        }
        commonalities: list[InternationalString] = []
        for container in _iter_children(
            element, "Commonality", namespace=COMPARATIVE_NS
        ):
            commonalities.extend(InternationalString.from_container(container))
        differences: list[InternationalString] = []
        for container in _iter_children(element, "Difference", namespace=REUSABLE_NS):
            differences.extend(InternationalString.from_container(container))
        commonality_type_el = element.find(qn(COMPARATIVE_NS, "CommonalityTypeCoded"))
        commonality_type = None
        if commonality_type_el is not None:
            commonality_type = CodeValue.from_xml(commonality_type_el)
        weight_el = element.find(qn(COMPARATIVE_NS, "CommonalityWeight"))
        properties = [
            _CorrespondenceProperty.from_xml(node)
            for node in _iter_children(
                element, "UserDefinedCorrespondenceProperty", namespace=REUSABLE_NS
            )
        ]
        other = [
            clone_element(child) for child in element if child.tag not in recognized
        ]
        weight = None
        if weight_el is not None and weight_el.text is not None:
            try:
                weight = float(weight_el.text)
            except ValueError:
                weight = None
        return cls(
            commonalities=commonalities,
            differences=differences,
            commonality_type=commonality_type,
            commonality_weight=weight,
            properties=properties,
            other_elements=other,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.commonalities:
            container = create_element(qn(COMPARATIVE_NS, "Commonality"))
            for value in self.commonalities:
                container.append(value.to_child())
            element.append(container)
        if self.differences:
            container = create_element(qn(REUSABLE_NS, "Difference"))
            for value in self.differences:
                container.append(value.to_child())
            element.append(container)
        if self.commonality_type is not None:
            element.append(
                self.commonality_type.to_xml(
                    "CommonalityTypeCoded", namespace=COMPARATIVE_NS
                )
            )
        if self.commonality_weight is not None:
            weight_el = create_element(qn(COMPARATIVE_NS, "CommonalityWeight"))
            weight_el.text = str(self.commonality_weight)
            element.append(weight_el)
        for prop in self.properties:
            element.append(prop.to_xml())
        for child in self.other_elements:
            element.append(clone_element(child))
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class ItemMap:
    """Representation of ``cm:ItemMap`` entries."""

    urn: str | None = None
    agency: str | None = None
    identifier: str | None = None
    version: str | None = None
    user_ids: list[UserID] = field(default_factory=list)
    user_attribute_pairs: list[UserAttributePair] = field(default_factory=list)
    version_rationales: list[VersionRationale] = field(default_factory=list)
    alias: str | None = None
    source_item_reference: Reference | None = None
    target_item_references: list[Reference] = field(default_factory=list)
    correspondence: Correspondence | None = None
    related_map_references: list[Reference] = field(default_factory=list)
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "ItemMap")

    @classmethod
    def from_xml(cls, element: Element) -> ItemMap:
        if element.tag != cls.TAG:
            raise ValueError("Expected a comparative:ItemMap element.")
        recognized = {
            qn(REUSABLE_NS, "URN"),
            qn(REUSABLE_NS, "Agency"),
            qn(REUSABLE_NS, "ID"),
            qn(REUSABLE_NS, "Version"),
            qn(REUSABLE_NS, "UserID"),
            qn(REUSABLE_NS, "UserAttributePair"),
            qn(REUSABLE_NS, "VersionRationale"),
            qn(COMPARATIVE_NS, "SourceItemReference"),
            qn(COMPARATIVE_NS, "TargetItemReference"),
            qn(COMPARATIVE_NS, "Correspondence"),
            qn(COMPARATIVE_NS, "RelatedMapReference"),
        }
        user_ids = [
            UserID.from_xml(node)
            for node in _iter_children(element, "UserID", namespace=REUSABLE_NS)
        ]
        user_attribute_pairs = [
            UserAttributePair.from_xml(node)
            for node in _iter_children(
                element, "UserAttributePair", namespace=REUSABLE_NS
            )
        ]
        version_rationales = [
            VersionRationale.from_xml(node)
            for node in _iter_children(
                element, "VersionRationale", namespace=REUSABLE_NS
            )
        ]
        source_reference = None
        source_el = element.find(qn(COMPARATIVE_NS, "SourceItemReference"))
        if source_el is not None:
            source_reference = Reference.from_xml(source_el)
        target_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                element, "TargetItemReference", namespace=COMPARATIVE_NS
            )
        ]
        correspondence_el = element.find(qn(COMPARATIVE_NS, "Correspondence"))
        correspondence = (
            Correspondence.from_xml(correspondence_el)
            if correspondence_el is not None
            else None
        )
        related_map_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                element, "RelatedMapReference", namespace=COMPARATIVE_NS
            )
        ]
        other = [
            clone_element(child) for child in element if child.tag not in recognized
        ]
        return cls(
            urn=_get_text(element, qn(REUSABLE_NS, "URN")),
            agency=_get_text(element, qn(REUSABLE_NS, "Agency")),
            identifier=_get_text(element, qn(REUSABLE_NS, "ID")),
            version=_get_text(element, qn(REUSABLE_NS, "Version")),
            user_ids=user_ids,
            user_attribute_pairs=user_attribute_pairs,
            version_rationales=version_rationales,
            alias=element.get("alias"),
            source_item_reference=source_reference,
            target_item_references=target_references,
            correspondence=correspondence,
            related_map_references=related_map_references,
            other_elements=other,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.alias:
            element.set("alias", self.alias)
        if self.urn:
            urn_el = create_element(qn(REUSABLE_NS, "URN"))
            urn_el.text = self.urn
            element.append(urn_el)
        for child in build_identification_elements(
            agency=self.agency,
            identifier=self.identifier,
            version=self.version,
        ):
            element.append(child)
        for user_id in self.user_ids:
            element.append(user_id.to_xml())
        for pair in self.user_attribute_pairs:
            element.append(pair.to_xml())
        for rationale in self.version_rationales:
            element.append(rationale.to_xml())
        if self.source_item_reference is not None:
            element.append(
                self.source_item_reference.to_xml(
                    "SourceItemReference", namespace=COMPARATIVE_NS
                )
            )
        for reference in self.target_item_references:
            element.append(
                reference.to_xml("TargetItemReference", namespace=COMPARATIVE_NS)
            )
        if self.correspondence is not None:
            element.append(self.correspondence.to_xml())
        for reference in self.related_map_references:
            element.append(
                reference.to_xml("RelatedMapReference", namespace=COMPARATIVE_NS)
            )
        for child in self.other_elements:
            element.append(clone_element(child))
        apply_other_attributes(element, self.other_attributes)
        return element


def _get_text(parent: Element, tag: str) -> str | None:
    child = parent.find(tag)
    return None if child is None else child.text


@dataclass
class _GenericMap(VersionableMaintainableBase):
    """Shared representation of ``cm:GenericMapType`` maintainables."""

    names: list[InternationalString] = field(default_factory=list)
    type_of_mapped_item: CodeValue | None = None
    source_scheme_reference: Reference | None = None
    target_scheme_reference: Reference | None = None
    correspondence: Correspondence | None = None
    item_maps: list[ItemMap] = field(default_factory=list)

    NAME_TAG: ClassVar[str] = "MapName"

    @classmethod
    def _collect_generic_map_common(
        cls,
        element: Element,
        *,
        recognized_children: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        name_tag = qn(COMPARATIVE_NS, cls.NAME_TAG)
        recognized = {
            name_tag,
            qn(COMPARATIVE_NS, "TypeOfMappedItem"),
            qn(COMPARATIVE_NS, "SourceSchemeReference"),
            qn(COMPARATIVE_NS, "TargetSchemeReference"),
            qn(COMPARATIVE_NS, "Correspondence"),
            qn(COMPARATIVE_NS, "ItemMap"),
        }
        if recognized_children:
            recognized.update(recognized_children)
        data: dict[str, Any] = dict(
            cls._collect_versionable_common(element, recognized_children=recognized)
        )
        names: list[InternationalString] = []
        for container in element.findall(name_tag):
            names.extend(InternationalString.from_container(container))
        type_el = element.find(qn(COMPARATIVE_NS, "TypeOfMappedItem"))
        type_of_mapped_item = None
        if type_el is not None:
            type_of_mapped_item = CodeValue.from_xml(type_el)
        source_el = element.find(qn(COMPARATIVE_NS, "SourceSchemeReference"))
        target_el = element.find(qn(COMPARATIVE_NS, "TargetSchemeReference"))
        correspondence_el = element.find(qn(COMPARATIVE_NS, "Correspondence"))
        item_maps = [
            ItemMap.from_xml(node)
            for node in element.findall(qn(COMPARATIVE_NS, "ItemMap"))
        ]
        data.update(
            {
                "names": names,
                "type_of_mapped_item": type_of_mapped_item,
                "source_scheme_reference": (
                    Reference.from_xml(source_el) if source_el is not None else None
                ),
                "target_scheme_reference": (
                    Reference.from_xml(target_el) if target_el is not None else None
                ),
                "correspondence": (
                    Correspondence.from_xml(correspondence_el)
                    if correspondence_el is not None
                    else None
                ),
                "item_maps": item_maps,
            }
        )
        return data

    @classmethod
    def from_xml(cls, element: Element) -> _GenericMap:
        data = cls._collect_generic_map_common(element)
        return cls(**data)

    def _append_generic_map_common(self, element: Element) -> None:
        self._append_versionable_common(element)
        with self._labels_last(element):
            if self.type_of_mapped_item is not None:
                element.append(
                    self.type_of_mapped_item.to_xml(
                        "TypeOfMappedItem", namespace=COMPARATIVE_NS
                    )
                )
            for name in self.names:
                container = create_element(qn(COMPARATIVE_NS, self.NAME_TAG))
                container.append(name.to_child(child_tag="String"))
                element.append(container)
        if self.source_scheme_reference is not None:
            element.append(
                self.source_scheme_reference.to_xml(
                    "SourceSchemeReference", namespace=COMPARATIVE_NS
                )
            )
        if self.target_scheme_reference is not None:
            element.append(
                self.target_scheme_reference.to_xml(
                    "TargetSchemeReference", namespace=COMPARATIVE_NS
                )
            )
        if self.correspondence is not None:
            element.append(self.correspondence.to_xml())
        for item_map in self.item_maps:
            element.append(item_map.to_xml())

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_generic_map_common(element)
        self._append_other_elements(element)
        cleanup_namespaces(
            element,
            {
                "cmp": COMPARATIVE_NS,
                "r": REUSABLE_NS,
            },
        )
        return element


@dataclass
class ConceptMap(_GenericMap):
    """Representation of ``cm:ConceptMap`` maintainables."""

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "ConceptMap")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp")

    @classmethod
    def from_xml(cls, element: Element) -> ConceptMap:
        return cast("ConceptMap", super().from_xml(element))


@dataclass
class VariableMap(_GenericMap):
    """Representation of ``cm:VariableMap`` maintainables."""

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "VariableMap")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp")

    @classmethod
    def from_xml(cls, element: Element) -> VariableMap:
        return cast("VariableMap", super().from_xml(element))


@dataclass
class QuestionMap(_GenericMap):
    """Representation of ``cm:QuestionMap`` maintainables."""

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "QuestionMap")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp")

    @classmethod
    def from_xml(cls, element: Element) -> QuestionMap:
        return cast("QuestionMap", super().from_xml(element))


@dataclass
class UsageGuide:
    """Representation of ``d:UsageGuide`` instructions."""

    examples: list[InternationalString] = field(default_factory=list)
    restrictions: list[InternationalString] = field(default_factory=list)
    recommendations: list[InternationalString] = field(default_factory=list)
    command_codes: list[Element] = field(default_factory=list)
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "UsageGuide")

    @classmethod
    def from_xml(cls, element: Element) -> UsageGuide:
        if element.tag != cls.TAG:
            raise ValueError("Expected a datacollection:UsageGuide element.")
        recognized = {
            qn(DATA_COLLECTION_NS, "UsageExample"),
            qn(DATA_COLLECTION_NS, "UsageRestrictions"),
            qn(DATA_COLLECTION_NS, "UsageRecommendations"),
            qn(REUSABLE_NS, "CommandCode"),
        }
        examples: list[InternationalString] = []
        for container in _iter_children(
            element, "UsageExample", namespace=DATA_COLLECTION_NS
        ):
            examples.extend(InternationalString.from_container(container))
        restrictions: list[InternationalString] = []
        for container in _iter_children(
            element, "UsageRestrictions", namespace=DATA_COLLECTION_NS
        ):
            restrictions.extend(InternationalString.from_container(container))
        recommendations: list[InternationalString] = []
        for container in _iter_children(
            element, "UsageRecommendations", namespace=DATA_COLLECTION_NS
        ):
            recommendations.extend(InternationalString.from_container(container))
        command_codes = [
            clone_element(node)
            for node in _iter_children(element, "CommandCode", namespace=REUSABLE_NS)
        ]
        other = [
            clone_element(child) for child in element if child.tag not in recognized
        ]
        return cls(
            examples=examples,
            restrictions=restrictions,
            recommendations=recommendations,
            command_codes=command_codes,
            other_elements=other,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.examples:
            container = create_element(qn(DATA_COLLECTION_NS, "UsageExample"))
            for value in self.examples:
                container.append(value.to_child())
            element.append(container)
        if self.restrictions:
            container = create_element(qn(DATA_COLLECTION_NS, "UsageRestrictions"))
            for value in self.restrictions:
                container.append(value.to_child())
            element.append(container)
        if self.recommendations:
            container = create_element(qn(DATA_COLLECTION_NS, "UsageRecommendations"))
            for value in self.recommendations:
                container.append(value.to_child())
            element.append(container)
        for node in self.command_codes:
            element.append(clone_element(node))
        for child in self.other_elements:
            element.append(clone_element(child))
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class StandardWeight:
    """Representation of ``d:StandardWeight`` entries."""

    urn: str | None = None
    agency: str | None = None
    identifier: str | None = None
    version: str | None = None
    user_ids: list[UserID] = field(default_factory=list)
    user_attribute_pairs: list[UserAttributePair] = field(default_factory=list)
    standard_weight_value: float | None = None
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "StandardWeight")

    @classmethod
    def from_xml(cls, element: Element) -> StandardWeight:
        if element.tag != cls.TAG:
            raise ValueError("Expected a datacollection:StandardWeight element.")
        recognized = {
            qn(REUSABLE_NS, "URN"),
            qn(REUSABLE_NS, "Agency"),
            qn(REUSABLE_NS, "ID"),
            qn(REUSABLE_NS, "Version"),
            qn(REUSABLE_NS, "UserID"),
            qn(REUSABLE_NS, "UserAttributePair"),
            qn(DATA_COLLECTION_NS, "StandardWeightValue"),
        }
        user_ids = [
            UserID.from_xml(node)
            for node in _iter_children(element, "UserID", namespace=REUSABLE_NS)
        ]
        user_attribute_pairs = [
            UserAttributePair.from_xml(node)
            for node in _iter_children(
                element, "UserAttributePair", namespace=REUSABLE_NS
            )
        ]
        value_el = element.find(qn(DATA_COLLECTION_NS, "StandardWeightValue"))
        weight_value = None
        if value_el is not None and value_el.text is not None:
            try:
                weight_value = float(value_el.text)
            except ValueError:
                weight_value = None
        other = [
            clone_element(child) for child in element if child.tag not in recognized
        ]
        return cls(
            urn=_get_text(element, qn(REUSABLE_NS, "URN")),
            agency=_get_text(element, qn(REUSABLE_NS, "Agency")),
            identifier=_get_text(element, qn(REUSABLE_NS, "ID")),
            version=_get_text(element, qn(REUSABLE_NS, "Version")),
            user_ids=user_ids,
            user_attribute_pairs=user_attribute_pairs,
            standard_weight_value=weight_value,
            other_elements=other,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.urn:
            urn_el = create_element(qn(REUSABLE_NS, "URN"))
            urn_el.text = self.urn
            element.append(urn_el)
        for child in build_identification_elements(
            agency=self.agency,
            identifier=self.identifier,
            version=self.version,
        ):
            element.append(child)
        for user_id in self.user_ids:
            element.append(user_id.to_xml())
        for pair in self.user_attribute_pairs:
            element.append(pair.to_xml())
        if self.standard_weight_value is not None:
            value_el = create_element(qn(DATA_COLLECTION_NS, "StandardWeightValue"))
            value_el.text = str(self.standard_weight_value)
            element.append(value_el)
        for child in self.other_elements:
            element.append(clone_element(child))
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class Weighting(VersionableMaintainableBase):
    """Representation of ``d:Weighting`` descriptions."""

    type_of_weighting: CodeValue | None = None
    weighting_methodology_references: list[Reference] = field(default_factory=list)
    analysis_unit: CodeValue | None = None
    usage_guide: UsageGuide | None = None
    standard_weights: list[StandardWeight] = field(default_factory=list)
    based_on_sample_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Weighting")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_weighting": (
            qn(DATA_COLLECTION_NS, "TypeOfWeighting"),
            "code_value",
            False,
        ),
        "weighting_methodology_references": (
            qn(DATA_COLLECTION_NS, "WeightingMethodologyReference"),
            "reference",
            True,
        ),
        "analysis_unit": (qn(REUSABLE_NS, "AnalysisUnit"), "code_value", False),
        "usage_guide": (qn(DATA_COLLECTION_NS, "UsageGuide"), "element", False),
        "standard_weights": (qn(DATA_COLLECTION_NS, "StandardWeight"), "element", True),
        "based_on_sample_references": (
            qn(DATA_COLLECTION_NS, "BasedOnSampleReference"),
            "reference",
            True,
        ),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "VersionResponsibility"),
        qn(REUSABLE_NS, "VersionResponsibilityReference"),
        qn(REUSABLE_NS, "VersionRationale"),
        qn(REUSABLE_NS, "BasedOnObject"),
        qn(REUSABLE_NS, "RelatedOtherMaterialReference"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(DATA_COLLECTION_NS, "TypeOfWeighting"),
        qn(REUSABLE_NS, "Description"),
        qn(DATA_COLLECTION_NS, "WeightingMethodologyReference"),
        qn(REUSABLE_NS, "AnalysisUnit"),
        qn(DATA_COLLECTION_NS, "UsageGuide"),
        qn(DATA_COLLECTION_NS, "StandardWeight"),
        qn(DATA_COLLECTION_NS, "BasedOnSampleReference"),
    ]

    @classmethod
    def from_xml(cls, element: Element) -> Weighting:
        recognized = {
            qn(DATA_COLLECTION_NS, "TypeOfWeighting"),
            qn(REUSABLE_NS, "Description"),
            qn(DATA_COLLECTION_NS, "WeightingMethodologyReference"),
            qn(REUSABLE_NS, "AnalysisUnit"),
            qn(DATA_COLLECTION_NS, "UsageGuide"),
            qn(DATA_COLLECTION_NS, "StandardWeight"),
            qn(DATA_COLLECTION_NS, "BasedOnSampleReference"),
        }
        data: dict[str, Any] = dict(
            cls._collect_versionable_common(element, recognized_children=recognized)
        )
        type_el = element.find(qn(DATA_COLLECTION_NS, "TypeOfWeighting"))
        type_of_weighting = None
        if type_el is not None:
            type_of_weighting = CodeValue.from_xml(type_el)
        methodology_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                element, "WeightingMethodologyReference", namespace=DATA_COLLECTION_NS
            )
        ]
        analysis_unit_el = element.find(qn(REUSABLE_NS, "AnalysisUnit"))
        analysis_unit = None
        if analysis_unit_el is not None:
            analysis_unit = CodeValue.from_xml(analysis_unit_el)
        usage_guide_el = element.find(qn(DATA_COLLECTION_NS, "UsageGuide"))
        usage_guide = (
            UsageGuide.from_xml(usage_guide_el) if usage_guide_el is not None else None
        )
        standard_weights = [
            StandardWeight.from_xml(node)
            for node in _iter_children(
                element, "StandardWeight", namespace=DATA_COLLECTION_NS
            )
        ]
        based_on_sample_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                element, "BasedOnSampleReference", namespace=DATA_COLLECTION_NS
            )
        ]
        data.update(
            {
                "type_of_weighting": type_of_weighting,
                "weighting_methodology_references": methodology_references,
                "analysis_unit": analysis_unit,
                "usage_guide": usage_guide,
                "standard_weights": standard_weights,
                "based_on_sample_references": based_on_sample_references,
            }
        )
        return cls(**data)

    def to_xml(self) -> Element:
        element = self._build_base_element()
        description_nodes = element.findall(qn(REUSABLE_NS, "Description"))
        for node in description_nodes:
            element.remove(node)
        self._append_versionable_common(element)
        if self.type_of_weighting is not None:
            element.append(
                self.type_of_weighting.to_xml(
                    "TypeOfWeighting", namespace=DATA_COLLECTION_NS
                )
            )
        for node in description_nodes:
            element.append(node)
        for reference in self.weighting_methodology_references:
            element.append(
                reference.to_xml(
                    "WeightingMethodologyReference", namespace=DATA_COLLECTION_NS
                )
            )
        if self.analysis_unit is not None:
            element.append(
                self.analysis_unit.to_xml("AnalysisUnit", namespace=REUSABLE_NS)
            )
        if self.usage_guide is not None:
            element.append(self.usage_guide.to_xml())
        for weight in self.standard_weights:
            element.append(weight.to_xml())
        for reference in self.based_on_sample_references:
            element.append(
                reference.to_xml("BasedOnSampleReference", namespace=DATA_COLLECTION_NS)
            )
        self._append_other_elements(element)
        cleanup_namespaces(
            element,
            {
                "d": DATA_COLLECTION_NS,
                "r": REUSABLE_NS,
            },
        )
        return element


@dataclass
class WeightingMethodology(WeightingMethodologyFields):
    """Representation of ``d:WeightingMethodology`` descriptions."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "WeightingMethodology")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")


@dataclass
class PhysicalInstanceGroup(PhysicalInstanceGroupFields):
    """Maintainable representation of ``pi:PhysicalInstanceGroup`` modules."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "PhysicalInstanceGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi", "r")
