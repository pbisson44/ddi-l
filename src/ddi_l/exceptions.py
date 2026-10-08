"""Standardized exception hierarchy for DDI operations.

All DDI-specific exceptions inherit from DDIError and provide rich
context including source location, XPath, and original cause.

Exception Hierarchy:
    DDIError (base)
    ├── DDIReadError       - File/stream reading failures
    │   └── DDIParseError  - Malformed XML or unexpected elements
    ├── DDIWriteError      - Serialization failures
    ├── DDIValidationError - Schema validation failures
    ├── DDIModelError      - Model constraint violations
    │   ├── ModelValidationError      - Validation check failures
    │   ├── ModelBuildError           - Builder/construction failures
    │   └── DuplicateIdentifierError  - Identifier already in use (ValueError)
    └── DDIReferenceError  - Reference resolution failures (LookupError)

Warning hierarchy:
    UserWarning
    └── DDIReferenceWarning - References to items missing from a saved study
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .schema_loader import SchemaValidationIssue

__all__ = [
    "DDIError",
    "DDIModelError",
    "DDIParseError",
    "DDIReadError",
    "DDIReferenceError",
    "DDIReferenceWarning",
    "DDIValidationError",
    "DDIWriteError",
    "DuplicateIdentifierError",
    "ErrorLocation",
    "ModelBuildError",
    "ModelValidationError",
    "build_error_location",
    "location_from_element",
    "location_from_source",
]


def _string_looks_like_xml(value: str) -> bool:
    """Check if a string appears to be XML content."""
    preview = value.lstrip()
    return bool(preview) and preview.startswith("<")


def _coerce_filename(source: object) -> str | None:
    """Extract a filename from various source types."""
    if isinstance(source, Path):
        return str(source)
    if isinstance(source, str):
        if _string_looks_like_xml(source):
            return None
        potential = Path(source)
        if potential.exists():
            return str(potential)
        return None
    name = getattr(source, "name", None)
    if isinstance(name, (str, Path)) and name:
        return str(name)
    return None


@dataclass(frozen=True)
class ErrorLocation:
    """Structured details describing where a problem originated.

    Attributes:
        filename: Source file path, if known.
        xpath: XPath to the problematic element, if applicable.
        line: Line number in source, if available.
        column: Column number in source, if available.
        element_tag: Tag name of the problematic element.

    Example:
        >>> loc = ErrorLocation(
        ...     filename="study.xml", line=42,
        ...     xpath="/DDIInstance/StudyUnit",
        ... )
        >>> print(loc.describe())
        study.xml:42, xpath /DDIInstance/StudyUnit
    """

    filename: str | None = None
    xpath: str | None = None
    line: int | None = None
    column: int | None = None
    element_tag: str | None = None

    def describe(self) -> str | None:
        """Return a human-readable description of this location."""
        parts: list[str] = []

        if self.filename:
            location = self.filename
            if self.line is not None:
                location = f"{location}:{self.line}"
                if self.column is not None:
                    location = f"{location}:{self.column}"
            parts.append(location)
        else:
            line_bits: list[str] = []
            if self.line is not None:
                line_bits.append(f"line {self.line}")
            if self.column is not None:
                line_bits.append(f"column {self.column}")
            if line_bits:
                parts.append(", ".join(line_bits))

        if self.xpath:
            parts.append(f"xpath {self.xpath}")
        elif self.element_tag:
            parts.append(f"element <{self.element_tag}>")

        return ", ".join(parts) if parts else None

    def merge(self, other: ErrorLocation | None) -> ErrorLocation:
        """Combine this location with another, preferring non-None values."""
        if other is None:
            return self
        return ErrorLocation(
            filename=self.filename or other.filename,
            xpath=self.xpath or other.xpath,
            line=self.line or other.line,
            column=self.column or other.column,
            element_tag=self.element_tag or other.element_tag,
        )

    @classmethod
    def combine(cls, *locations: ErrorLocation | None) -> ErrorLocation | None:
        """Combine multiple locations into one."""
        combined: ErrorLocation | None = None
        for location in locations:
            if location is None:
                continue
            combined = location if combined is None else combined.merge(location)
        return combined

    @classmethod
    def from_element(
        cls, element: Any, *, xpath: str | None = None
    ) -> ErrorLocation | None:
        """Create location from an XML element."""
        if element is None:
            return None

        line = getattr(element, "sourceline", None)
        column = getattr(element, "sourcecolumn", None)
        tag = getattr(element, "tag", None)

        # Extract local name from Clark notation
        element_tag = None
        if isinstance(tag, str):
            element_tag = tag.split("}")[-1] if "}" in tag else tag

        location = cls(xpath=xpath, line=line, column=column, element_tag=element_tag)
        return location if location.describe() else None

    @classmethod
    def from_issue(cls, issue: SchemaValidationIssue) -> ErrorLocation | None:
        """Create location from a schema validation issue."""
        location = cls(xpath=issue.xpath, line=issue.line, column=issue.column)
        return location if location.describe() else None


def location_from_element(
    element: object, *, xpath: str | None = None
) -> ErrorLocation | None:
    """Create an ErrorLocation from an XML element."""
    return ErrorLocation.from_element(element, xpath=xpath)


def location_from_source(source: object) -> ErrorLocation | None:
    """Create an ErrorLocation from a source (file path, file object, etc.)."""
    filename = _coerce_filename(source)
    return ErrorLocation(filename=filename) if filename else None


def element_xpath(element: object) -> str | None:
    """Extract a simple XPath from an element's tag."""
    tag = getattr(element, "tag", None)
    if not isinstance(tag, str):
        return None
    if tag.startswith("{"):
        tag = tag.split("}", 1)[1]
    return f"/{tag}" if tag else None


