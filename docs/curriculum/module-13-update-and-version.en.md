# Module 13: Update and Version Your Documents

!!! info "What you will learn"
    - Explain why versioning matters for surveys and studies.
    - Open an existing DDI document and add new content.
    - Use version numbers to track changes over time.
    - Increment major, minor, and sub-version numbers.
    - Record why a change was made using `VersionRationale`.
    - Set who is responsible for a version change.
    - Change the wording of an existing question.
    - Switch a variable from one code list to another.
    - Keep references pointing at the new version of an edited item.
    - Describe a new data file and update many variables from it in one loop.

**Prerequisites:** [Module 12: Custom Fields](module-12-custom-fields.md).

**Time:** 65 min self-paced / 75 min instructor-led.

---

## 1. Why versioning matters

Surveys change over time. A census might add a new question about internet
access in 2024. A labour force survey might remove an outdated question about
fax machines. When you change a document, you need to answer two questions:

1. **What changed?** Which items were added, removed, or edited?
2. **Why did it change?** What was the reason for the update?

**Versioning** means giving each copy of a document a number (like "1.0.0" or
"2.1.0") so you can tell them apart. Think of it like saving a school essay as
"essay-v1", "essay-v2", and "essay-v3". Each version is a snapshot in time.

Without versioning, you cannot go back to an earlier copy. You cannot compare
what changed between years. And you cannot explain your choices to other people.

---

## 2. The update workflow

The basic steps to update a DDI document are:

1. **Open** the existing file.
2. **Add** new content (questions, variables, concepts).
3. **Remove** outdated content.
4. **Save** the updated file with a new name.

Here is a short example. The first two lines stand in for last year's file;
if you already have a DDI file of your own, open that instead and skip them.

```python
import ddi_l as ddi

# Stand-in for last year's file
ddi.new_study(title="Labour Force Survey 2023", agency="example.org").save(
    "lfs-2023.xml"
)

# Step 1: Open the existing file
doc = ddi.open_ddi("lfs-2023.xml")

# Step 2: Add a new question
doc.add_question(text="Do you work from home?")

# Step 3: Save with a new filename
doc.save("lfs-2024.xml")
```

The function `ddi.open_ddi()` reads a DDI XML file from disk and gives you a
`Document` object. You can then add or remove items just like you did when you
first created the document. The function `doc.save()` writes the updated
document to a new file.

---

## 3. Version numbers

Every DDI item has a **version** field. A version is a string of numbers
separated by dots, such as `"1.0.0"`. The three parts are:

| Part    | Position | Meaning                 | Example       |
| ------- | -------- | ----------------------- | ------------- |
| Major   | First    | Big, breaking changes   | **2**.0.0     |
| Minor   | Second   | Additions or extensions | 1.**1**.0     |
| Sub     | Third    | Small fixes or patches  | 1.0.**1**     |

You can read the current version of any item:

```python
study = doc.study_unit
print(study.version)  # e.g. "1"
```

When you first create a study with `ddi.new_study()`, the default version is
`"1"`. You can set it to `"1.0.0"` if you prefer three-part numbers.

---

## 4. Increment versions

`ddi-l` gives you three methods to bump a version number. Each one is a
method on any DDI item (question, variable, concept, study, and so on). An
**item** is any object that extends `MaintainableBase`, the base class for
all DDI objects.

### Major version: big changes

Use `increment_major_version()` when you make a large change that could break
things. For example, you redesign the entire questionnaire.

<!-- docs-test: skip -- fragment: `item` is whichever item the reader is versioning -->
```python
item.increment_major_version()
# 1.0.0 → 2.0.0
```

### Minor version: additions

Use `increment_minor_version()` when you add something new but keep everything
else the same. For example, you add two new questions to a survey.

<!-- docs-test: skip -- fragment: `item` is whichever item the reader is versioning -->
```python
item.increment_minor_version()
# 1.0.0 → 1.1.0
```

### Sub-version: small fixes

Use `increment_subversion()` when you fix a typo or correct a small error.
Nothing big changed.

