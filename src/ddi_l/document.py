"""High-level helpers for working with DDI instance documents."""

from __future__ import annotations

import builtins
import dataclasses
import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)
from uuid import uuid4

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from .index import Index
    from .lint import LintFinding
    from .models.archive import Archive
    from .models.comparison import Comparison
    from .models.concept import Concept, Universe
    from .models.conceptualcomponent import ConceptualComponent
    from .models.datacollection import DataCollection, QuestionItem
    from .models.dataset import DataSet
    from .models.group import LocalHoldingPackage, ResourcePackage
    from .models.instance import TranslationInformation
    from .models.logicalproduct import (
        CodeList,
        DataRelationship,
        LogicalProduct,
        LogicalRecord,
        NCube,
        Variable,
    )
    from .models.physical import RecordLayout
    from .models.profile import DDIProfile

from . import schema_loader
from ._document_maintainables import (
    MaintainableIdentifier,
    MaintainableManagementMixin,
    MaintainableT,
)
from ._document_namespaces import NamespaceManagementMixin
from ._etree import (
    PARSER_ERRORS,
    XMLNS,
    Element,
    cleanup_namespaces,
    create_element,
    tostring,
)
from .constants import (
    COMPARATIVE_NS,
    DDI_PROFILE_NS,
    DEFAULT_NSMAP,
    GROUP_NS,
    INSTANCE_NS,
    REUSABLE_NS,
    STUDY_UNIT_NS,
    XML_NS,
    XSI_NS,
    get_default_nsmap,
    get_namespace_set,
)
from .exceptions import (
    DDIModelError,
    DDIParseError,
    DDIReferenceError,
    DDIValidationError,
    DuplicateIdentifierError,
    build_error_location,
)
from .models.base import (
    InternationalString,
    MaintainableBase,
    Reference,
    build_identification_elements,
    clone_element,
    qn,
    suppress_serialize_validation,
)
from .models.study import StudyUnit
from .namespace_utils import apply_namespace_map, extract_namespace_declarations
from .namespaces import NAMESPACE_PREFIXES, canonicalize_prefixes
from .schema_loader._versions import detect_version_from_element, normalize_version
from .xml_utils import coerce_element as _coerce_xml_input

SourceType = str | Path | bytes | Element


@dataclass(frozen=True)
class _ItemSlot:
    """Registry entry mapping an item type to its parent module and list."""

    module: str
    attr: str
    scheme_flag: str | None = None
    filter_type: type | None = None
    name_attr: str | None = "names"


def _build_item_registry() -> dict[type[MaintainableBase], _ItemSlot]:
    """Build the mapping from item type to module/attribute.

    Deferred to avoid circular imports; classes are resolved at first call.
    """
    from .models.concept import Concept, ConceptualVariable, UnitType, Universe
    from .models.datacollection import (
        CollectionActivity,
        CollectionEvent,
        ComputationItem,
        DataCaptureMethod,
        IfThenElse,
        Instruction,
        InstructionGroup,
        Instrument,
        Loop,
        ObservationPlan,
        QuestionBlock,
        QuestionConstruct,
        QuestionGrid,
        QuestionGroup,
        QuestionItem,
        Sequence,
        StatementItem,
    )
    from .models.logicalproduct import (
        Category,
        CodeList,
        DataRelationship,
        NCube,
        RepresentedVariable,
        Variable,
    )
    from .models.methodology import Methodology
    from .models.physical import PhysicalInstance, RecordLayout

    return {
        QuestionItem: _ItemSlot("dc", "questions"),
        QuestionGrid: _ItemSlot("dc", "question_grids"),
        QuestionBlock: _ItemSlot("dc", "question_blocks"),
        QuestionGroup: _ItemSlot("dc", "question_groups"),
        Instrument: _ItemSlot("dc", "instruments"),
        CollectionEvent: _ItemSlot("dc", "collection_events"),
        CollectionActivity: _ItemSlot("dc", "collection_activities"),
        ObservationPlan: _ItemSlot("dc", "observation_plans"),
        DataCaptureMethod: _ItemSlot("dc", "data_capture_methods"),
        Methodology: _ItemSlot("dc", "methodologies"),
        Instruction: _ItemSlot("dc", "interviewer_instructions"),
        InstructionGroup: _ItemSlot("dc", "interviewer_instruction_groups"),
        QuestionConstruct: _ItemSlot(
            "dc",
            "control_constructs",
            filter_type=QuestionConstruct,
            name_attr="construct_names",
        ),
        Sequence: _ItemSlot(
            "dc",
            "control_constructs",
            filter_type=Sequence,
            name_attr="construct_names",
        ),
        IfThenElse: _ItemSlot(
            "dc",
            "control_constructs",
            filter_type=IfThenElse,
            name_attr="construct_names",
        ),
        StatementItem: _ItemSlot(
            "dc",
            "control_constructs",
            filter_type=StatementItem,
            name_attr="construct_names",
        ),
        ComputationItem: _ItemSlot(
            "dc",
            "control_constructs",
            filter_type=ComputationItem,
            name_attr="construct_names",
        ),
        Loop: _ItemSlot(
            "dc", "control_constructs", filter_type=Loop, name_attr="construct_names"
        ),
        Variable: _ItemSlot("lp", "variables"),
        DataRelationship: _ItemSlot(
            "lp", "data_relationships", filter_type=DataRelationship, name_attr=None
        ),
        NCube: _ItemSlot("lp", "n_cubes", filter_type=NCube),
        CodeList: _ItemSlot("lp", "code_lists"),
        Category: _ItemSlot("lp", "categories"),
        RepresentedVariable: _ItemSlot("lp", "represented_variables"),
        Concept: _ItemSlot("cc", "concepts", "has_concept_scheme"),
        Universe: _ItemSlot("cc", "universes", "has_universe_scheme"),
        ConceptualVariable: _ItemSlot(
            "cc", "conceptual_variables", "has_conceptual_variable_scheme"
        ),
        UnitType: _ItemSlot("cc", "unit_types", "has_unit_type_scheme"),
        PhysicalInstance: _ItemSlot(
            "su",
            "physical_instances",
            filter_type=PhysicalInstance,
            name_attr=None,
        ),
        RecordLayout: _ItemSlot(
            "su",
            "record_layouts",
            filter_type=RecordLayout,
            name_attr=None,
        ),
    }


_ITEM_REGISTRY: dict[type[MaintainableBase], _ItemSlot] | None = None


def _get_item_registry() -> dict[type[MaintainableBase], _ItemSlot]:
    global _ITEM_REGISTRY
    if _ITEM_REGISTRY is None:
        _ITEM_REGISTRY = _build_item_registry()
    return _ITEM_REGISTRY


def _parse_source(source: SourceType) -> Element:
    """Convert a supported XML input into an :class:`Element` tree.

    Args:
        source: Raw XML, a filesystem path, or an :class:`Element` instance to
            wrap.

    Returns:
        Element: The parsed root element for the provided ``source``.

    Raises:
        FileNotFoundError: If ``source`` names a file that does not exist.
        TypeError: If ``source`` cannot be interpreted as XML content.
        DDIParseError: If the XML is malformed.
    """
    try:
        # A string that looks like a filename is never well-formed XML, so
        # treating a missing file as text only trades a clear FileNotFoundError
        # for "Start tag expected, '<' not found".
        return _coerce_xml_input(source, require_existing_path=True)
    except PARSER_ERRORS as exc:
        raise DDIParseError.from_parser_error(exc, sources=[source]) from exc
    except TypeError as exc:  # pragma: no cover - defensive guard
        raise TypeError("Unsupported source type for XML parsing.") from exc


def _create_international_string(
    tag: str, text: str, *, lang: str = "en", ns: str = REUSABLE_NS
) -> Element:
    """Create a reusable string container for basic citation fields.

    Args:
        tag: Local tag name (e.g., "Title").
        text: The string content.
        lang: Language tag for the content.
        ns: Reusable namespace URI of the DDI version being written.

    Returns:
        Element with the internationalized string content.
    """
    container = InternationalString(
        text=text, lang=lang, child_tag="String"
    ).to_element(qn(ns, tag))
    for child in container:
        child.tag = qn(ns, "String")
    return container


def citation_title(citation: Element | None) -> str | None:
    """Return the title text of ``citation``, or ``None`` when it has none.

    DDI 3.3 nests the text one level down: ``r:Title`` holds one
    ``r:String`` per language, as :meth:`DDIDocument.set_citation` writes it.
    Some producers write ``<r:Title>text</r:Title>`` without the wrapper, so
    direct text is accepted as well.
    """
    if citation is None:
        return None
    for title_el in citation.findall(qn(REUSABLE_NS, "Title")):
        for string_el in title_el.findall(qn(REUSABLE_NS, "String")):
            text = (string_el.text or "").strip()
            if text:
                return text
        text = (title_el.text or "").strip()
        if text:
            return text
    return None


def _collect_used_namespace_uris(element: Element) -> set[str]:
    """Return namespace URIs referenced by ``element`` and its descendants."""
    used: set[str] = set()
    for node in element.iter():
        tag = getattr(node, "tag", "")
        if isinstance(tag, str) and tag.startswith("{"):
            uri, _ = tag[1:].split("}", 1)
            used.add(uri)
        for attr_name in getattr(node, "attrib", {}):
            if not attr_name.startswith("{"):
                continue
            uri, _ = attr_name[1:].split("}", 1)
            if uri != XMLNS:
                used.add(uri)
    return used


def _build_serialization_nsmap(
    root: Element,
    overrides: Mapping[str | None, str] | None = None,
    base_nsmap: Mapping[str | None, str] | None = None,
) -> dict[str | None, str]:
    """Construct a namespace map suitable for serialising ``root``."""
    # Re-key onto canonical DDI prefixes before adopting them. A source file
    # may bind studyunit to ``p4``; only the lxml backend can see that, so
    # without this the two backends emit different prefixes for one input.
    declared = canonicalize_prefixes(extract_namespace_declarations(root))
    if overrides:
        # ``overrides`` is what the document recorded when it was opened, so
        # it carries whatever prefixes the source file used and needs the same
        # treatment -- otherwise the superseded prefix is merged back in.
        declared = {**canonicalize_prefixes(overrides), **declared}
    default_map = base_nsmap or _DEFAULT_NS_MAP
    nsmap: dict[str | None, str] = dict(default_map)
    nsmap.update({prefix: uri for prefix, uri in declared.items() if uri})
    used_uris = _collect_used_namespace_uris(root)
    declared_prefixes = {
        prefix for prefix, uri in declared.items() if prefix not in (None, "") and uri
    }
    for prefix, uri in list(nsmap.items()):
        if prefix in (None, ""):
            continue
        if prefix in declared_prefixes:
            continue
        if uri not in used_uris:
            nsmap.pop(prefix)
    nsmap.pop("xml", None)
    assigned_uris = set(nsmap.values())
    default_uri = nsmap.get(None)
    sequential = [
        uri
        for uri in sorted(used_uris)
        if uri not in assigned_uris and uri not in {default_uri, XML_NS}
    ]
    counter = 0
    existing_prefixes = set(filter(None, nsmap.keys()))
    canonical_prefixes = {uri: prefix for prefix, uri in NAMESPACE_PREFIXES.items()}
    for uri in sequential:
        # Prefer the canonical DDI prefix (e.g. ``pr`` for ddiprofile, ``s`` for
        # studyunit) over an auto-generated ``p0``/``p1`` when one is registered
        # and still free — this keeps prefixes stable across open/edit/save.
        canonical = canonical_prefixes.get(uri)
        if canonical is not None and canonical not in existing_prefixes:
            prefix = canonical
        else:
            prefix = f"p{counter}"
            counter += 1
            while prefix in existing_prefixes:
                prefix = f"p{counter}"
                counter += 1
        nsmap[prefix] = uri
        existing_prefixes.add(prefix)

    # Deterministic order (default namespace, then prefixes alphabetically)
    # so both XML backends emit the same root element.
    return {
        key: nsmap[key] for key in sorted(nsmap, key=lambda p: (p is not None, p or ""))
    }


