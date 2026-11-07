---
description: >-
  Module 17 of the ddi-l course: four capstone projects, for students,
  researchers, archivists and statistical office staff.
---

# Module 17: Real-world capstone projects

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Write a project plan for your track's dataset: one row per column with its question (or why it has none), its type and its code list, plus the techniques your track needs.
    - **O2.** Build the DDI document from the data with `ddi-l`, so that each asked column is a variable linked to its question, coded columns use code lists with categories, and the study has concepts and a universe.
    - **O3.** Validate and lint your document so that `doc.validate()` returns no errors, `doc.lint()` reports no error, and `ddi validate` passes on every file you save.
    - **O4.** Record the questionnaire flow, lineage, linkage, custom fields or specification your track asks for, so that a reader of the XML can follow it without your script.
    - **O5.** Version a change: increment the version, record a rationale and who is responsible, and save each version to its own file.
    - **O6.** Present your project in 5 minutes and justify two design choices, naming for each the option you rejected and why.

**Prerequisites:** All previous modules, from [Module 1](module-01-what-is-metadata.en.md) to [Module 16](module-16-advanced-questionnaire-spec.en.md). The table under "Choose your track" lists the modules each track leans on most.

**Time:** 60-90 min self-paced / 90 min instructor-led.

**New in this module:** nothing new. You combine what earlier modules taught, such as `ddi.new_study()`, `doc.add_variable()`, `set_coded()`, `source_variable_references`, `doc.add_comparison()`, `set_property()`, `doc.lint()`, `load_spec()`, `ddi validate` and `ddi spec validate`.

---

## Introduction

You have now learned all the tools. You know how to create DDI
documents, add metadata, validate files, manage versions, and use the command
line. Now it is time to put everything together in a real project.

Choose the **track** that matches your role. Each track walks you through a
complete workflow: plan the metadata, build it from a data file, record what
your track needs, validate it, version it, and present your choices.

If you are not sure which track to pick, try **Track A** (University Student).
It is the simplest starting point.

### Choose your track

Every track practises all six objectives. They differ in the data and in the
techniques you record for objective O4:

| Track | For | Data | Techniques for O4 | Modules to review |
| --- | --- | --- | --- | --- |
| A | University students | `thesis-data.csv`: 40 students, 12 columns | Lineage: a derived stress index | 11 |
| B | Researchers | `health-survey.csv`: 40 respondents, 15 columns | Lineage (body mass index) and linkage to a hospital register | 11, 12 |
| C | Archivists | Three small DDI files from three research teams | Custom fields from a catalog, with an audit | 6, 13, 14 |
| D | National statistical office staff | `census-data.csv`: 55 people in 20 households, 22 columns | Questionnaire flow and a specification | 10, 16 |

---

## Plan your project

**(O1)** Good metadata starts on paper. Before you write any code, write a **plan**: a
short table with one row per column of your data file, and a few lines under
it. The plan is your first deliverable. It also saves time, because most
mistakes in a capstone come from deciding these things halfway through the
code.

For each column, decide:

- **Question:** the exact wording the respondent saw, or why there is none. An
  identifier such as a student ID is *assigned*, and a score can be
  *computed*. Neither gets a question.
- **Type:** numeric, coded (one answer from a fixed list), text, or date.
- **Code list:** for a coded column, the list of allowed answers.
- **Concept:** the idea the column measures, such as "Well-being".

Here are four rows of a plan for Track A:

| Column | Question, or why there is none | Type | Code list | Concept |
| --- | --- | --- | --- | --- |
| StudentID | None: assigned by the researcher | Text | None | None |
| Gender | "What is your gender?" | Coded | Female, Male, Non-binary | Demographics |
| StressLevel | "On a scale of 1 to 10, how stressed have you felt this term?" | Numeric, 1 to 10 | None | Well-being |
| AnxietyScore | None: computed from a standard anxiety scale | Numeric | None | Well-being |

Under the table, write three short notes:

- **Techniques:** which techniques your track needs (see the table above),
  and where each one applies. For Track A: "StressIndex is derived from
  StressLevel and AnxietyScore."
