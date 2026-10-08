"""Schema validation utilities and structured reporting helpers."""

from __future__ import annotations

import sys
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass, field
from typing import (
    Any,
    cast,
)

from .._etree import Element
from .._schema_versions import SUPPORTED_SCHEMA_VERSIONS
from ..constants import get_namespace_set
from ..exceptions import DDIValidationError
from . import _libxml2
from ._conversion import _coerce_element
from ._namespaces import (
    _build_xpath_from_tree as _build_xpath_from_tree_python,
)
from ._namespaces import (
    _describe_node,
    _format_tag,
    _local_name,
)
from ._namespaces import (
    _gather_namespaces as _gather_namespaces_python,
)
from ._preflight import (
    _child_text,
    _ensure_identification_elements,
    _PreflightValidationError,
)
from ._versions import detect_version_from_element, normalize_version

_GATHER_NAMESPACES_FUNC = _gather_namespaces_python
_BUILD_XPATH_FROM_TREE_FUNC = _build_xpath_from_tree_python

_KNOWN_TYPE_NAMES_CACHE: set[str] | None = None
_FRAGMENT_GAP_CACHE: dict[str, tuple[frozenset[str], frozenset[tuple[str, str]]]] = {}


@dataclass(frozen=True)
class SchemaValidationIssue:
    """Structured details describing a schema validation problem."""

    message: str
    xpath: str | None
    context: str | None
    node: Element | None = field(default=None, repr=False)
    severity: str = "error"
    line: int | None = None
    column: int | None = None

    def to_dict(self, *, include_context: bool = True) -> dict[str, str | int | None]:
        payload: dict[str, str | int | None] = {
            "message": self.message,
            "xpath": self.xpath,
            "severity": self.severity,
            "line": self.line,
            "column": self.column,
        }
        if include_context:
            payload["context"] = self.context
        return payload


class SchemaValidationError(DDIValidationError):
    """Raised when schema validation fails and details are available.

    A :class:`~ddi_l.exceptions.DDIValidationError`, raised for example by
    ``open_ddi(..., validate=True)``.
    """

    def __init__(self, issues: Sequence[SchemaValidationIssue]):
        if issues:
            primary = issues[0]
            summary = primary.message
            if primary.xpath:
                summary = f"{summary} (at {primary.xpath})"
        else:
            summary = "Schema validation error"
        # DDIValidationError stores ``issues`` and, with no location, renders
        # the message verbatim -- so ``str(exc)`` is unchanged.
        super().__init__(summary, issues=issues)

    def to_dicts(
        self, *, include_context: bool = True
    ) -> list[dict[str, str | int | None]]:
        return [issue.to_dict(include_context=include_context) for issue in self.issues]


def _extract_validation_message(error: BaseException) -> str:
    for attr in ("reason", "message"):
        value = getattr(error, attr, None)
        if isinstance(value, str) and value:
            return value
    if error.args:
        first = error.args[0]
        if isinstance(first, str):
            return first
        return str(first)
    return str(error)