def _is_identified_item(value: object) -> bool:
    """Return whether ``value`` is a model item (not a reference) with an ID."""
    return (
        dataclasses.is_dataclass(value)
        and not isinstance(value, Reference)
        and hasattr(value, "identifier")
    )


def _require_text(value: object, field: str) -> str:
    """Return ``value`` if it is a non-blank string, else raise.

    Raises:
        TypeError: If ``value`` is not a string.
        ValueError: If ``value`` is empty or whitespace.
    """
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string, not {type(value).__name__}.")
    if not value.strip():
        raise ValueError(f"{field} must be a non-empty string.")
    return value


class DDIDocument(MaintainableManagementMixin, NamespaceManagementMixin):
    """A convenience wrapper around a DDI instance XML tree."""

    def __init__(self, root: Element):
        detected_version = normalize_version(detect_version_from_element(root))
        namespace_set = get_namespace_set(detected_version)
        instance_namespace = namespace_set["INSTANCE_NS"]
        self._version = detected_version
        self._instance_ns = instance_namespace
        self._reusable_ns = namespace_set["REUSABLE_NS"]
        self._default_ns_map = get_default_nsmap(detected_version)

        if root.tag != qn(instance_namespace, "DDIInstance"):
            raise ValueError(
                "Root element must be DDIInstance in the DDI instance namespace."
            )
        self._root = root
        self._index: Index | None = None
        cleanup_namespaces(self._root, dict(self._default_ns_map))
        # Record declarations after the cleanup so unused ones (such as an
        # unused ``xsi``) are not re-emitted on save; both backends then agree.
        self._declared_namespaces: dict[str | None, str] = (
            extract_namespace_declarations(self._root)
        )

    @property
    def root(self) -> Element:
        """Element: Direct access to the underlying XML tree."""
        return self._root

    def __repr__(self) -> str:
        root = self._root
        tag = root.tag.split("}")[-1] if isinstance(root.tag, str) else "?"
        version = detect_version_from_element(root) or "?"
        return f"DDIDocument(root={tag!r}, ddi_version={version!r})"

    @classmethod
    def create(
        cls,
        *,
        agency: str,
        identifier: str,
        version: str,
        title: str | None = None,
        title_language: str = "en",
        build_index: bool = False,
    ) -> DDIDocument:
        """Construct a new ``<DDIInstance>`` tree.

        Args:
            agency: Agency component of the instance identification.
            identifier: Identifier component of the instance identification.
            version: Version component of the instance identification.
            title: Optional human-readable title added to the citation.
            title_language: Language tag for ``title`` when provided.
            build_index: Build the resolver index now. By default it is built on
                first use of :attr:`DDIDocument.resolver`.

        Returns:
            DDIDocument: A wrapper ready for further manipulation.

        Raises:
            ValueError: If the generated root element is not a DDI instance.
        """
        root = create_element(
            qn(INSTANCE_NS, "DDIInstance"), nsmap=dict(_DEFAULT_NS_MAP)
        )
        document = cls(root)
        document.set_identification(
            agency=agency, identifier=identifier, version=version
        )
        if title:
            document.set_citation(title=title, lang=title_language)
        if build_index:
            document.build_index()
        return document

    @classmethod
    def from_xml(
        cls,
        source: SourceType,
        *,
        validate: bool = False,
        build_index: bool = False,
    ) -> DDIDocument:
        """Parse XML content into a document wrapper.

        Args:
            source: Raw XML text, bytes, a filesystem path, or an
                :class:`Element` instance.
            validate: Whether to validate the parsed XML against the DDI XML
                schema. When ``True``, invalid XML raises
                :class:`schema_loader.SchemaValidationError`.
            build_index: Build the resolver index now. By default it is built on
                first use of :attr:`DDIDocument.resolver`.

        Returns:
            DDIDocument: The parsed document wrapper.

        Raises:
            TypeError: If ``source`` cannot be converted into XML.
            schema_loader.SchemaValidationError: Raised when ``validate`` is
                ``True`` and the XML is not schema compliant.
        """
        root = _parse_source(source)
        if validate:
            schema_loader.validate(root)
        document = cls(root)
        if build_index:
            document.build_index()
        return document

    def to_xml(self, *, pretty_print: bool = True) -> str:
        """Serialise the document into an XML string.

        Args:
            pretty_print: When ``True`` the output is formatted for readability.

        Returns:
            str: UTF-8 encoded XML representation of the document.
        """
        clone = clone_element(self._root)
        nsmap = _build_serialization_nsmap(
            self._root,
            getattr(self, "_declared_namespaces", None),
            base_nsmap=self._default_ns_map,
        )
        normalised = apply_namespace_map(clone, nsmap, preserve_existing=True)
        return tostring(normalised, pretty_print=pretty_print)

    def to_dict(self) -> dict[str, object]:
        """Convert the document XML tree into a nested mapping representation.

        Returns:
            dict[str, object]: Mapping suitable for JSON serialisation or further
            manipulation.
        """
        return schema_loader.to_dict(self._root, process_namespaces=True)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, object],
        *,
        validate: bool = False,
        build_index: bool = False,
    ) -> DDIDocument:
        """Create a document from its mapping representation.

        Args:
            data: Mapping of tag names to values representing the root
                ``<DDIInstance>`` payload.
            validate: Whether to validate the generated XML against the DDI
                schema. When ``True``, invalid XML raises
                :class:`schema_loader.SchemaValidationError`.
            build_index: Build the resolver index now. By default it is built on
                first use of :attr:`DDIDocument.resolver`.

        Returns:
            DDIDocument: The document represented by ``data``.

        Raises:
            schema_loader.SchemaValidationError: Raised when ``validate`` is
                ``True`` and the generated XML is not schema compliant.
        """
        root_tag = qn(INSTANCE_NS, "DDIInstance")
        element = schema_loader.from_dict({root_tag: data}, process_namespaces=True)
        if validate:
            schema_loader.validate(element)
        document = cls(element)
        if build_index:
            document.build_index()
        return document

    def get_identification(self) -> dict[str, str | None]:
        """Return the identification metadata currently set on the document.

        Returns:
            dict[str, Optional[str]]: The agency, identifier, and version text
            stored on the document root.
        """
        return {
            "agency": self._text_or_none(
                self._root.find(qn(self._reusable_ns, "Agency"))
            ),
            "id": self._text_or_none(self._root.find(qn(self._reusable_ns, "ID"))),
            "version": self._text_or_none(
                self._root.find(qn(self._reusable_ns, "Version"))
            ),
        }

    def _text_or_none(self, element: Element | None) -> str | None:
        """Extract element text or ``None`` when the element is missing.

        Args:
            element: XML element whose textual content should be returned.

        Returns:
            Optional[str]: ``element.text`` when present, otherwise ``None``.
        """
        if element is None:
            return None
        return element.text

    def set_identification(
        self,
        *,
        agency: str,
        identifier: str,
        version: str,
        scope_of_uniqueness: str | None = None,
    ) -> None:
        """Replace the document's identification nodes and optional scope attribute.

        Args:
            agency: Maintenance agency responsible for the instance.
            identifier: Identifier value under ``agency``.
            version: Version number associated with the instance.
            scope_of_uniqueness: Optional scope attribute applied to the root
                element when provided.

        Returns:
            None: The document is updated in place.
        """
        for tag in ("URN", "Agency", "ID", "Version"):
            element = self._root.find(qn(self._reusable_ns, tag))
            if element is not None:
                self._root.remove(element)
        identification_elements = build_identification_elements(
            agency=agency,
            identifier=identifier,
            version=version,
            namespace=self._reusable_ns,
        )
        for insertion_index, element in enumerate(identification_elements):
            self._root.insert(insertion_index, element)

        # Drop any existing scope attribute before optionally re-applying.
        if "scopeOfUniqueness" in self._root.attrib:
            del self._root.attrib["scopeOfUniqueness"]
        if scope_of_uniqueness:
            self._root.set("scopeOfUniqueness", scope_of_uniqueness)

    def set_citation(self, *, title: str | None = None, lang: str = "en") -> Element:
        """Ensure a ``<Citation>`` exists and optionally rewrite the ``<Title>``.

        Args:
            title: Replacement citation title when provided.
            lang: Language tag applied to ``title``.

        Returns:
            Element: The citation element residing on the document root.
        """
        citation = self._root.find(qn(self._reusable_ns, "Citation"))
        if citation is None:
            citation = create_element(qn(self._reusable_ns, "Citation"))
            self._root.append(citation)
        if title is not None:
            for existing in list(citation.findall(qn(self._reusable_ns, "Title"))):
                citation.remove(existing)
            citation.append(
                _create_international_string(
                    "Title", title, lang=lang, ns=self._reusable_ns
                )
            )
        return citation

    def iter_study_units(self) -> Iterator[StudyUnit]:
        """Yield :class:`StudyUnit` wrappers for each inline study in the document."""
        yield from self.iter_maintainables(StudyUnit)

    def add_study_unit(self, study_unit: StudyUnit) -> Element:
        """Append a new :class:`StudyUnit` to the instance document."""
        return self.add_maintainable(study_unit)

    def add_maintainable(self, maintainable: MaintainableBase) -> Element:
        """Append ``maintainable`` and invalidate the index."""
        element = super().add_maintainable(maintainable)
        self._invalidate_index()
        return element

    def replace_maintainable(self, maintainable: MaintainableBase) -> Element:
        """Replace an existing maintainable and invalidate the index."""
        element = super().replace_maintainable(maintainable)
        self._invalidate_index()
        return element

    def remove_maintainable(
        self,
        target: MaintainableIdentifier,
        *,
        maintainable_type: type[MaintainableBase] | None = None,
    ) -> bool:
        """Remove a maintainable and invalidate the index."""
        removed = super().remove_maintainable(
            target, maintainable_type=maintainable_type
        )
        if removed:
            self._invalidate_index()
        return removed

    def lint(self, rules: Sequence[str] | None = None):
        """Run lint checks against the document using the shared registry."""
        from . import lint as lint_module

        return lint_module.run_lint(self, rules=rules)

    def _invalidate_index(self) -> None:
        """Clear the cached resolver so it is rebuilt on next access."""
        self._index = None

    @property
    def resolver(self) -> Index:
        """Return an :class:`Index` resolver for the document, caching results."""
        if self._index is None:
            self._index = self.build_index()
        return self._index

    def build_index(self) -> Index:
        """Construct an :class:`ddi_l.index.Index` for the document's content."""
        from .index import Index

        self._require_typed_models()
        index = Index.from_document(self)
        self._index = index
        return index

    def resolve(
        self,
        target: MaintainableBase | Reference | str | tuple[str | None, str, str | None],
        *,
        type: type[MaintainableBase] | None = None,
    ) -> MaintainableBase:
        """Resolve ``target`` to a maintainable instance using the cached resolver."""
        maintainable_type = type
        if maintainable_type is not None and (
            not isinstance(maintainable_type, builtins.type)
            or not issubclass(maintainable_type, MaintainableBase)
        ):
            raise TypeError("type must be a subclass of MaintainableBase.")

        if isinstance(target, MaintainableBase):
            if maintainable_type is not None and not isinstance(
                target, maintainable_type
            ):
                raise TypeError("Maintainable does not match the requested type.")
            return target

        if isinstance(target, Reference):
            reference = target
        elif isinstance(target, str):
            reference = Reference(
                urn=target,
                type_of_object=maintainable_type.__name__
                if maintainable_type
                else None,
            )
        elif isinstance(target, tuple):
            if len(target) != 3:
                msg = "Identifier tuples must be (agency, identifier, version)."
                raise ValueError(msg)
            agency, identifier, version = target
            reference = Reference(
                agency=agency,
                identifier=identifier,
                version=version,
                type_of_object=maintainable_type.__name__
                if maintainable_type
                else None,
            )
        else:
            raise TypeError("Unsupported target type for resolution.")

        result = self.resolver.resolve(reference, expected_type=maintainable_type)
        return result

    def to_etree(self) -> Element:
        """Return the root element for downstream XML operations.

        Returns:
            Element: The underlying XML element managed by this wrapper.
        """
        return self._root

    def validate(
        self, *, raise_error: bool = False
    ) -> list[schema_loader.SchemaValidationIssue]:
        """Validate the document and return structured error details when invalid.

        Args:
            raise_error: When ``True`` a validation failure raises
                :class:`schema_loader.SchemaValidationError` instead of
                returning issues.

        Returns:
            list[schema_loader.SchemaValidationIssue]: Collected schema
            validation issues, empty when the document is valid.
        """
        try:
            return schema_loader.validate(self._root, raise_error=raise_error)
        except schema_loader.SchemaValidationError as exc:
            if not raise_error:
                return list(exc.issues)
            fallback_location = build_error_location(element=self._root)
            raise DDIValidationError.from_schema_error(
                exc,
                fallback_location=fallback_location,
            ) from exc