- **Versions:** what changes in the next version, and why.
- **Two design choices** you will present at the end (see "Present your
  project" below). For example: why Program is coded rather than free text.

---

## Track A: University Student: Document Your Thesis Dataset

!!! example "Scenario"
    You just finished your thesis on student stress. Your dataset has 12
    columns. You need to create a DDI document so your university's research
    repository can catalog your data.

### Steps

1. **(O1)** **Plan the project.** Download the sample thesis dataset (40
   students, 12 columns) or use your own CSV file with at least 10 columns.
   Fill in the plan table for every column.

    [:material-download: Download `thesis-data.csv`](thesis-data.csv){ .md-button download="thesis-data.csv" }

2. **(O2)** **Create a DDI study:**

    ```python
    import ddi_l as ddi

    doc = ddi.new_study(
        title="Student Stress Survey 2024",
        agency="university.example.org",
    )
    ```

3. **(O2)** **Add variables** from your CSV columns. Create one variable for
   each column. Link each variable to the question it came from. An
   identifier such as StudentID is assigned, and AnxietyScore is computed, so
   neither needs a question.

    ```python
    q1 = doc.add_question(text="How many hours do you study per day?")
    v1 = doc.add_variable(name="StudyHours", question=q1)
    q2 = doc.add_question(
        text="On a scale of 1 to 10, how stressed have you felt this term?"
    )
    stress = doc.add_variable(name="StressLevel", question=q2)
    # AnxietyScore is computed from a standard scale, so it has no question.
    anxiety = doc.add_variable(name="AnxietyScore")
    # Repeat for each column...
    ```

4. **(O2)** **Add 3 concepts and 1 universe:**

    ```python
    c1 = doc.add_concept(name="Academic Workload")
    c2 = doc.add_concept(name="Mental Health")
    c3 = doc.add_concept(name="Demographics")
    u1 = doc.add_universe(name="Undergraduate students aged 18-25")
    ```

5. **(O2)** **Add a code list with categories** for each coded column. A
   **code list** is the set of allowed answers. Each answer is a
   **category** (its meaning) and a **code** (the value stored in the data)
   that points at the category. `set_coded()` tells the variable which code
   list holds its values.

    ```python
    from uuid import uuid4

    from ddi_l.models.logicalproduct import Category, CodeItem

    gender_codes = doc.add_code_list(name="Gender Codes")
    for number, label in enumerate(["Female", "Male", "Non-binary"], start=1):
        category = doc.add_item(Category, name=label, label=label)
        gender_codes.codes.append(
            CodeItem(
                agency=gender_codes.agency,
                identifier=str(uuid4()),
                version=gender_codes.version,
                value=str(number),
                category=category.to_reference(),
            )
        )

    q3 = doc.add_question(text="What is your gender?")
    gender = doc.add_variable(name="Gender", question=q3)
    gender.set_coded(gender_codes)
    print(f"Gender codes: {len(gender_codes.codes)}")  # -> Gender codes: 3
    ```

6. **(O2)** **Set custom properties** on at least 2 items. A custom property
   is extra metadata you define yourself, like a data source or collection
   date.

    ```python
    v1.set_property("dataSource", "Online survey tool")
    v1.set_property("collectionDate", "2024-03-15")
    anxiety.set_property("scoring", "Sum of a standard 10-item anxiety scale")
    ```

7. **(O3)** **Validate, lint and save as version 1.0:**

    ```python
    errors = doc.validate()
    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"Validation errors: {len(errors)}, lint errors: {len(lint_errors)}")
    # -> Validation errors: 0, lint errors: 0
    doc.save("thesis-v1.xml")
    ```

    Lint may also report warnings, such as an item with no label. Read them,
    but only errors stop you from saving.

8. **(O4)** **Record the lineage of a derived variable.** Add StressIndex,
   which combines StressLevel and AnxietyScore. It is computed, not asked, so
   it has no question. Instead, `source_variable_references` lists the
   variables it was computed from.

    ```python
    stress_index = doc.add_variable(name="StressIndex")
    stress_index.source_variable_references = [
        stress.to_reference(),
        anxiety.to_reference(),
    ]
    print(f"StressIndex sources: {len(stress_index.source_variable_references)}")
    # -> StressIndex sources: 2
    ```

9. **(O5)** **Version the change.** Increment the version to 1.1, and record
   why and by whom.

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Added the derived StressIndex variable")
            ]
        )
    )
    study.version_responsibility = "Thesis Author"
    print(study.version)  # -> 1.1
    ```

10. **(O3)** **Validate, lint and save as version 1.1:**

    ```python
    errors = doc.validate()
    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    if not errors and not lint_errors:
        doc.save("thesis-v1.1.xml")
        print("Saved thesis-v1.1.xml")  # -> Saved thesis-v1.1.xml
    else:
        print("Errors:", errors, lint_errors)
    ```

### Deliverables

- Your plan: one row per column, and the three notes.
- `thesis-v1.xml`: valid DDI document with a variable for every column.
- `thesis-v1.1.xml`: version 1.1, with StressIndex, its two sources and a
  rationale.

??? success "Sample solution"
    One complete script for all the steps above, using
    [`thesis-data.csv`](thesis-data.csv){ download="thesis-data.csv" }.

    ```python
    import csv
    from uuid import uuid4

    import ddi_l as ddi
    from ddi_l.models.base import InternationalString, VersionRationale
    from ddi_l.models.logicalproduct import Category, CodeItem


    def add_codes(doc, code_list, labels):
        """Add one Category and one Code per label, numbered from 1."""
        for number, label in enumerate(labels, start=1):
            category = doc.add_item(Category, name=label, label=label)
            code_list.codes.append(
                CodeItem(
                    agency=code_list.agency,
                    identifier=str(uuid4()),
                    version=code_list.version,
                    value=str(number),
                    category=category.to_reference(),
                )
            )


    with open("thesis-data.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    columns = list(rows[0])

    # Version 1.0
    doc = ddi.new_study(title="Student Stress Survey 2024", agency="university.example.org")
    # How each column was asked. StudentID is assigned and AnxietyScore is computed
    # from a questionnaire, so neither gets a question of its own.
    QUESTIONS = {
        "Age": "How old are you?",
        "Gender": "What is your gender?",
        "YearOfStudy": "What year of your program are you in?",
        "Program": "Which program are you enrolled in?",
        "StudyHours": "On a typical day, how many hours do you study?",
        "SleepHours": "On a typical night, how many hours do you sleep?",
        "WorkHours": "How many hours a week do you work for pay?",
        "ExerciseDays": "On how many days last week did you exercise?",
        "StressLevel": "On a scale of 1 to 10, how stressed have you felt this term?",
        "SoughtSupport": "Have you sought support from campus services this term?",
    }
    questions = {col: doc.add_question(text=text) for col, text in QUESTIONS.items()}
    variables = {
        col: doc.add_variable(name=col, question=questions.get(col)) for col in columns
    }

    # One code list per coded column, from the values in the file
    for col in ("Gender", "Program", "SoughtSupport"):
        code_list = doc.add_code_list(name=f"{col} Codes")
        add_codes(doc, code_list, sorted({row[col] for row in rows}))
        variables[col].set_coded(code_list)

    doc.add_concept(name="Demographics")
    doc.add_concept(name="Academic Workload")
    doc.add_concept(name="Well-Being")
    doc.add_universe(name="Undergraduate students aged 18-25")
    variables["StudyHours"].set_property("dataSource", "Online survey tool")
    variables["AnxietyScore"].set_property(
        "scoring", "Sum of a standard 10-item anxiety scale"
    )

    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"v1: {len(doc.validate())} validation errors, {len(lint_errors)} lint errors")
    doc.save("thesis-v1.xml")

    # Version 1.1: a derived variable and its lineage
    doc = ddi.open_ddi("thesis-v1.xml")
    by_name = {v.names[0].text: v for v in doc.variables}
    stress_index = doc.add_variable(name="StressIndex")
    stress_index.source_variable_references = [
        by_name["StressLevel"].to_reference(),
        by_name["AnxietyScore"].to_reference(),
    ]

    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Added the derived StressIndex variable")
            ]
        )
    )
    study.version_responsibility = "Thesis Author"

    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"v1.1: {len(doc.validate())} validation errors, {len(lint_errors)} lint errors")
    # -> v1.1: 0 validation errors, 0 lint errors
    doc.save("thesis-v1.1.xml")
    ```

---

## Track B: Researcher: Package a Health Survey for Publication

!!! example "Scenario"
    You lead a multi-country health study. Your data file has 15 columns of
    survey data. Your team also linked each respondent to a hospital
    admissions register. You need to package the metadata for an open data
    repository.

### Steps

1. **(O1)** **Plan the project and read the data.** Start from a data file
   with at least 15 columns. Download the sample health survey (40
   respondents, 15 columns) or use your own. Fill in the plan table, then read
   the column names:

    [:material-download: Download `health-survey.csv`](health-survey.csv){ .md-button download="health-survey.csv" }

    ```python
    import csv

    import ddi_l as ddi

    with open("health-survey.csv", newline="", encoding="utf-8") as f:
        columns = csv.DictReader(f).fieldnames

    doc = ddi.new_study(
        title="International Health Survey 2024",
        agency="health-research.example.org",
    )
    print(f"{len(columns)} columns")  # -> 15 columns
    ```

    If your data is in an Excel workbook, read the column names with pandas
    instead (see [Module 8](module-08-csv-to-ddi.en.md)):

    <!-- docs-test: skip -- needs pandas and a workbook the reader supplies -->
    ```python
    import pandas as pd

    columns = list(pd.read_excel("health-survey.xlsx").columns)
    ```

2. **(O2)** **Create the questions and variables** from the columns. The
   first line below creates one question per entry of `QUESTIONS`. The second
   creates one variable per column and links it to its question.
   `questions.get(col)` gives `None` for a column with no question, such as
   RespondentID.

    ```python
    # Copy the wording from your questionnaire. Columns left out, such as
    # RespondentID, become variables without a question.
    QUESTIONS = {
        "Age": "How old are you?",
        "SmokingStatus": "Which of these best describes your smoking?",
        "ExerciseFrequency": "How often do you exercise for at least 30 minutes?",
        "SelfRatedHealth": "In general, how would you rate your health?",
        # ...one entry for each column you asked about
    }
    questions = {col: doc.add_question(text=text) for col, text in QUESTIONS.items()}
    variables = {
        col: doc.add_variable(name=col, question=questions.get(col)) for col in columns
    }
    print(f"Variables: {len(doc.variables)}")  # -> Variables: 15
    ```

3. **(O2)** **Add 4 concepts and a universe:**

    ```python
    doc.add_concept(name="Physical Health")
    doc.add_concept(name="Mental Health")
    doc.add_concept(name="Access to Healthcare")
    doc.add_concept(name="Demographics")
    doc.add_universe(name="Adults aged 18 and over in the participating countries")
    ```

4. **(O2)** **Add 2 code lists** built from the values in the file. A
   **code list** is a set of allowed answers (like "Yes", "No", "Unsure").
   `{row[col] for row in rows}` collects the distinct values of a column; each
   one becomes a category and a code, and `set_coded()` points the variable at
   the list.

    ```python
    from uuid import uuid4

    from ddi_l.models.logicalproduct import Category, CodeItem

    with open("health-survey.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for col in ["SmokingStatus", "ExerciseFrequency"]:
        code_list = doc.add_code_list(name=f"{col} Codes")
        for number, label in enumerate(sorted({row[col] for row in rows}), start=1):
            category = doc.add_item(Category, name=label, label=label)
            code_list.codes.append(
                CodeItem(
                    agency=code_list.agency,
                    identifier=str(uuid4()),
                    version=code_list.version,
                    value=str(number),
                    category=category.to_reference(),
                )
            )
        variables[col].set_coded(code_list)

    print(f"Code lists: {len(doc.code_lists)}")  # -> Code lists: 2
    ```

5. **(O4)** **Record lineage.** Body mass index (BMI) is computed from
   height and weight. It gets no question; it lists its two sources instead
   (see [Module 11](module-11-data-lineage.en.md)):

    ```python
    bmi = doc.add_variable(name="BMI", label="Body mass index")
    bmi.source_variable_references = [
        variables["HeightCm"].to_reference(),
        variables["WeightKg"].to_reference(),
    ]
    ```

6. **(O4)** **Record the linkage.** Your team joined the survey to a
   hospital admissions register on RespondentID. Record it as in
   [Module 12](module-12-data-linkage.en.md): the register is a second study,
   the key is tagged on both sides, a `Comparison` maps the keys, and the
   linked variable names its sources in both studies.

    ```python
    register = doc.add_study(title="Hospital Admissions Register 2024")
    register_ds = doc.study(register.identifier)
    register_key = register_ds.add_variable(name="RespondentID")
    admissions = register_ds.add_variable(name="HospitalAdmissions")

    variables["RespondentID"].set_property("linkage_role", "key")
    register_key.set_property("linkage_role", "key")

    link = doc.add_comparison(name="Survey-to-register linkage 2024")
    exact = link.correspondence(
        commonality="The same respondent identifier in both sources.",
        weight=1.0,
    )
    link.add_variable_map(
        variables["RespondentID"].to_reference(),
        register_key.to_reference(),
        correspondence=exact,
    )
    link.set_property("linkage_method", "deterministic")

    linked = doc.add_variable(name="HealthByHospitalUse")
    linked.source_variable_references = [
        variables["SelfRatedHealth"].to_reference(),
        admissions.to_reference(),
    ]
    print(f"Comparisons: {len(doc.comparisons)}")  # -> Comparisons: 1
    ```

    When you save, `ddi-l` warns that a source variable is not in the current
    document. That is expected: it is in the register study.

7. **(O3)** **Validate and lint the document:**

    ```python
    errors = doc.validate()
    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"Validation errors: {len(errors)}, lint errors: {len(lint_errors)}")
    # -> Validation errors: 0, lint errors: 0
    ```

8. **(O3)** **Save as version 1.0:**

    ```python
    doc.save("health-survey-v1.xml")
    ```

    Then **export it to JSON** from the command line:

    ```bash
    ddi to-json health-survey-v1.xml --indent 2 > health-survey-v1.json
    ```

9. **(O5)** **Update to version 1.1** with a rationale. Add a new variable or
   fix a label.

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    q_dentist = doc.add_question(
        text="How many times did you see a dentist in the last 12 months?"
    )
    doc.add_variable(name="DentistVisitsLastYear", question=q_dentist)
    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added dental visit frequency question")]
        )
    )
    study.version_responsibility = "Principal Investigator"
    doc.save("health-survey-v1.1.xml")
    ```

    Check the new file from the command line with
    `ddi validate health-survey-v1.1.xml`.

