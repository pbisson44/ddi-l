"""Wrappers for the DDI DataCollection module."""

from __future__ import annotations

import typing
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field, is_dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
)
from uuid import UUID, uuid5

from ..._etree import Element, cleanup_namespaces, create_element
from ...constants import DATA_COLLECTION_NS, IDENTIFIER_NAMESPACE, REUSABLE_NS, XML_NS
from ...exceptions import ModelValidationError
from ...namespaces import NamespaceBindings, build_namespace_map
from .._generated.datacollection import (
    CollectionEventFields,
    ComputationItemFields,
    DataCaptureDevelopmentFields,
    GeneralInstructionFields,
    GenerationInstructionFields,
    InstructionFields,
    InstructionGroupFields,
    InstrumentFields,
    InterviewerInstructionSchemeFields,
    ProcessingEventSchemeFields,
    ProcessingInstructionGroupFields,
    ProcessingInstructionSchemeFields,
    QuestionConstructFields,
    QuestionSchemeFields,
    SamplingInformationGroupFields,
    SamplingInformationSchemeFields,
    SamplingPlanFields,
)
from ..base import (
    CodeValue,
    InternationalString,
    MaintainableBase,
    MaintainableInitData,
    Reference,
    UserAttributePair,
    UserID,
    VersionRationale,
    apply_other_attributes,
    clone_element,
    collect_other_attributes,
    preserve_unrecognized_children,
    qn,
    should_validate_on_serialize,
)

if TYPE_CHECKING:
    from ...maintainable_registry import MaintainableRegistry
    from ..methodology import Methodology

__all__ = [
    "CollectionActivity",
    "CollectionEvent",
    "ComputationItem",
    "DataCaptureDevelopment",
    "DataCaptureMethod",
    "DataCollection",
    "DynamicText",
    "ElseIf",
    "GeneralInstruction",
    "GenerationInstruction",
    "GridDimension",
    "IfThenElse",
    "Instruction",
    "InstructionGroup",
    "Instrument",
    "InterviewerInstructionReference",
    "InterviewerInstructionScheme",
    "ObservationPlan",
    "OutParameter",
    "ProcessingEvent",
    "ProcessingEventScheme",
    "ProcessingInstructionGroup",
    "ProcessingInstructionScheme",
    "QuestionBlock",
    "QuestionConstruct",
    "QuestionGrid",
    "QuestionGroup",
    "QuestionItem",
    "QuestionScheme",
    "SamplingInformationGroup",
    "SamplingInformationScheme",
    "SamplingPlan",
    "Sequence",
    "SourceReference",
    "StatementItem",
]

_REFERENCE_NAMESPACE = IDENTIFIER_NAMESPACE
_INLINE_FRAGMENT_TYPES = {
    "QuestionItem",
    "QuestionGrid",
    "QuestionBlock",
    "QuestionGroup",
}


class VersionableInitData(MaintainableInitData, total=False):
    """Initialization payload returned by :func:`_collect_versionable_common`."""

    user_ids: list[UserID]
    user_attribute_pairs: list[UserAttributePair]
    version_responsibility: str | None
    version_rationales: list[VersionRationale]
    based_on_reference: Reference | None
    based_on_version_date: str | None


def _is_uuid_like(value: str | None) -> bool:
    if value is None:
        return False
    try:
        UUID(value)
    except (TypeError, ValueError):
        return False
    return True


def _maybe_generate_reference_urn(reference: Reference) -> str | None:
    """Ensure ``reference`` has a stable URN when only human readable IDs exist."""
    canonical = reference._canonical_urn()
    if canonical is None:
        return None
    if reference.agency is None or reference.identifier is None:
        return None
    if _is_uuid_like(reference.identifier):
        if reference.urn and reference.urn != canonical:
            reference.urn = canonical
        return None
    version = reference.version or "1"
    generated_identifier = str(
        uuid5(_REFERENCE_NAMESPACE, f"{reference.agency}:{reference.identifier}")
    )
    reference.urn = f"urn:ddi:{reference.agency}:{generated_identifier}:{version}"
    if reference.type_of_object in _INLINE_FRAGMENT_TYPES:
        reference._auto_identifier = None
        return None
    reference._auto_identifier = generated_identifier
    return generated_identifier


def _normalize_reference_collections(
    value: object,
    seen: set[int] | None = None,
    generated_identifiers: dict[tuple[str | None, str | None, str | None], str]
    | None = None,
    pending: list[tuple[str | None, str | None, str | None, MaintainableBase]]
    | None = None,
) -> None:
    """Recursively normalise URNs for :class:`Reference` instances."""
    if value is None:
        return
    if seen is None:
        seen = set()
        root_call = True
    else:
        root_call = False
    if generated_identifiers is None:
        generated_identifiers = {}
    if pending is None:
        pending = []
    obj_id = id(value)
    if obj_id in seen:
        return
    seen.add(obj_id)

    if isinstance(value, Reference):
        generated_identifier = _maybe_generate_reference_urn(value)
        if generated_identifier:
            key = (value.agency, value.identifier, value.type_of_object)
            generated_identifiers[key] = generated_identifier
            generated_identifiers[(value.agency, value.identifier, None)] = (
                generated_identifier
            )
        return

    if isinstance(value, list):
        for item in value:
            if isinstance(item, Element):
                continue
            _normalize_reference_collections(item, seen, generated_identifiers, pending)
        return

    if isinstance(value, dict):
        for item in value.values():
            _normalize_reference_collections(item, seen, generated_identifiers, pending)
        return

    # ``InterviewerInstructionReference`` and similar wrappers expose a ``reference``
    # attribute which should be normalised as well.
    reference_attr = getattr(value, "reference", None)
    if isinstance(reference_attr, Reference):
        generated_identifier = _maybe_generate_reference_urn(reference_attr)
        if generated_identifier:
            key = (
                reference_attr.agency,
                reference_attr.identifier,
                reference_attr.type_of_object,
            )
            generated_identifiers[key] = generated_identifier
            generated_identifiers[
                (
                    reference_attr.agency,
                    reference_attr.identifier,
                    None,
                )
            ] = generated_identifier

    if is_dataclass(value):
        for item in vars(value).values():
            if isinstance(item, Element):
                continue
            _normalize_reference_collections(item, seen, generated_identifiers, pending)
        if isinstance(value, MaintainableBase):
            identifier_attr = getattr(value, "identifier", None)
            agency_attr = getattr(value, "agency", None)
            type_name = value.__class__.__name__
            generated_identifier = None
            if (
                agency_attr
                and identifier_attr
                and not _is_uuid_like(identifier_attr)
                and type_name not in _INLINE_FRAGMENT_TYPES
            ):
                key = (agency_attr, identifier_attr, type_name)
                generated_identifier = generated_identifiers.get(key)
                if generated_identifier is None:
                    generated_identifier = generated_identifiers.get(
                        (agency_attr, identifier_attr, None)
                    )
                if generated_identifier is None:
                    generated_identifier = str(
                        uuid5(
                            _REFERENCE_NAMESPACE,
                            f"{agency_attr}:{identifier_attr}",
                        )
                    )
                generated_identifiers[key] = generated_identifier
                generated_identifiers[(agency_attr, identifier_attr, None)] = (
                    generated_identifier
                )
            value._auto_identifier = generated_identifier
        else:
            identifier_attr = getattr(value, "identifier", None)
            agency_attr = getattr(value, "agency", None)
            type_name = value.__class__.__name__
            if hasattr(value, "identifier") and hasattr(value, "agency"):
                if (
                    agency_attr
                    and identifier_attr
                    and not _is_uuid_like(identifier_attr)
                    and type_name not in _INLINE_FRAGMENT_TYPES
                ):
                    generated_identifier = str(
                        uuid5(_REFERENCE_NAMESPACE, f"{agency_attr}:{identifier_attr}")
                    )
                    value._auto_identifier = generated_identifier  # type: ignore[union-attr]
                else:
                    value._auto_identifier = None  # type: ignore[union-attr]
    if root_call and pending:
        for pending_agency, pending_identifier, pending_type, maintainable in pending:
            generated_identifier = generated_identifiers.get(
                (pending_agency, pending_identifier, pending_type)
            )
            if generated_identifier is None:
                generated_identifier = generated_identifiers.get(
                    (pending_agency, pending_identifier, None)
                )
            if generated_identifier:
                maintainable._auto_identifier = generated_identifier


def _normalize_data_appraisal_information(element: Element) -> Element:
    """Ensure ``SamplingError`` children use the data collection namespace."""
    sampling_errors = list(element.findall(f".//{qn(REUSABLE_NS, 'SamplingError')}"))
    if not sampling_errors:
        return clone_element(element)

    normalized = clone_element(element)
    for node in normalized.findall(f".//{qn(REUSABLE_NS, 'SamplingError')}"):
        node.tag = qn(DATA_COLLECTION_NS, "SamplingError")
    return normalized


@dataclass
class VersionableMaintainableBase(MaintainableBase):
    """Maintainable structure extended with reusable version metadata."""

    user_ids: list[UserID] = field(default_factory=list)
    user_attribute_pairs: list[UserAttributePair] = field(default_factory=list)
    version_responsibility: str | None = None
    version_rationales: list[VersionRationale] = field(default_factory=list)
    based_on_reference: Reference | None = None
    based_on_version_date: str | None = None

    @classmethod
    def _collect_versionable_common(
        cls,
        element: Element,
        *,
        recognized_children: Iterable[str] | None = None,
    ) -> VersionableInitData:
        recognized = {
            qn(REUSABLE_NS, "UserID"),
            qn(REUSABLE_NS, "UserAttributePair"),
            qn(REUSABLE_NS, "VersionResponsibility"),
            qn(REUSABLE_NS, "VersionRationale"),
            qn(REUSABLE_NS, "BasedOnReference"),
            qn(REUSABLE_NS, "BasedOnVersionDate"),
        }
        if recognized_children:
            recognized.update(recognized_children)
        base_data = super()._collect_common(element, recognized_children=recognized)
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
        based_on_reference_el = element.find(qn(REUSABLE_NS, "BasedOnReference"))
        based_on_reference = (
            Reference.from_xml(based_on_reference_el)
            if based_on_reference_el is not None
            else None
        )
        based_on_version_date_el = element.find(qn(REUSABLE_NS, "BasedOnVersionDate"))
        versionable_data: VersionableInitData = {
            **base_data,
            "user_ids": user_ids,
            "user_attribute_pairs": user_attribute_pairs,
            "version_responsibility": (
                version_responsibility_el.text
                if version_responsibility_el is not None
                else None
            ),
            "version_rationales": version_rationales,
            "based_on_reference": based_on_reference,
            "based_on_version_date": (
                based_on_version_date_el.text
                if based_on_version_date_el is not None
                else None
            ),
        }
        return versionable_data

    def _append_versionable_common(self, element: Element) -> None:
        children: list[Element] = []
        for user_id in self.user_ids:
            children.append(user_id.to_xml())
        for pair in self.user_attribute_pairs:
            children.append(pair.to_xml())
        if self.version_responsibility:
            responsibility_el = create_element(qn(REUSABLE_NS, "VersionResponsibility"))
            responsibility_el.text = self.version_responsibility
            children.append(responsibility_el)
        for rationale in self.version_rationales:
            children.append(rationale.to_xml())
        if self.based_on_reference is not None:
            children.append(self.based_on_reference.to_xml("BasedOnReference"))
        if self.based_on_version_date is not None:
            based_on_date_el = create_element(qn(REUSABLE_NS, "BasedOnVersionDate"))
            based_on_date_el.text = self.based_on_version_date
            children.append(based_on_date_el)
        # VersionableType's children precede the type's own content, so they go
        # ahead of the r:Label / r:Description _build_base_element already
        # emitted. Appending them after it made every question with a version
        # responsibility or rationale and a label fail schema validation.
        own_content = {qn(REUSABLE_NS, "Label"), qn(REUSABLE_NS, "Description")}
        position = next(
            (index for index, child in enumerate(element) if child.tag in own_content),
            len(element),
        )
        for offset, child in enumerate(children):
            element.insert(position + offset, child)


