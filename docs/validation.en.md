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

## CLI validation

From the command line:

```bash
ddi validate my-study.xml              # Schema validation
ddi lint my-study.xml                  # Lint checks
ddi validate *.xml                     # Validate multiple files
```

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
