---
description: >-
  Module 8 of the ddi-l course: turn a CSV, Excel or SQL table into a
  documented DDI study, in one or two languages.
---

# Module 8: From a CSV or Excel table to DDI

!!! info "What you will learn"
    - Read column names from a CSV file using Python.
    - Create one DDI variable for each column automatically.
    - Do the same from an Excel file using pandas.
    - (Optional) Read column names from a SQL database.
    - Enrich the metadata with concepts, universes, and code lists.
    - Write a complete CSV-to-DDI script.

**Prerequisites:** Module 7.

**Time:** 45 min self-paced / 60 min instructor-led.

---

## Why this module matters

This is the key practical module.
Most researchers already have data in a CSV or Excel file.
They need DDI metadata that describes that data.

This module teaches the real-world workflow:
start from data you already have and produce a DDI document.

---

## 1. The workflow overview

Your data lives in a CSV or Excel file.
You want DDI metadata (an XML file) that describes it.

Here is the plan:

1. Python reads the **column names** from your data file.
2. For each column, it creates a **variable** in a DDI document.
3. You save the DDI document as XML.

The DDI file does not contain the data itself.
It contains **documentation about the data**: variable names, questions, concepts, and more.

## 2. Step 1: Read column names from a CSV

A **CSV file** (Comma-Separated Values) is a plain-text file where each line is a row of data.
The first line usually holds the column names.

Python has a built-in module called `csv` that can read these files.
We use `csv.DictReader` to get the column names.

```python
import csv

with open("survey_sample.csv") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames

print(columns)
```

**Expected output:**

```text
['respondent_id', 'age', 'gender', 'income', 'education_level']
```

The variable `columns` is now a list of strings.
Each string is a column name from your CSV file.

!!! note "Sample file"
    Download the sample CSV and save it next to your script, or create your
    own file with these columns:
    `respondent_id`, `age`, `gender`, `income`, `education_level`.

    [:material-download: Download `survey_sample.csv`](survey_sample.csv){ .md-button download="survey_sample.csv" }

## 3. Step 2: Create one variable per column

Now we use `ddi-l` to build a DDI document.
We loop over the column names and create one variable for each.

```python
import csv
import ddi_l as ddi

# Read columns from CSV
with open("survey_sample.csv") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames

# The question each column records, worded the way respondents saw it
QUESTIONS = {
    "age": "How old are you?",
    "gender": "What is your gender?",
    "income": "What was your total income last year, before taxes?",
    "education_level": "What is the highest level of education you have completed?",
}

# Build the DDI document
doc = ddi.new_study(title="Household Survey", agency="research.org")

for col in columns:
    wording = QUESTIONS.get(col)
    # A column nobody was asked about, such as respondent_id, gets no question
    q = doc.add_question(text=wording) if wording else None
    doc.add_variable(name=col, question=q)

doc.save("household-survey.xml")

print(f"Variables: {len(doc.variables)}")
```

**Expected output:**

```text
Variables: 5
```

What happened:

- We read 5 column names from the CSV.
- For each column, we added a variable.
- The four columns that record an answer also got a question, worded the way
  respondents saw it. `respondent_id` is assigned by the survey team, not
  asked, so its variable has no question.
- We saved everything to an XML file.

!!! tip "Why a lookup table?"
    A column name such as `education_level` is shorthand, not a question.
    Building the text from it (`f"What is the respondent's {col}?"`) produces
    "What is the respondent's education_level?", which nobody was ever asked.
    Copy the wording from your questionnaire into `QUESTIONS` instead, so the
    metadata records what respondents actually answered.

## 4. Step 3: Do the same from Excel

If your data is in an Excel file (`.xlsx`), you can use the **pandas** library.
Pandas is a popular Python tool for working with tables of data.

<!-- docs-test: skip -- needs pandas and a reader-supplied survey.xlsx -->
```python
import pandas as pd

df = pd.read_excel("survey.xlsx")
columns = list(df.columns)

print(columns)
```

