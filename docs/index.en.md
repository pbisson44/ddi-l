---
title: ddi-l
description: >-
  ddi-l is a Python library and CLI for creating, reading, validating and
  linting DDI Lifecycle 3.1, 3.2 and 3.3 XML, with a bilingual training course.
template: home.html
hide:
  - navigation
  - toc
hero:
  eyebrow: DDI Lifecycle 3.1, 3.2 and 3.3
  title: Document surveys and datasets with DDI, in Python
  lead: >-
    Work with studies, questions and variables as Python objects. ddi-l writes
    the XML, validates it against the DDI schemas and lints it for what the
    schemas miss.
  primary:
    text: Start the course
    link: curriculum/
  secondary:
    text: Install
    link: installation/
  facts:
    - Python 3.11+
    - MIT licence
    - English and French
  terminal:
    label: Install ddi-l and validate a file
    copy: pip install ddi-l
    lines:
      - cmd: pip install ddi-l
      - cmd: ddi validate household-survey.xml
      - out: Document is valid.
---

## Why ddi-l

[DDI](https://ddialliance.org/) (Data Documentation Initiative) is the
international standard that statistical agencies, data archives and
researchers use to describe surveys and datasets: what was asked, what each
variable means, and who was surveyed. Written as XML, that documentation is
deeply nested and full of cross-references. `ddi-l` lets you write and check
it in Python instead of editing the XML by hand.

<div class="grid cards ddi-features" markdown>

- :material-language-python:{ .lg } **Write DDI in Python**

    ---

    Create studies, questions, variables and code lists as Python objects.
    `ddi-l` writes the DDI 3.3 XML and every reference between the items.

- :material-check-decagram-outline:{ .lg } **Validate any 3.x version**

    ---

    Check [DDI Lifecycle](https://ddialliance.org/Specification/DDI-Lifecycle/)
    3.1, 3.2 and 3.3 files against the official schemas, so archives can
    check older holdings with the same tool.

- :material-format-list-checks:{ .lg } **Lint what the schemas miss**

    ---

    Find items without labels, references to items that do not exist,
    missing translations and conditions that can never be true.

- :material-table-arrow-right:{ .lg } **Start from a spreadsheet**

    ---

    Describe a study in CSV files or an Excel workbook, then load it as DDI
    in one step.

- :material-swap-horizontal:{ .lg } **Work with other tools**

    ---

    Export JSON-LD for linked data, edit Colectica exports, bring in
    DDI-Codebook files, and use it all from R or over HTTP.

- :material-school-outline:{ .lg } **Learn as you go**

    ---

    A free course in English and French, from "what is metadata?" to a
    validated, versioned DDI package. No DDI or XML experience needed.

</div>

## Quick start

Install `ddi-l` from PyPI. The `full` extra adds the faster `lxml` backend
(see [Installation](installation.en.md)).

=== "pip"
    ```bash
    pip install ddi-l
    ```

=== "uv"
    ```bash
    uv add ddi-l
    uv run ddi --help
    ```

=== "Poetry"
    ```bash
    poetry add ddi-l
    poetry run ddi --help
    ```

Create a study, add a question and the variable that records its answer, and
save it:

```python
import ddi_l as ddi

# Create a new study
doc = ddi.new_study(title="Household Survey", agency="example.org")

# Add a question and the variable that records its answer. `label=` is
# optional, but `ddi lint` warns about every item without one.
q_age = doc.add_question(text="How old are you?", label="Age question")
doc.add_variable(name="Age", question=q_age, label="Age in years")

# Save to XML
doc.save("household-survey.xml")
```

Open it again later:

```python
# Open an existing study
doc = ddi.open_ddi("household-survey.xml")

for v in doc.variables:
    print(v.identifier)
```

Check the file from the command line. Both commands exit with status 0 when
the file is clean, so you can use them in scripts and CI:

```bash
ddi validate household-survey.xml
ddi lint household-survey.xml
```

The [user guide](user-guide.en.md#how-a-study-fits-together) shows how a
study's parts fit together and tours the whole `Document` API.

## Find your way

<div class="grid cards ddi-paths" markdown>

- :material-school-outline:{ .lg } **New to DDI?**

    ---

    Take the [course](curriculum/index.en.md): 17 modules, then optional
    ones on questionnaire gates, the HTTP API, DDI-Codebook and DDI-CDI.

- :material-compass-outline:{ .lg } **Have a task to do?**

    ---

    The [how-to guides](guides/index.en.md) cover validation, spreadsheets,
    other tools, the command line, R and HTTP.

- :material-book-open-page-variant-outline:{ .lg } **Looking something up?**

    ---

    The [reference](reference/index.en.md) has the user guide, the API and
    model references, and every lint rule.

- :material-source-pull:{ .lg } **Want to contribute?**

    ---

    Start with the
    [contributor guide](https://github.com/pbisson44/ddi-l/blob/main/CONTRIBUTING.md),
    then the [development guide](DEVELOPMENT.en.md).

</div>

## Cite ddi-l

If you use `ddi-l` in research or in an archive's workflow, please cite it:

> Bisson, P. (2026). *ddi-l: a Python toolkit for DDI Lifecycle 3.3 XML
> documents* (Version 0.2.1) [Computer software].
> <https://github.com/pbisson44/ddi-l>

```bibtex
@software{bisson_ddi_l,
  author  = {Bisson, Philippe},
  title   = {ddi-l: a Python toolkit for DDI Lifecycle 3.3 XML documents},
  year    = {2026},
  version = {0.2.1},
  url     = {https://github.com/pbisson44/ddi-l},
  license = {MIT}
}
```

The repository's
[`CITATION.cff`](https://github.com/pbisson44/ddi-l/blob/main/CITATION.cff)
holds the same metadata; GitHub's "Cite this repository" button exports it in
other formats.
