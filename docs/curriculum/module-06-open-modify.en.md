---
description: >-
  Module 6 of the ddi-l course: open an existing DDI file, inspect and
  change it, validate it on load and save a new copy.
---

# Module 6: Open, modify, and re-save existing DDI files

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Open an existing DDI file with `ddi.open_ddi()` and print how many questions and variables it holds.
    - **O2.** Open a file with `validate=True`, catch the `ddi.DDIValidationError` that a broken file raises, and name the element its message points to.
    - **O3.** Add new items to an opened document, reword an existing question, and code a variable with a code list.
    - **O4.** Save the changed document under a new filename and re-open it to confirm that your changes were kept and the original file is unchanged.
    - **O5.** Predict what happens to XML that `ddi-l` does not model when you open and save a file, and check your prediction.

**Prerequisites:** [Module 5](module-05-concepts-universes.en.md).

**Time:** 30 min self-paced / 40 min instructor-led.

**New in this module:** `ddi.open_ddi()`, `open_ddi(..., validate=True)`, `ddi.DDIValidationError`, `question_texts`, `doc.add_code_list()`, `variable.set_coded()`.

---

## 1. Open an existing file

!!! note "First, get a file to open"
    This module works on a file called `my-study.xml`. If you do not have one
    yet, create it now, or reuse `well-being.xml` from
    [Module 3](module-03-first-study.en.md) and change the filename in the
    examples below.

    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="My Study", agency="example.org")
    doc.add_question(text="What is your age?")
    doc.add_variable(name="Age")
    doc.save("my-study.xml")
    ```

The function `ddi.open_ddi()` reads a DDI XML file from your computer and
gives you a `Document` object. A **Document** is the main object you use to
view and change DDI content.

```python
import ddi_l as ddi

doc = ddi.open_ddi("my-study.xml")
```

The argument is the **path**: the location of the file on your computer.
It can be a simple filename (like `"my-study.xml"`) if the file is in the
same folder as your script, or a full path (like `"/home/user/data/my-study.xml"`).

After this line runs, the variable `doc` holds the entire DDI document in
memory. You can now read its contents or make changes.

---

## 2. Explore what is inside

Once you open a document, you can count and list what it contains. The
`Document` object has properties (shortcuts) for the most common item types:

- `doc.questions`: a list of all questions.
- `doc.variables`: a list of all variables.
- `doc.concepts`: a list of all concepts.
- `doc.universes`: a list of all universes.
- `doc.code_lists`: a list of all code lists.

Here is how to count items and print their identifiers:

```python
doc = ddi.open_ddi("my-study.xml")

print(f"Questions:  {len(doc.questions)}")
print(f"Variables:  {len(doc.variables)}")
print(f"Concepts:   {len(doc.concepts)}")

# Print each question's identifier
for q in doc.questions:
    print(f"  Question: {q.identifier}")

# Print each variable's identifier
for v in doc.variables:
    print(f"  Variable: {v.identifier}")
```

An **identifier** is a unique name that DDI assigns to each item. It is like
a student ID number: no two items share the same one.

---

## 3. Open with validation

You can ask `ddi-l` to check the file against the DDI rules while it loads.
This is called **validation**. If the file has errors, you will see them right
away instead of discovering them later.

```python
doc = ddi.open_ddi("my-study.xml", validate=True)
```

The `validate=True` option tells `open_ddi()` to run the DDI schema check
during loading. A **schema** is a set of rules that says which elements are
allowed and how they must be arranged.

- If the file is valid, `open_ddi()` returns the document as usual.
- If the file breaks a schema rule, `open_ddi()` raises an **exception**: a
  Python error that stops the script unless you catch it. For a schema
  problem the exception is `ddi.DDIValidationError`.

To report the problem instead of stopping, catch the exception with
`try`/`except`:

```python
try:
    doc = ddi.open_ddi("my-study.xml", validate=True)
except ddi.DDIValidationError as error:
    print(f"Not valid: {error}")
```

The message has two parts. The first part names the rule that is broken. The
part in parentheses, after `at`, is the **path** to the element with the problem,
from the root of the file down. For example,
`(at /{ddi:instance:3_3}DDIInstance/{ddi:reusable:3_3}Version)` points to the
`Version` element directly under `DDIInstance`. You can ignore the parts in
curly braces: they name the DDI namespace each element belongs to.

If the file is not even well-formed XML (for example, a closing tag is
missing), `open_ddi()` raises `ddi.DDIParseError` instead, with or without
`validate=True`.

Validating on load is helpful when you receive a file from someone else and
want to make sure it follows the DDI standard before you start working with it.

---

## 4. Add new items to an existing document

You can add questions, variables, concepts, universes, and code lists to an
existing document. The methods are the same ones you used when you created a
new document:

```python
doc = ddi.open_ddi("my-study.xml")

