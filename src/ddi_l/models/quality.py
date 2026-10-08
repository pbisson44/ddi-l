"""Wrappers for reusable quality metadata structures."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar

from ..constants import REUSABLE_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.reusable import (
    QualitySchemeFields,
    QualityStandardFields,
    QualityStandardGroupFields,
    QualityStatementFields,
    QualityStatementGroupFields,
)
from .base import MaintainableBase, qn

__all__ = [
    "QualityScheme",
    "QualityStandard",
    "QualityStandardGroup",
    "QualityStatement",
    "QualityStatementGroup",
]


@dataclass
class QualityStandard(QualityStandardFields):
    """Maintainable wrapper for ``r:QualityStandard`` descriptions."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "QualityStandard")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")


@dataclass
class QualityStatement(QualityStatementFields):
    """Maintainable wrapper for ``r:QualityStatement`` entries."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "QualityStatement")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")


@dataclass
class QualityStatementGroup(QualityStatementGroupFields):
    """Maintainable wrapper for ``r:QualityStatementGroup`` collections."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "QualityStatementGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")


@dataclass
class QualityStandardGroup(QualityStandardGroupFields):
    """Maintainable wrapper for ``r:QualityStandardGroup`` structures."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "QualityStandardGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")


@dataclass
class QualityScheme(QualitySchemeFields):
    """Maintainable wrapper for ``r:QualityScheme`` instances."""

    TAG: ClassVar[str] = qn(REUSABLE_NS, "QualityScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("r")

    def __post_init__(self) -> None:
        def _suffix(base: str) -> Callable[[int, MaintainableBase], str | None]:
            return lambda index, _child: self._default_child_suffix(base, index)

        self._propagate_child_identification(
            self.quality_statements,  # type: ignore[arg-type]
            identifier_suffix_factory=_suffix("quality-statement"),
        )
        self._propagate_child_identification(
            self.quality_standards,  # type: ignore[arg-type]
            identifier_suffix_factory=_suffix("quality-standard"),
        )
        self._propagate_child_identification(
            self.quality_statement_groups,  # type: ignore[arg-type]
            identifier_suffix_factory=_suffix("quality-statement-group"),
        )
        self._propagate_child_identification(
            self.quality_standard_groups,  # type: ignore[arg-type]
            identifier_suffix_factory=_suffix("quality-standard-group"),
        )
