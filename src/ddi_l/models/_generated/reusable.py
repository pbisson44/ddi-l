"""AUTO-GENERATED base dataclasses for DDI 3.3 — reusable module.

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
from ddi_l.constants import REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class AbstractIdentifiableFields(MaintainableBase):
    """Used to identify described identifiable objects for purposes of internal and/or external referencing. Elements of this type cannot be versioned or maintained except as part of a complex parent element"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "AbstractIdentifiable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
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
    ]


@dataclass
class AbstractMaintainableFields(MaintainableBase):
    """Used to identify described maintainable objects for purposes of internal and/or external referencing. Elements of this type may be maintained as independent objects (outside of a parent object). Provi"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "AbstractMaintainable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
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
    ]


@dataclass
class AbstractVersionableFields(MaintainableBase):
    """Used to identify described versionable objects for purposes of internal and/or external referencing. Elements of this type cannot be maintained except as part of a complex parent element. Provides con"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "AbstractVersionable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
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
    ]


@dataclass
class AccessRestrictionDateFields(MaintainableBase):
    """The date or date range of the access restriction for all or portions of the data. Includes a reason for the access restriction as well as the user group to which the restriction applies."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "AccessRestrictionDate")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    simple_date: Optional[Element] = None  # [1..1]
    historical_date: Optional[Element] = None  # [0..1]
    start_date: Optional[Element] = None  # [1..1]
    historical_start_date: Optional[Element] = None  # [0..1]
    end_date: Optional[Element] = None  # [0..1]
    historical_end_date: Optional[Element] = None  # [0..1]
    cycle: Optional[int] = None  # [0..1]
    reason: Optional[Element] = None  # [0..1]
    user: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "simple_date": (qn(REUSABLE_NS, "SimpleDate"), "element", False),
        "historical_date": (qn(REUSABLE_NS, "HistoricalDate"), "element", False),
        "start_date": (qn(REUSABLE_NS, "StartDate"), "element", False),
        "historical_start_date": (qn(REUSABLE_NS, "HistoricalStartDate"), "element", False),
        "end_date": (qn(REUSABLE_NS, "EndDate"), "element", False),
        "historical_end_date": (qn(REUSABLE_NS, "HistoricalEndDate"), "element", False),
        "cycle": (qn(REUSABLE_NS, "Cycle"), "int", False),
        "reason": (qn(REUSABLE_NS, "Reason"), "element", False),
        "user": (qn(REUSABLE_NS, "User"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "SimpleDate"),
        qn(REUSABLE_NS, "HistoricalDate"),
        qn(REUSABLE_NS, "StartDate"),
        qn(REUSABLE_NS, "HistoricalStartDate"),
        qn(REUSABLE_NS, "EndDate"),
        qn(REUSABLE_NS, "HistoricalEndDate"),
        qn(REUSABLE_NS, "Cycle"),
        qn(REUSABLE_NS, "EndDate"),
        qn(REUSABLE_NS, "HistoricalEndDate"),
        qn(REUSABLE_NS, "Reason"),
        qn(REUSABLE_NS, "User"),
    ]


@dataclass
class ActionFields(MaintainableBase):
    """Describes the region of an image, recording, or text where an action where a specified action is performed and the type of action taken (i.e., Mark an "X" where the actor should be standing on the pic"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Action")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    region_of_action: Optional[Element] = None  # [0..1]
    regExp: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "region_of_action": (qn(REUSABLE_NS, "RegionOfAction"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "regExp": ("regExp", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RegionOfAction"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class AnchorFields(MaintainableBase):
    """Allows for the attachment of a category label at any anchor point in a scale."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Anchor")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    category_reference: Optional[Reference] = None  # [0..1]
    value: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "category_reference": (qn(REUSABLE_NS, "CategoryReference"), "reference", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "value": ("value", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "CategoryReference"),
    ]


@dataclass
class ApprovalReviewFields(MaintainableBase):
    """Provides information about the Approval Review undertaken in relation to the activity. Identifies the organization processing the review, the role of the approval review organization, case number, des"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ApprovalReview")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_approval_reviews: list[CodeValue] = field(default_factory=list)  # [0..*]
    review_object_references: list[Reference] = field(default_factory=list)  # [0..*]
    agency_organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    reviewer_role: Optional[CodeValue] = None  # [0..1]
    reference_identifiers: list[str] = field(default_factory=list)  # [0..*]
    approval_review_document: Optional[Element] = None  # [1..1]
    approval_review_document_reference: Optional[Reference] = None  # [1..1]
    application_date: Optional[Element] = None  # [0..1]
    approval_date: Optional[Element] = None  # [0..1]
    approved_period: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_approval_reviews": (qn(REUSABLE_NS, "TypeOfApprovalReview"), "code_value", True),
        "review_object_references": (qn(REUSABLE_NS, "ReviewObjectReference"), "reference", True),
        "agency_organization_references": (qn(REUSABLE_NS, "AgencyOrganizationReference"), "reference", True),
        "reviewer_role": (qn(REUSABLE_NS, "ReviewerRole"), "code_value", False),
        "reference_identifiers": (qn(REUSABLE_NS, "ReferenceIdentifier"), "str", True),
        "approval_review_document": (qn(REUSABLE_NS, "ApprovalReviewDocument"), "element", False),
        "approval_review_document_reference": (qn(REUSABLE_NS, "ApprovalReviewDocumentReference"), "reference", False),
        "application_date": (qn(REUSABLE_NS, "ApplicationDate"), "element", False),
        "approval_date": (qn(REUSABLE_NS, "ApprovalDate"), "element", False),
        "approved_period": (qn(REUSABLE_NS, "ApprovedPeriod"), "element", False),
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
        qn(REUSABLE_NS, "TypeOfApprovalReview"),
        qn(REUSABLE_NS, "ReviewObjectReference"),
        qn(REUSABLE_NS, "AgencyOrganizationReference"),
        qn(REUSABLE_NS, "ReviewerRole"),
        qn(REUSABLE_NS, "ReferenceIdentifier"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ApprovalReviewDocument"),
        qn(REUSABLE_NS, "ApprovalReviewDocumentReference"),
        qn(REUSABLE_NS, "ApplicationDate"),
        qn(REUSABLE_NS, "ApprovalDate"),
        qn(REUSABLE_NS, "ApprovedPeriod"),
    ]


@dataclass
class AreaCoverageFields(MaintainableBase):
    """Use to specify the area of land, water, total or other area coverage in terms of square miles/kilometers or other measure."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "AreaCoverage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_area: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    area_measure: Optional[float] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_area": (qn(REUSABLE_NS, "TypeOfArea"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "area_measure": (qn(REUSABLE_NS, "AreaMeasure"), "float", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "TypeOfArea"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "AreaMeasure"),
    ]


@dataclass
class AudioFields(MaintainableBase):
    """Describes the type and length of the audio segment."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Audio")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_audio_clip: Optional[CodeValue] = None  # [1..1]
    audio_clip_begin: Optional[str] = None  # [0..1]
    audio_clip_end: Optional[str] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_audio_clip": (qn(REUSABLE_NS, "TypeOfAudioClip"), "code_value", False),
        "audio_clip_begin": (qn(REUSABLE_NS, "AudioClipBegin"), "str", False),
        "audio_clip_end": (qn(REUSABLE_NS, "AudioClipEnd"), "str", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "TypeOfAudioClip"),
        qn(REUSABLE_NS, "AudioClipBegin"),
        qn(REUSABLE_NS, "AudioClipEnd"),
    ]


@dataclass
class AuthorizationSourceFields(MaintainableBase):
    """Identifies the authorizing agency for the study and allows for the full text of the authorization (law, regulation, or other form of authorization). May be used to list authorizations from oversight c"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "AuthorizationSource")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    authorizing_agency_references: list[Reference] = field(default_factory=list)  # [0..*]
    statement_of_authorizations: list[Element] = field(default_factory=list)  # [0..*]
    legal_mandates: list[str] = field(default_factory=list)  # [0..*]
    authorizationDate: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "authorizing_agency_references": (qn(REUSABLE_NS, "AuthorizingAgencyReference"), "reference", True),
        "statement_of_authorizations": (qn(REUSABLE_NS, "StatementOfAuthorization"), "element", True),
        "legal_mandates": (qn(REUSABLE_NS, "LegalMandate"), "str", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "authorizationDate": ("authorizationDate", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "AuthorizingAgencyReference"),
        qn(REUSABLE_NS, "StatementOfAuthorization"),
        qn(REUSABLE_NS, "LegalMandate"),
    ]


@dataclass
class AuthorizedPolicySourceFields(MaintainableBase):
    """Description and link to the policy source using the DDI Other Material structure."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "AuthorizedPolicySource")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    other_materials: list[Element] = field(default_factory=list)  # [0..*]
    other_material_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "other_materials": (qn(REUSABLE_NS, "OtherMaterial"), "element", True),
        "other_material_references": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
    ]


@dataclass
class AuthorizedSourceFields(MaintainableBase):
    """A stack of LocationValueReferences to each of the locations of the specified PrimaryComponentLevel type that make up the Component Area. Includes a GeographicTime to allow for repetition for change ov"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "AuthorizedSource")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    other_material: Optional[Element] = None  # [1..1]
    other_material_reference: Optional[Reference] = None  # [1..1]
    identifier_parsing_information: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "other_material": (qn(REUSABLE_NS, "OtherMaterial"), "element", False),
        "other_material_reference": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", False),
        "identifier_parsing_information": (qn(REUSABLE_NS, "IdentifierParsingInformation"), "element", False),
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
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
        qn(REUSABLE_NS, "IdentifierParsingInformation"),
    ]


@dataclass
class BasedOnObjectFields(MaintainableBase):
    """Use when creating an object that is based on an existing object or objects that are managed by a different agency or when the new object is NOT simply a version change but you wish to maintain a refer"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "BasedOnObject")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    based_on_references: list[Reference] = field(default_factory=list)  # [0..*]
    based_on_rationale_description: Optional[Element] = None  # [0..1]
    based_on_rationale_code: Optional[CodeValue] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "based_on_references": (qn(REUSABLE_NS, "BasedOnReference"), "reference", True),
        "based_on_rationale_description": (qn(REUSABLE_NS, "BasedOnRationaleDescription"), "element", False),
        "based_on_rationale_code": (qn(REUSABLE_NS, "BasedOnRationaleCode"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "BasedOnReference"),
        qn(REUSABLE_NS, "BasedOnRationaleDescription"),
        qn(REUSABLE_NS, "BasedOnRationaleCode"),
    ]


@dataclass
class BasicIncrementFields(MaintainableBase):
    """Describes the start, end, and increment value for an incremental string (numeric, character, or length)."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "BasicIncrement")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    increment: Optional[str] = None  # @attr
    startValue: Optional[str] = None  # @attr
    endValue: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "increment": ("increment", "str"),
        "startValue": ("startValue", "str"),
        "endValue": ("endValue", "str"),
    }


@dataclass
class BibliographicNameFields(MaintainableBase):
    """Personal names should be listed surname or family name first, followed by forename or given name. When in doubt, give the name as it appears, and do not invert. In the case of organizations where ther"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "BibliographicName")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    strings: list[Element] = field(default_factory=list)  # [1..*]
    affiliation: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "strings": (qn(REUSABLE_NS, "String"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "affiliation": ("affiliation", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "String"),
    ]


@dataclass
class BindingFields(MaintainableBase):
    """A structure used to bind the content of a parameter declared as the source to a parameter declared as the target. For example, binding the output of a question to the input of a generation instruction"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Binding")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    source_parameter_reference: Optional[Reference] = None  # [1..1]
    target_parameter_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "source_parameter_reference": (qn(REUSABLE_NS, "SourceParameterReference"), "reference", False),
        "target_parameter_reference": (qn(REUSABLE_NS, "TargetParameterReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "SourceParameterReference"),
        qn(REUSABLE_NS, "TargetParameterReference"),
    ]


@dataclass
class BoundingBoxFields(MaintainableBase):
    """Set of north, south, east, west coordinates defining a rectangle that encompasses the full extent of geographic coverage."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "BoundingBox")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    west_longitude: Optional[Element] = None  # [1..1]
    east_longitude: Optional[Element] = None  # [1..1]
    south_latitude: Optional[Element] = None  # [1..1]
    north_latitude: Optional[Element] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "west_longitude": (qn(REUSABLE_NS, "WestLongitude"), "element", False),
        "east_longitude": (qn(REUSABLE_NS, "EastLongitude"), "element", False),
        "south_latitude": (qn(REUSABLE_NS, "SouthLatitude"), "element", False),
        "north_latitude": (qn(REUSABLE_NS, "NorthLatitude"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "WestLongitude"),
        qn(REUSABLE_NS, "EastLongitude"),
        qn(REUSABLE_NS, "SouthLatitude"),
        qn(REUSABLE_NS, "NorthLatitude"),
    ]


@dataclass
class BudgetDocumentFields(MaintainableBase):
    """Description and link to the Budget Document using the DDI Other Material structure."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "BudgetDocument")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    other_material: Optional[Element] = None  # [1..1]
    other_material_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "other_material": (qn(REUSABLE_NS, "OtherMaterial"), "element", False),
        "other_material_reference": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
    ]


@dataclass
class BudgetFields(MaintainableBase):
    """A description of the budget for any of the main publication types that can contain a reference to an external budget document."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Budget")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    budget_documents: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "budget_documents": (qn(REUSABLE_NS, "BudgetDocument"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "BudgetDocument"),
    ]


@dataclass
class CategoryRepresentationBaseFields(MaintainableBase):
    """Describes a representation based on categorization. The CategorySchemeReference allows for the exclusion of selected items from the use of the CategoryScheme as a representation."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "CategoryRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    category_scheme_reference: Optional[Reference] = None  # [1..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "category_scheme_reference": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
    ]


@dataclass
class CharacterParameterFields(MaintainableBase):
    """Specification of the character offset for the beginning and end of the segment."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "CharacterParameter")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    start_char_offset: Optional[int] = None  # [1..1]
    end_char_offset: Optional[int] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "start_char_offset": (qn(REUSABLE_NS, "StartCharOffset"), "int", False),
        "end_char_offset": (qn(REUSABLE_NS, "EndCharOffset"), "int", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "StartCharOffset"),
        qn(REUSABLE_NS, "EndCharOffset"),
    ]