<!-- docs-test: skip -- fragment: `item` is whichever item the reader is versioning -->
```python
item.increment_subversion()
# 1.0.0 → 1.0.1
```

Each method increases one number and resets the numbers to its right back to
zero. For example, if the version is `1.2.3` and you call
`increment_minor_version()`, the result is `1.3.0`.

---

## 5. Record why you changed something

A **version rationale** is a short note that explains why a change was made.
DDI stores this information inside the XML so anyone who opens the file later
can understand the history.

You also set **version responsibility**: the name of the person or team who
made the change.

<!-- docs-test: skip -- fragment: `item` is whichever item the reader is versioning -->
```python
from ddi_l.models.base import VersionRationale, InternationalString

# Create a rationale with a description
rationale = VersionRationale(
    descriptions=[
        InternationalString(text="Added work-from-home question for 2024 wave")
    ]
)

# Attach it to an item
item.version_rationales.append(rationale)

# Record who made the change
item.version_responsibility = "Survey Design Team"
```

- `VersionRationale` is a small object that holds a list of descriptions. Each
  description is an `InternationalString` so you can write it in more than one
  language.
- `version_rationales` is a list. You can add more than one rationale if
  needed.
- `version_responsibility` is a plain text string with the name of the person
  or team.

---

## 6. Change the wording of a question

Adding and removing questions is only part of the job. Most survey updates
*edit* something that is already there: a question gets clearer wording, or
its answer categories change. This section and the next one show both, on the
same small file.

The file holds one question, "Do you work from home?". It is answered with a
**Yes/No** code list, and the answer is stored in the variable `WFH`. The block
below creates it, using the code-list pattern from
[Module 12](module-12-custom-fields.md). Skip it if you have a file of your
own.

```python
from uuid import uuid4

import ddi_l as ddi
from ddi_l.models.base import InternationalString, VersionRationale
from ddi_l.models.logicalproduct import Category, CodeItem


def add_codes(doc, code_list, answers):
    """Add one Category and one Code per (value, name) pair to code_list."""
    for value, name in answers:
        category = doc.add_item(Category, name=name, label=name)
        code_list.codes.append(
            CodeItem(
                agency=code_list.agency,
                identifier=str(uuid4()),
                version=code_list.version,
                value=value,
                category=category.to_reference(),
            )
        )


# Stand-in for last year's file
last_year = ddi.new_study(title="Labour Force Survey 2023", agency="example.org")
question = last_year.add_question(text="Do you work from home?", label="Work from home")
yes_no = last_year.add_code_list(name="Yes/No", label="Yes/No")
add_codes(last_year, yes_no, [("1", "Yes"), ("2", "No")])
wfh = last_year.add_variable(name="WFH", label="Works from home", question=question)
wfh.set_coded(yes_no)
last_year.save("wfh-2023.xml")
```

### Step 1: Find the question

Open the file and find the question by its current text:

```python
doc = ddi.open_ddi("wfh-2023.xml")

wfh_question = next(
    q for q in doc.questions if q.question_texts[0].text == "Do you work from home?"
)
```

If you know the question's identifier, `doc.find(identifier)` from
[Module 11](module-11-properties-find-validate.md) works as well.

### Step 2: Change the text

A question's wording is kept in `question_texts`, a list with one
`InternationalString` per language. Change the `text` of the language you are
updating:

```python
for text in wfh_question.question_texts:
    if text.lang == "en":
        text.text = "In a typical week, do you work from home?"

print(wfh_question.question_texts[0].text)
# -> In a typical week, do you work from home?
```

!!! warning "Update every language"
    If the question also has a French text (Module 3), change it too, in the
    same loop (`if text.lang == "fr": ...`). Otherwise the English and French
    versions no longer ask the same thing.

### Step 3: Version the question and say why

The question has changed, so its version must change. A small, clarifying
change like this one is a **sub-version**. If the new wording changed what the
question measures, so that answers are no longer comparable with last year,
use a **major** version instead.

