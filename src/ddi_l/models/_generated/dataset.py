"""AUTO-GENERATED base dataclasses for DDI 3.3 — dataset module.

These classes provide field definitions derived from the XSD schema.
Hand-written model classes inherit from these bases and add
``from_xml``, ``to_xml``, validation, and helper methods.

**Do not edit manually** — regenerate with:
    python -m codegen.generate_model_bases
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Optional

from ddi_l._etree import Element
from ddi_l.models.base import CodeValue, InternationalString, MaintainableBase, Reference
from ddi_l.constants import DATASET_NS, PHYSICAL_DATA_PRODUCT_NS, REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class DataSetFields(MaintainableBase):
    """DataSet is a substitution for a BaseRecordLayout and allows for in-line inclusion of micro or unit level data in the metadata file. This is valuable for small datasets or cases where there is a need t"""

    TAG: ClassVar[str] = qn(DATASET_NS, "DataSet")
    physical_structure_link_reference: Optional[Reference] = None  # [1..1]
    end_of_line_marker: Optional[CodeValue] = None  # [0..1]
    array_base: Optional[int] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    identifying_variable_reference: Optional[Reference] = None  # [0..1]
    default_variable_scheme_reference: Optional[Reference] = None  # [0..1]
    record_set: Optional[Element] = None  # [1..1]
    item_set: Optional[Element] = None  # [1..1]
    variable_set: Optional[Element] = None  # [1..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    textQualifier: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "physical_structure_link_reference": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference"), "reference", False),
        "end_of_line_marker": (qn(PHYSICAL_DATA_PRODUCT_NS, "EndOfLineMarker"), "code_value", False),
        "array_base": (qn(REUSABLE_NS, "ArrayBase"), "int", False),
        "names": (qn(DATASET_NS, "DataSetName"), "intl_string", True),
        "identifying_variable_reference": (qn(DATASET_NS, "IdentifyingVariableReference"), "reference", False),
        "default_variable_scheme_reference": (qn(REUSABLE_NS, "DefaultVariableSchemeReference"), "reference", False),
        "record_set": (qn(DATASET_NS, "RecordSet"), "element", False),
        "item_set": (qn(DATASET_NS, "ItemSet"), "element", False),
        "variable_set": (qn(DATASET_NS, "VariableSet"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "textQualifier": ("textQualifier", "str"),
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
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "EndOfLineMarker"),
        qn(REUSABLE_NS, "ArrayBase"),
        qn(DATASET_NS, "DataSetName"),
        qn(DATASET_NS, "IdentifyingVariableReference"),
        qn(REUSABLE_NS, "DefaultVariableSchemeReference"),
        qn(DATASET_NS, "RecordSet"),
        qn(DATASET_NS, "ItemSet"),
        qn(DATASET_NS, "VariableSet"),
    ]


@dataclass
class ItemSetFields(MaintainableBase):
    """Storage format for random order item variables. Each ItemValue references it's defining variable, it's record identifier, and the it's value."""

    TAG: ClassVar[str] = qn(DATASET_NS, "ItemSet")
    item_values: list[Element] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "item_values": (qn(DATASET_NS, "ItemValue"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATASET_NS, "ItemValue"),
    ]


@dataclass
class ItemValueFields(MaintainableBase):
    """Each value in the data set linked to it's variable and record identification."""

    TAG: ClassVar[str] = qn(DATASET_NS, "ItemValue")
    variable_reference: Optional[Reference] = None  # [0..1]
    record_reference: Optional[Reference] = None  # [1..1]
    values: list[Element] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
        "record_reference": (qn(DATASET_NS, "RecordReference"), "reference", False),
        "values": (qn(REUSABLE_NS, "Value"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableReference"),
        qn(DATASET_NS, "RecordReference"),
        qn(REUSABLE_NS, "Value"),
    ]


@dataclass
class RecordSetFields(MaintainableBase):
    """Storage format arranged record by record. A RecordSet requires a list of variables to appear in a specified order. Provides a consistent order for the variables and a set of values for each record dis"""

    TAG: ClassVar[str] = qn(DATASET_NS, "RecordSet")
    variable_order: Optional[Element] = None  # [0..1]
    records: list[Element] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_order": (qn(DATASET_NS, "VariableOrder"), "element", False),
        "records": (qn(DATASET_NS, "Record"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATASET_NS, "VariableOrder"),
        qn(DATASET_NS, "Record"),
    ]


@dataclass
class RecordFields(MaintainableBase):
    """For each record, contains the values for the items in order by the specified variable sequence."""

    TAG: ClassVar[str] = qn(DATASET_NS, "Record")
    values: list[Element] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "values": (qn(REUSABLE_NS, "Value"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Value"),
    ]


@dataclass
class VariableItemFields(MaintainableBase):
    """The set of values associated with a single variable (one for each record in storage order of records)."""

    TAG: ClassVar[str] = qn(DATASET_NS, "VariableItem")
    variable_reference: Optional[Reference] = None  # [0..1]
    values: list[Element] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
        "values": (qn(REUSABLE_NS, "Value"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableReference"),
        qn(REUSABLE_NS, "Value"),
    ]


@dataclass
class VariableOrderFields(MaintainableBase):
    """A set of References to Variable found in the record in storage order."""

    TAG: ClassVar[str] = qn(DATASET_NS, "VariableOrder")
    variable_references: list[Reference] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_references": (qn(REUSABLE_NS, "VariableReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableReference"),
    ]


@dataclass
class VariableSetFields(MaintainableBase):
    """Storage format arranged variable by variable. Item values are listed in record order with the assumption that each record will occupy the position in each array."""

    TAG: ClassVar[str] = qn(DATASET_NS, "VariableSet")
    variable_items: list[Element] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_items": (qn(DATASET_NS, "VariableItem"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DATASET_NS, "VariableItem"),
    ]