@dataclass
class CitationFields(MaintainableBase):
    """Provides bibliographic citation information for a DDI instance, a group of studies, a study unit, or a physical instance. Note that a native DDI citation is required - the citation information may be """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Citation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    title: Optional[Element] = None  # [0..1]
    sub_titles: list[Element] = field(default_factory=list)  # [0..*]
    alternate_titles: list[Element] = field(default_factory=list)  # [0..*]
    creators: list[Element] = field(default_factory=list)  # [0..*]
    publishers: list[Element] = field(default_factory=list)  # [0..*]
    contributors: list[Element] = field(default_factory=list)  # [0..*]
    publication_date: Optional[Element] = None  # [0..1]
    languages: list[CodeValue] = field(default_factory=list)  # [0..*]
    international_identifiers: list[Element] = field(default_factory=list)  # [0..*]
    copyrights: list[Element] = field(default_factory=list)  # [0..*]
    anies: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "title": (qn(REUSABLE_NS, "Title"), "element", False),
        "sub_titles": (qn(REUSABLE_NS, "SubTitle"), "element", True),
        "alternate_titles": (qn(REUSABLE_NS, "AlternateTitle"), "element", True),
        "creators": (qn(REUSABLE_NS, "Creator"), "element", True),
        "publishers": (qn(REUSABLE_NS, "Publisher"), "element", True),
        "contributors": (qn(REUSABLE_NS, "Contributor"), "element", True),
        "publication_date": (qn(REUSABLE_NS, "PublicationDate"), "element", False),
        "languages": (qn(REUSABLE_NS, "Language"), "code_value", True),
        "international_identifiers": (qn(REUSABLE_NS, "InternationalIdentifier"), "element", True),
        "copyrights": (qn(REUSABLE_NS, "Copyright"), "element", True),
        "anies": (qn("http://purl.org/dc/elements/1.1/", "any"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Title"),
        qn(REUSABLE_NS, "SubTitle"),
        qn(REUSABLE_NS, "AlternateTitle"),
        qn(REUSABLE_NS, "Creator"),
        qn(REUSABLE_NS, "Publisher"),
        qn(REUSABLE_NS, "Contributor"),
        qn(REUSABLE_NS, "PublicationDate"),
        qn(REUSABLE_NS, "Language"),
        qn(REUSABLE_NS, "InternationalIdentifier"),
        qn(REUSABLE_NS, "Copyright"),
        qn("http://purl.org/dc/elements/1.1/", "any"),
    ]


@dataclass
class CodeRepresentationBaseFields(MaintainableBase):
    """Describes the use of all or part of a CodeList as a representation used by a question response domain or variable value representation."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "CodeRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    code_list_reference: Optional[Reference] = None  # [1..1]
    statistical_classification_reference: Optional[Reference] = None  # [1..1]
    code_subset_information: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "code_list_reference": (qn(REUSABLE_NS, "CodeListReference"), "reference", False),
        "statistical_classification_reference": (qn(REUSABLE_NS, "StatisticalClassificationReference"), "reference", False),
        "code_subset_information": (qn(REUSABLE_NS, "CodeSubsetInformation"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "CodeListReference"),
        qn(REUSABLE_NS, "StatisticalClassificationReference"),
        qn(REUSABLE_NS, "CodeSubsetInformation"),
    ]


@dataclass
class CodeSubsetInformationFields(MaintainableBase):
    """Allows further specification of the codes to use from the CodeList by defining the level or only the most discrete codes of a hierarchical CodeList, the range of codes to use, or an itemized sub-set."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "CodeSubsetInformation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    included_levels: list[int] = field(default_factory=list)  # [0..*]
    included_code: Optional[Element] = None  # [0..1]
    data_existence: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "included_levels": (qn(REUSABLE_NS, "IncludedLevel"), "int", True),
        "included_code": (qn(REUSABLE_NS, "IncludedCode"), "element", False),
        "data_existence": (qn(REUSABLE_NS, "DataExistence"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "IncludedLevel"),
        qn(REUSABLE_NS, "IncludedCode"),
        qn(REUSABLE_NS, "DataExistence"),
    ]


@dataclass
class CodeValueFields(MaintainableBase):
    """Allows for string content which may be taken from an externally maintained controlled vocabulary (code value). If the content is from a controlled vocabulary provide the code value, as well as a refer"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "CodeValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    controlledVocabularyID: Optional[str] = None  # @attr
    controlledVocabularyName: Optional[str] = None  # @attr
    controlledVocabularyAgencyName: Optional[str] = None  # @attr
    controlledVocabularyVersionID: Optional[str] = None  # @attr
    otherValue: Optional[str] = None  # @attr
    controlledVocabularyURN: Optional[str] = None  # @attr
    controlledVocabularySchemeURN: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "controlledVocabularyID": ("controlledVocabularyID", "str"),
        "controlledVocabularyName": ("controlledVocabularyName", "str"),
        "controlledVocabularyAgencyName": ("controlledVocabularyAgencyName", "str"),
        "controlledVocabularyVersionID": ("controlledVocabularyVersionID", "str"),
        "otherValue": ("otherValue", "str"),
        "controlledVocabularyURN": ("controlledVocabularyURN", "str"),
        "controlledVocabularySchemeURN": ("controlledVocabularySchemeURN", "str"),
    }


@dataclass
class CommandCodeFields(MaintainableBase):
    """Contains information on the command used for processing data. Contains a description of the command which should clarify for the user the purpose and process of the command, an in-line provision of th"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "CommandCode")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    commands: list[Element] = field(default_factory=list)  # [0..*]
    command_files: list[Element] = field(default_factory=list)  # [0..*]
    structured_command: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "commands": (qn(REUSABLE_NS, "Command"), "element", True),
        "command_files": (qn(REUSABLE_NS, "CommandFile"), "element", True),
        "structured_command": (qn(REUSABLE_NS, "StructuredCommand"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Command"),
        qn(REUSABLE_NS, "CommandFile"),
        qn(REUSABLE_NS, "StructuredCommand"),
    ]


@dataclass
class CommandFileFields(MaintainableBase):
    """Identifies and provides a link to an external copy of the command, for example, a SAS Command Code script. Designates the programming language of the command file, designates input and output paramete"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "CommandFile")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    program_language: Optional[CodeValue] = None  # [1..1]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    location: Optional[Element] = None  # [0..1]
    uri: Optional[str] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "program_language": (qn(REUSABLE_NS, "ProgramLanguage"), "code_value", False),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "location": (qn(REUSABLE_NS, "Location"), "element", False),
        "uri": (qn(REUSABLE_NS, "URI"), "str", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ProgramLanguage"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(REUSABLE_NS, "Location"),
        qn(REUSABLE_NS, "URI"),
    ]


@dataclass
class CommandFields(MaintainableBase):
    """Provides the following information on the command: The content of the command, the programming language used, the pieces of information (InParameters) used by the command, the pieces of information cr"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Command")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    program_language: Optional[CodeValue] = None  # [1..1]
    in_parameters: list[Element] = field(default_factory=list)  # [0..*]
    out_parameters: list[Element] = field(default_factory=list)  # [0..*]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    command_content: Optional[str] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "program_language": (qn(REUSABLE_NS, "ProgramLanguage"), "code_value", False),
        "in_parameters": (qn(REUSABLE_NS, "InParameter"), "element", True),
        "out_parameters": (qn(REUSABLE_NS, "OutParameter"), "element", True),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
        "command_content": (qn(REUSABLE_NS, "CommandContent"), "str", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ProgramLanguage"),
        qn(REUSABLE_NS, "InParameter"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "Binding"),
        qn(REUSABLE_NS, "CommandContent"),
    ]


@dataclass
class ComplianceDefinitionFields(MaintainableBase):
    """Provides a list of quality concepts in the quality standard."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ComplianceDefinition")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    compliance_concept_reference: Optional[Reference] = None  # [0..1]
    external_compliance_code: Optional[CodeValue] = None  # [0..1]
    compliance_requirements: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "compliance_concept_reference": (qn(REUSABLE_NS, "ComplianceConceptReference"), "reference", False),
        "external_compliance_code": (qn(REUSABLE_NS, "ExternalComplianceCode"), "code_value", False),
        "compliance_requirements": (qn(REUSABLE_NS, "ComplianceRequirements"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ComplianceConceptReference"),
        qn(REUSABLE_NS, "ExternalComplianceCode"),
        qn(REUSABLE_NS, "ComplianceRequirements"),
    ]


@dataclass
class ComplianceFields(MaintainableBase):
    """Allows for a quality statement based on frameworks to be described using itemized properties. A reference to a concept, a coded value, or both can be used to specify the property from the standard fra"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Compliance")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    compliance_concept_reference: Optional[Reference] = None  # [0..1]
    external_compliance_code: Optional[CodeValue] = None  # [0..1]
    compliance_description: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "compliance_concept_reference": (qn(REUSABLE_NS, "ComplianceConceptReference"), "reference", False),
        "external_compliance_code": (qn(REUSABLE_NS, "ExternalComplianceCode"), "code_value", False),
        "compliance_description": (qn(REUSABLE_NS, "ComplianceDescription"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ComplianceConceptReference"),
        qn(REUSABLE_NS, "ExternalComplianceCode"),
        qn(REUSABLE_NS, "ComplianceDescription"),
    ]


@dataclass
class ContentDateOffsetFields(MaintainableBase):
    """Identifies the difference between the date applied to the data as a whole and this specific item such as previous year's income or residence 5 years ago. A value of true for the attribute isNegativeOf"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ContentDateOffset")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    controlledVocabularyID: Optional[str] = None  # @attr
    controlledVocabularyName: Optional[str] = None  # @attr
    controlledVocabularyAgencyName: Optional[str] = None  # @attr
    controlledVocabularyVersionID: Optional[str] = None  # @attr
    otherValue: Optional[str] = None  # @attr
    controlledVocabularyURN: Optional[str] = None  # @attr
    controlledVocabularySchemeURN: Optional[str] = None  # @attr
    numberOfUnits: Optional[int] = None  # @attr
    isNegativeOffset: Optional[bool] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "controlledVocabularyID": ("controlledVocabularyID", "str"),
        "controlledVocabularyName": ("controlledVocabularyName", "str"),
        "controlledVocabularyAgencyName": ("controlledVocabularyAgencyName", "str"),
        "controlledVocabularyVersionID": ("controlledVocabularyVersionID", "str"),
        "otherValue": ("otherValue", "str"),
        "controlledVocabularyURN": ("controlledVocabularyURN", "str"),
        "controlledVocabularySchemeURN": ("controlledVocabularySchemeURN", "str"),
        "numberOfUnits": ("numberOfUnits", "int"),
        "isNegativeOffset": ("isNegativeOffset", "bool"),
    }


@dataclass
class ContentFields(MaintainableBase):
    """Supports the optional use of XHTML formatting tags within the string structure. XHTML tag content is controlled by the schema, see Part I of the DDI Technical Manual for a detailed list of available t"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Content")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    h1s: list[Element] = field(default_factory=list)  # [0..*]
    h2s: list[Element] = field(default_factory=list)  # [0..*]
    h3s: list[Element] = field(default_factory=list)  # [0..*]
    h4s: list[Element] = field(default_factory=list)  # [0..*]
    h5s: list[Element] = field(default_factory=list)  # [0..*]
    h6s: list[Element] = field(default_factory=list)  # [0..*]
    uls: list[Element] = field(default_factory=list)  # [0..*]
    ols: list[Element] = field(default_factory=list)  # [0..*]
    dls: list[Element] = field(default_factory=list)  # [0..*]
    ps: list[Element] = field(default_factory=list)  # [0..*]
    divs: list[Element] = field(default_factory=list)  # [0..*]
    pres: list[Element] = field(default_factory=list)  # [0..*]
    blockquotes: list[Element] = field(default_factory=list)  # [0..*]
    address: list[Element] = field(default_factory=list)  # [0..*]
    hrs: list[Element] = field(default_factory=list)  # [0..*]
    tables: list[Element] = field(default_factory=list)  # [0..*]
    lang: Optional[str] = None  # @attr
    isTranslated: Optional[bool] = None  # @attr
    isTranslatable: Optional[bool] = None  # @attr
    translationSourceLanguage: Optional[str] = None  # @attr
    translationDate: Optional[str] = None  # @attr
    isPlainText: Optional[bool] = None  # @attr
    textFormat: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "h1s": (qn("http://www.w3.org/1999/xhtml", "h1"), "element", True),
        "h2s": (qn("http://www.w3.org/1999/xhtml", "h2"), "element", True),
        "h3s": (qn("http://www.w3.org/1999/xhtml", "h3"), "element", True),
        "h4s": (qn("http://www.w3.org/1999/xhtml", "h4"), "element", True),
        "h5s": (qn("http://www.w3.org/1999/xhtml", "h5"), "element", True),
        "h6s": (qn("http://www.w3.org/1999/xhtml", "h6"), "element", True),
        "uls": (qn("http://www.w3.org/1999/xhtml", "ul"), "element", True),
        "ols": (qn("http://www.w3.org/1999/xhtml", "ol"), "element", True),
        "dls": (qn("http://www.w3.org/1999/xhtml", "dl"), "element", True),
        "ps": (qn("http://www.w3.org/1999/xhtml", "p"), "element", True),
        "divs": (qn("http://www.w3.org/1999/xhtml", "div"), "element", True),
        "pres": (qn("http://www.w3.org/1999/xhtml", "pre"), "element", True),
        "blockquotes": (qn("http://www.w3.org/1999/xhtml", "blockquote"), "element", True),
        "address": (qn("http://www.w3.org/1999/xhtml", "address"), "element", True),
        "hrs": (qn("http://www.w3.org/1999/xhtml", "hr"), "element", True),
        "tables": (qn("http://www.w3.org/1999/xhtml", "table"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "lang": ("lang", "str"),
        "isTranslated": ("isTranslated", "bool"),
        "isTranslatable": ("isTranslatable", "bool"),
        "translationSourceLanguage": ("translationSourceLanguage", "str"),
        "translationDate": ("translationDate", "str"),
        "isPlainText": ("isPlainText", "bool"),
        "textFormat": ("textFormat", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn("http://www.w3.org/1999/xhtml", "h1"),
        qn("http://www.w3.org/1999/xhtml", "h2"),
        qn("http://www.w3.org/1999/xhtml", "h3"),
        qn("http://www.w3.org/1999/xhtml", "h4"),
        qn("http://www.w3.org/1999/xhtml", "h5"),
        qn("http://www.w3.org/1999/xhtml", "h6"),
        qn("http://www.w3.org/1999/xhtml", "ul"),
        qn("http://www.w3.org/1999/xhtml", "ol"),
        qn("http://www.w3.org/1999/xhtml", "dl"),
        qn("http://www.w3.org/1999/xhtml", "p"),
        qn("http://www.w3.org/1999/xhtml", "div"),
        qn("http://www.w3.org/1999/xhtml", "pre"),
        qn("http://www.w3.org/1999/xhtml", "blockquote"),
        qn("http://www.w3.org/1999/xhtml", "address"),
        qn("http://www.w3.org/1999/xhtml", "hr"),
        qn("http://www.w3.org/1999/xhtml", "table"),
    ]
    _MIXED: ClassVar[bool] = True


@dataclass
class ContributorFields(MaintainableBase):
    """Holds the name of the contributor, their role, and optional reference to the contributor as described within a DDI Organization scheme. Repeat this element for multiple creators."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Contributor")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: Optional[InternationalString] = None  # [1..1]
    contributor_roles: list[CodeValue] = field(default_factory=list)  # [0..*]
    contributor_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "ContributorName"), "intl_string", False),
        "contributor_roles": (qn(REUSABLE_NS, "ContributorRole"), "code_value", True),
        "contributor_reference": (qn(REUSABLE_NS, "ContributorReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ContributorName"),
        qn(REUSABLE_NS, "ContributorRole"),
        qn(REUSABLE_NS, "ContributorReference"),
    ]


@dataclass
class CoordinatePairsFields(MaintainableBase):
    """Field to capture coordinate pairs as individual pairs or as an array of pairs."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "CoordinatePairs")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    maxLength: Optional[int] = None  # @attr
    minLength: Optional[int] = None  # @attr
    regExp: Optional[str] = None  # @attr
    maxArray: Optional[int] = None  # @attr
    arraySeparator: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "maxLength": ("maxLength", "int"),
        "minLength": ("minLength", "int"),
        "regExp": ("regExp", "str"),
        "maxArray": ("maxArray", "int"),
        "arraySeparator": ("arraySeparator", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class CountryCodeFields(MaintainableBase):
    """Use of a Controlled Vocabulary is strongly recommended. Use of ISO 3166 Country Codes (2 character, 3 character, or Numeric) is preferred with or without attribution to a specific controlled vocabular"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "CountryCode")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    controlledVocabularyID: Optional[str] = None  # @attr
    controlledVocabularyName: Optional[str] = None  # @attr
    controlledVocabularyAgencyName: Optional[str] = None  # @attr
    controlledVocabularyVersionID: Optional[str] = None  # @attr
    otherValue: Optional[str] = None  # @attr
    controlledVocabularyURN: Optional[str] = None  # @attr
    controlledVocabularySchemeURN: Optional[str] = None  # @attr
    effectiveDate: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "controlledVocabularyID": ("controlledVocabularyID", "str"),
        "controlledVocabularyName": ("controlledVocabularyName", "str"),
        "controlledVocabularyAgencyName": ("controlledVocabularyAgencyName", "str"),
        "controlledVocabularyVersionID": ("controlledVocabularyVersionID", "str"),
        "otherValue": ("otherValue", "str"),
        "controlledVocabularyURN": ("controlledVocabularyURN", "str"),
        "controlledVocabularySchemeURN": ("controlledVocabularySchemeURN", "str"),
        "effectiveDate": ("effectiveDate", "str"),
    }


@dataclass
class CoverageFields(MaintainableBase):
    """Describes the temporal, spatial and topical coverage. At the instance level these descriptions should be inclusive of the coverage of all modules in the instance. The element is available within indiv"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Coverage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    topical_coverage_reference: Optional[Reference] = None  # [1..1]
    topical_coverage: Optional[Element] = None  # [1..1]
    spatial_coverage_reference: Optional[Reference] = None  # [1..1]
    spatial_coverage: Optional[Element] = None  # [1..1]
    temporal_coverage_reference: Optional[Reference] = None  # [1..1]
    temporal_coverage: Optional[Element] = None  # [1..1]
    restriction_process: Optional[Element] = None  # [0..1]
    isRestrictionOfParentCoverage: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "topical_coverage_reference": (qn(REUSABLE_NS, "TopicalCoverageReference"), "reference", False),
        "topical_coverage": (qn(REUSABLE_NS, "TopicalCoverage"), "element", False),
        "spatial_coverage_reference": (qn(REUSABLE_NS, "SpatialCoverageReference"), "reference", False),
        "spatial_coverage": (qn(REUSABLE_NS, "SpatialCoverage"), "element", False),
        "temporal_coverage_reference": (qn(REUSABLE_NS, "TemporalCoverageReference"), "reference", False),
        "temporal_coverage": (qn(REUSABLE_NS, "TemporalCoverage"), "element", False),
        "restriction_process": (qn(REUSABLE_NS, "RestrictionProcess"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isRestrictionOfParentCoverage": ("isRestrictionOfParentCoverage", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "TopicalCoverageReference"),
        qn(REUSABLE_NS, "TopicalCoverage"),
        qn(REUSABLE_NS, "SpatialCoverageReference"),
        qn(REUSABLE_NS, "SpatialCoverage"),
        qn(REUSABLE_NS, "TemporalCoverageReference"),
        qn(REUSABLE_NS, "TemporalCoverage"),
        qn(REUSABLE_NS, "RestrictionProcess"),
    ]


@dataclass
class CreatorFields(MaintainableBase):
    """Holds the name of the creator and/or a reference to the creator as described within a DDI Organization scheme. Repeat this element for multiple creators."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Creator")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: Optional[InternationalString] = None  # [0..1]
    creator_reference: Optional[Reference] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "CreatorName"), "intl_string", False),
        "creator_reference": (qn(REUSABLE_NS, "CreatorReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "CreatorName"),
        qn(REUSABLE_NS, "CreatorReference"),
    ]


@dataclass
class DataExistenceFields(MaintainableBase):
    """Use when only the lowest, most discrete codes in the CodeList will be expressed as valid values. Identifies those levels of a CodeList with a regular hierarchy or those indicates discrete codes within"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "DataExistence")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    level_number: Optional[int] = None  # [1..1]
    discrete_category: Optional[bool] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "level_number": (qn(REUSABLE_NS, "LevelNumber"), "int", False),
        "discrete_category": (qn(REUSABLE_NS, "DiscreteCategory"), "bool", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "LevelNumber"),
        qn(REUSABLE_NS, "DiscreteCategory"),
    ]


@dataclass
class DateTimeRepresentationBaseFields(MaintainableBase):
    """Structures the representation for any type of time format (including dates, etc.). Regardless of the format of the data the content may be treated as a date and or time and converted to ISO standard s"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "DateTimeRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    date_field_format: Optional[CodeValue] = None  # [0..1]
    date_type_code: Optional[CodeValue] = None  # [1..1]
    ranges: list[Element] = field(default_factory=list)  # [0..*]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    regExp: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "date_field_format": (qn(REUSABLE_NS, "DateFieldFormat"), "code_value", False),
        "date_type_code": (qn(REUSABLE_NS, "DateTypeCode"), "code_value", False),
        "ranges": (qn(REUSABLE_NS, "Range"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "regExp": ("regExp", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "DateFieldFormat"),
        qn(REUSABLE_NS, "DateTypeCode"),
        qn(REUSABLE_NS, "Range"),
    ]


@dataclass
class DateFields(MaintainableBase):
    """Provides the structure of a Date element, which allows a choice between single, simple dates (of BaseDateType) or date ranges. If the Date element contains a range, Cycle may be used to indicate occur"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Date")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    simple_date: Optional[Element] = None  # [1..1]
    historical_date: Optional[Element] = None  # [0..1]
    start_date: Optional[Element] = None  # [1..1]
    historical_start_date: Optional[Element] = None  # [0..1]
    end_date: Optional[Element] = None  # [0..1]
    historical_end_date: Optional[Element] = None  # [0..1]
    cycle: Optional[int] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "simple_date": (qn(REUSABLE_NS, "SimpleDate"), "element", False),
        "historical_date": (qn(REUSABLE_NS, "HistoricalDate"), "element", False),
        "start_date": (qn(REUSABLE_NS, "StartDate"), "element", False),
        "historical_start_date": (qn(REUSABLE_NS, "HistoricalStartDate"), "element", False),
        "end_date": (qn(REUSABLE_NS, "EndDate"), "element", False),
        "historical_end_date": (qn(REUSABLE_NS, "HistoricalEndDate"), "element", False),
        "cycle": (qn(REUSABLE_NS, "Cycle"), "int", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "SimpleDate"),
        qn(REUSABLE_NS, "HistoricalDate"),
        qn(REUSABLE_NS, "StartDate"),
        qn(REUSABLE_NS, "HistoricalStartDate"),
        qn(REUSABLE_NS, "EndDate"),
        qn(REUSABLE_NS, "HistoricalEndDate"),
        qn(REUSABLE_NS, "Cycle"),
        qn(REUSABLE_NS, "EndDate"),
        qn(REUSABLE_NS, "HistoricalEndDate"),
    ]


@dataclass
class DefiningCharacteristicFields(MaintainableBase):
    """Use to attach one or more characteristics to the parent object. The defining characteristic supports the use of a controlled vocabulary and may provide a time period for which the classification is va"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "DefiningCharacteristic")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    characteristic: Optional[CodeValue] = None  # [1..1]
    geographic_time: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "characteristic": (qn(REUSABLE_NS, "Characteristic"), "code_value", False),
        "geographic_time": (qn(REUSABLE_NS, "GeographicTime"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Characteristic"),
        qn(REUSABLE_NS, "GeographicTime"),
    ]


@dataclass
class DelimiterFields(MaintainableBase):
    """Defines the delimiter used to separate variables in a delimited record. Valid values include, space, tab, comma, semicolon, colon, pipe, and other. If "other" is used the characters used for separatin"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Delimiter")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    otherValue: Optional[str] = None  # @attr
    treatConsecutiveDelimiterAsOne: Optional[bool] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "otherValue": ("otherValue", "str"),
        "treatConsecutiveDelimiterAsOne": ("treatConsecutiveDelimiterAsOne", "bool"),
    }


