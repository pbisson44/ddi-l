# CLI recipes

The `ddi` console entry point bundles commands for validating and transforming
instance documents. This page collects the most common tasks as commands you
can copy and adapt.

!!! note "Bundled sample paths"
    When ``ddi-l`` is installed from a wheel, sample XML lives alongside the
    package. Export a helper variable before running the commands below so the
    paths resolve correctly on any platform:

    ```bash
    export DDI_L_FIXTURES=$(python -c "from pathlib import Path; import ddi_l; print(Path(ddi_l.__file__).resolve().parent / 'examples' / 'tests' / 'fixtures')")
    ```

    Replace ``src/ddi_l/examples/tests/fixtures/...`` in the examples with ``$DDI_L_FIXTURES/...``
    if you are not working from a cloned repository.

## Validate instances with `ddi validate`

Use the validator as a pre-flight check before committing XML changes or
shipping a new extract. The command exits with status code `0` for valid
payloads and `1` when schema or lint issues are detected.

=== "Command"
    ```bash
    ddi validate src/ddi_l/examples/tests/fixtures/minimal_instance.xml
    ```

=== "Expected output"
    ```text
    Document is valid.
    ```

Pass `-` to read from standard input when piping content from another tool.
Successful runs print exactly `Document is valid.` (no emoji or prefix), while
failing runs emit structured JSON so automated pipelines can react
programmatically.

