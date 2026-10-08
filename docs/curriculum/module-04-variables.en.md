# Module 4: Add Variables and Link Them to Questions

!!! info "What you will learn"
    - Define what a variable is in DDI.
    - Create variables using `doc.add_variable()`.
    - Link each variable to the question it came from.
    - List variables with `doc.variables`.
    - Explain why linking questions to variables matters.

**Prerequisites:** [Module 3: Create Your First DDI Study](module-03-first-study.md)

**Time:** 30 min self-paced / 40 min instructor-led.

**API taught:** `doc.add_variable(name=, question=)`, `doc.variables`

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
create the study and add the questions:

```python
import ddi_l as ddi

doc = ddi.new_study(
    title="Student Well-Being Survey",
    agency="university.edu",
)

q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")
```

Now add three variables. Each one is linked to a question using the
`question=` argument:

```python
v1 = doc.add_variable(name="Age", question=q1)
v2 = doc.add_variable(name="HealthRating", question=q2)
v3 = doc.add_variable(name="SleepHours", question=q3)
```

What this does:

- `doc.add_variable()` creates a new variable inside the study.
- `name=` gives the variable a short name, like a column header.
- `question=` links the variable to the question object that collected the
  data. Notice that you pass the **question object** (like `q1`), not the
  question text string.

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

## 6. Save and inspect

Save the complete document:

```python
doc.save("well-being.xml")
```

Open `well-being.xml` in a text editor. Look for a variable element. You
should see something like:

```xml
<l:Variable>
  <l:VariableName>
    <r:String>Age</r:String>
  </l:VariableName>
</l:Variable>
```

The XML also contains the reference that links each variable to its question.
`ddi-l` created all of this for you.

Cross-reference: [User guide: Add variables](../user-guide.md#add-variables)

---

## Exercises

!!! example "Scenario"
    You are continuing your work on the Student Well-Being Survey from
    Module 3. The professor now asks you to define the data columns
    (variables) and connect each one to the question that collected it.

**Exercise 1.** Build on Module 3. Create the study, add three questions,
then add three variables linked to those questions:

- `Age` linked to the age question.
- `HealthRating` linked to the health question.
- `SleepHours` linked to the sleep question.

Print the variable count.

```python
import ddi_l as ddi

doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")

q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")

v1 = doc.add_variable(name="Age", question=q1)
v2 = doc.add_variable(name="HealthRating", question=q2)
v3 = doc.add_variable(name="SleepHours", question=q3)

print(f"Variables: {len(doc.variables)}")
```

Expected output:

```text
Variables: 3
```

**Exercise 2.** Print the identifier of each variable using a for loop:

```python
for v in doc.variables:
    print(v.identifier)
```

You should see three unique identifiers printed, one per line.

**Exercise 3.** Save the document with `doc.save("well-being.xml")`. Open the
XML file in a text editor. Can you find a `<l:Variable>` element? Write down
the variable name you see inside the XML.

---

## Quiz

???+ question "Question 1: What does the question= argument do in doc.add_variable()?"
    **A.** It prints the question text on the screen.

    **B.** It links the variable to that question so DDI records the
    connection.

    **C.** It deletes the question from the study.

    **D.** It renames the question.

    ??? success "Answer"
        **B.** The `question=` argument creates a link in the DDI document
        between the variable and the question that collected the data.

???+ question "Question 2: How do you list all variables in a study?"
    **A.** `doc.list_variables()`

    **B.** `doc.get_vars()`

    **C.** `doc.variables`

    **D.** `ddi.variables(doc)`

    ??? success "Answer"
        **C.** `doc.variables` returns the list of all variables in the
        study. You can use `len(doc.variables)` to count them.

???+ question "Question 3: A variable is like a _____ in a spreadsheet."
    **A.** Row

    **B.** Cell

    **C.** Column

    **D.** Sheet name

    ??? success "Answer"
        **C.** A variable is like a column. Each column holds one type of
        information (such as age or income) for every person in the dataset.

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
    - **Hands-on check:** After Exercise 1, ask learners to share their
      output. Everyone should see `Variables: 3`.
    - **Extension activity:** Ask fast finishers to add a fourth question
      and a fourth variable, then save and inspect the updated XML.
    - **Reinforce the concept:** Ask the group: "If you only had the data
      file with no links to questions, how would you know what each column
      means?" This drives home the value of traceability.
