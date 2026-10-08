# Contributing to ddi-l

Thanks for helping improve `ddi-l`! This guide covers the development
environment, coding standards, the XSD-driven codegen pipeline, and how to
run the quality gates.

This file is the short version. The
[development guide](https://pbisson44.github.io/ddi-l/latest/DEVELOPMENT/)
([source](docs/DEVELOPMENT.en.md), [français](docs/DEVELOPMENT.fr.md)) is the
in-depth reference: architecture, the code generator, adding a DDI version, the
documentation toolchain and the release process.

## Set up your environment

**Python 3.11 or newer** is required. The project is managed with
[uv](https://docs.astral.sh/uv/); `uv.lock` pins every dependency version and
CI installs from it with `--locked`.

```bash
uv sync --group dev              # Runtime + development dependencies
uv sync --group dev --extra full # ...plus the optional lxml backend
uv sync --group docs             # Documentation toolchain
```

Note that `full` is an **extra**, not a dependency group: `--group full`
fails.

With plain pip instead:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[full]' --group dev   # pip 25.1+ reads dependency groups
```

## Coding standards

- **Formatting and linting**: `ruff format` and `ruff check` with the
  project configuration in `pyproject.toml`. Line length is 88 characters.
  `ruff` and `mypy` are pinned to exact versions; bump them deliberately.
- **Type hints**: `mypy` on `src/` and `tests/` is blocking in CI.
- **Docstrings**: Google style (`Args:`, `Returns:`, `Raises:` sections).
  Enforced by ruff's `D` rule set with `convention = "google"`.
- **Imports**: Ruff's isort integration handles ordering.
- **Tests**: `pytest` with `pytest-cov`. Tests go under `tests/`.
  Coverage target is 90%.
- **Documentation**: pages come in `.en.md` / `.fr.md` pairs. Update both
  when you change user-facing content.

## Quality gates

Run these before opening a pull request:

```bash
uv run ruff format --check .   # Formatting
uv run ruff check .            # Linting (includes docstring rules)
uv run mypy src tests          # Type checking
uv run pytest                  # Tests with coverage
uvx pip-audit --strict         # Dependency vulnerability scan
git diff --exit-code           # A test run must not modify tracked files
```

Or use the Makefile for release-level checks:

```bash
make release-check             # Build, verify assets, test install
```

`make release-check` builds both distributions, asserts the bundled XSDs and
examples are present, asserts `ddi_l` is the only top-level package in the
wheel, then installs the wheel into a clean virtualenv and validates a
document with it. Run it before proposing a release.

## XSD-driven codegen pipeline

All model classes are generated from the DDI 3.3 XSD files. The XSD is the
single source of truth for fields, ordering, namespaces, and documentation.

To regenerate models after modifying the codegen scripts:

```bash
uv run python -m codegen.generate_model_bases
```

CI runs a drift check (`git diff --exit-code src/ddi_l/models/_generated/`)
to ensure generated code stays in sync with the XSD. Never edit generated
files by hand.

Key codegen files:

- `codegen/xsd_introspect.py`: Extracts the XSD content model
- `codegen/generate_model_bases.py`: Emits generated field-only base classes
- `codegen/coverage_audit.py`: Regenerates `codegen/COVERAGE_AUDIT.md`
- `src/ddi_l/models/base.py`: Generic XML engine; `MaintainableBase.from_xml`
  and `.to_xml` drive serialization off the generated `_FIELD_XML_MAP`,
  `_ATTR_XML_MAP`, and `_ELEMENT_ORDER` tables
- `src/ddi_l/models/_generated/`: Generated output (do not edit), including
  `label_slots.py`, the schema-derived table of elements that may carry an
  `r:Label`

## Bundled schemas

The DDI XSDs live inside the package at `src/ddi_l/schemas/` so validation
works offline from a plain `pip install ddi-l`. Always resolve them through
`importlib.resources` (`resources.files("ddi_l.schemas")`), never a path
relative to the repository root, which works in a clone and breaks in an
installed wheel. The schemas are CC-BY-4.0 from the DDI Alliance; their
`license.txt` and `readme.txt` must stay in the distribution.

## Documentation

The documentation site uses MkDocs with the Material theme and bilingual
(EN/FR) support via `mkdocs-static-i18n`.

```bash
uv run mkdocs serve --strict   # Live preview on http://127.0.0.1:8000
uv run mkdocs build --strict   # Build and check for errors
# or
make docs-serve
make docs-build
```

## Submitting changes

1. Fork the repository and create a feature branch.
2. Write or update tests alongside code changes.
3. Update both the English and French documentation pages where relevant.
4. Run the quality gates listed above.
5. Commit with clear messages describing the intent of each change.
6. Open a pull request with a summary and any related issue references.

Thanks for contributing!