class DDIFragment:
    """A convenience wrapper around a DDI fragment instance XML tree."""

    def __init__(self, root: Element):
        detected_version = normalize_version(detect_version_from_element(root))
        namespace_set = get_namespace_set(detected_version)
        instance_namespace = namespace_set["INSTANCE_NS"]
        self._version = detected_version
        self._instance_ns = instance_namespace
        self._reusable_ns = namespace_set["REUSABLE_NS"]
        self._default_ns_map = get_default_nsmap(detected_version)

        if root.tag != qn(instance_namespace, "FragmentInstance"):
            raise ValueError(
                "Root element must be FragmentInstance in the DDI instance namespace."
            )
        self._root = root
        self._declared_namespaces: dict[str | None, str] = (
            extract_namespace_declarations(self._root)
        )
        cleanup_namespaces(self._root, dict(self._default_ns_map))

    @property
    def root(self) -> Element:
        """Element: Direct access to the fragment instance tree."""
        return self._root

    @classmethod
    def create(
        cls,
        top_level: Reference | MaintainableBase | None = None,
    ) -> DDIFragment:
        """Construct a new fragment wrapper with an optional top-level reference."""
        root = create_element(
            qn(INSTANCE_NS, "FragmentInstance"), nsmap=dict(_DEFAULT_NS_MAP)
        )
        fragment = cls(root)
        if top_level is not None:
            fragment.set_top_level_reference(top_level)
        return fragment

    @classmethod
    def from_xml(cls, source: SourceType, *, validate: bool = False) -> DDIFragment:
        """Parse XML content into a fragment wrapper.

        Args:
            source: Raw XML text, bytes, a filesystem path, or an
                :class:`Element` instance.
            validate: Whether to validate the parsed XML against the DDI XML
                schema. When ``True`` invalid XML raises
                :class:`schema_loader.SchemaValidationError`.

        Returns:
            DDIFragment: The parsed fragment wrapper.

        Raises:
            TypeError: If ``source`` cannot be converted into XML.
            schema_loader.SchemaValidationError: Raised when ``validate`` is
                ``True`` and the XML is not schema compliant.
        """
        root = _parse_source(source)
        if validate:
            schema_loader.validate(root)
        return cls(root)

    def to_xml(self, *, pretty_print: bool = True) -> str:
        """Serialise the fragment into an XML string.

        Args:
            pretty_print: When ``True`` the output is formatted for readability.

        Returns:
            str: UTF-8 encoded XML representation of the fragment.
        """
        clone = clone_element(self._root)
        nsmap = _build_serialization_nsmap(
            self._root, getattr(self, "_declared_namespaces", None)
        )
        normalised = apply_namespace_map(clone, nsmap, preserve_existing=True)
        return tostring(normalised, pretty_print=pretty_print)

    def to_dict(self) -> dict[str, object]:
        """Convert the fragment XML tree into a nested mapping representation.

        Returns:
            dict[str, object]: Mapping suitable for JSON serialisation or further
            manipulation.
        """
        return schema_loader.to_dict(self._root, process_namespaces=True)

    def _normalize_reference(
        self, reference: Reference | MaintainableBase | None
    ) -> Reference | None:
        if reference is None:
            return None
        if isinstance(reference, Reference):
            return reference
        if isinstance(reference, MaintainableBase):
            tag = reference.TAG
            type_of_object = tag.split("}", 1)[-1] if "}" in tag else tag
            return Reference(
                type_of_object=type_of_object,
                urn=reference.urn,
                agency=reference.agency,
                identifier=reference.identifier,
                version=reference.version,
            )
        raise TypeError("Unsupported reference type for fragment top-level reference.")

    def set_top_level_reference(
        self, reference: Reference | MaintainableBase | None
    ) -> Element | None:
        """Set (or clear) the ``<TopLevelReference>`` on the fragment root."""
        existing = self._root.find(qn(self._instance_ns, "TopLevelReference"))
        if existing is not None:
            self._root.remove(existing)

        normalized = self._normalize_reference(reference)
        if normalized is None:
            cleanup_namespaces(self._root, dict(_DEFAULT_NS_MAP))
            return None

        element = normalized.to_xml("TopLevelReference", namespace=self._instance_ns)
        self._root.insert(0, element)
        cleanup_namespaces(self._root, dict(_DEFAULT_NS_MAP))
        return element

    def get_top_level_reference(self) -> Reference | None:
        """Return the fragment's top-level reference (if present)."""
        element = self._root.find(qn(self._instance_ns, "TopLevelReference"))
        if element is None:
            return None
        return Reference.from_xml(element)

    def add_fragment(
        self, payload: MaintainableBase | Element | Iterable[Element]
    ) -> Element:
        """Append a ``<Fragment>`` node wrapping ``payload`` to the instance."""
        fragment = create_element(qn(self._instance_ns, "Fragment"))
        if isinstance(payload, MaintainableBase):
            if self._version != "3.3":
                raise DDIModelError(
                    f"Typed models are available for DDI 3.3 only; this fragment "
                    f"is DDI {self._version}. Pass XML elements instead."
                )
            fragment.append(payload.to_xml())
        elif isinstance(payload, Element):
            fragment.append(payload)
        else:
            try:
                iterator = iter(payload)
            except TypeError as exc:  # pragma: no cover - defensive guard
                raise TypeError(
                    "Unsupported payload type for fragment insertion."
                ) from exc
            for element in iterator:
                if not isinstance(element, Element):
                    raise TypeError(
                        "Fragment payload iterable must yield Element instances."
                    )
                fragment.append(element)

        self._root.append(fragment)
        cleanup_namespaces(self._root, dict(_DEFAULT_NS_MAP))
        return fragment

    def iter_fragments(self) -> Iterator[Element]:
        """Yield the raw ``<Fragment>`` container elements from the instance."""
        fragment_tag = qn(self._instance_ns, "Fragment")
        yield from self._root.findall(fragment_tag)

    def iter_fragment_payloads(self) -> Iterator[Element]:
        """Yield the payload elements contained within each ``<Fragment>`` node."""
        for fragment in self.iter_fragments():
            if len(fragment):
                yield from fragment

    def to_etree(self) -> Element:
        """Return the fragment root element for downstream XML operations.

        Returns:
            Element: The underlying XML element managed by this fragment.
        """
        return self._root

    def validate(
        self, *, raise_error: bool = False
    ) -> list[schema_loader.SchemaValidationIssue]:
        """Validate the fragment and return structured error details when invalid.

        Args:
            raise_error: When ``True`` a validation failure raises
                :class:`schema_loader.SchemaValidationError` instead of
                returning issues.

        Returns:
            list[schema_loader.SchemaValidationIssue]: Collected schema
            validation issues, empty when the fragment is valid.
        """
        try:
            return schema_loader.validate(self._root, raise_error=raise_error)
        except schema_loader.SchemaValidationError as exc:
            if not raise_error:
                return list(exc.issues)
            fallback_location = build_error_location(element=self._root)
            raise DDIValidationError.from_schema_error(
                exc,
                fallback_location=fallback_location,
            ) from exc


