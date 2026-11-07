---
description: >-
  Module 15 of the ddi-l course: update published DDI files, bump versions,
  record rationales and keep references pointing at the right version.
---

# Module 15: Update and version your documents

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Open an existing DDI file, add and remove items, and save the
      result under a new file name so the old file stays unchanged.
    - **O2.** Choose a major, minor or sub-version increment for a described
      change, and predict the version number it gives.
    - **O3.** Record a version rationale and a version responsibility on the
      item you changed.
    - **O4.** Change the wording of a question in every language, give it a
      sub-version, and repoint the variable that refers to it so `doc.lint()`
      reports no errors.
    - **O5.** Switch a variable to a different code list with `set_coded()`,
      check which list it now uses, and give it a new version with a
      rationale.

**Prerequisites:** [Module 14](module-14-custom-fields.en.md).

**Time:** 65 min self-paced / 75 min instructor-led.

**New in this module:** `increment_major_version()`,
`increment_minor_version()`, `increment_subversion()`, `allow_dotted=True`,
`VersionRationale`, `version_rationales`, `version_responsibility`,
`to_reference()`, `set_coded()`.

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
4. **Check** the result, and **save** it under a new name.

Here is a short example. The first three lines stand in for last year's file;
if you already have a DDI file of your own, open that instead and skip them.

```python
import ddi_l as ddi

# Stand-in for last year's file
last_year = ddi.new_study(title="Labour Force Survey 2023", agency="example.org")
last_year.add_question(text="Do you use a fax machine at work?")
last_year.save("lfs-2023.xml")

# Step 1: Open the existing file
doc = ddi.open_ddi("lfs-2023.xml")

# Step 2: Add a new question
doc.add_question(text="Do you work from home?")

# Step 3: Remove the outdated question, by its identifier
fax = next(
    q
    for q in doc.questions
    if q.question_texts[0].text == "Do you use a fax machine at work?"
)
doc.remove(fax.identifier)

# Step 4: Check, then save with a new filename
print(doc.validate())  # -> []
doc.save("lfs-2024.xml")
```

The function `ddi.open_ddi()` reads a DDI XML file from disk and gives you a
`Document` object. You can then add or remove items just like you did when you
first created the document. The function `doc.save()` writes the updated
document to a new file, so `lfs-2023.xml` stays exactly as it was: you can
still compare the two years, or go back.

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

An item keeps the numbering it has. On a single-number version such as `"1"`,
`increment_minor_version()` and `increment_subversion()` raise an error rather
than turn it into `"1.1"`, because some tools only read whole-number
versions. Set `"1.0.0"` first, or pass `allow_dotted=True` when
you do want `"1"` to become `"1.1"`. The examples below that start from a new
study pass it.

---

## 4. Increment versions

`ddi-l` gives you three methods to bump a version number. Each one is a
method on any DDI item (question, variable, concept, study, and so on). An
**item** is any object that extends `MaintainableBase`, the base class for
all DDI objects.

### Major version: big changes

Use `increment_major_version()` when you make a large change that could break
things. For example, you redesign the entire questionnaire, or answers are no
longer comparable with last year's.

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

### Check your prediction

Predict each printed version before you run the block:

```python
item = doc.add_question(text="How many hours do you work per week?")
print(item.version)  # -> 1

try:
    item.increment_minor_version()
except ddi.DDIModelError:
    print("Refused: a one-part version stays one-part")

item.increment_minor_version(allow_dotted=True)
print(item.version)  # -> 1.1

item.version = "1.2.3"
item.increment_minor_version()
print(item.version)  # -> 1.3.0
```

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
- `version_rationales` is a list, but the schema allows only one rationale
  per item: the reason for its current version. If the item already has one
  from an earlier change, replace it (`item.version_rationales = [rationale]`)
  instead of appending a second; with two, `doc.validate()` reports an error.
- `version_responsibility` is a plain text string with the name of the person
  or team.

Put the rationale and the responsibility on the item you changed. A reworded
question gets its own; the study gets one only for a change to the study.

---

## 6. Change the wording of a question

Adding and removing questions is only part of the job. Most survey updates
*edit* something that is already there: a question gets clearer wording, or
its answer categories change. This section and the next one show both, on the
same small file.