def _parse_bool_attribute(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() == "true"


def _format_bool_attribute(value: bool | None) -> str | None:
    if value is None:
        return None
    return "true" if value else "false"


@dataclass
class DynamicText:
    """Wrapper for ``d:DynamicTextType`` elements with literal content."""

    texts: list[InternationalString] = field(default_factory=list)
    audience_language: str | None = None
    is_structure_required: bool | None = None
    other_elements: list[Element] = field(default_factory=list)
    _source_tag: str | None = field(default=None, repr=False, compare=False)

    @classmethod
    def from_xml(cls, element: Element) -> DynamicText:
        texts: list[InternationalString] = []
        recognized_children = {qn(DATA_COLLECTION_NS, "LiteralText")}
        for literal in element.findall(qn(DATA_COLLECTION_NS, "LiteralText")):
            text_el = literal.find(qn(DATA_COLLECTION_NS, "Text"))
            if text_el is None:
                continue
            found = InternationalString.from_container(text_el)
            if found:
                texts.extend(found)
                continue
            lang = text_el.get(qn(XML_NS, "lang")) or "en"
            is_plain_raw = text_el.get("isPlainText")
            is_plain_text = None
            if is_plain_raw is not None:
                is_plain_text = is_plain_raw.lower() == "true"
            texts.append(
                InternationalString(
                    text=text_el.text or "",
                    lang=lang,
                    child_tag="Content",
                    is_plain_text=is_plain_text,
                )
            )
        other_elements = [
            clone_element(child)
            for child in element
            if child.tag not in recognized_children
        ]
        return cls(
            texts=texts,
            audience_language=element.get("audienceLanguage"),
            is_structure_required=_parse_bool_attribute(
                element.get("isStructureRequired")
            ),
            other_elements=other_elements,
            _source_tag=element.tag,
        )

    def to_xml(self, tag: str | None = None) -> Element:
        effective_tag = tag or self._source_tag
        if effective_tag is None:
            raise ValueError("DynamicText.to_xml requires a tag")
        if not effective_tag.startswith("{"):
            effective_tag = qn(DATA_COLLECTION_NS, effective_tag)
        element = create_element(effective_tag)
        if self.audience_language:
            element.set("audienceLanguage", self.audience_language)
        if self.is_structure_required is not None:
            element.set(
                "isStructureRequired",
                _format_bool_attribute(self.is_structure_required),  # type: ignore[arg-type]
            )
        for string in self.texts:
            literal = create_element(qn(DATA_COLLECTION_NS, "LiteralText"))
            text_el = create_element(qn(DATA_COLLECTION_NS, "Text"))
            if string.lang:
                text_el.set(qn(XML_NS, "lang"), string.lang)
            if string.is_plain_text is not None:
                text_el.set(
                    "isPlainText",
                    "true" if string.is_plain_text else "false",
                )
            text_el.text = string.text
            literal.append(text_el)
            element.append(literal)
        for child in self.other_elements:
            element.append(clone_element(child))
        return element


@dataclass
class GridDimension:
    """Representation of ``d:GridDimension`` entries within question grids."""

    rank: int
    code_domain: Element | None = None
    roster: Element | None = None
    create_summary: Element | None = None
    display_code: bool | None = None
    display_label: bool | None = None
    other_elements: list[Element] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GridDimension")

    @classmethod
    def from_xml(cls, element: Element) -> GridDimension:
        if element.tag != cls.TAG:
            raise ValueError("Expected a datacollection:GridDimension element.")
        recognized = {
            qn(DATA_COLLECTION_NS, "CodeDomain"),
            qn(DATA_COLLECTION_NS, "Roster"),
            qn(DATA_COLLECTION_NS, "CreateSummary"),
        }
        code_domain_el = element.find(qn(DATA_COLLECTION_NS, "CodeDomain"))
        roster_el = element.find(qn(DATA_COLLECTION_NS, "Roster"))
        create_summary_el = element.find(qn(DATA_COLLECTION_NS, "CreateSummary"))
        other_elements = [
            clone_element(child) for child in element if child.tag not in recognized
        ]
        rank_attr = element.get("rank")
        if rank_attr is None:
            raise ValueError("GridDimension requires a rank attribute.")
        return cls(
            rank=int(rank_attr),
            code_domain=clone_element(code_domain_el)
            if code_domain_el is not None
            else None,
            roster=clone_element(roster_el) if roster_el is not None else None,
            create_summary=clone_element(create_summary_el)
            if create_summary_el is not None
            else None,
            display_code=_parse_bool_attribute(element.get("displayCode")),
            display_label=_parse_bool_attribute(element.get("displayLabel")),
            other_elements=other_elements,
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        element.set("rank", str(self.rank))
        if self.display_code is not None:
            formatted = _format_bool_attribute(self.display_code)
            if formatted is not None:
                element.set("displayCode", formatted)
        if self.display_label is not None:
            formatted = _format_bool_attribute(self.display_label)
            if formatted is not None:
                element.set("displayLabel", formatted)
        if self.code_domain is not None:
            domain = clone_element(self.code_domain)
            for reference in domain.findall(qn(REUSABLE_NS, "CodeListReference")):
                if reference.find(qn(REUSABLE_NS, "TypeOfObject")) is None:
                    type_el = create_element(qn(REUSABLE_NS, "TypeOfObject"))
                    type_el.text = "CodeList"
                    reference.append(type_el)
            element.append(domain)
        if self.roster is not None:
            element.append(clone_element(self.roster))
        if self.create_summary is not None:
            element.append(clone_element(self.create_summary))
        for child in self.other_elements:
            element.append(clone_element(child))
        return element


@dataclass
class SourceReference:
    """Representation of ``d:SourceReferenceType`` entries with alias support."""

    reference: Reference
    alias: str | None = None
    other_elements: list[Element] = field(default_factory=list)
    _source_tag: str | None = field(default=None, repr=False, compare=False)

    _REFERENCE_CHILDREN: ClassVar[set[str]] = {
        qn(REUSABLE_NS, "URN"),
        qn(REUSABLE_NS, "Agency"),
        qn(REUSABLE_NS, "ID"),
        qn(REUSABLE_NS, "Version"),
        qn(REUSABLE_NS, "TypeOfObject"),
        qn(REUSABLE_NS, "Alias"),
    }

    @classmethod
    def from_xml(cls, element: Element) -> SourceReference:
        reference = Reference.from_xml(element)
        alias_el = element.find(qn(REUSABLE_NS, "Alias"))
        extras = [
            clone_element(child)
            for child in element
            if child.tag not in cls._REFERENCE_CHILDREN
        ]
        return cls(
            reference=reference,
            alias=alias_el.text if alias_el is not None else None,
            other_elements=extras,
            _source_tag=element.tag,
        )

    def to_xml(self, tag: str | None = None) -> Element:
        effective_tag = tag or self._source_tag
        if effective_tag is None:
            raise ValueError("SourceReference.to_xml requires a tag")
        if effective_tag.startswith("{"):
            ns, local = effective_tag[1:].split("}", 1)
            element = self.reference.to_xml(local, namespace=ns)
        else:
            element = self.reference.to_xml(effective_tag, namespace=DATA_COLLECTION_NS)
        if self.alias is not None:
            alias_el = create_element(qn(REUSABLE_NS, "Alias"))
            alias_el.text = self.alias
            element.append(alias_el)
        for child in self.other_elements:
            element.append(clone_element(child))
        return element


@dataclass
class ControlConstructBase(VersionableMaintainableBase):
    """Shared helpers for control-construct maintainables."""

    construct_names: list[InternationalString] = field(default_factory=list)

    @classmethod
    def _collect_control_common(
        cls,
        element: Element,
        *,
        recognized_children: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        recognized = {qn(DATA_COLLECTION_NS, "ConstructName")}
        if recognized_children:
            recognized.update(recognized_children)
        data: dict[str, Any] = dict(
            cls._collect_versionable_common(element, recognized_children=recognized)
        )
        construct_names: list[InternationalString] = []
        for container in element.findall(qn(DATA_COLLECTION_NS, "ConstructName")):
            construct_names.extend(InternationalString.from_container(container))
        data["construct_names"] = construct_names
        return data

    def _append_control_common(self, element: Element) -> None:
        self._append_versionable_common(element)
        # ConstructName precedes r:Label in every ControlConstruct's content
        # model, so the label has to step aside and come back after it.
        with self._labels_last(element):
            for name in self.construct_names:
                container = create_element(qn(DATA_COLLECTION_NS, "ConstructName"))
                container.append(name.to_child(child_tag="String"))
                element.append(container)


@dataclass
class QuestionMaintainableBase(VersionableMaintainableBase):
    """Common helpers for maintainable question fragments."""

    development_results_references: list[Reference] = field(default_factory=list)

    @classmethod
    def _collect_question_common(
        cls,
        element: Element,
        *,
        recognized_children: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        recognized = {qn(DATA_COLLECTION_NS, "DevelopmentResultsReference")}
        if recognized_children:
            recognized.update(recognized_children)
        data: dict[str, Any] = dict(
            cls._collect_versionable_common(element, recognized_children=recognized)
        )
        references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "DevelopmentResultsReference")
            )
        ]
        other_elements = [
            child
            for child in data.get("other_elements", [])
            if child.tag != qn(DATA_COLLECTION_NS, "DevelopmentResultsReference")
        ]
        data.update(
            {
                "development_results_references": references,
                "other_elements": other_elements,
            }
        )
        return data

    def _append_question_common(self, element: Element) -> None:
        self._append_versionable_common(element)
        for reference in self.development_results_references:
            element.append(
                reference.to_xml(
                    "DevelopmentResultsReference", namespace=DATA_COLLECTION_NS
                )
            )


@dataclass
class Instrument(InstrumentFields):
    """A reusable representation of ``d:Instrument``."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Instrument")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    def iter_control_construct_references(self) -> Iterable[Reference]:
        """Yield the control-construct references in declaration order."""
        if self.control_construct_reference is not None:
            yield self.control_construct_reference

    def control_construct_ids(self) -> list[str]:
        """Return the identifiers referenced by the instrument when available."""
        ref = self.control_construct_reference
        if ref is not None and ref.identifier is not None:
            return [ref.identifier]
        return []


@dataclass
class QuestionItem(QuestionMaintainableBase):
    """Representation of a ``d:QuestionItem`` including dynamic text support."""

    question_texts: list[InternationalString] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    @classmethod
    def from_xml(cls, element: Element) -> QuestionItem:
        recognized = {qn(DATA_COLLECTION_NS, "QuestionText")}
        texts: list[InternationalString] = []
        for container in element.findall(qn(DATA_COLLECTION_NS, "QuestionText")):
            for literal in container.findall(qn(DATA_COLLECTION_NS, "LiteralText")):
                text_el = literal.find(qn(DATA_COLLECTION_NS, "Text"))
                if text_el is None:
                    continue
                found = InternationalString.from_container(text_el)
                if found:
                    texts.extend(found)
                    continue
                lang = text_el.get(qn(XML_NS, "lang")) or "en"
                is_plain_raw = text_el.get("isPlainText")
                is_plain_text = None
                if is_plain_raw is not None:
                    is_plain_text = is_plain_raw.lower() == "true"
                texts.append(
                    InternationalString(
                        text=text_el.text or "",
                        lang=lang,
                        child_tag="Content",
                        is_plain_text=is_plain_text,
                    )
                )
        data = cls._collect_question_common(element, recognized_children=recognized)
        other_elements = [
            child
            for child in data.get("other_elements", [])
            if child.tag != qn(DATA_COLLECTION_NS, "QuestionText")
        ]
        data["other_elements"] = other_elements
        return cls(question_texts=texts, **data)

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_question_common(element)
        if self.question_texts:
            question_text = create_element(qn(DATA_COLLECTION_NS, "QuestionText"))
            for string in self.question_texts:
                literal = create_element(qn(DATA_COLLECTION_NS, "LiteralText"))
                text_el = create_element(qn(DATA_COLLECTION_NS, "Text"))
                if string.lang:
                    text_el.set(qn(XML_NS, "lang"), string.lang)
                if string.is_plain_text is not None:
                    text_el.set(
                        "isPlainText", "true" if string.is_plain_text else "false"
                    )
                text_el.text = string.text
                literal.append(text_el)
                question_text.append(literal)
            element.append(question_text)
        self._append_other_elements(element)
        return element


@dataclass
class QuestionScheme(QuestionSchemeFields):
    """Maintainable representation of ``d:QuestionScheme`` entries."""

    names: list[InternationalString] = field(default_factory=list)
    scheme_references: list[Reference] = field(default_factory=list)
    question_items: list[QuestionItem] = field(default_factory=list)  # type: ignore[assignment]
    question_item_references: list[Reference] = field(default_factory=list)
    question_grids: list[QuestionGrid] = field(default_factory=list)  # type: ignore[assignment]
    question_grid_references: list[Reference] = field(default_factory=list)
    question_blocks: list[QuestionBlock] = field(default_factory=list)  # type: ignore[assignment]
    question_block_references: list[Reference] = field(default_factory=list)
    question_groups: list[QuestionGroup] = field(default_factory=list)  # type: ignore[assignment]
    question_group_references: list[Reference] = field(default_factory=list)
    fragment_sequence: list[QuestionMaintainableBase] = field(
        default_factory=list, repr=False
    )
    reference_order: list[str] = field(default_factory=list, repr=False)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    def __post_init__(self) -> None:
        if not self.fragment_sequence:
            self.fragment_sequence = [
                *self.question_items,
                *self.question_grids,
                *self.question_blocks,
                *self.question_groups,
            ]

        def _suffix(base: str) -> Callable[[int, MaintainableBase], str | None]:
            return lambda index, _child: self._default_child_suffix(base, index)

        self._propagate_child_identification(
            self.question_items,
            identifier_suffix_factory=_suffix("question-item"),
        )
        self._propagate_child_identification(
            self.question_grids,
            identifier_suffix_factory=_suffix("question-grid"),
        )
        self._propagate_child_identification(
            self.question_blocks,
            identifier_suffix_factory=_suffix("question-block"),
        )
        self._propagate_child_identification(
            self.question_groups,
            identifier_suffix_factory=_suffix("question-group"),
        )

    @classmethod
    def from_xml(cls, element: Element) -> QuestionScheme:
        recognized = {
            qn(DATA_COLLECTION_NS, "QuestionSchemeName"),
            qn(REUSABLE_NS, "QuestionSchemeReference"),
            qn(DATA_COLLECTION_NS, "QuestionItem"),
            qn(DATA_COLLECTION_NS, "QuestionItemReference"),
            qn(DATA_COLLECTION_NS, "QuestionGrid"),
            qn(DATA_COLLECTION_NS, "QuestionGridReference"),
            qn(DATA_COLLECTION_NS, "QuestionBlock"),
            qn(DATA_COLLECTION_NS, "QuestionBlockReference"),
            qn(DATA_COLLECTION_NS, "QuestionGroup"),
            qn(DATA_COLLECTION_NS, "QuestionGroupReference"),
        }
        data = cls._collect_common(element, recognized_children=recognized)
        names: list[InternationalString] = []
        scheme_references: list[Reference] = []
        question_items: list[QuestionItem] = []
        question_item_references: list[Reference] = []
        question_grids: list[QuestionGrid] = []
        question_grid_references: list[Reference] = []
        question_blocks: list[QuestionBlock] = []
        question_block_references: list[Reference] = []
        question_groups: list[QuestionGroup] = []
        question_group_references: list[Reference] = []
        reference_order: list[str] = []
        fragment_sequence: list[QuestionMaintainableBase] = []

        for child in element:
            if child.tag == qn(DATA_COLLECTION_NS, "QuestionSchemeName"):
                names.extend(InternationalString.from_container(child))
            elif child.tag == qn(REUSABLE_NS, "QuestionSchemeReference"):
                scheme_references.append(Reference.from_xml(child))
            elif child.tag == qn(DATA_COLLECTION_NS, "QuestionItem"):
                question = QuestionItem.from_xml(child)
                question_items.append(question)
                fragment_sequence.append(question)
            elif child.tag == qn(DATA_COLLECTION_NS, "QuestionItemReference"):
                question_item_references.append(Reference.from_xml(child))
                reference_order.append("QuestionItemReference")
            elif child.tag == qn(DATA_COLLECTION_NS, "QuestionGrid"):
                grid = QuestionGrid.from_xml(child)
                question_grids.append(grid)
                fragment_sequence.append(grid)
            elif child.tag == qn(DATA_COLLECTION_NS, "QuestionGridReference"):
                question_grid_references.append(Reference.from_xml(child))
                reference_order.append("QuestionGridReference")
            elif child.tag == qn(DATA_COLLECTION_NS, "QuestionBlock"):
                block = QuestionBlock.from_xml(child)
                question_blocks.append(block)
                fragment_sequence.append(block)
            elif child.tag == qn(DATA_COLLECTION_NS, "QuestionBlockReference"):
                question_block_references.append(Reference.from_xml(child))
                reference_order.append("QuestionBlockReference")
            elif child.tag == qn(DATA_COLLECTION_NS, "QuestionGroup"):
                group = QuestionGroup.from_xml(child)
                question_groups.append(group)
                fragment_sequence.append(group)
            elif child.tag == qn(DATA_COLLECTION_NS, "QuestionGroupReference"):
                question_group_references.append(Reference.from_xml(child))
                reference_order.append("QuestionGroupReference")

        other_elements = [
            child
            for child in data.get("other_elements", [])
            if child.tag not in recognized
        ]
        data["other_elements"] = other_elements
        return cls(
            names=names,
            scheme_references=scheme_references,
            question_items=question_items,
            question_item_references=question_item_references,
            question_grids=question_grids,
            question_grid_references=question_grid_references,
            question_blocks=question_blocks,
            question_block_references=question_block_references,
            question_groups=question_groups,
            question_group_references=question_group_references,
            fragment_sequence=fragment_sequence,
            reference_order=reference_order,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        for name in self.names:
            container = create_element(qn(DATA_COLLECTION_NS, "QuestionSchemeName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        for reference in self.scheme_references:
            element.append(reference.to_xml("QuestionSchemeReference"))

        def _iter_fragments(
            fragment_type: type[QuestionMaintainableBase],
            fallback: Iterable[QuestionMaintainableBase],
        ) -> Iterable[QuestionMaintainableBase]:
            if self.fragment_sequence:
                for fragment in self.fragment_sequence:
                    if isinstance(fragment, fragment_type):
                        yield fragment
                return
            yield from fallback

        fragment_groups: typing.Sequence[
            tuple[
                type[QuestionMaintainableBase],
                Iterable[QuestionMaintainableBase],
                Iterable[Reference],
                str,
            ]
        ] = [
            (
                QuestionItem,
                tuple(self.question_items),
                self.question_item_references,
                "QuestionItemReference",
            ),
            (
                QuestionGrid,
                tuple(self.question_grids),
                self.question_grid_references,
                "QuestionGridReference",
            ),
            (
                QuestionBlock,
                tuple(self.question_blocks),
                self.question_block_references,
                "QuestionBlockReference",
            ),
            (
                QuestionGroup,
                tuple(self.question_groups),
                self.question_group_references,
                "QuestionGroupReference",
            ),
        ]

        for (
            fragment_type,
            inline_fragments,
            references,
            reference_tag,
        ) in fragment_groups:
            for fragment in _iter_fragments(fragment_type, inline_fragments):
                element.append(fragment.to_xml())
            for reference in references:
                element.append(
                    reference.to_xml(reference_tag, namespace=DATA_COLLECTION_NS)
                )
        self._append_other_elements(element)
        # QuestionSchemeType declares QuestionSchemeName before r:Label, but
        # the label comes from _build_base_element and is appended first.
        self._reorder_children_by_element_order(element)
        return element

    def iter_items(self) -> Iterable[QuestionItem]:
        """Iterate over inline ``QuestionItem`` fragments."""
        return iter(self.question_items)

    def iter_grids(self) -> Iterable[QuestionGrid]:
        """Iterate over inline ``QuestionGrid`` fragments."""
        return iter(self.question_grids)

    def iter_blocks(self) -> Iterable[QuestionBlock]:
        """Iterate over inline ``QuestionBlock`` fragments."""
        return iter(self.question_blocks)

    def iter_groups(self) -> Iterable[QuestionGroup]:
        """Iterate over inline ``QuestionGroup`` fragments."""
        return iter(self.question_groups)

    def iter_fragments(self) -> Iterable[QuestionMaintainableBase]:
        """Iterate over all inline question fragments preserving their order."""
        if self.fragment_sequence:
            yield from self.fragment_sequence
            return
        yield from self.question_items
        yield from self.question_grids
        yield from self.question_blocks
        yield from self.question_groups

    def get_fragment(self, identifier: str) -> QuestionMaintainableBase | None:
        """Return the fragment with ``identifier`` when present."""
        for fragment in self.iter_fragments():
            if fragment.identifier == identifier:
                return fragment
        return None


def _extract_first_text(element: Element) -> str | None:
    """Return the first non-empty text node within ``element``."""
    if element.text and element.text.strip():
        return element.text.strip()
    for child in element:
        value = _extract_first_text(child)
        if value:
            return value
    return None


@dataclass
class InstructionAttachmentLocationNode:
    """Wrapper capturing instruction attachment location content."""

    element: Element
    _text: str | None = field(default=None, repr=False)

    @classmethod
    def from_xml(cls, element: Element) -> InstructionAttachmentLocationNode:
        return cls(element=clone_element(element), _text=_extract_first_text(element))

    @property
    def text(self) -> str | None:
        return (
            self._text if self._text is not None else _extract_first_text(self.element)
        )

    def to_xml(self) -> Element:
        return clone_element(self.element)


@dataclass
class InterviewerInstructionReference:
    """Structured representation of ``d:InterviewerInstructionReference``."""

    reference: Reference
    is_displayed: bool = False
    attachment_locations: list[InstructionAttachmentLocationNode] = field(
        default_factory=list
    )
    other_elements: list[Element] = field(default_factory=list)
    _is_displayed_attribute_present: bool = False
    _source_tag: str | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.attachment_locations:
            return
        normalized: list[InstructionAttachmentLocationNode] = []
        for location in self.attachment_locations:
            if isinstance(location, InstructionAttachmentLocationNode):
                normalized.append(location)
            else:
                normalized.append(InstructionAttachmentLocationNode.from_xml(location))
        self.attachment_locations = normalized

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "InterviewerInstructionReference")
    ALT_TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "InstructionReference")

    @classmethod
    def from_xml(cls, element: Element) -> InterviewerInstructionReference:
        if element.tag not in {cls.TAG, cls.ALT_TAG}:
            raise ValueError(
                "Expected a datacollection:InterviewerInstructionReference element."
            )
        reference = Reference.from_xml(element)
        attachments = [
            InstructionAttachmentLocationNode.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "InstructionAttachmentLocation")
            )
        ]
        recognized = {
            qn(REUSABLE_NS, "URN"),
            qn(REUSABLE_NS, "Agency"),
            qn(REUSABLE_NS, "ID"),
            qn(REUSABLE_NS, "Version"),
            qn(REUSABLE_NS, "TypeOfObject"),
            qn(DATA_COLLECTION_NS, "InstructionAttachmentLocation"),
        }
        other_elements = [
            clone_element(child) for child in element if child.tag not in recognized
        ]
        raw_is_displayed = element.get("isDisplayed")
        default_displayed = raw_is_displayed is None and element.tag == cls.ALT_TAG
        parsed_displayed = _parse_bool_attribute(raw_is_displayed)
        is_displayed = (
            default_displayed if parsed_displayed is None else parsed_displayed
        )
        return cls(
            reference=reference,
            is_displayed=is_displayed,
            attachment_locations=attachments,
            other_elements=other_elements,
            _is_displayed_attribute_present=raw_is_displayed is not None,
            _source_tag=element.tag,
        )

    def to_xml(self, tag: str | None = None) -> Element:
        if tag is None and self._source_tag is not None:
            if self._source_tag.startswith("{"):
                ns, local = self._source_tag[1:].split("}", 1)
                element = self.reference.to_xml(local, namespace=ns)
            else:
                element = self.reference.to_xml(
                    self._source_tag, namespace=DATA_COLLECTION_NS
                )
        else:
            element = self.reference.to_xml(
                tag or "InterviewerInstructionReference", namespace=DATA_COLLECTION_NS
            )
        for location in self.attachment_locations:
            element.append(location.to_xml())
        for child in self.other_elements:
            element.append(clone_element(child))
        return element


@dataclass
class QuestionGrid(QuestionMaintainableBase):
    """Representation of ``d:QuestionGrid`` fragments."""

    names: list[InternationalString] = field(default_factory=list)
    question_texts: list[DynamicText] = field(default_factory=list)
    question_intent: list[InternationalString] = field(default_factory=list)
    grid_dimensions: list[GridDimension] = field(default_factory=list)
    response_domain: Element | None = None
    response_domain_reference: Element | None = None
    structured_mixed_response_domain: Element | None = None
    cell_labels: list[Element] = field(default_factory=list)
    fixed_cell_values: list[Element] = field(default_factory=list)
    external_aids: list[Element] = field(default_factory=list)
    interviewer_instruction_references: list[InterviewerInstructionReference] = field(
        default_factory=list
    )
    external_interviewer_instructions: list[Element] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionGrid")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    @classmethod
    def from_xml(cls, element: Element) -> QuestionGrid:
        response_domain_reference_tags = {
            qn(DATA_COLLECTION_NS, "ResponseDomainReference"),
            qn(DATA_COLLECTION_NS, "MissingValuesDomainReference"),
            qn(DATA_COLLECTION_NS, "TextDomainReference"),
            qn(DATA_COLLECTION_NS, "NumericDomainReference"),
            qn(DATA_COLLECTION_NS, "DateTimeDomainReference"),
            qn(DATA_COLLECTION_NS, "ScaleDomainReference"),
        }
        recognized = {
            qn(DATA_COLLECTION_NS, "QuestionGridName"),
            qn(DATA_COLLECTION_NS, "QuestionText"),
            qn(DATA_COLLECTION_NS, "QuestionIntent"),
            qn(DATA_COLLECTION_NS, "GridDimension"),
            qn(DATA_COLLECTION_NS, "ResponseDomain"),
            qn(DATA_COLLECTION_NS, "StructuredMixedGridResponseDomain"),
            qn(DATA_COLLECTION_NS, "CellLabel"),
            qn(DATA_COLLECTION_NS, "FixedCellValue"),
            qn(DATA_COLLECTION_NS, "ExternalAid"),
            qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
            qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        }
        recognized.update(response_domain_reference_tags)
        data = cls._collect_question_common(element, recognized_children=recognized)
        names: list[InternationalString] = []
        for container in element.findall(qn(DATA_COLLECTION_NS, "QuestionGridName")):
            names.extend(InternationalString.from_container(container))
        question_texts = [
            DynamicText.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "QuestionText"))
        ]
        question_intent: list[InternationalString] = []
        intent_el = element.find(qn(DATA_COLLECTION_NS, "QuestionIntent"))
        if intent_el is not None:
            question_intent.extend(InternationalString.from_container(intent_el))
        grid_dimensions = [
            GridDimension.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "GridDimension"))
        ]
        response_domain = element.find(qn(DATA_COLLECTION_NS, "ResponseDomain"))
        response_domain_reference = None
        for tag in response_domain_reference_tags:
            node = element.find(tag)
            if node is not None:
                response_domain_reference = node
                break
        structured_mixed = element.find(
            qn(DATA_COLLECTION_NS, "StructuredMixedGridResponseDomain")
        )
        cell_labels = [
            clone_element(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "CellLabel"))
        ]
        fixed_values = [
            clone_element(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "FixedCellValue"))
        ]
        external_aids = [
            clone_element(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "ExternalAid"))
        ]
        interviewer_instruction_references = [
            InterviewerInstructionReference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "InterviewerInstructionReference")
            )
        ]
        external_instructions = [
            clone_element(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction")
            )
        ]
        other_elements = [
            child
            for child in data.get("other_elements", [])
            if child.tag not in recognized
        ]
        data["other_elements"] = other_elements
        return cls(
            names=names,
            question_texts=question_texts,
            question_intent=question_intent,
            grid_dimensions=grid_dimensions,
            response_domain=clone_element(response_domain)
            if response_domain is not None
            else None,
            response_domain_reference=clone_element(response_domain_reference)
            if response_domain_reference is not None
            else None,
            structured_mixed_response_domain=clone_element(structured_mixed)
            if structured_mixed is not None
            else None,
            cell_labels=cell_labels,
            fixed_cell_values=fixed_values,
            external_aids=external_aids,
            interviewer_instruction_references=interviewer_instruction_references,
            external_interviewer_instructions=external_instructions,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_question_common(element)
        for name in self.names:
            container = create_element(qn(DATA_COLLECTION_NS, "QuestionGridName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        for text in self.question_texts:
            element.append(text.to_xml("QuestionText"))
        if self.question_intent:
            intent_el = create_element(qn(DATA_COLLECTION_NS, "QuestionIntent"))
            for string in self.question_intent:
                intent_el.append(string.to_child())
            element.append(intent_el)
        for dimension in self.grid_dimensions:
            element.append(dimension.to_xml())
        if self.response_domain is not None:
            element.append(clone_element(self.response_domain))
        if self.response_domain_reference is not None:
            element.append(clone_element(self.response_domain_reference))
        if self.structured_mixed_response_domain is not None:
            element.append(clone_element(self.structured_mixed_response_domain))
        for node in self.cell_labels:
            element.append(clone_element(node))
        for node in self.fixed_cell_values:
            element.append(clone_element(node))
        for node in self.external_aids:
            element.append(clone_element(node))
        for instruction_reference in self.interviewer_instruction_references:
            element.append(instruction_reference.to_xml())
        for node in self.external_interviewer_instructions:
            element.append(clone_element(node))
        self._append_other_elements(element)
        return element


@dataclass
class QuestionBlock(QuestionMaintainableBase):
    """Representation of ``d:QuestionBlock`` fragments."""

    names: list[InternationalString] = field(default_factory=list)
    intent: list[InternationalString] = field(default_factory=list)
    stimulus_materials: list[Element] = field(default_factory=list)
    question_item_references: list[Reference] = field(default_factory=list)
    question_grid_references: list[Reference] = field(default_factory=list)
    question_sequence: Element | None = None
    response_cardinality: Element | None = None
    concept_references: list[Reference] = field(default_factory=list)
    external_aids: list[Element] = field(default_factory=list)
    interviewer_instruction_references: list[InterviewerInstructionReference] = field(
        default_factory=list
    )
    external_interviewer_instructions: list[Element] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionBlock")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    @classmethod
    def from_xml(cls, element: Element) -> QuestionBlock:
        recognized = {
            qn(DATA_COLLECTION_NS, "QuestionBlockName"),
            qn(DATA_COLLECTION_NS, "QuestionBlockIntent"),
            qn(DATA_COLLECTION_NS, "StimulusMaterial"),
            qn(DATA_COLLECTION_NS, "QuestionItemReference"),
            qn(DATA_COLLECTION_NS, "QuestionGridReference"),
            qn(DATA_COLLECTION_NS, "QuestionSequence"),
            qn(REUSABLE_NS, "ResponseCardinality"),
            qn(REUSABLE_NS, "ConceptReference"),
            qn(DATA_COLLECTION_NS, "ExternalAid"),
            qn(DATA_COLLECTION_NS, "InterviewerInstructionReference"),
            qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction"),
        }
        data = cls._collect_question_common(element, recognized_children=recognized)
        names: list[InternationalString] = []
        for container in element.findall(qn(DATA_COLLECTION_NS, "QuestionBlockName")):
            names.extend(InternationalString.from_container(container))
        intent_strings: list[InternationalString] = []
        intent_el = element.find(qn(DATA_COLLECTION_NS, "QuestionBlockIntent"))
        if intent_el is not None:
            intent_strings.extend(InternationalString.from_container(intent_el))
        stimulus_materials = [
            clone_element(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "StimulusMaterial"))
        ]
        question_item_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "QuestionItemReference"))
        ]
        question_grid_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "QuestionGridReference"))
        ]
        question_sequence = element.find(qn(DATA_COLLECTION_NS, "QuestionSequence"))
        response_cardinality = element.find(qn(REUSABLE_NS, "ResponseCardinality"))
        concept_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "ConceptReference"))
        ]
        external_aids = [
            clone_element(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "ExternalAid"))
        ]
        interviewer_instruction_references = [
            InterviewerInstructionReference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "InterviewerInstructionReference")
            )
        ]
        external_instructions = [
            clone_element(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ExternalInterviewerInstruction")
            )
        ]
        other_elements = [
            child
            for child in data.get("other_elements", [])
            if child.tag not in recognized
        ]
        data["other_elements"] = other_elements
        return cls(
            names=names,
            intent=intent_strings,
            stimulus_materials=stimulus_materials,
            question_item_references=question_item_references,
            question_grid_references=question_grid_references,
            question_sequence=clone_element(question_sequence)
            if question_sequence is not None
            else None,
            response_cardinality=clone_element(response_cardinality)
            if response_cardinality is not None
            else None,
            concept_references=concept_references,
            external_aids=external_aids,
            interviewer_instruction_references=interviewer_instruction_references,
            external_interviewer_instructions=external_instructions,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_question_common(element)
        for name in self.names:
            container = create_element(qn(DATA_COLLECTION_NS, "QuestionBlockName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        if self.intent:
            intent_el = create_element(qn(DATA_COLLECTION_NS, "QuestionBlockIntent"))
            for string in self.intent:
                intent_el.append(string.to_child())
            element.append(intent_el)
        for node in self.stimulus_materials:
            element.append(clone_element(node))
        for reference in self.question_item_references:
            element.append(
                reference.to_xml("QuestionItemReference", namespace=DATA_COLLECTION_NS)
            )
        for reference in self.question_grid_references:
            element.append(
                reference.to_xml("QuestionGridReference", namespace=DATA_COLLECTION_NS)
            )
        if self.question_sequence is not None:
            element.append(clone_element(self.question_sequence))
        if self.response_cardinality is not None:
            element.append(clone_element(self.response_cardinality))
        for reference in self.concept_references:
            element.append(reference.to_xml("ConceptReference"))
        for node in self.external_aids:
            element.append(clone_element(node))
        for instruction_reference in self.interviewer_instruction_references:
            element.append(instruction_reference.to_xml())
        for node in self.external_interviewer_instructions:
            element.append(clone_element(node))
        self._append_other_elements(element)
        return element


@dataclass
class QuestionGroup(QuestionMaintainableBase):
    """Representation of ``d:QuestionGroup`` fragments."""

    type_of_question_group: CodeValue | None = None
    names: list[InternationalString] = field(default_factory=list)
    is_ordered: bool | None = None
    universe_references: list[Reference] = field(default_factory=list)
    concept_references: list[Reference] = field(default_factory=list)
    subjects: list[InternationalString] = field(default_factory=list)
    keywords: list[InternationalString] = field(default_factory=list)
    question_item_references: list[Reference] = field(default_factory=list)
    question_grid_references: list[Reference] = field(default_factory=list)
    question_block_references: list[Reference] = field(default_factory=list)
    question_group_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    @classmethod
    def from_xml(cls, element: Element) -> QuestionGroup:
        recognized = {
            qn(DATA_COLLECTION_NS, "TypeOfQuestionGroup"),
            qn(DATA_COLLECTION_NS, "QuestionGroupName"),
            qn(REUSABLE_NS, "UniverseReference"),
            qn(REUSABLE_NS, "ConceptReference"),
            qn(REUSABLE_NS, "Subject"),
            qn(REUSABLE_NS, "Keyword"),
            qn(DATA_COLLECTION_NS, "QuestionItemReference"),
            qn(DATA_COLLECTION_NS, "QuestionGridReference"),
            qn(DATA_COLLECTION_NS, "QuestionBlockReference"),
            qn(DATA_COLLECTION_NS, "QuestionGroupReference"),
        }
        data = cls._collect_question_common(element, recognized_children=recognized)
        type_el = element.find(qn(DATA_COLLECTION_NS, "TypeOfQuestionGroup"))
        names: list[InternationalString] = []
        for container in element.findall(qn(DATA_COLLECTION_NS, "QuestionGroupName")):
            names.extend(InternationalString.from_container(container))
        universe_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "UniverseReference"))
        ]
        concept_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "ConceptReference"))
        ]
        subjects = [
            InternationalString.from_container(node)[0]
            for node in element.findall(qn(REUSABLE_NS, "Subject"))
            if InternationalString.from_container(node)
        ]
        keywords = [
            InternationalString.from_container(node)[0]
            for node in element.findall(qn(REUSABLE_NS, "Keyword"))
            if InternationalString.from_container(node)
        ]
        question_item_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "QuestionItemReference"))
        ]
        question_grid_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "QuestionGridReference"))
        ]
        question_block_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "QuestionBlockReference")
            )
        ]
        question_group_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "QuestionGroupReference")
            )
        ]
        other_elements = [
            child
            for child in data.get("other_elements", [])
            if child.tag not in recognized
        ]
        data["other_elements"] = other_elements
        return cls(
            type_of_question_group=CodeValue.from_xml(type_el)
            if type_el is not None
            else None,
            names=names,
            is_ordered=_parse_bool_attribute(element.get("isOrdered")),
            universe_references=universe_references,
            concept_references=concept_references,
            subjects=subjects,
            keywords=keywords,
            question_item_references=question_item_references,
            question_grid_references=question_grid_references,
            question_block_references=question_block_references,
            question_group_references=question_group_references,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_question_common(element)
        if self.is_ordered is not None:
            formatted = _format_bool_attribute(self.is_ordered)
            if formatted is not None:
                element.set("isOrdered", formatted)
        if self.type_of_question_group is not None:
            element.append(
                self.type_of_question_group.to_xml(
                    "TypeOfQuestionGroup", namespace=DATA_COLLECTION_NS
                )
            )
        for name in self.names:
            container = create_element(qn(DATA_COLLECTION_NS, "QuestionGroupName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        for reference in self.universe_references:
            element.append(reference.to_xml("UniverseReference"))
        for reference in self.concept_references:
            element.append(reference.to_xml("ConceptReference"))
        for subject in self.subjects:
            element.append(subject.to_element("Subject"))
        for keyword in self.keywords:
            element.append(keyword.to_element("Keyword"))
        for reference in self.question_item_references:
            element.append(
                reference.to_xml("QuestionItemReference", namespace=DATA_COLLECTION_NS)
            )
        for reference in self.question_grid_references:
            element.append(
                reference.to_xml("QuestionGridReference", namespace=DATA_COLLECTION_NS)
            )
        for reference in self.question_block_references:
            element.append(
                reference.to_xml("QuestionBlockReference", namespace=DATA_COLLECTION_NS)
            )
        for reference in self.question_group_references:
            element.append(
                reference.to_xml("QuestionGroupReference", namespace=DATA_COLLECTION_NS)
            )
        self._append_other_elements(element)
        return element


@dataclass
class Instruction(InstructionFields):
    """Maintainable representation of ``d:Instruction`` elements."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Instruction")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    _TYPED_CHILDREN: ClassVar[dict[str, type]] = {
        "instruction_texts": DynamicText,
    }