# Add a new question
q = doc.add_question(text="What is your highest level of education?")

# Add a new variable linked to the question
v = doc.add_variable(name="Education", question=q)

# Add a concept
c = doc.add_concept(name="Educational Attainment")

# Add a universe
u = doc.add_universe(name="Adults aged 18 and over")
```

Each `add_*` method returns the new item. You can use that item later, for
example, to link a variable to a question or to set a custom property.

### Edit items that are already there

The items you get back, and the ones in `doc.questions`, `doc.variables` and
the other lists, are live objects. Change a field and the change is saved with
the document. A question keeps its wording in `question_texts`, a list with one
entry per language, so `question_texts[0].text` is the first wording.

A variable can also be **coded**: its values come from a **code list**, the
set of allowed answers to a question (for example "High school", "College",
"University"). Two calls are enough for now:

- `doc.add_code_list(name=...)` creates a new, empty code list in the document
  and returns it.
- `v.set_coded(code_list)` records that the values of variable `v` come from
  that code list. Calling it again with another list switches the variable to
  that list.

[Module 9](module-09-code-lists.en.md) covers code lists in depth, including how
to fill a list with its answers.

```python
# Reword the question added above
q.question_texts[0].text = "What is the highest level of education you have completed?"

# Code the variable with a code list; calling set_coded() again switches lists
levels = doc.add_code_list(name="Education Levels")
v.set_coded(levels)
```

In a published file, an edit like this is a new version of the item.
Later in the course, [Module 15](module-15-update-and-version.en.md#6-change-the-wording-of-a-question)
shows the whole workflow for rewording a question and
[switching a variable to another code list](module-15-update-and-version.en.md#7-switch-a-variable-to-a-different-code-list),
including the version bump and the references you must update.

---

## 5. Save the modified document

After you make changes, save the document to a file. You can save to the same
filename (to overwrite) or to a new filename (to keep both copies).
Your changes live only in memory until you call `doc.save()`.

```python
# Save to a new file; this keeps the original unchanged
doc.save("my-study-updated.xml")
```

It is usually best to save to a **new filename**. That way you always have the
original file as a backup.

```python
# Overwrite the original (use with care)
doc.save("my-study.xml")
```

To confirm that a save worked, open the new file again and count what is
inside, as in Section 2.

---

## 6. The round-trip guarantee

`ddi-l` makes a promise: **it will not delete content it does not
understand.** This is called the **round-trip guarantee**.

DDI XML files can contain many elements. `ddi-l` knows how to read and
write the most common ones (questions, variables, concepts, code lists, and
more). But if the file contains extra elements that `ddi-l` does not
recognize, those elements are kept exactly as they are. They pass through
the read-and-write cycle untouched.

This means you can safely open a file that was created by another tool, add
your metadata, and save it. The parts you did not touch will stay the same.

```text
Original file           ddi-l                  Saved file
┌──────────────┐        ┌────────────┐            ┌──────────────┐
│ Known items  │──────▶ │ Parsed     │──────────▶ │ Known items  │
│ Unknown XML  │──────▶ │ Preserved  │──────────▶ │ Unknown XML  │
└──────────────┘        └────────────┘            └──────────────┘
```

---

## Exercises

!!! example "Scenario"
    An archivist receives a DDI file from a research team. They need to check
    its contents, add missing metadata, validate the file, and save an updated
    copy.

**Exercise 1 (O1).** Create a study with two questions and two variables (or use a
file from an earlier module). Save it to disk. Then re-open it with
`open_ddi()` and print the question and variable counts.

Expected output:

```text
Saved.
Questions: 2
Variables: 2
```

??? success "Answer"
    ```python
    import ddi_l as ddi

    # Create and save
    doc = ddi.new_study(title="Census 2024", agency="stats.example.org")
    q1 = doc.add_question(text="What is your age?")
    q2 = doc.add_question(text="What is your gender?")
    v1 = doc.add_variable(name="Age", question=q1)
    v2 = doc.add_variable(name="Gender", question=q2)
    doc.save("census-2024.xml")
    print("Saved.")

    # Re-open and inspect
    doc2 = ddi.open_ddi("census-2024.xml")
    print(f"Questions: {len(doc2.questions)}")  # -> Questions: 2
    print(f"Variables: {len(doc2.variables)}")  # -> Variables: 2
    ```

**Exercise 2 (O2).** Files from other people are not always valid. Run this
code to make a broken copy of `census-2024.xml`: the first version number
becomes the word `one`.

```python
from pathlib import Path

