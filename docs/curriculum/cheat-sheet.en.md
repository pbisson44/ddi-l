# Cheat Sheet

This page is a quick reference for the `ddi-l` package. Keep it open
while you work through the modules or build your own projects.

---

## The basics in 30 seconds

```python
import ddi_l as ddi

doc = ddi.new_study(title="My Survey", agency="example.org")
q = doc.add_question(text="How old are you?", label="Age question")
v = doc.add_variable(name="Age", question=q, label="Age in years")
doc.save("my-survey.xml")
```

That is enough to create a valid DDI document. Everything below adds
detail.

`label=` is optional and worth the few characters: `ddi lint` reports every
maintainable without one, so a document written without labels arrives warning
about itself. Pass `label_lang=` when the label is in a different language from
the name.

---

## Create, open, and save

| What you want to do | Code |
| ---------------------- | ------ |
| Create a new study | `doc = ddi.new_study(title="...", agency="...")` |
| Open an existing file | `doc = ddi.open_ddi("file.xml")` |
| Open with validation | `doc = ddi.open_ddi("file.xml", validate=True)` |
| Save to disk | `doc.save("file.xml")` |
| Validate before saving | `errors = doc.validate()` |

---

## Add items to a study

```python
# Questions
q = doc.add_question(text="What is your income?")

# Variables (linked to a question)
v = doc.add_variable(name="Income", question=q)

# Concepts
c = doc.add_concept(name="Economic Status")

# Universes
u = doc.add_universe(name="Adults aged 18+")

# Variables with concept and universe
v = doc.add_variable(name="Income", question=q, concept=c)

# Code lists
cl = doc.add_code_list(name="Gender Codes")
```

---

## Variable types (representations)

Say what kind of values a variable holds. Each setter returns the variable,
so you can chain it onto `add_variable`:

```python
doc.add_variable(name="age").set_numeric("Integer", low=0, high=120)
doc.add_variable(name="sex").set_coded(cl)  # values from a code list
doc.add_variable(name="comment").set_text()  # free text
doc.add_variable(name="dob").set_datetime("Date")
```

---

## Count and list items

```python
print(len(doc.questions))  # Number of questions
print(len(doc.variables))  # Number of variables
print(len(doc.concepts))  # Number of concepts
print(len(doc.universes))  # Number of universes
print(len(doc.code_lists))  # Number of code lists

for q in doc.questions:
    print(q.identifier)
```

---

## Find, remove, and add any type

```python
# Find an item by identifier
item = doc.find("my-identifier")

# Remove an item by identifier
doc.remove("my-identifier")

# Add any DDI type (Category, Instrument, etc.)
from ddi_l.models.logicalproduct import Category

cat = doc.add_item(Category, name="Male")

# List all items of a type
for cat in doc.items(Category):
    print(cat.identifier)
```

---

## Custom properties

```python
# Set a property
q.set_property("sensitivity", "high")

# Read a property
print(q.get_property("sensitivity"))  # "high"

# List all properties
print(q.properties)  # {"sensitivity": "high"}

# Remove a property
q.remove_property("sensitivity")
```

---

## Custom fields (extend the standard)

DDI is open: add organization-specific fields through the standard's own
extension points, and they stay inside valid DDI and round-trip on save.

```python
from ddi_l.models.base import UserID

# Namespace your keys so they never collide with another org's
v.set_property("myorg:retention_policy", "destroy after 7 years")
v.set_property("myorg:source_system", "CRM-2024")

# Back a custom field with a controlled vocabulary (references the code list URN)
quality = doc.add_code_list(name="Quality Flag Codes")  # a code list = the vocabulary
v.set_property("myorg:quality_flag", "validated")  # a value from the vocabulary
v.set_property("myorg:quality_flag_codes", quality)  # references the code list

# An organization-specific external identifier (value + type)
v.user_ids.append(UserID(value="CAT-000734", type_of_user_id="InternalCatalogue"))

# Audit which items carry your custom fields
tagged = [x for x in doc.variables if any(k.startswith("myorg:") for k in x.properties)]
```

Custom fields serialize to `r:UserAttributePair` (and `r:UserID`), which is still valid
DDI. See [Module 12](module-12-custom-fields.md).

---

## Versioning