@dataclass
class InstructionGroup(InstructionGroupFields):
    """Maintainable representation of ``d:InstructionGroup`` entries."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "InstructionGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    _TYPED_CHILDREN: ClassVar[dict[str, type]] = {
        "instruction_references": InterviewerInstructionReference,
    }


@dataclass
class InterviewerInstructionScheme(InterviewerInstructionSchemeFields):
    """Maintainable representation of ``d:InterviewerInstructionScheme`` entries."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    _TYPED_CHILDREN: ClassVar[dict[str, type]] = {
        "instructions": Instruction,
        "instruction_references": InterviewerInstructionReference,
        "instruction_groups": InstructionGroup,
    }

    def __post_init__(self) -> None:
        def _suffix(base: str) -> Callable[[int, MaintainableBase], str | None]:
            return lambda index, _child: self._default_child_suffix(base, index)

        self._propagate_child_identification(
            self.instructions,  # type: ignore[arg-type]
            identifier_suffix_factory=_suffix("instruction"),
        )
        self._propagate_child_identification(
            self.instruction_groups,  # type: ignore[arg-type]
            identifier_suffix_factory=_suffix("instruction-group"),
        )


@dataclass
class CollectionEvent(CollectionEventFields):
    """Lightweight wrapper for ``d:CollectionEvent`` fragments."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CollectionEvent")
    NSMAP: ClassVar[dict[str | None, str]] = build_namespace_map(
        "r", default_namespace=DATA_COLLECTION_NS
    )


@dataclass
class CollectionActivity(VersionableMaintainableBase):
    """Maintainable representation of ``d:CollectionActivity`` entries."""

    names: list[InternationalString] = field(default_factory=list)
    activity_types: list[CodeValue] = field(default_factory=list)
    data_source_references: list[Reference] = field(default_factory=list)
    collection_event_references: list[Reference] = field(default_factory=list)
    observation_plan_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "CollectionActivity")
    NSMAP: ClassVar[dict[str | None, str]] = build_namespace_map(
        "r", default_namespace=DATA_COLLECTION_NS
    )

    @classmethod
    def from_xml(cls, element: Element) -> CollectionActivity:
        recognized = {
            qn(DATA_COLLECTION_NS, "CollectionActivityName"),
            qn(DATA_COLLECTION_NS, "TypeOfCollectionActivity"),
            qn(DATA_COLLECTION_NS, "DataSourceReference"),
            qn(DATA_COLLECTION_NS, "CollectionEventReference"),
            qn(DATA_COLLECTION_NS, "ObservationPlanReference"),
        }
        data = cls._collect_versionable_common(element, recognized_children=recognized)
        names: list[InternationalString] = []
        for container in element.findall(
            qn(DATA_COLLECTION_NS, "CollectionActivityName")
        ):
            names.extend(InternationalString.from_container(container))
        activity_types = [
            CodeValue.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "TypeOfCollectionActivity")
            )
        ]
        data_source_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "DataSourceReference"))
        ]
        collection_event_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "CollectionEventReference")
            )
        ]
        observation_plan_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ObservationPlanReference")
            )
        ]
        return cls(
            names=names,
            activity_types=activity_types,
            data_source_references=data_source_references,
            collection_event_references=collection_event_references,
            observation_plan_references=observation_plan_references,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_versionable_common(element)
        for name in self.names:
            container = create_element(qn(DATA_COLLECTION_NS, "CollectionActivityName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        for activity_type in self.activity_types:
            element.append(
                activity_type.to_xml(
                    "TypeOfCollectionActivity", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.data_source_references:
            element.append(
                reference.to_xml("DataSourceReference", namespace=DATA_COLLECTION_NS)
            )
        for reference in self.collection_event_references:
            element.append(
                reference.to_xml(
                    "CollectionEventReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.observation_plan_references:
            element.append(
                reference.to_xml(
                    "ObservationPlanReference", namespace=DATA_COLLECTION_NS
                )
            )
        self._append_other_elements(element)
        cleanup_namespaces(
            element,
            {
                None: DATA_COLLECTION_NS,
                "r": REUSABLE_NS,
            },
        )
        return element


@dataclass
class ObservationPlan(VersionableMaintainableBase):
    """Maintainable representation of ``d:ObservationPlan`` entries."""

    names: list[InternationalString] = field(default_factory=list)
    plan_types: list[CodeValue] = field(default_factory=list)
    observation_units: list[CodeValue] = field(default_factory=list)
    collection_activity_references: list[Reference] = field(default_factory=list)
    collection_event_references: list[Reference] = field(default_factory=list)
    observation_sequence_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ObservationPlan")
    NSMAP: ClassVar[dict[str | None, str]] = build_namespace_map(
        "r", default_namespace=DATA_COLLECTION_NS
    )

    @classmethod
    def from_xml(cls, element: Element) -> ObservationPlan:
        recognized = {
            qn(DATA_COLLECTION_NS, "ObservationPlanName"),
            qn(DATA_COLLECTION_NS, "TypeOfObservationPlan"),
            qn(DATA_COLLECTION_NS, "ObservationUnit"),
            qn(DATA_COLLECTION_NS, "CollectionActivityReference"),
            qn(DATA_COLLECTION_NS, "CollectionEventReference"),
            qn(DATA_COLLECTION_NS, "ObservationSequenceReference"),
        }
        data = cls._collect_versionable_common(element, recognized_children=recognized)
        names: list[InternationalString] = []
        for container in element.findall(qn(DATA_COLLECTION_NS, "ObservationPlanName")):
            names.extend(InternationalString.from_container(container))
        plan_types = [
            CodeValue.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "TypeOfObservationPlan"))
        ]
        observation_units = [
            CodeValue.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "ObservationUnit"))
        ]
        collection_activity_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "CollectionActivityReference")
            )
        ]
        collection_event_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "CollectionEventReference")
            )
        ]
        observation_sequence_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ObservationSequenceReference")
            )
        ]
        return cls(
            names=names,
            plan_types=plan_types,
            observation_units=observation_units,
            collection_activity_references=collection_activity_references,
            collection_event_references=collection_event_references,
            observation_sequence_references=observation_sequence_references,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_versionable_common(element)
        for name in self.names:
            container = create_element(qn(DATA_COLLECTION_NS, "ObservationPlanName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        for plan_type in self.plan_types:
            element.append(
                plan_type.to_xml("TypeOfObservationPlan", namespace=DATA_COLLECTION_NS)
            )
        for unit in self.observation_units:
            element.append(unit.to_xml("ObservationUnit", namespace=DATA_COLLECTION_NS))
        for reference in self.collection_activity_references:
            element.append(
                reference.to_xml(
                    "CollectionActivityReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.collection_event_references:
            element.append(
                reference.to_xml(
                    "CollectionEventReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.observation_sequence_references:
            element.append(
                reference.to_xml(
                    "ObservationSequenceReference", namespace=DATA_COLLECTION_NS
                )
            )
        self._append_other_elements(element)
        cleanup_namespaces(
            element,
            {
                None: DATA_COLLECTION_NS,
                "r": REUSABLE_NS,
            },
        )
        return element


@dataclass
class DataCaptureMethod(VersionableMaintainableBase):
    """Maintainable representation of ``d:DataCaptureMethod`` entries."""

    names: list[InternationalString] = field(default_factory=list)
    method_types: list[CodeValue] = field(default_factory=list)
    data_source_references: list[Reference] = field(default_factory=list)
    collection_activity_references: list[Reference] = field(default_factory=list)
    collection_event_references: list[Reference] = field(default_factory=list)
    observation_plan_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DataCaptureMethod")
    NSMAP: ClassVar[dict[str | None, str]] = build_namespace_map(
        "r", default_namespace=DATA_COLLECTION_NS
    )

    @classmethod
    def from_xml(cls, element: Element) -> DataCaptureMethod:
        recognized = {
            qn(DATA_COLLECTION_NS, "DataCaptureMethodName"),
            qn(DATA_COLLECTION_NS, "TypeOfDataCaptureMethod"),
            qn(DATA_COLLECTION_NS, "DataSourceReference"),
            qn(DATA_COLLECTION_NS, "CollectionActivityReference"),
            qn(DATA_COLLECTION_NS, "CollectionEventReference"),
            qn(DATA_COLLECTION_NS, "ObservationPlanReference"),
        }
        data = cls._collect_versionable_common(element, recognized_children=recognized)
        names: list[InternationalString] = []
        for container in element.findall(
            qn(DATA_COLLECTION_NS, "DataCaptureMethodName")
        ):
            names.extend(InternationalString.from_container(container))
        method_types = [
            CodeValue.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "TypeOfDataCaptureMethod")
            )
        ]
        data_source_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "DataSourceReference"))
        ]
        collection_activity_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "CollectionActivityReference")
            )
        ]
        collection_event_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "CollectionEventReference")
            )
        ]
        observation_plan_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ObservationPlanReference")
            )
        ]
        return cls(
            names=names,
            method_types=method_types,
            data_source_references=data_source_references,
            collection_activity_references=collection_activity_references,
            collection_event_references=collection_event_references,
            observation_plan_references=observation_plan_references,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_versionable_common(element)
        for name in self.names:
            container = create_element(qn(DATA_COLLECTION_NS, "DataCaptureMethodName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        for method_type in self.method_types:
            element.append(
                method_type.to_xml(
                    "TypeOfDataCaptureMethod", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.data_source_references:
            element.append(
                reference.to_xml("DataSourceReference", namespace=DATA_COLLECTION_NS)
            )
        for reference in self.collection_activity_references:
            element.append(
                reference.to_xml(
                    "CollectionActivityReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.collection_event_references:
            element.append(
                reference.to_xml(
                    "CollectionEventReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.observation_plan_references:
            element.append(
                reference.to_xml(
                    "ObservationPlanReference", namespace=DATA_COLLECTION_NS
                )
            )
        self._append_other_elements(element)
        cleanup_namespaces(
            element,
            {
                None: DATA_COLLECTION_NS,
                "r": REUSABLE_NS,
            },
        )
        return element


@dataclass
class DataCollection(VersionableMaintainableBase):
    """Maintainable wrapper for ``d:DataCollection`` structures in DDI 3.3.

    Field names intentionally mirror their XML counterparts so callers can see
    how module fragments are grouped:

    * ``collection_events`` holds inline ``d:CollectionEvent`` entries, whereas
      ``collection_activity_references`` and similar attributes store reusable
      reference elements that link to external schemes.
    * ``instruments`` captures the inline ``Instrument`` fragments discovered in
      nested ``InstrumentScheme`` containers. The related reference lists map to
      ``d:InstrumentReference`` and ``d:ProcessingEventSchemeReference`` nodes.
    * ``questions``/``question_grids``/``question_blocks``/``question_groups``
      represent inline question fragments resolved from ``d:QuestionScheme``
      children, while the corresponding ``*_references`` lists preserve
      ``d:Question{Item,Grid,Block,Group}Reference`` nodes to maintain ordering
      and allow hybrid inline/reference configurations.
    * ``interviewer_instructions`` and ``interviewer_instruction_groups`` expose
      content from ``d:InterviewerInstructionScheme`` children and keep related
      references in ``interviewer_instruction_references`` and
      ``interviewer_instruction_scheme_references``.
    * ``methodologies`` retains inline ``d:Methodology`` fragments with
      ``methodology_references`` covering ``d:MethodologyReference`` nodes.
    * ``coverage`` is a passthrough for ``r:Coverage`` elements, ensuring that
      mixed content and sub-structure is preserved verbatim.

    The doctest below creates a minimal inline ``CollectionEvent`` to
    demonstrate the bidirectional mapping between XML and the dataclass,
    highlighting that maintainables receive deterministic UUID identifiers
    when serialized::

        >>> from ddi_l.models.datacollection import CollectionEvent
        >>> event = CollectionEvent(agency="org", identifier="evt", version="1")
        >>> collection = DataCollection(
        ...     agency="org",
        ...     identifier="dc",
        ...     version="1",
        ...     collection_events=[event],
        ... )
        >>> parsed = DataCollection.from_xml(collection.to_xml())
        >>> parsed.identifier
        '2b947cb1-d912-51b2-89d7-c453a8e241fb'
        >>> [item.identifier for item in parsed.collection_events]
        ['fb861734-81ec-58d7-bdd2-6dde0f93d973']
    """

    instruments: list[Instrument] = field(default_factory=list)
    questions: list[QuestionItem] = field(default_factory=list)
    question_grids: list[QuestionGrid] = field(default_factory=list)
    question_blocks: list[QuestionBlock] = field(default_factory=list)
    question_groups: list[QuestionGroup] = field(default_factory=list)
    question_item_references: list[Reference] = field(default_factory=list)
    question_grid_references: list[Reference] = field(default_factory=list)
    question_block_references: list[Reference] = field(default_factory=list)
    question_group_references: list[Reference] = field(default_factory=list)
    question_fragments: list[QuestionMaintainableBase] = field(
        default_factory=list, repr=False
    )
    question_reference_order: list[str] = field(default_factory=list, repr=False)
    coverage: list[Element] = field(default_factory=list)
    collection_events: list[CollectionEvent] = field(default_factory=list)
    collection_activities: list[CollectionActivity] = field(default_factory=list)
    observation_plans: list[ObservationPlan] = field(default_factory=list)
    data_capture_methods: list[DataCaptureMethod] = field(default_factory=list)
    methodologies: list[Methodology] = field(default_factory=list)
    methodology_references: list[Reference] = field(default_factory=list)
    instrument_references: list[Reference] = field(default_factory=list)
    processing_event_scheme_references: list[Reference] = field(default_factory=list)
    collection_activity_references: list[Reference] = field(default_factory=list)
    collection_activity_scheme_references: list[Reference] = field(default_factory=list)
    observation_plan_references: list[Reference] = field(default_factory=list)
    observation_plan_scheme_references: list[Reference] = field(default_factory=list)
    data_capture_method_references: list[Reference] = field(default_factory=list)
    data_capture_method_scheme_references: list[Reference] = field(default_factory=list)
    interviewer_instructions: list[Instruction] = field(default_factory=list)
    interviewer_instruction_references: list[InterviewerInstructionReference] = field(
        default_factory=list
    )
    interviewer_instruction_groups: list[InstructionGroup] = field(default_factory=list)
    interviewer_instruction_group_references: list[Reference] = field(
        default_factory=list
    )
    interviewer_instruction_scheme_references: list[Reference] = field(
        default_factory=list
    )
    control_construct_scheme_references: list[Reference] = field(default_factory=list)
    control_constructs: list[MaintainableBase] = field(default_factory=list)
    control_construct_extras: list[Element] = field(default_factory=list, repr=False)
    question_scheme_references: list[Reference] = field(default_factory=list)
    measurement_scheme_references: list[Reference] = field(default_factory=list)
    processing_instruction_scheme_references: list[Reference] = field(
        default_factory=list
    )
    data_capture_development_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DataCollection")
    NSMAP: ClassVar[dict[str | None, str]] = build_namespace_map(
        "r", default_namespace=DATA_COLLECTION_NS
    )

    def __post_init__(self) -> None:
        if not self.question_fragments:
            self.question_fragments = [
                *self.questions,
                *self.question_grids,
                *self.question_blocks,
                *self.question_groups,
            ]

    def validate(self) -> None:
        super().validate()
        has_inline_content = bool(
            self.collection_events
            or self.collection_activities
            or self.observation_plans
            or self.data_capture_methods
            or self.instruments
            or self.questions
            or self.question_grids
            or self.question_blocks
            or self.question_groups
            or self.interviewer_instructions
            or self.interviewer_instruction_groups
        )
        has_references = bool(
            self.instrument_references
            or self.processing_event_scheme_references
            or self.collection_activity_references
            or self.collection_activity_scheme_references
            or self.observation_plan_references
            or self.observation_plan_scheme_references
            or self.data_capture_method_references
            or self.data_capture_method_scheme_references
            or self.interviewer_instruction_scheme_references
        )
        if not (has_inline_content or has_references):
            raise ModelValidationError(
                "DataCollection requires collection events,"
                " instruments, questions, or references"
                " before serialization."
            )
        unique_groups = (
            ("CollectionEvent", self.collection_events),
            ("CollectionActivity", self.collection_activities),
            ("ObservationPlan", self.observation_plans),
            ("DataCaptureMethod", self.data_capture_methods),
            ("Instrument", self.instruments),
            ("QuestionItem", self.questions),
            ("QuestionGrid", self.question_grids),
            ("QuestionBlock", self.question_blocks),
            ("QuestionGroup", self.question_groups),
            ("Instruction", self.interviewer_instructions),
            ("InstructionGroup", self.interviewer_instruction_groups),
            ("Methodology", self.methodologies),
        )
        for label, items in unique_groups:
            self._assert_unique_children(items, child_label=label)

    @classmethod
    def from_xml(cls, element: Element) -> DataCollection:
        from ..methodology import Methodology

        recognized = {
            qn(REUSABLE_NS, "UserID"),
            qn(REUSABLE_NS, "UserAttributePair"),
            qn(REUSABLE_NS, "VersionResponsibility"),
            qn(REUSABLE_NS, "VersionRationale"),
            qn(REUSABLE_NS, "Coverage"),
            qn(DATA_COLLECTION_NS, "CollectionEvent"),
            qn(DATA_COLLECTION_NS, "CollectionActivity"),
            qn(DATA_COLLECTION_NS, "CollectionActivityScheme"),
            qn(DATA_COLLECTION_NS, "CollectionActivityReference"),
            qn(DATA_COLLECTION_NS, "CollectionActivitySchemeReference"),
            qn(DATA_COLLECTION_NS, "ObservationPlan"),
            qn(DATA_COLLECTION_NS, "ObservationPlanScheme"),
            qn(DATA_COLLECTION_NS, "ObservationPlanReference"),
            qn(DATA_COLLECTION_NS, "ObservationPlanSchemeReference"),
            qn(DATA_COLLECTION_NS, "DataCaptureMethod"),
            qn(DATA_COLLECTION_NS, "DataCaptureMethodScheme"),
            qn(DATA_COLLECTION_NS, "DataCaptureMethodReference"),
            qn(DATA_COLLECTION_NS, "DataCaptureMethodSchemeReference"),
            qn(DATA_COLLECTION_NS, "Methodology"),
            qn(DATA_COLLECTION_NS, "MethodologyReference"),
            qn(DATA_COLLECTION_NS, "InstrumentReference"),
            qn(DATA_COLLECTION_NS, "ProcessingEventSchemeReference"),
            qn(DATA_COLLECTION_NS, "InstrumentScheme"),
            qn(DATA_COLLECTION_NS, "QuestionScheme"),
            qn(DATA_COLLECTION_NS, "ControlConstructScheme"),
            qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme"),
            qn(REUSABLE_NS, "InterviewerInstructionSchemeReference"),
            qn(REUSABLE_NS, "ControlConstructSchemeReference"),
            qn(REUSABLE_NS, "QuestionSchemeReference"),
            qn(REUSABLE_NS, "MeasurementSchemeReference"),
            qn(DATA_COLLECTION_NS, "ProcessingInstructionSchemeReference"),
            qn(DATA_COLLECTION_NS, "DataCaptureDevelopmentReference"),
        }
        coverage = [
            clone_element(node) for node in element.findall(qn(REUSABLE_NS, "Coverage"))
        ]
        collection_events = [
            CollectionEvent.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "CollectionEvent"))
        ]
        collection_activities = [
            CollectionActivity.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "CollectionActivity"))
        ]
        observation_plans = [
            ObservationPlan.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "ObservationPlan"))
        ]
        data_capture_methods = [
            DataCaptureMethod.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "DataCaptureMethod"))
        ]
        methodologies = [
            Methodology.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "Methodology"))
        ]
        methodology_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "MethodologyReference"))
        ]
        instrument_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "InstrumentReference"))
        ]
        processing_event_scheme_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ProcessingEventSchemeReference")
            )
        ]
        collection_activity_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "CollectionActivityReference")
            )
        ]
        collection_activity_scheme_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "CollectionActivitySchemeReference")
            )
        ]
        observation_plan_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ObservationPlanReference")
            )
        ]
        observation_plan_scheme_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ObservationPlanSchemeReference")
            )
        ]
        data_capture_method_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "DataCaptureMethodReference")
            )
        ]
        data_capture_method_scheme_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "DataCaptureMethodSchemeReference")
            )
        ]
        interviewer_instruction_scheme_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(REUSABLE_NS, "InterviewerInstructionSchemeReference")
            )
        ]
        control_construct_scheme_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(REUSABLE_NS, "ControlConstructSchemeReference")
            )
        ]
        question_scheme_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "QuestionSchemeReference"))
        ]
        measurement_scheme_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "MeasurementSchemeReference"))
        ]
        processing_instruction_scheme_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ProcessingInstructionSchemeReference")
            )
        ]
        data_capture_development_references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "DataCaptureDevelopmentReference")
            )
        ]
        instruments: list[Instrument] = []
        for scheme in element.findall(qn(DATA_COLLECTION_NS, "InstrumentScheme")):
            for instrument_el in scheme.findall(qn(DATA_COLLECTION_NS, "Instrument")):
                instruments.append(Instrument.from_xml(instrument_el))
        questions: list[QuestionItem] = []
        question_grids: list[QuestionGrid] = []
        question_blocks: list[QuestionBlock] = []
        question_groups: list[QuestionGroup] = []
        question_item_references: list[Reference] = []
        question_grid_references: list[Reference] = []
        question_block_references: list[Reference] = []
        question_group_references: list[Reference] = []
        question_fragments: list[QuestionMaintainableBase] = []
        question_reference_order: list[str] = []
        for scheme in element.findall(qn(DATA_COLLECTION_NS, "QuestionScheme")):
            question_scheme = QuestionScheme.from_xml(scheme)
            questions.extend(question_scheme.question_items)
            question_grids.extend(question_scheme.question_grids)
            question_blocks.extend(question_scheme.question_blocks)
            question_groups.extend(question_scheme.question_groups)
            question_item_references.extend(question_scheme.question_item_references)
            question_grid_references.extend(question_scheme.question_grid_references)
            question_block_references.extend(question_scheme.question_block_references)
            question_group_references.extend(question_scheme.question_group_references)
            question_fragments.extend(list(question_scheme.iter_fragments()))
            question_reference_order.extend(question_scheme.reference_order)
        control_constructs: list[MaintainableBase] = []
        control_construct_extras: list[Element] = []
        control_construct_by_tag = {
            construct_type.TAG: construct_type
            for construct_type in (
                QuestionConstruct,
                Sequence,
                IfThenElse,
                StatementItem,
                ComputationItem,
                Loop,
            )
        }
        control_scheme_identification = {
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
            qn(REUSABLE_NS, "Label"),
            qn(REUSABLE_NS, "Description"),
            qn(DATA_COLLECTION_NS, "ControlConstructSchemeName"),
            qn(REUSABLE_NS, "ControlConstructSchemeReference"),
        }
        for scheme in element.findall(qn(DATA_COLLECTION_NS, "ControlConstructScheme")):
            for child in scheme:
                construct_type = control_construct_by_tag.get(child.tag)
                if construct_type is not None:
                    control_constructs.append(construct_type.from_xml(child))
                elif child.tag not in control_scheme_identification:
                    # Preserve constructs we do not model (e.g. Loop, groups,
                    # references) so round-tripping an existing file is lossless.
                    control_construct_extras.append(clone_element(child))
        interviewer_instructions: list[Instruction] = []
        interviewer_instruction_references: list[InterviewerInstructionReference] = []
        interviewer_instruction_groups: list[InstructionGroup] = []
        interviewer_instruction_group_references: list[Reference] = []
        for scheme in element.findall(
            qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme")
        ):
            instruction_scheme = InterviewerInstructionScheme.from_xml(scheme)
            interviewer_instructions.extend(instruction_scheme.instructions)  # type: ignore[arg-type]
            interviewer_instruction_references.extend(
                instruction_scheme.instruction_references  # type: ignore[arg-type]
            )
            interviewer_instruction_groups.extend(instruction_scheme.instruction_groups)  # type: ignore[arg-type]
            interviewer_instruction_group_references.extend(
                instruction_scheme.instruction_group_references
            )
        for scheme in element.findall(
            qn(DATA_COLLECTION_NS, "CollectionActivityScheme")
        ):
            for activity_el in scheme.findall(
                qn(DATA_COLLECTION_NS, "CollectionActivity")
            ):
                collection_activities.append(CollectionActivity.from_xml(activity_el))
        for scheme in element.findall(qn(DATA_COLLECTION_NS, "ObservationPlanScheme")):
            for plan_el in scheme.findall(qn(DATA_COLLECTION_NS, "ObservationPlan")):
                observation_plans.append(ObservationPlan.from_xml(plan_el))
        for scheme in element.findall(
            qn(DATA_COLLECTION_NS, "DataCaptureMethodScheme")
        ):
            for method_el in scheme.findall(
                qn(DATA_COLLECTION_NS, "DataCaptureMethod")
            ):
                data_capture_methods.append(DataCaptureMethod.from_xml(method_el))
        data = cls._collect_versionable_common(element, recognized_children=recognized)
        return cls(
            instruments=instruments,
            questions=questions,
            question_grids=question_grids,
            question_blocks=question_blocks,
            question_groups=question_groups,
            question_item_references=question_item_references,
            question_grid_references=question_grid_references,
            question_block_references=question_block_references,
            question_group_references=question_group_references,
            question_fragments=question_fragments,
            question_reference_order=question_reference_order,
            coverage=coverage,
            collection_events=collection_events,
            collection_activities=collection_activities,
            observation_plans=observation_plans,
            data_capture_methods=data_capture_methods,
            methodologies=methodologies,
            methodology_references=methodology_references,
            instrument_references=instrument_references,
            processing_event_scheme_references=processing_event_scheme_references,
            collection_activity_references=collection_activity_references,
            collection_activity_scheme_references=collection_activity_scheme_references,
            observation_plan_references=observation_plan_references,
            observation_plan_scheme_references=observation_plan_scheme_references,
            data_capture_method_references=data_capture_method_references,
            data_capture_method_scheme_references=data_capture_method_scheme_references,
            interviewer_instructions=interviewer_instructions,
            interviewer_instruction_references=interviewer_instruction_references,
            interviewer_instruction_groups=interviewer_instruction_groups,
            interviewer_instruction_group_references=interviewer_instruction_group_references,
            interviewer_instruction_scheme_references=interviewer_instruction_scheme_references,
            control_construct_scheme_references=control_construct_scheme_references,
            control_constructs=control_constructs,
            control_construct_extras=control_construct_extras,
            question_scheme_references=question_scheme_references,
            measurement_scheme_references=measurement_scheme_references,
            processing_instruction_scheme_references=processing_instruction_scheme_references,
            data_capture_development_references=data_capture_development_references,
            **data,
        )

    def to_xml(self) -> Element:
        if should_validate_on_serialize(self):
            self.validate()
        _normalize_reference_collections(self)
        element = self._build_base_element()
        with self._labels_last(element):
            self._append_versionable_common(element)
        for coverage_el in self.coverage:
            element.append(clone_element(coverage_el))
        for event in self.collection_events:
            element.append(event.to_xml())
        for methodology in self.methodologies:
            element.append(methodology.to_xml())
        for reference in self.methodology_references:
            element.append(
                reference.to_xml("MethodologyReference", namespace=DATA_COLLECTION_NS)
            )
        for reference in self.instrument_references:
            element.append(
                reference.to_xml("InstrumentReference", namespace=DATA_COLLECTION_NS)
            )
        for reference in self.processing_event_scheme_references:
            element.append(
                reference.to_xml(
                    "ProcessingEventSchemeReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.collection_activity_references:
            element.append(
                reference.to_xml(
                    "CollectionActivityReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.collection_activity_scheme_references:
            element.append(
                reference.to_xml(
                    "CollectionActivitySchemeReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.observation_plan_references:
            element.append(
                reference.to_xml(
                    "ObservationPlanReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.observation_plan_scheme_references:
            element.append(
                reference.to_xml(
                    "ObservationPlanSchemeReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.data_capture_method_references:
            element.append(
                reference.to_xml(
                    "DataCaptureMethodReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.data_capture_method_scheme_references:
            element.append(
                reference.to_xml(
                    "DataCaptureMethodSchemeReference", namespace=DATA_COLLECTION_NS
                )
            )
        if self.collection_activities:
            scheme = create_element(qn(DATA_COLLECTION_NS, "CollectionActivityScheme"))
            self._append_child_identification(
                scheme, suffix="collection-activity-scheme"
            )
            for activity in self.collection_activities:
                scheme.append(activity.to_xml())
            element.append(scheme)
        if self.observation_plans:
            scheme = create_element(qn(DATA_COLLECTION_NS, "ObservationPlanScheme"))
            self._append_child_identification(scheme, suffix="observation-plan-scheme")
            for plan in self.observation_plans:
                scheme.append(plan.to_xml())
            element.append(scheme)
        if self.data_capture_methods:
            scheme = create_element(qn(DATA_COLLECTION_NS, "DataCaptureMethodScheme"))
            self._append_child_identification(
                scheme, suffix="data-capture-method-scheme"
            )
            for method in self.data_capture_methods:
                scheme.append(method.to_xml())
            element.append(scheme)
        if (
            self.questions
            or self.question_grids
            or self.question_blocks
            or self.question_groups
            or self.question_item_references
            or self.question_grid_references
            or self.question_block_references
            or self.question_group_references
        ):
            scheme = create_element(qn(DATA_COLLECTION_NS, "QuestionScheme"))
            self._append_child_identification(scheme, suffix="question-scheme")

            def _iter_question_fragments(
                fragment_type: type[QuestionMaintainableBase],
                fallback: Iterable[QuestionMaintainableBase],
            ) -> Iterable[QuestionMaintainableBase]:
                if self.question_fragments:
                    for fragment in self.question_fragments:
                        if isinstance(fragment, fragment_type):
                            yield fragment
                    return
                yield from fallback

            fragment_groups: typing.Sequence[
                tuple[
                    type[QuestionMaintainableBase],
                    Iterable[QuestionMaintainableBase],
                    Iterable[Reference],
                    str,
                ]
            ] = [
                (
                    QuestionItem,
                    tuple(self.questions),
                    self.question_item_references,
                    "QuestionItemReference",
                ),
                (
                    QuestionGrid,
                    tuple(self.question_grids),
                    self.question_grid_references,
                    "QuestionGridReference",
                ),
                (
                    QuestionBlock,
                    tuple(self.question_blocks),
                    self.question_block_references,
                    "QuestionBlockReference",
                ),
                (
                    QuestionGroup,
                    tuple(self.question_groups),
                    self.question_group_references,
                    "QuestionGroupReference",
                ),
            ]

            for (
                fragment_type,
                inline_fragments,
                references,
                reference_tag,
            ) in fragment_groups:
                for fragment in _iter_question_fragments(
                    fragment_type, inline_fragments
                ):
                    scheme.append(fragment.to_xml())
                for reference in references:
                    scheme.append(
                        reference.to_xml(reference_tag, namespace=DATA_COLLECTION_NS)
                    )
            element.append(scheme)
        if self.control_constructs or self.control_construct_extras:
            scheme = create_element(qn(DATA_COLLECTION_NS, "ControlConstructScheme"))
            self._append_child_identification(scheme, suffix="control-construct-scheme")
            for construct in self.control_constructs:
                scheme.append(construct.to_xml())
            for extra in self.control_construct_extras:
                scheme.append(clone_element(extra))
            element.append(scheme)
        for reference in self.interviewer_instruction_scheme_references:
            element.append(
                reference.to_xml(
                    "InterviewerInstructionSchemeReference",
                    namespace=REUSABLE_NS,
                )
            )
        for reference in self.control_construct_scheme_references:
            element.append(
                reference.to_xml(
                    "ControlConstructSchemeReference", namespace=REUSABLE_NS
                )
            )
        for reference in self.question_scheme_references:
            element.append(
                reference.to_xml("QuestionSchemeReference", namespace=REUSABLE_NS)
            )
        for reference in self.measurement_scheme_references:
            element.append(
                reference.to_xml("MeasurementSchemeReference", namespace=REUSABLE_NS)
            )
        for reference in self.processing_instruction_scheme_references:
            element.append(
                reference.to_xml(
                    "ProcessingInstructionSchemeReference", namespace=DATA_COLLECTION_NS
                )
            )
        for reference in self.data_capture_development_references:
            element.append(
                reference.to_xml(
                    "DataCaptureDevelopmentReference", namespace=DATA_COLLECTION_NS
                )
            )
        if (
            self.interviewer_instructions
            or self.interviewer_instruction_references
            or self.interviewer_instruction_groups
            or self.interviewer_instruction_group_references
        ):
            scheme = create_element(
                qn(DATA_COLLECTION_NS, "InterviewerInstructionScheme")
            )
            self._append_child_identification(
                scheme, suffix="interviewer-instruction-scheme"
            )
            for instruction in self.interviewer_instructions:
                scheme.append(instruction.to_xml())
            for instruction_reference in self.interviewer_instruction_references:
                scheme.append(instruction_reference.to_xml(tag="InstructionReference"))
            for group in self.interviewer_instruction_groups:
                scheme.append(group.to_xml())
            for group_reference in self.interviewer_instruction_group_references:
                scheme.append(
                    group_reference.to_xml(
                        "InstructionGroupReference", namespace=DATA_COLLECTION_NS
                    )
                )
            element.append(scheme)
        if self.instruments:
            scheme = create_element(qn(DATA_COLLECTION_NS, "InstrumentScheme"))
            self._append_child_identification(scheme, suffix="instrument-scheme")
            for instrument in self.instruments:
                scheme.append(instrument.to_xml())
            element.append(scheme)
        self._append_other_elements(element)
        cleanup_namespaces(
            element,
            {
                None: DATA_COLLECTION_NS,
                "r": REUSABLE_NS,
            },
        )
        return element

    def get_questions(
        self,
        *,
        resolver: MaintainableRegistry | None = None,
    ) -> list[QuestionMaintainableBase]:
        """Return inline and resolved question fragments for the collection."""
        from ...maintainable_registry import (
            MaintainableResolver,
            ResolveIdentifier,
        )
        from ...maintainable_registry import (
            resolve as resolve_maintainable,
        )

        resolve_fn: MaintainableResolver
        resolve_fn = resolve_maintainable if resolver is None else resolver.resolve

        def _resolve(target: ResolveIdentifier) -> MaintainableBase | None:
            return resolve_fn(target)

        fragments: list[QuestionMaintainableBase]
        if self.question_fragments:
            fragments = list(self.question_fragments)
        else:
            fragments = [
                *self.questions,
                *self.question_grids,
                *self.question_blocks,
                *self.question_groups,
            ]

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

        for fragment in fragments:
            _add(fragment)

        reference_groups = [
            self.question_item_references,
            self.question_grid_references,
            self.question_block_references,
            self.question_group_references,
        ]
        for references in reference_groups:
            for reference in references:
                resolved = _resolve(reference)
                if isinstance(resolved, QuestionMaintainableBase):
                    _add(resolved)

        return results


@dataclass
class DataCaptureDevelopment(DataCaptureDevelopmentFields):
    """Maintainable representation of ``d:DataCaptureDevelopment`` entries."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "DataCaptureDevelopment")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")


