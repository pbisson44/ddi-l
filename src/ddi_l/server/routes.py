"""HTTP handlers.

Every handler reads the request body, calls one function from
:mod:`ddi_l.operations` in a worker thread, and returns its result, so the
API and the CLI share one implementation.

The body is read with ``await request.body()`` because Litestar decodes a typed
``data`` parameter as JSON, and a DDI document is XML;
:mod:`ddi_l.server.openapi` documents the request bodies instead. Query
parameters are declared in the signatures so they appear in Swagger.
"""

from __future__ import annotations

import threading
from functools import partial
from typing import Annotated, Any

import anyio
import anyio.to_thread
import orjson
from litestar import Request, Response, get, post
from litestar.exceptions import ClientException, HTTPException
from litestar.openapi.datastructures import ResponseSpec
from litestar.openapi.spec import Example
from litestar.params import QueryParameter
from litestar.response import Redirect
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
)

from .. import __version__, operations
from ..exceptions import DDIError
from ..lint import ProfileResult
from .samples import (
    EXAMPLE_JSON_DOCUMENT,
    EXAMPLE_JSONLD_GRAPH,
    EXAMPLE_XML_DOCUMENT,
)
from .schemas import (
    EXAMPLE_CLIENT_ERROR,
    EXAMPLE_HEALTH,
    EXAMPLE_INDEX,
    EXAMPLE_INVALID_DOCUMENT,
    EXAMPLE_LINT,
    EXAMPLE_PAYLOAD_TOO_LARGE,
    EXAMPLE_PROFILE,
    EXAMPLE_TIMEOUT,
    EXAMPLE_VALID_DOCUMENT,
    EXAMPLE_VERSIONS,
    ErrorResponse,
    HealthResponse,
    IndexResponse,
    LintResponse,
    ProfileResponse,
    ValidationResponse,
    VersionsResponse,
    lint_finding,
    schema_issue,
    validation_message,
)


def _spec(
    container: Any,
    description: str,
    *examples: Example,
    media_type: str = "application/json",
) -> ResponseSpec:
    """A documented response.

    ``generate_examples=False`` stops Litestar inventing sample values; every
    example here is a captured response.
    """
    return ResponseSpec(
        data_container=container,
        description=description,
        media_type=media_type,
        examples=list(examples),
        generate_examples=False,
    )


# Error responses documented on every endpoint that parses a document, using
# Litestar's real envelope (`status_code`, `detail`). `data_container` must be
# `ErrorResponse`, not `None`, or Litestar drops the examples.
_ERROR_RESPONSES: dict[int, ResponseSpec] = {
    400: _spec(
        ErrorResponse,
        "The body was empty, not XML, or not a DDI document.",
        EXAMPLE_CLIENT_ERROR,
    ),
    413: _spec(
        ErrorResponse,
        "Body exceeded the configured limit (32 MiB by default).",
        EXAMPLE_PAYLOAD_TOO_LARGE,
    ),
    504: _spec(
        ErrorResponse,
        "Processing exceeded the configured request timeout.",
        EXAMPLE_TIMEOUT,
    ),
}


def _responses(success: ResponseSpec) -> dict[int, ResponseSpec]:
    """Combine a documented 200 with the shared error responses.

    Litestar builds the success response from the return annotation and then
    lets an entry in ``responses`` replace it, which is the only way to attach
    a whole-payload example to a 200. The schema is unchanged (the same
    dataclass goes in ``data_container``), so this documents the response, it
    does not redefine it.
    """
    return {HTTP_200_OK: success, **_ERROR_RESPONSES}


# Malformed input is a client error, not a server fault, and must not surface as
# a 500. `ValueError` covers `wrap_element` rejecting a non-DDI root and orjson's
# parse failures; `LookupError` covers an unknown schema version or lint profile.
_BAD_REQUEST_ERRORS = (DDIError, ValueError, LookupError)

VersionParam = Annotated[
    str | None,
    QueryParameter(
        name="version",
        required=False,
        description=(
            "DDI Lifecycle release to work against. Omit to use the version the "
            "document declares. See `GET /v1/versions` for what is bundled."
        ),
        examples=[Example(value="3.3"), Example(value="3.2")],
    ),
]


