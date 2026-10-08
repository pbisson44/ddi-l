# Build tools and applications with ddi-l

This guide is for developers who want to use `ddi-l` as a foundation for
their own products: dashboards, web services, CLI utilities, or data
pipelines.

!!! info "Prerequisites"
    - Python 3.11+ with `ddi-l` installed.
    - Familiarity with the [user guide](../user-guide.md) and the
      [models reference](../models.md).

## Read and query documents

```python
import ddi_l as ddi

doc = ddi.open_ddi("study.xml")

# Access typed collections
for q in doc.questions:
    print(q.identifier)

for v in doc.variables:
    print(v.identifier)

# Find by identifier
item = doc.find("some-id")

# Query any registered type
from ddi_l.models.logicalproduct import Category

categories = doc.items(Category)
```

## Create documents programmatically

```python
doc = ddi.new_study(title="Generated Survey", agency="app.org")

questions = ["Age", "Gender", "Income"]
for text in questions:
    q = doc.add_question(text=f"What is your {text.lower()}?")
    doc.add_variable(name=text, question=q)

doc.save("generated-survey.xml")
```

## Integrate validation

```python
doc = ddi.open_ddi("input.xml", validate=True)

issues = doc.validate()
if issues:
    for issue in issues:
        report_to_dashboard(issue.severity, issue.message)
```

## Work with the advanced model layer

For fine-grained control, use the model classes directly:

```python
from ddi_l.document import DDIDocument
from ddi_l.models.logicalproduct import Variable

instance = DDIDocument.from_xml("study.xml")

# Access raw XML
root = instance.root

# Build an index for cross-reference resolution
index = instance.build_index()
```

## CLI integration

Wrap the `ddi` CLI in your automation:

```bash
ddi validate *.xml                     # Batch validation
ddi to-json study.xml --indent 2       # Export for web APIs
ddi roundtrip input.xml output.xml     # Normalize formatting
```

## Architecture tips

- Use `ddi.new_study()` and `ddi.open_ddi()` for most workflows. Drop to
  `DDIDocument` only when you need the raw XML tree.
- The `add_item()` / `items()` generic methods cover all 30 DDI item types,
  so you can write type-agnostic code.
- All model classes preserve unknown XML in `other_elements`, so round-trips
  are lossless even for content the library does not model.
