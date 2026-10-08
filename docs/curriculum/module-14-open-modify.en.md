# Module 14: Open, Modify, and Re-Save Existing DDI Files

!!! info "What you will learn"
    - Open an existing DDI XML file with `ddi.open_ddi()`.
    - Explore the contents of a loaded document.
    - Open a file with validation turned on.
    - Add new items to an existing document.
    - Save the modified document to a new file.
    - Understand the round-trip guarantee: unknown XML is preserved.

**Prerequisites:** [Module 13: Update and Version Your Documents](module-13-update-and-version.md).

**Time:** 30 min self-paced / 40 min instructor-led.

---

## 1. Open an existing file

!!! note "First, get a file to open"
    This module works on a file called `my-study.xml`. If you do not have one
    yet, create it now, or reuse `household-survey.xml` from
    [Module 6](module-06-csv-to-ddi.md) and change the filename in the
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
- If the file has errors, `open_ddi()` raises an exception (an error message)
  that tells you what is wrong.

This is helpful when you receive a file from someone else and want to make
sure it follows the DDI standard before you start working with it.

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
the document:

```python
# Reword the question added above
q.question_texts[0].text = "What is the highest level of education you have completed?"

# Code the variable with a code list; calling set_coded() again switches lists
levels = doc.add_code_list(name="Education Levels")
v.set_coded(levels)
```

In a published file, an edit like this is a new version of the item.
[Module 13](module-13-update-and-version.md#6-change-the-wording-of-a-question)
shows the whole workflow for rewording a question and
[switching a variable to another code list](module-13-update-and-version.md#7-switch-a-variable-to-a-different-code-list),
including the version bump and the references you must update.

---

## 5. Save the modified document

After you make changes, save the document to a file. You can save to the same
filename (to overwrite) or to a new filename (to keep both copies).

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

**Exercise 1.** Create a study with two questions and two variables (or use a
file from an earlier module). Save it to disk. Then re-open it with
`open_ddi()` and print the question and variable counts.

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
print(f"Questions: {len(doc2.questions)}")
print(f"Variables: {len(doc2.variables)}")
```

Expected output:

```text
Saved.
Questions: 2
Variables: 2
```

**Exercise 2.** Add two new questions and two new variables to the re-opened
document. Validate it. Save to a new filename.

```python
q3 = doc2.add_question(text="What is your marital status?")
q4 = doc2.add_question(text="How many people live in your household?")
v3 = doc2.add_variable(name="MaritalStatus", question=q3)
v4 = doc2.add_variable(name="HouseholdSize", question=q4)

errors = doc2.validate()
if errors:
    print("Validation errors:", errors)
else:
    print("Document is valid.")
    doc2.save("census-2024-updated.xml")
    print("Saved updated file.")
```

**Exercise 3.** Re-open the new file. Verify that the counts increased.

```python
doc3 = ddi.open_ddi("census-2024-updated.xml")
print(f"Questions: {len(doc3.questions)}")
print(f"Variables: {len(doc3.variables)}")
```

Expected output:

```text
Questions: 4
Variables: 4
```

---

## Quiz

???+ question "Question 1: What does ddi.open_ddi() do?"
    **A.** It creates a brand-new, empty DDI document.

    **B.** It reads an existing DDI XML file from disk and returns a Document
    object.

    **C.** It deletes a DDI file from your computer.

    **D.** It sends a DDI file to a web server.

    ??? success "Answer"
        **B.** `ddi.open_ddi()` reads a DDI XML file and returns a `Document`
        object that you can inspect and modify.

???+ question "Question 2: What does validate=True do when you call open_ddi()?"
    **A.** It converts the file to JSON format.

    **B.** It checks the file against the DDI schema rules while loading it.

    **C.** It removes invalid items from the document.

    **D.** It prints the file contents to the screen.

    ??? success "Answer"
        **B.** When you pass `validate=True`, `open_ddi()` runs the DDI schema
        check during loading. If the file has errors, you get an error message
        right away.

???+ question "Question 3: Is existing content lost when you open a file, add items, and save it?"
    **A.** Yes, ddi-l deletes anything it does not understand.

    **B.** Yes, only the new items are saved.

    **C.** No, ddi-l preserves unknown XML elements during round-trip.

    **D.** No, but only if you save to the same filename.

    ??? success "Answer"
        **C.** `ddi-l` preserves unknown XML elements. This is called the
        round-trip guarantee. Content that `ddi-l` does not recognize passes
        through unchanged.

---

**See also:**

- [User guide: Open an existing file](../user-guide.md#open-an-existing-file)
- [From XML to objects](../tutorials/xml-to-objects.md)

---

!!! tip "Instructor notes"
    - **Hands-on first.** Have learners bring a DDI file from a previous
      module. If they do not have one, create a quick file together as a group.
      The goal is to practice the open-modify-save workflow with a real file.
    - **Validate on load.** Demonstrate what happens when you open a broken
      file with `validate=True`. You can create a broken file by editing the
      XML in a text editor and deleting a closing tag.
    - **Round-trip demo.** Open a file that contains extra XML elements (for
      example, `<r:Note>` blocks or custom extensions). Show that those
      elements survive the round-trip. This builds trust in the tool.
    - **Common mistake:** Learners sometimes forget to save after making
      changes. Remind them that changes live only in memory until `doc.save()`
      is called.
    - **Extension activity:** Ask advanced learners to open a file, add items,
      version the study (Module 13), and save, combining both modules into
      one workflow.