The variable `df` is a **DataFrame**: a table in memory.
The `columns` property gives you the column names, just like `csv.DictReader`.

After this step, the rest of the code is the same as Step 2.
Loop over `columns`, create variables, and save.

!!! note "Installing pandas"
    If you do not have pandas, install it with: `pip install pandas openpyxl`

## 5. Step 4 (optional): Read from a SQL database

This section is for advanced users who store data in a SQL database.
You can skip it if you only use CSV or Excel files.

**SQL** (Structured Query Language) is a language for working with databases.
We use Python's built-in `sqlite3` module to connect to a SQLite database.

<!-- docs-test: skip -- needs a reader-supplied survey.db -->
```python
import sqlite3

conn = sqlite3.connect("survey.db")
cursor = conn.execute("SELECT * FROM survey LIMIT 0")
columns = [desc[0] for desc in cursor.description]

print(columns)
```

The trick is `LIMIT 0`.
It reads zero rows but still gives us the column names from `cursor.description`.

After this, the rest is the same: loop over `columns` and create variables.

## 6. Enriching the metadata

Importing column names is a good start, but raw column names are not enough.
Good metadata needs more detail.

After importing, you should add:

- **Concepts** to group related variables (see Module 5).
- **Universes** to say who is being studied.
- **Code lists** to define allowed answers (see Module 9).

```python
# Add concepts
demo = doc.add_concept(name="Demographics")
econ = doc.add_concept(name="Economics")

# Add a universe
doc.add_universe(name="Canadian households, 2024")

# Link variables to concepts (you would do this for each variable)
```

This enrichment turns a bare list of column names into useful, shareable metadata.

## 7. Documenting in more than one language

Many surveys serve bilingual or multilingual populations. For example, a
Canadian survey might need metadata in both English and French. DDI stores
multiple language versions inside the same document.

In Module 3 you learned that every `add_*` method accepts a `lang=` argument.
Here is how to build a fully bilingual DDI document from a CSV file:

```python
import csv
import ddi_l as ddi
from ddi_l.models.base import InternationalString

with open("survey_sample.csv") as f:
    columns = csv.DictReader(f).fieldnames

doc = ddi.new_study(title="Household Survey", agency="statcan.gc.ca")

# English and French wording for each question
QUESTIONS = {
    "age": ("How old are you?", "Quel âge avez-vous ?"),
    "gender": ("What is your gender?", "Quel est votre genre ?"),
    "income": (
        "What was your total income last year, before taxes?",
        "Quel a été votre revenu total l'an dernier, avant impôts ?",
    ),
    "education_level": (
        "What is the highest level of education you have completed?",
        "Quel est le plus haut niveau de scolarité que vous avez atteint ?",
    ),
}

for col in columns:
    q = None
    if col in QUESTIONS:
        english, french = QUESTIONS[col]
        # Create the question in English (default)...
        q = doc.add_question(text=english)
        # ...and append the French wording to the same question
        q.question_texts.append(InternationalString(text=french, lang="fr"))

    # Create the variable with an English name
    v = doc.add_variable(name=col, question=q)

    # Append the French variable name
    v.names.append(InternationalString(text=col, lang="fr", child_tag="String"))

# Bilingual concepts
demo = doc.add_concept(name="Demographics")
demo.names.append(
    InternationalString(text="Démographie", lang="fr", child_tag="String")
)

econ = doc.add_concept(name="Economics")
econ.names.append(InternationalString(text="Économie", lang="fr", child_tag="String"))

# Bilingual universe
u = doc.add_universe(name="Canadian households, 2024")
u.names.append(
    InternationalString(text="Ménages canadiens, 2024", lang="fr", child_tag="String")
)

doc.save("household-survey-bilingual.xml")
print(f"Variables: {len(doc.variables)}")
```

