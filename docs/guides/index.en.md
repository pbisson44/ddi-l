---
description: >-
  Task-oriented guides for ddi-l: validate and lint DDI, load metadata from
  spreadsheets, exchange files with other tools, and run ddi-l from the
  command line, over HTTP or from R.
icon: material/compass-outline
---

# How-to guides

Each guide shows how to do one task, for readers who know the basics. New to
`ddi-l`? Start with the [course](../curriculum/index.en.md); looking up a
function? See the [reference](../reference/index.en.md).

## Check your metadata

<div class="grid cards" markdown>

- :material-check-decagram-outline:{ .lg } **[Validate and lint](../validation.en.md)**

    ---

    Check documents against the DDI 3.1, 3.2 and 3.3 schemas, run the lint
    rules, and read the results in Python or on the command line.

- :material-bug-outline:{ .lg } **[Troubleshoot schema errors](../tutorials/schema-troubleshooting-clinic.en.md)**

    ---

    Read a schema error, find the element it names and fix it, starting from
    deliberately broken files.

- :material-clipboard-check-outline:{ .lg } **[Check a questionnaire against a spec](../spec-conformance.en.md)**

    ---

    Write what a questionnaire should contain as a spec, then check an
    instrument against it with `ddi conform`.

- :material-robot-outline:{ .lg } **[Automate validation in CI](../tutorials/automation-playbook.en.md)**

    ---

    Fail a pipeline on invalid DDI, keep JSON reports, and bundle the checks
    into one script.

</div>

## Bring metadata in and out

<div class="grid cards" markdown>

- :material-table-arrow-right:{ .lg } **[Load DDI from spreadsheets](../spreadsheet-import.en.md)**

    ---

    Document a study in CSV files or an Excel workbook, then load it into
    DDI in bulk.

- :material-file-download-outline:{ .lg } **[Spreadsheet templates](../spreadsheet-templates.en.md)**

    ---

    Blank and example templates, bilingual, ready to fill in.

- :material-swap-horizontal:{ .lg } **[Work with other tools](../interoperability.en.md)**

    ---

    Exchange metadata with XML tools, linked data, JSON, R, DDI-Codebook
    files and DDI 3.2 tools.

- :material-file-replace-outline:{ .lg } **[Work with Colectica exports](../colectica.en.md)**

    ---

    Read, edit and write `FragmentInstance` exports, written back byte for
    byte in their own layout.

- :material-code-tags:{ .lg } **[Move between XML and objects](../tutorials/xml-to-objects.en.md)**

    ---

    Open raw DDI XML, explore it, and work with the typed model layer.

- :material-puzzle-outline:{ .lg } **[Reuse fragments](../tutorials/fragment-reuse-lab.en.md)**

    ---

    Package reusable fragments, share them, and attach them to new
    documents.

</div>

## Run ddi-l elsewhere

<div class="grid cards" markdown>

- :material-console:{ .lg } **[Use the command line](../cli-recipes.en.md)**

    ---

    Recipes for the `ddi` command: validate, lint, convert to JSON and
    JSON-LD, and round-trip DDI XML.

- :material-web:{ .lg } **[Serve the HTTP API](../server.en.md)**

    ---

    Validate, lint and convert documents over HTTP with `ddi serve`, from
    any language.

- :material-language-r:{ .lg } **[Use ddi-l from R](../r-users.en.md)**

    ---

    Create, open, validate and lint DDI documents without leaving R.

- :material-hammer-wrench:{ .lg } **[Build tools and applications](../tutorials/building-tools.en.md)**

    ---

    Use `ddi-l` as the base of dashboards, web services, command-line tools
    and data pipelines.

</div>