@dataclass
class DescribableFields(MaintainableBase):
    """A versionable object that has a Name, Label, and Description."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Describable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "Name"), "intl_string", True),
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
        qn(REUSABLE_NS, "Name"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class DimensionIntersectFields(MaintainableBase):
    """Identifies the point at which the scales of a multidimensional scale intersect. May include all or a subset of dimensions intersecting at a given point. Repeat for multiple intersect points."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "DimensionIntersect")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    included_dimensions: list[int] = field(default_factory=list)  # [0..*]
    forAllDimensions: Optional[bool] = None  # @attr
    intersectValue: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "included_dimensions": (qn(REUSABLE_NS, "IncludedDimension"), "int", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "forAllDimensions": ("forAllDimensions", "bool"),
        "intersectValue": ("intersectValue", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "IncludedDimension"),
    ]


@dataclass
class DimensionRankValueFields(MaintainableBase):
    """A dimension describes the rank or order of the dimension within the NCube structure and provides the specific coordinate value of the dimension for the data item. In the case where the value is found """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "DimensionRankValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    variable_reference: Optional[Reference] = None  # [1..1]
    value: Optional[Element] = None  # [1..1]
    rank: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "variable_reference": (qn(REUSABLE_NS, "VariableReference"), "reference", False),
        "value": (qn(REUSABLE_NS, "Value"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "rank": ("rank", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "VariableReference"),
        qn(REUSABLE_NS, "Value"),
    ]


@dataclass
class DistributionRepresentationBaseFields(MaintainableBase):
    """Means of describing Distributions as a representation so that they can be used as a response domain questions. Primarily used as a response domain in a QuestionGrid. In addition to the base of objects"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "DistributionRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    distribution_value: Optional[float] = None  # [1..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    decimalPositions: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "distribution_value": (qn(REUSABLE_NS, "DistributionValue"), "float", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "decimalPositions": ("decimalPositions", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "DistributionValue"),
    ]


@dataclass
class DoubleNumberRangeValueFields(MaintainableBase):
    """Describes a bounding value for a number range expressed as an xs:double."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "DoubleNumberRangeValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    isInclusive: Optional[bool] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isInclusive": ("isInclusive", "bool"),
    }


@dataclass
class EmailFields(MaintainableBase):
    """Email address type (Currently restricted to Internet format user@server.ext.)."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Email")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    internet_email: Optional[Element] = None  # [1..1]
    email_type_code: Optional[CodeValue] = None  # [0..1]
    effective_period: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "internet_email": (qn(REUSABLE_NS, "InternetEmail"), "element", False),
        "email_type_code": (qn(REUSABLE_NS, "EmailTypeCode"), "code_value", False),
        "effective_period": (qn(REUSABLE_NS, "EffectivePeriod"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "InternetEmail"),
        qn(REUSABLE_NS, "EmailTypeCode"),
        qn(REUSABLE_NS, "EffectivePeriod"),
    ]


@dataclass
class EmbargoFields(MaintainableBase):
    """Provides information about data that are not currently available because of policies established by the principal investigators and/or data producers. This item may be attached to specific levels of a"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Embargo")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    date: Optional[Element] = None  # [0..1]
    rationale: Optional[Element] = None  # [0..1]
    agency_organization_reference: Optional[Reference] = None  # [0..1]
    enforcement_agency_organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "EmbargoName"), "intl_string", True),
        "date": (qn(REUSABLE_NS, "Date"), "element", False),
        "rationale": (qn(REUSABLE_NS, "Rationale"), "element", False),
        "agency_organization_reference": (qn(REUSABLE_NS, "AgencyOrganizationReference"), "reference", False),
        "enforcement_agency_organization_references": (qn(REUSABLE_NS, "EnforcementAgencyOrganizationReference"), "reference", True),
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
        qn(REUSABLE_NS, "EmbargoName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Date"),
        qn(REUSABLE_NS, "Rationale"),
        qn(REUSABLE_NS, "AgencyOrganizationReference"),
        qn(REUSABLE_NS, "EnforcementAgencyOrganizationReference"),
    ]


@dataclass
class EmptyFields(MaintainableBase):
    """Element with no content. It is an abstract type, used to extend into subclasses."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Empty")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    pass


@dataclass
class EvaluatorFields(MaintainableBase):
    """Describes the type of evaluation, completion date, evaluation process and outcomes of the ExPost Evaluation. Allows identification of the Evaluator via reference to and organization or individual and """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Evaluator")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    evaluator_reference: Optional[Reference] = None  # [1..1]
    evaluator_roles: list[CodeValue] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "evaluator_reference": (qn(REUSABLE_NS, "EvaluatorReference"), "reference", False),
        "evaluator_roles": (qn(REUSABLE_NS, "EvaluatorRole"), "code_value", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "EvaluatorReference"),
        qn(REUSABLE_NS, "EvaluatorRole"),
    ]


@dataclass
class ExPostEvaluationFields(MaintainableBase):
    """Evaluation for the purpose of reviewing the study, data collection, data processing, or management processes. Results may feed into a revision process for future data collection or management. Identif"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ExPostEvaluation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_evaluations: list[CodeValue] = field(default_factory=list)  # [0..*]
    evaluators: list[Element] = field(default_factory=list)  # [0..*]
    evaluation_process: list[Element] = field(default_factory=list)  # [0..*]
    outcomes: list[Element] = field(default_factory=list)  # [0..*]
    completionDate: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_evaluations": (qn(REUSABLE_NS, "TypeOfEvaluation"), "code_value", True),
        "evaluators": (qn(REUSABLE_NS, "Evaluator"), "element", True),
        "evaluation_process": (qn(REUSABLE_NS, "EvaluationProcess"), "element", True),
        "outcomes": (qn(REUSABLE_NS, "Outcomes"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "completionDate": ("completionDate", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "TypeOfEvaluation"),
        qn(REUSABLE_NS, "Evaluator"),
        qn(REUSABLE_NS, "EvaluationProcess"),
        qn(REUSABLE_NS, "Outcomes"),
    ]


@dataclass
class ExternalCategoryRepresentationBaseFields(MaintainableBase):
    """Structures a response domain based on categorization that is described in an external non-DDI structure. Includes a UsageDescription that should provide information on how the external source is to be"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ExternalCategoryRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    external_category_reference: Optional[Reference] = None  # [1..1]
    usage_description: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "external_category_reference": (qn(REUSABLE_NS, "ExternalCategoryReference"), "reference", False),
        "usage_description": (qn(REUSABLE_NS, "UsageDescription"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "ExternalCategoryReference"),
        qn(REUSABLE_NS, "UsageDescription"),
    ]


@dataclass
class FundingInformationFields(MaintainableBase):
    """Provides information about the individual, agency and/or grant(s) which funded the described entity. Lists a reference to the agency or individual as described in a DDI Organization Scheme, the role o"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "FundingInformation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    agency_organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    funder_role: Optional[CodeValue] = None  # [0..1]
    grant_numbers: list[str] = field(default_factory=list)  # [0..*]
    funding_document: Optional[Element] = None  # [1..1]
    funding_document_reference: Optional[Reference] = None  # [1..1]
    funding_period: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "agency_organization_references": (qn(REUSABLE_NS, "AgencyOrganizationReference"), "reference", True),
        "funder_role": (qn(REUSABLE_NS, "FunderRole"), "code_value", False),
        "grant_numbers": (qn(REUSABLE_NS, "GrantNumber"), "str", True),
        "funding_document": (qn(REUSABLE_NS, "FundingDocument"), "element", False),
        "funding_document_reference": (qn(REUSABLE_NS, "FundingDocumentReference"), "reference", False),
        "funding_period": (qn(REUSABLE_NS, "FundingPeriod"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "AgencyOrganizationReference"),
        qn(REUSABLE_NS, "FunderRole"),
        qn(REUSABLE_NS, "GrantNumber"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "FundingDocument"),
        qn(REUSABLE_NS, "FundingDocumentReference"),
        qn(REUSABLE_NS, "FundingPeriod"),
    ]


@dataclass
class GeographicBoundaryFields(MaintainableBase):
    """A choice of a BoundingBox and/or a set of BoundingPolygons and ExcludingPolygons that describe an area for a specific time period."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicBoundary")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    area_coverages: list[Element] = field(default_factory=list)  # [0..*]
    bounding_box: Optional[Element] = None  # [0..1]
    bounding_polygons: list[Element] = field(default_factory=list)  # [0..*]
    excluding_polygons: list[Element] = field(default_factory=list)  # [0..*]
    geographic_time: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "area_coverages": (qn(REUSABLE_NS, "AreaCoverage"), "element", True),
        "bounding_box": (qn(REUSABLE_NS, "BoundingBox"), "element", False),
        "bounding_polygons": (qn(REUSABLE_NS, "BoundingPolygon"), "element", True),
        "excluding_polygons": (qn(REUSABLE_NS, "ExcludingPolygon"), "element", True),
        "geographic_time": (qn(REUSABLE_NS, "GeographicTime"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "AreaCoverage"),
        qn(REUSABLE_NS, "BoundingBox"),
        qn(REUSABLE_NS, "BoundingPolygon"),
        qn(REUSABLE_NS, "ExcludingPolygon"),
        qn(REUSABLE_NS, "GeographicTime"),
    ]


@dataclass
class GeographicCoverageFields(MaintainableBase):
    """Describes the geographic coverage of the data documented in a particular DDI module. If subordinate to another module, this description should be a sub-set of the parent module's geographic coverage. """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicCoverage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    bounding_box: Optional[Element] = None  # [0..1]
    country_codes: list[Element] = field(default_factory=list)  # [0..*]
    geography_structure_variable_reference: Optional[Reference] = None  # [0..1]
    spatial_object: Optional[Element] = None  # [0..1]
    geographic_structure_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_level_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_location_references: list[Reference] = field(default_factory=list)  # [0..*]
    location_value_references: list[Reference] = field(default_factory=list)  # [0..*]
    summary_data_references: list[Reference] = field(default_factory=list)  # [0..*]
    highest_level_reference: Optional[Reference] = None  # [0..1]
    lowest_level_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "bounding_box": (qn(REUSABLE_NS, "BoundingBox"), "element", False),
        "country_codes": (qn(REUSABLE_NS, "CountryCode"), "element", True),
        "geography_structure_variable_reference": (qn(REUSABLE_NS, "GeographyStructureVariableReference"), "reference", False),
        "spatial_object": (qn(REUSABLE_NS, "SpatialObject"), "element", False),
        "geographic_structure_references": (qn(REUSABLE_NS, "GeographicStructureReference"), "reference", True),
        "geographic_level_references": (qn(REUSABLE_NS, "GeographicLevelReference"), "reference", True),
        "geographic_location_references": (qn(REUSABLE_NS, "GeographicLocationReference"), "reference", True),
        "location_value_references": (qn(REUSABLE_NS, "LocationValueReference"), "reference", True),
        "summary_data_references": (qn(REUSABLE_NS, "SummaryDataReference"), "reference", True),
        "highest_level_reference": (qn(REUSABLE_NS, "HighestLevelReference"), "reference", False),
        "lowest_level_reference": (qn(REUSABLE_NS, "LowestLevelReference"), "reference", False),
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
        qn(REUSABLE_NS, "BoundingBox"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "CountryCode"),
        qn(REUSABLE_NS, "GeographyStructureVariableReference"),
        qn(REUSABLE_NS, "SpatialObject"),
        qn(REUSABLE_NS, "GeographicStructureReference"),
        qn(REUSABLE_NS, "GeographicLevelReference"),
        qn(REUSABLE_NS, "GeographicLocationReference"),
        qn(REUSABLE_NS, "LocationValueReference"),
        qn(REUSABLE_NS, "SummaryDataReference"),
        qn(REUSABLE_NS, "HighestLevelReference"),
        qn(REUSABLE_NS, "LowestLevelReference"),
    ]


@dataclass
class GeographicLevelFields(MaintainableBase):
    """Describes a level within the GeographicStructure. In addition to a name and description, provides one or more GeographicLevelCodes by which it is identified with specified system, any coverage limitat"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicLevel")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    geographic_level_codes: list[CodeValue] = field(default_factory=list)  # [0..*]
    coverage_limitation: Optional[Element] = None  # [0..1]
    primary_component_levels: list[Element] = field(default_factory=list)  # [0..*]
    parent_geographic_level_reference: Optional[Reference] = None  # [1..1]
    geographic_layer_base_references: list[Reference] = field(default_factory=list)  # [2..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "GeographicLevelName"), "intl_string", True),
        "geographic_level_codes": (qn(REUSABLE_NS, "GeographicLevelCode"), "code_value", True),
        "coverage_limitation": (qn(REUSABLE_NS, "CoverageLimitation"), "element", False),
        "primary_component_levels": (qn(REUSABLE_NS, "PrimaryComponentLevel"), "element", True),
        "parent_geographic_level_reference": (qn(REUSABLE_NS, "ParentGeographicLevelReference"), "reference", False),
        "geographic_layer_base_references": (qn(REUSABLE_NS, "GeographicLayerBaseReference"), "reference", True),
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
        qn(REUSABLE_NS, "GeographicLevelName"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "GeographicLevelCode"),
        qn(REUSABLE_NS, "CoverageLimitation"),
        qn(REUSABLE_NS, "PrimaryComponentLevel"),
        qn(REUSABLE_NS, "ParentGeographicLevelReference"),
        qn(REUSABLE_NS, "GeographicLayerBaseReference"),
    ]


@dataclass
class GeographicLocationCodeRepresentationBaseFields(MaintainableBase):
    """Allows for the use of all or part of a GeographicLocation description to be used as a response domain or value representation by a question or variable. In addition to the basic objects of a represent"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicLocationCodeRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    included_geographic_location_codes: Optional[Element] = None  # [0..1]
    limited_code_segment_captured: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "included_geographic_location_codes": (qn(REUSABLE_NS, "IncludedGeographicLocationCodes"), "element", False),
        "limited_code_segment_captured": (qn(REUSABLE_NS, "LimitedCodeSegmentCaptured"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "IncludedGeographicLocationCodes"),
        qn(REUSABLE_NS, "LimitedCodeSegmentCaptured"),
    ]