def _clean(version: str | None) -> str | None:
    """Treat `?version=` with no value as absent rather than as an empty version."""
    return version or None


async def _body_bytes(request: Request) -> bytes:
    """Return the raw request body, rejecting an empty one."""
    data = await request.body()
    if not data:
        raise ClientException(detail="Request body is empty.")
    return data


def _detail(error: Exception) -> str:
    """Return an error's message without ``KeyError``'s added quotes.

    ``KeyError.__str__`` is ``repr(args[0])``, which would quote the message.
    """
    if isinstance(error, KeyError) and error.args:
        return str(error.args[0])
    return str(error)


class _JobSlots:
    """Count running jobs, including ones whose request has timed out.

    A worker thread cannot be cancelled, so its slot is released by the thread
    itself when it finishes, not when the awaiting request gives up.
    """

    def __init__(self, capacity: int) -> None:
        self._free = threading.BoundedSemaphore(capacity)

    def try_acquire(self) -> bool:
        return self._free.acquire(blocking=False)

    def release(self) -> None:
        self._free.release()


class _Job:
    """Run ``call`` in a worker thread and free its slot exactly once."""

    def __init__(self, slots: _JobSlots, call: Any) -> None:
        self._slots = slots
        self._call = call
        self._lock = threading.Lock()
        self._state = "pending"  # -> "running" in the thread, or "abandoned"

    def __call__(self) -> Any:
        with self._lock:
            if self._state == "abandoned":
                return None
            self._state = "running"
        try:
            return self._call()
        finally:
            self._slots.release()

    def abandon(self) -> None:
        """Free the slot if the thread has not started; it then never runs."""
        with self._lock:
            if self._state == "pending":
                self._state = "abandoned"
                self._slots.release()


async def _run(request: Request, operation, /, *args, **kwargs):
    """Run a blocking operation in a worker thread, under the configured timeout.

    Failures from malformed input become 400; exceeding the timeout becomes 504.
    At most ``max_concurrent_jobs`` operations run at once, counting those whose
    request has timed out but whose thread is still working; requests beyond
    that get 503.
    """
    config = request.app.state.ddi_config
    timeout = config.request_timeout_seconds
    slots = request.app.state.get("ddi_job_slots")
    if slots is None:
        slots = _JobSlots(config.max_concurrent_jobs)
        request.app.state.ddi_job_slots = slots
    if not slots.try_acquire():
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server is busy processing other documents; retry shortly.",
            headers={"Retry-After": "1"},
        )
    job = _Job(slots, partial(operation, *args, **kwargs))
    try:
        with anyio.fail_after(timeout):
            return await anyio.to_thread.run_sync(
                job,
                abandon_on_cancel=True,
                limiter=anyio.CapacityLimiter(1),
            )
    except TimeoutError as error:
        raise HTTPException(
            status_code=HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Document took longer than {timeout:g}s to process.",
        ) from error
    except _BAD_REQUEST_ERRORS as error:
        raise ClientException(detail=_detail(error)) from error
    finally:
        job.abandon()


@get(
    "/",
    summary="Service index",
    sync_to_thread=False,
    responses={
        HTTP_200_OK: _spec(IndexResponse, "The available endpoints.", EXAMPLE_INDEX)
    },
)
def index(request: Request) -> Response[IndexResponse] | Redirect:
    """Send a browser to the API docs; give everything else a JSON index.

    Browsers (``Accept: text/html``) are redirected to `/schema`; other
    clients get the JSON index. No redirect when OpenAPI is disabled.
    """
    accepts_html = "text/html" in request.headers.get("accept", "")
    if accepts_html and request.app.openapi_config is not None:
        return Redirect(path="/schema")

    payload = IndexResponse(
        service="ddi-l",
        version=__version__,
        endpoints={
            "health": "/health",
            "versions": "/v1/versions",
            "validate": "POST /v1/validate",
            "lint": "POST /v1/lint",
            "to_json": "POST /v1/convert/json",
            "to_jsonld": "POST /v1/convert/jsonld",
            "to_xml": "POST /v1/convert/xml",
            "roundtrip": "POST /v1/roundtrip",
        },
    )
    if request.app.openapi_config is not None:
        payload.documentation = "/schema"
    return Response(content=payload)


