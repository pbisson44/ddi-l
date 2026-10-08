# Answer Keys

This page contains solutions for all exercises and quizzes in the
curriculum. Use it to check your work after completing each module.

---

## Module 1: What Is Metadata?

### Exercise solutions

**Exercise 1**: Three things a new person would need to know:

1. What each column means (what is "age"? In years? Months?)
2. Who was surveyed (students? Adults? Everyone?)
3. When the data was collected

**Exercise 2**: From the DDI Alliance website: "The Data Documentation
Initiative (DDI) is an international standard for describing data from
the social, behavioral, economic, and health sciences."

### Quiz answers

1. **(B) Information about data.** Metadata describes your data: what it
   contains, who collected it, and how.
2. **(C) Without it, people cannot understand what the data means.**
   Without documentation, nobody knows what the numbers mean.
3. **(B) Findable, Accessible, Interoperable, Re-usable.** These four
   principles guide how data should be shared. DDI metadata helps you
   meet all four.
4. **(B) A Python tool that creates, reads, updates, and validates DDI
   documents.** ddi-l handles the XML so you can focus on your data.

---

## Module 2: Set Up Your Environment

### Exercise solutions

**Exercise 1**: The last line of `pip install` output should show
"Successfully installed ddi-l-..." (the version may vary).

**Exercise 2**:

```python
import ddi_l as ddi

print(ddi.__version__)
# Output: 0.1.0 (or the current version)
```

**Exercise 3**: The number of commands varies by version. Typically 4-6
commands are listed.

### Quiz answers

1. **(b) 3.11.** ddi-l requires Python 3.11 or newer.
2. **(a) `ddi --help`.** This shows all available CLI commands.
3. **(a) Downloads and installs the ddi-l package.** pip is Python's
   package installer.

---

## Module 3: Create Your First Study

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi

doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")
q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")
doc.save("well-being.xml")
print(f"Questions: {len(doc.questions)}")
```

Output: `Questions: 3`

**Exercise 2**: Open `well-being.xml` in a text editor. Look for
`<r:Content>What is your age?</r:Content>` inside the XML.

**Exercise 3**:

```python
from ddi_l.models.base import InternationalString

q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
doc.save("well-being.xml")
```

Open the XML. You should see both `xml:lang="en"` and `xml:lang="fr"`
entries for the first question.

### Quiz answers

1. **(B) A Document object.** The Document holds your study and all its
   contents.
2. **(B) Adds a question to the study.** The question is stored inside
   a QuestionScheme in the DataCollection module.
3. **(C) Writes the DDI document to an XML file.** The file uses proper
   DDI namespace prefixes.
4. **(B) Append an InternationalString with lang="fr".** Both language
   versions are stored in the same question item.
5. **(B) `len(doc.questions)`.** The `questions` property returns a list.

---

## Module 4: Variables and Questions

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi

doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")
q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")

doc.add_variable(name="Age", question=q1)
doc.add_variable(name="HealthRating", question=q2)
doc.add_variable(name="SleepHours", question=q3)

print(f"Variables: {len(doc.variables)}")
```

Output: `Variables: 3`

**Exercise 2**:

```python
for v in doc.variables:
    print(v.identifier)
```

Each identifier is a UUID like `a1b2c3d4-...`.

**Exercise 3**: Save and compare. The XML file is now larger because it
contains both QuestionScheme and VariableScheme sections.

### Quiz answers

1. **(a) Links the variable to that question.** This creates a DDI
   reference element.
2. **(a) `doc.variables`.** Returns a list of all Variable objects.
3. **(a) Column.** A variable is like a column in a spreadsheet.

---

## Module 5: Concepts and Universes

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi

doc = ddi.new_study(title="Health Survey", agency="health.gc.ca")

q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="What is your weight?")
q3 = doc.add_question(text="How often do you exercise per week?")
q4 = doc.add_question(text="How many fruit servings do you eat per day?")

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
```

Output:

```text
Questions: 4
Variables: 4
Concepts: 3
Universes: 1
```

### Quiz answers

1. **(a) An abstract idea that a variable measures.** For example, "Age"
   the concept is measured by "Age" the variable.
2. **(a) The group of people or things being studied.** For example,
   "Adults aged 18+ in Canada".
3. **(a) Pass `concept=` when calling `add_variable()`.** This creates a
   reference link in the DDI document.

---

## Module 6: From CSV/Excel to DDI

### Exercise solutions

**Exercise 1**:

```python
import csv
import ddi_l as ddi

