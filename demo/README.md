# ddi-l demo suite

This folder contains demonstration scripts showcasing the capabilities of the
`ddi-l` library for working with DDI Lifecycle (DDI-L) XML documents.

## Quick Start

```bash
# Run all demos
python run_demos.py

# Run a specific demo
python run_demos.py 1

# Run multiple specific demos
python run_demos.py 1 3 5

# List available demos
python run_demos.py --list
```

Demos write their artifacts to `demo/output/`, which is not tracked in git
because each run generates fresh identifiers. Set `DDI_DEMO_OUTPUT_DIR` to
write them somewhere else.

## Available Demos

### Demo 1: Basic Document Creation (`demo1_basic_document.py`)

- Creating a study with `new_study()`
- Adding a question and a variable
- Serializing with `to_xml()` and saving with `save()`
- Reading the file back with `open_ddi()`

### Demo 2: Working with StudyUnits (`demo2_study_unit.py`)

- Adding concepts and universes
- Adding questions and variables to a study
- Reporting counts of each item type

### Demo 3: Variables and Code Lists (`demo3_variables.py`)

- The generic `add_item()` API for `Category` and `RepresentedVariable`
- Building a code list with `add_code_list()`, and filling it with `Code`s
  that each point at a `Category`
- Linking a variable to its code list with `set_coded()`
- Listing, finding and removing items (`items()`, `find()`, `remove()`)

### Demo 4: Questions and Data Collection (`demo4_questions.py`)

- Creating question items
- Wrapping each in a `QuestionConstruct` and ordering them in a `Sequence`
- Adding an `Instrument` with `add_item()`, pointed at the flow it administers

### Demo 5: Reading and Parsing (`demo5_reading.py`)

- Parsing DDI from an XML string with `read_ddi()`
- Streaming large documents with `iterparse_ddi()`
- Writing with `write_ddi()` and re-reading via `DDIDocument.from_xml()`

### Demo 6: Validation (`demo6_validation.py`)

- Schema validation with `doc.validate()`
- What a schema violation looks like, and why `doc.validate()` and
  `validate_document()` can disagree about the same document
- Model-level validation (`Variable.validate()`)
- The high-level `validate_document()` report
- Handling `DDIValidationError` and inspecting `.issues`

### Demo 7: Advanced Features (`demo7_advanced.py`)

- Building and resolving `Reference` objects
- Adding categories and code lists that reference each other
- Bilingual names and labels on a single variable
- Running the linter with `run_lint(rules=["ddi.reference.integrity"])` --
  and what it cannot tell you, since a reference that resolves says nothing
  about an object nobody references

## Output

All demos save their output to the `output/` subdirectory:

- `demo1_basic_document.xml`
- `demo2_study_unit.xml`
- `demo3_variables.xml`
- `demo4_questions.xml`
- `demo5_parsed.xml`
- `demo6_valid.xml`
- `demo7_advanced.xml`

Every one of them passes `ddi validate` and `ddi lint` with no findings at
all -- warnings included. If a change here makes one of them warn, that is a
regression, not a detail: `tests/test_demos.py` asserts it.

## Requirements

- Python 3.11+
- `ddi-l` installed (`pip install ddi-l`)
- Optional: `pip install 'ddi-l[full]'` for the faster lxml backend

Schema validation needs no extra install: `xmlschema` is a hard dependency and
the DDI XSDs are bundled, so `ddi validate` works offline.

## Common Patterns

### Creating a Document

```python
from ddi_l.document import DDIDocument

doc = DDIDocument.create(
    agency="example.org",
    identifier="my-study",
    version="1.0",
    title="My Study Title",
)
```

### Adding Maintainables

```python
from ddi_l.models.study import StudyUnit
from ddi_l.models.base import InternationalString

study = StudyUnit(
    agency="example.org",
    identifier="study-001",
    version="1.0",
    labels=[InternationalString(text="My Study", lang="en")],
)
doc.add_maintainable(study)
```

### Iterating Contents

```python
# iter_variables() walks the whole document. Note that
# doc.iter_maintainables(Variable) does *not* -- it looks only at the direct
# children of the DDIInstance root, and Variables live several levels down
# under StudyUnit/LogicalProduct/VariableScheme.
from ddi_l import iter_variables

for var in iter_variables(doc):
    print(var.identifier)
```

### Saving and Loading

```python
from ddi_l.io import write_ddi, read_ddi

# Save
write_ddi(doc, "output.xml")

# Load
doc = read_ddi("output.xml")
```

## Troubleshooting

### Import Errors

Make sure ddi-l is installed:

```bash
pip install ddi-l
# or, from a clone of this repository
uv sync --group dev
```

### Validation Errors

Validation works out of the box -- `xmlschema` is a hard dependency and the
DDI 3.1/3.2/3.3 XSDs ship inside the package. A validation failure raises
`DDIValidationError`, which carries the individual issues on `.issues`.

### Namespace Errors

Ensure you're using the correct namespace constants:

```python
from ddi_l.constants import REUSABLE_NS, LOGICAL_PRODUCT_NS
```

## Further Reading

- [DDI Alliance](https://ddialliance.org/)
- [DDI Lifecycle 3.3 Documentation](https://ddialliance.org/Specification/DDI-Lifecycle/3.3/)
- [ddi-l Package Documentation](../README.md)
