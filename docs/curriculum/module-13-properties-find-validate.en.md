---
description: >-
  Module 13 of the ddi-l course: attach custom properties, find and remove
  items by identifier, and validate before saving.
---

# Module 13: Custom properties, find, remove, and validate

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Add, read and remove custom properties on a DDI item with
      `set_property()`, `get_property()`, `properties` and `remove_property()`.
    - **O2.** Find an item by its identifier with `doc.find()`, and predict
      what `doc.find()` returns when no item has that identifier.
    - **O3.** Remove an item with `doc.remove()`, and fix the broken reference
      that `doc.lint()` reports when another item still points at it.
    - **O4.** Fix a document that fails validation: read each issue's message
      and context, correct the cause, and run `doc.validate()` again until it
      returns an empty list.

**Prerequisites:** [Module 12](module-12-data-linkage.en.md).

**Time:** 40 min self-paced / 50 min instructor-led.

**New in this module:** `set_property()`, `get_property()`, `properties`,
`remove_property()`, `doc.find()`, `doc.remove()`, `issue.message`,
`issue.context`.

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

doc = ddi.new_study(title="Household Survey", agency="survey.example.org")

q_age = doc.add_question(text="How old are you?")
q_income = doc.add_question(text="What is your household income?")
q_name = doc.add_question(text="What is your full name?")

# Tag the income question as high sensitivity
q_income.set_property("sensitivity", "high")

# Tag the name question too
q_name.set_property("sensitivity", "high")
q_name.set_property("data_source", "self-reported")
```

You can set as many properties as you need on any item. Setting a key that
the item already has replaces its value.

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

`properties` gives you a new dictionary each time you read it. Changing that
dictionary does not change the item: use the methods to do that.

## 4. Remove a property

Use `item.remove_property(key)` to delete a property.
It returns `True` if the property was found and removed, or `False` if the key was not there.

```python
removed = q_name.remove_property("data_source")
print(removed)  # -> True
print(q_name.properties)  # -> {'sensitivity': 'high'}
```

## 5. Find items by identifier

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
print(found.names[0].text)  # -> Age
```

If no item matches, `doc.find()` returns `None`. It does not raise an error,
so check the result before you use it:

```python
print(doc.find("not-an-identifier"))  # -> None
```

## 6. Remove items

Use `doc.remove(identifier)` to delete an item from the document.
It returns `True` if the item was found and removed, and `False` if no item
has that identifier.

```python
print(f"Questions before: {len(doc.questions)}")  # -> 3

# Remove the name question
doc.remove(q_name.identifier)

print(f"Questions after: {len(doc.questions)}")  # -> 2
```

Be careful: removing is permanent.
There is no undo.

### Removing leaves references behind

`doc.remove()` removes the item and nothing else. If another item refers to
it, that **reference** (the link from one item to another, Module 4) stays,
and now points at nothing. The variable `Age` refers to the age question.
Remove the question and ask `doc.lint()` (Module 3) what it finds:

```python
doc.remove(q_age.identifier)

for finding in doc.lint():
    if finding.severity == "error":
        print(finding.rule_id)  # -> ddi.reference.integrity
```

The rule `ddi.reference.integrity` means "this reference cannot be resolved to
an item in the document". `doc.validate()` does not report it: the schema
checks the shape of the file, not whether each reference finds its target.
`doc.save()` warns about it too.

You have two ways to fix it. Drop the reference, so the variable no longer
names a question. Or remove the variable as well, if it means nothing without
the question. Here the variable stays and the reference goes:

```python
v1.question_references = [
    ref for ref in v1.question_references if ref.identifier != q_age.identifier
]

errors = [finding for finding in doc.lint() if finding.severity == "error"]
print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
```

## 7. Read a validation issue

In Module 3 you ran `doc.validate()` on a correct study and got an empty
list. Here is what a problem looks like.

