"""Wrappers for archive metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from .._etree import Element, create_element
from ..constants import ARCHIVE_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.archive import ArchiveFields, OrganizationFields
from .base import (
    InternationalString,
    apply_other_attributes,
    clone_element,
    collect_other_attributes,
    qn,
)

__all__ = ["Archive", "Organization", "OrganizationIdentification"]


@dataclass
class Archive(ArchiveFields):
    """Representation of ``a:Archive`` modules."""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Archive")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")


@dataclass
class OrganizationIdentification:
    """Wrapper for ``a:OrganizationIdentification`` entries."""

    names: list[InternationalString] = field(default_factory=list)
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "OrganizationIdentification")

    @classmethod
    def from_xml(cls, element: Element) -> OrganizationIdentification:
        if element.tag != cls.TAG:
            raise ValueError("Expected an archive:OrganizationIdentification element.")
        recognized = {qn(ARCHIVE_NS, "OrganizationName")}
        names: list[InternationalString] = []
        for container in element.findall(qn(ARCHIVE_NS, "OrganizationName")):
            names.extend(InternationalString.from_container(container))
        extras = [
            clone_element(child) for child in element if child.tag not in recognized
        ]
        return cls(
            names=names,
            other_elements=extras,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        for name in self.names:
            container = create_element(qn(ARCHIVE_NS, "OrganizationName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        for child in self.other_elements:
            element.append(clone_element(child))
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class Organization(OrganizationFields):
    """Maintainable representation of ``a:Organization`` fragments."""

    TAG: ClassVar[str] = qn(ARCHIVE_NS, "Organization")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("a")