@dataclass
class OutParameter:
    """Representation of ``r:OutParameter`` definitions."""

    urn: str | None = None
    agency: str | None = None
    identifier: str | None = None
    version: str | None = None
    alias: str | None = None
    representation: Element | None = None
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(REUSABLE_NS, "OutParameter")

    @classmethod
    def from_xml(cls, element: Element) -> OutParameter:
        if element.tag != cls.TAG:
            raise ValueError("Expected a reusable:OutParameter element.")
        urn_el = element.find(qn(REUSABLE_NS, "URN"))
        agency_el = element.find(qn(REUSABLE_NS, "Agency"))
        identifier_el = element.find(qn(REUSABLE_NS, "ID"))
        version_el = element.find(qn(REUSABLE_NS, "Version"))
        alias_el = element.find(qn(REUSABLE_NS, "Alias"))
        representation_el = element.find(qn(REUSABLE_NS, "CodeRepresentation"))
        if representation_el is None:
            representation_el = element.find(qn(REUSABLE_NS, "NumericRepresentation"))
        recognized = {
            qn(REUSABLE_NS, "URN"),
            qn(REUSABLE_NS, "Agency"),
            qn(REUSABLE_NS, "ID"),
            qn(REUSABLE_NS, "Version"),
            qn(REUSABLE_NS, "Alias"),
        }
        if representation_el is not None:
            recognized.add(representation_el.tag)
        extras = preserve_unrecognized_children(element, recognized)
        return cls(
            urn=urn_el.text if urn_el is not None else None,
            agency=agency_el.text if agency_el is not None else None,
            identifier=identifier_el.text if identifier_el is not None else None,
            version=version_el.text if version_el is not None else None,
            alias=alias_el.text if alias_el is not None else None,
            representation=clone_element(representation_el)
            if representation_el is not None
            else None,
            other_elements=extras,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.urn:
            urn_el = create_element(qn(REUSABLE_NS, "URN"))
            urn_el.text = self.urn
            element.append(urn_el)
        if self.agency:
            agency_el = create_element(qn(REUSABLE_NS, "Agency"))
            agency_el.text = self.agency
            element.append(agency_el)
        if self.identifier:
            id_el = create_element(qn(REUSABLE_NS, "ID"))
            id_el.text = self.identifier
            element.append(id_el)
        if self.version:
            version_el = create_element(qn(REUSABLE_NS, "Version"))
            version_el.text = self.version
            element.append(version_el)
        if self.alias is not None:
            alias_el = create_element(qn(REUSABLE_NS, "Alias"))
            alias_el.text = self.alias
            element.append(alias_el)
        if self.representation is not None:
            element.append(clone_element(self.representation))
        for child in self.other_elements:
            element.append(clone_element(child))
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class ConstructSequence:
    """Representation of ``d:ConstructSequence`` containers."""

    item_sequence_type: str | None = None
    control_construct_references: list[Reference] = field(default_factory=list)
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ConstructSequence")

    @classmethod
    def from_xml(cls, element: Element) -> ConstructSequence:
        if element.tag != cls.TAG:
            raise ValueError("Expected a datacollection:ConstructSequence element.")
        recognized = {
            qn(DATA_COLLECTION_NS, "ItemSequenceType"),
            qn(DATA_COLLECTION_NS, "ControlConstructReference"),
        }
        item_sequence_el = element.find(qn(DATA_COLLECTION_NS, "ItemSequenceType"))
        item_sequence_type = (
            item_sequence_el.text if item_sequence_el is not None else None
        )
        references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ControlConstructReference")
            )
        ]
        extras = preserve_unrecognized_children(element, recognized)
        return cls(
            item_sequence_type=item_sequence_type,
            control_construct_references=references,
            other_elements=extras,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.item_sequence_type is not None:
            item_el = create_element(qn(DATA_COLLECTION_NS, "ItemSequenceType"))
            item_el.text = self.item_sequence_type
            element.append(item_el)
        for reference in self.control_construct_references:
            element.append(
                reference.to_xml(
                    "ControlConstructReference", namespace=DATA_COLLECTION_NS
                )
            )
        for child in self.other_elements:
            element.append(clone_element(child))
        apply_other_attributes(element, self.other_attributes)
        return element


@dataclass
class Sequence(ControlConstructBase):
    """Maintainable representation of ``d:Sequence`` control constructs."""

    out_parameters: list[OutParameter] = field(default_factory=list)
    type_of_sequence: str | None = None
    control_construct_references: list[Reference] = field(default_factory=list)
    construct_sequence: ConstructSequence | None = None
    bindings: list[Element] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Sequence")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    @classmethod
    def from_xml(cls, element: Element) -> Sequence:
        recognized = {
            qn(REUSABLE_NS, "OutParameter"),
            qn(DATA_COLLECTION_NS, "TypeOfSequence"),
            qn(DATA_COLLECTION_NS, "ControlConstructReference"),
            qn(DATA_COLLECTION_NS, "ConstructSequence"),
            qn(REUSABLE_NS, "Binding"),
        }
        data = cls._collect_control_common(element, recognized_children=recognized)
        out_parameters = [
            OutParameter.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "OutParameter"))
        ]
        type_of_sequence_el = element.find(qn(DATA_COLLECTION_NS, "TypeOfSequence"))
        type_of_sequence = (
            type_of_sequence_el.text if type_of_sequence_el is not None else None
        )
        references = [
            Reference.from_xml(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "ControlConstructReference")
            )
        ]
        construct_sequence_nodes = element.findall(
            qn(DATA_COLLECTION_NS, "ConstructSequence")
        )
        construct_sequence = None
        extra_constructs: list[Element] = []
        if construct_sequence_nodes:
            construct_sequence = ConstructSequence.from_xml(construct_sequence_nodes[0])
            if len(construct_sequence_nodes) > 1:
                extra_constructs = [
                    clone_element(node) for node in construct_sequence_nodes[1:]
                ]
        bindings = [
            clone_element(node) for node in element.findall(qn(REUSABLE_NS, "Binding"))
        ]
        if extra_constructs:
            other_elements = data.get("other_elements", [])
            other_elements.extend(extra_constructs)
            data["other_elements"] = other_elements
        return cls(
            out_parameters=out_parameters,
            type_of_sequence=type_of_sequence,
            control_construct_references=references,
            construct_sequence=construct_sequence,
            bindings=bindings,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_control_common(element)
        if self.type_of_sequence is not None:
            type_el = create_element(qn(DATA_COLLECTION_NS, "TypeOfSequence"))
            type_el.text = self.type_of_sequence
            element.append(type_el)
        for reference in self.control_construct_references:
            element.append(
                reference.to_xml(
                    "ControlConstructReference", namespace=DATA_COLLECTION_NS
                )
            )
        if self.construct_sequence is not None:
            element.append(self.construct_sequence.to_xml())
        for binding in self.bindings:
            element.append(clone_element(binding))
        for parameter in self.out_parameters:
            element.append(parameter.to_xml())
        self._append_other_elements(element)
        return element


@dataclass
class ProcessingEvent(VersionableMaintainableBase):
    """Maintainable representation of ``d:ProcessingEvent`` entries."""

    names: list[InternationalString] = field(default_factory=list)
    control_operations: list[Element] = field(default_factory=list)
    cleaning_operations: list[Element] = field(default_factory=list)
    weightings: list[Element] = field(default_factory=list)
    weighting_references: list[Reference] = field(default_factory=list)
    data_appraisal_information: list[Element] = field(default_factory=list)
    processing_instruction_references: list[Element] = field(default_factory=list)
    quality_statement_references: list[Reference] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ProcessingEvent")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    @classmethod
    def from_xml(cls, element: Element) -> ProcessingEvent:
        recognized = {
            qn(DATA_COLLECTION_NS, "ProcessingEventName"),
            qn(DATA_COLLECTION_NS, "ControlOperation"),
            qn(DATA_COLLECTION_NS, "CleaningOperation"),
            qn(DATA_COLLECTION_NS, "Weighting"),
            qn(DATA_COLLECTION_NS, "WeightingReference"),
            qn(DATA_COLLECTION_NS, "DataAppraisalInformation"),
            qn(REUSABLE_NS, "ProcessingInstructionReference"),
            qn(REUSABLE_NS, "QualityStatementReference"),
        }
        data = cls._collect_versionable_common(element, recognized_children=recognized)
        names: list[InternationalString] = []
        for container in element.findall(qn(DATA_COLLECTION_NS, "ProcessingEventName")):
            names.extend(InternationalString.from_container(container))
        control_operations = [
            clone_element(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "ControlOperation"))
        ]
        cleaning_operations = [
            clone_element(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "CleaningOperation"))
        ]
        weightings = [
            clone_element(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "Weighting"))
        ]
        weighting_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "WeightingReference"))
        ]
        data_appraisal_information = [
            _normalize_data_appraisal_information(node)
            for node in element.findall(
                qn(DATA_COLLECTION_NS, "DataAppraisalInformation")
            )
        ]
        processing_instruction_references = [
            clone_element(node)
            for node in element.findall(
                qn(REUSABLE_NS, "ProcessingInstructionReference")
            )
        ]
        quality_statement_references = [
            Reference.from_xml(node)
            for node in element.findall(qn(REUSABLE_NS, "QualityStatementReference"))
        ]
        return cls(
            names=names,
            control_operations=control_operations,
            cleaning_operations=cleaning_operations,
            weightings=weightings,
            weighting_references=weighting_references,
            data_appraisal_information=data_appraisal_information,
            processing_instruction_references=processing_instruction_references,
            quality_statement_references=quality_statement_references,
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_versionable_common(element)
        for name in self.names:
            container = create_element(qn(DATA_COLLECTION_NS, "ProcessingEventName"))
            container.append(name.to_child(child_tag="String"))
            element.append(container)
        for node in self.control_operations:
            element.append(clone_element(node))
        for node in self.cleaning_operations:
            element.append(clone_element(node))
        for node in self.weightings:
            element.append(clone_element(node))
        for reference in self.weighting_references:
            element.append(
                reference.to_xml("WeightingReference", namespace=DATA_COLLECTION_NS)
            )
        for node in self.data_appraisal_information:
            element.append(_normalize_data_appraisal_information(node))
        for node in self.processing_instruction_references:
            element.append(clone_element(node))
        for reference in self.quality_statement_references:
            element.append(reference.to_xml("QualityStatementReference"))
        self._append_other_elements(element)
        return element


@dataclass
class ProcessingEventScheme(ProcessingEventSchemeFields):
    """Maintainable wrapper for ``d:ProcessingEventScheme`` structures."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ProcessingEventScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    _TYPED_CHILDREN: ClassVar[dict[str, type]] = {
        "processing_events": ProcessingEvent,
    }

    def __post_init__(self) -> None:
        self._propagate_child_identification(
            self.processing_events,  # type: ignore[arg-type]
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "processing-event", index
            ),
        )


@dataclass
class GeneralInstruction(GeneralInstructionFields):
    """Maintainable representation of ``d:GeneralInstruction`` elements."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GeneralInstruction")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")


