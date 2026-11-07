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
from .lint import LintConfiguration, LintFinding, run_lint, run_profile
from .models import MaintainableBase

DocumentSource = Document | DDIDocument | Element | str | bytes | Path
FragmentSource = DDIFragment | Element | str | bytes | Path

_WrapperT = TypeVar("_WrapperT", DDIDocument, DDIFragment)


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
        """Build a message from a `SchemaValidationIssue`."""
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
        """Build a message from a `LintFinding`."""
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
        # it is the type a caller most naturally has. Flush pending edits and
        # read the underlying ``DDIDocument`` directly: ``.inner`` would also
        # detach any model the caller holds, losing its later edits.
        source._flush()
        inner = source._inner
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


def _collect_lint(
    document: DDIDocument | DDIFragment,
    *,
    lint_rules: Sequence[str] | None = None,
    lint_profile: str | None = None,
    configuration: LintConfiguration | None = None,
) -> list[LintFinding]:
    """Execute lint rules or a profile against ``document``.

    A fragment is linted as itself, as `ddi lint` does, so the rules that
    know a fragment from a whole document see one.
    """
    if lint_profile is not None:
        profile_result = run_profile(
            document,
            profile_name=lint_profile,
            include_schema=False,
            configuration=configuration,
        )
        return profile_result.lint_findings
    return run_lint(document, rules=lint_rules, configuration=configuration)


def validate_document(
    source: DocumentSource,
    *,
    include_lint: bool = True,
    lint_rules: Sequence[str] | None = None,
    lint_profile: str | None = None,
    raise_error: bool = False,
    include_context: bool = True,
    version: str | None = None,
    max_schema_issues: int | None = None,
    lint_configuration: LintConfiguration | None = None,
) -> ValidationReport:
    """Validate a DDI document and optionally execute lint rules.

    Args:
        source: Document payload to validate.
        include_lint: ``True`` to execute lint rules in addition to schema
            validation.
        lint_rules: Specific lint rule identifiers to run.
        lint_profile: Named lint profile to execute.
        raise_error: ``True`` to raise `DDIValidationError` when issues
            are detected.
        include_context: ``False`` to omit contextual snippets from reported
            schema issues.
        version: DDI schema version to validate against; ``None`` uses the
            version the document declares.
        max_schema_issues: Schema errors to report at most; ``None``
            reports them all.
        lint_configuration: The lint configuration for this call, from
            `ddi_l.lint.lint_configuration`; ``None`` keeps the process
            default.
    """
    document = _coerce_document(source)
    root = document.to_etree()
    try:
        schema_issues = schema_loader.validate(
            root,
            raise_error=raise_error,
            include_context=include_context,
            version=version,
            max_issues=max_schema_issues,
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
            document,
            lint_rules=lint_rules,
            lint_profile=lint_profile,
            configuration=lint_configuration,
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
    max_schema_issues: int | None = None,
    lint_configuration: LintConfiguration | None = None,
) -> ValidationReport:
    """Validate a fragment instance and return structured issues.

    Args:
        source: Fragment payload to validate.
        include_lint: ``True`` to execute lint rules in addition to schema
            validation.
        lint_rules: Specific lint rule identifiers to run.
        lint_profile: Named lint profile to execute.
        raise_error: ``True`` to raise `DDIValidationError` when issues
            are detected.
        include_context: ``False`` to omit contextual snippets from reported
            schema issues.
        version: DDI schema version to validate against; ``None`` uses the
            version the document declares.
        max_schema_issues: Schema errors to report at most; ``None``
            reports them all.
        lint_configuration: The lint configuration for this call, from
            `ddi_l.lint.lint_configuration`; ``None`` keeps the process
            default.
    """
    fragment = _coerce_fragment(source)
    root = fragment.to_etree()
    try:
        schema_issues = schema_loader.validate(
            root,
            raise_error=raise_error,
            include_context=include_context,
            version=version,
            max_issues=max_schema_issues,
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
            fragment,
            lint_rules=lint_rules,
            lint_profile=lint_profile,
            configuration=lint_configuration,
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
    lint_configuration: LintConfiguration | None = None,
) -> ValidationReport:
    """Validate an individual maintainable by wrapping it in a fragment.

    Args:
        maintainable: Maintainable instance to validate.
        include_lint: ``True`` to execute lint rules in addition to schema
            validation.
        lint_rules: Specific lint rule identifiers to run.
        lint_profile: Named lint profile to execute.
        raise_error: ``True`` to raise `DDIValidationError` when issues
            are detected.
        include_context: ``False`` to omit contextual snippets from reported
            schema issues.
        lint_configuration: As for `validate_fragment`.
    """
    fragment = _build_fragment_from_maintainable(maintainable)
    return validate_fragment(
        fragment,
        include_lint=include_lint,
        lint_rules=lint_rules,
        lint_profile=lint_profile,
        raise_error=raise_error,
        include_context=include_context,
        lint_configuration=lint_configuration,
    )


__all__ = [
    "ValidationMessage",
    "ValidationReport",
    "validate_document",
    "validate_fragment",
    "validate_maintainable",
]