with open("survey_sample.csv") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames

# The question each column records, worded the way respondents saw it
QUESTIONS = {
    "age": "How old are you?",
    "gender": "What is your gender?",
    "income": "What was your total income last year, before taxes?",
    "education_level": "What is the highest level of education you have completed?",
}

doc = ddi.new_study(title="Household Survey", agency="research.org")
for col in columns:
    wording = QUESTIONS.get(col)
    # A column nobody was asked about, such as respondent_id, gets no question
    q = doc.add_question(text=wording) if wording else None
    doc.add_variable(name=col, question=q)

doc.save("household-survey.xml")
print(f"Variables: {len(doc.variables)}")
```

Output: `Variables: 5`

**Exercise 2** (pandas):

<!-- docs-test: skip -- needs pandas, which ddi-l does not depend on -->
```python
import pandas as pd
import ddi_l as ddi

df = pd.read_csv("survey_sample.csv")
doc = ddi.new_study(title="Household Survey", agency="research.org")
for col in df.columns:
    doc.add_variable(name=col)
doc.save("household-survey-pandas.xml")
print(f"Variables: {len(doc.variables)}")
```

Output: `Variables: 5`

**Exercise 3** (enriched):

```python
doc.add_concept(name="Demographics")
doc.add_concept(name="Socioeconomic Status")
doc.add_universe(name="Canadian households")
issues = doc.validate()
print(f"Valid: {not issues}")
doc.save("household-survey-enriched.xml")
```

### Quiz answers

1. **(a) A list of column names.** `reader.fieldnames` gives you the
   header row from the CSV.
2. **(b) `df.columns`.** This returns the column names from the
   DataFrame.
3. **(a) A DDI XML file with one variable per column.** The script reads
   column names and creates DDI metadata.
4. **(a) Because column names alone are not useful metadata.** Concepts,
   universes, and code lists add meaning.

---

## Module 7: Code Lists

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi
from ddi_l.models.logicalproduct import Category

doc = ddi.new_study(title="Census", agency="statcan.gc.ca")

doc.add_code_list(name="Gender Codes")
doc.add_item(Category, name="Male")
doc.add_item(Category, name="Female")
doc.add_item(Category, name="Other")

doc.add_code_list(name="Employment Status")
doc.add_item(Category, name="Employed")
doc.add_item(Category, name="Unemployed")
doc.add_item(Category, name="Retired")
doc.add_item(Category, name="Student")

doc.add_code_list(name="Housing Type")
doc.add_item(Category, name="House")
doc.add_item(Category, name="Apartment")
doc.add_item(Category, name="Other")

print(f"Code lists: {len(doc.code_lists)}")
print(f"Categories: {len(doc.items(Category))}")
```

Output:

```text
Code lists: 3
Categories: 10
```

**Exercise 2**:

```python
for cat in doc.items(Category):
    print(cat.identifier)
```

**Exercise 3**:

```python
from ddi_l.models.datacollection import Instrument

doc.add_item(Instrument, name="Census Form")
```

### Quiz answers

1. **(b) A set of pre-defined answer choices.** Like "Male / Female /
   Other" for gender.
2. **(b) `doc.add_item(Category, name="...")`.** The `add_item` method
   works for any DDI type.
3. **(c) `doc.items(Category)`.** Returns all categories in the document.
4. **(c) They make answers consistent across surveys.** Everyone uses the
   same codes.

---

## Module 8: Questionnaire Flows

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi

doc = ddi.new_study(title="National Health Survey", agency="health.gc.ca")
q_age = doc.add_question(text="What is your age?")
q_gender = doc.add_question(text="What is your gender?")
q_employed = doc.add_question(text="Are you currently employed?")
q_occupation = doc.add_question(text="What is your occupation?")
q_health = doc.add_question(text="How would you rate your general health?")
q_smoke = doc.add_question(text="Do you smoke?")
print(f"Questions: {len(doc.questions)}")
```

Output: `Questions: 6`

**Exercise 2**:

```python
from ddi_l.models.datacollection import QuestionConstruct, Sequence

for q in doc.questions:
    doc.add_item(QuestionConstruct, name="Ask", question_reference=q.to_reference())

doc.add_item(Sequence, name="Section A - Demographics")
doc.add_item(Sequence, name="Section B - Employment")
doc.add_item(Sequence, name="Section C - Health")

print(f"QuestionConstructs: {len(doc.items(QuestionConstruct))}")
print(f"Sequences: {len(doc.items(Sequence))}")
```

Output:

```text
QuestionConstructs: 6
Sequences: 3
```

**Exercise 3**:

```python
from ddi_l.models.datacollection import IfThenElse