The file holds one question, "Do you work from home?". It is answered with a
**Yes/No** code list, and the answer is stored in the variable `WFH`. The block
below creates it, using the code-list pattern from
[Module 14](module-14-custom-fields.en.md). Skip it if you have a file of your
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
[Module 13](module-13-properties-find-validate.en.md) works as well.

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
wfh_question.increment_subversion(allow_dotted=True)
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

### Step 4: Point the variable at the new version

A DDI reference names one exact version of an item. The variable `WFH` still
says "question `…`, version `1`". That version is no longer in the file, so the
reference is now broken. Point it at the question's new version:

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

Then let `doc.lint()` check that nothing still points at the old version. Each
`ddi.reference.integrity` error it reports names an item you still have to
repoint:

```python
errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
```

In this file only the variable refers to the question. A larger file can have
more references to it: see
[Going further](#keep-every-reference-current).

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

In this file nothing refers to the variable. If something did (a derived
variable, a record layout), it would now point at the old version:
[Going further](#keep-every-reference-current) shows how to handle that.

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
    other tools often attach it to the **question** as
    well, in a `d:CodeDomain` element inside the question. `ddi-l` keeps that
    element exactly as it was read: `set_coded()` changes the variable only,
    and `ddi-l` has no helper yet for changing a question's response domain.
    If your file has one, open it in a text editor after the switch and check
    which code list the question's `r:CodeListReference` names.

---

## 8. Best practices

- **Keep old versions.** Save each version to a different filename (like
  `survey-v1.xml`, `survey-v2.xml`). Do not overwrite old files.
- **Use the right increment.** Match it to the size of the change: a
  sub-version for a fix, a minor version for an addition, a major version when
  answers are no longer comparable.
- **Version the item you edited, not only the study.** A reworded question or
  a variable with new answer categories gets its own version bump, rationale
  and responsibility.
- **Write clear rationales.** A good rationale says *what* changed and *why*.
- **Update the references, then check.** After a version bump, point every
  reference to the item at its new version. Run `doc.validate()` and
  `doc.lint()`, and fix every error before you share the file.

---

## Exercises

!!! example "Scenario"
    A national labour force survey runs every year. The 2024 version added a
    new question, retired an old one, and reworded and recoded the employment
    question. The agency needs to update the DDI document and record why.

**Exercise 1 (O1).** Create a study, "Labour Force Survey v1", with three
questions: "What is your current employment status?" (with the French text
"Quelle est votre situation d'emploi actuelle ?"), "How many hours do you work
per week?" and "Do you use a fax machine at work?". Add a variable `EMPSTAT`
for the first question. Save the study as `survey-v1.xml`.

Expected output:

```text
Saved with 3 questions and 1 variable.
```

??? success "Answer"
    ```python
    import ddi_l as ddi
    from ddi_l.models.base import InternationalString

    doc = ddi.new_study(title="Labour Force Survey v1", agency="stats.example.org")
    q1 = doc.add_question(text="What is your current employment status?")
    q1.question_texts.append(
        InternationalString(
            text="Quelle est votre situation d'emploi actuelle ?", lang="fr"
        )
    )
    q2 = doc.add_question(text="How many hours do you work per week?")
    q3 = doc.add_question(text="Do you use a fax machine at work?")
    doc.add_variable(name="EMPSTAT", label="Employment status", question=q1)

    doc.save("survey-v1.xml")
    print(f"Saved with {len(doc.questions)} questions and {len(doc.variables)} variable.")
    ```

**Exercise 2 (O1).** Re-open `survey-v1.xml`. Add the question "How many hours
do you sleep per night?". Remove the fax question, found by its text. Print the
question count before and after, and check the document with
`doc.validate()`.

Expected output:

```text
Before: 3 questions
After: 3 questions
[]
```

??? success "Answer"
    ```python
    doc = ddi.open_ddi("survey-v1.xml")
    print(f"Before: {len(doc.questions)} questions")

    # Add a new question
    doc.add_question(text="How many hours do you sleep per night?")

    # Remove the outdated fax question
    fax_q = next(
        q
        for q in doc.questions
        if q.question_texts[0].text == "Do you use a fax machine at work?"
    )
    doc.remove(fax_q.identifier)
    print(f"After: {len(doc.questions)} questions")
    print(doc.validate())  # -> []
    ```

    The count is the same, but the content is not: one question in, one out.
    `survey-v1.xml` on disk is unchanged until you save over it, which you
    will not do.

**Exercise 3 (O2).** A study is at version `1.2.0`. For each change below,
choose the increment and predict the new version, starting from `1.2.0` each
time: (a) you fix a typo in a question; (b) you add two questions; (c) you
replace the questionnaire, so answers are no longer comparable with last
year. Then check (b) and (c) in Python on a new study set to `1.2.0`.

Expected output:

```text
1.3.0
2.0.0
```

??? success "Answer"
    (a) Sub-version: `1.2.1`. (b) Minor: `1.3.0`. (c) Major: `2.0.0`.

    ```python
    check = ddi.new_study(title="Version check", agency="example.org").study_unit

    check.version = "1.2.0"
    check.increment_minor_version()
    print(check.version)  # -> 1.3.0

    check.version = "1.2.0"
    check.increment_major_version()
    print(check.version)  # -> 2.0.0
    ```

    Each increment resets the numbers to its right to zero.

**Exercise 4 (O3).** Back in the document of Exercise 2, get the study, call
`increment_minor_version()` on it (it is at `"1"`, so pass
`allow_dotted=True`), add a `VersionRationale`, and set
`version_responsibility`. Validate, save as `survey-v2.xml`, and print the
version, the rationale and the responsibility.

Expected output:

```text
Version: 1.1
Rationale: Added sleep question; retired fax question
Responsibility: Survey Design Team
```

??? success "Answer"
    ```python
    from ddi_l.models.base import VersionRationale

    study = doc.study_unit
    study.increment_minor_version(allow_dotted=True)
    study.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Added sleep question; retired fax question")
            ]
        )
    )
    study.version_responsibility = "Survey Design Team"

    errors = doc.validate()
    if errors:
        print("Errors:", errors)
    else:
        doc.save("survey-v2.xml")
        print(f"Version: {study.version}")  # -> Version: 1.1
        for r in study.version_rationales:
            for d in r.descriptions:
                print(f"Rationale: {d.text}")
        print(f"Responsibility: {study.version_responsibility}")
    ```

**Exercise 5 (O4).** Re-open `survey-v2.xml`. Change the wording of the
employment-status question, in both languages, to "What was your main activity
last week?" and "Quelle était votre activité principale la semaine
dernière ?". Give the question a sub-version bump and a rationale. Point
`EMPSTAT` at the question's new version, check with `doc.lint()`, and save the
file as `survey-v3.xml`.

Expected output:

```text
What was your main activity last week? (version 1.0.1)
Quelle était votre activité principale la semaine dernière ?
Lint errors: 0
```

??? success "Answer"
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
        if text.lang == "fr":
            text.text = "Quelle était votre activité principale la semaine dernière ?"

    status_q.increment_subversion(allow_dotted=True)
    status_q.version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(text="Aligned wording with the ILO definition")
            ]
        )
    )

    # Repoint the variable that references the question
    for variable in doc.variables:
        variable.question_references = [
            status_q.to_reference() if ref.identifier == status_q.identifier else ref
            for ref in variable.question_references
        ]

    print(f"{status_q.question_texts[0].text} (version {status_q.version})")
    # -> What was your main activity last week? (version 1.0.1)
    print(status_q.question_texts[1].text)

    errors = [finding for finding in doc.lint() if finding.severity == "error"]
    print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
    doc.save("survey-v3.xml")
    ```

    Skip the repointing loop once and run `doc.lint()`: it reports a
    `ddi.reference.integrity` error for `EMPSTAT`.

**Exercise 6 (O5).** In the same document, code `EMPSTAT` with a three-value
list (Employed, Unemployed, Not in labour force), as last year's file would
have it. Then switch it to a four-value list that splits "Not in labour force"
into "Student" and "Retired". Bump the variable's major version, record why,
and print the name of the code list it now uses and its version.

Expected output:

```text
Status (4)
2
```

??? success "Answer"
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

    empstat = next(v for v in doc.variables if v.names[0].text == "EMPSTAT")
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
    print(empstat.version)  # -> 2
    ```

    A major bump fits: last year's code 3 no longer means the same thing.

