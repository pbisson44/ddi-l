"""AUTO-GENERATED base dataclasses for DDI 3.3 — physicalinstance module.

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
from ddi_l.constants import PHYSICAL_INSTANCE_NS, REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class CategoryStatisticFields(MaintainableBase):
    """The value of a statistic associated with the category value."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "CategoryStatistic")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    type_of_category_statistic: Optional[CodeValue] = None  # [1..1]
    statistic: Optional[Element] = None  # [1..1]
    statistic_double: Optional[Element] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_category_statistic": (qn(PHYSICAL_INSTANCE_NS, "TypeOfCategoryStatistic"), "code_value", False),
        "statistic": (qn(PHYSICAL_INSTANCE_NS, "Statistic"), "element", False),
        "statistic_double": (qn(PHYSICAL_INSTANCE_NS, "StatisticDouble"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(PHYSICAL_INSTANCE_NS, "TypeOfCategoryStatistic"),
        qn(PHYSICAL_INSTANCE_NS, "Statistic"),
        qn(PHYSICAL_INSTANCE_NS, "StatisticDouble"),
    ]


@dataclass
class CategoryValueFields(MaintainableBase):
    """A category value for which one or more statistics are recorded. Each VariableCategory has one category value and any number of associated statistics."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "CategoryValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    code_reference: Optional[Reference] = None  # [1..1]
    value: Optional[Element] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "code_reference": (qn(REUSABLE_NS, "CodeReference"), "reference", False),
        "value": (qn(REUSABLE_NS, "Value"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "CodeReference"),
        qn(REUSABLE_NS, "Value"),
    ]


@dataclass
class DataFileIdentificationFields(MaintainableBase):
    """Identifies the data file documented in the physical instance and provides information about its location."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "DataFileIdentification")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    location: Optional[Element] = None  # [0..1]
    data_file_uri: Optional[Element] = None  # [1..1]
    size_in_bytes: Optional[int] = None  # [0..1]
    isMaster: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "location": (qn(REUSABLE_NS, "Location"), "element", False),
        "data_file_uri": (qn(PHYSICAL_INSTANCE_NS, "DataFileURI"), "element", False),
        "size_in_bytes": (qn(REUSABLE_NS, "SizeInBytes"), "int", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isMaster": ("isMaster", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Location"),
        qn(PHYSICAL_INSTANCE_NS, "DataFileURI"),
        qn(REUSABLE_NS, "SizeInBytes"),
    ]


@dataclass
class DataFileVersionFields(MaintainableBase):
    """Provides the version information for the data file related to this physical instance. Note that while Physical Instance allows for multiple copies of the same data file (such as backup copies) the ass"""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "DataFileVersion")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    type_of_version_number: Optional[str] = None  # [0..1]
    versionNumber: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_version_number": (qn(PHYSICAL_INSTANCE_NS, "TypeOfVersionNumber"), "str", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "versionNumber": ("versionNumber", "str"),
        "versionDate": ("versionDate", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(PHYSICAL_INSTANCE_NS, "TypeOfVersionNumber"),
        qn(REUSABLE_NS, "VersionResponsibility"),
        qn(REUSABLE_NS, "VersionResponsibilityReference"),
        qn(REUSABLE_NS, "VersionRationale"),
    ]


