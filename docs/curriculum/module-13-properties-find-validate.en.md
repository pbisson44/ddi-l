---
description: >-
  Module 13 of the ddi-l course: attach custom properties, find and remove
  items by identifier, and validate before saving.
---

# Module 13: Custom properties, find, remove, and validate

!!! info "What you will learn"
    - Attach custom key-value properties to any DDI item.
    - Read and remove properties.
    - Find items by their unique identifier.
    - Remove items from a document.
    - Validate a document against the DDI schema.
    - Use the validate-fix-validate loop before publishing.

**Prerequisites:** [Module 12: Data linkage](module-12-data-linkage.md).

**Time:** 40 min self-paced / 50 min instructor-led.

---

## 1. Custom properties

Every DDI item can carry extra information as **custom properties**.
A property is a **key-value pair**: a name and a value, like a label on a box.

For example, you might tag a question with:

- `"sensitivity"` = `"high"` (this question asks about private information)
- `"data_source"` = `"administrative records"` (this data comes from government files)

Properties let your team add notes and tags that the DDI standard does not have built-in fields for.

## 2. Set a property

Use `item.set_property(key, value)` to add a property to any item.

```python
import ddi_l as ddi

doc = ddi.new_study(title="Household Survey", agency="survey.gc.ca")

q_age = doc.add_question(text="How old are you?")
q_income = doc.add_question(text="What is your household income?")
q_name = doc.add_question(text="What is your full name?")

# Tag the income question as high sensitivity
q_income.set_property("sensitivity", "high")

# Tag the name question too
q_name.set_property("sensitivity", "high")
q_name.set_property("data_source", "self-reported")
```

You can set as many properties as you need on any item.

## 3. Read properties

Use `item.get_property(key)` to read one property.
It returns the value as a string, or `None` if the key does not exist.

```python
print(q_income.get_property("sensitivity"))  # -> high
print(q_age.get_property("sensitivity"))  # -> None
```

Use `item.properties` to get all properties as a dictionary.

```python
print(q_name.properties)
# -> {'sensitivity': 'high', 'data_source': 'self-reported'}
```

A **dictionary** (also called a dict) is a Python data structure that maps keys to values.

## 4. Remove a property

Use `item.remove_property(key)` to delete a property.
It returns `True` if the property was found and removed, or `False` if the key was not there.

```python
removed = q_name.remove_property("data_source")
print(removed)  # -> True
print(q_name.properties)  # -> {'sensitivity': 'high'}
```

## 5. Advanced: Pass a code list as a property value

You can pass a code list object (or any DDI item) as the value.
The library stores the item's **URN** (Uniform Resource Name) automatically.

A URN is a unique address that identifies the item.

```python
cl = doc.add_code_list(name="Income Brackets")
q_income.set_property("vocabulary", cl)

print(q_income.get_property("vocabulary"))
# Prints the URN string of the code list
```

This is useful when you want to link a question to the code list that defines its allowed answers.

## 6. Find items by identifier

Every item in a DDI document gets a unique **identifier** when it is created.
Think of it as a serial number.

Use `doc.find(identifier)` to look up any item by its identifier.

```python
v1 = doc.add_variable(name="Age", question=q_age)

# Save the identifier
age_id = v1.identifier
print(f"Identifier: {age_id}")

# Find it later
found = doc.find(age_id)
print(found)  # Prints the Variable object
```

If no item matches, `doc.find()` returns `None`.

## 7. Remove items

Use `doc.remove(identifier)` to delete an item from the document.
It returns `True` if the item was found and removed.

```python
print(f"Questions before: {len(doc.questions)}")  # -> 3

# Remove the name question
doc.remove(q_name.identifier)

print(f"Questions after: {len(doc.questions)}")  # -> 2
```

Be careful: removing is permanent.
There is no undo.

## 8. Validate the document

Use `doc.validate()` to check the document against the **DDI schema**.
A schema is a set of rules that defines what a valid DDI file looks like.

```python
issues = doc.validate()

if issues:
    for issue in issues:
        print(f"Problem: {issue.message}")
else:
    print("Document is valid!")
```

The method returns a list of issues.
If the list is empty, the document is valid.

## 9. The validate-fix-validate loop

Before you publish or share a DDI file, follow this loop:

1. **Create** your document (add questions, variables, concepts, etc.).
2. **Validate** it with `doc.validate()`.
3. **Fix** any problems that come up.
4. **Validate again** to make sure the fixes worked.
5. **Save** the final file.

```python
# Step 1: Create
doc = ddi.new_study(title="Household Survey", agency="survey.gc.ca")
q = doc.add_question(text="How old are you?")
doc.add_variable(name="Age", question=q)

# Step 2: Validate
issues = doc.validate()
print(f"Issues found: {len(issues) if issues else 0}")

# Step 3: Fix any problems (if needed)
# ... make changes here ...

# Step 4: Validate again
issues = doc.validate()
if not issues:
    print("All clear!")

# Step 5: Save
doc.save("household-survey.xml")
print("Saved!")
```

