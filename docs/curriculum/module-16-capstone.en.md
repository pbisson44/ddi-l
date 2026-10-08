# Module 16: Real-World Capstone Projects

!!! info "What you will learn"
    - Combine everything from Modules 1-15 into a complete project.
    - Build a DDI document from a CSV or Excel file.
    - Add variables, questions, concepts, universes, and code lists.
    - Set custom properties on items.
    - Version your document and record a rationale.
    - Validate and save the final XML.

**Prerequisites:** All previous modules (1-15).

**Time:** 60-90 min self-paced / 90 min instructor-led.

---

## Introduction

You have now learned all the tools. You know how to create DDI
documents, add metadata, validate files, manage versions, and use the command
line. Now it is time to put everything together in a real project.

Choose the **track** that matches your role. Each track walks you through a
complete workflow: start from a data file, build DDI metadata, version it,
validate it, and save the final output.

If you are not sure which track to pick, try **Track A** (University Student).
It is the simplest starting point.

---

## Track A: University Student: Document Your Thesis Dataset

!!! example "Scenario"
    You just finished your thesis on student stress. Your dataset has 10
    columns. You need to create a DDI document so your university's research
    repository can catalog your data.

### Steps

1. **Start from a CSV file** with at least 10 columns. Download the sample
   thesis dataset (40 students, 12 columns) or use your own.

    [:material-download: Download `thesis-data.csv`](thesis-data.csv){ .md-button download="thesis-data.csv" }

2. **Create a DDI study:**

    ```python
    import ddi_l as ddi

    doc = ddi.new_study(
        title="Student Stress Survey 2024",
        agency="university.example.org",
    )
    ```

3. **Add variables** from your CSV columns. Create one variable for each
   column. Link each variable to the question it came from; an identifier
   such as a student ID is assigned, not asked, and needs no question.

    ```python
    q1 = doc.add_question(text="How many hours do you study per day?")
    v1 = doc.add_variable(name="StudyHours", question=q1)
    # Repeat for each column...
    ```

4. **Add 3 concepts and 1 universe:**

    ```python
    c1 = doc.add_concept(name="Academic Workload")
    c2 = doc.add_concept(name="Mental Health")
    c3 = doc.add_concept(name="Demographics")
    u1 = doc.add_universe(name="Undergraduate students aged 18-25")
    ```

5. **Set custom properties** on at least 2 items. A custom property is extra
   metadata you define yourself, like a data source or collection date.

    ```python
    v1.set_property("dataSource", "Online survey via Qualtrics")
    v1.set_property("collectionDate", "2024-03-15")
    ```

6. **Save as version 1.0:**

    ```python
    doc.save("thesis-v1.xml")
    ```

7. **Update the document.** Add a new analysis variable (for example,
   "StressIndex" that combines several columns). Increment the version to
   1.1 and add a rationale.

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    q_new = doc.add_question(text="Computed: overall stress index")
    v_new = doc.add_variable(name="StressIndex", question=q_new)

    study = doc.study_unit
    study.increment_minor_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added computed stress index variable")]
        )
    )
    study.version_responsibility = "Thesis Author"
    ```

8. **Validate and save as version 1.1:**

    ```python
    errors = doc.validate()
    if not errors:
        doc.save("thesis-v1.1.xml")
        print("Saved thesis-v1.1.xml")
    else:
        print("Errors:", errors)
    ```

### Deliverables

- `thesis-v1.xml`: valid DDI document with 10+ variables.
- `thesis-v1.1.xml`: updated version with the new variable and a rationale.

---

## Track B: Researcher: Package a Health Survey for Publication

!!! example "Scenario"
    You lead a multi-country health study. Your Excel file has 15 columns of
    survey data. You need to package the metadata for an open data repository.

### Steps

1. **Start from a data file** with at least 15 columns. Download the sample
   health survey (40 respondents, 15 columns) or use your own, and read its
   column names:

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
    instead (see [Module 6](module-06-csv-to-ddi.md)):

    <!-- docs-test: skip -- needs pandas and a workbook the reader supplies -->
    ```python
    import pandas as pd

    columns = list(pd.read_excel("health-survey.xlsx").columns)
    ```

2. **Auto-generate variables** from the columns:

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
    for col in columns:
        q = doc.add_question(text=QUESTIONS[col]) if col in QUESTIONS else None
        v = doc.add_variable(name=col, question=q)
    ```