### Deliverables

- Your plan: one row per column, and the three notes.
- `health-survey-v1.xml`: valid DDI document, with BMI's lineage and the
  linkage to the register.
- `health-survey-v1.json`: JSON export of the document.
- `health-survey-v1.1.xml`: updated version with rationale.

??? success "Sample solution"
    One complete script, using
    [`health-survey.csv`](health-survey.csv){ download="health-survey.csv" }.
    Run `ddi to-json health-survey-v1.xml --indent 2 > health-survey-v1.json`
    after it.

    ```python
    import csv
    from uuid import uuid4

    import ddi_l as ddi
    from ddi_l.models.base import InternationalString, VersionRationale
    from ddi_l.models.logicalproduct import Category, CodeItem


    def add_codes(doc, code_list, labels):
        """Add one Category and one Code per label, numbered from 1."""
        for number, label in enumerate(labels, start=1):
            category = doc.add_item(Category, name=label, label=label)
            code_list.codes.append(
                CodeItem(
                    agency=code_list.agency,
                    identifier=str(uuid4()),
                    version=code_list.version,
                    value=str(number),
                    category=category.to_reference(),
                )
            )


    with open("health-survey.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    columns = list(rows[0])

    doc = ddi.new_study(
        title="International Health Survey 2024", agency="health-research.example.org"
    )
    # RespondentID is assigned, not asked, so it gets no question.
    QUESTIONS = {
        "Country": "In which country do you live?",
        "Age": "How old are you?",
        "Sex": "What is your sex?",
        "HeightCm": "How tall are you, in centimetres?",
        "WeightKg": "How much do you weigh, in kilograms?",
        "SmokingStatus": "Which of these best describes your smoking?",
        "ExerciseFrequency": "How often do you exercise for at least 30 minutes?",
        "AlcoholDrinksPerWeek": "How many alcoholic drinks do you have in a typical week?",
        "SelfRatedHealth": "In general, how would you rate your health?",
        "ChronicCondition": "Do you have a long-term health condition?",
        "DoctorVisitsLastYear": "How many times did you see a doctor in the last 12 months?",
        "HasHealthInsurance": "Do you have health insurance?",
        "SleepHours": "On a typical night, how many hours do you sleep?",
        "Wellbeing": "On a scale of 0 to 10, how satisfied are you with your life?",
    }
    questions = {col: doc.add_question(text=text) for col, text in QUESTIONS.items()}
    variables = {
        col: doc.add_variable(name=col, question=questions.get(col)) for col in columns
    }

    for col in ("SmokingStatus", "ExerciseFrequency"):
        code_list = doc.add_code_list(name=f"{col} Codes")
        add_codes(doc, code_list, sorted({row[col] for row in rows}))
        variables[col].set_coded(code_list)

    for name in (
        "Physical Health",
        "Mental Health",
        "Access to Healthcare",
        "Demographics",
    ):
        doc.add_concept(name=name)
    doc.add_universe(name="Adults aged 18 and over in the participating countries")

    # Lineage: BMI is computed from height and weight
    bmi = doc.add_variable(name="BMI", label="Body mass index")
    bmi.source_variable_references = [
        variables["HeightCm"].to_reference(),
        variables["WeightKg"].to_reference(),
    ]

    # Linkage: the register is a second study, joined on RespondentID
    register = doc.add_study(title="Hospital Admissions Register 2024")
    register_ds = doc.study(register.identifier)
    register_key = register_ds.add_variable(name="RespondentID")
    admissions = register_ds.add_variable(name="HospitalAdmissions")
    variables["RespondentID"].set_property("linkage_role", "key")
    register_key.set_property("linkage_role", "key")

    link = doc.add_comparison(name="Survey-to-register linkage 2024")
    exact = link.correspondence(
        commonality="The same respondent identifier in both sources.", weight=1.0
    )
    link.add_variable_map(
        variables["RespondentID"].to_reference(),
        register_key.to_reference(),
        correspondence=exact,
    )
    link.set_property("linkage_method", "deterministic")
    linked = doc.add_variable(name="HealthByHospitalUse")
    linked.source_variable_references = [
        variables["SelfRatedHealth"].to_reference(),
        admissions.to_reference(),
    ]

    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"v1: {len(doc.validate())} validation errors, {len(lint_errors)} lint errors")
    # -> v1: 0 validation errors, 0 lint errors
    doc.save("health-survey-v1.xml")

    # Version 1.1
    dentist = doc.add_question(
        text="How many times did you see a dentist in the last 12 months?"
    )
    doc.add_variable(name="DentistVisitsLastYear", question=dentist)
    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added dental visit frequency question")]
        )
    )
    study.version_responsibility = "Principal Investigator"
    print(f"v1.1: {len(doc.validate())} validation errors")
    # -> v1.1: 0 validation errors
    doc.save("health-survey-v1.1.xml")
    ```

