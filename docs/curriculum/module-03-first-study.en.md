---
description: >-
  Module 3 of the ddi-l course: create a DDI study, add questions in two
  languages, save it as XML and check it with validate and lint.
---

# Module 3: Create your first DDI study

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Write a script that creates a study with `ddi.new_study()` and
      adds three questions with `doc.add_question()`.
    - **O2.** Count the questions in a study with `len(doc.questions)` and
      print each question's identifier.
    - **O3.** Save the study to an XML file with `doc.save()` and find a
      question's text in the saved file.
    - **O4.** Add a French version of an existing question's text and label,
      so that one question holds both languages.
    - **O5.** Check a study with `doc.validate()` and `doc.lint()`, and fix
      the lint warnings until both report nothing.

**Prerequisites:** [Module 2](module-02-setup.en.md)

**Time:** 30 min self-paced / 45 min instructor-led.

**New in this module:** `ddi.new_study()`, `doc.add_question()`,
`doc.questions`, `doc.save()`, `InternationalString`, `doc.validate()`,
`doc.lint()`

---

## 1. What is a "study" in DDI?

A **study** is a container that holds all the information about one survey or
research project. Think of it like a folder that keeps everything together:
the title, the organization that ran the survey, the questions that were asked,
and the data that was collected.

In `ddi-l`, you create a study first, and then you add items (like questions
and variables) to it.

---

## 2. Create a study

Open a Python session or create a new script file. Type the following:

```python
import ddi_l as ddi

doc = ddi.new_study(
    title="Student Well-Being Survey",
    agency="university.edu",
)
```

What this does:

- `import ddi_l as ddi` loads the `ddi-l` package and gives it the short
  name `ddi`.
- `ddi.new_study()` creates a new DDI document. It returns a **Document**
  object, which we store in the variable called `doc`.
- `title=` sets the name of the study.
- `agency=` sets the organization responsible for the study. It is required:
  without it, `ddi.new_study()` raises a `TypeError`.

---

## 3. What is an "agency"?

An **agency** is the organization responsible for the study. It could be a
university, a government department, a research institute, or any group that
runs the survey. Its **agency ID** goes into every item it creates, beside the
item's own identifier and version, so that together they name the item.

