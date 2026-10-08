"""Request bodies for the generated OpenAPI schema.

The handlers read ``await request.body()`` rather than a typed ``data``
parameter (see :mod:`ddi_l.server.routes`), so Litestar cannot infer their
request bodies. They are added to the generated spec here. Paths are checked
against the app's routes at startup, and the sample payloads come from
:mod:`ddi_l.server.samples`.
"""

from __future__ import annotations

from litestar.openapi.spec import (
    OpenAPI,
    OpenAPIMediaType,
    OpenAPIType,
    RequestBody,
    Schema,
)

from .samples import EXAMPLE_JSON_DOCUMENT, EXAMPLE_XML_DOCUMENT

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


#: Which body each POST accepts. Every key is verified against the app's routes.
_BODIES = {
    "/v1/validate": _xml_body,
    "/v1/lint": _xml_body,
    "/v1/convert/json": _xml_body,
    "/v1/convert/jsonld": _xml_body,
    "/v1/roundtrip": _xml_body,
    "/v1/convert/xml": _json_body,
}


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
    return schema