@dataclass
class DataFingerprintFields(MaintainableBase):
    """Allows for assigning a hash value (digital fingerprint) to the data or data file. Set the attribute flag to "data" when the hash value provides a digital fingerprint to the data contained in the file """

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "DataFingerprint")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    digital_fingerprint_value: Optional[str] = None  # [1..1]
    algorithm_specification: Optional[str] = None  # [0..1]
    algorithm_version: Optional[str] = None  # [0..1]
    type: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "digital_fingerprint_value": (qn(PHYSICAL_INSTANCE_NS, "DigitalFingerprintValue"), "str", False),
        "algorithm_specification": (qn(PHYSICAL_INSTANCE_NS, "AlgorithmSpecification"), "str", False),
        "algorithm_version": (qn(PHYSICAL_INSTANCE_NS, "AlgorithmVersion"), "str", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "type": ("type", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(PHYSICAL_INSTANCE_NS, "DigitalFingerprintValue"),
        qn(PHYSICAL_INSTANCE_NS, "AlgorithmSpecification"),
        qn(PHYSICAL_INSTANCE_NS, "AlgorithmVersion"),
    ]


@dataclass
class DefaultMissingValuesReferenceFields(MaintainableBase):
    """Identifies the default missing value parameter for the this physical instance by referencing a ManagedMissingValuesRepresentation. Note that this MissingValues declaration overrides the value found in"""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "DefaultMissingValuesReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    type_of_object: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    isSystemMissingValue: Optional[bool] = None  # @attr
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
        "isSystemMissingValue": ("isSystemMissingValue", "bool"),
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
class FilterVariableCategoryFields(MaintainableBase):
    """Category statistics for the variable when the filter variable contains the specified value."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "FilterVariableCategory")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    filter_category_value: Optional[Element] = None  # [1..1]
    variable_categories: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "filter_category_value": (qn(PHYSICAL_INSTANCE_NS, "FilterCategoryValue"), "element", False),
        "variable_categories": (qn(PHYSICAL_INSTANCE_NS, "VariableCategory"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(PHYSICAL_INSTANCE_NS, "FilterCategoryValue"),
        qn(PHYSICAL_INSTANCE_NS, "VariableCategory"),
    ]


@dataclass
class FilteredCategoryStatisticsFields(MaintainableBase):
    """Category statistics filtered by the value of a second variable. Essentially a cross tabulation of one variable by another. For example variable may be crossed with country as is done in the Eurobarome"""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "FilteredCategoryStatistics")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    filter_variable_reference: Optional[Reference] = None  # [0..1]
    filter_variable_categories: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "filter_variable_reference": (qn(PHYSICAL_INSTANCE_NS, "FilterVariableReference"), "reference", False),
        "filter_variable_categories": (qn(PHYSICAL_INSTANCE_NS, "FilterVariableCategory"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(PHYSICAL_INSTANCE_NS, "FilterVariableReference"),
        qn(PHYSICAL_INSTANCE_NS, "FilterVariableCategory"),
    ]


@dataclass
class GrossFileStructureFields(MaintainableBase):
    """Includes information about the file structure, as well as other characteristics that are specific to the physical instance. Information includes place of production, processing checks to validate the """

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "GrossFileStructure")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    place_of_production: Optional[str] = None  # [0..1]
    processing_checks: list[Element] = field(default_factory=list)  # [0..*]
    processing_status: Optional[CodeValue] = None  # [0..1]
    creation_software: Optional[Element] = None  # [0..1]
    case_quantity: Optional[int] = None  # [0..1]
    overall_record_count: Optional[int] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "place_of_production": (qn(PHYSICAL_INSTANCE_NS, "PlaceOfProduction"), "str", False),
        "processing_checks": (qn(PHYSICAL_INSTANCE_NS, "ProcessingCheck"), "element", True),
        "processing_status": (qn(PHYSICAL_INSTANCE_NS, "ProcessingStatus"), "code_value", False),
        "creation_software": (qn(PHYSICAL_INSTANCE_NS, "CreationSoftware"), "element", False),
        "case_quantity": (qn(PHYSICAL_INSTANCE_NS, "CaseQuantity"), "int", False),
        "overall_record_count": (qn(PHYSICAL_INSTANCE_NS, "OverallRecordCount"), "int", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(PHYSICAL_INSTANCE_NS, "PlaceOfProduction"),
        qn(PHYSICAL_INSTANCE_NS, "ProcessingCheck"),
        qn(PHYSICAL_INSTANCE_NS, "ProcessingStatus"),
        qn(PHYSICAL_INSTANCE_NS, "CreationSoftware"),
        qn(PHYSICAL_INSTANCE_NS, "CaseQuantity"),
        qn(PHYSICAL_INSTANCE_NS, "OverallRecordCount"),
    ]


@dataclass
class PhysicalInstanceGroupFields(MaintainableBase):
    """Contains a group of PhysicalInstance descriptions, which may be ordered or hierarchical. In addition to the name, label, and description of the group, the structure allows for defining the group by re"""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "PhysicalInstanceGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    type_of_physical_instance_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    physical_instance_references: list[Reference] = field(default_factory=list)  # [0..*]
    physical_instance_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_physical_instance_group": (qn(PHYSICAL_INSTANCE_NS, "TypeOfPhysicalInstanceGroup"), "code_value", False),
        "names": (qn(PHYSICAL_INSTANCE_NS, "PhysicalInstanceGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "physical_instance_references": (qn(REUSABLE_NS, "PhysicalInstanceReference"), "reference", True),
        "physical_instance_group_references": (qn(REUSABLE_NS, "PhysicalInstanceGroupReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "lang": ("lang", "str"),
        "isOrdered": ("isOrdered", "bool"),
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
        qn(REUSABLE_NS, "Note"),
        qn(REUSABLE_NS, "Software"),
        qn(REUSABLE_NS, "MetadataQuality"),
        qn(PHYSICAL_INSTANCE_NS, "TypeOfPhysicalInstanceGroup"),
        qn(PHYSICAL_INSTANCE_NS, "PhysicalInstanceGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "PhysicalInstanceReference"),
        qn(REUSABLE_NS, "PhysicalInstanceGroupReference"),
    ]


@dataclass
class PhysicalInstanceFields(MaintainableBase):
    """Includes information about the physical instance of a data product (an actual data file). It completes the documentation contained in the Physical Data Product module that is specific to the individua"""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "PhysicalInstance")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    citation: Optional[Element] = None  # [0..1]
    data_fingerprints: list[Element] = field(default_factory=list)  # [0..*]
    coverage: Optional[Element] = None  # [0..1]
    data_relationship_references: list[Reference] = field(default_factory=list)  # [0..*]
    variable_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    record_layout_references: list[Reference] = field(default_factory=list)  # [0..*]
    default_missing_values_reference: Optional[Reference] = None  # [0..1]
    data_file_identifications: list[Element] = field(default_factory=list)  # [0..*]
    data_file_version: Optional[Element] = None  # [0..1]
    information_classifications: list[Element] = field(default_factory=list)  # [0..*]
    information_classification_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_statement_references: list[Reference] = field(default_factory=list)  # [0..*]
    gross_file_structure: Optional[Element] = None  # [0..1]
    proprietary_info: Optional[Element] = None  # [0..1]
    statistical_summary: Optional[Element] = None  # [0..1]
    byte_order: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "citation": (qn(REUSABLE_NS, "Citation"), "element", False),
        "data_fingerprints": (qn(PHYSICAL_INSTANCE_NS, "DataFingerprint"), "element", True),
        "coverage": (qn(REUSABLE_NS, "Coverage"), "element", False),
        "data_relationship_references": (qn(REUSABLE_NS, "DataRelationshipReference"), "reference", True),
        "variable_group_references": (qn(REUSABLE_NS, "VariableGroupReference"), "reference", True),
        "record_layout_references": (qn(REUSABLE_NS, "RecordLayoutReference"), "reference", True),
        "default_missing_values_reference": (qn(PHYSICAL_INSTANCE_NS, "DefaultMissingValuesReference"), "reference", False),
        "data_file_identifications": (qn(PHYSICAL_INSTANCE_NS, "DataFileIdentification"), "element", True),
        "data_file_version": (qn(PHYSICAL_INSTANCE_NS, "DataFileVersion"), "element", False),
        "information_classifications": (qn(REUSABLE_NS, "InformationClassification"), "element", True),
        "information_classification_references": (qn(REUSABLE_NS, "InformationClassificationReference"), "reference", True),
        "quality_statement_references": (qn(REUSABLE_NS, "QualityStatementReference"), "reference", True),
        "gross_file_structure": (qn(PHYSICAL_INSTANCE_NS, "GrossFileStructure"), "element", False),
        "proprietary_info": (qn(REUSABLE_NS, "ProprietaryInfo"), "element", False),
        "statistical_summary": (qn(PHYSICAL_INSTANCE_NS, "StatisticalSummary"), "element", False),
        "byte_order": (qn(PHYSICAL_INSTANCE_NS, "ByteOrder"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "lang": ("lang", "str"),
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
        qn(REUSABLE_NS, "Note"),
        qn(REUSABLE_NS, "Software"),
        qn(REUSABLE_NS, "MetadataQuality"),
        qn(REUSABLE_NS, "Citation"),
        qn(PHYSICAL_INSTANCE_NS, "DataFingerprint"),
        qn(REUSABLE_NS, "Coverage"),
        qn(REUSABLE_NS, "DataRelationshipReference"),
        qn(REUSABLE_NS, "VariableGroupReference"),
        qn(REUSABLE_NS, "RecordLayoutReference"),
        qn(PHYSICAL_INSTANCE_NS, "DefaultMissingValuesReference"),
        qn(PHYSICAL_INSTANCE_NS, "DataFileIdentification"),
        qn(PHYSICAL_INSTANCE_NS, "DataFileVersion"),
        qn(REUSABLE_NS, "InformationClassification"),
        qn(REUSABLE_NS, "InformationClassificationReference"),
        qn(REUSABLE_NS, "QualityStatementReference"),
        qn(PHYSICAL_INSTANCE_NS, "GrossFileStructure"),
        qn(REUSABLE_NS, "ProprietaryInfo"),
        qn(PHYSICAL_INSTANCE_NS, "StatisticalSummary"),
        qn(PHYSICAL_INSTANCE_NS, "ByteOrder"),
    ]


@dataclass
class StatisticDoubleFields(MaintainableBase):
    """The value (expressed as a double) of the statistics and whether it is weighted and/or includes missing values."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "StatisticDouble")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    isWeighted: Optional[bool] = None  # @attr
    computationBase: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isWeighted": ("isWeighted", "bool"),
        "computationBase": ("computationBase", "str"),
    }