A common mistake is a language tag written with an underscore, `fr_CA`. The
standard writes it with a hyphen: `fr-CA`. Add a French text with the wrong
tag and validate:

```python
from ddi_l.models.base import InternationalString

q_income.question_texts.append(
    InternationalString(text="Quel est le revenu de votre ménage ?", lang="fr_CA")
)

issues = doc.validate()
print(f"Issues: {len(issues)}")  # -> Issues: 1
for issue in issues:
    print(issue.message)
    print(issue.context)
```

Expected output:

```text
Issues: 1
attribute {http://www.w3.org/XML/1998/namespace}lang='fr_CA': value doesn't match any pattern of ['[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*']
<d:Text> Quel est le revenu de votre ménage ?
```

Each issue has two parts worth reading:

- **`message`** says which rule the file breaks. Here an attribute,
  `{http://www.w3.org/XML/1998/namespace}lang` (the long name of `xml:lang`),
  holds `fr_CA`. That value does not match the **pattern** the schema allows:
  letters, then optional parts that each start with a hyphen.
- **`context`** shows the element and the start of its text: a `<d:Text>`
  holding the French text you just added. That tells you which item to fix.

If the context is not enough, `issue.xpath` gives the full path to the
element in the file.

## 8. The validate-fix-validate loop

Before you publish or share a DDI file, follow this loop:

1. **Validate** with `doc.validate()`.
2. **Read** each issue's message and context.
3. **Fix** the cause in your document.
4. **Validate again**, and go back to step 2 until the list is empty.
5. **Save** the file.

Fix the language tag from section 7, validate again, and save:

```python
q_income.question_texts[-1].lang = "fr-CA"

issues = doc.validate()
print(f"Issues: {len(issues)}")  # -> Issues: 0

doc.save("household-survey.xml")
```

Step 4 is not a formality. A fix can be wrong, and the validator does not
always report every problem at once: when one error stops it checking the
rest of an element, the next problem shows up only after you fix the first.
Run `doc.lint()` as well, since validation does not see broken references
(section 6).

---

!!! example "Scenario"
    A survey team is preparing a household survey for publication.
    They need to tag some questions with sensitivity levels and data sources.
    Before publishing, they must remove a question they dropped, validate the
    document, fix any issues, and save a clean file.

---

## Exercises

1. **(O1)** Create a study with 3 questions: "How old are you?", "What is your household income?", and "What is your full name?". Set `"sensitivity"` = `"high"` on the income question. On the name question, set `"sensitivity"` = `"high"` and `"data_source"` = `"self-reported"`, and print its properties. Then remove `"data_source"`, print what `remove_property()` returns, and print the properties again.

    **Expected output:**

    ```text
    {'sensitivity': 'high', 'data_source': 'self-reported'}
    True
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
        q_name.set_property("sensitivity", "high")
        q_name.set_property("data_source", "self-reported")
        print(q_name.properties)
        # -> {'sensitivity': 'high', 'data_source': 'self-reported'}

        print(q_name.remove_property("data_source"))  # -> True
        print(q_name.properties)  # -> {'sensitivity': 'high'}
        ```

2. **(O2)** Add a variable named `Age` for the age question. Find it by its identifier and print its name. Then predict what `doc.find("not-an-identifier")` returns, and print it to check.

    **Expected output:**

    ```text
    Found: Age
    None
    ```

    ??? success "Answer"
        ```python
        v_age = doc.add_variable(name="Age", question=q_age)

        found = doc.find(v_age.identifier)
        print(f"Found: {found.names[0].text}")  # -> Found: Age
        print(doc.find("not-an-identifier"))  # -> None
        ```

        `doc.find()` returns `None` when nothing matches; it does not raise an error.

3. **(O3)** Remove the name question and print the new question count. Then call `doc.remove()` again with the same identifier and print what it returns.

    **Expected output:**

    ```text
    Questions: 2
    False
    ```

    ??? success "Answer"
        ```python
        doc.remove(q_name.identifier)
        print(f"Questions: {len(doc.questions)}")  # -> Questions: 2
        print(doc.remove(q_name.identifier))  # -> False
        ```

        The second call finds nothing to remove, so it returns `False`.

