"""The HTTP API.

Skipped unless the ``server`` extra is installed. The assertions mirror
``tests/test_cli.py``: malformed input is a client error, warnings do not make
a document invalid, and the library's parser hardening applies over HTTP.
"""

from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("litestar", reason="requires the 'server' extra")

from litestar.testing import TestClient

import ddi_l as ddi
from ddi_l.server import ServerConfig, create_app


@pytest.fixture
def client():
    with TestClient(app=create_app()) as test_client:
        yield test_client


@pytest.fixture
def document(tmp_path) -> bytes:
    """A small valid instance, built the way the README tells a reader to."""
    doc = ddi.new_study(title="Household Survey", agency="example.org")
    question = doc.add_question(text="How old are you?")
    doc.add_variable(name="Age", question=question)
    path = tmp_path / "study.xml"
    doc.save(path)
    return path.read_bytes()


BROWSER_ACCEPT = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}


def test_a_browser_at_the_root_lands_on_the_api_docs(client):
    """Opening the port in a browser should reach something usable.

    A browser is redirected to the interactive docs.
    """
    response = client.get("/", headers=BROWSER_ACCEPT, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == "/schema"


def test_the_docs_are_swagger_not_redoc(client):
    """Swagger UI has "Try it out"; ReDoc, which Litestar renders by default at
    the bare path, is read-only. Someone opening the docs wants to exercise the
    API against a document, so assert which UI actually lands."""
    body = client.get("/schema").text.lower()

    assert "swagger-ui" in body


def test_an_api_client_at_the_root_gets_json(client):
    """curl and httpx send `Accept: */*` and must not be redirected."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    payload = response.json()
    assert payload["service"] == "ddi-l"
    assert payload["version"] == ddi.__version__
    assert payload["documentation"] == "/schema"
    assert "POST /v1/validate" in payload["endpoints"].values()


def test_the_root_does_not_redirect_when_openapi_is_off():
    """`--no-openapi` leaves nothing to redirect to, so serve the index."""
    with TestClient(app=create_app(ServerConfig(enable_openapi=False))) as client:
        response = client.get("/", headers=BROWSER_ACCEPT, follow_redirects=False)

        assert response.status_code == 200
        # Declared in the response model, so the key is always present; it is
        # null rather than absent. A stable shape is easier for a client than a
        # key that appears and disappears with server configuration.
        assert response.json()["documentation"] is None


def test_health_reports_the_running_version(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": ddi.__version__}


def test_versions_matches_the_library(client):
    response = client.get("/v1/versions")

    assert response.status_code == 200
    assert response.json() == {
        "default": "3.3",
        "supported": ["3.1", "3.2", "3.3"],
    }


def test_validate_accepts_a_valid_document(client, document):
    response = client.post("/v1/validate", content=document)

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["schema_issues"] == []


def test_validate_reports_warnings_without_calling_the_document_invalid(
    client, document
):
    """Mirrors `ddi lint`'s default exit status: errors fail, warnings report.

    A freshly authored document raises `ddi.maintainable.labels` warnings for the
    scheme wrappers the model layer creates during serialization. Those are worth
    reporting and are not grounds for rejecting the document.
    """
    payload = client.post("/v1/validate", content=document).json()

    assert payload["valid"] is True
    assert any(message["severity"] == "warning" for message in payload["messages"]), (
        "expected the label warnings a minimal document produces"
    )


def test_validate_can_skip_lint(client, document):
    payload = client.post("/v1/validate?lint=false", content=document).json()

    assert payload["lint_findings"] == []


def test_lint_returns_findings(client, document):
    response = client.post("/v1/lint", content=document)

    assert response.status_code == 200
    assert response.json()["lint_findings"]


def test_json_round_trips_back_to_xml(client, document):
    as_json = client.post("/v1/convert/json", content=document)
    assert as_json.status_code == 200

    back = client.post("/v1/convert/xml", json=as_json.json())

    assert back.status_code == 200
    assert back.headers["content-type"].startswith("application/xml")
    assert back.content.lstrip().startswith(b"<?xml")


def test_jsonld_is_served_as_linked_data(client, document):
    """Correct media type, and a graph -- not JSON that merely resembles one."""
    response = client.post("/v1/convert/jsonld", content=document)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/ld+json")

    payload = response.json()
    assert payload["@context"]["disco"] == (
        "http://rdf-vocabulary.ddialliance.org/discovery#"
    )
    types = {node["@type"] for node in payload["@graph"]}
    assert "disco:Study" in types


def test_jsonld_has_no_reverse_endpoint(client, document):
    """Disco does not round-trip, so nothing should imply that it does."""
    schema = client.get("/schema/openapi.json").json()

    assert "/v1/convert/jsonld" in schema["paths"]
    assert "/v1/convert/jsonld/xml" not in schema["paths"]


def test_roundtrip_returns_a_parseable_document(client, document):
    response = client.post("/v1/roundtrip", content=document)

    assert response.status_code == 200
    # The response must itself validate, or the round trip lost something.
    assert client.post("/v1/validate", content=response.content).json()["valid"]


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/v1/validate", b""),
        ("/v1/validate", b"<not-ddi/>"),
        ("/v1/validate", b"this is not xml at all"),
        ("/v1/lint", b"<not-ddi/>"),
        ("/v1/convert/json", b"<not-ddi/>"),
        ("/v1/convert/xml", b"{not json"),
        ("/v1/convert/xml", b"[1, 2, 3]"),
    ],
)
def test_malformed_input_is_a_client_error(client, path, body):
    """Never a 500. Bad input is the caller's problem and must say so."""
    response = client.post(path, content=body)

    assert response.status_code == 400, response.text


def test_a_body_over_the_limit_is_rejected():
    """The cap is the difference between a service and a memory exhaustion."""
    tiny = ServerConfig(max_body_bytes=1024)
    with TestClient(app=create_app(tiny)) as client:
        response = client.post("/v1/validate", content=b"x" * 4096)

    assert response.status_code == 413


def test_a_slow_document_times_out(monkeypatch, document):
    """The configured timeout is applied to the running operation."""
    import time

    from ddi_l import operations

    monkeypatch.setattr(
        operations, "validate_source", lambda *a, **k: time.sleep(5), raising=True
    )

    impatient = ServerConfig(request_timeout_seconds=0.25)
    with TestClient(app=create_app(impatient)) as client:
        response = client.post("/v1/validate", content=document)

    assert response.status_code == 504
    assert "0.25s" in response.text


def test_entity_expansion_is_refused(client):
    """A billion-laughs payload must not be expanded.

    The server adds no parse path of its own -- it goes through
    `ddi_l.operations`, and so through the hardening in `ddi_l._etree`. This
    asserts that reaching the parser over HTTP does not bypass it.
    """
    bomb = b"""<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
]>
<DDIInstance xmlns="ddi:instance:3_3">&lol4;</DDIInstance>"""

    response = client.post("/v1/validate", content=bomb)

    assert response.status_code == 400
    assert "lollollol" not in response.text


def test_external_entities_are_not_resolved(client, tmp_path):
    """XXE: the parser must not read a local file the payload points at."""
    secret = tmp_path / "secret.txt"
    secret.write_text("TOP-SECRET-VALUE", encoding="utf-8")

    xxe = f"""<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file://{secret}">]>
<DDIInstance xmlns="ddi:instance:3_3">&xxe;</DDIInstance>""".encode()

    response = client.post("/v1/validate", content=xxe)

    assert response.status_code == 400
    assert "TOP-SECRET-VALUE" not in response.text


def test_cors_is_off_unless_configured(client, document):
    """A validation service is a natural thing to enable `*` on by reflex."""
    response = client.post(
        "/v1/validate", content=document, headers={"Origin": "https://example.com"}
    )

    assert "access-control-allow-origin" not in response.headers


def test_cors_can_be_enabled_for_named_origins(document):
    configured = ServerConfig(cors_allow_origins=("https://example.com",))
    with TestClient(app=create_app(configured)) as client:
        response = client.post(
            "/v1/validate",
            content=document,
            headers={"Origin": "https://example.com"},
        )

    assert response.headers["access-control-allow-origin"] == "https://example.com"


def test_openapi_is_served_by_default(client):
    response = client.get("/schema/openapi.json")

    assert response.status_code == 200
    assert "/v1/validate" in response.json()["paths"]


def test_openapi_can_be_disabled():
    """Useful internally, unwanted on an internet-facing deployment."""
    with TestClient(app=create_app(ServerConfig(enable_openapi=False))) as client:
        assert client.get("/schema/openapi.json").status_code == 404


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("?profile=nope", "Unknown lint profile requested: nope"),
        ("?version=9.9", "9.9"),
    ],
)
def test_a_bad_lookup_reads_as_a_sentence(client, document, query, expected):
    """`KeyError.__str__` is `repr(args[0])`, which quotes the message.

    An unknown profile reached the client as
    `"'Unknown lint profile requested: nope'"` -- quoted inside the JSON string,
    so the quotes look like part of the name being reported. Unknown profiles,
    rules and schema versions all raise `KeyError` and all arrived this way.
    """
    detail = client.post(f"/v1/lint{query}", content=document).json()["detail"]

    assert expected in detail
    assert not detail.startswith("'")


