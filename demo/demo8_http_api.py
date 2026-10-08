#!/usr/bin/env python
"""Demo 8: The HTTP API.

Walks every endpoint the optional ``ddi-l[server]`` extra exposes, showing the
request you would send and what comes back.

Topics covered:
- Starting the app in-process and calling it
- ``/v1/validate`` and ``/v1/lint``
- ``/v1/convert/json`` and ``/v1/convert/xml`` (lossless, round-trippable)
- ``/v1/convert/jsonld`` (linked data, one-way)
- ``/v1/roundtrip``, ``/v1/versions`` and ``/health``
- What the service rejects, and why

Why this runs without starting a server
---------------------------------------

It drives the app through Litestar's ``TestClient``, which speaks the real
request/response cycle over ASGI without binding a port -- so the demo is
deterministic, needs no cleanup, and cannot collide with something already
listening on 8000.

``TestClient`` is built on ``httpx``, so the calls below are the same ones you
would write against a running server. Swap the client for
``httpx.Client(base_url="http://localhost:8000")`` and the rest is unchanged.
Each step also prints the equivalent ``curl``.

Requires the server extra::

    pip install 'ddi-l[server]'

Without it the demo still builds and saves the study, then explains what to
install -- it does not fail.
"""

import json
import logging
import os
from pathlib import Path

import ddi_l as ddi

AGENCY = "demo.org"


def _output_dir() -> Path:
    """Return the directory demo artifacts are written to.

    Defaults to ``demo/output/`` so running a demo by hand leaves its result
    next to the script. Tests set ``DDI_DEMO_OUTPUT_DIR`` to a temporary path
    so a test run never modifies tracked files.
    """
    override = os.environ.get("DDI_DEMO_OUTPUT_DIR")
    path = Path(override) if override else Path(__file__).parent / "output"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _build_study() -> ddi.Document:
    """Create the small study every request below is made against."""
    doc = ddi.new_study(title="Household Survey", agency=AGENCY)
    demographics = doc.add_concept(name="Demographics", label="Demographics")
    adults = doc.add_universe(
        name="Canadian adults aged 18+", label="Canadian adults aged 18+"
    )
    age = doc.add_question(text="How old are you?", label="Age question")
    income = doc.add_question(
        text="What is your annual income?", label="Income question"
    )
    # Both variables point at the concept and the universe, so the JSON-LD in
    # step 7 has something to connect: an unreferenced concept renders as an
    # orphan node in the graph, present but joined to nothing.
    for variable in (
        doc.add_variable(name="Age", question=age, label="Age in years"),
        doc.add_variable(
            name="Income", question=income, label="Annual household income"
        ),
    ):
        variable.concept_references.append(demographics.to_reference())
        variable.universe_references.append(adults.to_reference())
    doc.study_unit.universe_references.append(adults.to_reference())
    return doc


def _section(title: str) -> None:
    print()
    print("-" * 60)
    print(title)
    print("-" * 60)