---

## Track C: Archivist: Enrich and Version Existing DDI Files

!!! example "Scenario"
    You manage a data collection at a national library. You receive 3 DDI files
    from different research teams. Some files are missing metadata. You need to
    check each file, add what is missing, record the archive's own facts about
    it, and create new versions.

### Steps

1. **(O1)** **Prepare 3 DDI files and plan.** Use files from earlier modules,
   or create 3 small studies now. Your plan has one row per file: what it
   holds, what is missing, and what you will add.

    ```python
    import ddi_l as ddi

    questions = [
        "How old are you?",
        "How many people live in your household?",
        "Did you vote in the last federal election?",
    ]
    for i, text in enumerate(questions, start=1):
        doc = ddi.new_study(
            title=f"Research Study {i}",
            agency="library.example.org",
        )
        doc.add_question(text=text)
        doc.add_variable(name=f"Var{i}")
        doc.save(f"study-{i}.xml")
    ```

2. **(O3)** **For each file, check completeness.** Open the file and list what
   it contains. The last line counts the variables linked to a question:

    ```python
    doc = ddi.open_ddi("study-1.xml")
    print(f"Questions:  {len(doc.questions)}")
    print(f"Variables:  {len(doc.variables)}")
    print(f"Concepts:   {len(doc.concepts)}")
    print(f"Universes:  {len(doc.universes)}")
    print(f"Code lists: {len(doc.code_lists)}")
    linked = sum(1 for v in doc.variables if v.question_references)
    print(f"Variables linked to a question: {linked}")
    # -> Variables linked to a question: 0
    ```

3. **(O2)** **Add missing metadata.** If a file has no concepts, add one. If
   it has no universe, add one. If a variable is not linked to its question,
   link it. If a question has a fixed set of answers, such as the vote
   question in study 3, add a code list with categories and point the
   variable at it (the sample solution shows how).

    ```python
    doc.add_concept(name="Social Sciences")
    doc.add_universe(name="General population")

    # Link the variable to the question it records
    variable, question = doc.variables[0], doc.questions[0]
    variable.question_references = [question.to_reference()]
    ```

4. **(O4)** **Add custom fields from a catalog.** Your archive records the
   same facts about every file it accepts. Write them down once as a
   **catalog**: one namespace (`archive:`) and the meaning of each key (see
   [Module 14](module-14-custom-fields.en.md)). Set fields only through a
   function that checks the catalog, so a typo cannot create a new key. Then
   audit the file: count the items that carry your fields.

    ```python
    ARCHIVE_FIELDS = {
        "archive:accession_date": "Date the archive received the file.",
        "archive:depositor": "Team that deposited the file.",
        "archive:retention": "How long the archive keeps the file.",
        "archive:access": "Who may use the data: open, registered or restricted.",
    }


    def set_archive_field(item, key, value):
        if key not in ARCHIVE_FIELDS:
            raise KeyError(f"{key!r} is not in the archive catalog")
        item.set_property(key, value)


    def count_archive_fields(doc):
        items = [doc.study_unit, *doc.questions, *doc.variables]
        return sum(
            any(key.startswith("archive:") for key in item.properties) for item in items
        )


    study = doc.study_unit
    set_archive_field(study, "archive:accession_date", "2024-11-04")
    set_archive_field(study, "archive:depositor", "Research team 1")
    set_archive_field(study, "archive:retention", "permanent")
    set_archive_field(variable, "archive:access", "open")
    print(f"Items with archive fields: {count_archive_fields(doc)}")
    # -> Items with archive fields: 2
    ```