**Expected output:**

```text
Variables: 5
```

Open the saved XML file. You will see both `xml:lang="en"` and
`xml:lang="fr"` entries for each question, variable, concept, and universe.

The pattern is the same for every item type:

1. Create the item with `add_*()` (uses `lang="en"` by default).
2. Append an `InternationalString` with `lang="fr"` to the item's text list
   (`question_texts` for questions, `names` for everything else).

You can add as many languages as you need. Just append one
`InternationalString` per language.

## 8. A complete script

Here is the full CSV-to-DDI pipeline in one file.
Copy this and change it to match your own data.

```python
import csv
import ddi_l as ddi

# Step 1: Read column names
with open("survey_sample.csv") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames

# The question each column records, worded the way respondents saw it
QUESTIONS = {
    "age": "How old are you?",
    "gender": "What is your gender?",
    "income": "What was your total income last year, before taxes?",
    "education_level": "What is the highest level of education you have completed?",
}

# Step 2: Build the DDI document
doc = ddi.new_study(title="Household Survey", agency="research.org")

for col in columns:
    wording = QUESTIONS.get(col)
    # A column nobody was asked about, such as respondent_id, gets no question
    q = doc.add_question(text=wording) if wording else None
    doc.add_variable(name=col, question=q)

# Step 3: Enrich
doc.add_concept(name="Demographics")
doc.add_concept(name="Economics")
doc.add_universe(name="Canadian households, 2024")

# Step 4: Save
doc.save("household-survey.xml")

# Step 5: Verify
print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
print(f"Concepts: {len(doc.concepts)}")
print(f"Universes: {len(doc.universes)}")
```

**Expected output:**

```text
Questions: 4
Variables: 5
Concepts: 2
Universes: 1
```

---

!!! example "Scenario"
    A researcher has a CSV file called `survey_sample.csv` from a household survey.
    It has five columns: `respondent_id`, `age`, `gender`, `income`, `education_level`.
    They need to create DDI metadata for this dataset.
    Your job is to write a Python script that reads the CSV, builds the DDI document,
    enriches it with concepts and a universe, and saves it as XML.

---

## Exercises

1. [Download](survey_sample.csv){ download="survey_sample.csv" } or create `survey_sample.csv` with these 5 columns: `respondent_id`, `age`, `gender`, `income`, `education_level`. Write a script that reads the CSV, creates a DDI document with one variable per column, and saves it. Print the count.

    **Expected output:**

    ```text
    Variables: 5
    ```

    ??? success "Answer"
        ```python
        import csv
        import ddi_l as ddi

        with open("survey_sample.csv") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames

        # The question each column records, worded the way respondents saw it
        QUESTIONS = {
            "age": "How old are you?",
            "gender": "What is your gender?",
            "income": "What was your total income last year, before taxes?",
            "education_level": "What is the highest level of education you have completed?",
        }

        doc = ddi.new_study(title="Household Survey", agency="research.org")
        for col in columns:
            wording = QUESTIONS.get(col)
            # A column nobody was asked about, such as respondent_id, gets no question
            q = doc.add_question(text=wording) if wording else None
            doc.add_variable(name=col, question=q)

        doc.save("household-survey.xml")
        print(f"Variables: {len(doc.variables)}")  # -> Variables: 5
        ```

2. (If pandas is installed) Do the same from an Excel file. Use `pd.read_excel()` to get the columns, then create variables the same way.

    ??? success "Answer"
        Save the sample CSV as `survey_sample.xlsx` in Excel first, or point
        `read_excel()` at a workbook of your own.

        <!-- docs-test: skip -- needs pandas, openpyxl and an Excel workbook -->
        ```python
        import pandas as pd
        import ddi_l as ddi

        df = pd.read_excel("survey_sample.xlsx")
        doc = ddi.new_study(title="Household Survey", agency="research.org")
        for col in df.columns:
            doc.add_variable(name=col)
        doc.save("household-survey-excel.xml")
        print(f"Variables: {len(doc.variables)}")
        ```