class Document:
    """A DDI Lifecycle 3.3 document with a simple CRUD API.

    This is the primary interface for creating, reading, updating, and
    deleting content in DDI documents. It manages a single StudyUnit
    and provides convenience methods for common operations.

    Args:
        inner: The underlying DDIDocument instance.

    Example:
        >>> import ddi_l as ddi
        >>> doc = ddi.new_study(title="My Survey", agency="example.org")
        >>> q = doc.add_question(text="How old are you?")
        >>> doc.save("my-study.xml")
    """

    def __init__(self, inner: DDIDocument) -> None:
        declared = detect_version_from_element(inner._root)
        if declared is not None and normalize_version(declared) != "3.3":
            raise DDIModelError(
                f"Document supports DDI Lifecycle 3.3; this document declares "
                f"{normalize_version(declared)}. Use ddi_l.read_ddi() for "
                "read-only access to earlier versions."
            )
        self._inner = inner
        self._study: StudyUnit | None = None
        # The element that contains the active StudyUnit: the DDIInstance root,
        # or a <g:Group> when the study is organized into a group.
        self._study_parent: Element | None = None
        # DDIProfiles attached at the DDIInstance level, re-serialized on flush.
        self._profiles: list[DDIProfile] = []
        # Instance-level reuse/holding packages, re-serialized on flush.
        self._resource_packages: list[ResourcePackage] = []
        self._local_holding_packages: list[LocalHoldingPackage] = []
        # Optional single TranslationInformation element on the DDIInstance.
        self._translation_information: TranslationInformation | None = None
        # Comparisons and additional studies, re-serialized into the group.
        self._comparisons: list[Comparison] = []
        self._extra_studies: list[StudyUnit] = []
        # Transiently redirects _get_study() to a specific study (used by
        # StudyCursor to target a non-primary study for the add_* helpers).
        self._study_override: StudyUnit | None = None
        # Language for the labels put on module and scheme wrappers this facade
        # generates. Set it when authoring in another language so the
        # containers are not the one part of the document tagged ``en``.
        self._generated_label_lang: str = "en"
        # The XML element ``_study`` was parsed from, so ``_flush`` can put the
        # edited study back exactly where it came from.
        self._study_element: Element | None = None
        self._dirty = False

    def __repr__(self) -> str:
        try:
            study = self._get_study()
        except DDIModelError:
            return "Document(<no StudyUnit>)"
        title = next(
            (text.text for text in study.abstracts if text.text), study.identifier
        )
        return (
            f"Document(title={title!r}, agency={study.agency!r}, "
            f"questions={len(self.questions)}, variables={len(self.variables)})"
        )

    def _locate_study_element(self) -> tuple[Element, Element] | None:
        """Return ``(parent, study_element)`` for the first StudyUnit.

        Searches direct children of the DDIInstance root first, then inside any
        ``<g:Group>`` so that group-organized documents are supported.
        """
        root = self._inner._root
        study_tag = qn(STUDY_UNIT_NS, "StudyUnit")
        direct = root.find(study_tag)
        if direct is not None:
            return root, direct
        for group in root.findall(qn(GROUP_NS, "Group")):
            nested = group.find(study_tag)
            if nested is not None:
                return group, nested
        return None

    def _get_study(self) -> StudyUnit:
        """Return the target StudyUnit (the override, else the cached primary)."""
        if self._study_override is not None:
            return self._study_override
        if self._study is None:
            located = self._locate_study_element()
            if located is None:
                raise DDIModelError("Document contains no StudyUnit.")
            parent, element = located
            self._study = StudyUnit.from_xml(element)
            self._study_parent = parent
            # Remember the element we loaded from. ``_flush`` replaces *this*
            # element rather than looking the study up again by identity: a
            # caller who bumped the version has changed that identity, and an
            # identity-based lookup would miss and append a duplicate StudyUnit.
            self._study_element = element
            self._load_group_studies(element)
        return self._study

    def _load_group_studies(self, primary_element: Element) -> None:
        """Track the group's other StudyUnits alongside the primary study."""
        group = self._inner._root.find(qn(GROUP_NS, "Group"))
        if group is None:
            return
        tracked = {study.identifier for study in self._extra_studies}
        for element in group.findall(qn(STUDY_UNIT_NS, "StudyUnit")):
            if element is primary_element:
                continue
            study = StudyUnit.from_xml(element)
            if study.identifier not in tracked:
                self._extra_studies.append(study)
                tracked.add(study.identifier)

    @contextmanager
    def _use_study(self, study: StudyUnit) -> Iterator[None]:
        """Redirect :meth:`_get_study` (and the ``add_*`` helpers) to ``study``."""
        previous = self._study_override
        self._study_override = study
        try:
            yield
        finally:
            self._study_override = previous

    def _flush(self, *, check_references: bool = False) -> None:
        """Sync the cached StudyUnit, DDIProfiles, and group content into XML.

        The cached :class:`StudyUnit` stays cached, so model objects handed out
        by the ``add_*`` helpers and list properties remain attached to the
        document after a flush.

        Args:
            check_references: Warn about references the study cannot resolve.
        """
        self._flush_instance_packages()
        self._flush_profiles()
        self._flush_group_content()
        self._flush_translation_information()
        # Always re-serialize a cached study: callers may mutate model objects
        # in place without going through an ``add_*`` helper.
        if self._study is None:
            return
        study = self._study
        with suppress_serialize_validation():
            parent = self._study_parent
            if self._study_element is not None and parent is not None:
                # Replace the exact element the study came from; an identity
                # lookup would miss after a version bump.
                element = self._replace_study_element(
                    parent,
                    self._study_element,
                    study,
                    check_references=check_references,
                )
            elif parent is None or parent is self._inner._root:
                try:
                    self._inner.replace_maintainable(study)
                except LookupError:
                    self._inner.add_study_unit(study)
                parent = self._inner._root
                element = self._find_study_child(parent, study)
            else:
                element = self._replace_study_in_parent(
                    parent, study, check_references=check_references
                )
        self._dirty = False
        self._study_parent = parent
        self._study_element = element

    def _release_study(self) -> None:
        """Flush, then drop the cached study so it is re-read from XML."""
        self._flush()
        self._study = None
        self._study_parent = None
        self._study_element = None

    @staticmethod
    def _find_study_child(parent: Element, study: StudyUnit) -> Element | None:
        """Return the StudyUnit element under ``parent`` carrying ``study``'s ID."""
        study_tag = qn(STUDY_UNIT_NS, "StudyUnit")
        id_tag = qn(REUSABLE_NS, "ID")
        for child in parent:
            if child.tag != study_tag:
                continue
            child_id = child.find(id_tag)
            if child_id is not None and child_id.text == study.identifier:
                return child
        return None

    def _replace_study_element(
        self,
        parent: Element,
        existing: Element,
        study: StudyUnit,
        *,
        check_references: bool = False,
    ) -> Element | None:
        """Swap ``existing`` for ``study``'s serialization; return the new element."""
        replacement = study.to_xml(validate_refs=check_references)
        children = list(parent)
        for index, child in enumerate(children):
            if child is existing:
                replacement.tail = child.tail
                parent.insert(index, replacement)
                parent.remove(child)
                cleanup_namespaces(self._inner._root, dict(_DEFAULT_NS_MAP))
                return replacement
        # The element was detached by the caller; fall back to identity lookup.
        if parent is self._inner._root:
            try:
                self._inner.replace_maintainable(study)
            except LookupError:
                self._inner.add_study_unit(study)
            return self._find_study_child(parent, study)
        return self._replace_study_in_parent(
            parent, study, check_references=check_references
        )

    def _replace_study_in_parent(
        self, parent: Element, study: StudyUnit, *, check_references: bool = False
    ) -> Element:
        """Replace ``study``'s element within ``parent`` (a group) and return it."""
        study_tag = qn(STUDY_UNIT_NS, "StudyUnit")
        id_tag = qn(REUSABLE_NS, "ID")
        replacement = study.to_xml(validate_refs=check_references)
        for index, child in enumerate(list(parent)):
            if child.tag != study_tag:
                continue
            child_id = child.find(id_tag)
            if child_id is not None and child_id.text == study.identifier:
                replacement.tail = child.tail
                parent.insert(index, replacement)
                parent.remove(child)
                return replacement
        parent.append(replacement)
        return replacement

    def _flush_profiles(self) -> None:
        """Serialize tracked DDIProfiles into the DDIInstance root (idempotent)."""
        if not self._profiles:
            return
        root = self._inner._root
        profile_tag = qn(INSTANCE_NS, "DDIProfile")
        ddiprofile_tag = qn(DDI_PROFILE_NS, "DDIProfile")
        id_tag = qn(REUSABLE_NS, "ID")
        for profile in self._profiles:
            new_element = profile.to_xml()
            replaced = False
            for index, child in enumerate(list(root)):
                if child.tag not in (profile_tag, ddiprofile_tag):
                    continue
                child_id = child.find(id_tag)
                if child_id is not None and child_id.text == profile.identifier:
                    new_element.tail = child.tail
                    root.insert(index, new_element)
                    root.remove(child)
                    replaced = True
                    break
            if not replaced:
                root.append(new_element)

    def _upsert_in_root(
        self,
        new_element: Element,
        identifier: str | None,
        *,
        match_tag: str,
        successor_tags: set[str],
    ) -> None:
        """Replace a root child with a matching id, else insert before successors."""
        root = self._inner._root
        id_tag = qn(REUSABLE_NS, "ID")
        for index, child in enumerate(list(root)):
            if child.tag != match_tag:
                continue
            child_id = child.find(id_tag)
            if child_id is not None and child_id.text == identifier:
                new_element.tail = child.tail
                root.insert(index, new_element)
                root.remove(child)
                return
        for index, child in enumerate(list(root)):
            if child.tag in successor_tags:
                root.insert(index, new_element)
                return
        root.append(new_element)

    def _flush_instance_packages(self) -> None:
        """Serialize ResourcePackages and LocalHoldingPackages onto the root."""
        if not self._resource_packages and not self._local_holding_packages:
            return
        rp_tag = qn(GROUP_NS, "ResourcePackage")
        lhp_tag = qn(GROUP_NS, "LocalHoldingPackage")
        su_tag = qn(STUDY_UNIT_NS, "StudyUnit")
        su_ref = qn(REUSABLE_NS, "StudyUnitReference")
        profile_tag = qn(DDI_PROFILE_NS, "DDIProfile")
        ti_tag = qn(INSTANCE_NS, "TranslationInformation")
        with suppress_serialize_validation():
            # ResourcePackage precedes LocalHoldingPackage, StudyUnit, and later.
            for package in self._resource_packages:
                self._upsert_in_root(
                    package.to_xml(),
                    package.identifier,
                    match_tag=rp_tag,
                    successor_tags={lhp_tag, su_tag, su_ref, profile_tag, ti_tag},
                )
            for holding in self._local_holding_packages:
                self._upsert_in_root(
                    holding.to_xml(),
                    holding.identifier,
                    match_tag=lhp_tag,
                    successor_tags={su_tag, su_ref, profile_tag, ti_tag},
                )

    def _flush_translation_information(self) -> None:
        """Serialize the TranslationInformation element (last on the root)."""
        if self._translation_information is None:
            return
        root = self._inner._root
        ti_tag = qn(INSTANCE_NS, "TranslationInformation")
        new_element = self._translation_information.to_xml()
        existing = root.find(ti_tag)
        if existing is not None:
            new_element.tail = existing.tail
            index = list(root).index(existing)
            root.insert(index, new_element)
            root.remove(existing)
        else:
            root.append(new_element)

    def _flush_group_content(self) -> None:
        """Re-serialize tracked comparisons and extra studies into the group."""
        if not self._comparisons and not self._extra_studies:
            return
        group = self._inner._root.find(qn(GROUP_NS, "Group"))
        if group is None:
            return
        study_tag = qn(STUDY_UNIT_NS, "StudyUnit")
        comparison_tag = qn(COMPARATIVE_NS, "Comparison")
        id_tag = qn(REUSABLE_NS, "ID")
        with suppress_serialize_validation():
            # Comparisons precede StudyUnits in the group's content model.
            for comparison in self._comparisons:
                self._upsert_in_group(
                    group,
                    comparison.to_xml(),
                    comparison.identifier,
                    match_tag=comparison_tag,
                    id_tag=id_tag,
                    before_tag=study_tag,
                )
            for study in self._extra_studies:
                self._upsert_in_group(
                    group,
                    study.to_xml(),
                    study.identifier,
                    match_tag=study_tag,
                    id_tag=id_tag,
                    before_tag=None,
                )

    @staticmethod
    def _upsert_in_group(
        group: Element,
        new_element: Element,
        identifier: str | None,
        *,
        match_tag: str,
        id_tag: str,
        before_tag: str | None,
    ) -> None:
        """Replace an element with matching id, else insert it (before before_tag)."""
        for index, child in enumerate(list(group)):
            if child.tag != match_tag:
                continue
            child_id = child.find(id_tag)
            if child_id is not None and child_id.text == identifier:
                new_element.tail = child.tail
                group.insert(index, new_element)
                group.remove(child)
                return
        if before_tag is not None:
            anchor = group.find(before_tag)
            if anchor is not None:
                group.insert(list(group).index(anchor), new_element)
                return
        group.append(new_element)

    @property
    def agency(self) -> str:
        """str: The agency of the primary StudyUnit."""
        return self._get_study().agency or ""

    @property
    def title(self) -> str | None:
        """Return the study's citation title, or None when unavailable.

        Reads the citation title from the StudyUnit when it carries its own
        ``r:Citation``, then the document-level one written by
        :func:`new_study` (and preserved by :func:`open_ddi`), falling back
        last to the StudyUnit's first abstract.
        """
        study = self._get_study()
        for citation in study.citations:
            title = citation_title(citation)
            if title:
                return title
        title = citation_title(self._inner._root.find(qn(REUSABLE_NS, "Citation")))
        if title:
            return title
        for abstract in study.abstracts:
            if abstract.text and abstract.text.strip():
                return abstract.text.strip()
        return None

    @staticmethod
    def _humanize_tag(local_name: str) -> str:
        """Turn ``"QuestionScheme"`` into ``"Question scheme"``."""
        words = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+", local_name)
        if not words:
            return local_name
        return " ".join([words[0]] + [w.lower() for w in words[1:]])

    def _label_generated_module(self, module: MaintainableBase, namespace: str) -> None:
        """Give a module and its scheme wrappers a descriptive label.

        The facade creates these containers on the caller's behalf, so it also
        labels them; that keeps its output clean under the
        ``ddi.maintainable.labels`` lint rule. The label describes the container,
        and :meth:`~MaintainableBase.set_scheme_label` overrides it. Parsed
        modules are never touched. Scheme names come from the generated
        label-slot table.
        """
        from .models._generated.label_slots import TAGS_ALLOWING_LABEL

        module.labels.append(
            InternationalString(
                text=self._humanize_tag(module.TAG.split("}")[-1]),
                lang=self._generated_label_lang,
            )
        )
        prefix = f"{{{namespace}}}"
        for tag in TAGS_ALLOWING_LABEL:
            if not tag.startswith(prefix):
                continue
            local = tag.split("}")[-1]
            if local.endswith("Scheme"):
                module.set_scheme_label(
                    local,
                    self._humanize_tag(local),
                    lang=self._generated_label_lang,
                )

    def _ensure_data_collection(self) -> DataCollection:
        from .constants import DATA_COLLECTION_NS
        from .models.datacollection import DataCollection

        study = self._get_study()
        if study.data_collections:
            return study.data_collections[0]
        dc = DataCollection(
            agency=study.agency,
            identifier=str(uuid4()),
            version=study.version or "1",
        )
        self._label_generated_module(dc, DATA_COLLECTION_NS)
        study.data_collections.append(dc)
        self._dirty = True
        return dc

    def _ensure_logical_product(self) -> LogicalProduct:
        from .constants import LOGICAL_PRODUCT_NS
        from .models.logicalproduct import LogicalProduct

        study = self._get_study()
        if study.logical_products:
            return study.logical_products[0]
        lp = LogicalProduct(
            agency=study.agency,
            identifier=str(uuid4()),
            version=study.version or "1",
        )
        self._label_generated_module(lp, LOGICAL_PRODUCT_NS)
        study.logical_products.append(lp)
        self._dirty = True
        return lp

    def _ensure_conceptual_component(self) -> ConceptualComponent:
        from .constants import CONCEPTUAL_COMPONENT_NS
        from .models.conceptualcomponent import ConceptualComponent

        study = self._get_study()
        if study.conceptual_components:
            return study.conceptual_components[0]
        cc = ConceptualComponent(
            agency=study.agency,
            identifier=str(uuid4()),
            version=study.version or "1",
        )
        self._label_generated_module(cc, CONCEPTUAL_COMPONENT_NS)
        study.conceptual_components.append(cc)
        self._dirty = True
        return cc

    def add_question(
        self,
        text: str,
        *,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        identifier: str | None = None,
    ) -> QuestionItem:
        """Add a question to the document.

        Args:
            text: The question text.
            lang: Language tag for the text.
            label: Optional human-readable label. Supplying one keeps the
                document clean under the ``ddi.maintainable.labels`` lint rule.
            label_lang: Language tag for ``label``; defaults to ``lang``.
            identifier: Optional identifier; auto-generated if omitted.

        Returns:
            QuestionItem: The newly created question.
        """
        from .models.datacollection import QuestionItem

        study = self._get_study()
        dc = self._ensure_data_collection()
        qi = QuestionItem(
            agency=study.agency,
            identifier=self._new_identifier(identifier),
            version=study.version or "1",
            labels=self._labels_for(label, lang, label_lang),
            question_texts=[
                InternationalString(
                    text=_require_text(text, "text"),
                    lang=lang,
                    child_tag="Content",
                    is_plain_text=True,
                )
            ],
        )
        dc.questions.append(qi)
        self._dirty = True
        return qi

    def add_variable(
        self,
        name: str,
        *,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        question: QuestionItem | Reference | None = None,
        concept: Concept | Reference | None = None,
        identifier: str | None = None,
    ) -> Variable:
        """Add a variable to the document.

        Args:
            name: The variable name.
            lang: Language tag for the name.
            label: Optional human-readable label. Supplying one keeps the
                document clean under the ``ddi.maintainable.labels`` lint rule.
            label_lang: Language tag for ``label``; defaults to ``lang``.
            question: Optional question to link via reference.
            concept: Optional concept to link via reference.
            identifier: Optional identifier; auto-generated if omitted.

        Returns:
            Variable: The newly created variable.
        """
        from .models.logicalproduct import Variable

        study = self._get_study()
        lp = self._ensure_logical_product()
        question_refs: list[Reference] = []
        if question is not None:
            question_refs.append(self._to_reference(question, "QuestionItem"))
        concept_refs: list[Reference] = []
        if concept is not None:
            concept_refs.append(self._to_reference(concept, "Concept"))
        var = Variable(
            agency=study.agency,
            identifier=self._new_identifier(identifier),
            version=study.version or "1",
            names=[
                InternationalString(
                    text=_require_text(name, "name"), lang=lang, child_tag="String"
                )
            ],
            labels=self._labels_for(label, lang, label_lang),
            question_references=question_refs,
            concept_references=concept_refs,
        )
        lp.variables.append(var)
        self._dirty = True
        return var

    def add_concept(
        self,
        name: str,
        *,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        identifier: str | None = None,
    ) -> Concept:
        """Add a concept to the document.

        Args:
            name: The concept name.
            lang: Language tag for the name.
            label: Optional human-readable label. Supplying one keeps the
                document clean under the ``ddi.maintainable.labels`` lint rule.
            label_lang: Language tag for ``label``; defaults to ``lang``.
            identifier: Optional identifier; auto-generated if omitted.

        Returns:
            Concept: The newly created concept.
        """
        from .models.concept import Concept

        study = self._get_study()
        cc = self._ensure_conceptual_component()
        c = Concept(
            agency=study.agency,
            identifier=self._new_identifier(identifier),
            version=study.version or "1",
            names=[
                InternationalString(
                    text=_require_text(name, "name"), lang=lang, child_tag="String"
                )
            ],
            labels=self._labels_for(label, lang, label_lang),
        )
        cc.concepts.append(c)
        cc.has_concept_scheme = True
        self._dirty = True
        return c

    def add_universe(
        self,
        name: str,
        *,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        identifier: str | None = None,
    ) -> Universe:
        """Add a universe to the document.

        Args:
            name: The universe name.
            lang: Language tag for the name.
            label: Optional human-readable label. Supplying one keeps the
                document clean under the ``ddi.maintainable.labels`` lint rule.
            label_lang: Language tag for ``label``; defaults to ``lang``.
            identifier: Optional identifier; auto-generated if omitted.

        Returns:
            Universe: The newly created universe.
        """
        from .models.concept import Universe

        study = self._get_study()
        cc = self._ensure_conceptual_component()
        u = Universe(
            agency=study.agency,
            identifier=self._new_identifier(identifier),
            version=study.version or "1",
            names=[
                InternationalString(
                    text=_require_text(name, "name"), lang=lang, child_tag="String"
                )
            ],
            labels=self._labels_for(label, lang, label_lang),
        )
        cc.universes.append(u)
        cc.has_universe_scheme = True
        self._dirty = True
        return u

    def add_code_list(
        self,
        name: str,
        *,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        identifier: str | None = None,
    ) -> CodeList:
        """Add a code list to the document.

        Args:
            name: The code list name.
            lang: Language tag for the name.
            label: Optional human-readable label. Supplying one keeps the
                document clean under the ``ddi.maintainable.labels`` lint rule.
            label_lang: Language tag for ``label``; defaults to ``lang``.
            identifier: Optional identifier; auto-generated if omitted.

        Returns:
            CodeList: The newly created code list.
        """
        from .models.logicalproduct import CodeList

        study = self._get_study()
        lp = self._ensure_logical_product()
        cl = CodeList(
            agency=study.agency,
            identifier=self._new_identifier(identifier),
            version=study.version or "1",
            names=[
                InternationalString(
                    text=_require_text(name, "name"), lang=lang, child_tag="String"
                )
            ],
            labels=self._labels_for(label, lang, label_lang),
        )
        lp.code_lists.append(cl)
        self._dirty = True
        return cl

    @staticmethod
    def _labels_for(
        label: str | None, lang: str, label_lang: str | None
    ) -> list[InternationalString]:
        """Build the ``labels`` list for a newly created item.

        Returns an empty list when ``label`` is ``None``.
        """
        if label is None:
            return []
        return [InternationalString(text=label, lang=label_lang or lang)]

    @staticmethod
    def _to_reference(
        obj: MaintainableBase | Reference, type_of_object: str
    ) -> Reference:
        """Convert a model object or Reference to a Reference."""
        if isinstance(obj, Reference):
            return obj
        return Reference(
            agency=obj.agency,
            identifier=obj.identifier,
            version=obj.version,
            type_of_object=type_of_object,
        )

    def _get_module(self, slot: _ItemSlot) -> object:
        """Return the parent module for ``slot``, creating it if needed."""
        if slot.module == "su":
            return self._get_study()
        if slot.module == "dc":
            return self._ensure_data_collection()
        if slot.module == "lp":
            return self._ensure_logical_product()
        return self._ensure_conceptual_component()

    def _iter_modules(self, slot: _ItemSlot) -> Iterator:
        """Yield existing parent modules for ``slot`` without creating new ones."""
        study = self._get_study()
        if slot.module == "su":
            yield study
        elif slot.module == "dc":
            yield from study.data_collections
        elif slot.module == "lp":
            yield from study.logical_products
        else:
            yield from study.conceptual_components

    # ------------------------------------------------------------------
    # Generic CRUD — works with any registered item type
    # ------------------------------------------------------------------

    def add_item(
        self,
        item_type: type[MaintainableBase],
        *,
        name: str | None = None,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        identifier: str | None = None,
        **kwargs: object,
    ) -> MaintainableBase:
        """Add an item of any registered type to the document.

        Args:
            item_type: The MaintainableBase subclass to create (e.g.
                ``Category``, ``Instrument``, ``RepresentedVariable``).
            name: Display name for the item. Passed as ``names`` for most
                types, or as ``question_texts`` for ``QuestionItem``.
            lang: Language tag for ``name``.
            label: Optional human-readable label. Supplying one keeps the
                document clean under the ``ddi.maintainable.labels`` lint rule.
                Ignored for types the DDI schema gives no ``r:Label`` slot.
            label_lang: Language tag for ``label``; defaults to ``lang``.
            identifier: Optional identifier; auto-generated if omitted.
            **kwargs: Extra keyword arguments forwarded to the item
                constructor.

        Returns:
            An instance of ``item_type`` that has been added to the document.

        Raises:
            TypeError: If ``item_type`` is not in the item registry.
        """
        registry = _get_item_registry()
        slot = registry.get(item_type)
        if slot is None:
            raise TypeError(f"{item_type.__name__} is not a registered item type.")

        study = self._get_study()
        module = self._get_module(slot)

        ident = self._new_identifier(identifier)
        init_kwargs: dict[str, object] = {
            "agency": study.agency,
            "identifier": ident,
            "version": study.version or "1",
            **kwargs,
        }
        if label is not None and "labels" not in kwargs and item_type.ALLOW_LABELS:
            init_kwargs["labels"] = self._labels_for(label, lang, label_lang)
        if (
            name is not None
            and slot.name_attr is not None
            and slot.name_attr not in kwargs
        ):
            from .models.datacollection import QuestionItem

            if item_type is QuestionItem:
                init_kwargs.setdefault(
                    "question_texts",
                    [
                        InternationalString(
                            text=name,
                            lang=lang,
                            child_tag="Content",
                            is_plain_text=True,
                        )
                    ],
                )
            else:
                init_kwargs[slot.name_attr] = [
                    InternationalString(
                        text=_require_text(name, "name"), lang=lang, child_tag="String"
                    )
                ]

        item = item_type(**init_kwargs)  # type: ignore[arg-type]
        # Types with no Name element (e.g. PhysicalInstance) are titled via a
        # citation; route the convenience ``name`` there when available.
        if (
            name is not None
            and slot.name_attr is None
            and hasattr(item, "set_citation_title")
        ):
            item.set_citation_title(name, lang=lang)
        getattr(module, slot.attr).append(item)
        if slot.scheme_flag is not None:
            setattr(module, slot.scheme_flag, True)
        self._dirty = True
        return item

    def add_record_layout(
        self,
        *,
        identifier: str | None = None,
        logical_record: LogicalRecord | None = None,
    ) -> RecordLayout:
        """Create a record layout that maps variables to positions in a file.

        Builds a backing physical structure and a linked ``RecordLayout``, both
        stored on the study and serialized inside a ``PhysicalDataProduct``. Add
        variable-to-position mappings on the returned layout with
        :meth:`RecordLayout.add_data_item`::

            rl = doc.add_record_layout()
            rl.add_data_item(age.to_reference(), start_position=1, width=2)

        Pass ``logical_record`` (from
        :meth:`DataRelationship.add_logical_record`) to tie the backing physical
        structure to that logical record, so the layout describes a modeled
        record rather than a placeholder.

        Returns:
            RecordLayout: the new, document-attached record layout.
        """
        from .models.base import Reference
        from .models.physical import PhysicalStructure, RecordLayout

        study = self._get_study()
        agency = study.agency
        version = study.version or "1"

        structure = PhysicalStructure(
            agency=agency,
            identifier=str(uuid4()),
            version=version,
            labels=[
                InternationalString(
                    text="Physical structure", lang=self._generated_label_lang
                )
            ],
        )
        study.physical_structures.append(structure)
        study._label_generated_wrappers = True  # type: ignore[attr-defined]

        segment_identifier = str(uuid4())
        if logical_record is not None:
            structure.link_logical_record(
                logical_record.to_reference(), segment_identifier=segment_identifier
            )

        layout = RecordLayout(
            agency=agency,
            identifier=self._new_identifier(identifier),
            version=version,
            array_base=0,
            physical_structure_link_reference=Reference(
                agency=agency,
                identifier=structure.identifier,
                version=version,
                type_of_object="PhysicalStructure",
            ),
            physical_record_segment_used=segment_identifier,
        )
        study.record_layouts.append(layout)
        self._dirty = True
        return layout

    def add_dataset(
        self,
        *,
        name: str | None = None,
        identifier: str | None = None,
        lang: str = "en",
    ) -> DataSet:
        """Create an inline dataset (data values stored in the document).

        Add values on the returned dataset with
        :meth:`DataSet.add_item_value`::

            ds = doc.add_dataset(name="Sample rows")
            ds.add_item_value(age.to_reference(), record="1", value="42")

        Returns:
            DataSet: the new, document-attached inline dataset.
        """
        from .models.base import Reference
        from .models.dataset import DataSet
        from .models.physical import PhysicalStructure

        study = self._get_study()
        agency = study.agency
        version = study.version or "1"

        structure = PhysicalStructure(
            agency=agency,
            identifier=str(uuid4()),
            version=version,
            labels=[
                InternationalString(
                    text="Physical structure", lang=self._generated_label_lang
                )
            ],
        )
        study.physical_structures.append(structure)
        study._label_generated_wrappers = True  # type: ignore[attr-defined]

        names = (
            [
                InternationalString(
                    text=_require_text(name, "name"), lang=lang, child_tag="String"
                )
            ]
            if name is not None
            else []
        )
        dataset = DataSet(
            agency=agency,
            identifier=self._new_identifier(identifier),
            version=version,
            names=names,
            array_base=0,
            physical_structure_link_reference=Reference(
                agency=agency,
                identifier=structure.identifier,
                version=version,
                type_of_object="PhysicalStructure",
            ),
            physical_record_segment_used=str(uuid4()),
        )
        study.datasets.append(dataset)
        study._label_generated_wrappers = True  # type: ignore[attr-defined]
        self._dirty = True
        return dataset

    def add_data_relationship(
        self,
        *,
        identifier: str | None = None,
        label: str | None = None,
        lang: str = "en",
    ) -> DataRelationship:
        """Create a data relationship in the logical product.

        A data relationship groups the dataset's logical records. Add records
        with :meth:`DataRelationship.add_logical_record`::

            dr = doc.add_data_relationship()
            dr.add_logical_record()  # all variables in one rectangular record

        Returns:
            DataRelationship: the new, document-attached data relationship.
        """
        from .models.logicalproduct import DataRelationship

        product = self._ensure_logical_product()
        relationship = DataRelationship(
            agency=product.agency,
            identifier=self._new_identifier(identifier),
            version=product.version or "1",
            labels=self._labels_for(label, lang, None),
        )
        product.data_relationships.append(relationship)
        self._dirty = True
        return relationship

    def add_ncube(
        self,
        *,
        name: str | None = None,
        identifier: str | None = None,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
    ) -> NCube:
        """Create a multidimensional cube (NCube) in the logical product.

        Add axes and measured values on the returned cube::

            cube = doc.add_ncube(name="Population by year and region")
            cube.add_dimension(year.to_reference())
            cube.add_dimension(region.to_reference())
            cube.add_measure(population.to_reference())

        Returns:
            NCube: the new, document-attached cube.
        """
        from .models.logicalproduct import NCube

        product = self._ensure_logical_product()
        names = (
            [
                InternationalString(
                    text=_require_text(name, "name"), lang=lang, child_tag="String"
                )
            ]
            if name is not None
            else []
        )
        cube = NCube(
            agency=product.agency,
            identifier=self._new_identifier(identifier),
            version=product.version or "1",
            names=names,
            labels=self._labels_for(label, lang, label_lang),
        )
        product.n_cubes.append(cube)
        self._dirty = True
        return cube

    def add_group(self, *, identifier: str | None = None):
        """Organize the document's study into a ``Group`` (study series/package).

        The StudyUnit is moved under a new ``<g:Group>`` in the DDIInstance. The
        document stays fully editable: `add_variable`, `add_question`, and the
        rest still resolve to the now-grouped study. Returns the new `Group`.
        """
        from .models.group import Group

        self._flush()
        study = self._get_study()
        agency = study.agency
        version = study.version or "1"

        root = self._inner._root
        study_elements = root.findall(qn(STUDY_UNIT_NS, "StudyUnit"))
        if not study_elements:
            raise ValueError("Document contains no StudyUnit to group.")

        group = Group(
            agency=agency, identifier=self._new_identifier(identifier), version=version
        )
        group_element = group.to_xml()
        for study_element in study_elements:
            root.remove(study_element)
            group_element.append(study_element)
        root.append(group_element)

        # The study elements moved, not changed: keep the cached study attached.
        if self._study_element is not None and any(
            element is self._study_element for element in study_elements
        ):
            self._study_parent = group_element
        else:
            self._study = None
            self._study_parent = None
            self._study_element = None
        self._dirty = False
        return group

    @property
    def groups(self):
        """list[Group]: groups declared directly under the DDIInstance."""
        from .models.group import Group

        self._flush()
        return [
            Group.from_xml(element)
            for element in self._inner._root.findall(qn(GROUP_NS, "Group"))
        ]

    def add_ddi_profile(
        self,
        *,
        name: str | None = None,
        x_path_version: float = 1.0,
        used_xpaths: Iterable[str] | None = None,
        identifier: str | None = None,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
    ) -> DDIProfile:
        """Attach a ``DDIProfile`` declaring which DDI elements are used.

        Pass ``used_xpaths`` for the common case, or call :meth:`DDIProfile.add_used`
        on the returned profile; it is re-serialized on save either way::

            profile = doc.add_ddi_profile(name="Deposit profile")
            profile.add_used("//s:StudyUnit", is_required=True)

        Returns:
            DDIProfile: the new profile, attached at the DDIInstance level.
        """
        from .models.base import InternationalString
        from .models.profile import DDIProfile

        study = self._get_study()
        names = (
            [
                InternationalString(
                    text=_require_text(name, "name"), lang=lang, child_tag="String"
                )
            ]
            if name is not None
            else []
        )
        profile = DDIProfile(
            agency=study.agency,
            identifier=self._new_identifier(identifier),
            version=study.version or "1",
            names=names,
            x_path_version=x_path_version,
            labels=self._labels_for(label, lang, label_lang),
        )
        for xpath in used_xpaths or []:
            profile.add_used(xpath)
        self._profiles.append(profile)
        return profile

    @property
    def ddi_profiles(self):
        """list[DDIProfile]: DDIProfiles declared on the DDIInstance."""
        from .models.profile import DDI_PROFILE_NS, DDIProfile

        self._flush()
        return [
            DDIProfile.from_xml(element)
            for element in self._inner._root.findall(qn(DDI_PROFILE_NS, "DDIProfile"))
        ]

    def _ensure_group(self):
        """Return the group element, creating one (around the study) if needed."""
        self._flush()
        group = self._inner._root.find(qn(GROUP_NS, "Group"))
        if group is None:
            self.add_group()
            group = self._inner._root.find(qn(GROUP_NS, "Group"))
        return group

    def add_study(
        self,
        *,
        title: str,
        identifier: str | None = None,
        lang: str | None = None,
    ) -> StudyUnit:
        """Add an additional StudyUnit to the document's group (a study series).

        The document is organized into a group if it is not already. The new
        study is returned for model-layer building; it is re-serialized into the
        group on save. To target it with the high-level ``add_*`` helpers, use
        the cursor from :meth:`study`::

            wave2 = doc.add_study(title="Wave 2")
            doc.study(wave2.identifier).add_variable(name="income")

        Args:
            title: Title of the new study.
            identifier: Optional identifier; generated when omitted.
            lang: Language of ``title``; defaults to the document's language.

        Returns:
            StudyUnit: the new, group-attached study unit.
        """
        self._ensure_group()
        primary = self._get_study()
        study = _build_study_unit(
            title=title,
            agency=primary.agency,
            identifier=self._new_identifier(identifier),
            version=primary.version or "1",
            lang=lang or self._generated_label_lang,
        )
        self._extra_studies.append(study)
        self._dirty = True
        return study

    def study(self, identifier: str | None = None) -> StudyCursor:
        """Return a cursor whose ``add_*`` helpers target a specific study.

        With no ``identifier`` (or the primary study's id) the cursor targets the
        primary study; otherwise it targets a study previously added with
        :meth:`add_study`. This is how you edit a non-primary study in a
        multi-study series::

            doc.study(wave2.identifier).add_variable(name="income")

        Returns:
            StudyCursor: a cursor bound to the resolved study.

        Raises:
            DDIReferenceError: If no study matches ``identifier`` (a
                :class:`LookupError`).
        """
        primary = self._get_study()
        if identifier is None or identifier == primary.identifier:
            return StudyCursor(self, primary)
        for study in self._extra_studies:
            if study.identifier == identifier:
                return StudyCursor(self, study)
        raise DDIReferenceError(f"No study with identifier {identifier!r}.")

    def add_comparison(
        self,
        *,
        name: str | None = None,
        identifier: str | None = None,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
    ) -> Comparison:
        """Add a Comparison (harmonization maps) to the document's group.

        Map items across studies/versions on the returned comparison::

            cmp = doc.add_comparison(name="2020 to 2021")
            cmp.add_variable_map(age_2020.to_reference(), age_2021.to_reference())

        Returns:
            Comparison: the new, group-attached comparison.
        """
        from .models.comparison import Comparison

        self._ensure_group()
        primary = self._get_study()
        names = (
            [
                InternationalString(
                    text=_require_text(name, "name"), lang=lang, child_tag="String"
                )
            ]
            if name is not None
            else []
        )
        comparison = Comparison(
            agency=primary.agency,
            identifier=self._new_identifier(identifier),
            version=primary.version or "1",
            names=names,
            labels=self._labels_for(label, lang, label_lang),
        )
        self._comparisons.append(comparison)
        self._dirty = True
        return comparison

    @property
    def comparisons(self):
        """list[Comparison]: comparisons declared in the document's group."""
        from .models.comparison import Comparison

        self._flush()
        group = self._inner._root.find(qn(GROUP_NS, "Group"))
        if group is None:
            return []
        return [
            Comparison.from_xml(element)
            for element in group.findall(qn(COMPARATIVE_NS, "Comparison"))
        ]

    # ------------------------------------------------------------------
    # Instance-level packages, archive, and translation information
    # ------------------------------------------------------------------

    def add_archive(
        self,
        *,
        identifier: str | None = None,
        label: str | None = None,
        lang: str = "en",
    ) -> Archive:
        """Attach an ``Archive`` module to the primary study.

        The archive holds archive-specific lifecycle metadata for the study.
        Populate it further on the returned model object; it is re-serialized on
        save.

        Returns:
            Archive: the new archive, attached to the primary StudyUnit.
        """
        from .models.archive import Archive

        study = self._get_study()
        archive = Archive(
            agency=study.agency,
            identifier=self._new_identifier(identifier),
            version=study.version or "1",
            labels=self._labels_for(label, lang, None),
        )
        study.archives.append(archive)
        self._dirty = True
        return archive

    @property
    def archives(self) -> list[Archive]:
        """list[Archive]: Archive modules on the primary study."""
        return list(self._get_study().archives)

    def add_resource_package(self, *, identifier: str | None = None) -> ResourcePackage:
        """Attach a ``ResourcePackage`` (reusable metadata) to the DDIInstance.

        Returns:
            ResourcePackage: the new package, at the DDIInstance level.
        """
        from .models.group import ResourcePackage

        study = self._get_study()
        package = ResourcePackage(
            agency=study.agency,
            identifier=self._new_identifier(identifier),
            version=study.version or "1",
        )
        self._resource_packages.append(package)
        self._dirty = True
        return package

    @property
    def resource_packages(self) -> list[ResourcePackage]:
        """list[ResourcePackage]: ResourcePackages on the DDIInstance."""
        from .models.group import ResourcePackage

        self._flush()
        return [
            ResourcePackage.from_xml(element)
            for element in self._inner._root.findall(qn(GROUP_NS, "ResourcePackage"))
        ]

    def add_local_holding_package(
        self,
        *,
        depository_study_unit: MaintainableBase | Reference | None = None,
        identifier: str | None = None,
    ) -> LocalHoldingPackage:
        """Attach a ``LocalHoldingPackage`` recording a local holding.

        A local holding package references the deposited object it holds. By
        default it points at the primary study; pass ``depository_study_unit`` to
        reference a different study unit.

        Returns:
            LocalHoldingPackage: the new package, at the DDIInstance level.
        """
        from .models.group import LocalHoldingPackage

        study = self._get_study()
        if depository_study_unit is not None:
            ref = self._to_reference(depository_study_unit, "StudyUnit")
        else:
            ref = Reference(
                agency=study.agency,
                identifier=study.identifier,
                version=study.version or "1",
                type_of_object="StudyUnit",
            )
        package = LocalHoldingPackage(
            agency=study.agency,
            identifier=self._new_identifier(identifier),
            version=study.version or "1",
            depository_study_unit_references=[ref],
        )
        self._local_holding_packages.append(package)
        self._dirty = True
        return package

    @property
    def local_holding_packages(self) -> list[LocalHoldingPackage]:
        """list[LocalHoldingPackage]: LocalHoldingPackages on the DDIInstance."""
        from .models.group import LocalHoldingPackage

        self._flush()
        return [
            LocalHoldingPackage.from_xml(element)
            for element in self._inner._root.findall(
                qn(GROUP_NS, "LocalHoldingPackage")
            )
        ]

    def add_translation_information(
        self,
        *,
        languages: Iterable[str] | None = None,
        description: str | None = None,
        lang: str = "en",
    ) -> TranslationInformation:
        """Set the DDIInstance ``TranslationInformation``.

        Describes which languages are involved in translating the instance, with
        an optional description. Replaces any existing translation information.

        Returns:
            TranslationInformation: the translation information element.
        """
        from .models.instance import TranslationInformation

        info = TranslationInformation(
            languages=list(languages or []),
            description=description,
            description_lang=lang,
            lang=lang,
        )
        self._translation_information = info
        self._dirty = True
        return info

    @property
    def translation_information(self) -> TranslationInformation | None:
        """TranslationInformation | None: the instance's translation info."""
        from .models.instance import TranslationInformation

        self._flush()
        element = self._inner._root.find(qn(INSTANCE_NS, "TranslationInformation"))
        if element is None:
            return None
        return TranslationInformation.from_xml(element)

    def items(self, item_type: type[MaintainableBase]) -> list[MaintainableBase]:
        """Return all items of ``item_type`` in the document.

        Args:
            item_type: The MaintainableBase subclass to query (e.g.
                ``Category``, ``Instrument``, ``RepresentedVariable``).

        Returns:
            list: All items of the requested type.

        Raises:
            TypeError: If ``item_type`` is not in the item registry.
        """
        registry = _get_item_registry()
        slot = registry.get(item_type)
        if slot is None:
            raise TypeError(f"{item_type.__name__} is not a registered item type.")
        result: list[MaintainableBase] = []
        for module in self._iter_modules(slot):
            values = getattr(module, slot.attr)
            if slot.filter_type is not None:
                values = [v for v in values if isinstance(v, slot.filter_type)]
            result.extend(values)
        return result

    # ------------------------------------------------------------------
    # Convenience properties — shortcuts for the most common types
    # ------------------------------------------------------------------

    @property
    def questions(self) -> list[QuestionItem]:
        """list[QuestionItem]: All questions in the document."""
        from .models.datacollection import QuestionItem

        return self.items(QuestionItem)  # type: ignore[return-value]

    @property
    def variables(self) -> list[Variable]:
        """list[Variable]: All variables in the document."""
        from .models.logicalproduct import Variable

        return self.items(Variable)  # type: ignore[return-value]

    @property
    def concepts(self) -> list[Concept]:
        """list[Concept]: All concepts in the document."""
        from .models.concept import Concept

        return self.items(Concept)  # type: ignore[return-value]

    @property
    def universes(self) -> list[Universe]:
        """list[Universe]: All universes in the document."""
        from .models.concept import Universe

        return self.items(Universe)  # type: ignore[return-value]

    @property
    def code_lists(self) -> list[CodeList]:
        """list[CodeList]: All code lists in the document."""
        from .models.logicalproduct import CodeList

        return self.items(CodeList)  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Find / Remove — scan all registered types
    # ------------------------------------------------------------------

    def _new_identifier(self, identifier: str | None) -> str:
        """Return ``identifier``, or a fresh UUID when it is ``None``.

        Raises:
            DuplicateIdentifierError: If ``identifier`` is already used by an
                item in the document.
            ValueError: If ``identifier`` is an empty string.
        """
        if identifier is None:
            return str(uuid4())
        if not identifier.strip():
            raise ValueError("identifier must be a non-empty string.")
        if self.find(identifier) is not None:
            raise DuplicateIdentifierError(
                f"Identifier {identifier!r} is already used in this document."
            )
        return identifier

    def _studies(self) -> list[StudyUnit]:
        """Return the primary study followed by any studies added to the group."""
        return [self._get_study(), *self._extra_studies]

    def _iter_item_slots(self) -> Iterator[tuple[list, Any]]:
        """Yield ``(container, item)`` for every identified item in every study.

        Walks the model graph, so items outside the item registry (data sets,
        NCubes, physical structures) are reached as well.
        """
        seen: set[int] = set()
        pending: list[object] = list(self._studies())
        while pending:
            node = pending.pop()
            if id(node) in seen or not dataclasses.is_dataclass(node):
                continue
            seen.add(id(node))
            for spec in dataclasses.fields(node):
                value = getattr(node, spec.name, None)
                if isinstance(value, list):
                    for entry in value:
                        if _is_identified_item(entry):
                            yield value, entry
                            pending.append(entry)
                elif _is_identified_item(value):
                    pending.append(value)

    def find(self, identifier: str | None) -> Any | None:
        """Find an item by identifier in any study of the document.

        Args:
            identifier: The identifier to search for.

        Returns:
            The matching model object, or ``None`` (always ``None`` when
            ``identifier`` is ``None``).
        """
        if identifier is None:
            return None
        for study in self._studies():
            if study.identifier == identifier:
                return study
        for _, item in self._iter_item_slots():
            if item.identifier == identifier:
                return item
        return None

    def remove(self, identifier: str | None) -> bool:
        """Remove an item by identifier from any study of the document.

        References to the removed item elsewhere in the document are left in
        place; :meth:`validate` reports them as dangling.

        Args:
            identifier: The identifier of the item to remove.

        Returns:
            bool: True if an item was removed, False if not found.
        """
        if identifier is None:
            return False
        for container, item in self._iter_item_slots():
            if item.identifier == identifier:
                container.remove(item)
                self._dirty = True
                return True
        return False

    # ------------------------------------------------------------------
    # Persistence & validation
    # ------------------------------------------------------------------

    def save(self, path: str | Path, *, pretty_print: bool = True) -> None:
        """Save the document to an XML file.

        Args:
            path: Filesystem path to write to.
            pretty_print: Format the output for readability.

        Warns:
            DDIReferenceWarning: If a reference in the study points at an item
                the document does not contain.
        """
        self._flush(check_references=True)
        Path(path).write_bytes(
            self._serialize(pretty_print=pretty_print).encode("utf-8")
        )

    def to_xml(self, *, pretty_print: bool = True) -> str:
        """Serialize the document to an XML string.

        Args:
            pretty_print: Format the output for readability.

        Returns:
            str: UTF-8 XML representation, including the XML declaration.
        """
        self._flush()
        return self._serialize(pretty_print=pretty_print)

    def _serialize(self, *, pretty_print: bool) -> str:
        """Render the already-flushed XML tree as a string."""
        # ``_finalize_document`` normalizes the declaration and trailing newline
        # so the output does not depend on which XML backend is installed.
        from .io import _finalize_document

        return _finalize_document(
            self._inner.to_xml(pretty_print=pretty_print),
            pretty_print=pretty_print,
            xml_declaration=True,
            encoding="utf-8",
        ).decode("utf-8")

    def validate(self) -> list:
        """Validate the document against the DDI schema.

        Returns:
            list: Schema validation issues; empty if valid.
        """
        self._flush()
        return self._inner.validate()

    def lint(self, rules: Sequence[str] | None = None) -> list[LintFinding]:
        """Run the lint rules against the document.

        Args:
            rules: Rule identifiers to run; ``None`` runs the default set.

        Returns:
            list[LintFinding]: Findings; empty when the document is clean.
        """
        self._flush()
        return self._inner.lint(rules=rules)

    @property
    def study_unit(self) -> StudyUnit:
        """StudyUnit: The document's active :class:`StudyUnit` model object.

        Use this to reach study-level metadata the CRUD helpers do not cover ---
        versioning (:meth:`~MaintainableBase.increment_minor_version`), version
        rationales, custom properties on the study itself.

        The object is live: mutating it changes the document, and the changes
        are serialized by :meth:`save`, :meth:`to_xml` and :meth:`validate`.

        Raises:
            DDIModelError: If the document contains no StudyUnit.

        Example:
            >>> import ddi_l as ddi
            >>> doc = ddi.new_study(title="My Survey", agency="example.org")
            >>> doc.study_unit.increment_minor_version()
        """
        return self._get_study()

    @property
    def inner(self) -> DDIDocument:
        """DDIDocument: The underlying XML-level document, for advanced use.

        Accessing it hands the XML tree to the caller: pending edits are
        written out and model objects obtained earlier from this
        :class:`Document` are detached, so later XML edits are picked up.
        """
        self._release_study()
        return self._inner