def _build_validation_issue(
    error: BaseException,
    *,
    root: Element,
    schema: Any,
    severity: str = "error",
    include_context: bool = True,
) -> SchemaValidationIssue:
    namespaces = _GATHER_NAMESPACES_FUNC(root, schema)
    node: Element | None = getattr(error, "elem", None)
    if node is None:
        candidate = getattr(error, "obj", None)
        if isinstance(candidate, Element):
            node = candidate
    message = _extract_validation_message(error)

    def _coerce_position(value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return None
        return None

    line: int | None = getattr(error, "line", None)
    column: int | None = getattr(error, "column", None)

    position = getattr(error, "position", None)
    if isinstance(position, tuple):
        if line is None and len(position) >= 1:
            line = _coerce_position(position[0])
        if column is None and len(position) >= 2:
            column = _coerce_position(position[1])

    if line is None:
        candidate_line = getattr(error, "sourceline", None)
        if candidate_line is not None:
            line = _coerce_position(candidate_line)

    if column is None:
        candidate_column = getattr(error, "sourcecolumn", None)
        if candidate_column is not None:
            column = _coerce_position(candidate_column)

    if node is not None:
        if line is None:
            candidate_line = getattr(node, "sourceline", None)
            if candidate_line is not None:
                line = _coerce_position(candidate_line)
        if column is None:
            candidate_column = getattr(node, "sourcecolumn", None)
            if candidate_column is not None:
                column = _coerce_position(candidate_column)

    raw_path = getattr(error, "path", None)
    if raw_path:
        xpath: str | None = str(raw_path)
    else:
        raw_path = getattr(error, "xpath", None)
        xpath = str(raw_path) if raw_path else None
    if not xpath and node is not None:
        xpath = _BUILD_XPATH_FROM_TREE_FUNC(root, node, namespaces)
    if not xpath:
        xpath = f"/{_format_tag(root.tag, namespaces)}"

    target_for_context = node if node is not None else root
    context = (
        _describe_node(target_for_context, namespaces) if include_context else None
    )
    return SchemaValidationIssue(
        message=message,
        xpath=xpath,
        context=context,
        node=node,
        severity=severity,
        line=line,
        column=column,
    )


def _namespace_value(namespaces: Mapping[str, object], key: str) -> str:
    return cast(str, namespaces[key])


def _build_fragment_gap_sets(
    namespaces: Mapping[str, object],
    reusable_namespace: str,
    *,
    version: str | None = None,
) -> tuple[frozenset[str], frozenset[tuple[str, str]]]:
    cache_key = version
    if cache_key is not None:
        cached = _FRAGMENT_GAP_CACHE.get(cache_key)
        if cached is not None:
            return cached

    data_collection_ns = _namespace_value(namespaces, "DATA_COLLECTION_NS")
    methodology_ns = _namespace_value(namespaces, "METHODOLOGY_NS")
    process_ns = _namespace_value(namespaces, "PROCESS_NS")
    study_unit_ns = _namespace_value(namespaces, "STUDY_UNIT_NS")
    logical_product_ns = _namespace_value(namespaces, "LOGICAL_PRODUCT_NS")

    gap_tags: frozenset[str] = frozenset(
        {
            f"{{{data_collection_ns}}}CollectionActivity",
            f"{{{data_collection_ns}}}CollectionEvent",
            f"{{{data_collection_ns}}}DataCaptureDevelopment",
            f"{{{data_collection_ns}}}DataCaptureMethod",
            f"{{{data_collection_ns}}}DataCollectionMethodology",
            f"{{{data_collection_ns}}}DeviationFromSampleDesign",
            f"{{{data_collection_ns}}}ObservationPlan",
            f"{{{data_collection_ns}}}SamplingProcedure",
            f"{{{data_collection_ns}}}TimeMethod",
            f"{{{data_collection_ns}}}WeightingMethodology",
            f"{{{methodology_ns}}}Methodology",
            f"{{{methodology_ns}}}MethodologyItem",
            f"{{{methodology_ns}}}MethodologyScheme",
            f"{{{methodology_ns}}}ReviewEvent",
            f"{{{process_ns}}}Process",
            f"{{{process_ns}}}ProcessControl",
            f"{{{process_ns}}}ProcessControlScheme",
            f"{{{process_ns}}}ProcessMethod",
            f"{{{process_ns}}}ProcessMethodScheme",
            f"{{{process_ns}}}ProcessScheme",
            f"{{{process_ns}}}ProcessStep",
            f"{{{process_ns}}}ProcessStepScheme",
            f"{{{study_unit_ns}}}StudyUnit",
        }
    )

    child_gaps: frozenset[tuple[str, str]] = frozenset(
        {
            (
                f"{{{logical_product_ns}}}StatisticalClassification",
                f"{{{reusable_namespace}}}CodeListReference",
            ),
        }
    )

    results = (gap_tags, child_gaps)
    if cache_key is not None:
        _FRAGMENT_GAP_CACHE[cache_key] = results
    return results


def _clear_fragment_gap_cache() -> None:
    """Reset the cached fragment gap definitions."""
    _FRAGMENT_GAP_CACHE.clear()


def _clear_known_type_name_cache() -> None:
    """Reset the cached maintainable type names."""
    global _KNOWN_TYPE_NAMES_CACHE
    _KNOWN_TYPE_NAMES_CACHE = None


def _resolve_known_type_names() -> set[str]:
    global _KNOWN_TYPE_NAMES_CACHE
    if _KNOWN_TYPE_NAMES_CACHE is not None:
        return set(_KNOWN_TYPE_NAMES_CACHE)
    try:  # pragma: no cover - import guarded for circular dependency
        from ..models.base import MaintainableBase
    except (
        Exception
    ):  # pragma: no cover - defensive fallback when models are unavailable
        names: set[str] = set()
    else:
        names = {_local_name(tag) for tag in MaintainableBase._TAG_REGISTRY}
    _KNOWN_TYPE_NAMES_CACHE = set(names)
    return set(names)


def _evaluate_reference(
    reference: Element,
    *,
    root: Element,
    schema: Any,
    known_types: set[str],
    reusable_namespace: str,
    include_context: bool,
) -> list[SchemaValidationIssue]:
    warnings: list[SchemaValidationIssue] = []
    urn = _child_text(reference, reusable_namespace, "URN")
    agency = _child_text(reference, reusable_namespace, "Agency")
    identifier = _child_text(reference, reusable_namespace, "ID")
    version = _child_text(reference, reusable_namespace, "Version")

    has_structured_identity = bool(agency and identifier)
    if urn is None and not has_structured_identity:
        error = _PreflightValidationError(
            "Reference is missing both URN and Agency/ID identifiers.",
            node=reference,
        )
        warnings.append(
            _build_validation_issue(
                error,
                root=root,
                schema=schema,
                severity="warning",
                include_context=include_context,
            )
        )

    if has_structured_identity and version is None:
        error = _PreflightValidationError(
            "Reference is missing a Version for the provided Agency/ID pair.",
            node=reference,
        )
        warnings.append(
            _build_validation_issue(
                error,
                root=root,
                schema=schema,
                severity="warning",
                include_context=include_context,
            )
        )

    type_of_object = _child_text(reference, reusable_namespace, "TypeOfObject")
    if type_of_object is None:
        error = _PreflightValidationError(
            "Reference is missing a TypeOfObject value.",
            node=reference,
        )
        warnings.append(
            _build_validation_issue(
                error,
                root=root,
                schema=schema,
                severity="warning",
                include_context=include_context,
            )
        )
    else:
        normalized = type_of_object.strip()
        if not normalized:
            error = _PreflightValidationError(
                "Reference TypeOfObject value is empty.",
                node=reference,
            )
            warnings.append(
                _build_validation_issue(
                    error,
                    root=root,
                    schema=schema,
                    severity="warning",
                    include_context=include_context,
                )
            )
        elif " " in normalized:
            error = _PreflightValidationError(
                "Reference TypeOfObject value contains whitespace.",
                node=reference,
            )
            warnings.append(
                _build_validation_issue(
                    error,
                    root=root,
                    schema=schema,
                    severity="warning",
                    include_context=include_context,
                )
            )

    return warnings


def _collect_structural_warnings_python(
    root: Element,
    *,
    schema: Any,
    reusable_namespace: str,
    include_context: bool,
) -> list[SchemaValidationIssue]:
    from . import xmlschema as xmlschema_module

    if xmlschema_module is not None:
        return []

    known_types = _resolve_known_type_names()
    warnings: list[SchemaValidationIssue] = []
    for element in root.iter():
        tag = getattr(element, "tag", None)
        if not isinstance(tag, str):
            continue
        local = _local_name(tag)
        if not local.endswith("Reference"):
            continue
        warnings.extend(
            _evaluate_reference(
                element,
                root=root,
                schema=schema,
                known_types=known_types,
                reusable_namespace=reusable_namespace,
                include_context=include_context,
            )
        )
    return warnings


_COLLECT_STRUCTURAL_WARNINGS_FUNC: Callable[..., list[SchemaValidationIssue]] = (
    _collect_structural_warnings_python
)

_PYTHON_VALIDATION_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "gather_namespaces": _gather_namespaces_python,
    "build_xpath_from_tree": _build_xpath_from_tree_python,
    "collect_structural_warnings": _collect_structural_warnings_python,
}