text = Path("census-2024.xml").read_text(encoding="utf-8")
broken = text.replace("<r:Version>1</r:Version>", "<r:Version>one</r:Version>", 1)
Path("census-2024-broken.xml").write_text(broken, encoding="utf-8")
```

Then:

1. Open `census-2024-broken.xml` with `validate=True`. Catch the
   `ddi.DDIValidationError` and print its message.
2. From the message, name the element that is wrong and say what is wrong
   with it.
3. Open the same file without `validate=True` and print its question count.
   What does this tell you?

Expected output:

```text
Not valid: value doesn't match any pattern of ['[0-9]+(\\.[0-9]+)*'] (at /{ddi:instance:3_3}DDIInstance/{ddi:reusable:3_3}Version)
Opened without checking: 2 questions
```

??? success "Answer"
    ```python
    try:
        ddi.open_ddi("census-2024-broken.xml", validate=True)
    except ddi.DDIValidationError as error:
        print(f"Not valid: {error}")

    unchecked = ddi.open_ddi("census-2024-broken.xml")
    print(f"Opened without checking: {len(unchecked.questions)} questions")
    ```

    The path after `at` points to the `Version` element directly under
    `DDIInstance`. Its value, `one`, does not match the pattern for versions:
    `[0-9]+(\.[0-9]+)*` means digits, optionally followed by more groups of
    a dot and digits, such as `1` or `1.0.0`.

    Without `validate=True`, the broken file opens with no complaint. Only
    validation tells you that the file breaks the DDI rules.

**Exercise 3 (O3).** Work on the document you re-opened in Exercise 1
(`doc2`):

1. Add two new questions and two new variables linked to them
   (MaritalStatus and HouseholdSize).
2. Reword the first question to "What was your age at your last birthday?".
3. Create a code list called "Marital Status Codes" and code the
   MaritalStatus variable with it.
4. Validate the document. If it is valid, save it as
   `census-2024-updated.xml`.

Expected output:

```text
Document is valid.
Saved updated file.
```

??? success "Answer"
    ```python
    q3 = doc2.add_question(text="What is your marital status?")
    q4 = doc2.add_question(text="How many people live in your household?")
    v3 = doc2.add_variable(name="MaritalStatus", question=q3)
    v4 = doc2.add_variable(name="HouseholdSize", question=q4)

    doc2.questions[0].question_texts[0].text = "What was your age at your last birthday?"

    statuses = doc2.add_code_list(name="Marital Status Codes")
    v3.set_coded(statuses)

    errors = doc2.validate()
    if errors:
        print("Validation errors:", errors)
    else:
        print("Document is valid.")
        doc2.save("census-2024-updated.xml")
        print("Saved updated file.")
    ```

**Exercise 4 (O4).** Re-open `census-2024-updated.xml`. Print its question,
variable and code list counts, and the wording of its first question. Then
re-open the original `census-2024.xml` and confirm that it still has two
questions.

Expected output:

```text
Questions: 4
Variables: 4
Code lists: 1
First question: What was your age at your last birthday?
Original questions: 2
```

??? success "Answer"
    ```python
    doc3 = ddi.open_ddi("census-2024-updated.xml")
    print(f"Questions: {len(doc3.questions)}")  # -> Questions: 4
    print(f"Variables: {len(doc3.variables)}")
    print(f"Code lists: {len(doc3.code_lists)}")
    print(f"First question: {doc3.questions[0].question_texts[0].text}")

    original = ddi.open_ddi("census-2024.xml")
    print(f"Original questions: {len(original.questions)}")
    ```

    The counts grew in the new file, and the original kept its two questions:
    saving under a new filename left it untouched.

**Exercise 5 (O5).** A partner's copy of your file contains an element that
`ddi-l` does not model: a description of the units the study covers. Run this
code to make that copy:

```python
from pathlib import Path

