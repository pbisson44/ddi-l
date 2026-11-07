---
description: >-
  Module 9 of the ddi-l course: build code lists and categories, and
  generate them from the values in a data column.
---

# Module 9: Build code lists and controlled vocabularies

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Explain in two sentences what a code list and a category are, and why two surveys that share a code list can be compared.
    - **O2.** Write a script that creates code lists with `doc.add_code_list()` and adds their categories with `doc.add_item(Category, name=...)`.
    - **O3.** Write a loop over `doc.items(Category)` that prints the name of every category, and predict the counts that `len(doc.code_lists)` and `len(doc.items(Category))` return.
    - **O4.** Write a script that reads the distinct values of a CSV column and creates one category for each value.

**Prerequisites:** [Module 8](module-08-csv-to-ddi.en.md).

**Time:** 40 min self-paced / 50 min instructor-led.

**New in this module:** `doc.add_code_list()`, `doc.code_lists`, `Category`, `doc.add_item()`, `doc.items()`, `item.names[0].text`.

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

!!! note "Categories and codes"
    `doc.add_item(Category, ...)` adds the category to the study. It does not
    yet place it inside one particular code list. In this module you build the
    code lists and their categories side by side.
    [Module 14](module-14-custom-fields.en.md) shows how to put each category into
    its list as a **code** (a value such as `1` that points to the category).

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
print(f"Total categories: {len(all_categories)}")  # -> Total categories: 10

for cat in all_categories:
    print(f"  - {cat.names[0].text}")
