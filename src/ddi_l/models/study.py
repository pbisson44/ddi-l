"""StudyUnit wrappers combining the other module abstractions."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from .._etree import Element, create_element
from ..constants import (
    ARCHIVE_NS,
    CONCEPTUAL_COMPONENT_NS,
    DATA_COLLECTION_NS,
    DATASET_NS,
    LOGICAL_PRODUCT_NS,
    PHYSICAL_DATA_PRODUCT_NS,
    PHYSICAL_INSTANCE_NS,
    REUSABLE_NS,
    STUDY_UNIT_NS,
)
from ..exceptions import DDIReferenceWarning, ModelValidationError
from ..namespaces import build_namespace_map
from ._generated.studyunit import StudyUnitFields
from .archive import Archive
from .base import (
    CodeValue,
    InternationalString,
    MaintainableBase,
    Reference,
    UserAttributePair,
    UserID,
    VersionRationale,
    clone_element,
    qn,
    should_validate_on_serialize,
    warn_at_caller,
)
from .concept import Concept, Universe
from .conceptualcomponent import ConceptualComponent
from .datacollection import DataCollection, QuestionMaintainableBase
from .dataset import DataSet
from .logicalproduct import LogicalProduct, Variable
from .physical import PhysicalInstance, PhysicalStructure, RecordLayout

if TYPE_CHECKING:
    from ..maintainable_registry import MaintainableRegistry


def _references_from_elements(elements: list[Element]) -> list[Reference]:
    """Extract reusable ``Reference`` objects from ``elements``."""
    references: list[Reference] = []
    for element in elements:
        local_name = element.tag.split("}")[-1]
        if local_name.endswith("Reference"):
            references.append(Reference.from_xml(element))
    return references


def _should_use_default_namespace(element: Element) -> bool:
    """Determine whether ``element`` used the default study unit namespace."""
    default_binding = (
        getattr(element, "nsmap", {}).get(None) if hasattr(element, "nsmap") else None
    )
    prefix = getattr(element, "prefix", None)
    return prefix in (None, "") and default_binding == STUDY_UNIT_NS


__all__ = ["StudyUnit"]


def _append_wrapper_label(element: Element, text: str) -> None:
    """Label a wrapper element that serialization creates on the study's behalf."""
    label = create_element(qn(REUSABLE_NS, "Label"))
    label.append(InternationalString(text=text, lang="en").to_child("Content"))
    element.append(label)