```python
item = doc.add_variable(name="age")  # or any DDI item

# Read the current version
print(item.version)  # "1": newly created items start at "1"

# Set a three-part version if you want major/minor/patch semantics
item.version = "1.0.0"

# Bump the version
item.increment_major_version()  # 1.0.0 → 2.0.0
item.increment_minor_version()  # 1.0.0 → 1.1.0
item.increment_subversion()  # 1.0.0 → 1.0.1

# Record why you changed something
from ddi_l.models.base import VersionRationale, InternationalString

item.version_rationales.append(
    VersionRationale(
        descriptions=[InternationalString(text="Added income question for 2024 wave")]
    )
)
item.version_responsibility = "Survey Design Team"
```

Edit an item that is already in the file, then version it (see Module 13, sections 6 and 7):

<!-- docs-test: skip -- fragment: `question`, `variable` and `new_code_list` are the reader's own items -->
```python
question.question_texts[0].text = "In a typical week, do you work from home?"
question.increment_subversion()
variable.set_coded(new_code_list)  # switch to another code list
variable.increment_major_version()

# After a version bump, point references at the new version
variable.question_references = [
    question.to_reference() if ref.identifier == question.identifier else ref
    for ref in variable.question_references
]
```

---

## Questionnaire flow constructs

Questionnaire flow (the order questions are asked, and "skip" or "branch"
rules) is built from these control constructs:

| Construct | What it does |
| ----------- | -------------- |
| `QuestionConstruct` | Wraps one question so it can sit in a flow |
| `Sequence` | Runs steps in order (step 1, step 2, step 3) |
| `IfThenElse` | Branches based on a condition (skip logic) |
| `StatementItem` | Shows a message instead of asking a question |
| `Instrument` | The whole questionnaire; points to the top sequence |

You add each one with `doc.add_item(...)`, and link them with
`.to_reference()`:

```python
from ddi_l.models.datacollection import (
    QuestionConstruct,
    Sequence,
    IfThenElse,
    StatementItem,
    Instrument,
)

q = doc.add_question(text="What is your age?")

# Wrap a question, then group constructs into an ordered section
qc_age = doc.add_item(
    QuestionConstruct, name="Ask Age", question_reference=q.to_reference()
)
section_a = doc.add_item(
    Sequence, name="Section A", control_construct_references=[qc_age.to_reference()]
)
section_c = doc.add_item(Sequence, name="Section C")

# Branch: run section A if true, section C if false
gate = doc.add_item(IfThenElse, name="Age gate")
gate.then_construct_reference = section_a.to_reference()
gate.else_construct_reference = section_c.to_reference()

# Show a message; tie the whole thing together with an Instrument
doc.add_item(StatementItem, name="Welcome to the survey")
doc.add_item(Instrument, name="Survey Instrument")
```

`Loop` works the same way (`doc.add_item(Loop, name="...")`), with its
repeated section set via `loop.control_construct_reference`. See
[Module 8](module-08-questionnaire-flows.md) for the full worked example.

---

## Data files (physical instances)

A `PhysicalInstance` describes one real data file: where it lives and how big
it is. Add it like any other item; it lives at the study level.

```python
from ddi_l.models.physical import PhysicalInstance

pi = doc.add_item(PhysicalInstance, name="2021 Microdata File")
pi.set_data_file("https://example.org/health-2021.csv")  # where the file is
pi.set_record_count(15000)  # how many records
```

`name` becomes the file's citation title (a physical instance has no Name
element in DDI).

To say *where each variable sits* in that file, add a record layout:

<!-- docs-test: skip -- fragment: age/income come from the reader's own document -->
```python
rl = doc.add_record_layout()
rl.add_data_item(age.to_reference(), start_position=1, width=2)
rl.add_data_item(income.to_reference(), start_position=3, width=8)
```

Omit the positions for a delimited (comma/tab) file.

