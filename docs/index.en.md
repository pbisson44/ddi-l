# ddi-l

`ddi-l` is a Python library for creating, reading, updating and validating
[DDI Lifecycle 3.3](https://ddialliance.org/Specification/DDI-Lifecycle/3.3/)
XML documents. You work with studies, questions and variables as Python
objects, and `ddi-l` writes and checks the XML.

<div class="ddi-cta-group" markdown>

[Install ddi-l](installation.md#install-from-pypi){ .md-button .md-button--primary }
[Browse CLI recipes](cli-recipes.md){ .md-button .md-button--secondary .md-button--outlined }

</div>

## Quick start

```python
import ddi_l as ddi

# Create a new study
doc = ddi.new_study(title="Household Survey", agency="example.org")

# Add questions
q = doc.add_question(text="How old are you?")

# Add variables linked to questions
doc.add_variable(name="Age", question=q)

# Save to XML
doc.save("household-survey.xml")
```

```python
# Open an existing study
doc = ddi.open_ddi("household-survey.xml")

for v in doc.variables:
    print(v.identifier)
```

## Install

Install `ddi-l` with pip or Poetry. The `full` extra adds the faster `lxml`
backend (see [Installation](installation.md)).

=== "pip"
    ```bash
    pip install ddi-l
    ```

=== "Poetry"
    ```bash
    poetry add ddi-l
    poetry run ddi --help
    ```

## Where to go next

<div class="grid cards landing-tiles" markdown>

- **Install**

    Install the package with `pip` or `poetry` and check that it works.

    [Installation guide →](installation.md#install-from-pypi){ .md-button .md-button--primary }

- **Validate**

    Validate documents against the DDI schemas, run the lint rules, and add
    the checks to CI.

    [Validation guide →](validation.md){ .md-button .md-button--secondary .md-button--outlined }

- **Author**

    Build DDI documents step by step with the CRUD API.

    [Authoring tutorials →](tutorials/authoring.md){ .md-button .md-button--secondary .md-button--outlined }

- **Use the CLI**

    Validate, round-trip and convert files with the `ddi` command.

    [CLI recipes →](cli-recipes.md){ .md-button .md-button--secondary .md-button--outlined }

</div>

The site also has a 16-module [training curriculum](curriculum/index.md), an
[API reference](api.md) and a [models reference](models.md). To contribute,
see the [development guide](DEVELOPMENT.md) and the
[contributor guide](https://github.com/pbisson44/ddi-l/blob/main/CONTRIBUTING.md).