@dataclass
class GenerationInstruction(GenerationInstructionFields):
    """Maintainable representation of ``d:GenerationInstruction`` entries."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "GenerationInstruction")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    _TYPED_CHILDREN: ClassVar[dict[str, type]] = {
        "input_question_references": SourceReference,
        "input_measurement_references": SourceReference,
        "input_variable_references": SourceReference,
    }


@dataclass
class ProcessingInstructionGroup(ProcessingInstructionGroupFields):
    """Maintainable wrapper for ``d:ProcessingInstructionGroup`` entries."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ProcessingInstructionGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")


@dataclass
class ProcessingInstructionScheme(ProcessingInstructionSchemeFields):
    """Maintainable wrapper for ``d:ProcessingInstructionScheme`` items."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ProcessingInstructionScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    _TYPED_CHILDREN: ClassVar[dict[str, type]] = {
        "general_instructions": GeneralInstruction,
        "generation_instructions": GenerationInstruction,
        "processing_instruction_groups": ProcessingInstructionGroup,
    }

    def __post_init__(self) -> None:
        def _suffix(base: str) -> Callable[[int, MaintainableBase], str | None]:
            return lambda index, _child: self._default_child_suffix(base, index)

        self._propagate_child_identification(
            self.general_instructions,  # type: ignore[arg-type]
            identifier_suffix_factory=_suffix("general-instruction"),
        )
        self._propagate_child_identification(
            self.generation_instructions,  # type: ignore[arg-type]
            identifier_suffix_factory=_suffix("generation-instruction"),
        )
        self._propagate_child_identification(
            self.processing_instruction_groups,  # type: ignore[arg-type]
            identifier_suffix_factory=_suffix("processing-instruction-group"),
        )


@dataclass
class SamplingPlan(SamplingPlanFields):
    """Maintainable representation of ``d:SamplingPlan`` entries."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SamplingPlan")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")


