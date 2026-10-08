# ddi-l

[![PyPI version](https://img.shields.io/pypi/v/ddi-l.svg)](https://pypi.org/project/ddi-l/)
[![Python versions](https://img.shields.io/pypi/pyversions/ddi-l.svg)](https://pypi.org/project/ddi-l/)
[![Development status](https://img.shields.io/pypi/status/ddi-l.svg)](https://pypi.org/project/ddi-l/)
[![Typed](https://img.shields.io/pypi/types/ddi-l.svg)](https://peps.python.org/pep-0561/)
[![DDI Lifecycle](https://img.shields.io/badge/DDI%20Lifecycle-3.1%20%7C%203.2%20%7C%203.3-0b7285.svg)](https://ddialliance.org/Specification/DDI-Lifecycle/3.3/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/pbisson44/ddi-l/blob/main/LICENSE)

[![CI](https://img.shields.io/github/actions/workflow/status/pbisson44/ddi-l/ci.yml?branch=main&label=CI&logo=github)](https://github.com/pbisson44/ddi-l/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/github/actions/workflow/status/pbisson44/ddi-l/deploy-docs.yml?branch=main&label=docs&logo=readthedocs&logoColor=white)](https://pbisson44.github.io/ddi-l/)
[![Coverage](https://img.shields.io/badge/coverage-%E2%89%A590%25%20%28CI%20gate%29-brightgreen.svg)](https://github.com/pbisson44/ddi-l/blob/main/pyproject.toml)

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-2a6db2.svg)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pbisson44/ddi-l/blob/main/.pre-commit-config.yaml)

A Python library for creating, reading, updating, and validating
[DDI Lifecycle](https://ddialliance.org/Specification/DDI-Lifecycle/) XML
documents. It reads, validates and lints DDI 3.1, 3.2 and 3.3, and authors new
documents in DDI 3.3.

**[Documentation](https://pbisson44.github.io/ddi-l/)**: guides, a models
reference, CLI recipes and a 16-module training curriculum, in English and
French.

## Installation

```bash
pip install ddi-l     # or: uv add ddi-l
```

Optional extras:

```bash
pip install 'ddi-l[full]'     # lxml: faster parsing and validation
pip install 'ddi-l[server]'   # HTTP API (see `ddi serve` below)
```

The DDI 3.1, 3.2, and 3.3 XML Schemas are bundled with the package, so
validation works offline with no additional download.

**Using R?** Call `ddi-l` through [reticulate](https://rstudio.github.io/reticulate/);
see [Using ddi-l from R](https://pbisson44.github.io/ddi-l/latest/r-users/).

## Quick start

### Create a study

```python
import ddi_l as ddi

doc = ddi.new_study(title="Household Survey", agency="example.org")

# Add questions. `label=` is optional, but `ddi lint` reports every
# maintainable without one, so labelling here is the difference between
# output that passes the linter this package ships and output that warns
# about itself.
q_age = doc.add_question(text="How old are you?", label="Age question")
q_gender = doc.add_question(text="What is your gender?", label="Gender question")

# Add variables linked to questions
doc.add_variable(name="Age", question=q_age, label="Age in years")
doc.add_variable(name="Gender", question=q_gender, label="Gender of respondent")

# Add concepts and universes
doc.add_concept(name="Demographics", label="Demographics")
doc.add_universe(name="Canadian adults aged 18+", label="Canadian adults aged 18+")

# Save to XML
doc.save("household-survey.xml")
```

### Open and explore

```python
import ddi_l as ddi

doc = ddi.open_ddi("household-survey.xml")

print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")

for v in doc.variables:
    print(f"  {v.identifier}")
```

### Update and delete

```python
# Find an item by identifier
item = doc.find("some-identifier")

# Remove an item
doc.remove("some-identifier")

# Save changes
doc.save("household-survey.xml")
```

### Validate

```python
import ddi_l as ddi

doc = ddi.open_ddi("household-survey.xml", validate=True)

issues = doc.validate()
for issue in issues:
    print(f"[{issue.severity}] {issue.message}")
```

### Work with any DDI item type

The `add_item()` method supports all 30 registered DDI item types:

```python
from ddi_l.models.logicalproduct import Category, RepresentedVariable
from ddi_l.models.datacollection import Instrument

doc.add_item(Category, name="Male")
doc.add_item(Category, name="Female")
doc.add_item(RepresentedVariable, name="Gender Representation")
doc.add_item(Instrument, name="CAWI Questionnaire")

# Query items by type
print(f"Categories: {len(doc.items(Category))}")
```

### Command-line interface

```bash
ddi --version                                # Version and default DDI schema version
ddi validate my-study.xml                    # Schema validation
ddi lint my-study.xml                        # Lint checks (exits 1 on errors)
ddi to-json my-study.xml                     # Convert to JSON (round-trippable)
ddi to-jsonld my-study.xml                   # Convert to JSON-LD (linked data)
ddi from-json my-study.json -o my-study.xml  # Convert back from JSON
ddi roundtrip my-study.xml -o out.xml        # Round-trip XML
ddi versions                                 # List supported DDI schema versions
ddi serve                                    # HTTP API (needs the 'server' extra)
```

`ddi validate` and `ddi lint` exit non-zero when they find **errors**, which is
what makes them usable as CI gates. Warnings are reported but do not fail the
run; add `--fail-severity warning` to `ddi lint` once a corpus is clean enough
to hold that line.

### HTTP API

With `ddi-l[server]` installed, the same validate, lint and convert operations
are available over HTTP, which is useful when DDI validation has to be reachable from
outside Python:

```bash
ddi serve --port 8080
curl --data-binary @my-study.xml http://localhost:8080/v1/validate
```

`/v1/convert/jsonld` renders a study as linked data using the DDI Alliance's
own [DDI-RDF Discovery vocabulary](https://rdf-vocabulary.ddialliance.org/discovery.html),
ready to load into a triple store. It covers DDI's discovery subset and does not
convert back; use `/v1/convert/json` when the payload has to return to XML.

Open <http://localhost:8080/> in a browser and you land on **[Swagger UI](https://swagger.io/tools/swagger-ui/)
at `/schema`**: every endpoint with its request body, query parameters and
response schema, each carrying a real example. "Try it out" comes prefilled with
a valid DDI document, so you can validate one without writing a request first.
The raw OpenAPI document is at `/schema/openapi.json`.

See the [HTTP API guide](https://pbisson44.github.io/ddi-l/latest/server/) for the
endpoint reference and the limits to set before exposing it.

## What's public, and what's stable

`ddi-l` has a wide surface, so it is worth saying which part is the front door.

**Start here.** `ddi.new_study()` and `ddi.open_ddi()` return a `Document`, and
`Document` is the supported API for authoring and editing. Almost everything in
the guides uses it.

**The advanced layer** (`DDIDocument`, `DDIFragment`, `StudyCursor`, and the
generated classes under `ddi_l.models`) is public and documented, and is what
you reach for when you need raw elements, partial instances, or a specific study
in a multi-study file.

**Semantic versioning applies to** the `ddi_l` top-level exports, `ddi_l.models`,
`ddi_l.io`, `ddi_l.lint`, `ddi_l.validation`, `ddi_l.operations`, and the `ddi`
CLI's commands and exit codes.

**Provisional in 0.1.x**, and may change without a major bump:

- `ddi_l.models._generated`: regenerated from the XSDs; import the public
  re-exports in `ddi_l.models` instead.
- `ddi_l.server` and its HTTP routes: new in this release and not yet exercised
  against real deployments.
- Anything prefixed with `_`.

While `0.x`, breaking changes land in minor versions and are called out in the
[release notes](https://pbisson44.github.io/ddi-l/latest/release-notes/).

## Supported Python versions

Python 3.11, 3.12, 3.13, and 3.14.

## Contributing

See [CONTRIBUTING.md](https://github.com/pbisson44/ddi-l/blob/main/CONTRIBUTING.md) for development setup, coding standards,
and testing instructions.

## Citing ddi-l

If you use `ddi-l` in research or in an archive's workflow, please cite it.
GitHub's "Cite this repository" button exports
[CITATION.cff](https://github.com/pbisson44/ddi-l/blob/main/CITATION.cff) as
APA or BibTeX:

> Bisson, P. (2026). *ddi-l: a Python toolkit for DDI Lifecycle 3.3 XML
> documents* (Version 0.1.0) [Computer software].
> <https://github.com/pbisson44/ddi-l>

## License

The `ddi-l` source code is [MIT](https://github.com/pbisson44/ddi-l/blob/main/LICENSE) licensed.

### Bundled third-party content

This package redistributes the official DDI Lifecycle XML Schemas (versions
3.1, 3.2, and 3.3) under `ddi_l/schemas/`, so that validation works offline.

- **Schemas:** © [DDI Alliance](https://ddialliance.org/), licensed
  [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
- The full license text and the DDI Alliance release notes ship alongside the
  schemas as `license.txt` and `readme.txt`.

The MIT license above covers the `ddi-l` code only; it does not alter the
terms under which the DDI schemas are provided.