def build_error_location(
    *,
    sources: Iterable[object] | None = None,
    element: object | None = None,
    xpath: str | None = None,
    line: int | None = None,
    column: int | None = None,
) -> ErrorLocation | None:
    """Build an ErrorLocation from various sources of information.

    Args:
        sources: File paths or file objects to extract filename from.
        element: XML element to extract line/column/tag from.
        xpath: Explicit XPath override.
        line: Explicit line number override.
        column: Explicit column number override.

    Returns:
        Combined ErrorLocation, or None if no location info available.
    """
    explicit = ErrorLocation(xpath=xpath, line=line, column=column)
    location = explicit if explicit.describe() else None

    if element is not None:
        element_location = ErrorLocation.from_element(
            element,
            xpath=xpath or element_xpath(element),
        )
        location = ErrorLocation.combine(location, element_location)

    if sources:
        source_locations = [location_from_source(source) for source in sources]
        location = ErrorLocation.combine(location, *source_locations)

    return location


class DDIError(Exception):
    """Base class for all DDI-specific exceptions.

    All DDI exceptions provide:
    - A human-readable message
    - Optional location information (file, line, xpath)
    - Optional original cause for exception chaining

    Attributes:
        message: The error message without location info.
        location: Structured location information.
        original_exception: The underlying cause, if any.

    Example:
        >>> try:
        ...     raise DDIError("Something went wrong", location=ErrorLocation(line=42))
        ... except DDIError as e:
        ...     print(e.location.line)
        42
    """

    def __init__(
        self,
        message: str,
        *,
        cause: BaseException | None = None,
        location: ErrorLocation | None = None,
    ) -> None:
        self._message = message
        self.location = location

        # Build the full message with location
        rendered = message
        if location is not None:
            description = location.describe()
            if description:
                rendered = f"{message} ({description})"

        super().__init__(rendered)

        # Ensure exception chaining works properly
        self.__cause__ = cause
        self.__ddi_cause__ = cause

    @property
    def message(self) -> str:
        """The error message without location information."""
        return self._message

    @property
    def original_exception(self) -> BaseException | None:
        """The original exception that triggered this error, if any."""
        return self.__ddi_cause__

    def with_location(self, location: ErrorLocation) -> DDIError:
        """Return a copy of this exception with updated location."""
        new_location = self.location.merge(location) if self.location else location
        return self.__class__(
            self._message,
            cause=self.__ddi_cause__,
            location=new_location,
        )