doc.add_item(IfThenElse, name="Age gate for employment")
doc.add_item(IfThenElse, name="Occupation routing")
print(f"IfThenElse: {len(doc.items(IfThenElse))}")
```

Output: `IfThenElse: 2`

**Exercise 4**:

```python
from ddi_l.models.datacollection import StatementItem, Instrument

doc.add_item(Sequence, name="Main Survey Flow")
doc.add_item(StatementItem, name="Welcome")
doc.add_item(Instrument, name="Health Survey Instrument")

print(f"Sequences: {len(doc.items(Sequence))}")
print(f"StatementItems: {len(doc.items(StatementItem))}")
print(f"Instruments: {len(doc.items(Instrument))}")
```

Output:

```text
Sequences: 4
StatementItems: 1
Instruments: 1
```

### Quiz answers

1. **(b) Sequence.** Groups steps in order, like a section.
2. **(c) IfThenElse with a condition on age.** Routes the respondent.
3. **(b) It wraps a question for use in a Sequence.** Separates content
   from flow.
4. **(d) Loop.** Repeats a section for each item in a list.
5. **(c) List all questions and create QuestionConstructs.** Then build
   the flow around them.

---

## Module 9: Data Lineage

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi

doc = ddi.new_study(title="National Health Survey", agency="health.gc.ca")

q_age = doc.add_question(text="What is your age?")
q_gender = doc.add_question(text="What is your gender?")
q_employed = doc.add_question(text="Are you currently employed?")
q_occupation = doc.add_question(text="What is your occupation?")
q_health = doc.add_question(text="How would you rate your general health?")
q_smoke = doc.add_question(text="Do you smoke?")

v_age = doc.add_variable(name="age", question=q_age)
v_gender = doc.add_variable(name="gender", question=q_gender)
v_employed = doc.add_variable(name="employed", question=q_employed)
v_occupation = doc.add_variable(name="occupation", question=q_occupation)
v_health = doc.add_variable(name="health_rating", question=q_health)
v_smoke = doc.add_variable(name="smoker", question=q_smoke)

print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
```

Output:

```text
Questions: 6
Variables: 6
```

**Exercise 2**:

```python
from ddi_l.models.logicalproduct import Category
from ddi_l.models.base import Reference

cl = doc.add_code_list(name="Age Group Codes")
doc.add_item(Category, name="0-15")
doc.add_item(Category, name="16-24")
doc.add_item(Category, name="25-44")
doc.add_item(Category, name="45-64")
doc.add_item(Category, name="65+")

v_age_group = doc.add_variable(name="age_group", question=q_age)
v_age_group.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_age.identifier, version="1"),
]

print(f"Code lists: {len(doc.code_lists)}")
print(f"Variables: {len(doc.variables)}")
```

Output:

```text
Code lists: 1
Variables: 7
```

**Exercise 3**:

```python
v_emp_code = doc.add_variable(name="employment_status_code", question=q_employed)
v_emp_code.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_employed.identifier, version="1"),
]

v_health_score = doc.add_variable(name="health_score", question=q_health)
v_health_score.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_health.identifier, version="1"),
]

print(f"Variables: {len(doc.variables)}")
```

Output: `Variables: 9`

**Exercise 4**:

```python
v_master_ag = doc.add_variable(name="age_group_master", question=q_age)
v_master_ag.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_age_group.identifier, version="1"),
]

v_master_emp = doc.add_variable(name="employment_status_master", question=q_employed)
v_master_emp.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_emp_code.identifier, version="1"),
]

v_master_hs = doc.add_variable(name="health_score_master", question=q_health)
v_master_hs.source_variable_references = [
    Reference(agency="health.gc.ca", identifier=v_health_score.identifier, version="1"),
]

print(f"Total variables: {len(doc.variables)}")
```

Output: `Total variables: 12`

### Quiz answers

1. **(b) Which other variables a derived variable was computed from.**
2. **(c) Use `doc.add_variable(name=..., question=q)`.**
3. **(c) Both collection variables and derived variables.**
4. **(c) 2: one for height and one for weight.**
5. **(b) Trace any variable back to the original question and data.**

---

## Module 10: Data Linkage

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi
from ddi_l.models.base import Reference

doc = ddi.new_study(
    title="Canadian Community Health Survey 2021",
    agency="statcan.gc.ca",
)
q_key = doc.add_question(text="Anonymized linkage key")
q_health = doc.add_question(text="How would you rate your general health?")