@dataclass
class GeographicLocationIdentifierFields(MaintainableBase):
    """Describes the GeographicLocation as represented by a specific GeographicCode provided by an Authorized Source."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicLocationIdentifier")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    geographic_code: Optional[str] = None  # [0..1]
    authorized_source_reference: Optional[Reference] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "geographic_code": (qn(REUSABLE_NS, "GeographicCode"), "str", False),
        "authorized_source_reference": (qn(REUSABLE_NS, "AuthorizedSourceReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "GeographicCode"),
        qn(REUSABLE_NS, "AuthorizedSourceReference"),
    ]


@dataclass
class GeographicLocationReferenceFields(MaintainableBase):
    """Reference to an existing GeographicLocation using the Reference structure plus the ability to exclude any number of contained location values as specified by reference. TypeOfObject should be set to G"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicLocationReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    excluded_location_value_references: list[Reference] = field(default_factory=list)  # [0..*]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "excluded_location_value_references": (qn(REUSABLE_NS, "ExcludedLocationValueReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isExternal": ("isExternal", "bool"),
        "isReference": ("isReference", "bool"),
        "lateBound": ("lateBound", "bool"),
        "lateBoundRestriction": ("lateBoundRestriction", "str"),
        "objectLanguage": ("objectLanguage", "str"),
        "sourceContext": ("sourceContext", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "ExcludedLocationValueReference"),
    ]


@dataclass
class GeographicLocationFields(MaintainableBase):
    """Describes specific instances of GeographicLocations associated with a specified GeographicLevel in a GeographicStructure. In addition to the standard name, level, and description, specifies the Geogra"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicLocation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    geographic_level_reference: Optional[Reference] = None  # [1..1]
    geographic_level_description: Optional[Element] = None  # [1..1]
    authorized_sources: list[Element] = field(default_factory=list)  # [0..*]
    location_values: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "GeographicLocationName"), "intl_string", True),
        "geographic_level_reference": (qn(REUSABLE_NS, "GeographicLevelReference"), "reference", False),
        "geographic_level_description": (qn(REUSABLE_NS, "GeographicLevelDescription"), "element", False),
        "authorized_sources": (qn(REUSABLE_NS, "AuthorizedSource"), "element", True),
        "location_values": (qn(REUSABLE_NS, "LocationValue"), "element", True),
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
        qn(REUSABLE_NS, "GeographicLocationName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "GeographicLevelReference"),
        qn(REUSABLE_NS, "GeographicLevelDescription"),
        qn(REUSABLE_NS, "AuthorizedSource"),
        qn(REUSABLE_NS, "LocationValue"),
    ]


@dataclass
class GeographicRepresentationBaseFields(MaintainableBase):
    """Structures the representation for a geographic point to ensure collection of relevant information using a single response domain structure. The point may be associated with a polygon (such as the cent"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    datum: Optional[CodeValue] = None  # [1..1]
    coordinate_system: Optional[CodeValue] = None  # [1..1]
    coordinate_zone: Optional[CodeValue] = None  # [0..1]
    coordinate_source: Optional[CodeValue] = None  # [1..1]
    error_correction: Optional[CodeValue] = None  # [1..1]
    offset: Optional[str] = None  # [1..1]
    georeferenced_object: Optional[CodeValue] = None  # [1..1]
    address_match_type: Optional[CodeValue] = None  # [0..1]
    coordinate_pairs: list[Element] = field(default_factory=list)  # [1..*]
    alternate_offset: Optional[Element] = None  # [0..1]
    alternate_object: Optional[Element] = None  # [0..1]
    alternate_coordinate_system: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    pointFormat: Optional[str] = None  # @attr
    spatialPrimitive: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "datum": (qn(REUSABLE_NS, "Datum"), "code_value", False),
        "coordinate_system": (qn(REUSABLE_NS, "CoordinateSystem"), "code_value", False),
        "coordinate_zone": (qn(REUSABLE_NS, "CoordinateZone"), "code_value", False),
        "coordinate_source": (qn(REUSABLE_NS, "CoordinateSource"), "code_value", False),
        "error_correction": (qn(REUSABLE_NS, "ErrorCorrection"), "code_value", False),
        "offset": (qn(REUSABLE_NS, "Offset"), "str", False),
        "georeferenced_object": (qn(REUSABLE_NS, "GeoreferencedObject"), "code_value", False),
        "address_match_type": (qn(REUSABLE_NS, "AddressMatchType"), "code_value", False),
        "coordinate_pairs": (qn(REUSABLE_NS, "CoordinatePairs"), "element", True),
        "alternate_offset": (qn(REUSABLE_NS, "AlternateOffset"), "element", False),
        "alternate_object": (qn(REUSABLE_NS, "AlternateObject"), "element", False),
        "alternate_coordinate_system": (qn(REUSABLE_NS, "AlternateCoordinateSystem"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "pointFormat": ("pointFormat", "str"),
        "spatialPrimitive": ("spatialPrimitive", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "Datum"),
        qn(REUSABLE_NS, "CoordinateSystem"),
        qn(REUSABLE_NS, "CoordinateZone"),
        qn(REUSABLE_NS, "CoordinateSource"),
        qn(REUSABLE_NS, "ErrorCorrection"),
        qn(REUSABLE_NS, "Offset"),
        qn(REUSABLE_NS, "GeoreferencedObject"),
        qn(REUSABLE_NS, "AddressMatchType"),
        qn(REUSABLE_NS, "CoordinatePairs"),
        qn(REUSABLE_NS, "AlternateOffset"),
        qn(REUSABLE_NS, "AlternateObject"),
        qn(REUSABLE_NS, "AlternateCoordinateSystem"),
    ]


@dataclass
class GeographicStructureCodeRepresentationBaseFields(MaintainableBase):
    """Allows for the use of all or part of a GeographicStructure description to be used as a response domain or value representation by a question or variable. In addition to the basic objects of a represen"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicStructureCodeRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    included_geographic_structure_codes: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "included_geographic_structure_codes": (qn(REUSABLE_NS, "IncludedGeographicStructureCodes"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "IncludedGeographicStructureCodes"),
    ]


@dataclass
class GeographicStructureReferenceFields(MaintainableBase):
    """Reference to an existing GeographicStructure using the Reference structure plus the ability to exclude any number of contained GeographicLevels as specified by reference. TypeOfObject should be set to"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicStructureReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    excluded_geographic_level_references: list[Reference] = field(default_factory=list)  # [0..*]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "excluded_geographic_level_references": (qn(REUSABLE_NS, "ExcludedGeographicLevelReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isExternal": ("isExternal", "bool"),
        "isReference": ("isReference", "bool"),
        "lateBound": ("lateBound", "bool"),
        "lateBoundRestriction": ("lateBoundRestriction", "str"),
        "objectLanguage": ("objectLanguage", "str"),
        "sourceContext": ("sourceContext", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "ExcludedGeographicLevelReference"),
    ]


@dataclass
class GeographicStructureFields(MaintainableBase):
    """Contains information on the hierarchy of the geographic structure. In addition to the standard name, label, and description identifies one or more AuthorizedSources for the level codes/descriptions pr"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "GeographicStructure")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    authorized_sources: list[Element] = field(default_factory=list)  # [0..*]
    geographic_levels: list[Element] = field(default_factory=list)  # [0..*]
    geographic_level_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "GeographicStructureName"), "intl_string", True),
        "authorized_sources": (qn(REUSABLE_NS, "AuthorizedSource"), "element", True),
        "geographic_levels": (qn(REUSABLE_NS, "GeographicLevel"), "element", True),
        "geographic_level_references": (qn(REUSABLE_NS, "GeographicLevelReference"), "reference", True),
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
        qn(REUSABLE_NS, "GeographicStructureName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "AuthorizedSource"),
        qn(REUSABLE_NS, "GeographicLevel"),
        qn(REUSABLE_NS, "GeographicLevelReference"),
    ]


@dataclass
class HistoricalDateFields(MaintainableBase):
    """Used to preserve an historical date, formatted in a non-ISO fashion."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "HistoricalDate")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    non_iso_date: Optional[str] = None  # [1..1]
    historical_date_format: Optional[CodeValue] = None  # [0..1]
    calendar: Optional[CodeValue] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "non_iso_date": (qn(REUSABLE_NS, "NonISODate"), "str", False),
        "historical_date_format": (qn(REUSABLE_NS, "HistoricalDateFormat"), "code_value", False),
        "calendar": (qn(REUSABLE_NS, "Calendar"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "NonISODate"),
        qn(REUSABLE_NS, "HistoricalDateFormat"),
        qn(REUSABLE_NS, "Calendar"),
    ]


@dataclass
class IDFields(MaintainableBase):
    """ID type. A fixed attribute is added to the string to ensure that only one ID can be provided."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ID")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "type": ("type", "str"),
    }


@dataclass
class IdentifiableFields(MaintainableBase):
    """XSD type: IdentifiableType"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Identifiable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
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
    ]


@dataclass
class IdentificationPortionFields(MaintainableBase):
    """Provides structural information for parsing the identification code structure of the Authorized Source into its separate parts."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "IdentificationPortion")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    geographic_level_references: list[Reference] = field(default_factory=list)  # [0..*]
    startPosition: Optional[int] = None  # @attr
    length: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "geographic_level_references": (qn(REUSABLE_NS, "GeographicLevelReference"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "startPosition": ("startPosition", "int"),
        "length": ("length", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "GeographicLevelReference"),
    ]


@dataclass
class IdentifierParsingInformationFields(MaintainableBase):
    """Provides structural information for parsing the identification code structure of the Authorized Source into its separate parts."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "IdentifierParsingInformation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    parent_identification_portions: list[Element] = field(default_factory=list)  # [0..*]
    unique_identification_portion: Optional[Element] = None  # [0..1]
    array_base: Optional[int] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "parent_identification_portions": (qn(REUSABLE_NS, "ParentIdentificationPortion"), "element", True),
        "unique_identification_portion": (qn(REUSABLE_NS, "UniqueIdentificationPortion"), "element", False),
        "array_base": (qn(REUSABLE_NS, "ArrayBase"), "int", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ParentIdentificationPortion"),
        qn(REUSABLE_NS, "UniqueIdentificationPortion"),
        qn(REUSABLE_NS, "ArrayBase"),
    ]


@dataclass
class ImageAreaFields(MaintainableBase):
    """Defines the shape and area of an image used as part of a location representation. The shape is defined as a Rectangle, Circle, or Polygon and Coordinates provides the information required to define it"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ImageArea")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    shape: Optional[Element] = None  # [1..1]
    coordinates: Optional[str] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "shape": (qn(REUSABLE_NS, "Shape"), "element", False),
        "coordinates": (qn(REUSABLE_NS, "Coordinates"), "str", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Shape"),
        qn(REUSABLE_NS, "Coordinates"),
    ]


@dataclass
class ImageFields(MaintainableBase):
    """A reference to an image, with a description of its properties and type."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Image")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    image_location: Optional[str] = None  # [1..1]
    type_of_image: Optional[CodeValue] = None  # [0..1]
    dpi: Optional[int] = None  # @attr
    languageOfImage: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "image_location": (qn(REUSABLE_NS, "ImageLocation"), "str", False),
        "type_of_image": (qn(REUSABLE_NS, "TypeOfImage"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "dpi": ("dpi", "int"),
        "languageOfImage": ("languageOfImage", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ImageLocation"),
        qn(REUSABLE_NS, "TypeOfImage"),
    ]


@dataclass
class InParameterFields(MaintainableBase):
    """A parameter that may accept content from outside its parent element. In addition to standard parameter content may provide the instructions for limiting the allowable array index."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "InParameter")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    parameter_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    alias: Optional[str] = None  # [0..1]
    value_representation: Optional[Element] = None  # [1..1]
    value_representation_reference: Optional[Reference] = None  # [1..1]
    default_value: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    isArray: Optional[bool] = None  # @attr
    limitArrayIndex: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "parameter_names": (qn(REUSABLE_NS, "ParameterName"), "intl_string", True),
        "alias": (qn(REUSABLE_NS, "Alias"), "str", False),
        "value_representation": (qn(REUSABLE_NS, "ValueRepresentation"), "element", False),
        "value_representation_reference": (qn(REUSABLE_NS, "ValueRepresentationReference"), "reference", False),
        "default_value": (qn(REUSABLE_NS, "DefaultValue"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "isArray": ("isArray", "bool"),
        "limitArrayIndex": ("limitArrayIndex", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "ParameterName"),
        qn(REUSABLE_NS, "Alias"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ValueRepresentation"),
        qn(REUSABLE_NS, "ValueRepresentationReference"),
        qn(REUSABLE_NS, "DefaultValue"),
    ]


@dataclass
class IncludedCodeFields(MaintainableBase):
    """Specifies the codes to include in the representation by providing the references to the included Codes or a range of Values from the Code."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "IncludedCode")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    code_references: list[Reference] = field(default_factory=list)  # [0..*]
    ranges: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "code_references": (qn(REUSABLE_NS, "CodeReference"), "reference", True),
        "ranges": (qn(REUSABLE_NS, "Range"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "CodeReference"),
        qn(REUSABLE_NS, "Range"),
    ]


@dataclass
class IncludedGeographicLocationCodesFields(MaintainableBase):
    """Specifies the Geographic Location Codes included in the representation by providing a reference to the authorized source of the code, the GeographicLocation used, and any excluded values."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "IncludedGeographicLocationCodes")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    authorized_source_reference: Optional[Reference] = None  # [0..1]
    geographic_location_reference: Optional[Reference] = None  # [0..1]
    excluded_location_value_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "authorized_source_reference": (qn(REUSABLE_NS, "AuthorizedSourceReference"), "reference", False),
        "geographic_location_reference": (qn(REUSABLE_NS, "GeographicLocationReference"), "reference", False),
        "excluded_location_value_references": (qn(REUSABLE_NS, "ExcludedLocationValueReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "AuthorizedSourceReference"),
        qn(REUSABLE_NS, "GeographicLocationReference"),
        qn(REUSABLE_NS, "ExcludedLocationValueReference"),
    ]


@dataclass
class IncludedGeographicStructureCodesFields(MaintainableBase):
    """Specifies the Geographic Structure Codes included in the representation by providing a reference to the authorized source of the code, the GeographicStructure used, and any excluded levels."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "IncludedGeographicStructureCodes")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    authorized_source_reference: Optional[Reference] = None  # [0..1]
    geographic_structure_reference: Optional[Reference] = None  # [0..1]
    excluded_geographic_level_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "authorized_source_reference": (qn(REUSABLE_NS, "AuthorizedSourceReference"), "reference", False),
        "geographic_structure_reference": (qn(REUSABLE_NS, "GeographicStructureReference"), "reference", False),
        "excluded_geographic_level_references": (qn(REUSABLE_NS, "ExcludedGeographicLevelReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "AuthorizedSourceReference"),
        qn(REUSABLE_NS, "GeographicStructureReference"),
        qn(REUSABLE_NS, "ExcludedGeographicLevelReference"),
    ]


@dataclass
class InformationClassificationFields(MaintainableBase):
    """Used to describe the rules and guidelines on how the data is allowed to be handled, transferred, stored and disposed. These confidentiality policies are often dictated by national laws and/or data own"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "InformationClassification")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    type_of_information_classification: Optional[CodeValue] = None  # [0..1]
    level_of_information_classification: Optional[CodeValue] = None  # [0..1]
    agency_organization_reference: Optional[Reference] = None  # [0..1]
    data_handling_personnel_rules: list[Element] = field(default_factory=list)  # [0..*]
    data_encryption_rules: list[Element] = field(default_factory=list)  # [0..*]
    data_storage_rules: list[Element] = field(default_factory=list)  # [0..*]
    disposal_rules: list[Element] = field(default_factory=list)  # [0..*]
    data_transfer_rules: list[Element] = field(default_factory=list)  # [0..*]
    authorized_policy_sources: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "Name"), "intl_string", True),
        "type_of_information_classification": (qn(REUSABLE_NS, "TypeOfInformationClassification"), "code_value", False),
        "level_of_information_classification": (qn(REUSABLE_NS, "LevelOfInformationClassification"), "code_value", False),
        "agency_organization_reference": (qn(REUSABLE_NS, "AgencyOrganizationReference"), "reference", False),
        "data_handling_personnel_rules": (qn(REUSABLE_NS, "DataHandlingPersonnelRules"), "element", True),
        "data_encryption_rules": (qn(REUSABLE_NS, "DataEncryptionRules"), "element", True),
        "data_storage_rules": (qn(REUSABLE_NS, "DataStorageRules"), "element", True),
        "disposal_rules": (qn(REUSABLE_NS, "DisposalRules"), "element", True),
        "data_transfer_rules": (qn(REUSABLE_NS, "DataTransferRules"), "element", True),
        "authorized_policy_sources": (qn(REUSABLE_NS, "AuthorizedPolicySource"), "element", True),
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
        qn(REUSABLE_NS, "Name"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "TypeOfInformationClassification"),
        qn(REUSABLE_NS, "LevelOfInformationClassification"),
        qn(REUSABLE_NS, "AgencyOrganizationReference"),
        qn(REUSABLE_NS, "DataHandlingPersonnelRules"),
        qn(REUSABLE_NS, "DataEncryptionRules"),
        qn(REUSABLE_NS, "DataStorageRules"),
        qn(REUSABLE_NS, "DisposalRules"),
        qn(REUSABLE_NS, "DataTransferRules"),
        qn(REUSABLE_NS, "AuthorizedPolicySource"),
    ]


@dataclass
class InternationalCodeValueFields(MaintainableBase):
    """Allows for string content which may be taken from an externally maintained controlled vocabulary. If the content is from a controlled vocabulary provide the code value, as well as a reference to the c"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "InternationalCodeValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    lang: Optional[str] = None  # @attr
    isTranslated: Optional[bool] = None  # @attr
    isTranslatable: Optional[bool] = None  # @attr
    translationSourceLanguage: Optional[str] = None  # @attr
    translationDate: Optional[str] = None  # @attr
    controlledVocabularyID: Optional[str] = None  # @attr
    controlledVocabularyName: Optional[str] = None  # @attr
    controlledVocabularyAgencyName: Optional[str] = None  # @attr
    controlledVocabularyVersionID: Optional[str] = None  # @attr
    otherValue: Optional[str] = None  # @attr
    controlledVocabularyURN: Optional[str] = None  # @attr
    controlledVocabularySchemeURN: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "lang": ("lang", "str"),
        "isTranslated": ("isTranslated", "bool"),
        "isTranslatable": ("isTranslatable", "bool"),
        "translationSourceLanguage": ("translationSourceLanguage", "str"),
        "translationDate": ("translationDate", "str"),
        "controlledVocabularyID": ("controlledVocabularyID", "str"),
        "controlledVocabularyName": ("controlledVocabularyName", "str"),
        "controlledVocabularyAgencyName": ("controlledVocabularyAgencyName", "str"),
        "controlledVocabularyVersionID": ("controlledVocabularyVersionID", "str"),
        "otherValue": ("otherValue", "str"),
        "controlledVocabularyURN": ("controlledVocabularyURN", "str"),
        "controlledVocabularySchemeURN": ("controlledVocabularySchemeURN", "str"),
    }


@dataclass
class InternationalIdentifierFields(MaintainableBase):
    """An identifier whose scope of uniqueness is broader than the local archive. Common forms of an international identifier are ISBN, ISSN, DOI or similar designator. Provides both the value of the identif"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "InternationalIdentifier")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    identifier_content: Optional[str] = None  # [1..1]
    managing_agency: Optional[CodeValue] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "identifier_content": (qn(REUSABLE_NS, "IdentifierContent"), "str", False),
        "managing_agency": (qn(REUSABLE_NS, "ManagingAgency"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "IdentifierContent"),
        qn(REUSABLE_NS, "ManagingAgency"),
    ]


@dataclass
class InternationalStringFields(MaintainableBase):
    """Packaging structure for multiple language versions of the same string content. Where an element of this type is repeatable, the expectation is that each repetition contains different content, each of """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "InternationalString")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    strings: list[Element] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "strings": (qn(REUSABLE_NS, "String"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "String"),
    ]


@dataclass
class KindOfDataFields(MaintainableBase):
    """Describes, with a string or a term from a controlled vocabulary, the kind of data documented in the logical product(s) of a study unit. Examples include survey data, census/enumeration data, administr"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "KindOfData")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    controlledVocabularyID: Optional[str] = None  # @attr
    controlledVocabularyName: Optional[str] = None  # @attr
    controlledVocabularyAgencyName: Optional[str] = None  # @attr
    controlledVocabularyVersionID: Optional[str] = None  # @attr
    otherValue: Optional[str] = None  # @attr
    controlledVocabularyURN: Optional[str] = None  # @attr
    controlledVocabularySchemeURN: Optional[str] = None  # @attr
    type: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "controlledVocabularyID": ("controlledVocabularyID", "str"),
        "controlledVocabularyName": ("controlledVocabularyName", "str"),
        "controlledVocabularyAgencyName": ("controlledVocabularyAgencyName", "str"),
        "controlledVocabularyVersionID": ("controlledVocabularyVersionID", "str"),
        "otherValue": ("otherValue", "str"),
        "controlledVocabularyURN": ("controlledVocabularyURN", "str"),
        "controlledVocabularySchemeURN": ("controlledVocabularySchemeURN", "str"),
        "type": ("type", "str"),
    }


@dataclass
class LabelFields(MaintainableBase):
    """A structured display label for the element. Label provides display content of a fully human readable display for the identification of the element. DDI does not impose any length limitations on Label."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Label")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    contents: list[Element] = field(default_factory=list)  # [1..*]
    type_of_label: Optional[CodeValue] = None  # [0..1]
    locationVariant: Optional[str] = None  # @attr
    validForStartDate: Optional[str] = None  # @attr
    validForEndDate: Optional[str] = None  # @attr
    maxLength: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "contents": (qn(REUSABLE_NS, "Content"), "element", True),
        "type_of_label": (qn(REUSABLE_NS, "TypeOfLabel"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "locationVariant": ("locationVariant", "str"),
        "validForStartDate": ("validForStartDate", "str"),
        "validForEndDate": ("validForEndDate", "str"),
        "maxLength": ("maxLength", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Content"),
        qn(REUSABLE_NS, "TypeOfLabel"),
    ]


@dataclass
class LevelReferenceFields(MaintainableBase):
    """Contains a Reference to a GeographicLevel if available and a name for the level. Only one reference can be provided but multiple name provided."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "LevelReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    geographic_level_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_level_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "geographic_level_references": (qn(REUSABLE_NS, "GeographicLevelReference"), "reference", True),
        "geographic_level_names": (qn(REUSABLE_NS, "GeographicLevelName"), "intl_string", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "GeographicLevelReference"),
        qn(REUSABLE_NS, "GeographicLevelName"),
    ]