3. **Add 4 concepts:**

    ```python
    doc.add_concept(name="Physical Health")
    doc.add_concept(name="Mental Health")
    doc.add_concept(name="Access to Healthcare")
    doc.add_concept(name="Demographics")
    ```

4. **Add 2 code lists** auto-generated from column unique values. A
   **code list** is a set of allowed answers (like "Yes", "No", "Unsure").

    ```python
    cl1 = doc.add_code_list(name="SmokingStatus")
    cl2 = doc.add_code_list(name="ExerciseFrequency")
    ```

5. **Validate the document:**

    ```python
    errors = doc.validate()
    print("Valid" if not errors else errors)
    ```

6. **Save as version 1.0:**

    ```python
    doc.save("health-survey-v1.xml")
    ```

7. **Export to JSON** using the command line:

    ```bash
    ddi to-json health-survey-v1.xml --indent 2 > health-survey-v1.json
    ```

8. **Update to version 1.1** with a rationale. Add a new variable or fix a
   label.

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    doc.add_question(text="How often do you visit a dentist?")
    study = doc.study_unit
    study.increment_minor_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added dental visit frequency question")]
        )
    )
    doc.save("health-survey-v1.1.xml")
    ```

### Deliverables

- `health-survey-v1.xml`: valid DDI document.
- `health-survey-v1.json`: JSON export of the document.
- `health-survey-v1.1.xml`: updated version with rationale.

---

## Track C: Archivist: Enrich and Version Existing DDI Files

!!! example "Scenario"
    You manage a data collection at a national library. You receive 3 DDI files
    from different research teams. Some files are missing metadata. You need to
    check each file, add what is missing, and create new versions.

### Steps

1. **Prepare 3 DDI files.** Use files from earlier modules, or create 3 small
   studies now:

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

2. **For each file, check completeness.** Open the file and list what it
   contains:

    ```python
    doc = ddi.open_ddi("study-1.xml")
    print(f"Questions:  {len(doc.questions)}")
    print(f"Variables:  {len(doc.variables)}")
    print(f"Concepts:   {len(doc.concepts)}")
    print(f"Universes:  {len(doc.universes)}")
    print(f"Code lists: {len(doc.code_lists)}")
    ```

3. **Add missing metadata.** If a file has no concepts, add one. If it has no
   universe, add one. If variables have no linked questions, add questions and
   re-create the variables.

    ```python
    doc.add_concept(name="Social Sciences")
    doc.add_universe(name="General population")
    cl = doc.add_code_list(name="YesNo")
    ```

4. **Increment the version with a rationale:**

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    study = doc.study_unit
    study.increment_minor_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(
                    text="Enriched metadata: added concept, universe, and code list"
                )
            ]
        )
    )
    study.version_responsibility = "Archive Metadata Team"
    ```

5. **Validate and save:**

    ```python
    errors = doc.validate()
    if not errors:
        doc.save("study-1-enriched.xml")
    ```

6. **Repeat for all 3 files.**

### Deliverables

- 3 updated XML files (`study-1-enriched.xml`, `study-2-enriched.xml`,
  `study-3-enriched.xml`), all valid, each with a version rationale.

---

## Track D: NSO Staff: Build a Census Instrument

!!! example "Scenario"
    You work at a national statistics office. Your census team has a large CSV
    file with 20+ columns. You need to build a complete DDI document, create
    code lists from the data, manage multiple versions, and automate validation
    with a bash script.

### Steps

1. **Start from a large CSV** with 20+ columns. Download the sample census
   extract (20 households, 22 columns, including the five categorical columns
   used in step 3) or use your own.

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

