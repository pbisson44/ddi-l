"""Mixins and helpers for managing maintainables within DDI documents."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import TypeVar

from ._etree import Element, cleanup_namespaces
from .constants import DEFAULT_NSMAP, REUSABLE_NS
from .exceptions import DDIModelError
from .maintainable_registry import maintainable_type_from_name
from .models.base import MaintainableBase, Reference, qn

_DEFAULT_NS_MAP: Mapping[str | None, str] = DEFAULT_NSMAP


MaintainableT = TypeVar("MaintainableT", bound=MaintainableBase)

MaintainableIdentifier = (
    MaintainableBase | Reference | str | tuple[str | None, str, str | None]
)


class MaintainableManagementMixin:
    """Provide maintainable CRUD helpers for document-like wrappers."""

    _root: Element

    def _require_typed_models(self) -> None:
        """Raise when the document's DDI version has no typed models."""
        version = getattr(self, "_version", None)
        if version is not None and version != "3.3":
            raise DDIModelError(
                f"Typed models are available for DDI 3.3 only; this document is "
                f"DDI {version}. Work with its XML through .root instead."
            )

    def _iter_maintainable_elements(
        self,
        maintainable_type: type[MaintainableBase] | None = None,
    ) -> Iterator[tuple[int, Element, type[MaintainableBase]]]:
        for index, child in enumerate(list(self._root)):
            if maintainable_type is not None:
                if child.tag != maintainable_type.TAG:
                    continue
                yield index, child, maintainable_type
                continue
            maintainable_cls = MaintainableBase.for_tag(child.tag)
            if maintainable_cls is None:
                continue
            yield index, child, maintainable_cls

    def _maintainable_metadata(
        self,
        maintainable: MaintainableBase | Element,
        maintainable_type: type[MaintainableBase] | None = None,
    ) -> tuple[str | None, tuple[str | None, str, str | None] | None]:
        key: tuple[str | None, str, str | None] | None = None

        if isinstance(maintainable, MaintainableBase):
            urn = maintainable._format_urn()
            if maintainable.identifier:
                key = (
                    maintainable.agency,
                    maintainable.identifier,
                    maintainable.version,
                )
            return urn, key

        if not isinstance(maintainable, Element):
            raise TypeError(
                "maintainable must be a MaintainableBase instance or XML element."
            )

        xml_element = maintainable

        def _text(tag: str) -> str | None:
            child = xml_element.find(qn(REUSABLE_NS, tag))
            return None if child is None else child.text

        if maintainable_type is None:
            maintainable_type = MaintainableBase.for_tag(xml_element.tag)

        urn = _text("URN")
        agency = _text("Agency")
        identifier = _text("ID")
        version = _text("Version")

        if (
            urn is None
            and identifier
            and maintainable_type is not None
            and maintainable_type.AUTO_GENERATE_URN
            and agency
            and version
        ):
            urn = f"urn:ddi:{agency}:{identifier}:{version}"

        if identifier:
            key = (agency, identifier, version)

        return urn, key

    def _maintainable_type_from_name(
        self, type_name: str
    ) -> type[MaintainableBase] | None:
        return maintainable_type_from_name(type_name)

    def _reference_metadata(
        self,
        target: MaintainableIdentifier,
    ) -> tuple[
        str | None,
        tuple[str | None, str, str | None] | None,
        type[MaintainableBase] | None,
    ]:
        maintainable_type: type[MaintainableBase] | None = None
        if isinstance(target, MaintainableBase):
            urn, key = self._maintainable_metadata(target)
            maintainable_type = type(target)
        elif isinstance(target, Reference):
            urn = target.urn
            key = (
                None
                if target.identifier is None
                else (target.agency, target.identifier, target.version)
            )
            if target.type_of_object:
                maintainable_type = self._maintainable_type_from_name(
                    target.type_of_object
                )
        elif isinstance(target, str):
            urn = target
            key = None
        elif isinstance(target, tuple):
            if len(target) != 3:
                raise ValueError(
                    "Identifier tuples must contain (agency, identifier, version)."
                )
            urn = None
            key = target
        else:
            raise TypeError(
                f"Unsupported maintainable identifier type: {type(target).__name__}."
            )
        return urn, key, maintainable_type

    def _metadata_matches(
        self,
        candidate_urn: str | None,
        candidate_key: tuple[str | None, str, str | None] | None,
        target_urn: str | None,
        target_key: tuple[str | None, str, str | None] | None,
    ) -> bool:
        if target_urn and candidate_urn and candidate_urn == target_urn:
            return True
        if target_key and candidate_key:
            agency_target, identifier_target, version_target = target_key
            agency_candidate, identifier_candidate, version_candidate = candidate_key
            if identifier_candidate != identifier_target:
                return False
            if version_target is not None and version_candidate != version_target:
                return False
            return not (agency_target is not None and agency_candidate != agency_target)
        return False

    def iter_maintainables(
        self, maintainable_type: type[MaintainableT]
    ) -> Iterator[MaintainableT]:
        """Yield maintainable instances for ``maintainable_type`` stored on the root."""
        self._require_typed_models()
        if not isinstance(maintainable_type, type) or not issubclass(
            maintainable_type, MaintainableBase
        ):
            raise TypeError("maintainable_type must be a subclass of MaintainableBase.")
        for element in self._root.findall(maintainable_type.TAG):
            yield maintainable_type.from_xml(element)

    def add_maintainable(self, maintainable: MaintainableBase) -> Element:
        """Append ``maintainable`` to the document and return the inserted element."""
        self._require_typed_models()
        if not isinstance(maintainable, MaintainableBase):
            raise TypeError("maintainable must be an instance of MaintainableBase.")
        element = maintainable.to_xml()
        self._root.append(element)
        cleanup_namespaces(self._root, dict(_DEFAULT_NS_MAP))
        return element

    def replace_maintainable(self, maintainable: MaintainableBase) -> Element:
        """Replace an existing maintainable matching ``maintainable``'s identity."""
        self._require_typed_models()
        if not isinstance(maintainable, MaintainableBase):
            raise TypeError("maintainable must be an instance of MaintainableBase.")
        target_urn, target_key = self._maintainable_metadata(maintainable)
        if target_urn is None and target_key is None:
            raise ValueError(
                "Maintainable must define a URN or identifier to support replacement."
            )

        matches: list[tuple[int, Element]] = []
        for index, element, cls in self._iter_maintainable_elements(type(maintainable)):
            candidate_urn, candidate_key = self._maintainable_metadata(element, cls)
            if self._metadata_matches(
                candidate_urn, candidate_key, target_urn, target_key
            ):
                matches.append((index, element))

        if not matches:
            raise LookupError("Maintainable not found for replacement.")
        if len(matches) > 1:
            raise ValueError("Multiple maintainables match the provided identity.")

        index, element = matches[0]
        replacement = maintainable.to_xml()
        replacement.tail = element.tail
        self._root.insert(index, replacement)
        self._root.remove(element)
        cleanup_namespaces(self._root, dict(_DEFAULT_NS_MAP))
        return replacement

    def remove_maintainable(
        self,
        target: MaintainableIdentifier,
        *,
        maintainable_type: type[MaintainableBase] | None = None,
    ) -> bool:
        """Remove a maintainable identified by ``target`` from the document."""
        self._require_typed_models()
        urn, key, inferred_type = self._reference_metadata(target)
        if urn is None and key is None:
            raise ValueError("Maintainable removal requires a URN or identifier tuple.")
        if maintainable_type is None:
            maintainable_type = inferred_type

        matches: list[tuple[int, Element]] = []
        for index, element, cls in self._iter_maintainable_elements(maintainable_type):
            candidate_urn, candidate_key = self._maintainable_metadata(element, cls)
            if self._metadata_matches(candidate_urn, candidate_key, urn, key):
                matches.append((index, element))

        if not matches:
            return False
        if len(matches) > 1:
            raise ValueError("Multiple maintainables match the provided identity.")

        _, element = matches[0]
        self._root.remove(element)
        cleanup_namespaces(self._root, dict(_DEFAULT_NS_MAP))
        return True


__all__ = [
    "MaintainableIdentifier",
    "MaintainableManagementMixin",
    "MaintainableT",
]
