"""AUTO-GENERATED base dataclasses for DDI 3.3 — physicaldataproduct_ncube_normal module.

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
class AttachedAttributeFields(MaintainableBase):
    """References the attribute description in the NCube and provides for a choice between describing an explicit value, or a location in a file where the value can be found."""

    TAG: ClassVar[str] = qn("ddi:physicaldataproduct_ncube_normal:3_3", "AttachedAttribute")
    attribute_reference: Optional[Reference] = None  # [1..1]
    physical_location: Optional[Element] = None  # [1..1]
    value: Optional[Element] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "attribute_reference": (qn(REUSABLE_NS, "AttributeReference"), "reference", False),
        "physical_location": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalLocation"), "element", False),
        "value": (qn(REUSABLE_NS, "Value"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "AttributeReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalLocation"),
        qn(REUSABLE_NS, "Value"),
    ]


@dataclass
class DataItemFields(MaintainableBase):
    """Describes a single data item or cell within an NCube Instance. It defines its location within the NCube by its coordinate (matrix) address which is its intersect point on each dimension. Allows for th"""

    TAG: ClassVar[str] = qn("ddi:physicaldataproduct_ncube_normal:3_3", "DataItem")
    dimension_rank_values: list[Element] = field(default_factory=list)  # [1..*]
    attached_attributes: list[Element] = field(default_factory=list)  # [0..*]
    measures: list[Element] = field(default_factory=list)  # [1..*]
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "dimension_rank_values": (qn(REUSABLE_NS, "DimensionRankValue"), "element", True),
        "attached_attributes": (qn("ddi:physicaldataproduct_ncube_normal:3_3", "AttachedAttribute"), "element", True),
        "measures": (qn("ddi:physicaldataproduct_ncube_normal:3_3", "Measure"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "lang": ("lang", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "DimensionRankValue"),
        qn("ddi:physicaldataproduct_ncube_normal:3_3", "AttachedAttribute"),
        qn("ddi:physicaldataproduct_ncube_normal:3_3", "Measure"),
    ]


@dataclass
class MeasureFields(MaintainableBase):
    """Identifies the specific measure of the cell by reference and provides information on the storage location of the value for the measure. When individual measures are stored in separately identifiable l"""

    TAG: ClassVar[str] = qn("ddi:physicaldataproduct_ncube_normal:3_3", "Measure")
    measure_definition_references: list[Reference] = field(default_factory=list)  # [1..*]
    physical_location: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "measure_definition_references": (qn(REUSABLE_NS, "MeasureDefinitionReference"), "reference", True),
        "physical_location": (qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalLocation"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "MeasureDefinitionReference"),
        qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalLocation"),
    ]


@dataclass
class NCubeInstanceFields(MaintainableBase):
    """A container for defining an instance of an NCube, indicating the matrix address of each cell and where the data for each measure within a cell of the NCube is stored. Allows specifying the values of t"""

    TAG: ClassVar[str] = qn("ddi:physicaldataproduct_ncube_normal:3_3", "NCubeInstance")
    n_cube_reference: Optional[Reference] = None  # [1..1]
    measure_dimension: Optional[Element] = None  # [0..1]
    attached_attributes: list[Element] = field(default_factory=list)  # [0..*]
    data_items: list[Element] = field(default_factory=list)  # [0..*]
    default_data_type: Optional[CodeValue] = None  # [0..1]
    default_delimiter: Optional[Element] = None  # [0..1]
    default_decimal_positions: Optional[int] = None  # [0..1]
    default_decimal_separator: Optional[Element] = None  # [0..1]
    default_digit_group_separator: Optional[Element] = None  # [0..1]
    number_of_cases: Optional[int] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "n_cube_reference": (qn(REUSABLE_NS, "NCubeReference"), "reference", False),
        "measure_dimension": (qn(REUSABLE_NS, "MeasureDimension"), "element", False),
        "attached_attributes": (qn("ddi:physicaldataproduct_ncube_normal:3_3", "AttachedAttribute"), "element", True),
        "data_items": (qn("ddi:physicaldataproduct_ncube_normal:3_3", "DataItem"), "element", True),
        "default_data_type": (qn(REUSABLE_NS, "DefaultDataType"), "code_value", False),
        "default_delimiter": (qn(REUSABLE_NS, "DefaultDelimiter"), "element", False),
        "default_decimal_positions": (qn(REUSABLE_NS, "DefaultDecimalPositions"), "int", False),
        "default_decimal_separator": (qn(REUSABLE_NS, "DefaultDecimalSeparator"), "element", False),
        "default_digit_group_separator": (qn(REUSABLE_NS, "DefaultDigitGroupSeparator"), "element", False),
        "number_of_cases": (qn(REUSABLE_NS, "NumberOfCases"), "int", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
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
        qn(REUSABLE_NS, "NCubeReference"),
        qn(REUSABLE_NS, "MeasureDimension"),
        qn("ddi:physicaldataproduct_ncube_normal:3_3", "AttachedAttribute"),
        qn("ddi:physicaldataproduct_ncube_normal:3_3", "DataItem"),
        qn(REUSABLE_NS, "DefaultDataType"),
        qn(REUSABLE_NS, "DefaultDelimiter"),
        qn(REUSABLE_NS, "DefaultDecimalPositions"),
        qn(REUSABLE_NS, "DefaultDecimalSeparator"),
        qn(REUSABLE_NS, "DefaultDigitGroupSeparator"),
        qn(REUSABLE_NS, "NumberOfCases"),
    ]


@dataclass
class RecordLayoutFields(MaintainableBase):
    """A member of the BaseRecordLayout substitution group intended for use with archival formats of NCube Instances or mixed NCube and microdata (i.e., a set of NCubes where the case identification is not d"""

    TAG: ClassVar[str] = qn("ddi:physicaldataproduct_ncube_normal:3_3", "RecordLayout")
    physical_structure_link_reference: Optional[Reference] = None  # [1..1]
    end_of_line_marker: Optional[CodeValue] = None  # [0..1]
    character_set: Optional[CodeValue] = None  # [0..1]
    array_base: Optional[int] = None  # [1..1]
    data_items: list[Element] = field(default_factory=list)  # [0..*]
    n_cube_instances: list[Element] = field(default_factory=list)  # [0..*]
    n_cube_instance_references: list[Reference] = field(default_factory=list)  # [0..*]
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
        "data_items": (qn(PHYSICAL_DATA_PRODUCT_NS, "DataItem"), "element", True),
        "n_cube_instances": (qn("ddi:physicaldataproduct_ncube_normal:3_3", "NCubeInstance"), "element", True),
        "n_cube_instance_references": (qn(REUSABLE_NS, "NCubeInstanceReference"), "reference", True),
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
        qn(PHYSICAL_DATA_PRODUCT_NS, "DataItem"),
        qn("ddi:physicaldataproduct_ncube_normal:3_3", "NCubeInstance"),
        qn(REUSABLE_NS, "NCubeInstanceReference"),
    ]

