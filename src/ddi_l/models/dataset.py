"""High-level wrapper for ``ds:DataSet`` (inline data values).

A DataSet stores actual data inline (rather than referencing an external file).
Like ``RecordLayout`` it is a ``BaseRecordLayout`` and lives in a
``RecordLayoutScheme``. The generated base for this type is emitted in the wrong
namespace, so this wrapper builds the element directly in ``ddi:dataset:3_3``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from .._etree import Element, create_element
from ..constants import DATASET_NS, PHYSICAL_DATA_PRODUCT_NS, REUSABLE_NS
from .base import (
    InternationalString,
    Reference,
    apply_other_attributes,
    clone_element,
    collect_other_attributes,
    qn,
)

__all__ = ["DataSet"]


@dataclass
class DataSet:
    """Inline data: variable values stored directly in the DDI document.

    Build one with :meth:`ddi_l.document.Document.add_dataset` and add values
    with :meth:`add_item_value`.
    """

    agency: str | None = None
    identifier: str | None = None
    version: str | None = None
    names: list[InternationalString] = field(default_factory=list)
    physical_structure_link_reference: Reference | None = None
    physical_record_segment_used: str | None = None
    array_base: int = 0
    item_values: list[Element] = field(default_factory=list)
    variable_order: list[Reference] = field(default_factory=list)
    records: list[Element] = field(default_factory=list)
    variable_items: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(DATASET_NS, "DataSet")

    def add_item_value(
        self, variable_reference: Reference, *, record: str | int, value: str
    ) -> Element:
        """Record one value: ``variable`` in ``record`` has ``value``. Returns it.

        Populates an ``ItemSet`` (values keyed by variable and record).
        """
        item_value = create_element(qn(DATASET_NS, "ItemValue"))
        item_value.append(
            variable_reference.to_xml("VariableReference", namespace=REUSABLE_NS)
        )
        record_el = create_element(qn(DATASET_NS, "RecordReference"))
        record_el.text = str(record)
        item_value.append(record_el)
        value_el = create_element(qn(REUSABLE_NS, "Value"))
        value_el.text = str(value)
        item_value.append(value_el)
        self.item_values.append(item_value)
        return item_value

    def set_variable_order(self, variable_references: list[Reference]) -> None:
        """Set the column order for :meth:`add_record` (a ``RecordSet``)."""
        self.variable_order = list(variable_references)

    def add_record(self, values: list[str]) -> Element:
        """Add one record (a row of values) to a ``RecordSet``. Returns it.

        Values are positional, matching :meth:`set_variable_order`.
        """
        record = create_element(qn(DATASET_NS, "Record"))
        for value in values:
            value_el = create_element(qn(REUSABLE_NS, "Value"))
            value_el.text = str(value)
            record.append(value_el)
        self.records.append(record)
        return record

    def add_variable_item(
        self, variable_reference: Reference | None, values: list[str]
    ) -> Element:
        """Add all values for one variable (a ``VariableSet`` column). Returns it."""
        item = create_element(qn(DATASET_NS, "VariableItem"))
        if variable_reference is not None:
            item.append(
                variable_reference.to_xml("VariableReference", namespace=REUSABLE_NS)
            )
        for value in values:
            value_el = create_element(qn(REUSABLE_NS, "Value"))
            value_el.text = str(value)
            item.append(value_el)
        self.variable_items.append(item)
        return item

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        for tag, content in (
            ("Agency", self.agency),
            ("ID", self.identifier),
            ("Version", self.version),
        ):
            if content is not None:
                child = create_element(qn(REUSABLE_NS, tag))
                child.text = content
                element.append(child)
        if self.physical_structure_link_reference is not None:
            link = self.physical_structure_link_reference.to_xml(
                "PhysicalStructureLinkReference", namespace=PHYSICAL_DATA_PRODUCT_NS
            )
            if self.physical_record_segment_used is not None:
                segment = create_element(
                    qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalRecordSegmentUsed")
                )
                segment.text = self.physical_record_segment_used
                link.append(segment)
            element.append(link)
        array_base = create_element(qn(REUSABLE_NS, "ArrayBase"))
        array_base.text = str(self.array_base)
        element.append(array_base)
        for name in self.names:
            name_el = create_element(qn(DATASET_NS, "DataSetName"))
            name_el.append(name.to_child(child_tag="String"))
            element.append(name_el)
        # RecordSet, ItemSet, and VariableSet are mutually exclusive (an XSD
        # choice); emit whichever form has been populated.
        if self.records:
            record_set = create_element(qn(DATASET_NS, "RecordSet"))
            if self.variable_order:
                order = create_element(qn(DATASET_NS, "VariableOrder"))
                for reference in self.variable_order:
                    order.append(
                        reference.to_xml("VariableReference", namespace=REUSABLE_NS)
                    )
                record_set.append(order)
            for record in self.records:
                record_set.append(clone_element(record))
            element.append(record_set)
        elif self.item_values:
            item_set = create_element(qn(DATASET_NS, "ItemSet"))
            for item_value in self.item_values:
                item_set.append(clone_element(item_value))
            element.append(item_set)
        elif self.variable_items:
            variable_set = create_element(qn(DATASET_NS, "VariableSet"))
            for variable_item in self.variable_items:
                variable_set.append(clone_element(variable_item))
            element.append(variable_set)
        apply_other_attributes(element, self.other_attributes)
        return element

    @classmethod
    def from_xml(cls, element: Element) -> DataSet:
        def _text(ns: str, tag: str) -> str | None:
            child = element.find(qn(ns, tag))
            return child.text if child is not None else None

        link_el = element.find(
            qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference")
        )
        segment_used = None
        link_reference = None
        if link_el is not None:
            link_reference = Reference.from_xml(link_el)
            segment_el = link_el.find(
                qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalRecordSegmentUsed")
            )
            if segment_el is not None:
                segment_used = segment_el.text
        array_base_text = _text(REUSABLE_NS, "ArrayBase")
        names = [
            name
            for container in element.findall(qn(DATASET_NS, "DataSetName"))
            for name in InternationalString.from_container(container)
        ]
        item_values: list[Element] = []
        for item_set in element.findall(qn(DATASET_NS, "ItemSet")):
            item_values.extend(
                clone_element(node)
                for node in item_set.findall(qn(DATASET_NS, "ItemValue"))
            )
        variable_order: list[Reference] = []
        records: list[Element] = []
        record_set = element.find(qn(DATASET_NS, "RecordSet"))
        if record_set is not None:
            order_el = record_set.find(qn(DATASET_NS, "VariableOrder"))
            if order_el is not None:
                variable_order = [
                    Reference.from_xml(ref)
                    for ref in order_el.findall(qn(REUSABLE_NS, "VariableReference"))
                ]
            records = [
                clone_element(node)
                for node in record_set.findall(qn(DATASET_NS, "Record"))
            ]
        variable_items: list[Element] = []
        variable_set = element.find(qn(DATASET_NS, "VariableSet"))
        if variable_set is not None:
            variable_items = [
                clone_element(node)
                for node in variable_set.findall(qn(DATASET_NS, "VariableItem"))
            ]
        return cls(
            agency=_text(REUSABLE_NS, "Agency"),
            identifier=_text(REUSABLE_NS, "ID"),
            version=_text(REUSABLE_NS, "Version"),
            names=names,
            physical_structure_link_reference=link_reference,
            physical_record_segment_used=segment_used,
            array_base=int(array_base_text) if array_base_text else 0,
            item_values=item_values,
            variable_order=variable_order,
            records=records,
            variable_items=variable_items,
            other_attributes=collect_other_attributes(element),
        )