def _collect_structural_warnings(
    root: Element,
    *,
    schema: Any,
    reusable_namespace: str,
    include_context: bool,
) -> list[SchemaValidationIssue]:
    return _COLLECT_STRUCTURAL_WARNINGS_FUNC(
        root,
        schema=schema,
        reusable_namespace=reusable_namespace,
        include_context=include_context,
    )


def _run_preflight_checks(
    root: Element,
    *,
    schema: Any,
    instance_namespace: str,
    fragment_root_tag: str,
    reusable_namespace: str,
    include_context: bool,
) -> tuple[SchemaValidationIssue | None, list[SchemaValidationIssue]]:
    instance_tag = f"{{{instance_namespace}}}DDIInstance"
    warnings: list[SchemaValidationIssue] = []

    if root.tag not in {instance_tag, fragment_root_tag}:
        error = _PreflightValidationError(
            "Document root must be DDIInstance or "
            "FragmentInstance in the DDI instance namespace.",
            node=root,
        )
        return (
            _build_validation_issue(
                error,
                root=root,
                schema=schema,
                include_context=include_context,
            ),
            warnings,
        )

    if root.tag == instance_tag:
        try:
            _ensure_identification_elements(root, reusable_namespace=reusable_namespace)
        except (
            _PreflightValidationError
        ) as exc:  # pragma: no cover - depends on runtime configuration
            return (
                _build_validation_issue(
                    exc,
                    root=root,
                    schema=schema,
                    include_context=include_context,
                ),
                warnings,
            )

    warnings.extend(
        _collect_structural_warnings(
            root,
            schema=schema,
            reusable_namespace=reusable_namespace,
            include_context=include_context,
        )
    )

    return None, warnings