@dataclass
class LifecycleEventFields(MaintainableBase):
    """Documents an event in the life cycle of a study or group of studies. A life cycle event can be any event which is judged to be significant enough to document by the agency maintaining the documentatio"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "LifecycleEvent")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    event_type: Optional[CodeValue] = None  # [0..1]
    date: Optional[Element] = None  # [0..1]
    agency_organization_references: list[Reference] = field(default_factory=list)  # [0..*]
    relationships: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "event_type": (qn(REUSABLE_NS, "EventType"), "code_value", False),
        "date": (qn(REUSABLE_NS, "Date"), "element", False),
        "agency_organization_references": (qn(REUSABLE_NS, "AgencyOrganizationReference"), "reference", True),
        "relationships": (qn(REUSABLE_NS, "Relationship"), "element", True),
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
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "EventType"),
        qn(REUSABLE_NS, "Date"),
        qn(REUSABLE_NS, "AgencyOrganizationReference"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Relationship"),
    ]


@dataclass
class LifecycleInformationFields(MaintainableBase):
    """Allows a listing of events in the life cycle of a data set or collection. Identification, date, agency, and descriptive information are provided for each event. Note that the agency that documents a l"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "LifecycleInformation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    lifecycle_events: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "lifecycle_events": (qn(REUSABLE_NS, "LifecycleEvent"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "LifecycleEvent"),
    ]


@dataclass
class LimitedCodeSegmentCapturedFields(MaintainableBase):
    """When the code is a concatenation this structure allows you to limit the portion of the concatenated code that this object captures. Provides an description of the segment, declares the array base used"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "LimitedCodeSegmentCaptured")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    array_base: Optional[int] = None  # [1..1]
    startPosition: Optional[int] = None  # @attr
    length: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "array_base": (qn(REUSABLE_NS, "ArrayBase"), "int", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "startPosition": ("startPosition", "int"),
        "length": ("length", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ArrayBase"),
    ]


@dataclass
class LineParameterFields(MaintainableBase):
    """Specification of the line and offset for the beginning and end of the segment."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "LineParameter")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    start_line: Optional[int] = None  # [1..1]
    start_offset: Optional[int] = None  # [1..1]
    end_line: Optional[int] = None  # [0..1]
    end_offset: Optional[int] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "start_line": (qn(REUSABLE_NS, "StartLine"), "int", False),
        "start_offset": (qn(REUSABLE_NS, "StartOffset"), "int", False),
        "end_line": (qn(REUSABLE_NS, "EndLine"), "int", False),
        "end_offset": (qn(REUSABLE_NS, "EndOffset"), "int", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "StartLine"),
        qn(REUSABLE_NS, "StartOffset"),
        qn(REUSABLE_NS, "EndLine"),
        qn(REUSABLE_NS, "EndOffset"),
    ]


@dataclass
class LocationRepresentationBaseFields(MaintainableBase):
    """Means of describing the Location of an action and the action itself within a repesentation so that they can be used by questions as a response domain. In addition to the basic objects of the represent"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "LocationRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    object: Optional[CodeValue] = None  # [0..1]
    actions: list[Element] = field(default_factory=list)  # [0..*]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "object": (qn(REUSABLE_NS, "Object"), "code_value", False),
        "actions": (qn(REUSABLE_NS, "Action"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "Object"),
        qn(REUSABLE_NS, "Action"),
    ]


@dataclass
class LocationValueBundleFields(MaintainableBase):
    """A stack of LocationValueReferences to each of the locations bundled together for a specific purpose Includes a GeographicTime to allow for repetition for change over time."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "LocationValueBundle")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    location_value_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_time: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "location_value_references": (qn(REUSABLE_NS, "LocationValueReference"), "reference", True),
        "geographic_time": (qn(REUSABLE_NS, "GeographicTime"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "LocationValueReference"),
        qn(REUSABLE_NS, "GeographicTime"),
    ]


@dataclass
class LocationValueFields(MaintainableBase):
    """A location of the specified geographic level providing information on its name, identification codes, temporal and spatial coverage as expressed by bounding and excluding polygon descriptions or refer"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "LocationValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    geographic_location_identifiers: list[Element] = field(default_factory=list)  # [0..*]
    defining_characteristics: list[Element] = field(default_factory=list)  # [0..*]
    component_parts: list[Element] = field(default_factory=list)  # [0..*]
    immediate_parent_locations: list[Element] = field(default_factory=list)  # [0..*]
    geographic_time: Optional[Element] = None  # [0..1]
    geographic_boundaries: list[Element] = field(default_factory=list)  # [0..*]
    supersedes_location_values: list[Element] = field(default_factory=list)  # [0..*]
    precedes_location_values: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "LocationValueName"), "intl_string", True),
        "geographic_location_identifiers": (qn(REUSABLE_NS, "GeographicLocationIdentifier"), "element", True),
        "defining_characteristics": (qn(REUSABLE_NS, "DefiningCharacteristic"), "element", True),
        "component_parts": (qn(REUSABLE_NS, "ComponentParts"), "element", True),
        "immediate_parent_locations": (qn(REUSABLE_NS, "ImmediateParentLocation"), "element", True),
        "geographic_time": (qn(REUSABLE_NS, "GeographicTime"), "element", False),
        "geographic_boundaries": (qn(REUSABLE_NS, "GeographicBoundary"), "element", True),
        "supersedes_location_values": (qn(REUSABLE_NS, "SupersedesLocationValue"), "element", True),
        "precedes_location_values": (qn(REUSABLE_NS, "PrecedesLocationValue"), "element", True),
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
        qn(REUSABLE_NS, "LocationValueName"),
        qn(REUSABLE_NS, "GeographicLocationIdentifier"),
        qn(REUSABLE_NS, "DefiningCharacteristic"),
        qn(REUSABLE_NS, "ComponentParts"),
        qn(REUSABLE_NS, "ImmediateParentLocation"),
        qn(REUSABLE_NS, "GeographicTime"),
        qn(REUSABLE_NS, "GeographicBoundary"),
        qn(REUSABLE_NS, "SupersedesLocationValue"),
        qn(REUSABLE_NS, "PrecedesLocationValue"),
    ]


@dataclass
class MaintainableObjectFields(MaintainableBase):
    """Provides information on the Maintainable Parent of the object. If the scope of the Identifiable or Versionable Object is the Maintinable, this information must be provided in order to provide all the """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "MaintainableObject")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    maintainable_id: Optional[Element] = None  # [1..1]
    maintainable_version: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "maintainable_id": (qn(REUSABLE_NS, "MaintainableID"), "element", False),
        "maintainable_version": (qn(REUSABLE_NS, "MaintainableVersion"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableID"),
        qn(REUSABLE_NS, "MaintainableVersion"),
    ]


@dataclass
class MaintainableFields(MaintainableBase):
    """Adds the attribute identifying this as a maintainable object. All content of Maintainable is considered to be administrative metadata. Note that changes to the administrative metadata does not drive a"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Maintainable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
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
    ]


@dataclass
class ManagedDateTimeRepresentationFields(MaintainableBase):
    """Means of describing DateTime so that they can be reused by multiple variables or questions/question constructs. Regardless of the format of the data the content may be treated as a date and or time an"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ManagedDateTimeRepresentation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    date_field_format: Optional[CodeValue] = None  # [0..1]
    date_type_code: Optional[CodeValue] = None  # [1..1]
    ranges: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    regExp: Optional[str] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "ManagedDateTimeRepresentationName"), "intl_string", True),
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "date_field_format": (qn(REUSABLE_NS, "DateFieldFormat"), "code_value", False),
        "date_type_code": (qn(REUSABLE_NS, "DateTypeCode"), "code_value", False),
        "ranges": (qn(REUSABLE_NS, "Range"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "regExp": ("regExp", "str"),
        "classificationLevel": ("classificationLevel", "str"),
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
        qn(REUSABLE_NS, "ManagedDateTimeRepresentationName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "DateFieldFormat"),
        qn(REUSABLE_NS, "DateTypeCode"),
        qn(REUSABLE_NS, "Range"),
    ]


@dataclass
class ManagedMissingValuesRepresentationFields(MaintainableBase):
    """Means of describing the Missing Values within a managed representation so that they can be reused by multiple variables and questions. Variable has a separate Missing Values location for this represen"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ManagedMissingValuesRepresentation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    missing_code_representations: list[Element] = field(default_factory=list)  # [0..*]
    missing_numeric_representations: list[Element] = field(default_factory=list)  # [0..*]
    missing_text_representations: list[Element] = field(default_factory=list)  # [0..*]
    processing_instruction_reference: Optional[Reference] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isBlankMissingValue: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "ManagedMissingValuesRepresentationName"), "intl_string", True),
        "missing_code_representations": (qn(REUSABLE_NS, "MissingCodeRepresentation"), "element", True),
        "missing_numeric_representations": (qn(REUSABLE_NS, "MissingNumericRepresentation"), "element", True),
        "missing_text_representations": (qn(REUSABLE_NS, "MissingTextRepresentation"), "element", True),
        "processing_instruction_reference": (qn(REUSABLE_NS, "ProcessingInstructionReference"), "reference", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "isBlankMissingValue": ("isBlankMissingValue", "bool"),
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
        qn(REUSABLE_NS, "ManagedMissingValuesRepresentationName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "MissingCodeRepresentation"),
        qn(REUSABLE_NS, "MissingNumericRepresentation"),
        qn(REUSABLE_NS, "MissingTextRepresentation"),
        qn(REUSABLE_NS, "ProcessingInstructionReference"),
    ]


@dataclass
class ManagedNumericRepresentationFields(MaintainableBase):
    """A means of capturing a managed representation of a numbers (item that are analyzed as numbers) which can be referenced by a variable or question and used as a value representation or response domain. """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ManagedNumericRepresentation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    number_ranges: list[Element] = field(default_factory=list)  # [0..*]
    numeric_type_code: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    format: Optional[str] = None  # @attr
    scale: Optional[int] = None  # @attr
    decimalPositions: Optional[int] = None  # @attr
    interval: Optional[int] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    accuracy: Optional[float] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "ManagedNumericRepresentationName"), "intl_string", True),
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "number_ranges": (qn(REUSABLE_NS, "NumberRange"), "element", True),
        "numeric_type_code": (qn(REUSABLE_NS, "NumericTypeCode"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "format": ("format", "str"),
        "scale": ("scale", "int"),
        "decimalPositions": ("decimalPositions", "int"),
        "interval": ("interval", "int"),
        "classificationLevel": ("classificationLevel", "str"),
        "accuracy": ("accuracy", "float"),
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
        qn(REUSABLE_NS, "ManagedNumericRepresentationName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "NumberRange"),
        qn(REUSABLE_NS, "NumericTypeCode"),
    ]


@dataclass
class ManagedRepresentationGroupFields(MaintainableBase):
    """Contains a group of managed representation and other managed objects used for representation, that are grouped for conceptual, administrative, or other purposes. Contents of the group may be ordered o"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ManagedRepresentationGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_managed_representation_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    managed_representation_references: list[Reference] = field(default_factory=list)  # [0..*]
    category_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    code_list_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_structure_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    geographic_location_references: list[Reference] = field(default_factory=list)  # [0..*]
    managed_representation_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_managed_representation_group": (qn(REUSABLE_NS, "TypeOfManagedRepresentationGroup"), "code_value", False),
        "names": (qn(REUSABLE_NS, "ManagedRepresentationGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "managed_representation_references": (qn(REUSABLE_NS, "ManagedRepresentationReference"), "reference", True),
        "category_scheme_references": (qn(REUSABLE_NS, "CategorySchemeReference"), "reference", True),
        "code_list_references": (qn(REUSABLE_NS, "CodeListReference"), "reference", True),
        "geographic_structure_scheme_references": (qn(REUSABLE_NS, "GeographicStructureSchemeReference"), "reference", True),
        "geographic_location_references": (qn(REUSABLE_NS, "GeographicLocationReference"), "reference", True),
        "managed_representation_group_references": (qn(REUSABLE_NS, "ManagedRepresentationGroupReference"), "reference", True),
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
        qn(REUSABLE_NS, "TypeOfManagedRepresentationGroup"),
        qn(REUSABLE_NS, "ManagedRepresentationGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "ManagedRepresentationReference"),
        qn(REUSABLE_NS, "CategorySchemeReference"),
        qn(REUSABLE_NS, "CodeListReference"),
        qn(REUSABLE_NS, "GeographicStructureSchemeReference"),
        qn(REUSABLE_NS, "GeographicLocationReference"),
        qn(REUSABLE_NS, "ManagedRepresentationGroupReference"),
    ]


@dataclass
class ManagedRepresentationSchemeFields(MaintainableBase):
    """This scheme contains sets of values described by ManagedRepresentation. These are used by reference to define Variable Representation and Question Response Domain. Text representations cover all non-c"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ManagedRepresentationScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    managed_representation_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    managed_representations: list[Element] = field(default_factory=list)  # [0..*]
    managed_representation_references: list[Reference] = field(default_factory=list)  # [0..*]
    managed_representation_groups: list[Element] = field(default_factory=list)  # [0..*]
    managed_representation_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "ManagedRepresentationSchemeName"), "intl_string", True),
        "managed_representation_scheme_references": (qn(REUSABLE_NS, "ManagedRepresentationSchemeReference"), "reference", True),
        "managed_representations": (qn(REUSABLE_NS, "ManagedRepresentation"), "element", True),
        "managed_representation_references": (qn(REUSABLE_NS, "ManagedRepresentationReference"), "reference", True),
        "managed_representation_groups": (qn(REUSABLE_NS, "ManagedRepresentationGroup"), "element", True),
        "managed_representation_group_references": (qn(REUSABLE_NS, "ManagedRepresentationGroupReference"), "reference", True),
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
        qn(REUSABLE_NS, "ManagedRepresentationSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ManagedRepresentationSchemeReference"),
        qn(REUSABLE_NS, "ManagedRepresentation"),
        qn(REUSABLE_NS, "ManagedRepresentationReference"),
        qn(REUSABLE_NS, "ManagedRepresentationGroup"),
        qn(REUSABLE_NS, "ManagedRepresentationGroupReference"),
    ]


