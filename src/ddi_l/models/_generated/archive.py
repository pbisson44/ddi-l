"""AUTO-GENERATED base dataclasses for DDI 3.3 — archive module.

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
from ddi_l.constants import ARCHIVE_NS, REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class AccessFields(MaintainableBase):
    """Describes access to the holdings of the archive or to a specific data product. In addition to the name, label, and description for access. This item includes a confidentiality statement, descriptions """

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Access")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    type_of_access: Optional[CodeValue] = None  # [0..1]
    access_type_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    confidentiality_statement: Optional[Element] = None  # [0..1]
    access_permissions: list[Element] = field(default_factory=list)  # [0..*]
    restrictions: Optional[Element] = None  # [0..1]
    citation_requirement: Optional[Element] = None  # [0..1]
    deposit_requirement: Optional[Element] = None  # [0..1]
    access_conditions: Optional[Element] = None  # [0..1]
    disclaimer: Optional[Element] = None  # [0..1]
    access_restriction_date: Optional[Element] = None  # [0..1]
    contact_organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_access": (qn(ARCHIVE_NS, "TypeOfAccess"), "code_value", False),
        "access_type_names": (qn(ARCHIVE_NS, "AccessTypeName"), "intl_string", True),
        "confidentiality_statement": (qn(ARCHIVE_NS, "ConfidentialityStatement"), "element", False),
        "access_permissions": (qn(ARCHIVE_NS, "AccessPermission"), "element", True),
        "restrictions": (qn(ARCHIVE_NS, "Restrictions"), "element", False),
        "citation_requirement": (qn(ARCHIVE_NS, "CitationRequirement"), "element", False),
        "deposit_requirement": (qn(ARCHIVE_NS, "DepositRequirement"), "element", False),
        "access_conditions": (qn(ARCHIVE_NS, "AccessConditions"), "element", False),
        "disclaimer": (qn(ARCHIVE_NS, "Disclaimer"), "element", False),
        "access_restriction_date": (qn(ARCHIVE_NS, "AccessRestrictionDate"), "element", False),
        "contact_organization_references": (qn(ARCHIVE_NS, "ContactOrganizationReference"), "reference", True),
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
        qn(ARCHIVE_NS, "TypeOfAccess"),
        qn(ARCHIVE_NS, "AccessTypeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(ARCHIVE_NS, "ConfidentialityStatement"),
        qn(ARCHIVE_NS, "AccessPermission"),
        qn(ARCHIVE_NS, "Restrictions"),
        qn(ARCHIVE_NS, "CitationRequirement"),
        qn(ARCHIVE_NS, "DepositRequirement"),
        qn(ARCHIVE_NS, "AccessConditions"),
        qn(ARCHIVE_NS, "Disclaimer"),
        qn(ARCHIVE_NS, "AccessRestrictionDate"),
        qn(ARCHIVE_NS, "ContactOrganizationReference"),
    ]


@dataclass
class AdditionalInformationFields(MaintainableBase):
    """Any information not captured by the other descriptive objects. The privacy code may be set to indicate access restriction to this information. Supports multiple language versions of the same content a"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "AdditionalInformation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    contents: list[Element] = field(default_factory=list)  # [1..*]
    effective_period: Optional[Element] = None  # [0..1]
    privacy: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "contents": (qn(REUSABLE_NS, "Content"), "element", True),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "privacy": ("privacy", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Content"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]


@dataclass
class AddressFields(MaintainableBase):
    """Location address identifying each part of the address as separate elements, identifying the type of address, the level of privacy associated with the release of the address, and a flag to identify the"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Address")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    type_of_address: Optional[CodeValue] = None  # [0..1]
    lines: list[str] = field(default_factory=list)  # [0..*]
    city_place_local: Optional[str] = None  # [0..1]
    state_province: Optional[str] = None  # [0..1]
    postal_code: Optional[str] = None  # [0..1]
    country_code: Optional[Element] = None  # [0..1]
    geographic_point: Optional[Element] = None  # [0..1]
    time_zone: Optional[CodeValue] = None  # [0..1]
    effective_period: Optional[Element] = None  # [0..1]
    privacy: Optional[str] = None  # @attr
    isPreferred: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_address": (qn(ARCHIVE_NS, "TypeOfAddress"), "code_value", False),
        "lines": (qn(ARCHIVE_NS, "Line"), "str", True),
        "city_place_local": (qn(ARCHIVE_NS, "CityPlaceLocal"), "str", False),
        "state_province": (qn(ARCHIVE_NS, "StateProvince"), "str", False),
        "postal_code": (qn(ARCHIVE_NS, "PostalCode"), "str", False),
        "country_code": (qn(REUSABLE_NS, "CountryCode"), "element", False),
        "geographic_point": (qn(ARCHIVE_NS, "GeographicPoint"), "element", False),
        "time_zone": (qn(REUSABLE_NS, "TimeZone"), "code_value", False),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "privacy": ("privacy", "str"),
        "isPreferred": ("isPreferred", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "TypeOfAddress"),
        qn(ARCHIVE_NS, "Line"),
        qn(ARCHIVE_NS, "CityPlaceLocal"),
        qn(ARCHIVE_NS, "StateProvince"),
        qn(ARCHIVE_NS, "PostalCode"),
        qn(REUSABLE_NS, "CountryCode"),
        qn(ARCHIVE_NS, "GeographicPoint"),
        qn(REUSABLE_NS, "TimeZone"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]


@dataclass
class AgentFields(MaintainableBase):
    """Base class for Individual and Organization. This allows strongly typed references."""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Agent")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
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
    ]


@dataclass
class ArchiveSpecificFields(MaintainableBase):
    """Contains metadata specific to a particular archive's holding. This includes information on the items or collection of items held by the archive, the default terms of access, funding information and bu"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "ArchiveSpecific")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    archive_organization_reference: Optional[Reference] = None  # [0..1]
    items: list[Element] = field(default_factory=list)  # [0..*]
    collections: list[Element] = field(default_factory=list)  # [0..*]
    default_access: list[Element] = field(default_factory=list)  # [0..*]
    funding_informations: list[Element] = field(default_factory=list)  # [0..*]
    budgets: list[Element] = field(default_factory=list)  # [0..*]
    quality_statement_references: list[Reference] = field(default_factory=list)  # [0..*]
    coverage: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "archive_organization_reference": (qn(ARCHIVE_NS, "ArchiveOrganizationReference"), "reference", False),
        "items": (qn(ARCHIVE_NS, "Item"), "element", True),
        "collections": (qn(ARCHIVE_NS, "Collection"), "element", True),
        "default_access": (qn(ARCHIVE_NS, "DefaultAccess"), "element", True),
        "funding_informations": (qn(REUSABLE_NS, "FundingInformation"), "element", True),
        "budgets": (qn(REUSABLE_NS, "Budget"), "element", True),
        "quality_statement_references": (qn(REUSABLE_NS, "QualityStatementReference"), "reference", True),
        "coverage": (qn(REUSABLE_NS, "Coverage"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "ArchiveOrganizationReference"),
        qn(ARCHIVE_NS, "Item"),
        qn(ARCHIVE_NS, "Collection"),
        qn(ARCHIVE_NS, "DefaultAccess"),
        qn(REUSABLE_NS, "FundingInformation"),
        qn(REUSABLE_NS, "Budget"),
        qn(REUSABLE_NS, "QualityStatementReference"),
        qn(REUSABLE_NS, "Coverage"),
    ]


@dataclass
class ArchiveFields(MaintainableBase):
    """A maintainable module containing information related to the archiving (longer term access and/or preservation) of the data and metadata. Note that in DDI Archive refers to a set of processes rather th"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Archive")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    archive_module_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    archive_specifics: list[Element] = field(default_factory=list)  # [0..*]
    organization_schemes: list[Element] = field(default_factory=list)  # [0..*]
    organization_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    lifecycle_information: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "archive_module_names": (qn(ARCHIVE_NS, "ArchiveModuleName"), "intl_string", True),
        "archive_specifics": (qn(ARCHIVE_NS, "ArchiveSpecific"), "element", True),
        "organization_schemes": (qn(ARCHIVE_NS, "OrganizationScheme"), "element", True),
        "organization_scheme_references": (qn(REUSABLE_NS, "OrganizationSchemeReference"), "reference", True),
        "lifecycle_information": (qn(REUSABLE_NS, "LifecycleInformation"), "element", False),
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
        qn(ARCHIVE_NS, "ArchiveModuleName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(ARCHIVE_NS, "ArchiveSpecific"),
        qn(ARCHIVE_NS, "OrganizationScheme"),
        qn(REUSABLE_NS, "OrganizationSchemeReference"),
        qn(REUSABLE_NS, "LifecycleInformation"),
    ]


@dataclass
class CollectionFields(MaintainableBase):
    """Describes a collection of items held or distributed by the archive in connection with a study, group of studies, or resource packages. What constitutes an collection is determined by the archive. Thes"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Collection")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    citation: Optional[Element] = None  # [0..1]
    location_in_archives: list[Element] = field(default_factory=list)  # [0..*]
    call_number: Optional[str] = None  # [0..1]
    uri: Optional[str] = None  # [0..1]
    item_quantity: Optional[int] = None  # [0..1]
    study_class: Optional[Element] = None  # [0..1]
    default_access: Optional[Element] = None  # [0..1]
    original_archive_organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    availability_status: Optional[Element] = None  # [0..1]
    data_file_quantity: Optional[int] = None  # [0..1]
    collection_completeness: Optional[Element] = None  # [0..1]
    items: list[Element] = field(default_factory=list)  # [0..*]
    collections: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "citation": (qn(REUSABLE_NS, "Citation"), "element", False),
        "location_in_archives": (qn(ARCHIVE_NS, "LocationInArchive"), "element", True),
        "call_number": (qn(ARCHIVE_NS, "CallNumber"), "str", False),
        "uri": (qn(REUSABLE_NS, "URI"), "str", False),
        "item_quantity": (qn(ARCHIVE_NS, "ItemQuantity"), "int", False),
        "study_class": (qn(ARCHIVE_NS, "StudyClass"), "element", False),
        "default_access": (qn(ARCHIVE_NS, "DefaultAccess"), "element", False),
        "original_archive_organization_references": (qn(ARCHIVE_NS, "OriginalArchiveOrganizationReference"), "reference", True),
        "availability_status": (qn(ARCHIVE_NS, "AvailabilityStatus"), "element", False),
        "data_file_quantity": (qn(ARCHIVE_NS, "DataFileQuantity"), "int", False),
        "collection_completeness": (qn(ARCHIVE_NS, "CollectionCompleteness"), "element", False),
        "items": (qn(ARCHIVE_NS, "Item"), "element", True),
        "collections": (qn(ARCHIVE_NS, "Collection"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Citation"),
        qn(ARCHIVE_NS, "LocationInArchive"),
        qn(ARCHIVE_NS, "CallNumber"),
        qn(REUSABLE_NS, "URI"),
        qn(ARCHIVE_NS, "ItemQuantity"),
        qn(ARCHIVE_NS, "StudyClass"),
        qn(ARCHIVE_NS, "DefaultAccess"),
        qn(ARCHIVE_NS, "OriginalArchiveOrganizationReference"),
        qn(ARCHIVE_NS, "AvailabilityStatus"),
        qn(ARCHIVE_NS, "DataFileQuantity"),
        qn(ARCHIVE_NS, "CollectionCompleteness"),
        qn(ARCHIVE_NS, "Item"),
        qn(ARCHIVE_NS, "Collection"),
    ]


@dataclass
class ContactInformationFields(MaintainableBase):
    """Contact information for the individual or organization including location specification, address, URL, phone numbers, and other means of communication access. Address, location, telephone, and other m"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "ContactInformation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    location_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    address: list[Element] = field(default_factory=list)  # [0..*]
    telephones: list[Element] = field(default_factory=list)  # [0..*]
    urls: list[Element] = field(default_factory=list)  # [0..*]
    emails: list[Element] = field(default_factory=list)  # [0..*]
    instant_messagings: list[Element] = field(default_factory=list)  # [0..*]
    regional_coverage: Optional[CodeValue] = None  # [0..1]
    type_of_location: Optional[CodeValue] = None  # [0..1]
    privacy: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "location_names": (qn(ARCHIVE_NS, "LocationName"), "intl_string", True),
        "address": (qn(ARCHIVE_NS, "Address"), "element", True),
        "telephones": (qn(ARCHIVE_NS, "Telephone"), "element", True),
        "urls": (qn(ARCHIVE_NS, "URL"), "element", True),
        "emails": (qn(ARCHIVE_NS, "Email"), "element", True),
        "instant_messagings": (qn(ARCHIVE_NS, "InstantMessaging"), "element", True),
        "regional_coverage": (qn(ARCHIVE_NS, "RegionalCoverage"), "code_value", False),
        "type_of_location": (qn(ARCHIVE_NS, "TypeOfLocation"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "privacy": ("privacy", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "LocationName"),
        qn(ARCHIVE_NS, "Address"),
        qn(ARCHIVE_NS, "Telephone"),
        qn(ARCHIVE_NS, "URL"),
        qn(ARCHIVE_NS, "Email"),
        qn(ARCHIVE_NS, "InstantMessaging"),
        qn(ARCHIVE_NS, "RegionalCoverage"),
        qn(ARCHIVE_NS, "TypeOfLocation"),
    ]


@dataclass
class DDIMaintenanceAgencyIDFields(MaintainableBase):
    """Provides the official DDI ID of a maintenance agency as a value taken from the registry cited in @registryID."""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "DDIMaintenanceAgencyID")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    registryID: Optional[str] = None  # @attr
    activationDate: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "registryID": ("registryID", "str"),
        "activationDate": ("activationDate", "str"),
    }


@dataclass
class FormFields(MaintainableBase):
    """A link to a form used by the metadata containing the form number, a statement regarding the contents of the form, a statement as to the mandatory nature of the form and a privacy level designation."""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Form")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    form_number: Optional[str] = None  # [0..1]
    uri: Optional[str] = None  # [0..1]
    statement: Optional[Element] = None  # [0..1]
    isRequired: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "form_number": (qn(ARCHIVE_NS, "FormNumber"), "str", False),
        "uri": (qn(REUSABLE_NS, "URI"), "str", False),
        "statement": (qn(ARCHIVE_NS, "Statement"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isRequired": ("isRequired", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "FormNumber"),
        qn(REUSABLE_NS, "URI"),
        qn(ARCHIVE_NS, "Statement"),
    ]


@dataclass
class IndividualIdentificationFields(MaintainableBase):
    """Identifying information about the individual including name, DDI Maintenance Agency IDs, Researcher IDs, an image and an effective period for the information."""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "IndividualIdentification")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    individual_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    ddi_maintenance_agency_ids: list[Element] = field(default_factory=list)  # [0..*]
    researcher_ids: list[Element] = field(default_factory=list)  # [0..*]
    individual_images: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "individual_names": (qn(ARCHIVE_NS, "IndividualName"), "intl_string", True),
        "ddi_maintenance_agency_ids": (qn(ARCHIVE_NS, "DDIMaintenanceAgencyID"), "element", True),
        "researcher_ids": (qn(ARCHIVE_NS, "ResearcherID"), "element", True),
        "individual_images": (qn(ARCHIVE_NS, "IndividualImage"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "IndividualName"),
        qn(ARCHIVE_NS, "DDIMaintenanceAgencyID"),
        qn(ARCHIVE_NS, "ResearcherID"),
        qn(ARCHIVE_NS, "IndividualImage"),
    ]


@dataclass
class IndividualLanguageFields(MaintainableBase):
    """Use to specify the languages known by the individual in terms of their ability to  speak, read, and write the language. May be repeated to cover multiple languages. This information is useful for fore"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "IndividualLanguage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    language: Optional[CodeValue] = None  # [1..1]
    read: Optional[CodeValue] = None  # [0..1]
    write: Optional[CodeValue] = None  # [0..1]
    speak: Optional[CodeValue] = None  # [0..1]
    effective_period: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "language": (qn(REUSABLE_NS, "Language"), "code_value", False),
        "read": (qn(ARCHIVE_NS, "Read"), "code_value", False),
        "write": (qn(ARCHIVE_NS, "Write"), "code_value", False),
        "speak": (qn(ARCHIVE_NS, "Speak"), "code_value", False),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Language"),
        qn(ARCHIVE_NS, "Read"),
        qn(ARCHIVE_NS, "Write"),
        qn(ARCHIVE_NS, "Speak"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]


@dataclass
class IndividualNameFields(MaintainableBase):
    """The name of an individual broken out into its component parts of prefix, first/given name, middle name, last/family/surname, and suffix. The preferred compilation of the name parts may also be provide"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "IndividualName")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    prefix: Optional[str] = None  # [0..1]
    first_given: Optional[str] = None  # [0..1]
    middles: list[str] = field(default_factory=list)  # [0..*]
    last_family: Optional[str] = None  # [0..1]
    suffix: Optional[str] = None  # [0..1]
    full_name: Optional[Element] = None  # [0..1]
    effective_period: Optional[Element] = None  # [0..1]
    abbreviation: Optional[Element] = None  # [0..1]
    type_of_individual_name: Optional[CodeValue] = None  # [0..1]
    sex: Optional[str] = None  # @attr
    isPreferred: Optional[bool] = None  # @attr
    context: Optional[str] = None  # @attr
    isFormal: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "prefix": (qn(ARCHIVE_NS, "Prefix"), "str", False),
        "first_given": (qn(ARCHIVE_NS, "FirstGiven"), "str", False),
        "middles": (qn(ARCHIVE_NS, "Middle"), "str", True),
        "last_family": (qn(ARCHIVE_NS, "LastFamily"), "str", False),
        "suffix": (qn(ARCHIVE_NS, "Suffix"), "str", False),
        "full_name": (qn(ARCHIVE_NS, "FullName"), "element", False),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
        "abbreviation": (qn(REUSABLE_NS, "Abbreviation"), "element", False),
        "type_of_individual_name": (qn(ARCHIVE_NS, "TypeOfIndividualName"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "sex": ("sex", "str"),
        "isPreferred": ("isPreferred", "bool"),
        "context": ("context", "str"),
        "isFormal": ("isFormal", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "Prefix"),
        qn(ARCHIVE_NS, "FirstGiven"),
        qn(ARCHIVE_NS, "Middle"),
        qn(ARCHIVE_NS, "LastFamily"),
        qn(ARCHIVE_NS, "Suffix"),
        qn(ARCHIVE_NS, "FullName"),
        qn(REUSABLE_NS, "EffectivePeriod"),
        qn(REUSABLE_NS, "Abbreviation"),
        qn(ARCHIVE_NS, "TypeOfIndividualName"),
    ]


@dataclass
class IndividualFields(MaintainableBase):
    """Details of an individual including name, contact information, a definition, keywords to support searching, their regional affiliation, language ability and any additional information. The individual a"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Individual")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    individual_identification: Optional[Element] = None  # [0..1]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    regional_coverages: list[CodeValue] = field(default_factory=list)  # [0..*]
    additional_informations: list[Element] = field(default_factory=list)  # [0..*]
    language_abilities: list[Element] = field(default_factory=list)  # [0..*]
    contact_informations: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    privacy: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "individual_identification": (qn(ARCHIVE_NS, "IndividualIdentification"), "element", False),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "regional_coverages": (qn(ARCHIVE_NS, "RegionalCoverage"), "code_value", True),
        "additional_informations": (qn(ARCHIVE_NS, "AdditionalInformation"), "element", True),
        "language_abilities": (qn(ARCHIVE_NS, "LanguageAbility"), "element", True),
        "contact_informations": (qn(ARCHIVE_NS, "ContactInformation"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "privacy": ("privacy", "str"),
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
        qn(ARCHIVE_NS, "IndividualIdentification"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Keyword"),
        qn(ARCHIVE_NS, "RegionalCoverage"),
        qn(ARCHIVE_NS, "AdditionalInformation"),
        qn(ARCHIVE_NS, "LanguageAbility"),
        qn(ARCHIVE_NS, "ContactInformation"),
    ]


@dataclass
class InstantMessagingFields(MaintainableBase):
    """Indicates type of Instant messaging account identification"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "InstantMessaging")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    im_identification: Optional[str] = None  # [1..1]
    type_of_instant_messaging: Optional[CodeValue] = None  # [1..1]
    effective_period: Optional[Element] = None  # [0..1]
    privacy: Optional[str] = None  # @attr
    isPreferred: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "im_identification": (qn(ARCHIVE_NS, "IMIdentification"), "str", False),
        "type_of_instant_messaging": (qn(ARCHIVE_NS, "TypeOfInstantMessaging"), "code_value", False),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "privacy": ("privacy", "str"),
        "isPreferred": ("isPreferred", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "IMIdentification"),
        qn(ARCHIVE_NS, "TypeOfInstantMessaging"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]


@dataclass
class ItemFields(MaintainableBase):
    """Describes individual items held or distributed by the archive in connection with a study, group of studies, or resource packages. What constitutes an item is determined by the archive. Provides identi"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Item")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    citation: Optional[Element] = None  # [0..1]
    location_in_archives: list[Element] = field(default_factory=list)  # [0..*]
    call_number: Optional[str] = None  # [0..1]
    uri: Optional[str] = None  # [0..1]
    item_format: Optional[CodeValue] = None  # [0..1]
    media: Optional[CodeValue] = None  # [0..1]
    study_class: Optional[Element] = None  # [0..1]
    access: Optional[Element] = None  # [0..1]
    original_archive_organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    availability_status: Optional[Element] = None  # [0..1]
    data_file_quantity: Optional[int] = None  # [0..1]
    collection_completeness: Optional[Element] = None  # [0..1]
    items: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "citation": (qn(REUSABLE_NS, "Citation"), "element", False),
        "location_in_archives": (qn(ARCHIVE_NS, "LocationInArchive"), "element", True),
        "call_number": (qn(ARCHIVE_NS, "CallNumber"), "str", False),
        "uri": (qn(REUSABLE_NS, "URI"), "str", False),
        "item_format": (qn(ARCHIVE_NS, "ItemFormat"), "code_value", False),
        "media": (qn(ARCHIVE_NS, "Media"), "code_value", False),
        "study_class": (qn(ARCHIVE_NS, "StudyClass"), "element", False),
        "access": (qn(ARCHIVE_NS, "Access"), "element", False),
        "original_archive_organization_references": (qn(ARCHIVE_NS, "OriginalArchiveOrganizationReference"), "reference", True),
        "availability_status": (qn(ARCHIVE_NS, "AvailabilityStatus"), "element", False),
        "data_file_quantity": (qn(ARCHIVE_NS, "DataFileQuantity"), "int", False),
        "collection_completeness": (qn(ARCHIVE_NS, "CollectionCompleteness"), "element", False),
        "items": (qn(ARCHIVE_NS, "Item"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Citation"),
        qn(ARCHIVE_NS, "LocationInArchive"),
        qn(ARCHIVE_NS, "CallNumber"),
        qn(REUSABLE_NS, "URI"),
        qn(ARCHIVE_NS, "ItemFormat"),
        qn(ARCHIVE_NS, "Media"),
        qn(ARCHIVE_NS, "StudyClass"),
        qn(ARCHIVE_NS, "Access"),
        qn(ARCHIVE_NS, "OriginalArchiveOrganizationReference"),
        qn(ARCHIVE_NS, "AvailabilityStatus"),
        qn(ARCHIVE_NS, "DataFileQuantity"),
        qn(ARCHIVE_NS, "CollectionCompleteness"),
        qn(ARCHIVE_NS, "Item"),
    ]


@dataclass
class LocationNameFields(MaintainableBase):
    """Name of the location using the DDI Name structure and the ability to add an effective date."""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "LocationName")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    strings: list[Element] = field(default_factory=list)  # [1..*]
    effective_period: Optional[Element] = None  # [0..1]
    isPreferred: Optional[bool] = None  # @attr
    context: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "strings": (qn(REUSABLE_NS, "String"), "element", True),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isPreferred": ("isPreferred", "bool"),
        "context": ("context", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "String"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]


@dataclass
class OrganizationGroupFields(MaintainableBase):
    """Contains a group of Organizations, Individuals, and/or Relations, which may describe an ordered or hierarchical relationship structure. Specifies the purpose of the group, a name, label, and descripti"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "OrganizationGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    type_of_organization_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    individual_references: list[Reference] = field(default_factory=list)  # [0..*]
    relation_references: list[Reference] = field(default_factory=list)  # [0..*]
    organization_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_organization_group": (qn(ARCHIVE_NS, "TypeOfOrganizationGroup"), "code_value", False),
        "names": (qn(ARCHIVE_NS, "OrganizationGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "organization_references": (qn(ARCHIVE_NS, "OrganizationReference"), "reference", True),
        "individual_references": (qn(ARCHIVE_NS, "IndividualReference"), "reference", True),
        "relation_references": (qn(ARCHIVE_NS, "RelationReference"), "reference", True),
        "organization_group_references": (qn(ARCHIVE_NS, "OrganizationGroupReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
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
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(ARCHIVE_NS, "TypeOfOrganizationGroup"),
        qn(ARCHIVE_NS, "OrganizationGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(ARCHIVE_NS, "OrganizationReference"),
        qn(ARCHIVE_NS, "IndividualReference"),
        qn(ARCHIVE_NS, "RelationReference"),
        qn(ARCHIVE_NS, "OrganizationGroupReference"),
    ]


@dataclass
class OrganizationIdentificationFields(MaintainableBase):
    """Means of identifying an organization. The structure contains a repeatable OrganizationName. At minimum enter the current legal or formal name setting the attribute isFormal to "true". Additional Organ"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "OrganizationIdentification")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    organization_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    ddi_maintenance_agency_ids: list[Element] = field(default_factory=list)  # [0..*]
    organization_images: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "organization_names": (qn(ARCHIVE_NS, "OrganizationName"), "intl_string", True),
        "ddi_maintenance_agency_ids": (qn(ARCHIVE_NS, "DDIMaintenanceAgencyID"), "element", True),
        "organization_images": (qn(ARCHIVE_NS, "OrganizationImage"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "OrganizationName"),
        qn(ARCHIVE_NS, "DDIMaintenanceAgencyID"),
        qn(ARCHIVE_NS, "OrganizationImage"),
    ]


@dataclass
class OrganizationNameFields(MaintainableBase):
    """Names by which the organization is known. Use the attribute isFormal="true" to designate the legal or formal name of the Organization. The preferred name should be noted with the isPreferred attribute"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "OrganizationName")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    strings: list[Element] = field(default_factory=list)  # [1..*]
    abbreviation: Optional[Element] = None  # [0..1]
    type_of_organization_name: Optional[CodeValue] = None  # [0..1]
    effective_period: Optional[Element] = None  # [0..1]
    isPreferred: Optional[bool] = None  # @attr
    context: Optional[str] = None  # @attr
    isFormal: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "strings": (qn(REUSABLE_NS, "String"), "element", True),
        "abbreviation": (qn(REUSABLE_NS, "Abbreviation"), "element", False),
        "type_of_organization_name": (qn(ARCHIVE_NS, "TypeOfOrganizationName"), "code_value", False),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isPreferred": ("isPreferred", "bool"),
        "context": ("context", "str"),
        "isFormal": ("isFormal", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "String"),
        qn(REUSABLE_NS, "Abbreviation"),
        qn(ARCHIVE_NS, "TypeOfOrganizationName"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]


@dataclass
class OrganizationSchemeFields(MaintainableBase):
    """XSD type: OrganizationSchemeType"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "OrganizationScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    organization_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    organizations: list[Element] = field(default_factory=list)  # [0..*]
    organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    individuals: list[Element] = field(default_factory=list)  # [0..*]
    individual_references: list[Reference] = field(default_factory=list)  # [0..*]
    relations: list[Element] = field(default_factory=list)  # [0..*]
    relation_references: list[Reference] = field(default_factory=list)  # [0..*]
    organization_groups: list[Element] = field(default_factory=list)  # [0..*]
    organization_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(ARCHIVE_NS, "OrganizationSchemeName"), "intl_string", True),
        "organization_scheme_references": (qn(REUSABLE_NS, "OrganizationSchemeReference"), "reference", True),
        "organizations": (qn(ARCHIVE_NS, "Organization"), "element", True),
        "organization_references": (qn(ARCHIVE_NS, "OrganizationReference"), "reference", True),
        "individuals": (qn(ARCHIVE_NS, "Individual"), "element", True),
        "individual_references": (qn(ARCHIVE_NS, "IndividualReference"), "reference", True),
        "relations": (qn(ARCHIVE_NS, "Relation"), "element", True),
        "relation_references": (qn(ARCHIVE_NS, "RelationReference"), "reference", True),
        "organization_groups": (qn(ARCHIVE_NS, "OrganizationGroup"), "element", True),
        "organization_group_references": (qn(ARCHIVE_NS, "OrganizationGroupReference"), "reference", True),
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
        qn(ARCHIVE_NS, "OrganizationSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OrganizationSchemeReference"),
        qn(ARCHIVE_NS, "Organization"),
        qn(ARCHIVE_NS, "OrganizationReference"),
        qn(ARCHIVE_NS, "Individual"),
        qn(ARCHIVE_NS, "IndividualReference"),
        qn(ARCHIVE_NS, "Relation"),
        qn(ARCHIVE_NS, "RelationReference"),
        qn(ARCHIVE_NS, "OrganizationGroup"),
        qn(ARCHIVE_NS, "OrganizationGroupReference"),
    ]


