"""Fallback schema used when the optional ``xmlschema`` dependency is missing."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from .._etree import Element
from ..constants import XML_NS, get_namespace_set
from ._constants import XMLNS_NAMESPACE
from ._conversion import _coerce_element, _dict_to_element
from ._conversion_runtime import (  # type: ignore[attr-defined]
    _collect_declared_namespaces,
    _element_to_dict,
    _normalize_input_mapping,
    _normalize_result_namespaces,
)
from ._preflight import _ensure_identification_elements, _PreflightValidationError


@dataclass
class _FallbackSchema:
    """Minimal schema helper used when the xmlschema package is unavailable."""

    path: Path
    version: str
    namespaces: dict[str | None, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        namespace_set = cast(Mapping[str, str], get_namespace_set(self.version))
        self.instance_namespace: str = namespace_set["INSTANCE_NS"]
        self.reusable_namespace: str = namespace_set["REUSABLE_NS"]
        self.instance_tag = f"{{{self.instance_namespace}}}DDIInstance"
        self.fragment_tag = f"{{{self.instance_namespace}}}FragmentInstance"

        if not self.namespaces:
            self.namespaces.update(
                {
                    None: self.instance_namespace,
                    "": self.instance_namespace,
                    "r": self.reusable_namespace,
                    "s": namespace_set["STUDY_UNIT_NS"],
                    "c": namespace_set["CONCEPTUAL_COMPONENT_NS"],
                    "xml": XML_NS,
                    "xmlns": XMLNS_NAMESPACE,
                }
            )

    def _node_coordinates(self, node: Element | None) -> tuple[int | None, int | None]:
        if node is None:
            return None, None

        def _coerce(value: Any) -> int | None:
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                try:
                    return int(value)
                except ValueError:
                    return None
            return None

        line = _coerce(getattr(node, "sourceline", None))
        column = _coerce(getattr(node, "sourcecolumn", None))
        position = getattr(node, "position", None)
        if isinstance(position, tuple):
            if line is None and len(position) >= 1:
                candidate = _coerce(position[0])
                if candidate is not None:
                    line = candidate
            if column is None and len(position) >= 2:
                candidate = _coerce(position[1])
                if candidate is not None:
                    column = candidate
        return line, column

    def validate(self, document: Any) -> None:
        from . import XMLSchemaValidationError as validation_error_cls  # noqa: N813

        element = _coerce_element(document)
        if element.tag not in {self.instance_tag, self.fragment_tag}:
            line, column = self._node_coordinates(element)
            raise cast(Any, validation_error_cls)(
                "Document root must be DDIInstance or "
                "FragmentInstance in the DDI instance namespace.",
                element,
                line=line,
                column=column,
            )

        if element.tag == self.instance_tag:
            try:
                _ensure_identification_elements(
                    element, reusable_namespace=self.reusable_namespace
                )
            except _PreflightValidationError as exc:
                line, column = self._node_coordinates(element)
                raise cast(Any, validation_error_cls)(
                    exc.message,
                    element,
                    exc.path,
                    line=line,
                    column=column,
                ) from exc

    def to_dict(self, element: Element, *, process_namespaces: bool = True) -> dict:
        result = _element_to_dict(element, process_namespaces=process_namespaces)
        return _normalize_result_namespaces(
            result,
            element,
            self,
            process_namespaces=process_namespaces,
        )

    def from_dict(
        self, data: Mapping[str, Any], *, process_namespaces: bool = True
    ) -> Element:
        normalized = _normalize_input_mapping(
            data,
            self,
            process_namespaces=process_namespaces,
        )
        nsmap: dict[str | None, str] | None = None
        if process_namespaces:
            nsmap = dict(self.namespaces)
            declared = _collect_declared_namespaces(data)
            nsmap.update(declared)
        return _dict_to_element(
            normalized,
            process_namespaces=process_namespaces,
            nsmap=nsmap,
        )


__all__ = ["_FallbackSchema"]
