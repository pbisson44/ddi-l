---
description: >-
  Module 8 of the ddi-l course: turn a CSV, Excel or SQL table into a
  documented DDI study, in one or two languages.
---

# Module 8: From a CSV or Excel table to DDI

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Write a script that reads the header of a CSV file and creates one DDI variable per column, with question text taken from a lookup table.
    - **O2.** Adapt the script to read the column names from an Excel sheet with pandas.
    - **O3.** Add concepts and a universe to the generated document and link each measured variable to its concept.
    - **O4.** Add question text in a second language and confirm that both wordings appear in the saved XML.
    - **O5.** Validate the generated document with `doc.validate()` and fix any error it reports before saving.

**Prerequisites:** [Module 7](module-07-cli-validation.en.md).

**Time:** 45 min self-paced / 60 min instructor-led.

**New in this module:** `csv.DictReader`, `reader.fieldnames`, `pd.read_excel()`, `df.columns`, `question_texts.append()`, `issue.message`, `issue.xpath`.

---

## 1. The workflow overview

This is the key practical module.
Most researchers already have data in a CSV or Excel file.
They need DDI metadata that describes that data.
This module teaches the real-world workflow:
start from data you already have and produce a DDI document.

!!! tip "Already documenting in spreadsheets?"
    This module builds the DDI in code, one column at a time. If your study's
    concepts, questions, questionnaire, code lists, variables and data files
    are already in spreadsheets, lay them out as in [Load DDI from spreadsheets](../spreadsheet-import.en.md) and load
    them all in one step, in any number of languages. The
    [spreadsheet templates](../spreadsheet-templates.en.md) are a starting point.

Your data lives in a CSV or Excel file.
You want DDI metadata (an XML file) that describes it.

Here is the plan:

1. Python reads the **column names** from your data file.
2. For each column, it creates a **variable** in a DDI document.
3. You link the variables to concepts, add a second language, and validate.
4. You save the DDI document as XML.

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

## 4. Step 3: Read the columns from Excel

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
`pd.read_excel()` reads the first sheet of the workbook; pass
`sheet_name="Data"` to read the sheet called "Data" instead.

After this step, the rest of the code is the same as Step 2.
Loop over `columns`, create variables, and save.

!!! note "Installing pandas"
    If you do not have pandas, install it with: `pip install pandas openpyxl`

## 5. Link variables to concepts and a universe

Importing column names is a good start, but raw column names are not enough.
Good metadata needs more detail. After importing, add:

- **Concepts** to group related variables (see [Module 5](module-05-concepts-universes.en.md)).
- A **universe** to say who is being studied.

To link each variable to its concept inside the loop, create the concepts
first and keep a second lookup table, `CONCEPTS`, that gives the concept for
each measured column:

```python
doc = ddi.new_study(title="Household Survey", agency="research.org")

# Concepts and the universe come first, so the loop can link to them
demo = doc.add_concept(name="Demographics")
econ = doc.add_concept(name="Economics")
doc.add_universe(name="Canadian households, 2024")

# The concept each measured column belongs to
CONCEPTS = {
    "age": demo,
    "gender": demo,
    "income": econ,
    "education_level": demo,
}

for col in columns:
    wording = QUESTIONS.get(col)
    q = doc.add_question(text=wording) if wording else None
    # respondent_id measures nothing, so CONCEPTS.get() returns None: no link
    doc.add_variable(name=col, question=q, concept=CONCEPTS.get(col))

linked = [v for v in doc.variables if v.concept_references]
print(f"Linked variables: {len(linked)}")  # -> Linked variables: 4
```

This turns a bare list of column names into useful, shareable metadata.
Code lists, which record the allowed answers to each question, are the
subject of [Module 9](module-09-code-lists.en.md).

## 6. Documenting in more than one language

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

doc = ddi.new_study(title="Household Survey", agency="research.org")

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

The pattern is the same for every item type:

1. Create the item with `add_*()` (uses `lang="en"` by default).
2. Append an `InternationalString` with `lang="fr"` to the item's text list
   (`question_texts` for questions, `names` for everything else).

You can add as many languages as you need. Just append one
`InternationalString` per language.

To confirm that both languages were saved, open the XML file in a text editor:
you will see both `xml:lang="en"` and `xml:lang="fr"` entries for each
question, variable, concept, and universe. Or let Python check: read the saved
file as text and look for both wordings of a question.

