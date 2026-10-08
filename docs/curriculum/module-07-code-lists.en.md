# Module 7: Build Code Lists and Controlled Vocabularies

!!! info "What you will learn"
    - Understand what a **code list** is and why it matters.
    - Create code lists with `doc.add_code_list()`.
    - Add categories with `doc.add_item(Category, name=)`.
    - Query all categories with `doc.items(Category)`.
    - Import `Category` from `ddi_l.models.logicalproduct`.
    - Import `Instrument` from `ddi_l.models.datacollection`.
    - Build code lists from CSV column values.

**Prerequisites:** Module 6.

**Time:** 40 min self-paced / 50 min instructor-led.

---

## 1. What is a code list?

A **code list** is a set of allowed answers for a question.
It is also called a **controlled vocabulary**.

For example, the question "What is your gender?" might allow these answers:

- Male
- Female
- Other

That set of three answers is a code list.
Each answer in the list is called a **category**.

## 2. Why code lists matter

Code lists keep your data consistent.
Without them, one person might type "M" and another might type "Male."
The data becomes messy and hard to analyze.

Code lists also make surveys **comparable**.
If two surveys use the same code list for employment status, you can compare their results.

National surveys often share standard code lists so that data from different countries can be combined.

## 3. Create a code list

Use `doc.add_code_list(name=)` to create a new code list.

```python
import ddi_l as ddi

doc = ddi.new_study(title="National Census", agency="census.gc.ca")

cl_gender = doc.add_code_list(name="Gender Codes")
cl_employment = doc.add_code_list(name="Employment Status Codes")
cl_housing = doc.add_code_list(name="Housing Type Codes")

print(f"Code lists: {len(doc.code_lists)}")  # -> Code lists: 3
```

Each call creates one code list and adds it to the document.

## 4. Add categories

A **category** is one allowed answer in a code list.
To add categories, use `doc.add_item()` with the `Category` type.

First, import `Category`:

```python
from ddi_l.models.logicalproduct import Category
```

Then add categories one at a time:

```python
# Gender categories
doc.add_item(Category, name="Male")
doc.add_item(Category, name="Female")
doc.add_item(Category, name="Other")

# Employment status categories
doc.add_item(Category, name="Employed")
doc.add_item(Category, name="Unemployed")
doc.add_item(Category, name="Retired")
doc.add_item(Category, name="Student")

# Housing type categories
doc.add_item(Category, name="House")
doc.add_item(Category, name="Apartment")
doc.add_item(Category, name="Other Housing")

print(f"Categories: {len(doc.items(Category))}")  # -> Categories: 10
```

## 5. The add_item() method

The `add_item()` method is a general tool.
It works for any DDI item type, not just categories.

The pattern is always the same:

<!-- docs-test: skip -- SomeType is a placeholder for any registered item type -->
```python
doc.add_item(SomeType, name="Some Name")
```

You pass the **type** as the first argument and the **name** as a keyword argument.
This is how you add items that do not have their own convenience method like `add_question()` or `add_variable()`.

## 6. Query items by type

Use `doc.items(Category)` to get a list of all categories in the document.

```python
all_categories = doc.items(Category)
print(f"Total categories: {len(all_categories)}")

for cat in all_categories:
    print(f"  - {cat.identifier}")
```

This works for any registered type.
Pass the type you want, and you get back a list of all items of that type.

## 7. Build code lists from CSV column values

In Module 6, you learned to read columns from a CSV file.
You can go further: read the **unique values** in a column and turn them into categories.

This is useful when your data already has coded answers.
The examples use the Module 6 sample file:

[:material-download: Download `survey_sample.csv`](survey_sample.csv){ .md-button download="survey_sample.csv" }

<!-- docs-test: skip -- needs pandas, which ddi-l does not depend on -->
```python
import pandas as pd

df = pd.read_csv("survey_sample.csv")

# Get unique values from the "gender" column
unique_genders = df["gender"].dropna().unique()
print(unique_genders)  # -> ['Female' 'Male' 'Other']

# Create a code list and add one category per unique value
cl = doc.add_code_list(name="Gender Codes")
for val in unique_genders:
    doc.add_item(Category, name=str(val))

print(f"Categories: {len(doc.items(Category))}")
```