5. **(O5)** **Increment the version with a rationale:**

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(
                    text="Enriched metadata: added concept, universe, question link and archive fields"
                )
            ]
        )
    )
    study.version_responsibility = "Archive Metadata Team"
    ```

6. **(O3)** **Validate, lint and save:**

    ```python
    errors = doc.validate()
    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    if not errors and not lint_errors:
        doc.save("study-1-enriched.xml")
        print("Saved study-1-enriched.xml")  # -> Saved study-1-enriched.xml
    ```

7. **Repeat steps 2 to 6 for all 3 files.**

### Deliverables

- Your plan: one row per file.
- 3 updated XML files (`study-1-enriched.xml`, `study-2-enriched.xml`,
  `study-3-enriched.xml`), all valid, each with a version rationale.
- Your custom-field catalog, and the audit count for each file.

??? success "Sample solution"
    One loop over the three files from step 1.

    ```python
    from uuid import uuid4

    import ddi_l as ddi
    from ddi_l.models.base import InternationalString, VersionRationale
    from ddi_l.models.logicalproduct import Category, CodeItem

    ARCHIVE_FIELDS = {
        "archive:accession_date": "Date the archive received the file.",
        "archive:depositor": "Team that deposited the file.",
        "archive:retention": "How long the archive keeps the file.",
        "archive:access": "Who may use the data: open, registered or restricted.",
    }
    YES_NO_FILES = {3}  # from the plan: study 3 asks a yes/no question


    def set_archive_field(item, key, value):
        if key not in ARCHIVE_FIELDS:
            raise KeyError(f"{key!r} is not in the archive catalog")
        item.set_property(key, value)


    def count_archive_fields(doc):
        items = [doc.study_unit, *doc.questions, *doc.variables]
        return sum(
            any(key.startswith("archive:") for key in item.properties) for item in items
        )


    for i in (1, 2, 3):
        doc = ddi.open_ddi(f"study-{i}.xml")
        if not doc.concepts:
            doc.add_concept(name="Social Sciences")
        if not doc.universes:
            doc.add_universe(name="General population")
        variable, question = doc.variables[0], doc.questions[0]
        if not variable.question_references:
            variable.question_references = [question.to_reference()]
        if i in YES_NO_FILES:
            yes_no = doc.add_code_list(name="Yes/No")
            for value, label in (("1", "Yes"), ("2", "No")):
                category = doc.add_item(Category, name=label, label=label)
                yes_no.codes.append(
                    CodeItem(
                        agency=yes_no.agency,
                        identifier=str(uuid4()),
                        version=yes_no.version,
                        value=value,
                        category=category.to_reference(),
                    )
                )
            variable.set_coded(yes_no)

        study = doc.study_unit
        set_archive_field(study, "archive:accession_date", "2024-11-04")
        set_archive_field(study, "archive:depositor", f"Research team {i}")
        set_archive_field(study, "archive:retention", "permanent")
        set_archive_field(variable, "archive:access", "open")

        study.increment_minor_version(allow_dotted=True)
        study.version_rationales.append(
            VersionRationale(
                descriptions=[
                    InternationalString(
                        text="Enriched metadata: added concept, universe, question link and archive fields"
                    )
                ]
            )
        )
        study.version_responsibility = "Archive Metadata Team"

        lint_errors = [f for f in doc.lint() if f.severity == "error"]
        print(
            f"study-{i}: {len(doc.validate())} validation errors, "
            f"{len(lint_errors)} lint errors, "
            f"{count_archive_fields(doc)} items with archive fields"
        )
        doc.save(f"study-{i}-enriched.xml")
    # -> study-3: 0 validation errors, 0 lint errors, 2 items with archive fields
    ```

---

## Track D: NSO Staff: Build a Census Instrument

!!! example "Scenario"
    You work at a national statistics office. Your census team has a large CSV
    file with 20+ columns. You need to build a complete DDI document, create
    code lists from the data, describe the questionnaire's flow and write its
    specification, manage multiple versions, and automate validation with a
    bash script.

### Steps

1. **(O1)** **Plan the project and read the data.** Start from a large CSV
   with 20+ columns. Download the sample census extract (55 people in 20
   households, 22 columns, including the five coded columns used in step 3)
   or use your own. Fill in the plan table. Note that EmploymentType says
   "Not applicable" for children: that is a gate, which step 5 records.

    [:material-download: Download `census-data.csv`](census-data.csv){ .md-button download="census-data.csv" }

    ```python
    import csv

    import ddi_l as ddi

    with open("census-data.csv", newline="", encoding="utf-8") as f:
        columns = csv.DictReader(f).fieldnames

    doc = ddi.new_study(
        title="National Census 2024",
        agency="census.example.gov",
    )
    print(f"{len(columns)} columns")  # -> 22 columns
    ```

2. **(O2)** **Create 20+ variables** from the CSV columns, each linked to its
   question:

    ```python
    # Wording from the census questionnaire. HouseholdID and PersonNumber are
    # assigned, not asked, so they are left out and get no question.
    QUESTIONS = {
        "Province": "In which province or territory do you live?",
        "Age": "What was your age at your last birthday?",
        "Gender": "What is your gender?",
        "MaritalStatus": "What is your marital status?",
        "EmploymentType": "Last week, were you an employee, self-employed, or not working?",
        "HousingType": "What type of dwelling do you live in?",
        # ...one entry for each remaining column
    }
    questions = {col: doc.add_question(text=text) for col, text in QUESTIONS.items()}
    variables = {
        col: doc.add_variable(name=col, question=questions.get(col)) for col in columns
    }
    print(f"Variables: {len(doc.variables)}")  # -> Variables: 22
    ```

3. **(O2)** **Build 5 code lists** from the values in the file, each with
   one category and one code per value:

    ```python
    from uuid import uuid4

    from ddi_l.models.logicalproduct import Category, CodeItem

    with open("census-data.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    categorical_cols = [
        "Province",
        "Gender",
        "MaritalStatus",
        "EmploymentType",
        "HousingType",
    ]
    for col in categorical_cols:
        code_list = doc.add_code_list(name=f"{col}Codes")
        for number, label in enumerate(sorted({row[col] for row in rows}), start=1):
            category = doc.add_item(Category, name=label, label=label)
            code_list.codes.append(
                CodeItem(
                    agency=code_list.agency,
                    identifier=str(uuid4()),
                    version=code_list.version,
                    value=str(number),
                    category=category.to_reference(),
                )
            )
        variables[col].set_coded(code_list)

    print(f"Code lists: {len(doc.code_lists)}")  # -> Code lists: 5
    ```

4. **(O2)** **Add concepts, a universe and custom properties.** Set custom
   properties, such as a classification, on at least 2 items:

    ```python
    doc.add_concept(name="Population")
    doc.add_concept(name="Labour")
    doc.add_universe(name="All persons usually resident in private dwellings")

    variables["Occupation"].set_property("classification", "ISCO-08")
    variables["AnnualIncome"].set_property("referencePeriod", "Calendar year 2023")
    ```

5. **(O4)** **Build the questionnaire flow.** Everyone answers the person
   questions. Only people aged 15 and over answer the labour questions. Build
   the flow as in [Module 10](module-10-questionnaire-flows.en.md): a
   `QuestionConstruct` for each question, a `Sequence` for each section, an
   `IfThenElse` for the gate, and an `Instrument` that points at the main
   sequence.

    ```python
    from ddi_l.models.datacollection import (
        IfThenElse,
        Instrument,
        QuestionConstruct,
        Sequence,
    )

    AGE_GATE = "Age >= 15"


    def ask(col):
        """A QuestionConstruct that asks the question of column col."""
        return doc.add_item(
            QuestionConstruct, name=col, question_reference=questions[col].to_reference()
        )


    person = doc.add_item(
        Sequence,
        name="person",
        control_construct_references=[
            ask("Age").to_reference(),
            ask("Gender").to_reference(),
        ],
    )
    labour = doc.add_item(
        Sequence,
        name="labour",
        control_construct_references=[ask("EmploymentType").to_reference()],
    )
    gate = doc.add_item(IfThenElse, name="Working-age gate")
    gate.set_condition(AGE_GATE, description="Persons aged 15 and over")
    gate.then_construct_reference = labour.to_reference()

    main = doc.add_item(
        Sequence,
        name="Census flow",
        control_construct_references=[person.to_reference(), gate.to_reference()],
    )
    instrument = doc.add_item(Instrument, name="Census 2024 questionnaire")
    instrument.control_construct_reference = main.to_reference()
    print(f"Instruments: {len(doc.items(Instrument))}")  # -> Instruments: 1
    ```

6. **(O4)** **Write the specification.** A spec says what the instrument must
   contain: its modules, their questions and the gates (see
   [Module 16](module-16-advanced-questionnaire-spec.en.md)). Write it to a file,
   load it, and check that its gate says the same as the instrument's.

    ```python
    from pathlib import Path

    from ddi_l.spec import equivalent, load_spec

    SPEC = """\
    spec: census-2024
    version: "1"
    code_lists:
      Employment:
        values: {1: Employee, 2: Self-employed, 3: Unemployed, 4: Not in labour force}
    modules:
      - id: person
        questions:
          - id: Age
            domain: {numeric: {min: 0, max: 120, decimals: 0}}
      - id: labour
        gate: Age >= 15
        questions:
          - id: EmploymentType
            domain: {code: {list: Employment}}
    """
    Path("census.spec.yaml").write_text(SPEC, encoding="utf-8")

    spec = load_spec("census.spec.yaml")
    labour_gate = spec.module("labour").gate_text
    print(labour_gate, equivalent(labour_gate, AGE_GATE))  # -> Age >= 15 True
    print(equivalent(AGE_GATE, "not Age < 15"))  # -> False
    ```

    Decide what the gate does when Age has no answer, and write it in your
    plan. `Age >= 15` is false when Age is missing, so a person with no age
    skips the labour questions. `not Age < 15` would ask them, which is why
    `equivalent()` says the two differ. "Not applicable" is not in the spec's
    code list: it is what the data holds for people the gate skipped.

    Check the spec file from the command line too:

    ```bash
    ddi spec validate census.spec.yaml
    ```

7. **(O3)** **Validate, lint and save as version 1.0:**

    ```python
    errors = doc.validate()
    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"Validation errors: {len(errors)}, lint errors: {len(lint_errors)}")
    # -> Validation errors: 0, lint errors: 0
    doc.save("census-v1.xml")
    ```

8. **(O5)** **Update to version 1.1**: add a new question and variable:

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    q_internet = doc.add_question(text="Do you have access to high-speed internet?")
    doc.add_variable(name="HighSpeedInternet", question=q_internet)
    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added internet access question")]
        )
    )
    study.version_responsibility = "Census Content Team"
    doc.save("census-v1.1.xml")
    ```

