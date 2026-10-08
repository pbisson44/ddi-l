"""AUTO-GENERATED base dataclasses for DDI 3.3 — ddiprofile module.

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
from ddi_l.models.base import CodeValue, InternationalString, MaintainableBase
from ddi_l.constants import DDI_PROFILE_NS, REUSABLE_NS
from ddi_l.namespaces import NamespaceBindings, build_namespace_map
from ddi_l.models.base import qn


@dataclass
class DDIProfileFields(MaintainableBase):
    """Describes the subset of valid DDI objects used by an agency for a specified purpose. This may be the required and supported objects for a specific system, a profile for deposit in an archive, requirem"""

    TAG: ClassVar[str] = qn(DDI_PROFILE_NS, "DDIProfile")
    names: list[InternationalString] = field(default_factory=list)  # [0..*]
    application_of_profiles: list[CodeValue] = field(default_factory=list)  # [0..*]
    purpose: Optional[Element] = None  # [0..1]
    x_path_version: Optional[float] = None  # [1..1]
    ddi_namespace: Optional[float] = None  # [0..1]
    xml_prefix_maps: list[Element] = field(default_factory=list)  # [0..*]
    instructions: Optional[Element] = None  # [0..1]
    useds: list[Element] = field(default_factory=list)  # [0..*]
    not_useds: list[Element] = field(default_factory=list)  # [0..*]
    inheritanceAction: Optional[str] = None  # @attr
    objectSource: Optional[str] = None  # @attr
    scopeOfUniqueness: Optional[str] = None  # @attr
    versionDate: Optional[str] = None  # @attr
    isPublished: Optional[bool] = None  # @attr
    lang: Optional[str] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "names": (qn(DDI_PROFILE_NS, "DDIProfileName"), "intl_string", True),
        "application_of_profiles": (qn(DDI_PROFILE_NS, "ApplicationOfProfile"), "code_value", True),
        "purpose": (qn(REUSABLE_NS, "Purpose"), "element", False),
        "x_path_version": (qn(DDI_PROFILE_NS, "XPathVersion"), "float", False),
        "ddi_namespace": (qn(DDI_PROFILE_NS, "DDINamespace"), "float", False),
        "xml_prefix_maps": (qn(DDI_PROFILE_NS, "XMLPrefixMap"), "element", True),
        "instructions": (qn(DDI_PROFILE_NS, "Instructions"), "element", False),
        "useds": (qn(DDI_PROFILE_NS, "Used"), "element", True),
        "not_useds": (qn(DDI_PROFILE_NS, "NotUsed"), "element", True),
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
        qn(DDI_PROFILE_NS, "DDIProfileName"),
        qn(REUSABLE_NS, "Label"),
        qn(REUSABLE_NS, "Description"),
        qn(DDI_PROFILE_NS, "ApplicationOfProfile"),
        qn(REUSABLE_NS, "Purpose"),
        qn(DDI_PROFILE_NS, "XPathVersion"),
        qn(DDI_PROFILE_NS, "DDINamespace"),
        qn(DDI_PROFILE_NS, "XMLPrefixMap"),
        qn(DDI_PROFILE_NS, "Instructions"),
        qn(DDI_PROFILE_NS, "Used"),
        qn(DDI_PROFILE_NS, "NotUsed"),
    ]


@dataclass
class NotUsedFields(MaintainableBase):
    """Identifies DDI objects expressed as an XPath that are not supported by the system or agency using this profile."""

    TAG: ClassVar[str] = qn(DDI_PROFILE_NS, "NotUsed")
    xpath: Optional[str] = None  # @attr
    _ATTR_XML_MAP: ClassVar[dict] = {
        "xpath": ("xpath", "str"),
    }


@dataclass
class UsedFields(MaintainableBase):
    """Specifies a DDI object and all its sub-objects supported by the DDIProfile. May specify an alternate local name and description of an object, instructions for its use, and set limits on its allowed us"""

    TAG: ClassVar[str] = qn(DDI_PROFILE_NS, "Used")
    alternate_name: Optional[Element] = None  # [0..1]
    instructions: Optional[Element] = None  # [0..1]
    default_value: Optional[Element] = None  # [0..1]
    isRequired: Optional[bool] = None  # @attr
    xpath: Optional[str] = None  # @attr
    limitMaxOccurs: Optional[str] = None  # @attr
    fixedValue: Optional[bool] = None  # @attr
    _FIELD_XML_MAP: ClassVar[dict] = {
        "alternate_name": (qn(DDI_PROFILE_NS, "AlternateName"), "element", False),
        "instructions": (qn(DDI_PROFILE_NS, "Instructions"), "element", False),
        "default_value": (qn(REUSABLE_NS, "DefaultValue"), "element", False),
    }
    _ATTR_XML_MAP: ClassVar[dict] = {
        "isRequired": ("isRequired", "bool"),
        "xpath": ("xpath", "str"),
        "limitMaxOccurs": ("limitMaxOccurs", "str"),
        "fixedValue": ("fixedValue", "bool"),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DDI_PROFILE_NS, "AlternateName"),
        qn(REUSABLE_NS, "Description"),
        qn(DDI_PROFILE_NS, "Instructions"),
        qn(REUSABLE_NS, "DefaultValue"),
    ]


@dataclass
class XMLPrefixMapFields(MaintainableBase):
    """Maps a specified prefix to a namespace. For each XML namespace used in the profile's XPath expressions, the XML namespaces must have their prefix specified using this element."""

    TAG: ClassVar[str] = qn(DDI_PROFILE_NS, "XMLPrefixMap")
    xml_prefix: Optional[str] = None  # [1..1]
    xml_namespace: Optional[str] = None  # [1..1]
    _FIELD_XML_MAP: ClassVar[dict] = {
        "xml_prefix": (qn(DDI_PROFILE_NS, "XMLPrefix"), "str", False),
        "xml_namespace": (qn(DDI_PROFILE_NS, "XMLNamespace"), "str", False),
    }
    _ELEMENT_ORDER: ClassVar[list[str]] = [
        qn(DDI_PROFILE_NS, "XMLPrefix"),
        qn(DDI_PROFILE_NS, "XMLNamespace"),
    ]

