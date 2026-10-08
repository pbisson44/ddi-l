"""Wrappers for reusable logical product classification structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from .._etree import Element, create_element
from ..constants import LOGICAL_PRODUCT_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.logicalproduct import (
    ClassificationFamilyFields,
    ClassificationItemFields,
    ClassificationSeriesFields,
    StatisticalClassificationFields,
)
from .base import (
    MaintainableBase,
    Reference,
    apply_other_attributes,
    clone_element,
    collect_other_attributes,
    qn,
)

__all__ = [
    "ClassificationFamily",
    "ClassificationItem",
    "ClassificationLevelContext",
    "ClassificationScheme",
    "ClassificationSeries",
]


CLASSIFICATION_NS = LOGICAL_PRODUCT_NS


@dataclass
class ClassificationItem(ClassificationItemFields):
    """Representation of ``l:ClassificationItem`` entries."""

    TAG: ClassVar[str] = qn(CLASSIFICATION_NS, "ClassificationItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")


@dataclass
class ClassificationLevelContext:
    """Representation of ``l:LevelContext`` structures grouping classification items."""

    level_number: str | None = None
    classification_level: Element | None = None
    classification_level_reference: Reference | None = None
    classification_items: list[ClassificationItem] = field(default_factory=list)
    classification_item_references: list[Reference] = field(default_factory=list)
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(CLASSIFICATION_NS, "LevelContext")

    @classmethod
    def from_xml(cls, element: Element) -> ClassificationLevelContext:
        if element.tag != cls.TAG:
            raise ValueError("Expected a logicalproduct:LevelContext element.")
        recognized = {
            qn(CLASSIFICATION_NS, "LevelNumber"),
            qn(CLASSIFICATION_NS, "ClassificationLevel"),
            qn(CLASSIFICATION_NS, "ClassificationLevelReference"),
            qn(CLASSIFICATION_NS, "ClassificationItem"),
            qn(CLASSIFICATION_NS, "ClassificationItemReference"),
        }
        level_number_el = element.find(qn(CLASSIFICATION_NS, "LevelNumber"))
        level_el = element.find(qn(CLASSIFICATION_NS, "ClassificationLevel"))
        level_ref_el = element.find(
            qn(CLASSIFICATION_NS, "ClassificationLevelReference")
        )
        classification_items = [
            ClassificationItem.from_xml(node)
            for node in element.findall(qn(CLASSIFICATION_NS, "ClassificationItem"))
        ]
        classification_item_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(CLASSIFICATION_NS, "ClassificationItemReference")
            )
        ]
        other_elements = [
            clone_element(child) for child in element if child.tag not in recognized
        ]
        return cls(
            level_number=level_number_el.text if level_number_el is not None else None,
            classification_level=clone_element(level_el)
            if level_el is not None
            else None,
            classification_level_reference=(
                Reference.from_xml(level_ref_el) if level_ref_el is not None else None
            ),
            classification_items=classification_items,
            classification_item_references=classification_item_references,
            other_elements=other_elements,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.level_number is not None:
            level_number_el = create_element(qn(CLASSIFICATION_NS, "LevelNumber"))
            level_number_el.text = self.level_number
            element.append(level_number_el)
        if (
            self.classification_level is not None
            and self.classification_level_reference is not None
        ):
            raise ValueError(
                "Level context cannot contain both inline"
                " ClassificationLevel and a reference."
            )
        if self.classification_level is not None:
            element.append(clone_element(self.classification_level))
        elif self.classification_level_reference is not None:
            element.append(
                self.classification_level_reference.to_xml(
                    "ClassificationLevelReference", namespace=CLASSIFICATION_NS
                )
            )
        for item in self.classification_items:
            element.append(item.to_xml())
        for reference in self.classification_item_references:
            element.append(
                reference.to_xml(
                    "ClassificationItemReference", namespace=CLASSIFICATION_NS
                )
            )
        for node in self.other_elements:
            element.append(clone_element(node))
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class ClassificationScheme(StatisticalClassificationFields):
    """Maintainable wrapper for ``l:StatisticalClassification`` structures."""

    TAG: ClassVar[str] = qn(CLASSIFICATION_NS, "StatisticalClassification")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")

    @property
    def classification_items(self) -> list[MaintainableBase]:
        """Flatten classification items across level contexts for convenience."""
        items: list[MaintainableBase] = []
        for context_el in self.level_contexts:
            for child in context_el.findall(
                qn(CLASSIFICATION_NS, "ClassificationItem")
            ):
                items.append(ClassificationItem.from_xml(child))
        return items


@dataclass
class ClassificationSeries(ClassificationSeriesFields):
    """Maintainable wrapper for ``l:ClassificationSeries`` objects."""

    TAG: ClassVar[str] = qn(CLASSIFICATION_NS, "ClassificationSeries")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")


@dataclass
class ClassificationFamily(ClassificationFamilyFields):
    """Maintainable wrapper for ``l:ClassificationFamily`` objects."""

    TAG: ClassVar[str] = qn(CLASSIFICATION_NS, "ClassificationFamily")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("l")
