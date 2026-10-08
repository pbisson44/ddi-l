"""Wrappers for conceptual components grouping concepts and universes."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import ClassVar

from .._etree import Element, create_element
from ..constants import CONCEPTUAL_COMPONENT_NS, REUSABLE_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.conceptualcomponent import ConceptualComponentFields
from .base import MaintainableBase, Reference, clone_element, qn
from .concept import Concept, ConceptualVariable, UnitType, Universe

__all__ = ["ConceptualComponent"]


@dataclass
class ConceptualComponent(ConceptualComponentFields):
    """Representation of ``c:ConceptualComponent`` maintainable modules."""

    concepts: list[Concept] = field(default_factory=list)
    universes: list[Universe] = field(default_factory=list)
    conceptual_variables: list[ConceptualVariable] = field(default_factory=list)
    unit_types: list[UnitType] = field(default_factory=list)
    concept_scheme_references: list[Reference] = field(default_factory=list)
    universe_scheme_references: list[Reference] = field(default_factory=list)
    conceptual_variable_scheme_references: list[Reference] = field(default_factory=list)
    unit_type_scheme_references: list[Reference] = field(default_factory=list)
    geographic_location_scheme_references: list[Reference] = field(default_factory=list)
    geographic_structure_scheme_references: list[Reference] = field(
        default_factory=list
    )
    has_concept_scheme: bool = False
    has_universe_scheme: bool = False
    has_conceptual_variable_scheme: bool = False
    has_unit_type_scheme: bool = False
    inline_only: bool = False

    TAG: ClassVar[str] = qn(CONCEPTUAL_COMPONENT_NS, "ConceptualComponent")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("c")

    def __post_init__(self) -> None:
        def _suffix(base: str) -> Callable[[int, MaintainableBase], str | None]:
            return lambda index, _child: self._default_child_suffix(base, index)

        self._propagate_child_identification(
            self.concepts, identifier_suffix_factory=_suffix("concept")
        )
        self._propagate_child_identification(
            self.universes, identifier_suffix_factory=_suffix("universe")
        )
        self._propagate_child_identification(
            self.conceptual_variables,
            identifier_suffix_factory=_suffix("conceptual-variable"),
        )
        self._propagate_child_identification(
            self.unit_types, identifier_suffix_factory=_suffix("unit-type")
        )

    @classmethod
    def from_xml(cls, element: Element) -> ConceptualComponent:
        concept_scheme_tag = qn(CONCEPTUAL_COMPONENT_NS, "ConceptScheme")
        concept_tag = Concept.TAG
        universe_scheme_tag = qn(CONCEPTUAL_COMPONENT_NS, "UniverseScheme")
        universe_tag = Universe.TAG
        conceptual_variable_scheme_tag = qn(
            CONCEPTUAL_COMPONENT_NS, "ConceptualVariableScheme"
        )
        conceptual_variable_tag = ConceptualVariable.TAG
        unit_type_scheme_tag = qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeScheme")
        unit_type_tag = UnitType.TAG

        recognized = {
            concept_scheme_tag,
            concept_tag,
            universe_scheme_tag,
            universe_tag,
            conceptual_variable_scheme_tag,
            conceptual_variable_tag,
            unit_type_scheme_tag,
            unit_type_tag,
            qn(REUSABLE_NS, "ConceptSchemeReference"),
            qn(REUSABLE_NS, "UniverseSchemeReference"),
            qn(REUSABLE_NS, "ConceptualVariableSchemeReference"),
            qn(REUSABLE_NS, "UnitTypeSchemeReference"),
            qn(REUSABLE_NS, "GeographicLocationSchemeReference"),
            qn(REUSABLE_NS, "GeographicStructureSchemeReference"),
        }

        concepts: list[Concept] = []
        concept_scheme_elements = element.findall(concept_scheme_tag)
        for scheme in concept_scheme_elements:
            for child in scheme.findall(concept_tag):
                concepts.append(Concept.from_xml(child))
        for child in element.findall(concept_tag):
            concepts.append(Concept.from_xml(child))

        universes: list[Universe] = []
        universe_scheme_elements = element.findall(universe_scheme_tag)
        for scheme in universe_scheme_elements:
            for child in scheme.findall(universe_tag):
                universes.append(Universe.from_xml(child))
        for child in element.findall(universe_tag):
            universes.append(Universe.from_xml(child))

        conceptual_variables: list[ConceptualVariable] = []
        conceptual_variable_scheme_elements = element.findall(
            conceptual_variable_scheme_tag
        )
        for scheme in conceptual_variable_scheme_elements:
            for child in scheme.findall(conceptual_variable_tag):
                conceptual_variables.append(ConceptualVariable.from_xml(child))
        for child in element.findall(conceptual_variable_tag):
            conceptual_variables.append(ConceptualVariable.from_xml(child))

        unit_types: list[UnitType] = []
        unit_type_scheme_elements = element.findall(unit_type_scheme_tag)
        for scheme in unit_type_scheme_elements:
            for child in scheme.findall(unit_type_tag):
                unit_types.append(UnitType.from_xml(child))
        for child in element.findall(unit_type_tag):
            unit_types.append(UnitType.from_xml(child))

        concept_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "ConceptSchemeReference"))
        ]
        universe_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "UniverseSchemeReference"))
        ]
        conceptual_variable_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(
                qn(REUSABLE_NS, "ConceptualVariableSchemeReference")
            )
        ]
        unit_type_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(qn(REUSABLE_NS, "UnitTypeSchemeReference"))
        ]
        geographic_location_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(
                qn(REUSABLE_NS, "GeographicLocationSchemeReference")
            )
        ]
        geographic_structure_scheme_references = [
            Reference.from_xml(ref)
            for ref in element.findall(
                qn(REUSABLE_NS, "GeographicStructureSchemeReference")
            )
        ]
        data = cls._collect_common(element, recognized_children=recognized)
        return cls(
            concepts=concepts,
            universes=universes,
            conceptual_variables=conceptual_variables,
            unit_types=unit_types,
            concept_scheme_references=concept_scheme_references,
            universe_scheme_references=universe_scheme_references,
            conceptual_variable_scheme_references=conceptual_variable_scheme_references,
            unit_type_scheme_references=unit_type_scheme_references,
            geographic_location_scheme_references=geographic_location_scheme_references,
            geographic_structure_scheme_references=geographic_structure_scheme_references,
            has_concept_scheme=bool(concept_scheme_elements),
            has_universe_scheme=bool(universe_scheme_elements),
            has_conceptual_variable_scheme=bool(conceptual_variable_scheme_elements),
            has_unit_type_scheme=bool(unit_type_scheme_elements),
            **data,
        )

    def to_xml(self) -> Element:
        if self.inline_only:
            raise ValueError(
                "Inline conceptual components do not produce"
                " a standalone ConceptualComponent element."
            )
        element = self._build_base_element()
        if self.concepts:
            if self.has_concept_scheme:
                concept_scheme = create_element(
                    qn(CONCEPTUAL_COMPONENT_NS, "ConceptScheme")
                )
                self._append_child_identification(concept_scheme, suffix="concepts")
                for concept in self.concepts:
                    concept_scheme.append(concept.to_xml())
                element.append(concept_scheme)
            else:
                for concept in self.concepts:
                    element.append(concept.to_xml())
        if self.universes:
            if self.has_universe_scheme:
                universe_scheme = create_element(
                    qn(CONCEPTUAL_COMPONENT_NS, "UniverseScheme")
                )
                self._append_child_identification(universe_scheme, suffix="universes")
                for universe in self.universes:
                    universe_scheme.append(universe.to_xml())
                element.append(universe_scheme)
            else:
                for universe in self.universes:
                    element.append(universe.to_xml())
        if self.conceptual_variables:
            if self.has_conceptual_variable_scheme:
                variable_scheme = create_element(
                    qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableScheme")
                )
                self._append_child_identification(
                    variable_scheme, suffix="conceptual-variables"
                )
                for conceptual_variable in self.conceptual_variables:
                    variable_scheme.append(conceptual_variable.to_xml())
                element.append(variable_scheme)
            else:
                for conceptual_variable in self.conceptual_variables:
                    element.append(conceptual_variable.to_xml())
        if self.unit_types:
            if self.has_unit_type_scheme:
                unit_type_scheme = create_element(
                    qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeScheme")
                )
                self._append_child_identification(unit_type_scheme, suffix="unit-types")
                for unit_type in self.unit_types:
                    unit_type_scheme.append(unit_type.to_xml())
                element.append(unit_type_scheme)
            else:
                for unit_type in self.unit_types:
                    element.append(unit_type.to_xml())
        for ref in self.concept_scheme_references:
            element.append(ref.to_xml("ConceptSchemeReference"))
        for ref in self.universe_scheme_references:
            element.append(ref.to_xml("UniverseSchemeReference"))
        for ref in self.conceptual_variable_scheme_references:
            element.append(ref.to_xml("ConceptualVariableSchemeReference"))
        for ref in self.unit_type_scheme_references:
            element.append(ref.to_xml("UnitTypeSchemeReference"))
        for ref in self.geographic_location_scheme_references:
            element.append(ref.to_xml("GeographicLocationSchemeReference"))
        for ref in self.geographic_structure_scheme_references:
            element.append(ref.to_xml("GeographicStructureSchemeReference"))
        self._append_other_elements(element)
        return element

    def append_inline_children(self, parent: Element) -> None:
        """Append conceptual content directly to ``parent`` when inline-only."""
        if self.concepts:
            if self.has_concept_scheme:
                concept_scheme = create_element(
                    qn(CONCEPTUAL_COMPONENT_NS, "ConceptScheme")
                )
                for concept in self.concepts:
                    concept_scheme.append(concept.to_xml())
                parent.append(concept_scheme)
            else:
                for concept in self.concepts:
                    parent.append(concept.to_xml())
        if self.universes:
            if self.has_universe_scheme:
                universe_scheme = create_element(
                    qn(CONCEPTUAL_COMPONENT_NS, "UniverseScheme")
                )
                for universe in self.universes:
                    universe_scheme.append(universe.to_xml())
                parent.append(universe_scheme)
            else:
                for universe in self.universes:
                    parent.append(universe.to_xml())
        if self.conceptual_variables:
            if self.has_conceptual_variable_scheme:
                variable_scheme = create_element(
                    qn(CONCEPTUAL_COMPONENT_NS, "ConceptualVariableScheme")
                )
                for conceptual_variable in self.conceptual_variables:
                    variable_scheme.append(conceptual_variable.to_xml())
                parent.append(variable_scheme)
            else:
                for conceptual_variable in self.conceptual_variables:
                    parent.append(conceptual_variable.to_xml())
        if self.unit_types:
            if self.has_unit_type_scheme:
                unit_type_scheme = create_element(
                    qn(CONCEPTUAL_COMPONENT_NS, "UnitTypeScheme")
                )
                for unit_type in self.unit_types:
                    unit_type_scheme.append(unit_type.to_xml())
                parent.append(unit_type_scheme)
            else:
                for unit_type in self.unit_types:
                    parent.append(unit_type.to_xml())
        for extra in self.other_elements:
            parent.append(clone_element(extra))