class _LazySchema:
    """Load the xmlschema schema only when an attribute is first read."""

    def __init__(self, loader: Callable[..., Any], version: str) -> None:
        self._loader = loader
        self._version = version
        self._schema: Any = None

    def __getattr__(self, name: str) -> Any:
        if self._schema is None:
            self._schema = self._loader(version=self._version)
        return getattr(self._schema, name)


def validate(
    document: Any,
    *,
    raise_error: bool = True,
    version: str | None = None,
    include_context: bool = True,
) -> list[SchemaValidationIssue]:
    """Validate a document against the cached schema.

    Args:
        document: XML document or compatible object to validate.
        raise_error: When ``True`` (the default), raise a
            :class:`SchemaValidationError` if issues are found.
        version: Optional schema version override.
        include_context: ``False`` omits the contextual snippet from each
            reported issue to avoid leaking sensitive data.
    """
    from . import get_schema as _get_schema

    root = _coerce_element(document)
    detected_version = version or detect_version_from_element(root)
    try:
        target_version = normalize_version(detected_version)
    except ValueError:
        supported_versions = ", ".join(
            sorted(str(v) for v in SUPPORTED_SCHEMA_VERSIONS)
        )
        if version is not None:
            message = (
                f"Schema version override {version!r} is not "
                f"supported. Supported releases: "
                f"{supported_versions}."
            )
        elif detected_version is not None:
            message = (
                "Document declares unsupported DDI schema version "
                f"{detected_version!r}. Supported releases: {supported_versions}."
            )
        else:
            message = (
                "The document could not be matched to a supported DDI schema "
                f"release. Supported releases: {supported_versions}."
            )
        issue = SchemaValidationIssue(message=message, xpath=None, context=None)
        if raise_error:
            raise SchemaValidationError([issue]) from None
        return [issue]

    namespace_set = get_namespace_set(target_version)
    instance_namespace = _namespace_value(namespace_set, "INSTANCE_NS")
    reusable_namespace = _namespace_value(namespace_set, "REUSABLE_NS")
    fragment_root_tag = f"{{{instance_namespace}}}FragmentInstance"
    fragment_gap_tags, fragment_child_gaps = _build_fragment_gap_sets(
        namespace_set, reusable_namespace, version=target_version
    )

    from . import XMLSchemaValidationError as validation_error_cls  # noqa: N813

    # Loaded on first use: a document libxml2 confirms valid never needs it.
    schema: Any = _LazySchema(_get_schema, target_version)

    is_fragment_document = root.tag == fragment_root_tag

    preflight_error, preflight_warnings = _run_preflight_checks(
        root,
        schema=schema,
        instance_namespace=instance_namespace,
        fragment_root_tag=fragment_root_tag,
        reusable_namespace=reusable_namespace,
        include_context=include_context,
    )
    if preflight_error is not None:
        issues = [preflight_error, *preflight_warnings]
        if raise_error:
            raise SchemaValidationError(issues) from None
        return issues

    if IMPLEMENTATION == "lxml" and _libxml2.is_valid(root, target_version):
        return preflight_warnings

    try:
        schema.validate(root)
    except validation_error_cls as exc:
        gap_child = (
            _identify_fragment_schema_gap(
                exc,
                root=root,
                fragment_gap_tags=fragment_gap_tags,
                fragment_child_gaps=fragment_child_gaps,
            )
            if is_fragment_document
            else None
        )
        if gap_child is not None:
            try:
                _ensure_identification_elements(
                    gap_child, reusable_namespace=reusable_namespace
                )
            except _PreflightValidationError as identification_error:
                issue = _build_validation_issue(
                    identification_error,
                    root=root,
                    schema=schema,
                    include_context=include_context,
                )
                issues = [issue, *preflight_warnings]
                if raise_error:
                    raise SchemaValidationError(issues) from None
                return issues
            if preflight_warnings:
                return preflight_warnings
            return []

        issue = _build_validation_issue(
            exc,
            root=root,
            schema=schema,
            include_context=include_context,
        )
        issues = [issue, *preflight_warnings]
        if raise_error:
            raise SchemaValidationError(issues) from None
        return issues

    if preflight_warnings:
        return preflight_warnings

    return []


