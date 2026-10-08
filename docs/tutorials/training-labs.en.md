# Interactive training exercises

These guided labs walk learners through the `ddi-l` CRUD API. Each lab is
designed for live facilitation or self-paced study.

## Lab 1: Build a survey from scratch

!!! info "Objectives"
    - Create a study, add questions and variables, and save to XML.
    - Practice using the CRUD API in a Python session.

### Steps

1. Install `ddi-l` and open a Python session:

    ```bash
    pip install -e .
    python
    ```

2. Create a study:

    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="Lab 1 Survey", agency="lab.org")
    ```

3. Add at least three questions and three variables. Link each variable to
   its question:

    ```python
    q1 = doc.add_question(text="What is your age?")
    doc.add_variable(name="Age", question=q1)
    ```

4. Add a concept and a universe:

    ```python
    doc.add_concept(name="Demographics")
    doc.add_universe(name="Adults")
    ```

5. Save and validate:

    ```python
    doc.save("lab1.xml")
    issues = doc.validate()
    print(f"Issues: {len(issues) if issues else 0}")
    ```

!!! success "Checkpoint"
    Your file `lab1.xml` should contain at least 3 questions, 3 variables,
    1 concept, and 1 universe.

## Lab 2: Open, modify, and re-validate

!!! info "Objectives"
    - Open an existing DDI file.
    - Add new content and remove existing items.
    - Validate and save.

### Steps

1. Open the file from Lab 1:

    ```python
    doc = ddi.open_ddi("lab1.xml")
    print(f"Questions: {len(doc.questions)}")
    ```

2. Add a code list and two categories:

    ```python
    from ddi_l.models.logicalproduct import Category

    doc.add_code_list(name="Age Groups")
    doc.add_item(Category, name="18-34")
    doc.add_item(Category, name="35-54")
    ```

3. Find a variable by identifier and remove it:

    ```python
    vars_list = doc.variables
    if vars_list:
        doc.remove(vars_list[0].identifier)
    ```

4. Validate and save:

    ```python
    issues = doc.validate()
    doc.save("lab2.xml")
    ```

!!! success "Checkpoint"
    `lab2.xml` should have one fewer variable than `lab1.xml` and include
    a code list with categories.

## Lab 3: CLI validation

!!! info "Objectives"
    - Use the `ddi` command-line tool to validate and inspect documents.

### Steps

1. Validate a file:

    ```bash
    ddi validate lab1.xml
    ```

2. Convert to JSON:

    ```bash
    ddi to-json lab1.xml --indent 2
    ```

3. Run lint checks:

    ```bash
    ddi lint lab1.xml
    ```

4. Round-trip a file:

    ```bash
    ddi roundtrip lab1.xml lab1-roundtrip.xml
    ```

!!! success "Checkpoint"
    All commands should complete without errors.