```python
wfh_question.increment_subversion()
wfh_question.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(text="Added the reference period 'in a typical week'")
        ]
    )
)
wfh_question.version_responsibility = "Survey Design Team"

print(wfh_question.version)  # -> 1.0.1
```

### Step 4: Point the references at the new version

A DDI reference names one exact version of an item. The variable `WFH` still
says "question `…`, version `1`". That version is no longer in the file, so the
reference is now broken. Point every reference to the question at its new
version. In this file only the variable refers to the question:

```python
for variable in doc.variables:
    variable.question_references = [
        wfh_question.to_reference()
        if ref.identifier == wfh_question.identifier
        else ref
        for ref in variable.question_references
    ]
```

`to_reference()` builds a reference to the item as it is *now*, with its new
version.

A file with a questionnaire flow (Module 8) has more references to the
question: each `QuestionConstruct` that asks it holds a `question_reference`.
Repoint those the same way. In this file there are none, so the loop does
nothing:

```python
from ddi_l.models.datacollection import QuestionConstruct

for construct in doc.items(QuestionConstruct):
    ref = construct.question_reference
    if ref is not None and ref.identifier == wfh_question.identifier:
        construct.question_reference = wfh_question.to_reference()
```

Then let `doc.lint()` check that nothing still points at the old version. Each
`ddi.reference.integrity` error it reports names an item you still have to
repoint:

```python
errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
```

---

## 7. Switch a variable to a different code list

For the 2024 wave, a simple Yes/No answer is not enough. The team wants to
know *how often* people work from home. The answer categories change from
**Yes/No** to a new **Frequency** code list.

### Step 1: Create the new code list

```python
frequency = doc.add_code_list(name="Frequency", label="Frequency")
add_codes(doc, frequency, [("1", "Every day"), ("2", "Some days"), ("3", "Never")])
```

### Step 2: Point the variable at it

`set_coded()` tells a variable which code list holds its values. Calling it
again replaces the old code list with the new one:

```python
wfh = next(v for v in doc.variables if v.names[0].text == "WFH")
wfh.set_coded(frequency)
```

You can check which code list a variable uses now. Read the reference from the
variable's representation, and then look it up with `doc.find()`:

```python
reference = wfh.variable_representation.code_representation.code_list_reference
current = doc.find(reference.identifier)

print(current.names[0].text)  # -> Frequency
print([code.value for code in current.codes])  # -> ['1', '2', '3']
```

### Step 3: Version the variable and say why

New answer categories change what the variable can hold. Answers coded 1 or 2
last year and 1, 2 or 3 this year cannot be compared directly, so this is at
least a **minor** change, and often a **major** one:

```python
wfh.increment_major_version()
wfh.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(
                text="Answer categories changed from Yes/No to Frequency"
            )
        ]
    )
)
wfh.version_responsibility = "Survey Design Team"

print(wfh.version)  # -> 2
```

The variable started at version `"1"`, so a major bump gives `"2"`. The
question's sub-version bump gave `"1.0.1"` because a sub-version needs all
three parts.

As with the question, anything that refers to the variable now points at its
old version. In this file nothing does. In a larger file, check the variables
derived from it (their `source_variable_references`, Module 9) and any record
layout (section 8). Repoint them the same way, or build them after the bump.

### Step 4: Keep or remove the old code list

The Yes/No code list is still in the file. Keep it if other variables still use
it, or if you want the file to show what last year's answers meant. If nothing
uses it any more, remove it:

```python
old_list = next(cl for cl in doc.code_lists if cl.names[0].text == "Yes/No")
doc.remove(old_list.identifier)

print([cl.names[0].text for cl in doc.code_lists])  # -> ['Frequency']
```

The categories "Yes" and "No" stay in the file. That is harmless, and other
code lists can still reuse them.

Finally, check the file and save it under a new name, so last year's file
stays as it was. `doc.validate()` checks the file against the DDI schema only.
It does not notice a reference to a version that is no longer there, so run
`doc.lint()` as well:

```python
errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
print(doc.validate())  # -> []

doc.save("wfh-2024.xml")
```

