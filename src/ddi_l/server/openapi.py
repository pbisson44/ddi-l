"""Request bodies for the generated OpenAPI schema.

The handlers read ``await request.body()`` rather than a typed ``data``
parameter (see :mod:`ddi_l.server.routes`), so Litestar cannot infer their
request bodies. They are added to the generated spec here. Paths are checked
against the app's routes at startup, and the sample payloads come from
:mod:`ddi_l.server.samples`.

Also added here: the zip variant of `GET /v1/tables/template`, since a route
declares one media type per response.
"""

from __future__ import annotations

from litestar.openapi.spec import (
    OpenAPI,
    OpenAPIFormat,
    OpenAPIMediaType,
    OpenAPIType,
    RequestBody,
    Schema,
)

from ..operations import TEMPLATE_FORMATS
from .samples import (
    EXAMPLE_JSON_DOCUMENT,
    EXAMPLE_TABLES_WORKBOOK,
    EXAMPLE_TABLES_ZIP,
    EXAMPLE_TEMPLATE_ZIP,
    EXAMPLE_XML_DOCUMENT,
)

__all__ = ["document_request_bodies"]

_XML_DESCRIPTION = (
    "A DDI Lifecycle XML document, sent as the raw request body -- not "
    "multipart, not JSON-wrapped. `curl --data-binary @study.xml` is the shape."
)


def _xml_body() -> RequestBody:
    """The request body for every endpoint that takes a DDI document."""
    return RequestBody(
        required=True,
        description=_XML_DESCRIPTION,
        content={
            "application/xml": OpenAPIMediaType(
                schema=Schema(type=OpenAPIType.STRING, description=_XML_DESCRIPTION),
                examples={"document": EXAMPLE_XML_DOCUMENT},
            )
        },
    )


def _json_body() -> RequestBody:
    """The request body for the one endpoint that takes JSON instead."""
    description = (
        "A JSON document in the form `POST /v1/convert/json` produces: "
        "Clark-notation keys, `@` for attributes, `#text` for content."
    )
    return RequestBody(
        required=True,
        description=description,
        content={
            "application/json": OpenAPIMediaType(
                schema=Schema(type=OpenAPIType.OBJECT, description=description),
                examples={"document": EXAMPLE_JSON_DOCUMENT},
            )
        },
    )


_TABLES_DESCRIPTION = (
    "The metadata tables: an .xlsx workbook with one sheet per table, or a "
    ".zip of CSV files, one per table, sent as the raw request body. "
    "`curl --data-binary @my-survey.xlsx` is the shape."
)


def _binary(description: str) -> Schema:
    return Schema(
        type=OpenAPIType.STRING,
        format=OpenAPIFormat.BINARY,
        description=description,
    )


def _tables_body() -> RequestBody:
    """The request body of `POST /v1/tables/import`: a workbook or a zip."""
    return RequestBody(
        required=True,
        description=_TABLES_DESCRIPTION,
        content={
            TEMPLATE_FORMATS["xlsx"]: OpenAPIMediaType(
                schema=_binary(_TABLES_DESCRIPTION),
                examples={"workbook": EXAMPLE_TABLES_WORKBOOK},
            ),
            TEMPLATE_FORMATS["zip"]: OpenAPIMediaType(
                schema=_binary(_TABLES_DESCRIPTION),
                examples={"csv-files": EXAMPLE_TABLES_ZIP},
            ),
        },
    )


#: Which body each POST accepts. Every key is verified against the app's routes.
_BODIES = {
    "/v1/validate": _xml_body,
    "/v1/lint": _xml_body,
    "/v1/convert/json": _xml_body,
    "/v1/convert/jsonld": _xml_body,
    "/v1/roundtrip": _xml_body,
    "/v1/convert/xml": _json_body,
    "/v1/tables/import": _tables_body,
}

_TEMPLATE_PATH = "/v1/tables/template"


def document_request_bodies(schema: OpenAPI) -> OpenAPI:
    """Attach request bodies to ``schema`` in place, and return it.

    Raises:
        RuntimeError: If a documented path is missing from the schema or has
            no ``POST`` (a route was renamed or removed without updating this
            module).
    """
    paths = schema.paths or {}
    for path, build in _BODIES.items():
        path_item = paths.get(path)
        operation = getattr(path_item, "post", None)
        if operation is None:
            raise RuntimeError(
                f"{path} has no documented POST operation. "
                "ddi_l.server.openapi is out of step with ddi_l.server.routes."
            )
        operation.request_body = build()
    _document_template_formats(paths)
    return schema


def _document_template_formats(paths: dict) -> None:
    """Give `GET /v1/tables/template` its zip response next to the workbook."""
    operation = getattr(paths.get(_TEMPLATE_PATH), "get", None)
    responses = getattr(operation, "responses", None) or {}
    success = responses.get("200")
    if success is None or not success.content:
        raise RuntimeError(
            f"{_TEMPLATE_PATH} has no documented 200 response. "
            "ddi_l.server.openapi is out of step with ddi_l.server.routes."
        )
    workbook = success.content[TEMPLATE_FORMATS["xlsx"]]
    success.content[TEMPLATE_FORMATS["zip"]] = OpenAPIMediaType(
        schema=_binary("A zip of CSV files, one per table."),
        examples={"csv-files": EXAMPLE_TEMPLATE_ZIP},
    )
    workbook.schema = _binary("An .xlsx workbook, one sheet per table.")
