---
description: >-
  Module 4 of the ddi-l course: add variables and link each one to the
  question that collected it.
---

# Module 4: Add variables and link them to questions

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Explain in one sentence what a variable is, using a
      spreadsheet column as the example.
    - **O2.** Write a script that adds a labelled variable for each question
      with `doc.add_variable()` and links it with `question=`, so that
      `doc.validate()` and `doc.lint()` report nothing.
    - **O3.** Count the variables with `len(doc.variables)` and print each
      variable's identifier.
    - **O4.** Explain in two sentences why linking a variable to its question
      matters, using one data column as the example.
    - **O5.** Find a variable's name and its link to its question
      (`<r:QuestionReference>`) in the saved XML.

**Prerequisites:** [Module 3](module-03-first-study.en.md)

**Time:** 30 min self-paced / 40 min instructor-led.

**New in this module:** `doc.add_variable()` (with `name=`, `label=`, and
`question=`), `doc.variables`

---

## 1. What is a variable?

A **variable** is like a column in a spreadsheet. If you have a spreadsheet of
survey results, each column holds one piece of information for every person who
answered the survey. For example:

| Age | HealthRating | SleepHours |
| --: | -----------: | ---------: |
|  19 |            4 |          7 |
|  21 |            3 |          6 |
|  20 |            5 |          8 |

In this table, `Age`, `HealthRating`, and `SleepHours` are the three
variables. Each one stores the answers to one question from the survey.

---

## 2. The connection between questions and variables

Every variable comes from a question. The question asks for information, and
the variable stores the answers.

```text
Question: "What is your age?"   --->   Variable: Age
Question: "Rate your health?"   --->   Variable: HealthRating
Question: "Hours of sleep?"     --->   Variable: SleepHours
```

In DDI, you can **link** a variable to the question that produced it. This
link is stored inside the DDI document so anyone reading the metadata can
follow the chain from a data column back to the exact question that collected
the data.

---

## 3. Add variables linked to questions

Let us continue with the Student Well-Being Survey from Module 3. First,
create the study and add the questions, each with a label as you learned in
Module 3:

```python
import ddi_l as ddi

doc = ddi.new_study(
    title="Student Well-Being Survey",
    agency="university.edu",
)

q1 = doc.add_question(text="What is your age?", label="Age")
q2 = doc.add_question(text="How would you rate your health?", label="Self-rated health")
q3 = doc.add_question(
    text="How many hours do you sleep per night?", label="Hours of sleep"
)
```

Now add three variables. Each one is linked to a question using the
`question=` argument:

```python
v1 = doc.add_variable(name="Age", label="Age in years", question=q1)
v2 = doc.add_variable(
    name="HealthRating", label="Self-rated health, 1 to 5", question=q2
)
v3 = doc.add_variable(name="SleepHours", label="Hours of sleep per night", question=q3)
```

What this does:

- `doc.add_variable()` creates a new variable inside the study.
- `name=` gives the variable a short name, like a column header.
- `label=` gives it a human-readable label, as you did for questions in
  Module 3. Without a label, `doc.lint()` reports a warning.
- `question=` links the variable to the question object that collected the
  data. Notice that you pass the **question object** (like `q1`), not the
  question text string. Passing the text, as in
  `question="What is your age?"`, raises an error.

---

## 4. List all variables

You can count the variables and loop through them, just like you did with
questions:

```python
print(f"Variables: {len(doc.variables)}")
```

Expected output:

```text
Variables: 3
```

To print the identifier of each variable:

```python
for v in doc.variables:
    print(v.identifier)
```

Each variable gets a unique **identifier** (a label assigned by DDI) so it can
be found and referenced inside the document.

---

## 5. Why linking matters

Linking variables to questions creates **traceability**. Traceability means
you can follow the path from any piece of data back to where it came from.

Imagine you are looking at a column called `SleepHours` in a dataset. You
wonder: "What exactly did the survey ask?" Because the variable is linked to
the question, you can look up the question and see: "How many hours do you
sleep per night?"

This is important for:

- **Researchers** who need to understand how data was collected.
- **Archivists** who preserve data for future use.
- **Auditors** who verify that data was collected properly.

Without the link, you would have to guess which question produced which
column. With DDI, the connection is clear and automatic.

---

## 6. Check, save, and inspect

Check your work, as you learned in Module 3, then save the complete document:

```python
print(f"Schema problems: {len(doc.validate())}")
print(f"Lint findings: {len(doc.lint())}")
doc.save("well-being.xml")
```

Expected output:

```text
Schema problems: 0
Lint findings: 0
```

Open `well-being.xml` in a text editor. Look for a variable element. You
should see something like:

```xml
<l:Variable>
  <r:ID>c4eefbc3-...</r:ID>
  <l:VariableName>
    <r:String xml:lang="en">Age</r:String>
  </l:VariableName>
  <r:Label>
    <r:Content xml:lang="en">Age in years</r:Content>
  </r:Label>
  <r:QuestionReference>
    <r:ID>86aed7cf-...</r:ID>
    <r:TypeOfObject>QuestionItem</r:TypeOfObject>
  </r:QuestionReference>
</l:Variable>
```

`<l:VariableName>` holds the name. `<r:QuestionReference>` is the link: the
`<r:ID>` inside it is the identifier of the question `q1`, so a reader can
find the exact question. `ddi-l` created all of this for you.

Cross-reference: [User guide: Add variables](../user-guide.en.md#add-variables)

---

## Exercises

!!! example "Scenario"
    You are continuing your work on the Student Well-Being Survey from
    Module 3. The professor now asks you to define the data columns
    (variables) and connect each one to the question that collected it.

**Exercise 1 (O1).** A first-year student shows you this extract from her
data file:

| StudentID | SleepHours | ExerciseDays |
| --------- | ---------: | -----------: |
| S001      |        6.9 |            7 |
| S002      |        7.6 |            7 |
| S003      |        6.6 |            2 |

Write **one sentence** that explains what a variable is, using `SleepHours`
as your example.

Expected output: one sentence.

??? success "Answer"
    For example: "A variable is one column of a data file, such as
    `SleepHours`, which holds every student's answer to the same question:
    how many hours they sleep per night."

**Exercise 2 (O2).** Build on Module 3. Create the study and add three
questions, each with a label. Then add three variables, each with a label and
linked to its question:

- `Age` linked to the age question.
- `HealthRating` linked to the health question.
- `SleepHours` linked to the sleep question.

Check your work with `doc.validate()` and `doc.lint()`.

Expected output:

```text
Schema problems: 0
Lint findings: 0
```

??? success "Answer"
    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")

    q1 = doc.add_question(text="What is your age?", label="Age")
    q2 = doc.add_question(text="How would you rate your health?", label="Self-rated health")
    q3 = doc.add_question(
        text="How many hours do you sleep per night?", label="Hours of sleep"
    )

    v1 = doc.add_variable(name="Age", label="Age in years", question=q1)
    v2 = doc.add_variable(
        name="HealthRating", label="Self-rated health, 1 to 5", question=q2
    )
    v3 = doc.add_variable(name="SleepHours", label="Hours of sleep per night", question=q3)

    print(f"Schema problems: {len(doc.validate())}")  # -> Schema problems: 0
    print(f"Lint findings: {len(doc.lint())}")  # -> Lint findings: 0
    ```

    If `doc.lint()` reports "Maintainable element is missing a label.", one
    of your questions or variables has no `label=`.

**Exercise 3 (O3).** Print the number of variables, then the identifier of
each variable using a `for` loop.

Expected output: `Variables: 3`, then three unique identifiers, one per line
(yours will differ).

??? success "Answer"
    ```python
    print(f"Variables: {len(doc.variables)}")  # -> Variables: 3
    for v in doc.variables:
        print(v.identifier)
    ```

    Each identifier is a UUID, such as `a1b2c3d4-...`.

**Exercise 4 (O4).** A colleague finds the column `HealthRating`, with values
from 1 to 5, in your data file. Write **two sentences**: what the link from
`HealthRating` to its question tells your colleague, and what could go wrong
if the link were missing.

Expected output: two sentences.

??? success "Answer"
    For example: "The link leads to the question 'How would you rate your
    health?', so my colleague knows the values are each student's own rating
    of their health. Without it, they might guess wrongly, for example that
    the values were measured by a doctor, or that 1 means the best health."

**Exercise 5 (O5).** Save the document with `doc.save("well-being.xml")`.
Open the XML file in a text editor and find the `<l:Variable>` element for
`Age`. Write down:

1. The variable name inside `<l:VariableName>`.
2. The `<r:ID>` inside its `<r:QuestionReference>`.

Then run `print(q1.identifier)` and compare.

Expected output: the name `Age`, and an identifier that matches the one
`print(q1.identifier)` shows.

??? success "Answer"
    ```python
    doc.save("well-being.xml")
    print(q1.identifier)
    ```

    The variable's name is in `<l:VariableName>`:

    ```xml
    <l:VariableName>
      <r:String xml:lang="en">Age</r:String>
    </l:VariableName>
    ```

    The `<r:ID>` inside the `<r:QuestionReference>` a few lines below is the
    same identifier that `print(q1.identifier)` shows. That shared identifier
    is the link from the variable to the question.

---

## Quiz

???+ question "Question 1 (O1): In a table with the columns Age, HealthRating, and SleepHours, which of these is a variable?"
    **A.** The row for the first respondent.

    **B.** The value 4 in the second column.

    **C.** The column `HealthRating`, which holds every respondent's answer
    to one question.

    **D.** The name of the spreadsheet tab.

    ??? success "Answer"
        **C.** A variable is like a column. Each column holds one type of
        information, such as a health rating, for every person in the
        dataset. A row is one person; a value is one answer.

???+ question "Question 2 (O2): What happens when you run `doc.add_variable(name='Age', question='What is your age?')`?"
    **A.** `ddi-l` finds the question by its text and links it.

    **B.** It raises an error, because `question=` expects the question
    object (like `q1`), not the question text.

    **C.** The variable is created with no link to a question.

    **D.** A new question with that text is created.

    ??? success "Answer"
        **B.** `question=` needs the object that `doc.add_question()`
        returned. A plain string is not a question, so the call fails with
        an `AttributeError`. Pass `q1` instead.

???+ question "Question 3 (O2): What does `question=q2` do in `doc.add_variable(name='HealthRating', question=q2)`?"
    **A.** It records, in the DDI document, a reference from the variable to
    the question `q2`.

    **B.** It prints the question text on the screen.

    **C.** It deletes `q2` from the study.

    **D.** It renames the question to `HealthRating`.

    ??? success "Answer"
        **A.** The `question=` argument stores a link between the variable
        and the question that collected the data. You can see it in the XML
        as `<r:QuestionReference>`.

???+ question "Question 4 (O3): Which code prints the identifier of every variable in the study?"
    **A.** `print(doc.variables.identifier)`

    **B.** `doc.list_variables()`

    **C.** `for v in doc.questions: print(v.identifier)`

    **D.** `for v in doc.variables: print(v.identifier)`

    ??? success "Answer"
        **D.** `doc.variables` is a list, so you loop through it and print
        each variable's `identifier`. Option A fails because a list has no
        `identifier`, and option C loops through the questions, not the
        variables.

???+ question "Question 5 (O4): A data user sees the column SleepHours and wants to know exactly what was asked. How does the link from the variable to its question help?"
    **A.** It converts the hours into minutes.

    **B.** The user can follow the link to the question "How many hours do
    you sleep per night?" instead of guessing.

    **C.** It hides the column from users who do not need it.

    **D.** It makes the data file smaller.

    ??? success "Answer"
        **B.** This is traceability: the link takes the user from the data
        column back to the exact question that collected the data.

???+ question "Question 6 (O5): In the saved XML, which element links a variable to the question that collected it?"
    **A.** `<l:VariableName>`

    **B.** `<r:Agency>`

    **C.** `<r:QuestionReference>`

    **D.** `<d:QuestionText>`

    ??? success "Answer"
        **C.** `<r:QuestionReference>` sits inside the `<l:Variable>` element
        and holds the question's identifier. `<l:VariableName>` holds the
        variable's name, and `<d:QuestionText>` belongs to the question
        itself.

---

## Check yourself

- [ ] I can explain in one sentence what a variable is, using a spreadsheet
  column as the example. (O1)
- [ ] I can write a script that adds a labelled variable for each question
  and links it with `question=`, so that `doc.validate()` and `doc.lint()`
  report nothing. (O2)
- [ ] I can count the variables with `len(doc.variables)` and print each
  variable's identifier. (O3)
- [ ] I can explain in two sentences why linking a variable to its question
  matters. (O4)
- [ ] I can find a variable's name and its `<r:QuestionReference>` in the
  saved XML. (O5)

---

!!! tip "Instructor notes"
    - **Visual aid:** Draw this diagram on the board or screen:
      `Question --> Variable --> Data column`. Walk through one example:
      "What is your age?" leads to the variable `Age`, which becomes the
      `Age` column in the spreadsheet.
    - **Common mistake:** Learners sometimes pass the question text (a
      string like `"What is your age?"`) instead of the question object
      (`q1`). Remind them that `question=` expects the object returned by
      `doc.add_question()`, not the text.
    - **Hands-on check:** After Exercises 2 and 3, ask learners to share
      their output. Everyone should see `Lint findings: 0` and
      `Variables: 3`.
    - **Extension activity:** Ask fast finishers to add a fourth question
      and a fourth variable, then check, save, and inspect the updated XML.
    - **Reinforce the concept:** Ask the group: "If you only had the data
      file with no links to questions, how would you know what each column
      means?" This drives home the value of traceability (Exercise 4).