@dataclass
class OrganizationFields(MaintainableBase):
    """Details of an organization including name, contact information, a description, keywords to support searching, their regional affiliation, and any additional information. In addition the organization m"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Organization")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    organization_identification: Optional[Element] = None  # [0..1]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    regional_coverages: list[CodeValue] = field(default_factory=list)  # [0..*]
    additional_informations: list[Element] = field(default_factory=list)  # [0..*]
    version_distinctions: list[Element] = field(default_factory=list)  # [0..*]
    contact_informations: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    privacy: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "organization_identification": (qn(ARCHIVE_NS, "OrganizationIdentification"), "element", False),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "regional_coverages": (qn(ARCHIVE_NS, "RegionalCoverage"), "code_value", True),
        "additional_informations": (qn(ARCHIVE_NS, "AdditionalInformation"), "element", True),
        "version_distinctions": (qn(ARCHIVE_NS, "VersionDistinction"), "element", True),
        "contact_informations": (qn(ARCHIVE_NS, "ContactInformation"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "privacy": ("privacy", "str"),
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
        qn(ARCHIVE_NS, "OrganizationIdentification"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Keyword"),
        qn(ARCHIVE_NS, "RegionalCoverage"),
        qn(ARCHIVE_NS, "AdditionalInformation"),
        qn(ARCHIVE_NS, "VersionDistinction"),
        qn(ARCHIVE_NS, "ContactInformation"),
    ]


@dataclass
class PrivateImageFields(MaintainableBase):
    """References an image using the standard Image description. In addition to the standard attributes provides an effective date (period), the type of image, and a privacy ranking."""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "PrivateImage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    image_location: Optional[str] = None  # [1..1]
    type_of_image: Optional[CodeValue] = None  # [0..1]
    effective_period: Optional[Element] = None  # [0..1]
    dpi: Optional[int] = None  # @attr
    languageOfImage: Optional[str] = None  # @attr
    privacy: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "image_location": (qn(REUSABLE_NS, "ImageLocation"), "str", False),
        "type_of_image": (qn(REUSABLE_NS, "TypeOfImage"), "code_value", False),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "dpi": ("dpi", "int"),
        "languageOfImage": ("languageOfImage", "str"),
        "privacy": ("privacy", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ImageLocation"),
        qn(REUSABLE_NS, "TypeOfImage"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]


@dataclass
class RelationFields(MaintainableBase):
    """Describes the relationship between any two organizations or individual, or an individual and an organization. This is a pairwise relationship and relationships may be unidirectional. Identifies the So"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Relation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    source_object: Optional[Element] = None  # [1..1]
    target_object: Optional[Element] = None  # [1..1]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    effective_periods: list[Element] = field(default_factory=list)  # [0..*]
    additional_informations: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    privacy: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "source_object": (qn(ARCHIVE_NS, "SourceObject"), "element", False),
        "target_object": (qn(ARCHIVE_NS, "TargetObject"), "element", False),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "effective_periods": (qn(REUSABLE_NS, "EffectivePeriod"), "element", True),
        "additional_informations": (qn(ARCHIVE_NS, "AdditionalInformation"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "privacy": ("privacy", "str"),
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
        qn(ARCHIVE_NS, "SourceObject"),
        qn(ARCHIVE_NS, "TargetObject"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "EffectivePeriod"),
        qn(ARCHIVE_NS, "AdditionalInformation"),
    ]


@dataclass
class ResearcherIDFields(MaintainableBase):
    """Captures an individuals assigned researcher ID within a specified system. Includes the type or researcher ID provided, the ID, a URI of the location or link, and a description of the researcher ID pro"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "ResearcherID")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    type_of_id: Optional[CodeValue] = None  # [0..1]
    researcher_identification: Optional[str] = None  # [0..1]
    uri: Optional[str] = None  # [0..1]
    effective_period: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_id": (qn(ARCHIVE_NS, "TypeOfID"), "code_value", False),
        "researcher_identification": (qn(ARCHIVE_NS, "ResearcherIdentification"), "str", False),
        "uri": (qn(REUSABLE_NS, "URI"), "str", False),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "TypeOfID"),
        qn(ARCHIVE_NS, "ResearcherIdentification"),
        qn(REUSABLE_NS, "URI"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]


@dataclass
class RoleFields(MaintainableBase):
    """Describes the role of Target Individual or Organization in relation to the Source Object. Provides a description and classification of the role, the period for which the role was valid, and any additi"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Role")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    effective_periods: list[Element] = field(default_factory=list)  # [0..*]
    additional_informations: list[Element] = field(default_factory=list)  # [0..*]
    privacy: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "effective_periods": (qn(REUSABLE_NS, "EffectivePeriod"), "element", True),
        "additional_informations": (qn(ARCHIVE_NS, "AdditionalInformation"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "privacy": ("privacy", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "EffectivePeriod"),
        qn(ARCHIVE_NS, "AdditionalInformation"),
    ]


@dataclass
class SourceObjectFields(MaintainableBase):
    """Identifies the Source organization or individual in the relationship. References either an Organization or an Individual and specifies their relationship in terms of parent, child, or sibling."""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "SourceObject")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    organization_reference: Optional[Reference] = None  # [1..1]
    individual_reference: Optional[Reference] = None  # [1..1]
    relationship_code: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "organization_reference": (qn(ARCHIVE_NS, "OrganizationReference"), "reference", False),
        "individual_reference": (qn(ARCHIVE_NS, "IndividualReference"), "reference", False),
        "relationship_code": (qn(ARCHIVE_NS, "RelationshipCode"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "OrganizationReference"),
        qn(ARCHIVE_NS, "IndividualReference"),
        qn(ARCHIVE_NS, "RelationshipCode"),
    ]


