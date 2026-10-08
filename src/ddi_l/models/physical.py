"""Wrappers for the PhysicalDataProduct module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .._etree import Element, create_element
from ..constants import (
    PHYSICAL_DATA_PRODUCT_NS,
    PHYSICAL_INSTANCE_NS,
    REUSABLE_NS,
)
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.physicaldataproduct import (
    PhysicalStructureFields,
    RecordLayoutFields,
)
from ._generated.physicalinstance import PhysicalInstanceFields
from .base import InternationalString, Reference, qn

__all__ = ["PhysicalInstance", "PhysicalStructure", "RecordLayout"]


@dataclass
class PhysicalStructure(PhysicalStructureFields):
    """Representation of ``p:PhysicalStructure`` descriptions."""

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructure")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")

    def link_logical_record(
        self,
        logical_record_reference: Reference,
        *,
        segment_identifier: str,
        key_variable: Reference | None = None,
        key_value: str = "",
    ) -> Element:
        """Add a gross record structure linking this file to a logical record.

        Builds a ``GrossRecordStructure`` (referencing the logical record) with a
        single ``PhysicalRecordSegment`` whose id is ``segment_identifier``, the
        segment a record layout points at via ``PhysicalRecordSegmentUsed``.
        Returns the gross record structure element.

        Pass ``key_variable`` to declare a segment key: the segment is marked
        ``hasSegmentKey`` and gets a ``KeyVariableReference`` to that variable,
        carrying ``key_value`` (the variable's value that identifies this
        segment).
        """
        gross = create_element(qn(PHYSICAL_DATA_PRODUCT_NS, "GrossRecordStructure"))
        self._append_child_identification(
            gross, suffix=f"gross-record-{len(self.gross_record_structures) + 1}"
        )
        gross.append(
            logical_record_reference.to_xml(
                "LogicalRecordReference", namespace=PHYSICAL_DATA_PRODUCT_NS
            )
        )
        segment = create_element(qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalRecordSegment"))
        if key_variable is not None:
            segment.set("hasSegmentKey", "true")
        for tag, value in (
            ("Agency", self.agency),
            ("ID", segment_identifier),
            ("Version", self.version or "1"),
        ):
            if value is not None:
                child = create_element(qn(REUSABLE_NS, tag))
                child.text = value
                segment.append(child)
        if key_variable is not None:
            key_reference = key_variable.to_xml(
                "KeyVariableReference", namespace=PHYSICAL_DATA_PRODUCT_NS
            )
            # KeyVariableReferenceType requires the key variable's Value.
            value_el = create_element(qn(REUSABLE_NS, "Value"))
            value_el.text = key_value
            key_reference.append(value_el)
            segment.append(key_reference)
        gross.append(segment)
        self.gross_record_structures.append(gross)
        return gross


@dataclass
class PhysicalInstance(PhysicalInstanceFields):
    """Maintainable wrapper for ``pi:PhysicalInstance`` descriptions.

    A physical instance documents one concrete data file: where it lives
    (:meth:`set_data_file`), how many records it holds
    (:meth:`set_record_count`), and what it is called
    (:meth:`set_citation_title`). It has no ``Name`` element in DDI; it is
    titled through its citation.
    """

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "PhysicalInstance")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")

    def set_citation_title(self, title: str, *, lang: str = "en") -> PhysicalInstance:
        """Set the citation title (the human name of the data file). Returns self."""
        title_el = create_element(qn(REUSABLE_NS, "Title"))
        title_el.append(
            InternationalString(text=title, lang=lang).to_child(child_tag="String")
        )
        citation = create_element(qn(REUSABLE_NS, "Citation"))
        citation.append(title_el)
        self.citation = citation
        return self

    def set_data_file(self, uri: str) -> PhysicalInstance:
        """Point this instance at a data file by URI. Returns self.

        Replaces any existing data-file identifications with a single entry.
        """
        identification = create_element(
            qn(PHYSICAL_INSTANCE_NS, "DataFileIdentification")
        )
        uri_el = create_element(qn(PHYSICAL_INSTANCE_NS, "DataFileURI"))
        uri_el.text = uri
        identification.append(uri_el)
        self.data_file_identifications = [identification]
        return self

    def set_record_count(self, count: int) -> PhysicalInstance:
        """Record the number of cases (records) in the data file. Returns self."""
        gross = create_element(qn(PHYSICAL_INSTANCE_NS, "GrossFileStructure"))
        # GrossFileStructure is an IdentifiableType: it needs Agency/ID/Version
        # before its content.
        self._append_child_identification(gross, suffix="gross-file-structure")
        case_quantity = create_element(qn(PHYSICAL_INSTANCE_NS, "CaseQuantity"))
        case_quantity.text = str(count)
        gross.append(case_quantity)
        self.gross_file_structure = gross
        return self


@dataclass
class RecordLayout(RecordLayoutFields):
    """Maintainable wrapper for ``p:RecordLayout`` descriptions.

    A record layout maps variables to their physical position in a data file.
    Build one with :meth:`ddi_l.document.Document.add_record_layout` and add
    mappings with :meth:`add_data_item`.
    """

    physical_record_segment_used: str | None = None

    TAG: ClassVar[str] = qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayout")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("p")

    def add_data_item(
        self,
        variable_reference: Reference,
        *,
        start_position: int | None = None,
        width: int | None = None,
        end_position: int | None = None,
        storage_format: str | None = None,
        delimiter: str | None = None,
        decimal_positions: int | None = None,
    ) -> Element:
        """Map a variable to a physical position in the record. Returns the item.

        ``start_position``/``width``/``end_position`` describe where the value
        sits in a fixed-width record; omit them all for a delimited file.
        ``storage_format`` names the storage encoding (e.g. ``"ASCII"``),
        ``delimiter`` is one of the DDI codes (``"comma"``, ``"tab"``,
        ``"space"``, ``"semicolon"``, ``"colon"``, ``"pipe"``, ``"other"``), and
        ``decimal_positions`` records the number of implied decimal places.
        """
        item = create_element(qn(PHYSICAL_DATA_PRODUCT_NS, "DataItem"))
        item.append(
            variable_reference.to_xml("VariableReference", namespace=REUSABLE_NS)
        )
        location_fields = (
            storage_format,
            delimiter,
            start_position,
            end_position,
            width,
            decimal_positions,
        )
        if any(value is not None for value in location_fields):
            location = create_element(qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalLocation"))
            # PhysicalLocationType order: StorageFormat, Delimiter, StartPosition,
            # EndPosition, Width, DecimalPositions.
            for tag, value in (
                ("StorageFormat", storage_format),
                ("Delimiter", delimiter),
                ("StartPosition", start_position),
                ("EndPosition", end_position),
                ("Width", width),
                ("DecimalPositions", decimal_positions),
            ):
                if value is not None:
                    child = create_element(qn(PHYSICAL_DATA_PRODUCT_NS, tag))
                    child.text = str(value)
                    location.append(child)
            item.append(location)
        self.data_items.append(item)
        return item

    def to_xml(self) -> Element:
        element = super().to_xml()
        # PhysicalStructureLinkReference requires a PhysicalRecordSegmentUsed
        # child that the generic reference serializer does not emit.
        if self.physical_record_segment_used is not None:
            link = element.find(
                qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference")
            )
            if link is not None:
                segment = create_element(
                    qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalRecordSegmentUsed")
                )
                segment.text = self.physical_record_segment_used
                link.append(segment)
        return element

    @classmethod
    def from_xml(cls, element: Element) -> RecordLayout:
        obj = super().from_xml(element)
        link = element.find(
            qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference")
        )
        if link is not None:
            segment = link.find(
                qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalRecordSegmentUsed")
            )
            if segment is not None:
                obj.physical_record_segment_used = segment.text
        return obj