3. Enrich your document: add a concept for each variable and a universe. Validate the document and save it.

    ??? success "Answer"
        Continuing from Exercise 1:

        ```python
        doc.add_concept(name="Respondent identification")
        doc.add_concept(name="Age")
        doc.add_concept(name="Gender")
        doc.add_concept(name="Income")
        doc.add_concept(name="Educational attainment")
        doc.add_universe(name="Canadian households")

        issues = doc.validate()
        if issues:
            for issue in issues:
                print(issue.message)
        else:
            print("Document is valid!")
        doc.save("household-survey-enriched.xml")
        ```

        To link a variable to its concept, pass `concept=` when you add the variable,
        as in Section 6.

4. (Bilingual) Add French translations to at least 2 questions and 1 concept in your document. Save the file and open the XML to verify both languages appear.

    ??? success "Answer"
        ```python
        from ddi_l.models.base import InternationalString

        # The first question asks for the respondent's age
        q = doc.questions[0]
        q.question_texts.append(InternationalString(text="Quel âge avez-vous ?", lang="fr"))

        # The second asks for their gender
        doc.questions[1].question_texts.append(
            InternationalString(text="Quel est votre genre ?", lang="fr")
        )

        # And one concept
        doc.concepts[0].names.append(
            InternationalString(text="Identification du répondant", lang="fr")
        )
        doc.save("household-survey-bilingual.xml")
        ```

        Open the XML and look for `xml:lang="fr"` next to the English text.

---

## Quiz

???+ question "Q1: What does csv.DictReader give you?"
    **A.** The entire CSV file as one big string.

    **B.** A reader object whose `fieldnames` property lists the column
    names.

    **C.** A list of numbers.

    **D.** An XML document.

    ??? success "Answer"
        **B.** `csv.DictReader` reads a CSV file. Its `fieldnames`
        property returns the column names from the first row.

???+ question "Q2: How do you get column names from a pandas DataFrame?"
    **A.** `df.rows`

    **B.** `df.fieldnames`

    **C.** `df.columns`

    **D.** `df.headers`

    ??? success "Answer"
        **C.** Use `df.columns` to get the column names from a pandas
        DataFrame. Wrap it in `list()` to get a plain list.

???+ question "Q3: What does the script produce?"
    **A.** A CSV file with new data.

    **B.** A DDI XML file with metadata about the data.

    **C.** A copy of the original CSV.

    **D.** A SQL database.

    ??? success "Answer"
        **B.** The script produces a DDI XML file. This file describes
        the data (variable names, questions, concepts) but does not
        contain the data itself.

???+ question "Q4: Why should you add concepts after importing columns?"
    **A.** Concepts delete the columns.

    **B.** Python requires it.

    **C.** Concepts group variables and make the metadata more useful
    and organized.

    **D.** The file will not save without concepts.

    ??? success "Answer"
        **C.** Concepts group related variables together. Without them,
        you just have a flat list of names. Concepts add meaning and
        structure.

---

!!! tip "Instructor notes"
    - This is the "aha" module for researchers and NSO staff. Many learners will recognize their own workflow here.
    - **Key message:** The CSV is the **data**. The DDI XML is **documentation about the data**. They are two separate files with two separate purposes.
    - Walk through the complete script line by line. Let learners type along.
    - The SQL section (Step 4) is optional. Skip it for non-technical audiences. It is there for database-savvy participants who ask "what about SQL?"
    - If time allows, let learners try with their own CSV files. Real data makes the exercise more meaningful.
    - Common mistake: learners confuse the CSV file with the XML output. Remind them that `doc.save()` writes metadata, not data.

---

**See also:** [Download the sample CSV file](survey_sample.csv){ download="survey_sample.csv" } (`survey_sample.csv`).
