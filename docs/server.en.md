# HTTP API

`ddi-l` ships an optional HTTP service that exposes the same validate, lint and
convert operations as the CLI. It is built on [Litestar](https://litestar.dev/).

Use it when DDI validation has to be reachable from somewhere that is not
Python (a deposit form, a Java pipeline, a CI job in another language) without
each of those reimplementing DDI handling.

!!! info "It is the same code"
    Every endpoint is a thin wrapper over `ddi_l.operations`, which is also what
    the `ddi` CLI calls, so both give the same answer for the same document.

## Install and run

The server is an optional extra, so a plain install never pays for Litestar:

```bash
pip install 'ddi-l[server]'
ddi serve
```

That binds to `127.0.0.1:8000`: this machine only. To accept connections from
elsewhere:

```bash
ddi serve --host 0.0.0.0 --port 8080
```

## Interactive documentation

Open the port in a browser and you land on **[Swagger UI](https://swagger.io/tools/swagger-ui/)
at `/schema`**: <http://localhost:8000/schema>. A browser hitting `/` is
redirected there, so there is nothing to remember.

It is generated from the code, not written by hand, and it documents both
directions of every call:

- **What to send.** Each `POST` declares its request body, and "Try it out"
  arrives prefilled with a valid DDI instance. Press Execute and you get a real
  validation response without composing a request first.
- **Query parameters.** `?version=`, `?lint=` and `?profile=` appear as fields
  you can fill in rather than as prose you have to notice.
- **What comes back.** Every response carries a captured example, including the
  failure cases: what a schema error looks like, and the `{"status_code",
  "detail"}` envelope a `400`, `413`, `503` or `504` returns.

The examples are captured responses, and the test suite checks them against a
running service.

| Path | Serves |
| ------ | -------- |
| `/schema` | Swagger UI; start here |
| `/schema/redoc` | [ReDoc](https://redocly.com/redoc), read-only reference |
| `/schema/elements`, `/schema/rapidoc` | Alternative renderings |
| `/schema/openapi.json`, `/schema/openapi.yaml` | The raw document, for client generators |
| `/schema/fr` | Swagger UI with the descriptions in French |
| `/schema/openapi.fr.json` | The raw document in French |

An API client that requests `/` without `Accept: text/html` is not redirected; it
gets a JSON index of the endpoints instead.

### The French rendering

`/schema/fr` serves the same API with its prose translated: endpoint summaries,
parameter and field descriptions, example captions. What it does **not**
translate is anything a client parses: field names, enum values and the sample
documents are byte-identical to the English spec, because they are the contract
rather than the documentation. `info.title` stays `ddi-l` for the same reason.

Swagger UI's own buttons ("Try it out", "Execute", "Parameters") remain in
English. swagger-ui has no i18n support, and neither do ReDoc, RapiDoc or
Stoplight, so a French reader gets French prose in an English-chromed page.

!!! info "Kept in step with the English"
    The test suite checks that every string in the live spec has a French
    entry, and that every French entry still matches its English source.

## Endpoints

| Method | Path | Does |
| -------- | ------ | ------ |
| `GET` | `/` | Service index: version and the available endpoints. |
| `GET` | `/health` | Liveness probe; returns the running version. |
| `GET` | `/v1/versions` | Bundled DDI schema releases and the default. |
| `POST` | `/v1/validate` | Schema validation plus lint findings. |
| `POST` | `/v1/lint` | Lint rules only. |
| `POST` | `/v1/convert/json` | DDI XML → JSON (lossless, round-trippable). |
| `POST` | `/v1/convert/jsonld` | DDI XML → JSON-LD (linked data, one-way). |
| `POST` | `/v1/convert/xml` | JSON → DDI XML. |
| `POST` | `/v1/roundtrip` | Re-serialize a document through the model layer. |

`POST` endpoints take the document as the raw request body. All accept
`?version=3.1|3.2|3.3` to pin the schema release instead of using the one the
document declares.

### Validate

```bash
curl --data-binary @my-study.xml http://localhost:8000/v1/validate
```

```json
{
  "valid": true,
  "schema_issues": [],
  "lint_findings": [ ... ],
  "messages": [ ... ]
}
```

`valid` answers the caller's actual question and reflects **errors only**:
warnings are reported but do not make a document invalid, matching what
`ddi lint` does with its exit status. Add `?lint=false` for schema validation
alone.

### Lint

```bash
curl --data-binary @my-study.xml http://localhost:8000/v1/lint
curl --data-binary @my-study.xml 'http://localhost:8000/v1/lint?profile=DDI_PROFILE_DEFAULT'
```

### Convert

```bash
curl --data-binary @my-study.xml http://localhost:8000/v1/convert/json > study.json
curl -H 'Content-Type: application/json' --data-binary @study.json \
  http://localhost:8000/v1/convert/xml > study.xml
```

### JSON-LD (linked data)

`/v1/convert/jsonld` renders the document as JSON-LD using the DDI Alliance's
own [DDI-RDF Discovery vocabulary](https://rdf-vocabulary.ddialliance.org/discovery.html)
("Disco"), served as `application/ld+json`:

```bash
curl --data-binary @my-study.xml http://localhost:8000/v1/convert/jsonld > study.jsonld
```

```json
{
  "@context": {"disco": "http://rdf-vocabulary.ddialliance.org/discovery#", "...": "..."},
  "@graph": [
    {
      "@id": "urn:ddi:example.org:8f3a...:1",
      "@type": "disco:Study",
      "dcterms:title": "Household Survey",
      "disco:variable": [{"@id": "urn:ddi:example.org:1c9d...:1"}]
    },
    {
      "@id": "urn:ddi:example.org:1c9d...:1",
      "@type": "disco:Variable",
      "skos:prefLabel": [{"@value": "Age", "@language": "en"}],
      "disco:question": [{"@id": "urn:ddi:example.org:44b1...:1"}]
    }
  ]
}
```

This is a **semantic** mapping, not a transcription of the XML. Studies,
variables, questions and universes become Disco terms with Dublin Core and SKOS
for labels, so the result loads straight into a triple store. `@id` values are
the DDI URNs the library already mints, which are valid IRIs.

!!! warning "Lossy and one-way, by design"
    Disco covers DDI's **discovery** subset: what a dataset is about, so it can
    be found and compared. It has no vocabulary for questionnaire flow logic,
    record layouts, NCubes or processing instructions, and those are dropped
    rather than approximated. Its specification is explicit that the reverse
    transformation "is not intended", so there is no JSON-LD → XML endpoint.

    Use `/v1/convert/json` when the payload has to come back as XML. That format
    is an exact transcription and round-trips through `/v1/convert/xml`.

## Running it safely

A library parses what its caller chose to open. A service parses whatever
reaches the port, so the defaults are deliberately conservative.

- **Request bodies are capped at 32 MiB.** Change it with `--max-body-mb`.
  Without a cap, one request can exhaust a worker's memory.
- **XML parsing is hardened, and the server adds no parser of its own.** It goes
  through the same code as the library, which disables entity resolution and
  network access and routes standard-library parsing through `defusedxml`.
  Entity-expansion ("billion laughs") and external-entity (XXE) payloads are
  rejected; `tests/test_server.py` asserts both over HTTP.
- **Requests are bounded at 60 seconds** by default. This caps how long a
  *client* waits, not how long the work runs: validation happens in a worker
  thread and a running Python thread cannot be cancelled, so on timeout the
  caller gets `504` while that thread finishes. The body cap is what bounds the
  work itself.
- **Concurrent work is bounded.** At most `--max-jobs` documents are processed
  at once (default: the number of CPUs); further requests get `503` with
  `Retry-After`. The default schema is loaded at startup, so the first request
  does not pay for it.
- **Nothing is written to disk.** Documents are parsed from memory.
- **CORS is off.** Enable named origins with `--cors-allow-origin`; there is
  deliberately no wildcard flag.
- **`/schema` can be turned off** with `--no-openapi` for an internet-facing
  deployment.

!!! warning "Validation is CPU-bound"
    Schema-validating a large instance occupies a worker for the duration. Run
    behind a reverse proxy that enforces its own timeouts and rate limits, and
    size the worker pool for your largest expected document, not your median
    one.

## Embedding it

`ddi serve` is a convenience. For a real deployment, build the app yourself and
run it under any ASGI server:

```python
from ddi_l.server import ServerConfig, create_app

app = create_app(
    ServerConfig(
        max_body_bytes=8 * 1024 * 1024,
        cors_allow_origins=("https://metadata.example.org",),
        enable_openapi=False,
    )
)
```

```bash
uvicorn myapp:app --workers 4
```
