# Command-line Automation Playbook

This playbook chains the ``ddi`` CLI commands into repeatable automation tasks
that you can add to CI/CD pipelines. The exercises cover exit codes, logging
and keeping the output files, so that a failed run tells you what to fix.

!!! note
    The snippets assume the CLI is on your ``PATH`` (``pip install -e .``) and
    that you are running from the repository root.

!!! note "Use the packaged examples"
    The published wheel bundles the ``examples/`` directory. Resolve the
    installed path with ``importlib.resources`` (see the
    [installation guide](../installation.md)) instead
    of cloning the repository just to access sample XML payloads.

## 1. Validate and capture JSON reports

The repository provides a ready-to-use sample at
``examples/Quality_of_Life.xml``; replace it with your own file before running
the commands if needed.

1. Create the reports directory with ``mkdir -p reports`` so that redirecting
   output succeeds even when the workspace starts empty.
2. Run ``ddi validate --format json examples/Quality_of_Life.xml > reports/validation.json``.
3. Inspect the exit status: a zero status indicates success, while ``1`` means
   validation failed. The redirected output is a JSON array of issues, empty
   when the document is valid.
4. Capture the output in your CI pipeline so that successful runs record an
   empty array and
   failing runs persist the JSON payload for further analysis.

## 2. Convert XML to JSON for downstream systems

1. Create an output directory (for example ``build/artifacts``).
2. Execute ``ddi to-json examples/Quality_of_Life.xml --indent 2 > build/artifacts/quality_of_life.json``.
3. Store the generated JSON in your build artefacts so analytics systems can
   ingest structured data without parsing XML.

## 3. Round-trip conversions as a regression guard

1. Create the round-trip output directory with ``mkdir -p build/roundtrip``
   before running conversions; you only need to create it once per workspace.
2. Run ``ddi roundtrip examples/Quality_of_Life.xml build/roundtrip/Quality_of_Life.xml``
   to re-serialize the document after parsing it with the model.
3. Pass flags such as ``--validate``, ``--no-pretty-print``, or
   ``--no-declaration`` when you need schema checks or to adjust the emitted XML.
4. Diff the regenerated XML against the original to ensure the converter is
   stable. Include this diff as part of your pull request checks.

## 4. Bundle the workflow into a script

1. Create ``scripts/validate.sh`` with the following content (the ``Quality_of_Life.xml``
   sample ships with the repository; to regenerate a synthetic instance, run
   ``python -m ddi_l.examples.build_and_validate --refresh`` to create
   ``examples/example_instance.xml``):

    ```bash
    #!/usr/bin/env bash
    set -euo pipefail

    INPUT=${1:-examples/Quality_of_Life.xml}
    REPORT_DIR=${2:-reports}

    mkdir -p "$REPORT_DIR" build/artifacts build/roundtrip

    ddi validate "$INPUT" > "$REPORT_DIR"/validation.json
    ddi to-json "$INPUT" --indent 2 \
      > build/artifacts/$(basename "$INPUT" .xml).json
    ROUNDTRIP_OUTPUT="build/roundtrip/$(basename "$INPUT")"
    ddi roundtrip "$INPUT" "$ROUNDTRIP_OUTPUT"
    ```

2. Mark the script as executable (``chmod +x scripts/validate.sh``).
3. Call the script from your CI configuration and rely on the non-zero exit code
   to fail the pipeline when validation or conversion encounters an error.

## 5. Surface findings in CI dashboards

- Review and redact ``reports/validation.json`` before uploading it and
  ``build/artifacts`` as build artefacts so stakeholders can review them without
  digging into logs.
- Parse the JSON report (after confirming any sensitive content is removed) to
  comment on pull requests or annotate commits when violations occur.
- Schedule the script to run nightly against canonical instances to detect drift
  even when no code changes are in flight, but ensure the published output is
  redacted appropriately.

!!! caution
    Scrub identifiers or restrict access to the generated artefacts whenever
    they contain confidential data before sharing them on dashboards or other
    collaborative platforms.