@dataclass
class StudyUnit(StudyUnitFields):
    """Representation of ``s:StudyUnit`` maintainables in DDI 3.3.

    The main attributes mirror the ``StudyUnit`` structure in the Study Unit
    schema and expose a Pythonic view over the nested module content:

    * ``data_collections`` aggregates inline ``d:DataCollection`` entries while
      ``data_collection_references`` retains ``r:DataCollectionReference``
      pointers for external fragments.
    * ``logical_products`` and ``physical_structures`` model ``l:LogicalProduct``
      and ``p:PhysicalStructure`` children respectively, including the
      ``PhysicalStructure`` instances discovered inside nested
      ``p:PhysicalDataProduct`` schemes.
    * ``conceptual_components`` provides access to ``c:ConceptualComponent``
      children, synthesising ad-hoc containers when only inline ``Concept`` or
      ``Universe`` elements are present.
    * ``archives`` keeps ``a:Archive`` children, ``citations`` retains raw
      ``r:Citation`` elements, and ``abstracts``/``purposes`` expose the
      corresponding reusable international string containers.
    * ``user_ids``, ``user_attribute_pairs``, ``version_responsibility`` and
      ``version_rationales`` surface the reusable versioning metadata, while
      ``required_resource_packages`` and ``funding_information`` store the raw
      ``r:RequiredResourcePackages`` and ``r:FundingInformation`` nodes so that
      custom extensions are not lost.
    * ``physical_instance_references`` and ``universe_references`` mirror the
      ``r:PhysicalInstanceReference`` and ``r:UniverseReference`` leaf nodes.

    Parsing a minimal ``StudyUnit`` with an inline ``DataCollection``::

        >>> from ddi_l.constants import DATA_COLLECTION_NS, STUDY_UNIT_NS
        >>> from ddi_l.models.base import build_identification_elements, qn
        >>> from ddi_l._etree import create_element
        >>> study_el = create_element(
        ...     qn(STUDY_UNIT_NS, "StudyUnit")
        ... )
        >>> id_els = build_identification_elements(
        ...     agency="org", identifier="study", version="1"
        ... )
        >>> for node in id_els:
        ...     study_el.append(node)
        >>> dc_el = create_element(
        ...     qn(DATA_COLLECTION_NS, "DataCollection")
        ... )
        >>> id_els = build_identification_elements(
        ...     agency="org", identifier="dc", version="1"
        ... )
        >>> for node in id_els:
        ...     dc_el.append(node)
        >>> study_el.append(dc_el)
        >>> study = StudyUnit.from_xml(study_el)
        >>> [dc.identifier for dc in study.data_collections]
        ['dc']
    """

    type_of_study_unit: CodeValue | None = None
    data_collections: list[DataCollection] = field(default_factory=list)  # type: ignore[assignment]
    logical_products: list[LogicalProduct] = field(default_factory=list)
    physical_structures: list[PhysicalStructure] = field(default_factory=list)
    record_layouts: list[RecordLayout] = field(default_factory=list)
    datasets: list[DataSet] = field(default_factory=list)
    physical_instances: list[PhysicalInstance] = field(  # type: ignore[assignment]
        default_factory=list
    )
    archives: list[Archive] = field(default_factory=list)  # type: ignore[assignment]
    conceptual_components: list[ConceptualComponent] = field(default_factory=list)  # type: ignore[assignment]
    user_ids: list[UserID] = field(default_factory=list)
    user_attribute_pairs: list[UserAttributePair] = field(default_factory=list)
    version_responsibility: str | None = None
    version_rationales: list[VersionRationale] = field(default_factory=list)
    citations: list[Element] = field(default_factory=list)
    abstracts: list[InternationalString] = field(default_factory=list)
    authorization_sources: list[Element] = field(default_factory=list)
    series_statements: list[Element] = field(default_factory=list)
    quality_statement_references: list[Reference] = field(default_factory=list)
    quality_scheme_references: list[Reference] = field(default_factory=list)
    purposes: list[InternationalString] = field(default_factory=list)
    coverage: list[Element] = field(default_factory=list)  # type: ignore[assignment]
    analysis_units: list[CodeValue] = field(default_factory=list)
    kind_of_data: list[Element] = field(default_factory=list)
    general_data_formats: list[CodeValue] = field(default_factory=list)
    funding_information: list[Element] = field(default_factory=list)
    embargos: list[Element] = field(default_factory=list)
    required_resource_packages: list[Element] = field(default_factory=list)  # type: ignore[assignment]
    data_collection_references: list[Reference] = field(default_factory=list)
    logical_product_references: list[Reference] = field(default_factory=list)
    physical_data_product_references: list[Reference] = field(default_factory=list)
    physical_instance_references: list[Reference] = field(default_factory=list)
    archive_references: list[Reference] = field(default_factory=list)
    conceptual_component_references: list[Reference] = field(default_factory=list)
    universe_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(STUDY_UNIT_NS, "StudyUnit")
    NSMAP: ClassVar[dict[str | None, str]] = build_namespace_map(
        "a", "c", "d", "l", "p", "r", "s"
    )
    _use_default_namespace: bool = field(
        default=False, init=False, repr=False, compare=False
    )

    def validate(self) -> None:
        super().validate()
        has_data_collections = bool(self.data_collections)
        has_data_collection_references = bool(self.data_collection_references)
        if not (has_data_collections or has_data_collection_references):
            raise ModelValidationError(
                "StudyUnit requires at least one DataCollection"
                " or DataCollectionReference before serialization."
            )
        self._assert_unique_children(
            self.data_collections, child_label="DataCollection"
        )
        self._assert_unique_children(
            self.logical_products, child_label="LogicalProduct"
        )
        self._assert_unique_children(
            self.physical_structures, child_label="PhysicalStructure"
        )
        self._assert_unique_children(self.archives, child_label="Archive")
        self._assert_unique_children(
            self.conceptual_components, child_label="ConceptualComponent"
        )

    @classmethod
    def from_xml(cls, element: Element) -> StudyUnit:
        recognized = {
            qn(STUDY_UNIT_NS, "TypeOfStudyUnit"),
            qn(DATA_COLLECTION_NS, "DataCollection"),
            qn(LOGICAL_PRODUCT_NS, "LogicalProduct"),
            qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructure"),
            qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProduct"),
            qn(PHYSICAL_INSTANCE_NS, "PhysicalInstance"),
            qn(ARCHIVE_NS, "Archive"),
            qn(CONCEPTUAL_COMPONENT_NS, "ConceptualComponent"),
            qn(CONCEPTUAL_COMPONENT_NS, "Concept"),
            qn(CONCEPTUAL_COMPONENT_NS, "Universe"),
            qn(REUSABLE_NS, "UserID"),
            qn(REUSABLE_NS, "UserAttributePair"),
            qn(REUSABLE_NS, "VersionResponsibility"),
            qn(REUSABLE_NS, "VersionRationale"),
            qn(REUSABLE_NS, "Citation"),
            qn(REUSABLE_NS, "Abstract"),
            qn(REUSABLE_NS, "AuthorizationSource"),
            qn(REUSABLE_NS, "SeriesStatement"),
            qn(REUSABLE_NS, "QualityStatementReference"),
            qn(REUSABLE_NS, "QualitySchemeReference"),
            qn(REUSABLE_NS, "Purpose"),
            qn(REUSABLE_NS, "Coverage"),
            qn(REUSABLE_NS, "AnalysisUnit"),
            qn(REUSABLE_NS, "KindOfData"),
            qn(REUSABLE_NS, "GeneralDataFormat"),
            qn(REUSABLE_NS, "FundingInformation"),
            qn(REUSABLE_NS, "Embargo"),
            qn(REUSABLE_NS, "RequiredResourcePackages"),
            qn(REUSABLE_NS, "DataCollectionReference"),
            qn(REUSABLE_NS, "LogicalProductReference"),
            qn(REUSABLE_NS, "PhysicalDataProductReference"),
            qn(REUSABLE_NS, "PhysicalInstanceReference"),
            qn(REUSABLE_NS, "ArchiveReference"),
            qn(REUSABLE_NS, "ConceptualComponentReference"),
            qn(REUSABLE_NS, "UniverseReference"),
        }
        data_collections = [
            DataCollection.from_xml(child)
            for child in element.findall(qn(DATA_COLLECTION_NS, "DataCollection"))
        ]
        logical_products = [
            LogicalProduct.from_xml(child)
            for child in element.findall(qn(LOGICAL_PRODUCT_NS, "LogicalProduct"))
        ]
        physical_structures: list[PhysicalStructure] = []
        record_layouts: list[RecordLayout] = []
        datasets: list[DataSet] = []
        for child in element.findall(qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructure")):
            physical_structures.append(PhysicalStructure.from_xml(child))
        for product in element.findall(
            qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProduct")
        ):
            for scheme in product.findall(
                qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureScheme")
            ):
                for structure in scheme.findall(
                    qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructure")
                ):
                    physical_structures.append(PhysicalStructure.from_xml(structure))
            for layout_scheme in product.findall(
                qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutScheme")
            ):
                for layout in layout_scheme.findall(
                    qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayout")
                ):
                    record_layouts.append(RecordLayout.from_xml(layout))
                for dataset in layout_scheme.findall(qn(DATASET_NS, "DataSet")):
                    datasets.append(DataSet.from_xml(dataset))
        physical_instances = [
            PhysicalInstance.from_xml(child)
            for child in element.findall(qn(PHYSICAL_INSTANCE_NS, "PhysicalInstance"))
        ]
        archives = [
            Archive.from_xml(child)
            for child in element.findall(qn(ARCHIVE_NS, "Archive"))
        ]
        conceptual_components = [
            ConceptualComponent.from_xml(child)
            for child in element.findall(
                qn(CONCEPTUAL_COMPONENT_NS, "ConceptualComponent")
            )
        ]
        if not conceptual_components:
            concepts = [
                Concept.from_xml(child)
                for child in element.findall(qn(CONCEPTUAL_COMPONENT_NS, "Concept"))
            ]
            universes = [
                Universe.from_xml(child)
                for child in element.findall(qn(CONCEPTUAL_COMPONENT_NS, "Universe"))
            ]
            if concepts or universes:
                conceptual_components = [
                    ConceptualComponent(
                        concepts=concepts,
                        universes=universes,
                        inline_only=True,
                    )
                ]
        user_ids = [
            UserID.from_xml(node) for node in element.findall(qn(REUSABLE_NS, "UserID"))
        ]
        user_attribute_pairs = [
            UserAttributePair.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "UserAttributePair"))
        ]
        version_responsibility_el = element.find(
            qn(REUSABLE_NS, "VersionResponsibility")
        )
        version_rationales = [
            VersionRationale.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "VersionRationale"))
        ]
        type_of_study_el = element.find(qn(STUDY_UNIT_NS, "TypeOfStudyUnit"))
        type_of_study_unit = (
            CodeValue.from_xml(type_of_study_el)
            if type_of_study_el is not None
            else None
        )
        citations = [
            clone_element(node) for node in element.findall(qn(REUSABLE_NS, "Citation"))
        ]
        abstracts: list[InternationalString] = []
        for container in element.findall(qn(REUSABLE_NS, "Abstract")):
            abstracts.extend(InternationalString.from_container(container))
        authorization_sources = [
            clone_element(node)
            for node in element.findall(qn(REUSABLE_NS, "AuthorizationSource"))
        ]
        series_statements = [
            clone_element(node)
            for node in element.findall(qn(REUSABLE_NS, "SeriesStatement"))
        ]
        quality_statement_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "QualityStatementReference"))
        ]
        quality_scheme_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "QualitySchemeReference"))
        ]
        purposes: list[InternationalString] = []
        for container in element.findall(qn(REUSABLE_NS, "Purpose")):
            purposes.extend(InternationalString.from_container(container))
        coverage = [
            clone_element(node) for node in element.findall(qn(REUSABLE_NS, "Coverage"))
        ]
        analysis_units = [
            CodeValue.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "AnalysisUnit"))
        ]
        kind_of_data = [
            clone_element(node)
            for node in element.findall(qn(REUSABLE_NS, "KindOfData"))
        ]
        general_data_formats = [
            CodeValue.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "GeneralDataFormat"))
        ]
        funding_information = [
            clone_element(node)
            for node in element.findall(qn(REUSABLE_NS, "FundingInformation"))
        ]
        embargos = [
            clone_element(node) for node in element.findall(qn(REUSABLE_NS, "Embargo"))
        ]
        required_resource_packages = [
            clone_element(node)
            for node in element.findall(qn(REUSABLE_NS, "RequiredResourcePackages"))
        ]
        data_collection_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "DataCollectionReference"))
        ]
        logical_product_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "LogicalProductReference"))
        ]
        physical_data_product_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "PhysicalDataProductReference"))
        ]
        physical_instance_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "PhysicalInstanceReference"))
        ]
        archive_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "ArchiveReference"))
        ]
        conceptual_component_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "ConceptualComponentReference"))
        ]
        universe_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "UniverseReference"))
        ]
        data = cls._collect_common(element, recognized_children=recognized)
        instance = cls(  # type: ignore[misc]
            type_of_study_unit=type_of_study_unit,
            data_collections=data_collections,
            logical_products=logical_products,
            physical_structures=physical_structures,
            record_layouts=record_layouts,
            datasets=datasets,
            physical_instances=physical_instances,
            archives=archives,
            conceptual_components=conceptual_components,
            user_ids=user_ids,
            user_attribute_pairs=user_attribute_pairs,
            version_responsibility=version_responsibility_el.text
            if version_responsibility_el is not None
            else None,
            version_rationales=version_rationales,
            citations=citations,
            abstracts=abstracts,
            authorization_sources=authorization_sources,
            series_statements=series_statements,
            quality_statement_references=quality_statement_references,
            quality_scheme_references=quality_scheme_references,
            purposes=purposes,
            coverage=coverage,
            analysis_units=analysis_units,
            kind_of_data=kind_of_data,
            general_data_formats=general_data_formats,
            funding_information=funding_information,
            embargos=embargos,
            required_resource_packages=required_resource_packages,
            data_collection_references=data_collection_references,
            logical_product_references=logical_product_references,
            physical_data_product_references=physical_data_product_references,
            physical_instance_references=physical_instance_references,
            archive_references=archive_references,
            conceptual_component_references=conceptual_component_references,
            universe_references=universe_references,
            **data,
        )

        instance._use_default_namespace = _should_use_default_namespace(element)
        return instance

    def _nsmap(self) -> dict[str | None, str]:  # type: ignore[misc, unused-ignore]
        if self._nsmap_override is not None:
            override = super()._nsmap() or {}  # type: ignore[misc]
            return dict(override)

        base_map = super()._nsmap() or {}  # type: ignore[misc]
        nsmap = dict(base_map)
        if self._use_default_namespace:
            nsmap.pop("s", None)
            nsmap[None] = STUDY_UNIT_NS
        return nsmap

    def to_xml(self, *, validate_refs: bool = True) -> Element:
        """Serialize to XML, optionally validating cross-references first.

        When ``validate_refs`` is ``True`` every :class:`Reference` in the
        study is checked against the objects the study contains, and one
        :class:`~ddi_l.exceptions.DDIReferenceWarning` lists any that cannot
        be resolved.

        Args:
            validate_refs: Whether to check cross-references first.

        Returns:
            XML Element representation.
        """
        if should_validate_on_serialize(self):
            self.validate()

        if validate_refs:
            unresolved = self.validate_tree()
            if unresolved:
                warn_at_caller(DDIReferenceWarning(unresolved))

        element = self._build_base_element()
        with self._labels_last(element):
            for user_id in self.user_ids:
                element.append(user_id.to_xml())
            for pair in self.user_attribute_pairs:
                element.append(pair.to_xml())
            if self.version_responsibility:
                responsibility_el = create_element(
                    qn(REUSABLE_NS, "VersionResponsibility")
                )
                responsibility_el.text = self.version_responsibility
                element.append(responsibility_el)
            for rationale in self.version_rationales:
                element.append(rationale.to_xml())
        if self.type_of_study_unit is not None:
            element.append(
                self.type_of_study_unit.to_xml(
                    "TypeOfStudyUnit", namespace=STUDY_UNIT_NS
                )
            )
        for citation in self.citations:
            element.append(clone_element(citation))
        if self.abstracts:
            abstract_el = create_element(qn(REUSABLE_NS, "Abstract"))
            for value in self.abstracts:
                abstract_el.append(value.to_child())
            element.append(abstract_el)
        for auth in self.authorization_sources:
            element.append(clone_element(auth))
        for series in self.series_statements:
            element.append(clone_element(series))
        for ref in self.quality_statement_references:
            element.append(ref.to_xml("QualityStatementReference"))
        for ref in self.quality_scheme_references:
            element.append(ref.to_xml("QualitySchemeReference"))
        for reference in self.universe_references:
            element.append(reference.to_xml("UniverseReference"))
        for info in self.funding_information:
            element.append(clone_element(info))
        if self.purposes:
            purpose_el = create_element(qn(REUSABLE_NS, "Purpose"))
            for value in self.purposes:
                purpose_el.append(value.to_child())
            element.append(purpose_el)
        for coverage_el in self.coverage:
            element.append(clone_element(coverage_el))
        for unit in self.analysis_units:
            element.append(unit.to_xml("AnalysisUnit", namespace=REUSABLE_NS))
        for kind in self.kind_of_data:
            element.append(clone_element(kind))
        for fmt in self.general_data_formats:
            element.append(fmt.to_xml("GeneralDataFormat", namespace=REUSABLE_NS))
        for embargo in self.embargos:
            element.append(clone_element(embargo))
        for required in self.required_resource_packages:
            element.append(clone_element(required))
        for ref in self.conceptual_component_references:
            element.append(ref.to_xml("ConceptualComponentReference"))
        for reference in self.data_collection_references:
            element.append(reference.to_xml("DataCollectionReference"))
        for ref in self.logical_product_references:
            element.append(ref.to_xml("LogicalProductReference"))
        for ref in self.physical_data_product_references:
            element.append(ref.to_xml("PhysicalDataProductReference"))
        for reference in self.physical_instance_references:
            element.append(reference.to_xml("PhysicalInstanceReference"))
        for ref in self.archive_references:
            element.append(ref.to_xml("ArchiveReference"))
        for component in self.conceptual_components:
            if component.inline_only:
                component.append_inline_children(element)
            else:
                element.append(component.to_xml())
        for data_collection in self.data_collections:
            element.append(data_collection.to_xml())
        for logical_product in self.logical_products:
            element.append(logical_product.to_xml())
        # Label only wrappers for studies authored through the Document facade;
        # parsed studies round-trip without added content.
        label_wrappers = getattr(self, "_label_generated_wrappers", False)
        for index, physical_structure in enumerate(self.physical_structures, start=1):
            product_el = create_element(
                qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProduct")
            )
            suffix = f"pdp-{index}"
            physical_structure._append_child_identification(product_el, suffix=suffix)
            if label_wrappers:
                _append_wrapper_label(product_el, "Physical data product")

            scheme_el = create_element(
                qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalStructureScheme")
            )
            physical_structure._append_child_identification(
                scheme_el, suffix=f"scheme-{index}"
            )
            if label_wrappers:
                _append_wrapper_label(scheme_el, "Physical structure scheme")
            scheme_el.append(physical_structure.to_xml())

            product_el.append(scheme_el)
            element.append(product_el)
        if self.record_layouts or self.datasets:
            layout_product_el = create_element(
                qn(PHYSICAL_DATA_PRODUCT_NS, "PhysicalDataProduct")
            )
            self._append_child_identification(
                layout_product_el, suffix="pdp-record-layouts"
            )
            if label_wrappers:
                _append_wrapper_label(layout_product_el, "Physical data product")
            layout_scheme_el = create_element(
                qn(PHYSICAL_DATA_PRODUCT_NS, "RecordLayoutScheme")
            )
            self._append_child_identification(
                layout_scheme_el, suffix="record-layout-scheme"
            )
            if label_wrappers:
                _append_wrapper_label(layout_scheme_el, "Record layout scheme")
            for layout in self.record_layouts:
                layout_scheme_el.append(layout.to_xml())
            for dataset in self.datasets:
                layout_scheme_el.append(dataset.to_xml())
            layout_product_el.append(layout_scheme_el)
            element.append(layout_product_el)
        for physical_instance in self.physical_instances:
            element.append(physical_instance.to_xml())
        for archive in self.archives:
            element.append(archive.to_xml())
        self._append_other_elements(element)
        return element

    def iter_variables(
        self,
        *,
        identifier: str | None = None,
        urn: str | None = None,
        scheme_identifier: str | None = None,
        scheme_urn: str | None = None,
    ) -> Iterator[Variable]:
        """Yield variables from any inline logical products.

        Args:
            identifier: Optional variable identifier filter.
            urn: Optional URN filter.
            scheme_identifier: Optional variable scheme identifier filter.
            scheme_urn: Optional variable scheme URN filter.
        """
        for product in self.logical_products:
            yield from product.iter_variables(
                identifier=identifier,
                urn=urn,
                scheme_identifier=scheme_identifier,
                scheme_urn=scheme_urn,
            )

    def iter_data_collections(
        self,
        *,
        identifier: str | None = None,
        urn: str | None = None,
    ) -> Iterator[DataCollection]:
        """Stream data-collection maintainables embedded in the study."""
        for data_collection in self.data_collections:
            if identifier is not None and data_collection.identifier != identifier:
                continue
            if urn is not None and data_collection.urn != urn:
                continue
            yield data_collection

    def get_dataset(self, identifier: str) -> PhysicalStructure | None:
        """Return the physical structure for ``identifier`` when present."""
        for structure in self.physical_structures:
            if structure.identifier == identifier:
                return structure
        return None

    def get_variables(
        self,
        *,
        resolver: MaintainableRegistry | None = None,
    ) -> list[Variable]:
        """Return variables defined inline or referenced by the study."""
        from ..maintainable_registry import (
            MaintainableResolver,
            ResolveIdentifier,
        )
        from ..maintainable_registry import (
            resolve as resolve_maintainable,
        )

        resolve_fn: MaintainableResolver
        resolve_fn = resolve_maintainable if resolver is None else resolver.resolve

        def _resolve(target: ResolveIdentifier) -> MaintainableBase | None:
            return resolve_fn(target)

        results: list[Variable] = []
        seen: set[object] = set()

        def _add(candidate: MaintainableBase | None) -> None:
            if candidate is None or not isinstance(candidate, Variable):
                return
            identity: object = candidate._format_urn() or (
                candidate.agency,
                candidate.identifier,
                candidate.version,
            )
            if identity is None:
                identity = id(candidate)
            if identity in seen:
                return
            seen.add(identity)
            results.append(candidate)

        for logical_product in self.logical_products:
            for variable in logical_product.iter_variables():
                _add(variable)
            for reference in _references_from_elements(logical_product.other_elements):
                _add(_resolve(reference))

        return results

    def get_questions(
        self,
        *,
        resolver: MaintainableRegistry | None = None,
    ) -> list[QuestionMaintainableBase]:
        """Return questions from inline and referenced data collections."""
        from ..maintainable_registry import (
            MaintainableResolver,
            ResolveIdentifier,
        )
        from ..maintainable_registry import (
            resolve as resolve_maintainable,
        )

        resolve_fn: MaintainableResolver
        resolve_fn = resolve_maintainable if resolver is None else resolver.resolve

        def _resolve(target: ResolveIdentifier) -> MaintainableBase | None:
            return resolve_fn(target)

        results: list[QuestionMaintainableBase] = []
        seen: set[object] = set()

        def _add(candidate: QuestionMaintainableBase | None) -> None:
            if candidate is None:
                return
            identity: object = candidate._format_urn() or (
                candidate.agency,
                candidate.identifier,
                candidate.version,
            )
            if identity is None:
                identity = id(candidate)
            if identity in seen:
                return
            seen.add(identity)
            results.append(candidate)

        for collection in self.data_collections:
            for question in collection.get_questions(resolver=resolver):
                _add(question)

        for reference in self.data_collection_references:
            resolved = _resolve(reference)
            if isinstance(resolved, DataCollection):
                for question in resolved.get_questions(resolver=resolver):
                    _add(question)

        return results

    def get_datasets(
        self,
        *,
        resolver: MaintainableRegistry | None = None,
    ) -> list[MaintainableBase]:
        """Return physical and derived datasets linked to the study."""
        from ..maintainable_registry import (
            MaintainableResolver,
            ResolveIdentifier,
        )
        from ..maintainable_registry import (
            resolve as resolve_maintainable,
        )

        resolve_fn: MaintainableResolver
        resolve_fn = resolve_maintainable if resolver is None else resolver.resolve

        def _resolve(target: ResolveIdentifier) -> MaintainableBase | None:
            return resolve_fn(target)

        results: list[MaintainableBase] = []
        seen: set[object] = set()

        def _is_dataset(candidate: MaintainableBase) -> bool:
            if isinstance(candidate, PhysicalStructure):
                return True
            module = candidate.__class__.__module__
            if module.endswith(".physical"):
                return True
            return "dataset" in candidate.__class__.__name__.lower()

        def _add(candidate: MaintainableBase | None) -> None:
            if candidate is None or not _is_dataset(candidate):
                return
            identity: object = candidate._format_urn() or (
                candidate.agency,
                candidate.identifier,
                candidate.version,
            )
            if identity is None:
                identity = id(candidate)
            if identity in seen:
                return
            seen.add(identity)
            results.append(candidate)

        for structure in self.physical_structures:
            _add(structure)

        for reference in self.physical_instance_references:
            _add(_resolve(reference))

        for logical_product in self.logical_products:
            for dataset in logical_product.iter_derived_datasets():
                _add(dataset)
            for reference in _references_from_elements(logical_product.other_elements):
                _add(_resolve(reference))

        return results