Always validate before sharing your file.
It is much easier to fix problems before others depend on your metadata.

---

!!! example "Scenario"
    A survey team is preparing a household survey for publication.
    They need to tag some questions with sensitivity levels and data sources.
    Before publishing, they must validate the document, fix any issues, and save a clean file.
    Your job is to use properties, find, remove, and validate to get the document ready.

---

## Exercises

1. Create a study with 3 questions: "How old are you?", "What is your household income?", and "What is your full name?". Set `"sensitivity"` = `"high"` on the income question. Print its properties.

    **Expected output:**

    ```text
    {'sensitivity': 'high'}
    ```

    ??? success "Answer"
        ```python
        import ddi_l as ddi

        doc = ddi.new_study(title="Household Survey", agency="research.org")
        q_age = doc.add_question(text="How old are you?")
        q_income = doc.add_question(text="What is your household income?")
        q_name = doc.add_question(text="What is your full name?")

        q_income.set_property("sensitivity", "high")
        print(q_income.properties)  # -> {'sensitivity': 'high'}
        ```

2. Add a variable for the age question. Find it by its identifier. Print the identifier.

    ??? success "Answer"
        ```python
        v = doc.add_variable(name="Age", question=q_age)
        found = doc.find(v.identifier)
        print(f"Found: {found.identifier}")
        ```

3. Remove one question from the document. Print the new count to verify it dropped.

    **Expected output:**

    ```text
    Questions: 2
    ```

    ??? success "Answer"
        ```python
        doc.remove(q_name.identifier)
        print(f"Questions: {len(doc.questions)}")
        ```

4. Validate the document. Print whether it is valid.

    ??? success "Answer"
        ```python
        issues = doc.validate()
        if issues:
            for issue in issues:
                print(f"Problem: {issue.message}")
        else:
            print("Document is valid!")
        ```

---

## Quiz

???+ question "Q1: What does set_property do?"
    **A.** Creates a new variable.

    **B.** Attaches a key-value pair to a DDI item.

    **C.** Saves the document to a file.

    **D.** Deletes a property from an item.

    ??? success "Answer"
        **B.** `set_property(key, value)` attaches a custom key-value
        pair to any DDI item. For example,
        `q.set_property("sensitivity", "high")`.

???+ question "Q2: How do you read all properties on an item?"
    **A.** `item.get_property()`

    **B.** `item.all_properties()`

    **C.** `item.properties`

    **D.** `doc.properties(item)`

    ??? success "Answer"
        **C.** Use `item.properties` (no parentheses; it is a
        property, not a method). It returns a dictionary of all
        key-value pairs.

???+ question "Q3: What does doc.find(identifier) return?"
    **A.** A list of all items.

    **B.** The item with that identifier, or None if not found.

    **C.** A True/False value.

    **D.** The identifier string itself.

    ??? success "Answer"
        **B.** `doc.find(identifier)` searches all item types and
        returns the matching item. If nothing matches, it returns
        `None`.

???+ question "Q4: What does doc.validate() do?"
    **A.** Saves the document.

    **B.** Deletes invalid items.

    **C.** Checks the document against the DDI schema and returns a
    list of issues.

    **D.** Adds missing fields automatically.

    ??? success "Answer"
        **C.** `validate()` checks whether the document follows the DDI
        rules. It returns a list of issues. An empty list means the
        document is valid.

???+ question "Q5: What does doc.remove(identifier) do?"
    **A.** Removes a property from an item.

    **B.** Deletes the XML file from disk.

    **C.** Removes the item with that identifier and returns True, or
    returns False if not found.

    **D.** Removes all items from the document.

    ??? success "Answer"
        **C.** `doc.remove(identifier)` finds the item with that
        identifier, removes it from the document, and returns `True`.
        If no item has that identifier, it returns `False`.

---

!!! tip "Instructor notes"
    - Properties are the most flexible part of the API. Emphasize that they are for team-specific metadata that DDI does not have a built-in field for.
    - The `find()` and `remove()` methods work with identifiers, not names. Remind learners to save the identifier when they create an item.
    - The validate-fix-validate loop is a professional habit. Compare it to spell-checking a document before sending it.
    - Common mistake: learners forget that `properties` is a property (no parentheses), while `get_property()` and `set_property()` are methods (with parentheses).
    - If learners ask about the URN in the advanced properties section: explain that a URN is like a web address for a DDI item. It lets other systems find the item. They do not need to memorize the format.
    - This module ties together everything from Modules 5 and 8-11. Consider ending with a mini-project: build a complete document with questions, variables, concepts, code lists, and properties, then validate and save.

---

**See also:** [Validation guide](../validation.md)