```python
from pathlib import Path

saved = Path("household-survey-bilingual.xml").read_text(encoding="utf-8")
print("How old are you?" in saved, "Quel âge avez-vous ?" in saved)  # -> True True
```

## 7. Validate before you save

A script that builds metadata from a file can build something invalid without
noticing: a typo in a lookup table is enough. Check the document with
`doc.validate()` before you save it. It returns a list of **issues**, empty
when the document follows the DDI schema. Each issue has:

- `issue.message`: the rule that is broken.
- `issue.xpath`: where, as a path from the root of the document, like the path
  after `at` in Module 7.

```python
issues = doc.validate()
if issues:
    for issue in issues:
        print(issue.message)
        print(f"  at {issue.xpath}")
else:
    doc.save("household-survey-bilingual.xml")
    print("Document is valid. Saved.")  # -> Document is valid. Saved.
```

Only save when the list is empty; otherwise, read each message, fix the
script, and run it again.

!!! warning "A common mistake: the language code"
    Language codes follow the BCP 47 standard: a language, then optionally a
    region, joined by a **hyphen**: `fr`, `fr-CA`, `en-GB`. Some software
    writes `fr_CA`, with an underscore. The DDI schema rejects it, and
    `doc.validate()` reports an issue whose message contains `lang='fr_CA'`.

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

# Step 2: Build the DDI document, with its concepts and universe
doc = ddi.new_study(title="Household Survey", agency="research.org")
demo = doc.add_concept(name="Demographics")
econ = doc.add_concept(name="Economics")
doc.add_universe(name="Canadian households, 2024")

# The concept each measured column belongs to
CONCEPTS = {
    "age": demo,
    "gender": demo,
    "income": econ,
    "education_level": demo,
}

# Step 3: One variable per column, linked to its question and concept
for col in columns:
    wording = QUESTIONS.get(col)
    # A column nobody was asked about, such as respondent_id, gets no question
    q = doc.add_question(text=wording) if wording else None
    doc.add_variable(name=col, question=q, concept=CONCEPTS.get(col))

# Step 4: Validate, and save only a valid document
issues = doc.validate()
for issue in issues:
    print(issue.message)
if not issues:
    doc.save("household-survey.xml")

