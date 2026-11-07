---
description: >-
  Validate DDI documents against the bundled 3.1, 3.2 and 3.3 schemas, run
  the lint rules, and read the results in Python or the CLI.
---

# Validate and lint DDI content

`ddi-l` checks documents in two ways: schema validation against the DDI
XSDs, and lint rules for problems the schema allows (missing labels, broken
references, agency rules).

!!! info "Prerequisites"
    - Python 3.11 or newer with `ddi-l` installed.
    - Access to the bundled schemas (installed automatically with the package).

## Validate on load

Pass `validate=True` when opening a document to run schema validation
immediately:

```python
import ddi_l as ddi

doc = ddi.open_ddi("my-study.xml", validate=True)
```

If the document fails validation, a `DDIValidationError` is raised.

## Validate an existing document

Call `doc.validate()` on any `Document` to check it against the DDI schema:

```python
doc = ddi.new_study(title="Test", agency="example.org")
doc.add_question(text="How old are you?")

issues = doc.validate()
if issues:
    for issue in issues:
        print(f"[{issue.severity}] {issue.message}")
else:
    print("Document is valid!")
```

### How schema validation runs

Every error is reported, with the same message and path whichever way it
runs. `schema_loader.validate(..., backend=...)` picks the way for one call;
the best available is the default:

- **`native`**, on the [native backend](installation.en.md#xml-backends): one
  pass over the document checks it against a compiled form of the schema.
  A valid document is done; xmlschema is not even loaded. For each element
  that may be wrong, xmlschema checks that element alone and words its
  errors, which also carry the line the element starts on. On a 9 MB
  export: 0.09 s when it is valid, 0.13 s with an error (2.6 s on the first
  call, which loads xmlschema).
- **`lxml`**, with lxml installed: libxml2 confirms a valid document quickly;
  if it finds a problem, xmlschema validates the whole document again to
  report it (6.5 s with one error on the same export).
- **`python`**: xmlschema validates the whole document.

## High-level validation

The `ddi_l.validation` module provides `validate_document()` for combined
schema and lint validation:

```python
from ddi_l.validation import validate_document

report = validate_document(doc)
print(f"Schema issues: {len(report.schema_issues)}")
print(f"Lint findings: {len(report.lint_findings)}")

if report.has_errors():
    print("Document has errors!")
```

## Model-level validation

Individual model objects can be validated with their `.validate()` method:

```python
from ddi_l.models.logicalproduct import Variable
from ddi_l.models.base import InternationalString

var = Variable(
    agency="example.org",
    identifier="var-1",
    version="1.0",
    labels=[InternationalString(text="Age")],
)
var.validate()  # raises ModelValidationError on failure
```

## Lint rules

The lint engine runs configurable rules against documents. Use `run_lint()`
to check referential integrity and other quality rules:

```python
from ddi_l.document import DDIDocument
from ddi_l.lint import run_lint

doc = DDIDocument.from_xml("my-study.xml")
findings = run_lint(doc, rules=["ddi.reference.integrity"])
for f in findings:
    print(f"[{f.severity}] {f.message}")
```

Without `rules=`, `run_lint()` runs the default profile, `DDI_PROFILE_DEFAULT`.
`run_profile(doc, name)` runs a named profile instead; `ddi lint
--list-profiles` lists them.

| Rule | Severity | Reports |
| --- | --- | --- |
| `ddi.agency.allowed` | error | A missing agency, or one outside the configured allow-list |
| `ddi.citation.present` | error | A `DDIInstance` without a citation |
| `ddi.citation.title.present` | error | A citation without a title |
| `ddi.citation.title.languages` | warning | A citation title missing a required language |
| `ddi.maintainable.labels` | warning | An item without an `r:Label` |
| `ddi.reference.integrity` | error (warning in a fragment) | A reference whose item is not in the file |
| `ddi.reference.version` | warning | A reference whose item is in the file, but not at the version named |
| `ddi.reference.provenance-external` | info | A `BasedOn` or user-attribute reference to an item outside the file |
| `colectica.maintainable.labels` | warning | An item with no label or name with text (`colectica-questionnaire` profile only) |

Every finding has one of three severities: `error`, `warning` or `info`.
`info` reports something worth knowing that is not a defect, and never fails
`ddi lint` unless you pass `--fail-severity info`. A rule that yields any
other severity raises `ValueError`.

A rule you add with `register_rule()` joins the default profile unless you
pass `default=False`, for a rule meant only for a named profile. The
`colectica-questionnaire` profile is for Colectica exports; see
[Work with Colectica exports](colectica.en.md#lint-an-export). The
[lint rule reference](lint-rules.en.md) lists every rule.

## CLI validation

From the command line:

```bash
ddi validate my-study.xml              # Schema validation
ddi lint my-study.xml                  # Lint checks
ddi lint export.xml --profile colectica-questionnaire
ddi lint my-study.xml --fail-severity warning   # Fail on warnings too
ddi validate *.xml                     # Validate multiple files
```

`ddi lint` exits non-zero when a finding reaches `--fail-severity`: `error`
(the default), `warning` or `info`.

The output is JSON with `message`, `xpath`, and `context` fields for each
issue found.

## Error types

| Exception | When it is raised |
| --- | --- |
| `DDIValidationError` | Schema validation fails (via `validate=True` or `validate_document()`) |
| `ModelValidationError` | A model object fails business rule checks |
| `DDIReadError` | The instance cannot be read |
| `DDIParseError` | The XML is malformed (a `DDIReadError`; carries line and column) |
| `DDIWriteError` | Serialization cannot complete |
| `DDIReferenceError` | A reference or study identifier cannot be resolved (a `LookupError`) |
| `DuplicateIdentifierError` | An item is added with an identifier already in the document (a `ValueError`) |

`Document.save()` also issues a `DDIReferenceWarning` when a reference in the
study points at an item the document does not contain. Filter it like any
warning category:

```python
import warnings

from ddi_l import DDIReferenceWarning

warnings.simplefilter("error", DDIReferenceWarning)  # fail instead of warn
```
