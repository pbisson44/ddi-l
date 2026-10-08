"""High-level validation helpers for DDI documents and maintainables."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar

from . import schema_loader
from ._etree import Element
from .document import DDIDocument, DDIFragment, Document
from .exceptions import DDIValidationError, ErrorLocation, build_error_location
from .lint import LintFinding, run_lint, run_profile
from .models import MaintainableBase, clone_element

DocumentSource = Document | DDIDocument | Element | str | bytes | Path
FragmentSource = DDIFragment | Element | str | bytes | Path

_WrapperT = TypeVar("_WrapperT", DDIDocument, DDIFragment)

_LINT_CONTAINER_AGENCY = "example.agency"
_LINT_CONTAINER_IDENTIFIER = "lint.container"
_LINT_CONTAINER_VERSION = "1.0"
_LINT_CONTAINER_TITLE = "Lint validation container"


@dataclass(frozen=True)
class ValidationMessage:
    """Normalized representation of validation feedback for UI consumption."""

    message: str
    severity: str
    source: str
    xpath: str | None = None
    context: str | None = None
    location: str | None = None
    rule_id: str | None = None

    def to_dict(self) -> dict:
        """Return a JSON-serialisable representation of the message."""
        return {
            "message": self.message,
            "severity": self.severity,
            "source": self.source,
            "xpath": self.xpath,
            "context": self.context,
            "location": self.location,
            "rule_id": self.rule_id,
        }

    @classmethod
    def from_schema_issue(
        cls, issue: schema_loader.SchemaValidationIssue
    ) -> ValidationMessage:
        """Build a message from a :class:`SchemaValidationIssue`."""
        location = ErrorLocation.from_issue(issue)
        location_description = location.describe() if location else None
        return cls(
            message=issue.message,
            severity=issue.severity,
            source="schema",
            xpath=issue.xpath,
            context=issue.context,
            location=location_description,
        )

    @classmethod
    def from_lint_finding(cls, finding: LintFinding) -> ValidationMessage:
        """Build a message from a :class:`LintFinding`."""
        return cls(
            message=finding.message,
            severity=finding.severity,
            source="lint",
            location=finding.location,
            rule_id=finding.rule_id,
        )


@dataclass
class ValidationReport:
    """Aggregate of schema issues and lint findings produced during validation."""

    schema_issues: list[schema_loader.SchemaValidationIssue]
    lint_findings: list[LintFinding]
    _severity_cache: tuple[bool, bool] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._severity_cache = self._compute_severity()

    def _compute_severity(self) -> tuple[bool, bool]:
        has_error = False
        has_warning = False

        def _consume_severity(severity: str | None) -> None:
            nonlocal has_error, has_warning
            if severity is None:
                return
            normalized = severity.lower()
            if normalized == "error":
                has_error = True
            elif normalized == "warning":
                has_warning = True

        for issue in self.schema_issues:
            _consume_severity(issue.severity)
            if has_error and has_warning:
                break

        if not (has_error and has_warning):
            for finding in self.lint_findings:
                _consume_severity(finding.severity)
                if has_error and has_warning:
                    break

        return (has_error, has_warning)

    def iter_messages(self) -> Iterator[ValidationMessage]:
        """Iterate over unified validation messages."""
        for issue in self.schema_issues:
            yield ValidationMessage.from_schema_issue(issue)
        for finding in self.lint_findings:
            yield ValidationMessage.from_lint_finding(finding)

    def messages(self) -> list[ValidationMessage]:
        """Return a list of merged validation messages."""
        return list(self.iter_messages())

    def has_errors(self) -> bool:
        """Return ``True`` when any message is marked as an error."""
        has_error, _ = self._severity_cache
        return has_error

    def has_warnings(self) -> bool:
        """Return ``True`` when any message is marked as a warning."""
        _, has_warning = self._severity_cache
        return has_warning

    def to_dict(self, *, include_context: bool = True) -> dict:
        """Return a JSON-serialisable representation of the aggregated result."""
        messages: list[dict] = []
        for message in self.iter_messages():
            payload = message.to_dict()
            if not include_context:
                payload.pop("context", None)
            messages.append(payload)

        return {
            "schema_issues": [
                issue.to_dict(include_context=include_context)
                for issue in self.schema_issues
            ],
            "lint_findings": [finding.as_dict() for finding in self.lint_findings],
            "messages": messages,
        }


def _coerce_wrapper(
    source: _WrapperT | Document | Element | str | bytes | Path,
    wrapper_cls: type[_WrapperT],
    *,
    source_label: str,
) -> _WrapperT:
    if isinstance(source, wrapper_cls):
        return source
    if isinstance(source, Document):
        # ``Document`` is what ``new_study()`` and ``open_ddi()`` hand back, so
        # it is the type a caller most naturally has. ``.inner`` flushes any
        # pending edits before returning the underlying ``DDIDocument``.
        inner = source.inner
        if isinstance(inner, wrapper_cls):
            return inner
    if isinstance(source, Element):
        return wrapper_cls(source)
    if isinstance(source, (str, bytes, Path)):
        return wrapper_cls.from_xml(source, validate=False)
    raise TypeError(f"Unsupported {source_label} source type: {type(source)!r}")


def _coerce_document(source: DocumentSource) -> DDIDocument:
    return _coerce_wrapper(source, DDIDocument, source_label="document")


def _coerce_fragment(source: FragmentSource) -> DDIFragment:
    return _coerce_wrapper(source, DDIFragment, source_label="fragment")


def _build_fragment_from_maintainable(maintainable: MaintainableBase) -> DDIFragment:
    fragment = DDIFragment.create(top_level=maintainable)
    fragment.add_fragment(maintainable)
    return fragment


def _build_document_for_lint(fragment: DDIFragment) -> DDIDocument:
    """Create a temporary document container for fragment lint execution."""
    document = DDIDocument.create(
        agency=_LINT_CONTAINER_AGENCY,
        identifier=_LINT_CONTAINER_IDENTIFIER,
        version=_LINT_CONTAINER_VERSION,
        title=_LINT_CONTAINER_TITLE,
    )
    for payload in fragment.iter_fragment_payloads():
        document.root.append(clone_element(payload))
    return document


def _collect_lint(
    document: DDIDocument,
    *,
    lint_rules: Sequence[str] | None = None,
    lint_profile: str | None = None,
) -> list[LintFinding]:
    """Execute lint rules or a profile against ``document``."""
    if lint_profile is not None:
        profile_result = run_profile(
            document, profile_name=lint_profile, include_schema=False
        )
        return profile_result.lint_findings
    return run_lint(document, rules=lint_rules)


def _collect_fragment_lint(
    fragment: DDIFragment,
    *,
    lint_rules: Sequence[str] | None = None,
    lint_profile: str | None = None,
) -> list[LintFinding]:
    """Execute lint rules against ``fragment`` by wrapping it in a document."""
    document = _build_document_for_lint(fragment)
    return _collect_lint(document, lint_rules=lint_rules, lint_profile=lint_profile)


def validate_document(
    source: DocumentSource,
    *,
    include_lint: bool = True,
    lint_rules: Sequence[str] | None = None,
    lint_profile: str | None = None,
    raise_error: bool = False,
    include_context: bool = True,
    version: str | None = None,
) -> ValidationReport:
    """Validate a DDI document and optionally execute lint rules.

    Args:
        source: Document payload to validate.
        include_lint: ``True`` to execute lint rules in addition to schema
            validation.
        lint_rules: Specific lint rule identifiers to run.
        lint_profile: Named lint profile to execute.
        raise_error: ``True`` to raise :class:`DDIValidationError` when issues
            are detected.
        include_context: ``False`` to omit contextual snippets from reported
            schema issues.
        version: DDI schema version to validate against; ``None`` uses the
            version the document declares.
    """
    document = _coerce_document(source)
    root = document.to_etree()
    try:
        schema_issues = schema_loader.validate(
            root,
            raise_error=raise_error,
            include_context=include_context,
            version=version,
        )
    except schema_loader.SchemaValidationError as exc:
        fallback_location = build_error_location(element=root)
        raise DDIValidationError.from_schema_error(
            exc,
            sources=[source],
            fallback_location=fallback_location,
        ) from exc

    lint_findings: list[LintFinding] = []
    if include_lint:
        lint_findings = _collect_lint(
            document, lint_rules=lint_rules, lint_profile=lint_profile
        )

    return ValidationReport(schema_issues=schema_issues, lint_findings=lint_findings)


def validate_fragment(
    source: FragmentSource,
    *,
    include_lint: bool = True,
    lint_rules: Sequence[str] | None = None,
    lint_profile: str | None = None,
    raise_error: bool = False,
    include_context: bool = True,
    version: str | None = None,
) -> ValidationReport:
    """Validate a fragment instance and return structured issues.

    Args:
        source: Fragment payload to validate.
        include_lint: ``True`` to execute lint rules in addition to schema
            validation.
        lint_rules: Specific lint rule identifiers to run.
        lint_profile: Named lint profile to execute.
        raise_error: ``True`` to raise :class:`DDIValidationError` when issues
            are detected.
        include_context: ``False`` to omit contextual snippets from reported
            schema issues.
        version: DDI schema version to validate against; ``None`` uses the
            version the document declares.
    """
    fragment = _coerce_fragment(source)
    root = fragment.to_etree()
    try:
        schema_issues = schema_loader.validate(
            root,
            raise_error=raise_error,
            include_context=include_context,
            version=version,
        )
    except schema_loader.SchemaValidationError as exc:
        fallback_location = build_error_location(element=root)
        raise DDIValidationError.from_schema_error(
            exc,
            sources=[source],
            fallback_location=fallback_location,
        ) from exc
    lint_findings: list[LintFinding] = []
    if include_lint:
        lint_findings = _collect_fragment_lint(
            fragment, lint_rules=lint_rules, lint_profile=lint_profile
        )
    return ValidationReport(schema_issues=schema_issues, lint_findings=lint_findings)


def validate_maintainable(
    maintainable: MaintainableBase,
    *,
    include_lint: bool = True,
    lint_rules: Sequence[str] | None = None,
    lint_profile: str | None = None,
    raise_error: bool = False,
    include_context: bool = True,
) -> ValidationReport:
    """Validate an individual maintainable by wrapping it in a fragment.

    Args:
        maintainable: Maintainable instance to validate.
        include_lint: ``True`` to execute lint rules in addition to schema
            validation.
        lint_rules: Specific lint rule identifiers to run.
        lint_profile: Named lint profile to execute.
        raise_error: ``True`` to raise :class:`DDIValidationError` when issues
            are detected.
        include_context: ``False`` to omit contextual snippets from reported
            schema issues.
    """
    fragment = _build_fragment_from_maintainable(maintainable)
    return validate_fragment(
        fragment,
        include_lint=include_lint,
        lint_rules=lint_rules,
        lint_profile=lint_profile,
        raise_error=raise_error,
        include_context=include_context,
    )


__all__ = [
    "ValidationMessage",
    "ValidationReport",
    "validate_document",
    "validate_fragment",
    "validate_maintainable",
]
