# Security policy

## Supported versions

Security fixes are applied to the latest released version of `ddi-l`.

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a vulnerability

Please report security issues privately rather than in a public issue.

- Use GitHub's [private vulnerability reporting](https://github.com/pbisson44/ddi-l/security/advisories/new)
  for this repository, or
- email the maintainer at <pbisson44@gmail.com>.

Include the affected version, a description of the issue, and a reproduction
case if you have one. You can expect an acknowledgement within 7 days and an
assessment within 30 days.

Please do not disclose the issue publicly until a fix is available.

## Threat model

`ddi-l` parses XML from sources the calling application may not control, so
untrusted input is an expected condition rather than an edge case.

- XML parsing goes through `defusedxml`, which rejects entity-expansion
  ("billion laughs"), external-entity (XXE), and DTD-retrieval attacks.
- Schema validation resolves only the XSDs bundled inside the package; it does
  not fetch schemas over the network at validation time.
- `ddi_l.schema_sync` is the one component that performs network I/O, and only
  when a maintainer explicitly invokes it to refresh the bundled schemas. It
  verifies downloaded archives against the checksums recorded in
  `SCHEMA_ARCHIVE_CHECKSUMS`.

Reports of parser behaviour that bypasses these protections are in scope.
Denial of service from documents that are simply very large is generally out
of scope **for the library**: the caller chooses what to open, and
`ddi_l.io.iterparse_ddi` streams when input size is unbounded.

### The HTTP API

`ddi_l.server` (the optional `server` extra) does not get that assumption: the
caller is whoever reached the port. It therefore ships limits the library has no
business setting.

- Request bodies are capped, 32 MiB by default (`--max-body-mb`).
- Documents are parsed from memory; the service writes nothing to disk.
- It adds no parser of its own. Parsing goes through `ddi_l.operations` and so
  through the hardening above; `tests/test_server.py` asserts that entity
  expansion and external-entity payloads are still refused when they arrive over
  HTTP rather than from a file.
- CORS is off unless origins are named explicitly. There is no wildcard option.

Resource exhaustion **through the HTTP API** is in scope where it defeats those
limits: a body that bypasses the cap, or a document whose validation cost is
wildly disproportionate to its size. Simply sending many large-but-legal
documents is not: schema validation is CPU-bound and a public deployment is
expected to sit behind a proxy enforcing its own timeouts and rate limits, as
`docs/server.en.md` says.

## Dependency scanning

CI runs `pip-audit --strict` against the locked dependency set on every push
and pull request.