@dataclass
class ManagedRepresentationFields(MaintainableBase):
    """Substitution group head for referencing Managed Representations."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ManagedRepresentation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
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
class ManagedScaleRepresentationFields(MaintainableBase):
    """A means of capturing a managed representation of a Scale for use by a Response Domain Reference or Value Representation Reference. In addition to the name, label, and description of the representation"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ManagedScaleRepresentation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    scale_dimensions: list[Element] = field(default_factory=list)  # [0..*]
    dimension_intersects: list[Element] = field(default_factory=list)  # [0..*]
    display_layout: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "ManagedScaleRepresentationName"), "intl_string", True),
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "scale_dimensions": (qn(REUSABLE_NS, "ScaleDimension"), "element", True),
        "dimension_intersects": (qn(REUSABLE_NS, "DimensionIntersect"), "element", True),
        "display_layout": (qn(REUSABLE_NS, "DisplayLayout"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
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
        qn(REUSABLE_NS, "ManagedScaleRepresentationName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "ScaleDimension"),
        qn(REUSABLE_NS, "DimensionIntersect"),
        qn(REUSABLE_NS, "DisplayLayout"),
    ]


@dataclass
class ManagedTextRepresentationFields(MaintainableBase):
    """Means of describing text based content used by reference to define Variable Representation and Question Response Domain. Text Representations cover all non-code and non-category representations/respon"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ManagedTextRepresentation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    maxLength: Optional[int] = None  # @attr
    minLength: Optional[int] = None  # @attr
    regExp: Optional[str] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "ManagedTextRepresentationName"), "intl_string", True),
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "versionDate": ("versionDate", "str"),
        "isPublished": ("isPublished", "bool"),
        "maxLength": ("maxLength", "int"),
        "minLength": ("minLength", "int"),
        "regExp": ("regExp", "str"),
        "classificationLevel": ("classificationLevel", "str"),
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
        qn(REUSABLE_NS, "ManagedTextRepresentationName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
    ]


@dataclass
class MeasureDefinitionReferenceFields(MaintainableBase):
    """Reference to the description of a MeasureDefinition in the NCube with a designation for its place in an array of measures if applicable. TypeOfObject should be set to MeasureDefinition."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "MeasureDefinitionReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    arrayOrder: Optional[int] = None  # @attr
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
        "arrayOrder": ("arrayOrder", "int"),
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
class MeasureDimensionFields(MaintainableBase):
    """This element defines the structure of a measure dimension for the NCube Instance. A value along the MeasureDimension is defined by a stack of references to one or more MeasureDefinitions found in the """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "MeasureDimension")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    n_cube_measure_definition_references: list[Reference] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "n_cube_measure_definition_references": (qn(REUSABLE_NS, "NCubeMeasureDefinitionReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "NCubeMeasureDefinitionReference"),
    ]


@dataclass
class MeasureDimensionValueFields(MaintainableBase):
    """Specifies the orderValue of the Measure in the MeasureDimension described in the NCubeInstance along with its arrayOrder if multiple measures are provided as an array in a single storage location."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "MeasureDimensionValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    dimensionValue: Optional[int] = None  # @attr
    arrayOrder: Optional[int] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "dimensionValue": ("dimensionValue", "int"),
        "arrayOrder": ("arrayOrder", "int"),
    }


@dataclass
class MetadataQualityFields(MaintainableBase):
    """An assessment of the quality of the metadata within the Maintainable object, e.g. the quality of the transcription, completeness, editing status, etc. It indicates the type of metadata quality being a"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "MetadataQuality")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_metadata_quality: Optional[CodeValue] = None  # [1..1]
    measure_purpose: Optional[Element] = None  # [0..1]
    measure_value: Optional[CodeValue] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_metadata_quality": (qn(REUSABLE_NS, "TypeOfMetadataQuality"), "code_value", False),
        "measure_purpose": (qn(REUSABLE_NS, "MeasurePurpose"), "element", False),
        "measure_value": (qn(REUSABLE_NS, "MeasureValue"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "TypeOfMetadataQuality"),
        qn(REUSABLE_NS, "MeasurePurpose"),
        qn(REUSABLE_NS, "MeasureValue"),
        qn(REUSABLE_NS, "Description"),
    ]


@dataclass
class NCubeMeasureDefinitionReferenceFields(MaintainableBase):
    """This is a reference to a MeasureDefinition as described in the parent NCube logical structure. The reference has an additional attribute orderValue which defines the position of the referenced Measure"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "NCubeMeasureDefinitionReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    orderValue: Optional[int] = None  # @attr
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
        "orderValue": ("orderValue", "int"),
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
class NameFields(MaintainableBase):
    """A reusable type assigned to an element with the naming convention XxxName e.g. OrganizationName at selected locations where the element may be assumed to be administered by a registry or is otherwise """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Name")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    strings: list[Element] = field(default_factory=list)  # [1..*]
    isPreferred: Optional[bool] = None  # @attr
    context: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "strings": (qn(REUSABLE_NS, "String"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isPreferred": ("isPreferred", "bool"),
        "context": ("context", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "String"),
    ]


@dataclass
class NominalRepresentationBaseFields(MaintainableBase):
    """A means of capturing the features of a nominal (marked/unmarked) response domain. Note that this is not the same as a code or category list with a yes/no set of responses. This representation is gener"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "NominalRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    regExp: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "regExp": ("regExp", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
    ]


@dataclass
class NoteFields(MaintainableBase):
    """A note related to one or more identifiable objects. Note is designed to be an inherent part of the DDI. (Unlike XML comments or other types of system-level annotations, which may be removed during pro"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Note")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_note: Optional[CodeValue] = None  # [0..1]
    note_subject: Optional[CodeValue] = None  # [0..1]
    relationships: list[Element] = field(default_factory=list)  # [1..*]
    responsibility: Optional[str] = None  # [0..1]
    header: Optional[Element] = None  # [0..1]
    note_content: Optional[Element] = None  # [0..1]
    proprietary_info: Optional[Element] = None  # [0..1]
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_note": (qn(REUSABLE_NS, "TypeOfNote"), "code_value", False),
        "note_subject": (qn(REUSABLE_NS, "NoteSubject"), "code_value", False),
        "relationships": (qn(REUSABLE_NS, "Relationship"), "element", True),
        "responsibility": (qn(REUSABLE_NS, "Responsibility"), "str", False),
        "header": (qn(REUSABLE_NS, "Header"), "element", False),
        "note_content": (qn(REUSABLE_NS, "NoteContent"), "element", False),
        "proprietary_info": (qn(REUSABLE_NS, "ProprietaryInfo"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "lang": ("lang", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "TypeOfNote"),
        qn(REUSABLE_NS, "NoteSubject"),
        qn(REUSABLE_NS, "Relationship"),
        qn(REUSABLE_NS, "Responsibility"),
        qn(REUSABLE_NS, "Header"),
        qn(REUSABLE_NS, "NoteContent"),
        qn(REUSABLE_NS, "ProprietaryInfo"),
    ]


@dataclass
class NumberRangeFields(MaintainableBase):
    """Structures a numeric range. Low and High values are designated. The structure identifies Low values that should be treated as bottom coded (Stated value and bellow, High values that should be treated """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "NumberRange")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    low: Optional[Element] = None  # [1..1]
    low_double: Optional[Element] = None  # [1..1]
    high: Optional[Element] = None  # [0..1]
    high_double: Optional[Element] = None  # [0..1]
    top_code: Optional[float] = None  # [1..1]
    top_code_double: Optional[float] = None  # [1..1]
    bottom_code: Optional[float] = None  # [1..1]
    bottom_code_double: Optional[float] = None  # [1..1]
    regExp: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "low": (qn(REUSABLE_NS, "Low"), "element", False),
        "low_double": (qn(REUSABLE_NS, "LowDouble"), "element", False),
        "high": (qn(REUSABLE_NS, "High"), "element", False),
        "high_double": (qn(REUSABLE_NS, "HighDouble"), "element", False),
        "top_code": (qn(REUSABLE_NS, "TopCode"), "float", False),
        "top_code_double": (qn(REUSABLE_NS, "TopCodeDouble"), "float", False),
        "bottom_code": (qn(REUSABLE_NS, "BottomCode"), "float", False),
        "bottom_code_double": (qn(REUSABLE_NS, "BottomCodeDouble"), "float", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "regExp": ("regExp", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Low"),
        qn(REUSABLE_NS, "LowDouble"),
        qn(REUSABLE_NS, "High"),
        qn(REUSABLE_NS, "HighDouble"),
        qn(REUSABLE_NS, "TopCode"),
        qn(REUSABLE_NS, "TopCodeDouble"),
        qn(REUSABLE_NS, "BottomCode"),
        qn(REUSABLE_NS, "BottomCodeDouble"),
    ]


@dataclass
class NumberRangeValueFields(MaintainableBase):
    """Describes a bounding value for a number range expressed as an xs:demical."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "NumberRangeValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    isInclusive: Optional[bool] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isInclusive": ("isInclusive", "bool"),
    }


@dataclass
class NumericRepresentationBaseFields(MaintainableBase):
    """Defines the representation for a numeric response. May be a range or specific value, or a list of ranges."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "NumericRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    number_ranges: list[Element] = field(default_factory=list)  # [0..*]
    numeric_type_code: Optional[CodeValue] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    format: Optional[str] = None  # @attr
    scale: Optional[int] = None  # @attr
    decimalPositions: Optional[int] = None  # @attr
    interval: Optional[int] = None  # @attr
    accuracy: Optional[float] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "number_ranges": (qn(REUSABLE_NS, "NumberRange"), "element", True),
        "numeric_type_code": (qn(REUSABLE_NS, "NumericTypeCode"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "format": ("format", "str"),
        "scale": ("scale", "int"),
        "decimalPositions": ("decimalPositions", "int"),
        "interval": ("interval", "int"),
        "accuracy": ("accuracy", "float"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "NumberRange"),
        qn(REUSABLE_NS, "NumericTypeCode"),
    ]


@dataclass
class OtherMaterialGroupFields(MaintainableBase):
    """Contains a group of OtherMaterials, which may describe an ordered or hierarchical relationship structure. Specifies the purpose of the group, a name, label, and description of the group, its relations"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "OtherMaterialGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_other_material_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    other_material_references: list[Reference] = field(default_factory=list)  # [0..*]
    other_material_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_other_material_group": (qn(REUSABLE_NS, "TypeOfOtherMaterialGroup"), "code_value", False),
        "names": (qn(REUSABLE_NS, "OtherMaterialGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "other_material_references": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", True),
        "other_material_group_references": (qn(REUSABLE_NS, "OtherMaterialGroupReference"), "reference", True),
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
        qn(REUSABLE_NS, "TypeOfOtherMaterialGroup"),
        qn(REUSABLE_NS, "OtherMaterialGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
        qn(REUSABLE_NS, "OtherMaterialGroupReference"),
    ]


@dataclass
class OtherMaterialSchemeFields(MaintainableBase):
    """This scheme contains a set of other materials referenced by the metadata. In addition to the name, label, and description of the scheme, the structure supports the inclusion of another OtherMaterialSc"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "OtherMaterialScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    other_material_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    other_materials: list[Element] = field(default_factory=list)  # [0..*]
    other_material_references: list[Reference] = field(default_factory=list)  # [0..*]
    other_material_groups: list[Element] = field(default_factory=list)  # [0..*]
    other_material_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "OtherMaterialSchemeName"), "intl_string", True),
        "other_material_scheme_references": (qn(REUSABLE_NS, "OtherMaterialSchemeReference"), "reference", True),
        "other_materials": (qn(REUSABLE_NS, "OtherMaterial"), "element", True),
        "other_material_references": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", True),
        "other_material_groups": (qn(REUSABLE_NS, "OtherMaterialGroup"), "element", True),
        "other_material_group_references": (qn(REUSABLE_NS, "OtherMaterialGroupReference"), "reference", True),
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
        qn(REUSABLE_NS, "OtherMaterialSchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OtherMaterialSchemeReference"),
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
        qn(REUSABLE_NS, "OtherMaterialGroup"),
        qn(REUSABLE_NS, "OtherMaterialGroupReference"),
    ]


@dataclass
class OtherMaterialFields(MaintainableBase):
    """OtherMaterialType describes the structure of the OtherMaterial element, used to reference external resources. It includes citations to materials related to the content of the DDI Instance. This includ"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "OtherMaterial")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_material: Optional[CodeValue] = None  # [0..1]
    citation: Optional[Element] = None  # [0..1]
    external_url_references: list[Reference] = field(default_factory=list)  # [0..*]
    external_urn_reference: Optional[Reference] = None  # [0..1]
    relationships: list[Element] = field(default_factory=list)  # [0..*]
    mime_type: Optional[CodeValue] = None  # [0..1]
    segments: list[Element] = field(default_factory=list)  # [0..*]
    size_in_bytes: Optional[int] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_material": (qn(REUSABLE_NS, "TypeOfMaterial"), "code_value", False),
        "citation": (qn(REUSABLE_NS, "Citation"), "element", False),
        "external_url_references": (qn(REUSABLE_NS, "ExternalURLReference"), "reference", True),
        "external_urn_reference": (qn(REUSABLE_NS, "ExternalURNReference"), "reference", False),
        "relationships": (qn(REUSABLE_NS, "Relationship"), "element", True),
        "mime_type": (qn(REUSABLE_NS, "MIMEType"), "code_value", False),
        "segments": (qn(REUSABLE_NS, "Segment"), "element", True),
        "size_in_bytes": (qn(REUSABLE_NS, "SizeInBytes"), "int", False),
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
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "TypeOfMaterial"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Citation"),
        qn(REUSABLE_NS, "ExternalURLReference"),
        qn(REUSABLE_NS, "ExternalURNReference"),
        qn(REUSABLE_NS, "Relationship"),
        qn(REUSABLE_NS, "MIMEType"),
        qn(REUSABLE_NS, "Segment"),
        qn(REUSABLE_NS, "SizeInBytes"),
    ]


@dataclass
class ParameterFields(MaintainableBase):
    """A parameter is a structure that specifically identifies a source of input or output information so that it can be use pragmatically."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Parameter")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    alias: Optional[str] = None  # [0..1]
    value_representation: Optional[Element] = None  # [1..1]
    value_representation_reference: Optional[Reference] = None  # [1..1]
    default_value: Optional[Element] = None  # [0..1]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    isArray: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "ParameterName"), "intl_string", True),
        "alias": (qn(REUSABLE_NS, "Alias"), "str", False),
        "value_representation": (qn(REUSABLE_NS, "ValueRepresentation"), "element", False),
        "value_representation_reference": (qn(REUSABLE_NS, "ValueRepresentationReference"), "reference", False),
        "default_value": (qn(REUSABLE_NS, "DefaultValue"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "inheritanceAction": ("inheritanceAction", "str"),
        "objectSource": ("objectSource", "str"),
        "scopeOfUniqueness": ("scopeOfUniqueness", "str"),
        "isArray": ("isArray", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "UserID"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "ParameterName"),
        qn(REUSABLE_NS, "Alias"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "ValueRepresentation"),
        qn(REUSABLE_NS, "ValueRepresentationReference"),
        qn(REUSABLE_NS, "DefaultValue"),
    ]


@dataclass
class ParentGeographicLevelReferenceFields(MaintainableBase):
    """References a parent geography and describes whether the geographic level completely fills its parent level. TypeOfObject should be set to GeographicLevel."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ParentGeographicLevelReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    isExhaustiveCoverage: Optional[bool] = None  # @attr
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
        "isExhaustiveCoverage": ("isExhaustiveCoverage", "bool"),
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
class PointFields(MaintainableBase):
    """A geographic point consisting of an X and Y coordinate. Each coordinate value is expressed separately providing its value and format."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Point")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    x_coordinate: Optional[Element] = None  # [1..1]
    y_coordinate: Optional[Element] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "x_coordinate": (qn(REUSABLE_NS, "XCoordinate"), "element", False),
        "y_coordinate": (qn(REUSABLE_NS, "YCoordinate"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "XCoordinate"),
        qn(REUSABLE_NS, "YCoordinate"),
    ]


@dataclass
class PolygonFields(MaintainableBase):
    """A closed plane figure bounded by three or more line segments, representing a geographic area. Contains either the URI of the file containing the polygon, a specific link code for the shape within the """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Polygon")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    external_uri: Optional[str] = None  # [1..1]
    polygon_link_code: Optional[str] = None  # [0..1]
    shape_file_format: Optional[CodeValue] = None  # [0..1]
    points: list[Element] = field(default_factory=list)  # [4..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "external_uri": (qn(REUSABLE_NS, "ExternalURI"), "str", False),
        "polygon_link_code": (qn(REUSABLE_NS, "PolygonLinkCode"), "str", False),
        "shape_file_format": (qn(REUSABLE_NS, "ShapeFileFormat"), "code_value", False),
        "points": (qn(REUSABLE_NS, "Point"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ExternalURI"),
        qn(REUSABLE_NS, "PolygonLinkCode"),
        qn(REUSABLE_NS, "ShapeFileFormat"),
        qn(REUSABLE_NS, "Point"),
    ]


@dataclass
class PrimaryComponentLevelFields(MaintainableBase):
    """Provides references to the base level elements that are used as building blocks for composed geographies. For example, Metropolitan areas that are composed of counties except in the New England States"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "PrimaryComponentLevel")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    geographic_level_reference: Optional[Reference] = None  # [0..1]
    coverage_limitation: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "geographic_level_reference": (qn(REUSABLE_NS, "GeographicLevelReference"), "reference", False),
        "coverage_limitation": (qn(REUSABLE_NS, "CoverageLimitation"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "GeographicLevelReference"),
        qn(REUSABLE_NS, "CoverageLimitation"),
    ]


@dataclass
class ProprietaryInfoFields(MaintainableBase):
    """Contains information proprietary to the software package which produced the data file. This is expressed as a set of key(name)-value pairs."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ProprietaryInfo")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    proprietary_properties: list[Element] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "proprietary_properties": (qn(REUSABLE_NS, "ProprietaryProperty"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ProprietaryProperty"),
    ]


@dataclass
class PublicationFields(MaintainableBase):
    """Description and link to the Publication using the DDI Other Material structure."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Publication")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    other_material: Optional[Element] = None  # [1..1]
    other_material_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "other_material": (qn(REUSABLE_NS, "OtherMaterial"), "element", False),
        "other_material_reference": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
    ]