@dataclass
class StatisticFields(MaintainableBase):
    """The value (expressed as a decimal) of the statistics and whether it is weighted and/or includes missing values."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "Statistic")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    isWeighted: Optional[bool] = None  # @attr
    computationBase: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isWeighted": ("isWeighted", "bool"),
        "computationBase": ("computationBase", "str"),
    }


@dataclass
class StatisticalDataLocationFields(MaintainableBase):
    """References a PhysicalInstance module that describes a data file containing the summary and/or category statistics OR contains the statistics in-line.  For example, when the same data are stored as an """

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "StatisticalDataLocation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    physical_instance_reference: Optional[Reference] = None  # [1..1]
    isInline: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "physical_instance_reference": (qn(REUSABLE_NS, "PhysicalInstanceReference"), "reference", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isInline": ("isInline", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "PhysicalInstanceReference"),
    ]


@dataclass
class StatisticalSummaryFields(MaintainableBase):
    """Provides a statistical summary of the data in the related file as a set of variable level and category level statistics. May refer to a set of statistics provided in another physical instance (for exa"""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "StatisticalSummary")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    statistical_data_locations: list[Element] = field(default_factory=list)  # [0..*]
    variable_statistics: list[Element] = field(default_factory=list)  # [0..*]
    variable_statistics_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "statistical_data_locations": (qn(PHYSICAL_INSTANCE_NS, "StatisticalDataLocation"), "element", True),
        "variable_statistics": (qn(PHYSICAL_INSTANCE_NS, "VariableStatistics"), "element", True),
        "variable_statistics_references": (qn(PHYSICAL_INSTANCE_NS, "VariableStatisticsReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(PHYSICAL_INSTANCE_NS, "StatisticalDataLocation"),
        qn(PHYSICAL_INSTANCE_NS, "VariableStatistics"),
        qn(PHYSICAL_INSTANCE_NS, "VariableStatisticsReference"),
    ]


@dataclass
class SummaryStatisticFields(MaintainableBase):
    """Describes a summary statistic for a variable."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "SummaryStatistic")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    type_of_summary_statistic: Optional[CodeValue] = None  # [1..1]
    statistic: Optional[Element] = None  # [1..1]
    statistic_double: Optional[Element] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_summary_statistic": (qn(PHYSICAL_INSTANCE_NS, "TypeOfSummaryStatistic"), "code_value", False),
        "statistic": (qn(PHYSICAL_INSTANCE_NS, "Statistic"), "element", False),
        "statistic_double": (qn(PHYSICAL_INSTANCE_NS, "StatisticDouble"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(PHYSICAL_INSTANCE_NS, "TypeOfSummaryStatistic"),
        qn(PHYSICAL_INSTANCE_NS, "Statistic"),
        qn(PHYSICAL_INSTANCE_NS, "StatisticDouble"),
    ]


@dataclass
class URIFields(MaintainableBase):
    """A URN or URL for a file with a flag to indicate if it is a public copy."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "URI")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    isPublic: Optional[bool] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isPublic": ("isPublic", "bool"),
    }


@dataclass
class UnfilteredCategoryStatisticsFields(MaintainableBase):
    """The unfiltered values of any number of statistics by category value representing the full response distribution of the variable."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "UnfilteredCategoryStatistics")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    variable_categories: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_categories": (qn(PHYSICAL_INSTANCE_NS, "VariableCategory"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(PHYSICAL_INSTANCE_NS, "VariableCategory"),
    ]


@dataclass
class VariableCategoryFields(MaintainableBase):
    """A category value for which one or more statistics are recorded. Each VariableCategory has one category value and any number of associated statistics."""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "VariableCategory")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    category_value: Optional[Element] = None  # [1..1]
    category_statistics: list[Element] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "category_value": (qn(PHYSICAL_INSTANCE_NS, "CategoryValue"), "element", False),
        "category_statistics": (qn(PHYSICAL_INSTANCE_NS, "CategoryStatistic"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(PHYSICAL_INSTANCE_NS, "CategoryValue"),
        qn(PHYSICAL_INSTANCE_NS, "CategoryStatistic"),
    ]


@dataclass
class VariableStatisticsFields(MaintainableBase):
    """Contains summary and category level statistics for the referenced variable. Includes information on the total number of responses, the weights in calculating the statistics, variable level summary sta"""

    TAG: ClassVar[str] = qn(PHYSICAL_INSTANCE_NS, "VariableStatistics")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("pi")
    variable_reference: Optional[Reference] = None  # [1..1]
    total_responses: Optional[int] = None  # [0..1]
    standard_weight_reference: Optional[Reference] = None  # [1..1]
    weight_variable_reference: Optional[Reference] = None  # [1..1]
    missing_values_reference: Optional[Reference] = None  # [0..1]
    summary_statistics: list[Element] = field(default_factory=list)  # [0..*]
    unfiltered_category_statistics: list[Element] = field(default_factory=list)  # [0..*]
    filtered_category_statistics: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
        "total_responses": (qn(PHYSICAL_INSTANCE_NS, "TotalResponses"), "int", False),
        "standard_weight_reference": (qn(PHYSICAL_INSTANCE_NS, "StandardWeightReference"), "reference", False),
        "weight_variable_reference": (qn(REUSABLE_NS, "WeightVariableReference"), "reference", False),
        "missing_values_reference": (qn(PHYSICAL_INSTANCE_NS, "MissingValuesReference"), "reference", False),
        "summary_statistics": (qn(PHYSICAL_INSTANCE_NS, "SummaryStatistic"), "element", True),
        "unfiltered_category_statistics": (qn(PHYSICAL_INSTANCE_NS, "UnfilteredCategoryStatistics"), "element", True),
        "filtered_category_statistics": (qn(PHYSICAL_INSTANCE_NS, "FilteredCategoryStatistics"), "element", True),
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
        qn(REUSABLE_NS, "VariableReference"),
        qn(PHYSICAL_INSTANCE_NS, "TotalResponses"),
        qn(PHYSICAL_INSTANCE_NS, "StandardWeightReference"),
        qn(REUSABLE_NS, "WeightVariableReference"),
        qn(PHYSICAL_INSTANCE_NS, "MissingValuesReference"),
        qn(PHYSICAL_INSTANCE_NS, "SummaryStatistic"),
        qn(PHYSICAL_INSTANCE_NS, "UnfilteredCategoryStatistics"),
        qn(PHYSICAL_INSTANCE_NS, "FilteredCategoryStatistics"),
    ]