survey_key = doc.add_variable(name="anon_id", question=q_key)
survey_health = doc.add_variable(name="health_rating", question=q_health)
survey_key.set_property("linkage_role", "key")

print(f"Survey variables: {len(doc.variables)}")
print(f"anon_id linkage_role: {survey_key.get_property('linkage_role')}")
```

Output:

```text
Survey variables: 2
anon_id linkage_role: key
```

**Exercise 2**:

```python
admin = doc.add_study(title="Hospital Admissions Register 2021")
admin_ds = doc.study(admin.identifier)

admin_key = admin_ds.add_variable(name="anon_id")
admin_visits = admin_ds.add_variable(name="hospital_visits")
admin_key.set_property("linkage_role", "key")

cmp = doc.add_comparison(name="Survey-to-Admin Microdata Linkage 2021")
key_match = cmp.correspondence(
    commonality="Anonymized personal identifier common to both sources.",
    weight=1.0,
)
cmp.add_variable_map(
    survey_key.to_reference(),
    admin_key.to_reference(),
    correspondence=key_match,
)

print(f"Comparisons: {len(doc.comparisons)}")
```

Output: `Comparisons: 1`

**Exercise 3**:

```python
cmp.set_property("linkage_method", "deterministic")
cmp.set_property("match_rate", "0.94")

print(cmp.get_property("linkage_method"))
```

Output: `deterministic`

**Exercise 4**:

```python
linked = doc.add_variable(name="health_by_hospital_use")
linked.source_variable_references = [
    Reference(agency="statcan.gc.ca", identifier=survey_health.identifier, version="1"),
    Reference(agency="statcan.gc.ca", identifier=admin_visits.identifier, version="1"),
]

print(f"Linked variable sources: {len(linked.source_variable_references)}")
```

Output: `Linked variable sources: 2`

**Exercise 5** (bonus: probabilistic linkage):

```python
prob = doc.add_comparison(name="Probabilistic Linkage")

dob = doc.add_variable(name="date_of_birth")
sex = doc.add_variable(name="sex")
postal = doc.add_variable(name="postal_code")
for v in (dob, sex, postal):
    v.set_property("linkage_role", "matching")

weighted = prob.correspondence(
    commonality="Agreement across date of birth, sex, and postal code.",
    weight=0.85,
)

for v in (dob, sex, postal):
    print(f"{v.names[0].text}: {v.get_property('linkage_role')}")
```

Output:

```text
date_of_birth: matching
sex: matching
postal_code: matching
```

### Quiz answers

1. **(b) Combining records from two or more sources that refer to the same unit.**
2. **(b) The variable common to both sources that connects matching records.**
3. **(a) Deterministic matches on an exact key; probabilistic weighs agreement across several quasi-identifiers.**
4. **(b) Put both sources in `source_variable_references`.**
5. **(b) To protect confidentiality. Personal identifiers are removed so the linked file is anonymized.**

---

## Module 11: Properties, Find, and Validate

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi

doc = ddi.new_study(title="Household Survey", agency="research.org")
q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="What is your gender?")
q3 = doc.add_question(text="What is your income?")

q3.set_property("sensitivity", "high")
print(q3.properties)
```

Output: `{'sensitivity': 'high'}`

**Exercise 2**:

```python
doc.add_variable(name="Age", question=q1)
v = doc.variables[0]
print(v.identifier)
```

**Exercise 3**:

```python
doc.remove(q1.identifier)
print(f"Questions after removal: {len(doc.questions)}")
```

Output: `Questions after removal: 2`

**Exercise 4**:

```python
issues = doc.validate()
if not issues:
    print("Document is valid!")
```

### Quiz answers

1. **(a) Attaches a custom key-value pair to the item.** Stored as a
   UserAttributePair in the XML.
2. **(a) `item.properties`.** Returns a dict of all key-value pairs.
3. **(a) The item object.** Returns None if not found.
4. **(a) Checks the document against the DDI schema.** Returns a list of
   issues (empty if valid).
5. **(a) Deletes the item from the document.** Returns True if found.

---

## Module 12: Custom Fields

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi

doc = ddi.new_study(title="Household Survey", agency="survey.gc.ca")
q_income = doc.add_question(text="What is your household income?")
income = doc.add_variable(name="income", question=q_income)

study = doc.study_unit
study.set_property("myorg:retention_policy", "destroy after 7 years")
study.set_property("myorg:security_class", "Protected B")