@pytest.mark.parametrize(
    ("argv", "expected", "unexpected"),
    [
        (["serve"], "http://localhost:8000/schema", "docs disabled"),
        (["serve", "--host", "0.0.0.0"], "http://localhost:", "0.0.0.0:"),
        (["serve", "--no-openapi"], "docs disabled", "/schema"),
    ],
)
def test_serve_prints_where_the_docs_are(monkeypatch, argv, expected, unexpected):
    """uvicorn logs the bind address and nothing else.

    A reader left with `http://127.0.0.1:8000` has no reason to think opening it
    reaches interactive documentation -- the first report against this service
    was someone doing exactly that and asking why it was not a Swagger page. The
    `0.0.0.0` case matters because that address is not one a browser can open;
    what the reader needs printed is `localhost`.
    """
    import contextlib
    import io

    import uvicorn

    from ddi_l.cli import main

    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: None)
    # Free the port check, which would otherwise fail on a busy CI machine.
    monkeypatch.setattr("socket.socket.bind", lambda self, address: None)

    # `redirect_stdout` rather than `capsys`: the TestClient fixtures in this
    # module leave worker threads that log through conftest's autouse handler,
    # and that handler keeps writing after capsys has closed its buffer --
    # producing a page of "I/O operation on closed file" from an unrelated test.
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        assert main(argv) == 0

    printed = buffer.getvalue()
    assert expected in printed
    assert unexpected not in printed