@get(
    "/health",
    summary="Liveness probe",
    sync_to_thread=False,
    responses={
        HTTP_200_OK: _spec(HealthResponse, "The service is up.", EXAMPLE_HEALTH)
    },
)
def health() -> HealthResponse:
    """Report that the service is up and which version is serving."""
    return HealthResponse(status="ok", version=__version__)


@get(
    "/v1/versions",
    summary="Supported DDI schema versions",
    sync_to_thread=False,
    responses={
        HTTP_200_OK: _spec(
            VersionsResponse, "The bundled DDI Lifecycle releases.", EXAMPLE_VERSIONS
        )
    },
)
def versions() -> VersionsResponse:
    """List the bundled DDI Lifecycle releases and the default."""
    payload = operations.supported_versions()
    return VersionsResponse(default=payload["default"], supported=payload["supported"])


@post(
    "/v1/validate",
    summary="Validate a DDI document",
    status_code=HTTP_200_OK,
    responses=_responses(
        _spec(
            ValidationResponse,
            "The verdict. Note that an *invalid document* is still a 200 -- "
            "read `valid`, not the status code.",
            EXAMPLE_VALID_DOCUMENT,
            EXAMPLE_INVALID_DOCUMENT,
        )
    ),
)
async def validate(
    request: Request,
    version: VersionParam = None,
    lint: Annotated[
        bool,
        QueryParameter(
            name="lint",
            required=False,
            description=(
                "Run lint rules alongside schema validation. Pass `false` to skip them."
            ),
        ),
    ] = True,
) -> ValidationResponse:
    """Validate an XML document against the DDI schema, with lint findings.

    Warnings are reported but do not make a document invalid, matching what
    `ddi lint` uses for its exit status.
    """
    data = await _body_bytes(request)
    report = await _run(
        request,
        operations.validate_source,
        data,
        version=_clean(version),
        lint=lint,
    )
    payload = report.to_dict()
    return ValidationResponse(
        # The caller's actual question.
        valid=not report.has_errors(),
        schema_issues=[schema_issue(i) for i in payload["schema_issues"]],
        lint_findings=[lint_finding(f) for f in payload["lint_findings"]],
        messages=[validation_message(m) for m in payload["messages"]],
    )


@post(
    "/v1/lint",
    summary="Lint a DDI document",
    status_code=HTTP_200_OK,
    responses=_responses(
        _spec(
            LintResponse,
            "Rule findings. With `?profile=` the response instead carries "
            "`schema_issues` and `lint_findings`, since a profile validates as "
            "well as lints -- see the second example.",
            EXAMPLE_LINT,
            EXAMPLE_PROFILE,
        )
    ),
)
async def lint(
    request: Request,
    version: VersionParam = None,
    profile: Annotated[
        str | None,
        QueryParameter(
            name="profile",
            required=False,
            description=(
                "Run a named lint profile instead of the default rule set. "
                "A profile validates as well as lints, changing the response shape."
            ),
        ),
    ] = None,
) -> LintResponse | ProfileResponse:
    """Run lint rules over a document. ``?profile=NAME`` runs a named profile."""
    data = await _body_bytes(request)
    result = await _run(
        request,
        operations.lint_source,
        data,
        version=_clean(version),
        profile=_clean(profile),
    )
    if isinstance(result, ProfileResult):
        # A profile bundles schema validation with the rules, so it answers with
        # both lists -- a different shape from the bare rule run below.
        profile_payload = result.as_dict()
        return ProfileResponse(
            schema_issues=[schema_issue(i) for i in profile_payload["schema_issues"]],
            lint_findings=[lint_finding(f) for f in profile_payload["lint_findings"]],
        )
    return LintResponse(
        lint_findings=[lint_finding(finding.as_dict()) for finding in result]
    )