!!! note "The question's response domain"
    In this curriculum a code list is attached to the **variable**. Files from
    other tools, such as Colectica, often attach it to the **question** as
    well, in a `d:CodeDomain` element inside the question. `ddi-l` keeps that
    element exactly as it was read: `set_coded()` changes the variable only,
    and `ddi-l` has no helper yet for changing a question's response domain.
    If your file has one, open it in a text editor after the switch and check
    which code list the question's `r:CodeListReference` names.

---

## 8. Update many variables from a new data file

A new wave usually arrives as a **data file**. The metadata has to catch up
with it: the new file needs describing, and many variables need the same kind
of change. In DDI, a data file is described by a **physical instance**
(`PhysicalInstance`): where the file is and how many records it holds.

This section puts the pieces together. You describe the new file, then loop
over the variables once and update each one from the data, versioning each
change as you go.

The example uses the sample file from Module 6:

[:material-download: Download `survey_sample.csv`](survey_sample.csv){ .md-button download="survey_sample.csv" }

Last year's document already describes the same five columns, and the 2023
data file. The block below creates it. Skip it if you have a file of your own.

```python
import csv

from ddi_l.models.physical import PhysicalInstance

# Stand-in for last year's file
last_year = ddi.new_study(title="Income Survey 2023", agency="example.org")
for column in ("respondent_id", "age", "gender", "income", "education_level"):
    last_year.add_variable(name=column, label=column)
data_2023 = last_year.add_item(PhysicalInstance, name="Income Survey 2023 data")
data_2023.set_data_file("https://example.org/data/income-2023.csv")
data_2023.set_record_count(4800)
last_year.save("income-2023.xml")
```

### Step 1: Open the document and read the new data file

```python
doc = ddi.open_ddi("income-2023.xml")

with open("survey_sample.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"{len(rows)} records")  # -> 5 records
```

### Step 2: Describe the new file

Add a physical instance for the 2024 file. Keep the 2023 one: it still
describes last year's file correctly.

```python
data_2024 = doc.add_item(PhysicalInstance, name="Income Survey 2024 data")
data_2024.set_data_file("https://example.org/data/income-2024.csv")
data_2024.set_record_count(len(rows))
```

### Step 3: Write down the changes

Put the changes in one place before you touch any variable. Here every
variable gets a clearer label, two get a numeric range, and two get a code
list:

```python
new_labels = {
    "respondent_id": "Respondent identifier",
    "age": "Age in years",
    "gender": "Gender",
    "income": "Annual income (CAD)",
    "education_level": "Highest level of education",
}
numeric_columns = {"age", "income"}
coded_columns = {"gender", "education_level"}
```

### Step 4: Update every variable in one loop

For each variable, find its column in the data file, apply the changes, and
then version it. The code lists use the `add_codes()` helper from section 6.

```python
for variable in doc.variables:
    column = variable.names[0].text
    values = [row[column] for row in rows if row[column] != ""]

    # A clearer label
    variable.labels = [InternationalString(text=new_labels[column], lang="en")]

    # What the variable holds, taken from the new file
    if column in numeric_columns:
        numbers = [int(value) for value in values]
        variable.set_numeric("Integer", low=min(numbers), high=max(numbers))
    elif column in coded_columns:
        code_list = doc.add_code_list(name=new_labels[column], label=new_labels[column])
        answers = sorted(set(values))
        add_codes(doc, code_list, [(str(n), a) for n, a in enumerate(answers, 1)])
        variable.set_coded(code_list)
    else:
        variable.set_text()

    # Version the change and say why
    variable.increment_minor_version()
    variable.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Label and representation updated for 2024")
            ]
        )
    )
    variable.version_responsibility = "Data Processing Unit"

for variable in doc.variables:
    print(variable.names[0].text, variable.version)
```

```text
respondent_id 1.1
age 1.1
gender 1.1
income 1.1
education_level 1.1
```

You can check one of them. The `age` range now matches the ages in the new
file:

```python
age = next(v for v in doc.variables if v.names[0].text == "age")
age_range = age.variable_representation.numeric_representation.number_range
print(age_range.low, age_range.high)  # -> 22 51
```

### Step 5: Say where each variable sits in the new file

A **record layout** lists the variables in the data file. Build it *after* the
version bumps, so that it points at the new versions. A layout built before
the loop would point at the old ones. Then link the layout to the 2024 file:

```python
layout = doc.add_record_layout()
for variable in doc.variables:
    layout.add_data_item(variable.to_reference(), delimiter="comma")
data_2024.record_layout_references.append(layout.to_reference())
```

### Step 6: Check and save

```python
errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
print(doc.validate())  # -> []

doc.save("income-2024.xml")
```

!!! tip "One loop, one rationale per item"
    The pattern scales. Whether you change five variables or five hundred,
    write the changes down first (Step 3). Then apply them in a single loop
    that changes, versions and explains each item. Every changed variable
    ends up with its own version and its own rationale, so the history stays
    readable item by item.

---

## 9. The full update cycle

Here is the complete workflow from start to finish:

```python
import ddi_l as ddi
from ddi_l.models.base import VersionRationale, InternationalString

# Stand-in for last year's file (skip if you have one of your own)
first = ddi.new_study(title="Survey v1", agency="example.org")
first.add_question(text="Do you own a fax machine?")
first.save("survey-v1.xml")

# 1. Open the existing document
doc = ddi.open_ddi("survey-v1.xml")

# 2. Add new content
doc.add_question(text="How many hours do you sleep per night?")

# 3. Remove outdated content (use the identifier of the old item)
old_question = doc.questions[0]
doc.remove(old_question.identifier)

# 4. Increment the version on the study
study = doc.study_unit
study.increment_minor_version()

# 5. Add a rationale
study.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(text="Added sleep question; removed outdated item")
        ]
    )
)
study.version_responsibility = "Research Methods Unit"

# 6. Validate
errors = doc.validate()
if errors:
    print("Errors:", errors)
else:
    print("Document is valid.")  # -> Document is valid.

# 7. Save
doc.save("survey-v2.xml")
```

---

## 10. Best practices

Follow these rules to keep your versioning clean and useful:

- **Always validate before you publish.** Run `doc.validate()` and fix any
  errors before sharing the file.
- **Keep old versions.** Save each version to a different filename (like
  `survey-v1.xml`, `survey-v2.xml`). Do not overwrite old files.
- **Write clear rationales.** Future users will thank you. A good rationale
  says *what* changed and *why*.
- **Use the right increment.** Do not use a major version bump for a small fix.
  Match the increment to the size of the change.
- **Set version responsibility.** Record who approved or made the change so
  there is a contact for questions.
- **Version the item you edited, not only the study.** A reworded question or
  a variable with new answer categories gets its own version bump and
  rationale.
- **Update the references.** After a version bump, point every reference to
  the item at its new version, then run `doc.lint()` to confirm nothing is
  broken.

---

## Exercises

!!! example "Scenario"
    A national labour force survey runs every year. The 2024 version added two
    new questions and retired one old question. The agency needs to update the
    DDI document and record why.

**Exercise 1.** Create a study with three questions ("Survey v1"). Save it as
`survey-v1.xml`.

```python
import ddi_l as ddi

doc = ddi.new_study(title="Labour Force Survey v1", agency="stats.example.org")
q1 = doc.add_question(text="What is your current employment status?")
q2 = doc.add_question(text="How many hours do you work per week?")
q3 = doc.add_question(text="Do you use a fax machine at work?")
doc.save("survey-v1.xml")
print(f"Saved with {len(doc.questions)} questions.")
```

**Exercise 2.** Re-open `survey-v1.xml`. Add one new question. Remove one old
question.

```python
doc = ddi.open_ddi("survey-v1.xml")
print(f"Before: {len(doc.questions)} questions")

# Add a new question
doc.add_question(text="How many hours do you sleep per night?")

# Remove the outdated fax question (the third one)
fax_q = doc.questions[2]
doc.remove(fax_q.identifier)
print(f"After: {len(doc.questions)} questions")
```