4. **(O3)** Remove the age question, which the `Age` variable refers to. Run `doc.lint()` and print the rule of each error. Fix the broken reference by dropping it from the variable, then print the number of lint errors.

    **Expected output:**

    ```text
    ddi.reference.integrity
    Lint errors: 0
    ```

    ??? success "Answer"
        ```python
        doc.remove(q_age.identifier)

        for finding in doc.lint():
            if finding.severity == "error":
                print(finding.rule_id)  # -> ddi.reference.integrity

        v_age.question_references = [
            ref for ref in v_age.question_references if ref.identifier != q_age.identifier
        ]
        errors = [finding for finding in doc.lint() if finding.severity == "error"]
        print(f"Lint errors: {len(errors)}")  # -> Lint errors: 0
        ```

        Removing the `Age` variable too (`doc.remove(v_age.identifier)`) is also a correct fix, if the variable means nothing without its question.

5. **(O4)** The block below puts two mistakes in the income question. Run `doc.validate()` and print the number of issues and the context of the first one. Fix that cause, and validate again. Repeat until there are no issues, then save the document as `household-clean.xml`.

    ```python
    from ddi_l.models.base import InternationalString

    q_income.question_texts.append(
        InternationalString(text="Revenu du ménage ?", lang="fr_CA")
    )
    q_income.version = "1.a"
    ```

    **Expected output:**

    ```text
    Issues: 1
    <r:Version> 1.a
    Issues: 1
    <d:Text> Revenu du ménage ?
    Issues: 0
    ```

    ??? success "Answer"
        ```python
        issues = doc.validate()
        print(f"Issues: {len(issues)}")  # -> Issues: 1
        print(issues[0].context)  # -> <r:Version> 1.a

        # A version is numbers separated by dots
        q_income.version = "1.1"
        issues = doc.validate()
        print(f"Issues: {len(issues)}")
        print(issues[0].context)  # -> <d:Text> Revenu du ménage ?

        # A language tag uses a hyphen, not an underscore
        q_income.question_texts[-1].lang = "fr-CA"
        issues = doc.validate()
        print(f"Issues: {len(issues)}")  # -> Issues: 0

        doc.save("household-clean.xml")
        ```

        The first run reports only the version. The language tag shows up once the version is fixed, which is why you validate again after every fix.

---

## Quiz

???+ question "Question 1 (O1): What does print(q.properties) show after these two calls?"
    `q.set_property("sensitivity", "high")`, then
    `q.set_property("sensitivity", "low")`.

    **A.** `{'sensitivity': 'high'}`

    **B.** `{'sensitivity': ['high', 'low']}`

    **C.** `{'sensitivity': 'low'}`

    **D.** An error, because the key already exists.

    ??? success "Answer"
        **C.** Setting a key the item already has replaces its value. An
        item has at most one value per key.

???+ question "Question 2 (O1): Which line removes the property data_source from the item q?"
    **A.** `q.remove_property("data_source")`

    **B.** `del q.properties["data_source"]`

    **C.** `doc.remove("data_source")`

    **D.** `q.get_property("data_source")`

    ??? success "Answer"
        **A.** `remove_property()` removes the key and returns `True`. B
        deletes the key from a new dictionary that `properties` built, so
        the item keeps it. C removes items by identifier, not properties. D
        only reads the value.

???+ question "Question 3 (O2): doc.remove(v.identifier) just returned True. What does doc.find(v.identifier) return now?"
    **A.** The variable `v`.

    **B.** `True`

    **C.** An error, because the identifier is unknown.

    **D.** `None`

    ??? success "Answer"
        **D.** The variable is no longer in the document, so nothing
        matches, and `doc.find()` returns `None` rather than raising an
        error.

