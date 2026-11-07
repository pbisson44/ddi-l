"""Schema validation utilities and structured reporting helpers."""

from __future__ import annotations

from collections.abc import Callable, Collection, Iterator, Mapping, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import (
    Any,
    cast,
)

from .._etree import Element
from .._schema_versions import SUPPORTED_SCHEMA_VERSIONS
from ..constants import get_namespace_set
from ..exceptions import DDIValidationError
from . import _libxml2, _native_validation
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

# The maintainable type names, read once from the model registry.
_KNOWN_TYPE_NAMES_CACHE: dict[str, frozenset[str]] = {}
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

    A `DDIValidationError`, raised for example by
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
    namespaces = _gather_namespaces_python(root, schema)
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
        xpath = _build_xpath_from_tree_python(root, node, namespaces)
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
    logical_product_ns = _namespace_value(namespaces, "LOGICAL_PRODUCT_NS")

    # Elements this library writes as fragments that DDI's FragmentType does
    # not list (DDI elements that are not items), plus the library's own
    # extension types, which no DDI schema defines. Real fragment items --
    # s:StudyUnit, d:DataCaptureDevelopment, d:WeightingMethodology -- are not
    # gaps: an error inside one is an error.
    gap_tags: frozenset[str] = frozenset(
        {
            f"{{{data_collection_ns}}}CollectionActivity",
            f"{{{data_collection_ns}}}CollectionEvent",
            f"{{{data_collection_ns}}}DataCaptureMethod",
            f"{{{data_collection_ns}}}DataCollectionMethodology",
            f"{{{data_collection_ns}}}DeviationFromSampleDesign",
            f"{{{data_collection_ns}}}ObservationPlan",
            f"{{{data_collection_ns}}}SamplingProcedure",
            f"{{{data_collection_ns}}}TimeMethod",
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
    _KNOWN_TYPE_NAMES_CACHE.clear()


def _resolve_known_type_names() -> set[str]:
    cached = _KNOWN_TYPE_NAMES_CACHE.get("names")
    if cached is not None:
        return set(cached)
    try:  # pragma: no cover - import guarded for circular dependency
        from ..models.base import MaintainableBase
    except (
        Exception
    ):  # pragma: no cover - defensive fallback when models are unavailable
        names: set[str] = set()
    else:
        names = {_local_name(tag) for tag in MaintainableBase._TAG_REGISTRY}
    _KNOWN_TYPE_NAMES_CACHE["names"] = frozenset(names)
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


def _collect_structural_warnings(
    root: Element,
    *,
    schema: Any,
    reusable_namespace: str,
    include_context: bool,
) -> list[SchemaValidationIssue]:
    return _collect_structural_warnings_python(
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
    max_issues: int | None = None,
    backend: str | None = None,
) -> list[SchemaValidationIssue]:
    """Validate a document against the cached schema.

    Every schema error is reported, in document order, then the warnings.
    An error found before the schema is read (a missing identification, an
    unsupported version) is reported alone.

    Args:
        document: XML document or compatible object to validate.
        raise_error: When ``True`` (the default), raise a
            `SchemaValidationError` if issues are found.
        version: Optional schema version override.
        include_context: ``False`` omits the contextual snippet from each
            reported issue to avoid leaking sensitive data.
        max_issues: Stop after this many schema errors and add a warning
            saying so; ``None`` reports them all.
        backend: ``"python"``, ``"lxml"`` or ``"native"`` (see
            `get_available_validation_backends`); ``None`` uses
            `get_validation_backend`. The issues are the same on each.

    Raises:
        ValueError: If ``max_issues`` is below one, or ``backend`` is not
            available.
    """
    from . import get_schema as _get_schema

    if max_issues is not None and max_issues < 1:
        raise ValueError(f"max_issues must be at least 1, not {max_issues}.")
    backend = _checked_backend(backend) if backend else get_validation_backend()

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

    if backend == "lxml" and _libxml2.is_valid(root, target_version):
        return preflight_warnings
    schema_errors = _schema_errors(schema, root, validation_error_cls)
    if backend == "native":
        flagged = _native_validation.unflagged(root, target_version)
        if flagged == []:
            return preflight_warnings
        if flagged is not None:
            schema_errors = _native_validation.schema_errors(
                _get_schema(target_version), root, target_version, flagged
            )

    # A known gap is checked for identification and passed over; validation
    # then goes on, so a gap early in a fragment does not hide an error in a
    # later one.
    errors: list[SchemaValidationIssue] = []
    parents: dict[int, Element] = {}
    for exc in schema_errors:
        if max_issues is not None and len(errors) == max_issues:
            noun = "error" if max_issues == 1 else "errors"
            errors.append(
                SchemaValidationIssue(
                    message=(
                        f"Schema validation stopped after {max_issues} {noun}; "
                        "there may be more."
                    ),
                    xpath=None,
                    context=None,
                    severity="warning",
                )
            )
            break
        gap_child = (
            _identify_fragment_schema_gap(
                exc,
                root=root,
                fragment_gap_tags=fragment_gap_tags,
                fragment_child_gaps=fragment_child_gaps,
                parents=parents,
            )
            if is_fragment_document
            else None
        )
        if gap_child is not None:
            if gap_child.tag not in fragment_gap_tags:
                # Extension content nested in an item (m:MethodologyStatement):
                # nothing a schema or an identification check can say about it.
                continue
            try:
                _ensure_identification_elements(
                    gap_child, reusable_namespace=reusable_namespace
                )
            except _PreflightValidationError as identification_error:
                errors.append(
                    _build_validation_issue(
                        identification_error,
                        root=root,
                        schema=schema,
                        include_context=include_context,
                    )
                )
            continue

        errors.append(
            _build_validation_issue(
                exc,
                root=root,
                schema=schema,
                include_context=include_context,
            )
        )

    issues = [*errors, *preflight_warnings]
    if errors and raise_error:
        raise SchemaValidationError(issues) from None
    return issues


def _schema_errors(
    schema: Any, root: Element, error_cls: type[BaseException]
) -> Iterator[BaseException]:
    """Yield the schema errors in ``root``.

    All of them where the schema object can iterate them (xmlschema), else
    the first one ``validate`` raises.
    """
    iter_errors = getattr(schema, "iter_errors", None)
    if callable(iter_errors):
        yield from iter_errors(root)
        return
    try:
        schema.validate(root)
    except error_cls as exc:
        yield exc


def _identify_fragment_schema_gap(
    error: BaseException,
    *,
    root: Element,
    fragment_gap_tags: Collection[str],
    fragment_child_gaps: Collection[tuple[str, str]],
    parents: dict[int, Element] | None = None,
) -> Element | None:
    """Return the fragment child associated with a known schema gap if present.

    A DDI element that is not a fragment item (``d:CollectionEvent``) is a gap
    only where it stands as a fragment: directly in a ``<Fragment>``. Inside
    an item it is ordinary DDI content and its errors are real. Only the
    library's extension types (``urn:ddi-l:extension:...``), which no schema
    can check, are passed over wherever an error inside them is reported.
    """
    extension_tags = frozenset(tag for tag in fragment_gap_tags if _is_extension(tag))
    invalid_child = getattr(error, "invalid_child", None)
    parent = getattr(error, "obj", None)
    if isinstance(invalid_child, Element):
        if _is_extension(invalid_child.tag):
            return invalid_child
        if (
            invalid_child.tag in fragment_gap_tags
            and isinstance(parent, Element)
            and isinstance(parent.tag, str)
            and parent.tag.endswith("}Fragment")
        ):
            return invalid_child
        if (
            isinstance(parent, Element)
            and (parent.tag, invalid_child.tag) in fragment_child_gaps
        ):
            return parent
    candidate = parent
    if isinstance(candidate, Element) and _is_extension(candidate.tag):
        return candidate

    # Walk up from the element the error was reported on: content nested in
    # an extension type is reported on the nested element, not on it.
    for element in (invalid_child, candidate):
        if not isinstance(element, Element):
            continue
        ancestor = _find_gap_ancestor(root, element, extension_tags, parents)
        if ancestor is not None:
            return ancestor

    # Last resort for errors without an element reference: match the path.
    # xmlschema renders it in Clark notation only for stdlib trees, so this
    # alone would not work on lxml.
    path = getattr(error, "path", None)
    if isinstance(path, str):
        for tag in extension_tags:
            namespace, _, local = tag.partition("}")
            local_name = local or namespace
            if tag in path or f":{local_name}" in path or f"/{local_name}" in path:
                located = root.find(f".//{tag}")
                if isinstance(located, Element):
                    return located
    return None


def _is_extension(tag: object) -> bool:
    """Whether ``tag`` is in one of this library's extension namespaces."""
    return isinstance(tag, str) and tag.startswith("{urn:ddi-l:extension:")


def _find_gap_ancestor(
    root: Element,
    target: Element,
    fragment_gap_tags: Collection[str],
    parents: dict[int, Element] | None = None,
) -> Element | None:
    """Return the nearest ancestor of ``target`` carrying a gap tag.

    ``target`` itself counts. Ancestry is resolved by walking ``root`` because
    stdlib elements have no parent pointer, which keeps this identical across
    both XML backends. ``parents``, empty or filled by an earlier call on the
    same ``root``, keeps that walk to one per validation.
    """
    if target.tag in fragment_gap_tags:
        return target

    if parents is None:
        parents = {}
    if not parents:
        for parent in root.iter():
            for child in parent:
                parents[id(child)] = parent

    current: Element | None = parents.get(id(target))
    while current is not None:
        if current.tag in fragment_gap_tags:
            return current
        current = parents.get(id(current))
    return None


def get_available_validation_backends() -> tuple[str, ...]:
    """Return the validation backends usable in this environment, best last.

    ``python`` validates with xmlschema. ``lxml`` (with the ``full`` extra)
    first checks the document with libxml2 and only runs xmlschema when that
    check fails. ``native`` (on the native XML backend) checks the document
    in one pass and has xmlschema word the errors of each element it flags.
    The issues reported are the same on every backend.
    """
    found = ["python"]
    if _libxml2.available():
        found.append("lxml")
    if _native_validation.available():
        found.append("native")
    return tuple(found)


def _checked_backend(backend: str) -> str:
    name = backend.lower().strip()
    if name not in get_available_validation_backends():
        raise ValueError(f"Unsupported validation backend: {backend}")
    return name


# The best backend this environment has, chosen at import.
IMPLEMENTATION: str = get_available_validation_backends()[-1]
# The application default, which only `set_validation_backend` changes.
_DEFAULT_BACKEND = IMPLEMENTATION
_SCOPED_BACKEND: ContextVar[str | None] = ContextVar(
    "ddi_l_validation_backend", default=None
)


def get_validation_backend() -> str:
    """Return the backend `validate` uses when given none.

    That is the one a `validation_backend` block in this thread or task set,
    else the application default.
    """
    return _SCOPED_BACKEND.get() or _DEFAULT_BACKEND


def set_validation_backend(backend: str) -> None:
    """Make ``backend`` the application default for `validate`."""
    global _DEFAULT_BACKEND
    _DEFAULT_BACKEND = _checked_backend(backend)


@contextmanager
def validation_backend(backend: str) -> Iterator[str]:
    """Use ``backend`` in the ``with`` block, in this thread or task only."""
    token = _SCOPED_BACKEND.set(_checked_backend(backend))
    try:
        yield _SCOPED_BACKEND.get() or backend
    finally:
        _SCOPED_BACKEND.reset(token)


__all__ = [
    "IMPLEMENTATION",
    "SchemaValidationError",
    "SchemaValidationIssue",
    "get_available_validation_backends",
    "get_validation_backend",
    "set_validation_backend",
    "validate",
    "validation_backend",
]
