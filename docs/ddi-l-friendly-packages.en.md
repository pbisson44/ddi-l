---
description: >-
  Python packages that work well next to ddi-l for parsing, validating,
  transforming and publishing DDI Lifecycle content.
---

# Related Python packages

Packages that are useful next to `ddi-l` when you read, validate or transform
DDI Lifecycle (DDI-L) content. Apart from the dependencies `ddi-l` already
installs, none of them is required.

## XML parsing and validation

- **`xmlschema`**: validates documents against the bundled DDI schemas. It is a
  dependency of `ddi-l`, so it is always installed.
- **`lxml`**: a faster XML parser and serializer. Install it with
  `pip install 'ddi-l[full]'`; `ddi-l` uses it automatically when it is
  present and falls back to the standard library otherwise.

## Data processing

- **`pandas`**: turn variables, questions or code lists into tables for
  reports and checks.
- **`polars`**: a faster alternative to pandas for large documents or many
  files.
- **`pyarrow`**: write Parquet or Feather files, or move data frames between
  pandas and polars.

## Files, HTTP and command-line tools

- **`requests` or `httpx`**: download DDI instances, schemas or controlled
  vocabularies before you validate them.
- **`typer` or `click`**: build your own command-line tools on top of `ddi-l`.
- **`fsspec`**: read and write files on local disk, S3-compatible storage or
  other remote file systems with the same code.

## Testing

- **`pytest`**: the test runner this repository uses.
- **`hypothesis`**: property-based tests for validation rules or conversion
  code.
- **`ruff`**: linting and formatting.

## Dependency management

- **`uv`**: this repository uses uv and its `uv.lock` file. Run
  `uv sync --group dev` to get the same development tools as CI.

## Choosing packages

- Pin optional dependencies in a lock file, and use the same lock file in
  deployment, so a pipeline behaves the same everywhere.
- Validate at the boundaries of each pipeline step (`doc.validate()`, or
  `ddi validate` on the command line) so a malformed file is caught where it
  enters, not several steps later.