class StudyCursor:
    """A handle to one study whose ``add_*`` helpers target that study.

    Obtained from :meth:`Document.study`. Each method forwards to the matching
    :class:`Document` helper with this cursor's study as the target, so the same
    validation and serialization apply. This is how you edit a non-primary study
    in a multi-study series.
    """

    def __init__(self, document: Document, study: StudyUnit) -> None:
        self._document = document
        self._study = study

    def __repr__(self) -> str:
        return f"StudyCursor(identifier={self._study.identifier!r})"

    @property
    def study_unit(self) -> StudyUnit:
        """StudyUnit: the study this cursor targets."""
        return self._study

    @property
    def identifier(self) -> str | None:
        """Return the identifier of the targeted study (or ``None``)."""
        return self._study.identifier

    def add_question(
        self,
        text: str,
        *,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        identifier: str | None = None,
    ) -> QuestionItem:
        """Add a question to this study (see :meth:`Document.add_question`)."""
        with self._document._use_study(self._study):
            return self._document.add_question(
                text,
                lang=lang,
                label=label,
                label_lang=label_lang,
                identifier=identifier,
            )

    def add_variable(
        self,
        name: str,
        *,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        question: QuestionItem | Reference | None = None,
        concept: Concept | Reference | None = None,
        identifier: str | None = None,
    ) -> Variable:
        """Add a variable to this study (see :meth:`Document.add_variable`)."""
        with self._document._use_study(self._study):
            return self._document.add_variable(
                name,
                lang=lang,
                label=label,
                label_lang=label_lang,
                question=question,
                concept=concept,
                identifier=identifier,
            )

    def add_concept(
        self,
        name: str,
        *,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        identifier: str | None = None,
    ) -> Concept:
        """Add a concept to this study (see :meth:`Document.add_concept`)."""
        with self._document._use_study(self._study):
            return self._document.add_concept(
                name,
                lang=lang,
                label=label,
                label_lang=label_lang,
                identifier=identifier,
            )

    def add_universe(
        self,
        name: str,
        *,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        identifier: str | None = None,
    ) -> Universe:
        """Add a universe to this study (see :meth:`Document.add_universe`)."""
        with self._document._use_study(self._study):
            return self._document.add_universe(
                name,
                lang=lang,
                label=label,
                label_lang=label_lang,
                identifier=identifier,
            )

    def add_code_list(
        self,
        name: str,
        *,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        identifier: str | None = None,
    ) -> CodeList:
        """Add a code list to this study (see :meth:`Document.add_code_list`)."""
        with self._document._use_study(self._study):
            return self._document.add_code_list(
                name,
                lang=lang,
                label=label,
                label_lang=label_lang,
                identifier=identifier,
            )

    def add_item(
        self,
        item_type: type[MaintainableBase],
        *,
        name: str | None = None,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
        identifier: str | None = None,
        **kwargs: object,
    ) -> MaintainableBase:
        """Add any registered item to this study (see :meth:`Document.add_item`)."""
        with self._document._use_study(self._study):
            return self._document.add_item(
                item_type,
                name=name,
                lang=lang,
                label=label,
                label_lang=label_lang,
                identifier=identifier,
                **kwargs,
            )

    def add_ncube(
        self,
        *,
        name: str | None = None,
        identifier: str | None = None,
        lang: str = "en",
        label: str | None = None,
        label_lang: str | None = None,
    ) -> NCube:
        """Add an NCube to this study (see :meth:`Document.add_ncube`)."""
        with self._document._use_study(self._study):
            return self._document.add_ncube(
                name=name,
                identifier=identifier,
                lang=lang,
                label=label,
                label_lang=label_lang,
            )

    def add_data_relationship(
        self,
        *,
        identifier: str | None = None,
        label: str | None = None,
        lang: str = "en",
    ) -> DataRelationship:
        """Add a data relationship (see :meth:`Document.add_data_relationship`)."""
        with self._document._use_study(self._study):
            return self._document.add_data_relationship(
                identifier=identifier, label=label, lang=lang
            )

    def add_record_layout(
        self,
        *,
        identifier: str | None = None,
        logical_record: LogicalRecord | None = None,
    ) -> RecordLayout:
        """Add a record layout (see :meth:`Document.add_record_layout`)."""
        with self._document._use_study(self._study):
            return self._document.add_record_layout(
                identifier=identifier, logical_record=logical_record
            )

    def add_dataset(
        self,
        *,
        name: str | None = None,
        identifier: str | None = None,
        lang: str = "en",
    ) -> DataSet:
        """Add an inline dataset (see :meth:`Document.add_dataset`)."""
        with self._document._use_study(self._study):
            return self._document.add_dataset(
                name=name, identifier=identifier, lang=lang
            )

    def add_archive(
        self,
        *,
        identifier: str | None = None,
        label: str | None = None,
        lang: str = "en",
    ) -> Archive:
        """Add an archive to this study (see :meth:`Document.add_archive`)."""
        with self._document._use_study(self._study):
            return self._document.add_archive(
                identifier=identifier, label=label, lang=lang
            )


