---
description: >-
  Module 5 of the ddi-l course: group variables under concepts and describe
  who a study covers with universes.
---

# Module 5: Organize with concepts and universes

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Explain, in one sentence each, what a **concept** and a **universe** describe, and sort example phrases into concepts and universes.
    - **O2.** Add concepts and a universe to a document with `doc.add_concept()` and `doc.add_universe()`.
    - **O3.** Link each variable to the concept it measures by passing `concept=` to `doc.add_variable()`, and check the link.
    - **O4.** Print the names of all the concepts and universes in a document, using `doc.concepts` and `doc.universes`.

**Prerequisites:** [Module 4](module-04-variables.en.md).

**Time:** 30 min self-paced / 40 min instructor-led.

**New in this module:** `doc.add_concept()`, `doc.add_universe()`, the `concept=` argument of `doc.add_variable()`, `doc.concepts`, `doc.universes`, `concept_references`, `names[0].text`.

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

!!! tip "Concept or universe? A quick test"
    Ask two questions about a phrase:

    - Does it say **what** is measured? Then it is a concept ("Nutrition", "Sleep quality").
    - Does it say **who or what** is measured? Then it is a universe ("Adults aged 18+ in Canada", "Public schools in Ontario").

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

To check a link, look at the variable's `concept_references` list.
Each entry is a **reference**: a pointer that holds the identifier of the
concept. If the identifier matches the concept's, the link is right:

```python
age = doc.variables[0]
print(age.concept_references[0].identifier == demo.identifier)  # -> True
```

A variable added without `concept=` has an empty `concept_references` list.

## 6. List concepts and universes

Use `doc.concepts` and `doc.universes` to see all items in the document.

```python
print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
print(f"Universes: {len(doc.universes)}")  # -> Universes: 1
```

These properties return lists, so you can loop over them.
Each item keeps its name in a list called `names`, with one entry per language.
`names[0].text` is the text of the first name:

```python
for concept in doc.concepts:
    print(concept.names[0].text)
```

Expected output:

```text
Demographics
Physical Activity
Nutrition
```

---

## Exercises

!!! example "Scenario"
    A national health authority surveys adults about diet and exercise.
    They need three concepts: **Nutrition**, **Physical Activity**, and **Demographics**.
    The universe is **Adults aged 18+ in Canada**.
    Your job is to build this structure in code.

**Exercise 1 (O1).** For each phrase below, write "concept" or "universe".
Then write one sentence that explains what a concept describes and one
sentence that explains what a universe describes.

- Nutrition
- Adults aged 18+ in Canada
- Sleep quality
- Public schools in Ontario
- Employment
- Children aged 6 to 11 living in private households

??? success "Answer"
    - Nutrition: concept.
    - Adults aged 18+ in Canada: universe.
    - Sleep quality: concept.
    - Public schools in Ontario: universe.
    - Employment: concept.
    - Children aged 6 to 11 living in private households: universe.

    A concept is the idea that a variable measures, such as "Nutrition".
    A universe is the group of people or things a study covers, such as
    "Adults aged 18+ in Canada".

**Exercise 2 (O2).** Create a document with the title "National Health
Survey" and the agency "health.gc.ca". Add three concepts (Demographics,
Physical Activity, Nutrition) and one universe (Adults aged 18+ in Canada).
Keep each concept in a Python variable: you link to them in Exercise 3.
Print the counts.

**Expected output:**

```text
Concepts: 3
Universes: 1
```

??? success "Answer"
    ```python
    import ddi_l as ddi

    doc = ddi.new_study(title="National Health Survey", agency="health.gc.ca")

    demo = doc.add_concept(name="Demographics")
    activity = doc.add_concept(name="Physical Activity")
    nutrition = doc.add_concept(name="Nutrition")

    doc.add_universe(name="Adults aged 18+ in Canada")

    print(f"Concepts: {len(doc.concepts)}")  # -> Concepts: 3
    print(f"Universes: {len(doc.universes)}")  # -> Universes: 1
    ```

**Exercise 3 (O3).** Continue with the same document.

1. Add four questions:
    - "How old are you?"
    - "What is your weight in kg?"
    - "How many days per week do you exercise?"
    - "How many servings of fruit do you eat per day?"

2. Add four variables. Link each one to its matching concept:
    - Age -> Demographics
    - Weight -> Demographics
    - ExerciseFrequency -> Physical Activity
    - FruitServings -> Nutrition

3. Check that Weight is linked to Demographics, then check the document
   against the schema with `doc.validate()`.

**Expected output:**

```text
Questions: 4
Variables: 4
Weight is linked to Demographics: True
Schema problems: 0
```