def main():
    print("=" * 60)
    print("Demo 8: The HTTP API")
    print("=" * 60)

    output_dir = _output_dir()

    doc = _build_study()
    study_path = output_dir / "demo8_study.xml"
    doc.save(study_path)
    xml = study_path.read_bytes()
    print(f"\nBuilt a study and saved it to {study_path.name} ({len(xml):,} bytes)")

    try:
        from litestar.testing import TestClient

        from ddi_l.server import ServerConfig, create_app
    except ImportError:
        print("\nThe HTTP API is an optional extra and is not installed.")
        print("Install it to see the rest of this demo:")
        print("\n    pip install 'ddi-l[server]'\n")
        return

    # TestClient is httpx-based, and httpx logs every request at INFO. Whatever
    # logging the surrounding process has configured, those lines land on
    # stderr interleaved mid-sentence with this demo's stdout -- output like
    # `}INFO - httpx - HTTP Request: GET ...`, which is unreadable in exactly
    # the place a demo has to be readable. The equivalent curl is printed for
    # each step anyway, so the log adds nothing here.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # The same factory `ddi serve` uses. Passing a config is optional; the
    # defaults are deliberately conservative (32 MiB body cap, CORS off).
    app = create_app(ServerConfig())

    with TestClient(app=app) as client:
        _section("1. Is the service up?  GET /health")
        print("$ curl http://localhost:8000/health")
        print(json.dumps(client.get("/health").json(), indent=2))

        _section("2. Which DDI versions?  GET /v1/versions")
        print("$ curl http://localhost:8000/v1/versions")
        print(json.dumps(client.get("/v1/versions").json(), indent=2))

        _section("3. Validate a document.  POST /v1/validate")
        print("$ curl --data-binary @study.xml \\")
        print("      http://localhost:8000/v1/validate")
        report = client.post("/v1/validate", content=xml).json()
        print(f"\n  valid          : {report['valid']}")
        print(f"  schema issues  : {len(report['schema_issues'])}")
        print(f"  lint findings  : {len(report['lint_findings'])}")
        print("\n`valid` reflects errors only. Warnings are reported but do not")
        print("make a document invalid -- the same rule `ddi lint` uses for its")
        print("exit status. Add ?lint=false for schema validation alone.")

        _section("4. Lint only.  POST /v1/lint")
        print("$ curl --data-binary @study.xml http://localhost:8000/v1/lint")
        findings = client.post("/v1/lint", content=xml).json()["lint_findings"]
        by_severity: dict[str, int] = {}
        for finding in findings:
            by_severity[finding["severity"]] = (
                by_severity.get(finding["severity"], 0) + 1
            )
        print(f"\n  {len(findings)} findings: {by_severity or 'none'}")
        for finding in findings[:3]:
            rule = finding["rule_id"]
            print(f"    [{finding['severity']}] {rule}: {finding['message']}")
        if len(findings) > 3:
            print(f"    ... and {len(findings) - 3} more")

        # A clean document shows what the endpoint returns but not what it is
        # for, so lint one with a defect too. Dropping a variable's label is
        # the everyday case: the document is still perfectly schema-valid.
        unlabelled = xml.replace(
            b'<r:Label>\n            <r:Content xml:lang="en">Age in years'
            b"</r:Content>\n          </r:Label>\n",
            b"",
        )
        if unlabelled != xml:
            print("\n  the same document with one label removed:")
            for finding in client.post("/v1/lint", content=unlabelled).json()[
                "lint_findings"
            ]:
                rule = finding["rule_id"]
                print(f"    [{finding['severity']}] {rule} at {finding['location']}")
            still = client.post("/v1/validate", content=unlabelled).json()
            print(f"    schema-valid all the same: {still['valid']}")

        _section("5. Convert to JSON.  POST /v1/convert/json")
        print("$ curl --data-binary @study.xml \\")
        print("      http://localhost:8000/v1/convert/json > study.json")
        as_json = client.post("/v1/convert/json", content=xml).json()
        json_path = output_dir / "demo8_study.json"
        json_path.write_text(json.dumps(as_json, indent=2), encoding="utf-8")
        print(f"\n  wrote {json_path.name}")
        print("  This is an exact transcription of the XML tree -- keys are")
        print("  Clark notation, and nothing is lost. It converts back.")
        print("  The @isMaintainable and @type keys you will see are the")
        print("  schema's fixed values, filled in for the JSON view; they are")
        print("  dropped again on the way back, so step 6 returns what")
        print("  step 5 was given rather than a decorated copy of it.")

        _section("6. Convert back to XML.  POST /v1/convert/xml")
        print("$ curl -H 'Content-Type: application/json' \\")
        print("      --data-binary @study.json \\")
        print("      http://localhost:8000/v1/convert/xml > roundtripped.xml")
        back = client.post("/v1/convert/xml", json=as_json)
        restored_path = output_dir / "demo8_roundtripped.xml"
        restored_path.write_bytes(back.content)
        print(f"\n  wrote {restored_path.name} ({len(back.content):,} bytes)")
        recheck = client.post("/v1/validate", content=back.content).json()
        print(f"  still valid: {recheck['valid']}")
        print(f"  identical to what went in: {back.content == xml}")

        _section("7. Convert to JSON-LD.  POST /v1/convert/jsonld")
        print("$ curl --data-binary @study.xml \\")
        print("      http://localhost:8000/v1/convert/jsonld > study.jsonld")
        response = client.post("/v1/convert/jsonld", content=xml)
        as_jsonld = response.json()
        jsonld_path = output_dir / "demo8_study.jsonld"
        jsonld_path.write_text(json.dumps(as_jsonld, indent=2), encoding="utf-8")
        print(f"\n  content-type : {response.headers['content-type']}")
        print(f"  wrote {jsonld_path.name} -- {len(as_jsonld['@graph'])} nodes")
        types: dict[str, int] = {}
        for node in as_jsonld["@graph"]:
            types[node["@type"]] = types.get(node["@type"], 0) + 1
        for rdf_type, count in sorted(types.items()):
            print(f"    {count} x {rdf_type}")
        print("\n  Unlike step 5 this is a *semantic* mapping, onto the DDI")
        print("  Alliance's DDI-RDF Discovery vocabulary. It loads straight")
        print("  into a triple store -- but it covers DDI's discovery subset")
        print("  and does not convert back. Use JSON when you need XML again.")

        _section("8. Re-serialize a document.  POST /v1/roundtrip")
        print("$ curl --data-binary @study.xml http://localhost:8000/v1/roundtrip")
        reserialized = client.post("/v1/roundtrip", content=xml).content
        print(f"\n  {len(reserialized):,} bytes back, for {len(xml):,} sent")
        print(f"  identical: {reserialized == xml}")
        print("  A smoke test for hand-edited files: if what returns differs")
        print("  from what you sent, something did not survive the parse.")
        if reserialized != xml:
            print("  ^ that is this document failing its own smoke test.")

        _section("9. What the service refuses")
        for label, path, body in [
            ("empty body", "/v1/validate", b""),
            ("not DDI", "/v1/validate", b"<not-ddi/>"),
            ("not XML at all", "/v1/validate", b"hello"),
            ("malformed JSON", "/v1/convert/xml", b"{oops"),
        ]:
            status = client.post(path, content=body).status_code
            print(f"  {label:16} -> HTTP {status}")
        print("\n  Bad input is always 4xx, never a 500. Requests are also")
        print("  capped at 32 MiB and time out after 60s by default.")

        _section("10. The API documents itself")
        schema = client.get("/schema/openapi.json").json()
        print("  Swagger UI at /schema, OpenAPI at /schema/openapi.json")
        print("  A browser opening / is redirected to the docs.")
        print()
        print(f"  {len(schema['paths'])} paths documented:")
        for route in sorted(schema["paths"]):
            print(f"    {route}")

        # The schema is generated from the handlers, so this counts what a
        # reader will actually find there rather than asserting it in prose.
        operations = [
            operation
            for item in schema["paths"].values()
            for method, operation in item.items()
            if method in {"get", "post"}
        ]
        with_body = sum(1 for op in operations if op.get("requestBody"))
        with_params = sum(1 for op in operations if op.get("parameters"))
        documented = sum(
            1
            for op in operations
            for response in op["responses"].values()
            for media in (response.get("content") or {}).values()
            if media.get("examples")
        )
        print()
        print(f"  {with_body} endpoints declare what to send, prefilled with a")
        print("    valid DDI document -- 'Try it out' works without writing one")
        print(f"  {with_params} declare their query parameters")
        print("    (?version=, ?lint=, ?profile=)")
        print(f"  {documented} responses carry a real captured example,")
        print("    errors included")

    print()
    print("=" * 60)
    print("Demo 8 complete. Against a real server, the only change is:")
    print()
    print("    import httpx")
    print("    client = httpx.Client(base_url='http://localhost:8000')")
    print()
    print("Start one with:  ddi serve --port 8000")
    print("=" * 60)


if __name__ == "__main__":
    main()