9. **(O5)** **Update to version 2.0**: major redesign (add 5 new questions,
   retire 3 old ones). Retiring a question also retires the variable that
   recorded its answers; otherwise the variable would keep pointing at a
   question that is no longer in the file (see
   [Module 15](module-15-update-and-version.en.md)). Retire only questions the
   flow does not use. A version holds one rationale, so replace the one from
   version 1.1; `census-v1.1.xml` keeps it.

    ```python
    # Add new questions
    for text in [
        "What is your primary language at home?",
        "Do you identify as Indigenous?",
        "What is your highest degree?",
        "Do you have a disability?",
        "What is your annual household income?",
    ]:
        doc.add_question(text=text)

    # Retire 3 old questions, and the variables that recorded their answers
    for col in ["Province", "MaritalStatus", "HousingType"]:
        doc.remove(variables[col].identifier)
        doc.remove(questions[col].identifier)

    study.increment_major_version()
    study.version_rationales = [
        VersionRationale(
            descriptions=[
                InternationalString(
                    text="Major redesign: added equity and income questions"
                )
            ]
        )
    ]
    errors = [finding for finding in doc.lint() if finding.severity == "error"]
    print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
    print(f"Validation errors: {len(doc.validate())}")  # -> Validation errors: 0
    doc.save("census-v2.xml")
    ```

10. **(O3)** **Batch validate** all three files from the command line:

    ```bash
    ddi validate census-v1.xml
    ddi validate census-v1.1.xml
    ddi validate census-v2.xml
    ```

11. **(O3)** **Write a bash script** that runs the full pipeline:

    ```bash
    #!/bin/bash
    # validate.sh: check the spec, then validate all census DDI files.

    echo "=== Checking the spec ==="
    ddi spec validate census.spec.yaml

    echo "=== Validating census files ==="
    for f in census-v*.xml; do
        echo "--- $f ---"
        ddi validate "$f"
        if [ $? -eq 0 ]; then
            echo "PASS"
        else
            echo "FAIL"
        fi
        echo ""
    done
    echo "=== Done ==="
    ```

    Make the script executable and run it:

    ```bash
    chmod +x validate.sh
    ./validate.sh
    ```

### Deliverables

- Your plan: one row per column, the three notes, and what the gate does
  with a missing age.
- `census-v1.xml`: version 1.0, valid, with the instrument and its gate.
- `census.spec.yaml`: the specification, passing `ddi spec validate`.
- `census-v1.1.xml`: version 1.1, valid, with rationale.
- `census-v2.xml`: version 2.0, valid, with rationale.
- `validate.sh`: bash script that checks the spec and validates all files.