@pytest.mark.parametrize(
    "config_kwargs",
    [{"max_body_bytes": 0}, {"max_body_bytes": -1}, {"request_timeout_seconds": 0}],
)
def test_limits_that_would_disable_themselves_are_rejected(config_kwargs):
    with pytest.raises(ValueError):
        ServerConfig(**config_kwargs)


class _SaturatedSlots:
    def try_acquire(self):
        return False


def test_a_saturated_server_answers_503(document):
    app = create_app(ServerConfig(max_concurrent_jobs=1, preload_schema=False))
    app.state.ddi_job_slots = _SaturatedSlots()
    with TestClient(app=app) as busy:
        response = busy.post("/v1/validate", content=document)

    assert response.status_code == 503
    assert response.headers["retry-after"] == "1"


def test_a_timed_out_job_keeps_its_slot_until_its_thread_finishes(
    monkeypatch, document
):
    import threading

    from ddi_l import operations

    release = threading.Event()
    finished = threading.Event()

    def slow(*args, **kwargs):
        release.wait(10)
        finished.set()
        return []

    real_validate_source = operations.validate_source
    monkeypatch.setattr(operations, "validate_source", slow, raising=True)
    config = ServerConfig(
        max_concurrent_jobs=1, request_timeout_seconds=0.1, preload_schema=False
    )
    with TestClient(app=create_app(config)) as client:
        assert client.post("/v1/validate", content=document).status_code == 504
        assert client.post("/v1/validate", content=document).status_code == 503

        release.set()
        assert finished.wait(10)
        monkeypatch.setattr(operations, "validate_source", real_validate_source)
        for _ in range(50):
            response = client.post("/v1/validate", content=document)
            if response.status_code != 503:
                break
        assert response.status_code == 200


def test_the_default_schema_is_loaded_at_startup():
    from ddi_l import schema_loader

    schema_loader.clear_schema_cache()
    with TestClient(app=create_app(ServerConfig(preload_schema=True))):
        cache_info: Any = schema_loader.get_schema.cache_info  # type: ignore[attr-defined]
        assert cache_info().currsize == 1


def test_max_concurrent_jobs_must_be_positive():
    with pytest.raises(ValueError, match="max_concurrent_jobs"):
        ServerConfig(max_concurrent_jobs=0)
