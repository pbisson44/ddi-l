"""Wrappers for conceptual content such as concepts and universes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..constants import CONCEPTUAL_COMPONENT_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.conceptualcomponent import (
    ConceptFields,
    ConceptualVariableFields,
    UnitTypeFields,
    UniverseFields,
)
from .base import qn

__all__ = ["Concept", "ConceptualVariable", "UnitType", "Universe"]


@dataclass
class Concept(ConceptFields):
    """Representation of ``c:Concept`` elements."""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "Concept")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")


@dataclass
class ConceptualVariable(ConceptualVariableFields):
    """Representation of ``c:ConceptualVariable`` entries."""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariable")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")


@dataclass
class Universe(UniverseFields):
    """Representation of ``c:Universe`` elements."""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "Universe")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")


@dataclass
class UnitType(UnitTypeFields):
    """Representation of ``c:UnitType`` entries."""

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "UnitType")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")