---

## Quiz

???+ question "Question 1 (O1): You opened survey-2023.xml and added two questions. Which line keeps last year's file unchanged?"
    **A.** `doc.save("survey-2023.xml")`

    **B.** `doc.validate()`

    **C.** `doc.save("survey-2024.xml")`

    **D.** `ddi.open_ddi("survey-2024.xml")`

    ??? success "Answer"
        **C.** Saving under a new name writes the update to a new file and
        leaves `survey-2023.xml` as it was. A overwrites last year's file. B
        checks but saves nothing; D reads a file that does not exist yet.

???+ question "Question 2 (O2): A question is at version 1.2.3. You call increment_minor_version(). What is its version now?"
    **A.** `1.3.3`

    **B.** `2.0.0`

    **C.** `1.2.4`

    **D.** `1.3.0`

    ??? success "Answer"
        **D.** The minor number goes up by one, and the number to its right
        resets to zero.

???+ question "Question 3 (O2): A variable is at version 1. You call increment_subversion() with no arguments. What happens?"
    **A.** It raises an error: pass `allow_dotted=True` to get `1.0.1`, or
    use `increment_major_version()`.

    **B.** The version becomes `1.0.1`.

    **C.** The version becomes `2`.

    **D.** Nothing: the version stays `1` and no error is raised.

    ??? success "Answer"
        **A.** An item keeps the numbering it has. A one-part version stays
        one-part unless you pass `allow_dotted=True`, because some tools only
        read whole-number versions.