@dataclass
class PublisherFields(MaintainableBase):
    """Holds the name of the publisher with their role and/or a reference to the publisher as described within a DDI Organization scheme. Repeat this element for multiple publishers."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Publisher")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: Optional[InternationalString] = None  # [0..1]
    publisher_roles: list[CodeValue] = field(default_factory=list)  # [0..*]
    publisher_reference: Optional[Reference] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "PublisherName"), "intl_string", False),
        "publisher_roles": (qn(REUSABLE_NS, "PublisherRole"), "code_value", True),
        "publisher_reference": (qn(REUSABLE_NS, "PublisherReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "PublisherName"),
        qn(REUSABLE_NS, "PublisherRole"),
        qn(REUSABLE_NS, "PublisherReference"),
    ]


@dataclass
class QualitySchemeFields(MaintainableBase):
    """This scheme contains a set of quality statements and quality standards referenced by the metadata at different points in the lifecycle. In addition to the name, label, and description of the scheme, t"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "QualityScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    quality_scheme_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_statements: list[Element] = field(default_factory=list)  # [0..*]
    quality_statement_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_standards: list[Element] = field(default_factory=list)  # [0..*]
    quality_standard_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_statement_groups: list[Element] = field(default_factory=list)  # [0..*]
    quality_statement_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_standard_groups: list[Element] = field(default_factory=list)  # [0..*]
    quality_standard_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "QualitySchemeName"), "intl_string", True),
        "quality_scheme_references": (qn(REUSABLE_NS, "QualitySchemeReference"), "reference", True),
        "quality_statements": (qn(REUSABLE_NS, "QualityStatement"), "element", True),
        "quality_statement_references": (qn(REUSABLE_NS, "QualityStatementReference"), "reference", True),
        "quality_standards": (qn(REUSABLE_NS, "QualityStandard"), "element", True),
        "quality_standard_references": (qn(REUSABLE_NS, "QualityStandardReference"), "reference", True),
        "quality_statement_groups": (qn(REUSABLE_NS, "QualityStatementGroup"), "element", True),
        "quality_statement_group_references": (qn(REUSABLE_NS, "QualityStatementGroupReference"), "reference", True),
        "quality_standard_groups": (qn(REUSABLE_NS, "QualityStandardGroup"), "element", True),
        "quality_standard_group_references": (qn(REUSABLE_NS, "QualityStandardGroupReference"), "reference", True),
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
        qn(REUSABLE_NS, "QualitySchemeName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "QualitySchemeReference"),
        qn(REUSABLE_NS, "QualityStatement"),
        qn(REUSABLE_NS, "QualityStatementReference"),
        qn(REUSABLE_NS, "QualityStandard"),
        qn(REUSABLE_NS, "QualityStandardReference"),
        qn(REUSABLE_NS, "QualityStatementGroup"),
        qn(REUSABLE_NS, "QualityStatementGroupReference"),
        qn(REUSABLE_NS, "QualityStandardGroup"),
        qn(REUSABLE_NS, "QualityStandardGroupReference"),
    ]


@dataclass
class QualityStandardGroupFields(MaintainableBase):
    """Contains a group of QualityStatements, which may describe an ordered or hierarchical relationship structure. Specifies the purpose of the group, a name, label, and description of the group, its relati"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "QualityStandardGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_quality_standard_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    quality_standard_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_standard_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_quality_standard_group": (qn(REUSABLE_NS, "TypeOfQualityStandardGroup"), "code_value", False),
        "names": (qn(REUSABLE_NS, "QualityStandardGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "quality_standard_references": (qn(REUSABLE_NS, "QualityStandardReference"), "reference", True),
        "quality_standard_group_references": (qn(REUSABLE_NS, "QualityStandardGroupReference"), "reference", True),
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
        qn(REUSABLE_NS, "TypeOfQualityStandardGroup"),
        qn(REUSABLE_NS, "QualityStandardGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "QualityStandardReference"),
        qn(REUSABLE_NS, "QualityStandardGroupReference"),
    ]


@dataclass
class QualityStandardFields(MaintainableBase):
    """A formal description of a quality standard, and the quality concepts which it requires."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "QualityStandard")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    standard_used: Optional[Element] = None  # [0..1]
    compliance_definitions: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "QualityStandardName"), "intl_string", True),
        "standard_used": (qn(REUSABLE_NS, "StandardUsed"), "element", False),
        "compliance_definitions": (qn(REUSABLE_NS, "ComplianceDefinition"), "element", True),
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
        qn(REUSABLE_NS, "QualityStandardName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "StandardUsed"),
        qn(REUSABLE_NS, "ComplianceDefinition"),
    ]


@dataclass
class QualityStatementGroupFields(MaintainableBase):
    """Contains a group of QualityStatements, which may describe an ordered or hierarchical relationship structure. Specifies the purpose of the group, a name, label, and description of the group, its relati"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "QualityStatementGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_quality_statement_group: Optional[CodeValue] = None  # [0..1]
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    universe_references: list[Reference] = field(default_factory=list)  # [0..*]
    concept_reference: Optional[Reference] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    quality_statement_references: list[Reference] = field(default_factory=list)  # [0..*]
    quality_statement_group_references: list[Reference] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    isOrdered: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_quality_statement_group": (qn(REUSABLE_NS, "TypeOfQualityStatementGroup"), "code_value", False),
        "names": (qn(REUSABLE_NS, "QualityStatementGroupName"), "intl_string", True),
        "universe_references": (qn(REUSABLE_NS, "UniverseReference"), "reference", True),
        "concept_reference": (qn(REUSABLE_NS, "ConceptReference"), "reference", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
        "quality_statement_references": (qn(REUSABLE_NS, "QualityStatementReference"), "reference", True),
        "quality_statement_group_references": (qn(REUSABLE_NS, "QualityStatementGroupReference"), "reference", True),
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
        qn(REUSABLE_NS, "TypeOfQualityStatementGroup"),
        qn(REUSABLE_NS, "QualityStatementGroupName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "UniverseReference"),
        qn(REUSABLE_NS, "ConceptReference"),
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
        qn(REUSABLE_NS, "QualityStatementReference"),
        qn(REUSABLE_NS, "QualityStatementGroupReference"),
    ]


@dataclass
class QualityStatementFields(MaintainableBase):
    """A statement of quality which may be related to an external standard or contain a simple statement of internal quality goals or expectations. When relating to an external standard information on compli"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "QualityStatement")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    quality_standard: Optional[Element] = None  # [1..1]
    quality_standard_reference: Optional[Reference] = None  # [1..1]
    other_statement_of_quality: Optional[Element] = None  # [1..1]
    compliance_statement: Optional[Element] = None  # [0..1]
    compliances: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "QualityStatementName"), "intl_string", True),
        "quality_standard": (qn(REUSABLE_NS, "QualityStandard"), "element", False),
        "quality_standard_reference": (qn(REUSABLE_NS, "QualityStandardReference"), "reference", False),
        "other_statement_of_quality": (qn(REUSABLE_NS, "OtherStatementOfQuality"), "element", False),
        "compliance_statement": (qn(REUSABLE_NS, "ComplianceStatement"), "element", False),
        "compliances": (qn(REUSABLE_NS, "Compliance"), "element", True),
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
        qn(REUSABLE_NS, "QualityStatementName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "QualityStandard"),
        qn(REUSABLE_NS, "QualityStandardReference"),
        qn(REUSABLE_NS, "OtherStatementOfQuality"),
        qn(REUSABLE_NS, "ComplianceStatement"),
        qn(REUSABLE_NS, "Compliance"),
    ]


@dataclass
class RangeFields(MaintainableBase):
    """Indicates the range of items expressed as a string, such as an alphabetic range."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Range")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    collation_algorithm: Optional[CodeValue] = None  # [0..1]
    range_unit: Optional[str] = None  # [0..1]
    minimum_value: Optional[Element] = None  # [0..1]
    maximum_value: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "collation_algorithm": (qn(REUSABLE_NS, "CollationAlgorithm"), "code_value", False),
        "range_unit": (qn(REUSABLE_NS, "RangeUnit"), "str", False),
        "minimum_value": (qn(REUSABLE_NS, "MinimumValue"), "element", False),
        "maximum_value": (qn(REUSABLE_NS, "MaximumValue"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "CollationAlgorithm"),
        qn(REUSABLE_NS, "RangeUnit"),
        qn(REUSABLE_NS, "MinimumValue"),
        qn(REUSABLE_NS, "MaximumValue"),
    ]


@dataclass
class RangeValueFields(MaintainableBase):
    """Describes a bounding value of a string."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "RangeValue")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    space: Optional[str] = None  # @attr
    included: Optional[bool] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "space": ("space", "str"),
        "included": ("included", "bool"),
    }


@dataclass
class RankingRangeFields(MaintainableBase):
    """Describes the range of values used in the ranking system using Range and sets the number of times a single value can be repeated."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "RankingRange")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    collation_algorithm: Optional[CodeValue] = None  # [0..1]
    range_unit: Optional[str] = None  # [0..1]
    minimum_value: Optional[Element] = None  # [0..1]
    maximum_value: Optional[Element] = None  # [0..1]
    maximumRepetitionOfSingleValue: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "collation_algorithm": (qn(REUSABLE_NS, "CollationAlgorithm"), "code_value", False),
        "range_unit": (qn(REUSABLE_NS, "RangeUnit"), "str", False),
        "minimum_value": (qn(REUSABLE_NS, "MinimumValue"), "element", False),
        "maximum_value": (qn(REUSABLE_NS, "MaximumValue"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "maximumRepetitionOfSingleValue": ("maximumRepetitionOfSingleValue", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "CollationAlgorithm"),
        qn(REUSABLE_NS, "RangeUnit"),
        qn(REUSABLE_NS, "MinimumValue"),
        qn(REUSABLE_NS, "MaximumValue"),
    ]


@dataclass
class RankingRepresentationBaseFields(MaintainableBase):
    """A means of capturing the representation of Ranking to be used as a response domain used by a question. In addition to the basic objects of the representation, the structure defines the range used for """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "RankingRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    ranking_range: Optional[Element] = None  # [1..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "ranking_range": (qn(REUSABLE_NS, "RankingRange"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "RankingRange"),
    ]


@dataclass
class ReferenceDateFields(MaintainableBase):
    """The date that the data reference such as at the point of collection, a previous year or date, etc. This is expressed as a date (singular or range) and may have specific subjects associated with it. Fo"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ReferenceDate")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    simple_date: Optional[Element] = None  # [1..1]
    historical_date: Optional[Element] = None  # [0..1]
    start_date: Optional[Element] = None  # [1..1]
    historical_start_date: Optional[Element] = None  # [0..1]
    end_date: Optional[Element] = None  # [0..1]
    historical_end_date: Optional[Element] = None  # [0..1]
    cycle: Optional[int] = None  # [0..1]
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "simple_date": (qn(REUSABLE_NS, "SimpleDate"), "element", False),
        "historical_date": (qn(REUSABLE_NS, "HistoricalDate"), "element", False),
        "start_date": (qn(REUSABLE_NS, "StartDate"), "element", False),
        "historical_start_date": (qn(REUSABLE_NS, "HistoricalStartDate"), "element", False),
        "end_date": (qn(REUSABLE_NS, "EndDate"), "element", False),
        "historical_end_date": (qn(REUSABLE_NS, "HistoricalEndDate"), "element", False),
        "cycle": (qn(REUSABLE_NS, "Cycle"), "int", False),
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "SimpleDate"),
        qn(REUSABLE_NS, "HistoricalDate"),
        qn(REUSABLE_NS, "StartDate"),
        qn(REUSABLE_NS, "HistoricalStartDate"),
        qn(REUSABLE_NS, "EndDate"),
        qn(REUSABLE_NS, "HistoricalEndDate"),
        qn(REUSABLE_NS, "Cycle"),
        qn(REUSABLE_NS, "EndDate"),
        qn(REUSABLE_NS, "HistoricalEndDate"),
        qn(REUSABLE_NS, "Subject"),
    ]


@dataclass
class ReferenceFields(MaintainableBase):
    """Used for referencing an identified entity expressed in DDI XML, either by a URN and/or an identification sequence. If both are supplied, the URN takes precedence. At a minimum, one or the other is req"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Reference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
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
class ReferenceWithBindingFields(MaintainableBase):
    """A reference to an object containing a Binding, e.g. a GeneralInstruction, GenerationInstruction, ControlConstruct, etc. The basic Reference structure is extended to allow for the use of Binding to lin"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ReferenceWithBinding")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    bindings: list[Element] = field(default_factory=list)  # [0..*]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "bindings": (qn(REUSABLE_NS, "Binding"), "element", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isExternal": ("isExternal", "bool"),
        "isReference": ("isReference", "bool"),
        "lateBound": ("lateBound", "bool"),
        "lateBoundRestriction": ("lateBoundRestriction", "str"),
        "objectLanguage": ("objectLanguage", "str"),
        "sourceContext": ("sourceContext", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "Binding"),
    ]


@dataclass
class RelatedLocationValueReferenceFields(MaintainableBase):
    """Provides a reference to the LocationValue or Values that is related to the current LocationValue partially or fully. TypeOfObject should be set to LocationValue."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "RelatedLocationValueReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    isFull: Optional[bool] = None  # @attr
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
        "isFull": ("isFull", "bool"),
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
class RelationshipFields(MaintainableBase):
    """Relationship specification between this item and the item to which it is related. Provides a reference to any identifiable object and a description of the relationship."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Relationship")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    related_to_reference: Optional[Reference] = None  # [1..1]
    relationship_description: Optional[Element] = None  # [0..1]
    type_of_relationship: Optional[CodeValue] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "related_to_reference": (qn(REUSABLE_NS, "RelatedToReference"), "reference", False),
        "relationship_description": (qn(REUSABLE_NS, "RelationshipDescription"), "element", False),
        "type_of_relationship": (qn(REUSABLE_NS, "TypeOfRelationship"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RelatedToReference"),
        qn(REUSABLE_NS, "RelationshipDescription"),
        qn(REUSABLE_NS, "TypeOfRelationship"),
    ]


@dataclass
class RepresentationReferenceFields(MaintainableBase):
    """References the managed representation of the variables' values. Allows for the listing of values to be treated as missing in order to support 3.1 structures. The prefered method is the use of a refere"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "RepresentationReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
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
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
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
class RepresentationFields(MaintainableBase):
    """Abstract type for the head of a substitution group for a variable representation or a question response domain. If specific values are used to denote missing values, these can be indicated as a space-"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Representation")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
    ]