# Step 5: Verify
print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
print(f"Concepts: {len(doc.concepts)}")
print(f"Universes: {len(doc.universes)}")
print(f"Schema problems: {len(issues)}")
```

**Expected output:**

```text
Questions: 4
Variables: 5
Concepts: 2
Universes: 1
Schema problems: 0
```

---

## Exercises

!!! example "Scenario"
    A researcher has a CSV file called `survey_sample.csv` from a household survey.
    It has five columns: `respondent_id`, `age`, `gender`, `income`, `education_level`.
    They need to create DDI metadata for this dataset.
    Your job is to write a Python script that reads the CSV, builds the DDI document,
    links it to concepts and a universe, adds French wording, validates it, and saves it as XML.

1. **(O1)** [Download](survey_sample.csv){ download="survey_sample.csv" } or create `survey_sample.csv` with these 5 columns: `respondent_id`, `age`, `gender`, `income`, `education_level`. Write a script that reads the CSV, creates a DDI document with one variable per column (with the question text from a lookup table), and saves it. Print the count.

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

2. **(O2)** (If pandas is installed) Adapt your Exercise 1 script to read the column names from an Excel sheet. To get a workbook, convert the sample CSV once with `pd.read_csv("survey_sample.csv").to_excel("survey_sample.xlsx", index=False)`, or save it as `survey_sample.xlsx` from your spreadsheet program. Then use `pd.read_excel()` to get the columns, and create the variables the same way.

    **Expected output:**

    ```text
    Variables: 5
    ```

    ??? success "Answer"
        Only the lines that read the column names change. `QUESTIONS` is the
        lookup table from Exercise 1.

        <!-- docs-test: skip -- needs pandas, openpyxl and an Excel workbook -->
        ```python
        import pandas as pd
        import ddi_l as ddi

        # Make a workbook from the sample CSV (once)
        pd.read_csv("survey_sample.csv").to_excel("survey_sample.xlsx", index=False)

        df = pd.read_excel("survey_sample.xlsx")
        columns = list(df.columns)

        doc = ddi.new_study(title="Household Survey", agency="research.org")
        for col in columns:
            wording = QUESTIONS.get(col)
            q = doc.add_question(text=wording) if wording else None
            doc.add_variable(name=col, question=q)
        doc.save("household-survey-excel.xml")
        print(f"Variables: {len(doc.variables)}")
        ```

3. **(O3)** Rebuild the document from Exercise 1 with three concepts and one universe: Demographics (for `age` and `gender`), Economics (for `income`), Education (for `education_level`), and the universe "Canadian households, 2024". Link each measured variable to its concept; `respondent_id` gets no concept. Print the counts and the number of linked variables.

    **Expected output:**

    ```text
    Concepts: 3
    Universes: 1
    Linked variables: 4
    ```

    ??? success "Answer"
        Continuing from Exercise 1 (`columns` and `QUESTIONS`):

        ```python
        doc = ddi.new_study(title="Household Survey", agency="research.org")

        demo = doc.add_concept(name="Demographics")
        econ = doc.add_concept(name="Economics")
        educ = doc.add_concept(name="Education")
        doc.add_universe(name="Canadian households, 2024")

        CONCEPTS = {
            "age": demo,
            "gender": demo,
            "income": econ,
            "education_level": educ,
        }

        for col in columns:
            wording = QUESTIONS.get(col)
            q = doc.add_question(text=wording) if wording else None
            doc.add_variable(name=col, question=q, concept=CONCEPTS.get(col))

        linked = [v for v in doc.variables if v.concept_references]
        print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
        print(f"Universes: {len(doc.universes)}")  # -> Universes: 1
        print(f"Linked variables: {len(linked)}")  # -> Linked variables: 4
        ```

4. **(O4)** Add French wording to the `age` and `gender` questions and a French name to the Demographics concept. Save the file as `household-survey-bilingual.xml`. Then read the saved file and confirm that both wordings of the age question are in it.

    **Expected output:**

    ```text
    True True
    ```

    ??? success "Answer"
        ```python
        from pathlib import Path

        from ddi_l.models.base import InternationalString

        # The first question asks for the respondent's age, the second for their gender
        doc.questions[0].question_texts.append(
            InternationalString(text="Quel âge avez-vous ?", lang="fr")
        )
        doc.questions[1].question_texts.append(
            InternationalString(text="Quel est votre genre ?", lang="fr")
        )
        doc.concepts[0].names.append(
            InternationalString(text="Démographie", lang="fr", child_tag="String")
        )
        doc.save("household-survey-bilingual.xml")

        saved = Path("household-survey-bilingual.xml").read_text(encoding="utf-8")
        print("How old are you?" in saved, "Quel âge avez-vous ?" in saved)  # -> True True
        ```

        You can also open the XML in a text editor and look for
        `xml:lang="fr"` next to the English text.

5. **(O5)** This code adds French wording to the income question, but it has a mistake. Run it and read the issue that `doc.validate()` reports. Then fix the mistake, validate again, and save the document once it is valid.

    ```python
    doc.questions[2].question_texts.append(
        InternationalString(
            text="Quel a été votre revenu total l'an dernier, avant impôts ?",
            lang="fr_CA",
        )
    )
    for issue in doc.validate():
        print(issue.message)
    ```

    **Expected output** (before the fix, then after it):

    ```text
    attribute {http://www.w3.org/XML/1998/namespace}lang='fr_CA': value doesn't match any pattern of ['[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*']
    Document is valid.
    ```

    ??? success "Answer"
        The message names the `lang` attribute and its value, `fr_CA`. The
        pattern `[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*` means letters, optionally
        followed by groups of a **hyphen** and letters or digits. An
        underscore is not allowed, so write `fr-CA` (or just `fr`):

        ```python
        doc.questions[2].question_texts[-1].lang = "fr-CA"

        issues = doc.validate()
        if issues:
            for issue in issues:
                print(issue.message)
        else:
            print("Document is valid.")  # -> Document is valid.
            doc.save("household-survey-bilingual.xml")
        ```

---

## Quiz

???+ question "Question 1 (O1): How many variables does the document hold?"
    A CSV header is `id,age,income`. The script loops over
    `reader.fieldnames` and calls `doc.add_variable(name=col, question=q)`
    once per column.

    **A.** 1

    **B.** 2, because `id` was not asked of anyone.

    **C.** 0, until you save the document.

    **D.** 3

    ??? success "Answer"
        **D.** The loop adds one variable per column, and there are three
        columns. A column with no question, such as `id`, still gets a
        variable.

???+ question "Question 2 (O1): Why does the script take question text from the QUESTIONS lookup table?"
    The alternative is to build it from the column name, with
    `f"What is the respondent's {col}?"`.

    **A.** Python cannot format strings that contain a column name.

    **B.** So the metadata records the wording respondents actually saw,
    not a sentence made from a column name.

    **C.** A lookup table makes the script run faster.

    **D.** DDI does not allow question marks in generated text.

    ??? success "Answer"
        **B.** A column name such as `education_level` is shorthand. The
        question text in DDI should be the wording from the questionnaire.

???+ question "Question 3 (O2): How do you get column names from a pandas DataFrame?"
    **A.** `df.rows`

    **B.** `df.fieldnames`

    **C.** `df.columns`

    **D.** `df.headers`

    ??? success "Answer"
        **C.** Use `df.columns` to get the column names from a pandas
        DataFrame. Wrap it in `list()` to get a plain list.
        `fieldnames` belongs to `csv.DictReader`, not to pandas.

???+ question "Question 4 (O3): Which call adds the income variable and links it to the Economics concept econ?"
    **A.** `doc.add_variable(name="income", question=q, concept=econ)`

    **B.** `doc.add_concept(name="income", concept=econ)`

    **C.** `econ.add_variable("income")`

    **D.** `doc.add_universe(name="income")`

    ??? success "Answer"
        **A.** Pass the concept with `concept=` when you add the variable. In
        a loop, `concept=CONCEPTS.get(col)` does the same for every column.

???+ question "Question 5 (O4): How can you confirm that French wording was saved?"
    You appended French wording to a question with
    `q.question_texts.append(InternationalString(text=french, lang="fr"))`
    and saved the document.

    **A.** Count the variables in the document.

    **B.** Run `doc.validate()`: it lists the languages in the document.

    **C.** Open the CSV file and look for the French text.

    **D.** Read the saved XML file and check that it contains the French
    wording, next to `xml:lang="fr"`.

    ??? success "Answer"
        **D.** The saved XML is what other people receive, so check it: open
        it in a text editor, or read it with `Path(...).read_text()` and test
        `"Quel âge avez-vous ?" in saved`. The CSV holds data, not metadata.

???+ question "Question 6 (O5): doc.validate() reports this issue. What is the fix?"
    `attribute {http://www.w3.org/XML/1998/namespace}lang='fr_CA': value doesn't match any pattern of ['[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*']`

    **A.** Write the language code with a hyphen, `fr-CA`, or just `fr`.

    **B.** Remove the French text from the document.

    **C.** Save the file anyway: the issue is only a warning.

    **D.** Rename the variable that holds the question.

    ??? success "Answer"
        **A.** The pattern allows letters joined by hyphens, not underscores.
        A schema issue makes the document invalid, so fix it before you save.

---

## Going further (optional)

This section is for readers who store data in a SQL database. It has no
objective, and you can skip it if you only use CSV or Excel files.

### Read column names from a SQL database

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

---

## Check yourself

- [ ] I can write a script that reads a CSV header and creates one variable per column, with question text from a lookup table. (O1)
- [ ] I can adapt the script to read the column names from an Excel sheet with pandas. (O2)
- [ ] I can add concepts and a universe and link each measured variable to its concept. (O3)
- [ ] I can add question text in a second language and confirm that both wordings are in the saved XML. (O4)
- [ ] I can validate the generated document and fix any error it reports before saving. (O5)

---

!!! tip "Instructor notes"
    - This is the "aha" module for researchers and NSO staff. Many learners will recognize their own workflow here.
    - **Key message:** The CSV is the **data**. The DDI XML is **documentation about the data**. They are two separate files with two separate purposes.
    - Walk through the complete script line by line. Let learners type along.
    - The SQL example under "Going further" is optional. Skip it for non-technical audiences. It is there for database-savvy participants who ask "what about SQL?"
    - Exercise 5 plants a language code with an underscore (`fr_CA`). Many learners have seen that style in other software; let them find the fix from the message before you explain it.
    - If time allows, let learners try with their own CSV files. Real data makes the exercise more meaningful.
    - Common mistake: learners confuse the CSV file with the XML output. Remind them that `doc.save()` writes metadata, not data.

---

**See also:** [Download the sample CSV file](survey_sample.csv){ download="survey_sample.csv" } (`survey_sample.csv`).