print(study.properties)
```

Output:

```text
{'myorg:retention_policy': 'destroy after 7 years', 'myorg:security_class': 'Protected B'}
```

**Exercise 2**:

```python
income.set_property("myorg:source_system", "CRM-2024")
q_income.set_property("myorg:steward", "Survey Methods")


def items_with_custom_fields(doc, prefix="myorg:"):
    count = 0
    for collection in (doc.questions, doc.variables):
        for item in collection:
            if any(key.startswith(prefix) for key in item.properties):
                count += 1
    return count


print(f"Items with custom fields: {items_with_custom_fields(doc)}")
```

Output: `Items with custom fields: 2`

**Exercise 3**:

```python
from ddi_l.models.base import UserID

income.user_ids.append(UserID(value="CAT-000734", type_of_user_id="InternalCatalogue"))

uid = income.user_ids[0]
print(f"{uid.type_of_user_id}: {uid.value}")
```

Output: `InternalCatalogue: CAT-000734`

**Exercise 4**:

```python
doc.save("household-survey.xml")

reopened = ddi.open_ddi("household-survey.xml")
print(reopened.variables[0].get_property("myorg:source_system"))
```

Output: `CRM-2024`

**Exercise 5** (bonus: controlled vocabulary):

```python
from uuid import uuid4

from ddi_l.models.logicalproduct import Category, CodeItem

# Build the controlled vocabulary. Each allowed value needs a Category (its
# meaning) AND a Code in the list that references it; a Category alone is not
# in any list. Each Code gets its own UUID4-based URN.
quality_codes = doc.add_code_list(name="Quality Flag Codes")
for value in ("validated", "provisional", "suppressed"):
    category = doc.add_item(Category, name=value)
    quality_codes.codes.append(
        CodeItem(
            agency=quality_codes.agency,
            identifier=str(uuid4()),
            version=quality_codes.version,
            value=value,
            category=category.to_reference(),
        )
    )

# A field whose value is drawn from the vocabulary, plus a field that
# references the code list defining the allowed values
income.set_property("myorg:quality_flag", "validated")
income.set_property("myorg:quality_flag_codes", quality_codes)

print(income.get_property("myorg:quality_flag"))
print(income.get_property("myorg:quality_flag_codes").startswith("urn:ddi:"))
```

Output:

```text
validated
True
```

!!! note "Objects stay attached"
    Variables you hold remain the objects the document serializes, before
    and after `save()`.

### Quiz answers

1. **(b) Because DDI is an open, extensible standard with a built-in extension point.**
2. **(b) `UserAttributePair`.** `set_property` writes an `AttributeKey`/`AttributeValue` pair.
3. **(b) They survive: they are written to the DDI XML and read straight back.**
4. **(a) When the value identifies the item in another system.** Use a custom property when it describes the item.
5. **(b) To keep your fields distinct so they never collide with another organization's fields.**

---

## Module 13: Update and Version

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi

doc = ddi.new_study(title="Survey v1", agency="lab.org")
q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="What is your gender?")
q3 = doc.add_question(text="How often do you exercise?")
doc.add_variable(name="Age", question=q1)
doc.add_variable(name="Gender", question=q2)
doc.add_variable(name="Exercise", question=q3)
doc.save("survey-v1.xml")
```

**Exercise 2**:

```python
doc = ddi.open_ddi("survey-v1.xml")
q4 = doc.add_question(text="How many hours do you sleep?")
doc.add_variable(name="Sleep", question=q4)
doc.remove(doc.questions[0].identifier)
```

**Exercise 3**:

```python
from ddi_l.models.base import VersionRationale, InternationalString

study = doc.study_unit
study.increment_minor_version()
study.version_rationales.append(
    VersionRationale(
        descriptions=[
            InternationalString(text="Added sleep quality question for wave 2")
        ]
    )
)
study.version_responsibility = "Survey Design Team"
```

**Exercise 4**:

```python
issues = doc.validate()
doc.save("survey-v2.xml")
print(f"Version: {study.version}")
for r in study.version_rationales:
    for d in r.descriptions:
        print(f"Rationale: {d.text}")
```

Output:

```text
Version: 1.1
Rationale: Added sleep quality question for wave 2
```

### Quiz answers

1. **(a) Changes the version from 1.0.0 to 1.1.0.** Minor version bumps
   are for additions and small changes.
2. **(a) Why a change was made.** A text explanation stored in the DDI
   document.
3. **(a) Who made the change.** A text field identifying the responsible
   person or team.
