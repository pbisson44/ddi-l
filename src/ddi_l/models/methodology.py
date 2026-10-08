"""Wrappers for DDI Methodology maintainables and versionable items."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import ClassVar

from .._etree import Element, create_element
from ..constants import DATA_COLLECTION_NS, METHODOLOGY_NS, REUSABLE_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from .base import (
    CodeValue,
    InternationalString,
    MaintainableBase,
    Reference,
    clone_element,
    qn,
)
from .datacollection import VersionableMaintainableBase

__all__ = [
    "Methodology",
    "MethodologyItem",
    "MethodologyScheme",
    "ReviewEvent",
]


_ITEM_LOCAL_NAMES: tuple[str, ...] = (
    "MethodologyItem",
    "DataCollectionMethodology",
    "TimeMethod",
    "SamplingProcedure",
    "DeviationFromSampleDesign",
    "WeightingMethodology",
)


def _normalize_methodology_element(
    element: Element,
    local_name: str,
    *,
    target: str = METHODOLOGY_NS,
) -> Element:
    """Return ``element`` retagged into ``target`` when it is the other spelling.

    ``Methodology`` is a real DDI 3.3 element in ``ddi:datacollection:3_3``,
    so it normalizes *towards* that namespace. The surrounding
    ``MethodologyItem`` / ``ReviewEvent`` types have no counterpart in any DDI
    release and keep the library's own namespace, so they normalize the other
    way. Hence the explicit target rather than one fixed direction.
    """
    other = DATA_COLLECTION_NS if target == METHODOLOGY_NS else METHODOLOGY_NS
    if element.tag == qn(target, local_name):
        return element
    if element.tag == qn(other, local_name):
        normalized = clone_element(element)
        normalized.tag = qn(target, local_name)
        return normalized
    return element


def _iter_children(
    element: Element, local_name: str, *, namespaces: Iterable[str]
) -> list[Element]:
    """Return children named ``local_name`` in any of ``namespaces``."""
    matches: list[Element] = []
    for namespace in namespaces:
        matches.extend(element.findall(qn(namespace, local_name)))
    return matches


@dataclass
class ReviewEvent(VersionableMaintainableBase):
    """Representation of ``m:ReviewEvent`` provenance statements."""

    names: list[InternationalString] = field(default_factory=list)
    event_type: CodeValue | None = None
    event_dates: list[Element] = field(default_factory=list)
    organization_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(METHODOLOGY_NS, "ReviewEvent")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("m", "r")

    @classmethod
    def from_xml(cls, element: Element) -> ReviewEvent:
        normalized = _normalize_methodology_element(element, "ReviewEvent")
        recognized = {
            qn(METHODOLOGY_NS, "ReviewEventName"),
            qn(METHODOLOGY_NS, "TypeOfReviewEvent"),
            qn(METHODOLOGY_NS, "EventDate"),
            qn(REUSABLE_NS, "OrganizationReference"),
        }
        data = cls._collect_versionable_common(
            normalized, recognized_children=recognized
        )
        names: list[InternationalString] = []
        for container in _iter_children(
            normalized, "ReviewEventName", namespaces=(METHODOLOGY_NS,)
        ):
            names.extend(InternationalString.from_container(container))
        event_type_el = normalized.find(qn(METHODOLOGY_NS, "TypeOfReviewEvent"))
        event_type = (
            CodeValue.from_xml(event_type_el) if event_type_el is not None else None
        )
        event_dates = [
            clone_element(node)
            for node in _iter_children(
                normalized, "EventDate", namespaces=(METHODOLOGY_NS,)
            )
        ]
        organization_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                normalized, "OrganizationReference", namespaces=(REUSABLE_NS,)
            )
        ]
        return cls(
            names=names,
            event_type=event_type,
            event_dates=event_dates,
            organization_references=organization_references,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_versionable_common(element)
        for name in self.names:
            container = create_element(qn(METHODOLOGY_NS, "ReviewEventName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        if self.event_type is not None:
            element.append(
                self.event_type.to_xml("TypeOfReviewEvent", namespace=METHODOLOGY_NS)
            )
        for node in self.event_dates:
            element.append(clone_element(node))
        for reference in self.organization_references:
            element.append(
                reference.to_xml("OrganizationReference", namespace=REUSABLE_NS)
            )
        self._append_other_elements(element)
        return element


@dataclass
class MethodologyItem(VersionableMaintainableBase):
    """Flexible wrapper for methodology statements and sampling details."""

    item_kind: str = "MethodologyItem"
    names: list[InternationalString] = field(default_factory=list)
    classification: CodeValue | None = None
    statements: list[InternationalString] = field(default_factory=list)
    sampling_plan_reference: Reference | None = None
    sample_reference: Reference | None = None
    review_events: list[ReviewEvent] = field(default_factory=list)
    review_event_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(METHODOLOGY_NS, "MethodologyItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("m", "d", "r")

    @classmethod
    def from_xml(cls, element: Element) -> MethodologyItem:
        local_name = element.tag.split("}")[-1]
        if local_name != "MethodologyItem" and local_name in _ITEM_LOCAL_NAMES:
            normalized = clone_element(element)
            normalized.tag = cls.TAG
        else:
            normalized = _normalize_methodology_element(element, "MethodologyItem")
        recognized = {
            qn(METHODOLOGY_NS, "MethodologyItemName"),
            qn(METHODOLOGY_NS, "MethodologyStatement"),
            qn(METHODOLOGY_NS, "ReviewEvent"),
            qn(METHODOLOGY_NS, "ReviewEventReference"),
            qn(METHODOLOGY_NS, "TypeOfMethodologyItem"),
            qn(DATA_COLLECTION_NS, "TypeOfDataCollectionMethodology"),
            qn(DATA_COLLECTION_NS, "TypeOfTimeMethod"),
            qn(DATA_COLLECTION_NS, "TypeOfSamplingProcedure"),
            qn(DATA_COLLECTION_NS, "TypeOfDeviationFromSampleDesign"),
            qn(DATA_COLLECTION_NS, "SamplingPlanReference"),
            qn(DATA_COLLECTION_NS, "SampleReference"),
            qn(METHODOLOGY_NS, "TypeOfReviewEvent"),
        }
        data = cls._collect_versionable_common(
            normalized, recognized_children=recognized
        )

        names: list[InternationalString] = []
        for container in _iter_children(
            normalized, "MethodologyItemName", namespaces=(METHODOLOGY_NS,)
        ):
            names.extend(InternationalString.from_container(container))

        statements: list[InternationalString] = []
        for container in _iter_children(
            normalized, "MethodologyStatement", namespaces=(METHODOLOGY_NS,)
        ):
            statements.extend(InternationalString.from_container(container))

        classification = None
        type_tag_map = {
            "MethodologyItem": qn(METHODOLOGY_NS, "TypeOfMethodologyItem"),
            "DataCollectionMethodology": qn(
                DATA_COLLECTION_NS, "TypeOfDataCollectionMethodology"
            ),
            "TimeMethod": qn(DATA_COLLECTION_NS, "TypeOfTimeMethod"),
            "SamplingProcedure": qn(DATA_COLLECTION_NS, "TypeOfSamplingProcedure"),
            "DeviationFromSampleDesign": qn(
                DATA_COLLECTION_NS, "TypeOfDeviationFromSampleDesign"
            ),
            "WeightingMethodology": qn(
                DATA_COLLECTION_NS, "TypeOfWeightingMethodology"
            ),
        }
        type_tag = type_tag_map.get(local_name) or type_tag_map["MethodologyItem"]
        classification_el = normalized.find(type_tag)
        if classification_el is None and type_tag != type_tag_map["MethodologyItem"]:
            # Some payloads use the methodology namespace for type elements.
            fallback = qn(METHODOLOGY_NS, type_tag.split("}")[-1])
            classification_el = normalized.find(fallback)
        if classification_el is not None:
            classification = CodeValue.from_xml(classification_el)

        sampling_plan_reference = None
        sample_reference = None
        if local_name == "SamplingProcedure":
            plan_el = normalized.find(qn(DATA_COLLECTION_NS, "SamplingPlanReference"))
            if plan_el is not None:
                sampling_plan_reference = Reference.from_xml(plan_el)
            sample_el = normalized.find(qn(DATA_COLLECTION_NS, "SampleReference"))
            if sample_el is not None:
                sample_reference = Reference.from_xml(sample_el)

        review_events = [
            ReviewEvent.from_xml(node)
            for node in _iter_children(
                normalized, "ReviewEvent", namespaces=(METHODOLOGY_NS,)
            )
        ]
        review_event_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                normalized, "ReviewEventReference", namespaces=(METHODOLOGY_NS,)
            )
        ]

        instance = cls(
            item_kind=local_name,
            names=names,
            classification=classification,
            statements=statements,
            sampling_plan_reference=sampling_plan_reference,
            sample_reference=sample_reference,
            review_events=review_events,
            review_event_references=review_event_references,
            **data,
        )
        return instance

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_versionable_common(element)
        for name in self.names:
            container = create_element(qn(METHODOLOGY_NS, "MethodologyItemName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        if self.statements:
            for statement in self.statements:
                container = create_element(qn(METHODOLOGY_NS, "MethodologyStatement"))
                container.append(statement.to_child())
                element.append(container)
        if self.classification is not None:
            if self.item_kind == "MethodologyItem":
                element.append(
                    self.classification.to_xml(
                        "TypeOfMethodologyItem", namespace=METHODOLOGY_NS
                    )
                )
            else:
                tag_map = {
                    "DataCollectionMethodology": "TypeOfDataCollectionMethodology",
                    "TimeMethod": "TypeOfTimeMethod",
                    "SamplingProcedure": "TypeOfSamplingProcedure",
                    "DeviationFromSampleDesign": "TypeOfDeviationFromSampleDesign",
                    "WeightingMethodology": "TypeOfWeightingMethodology",
                }
                local = tag_map.get(self.item_kind)
                if local:
                    element.append(
                        self.classification.to_xml(local, namespace=DATA_COLLECTION_NS)
                    )
                else:
                    element.append(
                        self.classification.to_xml(
                            "TypeOfMethodologyItem", namespace=METHODOLOGY_NS
                        )
                    )
        if self.sampling_plan_reference is not None:
            element.append(
                self.sampling_plan_reference.to_xml(
                    "SamplingPlanReference", namespace=DATA_COLLECTION_NS
                )
            )
        if self.sample_reference is not None:
            element.append(
                self.sample_reference.to_xml(
                    "SampleReference", namespace=DATA_COLLECTION_NS
                )
            )
        for review_event in self.review_events:
            element.append(review_event.to_xml())
        for reference in self.review_event_references:
            element.append(
                reference.to_xml("ReviewEventReference", namespace=METHODOLOGY_NS)
            )
        self._append_other_elements(element)

        if self.item_kind != "MethodologyItem":
            target = qn(
                DATA_COLLECTION_NS
                if self.item_kind in _ITEM_LOCAL_NAMES
                else METHODOLOGY_NS,
                self.item_kind,
            )
            element.tag = target
        return element


@dataclass
class Methodology(VersionableMaintainableBase):
    """Maintainable representation of ``m:Methodology`` entries."""

    names: list[InternationalString] = field(default_factory=list)
    methodology_items: list[MethodologyItem] = field(default_factory=list)
    methodology_item_references: list[Reference] = field(default_factory=list)
    review_events: list[ReviewEvent] = field(default_factory=list)
    review_event_references: list[Reference] = field(default_factory=list)
    quality_statement_references: list[Reference] = field(default_factory=list)

    # DDI 3.3 declares <Methodology> in ddi:datacollection:3_3. Emitting it
    # into the library's own namespace produced files no DDI tool could read.
    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Methodology")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d", "m", "r")

    @classmethod
    def from_xml(cls, element: Element) -> Methodology:
        normalized = _normalize_methodology_element(
            element, "Methodology", target=DATA_COLLECTION_NS
        )
        recognized = {
            qn(METHODOLOGY_NS, "MethodologyName"),
            qn(DATA_COLLECTION_NS, "MethodologyName"),
            qn(METHODOLOGY_NS, "MethodologyItem"),
            qn(DATA_COLLECTION_NS, "DataCollectionMethodology"),
            qn(DATA_COLLECTION_NS, "TimeMethod"),
            qn(DATA_COLLECTION_NS, "SamplingProcedure"),
            qn(DATA_COLLECTION_NS, "DeviationFromSampleDesign"),
            qn(DATA_COLLECTION_NS, "WeightingMethodology"),
            qn(METHODOLOGY_NS, "MethodologyItemReference"),
            qn(METHODOLOGY_NS, "ReviewEvent"),
            qn(METHODOLOGY_NS, "ReviewEventReference"),
            qn(REUSABLE_NS, "QualityStatementReference"),
        }
        data = cls._collect_versionable_common(
            normalized, recognized_children=recognized
        )
        names: list[InternationalString] = []
        for container in _iter_children(
            normalized,
            "MethodologyName",
            namespaces=(METHODOLOGY_NS, DATA_COLLECTION_NS),
        ):
            names.extend(InternationalString.from_container(container))
        methodology_items: list[MethodologyItem] = []
        for child in normalized:
            if child.tag.split("}")[-1] in _ITEM_LOCAL_NAMES:
                methodology_items.append(MethodologyItem.from_xml(child))
        methodology_item_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                normalized, "MethodologyItemReference", namespaces=(METHODOLOGY_NS,)
            )
        ]
        review_events = [
            ReviewEvent.from_xml(node)
            for node in _iter_children(
                normalized, "ReviewEvent", namespaces=(METHODOLOGY_NS,)
            )
        ]
        review_event_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                normalized, "ReviewEventReference", namespaces=(METHODOLOGY_NS,)
            )
        ]
        quality_statement_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                normalized, "QualityStatementReference", namespaces=(REUSABLE_NS,)
            )
        ]
        return cls(
            names=names,
            methodology_items=methodology_items,
            methodology_item_references=methodology_item_references,
            review_events=review_events,
            review_event_references=review_event_references,
            quality_statement_references=quality_statement_references,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_versionable_common(element)
        for name in self.names:
            container = create_element(qn(METHODOLOGY_NS, "MethodologyName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        for item in self.methodology_items:
            element.append(item.to_xml())
        for reference in self.methodology_item_references:
            element.append(
                reference.to_xml("MethodologyItemReference", namespace=METHODOLOGY_NS)
            )
        for event in self.review_events:
            element.append(event.to_xml())
        for reference in self.review_event_references:
            element.append(
                reference.to_xml("ReviewEventReference", namespace=METHODOLOGY_NS)
            )
        for reference in self.quality_statement_references:
            element.append(
                reference.to_xml("QualityStatementReference", namespace=REUSABLE_NS)
            )
        self._append_other_elements(element)
        return element


@dataclass
class MethodologyScheme(MaintainableBase):
    """Maintainable representation of ``m:MethodologyScheme`` collections."""

    names: list[InternationalString] = field(default_factory=list)
    methodology_references: list[Reference] = field(default_factory=list)
    methodologies: list[Methodology] = field(default_factory=list)
    review_events: list[ReviewEvent] = field(default_factory=list)
    review_event_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(METHODOLOGY_NS, "MethodologyScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("m", "r")

    def __post_init__(self) -> None:
        def _suffix(base: str) -> Callable[[int, MaintainableBase], str | None]:
            return lambda index, _child: self._default_child_suffix(base, index)

        self._propagate_child_identification(
            self.methodologies,
            identifier_suffix_factory=_suffix("methodology"),
        )
        self._propagate_child_identification(
            self.review_events,
            identifier_suffix_factory=_suffix("review-event"),
        )

    @classmethod
    def from_xml(cls, element: Element) -> MethodologyScheme:
        normalized = _normalize_methodology_element(element, "MethodologyScheme")
        recognized = {
            qn(METHODOLOGY_NS, "MethodologySchemeName"),
            qn(METHODOLOGY_NS, "Methodology"),
            qn(DATA_COLLECTION_NS, "Methodology"),
            qn(METHODOLOGY_NS, "MethodologyReference"),
            qn(METHODOLOGY_NS, "ReviewEvent"),
            qn(METHODOLOGY_NS, "ReviewEventReference"),
        }
        data = cls._collect_common(normalized, recognized_children=recognized)
        names: list[InternationalString] = []
        for container in _iter_children(
            normalized, "MethodologySchemeName", namespaces=(METHODOLOGY_NS,)
        ):
            names.extend(InternationalString.from_container(container))
        methodologies = [
            Methodology.from_xml(node)
            for node in _iter_children(
                normalized,
                "Methodology",
                namespaces=(METHODOLOGY_NS, DATA_COLLECTION_NS),
            )
        ]
        methodology_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                normalized, "MethodologyReference", namespaces=(METHODOLOGY_NS,)
            )
        ]
        review_events = [
            ReviewEvent.from_xml(node)
            for node in _iter_children(
                normalized, "ReviewEvent", namespaces=(METHODOLOGY_NS,)
            )
        ]
        review_event_references = [
            Reference.from_xml(node)
            for node in _iter_children(
                normalized, "ReviewEventReference", namespaces=(METHODOLOGY_NS,)
            )
        ]
        return cls(
            names=names,
            methodology_references=methodology_references,
            methodologies=methodologies,
            review_events=review_events,
            review_event_references=review_event_references,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        for name in self.names:
            container = create_element(qn(METHODOLOGY_NS, "MethodologySchemeName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        for methodology in self.methodologies:
            element.append(methodology.to_xml())
        for reference in self.methodology_references:
            element.append(
                reference.to_xml("MethodologyReference", namespace=METHODOLOGY_NS)
            )
        for event in self.review_events:
            element.append(event.to_xml())
        for reference in self.review_event_references:
            element.append(
                reference.to_xml("ReviewEventReference", namespace=METHODOLOGY_NS)
            )
        self._append_other_elements(element)
        return element