class DDIReadError(DDIError):
    """Raised when reading a DDI document fails.

    This covers file access errors, encoding issues, and other I/O
    problems during document loading.
    """

    pass


class DDIParseError(DDIReadError):
    """Raised when XML parsing fails.

    This covers syntax errors, malformed XML, and structural issues
    encountered during parsing. It is a :class:`DDIReadError`, so code that
    handles read failures also handles malformed input.

    Attributes:
        expected_tag: The tag that was expected, if applicable.
        actual_tag: The tag that was found, if applicable.
        element: The problematic element, if available.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: BaseException | None = None,
        location: ErrorLocation | None = None,
        expected_tag: str | None = None,
        actual_tag: str | None = None,
        element: Any | None = None,
    ) -> None:
        # Auto-build location from element if not provided
        if location is None and element is not None:
            location = ErrorLocation.from_element(element)

        super().__init__(message, cause=cause, location=location)
        self.expected_tag = expected_tag
        self.actual_tag = actual_tag
        self.element = element

    @classmethod
    def tag_mismatch(
        cls,
        expected: str,
        actual: str,
        element: Any | None = None,
    ) -> DDIParseError:
        """Create error for tag mismatch."""
        # Clean up Clark notation for display
        expected_display = expected.split("}")[-1] if "}" in expected else expected
        actual_display = actual.split("}")[-1] if "}" in actual else actual

        return cls(
            f"Expected element <{expected_display}>, found <{actual_display}>",
            expected_tag=expected,
            actual_tag=actual,
            element=element,
        )

    @classmethod
    def from_parser_error(
        cls, error: BaseException, *, sources: Iterable[object] | None = None
    ) -> DDIParseError:
        """Wrap an lxml or stdlib parser error, keeping its line and column."""
        position = getattr(error, "position", None)
        line = getattr(error, "lineno", None)
        column = None
        if isinstance(position, tuple) and len(position) == 2:
            line, column = position
        location = build_error_location(sources=sources, line=line, column=column)
        detail = str(getattr(error, "msg", None) or error)
        # lxml appends the position to its message; the location carries it.
        detail = re.sub(r"[:,]?\s*line \d+, column \d+$", "", detail)
        return cls(f"Malformed XML: {detail}", cause=error, location=location)


class DDIWriteError(DDIError):
    """Raised when writing/serializing a DDI document fails.

    This covers file access errors, encoding issues, and serialization
    problems during document saving.
    """

    pass


class DDIValidationError(DDIError):
    """Raised when schema validation fails.

    Attributes:
        issues: List of individual validation issues found.

    Example:
        >>> try:
        ...     validate(document)
        ... except DDIValidationError as e:
        ...     for issue in e.issues:
        ...         print(f"{issue.severity}: {issue.message}")
    """

    def __init__(
        self,
        message: str,
        *,
        issues: Sequence[SchemaValidationIssue] | None = None,
        cause: BaseException | None = None,
        location: ErrorLocation | None = None,
    ) -> None:
        super().__init__(message, cause=cause, location=location)
        self.issues: list[SchemaValidationIssue] = list(issues or [])

    @classmethod
    def from_schema_error(
        cls,
        error: BaseException,
        *,
        sources: Iterable[object] | None = None,
        fallback_location: ErrorLocation | None = None,
    ) -> DDIValidationError:
        """Create from a schema validation error."""
        issues = list(getattr(error, "issues", []))
        message = str(error)

        issue_location: ErrorLocation | None = None
        if issues:
            primary = issues[0]
            message = primary.message
            issue_location = ErrorLocation.from_issue(primary)

        location = ErrorLocation.combine(issue_location, fallback_location)
        if sources:
            source_locations = [location_from_source(s) for s in sources]
            location = ErrorLocation.combine(location, *source_locations)

        return cls(message, issues=issues, cause=error, location=location)


class DDIModelError(DDIError):
    """Base class for model-related errors.

    Covers issues with model construction, validation, and constraints.
    """

    pass


class DuplicateIdentifierError(DDIModelError, ValueError):
    """Raised when an item is added with an identifier already in the document."""


class ModelValidationError(DDIModelError):
    """Raised when a model instance fails validation checks.

    This is raised by MaintainableBase.validate() and related methods
    when required fields are missing or constraints are violated.

    Attributes:
        model_type: The type of model that failed validation.
        field_name: The specific field that caused the failure, if applicable.

    Example:
        >>> study = StudyUnit(agency=None, identifier="test", version="1.0")
        >>> study.validate()
        ModelValidationError: StudyUnit requires agency when URN is not provided.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: BaseException | None = None,
        location: ErrorLocation | None = None,
        model_type: type | None = None,
        field_name: str | None = None,
    ) -> None:
        super().__init__(message, cause=cause, location=location)
        self.model_type = model_type
        self.field_name = field_name

    @classmethod
    def missing_field(
        cls,
        model_type: type,
        field_name: str,
        context: str | None = None,
    ) -> ModelValidationError:
        """Create error for a missing required field."""
        type_name = model_type.__name__
        message = f"{type_name} requires {field_name}"
        if context:
            message = f"{message} {context}"
        return cls(message, model_type=model_type, field_name=field_name)

    @classmethod
    def invalid_value(
        cls,
        model_type: type,
        field_name: str,
        value: Any,
        reason: str | None = None,
    ) -> ModelValidationError:
        """Create error for an invalid field value."""
        type_name = model_type.__name__
        message = f"{type_name} has invalid {field_name}: {value!r}"
        if reason:
            message = f"{message} ({reason})"
        return cls(message, model_type=model_type, field_name=field_name)


