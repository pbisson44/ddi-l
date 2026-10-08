"""Response models, so the OpenAPI schema describes real payloads.

Each dataclass mirrors a library payload (``LintFinding.as_dict()``,
``SchemaValidationIssue.to_dict()``, ``ValidationMessage.to_dict()``) with
the same optional fields and defaults. Litestar serializes by the declared
return annotation, so these types are what Swagger shows.

Every example below is a captured response; ``tests/test_server_examples.py``
checks that they still match the running service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Any

from litestar.openapi.spec import Example
from litestar.params import KwargDefinition

__all__ = [
    "EXAMPLE_CLIENT_ERROR",
    "EXAMPLE_HEALTH",
    "EXAMPLE_INDEX",
    "EXAMPLE_INVALID_DOCUMENT",
    "EXAMPLE_LINT",
    "EXAMPLE_PAYLOAD_TOO_LARGE",
    "EXAMPLE_PROFILE",
    "EXAMPLE_TIMEOUT",
    "EXAMPLE_VALID_DOCUMENT",
    "EXAMPLE_VERSIONS",
    "ErrorResponse",
    "HealthResponse",
    "IndexResponse",
    "LintFindingModel",
    "LintResponse",
    "ProfileResponse",
    "SchemaIssueModel",
    "ValidationMessageModel",
    "ValidationResponse",
    "VersionsResponse",
]


def _field(description: str, *examples: object) -> KwargDefinition:
    """Attach a description and examples to a model field.

    Uses ``KwargDefinition`` because ``Parameter`` describes request
    parameters, not response fields.
    """
    return KwargDefinition(
        description=description,
        examples=[Example(value=value) for value in examples],
    )


@dataclass
class SchemaIssueModel:
    """A single XSD validation failure."""

    message: Annotated[
        str,
        _field(
            "What the schema objected to.",
            "Missing required identification element(s): Agency, ID, Version",
        ),
    ]
    severity: Annotated[
        str,
        _field(
            "Always `error` -- a document either satisfies the XSD or does not.",
            "error",
        ),
    ]
    xpath: Annotated[
        str | None,
        _field(
            "Path to the offending element, when the validator reports one.",
            "/DDIInstance",
        ),
    ] = None
    line: Annotated[
        int | None, _field("1-based line in the submitted document.", 2)
    ] = None
    column: Annotated[
        int | None, _field("1-based column, when the validator reports one.", 17)
    ] = None
    context: Annotated[
        str | None,
        _field("The element's start tag, to orient a reader.", "<DDIInstance>"),
    ] = None


@dataclass
class LintFindingModel:
    """A single lint rule result."""

    rule_id: Annotated[
        str,
        _field(
            "Dotted identifier of the rule. Stable -- suppress or filter on this.",
            "ddi.maintainable.labels",
        ),
    ]
    message: Annotated[
        str, _field("What the rule found.", "Maintainable element is missing a label.")
    ]
    severity: Annotated[
        str,
        _field(
            "`error` or `warning`. Only `error` makes a document invalid, matching "
            "`ddi lint`'s default exit status.",
            "warning",
        ),
    ]
    location: Annotated[
        str | None,
        _field(
            "Prefixed path to the element that triggered the rule.",
            "/*/s:StudyUnit/d:DataCollection",
        ),
    ] = None


@dataclass
class ValidationMessageModel:
    """Schema issues and lint findings, normalized into one shape.

    ``source`` says which produced it: ``"schema"`` or ``"lint"``. Consumers
    that only want a flat list to display should read ``messages`` and ignore
    the two typed lists.
    """

    message: Annotated[
        str,
        _field(
            "The finding, from whichever check produced it.",
            "Maintainable element is missing a label.",
        ),
    ]
    severity: Annotated[str, _field("`error` or `warning`.", "warning")]
    source: Annotated[
        str, _field("Which check produced it: `schema` or `lint`.", "lint", "schema")
    ]
    xpath: Annotated[str | None, _field("Set on schema issues.", "/DDIInstance")] = None
    context: Annotated[str | None, _field("Set on schema issues.", "<DDIInstance>")] = (
        None
    )
    location: Annotated[
        str | None,
        _field(
            "Human-readable position. Schema issues render as `line N, xpath ...`; "
            "lint findings carry the element path.",
            "/*/s:StudyUnit/d:DataCollection",
            "line 2, xpath /DDIInstance",
        ),
    ] = None
    rule_id: Annotated[
        str | None, _field("Set on lint findings.", "ddi.maintainable.labels")
    ] = None


@dataclass
class ValidationResponse:
    """The result of `POST /v1/validate`."""

    valid: Annotated[
        bool,
        _field(
            "`true` when nothing at *error* severity was found. Warnings are "
            "reported but do not make a document invalid -- the same rule "
            "`ddi lint` applies to its exit status. This is the field to branch on.",
            True,
        ),
    ]
    schema_issues: Annotated[
        list[SchemaIssueModel],
        _field("XSD failures. Empty when the document validates."),
    ] = field(default_factory=list)
    lint_findings: Annotated[
        list[LintFindingModel],
        _field("Style and convention findings. Empty when `?lint=false` was passed."),
    ] = field(default_factory=list)
    messages: Annotated[
        list[ValidationMessageModel],
        _field(
            "Both lists again, flattened and normalized -- read this one to "
            "render a report."
        ),
    ] = field(default_factory=list)


@dataclass
class LintResponse:
    """The result of `POST /v1/lint` without a profile."""

    lint_findings: Annotated[
        list[LintFindingModel], _field("Every rule result, in document order.")
    ] = field(default_factory=list)


@dataclass
class ProfileResponse:
    """The result of `POST /v1/lint?profile=NAME`.

    A profile bundles schema validation with lint rules, so this carries both --
    which is why it is a different shape from :class:`LintResponse`.
    """

    schema_issues: Annotated[
        list[SchemaIssueModel],
        _field("XSD failures, because a profile validates as well as lints."),
    ] = field(default_factory=list)
    lint_findings: Annotated[
        list[LintFindingModel], _field("Results from the rules the profile selects.")
    ] = field(default_factory=list)


@dataclass
class VersionsResponse:
    """The bundled DDI schema releases."""

    default: Annotated[
        str,
        _field(
            "Used when a document declares no version and none is requested.", "3.3"
        ),
    ]
    supported: Annotated[
        list[str],
        _field("Every release accepted in `?version=`.", ["3.1", "3.2", "3.3"]),
    ]


@dataclass
class HealthResponse:
    """Liveness, and the version answering."""

    status: Annotated[
        str, _field("Always `ok`; a failing service does not answer.", "ok")
    ]
    version: Annotated[str, _field("The installed `ddi-l` version.", "0.1.0")]


@dataclass
class IndexResponse:
    """What `GET /` returns to a non-browser client."""

    service: Annotated[str, _field("Distribution name.", "ddi-l")]
    version: Annotated[str, _field("The installed `ddi-l` version.", "0.1.0")]
    endpoints: Annotated[
        dict[str, str], _field("Every route this service exposes, keyed by short name.")
    ]
    documentation: Annotated[
        str | None,
        _field(
            "Path to the interactive docs. `null` when started with `--no-openapi`.",
            "/schema",
        ),
    ] = None


@dataclass
class ErrorResponse:
    """The body of every non-2xx response.

    This is Litestar's error envelope: ``status_code`` and ``detail``.
    """

    status_code: Annotated[
        int, _field("Repeats the HTTP status, for clients that log the body only.", 400)
    ]
    detail: Annotated[
        str,
        _field(
            "What went wrong. For a 400 from a document endpoint this is the "
            "parser's or validator's own message, including position where it "
            "has one.",
            "Document root must be DDIInstance or FragmentInstance in the DDI "
            "instance namespace. (line 1, xpath /not-ddi)",
        ),
    ]
    extra: Annotated[
        list[dict[str, Any]] | None,
        _field(
            "Per-field detail, present only when a query parameter failed "
            "validation -- for example `?lint=maybe`.",
        ),
    ] = None


# --- Whole-payload examples: verbatim responses from the service -----------

_LABEL_WARNING = "Maintainable element is missing a label."
_VARIABLE_PATH = "/*/s:StudyUnit/l:LogicalProduct/l:VariableScheme/l:Variable"
_QUESTION_PATH = "/*/s:StudyUnit/d:DataCollection/d:QuestionScheme/d:QuestionItem"
_MISSING_IDENTIFICATION = (
    "Missing required identification element(s): Agency, ID, Version"
)

EXAMPLE_VALID_DOCUMENT = Example(
    summary="A valid document, with warnings",
    description=(
        "The common case for freshly authored DDI: the document satisfies the "
        "schema, so `valid` is `true`, while lint reports the items authored "
        "without a label. Pass `label=` to `add_question()` and friends and "
        "these go away. Warnings never flip `valid` to `false`."
    ),
    value={
        "valid": True,
        "schema_issues": [],
        "lint_findings": [
            {
                "rule_id": "ddi.maintainable.labels",
                "message": _LABEL_WARNING,
                "severity": "warning",
                "location": _QUESTION_PATH,
            },
            {
                "rule_id": "ddi.maintainable.labels",
                "message": _LABEL_WARNING,
                "severity": "warning",
                "location": _VARIABLE_PATH,
            },
        ],
        "messages": [
            {
                "message": _LABEL_WARNING,
                "severity": "warning",
                "source": "lint",
                "xpath": None,
                "context": None,
                "location": _QUESTION_PATH,
                "rule_id": "ddi.maintainable.labels",
            },
            {
                "message": _LABEL_WARNING,
                "severity": "warning",
                "source": "lint",
                "xpath": None,
                "context": None,
                "location": _VARIABLE_PATH,
                "rule_id": "ddi.maintainable.labels",
            },
        ],
    },
)

EXAMPLE_INVALID_DOCUMENT = Example(
    summary="A document that fails the schema",
    description=(
        "Note the status code is still 200 -- the service answered the question "
        "it was asked. `valid` is the field that reports the verdict; a non-2xx "
        "status means the request itself was unusable, not that the document was."
    ),
    value={
        "valid": False,
        "schema_issues": [
            {
                "message": _MISSING_IDENTIFICATION,
                "severity": "error",
                "xpath": "/DDIInstance",
                "line": 2,
                "column": None,
                "context": "<DDIInstance>",
            }
        ],
        "lint_findings": [],
        "messages": [
            {
                "message": _MISSING_IDENTIFICATION,
                "severity": "error",
                "source": "schema",
                "xpath": "/DDIInstance",
                "context": "<DDIInstance>",
                "location": "line 2, xpath /DDIInstance",
                "rule_id": None,
            }
        ],
    },
)

EXAMPLE_LINT = Example(
    summary="Rule findings",
    value={
        "lint_findings": [
            {
                "rule_id": "ddi.maintainable.labels",
                "message": _LABEL_WARNING,
                "severity": "warning",
                "location": _QUESTION_PATH,
            },
            {
                "rule_id": "ddi.maintainable.labels",
                "message": _LABEL_WARNING,
                "severity": "warning",
                "location": "/*/s:StudyUnit/d:DataCollection/d:QuestionScheme",
            },
        ]
    },
)

EXAMPLE_PROFILE = Example(
    summary="A named profile (?profile=...)",
    description=(
        "A profile validates as well as lints, so the response carries both lists."
    ),
    value={
        "schema_issues": [],
        "lint_findings": [
            {
                "rule_id": "ddi.maintainable.labels",
                "message": _LABEL_WARNING,
                "severity": "warning",
                "location": _QUESTION_PATH,
            }
        ],
    },
)

EXAMPLE_VERSIONS = Example(
    summary="Bundled schema releases",
    value={"default": "3.3", "supported": ["3.1", "3.2", "3.3"]},
)

EXAMPLE_HEALTH = Example(
    summary="Service is up", value={"status": "ok", "version": "0.1.0"}
)

EXAMPLE_INDEX = Example(
    summary="Service index",
    value={
        "service": "ddi-l",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "versions": "/v1/versions",
            "validate": "POST /v1/validate",
            "lint": "POST /v1/lint",
            "to_json": "POST /v1/convert/json",
            "to_jsonld": "POST /v1/convert/jsonld",
            "to_xml": "POST /v1/convert/xml",
            "roundtrip": "POST /v1/roundtrip",
        },
        "documentation": "/schema",
    },
)

EXAMPLE_CLIENT_ERROR = Example(
    summary="Not a DDI document",
    value={
        "status_code": 400,
        "detail": (
            "Document root must be DDIInstance or FragmentInstance in the DDI "
            "instance namespace. (line 1, xpath /not-ddi)"
        ),
    },
)

EXAMPLE_PAYLOAD_TOO_LARGE = Example(
    summary="Body over the configured cap",
    value={"status_code": 413, "detail": "Request Entity Too Large"},
)

EXAMPLE_TIMEOUT = Example(
    summary="Processing exceeded the timeout",
    value={"status_code": 504, "detail": "Document took longer than 60s to process."},
)


def schema_issue(payload: dict[str, Any]) -> SchemaIssueModel:
    """Build a :class:`SchemaIssueModel` from the library's dict form."""
    return SchemaIssueModel(
        message=payload.get("message", ""),
        severity=payload.get("severity", "error"),
        xpath=payload.get("xpath"),
        line=payload.get("line"),
        column=payload.get("column"),
        context=payload.get("context"),
    )


def lint_finding(payload: dict[str, Any]) -> LintFindingModel:
    """Build a :class:`LintFindingModel` from the library's dict form."""
    return LintFindingModel(
        rule_id=str(payload.get("rule_id", "")),
        message=str(payload.get("message", "")),
        severity=str(payload.get("severity", "")),
        location=payload.get("location"),
    )


def validation_message(payload: dict[str, Any]) -> ValidationMessageModel:
    """Build a :class:`ValidationMessageModel` from the library's dict form."""
    return ValidationMessageModel(
        message=payload.get("message", ""),
        severity=payload.get("severity", ""),
        source=payload.get("source", ""),
        xpath=payload.get("xpath"),
        context=payload.get("context"),
        location=payload.get("location"),
        rule_id=payload.get("rule_id"),
    )