4. **(a) Major for big changes, minor for additions.** Use major when the
   structure changes significantly, minor when you add or tweak.

---

## Module 14: Open and Modify Files

### Exercise solutions

**Exercise 1**:

```python
import ddi_l as ddi

doc = ddi.open_ddi("survey-v1.xml")
print(f"Questions: {len(doc.questions)}")
print(f"Variables: {len(doc.variables)}")
```

**Exercise 2**:

```python
q_new1 = doc.add_question(text="What is your education level?")
q_new2 = doc.add_question(text="What is your marital status?")
doc.add_variable(name="Education", question=q_new1)
doc.add_variable(name="MaritalStatus", question=q_new2)
issues = doc.validate()
doc.save("survey-updated.xml")
```

**Exercise 3**:

```python
doc2 = ddi.open_ddi("survey-updated.xml")
print(f"Questions: {len(doc2.questions)}")
print(f"Variables: {len(doc2.variables)}")
```

The counts should be 2 higher than Exercise 1.

### Quiz answers

1. **(a) Opens and parses a DDI XML file into a Document.** You can then
   read and modify it.
2. **(a) Checks the file against the DDI schema during loading.** Any
   errors are reported immediately.
3. **(a) No, existing content is preserved.** ddi-l keeps unknown XML
   in `other_elements` so nothing is lost.

---

## Module 15: CLI Validation

### Exercise solutions

**Exercise 1**:

```bash
ddi validate survey-v1.xml
```

Output: `Document is valid.`

**Exercise 2**:

```bash
ddi to-json survey-v1.xml --indent 2 > survey.json
wc -l survey.json
```

The number of lines depends on the document size.

**Exercise 3**:

```bash
ddi roundtrip survey-v1.xml --output survey-roundtrip.xml
ls -la survey-v1.xml survey-roundtrip.xml
```

The file sizes should be similar.

### Quiz answers

1. **(a) Checks the file against the DDI schema.** Prints "Document is
   valid." or a JSON error list.
2. **(a) The file is valid.** Exit code 0 means success in Unix.
3. **(a) Converts DDI XML to JSON format.** Useful for web APIs and
   analytics systems.

---

## Module 16: Capstone Projects

### Sample solution: Track A (Student)

Uses the sample dataset from the capstone page:
[`thesis-data.csv`](thesis-data.csv){ download="thesis-data.csv" }.

```python
import csv
import ddi_l as ddi
from ddi_l.models.base import VersionRationale, InternationalString

# Read CSV
with open("thesis-data.csv") as f:
    columns = csv.DictReader(f).fieldnames

# Create v1.0
doc = ddi.new_study(title="Thesis Dataset", agency="university.edu")
# How each column was asked. StudentID is assigned and AnxietyScore is computed
# from a questionnaire, so neither gets a question of its own.
QUESTIONS = {
    "Age": "How old are you?",
    "Gender": "What is your gender?",
    "YearOfStudy": "What year of your program are you in?",
    "Program": "Which program are you enrolled in?",
    "StudyHours": "On a typical day, how many hours do you study?",
    "SleepHours": "On a typical night, how many hours do you sleep?",
    "WorkHours": "How many hours a week do you work for pay?",
    "ExerciseDays": "On how many days last week did you exercise?",
    "StressLevel": "On a scale of 1 to 10, how stressed have you felt this term?",
    "SoughtSupport": "Have you sought support from campus services this term?",
}
for col in columns:
    wording = QUESTIONS.get(col)
    q = doc.add_question(text=wording) if wording else None
    v = doc.add_variable(name=col, question=q)
    v.set_property("source", "Primary survey data")

doc.add_concept(name="Demographics")
doc.add_concept(name="Academic Performance")
doc.add_concept(name="Well-Being")
doc.add_universe(name="Undergraduate students at University X")

doc.save("thesis-v1.xml")
issues = doc.validate()
print(f"v1 valid: {not issues}")

# Update to v1.1
doc = ddi.open_ddi("thesis-v1.xml")
q_new = doc.add_question(text="What is the student's GPA?")
v_new = doc.add_variable(name="GPA", question=q_new)

study = doc.study_unit
study.increment_minor_version()
study.version_rationales.append(
    VersionRationale(
        descriptions=[InternationalString(text="Added GPA variable for analysis")]
    )
)
study.version_responsibility = "Thesis Author"
doc.save("thesis-v1.1.xml")
print(f"v1.1 valid: {not doc.validate()}")
```

### Reflection questions

These are open-ended. There are no right or wrong answers. Use them for
discussion or written feedback.