class ModelBuildError(DDIModelError):
    """Raised when model construction via builders fails.

    This is raised by builder classes when required configuration
    is missing or invalid.
    """

    pass


class DDIReferenceError(DDIError, LookupError):
    """Raised when reference resolution fails.

    This occurs when a Reference cannot be resolved to its target
    maintainable within a document.

    Attributes:
        reference_urn: The URN that could not be resolved.
        reference_type: The type of object being referenced.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: BaseException | None = None,
        location: ErrorLocation | None = None,
        reference_urn: str | None = None,
        reference_type: str | None = None,
    ) -> None:
        super().__init__(message, cause=cause, location=location)
        self.reference_urn = reference_urn
        self.reference_type = reference_type

    @classmethod
    def unresolved(
        cls,
        urn: str | None = None,
        identifier: str | None = None,
        type_of_object: str | None = None,
    ) -> DDIReferenceError:
        """Create error for an unresolved reference."""
        if urn:
            message = f"Could not resolve reference: {urn}"
        elif identifier:
            obj = type_of_object or "object"
            message = f"Could not resolve reference to {obj}: {identifier}"
        else:
            message = "Could not resolve reference"

        return cls(message, reference_urn=urn, reference_type=type_of_object)


class DDIReferenceWarning(UserWarning):
    """Warns that references in a serialized model point at missing items.

    One warning is issued per serialization, listing every unresolved
    reference, so it can be filtered with ``warnings.filterwarnings`` by
    category.

    Attributes:
        records: The unresolved references, as
            :class:`~ddi_l.models.base.ReferenceWarning` records.
    """

    def __init__(self, records: Sequence[Any]) -> None:
        self.records = tuple(records)
        details = "; ".join(record.message.rstrip(".") for record in self.records)
        super().__init__(f"{len(self.records)} unresolved reference(s): {details}")