@dataclass
class StudyClassFields(MaintainableBase):
    """An archive specific classification. This may be a topical classification, a classification of intended processing levels, or information on the processing status. Consists of a description of the stud"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "StudyClass")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    class_type: Optional[CodeValue] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "class_type": (qn(ARCHIVE_NS, "ClassType"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(ARCHIVE_NS, "ClassType"),
    ]


@dataclass
class TargetObjectFields(MaintainableBase):
    """Identifies the Target organization or individual in the relationship. References either an Organiztion or an Individual and specifies the role of the Target in relationship to the Source. Multiple rol"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "TargetObject")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    organization_reference: Optional[Reference] = None  # [1..1]
    individual_reference: Optional[Reference] = None  # [1..1]
    roles: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "organization_reference": (qn(ARCHIVE_NS, "OrganizationReference"), "reference", False),
        "individual_reference": (qn(ARCHIVE_NS, "IndividualReference"), "reference", False),
        "roles": (qn(ARCHIVE_NS, "Role"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "OrganizationReference"),
        qn(ARCHIVE_NS, "IndividualReference"),
        qn(ARCHIVE_NS, "Role"),
    ]


@dataclass
class TelephoneFields(MaintainableBase):
    """Details of a telephone number including the number, type of number, a privacy setting and an indication of whether this is the preferred contact number."""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Telephone")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    telephone_number: Optional[str] = None  # [1..1]
    type_of_telephone: Optional[CodeValue] = None  # [0..1]
    effective_period: Optional[Element] = None  # [0..1]
    privacy: Optional[str] = None  # @attr
    isPreferred: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "telephone_number": (qn(ARCHIVE_NS, "TelephoneNumber"), "str", False),
        "type_of_telephone": (qn(ARCHIVE_NS, "TypeOfTelephone"), "code_value", False),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "privacy": ("privacy", "str"),
        "isPreferred": ("isPreferred", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "TelephoneNumber"),
        qn(ARCHIVE_NS, "TypeOfTelephone"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]


@dataclass
class URLFields(MaintainableBase):
    """A web site URL"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "URL")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    privacy: Optional[str] = None  # @attr
    isPreferred: Optional[bool] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "privacy": ("privacy", "str"),
        "isPreferred": ("isPreferred", "bool"),
    }


@dataclass
class VersionDistinctionFields(MaintainableBase):
    """Describes the data versioning scheme(s) used by an organization. If more than one, Name should differentiate between a standard versioning structure used by the organization and special structures use"""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "VersionDistinction")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    effective_period: Optional[Element] = None  # [0..1]
    regExp: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(ARCHIVE_NS, "VersionDistinctionName"), "intl_string", True),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "regExp": ("regExp", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(ARCHIVE_NS, "VersionDistinctionName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]