**Exercise 3.** Get the study from the document. Call
`increment_minor_version()` on it. Add a `VersionRationale`. Set
`version_responsibility`.

```python
from ddi_l.models.base import VersionRationale, InternationalString

study = doc.study_unit
study.increment_minor_version()

study.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(text="Added sleep quality question for wave 2")
        ]
    )
)
study.version_responsibility = "Survey Design Team"
```

**Exercise 4.** Validate and save as `survey-v2.xml`. Print the version and
rationale.

```python
errors = doc.validate()
if errors:
    print("Errors:", errors)
else:
    doc.save("survey-v2.xml")
    print(f"Version: {study.version}")
    for r in study.version_rationales:
        for d in r.descriptions:
            print(f"Rationale: {d.text}")
```

Expected output:

```text
Version: 1.1
Rationale: Added sleep quality question for wave 2
```

**Exercise 5.** Re-open `survey-v2.xml`. Change the wording of the
employment-status question to "What was your main activity last week?". Give
the question a sub-version bump and a rationale. Then save the file as
`survey-v3.xml`.

```python
doc = ddi.open_ddi("survey-v2.xml")

status_q = next(
    q
    for q in doc.questions
    if q.question_texts[0].text == "What is your current employment status?"
)
for text in status_q.question_texts:
    if text.lang == "en":
        text.text = "What was your main activity last week?"

status_q.increment_subversion()
status_q.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(text="Aligned wording with the ILO definition")
        ]
    )
)

# Repoint any variable that references the question
for variable in doc.variables:
    variable.question_references = [
        status_q.to_reference() if ref.identifier == status_q.identifier else ref
        for ref in variable.question_references
    ]

doc.save("survey-v3.xml")
print(f"{status_q.question_texts[0].text} (version {status_q.version})")
# -> What was your main activity last week? (version 1.0.1)
```

**Exercise 6.** In the same document, add a variable `EMPSTAT` for the
question. Code it with a three-value list (Employed, Unemployed, Not in labour
force). Then switch it to a four-value list that splits "Not in labour force"
into "Student" and "Retired". Bump the variable's major version and record
why.

```python
three_way = doc.add_code_list(name="Status (3)", label="Status (3)")
add_codes(
    doc,
    three_way,
    [("1", "Employed"), ("2", "Unemployed"), ("3", "Not in labour force")],
)
four_way = doc.add_code_list(name="Status (4)", label="Status (4)")
add_codes(
    doc,
    four_way,
    [("1", "Employed"), ("2", "Unemployed"), ("3", "Student"), ("4", "Retired")],
)

empstat = doc.add_variable(name="EMPSTAT", label="Employment status", question=status_q)
empstat.set_coded(three_way)

# The switch
empstat.set_coded(four_way)
empstat.increment_major_version()
empstat.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(
                text="Split 'Not in labour force' into Student and Retired"
            )
        ]
    )
)

reference = empstat.variable_representation.code_representation.code_list_reference
print(doc.find(reference.identifier).names[0].text)  # -> Status (4)
```

---

## Quiz

???+ question "Question 1: What does increment_minor_version() do?"
    **A.** It changes the version from 1.0.0 to 2.0.0.

    **B.** It changes the version from 1.0.0 to 1.1.0.

    **C.** It changes the version from 1.0.0 to 1.0.1.

    **D.** It deletes the version number.

    ??? success "Answer"
        **B.** `increment_minor_version()` increases the second number and
        resets the third number to zero. So 1.0.0 becomes 1.1.0.

???+ question "Question 2: What does a version rationale record?"
    **A.** The file size of the document.

    **B.** The number of questions in the survey.

    **C.** An explanation of why the document changed.

    **D.** The name of the Python file used to create the document.

    ??? success "Answer"
        **C.** A version rationale is a short note that explains why a change
        was made. It helps future users understand the history of the document.

