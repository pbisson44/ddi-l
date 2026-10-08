---
description: >-
  Module 5 of the ddi-l course: group variables under concepts and describe
  who a study covers with universes.
---

# Module 5: Organize with concepts and universes

!!! info "What you will learn"
    - Understand what a **concept** is and why it matters.
    - Understand what a **universe** is and why it matters.
    - Add concepts and universes to a DDI document.
    - Link a variable to a concept.
    - List all concepts and universes in a document.

**Prerequisites:** Module 4.

**Time:** 30 min self-paced / 40 min instructor-led.

---

## 1. What is a concept?

A **concept** is an abstract idea that a variable measures.
Think of it as a label for a group of related variables.

For example, the variable "Age" measures the concept "Demographics."
The variable "Fruit servings per day" measures the concept "Nutrition."

Concepts help you organize your survey.
When someone reads your metadata, they can quickly see which variables belong together.

## 2. What is a universe?

A **universe** is the group of people or things being studied.
It answers the question: "Who does this survey cover?"

For example: "Adults aged 18+ in Canada."

A single survey usually has one universe, but some surveys study more than one group.

## 3. Add concepts

Use `doc.add_concept(name=)` to add a concept to your document.
The method returns a concept object that you can use later.

```python
import ddi_l as ddi

doc = ddi.new_study(title="National Health Survey", agency="health.gc.ca")

demo = doc.add_concept(name="Demographics")
activity = doc.add_concept(name="Physical Activity")
nutrition = doc.add_concept(name="Nutrition")

print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
```

Each call creates one concept and adds it to the document.
We save the return value in a variable so we can link it later.

## 4. Add universes

Use `doc.add_universe(name=)` to add a universe.

```python
doc.add_universe(name="Adults aged 18+ in Canada")

print(f"Universes: {len(doc.universes)}")  # -> Universes: 1
```

The name should clearly describe who is being studied.

## 5. Link a variable to a concept

When you add a variable, you can pass a `concept=` argument.
This links the variable to that concept in the DDI metadata.

```python
q1 = doc.add_question(text="How old are you?")
q2 = doc.add_question(text="How many days per week do you exercise?")
q3 = doc.add_question(text="How many servings of fruit do you eat per day?")

doc.add_variable(name="Age", question=q1, concept=demo)
doc.add_variable(name="Exercise Frequency", question=q2, concept=activity)
doc.add_variable(name="Fruit Servings", question=q3, concept=nutrition)

print(f"Variables: {len(doc.variables)}")  # -> Variables: 3
```

Now each variable is connected to its concept.
Anyone who reads the DDI file can see that "Age" belongs to "Demographics."

## 6. List concepts and universes

Use `doc.concepts` and `doc.universes` to see all items in the document.

```python
print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
print(f"Universes: {len(doc.universes)}")  # -> Universes: 1
```

These properties return lists.
You can loop over them to print names or do other work.

---

!!! example "Scenario"
    A national health authority surveys adults about diet and exercise.
    They need three concepts: **Nutrition**, **Physical Activity**, and **Demographics**.
    The universe is **Adults aged 18+ in Canada**.
    Your job is to build this structure in code.

---

## Exercises

**Exercise 1.** Document a national health survey.

1. Create a health survey document with the title "National Health Survey" and agency "health.gc.ca".

2. Add four questions:
    - "How old are you?"
    - "What is your weight in kg?"
    - "How many days per week do you exercise?"
    - "How many servings of fruit do you eat per day?"

3. Add three concepts: Demographics, Physical Activity, Nutrition.

4. Add one universe: Adults aged 18+ in Canada.

5. Add four variables. Link each one to its matching concept:
    - Age -> Demographics
    - Weight -> Demographics
    - Exercise Frequency -> Physical Activity
    - Fruit Servings -> Nutrition

6. Print the counts:

```python
print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
print(f"Concepts: {len(doc.concepts)}")
print(f"Universes: {len(doc.universes)}")
```

**Expected output:**

```text
Questions: 4
Variables: 4
Concepts: 3
Universes: 1
```

Then check your work: `doc.validate()` should return an empty list.

??? success "Answer"
    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="National Health Survey", agency="health.gc.ca")

    q1 = doc.add_question(text="How old are you?")
    q2 = doc.add_question(text="What is your weight in kg?")
    q3 = doc.add_question(text="How many days per week do you exercise?")
    q4 = doc.add_question(text="How many servings of fruit do you eat per day?")

    demo = doc.add_concept(name="Demographics")
    activity = doc.add_concept(name="Physical Activity")
    nutrition = doc.add_concept(name="Nutrition")

    doc.add_universe(name="Adults aged 18+ in Canada")

    doc.add_variable(name="Age", question=q1, concept=demo)
    doc.add_variable(name="Weight", question=q2, concept=demo)
    doc.add_variable(name="ExerciseFrequency", question=q3, concept=activity)
    doc.add_variable(name="FruitServings", question=q4, concept=nutrition)

    print(f"Questions: {len(doc.questions)}")
    print(f"Variables: {len(doc.variables)}")
    print(f"Concepts: {len(doc.concepts)}")
    print(f"Universes: {len(doc.universes)}")
    print(f"Schema problems: {len(doc.validate())}")
    ```

---

## Quiz

???+ question "Q1: What is a concept?"
    **A.** A file format for surveys.

    **B.** An abstract idea that a variable measures.

    **C.** A list of allowed answers.

    **D.** The group of people being studied.

    ??? success "Answer"
        **B.** A concept is an abstract idea, like "Demographics" or
        "Nutrition." Variables measure concepts.

???+ question "Q2: What is a universe?"
    **A.** The software that runs the survey.

    **B.** A type of variable.

    **C.** The group of people or things being studied.

    **D.** A list of questions.

    ??? success "Answer"
        **C.** The universe tells you who the survey covers, for
        example, "Adults aged 18+ in Canada."

???+ question "Q3: How do you link a variable to a concept?"
    **A.** `doc.add_concept(variable=v)`

    **B.** `doc.add_variable(name="Age", concept=age_concept)`

    **C.** `doc.link(variable, concept)`

    **D.** `variable.set_concept(concept)`

    ??? success "Answer"
        **B.** Pass the `concept=` argument when you call
        `doc.add_variable()`.

---

!!! tip "Instructor notes"
    - Draw a diagram on the board: Concept at the top, with arrows pointing down to its variables. This helps visual learners.
    - Ask the class: "If you had a survey about schools, what would your universe be?" (e.g., "All public schools in Ontario.")
    - Common mistake: students forget to save the concept object in a variable. Remind them that `doc.add_concept()` returns something they need to keep.
    - Emphasize that concepts and universes are about **describing** the data; they do not change the data itself.

---

**See also:** [User guide: Concepts and universes](../user-guide.md#add-concepts-and-universes)