2. **Create 20+ variables** from the CSV columns:

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
    for col in columns:
        q = doc.add_question(text=QUESTIONS[col]) if col in QUESTIONS else None
        v = doc.add_variable(name=col, question=q)
    ```

3. **Build 5 code lists** auto-generated from column unique values:

    ```python
    categorical_cols = [
        "Province",
        "Gender",
        "MaritalStatus",
        "EmploymentType",
        "HousingType",
    ]
    for col in categorical_cols:
        cl = doc.add_code_list(name=f"{col}Codes")
    ```

4. **Set custom properties** for classification codes on at least 2 items:

    ```python
    v = doc.variables[0]
    v.set_property("classificationCode", "NAICS-2022")
    v.set_property("statisticalProgram", "Census of Population")
    ```

5. **Save as version 1.0:**

    ```python
    doc.save("census-v1.xml")
    ```

6. **Update to version 1.1**: add a new question and variable:

    ```python
    from ddi_l.models.base import VersionRationale, InternationalString

    doc.add_question(text="Do you have access to high-speed internet?")
    study = doc.study_unit
    study.increment_minor_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[InternationalString(text="Added internet access question")]
        )
    )
    doc.save("census-v1.1.xml")
    ```

7. **Update to version 2.0**: major redesign (add 5 new questions, retire
   3 old ones). Retiring a question also retires the variables that recorded
   its answers; otherwise they would keep pointing at a question that is no
   longer in the file (see [Module 13](module-13-update-and-version.md)):

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
    for q in doc.questions[:3]:
        for v in doc.variables:
            if any(ref.identifier == q.identifier for ref in v.question_references):
                doc.remove(v.identifier)
        doc.remove(q.identifier)

    study.increment_major_version()
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(
                    text="Major redesign: added equity and income questions"
                )
            ]
        )
    )
    errors = [finding for finding in doc.lint() if finding.severity == "error"]
    print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
    doc.save("census-v2.xml")
    ```

8. **Batch validate** all three files from the command line:

    ```bash
    ddi validate census-v1.xml
    ddi validate census-v1.1.xml
    ddi validate census-v2.xml
    ```

9. **Write a bash script** that runs the full pipeline:

    ```bash
    #!/bin/bash
    # validate.sh: validate all census DDI files.

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

- `census-v1.xml`: version 1.0, valid.
- `census-v1.1.xml`: version 1.1, valid, with rationale.
- `census-v2.xml`: version 2.0, valid, with rationale.
- `validate.sh`: bash script that validates all files.

---

## Capstone checklist (for all tracks)

Use this checklist to make sure your project is complete:

- [ ] Document starts from a CSV or Excel file.
- [ ] Every variable a respondent answered is linked to its question.
- [ ] At least one concept and one universe defined.
- [ ] Custom properties set on at least 2 items.
- [ ] Version incremented at least once with a rationale.
- [ ] Document passes `doc.validate()` with no errors.
- [ ] Final XML saved to disk.

---

## Self-assessment rubric

Use this table to score your own work. The maximum score is 100 points (plus
10 bonus points).

| Criteria                             | Points |
| ------------------------------------ | -----: |
| Valid XML output                     |     20 |
| Variables linked to questions        |     15 |
| Concepts and universes present       |     15 |
| Code lists with categories           |     15 |
| Custom properties used               |     10 |
| Version management with rationale    |     15 |
| Bonus: CLI validation or JSON export |     10 |

**Scoring guide:**

- **90-110:** Excellent. You have mastered `ddi-l`.
- **70-89:** Good. Review the areas where you lost points.
- **50-69:** Needs practice. Go back to the relevant modules and try again.
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

!!! tip "Instructor notes"
    - **Let learners choose their track.** Self-selection increases engagement.
      If the group is mixed (students, researchers, archivists, NSO staff),
      encourage small groups by role.
    - **Time management.** Track A takes about 60 minutes. Track D can take 90
      minutes or more. Set expectations at the start and let faster learners
      help slower ones.
    - **Peer review.** After learners finish, pair them up to review each
      other's deliverables. Each reviewer should run `ddi validate` on the
      other person's files and check the rubric.
    - **Show-and-tell.** End with a 5-minute show-and-tell where 2-3 learners
      share their screen and walk through their project. Focus on what they
      learned, not just what they built.
    - **Common issues:** Learners often forget to link variables to questions,
      or skip the version rationale. The checklist helps catch these gaps.
    - **Extension:** Advanced learners can try a second track or combine
      elements from two tracks (for example, Track B's auto-generation with
      Track D's bash scripting).
    - **Celebration.** This is the final module. Acknowledge the effort
      learners have put in. Hand out certificates or badges if your
      organization supports them.