???+ question "Question 3: What does version_responsibility track?"
    **A.** The computer where the file is stored.

    **B.** The person or team who made the version change.

    **C.** The date of the next survey wave.

    **D.** The total number of versions.

    ??? success "Answer"
        **B.** `version_responsibility` is a text field that records who made
        or approved the change. It could be a person's name or a team name.

???+ question "Question 4: When should you use a major version increment?"
    **A.** When you fix a typo in a question.

    **B.** When you add one new variable.

    **C.** When you make a big change, like redesigning the whole questionnaire.

    **D.** When you save the file to a new folder.

    ??? success "Answer"
        **C.** A major version increment (1.0.0 to 2.0.0) signals a large,
        potentially breaking change. Small additions use a minor increment.
        Typo fixes use a sub-version increment.

???+ question "Question 5: You reword a question and bump its version. What else must you do?"
    **A.** Nothing; the variable follows the question automatically.

    **B.** Delete the variable and create a new one.

    **C.** Point every reference to the question at its new version.

    **D.** Rename the file to `.ddi`.

    ??? success "Answer"
        **C.** A DDI reference names one exact version. After the bump, the
        variable's `question_references` (and any `QuestionConstruct` that
        asks the question) still name the old version, so replace them with
        `question.to_reference()`. `doc.lint()` reports a
        `ddi.reference.integrity` error for each one you miss.

???+ question "Question 6: How do you switch a variable from one code list to another?"
    **A.** Call `variable.set_coded(new_code_list)`.

    **B.** Rename the old code list.

    **C.** Add the new codes to the old code list.

    **D.** Call `doc.add_code_list()` with the variable's name.

    ??? success "Answer"
        **A.** `set_coded()` replaces the variable's representation with one
        that references the new code list. Then bump the variable's version,
        record a rationale, and remove the old code list if nothing else
        uses it.

???+ question "Question 7: You update 30 variables from a new data file. When should you build the new record layout?"
    **A.** Before the loop, so it is ready.

    **B.** After the version bumps, so it points at the new versions.

    **C.** Never; the physical instance finds the variables by name.

    **D.** Only if the file is fixed-width.

    ??? success "Answer"
        **B.** A record layout holds references to the variables, and each
        reference names a version. Built before the bumps, it would point at
        the old versions. Built after, `variable.to_reference()` gives the
        new ones.

---

!!! tip "Instructor notes"
    - **Key module for archivists and NSO staff.** Versioning is built into the
      DDI standard itself; it is not something added on top. Every
      maintainable object carries its own version, rationale, and
      responsibility fields.
    - **Show before/after XML.** Open `survey-v1.xml` and `survey-v2.xml` in a
      text editor side by side. Point out the `<r:Version>` and
      `<r:VersionRationale>` elements so learners see what the Python code
      produces.
    - **The version methods live on `MaintainableBase`.** All DDI objects
      (questions, variables, concepts, studies, code lists) inherit these
      methods. You can version any item, not just the top-level study.
    - **Common mistake:** Learners may forget to set the version to a
      three-part string like `"1.0.0"` before calling `increment_subversion()`.
      If the version is just `"1"`, the method will pad it automatically, but
      it helps to start with three parts for clarity.
    - **Edits, not just additions (sections 6 and 7).** Most real updates
      reword a question or change its answer categories. Stress the four steps:
      find the item, change it, version it with a rationale, repoint the
      references. Have learners skip the last step once and run `doc.lint()` to
      see the `ddi.reference.integrity` error for themselves.
    - **Wording vs. meaning.** Ask whether a wording change keeps answers
      comparable with last year. If yes, use a sub-version; if not, use a
      major version. The same question applies to a new code list.
    - **Bulk updates (section 8).** This is the realistic case for NSO staff:
      a new wave's data file arrives and dozens of variables need the same
      kind of change. Point out that Step 3 is a plain dictionary. Learners
      can keep it in a spreadsheet and load it, so subject-matter staff can
      review the changes before anyone runs the loop.
    - **Discussion prompt:** Ask learners how their organization currently
      tracks changes to survey instruments. Compare that process to DDI
      versioning.