- **Registered.** So that no two organizations share an agency ID, each
  registers its own with the
  [DDI Agency ID Registry](https://ddialliance.org/ddi-agency-id-registry).
  It can then add sub-agencies after a dot, for example one per division.
- **Format.** Letters, digits and hyphens, in parts joined by dots, each part
  at most 63 characters. `doc.validate()` checks the format, not whether the
  ID is registered.
- **In this course.** IDs such as `"university.edu"` and
  `"stats.example.org"` are made up. In a real document, use the ID your
  organization registered.

---

## 4. Add questions

A survey asks questions. In DDI, each question is stored as a separate item.
Let us add three questions to our study:

```python
q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")
```

Each call to `doc.add_question()` creates a new question inside the study and
returns a **question object**. We save each object in a variable (`q1`, `q2`,
`q3`) so we can use it later, for example, to link a variable to it.

---

## 5. Questions in more than one language

Many surveys are conducted in more than one language. For example, a Canadian
survey might be in both English and French. DDI can store the same question in
multiple languages inside a single document.

Every `add_question()` call accepts a `lang=` argument. The default is
`lang="en"` (English), so the questions you added above are in English. To
create a question in French, pass `lang="fr"`, as in
`doc.add_question(text="Quel est votre âge ?", lang="fr")`.

To add a French translation of the same question, append it to the
question's `question_texts` list:

```python
from ddi_l.models.base import InternationalString

q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
```

An `InternationalString` is a piece of text together with its language code
(`"en"`, `"fr"`, and so on). Now `q1` contains the question text in both
English and French. When someone opens the DDI file, they can see both
versions.

The `lang=` argument works on all `add_*` methods: `add_variable()`,
`add_concept()`, `add_universe()`, and `add_code_list()`. You can also append
translations to their `names` list the same way. Module 8 shows a complete
bilingual workflow.

---

## 6. Check your questions

You can see how many questions the study contains:

```python
print(f"Questions: {len(doc.questions)}")
```

Expected output:

```text
Questions: 3
```

You can also loop through all the questions and print their identifiers:

```python
for q in doc.questions:
    print(q.identifier)
```

An **identifier** is a unique label that DDI assigns to each item. It helps
you find and refer to specific items in the document.

---

## 7. Save to XML

To save your study to a file, use the `save()` method:

```python
doc.save("well-being.xml")
```

This creates a file called `well-being.xml` in your current folder. The file
contains your study in DDI XML format, a structured text format that follows
the DDI standard.

---

## 8. Look inside the XML

Open `well-being.xml` in a text editor (such as Notepad, VS Code, or any
plain-text editor). You will see XML tags: words wrapped in angle brackets
like `<QuestionItemName>`.

Look for the text of your first question. You should find something like:

```xml
<d:QuestionText>
  <d:LiteralText>
    <d:Text>What is your age?</d:Text>
  </d:LiteralText>
</d:QuestionText>
```

You do not need to understand all the XML. The point is that `ddi-l` turned
your five lines of Python into a complete, standards-compliant DDI document.

Cross-reference: [User guide: Create a study](../user-guide.en.md#create-a-study)

---

## 9. Check your work

Get into the habit of checking a study before you share it. `ddi-l` runs two
kinds of check:

- **Validation** compares the document with the DDI **schema**: the official
  rules for which elements are allowed, where they go, and which ones are
  required. A document that fails validation is not valid DDI.
- **Linting** looks for problems the schema allows but that are usually
  mistakes, such as an item with no label.

```python
issues = doc.validate()
print(f"Schema problems: {len(issues)}")

findings = doc.lint()
print(f"Lint findings: {len(findings)}")
for finding in findings:
    print(f"  [{finding.severity}] {finding.message}")
```

Expected output:

```text
Schema problems: 0
Lint findings: 3
  [warning] Maintainable element is missing a label.
  [warning] Maintainable element is missing a label.
  [warning] Maintainable element is missing a label.
```

The study is valid DDI. The three warnings say that your questions have no
**label**: a short name that catalogues and other tools show instead of the
full question text. Add a label to each question and check again:

```python
q1.labels.append(InternationalString(text="Age", lang="en"))
q2.labels.append(InternationalString(text="Self-rated health", lang="en"))
q3.labels.append(InternationalString(text="Hours of sleep", lang="en"))

print(f"Lint findings: {len(doc.lint())}")
doc.save("well-being.xml")
```

Expected output:

```text
Lint findings: 0
```

A label can have more than one language, just like the question text. Append
a French label to the same `labels` list:

```python
q1.labels.append(InternationalString(text="Âge", lang="fr"))
```

When you add a new item, you can give it a label straight away. Every `add_*`
method accepts `label=`:

```python
q4 = doc.add_question(text="Do you exercise every week?", label="Weekly exercise")
```

Warnings do not make a document invalid; schema errors do. Check your work
like this at the end of every module. [Module 7](module-07-cli-validation.en.md)
runs the same checks from the command line.

---

## Exercises

!!! example "Scenario"
    You are a research assistant. Your professor asks you to document a
    Student Well-Being Survey with three questions about age, health, and
    sleep. You will use `ddi-l` to create the documentation.

**Exercise 1 (O1, O2).** Create a study titled `"Student Well-Being Survey"`
with agency `"university.edu"`. Add three questions:

1. `"What is your age?"`
2. `"How would you rate your health?"`
3. `"How many hours do you sleep per night?"`

Print the question count, then the identifier of each question. Save the
study as `well-being.xml`.

Expected output: `Questions: 3`, then three identifiers, one per line (yours
will differ).

```text
Questions: 3
4f0c9a5e-...
9b1d2e7c-...
c3a8f610-...
```

??? success "Answer"
    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")

    q1 = doc.add_question(text="What is your age?")
    q2 = doc.add_question(text="How would you rate your health?")
    q3 = doc.add_question(text="How many hours do you sleep per night?")

    print(f"Questions: {len(doc.questions)}")  # -> Questions: 3
    for q in doc.questions:
        print(q.identifier)

    doc.save("well-being.xml")
    ```

**Exercise 2 (O3).** Open `well-being.xml`, the file you saved in
Exercise 1, in a text editor. Find the text of your first question inside the
XML. Write down the XML tag that wraps the question text.

Expected output: the name of one XML tag.

??? success "Answer"
    The question text sits in a `<d:Text>` element, inside `<d:LiteralText>`
    inside `<d:QuestionText>`:

    ```xml
    <d:Text xml:lang="en" isPlainText="true">What is your age?</d:Text>
    ```

**Exercise 3 (O5).** Continue from Exercise 1. Check the study with
`doc.validate()` and `doc.lint()`, and print how many problems each reports.
Then give each question an English label (`"Age"`, `"Self-rated health"`,
`"Hours of sleep"`), check again, and save.

Expected output:

```text
Schema problems: 0
Lint findings: 3
Lint findings: 0
```

??? success "Answer"
    ```python
    from ddi_l.models.base import InternationalString

    print(f"Schema problems: {len(doc.validate())}")  # -> Schema problems: 0
    print(f"Lint findings: {len(doc.lint())}")  # -> Lint findings: 3

    q1.labels.append(InternationalString(text="Age", lang="en"))
    q2.labels.append(InternationalString(text="Self-rated health", lang="en"))
    q3.labels.append(InternationalString(text="Hours of sleep", lang="en"))

    print(f"Lint findings: {len(doc.lint())}")  # -> Lint findings: 0
    doc.save("well-being.xml")
    ```

    The three warnings were "Maintainable element is missing a label.", one
    per question. A label fixes each one.

**Exercise 4 (O4).** Add French to the first question: the text
`"Quel est votre âge ?"` and the label `"Âge"`. Do not create a new question.
Print the question count and the lint count, save the file again, and check
the XML for both languages.

Expected output:

```text
Questions: 3
Lint findings: 0
```

In the XML, the first question has `xml:lang="en"` and `xml:lang="fr"`
entries for both its label and its text.

??? success "Answer"
    ```python
    q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
    q1.labels.append(InternationalString(text="Âge", lang="fr"))

    print(f"Questions: {len(doc.questions)}")  # -> Questions: 3
    print(f"Lint findings: {len(doc.lint())}")  # -> Lint findings: 0
    doc.save("well-being.xml")
    ```

    The count stays at 3 because both translations belong to `q1`. In the
    XML, the first question now reads:

    ```xml
    <r:Label>
      <r:Content xml:lang="en">Age</r:Content>
      <r:Content xml:lang="fr">Âge</r:Content>
    </r:Label>
    <d:QuestionText>
      <d:LiteralText>
        <d:Text xml:lang="en" isPlainText="true">What is your age?</d:Text>
      </d:LiteralText>
      <d:LiteralText>
        <d:Text xml:lang="fr">Quel est votre âge ?</d:Text>
      </d:LiteralText>
    </d:QuestionText>
    ```

---

## Quiz

???+ question "Question 1 (O1): You run `doc = ddi.new_study(title='Sleep Survey')` and get a TypeError. Why?"
    **A.** The title is too short.

    **B.** `agency=` is missing. Every study needs the organization
    responsible for it.

    **C.** You must import `InternationalString` first.

    **D.** `new_study()` takes no arguments.

    ??? success "Answer"
        **B.** `ddi.new_study()` requires both `title=` and `agency=`. The
        error message says so: "missing 1 required keyword-only argument:
        'agency'".

???+ question "Question 2 (O1): After `q1 = doc.add_question(text='What is your age?')`, what is `q1`?"
    **A.** The string `"What is your age?"`.

    **B.** The number of questions in the study.

    **C.** A question object stored in the study, which you can use later,
    for example to translate it or to link a variable to it.

    **D.** The XML text of the question.

    ??? success "Answer"
        **C.** `doc.add_question()` adds a question item to the study and
        returns that question object. Keeping it in a variable lets you work
        with it later.

???+ question "Question 3 (O2): A study has three questions. You add a fourth with `doc.add_question()`, then run `print(len(doc.questions))`. What is printed?"
    **A.** `4`

    **B.** `3`

    **C.** `1`

    **D.** An error, because `doc.questions` is not a list.

    ??? success "Answer"
        **A.** `doc.questions` is the list of every question in the study,
        and `len()` counts them: three plus the new one.

???+ question "Question 4 (O3): You open the file written by `doc.save('well-being.xml')`. Where do you find the text of your first question?"
    **A.** In a `<d:Text>` element inside `<d:QuestionText>`.

    **B.** Only in the file name.

    **C.** In the `<r:Agency>` element.

    **D.** Nowhere: `save()` writes only the study title.

    ??? success "Answer"
        **A.** `doc.save()` writes the whole study, and each question's text
        sits in `<d:Text>`, inside `<d:LiteralText>`, inside
        `<d:QuestionText>`.

???+ question "Question 5 (O4): You want the first question, `q1`, in both English and French. Which line does it?"
    **A.** `doc.add_question(text="Quel est votre âge ?", lang="fr")`

    **B.** `q1.lang = "fr"`

    **C.** `q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))`

    **D.** None: DDI cannot store more than one language in one question.

    ??? success "Answer"
        **C.** Appending an `InternationalString` with the new language
        stores both versions in the same question item. Option A creates a
        brand-new, separate question, not a translation of `q1`.

???+ question "Question 6 (O5): `doc.validate()` returns an empty list, but `doc.lint()` reports warnings. Is the document valid DDI?"
    **A.** No. Any finding makes a document invalid.

    **B.** Only after you save it.

    **C.** It depends on the language of the questions.

    **D.** Yes. Validation checks the schema; lint warnings point to quality
    problems, such as a missing label, that the schema allows.

    ??? success "Answer"
        **D.** An empty list from `doc.validate()` means the document follows
        the DDI schema. Lint warnings are worth fixing, but they do not make
        the document invalid.

???+ question "Question 7 (O5): `doc.lint()` reports 'Maintainable element is missing a label.' once for each of your three questions. Which change clears the warnings?"
    **A.** Save the document again with `doc.save()`.

    **B.** Give each question a label, for example
    `q1.labels.append(InternationalString(text="Age", lang="en"))`, or pass
    `label=` when you call `doc.add_question()`.

    **C.** Delete the questions and add them again with the same code.

    **D.** Call `doc.validate()` before `doc.lint()`.

    ??? success "Answer"
        **B.** The warning names the problem: the questions have no label.
        Saving or validating does not change the document, and adding the
        questions again with the same code brings the same warnings back.

---

## Check yourself

- [ ] I can write a script that creates a study with `ddi.new_study()` and
  adds three questions with `doc.add_question()`. (O1)
- [ ] I can count the questions with `len(doc.questions)` and print each
  question's identifier. (O2)
- [ ] I can save the study with `doc.save()` and find a question's text in
  the XML file. (O3)
- [ ] I can add a French version of an existing question's text and label
  without creating a new question. (O4)
- [ ] I can check a study with `doc.validate()` and `doc.lint()` and fix the
  lint warnings until both report nothing. (O5)

---

!!! tip "Instructor notes"
    - **This is the "aha" module.** Five lines of Python create a real,
      standards-compliant XML document. Demo it live to make the impact clear.
    - **Live coding:** Type the code on screen, line by line. Let learners
      follow along. Pause after each step to let people catch up.
    - **Common mistake:** Learners often forget the quotes around strings.
      For example, they type `text=What is your age?` instead of
      `text="What is your age?"`. Watch for this during exercises.
    - **Common mistake:** In Exercise 4, some learners call
      `doc.add_question(..., lang="fr")`. Ask them to print
      `len(doc.questions)`: a count of 4 shows they created a second
      question instead of translating the first.
    - **Explore the XML together:** Open the saved file on screen and scroll
      through it. Point out the question text inside the tags. Emphasize that
      learners did not need to write any of this XML by hand.
    - **Extension activity:** Ask fast finishers to add two more questions of
      their own, each with a `label=`, then check with `doc.lint()` and save
      the file again.