???+ question "Question 4 (O3): Which code records why question q changed and who changed it?"
    **A.** `q.labels.append(InternationalString(text="Reworded for 2024"))`

    **B.** `q.version_rationales.append(VersionRationale(descriptions=[InternationalString(text="Reworded for 2024")]))`,
    then `q.version_responsibility = "Survey Design Team"`

    **C.** `q.set_property("why", "Reworded for 2024")`

    **D.** `doc.save("survey-2024.xml")`

    ??? success "Answer"
        **B.** A `VersionRationale` holds the reason, and
        `version_responsibility` names who made the change. A changes the
        label; C stores a custom field that no DDI tool reads as a rationale.

???+ question "Question 5 (O4): You reworded a question and bumped its version. doc.lint() now reports ddi.reference.integrity. What do you fix?"
    **A.** Delete the variable and create a new one.

    **B.** Undo the version bump.

    **C.** Replace the variable's reference with `question.to_reference()`,
    which names the new version.

    **D.** Nothing: `doc.validate()` passes, so the file is fine.

    ??? success "Answer"
        **C.** A DDI reference names one exact version. After the bump, the
        variable's `question_references` still name the old one, so replace
        them with `question.to_reference()`. `doc.validate()` does not check
        references, which is why D is wrong.

???+ question "Question 6 (O5): How do you switch a variable from one code list to another?"
    **A.** Call `variable.set_coded(new_code_list)`.

    **B.** Rename the old code list.

    **C.** Add the new codes to the old code list.

    **D.** Call `doc.add_code_list()` with the variable's name.

    ??? success "Answer"
        **A.** `set_coded()` replaces the variable's representation with one
        that references the new code list. Then bump the variable's version,
        record a rationale, and remove the old code list if nothing else
        uses it.

???+ question "Question 7 (O5): A variable's answers change from Yes/No to Every day, Some days, Never. Which increment fits?"
    **A.** A sub-version: only the labels changed.

    **B.** A minor version: one category was added.

    **C.** None: the variable's name did not change.

    **D.** A major version: last year's answers cannot be compared directly
    with this year's.

    ??? success "Answer"
        **D.** New answer categories change what the variable holds. When
        answers are no longer comparable, the change is major.

---

## Going further (optional)

### Keep every reference current

Section 6 repointed the one variable that referred to the question. A larger
file can have more references to an item you version:

- **A questionnaire flow** (Module 10): each `QuestionConstruct` that asks a
  question holds a `question_reference`. Repoint it the same way:

    ```python
    from ddi_l.models.datacollection import QuestionConstruct


    def repoint_constructs(doc, question):
        """Point every QuestionConstruct that asks `question` at its new version."""
        for construct in doc.items(QuestionConstruct):
            ref = construct.question_reference
            if ref is not None and ref.identifier == question.identifier:
                construct.question_reference = question.to_reference()
    ```

- **Derived variables** (Module 11) refer to their sources in
  `source_variable_references`.