@dataclass
class RequiredResourcePackagesFields(MaintainableBase):
    """Specifies by reference the ResourcePackages required to resolve the module."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "RequiredResourcePackages")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    resource_package_references: list[Reference] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "resource_package_references": (qn(REUSABLE_NS, "ResourcePackageReference"), "reference", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ResourcePackageReference"),
    ]


@dataclass
class ResponseCardinalityFields(MaintainableBase):
    """Indicates the minimum and maximum number of occurrences of a response within the given parameters."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ResponseCardinality")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    minimumResponses: Optional[int] = None  # @attr
    maximumResponses: Optional[int] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "minimumResponses": ("minimumResponses", "int"),
        "maximumResponses": ("maximumResponses", "int"),
    }


@dataclass
class RestrictionProcessFields(MaintainableBase):
    """Allows for a specific machine actionable description of the restriction process using a ProcessingInstructionReference, if one currently exists, or through a CommandCode. In the case of a physical ins"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "RestrictionProcess")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    processing_instruction_reference: Optional[Reference] = None  # [1..1]
    command_code: Optional[Element] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "processing_instruction_reference": (qn(REUSABLE_NS, "ProcessingInstructionReference"), "reference", False),
        "command_code": (qn(REUSABLE_NS, "CommandCode"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "ProcessingInstructionReference"),
        qn(REUSABLE_NS, "CommandCode"),
    ]


@dataclass
class ScaleDimensionFields(MaintainableBase):
    """Defines a dimension of a scale providing it with a label, a numeric or character based range, the attachment of a category label at one or more of the scale values, the frequency of increment markers,"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ScaleDimension")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    number_range: Optional[Element] = None  # [1..1]
    range: Optional[Element] = None  # [1..1]
    anchors: list[Element] = field(default_factory=list)  # [0..*]
    marked_increment: Optional[Element] = None  # [0..1]
    value_increment: Optional[Element] = None  # [0..1]
    dimensionNumber: Optional[int] = None  # @attr
    degreeSlopeFromHorizontal: Optional[int] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "number_range": (qn(REUSABLE_NS, "NumberRange"), "element", False),
        "range": (qn(REUSABLE_NS, "Range"), "element", False),
        "anchors": (qn(REUSABLE_NS, "Anchor"), "element", True),
        "marked_increment": (qn(REUSABLE_NS, "MarkedIncrement"), "element", False),
        "value_increment": (qn(REUSABLE_NS, "ValueIncrement"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "dimensionNumber": ("dimensionNumber", "int"),
        "degreeSlopeFromHorizontal": ("degreeSlopeFromHorizontal", "int"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "NumberRange"),
        qn(REUSABLE_NS, "Range"),
        qn(REUSABLE_NS, "Anchor"),
        qn(REUSABLE_NS, "MarkedIncrement"),
        qn(REUSABLE_NS, "ValueIncrement"),
    ]


@dataclass
class ScaleRepresentationBaseFields(MaintainableBase):
    """A means of capturing the structure of Scale for use as a question response domain or variable value representation. In addition to the basic objects of the representation, the structure defines the di"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "ScaleRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    scale_dimensions: list[Element] = field(default_factory=list)  # [0..*]
    dimension_intersects: list[Element] = field(default_factory=list)  # [0..*]
    display_layout: Optional[CodeValue] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "scale_dimensions": (qn(REUSABLE_NS, "ScaleDimension"), "element", True),
        "dimension_intersects": (qn(REUSABLE_NS, "DimensionIntersect"), "element", True),
        "display_layout": (qn(REUSABLE_NS, "DisplayLayout"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "ScaleDimension"),
        qn(REUSABLE_NS, "DimensionIntersect"),
        qn(REUSABLE_NS, "DisplayLayout"),
    ]


@dataclass
class SchemeReferenceFields(MaintainableBase):
    """Used for referencing an scheme expressed in DDI XML using the standard reference structure plus the ability to exclude the inclusion of any specified items belonging to the scheme. TypeOfObject should"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "SchemeReference")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_object: Optional[Element] = None  # [1..1]
    excludes: list[Reference] = field(default_factory=list)  # [0..*]
    isExternal: Optional[bool] = None  # @attr
    isReference: Optional[bool] = None  # @attr
    lateBound: Optional[bool] = None  # @attr
    lateBoundRestriction: Optional[str] = None  # @attr
    objectLanguage: Optional[str] = None  # @attr
    sourceContext: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_object": (qn(REUSABLE_NS, "TypeOfObject"), "element", False),
        "excludes": (qn(REUSABLE_NS, "Exclude"), "reference", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isExternal": ("isExternal", "bool"),
        "isReference": ("isReference", "bool"),
        "lateBound": ("lateBound", "bool"),
        "lateBoundRestriction": ("lateBoundRestriction", "str"),
        "objectLanguage": ("objectLanguage", "str"),
        "sourceContext": ("sourceContext", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "MaintainableObject"),
        qn(REUSABLE_NS, "UserAttributePair"),
        qn(REUSABLE_NS, "Exclude"),
    ]


@dataclass
class SegmentFields(MaintainableBase):
    """A structure used to express explicit segments or regions within different types of external materials (Textual, Audio, Video, XML, and Image). Provides the appropriate start, stop, or region definitio"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Segment")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    textuals: list[Element] = field(default_factory=list)  # [0..*]
    audios: list[Element] = field(default_factory=list)  # [0..*]
    videos: list[Element] = field(default_factory=list)  # [0..*]
    xmls: list[str] = field(default_factory=list)  # [0..*]
    image_areas: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "textuals": (qn(REUSABLE_NS, "Textual"), "element", True),
        "audios": (qn(REUSABLE_NS, "Audio"), "element", True),
        "videos": (qn(REUSABLE_NS, "Video"), "element", True),
        "xmls": (qn(REUSABLE_NS, "XML"), "str", True),
        "image_areas": (qn(REUSABLE_NS, "ImageArea"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Textual"),
        qn(REUSABLE_NS, "Audio"),
        qn(REUSABLE_NS, "Video"),
        qn(REUSABLE_NS, "XML"),
        qn(REUSABLE_NS, "ImageArea"),
    ]


@dataclass
class SeriesStatementFields(MaintainableBase):
    """Series statement contains information about the series to which a study unit or group of study units belongs. You may point to the URL of a series repository and then use the SeriesName field to indic"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "SeriesStatement")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    series_repository_locations: list[str] = field(default_factory=list)  # [0..*]
    series_names: list[InternationalString] = field(default_factory=list)  # [0..*]
    series_abbreviations: list[CodeValue] = field(default_factory=list)  # [0..*]
    series_description: Optional[Element] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "series_repository_locations": (qn(REUSABLE_NS, "SeriesRepositoryLocation"), "str", True),
        "series_names": (qn(REUSABLE_NS, "SeriesName"), "intl_string", True),
        "series_abbreviations": (qn(REUSABLE_NS, "SeriesAbbreviation"), "code_value", True),
        "series_description": (qn(REUSABLE_NS, "SeriesDescription"), "element", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "SeriesRepositoryLocation"),
        qn(REUSABLE_NS, "SeriesName"),
        qn(REUSABLE_NS, "SeriesAbbreviation"),
        qn(REUSABLE_NS, "SeriesDescription"),
    ]


@dataclass
class SoftwareFields(MaintainableBase):
    """Describes a specific software package, which may be commercially available or custom-made."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Software")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    software_package: Optional[CodeValue] = None  # [0..1]
    software_version: Optional[str] = None  # [0..1]
    date: Optional[Element] = None  # [0..1]
    functions: list[CodeValue] = field(default_factory=list)  # [0..*]
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(REUSABLE_NS, "SoftwareName"), "intl_string", True),
        "software_package": (qn(REUSABLE_NS, "SoftwarePackage"), "code_value", False),
        "software_version": (qn(REUSABLE_NS, "SoftwareVersion"), "str", False),
        "date": (qn(REUSABLE_NS, "Date"), "element", False),
        "functions": (qn(REUSABLE_NS, "Function"), "code_value", True),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "lang": ("lang", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "SoftwareName"),
        qn(REUSABLE_NS, "SoftwarePackage"),
        qn(REUSABLE_NS, "SoftwareVersion"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "Date"),
        qn(REUSABLE_NS, "Function"),
    ]


@dataclass
class SpatialCoordinateFields(MaintainableBase):
    """Lists the value and format type for the coordinate value. Note that this is a single value (X coordinate or Y coordinate) rather than a coordinate pair."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "SpatialCoordinate")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    coordinate_value: Optional[str] = None  # [1..1]
    coordinateType: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "coordinate_value": (qn(REUSABLE_NS, "CoordinateValue"), "str", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "coordinateType": ("coordinateType", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "CoordinateValue"),
    ]


@dataclass
class StandardKeyValuePairFields(MaintainableBase):
    """A basic data representation for computing systems and applications expressed as a tuple (attribute key, value). Attribute keys may or may not be unique."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "StandardKeyValuePair")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    attribute_key: Optional[CodeValue] = None  # [1..1]
    attribute_value: Optional[CodeValue] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "attribute_key": (qn(REUSABLE_NS, "AttributeKey"), "code_value", False),
        "attribute_value": (qn(REUSABLE_NS, "AttributeValue"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "AttributeKey"),
        qn(REUSABLE_NS, "AttributeValue"),
    ]


@dataclass
class StandardUsedFields(MaintainableBase):
    """Provide the citation and location of the published standard using the OtherMaterialType."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "StandardUsed")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    other_material: Optional[Element] = None  # [1..1]
    other_material_reference: Optional[Reference] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "other_material": (qn(REUSABLE_NS, "OtherMaterial"), "element", False),
        "other_material_reference": (qn(REUSABLE_NS, "OtherMaterialReference"), "reference", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "OtherMaterial"),
        qn(REUSABLE_NS, "OtherMaterialReference"),
    ]


@dataclass
class StringFields(MaintainableBase):
    """Allows for non-formatted strings that may be translations from other languages, or that may be translatable into other languages. Only one string per language/location type is allowed. String contains"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "String")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    lang: Optional[str] = None  # @attr
    isTranslated: Optional[bool] = None  # @attr
    isTranslatable: Optional[bool] = None  # @attr
    translationSourceLanguage: Optional[str] = None  # @attr
    translationDate: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "lang": ("lang", "str"),
        "isTranslated": ("isTranslated", "bool"),
        "isTranslatable": ("isTranslatable", "bool"),
        "translationSourceLanguage": ("translationSourceLanguage", "str"),
        "translationDate": ("translationDate", "str"),
    }


@dataclass
class StructuredCommandFields(MaintainableBase):
    """This type structures an empty stub which is used as the basis for extensions added using external namespaces such as MathML. The DDI 3.0 extension methodology is used here - a new module is declared, """

    TAG: ClassVar[str] = qn(REUSABLE_NS, "StructuredCommand")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    pass


@dataclass
class StructuredStringFields(MaintainableBase):
    """Packaging structure for multiple language versions of the same string content for objects that allow for internal formatting using XHTML tags. Where an element of this type is repeatable, the expectat"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "StructuredString")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    contents: list[Element] = field(default_factory=list)  # [1..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "contents": (qn(REUSABLE_NS, "Content"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "Content"),
    ]


@dataclass
class TemporalCoverageFields(MaintainableBase):
    """Describes the temporal coverage of the data described in a particular DDI module. A date may have a subject attached to it if the referent date has limited application."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "TemporalCoverage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    reference_dates: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "reference_dates": (qn(REUSABLE_NS, "ReferenceDate"), "element", True),
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
        qn(REUSABLE_NS, "ReferenceDate"),
    ]


@dataclass
class TextDomainFields(MaintainableBase):
    """A response domain capturing a textual response. Contains the equivalent content of a TextRepresentation including the length of the text and restriction of content using a regular expression. Adds a s"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "TextDomain")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    out_parameter: Optional[Element] = None  # [0..1]
    response_cardinality: Optional[Element] = None  # [0..1]
    content_date_offset: Optional[Element] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    maxLength: Optional[int] = None  # @attr
    minLength: Optional[int] = None  # @attr
    regExp: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
        "out_parameter": (qn(REUSABLE_NS, "OutParameter"), "element", False),
        "response_cardinality": (qn(REUSABLE_NS, "ResponseCardinality"), "element", False),
        "content_date_offset": (qn(REUSABLE_NS, "ContentDateOffset"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "maxLength": ("maxLength", "int"),
        "minLength": ("minLength", "int"),
        "regExp": ("regExp", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(REUSABLE_NS, "OutParameter"),
        qn(REUSABLE_NS, "ResponseCardinality"),
        qn(REUSABLE_NS, "ContentDateOffset"),
    ]


@dataclass
class TextRepresentationBaseFields(MaintainableBase):
    """Structures a textual representation. MinLength and maxlength attributes are inclusive integers describing the number of permitted characters. The regExp attribute holds a regular expression describing"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "TextRepresentationBase")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    recommended_data_type: Optional[CodeValue] = None  # [0..1]
    generic_output_format: Optional[CodeValue] = None  # [0..1]
    measurement_unit: Optional[CodeValue] = None  # [0..1]
    missingValue: Optional[str] = None  # @attr
    blankIsMissingValue: Optional[bool] = None  # @attr
    classificationLevel: Optional[str] = None  # @attr
    maxLength: Optional[int] = None  # @attr
    minLength: Optional[int] = None  # @attr
    regExp: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "recommended_data_type": (qn(REUSABLE_NS, "RecommendedDataType"), "code_value", False),
        "generic_output_format": (qn(REUSABLE_NS, "GenericOutputFormat"), "code_value", False),
        "measurement_unit": (qn(REUSABLE_NS, "MeasurementUnit"), "code_value", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "missingValue": ("missingValue", "str"),
        "blankIsMissingValue": ("blankIsMissingValue", "bool"),
        "classificationLevel": ("classificationLevel", "str"),
        "maxLength": ("maxLength", "int"),
        "minLength": ("minLength", "int"),
        "regExp": ("regExp", "str"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RecommendedDataType"),
        qn(REUSABLE_NS, "GenericOutputFormat"),
        qn(REUSABLE_NS, "MeasurementUnit"),
    ]


@dataclass
class TextualFields(MaintainableBase):
    """Defines the segment of textual content used by the parent object. Can identify a set of lines and or characters used to define the segment."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Textual")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    line_parameters: list[Element] = field(default_factory=list)  # [0..*]
    character_parameters: list[Element] = field(default_factory=list)  # [0..*]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "line_parameters": (qn(REUSABLE_NS, "LineParameter"), "element", True),
        "character_parameters": (qn(REUSABLE_NS, "CharacterParameter"), "element", True),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "LineParameter"),
        qn(REUSABLE_NS, "CharacterParameter"),
    ]


@dataclass
class TopicalCoverageFields(MaintainableBase):
    """Describes the topical coverage of the module using Subject and Keyword. Note that upper level modules should include all the members of lower level modules. Subjects are members of structured classifi"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "TopicalCoverage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    subjects: list[CodeValue] = field(default_factory=list)  # [0..*]
    keywords: list[CodeValue] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "subjects": (qn(REUSABLE_NS, "Subject"), "code_value", True),
        "keywords": (qn(REUSABLE_NS, "Keyword"), "code_value", True),
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
        qn(REUSABLE_NS, "Subject"),
        qn(REUSABLE_NS, "Keyword"),
    ]


@dataclass
class URNFields(MaintainableBase):
    """Container for a URN following the pattern designed by DDIURNType. Provides a fixed type attribute signifying that it is a URN."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "URN")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "type": ("type", "str"),
    }


@dataclass
class UserIDFields(MaintainableBase):
    """A user provided identifier that is locally unique within its specific type. The required type attribute points to the local user identification system that defines the values. The optional userIDVersi"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "UserID")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    typeOfUserID: Optional[str] = None  # @attr
    userIDVersion: Optional[str] = None  # @attr
    typeOfUserVersion: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "typeOfUserID": ("typeOfUserID", "str"),
        "userIDVersion": ("userIDVersion", "str"),
        "typeOfUserVersion": ("typeOfUserVersion", "str"),
    }


@dataclass
class ValueFields(MaintainableBase):
    """The Value expressed as an xs:string with the ability to preserve whitespace if critical to the understanding of the content."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Value")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    space: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "space": ("space", "str"),
    }


@dataclass
class VersionRationaleFields(MaintainableBase):
    """Textual description of the rationale/purpose for the version change and a coded value to provide an internal processing flag within and organization or system. Note that versioning can only take place"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "VersionRationale")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    rationale_description: Optional[Element] = None  # [0..1]
    rationale_code: Optional[CodeValue] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "rationale_description": (qn(REUSABLE_NS, "RationaleDescription"), "element", False),
        "rationale_code": (qn(REUSABLE_NS, "RationaleCode"), "code_value", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "RationaleDescription"),
        qn(REUSABLE_NS, "RationaleCode"),
    ]


@dataclass
class VersionableFields(MaintainableBase):
    """Adds the attribute identifying this as a versionable object as well as the MaintainableObject. All versionable objects should provide their contextual information, the identity of their maintainable p"""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Versionable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
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
class VideoFields(MaintainableBase):
    """Describes the type and length of the video segment."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "Video")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")
    type_of_video_clip: Optional[CodeValue] = None  # [1..1]
    video_clip_begin: Optional[str] = None  # [0..1]
    video_clip_end: Optional[str] = None  # [0..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "type_of_video_clip": (qn(REUSABLE_NS, "TypeOfVideoClip"), "code_value", False),
        "video_clip_begin": (qn(REUSABLE_NS, "VideoClipBegin"), "str", False),
        "video_clip_end": (qn(REUSABLE_NS, "VideoClipEnd"), "str", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(REUSABLE_NS, "TypeOfVideoClip"),
        qn(REUSABLE_NS, "VideoClipBegin"),
        qn(REUSABLE_NS, "VideoClipEnd"),
    ]