@dataclass
class SamplingInformationGroup(SamplingInformationGroupFields):
    """Maintainable representation of ``d:SamplingInformationGroup`` entries."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SamplingInformationGroup")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")


@dataclass
class SamplingInformationScheme(SamplingInformationSchemeFields):
    """Maintainable representation of ``d:SamplingInformationScheme`` entries."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "SamplingInformationScheme")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
    _TYPED_CHILDREN: ClassVar[dict[str, type]] = {
        "sampling_plans": SamplingPlan,
        "sampling_information_groups": SamplingInformationGroup,
    }

    def __post_init__(self) -> None:
        self._propagate_child_identification(
            self.sampling_plans,  # type: ignore[arg-type]
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "sampling-plan", index
            ),
        )
        self._propagate_child_identification(
            self.sampling_information_groups,  # type: ignore[arg-type]
            identifier_suffix_factory=lambda index, _child: self._default_child_suffix(
                "sampling-information-group", index
            ),
        )


@dataclass
class ComputationItem(ComputationItemFields):
    """Maintainable representation of ``d:ComputationItem`` constructs."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ComputationItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")


@dataclass
class Loop(ControlConstructBase):
    """Maintainable representation of ``d:Loop`` control constructs.

    A loop repeats the construct named by ``control_construct_reference`` until
    the ``loop_while`` condition is met. All loop-specific children are
    optional in the DDI schema, so a loop created with just a name validates.
    """

    loop_variable_reference: Reference | None = None
    initial_value: Element | None = None
    loop_while: Element | None = None
    step_value: Element | None = None
    control_construct_reference: Reference | None = None

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "Loop")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    @classmethod
    def from_xml(cls, element: Element) -> Loop:
        recognized = {
            qn(DATA_COLLECTION_NS, "LoopVariableReference"),
            qn(DATA_COLLECTION_NS, "InitialValue"),
            qn(DATA_COLLECTION_NS, "LoopWhile"),
            qn(DATA_COLLECTION_NS, "StepValue"),
            qn(DATA_COLLECTION_NS, "ControlConstructReference"),
        }
        data = cls._collect_control_common(element, recognized_children=recognized)

        def _reference(tag: str) -> Reference | None:
            node = element.find(qn(DATA_COLLECTION_NS, tag))
            return Reference.from_xml(node) if node is not None else None

        def _element(tag: str) -> Element | None:
            node = element.find(qn(DATA_COLLECTION_NS, tag))
            return clone_element(node) if node is not None else None

        return cls(
            loop_variable_reference=_reference("LoopVariableReference"),
            initial_value=_element("InitialValue"),
            loop_while=_element("LoopWhile"),
            step_value=_element("StepValue"),
            control_construct_reference=_reference("ControlConstructReference"),
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_control_common(element)
        if self.loop_variable_reference is not None:
            element.append(
                self.loop_variable_reference.to_xml(
                    "LoopVariableReference", namespace=DATA_COLLECTION_NS
                )
            )
        if self.initial_value is not None:
            element.append(clone_element(self.initial_value))
        if self.loop_while is not None:
            element.append(clone_element(self.loop_while))
        if self.step_value is not None:
            element.append(clone_element(self.step_value))
        if self.control_construct_reference is not None:
            element.append(
                self.control_construct_reference.to_xml(
                    "ControlConstructReference", namespace=DATA_COLLECTION_NS
                )
            )
        self._append_other_elements(element)
        return element


@dataclass
class StatementItem(ControlConstructBase):
    """Maintainable representation of ``d:StatementItem`` constructs."""

    display_texts: list[Element] = field(default_factory=list)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "StatementItem")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    @classmethod
    def from_xml(cls, element: Element) -> StatementItem:
        recognized = {qn(DATA_COLLECTION_NS, "DisplayText")}
        data = cls._collect_control_common(element, recognized_children=recognized)
        display_texts = [
            _normalize_statement_display_text(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "DisplayText"))
        ]
        return cls(display_texts=display_texts, **data)

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_control_common(element)
        for node in self.display_texts:
            element.append(_normalize_statement_display_text(node))
        self._append_other_elements(element)
        return element


def _normalize_statement_display_text(element: Element) -> Element:
    """Clone ``DisplayText`` ensuring ``d:Text`` children inline their content."""
    normalized = clone_element(element)
    text_tag = qn(DATA_COLLECTION_NS, "Text")
    content_tag = qn(REUSABLE_NS, "Content")
    for text_el in normalized.findall(f".//{text_tag}"):
        original_children = list(text_el)
        if not original_children:
            continue
        original_attributes = dict(text_el.attrib)
        original_text = text_el.text if text_el.text and text_el.text.strip() else None
        original_tail = text_el.tail if text_el.tail and text_el.tail.strip() else None
        text_el.clear()
        text_el.attrib.update(original_attributes)
        text_el.text = original_text
        text_el.tail = original_tail
        last_node: Element | None = None
        for child in original_children:
            if child.tag != content_tag:
                new_child = clone_element(child)
                text_el.append(new_child)
                last_node = new_child
                continue
            for key, value in child.attrib.items():
                text_el.set(key, value)
            if child.text:
                if last_node is None:
                    text_el.text = (text_el.text or "") + child.text
                else:
                    last_node.tail = (last_node.tail or "") + child.text
            for grandchild in child:
                new_grandchild = clone_element(grandchild)
                text_el.append(new_grandchild)
                last_node = new_grandchild
            if child.tail:
                if last_node is None:
                    text_el.tail = (text_el.tail or "") + child.tail
                else:
                    last_node.tail = (last_node.tail or "") + child.tail
    return normalized


def _flatten_if_condition_element(condition: Element) -> Element:
    """Clone an ``IfCondition`` element, unwrapping ``r:CommandCode`` if present."""
    flattened = clone_element(condition)
    children = list(flattened)
    if len(children) == 1 and children[0].tag == qn(REUSABLE_NS, "CommandCode"):
        command_code = children[0]
        flattened.remove(command_code)
        for child in command_code:
            flattened.append(clone_element(child))
    return flattened


def make_if_condition(
    command: str,
    *,
    description: str | None = None,
    language: str = "python",
    lang: str = "en",
) -> Element:
    """Build a ``d:IfCondition`` element from a command expression.

    This is the value expected by :attr:`IfThenElse.if_condition` and
    :attr:`ElseIf.if_condition`. The result is a ``CommandCode`` carrying an
    optional human-readable ``Description`` and a single ``Command`` whose
    ``CommandContent`` holds the expression (e.g. ``"age >= 16"``).

    Args:
        command: The expression to evaluate, in ``language``.
        description: Optional plain-language summary of the condition.
        language: The programming language of ``command`` (default ``python``).
        lang: The language tag for ``description`` (default ``en``).

    Returns:
        Element: A ``d:IfCondition`` element ready to assign to a construct.
    """
    element = create_element(qn(DATA_COLLECTION_NS, "IfCondition"))
    if description is not None:
        description_el = create_element(qn(REUSABLE_NS, "Description"))
        description_el.append(
            InternationalString(text=description, lang=lang).to_child(
                child_tag="Content"
            )
        )
        element.append(description_el)
    command_el = create_element(qn(REUSABLE_NS, "Command"))
    program_language_el = create_element(qn(REUSABLE_NS, "ProgramLanguage"))
    program_language_el.text = language
    command_el.append(program_language_el)
    command_content_el = create_element(qn(REUSABLE_NS, "CommandContent"))
    command_content_el.text = command
    command_el.append(command_content_el)
    element.append(command_el)
    return element


@dataclass
class ElseIf:
    """Representation of ``d:ElseIf`` helper nodes within If-Then-Else flows."""

    if_condition: Element | None = None
    then_construct_reference: Reference | None = None
    other_elements: list[Element] = field(default_factory=list)
    other_attributes: dict[str, str] = field(default_factory=dict)

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "ElseIf")

    @classmethod
    def from_xml(cls, element: Element) -> ElseIf:
        if element.tag != cls.TAG:
            raise ValueError("Expected a datacollection:ElseIf element.")
        recognized = {
            qn(DATA_COLLECTION_NS, "IfCondition"),
            qn(DATA_COLLECTION_NS, "ThenConstructReference"),
        }
        if_condition = element.find(qn(DATA_COLLECTION_NS, "IfCondition"))
        then_reference_el = element.find(
            qn(DATA_COLLECTION_NS, "ThenConstructReference")
        )
        extras = preserve_unrecognized_children(element, recognized)
        return cls(
            if_condition=(
                _flatten_if_condition_element(if_condition)
                if if_condition is not None
                else None
            ),
            then_construct_reference=(
                Reference.from_xml(then_reference_el)
                if then_reference_el is not None
                else None
            ),
            other_elements=extras,
            other_attributes=collect_other_attributes(element),
        )

    def to_xml(self) -> Element:
        element = create_element(self.TAG)
        if self.if_condition is not None:
            element.append(_flatten_if_condition_element(self.if_condition))
        if self.then_construct_reference is not None:
            element.append(
                self.then_construct_reference.to_xml(
                    "ThenConstructReference", namespace=DATA_COLLECTION_NS
                )
            )
        apply_other_attributes(element, self.other_attributes)
        return element

    def set_condition(
        self,
        command: str,
        *,
        description: str | None = None,
        language: str = "python",
        lang: str = "en",
    ) -> ElseIf:
        """Set this branch's ``if_condition`` from an expression. Returns self."""
        self.if_condition = make_if_condition(
            command, description=description, language=language, lang=lang
        )
        return self