@post(
    "/v1/convert/json",
    summary="Convert DDI XML to JSON",
    status_code=HTTP_200_OK,
    responses=_responses(
        _spec(
            dict[str, Any],
            "A lossless transcription of the XML. Keys are Clark-notation tag "
            "names (`{namespace}Local`); `@`-prefixed keys are attributes and "
            "`#text` is element content. Round-trips through `POST /v1/convert/xml`.",
            EXAMPLE_JSON_DOCUMENT,
        )
    ),
)
async def to_json(request: Request, version: VersionParam = None) -> dict[str, Any]:
    """Convert an XML document into its JSON representation."""
    data = await _body_bytes(request)
    return await _run(
        request, operations.to_json_payload, data, version=_clean(version)
    )


@post(
    "/v1/convert/jsonld",
    summary="Convert DDI XML to JSON-LD (Disco)",
    status_code=HTTP_200_OK,
    media_type="application/ld+json",
    responses=_responses(
        _spec(
            dict[str, Any],
            "A Disco graph: `@context` binds the vocabulary prefixes and "
            "`@graph` is a flat list of nodes keyed by DDI URN, ready to load "
            "into a triple store.",
            EXAMPLE_JSONLD_GRAPH,
            media_type="application/ld+json",
        )
    ),
)
async def to_jsonld(request: Request, version: VersionParam = None) -> Response[bytes]:
    """Convert a document to JSON-LD using the DDI-RDF Discovery vocabulary.

    A semantic rendering, not a transcription of the XML: studies, variables,
    questions and universes become Disco terms, so the result is linked data
    that can be loaded into a triple store.

    Deliberately lossy and one-way. Disco covers a discovery subset of DDI-L and
    its specification states the reverse transformation is not intended, so
    there is no `/v1/convert/xml` counterpart for this format. Use
    `/v1/convert/json` when the payload has to come back.
    """
    data = await _body_bytes(request)
    payload = await _run(
        request, operations.to_jsonld_payload, data, version=_clean(version)
    )
    # Served as application/ld+json, the registered media type. Litestar would
    # otherwise label it application/json, which is true but tells a linked-data
    # client nothing.
    return Response(
        content=orjson.dumps(payload),
        media_type="application/ld+json",
    )


@post(
    "/v1/convert/xml",
    summary="Convert JSON back to DDI XML",
    status_code=HTTP_200_OK,
    media_type="application/xml",
    responses=_responses(
        _spec(
            str,
            "The reconstructed document.",
            EXAMPLE_XML_DOCUMENT,
            media_type="application/xml",
        )
    ),
)
async def to_xml(request: Request, version: VersionParam = None) -> Response[bytes]:
    """Convert a JSON representation back into DDI XML.

    Takes what `POST /v1/convert/json` produced. This is the only conversion
    that reads JSON rather than XML, so it is the only one whose 400 means
    *malformed JSON* rather than *malformed XML*.
    """
    body = await _body_bytes(request)
    try:
        payload = orjson.loads(body)
    except orjson.JSONDecodeError as error:
        raise ClientException(detail=f"Body is not valid JSON: {error}") from error
    if not isinstance(payload, dict):
        raise ClientException(detail="Body must be a JSON object.")

    xml = await _run(
        request, operations.from_json_payload, payload, version=_clean(version)
    )
    return Response(content=xml, media_type="application/xml")


@post(
    "/v1/roundtrip",
    summary="Re-serialize a DDI document",
    status_code=HTTP_200_OK,
    media_type="application/xml",
    responses=_responses(
        _spec(
            str,
            "The document as this library re-serializes it. Diff it against "
            "what you sent -- anything that changed did not survive a parse.",
            EXAMPLE_XML_DOCUMENT,
            media_type="application/xml",
        )
    ),
)
async def roundtrip(request: Request, version: VersionParam = None) -> Response[bytes]:
    """Parse a document with the model layer and serialize it again.

    A smoke test for formatting, namespace and encoding problems introduced by
    hand-editing: if the response differs from what was sent, something in the
    document did not survive a parse.
    """
    data = await _body_bytes(request)
    xml = await _run(
        request, operations.roundtrip_source, data, version=_clean(version)
    )
    return Response(content=xml, media_type="application/xml")


ROUTE_HANDLERS = [
    index,
    health,
    versions,
    validate,
    lint,
    to_json,
    to_jsonld,
    to_xml,
    roundtrip,
]