???+ question "Question 4 (O3): You remove a question that a variable refers to. doc.validate() returns an empty list. Is the document ready to share?"
    **A.** Yes. An empty list means there is nothing to fix.

    **B.** No. `doc.lint()` reports `ddi.reference.integrity`: the variable
    still points at the removed question, so fix that reference first.

    **C.** No. The schema should have caught it, so the schema is broken.

    **D.** Yes. `doc.save()` removes broken references for you.

    ??? success "Answer"
        **B.** Validation checks the shape of the file against the schema,
        not whether each reference finds its target. Lint does. `doc.save()`
        warns about the broken reference but keeps it.

???+ question "Question 5 (O4): Validation reports this issue. Which fix is right?"
    ```text
    attribute {http://www.w3.org/XML/1998/namespace}lang='en_US': value doesn't match any pattern of ['[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*']
    <d:Text> How old are you?
    ```

    **A.** Change the language tag of that question text to `en-US`.

    **B.** Remove the question "How old are you?".

    **C.** Add a label to the question.

    **D.** Save the file, then validate the saved file.

    ??? success "Answer"
        **A.** The message says the `xml:lang` value `en_US` does not match
        the allowed pattern, which uses hyphens. The context shows which
        text holds it. Removing the question (B) loses data to hide the
        problem; C and D do not change the tag.

???+ question "Question 6 (O4): Validation reports this issue on a question's version. Which value passes?"
    ```text
    value doesn't match any pattern of ['[0-9]+(\\.[0-9]+)*']
    <r:Version> 1.a
    ```

    **A.** `"1.a"`

    **B.** `"v1.1"`

    **C.** `"1.1"`

    **D.** `"1-1"`

    ??? success "Answer"
        **C.** The pattern allows numbers separated by dots, and nothing
        else. Validate again after the fix to confirm it, and to see any
        issue the first one hid.

---

## Going further (optional)

### Store a link to a code list in a property

You can pass a code list object (or any DDI item) as the value of a property.
The library stores the item's **URN** (Uniform Resource Name), a unique
address that identifies the item.

```python
cl = doc.add_code_list(name="Income Brackets")
q_income.set_property("vocabulary", cl)

print(q_income.get_property("vocabulary").startswith("urn:ddi:"))  # -> True
```

This links a question to the code list that defines its allowed answers.
[Module 14](module-14-custom-fields.en.md) uses it to back a custom field with a
controlled vocabulary.

---

## Check yourself

- [ ] I can add, read and remove custom properties on a DDI item. (O1)
- [ ] I can find an item by its identifier and say what `doc.find()` returns when nothing matches. (O2)
- [ ] I can remove an item and fix the broken reference that `doc.lint()` reports. (O3)
- [ ] I can read a validation issue, fix its cause, and validate again until the list is empty. (O4)

---

!!! tip "Instructor notes"
    - Properties are the most flexible part of the API. Emphasize that they are for team-specific metadata that DDI does not have a built-in field for.
    - The `find()` and `remove()` methods work with identifiers, not names. Remind learners to save the identifier when they create an item.
    - The validate-fix-validate loop is a professional habit. Compare it to spell-checking a document before sending it. Exercise 5 shows why step 4 matters: the second mistake only appears after the first is fixed.
    - Common mistake: learners forget that `properties` is a property (no parentheses), while `get_property()` and `set_property()` are methods (with parentheses).
    - Have learners skip the reference fix in Exercise 4 once and save: the `DDIReferenceWarning` makes the point that removing an item can break another.
    - This module builds on earlier ones. Module 12 already used `set_property()` to tag linkage keys; Module 3 introduced `doc.validate()` and `doc.lint()`, and Module 7 runs them from the command line. For a closing mini-project, have learners build a document with questions and variables (Modules 3 and 4), concepts (Module 5), code lists (Module 9) and properties, then validate, fix and save it.

---

**See also:** [Validation guide](../validation.en.md)