```

Each item keeps its names in a list called `names`, because an item can have a
name in more than one language. `names[0]` is the first name, and `.text` is its
text. The loop prints `Male`, `Female`, `Other`, and so on, in the order you
added them.

This works for any registered type.
Pass the type you want, and you get back a list of all items of that type.

## 7. Build code lists from CSV column values

In Module 8, you learned to read columns from a CSV file.
You can go further: read the **unique values** in a column and turn them into categories.

This is useful when your data already has coded answers.
The examples use the Module 8 sample file:

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

Without pandas, Python's built-in `csv` module and a `set` do the same job:
a set keeps one copy of each value. Exercise 5 uses that approach.

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

---

## Exercises

1. **(O1)** A colleague asks why the census should reuse the employment status code list from last year's labour survey instead of letting interviewers type each answer. Write your answer in two sentences.

    ??? success "Answer"
        A sample answer: "A code list is the fixed set of allowed answers to a
        question, and each allowed answer (such as Employed or Retired) is a
        category. If the census uses the same code list as the labour survey,
        every answer falls into the same categories in both, so we can count and
        compare them directly instead of cleaning free text such as 'M',
        'emp.' or 'working'."

2. **(O2)** Create a census study with the title "National Census" and agency "census.gc.ca". Add 3 code lists (Gender Codes, Employment Status Codes, Housing Type Codes) and their categories (10 total). Print the counts.

    **Expected output:**

    ```text
    Code lists: 3
    Categories: 10
    ```

    ??? success "Answer"
        ```python
        import ddi_l as ddi
        from ddi_l.models.logicalproduct import Category

        doc = ddi.new_study(title="National Census", agency="census.gc.ca")

        doc.add_code_list(name="Gender Codes")
        doc.add_item(Category, name="Male")
        doc.add_item(Category, name="Female")
        doc.add_item(Category, name="Other")

        doc.add_code_list(name="Employment Status Codes")
        doc.add_item(Category, name="Employed")
        doc.add_item(Category, name="Unemployed")
        doc.add_item(Category, name="Retired")
        doc.add_item(Category, name="Student")

        doc.add_code_list(name="Housing Type Codes")
        doc.add_item(Category, name="House")
        doc.add_item(Category, name="Apartment")
        doc.add_item(Category, name="Other Housing")

        print(f"Code lists: {len(doc.code_lists)}")
        print(f"Categories: {len(doc.items(Category))}")
        ```

3. **(O3)** List all category names. Loop over `doc.items(Category)` and print each category's name.

    **Expected output:**

    ```text
    Male
    Female
    Other
    Employed
    Unemployed
    Retired
    Student
    House
    Apartment
    Other Housing
    ```

    ??? success "Answer"
        ```python
        for cat in doc.items(Category):
            print(cat.names[0].text)
        ```

        The categories come back in the order you added them.

4. **(O2, O3)** The census also asks about marital status. Add a code list "Marital Status Codes" with four categories: Single, Married, Separated, Widowed. **Before you run your script**, write down the two counts it will print. Then run it and check your prediction.

    **Expected output:**

    ```text
    Code lists: 4
    Categories: 14
    ```

    ??? success "Answer"
        ```python
        doc.add_code_list(name="Marital Status Codes")
        for status in ("Single", "Married", "Separated", "Widowed"):
            doc.add_item(Category, name=status)

        print(f"Code lists: {len(doc.code_lists)}")
        print(f"Categories: {len(doc.items(Category))}")
        ```

        One new code list makes 3 + 1 = 4. Four new categories make
        10 + 4 = 14. The counts cover the whole document, not just the list you
        added last.

5. **(O4)** Generate categories from a CSV column's unique values. Read [`survey_sample.csv`](survey_sample.csv){ download="survey_sample.csv" }, get the unique values from the `education_level` column, and create a category for each one.

    **Expected output:**

    ```text
    Education levels: 4
    ```

    ??? success "Answer"
        Python's built-in `csv` module is enough; a `set` keeps one copy of each
        value:

        ```python
        import csv

        with open("survey_sample.csv") as f:
            levels = sorted({row["education_level"] for row in csv.DictReader(f)})

        doc.add_code_list(name="Education Level Codes")
        for level in levels:
            doc.add_item(Category, name=level)

        print(f"Education levels: {len(levels)}")
        ```

        The file has five rows but only four distinct levels, because
        "Bachelor" appears twice. With pandas,
        `df["education_level"].dropna().unique()` gives the same values, as in
        Section 7.

---

## Quiz

???+ question "Question 1 (O1): Why is Survey 2 easier to compare?"
    Survey 1 lets interviewers type employment status as free text. Survey 2
    uses the code list Employed / Unemployed / Retired / Student. Why is
    Survey 2 easier to compare with other surveys?

    **A.** Its data file is smaller.

    **B.** Python needs a code list before it can save a variable.

    **C.** DDI cannot store free-text answers.

    **D.** Every answer is one of a fixed set of categories, so another survey that uses the same code list counts exactly the same answers.

    ??? success "Answer"
        **D.** A code list fixes the allowed answers. Two surveys that share it
        put every answer into the same categories, so their counts line up.
        Free text such as "M", "emp." or "working" has to be cleaned first.

???+ question "Question 2 (O2): Which fix makes this script run?"
    A script calls `doc.add_item(Category, name="Male")` and stops with
    `NameError: name 'Category' is not defined`. Which fix makes it run?

    **A.** Add `from ddi_l.models.logicalproduct import Category` at the top of the script.

    **B.** Replace the call with `doc.add_category(name="Male")`.

    **C.** Call `doc.add_code_list(name="Male")` instead.

    **D.** Put the type in quotes: `doc.add_item("Category", name="Male")`.

    ??? success "Answer"
        **A.** `Category` is a class that you import before you use it.
        `doc.add_category()` does not exist, `add_code_list()` would create a
        code list called "Male", and `add_item()` needs the class itself, not
        its name as a string.

???+ question "Question 3 (O3): What does this script print?"
    ```python
    import ddi_l as ddi
    from ddi_l.models.logicalproduct import Category

    census = ddi.new_study(title="Census", agency="example.org")
    census.add_code_list(name="Yes/No")
    census.add_item(Category, name="Yes")
    census.add_item(Category, name="No")
    census.add_code_list(name="Tenure")
    census.add_item(Category, name="Owner")
    census.add_item(Category, name="Renter")
    census.add_item(Category, name="Other")
    print(len(census.code_lists), len(census.items(Category)))
    ```

    **A.** `2 2`

    **B.** `5 5`

    **C.** `2 5`

    **D.** `7 0`

    ??? success "Answer"
        **C.** The script creates two code lists and five categories.
        `items(Category)` counts every category in the document, whichever list
        you meant it for.

???+ question "Question 4 (O3): Which loop prints the name of every category in `doc`?"
    **A.** `for cat in doc.code_lists: print(cat.names[0].text)`

    **B.** `for cat in doc.items(Category): print(cat.names[0].text)`

    **C.** `for cat in doc.categories: print(cat)`

    **D.** `for cat in doc.items("Category"): print(cat.identifier)`

    ??? success "Answer"
        **B.** `doc.items(Category)` returns every category, and
        `names[0].text` is the first name of each one. Option A prints the code
        list names, `doc.categories` does not exist, and `items()` takes the
        class, not a string.

???+ question "Question 5 (O4): How many categories does a CSV column give?"
    A CSV `gender` column holds Female, Male, Female, (blank), Other, Male. You
    keep one copy of each value, skip the blank, and add one category per value.
    How many categories do you add?

    **A.** 3

    **B.** 4

    **C.** 5

    **D.** 6

    ??? success "Answer"
        **A.** The distinct non-blank values are Female, Male and Other. With
        pandas, `df["gender"].dropna().unique()` returns exactly those three.

---

## Check yourself

- [ ] I can explain in two sentences what a code list and a category are, and why a shared code list makes surveys comparable. (O1)
- [ ] I can write a script that creates code lists with `doc.add_code_list()` and adds categories with `doc.add_item(Category, name=...)`. (O2)
- [ ] I can write a loop over `doc.items(Category)` that prints every category's name, and predict what `len(doc.code_lists)` and `len(doc.items(Category))` return. (O3)
- [ ] I can write a script that turns the distinct values of a CSV column into categories. (O4)

---

!!! tip "Instructor notes"
    - Start by asking: "Have you ever seen a survey with a dropdown menu? That dropdown is a code list."
    - Show a real example: the gender dropdown on a government form. Point out that the choices are fixed. That is a controlled vocabulary.
    - The `add_item()` pattern can feel abstract. Remind learners: "You are telling Python what type to create and what to name it."
    - Exercise 4 asks learners to predict before they run. Collect a few predictions first. A common wrong prediction is `Categories: 4`, from learners who think the count covers only the new list.
    - Exercise 5 connects Module 8 (CSV) to Module 9 (code lists). Faster learners can repeat it for the `gender` column.
    - If learners ask how a category gets inside a particular code list in the DDI XML: each list holds **codes**, and each code points to a category. [Module 14](module-14-custom-fields.en.md) builds them. For now, learners create the lists and the categories side by side.

---

**See also:** [User guide: Code lists](../user-guide.en.md#add-code-lists) | [User guide: Any item type](../user-guide.en.md#work-with-any-item-type)