??? success "Sample solution"
    One complete script, using
    [`census-data.csv`](census-data.csv){ download="census-data.csv" }. Run
    `validate.sh` from step 11 after it.

    ```python
    import csv
    from pathlib import Path
    from uuid import uuid4

    import ddi_l as ddi
    from ddi_l.models.base import InternationalString, VersionRationale
    from ddi_l.models.datacollection import (
        IfThenElse,
        Instrument,
        QuestionConstruct,
        Sequence,
    )
    from ddi_l.models.logicalproduct import Category, CodeItem
    from ddi_l.spec import equivalent, load_spec


    def add_codes(doc, code_list, labels):
        """Add one Category and one Code per label, numbered from 1."""
        for number, label in enumerate(labels, start=1):
            category = doc.add_item(Category, name=label, label=label)
            code_list.codes.append(
                CodeItem(
                    agency=code_list.agency,
                    identifier=str(uuid4()),
                    version=code_list.version,
                    value=str(number),
                    category=category.to_reference(),
                )
            )


    def rationale(text):
        return VersionRationale(descriptions=[InternationalString(text=text)])


    with open("census-data.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    columns = list(rows[0])

    doc = ddi.new_study(title="National Census 2024", agency="census.example.gov")
    # HouseholdID and PersonNumber are assigned, not asked.
    QUESTIONS = {
        "Province": "In which province or territory do you live?",
        "Age": "What was your age at your last birthday?",
        "Gender": "What is your gender?",
        "MaritalStatus": "What is your marital status?",
        "RelationshipToHead": "What is your relationship to Person 1?",
        "CountryOfBirth": "In which country were you born?",
        "Citizenship": "Of what country are you a citizen?",
        "MotherTongue": "What language did you first learn at home in childhood?",
        "HighestEducation": "What is the highest level of education you have completed?",
        "EmploymentType": "Last week, were you an employee, self-employed, or not working?",
        "Occupation": "What was your main kind of work last week?",
        "WeeklyHoursWorked": "How many hours did you work last week?",
        "AnnualIncome": "What was your total income last year?",
        "CommuteMode": "How did you usually get to work last week?",
        "HousingType": "What type of dwelling do you live in?",
        "Tenure": "Is this dwelling owned or rented by a member of this household?",
        "Rooms": "How many rooms are in this dwelling?",
        "YearBuilt": "In what year was this dwelling built?",
        "HouseholdSize": "How many people usually live here?",
        "InternetAccess": "Does this household have access to the internet at home?",
    }
    questions = {col: doc.add_question(text=text) for col, text in QUESTIONS.items()}
    variables = {
        col: doc.add_variable(name=col, question=questions.get(col)) for col in columns
    }

    for col in ("Province", "Gender", "MaritalStatus", "EmploymentType", "HousingType"):
        code_list = doc.add_code_list(name=f"{col}Codes")
        add_codes(doc, code_list, sorted({row[col] for row in rows}))
        variables[col].set_coded(code_list)

    doc.add_concept(name="Population")
    doc.add_concept(name="Labour")
    doc.add_universe(name="All persons usually resident in private dwellings")
    variables["Occupation"].set_property("classification", "ISCO-08")
    variables["AnnualIncome"].set_property("referencePeriod", "Calendar year 2023")

    # The flow: everyone answers the person section; the labour section has a gate
    AGE_GATE = "Age >= 15"


    def ask(col):
        return doc.add_item(
            QuestionConstruct, name=col, question_reference=questions[col].to_reference()
        )


    person = doc.add_item(
        Sequence,
        name="person",
        control_construct_references=[ask(c).to_reference() for c in ("Age", "Gender")],
    )
    labour = doc.add_item(
        Sequence,
        name="labour",
        control_construct_references=[
            ask(c).to_reference()
            for c in ("EmploymentType", "Occupation", "WeeklyHoursWorked")
        ],
    )
    gate = doc.add_item(IfThenElse, name="Working-age gate")
    gate.set_condition(AGE_GATE, description="Persons aged 15 and over")
    gate.then_construct_reference = labour.to_reference()
    main = doc.add_item(
        Sequence,
        name="Census flow",
        control_construct_references=[person.to_reference(), gate.to_reference()],
    )
    instrument = doc.add_item(Instrument, name="Census 2024 questionnaire")
    instrument.control_construct_reference = main.to_reference()

    # The spec of the same flow. A person with no age skips the labour section.
    Path("census.spec.yaml").write_text(
        """\
    spec: census-2024
    version: "1"
    modules:
      - id: person
        questions:
          - id: Age
            domain: {numeric: {min: 0, max: 120, decimals: 0}}
      - id: labour
        gate: Age >= 15
        questions:
          - id: EmploymentType
            domain: {text: {max_length: 40}}
          - id: Occupation
            domain: {text: {max_length: 60}}
          - id: WeeklyHoursWorked
            domain: {numeric: {min: 0, max: 168, decimals: 0}}
    """,
        encoding="utf-8",
    )
    spec = load_spec("census.spec.yaml")
    print(f"Gates agree: {equivalent(spec.module('labour').gate_text, AGE_GATE)}")
    # -> Gates agree: True

    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"v1: {len(doc.validate())} validation errors, {len(lint_errors)} lint errors")
    doc.save("census-v1.xml")

    # Version 1.1: one question added
    q_internet = doc.add_question(text="Do you have access to high-speed internet?")
    doc.add_variable(name="HighSpeedInternet", question=q_internet)
    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(rationale("Added internet access question"))
    study.version_responsibility = "Census Content Team"
    doc.save("census-v1.1.xml")

    # Version 2.0: five questions added, three retired with their variables
    for text in [
        "What is your primary language at home?",
        "Do you identify as Indigenous?",
        "What is your highest degree?",
        "Do you have a disability?",
        "What is your annual household income?",
    ]:
        doc.add_question(text=text)
    for col in ("Province", "MaritalStatus", "HousingType"):
        doc.remove(variables[col].identifier)
        doc.remove(questions[col].identifier)
    study.increment_major_version()
    study.version_rationales = [
        rationale("Major redesign: added equity and income questions")
    ]

    lint_errors = [f for f in doc.lint() if f.severity == "error"]
    print(f"v2: {len(doc.validate())} validation errors, {len(lint_errors)} lint errors")
    # -> v2: 0 validation errors, 0 lint errors
    doc.save("census-v2.xml")
    ```

---

## Present your project

**(O6)** Finish with a 5-minute presentation to your group. If you work alone, write
the same content as a one-page note. Keep to this order:

1. **The data and its readers** (30 seconds): what the data is, and who will
   read the metadata.
2. **The plan** (1 minute): show your plan table, and say which techniques
   your track needed.
