# Authoring workflows

These hands-on tutorials show how to build DDI documents step by step using
the `ddi-l` CRUD API. Each lesson starts from a clean workspace and builds
up a study with questions, variables, concepts, and validation.

!!! note
    Install the package first so `ddi_l` is importable:

    ```bash
    pip install -e .
    ```

## Tutorial 1: Create a basic study

!!! info "Objectives"
    - Create a study with `ddi.new_study()`.
    - Add questions and variables.
    - Save to XML and verify the output.

1. Create the study:

    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="Tutorial Study", agency="tutorial.org")
    ```

2. Add questions:

    ```python
    q1 = doc.add_question(text="What is your age?")
    q2 = doc.add_question(text="What is your gender?")
    print(f"Questions: {len(doc.questions)}")
    ```

3. Add variables linked to questions:

    ```python
    doc.add_variable(name="Age", question=q1)
    doc.add_variable(name="Gender", question=q2)
    print(f"Variables: {len(doc.variables)}")
    ```

4. Save and inspect:

    ```python
    doc.save("tutorial-study.xml")
    ```

    Open the XML file to see the DDI structure with proper namespace prefixes.

## Tutorial 2: Add concepts and universes

!!! info "Objectives"
    - Add conceptual content to a study.
    - Link variables to concepts.

1. Build on the previous study:

    ```python
    age_concept = doc.add_concept(name="Age")
    gender_concept = doc.add_concept(name="Gender")
    doc.add_universe(name="Adults aged 18+")
    ```

2. Create variables with concept links:

    ```python
    doc.add_variable(name="Respondent age", question=q1, concept=age_concept)
    ```

3. Check the counts:

    ```python
    print(f"Concepts: {len(doc.concepts)}")
    print(f"Universes: {len(doc.universes)}")
    ```

## Tutorial 3: Use any item type

!!! info "Objectives"
    - Use `add_item()` for types beyond the basic five.
    - Query items with `items()`.
    - Find and remove items.

1. Add categories and instruments:

    ```python
    from ddi_l.models.logicalproduct import Category
    from ddi_l.models.datacollection import Instrument

    doc.add_item(Category, name="Male")
    doc.add_item(Category, name="Female")
    cat = doc.add_item(Category, name="Not specified")
    doc.add_item(Instrument, name="Online questionnaire")
    ```

2. Query by type:

    ```python
    print(f"Categories: {len(doc.items(Category))}")
    print(f"Instruments: {len(doc.items(Instrument))}")
    ```

3. Find and remove:

    ```python
    found = doc.find(cat.identifier)
    doc.remove(cat.identifier)
    print(f"Categories after removal: {len(doc.items(Category))}")
    ```

## Tutorial 4: Open, validate, and modify

!!! info "Objectives"
    - Open an existing DDI file.
    - Validate the document.
    - Add new content and save.

1. Open and validate:

    ```python
    doc = ddi.open_ddi("tutorial-study.xml", validate=True)
    ```

2. Add new content:

    ```python
    doc.add_question(text="What is your education level?")
    doc.add_code_list(name="Education Levels")
    ```

3. Validate and save:

    ```python
    issues = doc.validate()
    if not issues:
        doc.save("tutorial-study-updated.xml")
    ```

## Next steps

- See the [validation guide](../validation.md) for advanced validation options.
- See the [models reference](../models.md) for the full list of DDI types.
- Try the [training labs](training-labs.md) for self-paced exercises.
