"""Wrappers for the Comparative module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .._etree import Element, create_element
from ..constants import COMPARATIVE_NS, REUSABLE_NS
from ..namespaces import NamespaceBindings, build_namespace_map
from ._generated.comparative import ComparisonFields
from .base import InternationalString, Reference, clone_element, qn

__all__ = ["Comparison"]


@dataclass
class Comparison(ComparisonFields):
    """Representation of ``cm:Comparison`` modules.

    A comparison records how items in different study units (or versions)
    correspond. Add maps with :meth:`add_variable_map` and
    :meth:`add_concept_map`; build one at the high level with
    :meth:`ddi_l.document.Document.add_comparison`.
    """

    TAG: ClassVar[str] = qn(COMPARATIVE_NS, "Comparison")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("cmp", "r")

    def add_variable_map(
        self,
        source: Reference,
        target: Reference,
        *,
        source_scheme: Reference | None = None,
        target_scheme: Reference | None = None,
        correspondence: Element | None = None,
    ) -> Element:
        """Map a source variable to a target variable. Returns the map element."""
        return self._add_map(
            "VariableMap",
            self.variable_maps,
            source,
            target,
            source_scheme=source_scheme,
            target_scheme=target_scheme,
            correspondence=correspondence,
        )

    def add_concept_map(
        self,
        source: Reference,
        target: Reference,
        *,
        source_scheme: Reference | None = None,
        target_scheme: Reference | None = None,
        correspondence: Element | None = None,
    ) -> Element:
        """Map a source concept to a target concept. Returns the map element."""
        return self._add_map(
            "ConceptMap",
            self.concept_maps,
            source,
            target,
            source_scheme=source_scheme,
            target_scheme=target_scheme,
            correspondence=correspondence,
        )

    def add_question_map(
        self,
        source: Reference,
        target: Reference,
        *,
        source_scheme: Reference | None = None,
        target_scheme: Reference | None = None,
        correspondence: Element | None = None,
    ) -> Element:
        """Map a source question to a target question. Returns the map element."""
        return self._add_map(
            "QuestionMap",
            self.question_maps,
            source,
            target,
            source_scheme=source_scheme,
            target_scheme=target_scheme,
            correspondence=correspondence,
        )

    def add_category_map(
        self,
        source: Reference,
        target: Reference,
        *,
        source_scheme: Reference | None = None,
        target_scheme: Reference | None = None,
        correspondence: Element | None = None,
    ) -> Element:
        """Map a source category to a target category. Returns the map element."""
        return self._add_map(
            "CategoryMap",
            self.category_maps,
            source,
            target,
            source_scheme=source_scheme,
            target_scheme=target_scheme,
            correspondence=correspondence,
        )

    def add_universe_map(
        self,
        source: Reference,
        target: Reference,
        *,
        source_scheme: Reference | None = None,
        target_scheme: Reference | None = None,
        correspondence: Element | None = None,
    ) -> Element:
        """Map a source universe to a target universe. Returns the map element."""
        return self._add_map(
            "UniverseMap",
            self.universe_maps,
            source,
            target,
            source_scheme=source_scheme,
            target_scheme=target_scheme,
            correspondence=correspondence,
        )

    def _add_map(
        self,
        tag: str,
        store: list[Element],
        source: Reference,
        target: Reference,
        *,
        source_scheme: Reference | None = None,
        target_scheme: Reference | None = None,
        correspondence: Element | None = None,
    ) -> Element:
        generic_map = create_element(qn(COMPARATIVE_NS, tag))
        # GenericMapType is VersionableType and ItemMapType is IdentifiableType,
        # so both need Agency/ID/Version. Scheme references and a map-level
        # Correspondence precede the ItemMap in the content model.
        self._append_child_identification(generic_map, suffix=f"{tag}-{len(store) + 1}")
        if source_scheme is not None:
            generic_map.append(
                source_scheme.to_xml("SourceSchemeReference", namespace=COMPARATIVE_NS)
            )
        if target_scheme is not None:
            generic_map.append(
                target_scheme.to_xml("TargetSchemeReference", namespace=COMPARATIVE_NS)
            )
        if correspondence is not None:
            generic_map.append(clone_element(correspondence))
        item_map = create_element(qn(COMPARATIVE_NS, "ItemMap"))
        self._append_child_identification(
            item_map, suffix=f"{tag}-item-{len(store) + 1}"
        )
        item_map.append(source.to_xml("SourceItemReference", namespace=COMPARATIVE_NS))
        item_map.append(target.to_xml("TargetItemReference", namespace=COMPARATIVE_NS))
        generic_map.append(item_map)
        store.append(generic_map)
        return generic_map

    def add_managed_item_map(
        self,
        item_pairs: list[tuple[Reference, Reference]],
        *,
        type_of_mapped_item: str | None = None,
        source_scheme: Reference | None = None,
        target_scheme: Reference | None = None,
        correspondence: Element | None = None,
    ) -> Element:
        """Add a ``ManagedItemMap`` (a scheme-to-scheme map with many item maps).

        ``item_pairs`` is a list of ``(source, target)`` reference pairs, one per
        ``ItemMap``. ``type_of_mapped_item`` names what is mapped (e.g.
        ``"Variable"``); ``source_scheme``/``target_scheme`` reference the mapped
        schemes; ``correspondence`` is a map-level :meth:`correspondence`.
        Returns the managed item map element.
        """
        managed_map = create_element(qn(COMPARATIVE_NS, "ManagedItemMap"))
        self._append_child_identification(
            managed_map, suffix=f"managed-item-map-{len(self.managed_item_maps) + 1}"
        )
        if type_of_mapped_item is not None:
            type_el = create_element(qn(COMPARATIVE_NS, "TypeOfMappedItem"))
            type_el.text = type_of_mapped_item
            managed_map.append(type_el)
        if source_scheme is not None:
            managed_map.append(
                source_scheme.to_xml("SourceSchemeReference", namespace=COMPARATIVE_NS)
            )
        if target_scheme is not None:
            managed_map.append(
                target_scheme.to_xml("TargetSchemeReference", namespace=COMPARATIVE_NS)
            )
        if correspondence is not None:
            managed_map.append(clone_element(correspondence))
        for index, (source, target) in enumerate(item_pairs, start=1):
            item_map = create_element(qn(COMPARATIVE_NS, "ItemMap"))
            self._append_child_identification(
                item_map,
                suffix=f"managed-item-{len(self.managed_item_maps) + 1}-{index}",
            )
            item_map.append(
                source.to_xml("SourceItemReference", namespace=COMPARATIVE_NS)
            )
            item_map.append(
                target.to_xml("TargetItemReference", namespace=COMPARATIVE_NS)
            )
            managed_map.append(item_map)
        self.managed_item_maps.append(managed_map)
        return managed_map

    def add_representation_map(
        self,
        source_representation: Reference,
        target_representation: Reference,
        processing_instruction: Reference,
        *,
        source_kind: str = "CodeListReference",
        target_kind: str = "CodeListReference",
        correspondence: Element | None = None,
    ) -> Element:
        """Add a ``RepresentationMap`` (maps one value domain onto another).

        ``source_representation``/``target_representation`` reference the mapped
        representations (code lists by default; pass ``source_kind``/
        ``target_kind`` for another, e.g. ``"CategorySchemeReference"``).
        ``processing_instruction`` references the instruction that transforms
        source values into target values. Returns the representation map element.
        """
        representation_map = create_element(qn(COMPARATIVE_NS, "RepresentationMap"))
        self._append_child_identification(
            representation_map,
            suffix=f"representation-map-{len(self.representation_maps) + 1}",
        )
        source_el = create_element(qn(COMPARATIVE_NS, "SourceRepresentation"))
        source_el.append(
            source_representation.to_xml(source_kind, namespace=REUSABLE_NS)
        )
        representation_map.append(source_el)
        target_el = create_element(qn(COMPARATIVE_NS, "TargetRepresentation"))
        target_el.append(
            target_representation.to_xml(target_kind, namespace=REUSABLE_NS)
        )
        representation_map.append(target_el)
        if correspondence is not None:
            representation_map.append(clone_element(correspondence))
        representation_map.append(
            processing_instruction.to_xml(
                "ProcessingInstructionReference", namespace=REUSABLE_NS
            )
        )
        self.representation_maps.append(representation_map)
        return representation_map

    @staticmethod
    def correspondence(
        *,
        commonality: str | None = None,
        difference: str | None = None,
        weight: float | None = None,
        lang: str = "en",
    ) -> Element:
        """Build a ``Correspondence`` element describing how items relate.

        ``commonality`` and ``difference`` are human-readable descriptions;
        ``weight`` is a 0.0-1.0 measure of commonality. Pass the result to a map
        builder's ``correspondence=`` argument.
        """
        element = create_element(qn(COMPARATIVE_NS, "Correspondence"))
        if commonality is not None:
            commonality_el = create_element(qn(COMPARATIVE_NS, "Commonality"))
            commonality_el.append(
                InternationalString(
                    text=commonality, lang=lang, child_tag="Content", is_plain_text=True
                ).to_child("Content")
            )
            element.append(commonality_el)
        if difference is not None:
            difference_el = create_element(qn(REUSABLE_NS, "Difference"))
            difference_el.append(
                InternationalString(
                    text=difference, lang=lang, child_tag="Content", is_plain_text=True
                ).to_child("Content")
            )
            element.append(difference_el)
        if weight is not None:
            weight_el = create_element(qn(COMPARATIVE_NS, "CommonalityWeight"))
            weight_el.text = str(weight)
            element.append(weight_el)
        return element