3. **The proof** (1 minute): run `ddi validate` on your last file. Show one
   place in the XML where your technique is recorded, such as a
   `SourceVariableReference`, a `Comparison`, a `UserAttributePair` or an
   `IfThenElse`.
4. **Two design choices** (2 minutes): for each one, say what you chose, the
   option you rejected, and why.
5. **One thing you would change** next time (30 seconds).

Choices worth justifying:

- Coded or free text for a column such as Program or Occupation.
- Which columns get a question, and which are assigned or computed.
- A minor or a major version for your change.
- A custom field, or a field DDI already has.
- What a gate does when the answer it tests is missing (Track D).

---

## Capstone checklist (for all tracks)

Use this checklist to make sure your project is complete:

- [ ] A written plan covers every column (Track C: every file) and names your
  track's techniques.
- [ ] The document starts from a CSV or Excel file (Track C: from the DDI
  files you received).
- [ ] Every variable a respondent answered is linked to its question.
- [ ] Coded columns use code lists with categories.
- [ ] At least one concept and one universe are defined.
- [ ] Custom properties are set on at least 2 items.
- [ ] Questionnaire flow (Track D): an `Instrument` points at a main
  `Sequence` that holds an `IfThenElse` gate.
- [ ] Lineage (Tracks A and B): every derived variable lists its sources in
  `source_variable_references`.
- [ ] Linkage (Track B): the register is a second study, the key is tagged on
  both sides, and a `Comparison` maps the keys.
- [ ] Custom fields (Track C): every key comes from your catalog, and the
  audit counts the items that carry one.
- [ ] Specification (Track D): the spec passes `ddi spec validate`, and its
  gate matches the instrument's.
- [ ] The version was incremented at least once, with a rationale and a
  responsibility.
- [ ] Document passes `doc.validate()` and `doc.lint()` with no errors.
- [ ] Every saved file passes `ddi validate`.
- [ ] Two design choices are ready to present.

---

## Self-assessment rubric

Use this table to score your own work, or a partner's. The rubric measures
the six objectives of this module on your track's data. The maximum score is
100 points.

| Criteria | Objective | Modules | Points |
| --- | --- | --- | ---: |
| A plan, written before the code, covers every column and names your track's techniques | O1 | 8 | 10 |
| Every asked column is a variable linked to its question; assigned and computed columns have none | O2 | 4, 8 | 10 |
| At least one concept and one universe | O2 | 5 | 5 |
| Coded columns use code lists with categories | O2 | 9 | 10 |
| Custom properties on at least 2 items | O2 | 13 | 5 |
| No errors from `doc.validate()`, `doc.lint()` or `ddi validate` on any saved file | O3 | 3, 7, 13 | 15 |
| Your track's techniques (next table) | O4 | 10, 11, 12, 14, 16 | 20 |
| A version change with a rationale and a responsibility, each version in its own file | O5 | 15 | 10 |
| A 5-minute presentation that justifies two design choices against the options rejected | O6 | All | 15 |

**Track techniques (20 points).** Score only the rows for your track. Each
track's points add up to 20. Give half the points when a technique is there
but incomplete, for example a derived variable that lists one of its two
sources.

| Technique | Module | Full points when | A | B | C | D |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Questionnaire flow | 10 | An `Instrument` points at a main `Sequence`, and an `IfThenElse` gate routes at least one section | - | - | - | 10 |
| Lineage | 11 | Every derived variable lists all its source variables in `source_variable_references` | 20 | 10 | - | - |
| Linkage | 12 | Both sources are studies in one document, the key is tagged on both sides, a `Comparison` maps the keys, and the method is recorded | - | 10 | - | - |
| Custom fields | 14 | Every key comes from a written catalog with one namespace, and an audit counts the items that carry them | - | - | 20 | - |
| Specification | 16 | The spec passes `ddi spec validate`, its gates match the instrument's (`equivalent()`), and the plan says what each gate does with a missing answer | - | - | - | 10 |

**Scoring guide:**

- **90-100:** Excellent. You can take data from a file to a valid, versioned
  DDI document, record what your track needs, and explain your choices. The
  rubric checks these skills on one dataset; it does not test every part of
  `ddi-l`.
- **70-89:** Good. For each row where you lost points, review the modules
  listed beside it.
- **50-69:** Needs practice. Redo the exercises of the modules beside your
  weakest rows, and try again.
- **Below 50:** Start with Track A and work through the steps slowly.

---

## Reflection questions

These are open-ended questions. There are no right or wrong answers. Write
your thoughts in a notebook or discuss with your group.

1. **What was the hardest part of building your DDI document? What would you
   do differently next time?**

2. **How would you explain DDI to a colleague who has never heard of it?**
   Try to describe it in two or three simple sentences.

3. **Which part of the `ddi-l` API did you use the most? Why?** Think about
   which methods you called again and again, and what that tells you about your
   workflow.

---

## Check yourself

- [ ] I can write a plan that gives every column of my dataset its question (or the reason it has none), its type and its code list, and names the techniques my track needs. (O1)
- [ ] I can build the DDI document from the data, with each asked column linked to its question, code lists with categories, concepts and a universe. (O2)
- [ ] I can get no errors from `doc.validate()`, `doc.lint()` and `ddi validate` on every file I save. (O3)
- [ ] I can record the flow, lineage, linkage, custom fields or specification my track needs, and show where it is in the XML. (O4)
- [ ] I can version a change with a rationale and a responsibility, and keep each version in its own file. (O5)
- [ ] I can present my project in 5 minutes and justify two design choices against the options I rejected. (O6)

---

!!! tip "Instructor notes"
    - **Let learners choose their track.** Self-selection increases engagement.
      If the group is mixed (students, researchers, archivists, NSO staff),
      encourage small groups by role.
    - **Plan first.** Ask to see each plan before learners write code. Ten
      minutes on the plan saves half an hour of rework.
    - **Time management.** Track A takes about 60 minutes. Tracks B and D can
      take 90 minutes or more, because they record two techniques each. Set
      expectations at the start and let faster learners help slower ones.
    - **Peer review.** After learners finish, pair them up to review each
      other's deliverables. Each reviewer should run `ddi validate` on the
      other person's files and score them with the rubric.
    - **Show-and-tell.** End with the presentations: 2-3 learners share their
      screen and follow the five parts of "Present your project". Focus on
      the design choices, not just what they built.
    - **Common issues:** Learners often forget to link variables to questions,
      skip the version rationale, or append a second rationale to a study that
      already has one (a version holds one rationale, and the file fails
      validation). The checklist helps catch these gaps.
    - **Extension:** Advanced learners can try a second track or combine
      elements from two tracks (for example, Track B's linkage with Track D's
      bash scripting).
    - **Celebration.** This is the final module. Acknowledge the effort
      learners have put in. Hand out certificates or badges if your
      organization supports them.