To update many variables from a new data file, and version each change, see
[Module 13, section 8](module-13-update-and-version.md#8-update-many-variables-from-a-new-data-file).

---

## Logical records and cubes

<!-- docs-test: skip -- fragment: year/region come from the reader's own document -->
```python
# A logical record = which variables make up one case (one row)
dr = doc.add_data_relationship()
dr.add_logical_record()  # all variables, the usual rectangular file

# An NCube = multidimensional (cube) data: axes + measured values
cube = doc.add_ncube(name="Population by year and region")
cube.add_dimension(year.to_reference())
cube.add_dimension(region.to_reference())
cube.add_measure(population.to_reference())

# Attach an attribute to a specific region of the cube
region = cube.add_coordinate_region()
cube.add_dimension_value(region, rank=1, code_references=[code_2020.to_reference()])
cube.add_attribute(footnote.to_reference(), attachment_region=region)
```

Fine-grained physical and inline-data forms:

<!-- docs-test: skip -- fragment: age/income come from the reader's own document -->
```python
# Numeric range with inclusivity flags and missing values
age.set_numeric(
    "Integer",
    low=0,
    high=120,
    low_inclusive=True,
    high_inclusive=False,
    missing_values=["-9", "-8"],
)

# A data item's storage details in a fixed-width/delimited file
layout.add_data_item(
    age.to_reference(),
    start_position=1,
    width=3,
    storage_format="ASCII",
    delimiter="comma",
    decimal_positions=2,
)

# Inline data as a RecordSet (rows) or VariableSet (columns)
ds = doc.add_dataset(name="Sample rows")
ds.set_variable_order([age.to_reference(), sex.to_reference()])
ds.add_record(["42", "M"])
ds.add_variable_item(age.to_reference(), ["42", "37"])  # column form

# Harmonization: scheme-to-scheme and representation maps
cmp = doc.add_comparison(name="2020 to 2021")
cmp.add_managed_item_map(
    [(age_2020.to_reference(), age_2021.to_reference())], type_of_mapped_item="Variable"
)
cmp.add_representation_map(
    codes_2020.to_reference(), codes_2021.to_reference(), recode.to_reference()
)
```

---

## Organize a study into a group

<!-- docs-test: skip -- fragment: age_2020 comes from the reader's own document -->
```python
# Wrap the study in a Group (a study series / publication package)
doc.add_group()
# The document stays editable; this still reaches the grouped study
doc.add_variable(name="region")

# Add more studies to the series, and map items across them
wave2 = doc.add_study(title="Wave 2")
# Edit a specific study via its cursor (doc.study() targets the primary)
doc.study(wave2.identifier).add_variable(name="income")
cmp = doc.add_comparison(name="2020 to 2021")
cmp.add_variable_map(age_2020.to_reference(), age_2021.to_reference())
```

---

## Instance-level packages and translation

```python
# Archive-specific lifecycle metadata for the study
doc.add_archive()

# Reusable metadata shared across studies (a ResourcePackage)
doc.add_resource_package()

# A local holding of a deposited study (references the primary study by default)
doc.add_local_holding_package()

# Record which languages the instance was translated between
doc.add_translation_information(
    languages=["en", "fr"], description="Translated from French."
)
```

---

## Data lineage (variable derivation)

<!-- docs-test: skip -- fragment: q_age comes from the reader's own document -->
```python
# Collection variable, linked to a question
v_age = doc.add_variable(name="age", question=q_age)

# Derived variable, linked to its source variable(s)
from ddi_l.models.base import Reference

v_age_group = doc.add_variable(name="age_group")
v_age_group.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_age.identifier, version="1"),
]

# Multi-source derivation
v_bmi = doc.add_variable(name="bmi")
v_bmi.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_height.identifier, version="1"),
    Reference(agency="health.gc.ca", identifier=v_weight.identifier, version="1"),
]
```

---

## Data linkage (combining datasets)

Link records from two sources that share a common variable (the *linkage key*).
Each source is its own study in a group, a `Comparison` records how the keys
correspond, and linked variables trace back to both sources.

```python
import ddi_l as ddi
from ddi_l.models.base import Reference

# Source 1: survey (the primary study)
doc = ddi.new_study(title="Survey", agency="statcan.gc.ca")
survey_key = doc.add_variable(name="anon_id")
survey_key.set_property("linkage_role", "key")  # tag the common key
survey_health = doc.add_variable(name="health_rating")

# Source 2: admin register (a second study in the group)
admin = doc.add_study(title="Admin register")
admin_ds = doc.study(admin.identifier)
admin_key = admin_ds.add_variable(name="anon_id")
admin_key.set_property("linkage_role", "key")
admin_visits = admin_ds.add_variable(name="hospital_visits")

# Map the keys; record the linkage method and quality
cmp = doc.add_comparison(name="Survey-to-Admin Linkage")
match = cmp.correspondence(commonality="Shared anonymized id.", weight=1.0)
cmp.add_variable_map(
    survey_key.to_reference(), admin_key.to_reference(), correspondence=match
)
cmp.set_property("linkage_method", "deterministic")  # or "probabilistic"
cmp.set_property("match_rate", "0.94")

# Linked variable: provenance to BOTH sources
linked = doc.add_variable(name="health_by_hospital_use")
linked.source_variable_references = [
    Reference(agency="statcan.gc.ca", identifier=survey_health.identifier, version="1"),
    Reference(agency="statcan.gc.ca", identifier=admin_visits.identifier, version="1"),
]
```

Cross-study `source_variable_references` warn on save. That is expected for
linkage. See [Module 10](module-10-data-linkage.md).

---

## Multi-language support

```python
from ddi_l.models.base import InternationalString

# Create a question in English (default)
q = doc.add_question(text="What is your age?", lang="en")

# Add a French translation
q.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
```

---

## Read data from CSV or Excel

Sample file: [`survey_sample.csv`](survey_sample.csv){ download="survey_sample.csv" }

<!-- docs-test: skip -- needs pandas, which ddi-l does not depend on -->
```python
import csv
import ddi_l as ddi

# From CSV
with open("survey_sample.csv") as f:
    columns = csv.DictReader(f).fieldnames

# Question wording from the questionnaire; unlisted columns get no question
QUESTIONS = {
    "age": "How old are you?",
    "gender": "What is your gender?",
    "income": "What was your total income last year, before taxes?",
    "education_level": "What is the highest level of education you have completed?",
}

doc = ddi.new_study(title="Survey", agency="example.org")
for col in columns:
    q = doc.add_question(text=QUESTIONS[col]) if col in QUESTIONS else None
    doc.add_variable(name=col, question=q)
doc.save("survey.xml")

# From Excel (requires pandas + openpyxl)
import pandas as pd

df = pd.read_excel("survey.xlsx")
for col in df.columns:
    doc.add_variable(name=col)
```

---

## CLI commands

Run these in your terminal.

| Command | What it does |
| --------- | ------------- |
| `ddi validate file.xml` | Check a file against the DDI schema |
| `ddi lint file.xml` | Run best-practice checks |
| `ddi to-json file.xml` | Convert DDI XML to JSON |
| `ddi from-json file.json -o file.xml` | Convert JSON back to DDI XML |
| `ddi roundtrip in.xml -o out.xml` | Read and re-write (tests fidelity) |
| `ddi versions file.xml` | Show version info from the file |

Exit code `0` means success. Exit code `1` means failure.

---

## All import paths

The table below lists every import you might need. The **When you
need it** column tells you what task the import is for.

### Top-level package

You get these with `import ddi_l as ddi`.

| What you type | What it gives you |
| --------------- | ------------------- |
| `ddi.new_study()` | Create a new DDI study document |
| `ddi.open_ddi()` | Open a DDI XML file from disk |
| `ddi.Document` | The document object (returned by `new_study` and `open_ddi`) |
| `ddi.DDIDocument` | Advanced: full DDI instance with indexing |
| `ddi.DDIFragment` | Advanced: a DDI fragment (partial document) |
| `ddi.read_ddi()` | Advanced: parse DDI from file, bytes, or string |
| `ddi.write_ddi()` | Advanced: serialize DDI to file or bytes |
| `ddi.iter_variables()` | Advanced: stream variables from a large file |
| `ddi.iter_questions()` | Advanced: stream questions from a large file |
| `ddi.iterparse_ddi()` | Advanced: memory-efficient streaming parse |
| `ddi.__version__` | The installed version number |

### Base types: `ddi_l.models.base`

These are building blocks used across all DDI types.

```python
from ddi_l.models.base import InternationalString
from ddi_l.models.base import Reference
from ddi_l.models.base import MaintainableBase
from ddi_l.models.base import VersionRationale
from ddi_l.models.base import CodeValue
from ddi_l.models.base import UserID
from ddi_l.models.base import UserAttributePair
```

| Class | When you need it |
| ------- | ----------------- |
| `InternationalString` | Add multi-language text to questions, variables, or concepts |
| `Reference` | Create a link from one DDI item to another |
| `MaintainableBase` | Base class for all DDI items (you rarely use this directly) |
| `VersionRationale` | Record why a version was changed |
| `CodeValue` | Represent a code-value pair |
| `UserID` | Attach a user-defined identifier to an item |
| `UserAttributePair` | Attach a custom key-value pair to an item |

### Variables and code lists: `ddi_l.models.logicalproduct`

```python
from ddi_l.models.logicalproduct import Variable
from ddi_l.models.logicalproduct import CodeList
from ddi_l.models.logicalproduct import Category
from ddi_l.models.logicalproduct import CodeItem
from ddi_l.models.logicalproduct import RepresentedVariable
from ddi_l.models.logicalproduct import VariableRepresentation
from ddi_l.models.logicalproduct import NumericRepresentation
from ddi_l.models.logicalproduct import CodeRepresentation
from ddi_l.models.logicalproduct import TextRepresentation
from ddi_l.models.logicalproduct import DateTimeRepresentation
from ddi_l.models.logicalproduct import NumberRange
```

| Class | When you need it |
| ------- | ----------------- |
| `Variable` | Work with a variable object directly |
| `CodeList` | A set of allowed answers (e.g., gender codes) |
| `Category` | One answer in a code list (e.g., "Male") |
| `CodeItem` | A code-value pair inside a code list |
| `RepresentedVariable` | A variable with its measurement type defined |
| `VariableRepresentation` | Describe what kind of values a variable holds |
| `NumericRepresentation` | Variable holds numbers (integer, decimal) |
| `CodeRepresentation` | Variable holds codes from a code list |
| `TextRepresentation` | Variable holds free text |
| `DateTimeRepresentation` | Variable holds dates or times |
| `NumberRange` | Set min/max range for a numeric variable |

### Questions and instruments: `ddi_l.models.datacollection`

```python
from ddi_l.models.datacollection import QuestionItem
from ddi_l.models.datacollection import QuestionConstruct
from ddi_l.models.datacollection import Sequence
from ddi_l.models.datacollection import IfThenElse
from ddi_l.models.datacollection import ElseIf
from ddi_l.models.datacollection import StatementItem
from ddi_l.models.datacollection import ComputationItem
from ddi_l.models.datacollection import Instrument
from ddi_l.models.datacollection import CollectionEvent
from ddi_l.models.methodology import Methodology
from ddi_l.models.datacollection import DataCollection
from ddi_l.models.datacollection import GenerationInstruction
from ddi_l.models.datacollection import GeneralInstruction
```

| Class | When you need it |
| ------- | ----------------- |
| `QuestionItem` | A single survey question |
| `QuestionConstruct` | Wrap a question so it can appear in a flow sequence |
| `Sequence` | Run constructs in order (step 1, step 2, step 3) |
| `IfThenElse` | Skip or branch based on a condition |
| `ElseIf` | Add extra branches to an `IfThenElse` |
| `StatementItem` | Show a message or instruction (not a question) |
| `ComputationItem` | Perform a calculation inside the flow |
| `Instrument` | The complete questionnaire (holds the top-level sequence) |
| `CollectionEvent` | When and how data was collected |
| `Methodology` | How the study was designed |
| `DataCollection` | Container for all data-collection metadata |
| `GenerationInstruction` | Instruction for generating data |
| `GeneralInstruction` | General instruction text |

### Concepts and universes: `ddi_l.models.conceptualcomponent`

```python
from ddi_l.models.conceptualcomponent import Concept
from ddi_l.models.conceptualcomponent import Universe
from ddi_l.models.conceptualcomponent import ConceptualVariable
from ddi_l.models.conceptualcomponent import UnitType
```

| Class | When you need it |
| ------- | ----------------- |
| `Concept` | A topic your variable measures (e.g., "Income") |
| `Universe` | The population your study covers (e.g., "Adults 18+") |
| `ConceptualVariable` | An abstract variable before measurement |
| `UnitType` | The type of thing being measured (person, household) |

### Study: `ddi_l.models.study`

```python
from ddi_l.models.study import StudyUnit
```

| Class       | When you need it                                        |
| ----------- | ------------------------------------------------------- |
| `StudyUnit` | The main container for a study (title, agency, content) |

### Validation: `ddi_l.validation`

```python
from ddi_l.validation import validate_document
from ddi_l.validation import validate_fragment
from ddi_l.validation import validate_maintainable
from ddi_l.validation import ValidationReport
from ddi_l.validation import ValidationMessage
```

| Class / Function | When you need it |
| ----------------- | ----------------- |
| `validate_document()` | Validate a full DDI document against the schema |
| `validate_fragment()` | Validate a DDI fragment |
| `validate_maintainable()` | Validate a single maintainable item |
| `ValidationReport` | The result object from validation |
| `ValidationMessage` | One error or warning from validation |

### Linting: `ddi_l.lint`

```python
from ddi_l.lint import run_lint
from ddi_l.lint import LintFinding
```

| Class / Function | When you need it |
| ----------------- | ----------------- |
| `run_lint()` | Run best-practice checks on a document |
| `LintFinding` | One finding from a lint check |

### Namespaces: `ddi_l.namespaces`

```python
from ddi_l.namespaces import DDI_STUDY_UNIT_PROFILE
from ddi_l.namespaces import DDI_DATA_COLLECTION_PROFILE
from ddi_l.namespaces import DDI_LOGICAL_PRODUCT_PROFILE
```

| Constant | When you need it |
| ---------- | ----------------- |
| `DDI_STUDY_UNIT_PROFILE` | Namespace bindings for study-unit documents |
| `DDI_DATA_COLLECTION_PROFILE` | Namespace bindings for data-collection documents |
| `DDI_LOGICAL_PRODUCT_PROFILE` | Namespace bindings for logical-product documents |

### Exceptions: `ddi_l.exceptions`

```python
from ddi_l.exceptions import DDIError
from ddi_l.exceptions import DDIParseError
from ddi_l.exceptions import DDIValidationError
from ddi_l.exceptions import DDIReadError
from ddi_l.exceptions import DDIWriteError
```

| Class | When you need it |
| ------- | ----------------- |
| `DDIError` | Catch any error from `ddi-l` |
| `DDIParseError` | The XML could not be parsed |
| `DDIValidationError` | The document failed schema validation |
| `DDIReadError` | The file could not be read |
| `DDIWriteError` | The file could not be written |

---

## Common patterns

### Build a complete study from a CSV

```python
import csv
import ddi_l as ddi
from ddi_l.models.logicalproduct import Category

doc = ddi.new_study(title="Household Survey", agency="stats.example.org")
universe = doc.add_universe(name="All households in Canada")

QUESTIONS = {
    "age": "How old are you?",
    "gender": "What is your gender?",
    "income": "What was your total income last year, before taxes?",
    "education_level": "What is the highest level of education you have completed?",
}

with open("survey_sample.csv") as f:
    reader = csv.DictReader(f)
    for col in reader.fieldnames:
        q = doc.add_question(text=QUESTIONS[col]) if col in QUESTIONS else None
        concept = doc.add_concept(name=col.replace("_", " ").title())
        doc.add_variable(name=col, question=q, concept=concept)

errors = doc.validate()
if not errors:
    doc.save("household-survey.xml")
    print("Saved and valid.")
```

### Open, enrich, version, and re-save

```python
import ddi_l as ddi
from ddi_l.models.base import VersionRationale, InternationalString

doc = ddi.open_ddi("survey-v1.xml")

q = doc.add_question(text="What is your email address?")
doc.add_variable(name="Email", question=q)

study = doc.study_unit
study.increment_minor_version()
study.version_rationales.append(
    VersionRationale(
        descriptions=[InternationalString(text="Added email question for wave 2")]
    )
)
study.version_responsibility = "Survey Team"

doc.validate()
doc.save("survey-v2.xml")
```

### Batch-validate from the command line

```bash
for file in data/*.xml; do
    echo "Checking $file..."
    ddi validate "$file" || echo "FAILED: $file"
done
```

---

## Where to learn more

- [User guide](../user-guide.md): Full API walkthrough
- [Validation guide](../validation.md): Schema and lint details
- [CLI recipes](../cli-recipes.md): All command-line examples
- [Models reference](../models.md): Advanced model layer
- [Training modules](index.md): Step-by-step curriculum