!!! warning "Protect validation artefacts"
    Scrub personal or confidential details from the JSON output (or restrict
    distribution entirely) before sharing it outside the immediate team. Pass
    `--redact-context` to skip the contextual snippet in the CLI output, and use
    the flag alongside `--validate` for `to-json` and `roundtrip` when pipelines
    echo the diagnostic JSON. When calling the Python helpers directly,
    `validation.validate_document(..., include_context=False)` offers the same
    protection. For redaction workflows, revisit the
    [automation playbook's cautionary guidance](tutorials/automation-playbook.md#5-surface-findings-in-ci-dashboards).

=== "Failing run"
    ```bash
    cat src/ddi_l/examples/tests/fixtures/invalid_instance_missing_id.xml | ddi validate
    ```

    ```text
    error: Missing required identification element(s): ID (line 3)
        at /DDIInstance
        context: <DDIInstance>
    1 issue found.
    ```

=== "JSON issues"
    ```bash
    ddi validate --format json src/ddi_l/examples/tests/fixtures/invalid_instance_missing_id.xml
    ```

    ```json
    [
      {
        "message": "Missing required identification element(s): ID",
        "xpath": "/DDIInstance",
        "severity": "error",
        "line": 3,
        "column": null,
        "context": "<DDIInstance>"
      }
    ]
    ```

=== "Redacted JSON"
    ```bash
    ddi validate --format json --redact-context src/ddi_l/examples/tests/fixtures/invalid_instance_missing_id.xml
    ```

    ```json
    [
      {
        "message": "Missing required identification element(s): ID",
        "xpath": "/DDIInstance",
        "severity": "error",
        "line": 3,
        "column": null
      }
    ]
    ```

Continue with the [Validate and lint DDI content](validation.md) guide for a
deep dive into available lint rules, custom profiles, and advanced
configuration options.

## Tune lint checks with `ddi lint`

Run lint rules directly and customise the built-in checks without writing
Python code. Combine agency overrides, citation toggles, and language
requirements to mirror your organisation's policy.

Use `ddi lint --list-rules` or `ddi lint --list-profiles` to inspect the
available checks before running them. Pair `--list-format table` with either
flag for a compact columnar view instead of newline-delimited JSON.

=== "Command"
    ```bash
    ddi lint src/ddi_l/examples/tests/fixtures/minimal_instance.xml \
      --allowed-agency org.example --required-citation-language en \
      --no-require-citation-title --skip-rule ddi.agency.allowed
    ```

=== "What it does"
    - Turns on the agency check and restricts it to ``org.example``. The check
      is off by default: `ddi-l` has no basis to decide which organisation
      identifiers are legitimate, so it only runs once you supply the set your
      organisation accepts.
    - Enforces citation titles in English while letting the citation title rule
      be optional.
    - Ignores the agency allow-list lint finding when computing the exit code
      and in the output payload.
    - Returns exit code ``0`` unless a finding at or above the default
      ``error`` severity is emitted. Pass ``--fail-severity warning`` to fail on
      warnings too, which is what you want once a corpus is clean.

Pair the lint flags with ``--profile`` to run a custom profile or ``--validate``
to include schema issues alongside lint findings in the output JSON.

## Smoke-test edits with `ddi roundtrip`

`ddi roundtrip` re-serialises a document after parsing it with the internal
model. Use it to catch formatting problems, missing namespaces, or invalid
content introduced during manual edits.

=== "Command"
    ```bash
    ddi roundtrip src/ddi_l/examples/tests/fixtures/minimal_instance.xml --validate
    ```

=== "Expected output"
    ```xml
    <?xml version="1.0" encoding="UTF-8"?>
    <DDIInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <r:Agency>example.agency</r:Agency>
      <r:ID>minimal-instance</r:ID>
      <r:Version>1.0</r:Version>
      <r:Citation>
        <r:Title>
          <r:String xml:lang="en">Minimal Instance</r:String>
        </r:Title>
      </r:Citation>
    </DDIInstance>
    ```

Add `--no-pretty-print` or `--no-declaration` when you are diffing files that
should retain their original formatting. When you want to write to disk, pass a
destination path instead of `-`. With `--validate`, the command mirrors
`ddi validate` by returning exit code `1` and streaming JSON issues if the
source is invalid.

The [Command-line Automation Playbook](tutorials/automation-playbook.md)
shows how to integrate round-tripping with conversion and packaging steps for a
larger publishing pipeline.

## Export snapshots with `ddi to-json`

Transform XML into a normalised JSON structure for integration tests, content
mirrors, or downstream APIs. The converter reuses `DDIDocument.to_dict()` so the
shape matches the Python model.

=== "Command"
    ```bash
    ddi to-json src/ddi_l/examples/tests/fixtures/minimal_instance.xml --validate --indent 2
    ```

=== "Expected output"
    ```json
    {
      "@isMaintainable": true,
      "{ddi:reusable:3_3}Agency": "example.agency",
      "{ddi:reusable:3_3}ID": {
        "@type": "ID",
        "#text": "minimal-instance"
      },
      "{ddi:reusable:3_3}Version": "1.0",
      "{ddi:reusable:3_3}Citation": {
        "{ddi:reusable:3_3}Title": {
          "{ddi:reusable:3_3}String": {
            "@{http://www.w3.org/XML/1998/namespace}lang": "en",
            "#text": "Minimal Instance"
          }
        }
      }
    }
    ```

The converter streams only JSON to standard output so you can redirect it to a
file (`> build/artifacts/minimal.json`) or pipe it into other programs. Combine
the converter with `jq` or similar tools to extract specific sections when
preparing review packages.

## Wire the CLI into CI pipelines

Treat validation and conversion as regression tests by running them in your
continuous integration workflows. The snippet below illustrates a GitHub
Actions job that validates all XML files and keeps round-tripped output up to
date.

```yaml
name: Validate DDI payloads

on:
  push:
    paths:
      - "**/*.xml"
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install ddi-l
        run: |
          pip install . lxml
      - name: Validate XML fixtures
        run: |
          set -euo pipefail
          find src/ddi_l/examples/tests/fixtures -name "*.xml" -print0 \
            | xargs -0 -n1 -P4 ddi validate
      - name: Rebuild round-trip artefacts
        run: |
          mkdir -p build/roundtrip
          for input in src/ddi_l/examples/tests/fixtures/*.xml; do
            output="build/roundtrip/$(basename "$input")"
            ddi roundtrip "$input" --output "$output" --validate
          done
```

Augment the workflow with `ddi to-json` to publish machine-readable snapshots
alongside XML outputs or hand control to a custom script as described in the
[Command-line Automation Playbook](tutorials/automation-playbook.md).