The `dropna()` call removes missing values.
The `unique()` call returns only distinct values, with no duplicates.

## 8. Real-world example

National statistical offices use standard code lists for employment classification.
For example, the International Standard Classification of Occupations (ISCO) defines hundreds of job categories.

When multiple countries use the same code list, their employment data can be compared.
This is the power of controlled vocabularies: they make data interoperable.

In `ddi-l`, you build these code lists the same way: one category at a time, or by importing from a data file.

---

!!! example "Scenario"
    You are building metadata for a national census.
    You need code lists for **Gender** (Male, Female, Other),
    **Employment Status** (Employed, Unemployed, Retired, Student),
    and **Housing Type** (House, Apartment, Other).
    You also need to add an Instrument item to represent the questionnaire.

---

## Exercises

1. Create a census study with the title "National Census" and agency "census.gc.ca". Add 3 code lists (Gender Codes, Employment Status Codes, Housing Type Codes) and their categories (10 total). Print the counts.

    **Expected output:**

    ```text
    Code lists: 3
    Categories: 10
    ```

2. List all category names. Loop over `doc.items(Category)` and print each one's identifier.

    ```python
    from ddi_l.models.logicalproduct import Category

    for cat in doc.items(Category):
        print(cat.identifier)
    ```

3. Add an Instrument item to represent the census questionnaire.

    ```python
    from ddi_l.models.datacollection import Instrument

    doc.add_item(Instrument, name="Census Questionnaire")
    print(f"Instruments: {len(doc.items(Instrument))}")
    ```

    **Expected output:**

    ```text
    Instruments: 1
    ```

4. (Bonus) Auto-generate categories from a CSV column's unique values. Read [`survey_sample.csv`](survey_sample.csv){ download="survey_sample.csv" }, get the unique values from the `education_level` column, and create a category for each one.

---

## Quiz

???+ question "Q1: What is a code list?"
    **A.** A Python script.

    **B.** A set of allowed answers for a question.

    **C.** A list of column names.

    **D.** A type of CSV file.

    ??? success "Answer"
        **B.** A code list defines the allowed answers for a question.
        For example, "Male / Female / Other" for gender.

???+ question "Q2: How do you add a category to a document?"
    **A.** `doc.add_category(name="Male")`

    **B.** `doc.add_item(Category, name="Male")`

    **C.** `doc.add_code_list(category="Male")`

    **D.** `Category.add("Male")`

    ??? success "Answer"
        **B.** Use `doc.add_item(Category, name="Male")`. You must
        import `Category` from `ddi_l.models.logicalproduct` first.

???+ question "Q3: How do you get all categories in a document?"
    **A.** `doc.categories`

    **B.** `doc.get_categories()`

    **C.** `doc.items(Category)`

    **D.** `doc.code_lists`

    ??? success "Answer"
        **C.** Use `doc.items(Category)` to get a list of all Category
        items. This works for any registered DDI type.

???+ question "Q4: Why do code lists matter?"
    **A.** They make the file smaller.

    **B.** They are required by Python.

    **C.** They keep data consistent and make surveys comparable.

    **D.** They speed up the computer.

    ??? success "Answer"
        **C.** Code lists prevent messy, inconsistent answers. They also
        let different surveys share the same set of allowed values,
        making data comparable.

---

!!! tip "Instructor notes"
    - Start by asking: "Have you ever seen a survey with a dropdown menu? That dropdown is a code list."
    - Show a real example: the gender dropdown on a government form. Point out that the choices are fixed. That is a controlled vocabulary.
    - The `add_item()` pattern can feel abstract. Remind learners: "You are telling Python what type to create and what to name it."
    - Exercise 4 (bonus) connects Module 6 (CSV) to Module 7 (code lists). It is a great stretch goal for faster learners.
    - If learners ask about linking categories to code lists at the DDI XML level: that is an advanced topic. For now, they just need to know how to create both.

---

**See also:** [User guide: Code lists](../user-guide.md#add-code-lists) | [User guide: Any item type](../user-guide.md#work-with-any-item-type)