??? success "Answer"
    ```python
    q1 = doc.add_question(text="How old are you?")
    q2 = doc.add_question(text="What is your weight in kg?")
    q3 = doc.add_question(text="How many days per week do you exercise?")
    q4 = doc.add_question(text="How many servings of fruit do you eat per day?")

    doc.add_variable(name="Age", question=q1, concept=demo)
    weight = doc.add_variable(name="Weight", question=q2, concept=demo)
    doc.add_variable(name="ExerciseFrequency", question=q3, concept=activity)
    doc.add_variable(name="FruitServings", question=q4, concept=nutrition)

    linked = weight.concept_references[0].identifier == demo.identifier

    print(f"Questions: {len(doc.questions)}")  # -> Questions: 4
    print(f"Variables: {len(doc.variables)}")  # -> Variables: 4
    print(f"Weight is linked to Demographics: {linked}")
    print(f"Schema problems: {len(doc.validate())}")  # -> Schema problems: 0
    ```

**Exercise 4 (O4).** Print the name of every concept and every universe in
the document, under a heading for each kind.

**Expected output:**

```text
Concepts:
  Demographics
  Physical Activity
  Nutrition
Universes:
  Adults aged 18+ in Canada
```

??? success "Answer"
    ```python
    print("Concepts:")
    for concept in doc.concepts:
        print(f"  {concept.names[0].text}")

    print("Universes:")
    for universe in doc.universes:
        print(f"  {universe.names[0].text}")
    ```

---

## Quiz

???+ question "Question 1 (O1): Which phrase is the universe of this study?"
    A report says: "We asked adults aged 18+ in Canada about their sleep
    quality and their stress."

    **A.** Adults aged 18+ in Canada

    **B.** Sleep quality

    **C.** Stress

    **D.** The question "How many hours do you sleep?"

    ??? success "Answer"
        **A.** The universe says who is studied. "Sleep quality" and
        "Stress" say what is measured, so they are concepts. A question is
        neither.

???+ question "Question 2 (O1): Which sentence correctly explains a concept?"
    **A.** A concept is the group of people a study covers.

    **B.** A concept is a list of allowed answers.

    **C.** A concept is the idea a variable measures, such as "Nutrition";
    several variables can share one concept.

    **D.** A concept is a file format for surveys.

    ??? success "Answer"
        **C.** A concept is an abstract idea that variables measure. Option A
        describes a universe, and option B describes a code list.

???+ question "Question 3 (O2): What does this code print?"
    ```python
    doc = ddi.new_study(title="Sleep Study", agency="example.org")
    doc.add_concept(name="Sleep quality")
    doc.add_concept(name="Stress")
    doc.add_universe(name="Adults aged 18+ in Canada")
    print(len(doc.concepts), len(doc.universes))
    ```

    **A.** `3 0`

    **B.** `1 2`

    **C.** `0 0`

    **D.** `2 1`

    ??? success "Answer"
        **D.** Two calls to `doc.add_concept()` add two concepts, and one
        call to `doc.add_universe()` adds one universe.

???+ question "Question 4 (O3): The variable Age is not linked to its concept. Which call fixes it?"
    After `age = doc.add_variable(name="Age", question=q1)`,
    `age.concept_references` is an empty list.

    **A.** `doc.add_variable(name="Age", question=q1, universe=demo)`

    **B.** `doc.add_variable(name="Age", question=q1, concept=demo)`

    **C.** `doc.add_concept(name="Age", variable=q1)`

    **D.** `doc.link(q1, demo)`

    ??? success "Answer"
        **B.** Pass the concept with `concept=` when you call
        `doc.add_variable()`. The other calls do not exist.

???+ question "Question 5 (O4): Which loop prints the name of every universe?"
    **A.** `for u in doc.universes: print(u)`

    **B.** `print(doc.universes.names)`

    **C.** `for u in doc.universes: print(u.names[0].text)`

    **D.** `for u in doc.concepts: print(u.names[0].text)`

    ??? success "Answer"
        **C.** Each universe keeps its name in `names`; `names[0].text` is
        the text. Option A prints the whole object, option B fails because a
        list has no `names`, and option D loops over the concepts.

---

## Check yourself

- [ ] I can explain, in one sentence each, what a concept and a universe describe, and sort phrases into the two. (O1)
- [ ] I can add concepts and a universe with `doc.add_concept()` and `doc.add_universe()`. (O2)
- [ ] I can link a variable to its concept with `concept=` and check the link. (O3)
- [ ] I can print the names of all the concepts and universes in a document. (O4)

---

!!! tip "Instructor notes"
    - Draw a diagram on the board: Concept at the top, with arrows pointing down to its variables. This helps visual learners.
    - Ask the class: "If you had a survey about schools, what would your universe be?" (e.g., "All public schools in Ontario.")
    - Run Exercise 1 as a quick class poll before anyone writes code. The "what versus who" test in Section 2 settles most disagreements.
    - Common mistake: students forget to save the concept object in a variable. Remind them that `doc.add_concept()` returns something they need to keep.
    - Emphasize that concepts and universes are about **describing** the data; they do not change the data itself.

---

**See also:** [User guide: Concepts and universes](../user-guide.en.md#add-concepts-and-universes)
