"""Maintainable wrappers for the DDI Group module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..constants import GROUP_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.group import (
    GroupFields,
    LocalHoldingPackageFields,
    ResourcePackageFields,
)
from .base import qn

__all__ = ["Group", "LocalHoldingPackage", "ResourcePackage"]


@dataclass
class Group(GroupFields):
    """Representation of ``g:Group`` maintainables."""

    TAG: ClassVar[str] = qn(GROUP_NS, "Group")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("g")


@dataclass
class ResourcePackage(ResourcePackageFields):
    """Representation of ``g:ResourcePackage`` maintainables."""

    TAG: ClassVar[str] = qn(GROUP_NS, "ResourcePackage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("g")


@dataclass
class LocalHoldingPackage(LocalHoldingPackageFields):
    """Representation of ``g:LocalHoldingPackage`` maintainables."""

    TAG: ClassVar[str] = qn(GROUP_NS, "LocalHoldingPackage")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("g")