text = Path("census-2024.xml").read_text(encoding="utf-8")
extra = (
    '<r:AnalysisUnitsCovered><r:String xml:lang="en">'
    "Persons living in private households"
    "</r:String></r:AnalysisUnitsCovered>"
)
Path("census-2024-partner.xml").write_text(
    text.replace("<d:DataCollection>", extra + "<d:DataCollection>", 1),
    encoding="utf-8",
)
```

Before you go further, write down your prediction in one sentence: if you
open `census-2024-partner.xml`, add a variable called Region, and save it as
`census-2024-partner-updated.xml`, will the saved file still contain
"Persons living in private households"? Then do it, and check by searching the
saved file for that sentence.

Expected output:

```text
True
```

??? success "Answer"
    ```python
    partner = ddi.open_ddi("census-2024-partner.xml", validate=True)
    partner.add_variable(name="Region")
    partner.save("census-2024-partner-updated.xml")

    saved = Path("census-2024-partner-updated.xml").read_text(encoding="utf-8")
    print("Persons living in private households" in saved)  # -> True
    ```

    The element survives: `ddi-l` keeps XML it does not model exactly as it
    was, so opening and saving a file never deletes content you did not
    touch. This is the round-trip guarantee.

---

## Quiz

???+ question "Question 1 (O1): What does this code print for a file with 3 questions and 5 variables?"
    `doc = ddi.open_ddi("survey.xml")`, then
    `print(len(doc.questions), len(doc.variables))`

    **A.** `5 3`

    **B.** `0 0`, because a file must be validated before you can count
    its items.

    **C.** `8`

    **D.** `3 5`

    ??? success "Answer"
        **D.** `ddi.open_ddi()` reads the whole file. `doc.questions` and
        `doc.variables` list its questions and variables, in that order in
        the `print()` call.

???+ question "Question 2 (O2): What is wrong with this file?"
    `ddi.open_ddi("partner.xml", validate=True)` raises a
    `ddi.DDIValidationError` with this message:

    `value doesn't match any pattern of ['[0-9]+(\\.[0-9]+)*'] (at /{ddi:instance:3_3}DDIInstance/{ddi:reusable:3_3}Version)`

    **A.** The file `partner.xml` does not exist.

    **B.** The `Version` element directly under `DDIInstance` holds a value
    that is not a version number such as `1` or `1.0.0`.

    **C.** The file has too many questions.

    **D.** `ddi-l` cannot read DDI 3.3 files.

    ??? success "Answer"
        **B.** The path after `at` names the element: `Version`, under
        `DDIInstance`. The first part of the message says its value does not
        match the pattern for version numbers.

???+ question "Question 3 (O3): Which line codes the variable v with the code list levels?"
    **A.** `levels.set_coded(v)`

    **B.** `doc.add_code_list(v)`

    **C.** `v.set_coded(levels)`

    **D.** `v.code_list = "levels"`

    ??? success "Answer"
        **C.** `set_coded()` is a method of the variable, and it takes the
        code list as its argument. `doc.add_code_list()` creates a new list;
        it does not code a variable.

???+ question "Question 4 (O4): What does my-study.xml contain afterwards?"
    You open `my-study.xml`, add a variable, and close Python without calling
    `doc.save()`.

    **A.** The original content, without the new variable.

    **B.** The original content and the new variable.

    **C.** Nothing: the file is emptied.

    **D.** A backup copy of the original.

    ??? success "Answer"
        **A.** Changes live only in memory until you call `doc.save()`. The
        file on disk is unchanged.

???+ question "Question 5 (O5): What happens to an element that ddi-l does not model?"
    A partner's file contains an element that `ddi-l` does not model. You
    open the file, add a variable, and save it under a new name.

    **A.** It is deleted, because `ddi-l` writes only what it understands.

    **B.** It is moved to the end of the file.

    **C.** It is turned into a note.

    **D.** It is kept unchanged in the saved file.

    ??? success "Answer"
        **D.** This is the round-trip guarantee: content that `ddi-l` does not
        recognize passes through the read-and-write cycle untouched.

---

## Check yourself

- [ ] I can open an existing DDI file with `ddi.open_ddi()` and print how many questions and variables it holds. (O1)
- [ ] I can open a file with `validate=True`, catch `ddi.DDIValidationError`, and name the element its message points to. (O2)
- [ ] I can add items to an opened document, reword a question, and code a variable with a code list. (O3)
- [ ] I can save the changed document under a new filename and re-open it to confirm my changes and the untouched original. (O4)
- [ ] I can predict what happens to XML that `ddi-l` does not model when I open and save a file, and check it. (O5)

---

**See also:**

- [User guide: Open an existing file](../user-guide.en.md#open-an-existing-file)
- [From XML to objects](../tutorials/xml-to-objects.en.md)

---

!!! tip "Instructor notes"
    - **Hands-on first.** Have learners bring a DDI file from a previous
      module. If they do not have one, create a quick file together as a group.
      The goal is to practice the open-modify-save workflow with a real file.
    - **Validate on load.** Demonstrate what happens when you open a broken
      file with `validate=True`. Change a version number to a word, as in
      Exercise 2, to show a schema error (`ddi.DDIValidationError`). Delete a
      closing tag in a text editor to show a parse error
      (`ddi.DDIParseError`), which appears even without `validate=True`.
    - **Round-trip demo.** Exercise 5 adds an element that `ddi-l` does not
      model. Open the saved file in a text editor and show the element in
      place. This builds trust in the tool.
    - **Common mistake:** Learners sometimes forget to save after making
      changes. Remind them that changes live only in memory until `doc.save()`
      is called.
    - **Code lists come later.** This module uses `add_code_list()` and
      `set_coded()` with an empty list. If learners ask how to add the
      answers, point them to Module 9.
    - **Extension activity:** Ask advanced learners to open a file, add items,
      version the study (Module 15, later in the course), and save, combining both modules into
      one workflow.
