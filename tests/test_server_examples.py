"""The OpenAPI examples must be what the service actually returns.

Every test posts to a real application: the documented request body must be
accepted, and the documented response must be the response it gives.
"""

from __future__ import annotations

import pytest

pytest.importorskip("litestar", reason="requires the 'server' extra")
# ...and the 'full' extra: the documented examples are lxml output (with
# `line` populated from `sourceline`), so whole payloads only match there.
pytest.importorskip("lxml", reason="the documented examples are lxml-backend output")

from litestar.testing import TestClient

import ddi_l as ddi
from ddi_l.server import create_app
from ddi_l.server.openapi import _BODIES
from ddi_l.server.samples import SAMPLE_JSON, SAMPLE_JSONLD, SAMPLE_XML
from ddi_l.server.schemas import (
    EXAMPLE_CLIENT_ERROR,
    EXAMPLE_HEALTH,
    EXAMPLE_INDEX,
    EXAMPLE_INVALID_DOCUMENT,
    EXAMPLE_VALID_DOCUMENT,
    EXAMPLE_VERSIONS,
)


@pytest.fixture
def client():
    with TestClient(app=create_app()) as test_client:
        yield test_client


@pytest.fixture
def schema(client) -> dict:
    return client.get("/schema/openapi.json").json()


# --- The documented request body ------------------------------------------


def test_the_sample_document_is_valid_and_lint_clean(client):
    """Swagger prefills "Try it out" with this. Execute must succeed.

    The first thing anyone does with an API's docs is press the button. If the
    prefilled document came back invalid, every reader's first impression would
    be of a service reporting errors on its own example.
    """
    payload = client.post("/v1/validate", content=SAMPLE_XML.encode()).json()

    assert payload["valid"] is True
    assert payload["schema_issues"] == []
    assert payload["lint_findings"] == []


def test_the_sample_json_is_what_the_service_produces(client):
    """`SAMPLE_JSON` is documented as the JSON form of `SAMPLE_XML`."""
    assert (
        client.post("/v1/convert/json", content=SAMPLE_XML.encode()).json()
        == SAMPLE_JSON
    )


def test_the_sample_json_converts_back_to_xml(client):
    """It is documented as the body for `POST /v1/convert/xml`, so it must work there."""
    response = client.post("/v1/convert/xml", json=SAMPLE_JSON)

    assert response.status_code == 200
    assert client.post("/v1/validate", content=response.content).json()["valid"] is True


def test_the_sample_jsonld_is_what_the_service_produces(client):
    """`SAMPLE_JSONLD` is documented as the Disco graph for `SAMPLE_XML`.

    This is the assertion that would have caught `dcterms:title` reporting the
    abstract: the documented graph says "Household Survey", and the service has
    to agree.
    """
    assert (
        client.post("/v1/convert/jsonld", content=SAMPLE_XML.encode()).json()
        == SAMPLE_JSONLD
    )


def test_every_documented_request_body_names_a_real_endpoint(schema):
    """`ddi_l.server.openapi` writes bodies onto paths by string.

    `create_app` already raises when a path is missing, so this covers the other
    direction: an endpoint that takes a body and never got one documented.
    """
    documented = set(_BODIES)
    takes_a_body = {path for path, item in schema["paths"].items() if "post" in item}

    assert documented == takes_a_body


@pytest.mark.parametrize("path", sorted(_BODIES))
def test_each_post_documents_what_to_send(schema, path):
    """Without this the Swagger page has an Execute button and no input box."""
    body = schema["paths"][path]["post"]["requestBody"]
    media_type, media = next(iter(body["content"].items()))

    assert body["required"] is True
    assert media_type in {"application/xml", "application/json"}
    assert media["examples"], f"{path} documents no sample payload"


# --- The documented responses ---------------------------------------------


def test_the_valid_document_example_matches_a_real_response(client, tmp_path):
    """The example is captioned as what a freshly authored document returns.

    Built the way the README teaches, so it is the response most readers will
    see first. Findings are compared as a set of (rule, location) pairs: the
    example shows two of the six to stay readable, and the contract that matters
    is that each one it shows is real.
    """
    doc = ddi.new_study(title="Household Survey", agency="example.org")
    question = doc.add_question(text="How old are you?")
    doc.add_variable(name="Age", question=question)
    path = tmp_path / "study.xml"
    doc.save(path)

    actual = client.post("/v1/validate", content=path.read_bytes()).json()
    documented = EXAMPLE_VALID_DOCUMENT.value
    assert isinstance(documented, dict)

    assert actual.keys() == documented.keys()
    assert actual["valid"] == documented["valid"] is True
    assert actual["schema_issues"] == documented["schema_issues"] == []

    def findings(payload):
        return {
            (f["rule_id"], f["location"], f["severity"])
            for f in payload["lint_findings"]
        }

    assert findings(documented) <= findings(actual)
    assert all(
        message.keys() == actual["messages"][0].keys()
        for message in documented["messages"]
    )


def test_the_invalid_document_example_matches_a_real_response(client):
    """A document that is structurally DDI but fails the schema."""
    incomplete = b"""<?xml version="1.0" encoding="utf-8"?>
<DDIInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3" xmlns:s="ddi:studyunit:3_3">
  <r:Citation><r:Title>Household Survey</r:Title></r:Citation>
  <s:StudyUnit/>
</DDIInstance>"""

    response = client.post("/v1/validate?lint=false", content=incomplete)

    # The example's caption makes a point of this, so assert it rather than
    # leaving a reader to discover that an invalid document is still a 200.
    assert response.status_code == 200
    assert response.json() == EXAMPLE_INVALID_DOCUMENT.value


@pytest.mark.parametrize(
    ("path", "example"),
    [
        ("/health", EXAMPLE_HEALTH),
        ("/v1/versions", EXAMPLE_VERSIONS),
        ("/", EXAMPLE_INDEX),
    ],
)
def test_the_simple_examples_are_exact(client, path, example):
    """These payloads are small enough to document verbatim, so they must match.

    Only the version is substituted -- pinning the current version into an
    example would mean editing three files at every release.
    """
    expected = dict(example.value)
    if "version" in expected:
        expected["version"] = ddi.__version__

    assert client.get(path).json() == expected


def test_the_error_example_matches_a_real_error(client):
    """Clients unpack `detail`; the example has to show the real envelope."""
    payload = client.post("/v1/validate", content=b"<not-ddi/>").json()

    assert payload.keys() == {"status_code", "detail"}
    assert payload == EXAMPLE_CLIENT_ERROR.value


def test_query_parameters_are_documented_not_just_described(schema):
    """`?version=` and `?lint=` were prose in a docstring, invisible to Swagger."""
    validate = {
        p["name"] for p in schema["paths"]["/v1/validate"]["post"]["parameters"]
    }
    lint = {p["name"] for p in schema["paths"]["/v1/lint"]["post"]["parameters"]}

    assert validate == {"version", "lint"}
    assert lint == {"version", "profile"}


def test_every_response_the_schema_declares_carries_an_example(schema):
    """The whole point of the exercise: no bare `object` anywhere."""
    missing = []
    for path, item in schema["paths"].items():
        for method, operation in item.items():
            if method not in {"get", "post"}:
                continue
            for status, response in operation["responses"].items():
                content = response.get("content")
                if not content:
                    continue
                for media in content.values():
                    if not media.get("examples"):
                        missing.append(f"{method.upper()} {path} -> {status}")

    assert not missing, f"undocumented response payloads: {missing}"