@dataclass
class IfThenElse(ControlConstructBase):
    """Maintainable representation of ``d:IfThenElse`` constructs."""

    type_of_if_then_else: CodeValue | None = None
    if_condition: Element | None = None
    then_construct_reference: Reference | None = None
    else_if_branches: list[ElseIf] = field(default_factory=list)
    else_construct_reference: Reference | None = None

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "IfThenElse")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")

    @classmethod
    def from_xml(cls, element: Element) -> IfThenElse:
        recognized = {
            qn(DATA_COLLECTION_NS, "TypeOfIfThenElse"),
            qn(DATA_COLLECTION_NS, "IfCondition"),
            qn(DATA_COLLECTION_NS, "ThenConstructReference"),
            qn(DATA_COLLECTION_NS, "ElseIf"),
            qn(DATA_COLLECTION_NS, "ElseConstructReference"),
        }
        data = cls._collect_control_common(element, recognized_children=recognized)
        type_el = element.find(qn(DATA_COLLECTION_NS, "TypeOfIfThenElse"))
        if_condition = element.find(qn(DATA_COLLECTION_NS, "IfCondition"))
        then_reference_el = element.find(
            qn(DATA_COLLECTION_NS, "ThenConstructReference")
        )
        else_if_branches = [
            ElseIf.from_xml(node)
            for node in element.findall(qn(DATA_COLLECTION_NS, "ElseIf"))
        ]
        else_reference_el = element.find(
            qn(DATA_COLLECTION_NS, "ElseConstructReference")
        )
        return cls(
            type_of_if_then_else=CodeValue.from_xml(type_el)
            if type_el is not None
            else None,
            if_condition=(
                _flatten_if_condition_element(if_condition)
                if if_condition is not None
                else None
            ),
            then_construct_reference=(
                Reference.from_xml(then_reference_el)
                if then_reference_el is not None
                else None
            ),
            else_if_branches=else_if_branches,
            else_construct_reference=(
                Reference.from_xml(else_reference_el)
                if else_reference_el is not None
                else None
            ),
            **data,
        )

    def to_xml(self) -> Element:
        element = self._build_base_element()
        self._append_control_common(element)
        if self.type_of_if_then_else is not None:
            element.append(
                self.type_of_if_then_else.to_xml(
                    "TypeOfIfThenElse", namespace=DATA_COLLECTION_NS
                )
            )
        if self.if_condition is not None:
            element.append(_flatten_if_condition_element(self.if_condition))
        if self.then_construct_reference is not None:
            element.append(
                self.then_construct_reference.to_xml(
                    "ThenConstructReference", namespace=DATA_COLLECTION_NS
                )
            )
        for branch in self.else_if_branches:
            element.append(branch.to_xml())
        if self.else_construct_reference is not None:
            element.append(
                self.else_construct_reference.to_xml(
                    "ElseConstructReference", namespace=DATA_COLLECTION_NS
                )
            )
        self._append_other_elements(element)
        return element

    def set_condition(
        self,
        command: str,
        *,
        description: str | None = None,
        language: str = "python",
        lang: str = "en",
    ) -> IfThenElse:
        """Set the ``if_condition`` from an expression (e.g. ``"age >= 16"``).

        Returns ``self`` so the call can be chained after ``add_item``.
        """
        self.if_condition = make_if_condition(
            command, description=description, language=language, lang=lang
        )
        return self

    def add_elseif(
        self,
        then_construct_reference: Reference,
        *,
        command: str | None = None,
        description: str | None = None,
        language: str = "python",
        lang: str = "en",
    ) -> ElseIf:
        """Append an ``ElseIf`` branch and return it.

        ``then_construct_reference`` is the construct to run when the branch
        condition holds (use ``target.to_reference()``). Pass ``command`` to set
        the branch condition in one call.
        """
        branch = ElseIf(then_construct_reference=then_construct_reference)
        if command is not None:
            branch.set_condition(
                command, description=description, language=language, lang=lang
            )
        self.else_if_branches.append(branch)
        return branch


@dataclass
class QuestionConstruct(QuestionConstructFields):
    """Maintainable representation of ``d:QuestionConstruct`` control constructs."""

    TAG: ClassVar[str] = qn(DATA_COLLECTION_NS, "QuestionConstruct")
    NSMAP: ClassVar[NamespaceBindings] = build_namespace_map("d")