def _identify_fragment_schema_gap(
    error: BaseException,
    *,
    root: Element,
    fragment_gap_tags: Collection[str],
    fragment_child_gaps: Collection[tuple[str, str]],
) -> Element | None:
    """Return the fragment child associated with a known schema gap if present."""
    invalid_child = getattr(error, "invalid_child", None)
    if isinstance(invalid_child, Element):
        if invalid_child.tag in fragment_gap_tags:
            return invalid_child
        parent = getattr(error, "obj", None)
        if (
            isinstance(parent, Element)
            and (parent.tag, invalid_child.tag) in fragment_child_gaps
        ):
            return parent
    candidate = getattr(error, "obj", None)
    if isinstance(candidate, Element) and candidate.tag in fragment_gap_tags:
        return candidate

    # Walk up from the element the error was reported on. The offending element
    # is often nested inside the gap-tagged maintainable rather than being it,
    # so neither `invalid_child` nor `obj` matches directly.
    for element in (invalid_child, candidate):
        if not isinstance(element, Element):
            continue
        ancestor = _find_gap_ancestor(root, element, fragment_gap_tags)
        if ancestor is not None:
            return ancestor

    # Last resort for errors without an element reference: match the path.
    # xmlschema renders it in Clark notation only for stdlib trees, so this
    # alone would not work on lxml.
    path = getattr(error, "path", None)
    if isinstance(path, str):
        for tag in fragment_gap_tags:
            namespace, _, local = tag.partition("}")
            local_name = local or namespace
            if tag in path or f":{local_name}" in path or f"/{local_name}" in path:
                located = root.find(f".//{tag}")
                if isinstance(located, Element):
                    return located
    return None


def _find_gap_ancestor(
    root: Element, target: Element, fragment_gap_tags: Collection[str]
) -> Element | None:
    """Return the nearest ancestor of ``target`` carrying a gap tag.

    ``target`` itself counts. Ancestry is resolved by walking ``root`` because
    stdlib elements have no parent pointer, which keeps this identical across
    both XML backends.
    """
    if target.tag in fragment_gap_tags:
        return target

    parents: dict[int, Element] = {}
    for parent in root.iter():
        for child in parent:
            parents[id(child)] = parent

    current: Element | None = parents.get(id(target))
    while current is not None:
        if current.tag in fragment_gap_tags:
            return current
        current = parents.get(id(current))
    return None


def _bind_validation_functions(functions: dict[str, Callable[..., Any]]) -> None:
    global _GATHER_NAMESPACES_FUNC
    global _BUILD_XPATH_FROM_TREE_FUNC
    global _COLLECT_STRUCTURAL_WARNINGS_FUNC

    _GATHER_NAMESPACES_FUNC = functions["gather_namespaces"]
    _BUILD_XPATH_FROM_TREE_FUNC = functions["build_xpath_from_tree"]
    _COLLECT_STRUCTURAL_WARNINGS_FUNC = functions["collect_structural_warnings"]


def _apply_validation_backend(backend: str) -> None:
    backend = backend.lower()
    if backend not in get_available_validation_backends():
        raise ValueError(f"Unsupported backend: {backend}")

    _bind_validation_functions(_PYTHON_VALIDATION_FUNCTIONS)
    globals()["IMPLEMENTATION"] = backend


def get_available_validation_backends() -> tuple[str, ...]:
    """Return the validation backends usable in this environment.

    ``python`` validates with xmlschema. ``lxml`` (with the ``full`` extra)
    first checks the document with libxml2 and only runs xmlschema when that
    check fails, so the issues reported are the same on both backends.
    """
    return ("python", "lxml") if _libxml2.available() else ("python",)


def set_validation_backend(backend: str) -> None:
    backend = backend.lower().strip()
    _apply_validation_backend(backend)
    loader_module = sys.modules.get("ddi_l.schema_loader")
    if loader_module is not None:
        loader_module.VALIDATION_IMPLEMENTATION = IMPLEMENTATION  # type: ignore[attr-defined]


IMPLEMENTATION: str = "python"
_default_backend = "lxml" if _libxml2.available() else "python"
_apply_validation_backend(_default_backend)


__all__ = [
    "IMPLEMENTATION",
    "SchemaValidationError",
    "SchemaValidationIssue",
    "get_available_validation_backends",
    "set_validation_backend",
    "validate",
]
