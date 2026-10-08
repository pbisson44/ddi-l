"""Utilities for indexing maintainable DDI content and resolving references."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
)

from .constants import REUSABLE_NS
from .exceptions import DDIReferenceError
from .maintainable_registry import maintainable_type_from_name
from .models.base import MaintainableBase, Reference, qn
from .models.concept import Concept, ConceptualVariable, UnitType, Universe
from .models.conceptualcomponent import ConceptualComponent
from .models.datacollection import DataCollection, Instrument, QuestionItem
from .models.logicalproduct import CodeList, LogicalProduct, Variable
from .models.study import StudyUnit

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from .document import DDIDocument

Maintainable = TypeVar("Maintainable", bound=MaintainableBase)


@dataclass(frozen=True)
class ResourceMetadata:
    """Cached identification details for maintainable resources."""

    urn: str | None
    key: tuple[str | None, str, str | None] | None


class ResourceCollection(Generic[Maintainable]):
    """Container tracking maintainable resources and their identifiers."""

    def __init__(self) -> None:
        """Initialize empty lookup tables for maintainable resources."""
        self.by_urn: dict[str, Maintainable] = {}
        self.by_identifier: dict[tuple[str | None, str, str | None], Maintainable] = {}
        self.by_identifier_only: dict[str, list[Maintainable]] = {}
        self.by_identifier_version: dict[
            tuple[str, str | None], list[Maintainable]
        ] = {}
        self.items: list[Maintainable] = []
        self.metadata: dict[int, ResourceMetadata] = {}

    def add(self, resource: Maintainable) -> ResourceMetadata:
        """Add a maintainable resource to the collection.

        The resource is registered under its URN and identifier tuple, if
        available. Side effects include mutating the internal lookup tables
        ``by_urn`` and ``by_identifier`` as well as the ordered ``items`` list
        that preserves registration order.

        Args:
            resource: Maintainable object being tracked.

        Returns:
            Cached metadata describing the resource's URN and identifier tuple.

        Raises:
            ValueError: If another resource with the same URN or identifier tuple
                is already registered.
        """
        resource_id = id(resource)
        existing_metadata = self.metadata.get(resource_id)
        if existing_metadata is not None:
            return existing_metadata

        urn = _extract_urn(resource)
        key: tuple[str | None, str, str | None] | None = None
        if resource.identifier:
            key = (resource.agency, resource.identifier, resource.version)

        if urn is not None:
            existing = self.by_urn.get(urn)
            if existing is not None and existing is not resource:
                raise ValueError(
                    f"Duplicate URN {urn!r} detected for {type(resource).__name__}."
                )
            self.by_urn[urn] = resource

        if key is not None:
            existing = self.by_identifier.get(key)
            if existing is not None and existing is not resource:
                raise ValueError(
                    f"Duplicate identifier tuple {key!r} detected "
                    f"for {type(resource).__name__}."
                )
            self.by_identifier[key] = resource
            identifier_only_bucket = self.by_identifier_only.setdefault(key[1], [])
            identifier_only_bucket.append(resource)
            identifier_version_bucket = self.by_identifier_version.setdefault(
                (key[1], key[2]), []
            )
            identifier_version_bucket.append(resource)

        metadata = ResourceMetadata(urn=urn, key=key)
        self.metadata[resource_id] = metadata
        self.items.append(resource)
        return metadata

    def __iter__(self) -> Iterator[Maintainable]:
        """Iterate over the registered resources in insertion order."""
        return iter(self.items)

    def iter_identifier_matches(self, identifier: str) -> Iterable[Maintainable]:
        """Yield resources registered under a specific identifier."""
        return tuple(self.by_identifier_only.get(identifier, ()))

    def iter_identifier_version_matches(
        self, identifier: str, version: str | None
    ) -> Iterable[Maintainable]:
        """Yield resources registered for an identifier/version pair."""
        key = (identifier, version)
        return tuple(self.by_identifier_version.get(key, ()))


def _extract_urn(resource: MaintainableBase) -> str | None:
    """Retrieve the URN for a maintainable resource.

    Args:
        resource: Resource whose URN should be obtained.

    Returns:
        The URN string if it can be found either on the resource or within its
        ``other_elements`` payload; otherwise ``None``.
    """
    if resource.urn:
        return resource.urn
    for element in resource.other_elements:
        if element.tag == qn(REUSABLE_NS, "URN"):
            return element.text or None
    return None


def _reference_key(
    reference: Reference,
) -> tuple[str | None, str, str | None] | None:
    """Construct the lookup key tuple for a reference.

    Args:
        reference: The reference whose identifier tuple should be normalised.

    Returns:
        A tuple ``(agency, identifier, version)`` when the reference contains an
        identifier, otherwise ``None`` when insufficient data is present for
        identifier-based lookup.
    """
    if reference.identifier is None:
        return None
    return (reference.agency, reference.identifier, reference.version)


class Index:
    """Resolver over the maintainable content contained in one or more documents."""

    _SPECIALIZED_REGISTRARS: tuple[tuple[type[MaintainableBase], str], ...] = (
        (StudyUnit, "_register_study_unit"),
        (LogicalProduct, "_register_logical_product"),
        (DataCollection, "_register_data_collection"),
        (ConceptualComponent, "_register_conceptual_component"),
    )

    def __init__(self) -> None:
        """Create an empty index for maintainable resources."""
        self._collections: dict[type[MaintainableBase], ResourceCollection] = {}
        self._resource_metadata: dict[int, ResourceMetadata] = {}
        self._question_backlinks: dict[int, list[Variable]] = {}

    @classmethod
    def maintainable_classes(cls) -> tuple[type[MaintainableBase], ...]:
        """Return the maintainable classes currently registered with the base."""
        return MaintainableBase.maintainable_types()

    @classmethod
    def from_document(cls, document: DDIDocument) -> Index:
        """Build an index from a full DDI document.

        Args:
            document: Document whose contents will be registered.

        Returns:
            A populated :class:`Index` containing all maintainables from the
            document.
        """
        index = cls()
        index.add_document(document)
        return index

    def add_document(self, document: DDIDocument) -> None:
        """Register every maintainable resource contained in a document.

        Side effects include mutating the internal collections and rebuilding
        variable-to-question backlink caches.

        Args:
            document: Document to traverse for maintainables.
        """
        for study in document.iter_study_units():
            self._register_study_unit(study)
        self._rebuild_backlinks()

    def register_fragment(self, *resources: MaintainableBase) -> None:
        """Register maintainable resources or trees of resources.

        Args:
            *resources: Individual maintainables or iterables containing
                maintainables. Nested hierarchies are recursively registered.

        Raises:
            TypeError: If an unsupported maintainable type is encountered.
        """
        for resource in resources:
            if isinstance(resource, (list, tuple, set)):
                for item in resource:
                    self._register_tree(item)
            else:
                self._register_tree(resource)
        self._rebuild_backlinks()

    def resolve(
        self,
        reference: Reference,
        *,
        expected_type: type[MaintainableBase] | None = None,
    ) -> MaintainableBase:
        """Resolve a reference to its maintainable instance.

        Args:
            reference: Identification data of the maintainable resource.
            expected_type: Optional class restricting the search to a single
                maintainable type.

        Returns:
            The unique maintainable that satisfies the reference.

        Raises:
            LookupError: If the reference cannot be resolved or if multiple
                candidates are found across the registered collections.
        """
        classes: list[type[MaintainableBase]]
        if expected_type is not None:
            classes = [expected_type]
        elif reference.type_of_object:
            classes = [self._class_for_type(reference.type_of_object)]
        else:
            classes = list(self._collections.keys())

        matches: list[MaintainableBase] = []
        for cls in classes:
            collection = self._collections.get(cls)
            if not collection:
                continue
            result = self._resolve_in_collection(reference, collection)
            if result is not None:
                matches.append(result)
        if not matches:
            raise DDIReferenceError.unresolved(
                urn=getattr(reference, "urn", None),
                identifier=getattr(reference, "identifier", None),
                type_of_object=getattr(reference, "type_of_object", None),
            )
        if len(matches) > 1:
            raise DDIReferenceError(
                "Reference is ambiguous across registered resources."
            )
        return matches[0]

    def get_variable(
        self,
        identifier: str,
        *,
        agency: str | None = None,
        version: str | None = None,
    ) -> Variable:
        """Resolve and return a variable by identifier components.

        Args:
            identifier: Identifier of the variable to fetch.
            agency: Optional agency identifier to disambiguate matches.
            version: Optional version string for the variable.

        Returns:
            The resolved :class:`Variable` instance.

        Raises:
            LookupError: Propagated from :meth:`resolve` when the variable cannot
                be found.
        """
        reference = Reference(
            type_of_object="Variable",
            agency=agency,
            identifier=identifier,
            version=version,
        )
        result = self.resolve(reference, expected_type=Variable)
        assert isinstance(result, Variable)
        return result

    def find_questions(
        self,
        *,
        using_code_list: CodeList
        | Reference
        | str
        | tuple[str | None, str, str | None]
        | None = None,
    ) -> list[QuestionItem]:
        """Retrieve questions, optionally filtered by the code list they use.

        Args:
            using_code_list: Optional reference information describing the code
                list of interest. Accepts maintainable instances, references,
                URN strings, or identifier tuples.

        Returns:
            A list of questions matching the supplied criteria.

        Raises:
            LookupError: If insufficient information is provided to match a code
                list when filtering.
        """
        collection = self._collections.get(QuestionItem)
        if not collection:
            return []
        if using_code_list is None:
            return list(collection)

        _, metadata = self._normalize_reference_details(using_code_list, CodeList)
        if metadata.urn is None and metadata.key is None:
            raise LookupError("Insufficient identification data to match code lists.")

        matches: list[QuestionItem] = []
        for question in collection:
            if self._question_references_code_list(
                question, metadata.urn, metadata.key
            ):
                matches.append(question)
        return matches

    def get_variables_referencing_question(
        self,
        target: QuestionItem | Reference | str | tuple[str | None, str, str | None],
    ) -> list[Variable]:
        """Return variables that reference a specific question.

        Args:
            target: Question specification as a maintainable, reference, URN, or
                identifier tuple.

        Returns:
            A list of variables that link to the resolved question through the
            cached backlink map.
        """
        question = self._coerce_resource(target, QuestionItem)
        return list(self._question_backlinks.get(id(question), []))

    def iter_resources(self, cls: type[Maintainable]) -> Iterable[Maintainable]:
        """Iterate over registered resources of a particular type.

        Args:
            cls: Maintainable class whose registered instances should be
                returned.

        Returns:
            An iterable of maintainables for the requested type. Returns an
            empty list if none are registered.
        """
        collection = self._collections.get(cls)
        if not collection:
            return []
        return list(collection)

    def _register_tree(self, resource: MaintainableBase) -> None:
        """Register a maintainable resource and its child hierarchy.

        Depending on the resource type, this mutates the internal collections by
        registering the maintainable itself along with any nested maintainables
        reachable from it.

        Args:
            resource: Maintainable root whose descendants should be registered.

        Raises:
            TypeError: If the resource type is unsupported.
        """
        if not isinstance(resource, MaintainableBase):
            raise TypeError(f"Unsupported resource type: {type(resource).__name__}")

        for cls, handler_name in self._SPECIALIZED_REGISTRARS:
            if isinstance(resource, cls):
                handler = getattr(self, handler_name)
                handler(resource)
                return

        maintainable_classes = type(self).maintainable_classes()
        if not isinstance(resource, maintainable_classes):
            raise TypeError(f"Unsupported resource type: {type(resource).__name__}")

        self._register_resource(type(resource), resource)

    def _register_study_unit(self, study: StudyUnit) -> None:
        """Register a study unit and all related maintainables.

        Side effects include recursively populating collections for nested data
        collections, logical products, and conceptual components.
        """
        self._register_resource(StudyUnit, study)
        for data_collection in study.data_collections:
            self._register_data_collection(data_collection)
        for logical_product in study.logical_products:
            self._register_logical_product(logical_product)
        for component in study.conceptual_components:
            self._register_conceptual_component(component)

    def _register_logical_product(self, logical_product: LogicalProduct) -> None:
        """Register a logical product along with its variables and code lists.

        Each nested maintainable is added individually so they can be resolved
        without traversing the logical product tree in future lookups.
        """
        self._register_resource(LogicalProduct, logical_product)
        for code_list in logical_product.code_lists:
            self._register_resource(CodeList, code_list)
        for variable in logical_product.variables:
            self._register_resource(Variable, variable)

    def _register_data_collection(self, data_collection: DataCollection) -> None:
        """Register a data collection including nested questions and instruments.

        This ensures both direct resolution of the data collection and reuse of
        its child maintainables elsewhere in the index.
        """
        self._register_resource(DataCollection, data_collection)
        for question in data_collection.questions:
            self._register_resource(QuestionItem, question)
        for instrument in data_collection.instruments:
            self._register_resource(Instrument, instrument)

    def _register_conceptual_component(self, component: ConceptualComponent) -> None:
        """Register conceptual content including concepts, universes, and units.

        All child maintainables are stored separately for direct lookup.
        """
        self._register_resource(ConceptualComponent, component)
        for concept in component.concepts:
            self._register_resource(Concept, concept)
        for universe in component.universes:
            self._register_resource(Universe, universe)
        for conceptual_variable in component.conceptual_variables:
            self._register_resource(ConceptualVariable, conceptual_variable)
        for unit_type in component.unit_types:
            self._register_resource(UnitType, unit_type)

    def _register_resource(
        self, cls: type[MaintainableBase], resource: MaintainableBase
    ) -> None:
        """Add a resource instance to its class-specific collection.

        Side effects include updating resource metadata caches for quick
        reference normalization.
        """
        collection = self._collections.setdefault(cls, ResourceCollection())
        metadata = collection.add(resource)
        self._resource_metadata[id(resource)] = metadata

    def _rebuild_backlinks(self) -> None:
        """Recompute the cached mapping from questions to referencing variables.

        The existing backlink cache is replaced entirely, so unresolved
        references are dropped while new links are incorporated.
        """
        question_backlinks: dict[int, list[Variable]] = {}
        variable_collection = self._collections.get(Variable)
        question_collection = self._collections.get(QuestionItem)
        if not variable_collection or not question_collection:
            self._question_backlinks = {}
            return

        for variable in variable_collection:
            for reference in variable.question_references:
                question = self._resolve_question_reference(
                    reference, question_collection
                )
                if question is None:
                    continue
                question_backlinks.setdefault(id(question), []).append(variable)
        self._question_backlinks = question_backlinks

    def _resolve_in_collection(
        self, reference: Reference, collection: ResourceCollection[MaintainableBase]
    ) -> MaintainableBase | None:
        """Resolve a reference within a specific resource collection.

        Args:
            reference: Reference object to match against resources.
            collection: Resource collection scoped to a specific maintainable
                class.

        Returns:
            The matching maintainable if found, otherwise ``None``.

        Raises:
            LookupError: If identifier-based matching finds multiple candidates
                within the collection.

        Notes:
            Lookup prefers URNs, then exact identifier tuples, before falling
            back to relaxed identifier matching that tolerates missing agency or
            version information.
        """
        if reference.urn:
            resource = collection.by_urn.get(reference.urn)
            if resource is not None:
                return resource

        if reference.identifier:
            matches: list[MaintainableBase] = []
            key = _reference_key(reference)
            if key is not None:
                resource = collection.by_identifier.get(key)
                if resource is not None:
                    return resource
            identifier = reference.identifier
            if reference.agency is None:
                matches.extend(
                    collection.iter_identifier_version_matches(
                        identifier, reference.version
                    )
                )
            if not matches:
                for candidate in collection.iter_identifier_matches(identifier):
                    if (
                        reference.agency is not None
                        and candidate.agency != reference.agency
                    ):
                        continue
                    if (
                        reference.version is not None
                        and candidate.version != reference.version
                    ):
                        continue
                    matches.append(candidate)
            if len(matches) == 1:
                return matches[0]
            if len(matches) > 1:
                raise LookupError("Reference matches multiple resources in collection.")
        return None

    def _resolve_question_reference(
        self,
        reference: Reference,
        collection: ResourceCollection[QuestionItem],
    ) -> QuestionItem | None:
        """Resolve a question reference using direct collection lookups."""
        if reference.urn:
            question = collection.by_urn.get(reference.urn)
            if question is not None:
                return question

        if not reference.identifier:
            return None

        key = _reference_key(reference)
        if key is not None:
            question = collection.by_identifier.get(key)
            if question is not None:
                return question

        identifier = reference.identifier
        matches: list[QuestionItem] = []

        for candidate in collection.iter_identifier_version_matches(
            identifier, reference.version
        ):
            if reference.agency is not None and candidate.agency != reference.agency:
                continue
            matches.append(candidate)

        if not matches:
            for candidate in collection.iter_identifier_matches(identifier):
                if (
                    reference.version is not None
                    and candidate.version != reference.version
                ):
                    continue
                if (
                    reference.agency is not None
                    and candidate.agency != reference.agency
                ):
                    continue
                matches.append(candidate)

        if len(matches) == 1:
            return matches[0]
        return None

    def _coerce_resource(
        self,
        value: MaintainableBase | Reference | str | tuple[str | None, str, str | None],
        expected_type: type[Maintainable],
    ) -> Maintainable:
        """Resolve arbitrary inputs to a maintainable of ``expected_type``.

        Args:
            value: Maintainable instance, reference, URN string, or identifier
                tuple identifying the resource.
            expected_type: Class that the resolved value must satisfy.

        Returns:
            The resolved maintainable instance.

        Raises:
            ValueError: If identifier tuples are malformed.
            TypeError: If the input type cannot be processed.
            LookupError: Propagated when resolution fails.
        """
        if isinstance(value, expected_type):
            return value
        if isinstance(value, Reference):
            result = self.resolve(value, expected_type=expected_type)
            assert isinstance(result, expected_type)
            return result
        if isinstance(value, str):
            reference = Reference(urn=value, type_of_object=expected_type.__name__)
            result = self.resolve(reference, expected_type=expected_type)
            assert isinstance(result, expected_type)
            return result
        if isinstance(value, tuple):
            if len(value) != 3:
                raise ValueError(
                    "Identifier tuples must be of the form "
                    "(agency, identifier, version)."
                )
            agency, identifier, version = value
            reference = Reference(
                agency=agency,
                identifier=identifier,
                version=version,
                type_of_object=expected_type.__name__,
            )
            result = self.resolve(reference, expected_type=expected_type)
            assert isinstance(result, expected_type)
            return result
        raise TypeError(f"Unsupported reference type: {type(value).__name__}")

    def _normalize_reference_details(
        self,
        value: MaintainableBase | Reference | str | tuple[str | None, str, str | None],
        expected_type: type[MaintainableBase],
    ) -> tuple[MaintainableBase | None, ResourceMetadata]:
        """Return normalized metadata for a maintainable-like input.

        Args:
            value: Maintainable instance, reference, URN, or identifier tuple.
            expected_type: Maintainable class used to scope lookup attempts.

        Returns:
            A tuple of the resolved maintainable (if already registered) and its
            associated metadata. The maintainable component is ``None`` when the
            input is not already registered in the index.

        Raises:
            ValueError: If identifier tuples are malformed.
            TypeError: If the input type cannot be processed.

        Side Effects:
            When the value corresponds to a registered resource lacking cached
            metadata, the method populates ``_resource_metadata`` to avoid future
            recomputation.
        """
        if isinstance(value, expected_type):
            metadata = self._resource_metadata.get(id(value))
            if metadata is None:
                metadata = ResourceMetadata(
                    urn=_extract_urn(value),
                    key=(value.agency, value.identifier, value.version)
                    if value.identifier
                    else None,
                )
            return value, metadata
        if isinstance(value, Reference):
            return None, ResourceMetadata(urn=value.urn, key=_reference_key(value))
        if isinstance(value, str):
            collection = self._collections.get(expected_type)
            if collection is not None:
                resource = collection.by_urn.get(value)
                if resource is not None:
                    resource_id = id(resource)
                    metadata = self._resource_metadata.get(resource_id)
                    if metadata is None:
                        metadata = ResourceMetadata(
                            urn=_extract_urn(resource),
                            key=(resource.agency, resource.identifier, resource.version)
                            if resource.identifier
                            else None,
                        )
                        self._resource_metadata[resource_id] = metadata
                    return None, metadata
            return None, ResourceMetadata(urn=value, key=None)
        if isinstance(value, tuple):
            if len(value) != 3:
                raise ValueError(
                    "Identifier tuples must provide (agency, identifier, version)."
                )
            return None, ResourceMetadata(urn=None, key=value)
        raise TypeError(f"Unsupported reference type: {type(value).__name__}")

    def _question_references_code_list(
        self,
        question: QuestionItem,
        target_urn: str | None,
        target_key: tuple[str | None, str, str | None] | None,
    ) -> bool:
        """Check whether a question references a specific code list.

        The check inspects ``other_elements`` recursively so code list
        references embedded within nested structures are discovered.
        """
        reference_tag = qn(REUSABLE_NS, "CodeListReference")
        for element in question.other_elements:
            for candidate in element.iter():
                if candidate.tag != reference_tag:
                    continue
                reference = Reference.from_xml(candidate)
                if target_urn and reference.urn == target_urn:
                    return True
                if target_key:
                    agency, identifier, version = target_key
                    if reference.identifier != identifier:
                        continue
                    if version is not None and reference.version != version:
                        continue
                    if agency is not None and reference.agency != agency:
                        continue
                    return True
        return False

    def _class_for_type(self, type_name: str) -> type[MaintainableBase]:
        """Translate a type name into the corresponding maintainable class.

        Args:
            type_name: ``TypeOfObject`` or alias name to normalize.

        Returns:
            Maintainable class registered under the derived alias.

        Raises:
            LookupError: If the type name is not recognized.
        """
        cls = maintainable_type_from_name(type_name)
        if cls is None:
            raise LookupError(f"Unsupported TypeOfObject value: {type_name!r}")
        return cls
