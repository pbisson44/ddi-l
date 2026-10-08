"""AUTO-GENERATED base dataclasses for DDI 3.3 — physicaldataproduct_proprietary module.

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
from ddi_l.models.base import CodeValue, MaintainableBase, Reference
from ddi_l.constants import PHYSICAL_DATA_PRODUCT_NS, REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class CodedDataAsNumericFields(MaintainableBase):
    """Indicates that coded data should be treated as numeric, and references the definition of the numeric type as described in ManagedNumericRepresentation. TypeOfObject should be set to ManagedNumericRepr"""

    TAG: ClassVar[str] = qn("ddi:physicaldataproduct_proprietary:3_3", "CodedDataAsNumeric")
    type_of_object: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    treatCodedDataAsNumeric: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isExternal": ("isExternal", "bool"),
        "isReference": ("isReference", "bool"),
        "lateBound": ("lateBound", "bool"),
        "lateBoundRestriction": ("lateBoundRestriction", "str"),
        "objectLanguage": ("objectLanguage", "str"),
        "sourceContext": ("sourceContext", "str"),
        "treatCodedDataAsNumeric": ("treatCodedDataAsNumeric", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "UserAttributePair"),
    ]


@dataclass
class CodedDataAsTextFields(MaintainableBase):
    """Indicates that coded data should be treated as text, and references the definition of the text type as described in ManagedTextRepresentation. TypeOfObject should be set to ManagedTextRepresentation."""

    TAG: ClassVar[str] = qn("ddi:physicaldataproduct_proprietary:3_3", "CodedDataAsText")
    type_of_object: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    treatCodedDataAsText: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isExternal": ("isExternal", "bool"),
        "isReference": ("isReference", "bool"),
        "lateBound": ("lateBound", "bool"),
        "lateBoundRestriction": ("lateBoundRestriction", "str"),
        "objectLanguage": ("objectLanguage", "str"),
        "sourceContext": ("sourceContext", "str"),
        "treatCodedDataAsText": ("treatCodedDataAsText", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "UserAttributePair"),
    ]


@dataclass
class DataItemAddressFields(MaintainableBase):
    """Provides minimum information on data item address system, such as variable ID or Name, etc."""

    TAG: ClassVar[str] = qn("ddi:physicaldataproduct_proprietary:3_3", "DataItemAddress")
    pass
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class DataItemFields(MaintainableBase):
    """Describes a single data item within the record, linking it to its description in a variable and providing information on its data type and any item specific proprietary information."""

    TAG: ClassVar[str] = qn("ddi:physicaldataproduct_proprietary:3_3", "DataItem")
    variable_reference: Optional[Reference] = None  # [0..1]
    proprietary_data_type: Optional[CodeValue] = None  # [0..1]
    proprietary_output_format: Optional[CodeValue] = None  # [0..1]
    proprietary_info: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
        "proprietary_data_type": (qn("ddi:physicaldataproduct_proprietary:3_3", "ProprietaryDataType"), "code_value", False),
        "proprietary_output_format": (qn("ddi:physicaldataproduct_proprietary:3_3", "ProprietaryOutputFormat"), "code_value", False),
        "proprietary_info": (qn(REUSABLE_NS, "ProprietaryInfo"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableReference"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "ProprietaryDataType"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "ProprietaryOutputFormat"),
        qn(REUSABLE_NS, "ProprietaryInfo"),
    ]


@dataclass
class RecordLayoutFields(MaintainableBase):
    """A member of the BaseRecordLayout substitution group intended for use when the data items are stored in an external proprietary format. In addition to the link to the PhysicalStructure provided by Base"""

    TAG: ClassVar[str] = qn("ddi:physicaldataproduct_proprietary:3_3", "RecordLayout")
    physical_structure_link_reference: Optional[Reference] = None  # [1..1]
    end_of_line_marker: Optional[CodeValue] = None  # [0..1]
    character_set: Optional[CodeValue] = None  # [0..1]
    array_base: Optional[int] = None  # [0..1]
    system_software: Optional[Element] = None  # [1..1]
    data_item_address: Optional[Element] = None  # [0..1]
    default_numeric_data_type_reference: Optional[Reference] = None  # [0..1]
    default_text_data_type_reference: Optional[Reference] = None  # [0..1]
    default_date_time_data_type_reference: Optional[Reference] = None  # [0..1]
    coded_data_as_numeric: Optional[Element] = None  # [1..1]
    coded_data_as_text: Optional[Element] = None  # [1..1]
    default_variable_scheme_reference: Optional[Reference] = None  # [0..1]
    proprietary_info: Optional[Element] = None  # [0..1]
    data_items: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    textQualifier: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "physical_structure_link_reference": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureLinkReference"), "reference", False),
        "end_of_line_marker": (qn(PHYSICAL_DATA_PRODUCT_NS, "EndOfLineMarker"), "code_value", False),
        "character_set": (qn(REUSABLE_NS, "CharacterSet"), "code_value", False),
        "array_base": (qn(REUSABLE_NS, "ArrayBase"), "int", False),
        "system_software": (qn("ddi:physicaldataproduct_proprietary:3_3", "SystemSoftware"), "element", False),
        "data_item_address": (qn("ddi:physicaldataproduct_proprietary:3_3", "DataItemAddress"), "element", False),
        "default_numeric_data_type_reference": (qn("ddi:physicaldataproduct_proprietary:3_3", "DefaultNumericDataTypeReference"), "reference", False),
        "default_text_data_type_reference": (qn("ddi:physicaldataproduct_proprietary:3_3", "DefaultTextDataTypeReference"), "reference", False),
        "default_date_time_data_type_reference": (qn("ddi:physicaldataproduct_proprietary:3_3", "DefaultDateTimeDataTypeReference"), "reference", False),
        "coded_data_as_numeric": (qn("ddi:physicaldataproduct_proprietary:3_3", "CodedDataAsNumeric"), "element", False),
        "coded_data_as_text": (qn("ddi:physicaldataproduct_proprietary:3_3", "CodedDataAsText"), "element", False),
        "default_variable_scheme_reference": (qn(REUSABLE_NS, "DefaultVariableSchemeReference"), "reference", False),
        "proprietary_info": (qn(REUSABLE_NS, "ProprietaryInfo"), "element", False),
        "data_items": (qn("ddi:physicaldataproduct_proprietary:3_3", "DataItem"), "element", True),
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
        qn(REUSABLE_NS, "CharacterSet"),
        qn(REUSABLE_NS, "ArrayBase"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "SystemSoftware"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "DataItemAddress"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "DefaultNumericDataTypeReference"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "DefaultTextDataTypeReference"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "DefaultDateTimeDataTypeReference"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "CodedDataAsNumeric"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "CodedDataAsText"),
        qn(REUSABLE_NS, "DefaultVariableSchemeReference"),
        qn(REUSABLE_NS, "ProprietaryInfo"),
        qn("ddi:physicaldataproduct_proprietary:3_3", "DataItem"),
    ]