- **A record layout** refers to every variable of a data file (below).

Either repoint each one with `to_reference()`, or build it after the bump so it
points at the new version from the start. Then run `doc.lint()`: every
`ddi.reference.integrity` error names one you missed.

### Update many variables from a new data file

A new wave usually arrives as a **data file**. The metadata has to catch up
with it: the new file needs describing, and many variables need the same kind
of change. In DDI, a data file is described by a **physical instance**
(`PhysicalInstance`): where the file is and how many records it holds.

You describe the new file, then loop over the variables once and update each
one from the data, versioning each change as you go.

The example uses the sample file from Module 8:

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

**Step 1: Open the document and read the new data file.**

```python
doc = ddi.open_ddi("income-2023.xml")

with open("survey_sample.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"{len(rows)} records")  # -> 5 records
```

**Step 2: Describe the new file.** Add a physical instance for the 2024 file.
Keep the 2023 one: it still describes last year's file correctly.

```python
data_2024 = doc.add_item(PhysicalInstance, name="Income Survey 2024 data")
data_2024.set_data_file("https://example.org/data/income-2024.csv")
data_2024.set_record_count(len(rows))
```

**Step 3: Write down the changes.** Put the changes in one place before you
touch any variable. Here every variable gets a clearer label, two get a
numeric range, and two get a code list:

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

**Step 4: Update every variable in one loop.** For each variable, find its
column in the data file, apply the changes, and then version it. The code
lists use the `add_codes()` helper from section 6.

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
    variable.increment_minor_version(allow_dotted=True)
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

**Step 5: Say where each variable sits in the new file.** A **record layout**
lists the variables in the data file. Build it *after* the version bumps, so
that it points at the new versions. A layout built before the loop would point
at the old ones. Then link the layout to the 2024 file:

```python
layout = doc.add_record_layout()
for variable in doc.variables:
    layout.add_data_item(variable.to_reference(), delimiter="comma")
data_2024.record_layout_references.append(layout.to_reference())
```

**Step 6: Check and save.**

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

## Check yourself

- [ ] I can open a DDI file, add and remove items, and save the result under a new name. (O1)
- [ ] I can choose the increment for a change and predict the version it gives. (O2)
- [ ] I can record a version rationale and a version responsibility on the item I changed. (O3)
- [ ] I can reword a question in every language, version it, and repoint the variable that refers to it. (O4)
- [ ] I can switch a variable to another code list, check which list it uses, and version it. (O5)

---

!!! tip "Instructor notes"
    - **Key module for archivists and statistical-office staff.** Versioning
      is built into the DDI standard itself; it is not something added on
      top. Every maintainable object carries its own version, rationale, and
      responsibility fields.
    - **Show before/after XML.** Open `survey-v1.xml` and `survey-v2.xml` in a
      text editor side by side. Point out the `<r:Version>` and
      `<r:VersionRationale>` elements so learners see what the Python code
      produces.
    - **The version methods live on `MaintainableBase`.** All DDI objects
      (questions, variables, concepts, studies, code lists) inherit these
      methods. You can version any item, not just the top-level study.
    - **Common mistake:** calling `increment_minor_version()` or
      `increment_subversion()` on a one-part version such as `"1"`. The
      method raises an error rather than pad it. Learners either set
      `"1.0.0"` first or pass `allow_dotted=True`; section 4 lets them see
      the error.
    - **Edits, not just additions (sections 6 and 7).** Most real updates
      reword a question or change its answer categories. Stress the four steps:
      find the item, change it, version it with a rationale, repoint the
      references. Have learners skip the last step once and run `doc.lint()` to
      see the `ddi.reference.integrity` error for themselves.
    - **Wording vs. meaning.** Ask whether a wording change keeps answers
      comparable with last year. If yes, use a sub-version; if not, use a
      major version. The same question applies to a new code list.
    - **Bulk updates (Going further).** This is the realistic case for
      statistical-office staff: a new wave's data file arrives and dozens of
      variables need the same kind of change. Point out that Step 3 is a
      plain dictionary. Learners can keep it in a spreadsheet and load it, so
      subject-matter staff can review the changes before anyone runs the
      loop.
    - **Discussion prompt:** Ask learners how their organization currently
      tracks changes to survey instruments. Compare that process to DDI
      versioning.