def _build_study_unit(
    *,
    title: str,
    agency: str | None,
    identifier: str,
    version: str,
    lang: str,
) -> StudyUnit:
    """Build the StudyUnit that ``new_study`` and ``add_study`` both create.

    The title is written to ``r:Citation/r:Title`` and kept as the study's
    abstract, both tagged with ``lang``.
    """
    study = StudyUnit(
        agency=agency,
        identifier=identifier,
        version=version,
        abstracts=[InternationalString(text=_require_text(title, "title"), lang=lang)],
    )
    citation = create_element(qn(REUSABLE_NS, "Citation"))
    citation.append(_create_international_string("Title", title, lang=lang))
    study.citations.append(citation)
    study.VALIDATE_ON_SERIALIZE = False  # type: ignore[misc]
    return study


def new_study(
    *,
    title: str,
    agency: str,
    identifier: str | None = None,
    version: str = "1",
    lang: str = "en",
) -> Document:
    """Create a new DDI document with a StudyUnit.

    Args:
        title: Human-readable title for the study.
        agency: Maintenance agency responsible for the study.
        identifier: Optional identifier; auto-generated if omitted.
        version: Version string for the study.
        lang: Language tag for the study's title and abstract, and for the
            labels put on the module and scheme wrappers the helpers generate.

    Returns:
        Document: A new document ready for adding content.

    Example:
        >>> import ddi_l as ddi
        >>> doc = ddi.new_study(title="My Survey", agency="example.org")
    """
    doc_id = identifier or str(uuid4())
    ddi_doc = DDIDocument.create(
        agency=agency,
        identifier=doc_id,
        version=version,
        title=title,
        title_language=lang,
        build_index=False,
    )
    study = _build_study_unit(
        title=title,
        agency=agency,
        identifier=str(uuid4()),
        version=version,
        lang=lang,
    )
    element = ddi_doc.add_study_unit(study)
    doc = Document(ddi_doc)
    doc._generated_label_lang = lang
    doc._study = study
    # Pin the element the study occupies so the first flush replaces it rather
    # than looking it up by identity -- a version bump before the first save
    # would otherwise append a second StudyUnit next to the stale one.
    doc._study_parent = ddi_doc._root
    doc._study_element = element
    doc._dirty = True
    return doc


def open_ddi(
    path: str | Path,
    *,
    validate: bool = False,
) -> Document:
    """Open a DDI XML file.

    Args:
        path: Filesystem path to read.
        validate: Whether to validate against the DDI schema on load.

    Returns:
        Document: The parsed document.

    Example:
        >>> import ddi_l as ddi
        >>> doc = ddi.open_ddi("study.xml")
    """
    ddi_doc = DDIDocument.from_xml(Path(path), validate=validate, build_index=False)
    return Document(ddi_doc)


__all__ = [
    "DEFAULT_NSMAP",
    "INSTANCE_NS",
    "REUSABLE_NS",
    "XSI_NS",
    "DDIDocument",
    "DDIFragment",
    "Document",
    "MaintainableIdentifier",
    "MaintainableT",
    "new_study",
    "open_ddi",
]
_DEFAULT_NS_MAP: Mapping[str | None, str] = DEFAULT_NSMAP
