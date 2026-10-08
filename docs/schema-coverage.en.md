---
description: >-
  How much of the DDI Lifecycle 3.3 schema ddi-l supports, and at which
  level: round-trip, typed models or the Document API.
---

# Schema coverage

This page is an honest map of how much of the DDI Lifecycle 3.3 schema
`ddi-l` supports, and at which level. "Support" means three different things,
so the table separates them into three tiers.

## The three tiers

1. **High-level API**: you can create and manage these with the simple
   `Document` API: `new_study()`, `add_question()`, `add_variable()`,
   `add_item()`, `items()`, `find()`, `remove()`. This is the easy,
   one-line path most authoring needs.
2. **Typed model**: every type in the module is a typed Python class with
   full `from_xml()` / `to_xml()` support, so you can read, build, and edit it
   precisely from `ddi_l.models.*` even when there is no one-line helper.
3. **Round-trip preserved**: opening a file and saving it again keeps the
   content byte-for-byte faithful, even for parts the library does not model
   in detail. Unrecognized elements are preserved verbatim.

!!! info "Nothing is lost"
    All of DDI 3.3 is **modeled and validated**: the model layer is generated
    from the official XSD (about 500 types), and `doc.validate()` checks
    against the real `instance_3_3.xsd`. Round-trip fidelity is complete: a
    100,000-element production file re-saves with zero element loss. The only
    thing that varies by module is **ergonomics**: how much typing you do.

## Coverage by module

| DDI module | High-level API | Typed model | Round-trip |
| ------------ | :--------------: | :-----------: | :----------: |
| Study Unit | Yes | Yes | Yes |
| Conceptual Component (concepts, universes, unit types) | Yes | Yes | Yes |
| Data Collection (questions, instruments, **questionnaire flow**) | Yes | Yes | Yes |
| Logical Product (variables, code lists, data relationships, NCubes) | Yes | Yes | Yes |
| Reusable (shared types: references, names, dates…) | n/a | Yes | Yes |
| Archive (citations, coverage, provenance) | Yes | Yes | Yes |
| Methodology (data collection methodology) | Yes | Yes | Yes |
| Process types (`urn:ddi-l:extension:process:1`) | No | Yes | Yes |
| Comparative (harmonization maps) | Yes | Yes | Yes |
| Physical Data Product: record layouts | Yes | Yes | Yes |
| Physical Data Product: structures, NCube | Yes | Yes | Yes |
| Physical Instance (data files) | Yes | Yes | Yes |
| Group (study series) | Yes | Yes | Yes |
| Resource / Local Holding Packages | Yes | Yes | Yes |
| Translation information | Yes | Yes | Yes |
| DDI Profile (usage declaration) | Yes | Yes | Yes |
| Dataset (inline data) | Yes | Yes | Yes |

"No" in the High-level API column means there is no one-line helper; use the
typed model instead. n/a means not applicable.

!!! warning "About the Process types"
    `ddi_l.models.process` models `Process`, `ProcessStep`, `ProcessControl`,
    `ProcessMethod` and their schemes. **DDI Lifecycle does not define these**:
    they appear in none of the 3.1, 3.2 or 3.3 schemas, neither as elements nor
    as complexTypes. They are a `ddi-l` extension, and they serialize into
    `urn:ddi-l:extension:process:1` so that is unmistakable in the output. Other
    DDI tools will not recognise them. Build them from `ddi_l.models.process`
    when you want the modelling; do not expect them to interoperate.

    DDI's own process vocabulary is `ProcessingEvent`, `ProcessingInstruction`
    and `ControlConstruct`, which live in `ddi:datacollection:3_3` and are
    modeled separately. Questionnaire and data-capture
    **flow** in DDI 3.3 instead lives in Data Collection as control constructs
    (`QuestionConstruct`, `Sequence`, `IfThenElse`, `StatementItem`,
    `ComputationItem`, `Loop`), which *are* first-class `add_item` types.

## What "add_item" covers

`add_item()` / `items()` currently recognize 30 item types, including the
full questionnaire-flow set (`QuestionConstruct`, `Sequence`, `IfThenElse`,
`StatementItem`, `ComputationItem`, `Loop`; see
[Module 10](curriculum/module-10-questionnaire-flows.md)), `PhysicalInstance`,
`RecordLayout`, `DataRelationship`, and `NCube`. A physical instance describes
one data file; a record layout maps variables to positions within it.

The samples on this page all continue from this setup:

```python
import ddi_l as ddi

doc = ddi.new_study(title="Health Survey", agency="example.org")
age = doc.add_variable(name="age")
income = doc.add_variable(name="income")
year = doc.add_variable(name="year")
region = doc.add_variable(name="region")
population = doc.add_variable(name="population")
footnote = doc.add_variable(name="footnote")
age_2020 = doc.add_variable(name="age_2020")
age_2021 = doc.add_variable(name="age_2021")
sex_codes = doc.add_code_list(name="Sex Codes")
```

```python
from ddi_l.models.physical import PhysicalInstance

pi = doc.add_item(PhysicalInstance, name="2021 Microdata File")
pi.set_data_file("https://example.org/health-2021.csv")
pi.set_record_count(15000)

# Map variables to fixed-width columns
rl = doc.add_record_layout()
rl.add_data_item(age.to_reference(), start_position=1, width=2)
rl.add_data_item(income.to_reference(), start_position=3, width=8)

# Logical records (which variables make up one case)
dr = doc.add_data_relationship()
dr.add_logical_record()  # all variables, one rectangular record

# Multidimensional (cube) data (with a coordinate region for an attribute)
cube = doc.add_ncube(name="Population by year and region")
cube.add_dimension(year.to_reference())
cube.add_dimension(region.to_reference())
cube.add_measure(population.to_reference())
region = cube.add_coordinate_region()
cube.add_attribute(footnote.to_reference(), attachment_region=region)

# Variable types: numeric / coded / text / datetime
# (numeric ranges take inclusivity flags and missing values)
doc.add_variable(name="age").set_numeric(
    "Integer", low=0, high=120, low_inclusive=True, missing_values=["-9"]
)
doc.add_variable(name="sex").set_coded(sex_codes)
```

## Reaching the model layer

When a module has no one-line helper, you still have full typed access. Build
the object from `ddi_l.models.*` and attach it, or read it back after
`open_ddi()`. For example, the physical data layer lives in
`ddi_l.models.physical`, the archive layer in `ddi_l.models.archive`, and so
on. Because every type round-trips, you can also open an existing file, reach
the part you need, edit it, and save; nothing else in the document changes.

## Groups

A document can be organized as a **Group** (a study series / publication
package). `doc.add_group()` moves the study under a `<g:Group>`, and the
document stays fully editable. Group-organized files open and round-trip:

```python
doc = ddi.new_study(title="Wave 1", agency="example.org")
doc.add_variable(name="age")
doc.add_group()  # organize the study into a group
doc.add_variable(name="income")  # still edits the (now grouped) study
```

Add **more** studies with `doc.add_study(title=...)`, and relate items across
them with a **Comparison**:

```python
doc.add_study(title="Wave 2")  # a second study in the series
cmp = doc.add_comparison(name="2020 to 2021")
cmp.add_variable_map(age_2020.to_reference(), age_2021.to_reference())
```

The high-level `add_*` helpers edit the *primary* study by default. To edit a
different study in the series, use its cursor: `doc.study(identifier)` returns a
`StudyCursor` whose `add_*` helpers target that study:

```python
wave2 = doc.add_study(title="Wave 2")
doc.study(wave2.identifier).add_variable(name="income")  # edits wave 2
doc.study().add_variable(name="age")  # edits the primary study
```

## Instance-level packages, archive, and translation

Beyond the study, a `DDIInstance` can carry reusable and holding packages, an
archive, and translation information, each with a one-line helper:

```python
doc.add_archive()  # archive lifecycle metadata on the study
doc.add_resource_package()  # reusable metadata shared across studies
doc.add_local_holding_package()  # a local holding of a deposited study
doc.add_translation_information(  # which languages the instance was translated between
    languages=["en", "fr"], description="Translated from French."
)
```

Read them back with `doc.archives`, `doc.resource_packages`,
`doc.local_holding_packages`, and `doc.translation_information`. Packages and
translation information are serialized into their correct positions in the
`DDIInstance` content model on save.

## Coverage summary

The high-level API spans **every** DDI Lifecycle 3.3 instance module: study
units, concepts, data collection and questionnaire flow, logical products
(variables with typed representations including inclusivity flags and missing
values, code lists, data relationships, NCubes with
dimensions/measures/attributes and coordinate regions), physical instances,
structures and record layouts (including segment keys and storage/decimal
details), inline datasets (item, record, and variable sets), study groups with
multi-study series (`doc.study(id)`) and the full set of comparison maps
(variable/concept/… maps plus managed-item and representation maps),
instance-level packages (resource, local-holding, archive, translation), and DDI
profiles. The one group that is model-layer-only is the **Process** types
(`urn:ddi-l:extension:process:1`), which DDI does not define at all. Everything
in every actual DDI module is modeled, validated, and round-tripped.
