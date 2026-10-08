# Module 3: Create Your First DDI Study

!!! info "What you will learn"
    - Create a new DDI study using `ddi.new_study()`.
    - Add survey questions using `doc.add_question()`.
    - List questions with `doc.questions`.
    - Save the study to an XML file using `doc.save()`.

**Prerequisites:** [Module 2: Set Up Your Python Environment](module-02-setup.md)

**Time:** 30 min self-paced / 45 min instructor-led.

**API taught:** `ddi.new_study()`, `doc.add_question()`, `doc.questions`,
`doc.save()`

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
- `agency=` sets the organization responsible for the study.

---

## 3. What is an "agency"?

An **agency** is the organization responsible for the study. It could be a
university, a government department, a research institute, or any group that
runs the survey. Examples:

- `"university.edu"`: a university
- `"statistics.gc.ca"`: Statistics Canada
- `"worldbank.org"`: The World Bank

The agency value is usually written as a domain name. It helps identify who
created the document.

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
`lang="en"` (English). To create a question in French, pass `lang="fr"`:

```python
q1 = doc.add_question(text="What is your age?", lang="en")
```

To add a French translation of the same question, append it to the
question's `question_texts` list:

```python
from ddi_l.models.base import InternationalString

q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
```

Now `q1` contains the question text in both English and French. When someone
opens the DDI file, they can see both versions.

The `lang=` argument works on all `add_*` methods: `add_variable()`,
`add_concept()`, `add_universe()`, and `add_code_list()`. You can also append
translations to their `names` list the same way. Module 6 shows a complete
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

Cross-reference: [User guide: Create a study](../user-guide.md#create-a-study)

---

## Exercises

!!! example "Scenario"
    You are a research assistant. Your professor asks you to document a
    Student Well-Being Survey with three questions about age, health, and
    sleep. You will use `ddi-l` to create the documentation.

**Exercise 1.** Create a study titled `"Student Well-Being Survey"` with
agency `"university.edu"`. Add three questions:

1. `"What is your age?"`
2. `"How would you rate your health?"`
3. `"How many hours do you sleep per night?"`

Save the study as `well-being.xml`. Print the question count.

```python
import ddi_l as ddi

doc = ddi.new_study(title="Student Well-Being Survey", agency="university.edu")

q1 = doc.add_question(text="What is your age?")
q2 = doc.add_question(text="How would you rate your health?")
q3 = doc.add_question(text="How many hours do you sleep per night?")

print(f"Questions: {len(doc.questions)}")
doc.save("well-being.xml")
```

Expected output:

```text
Questions: 3
```

**Exercise 2.** Open `well-being.xml` in a text editor. Can you find the text
of your first question inside the XML? Write down the XML tag that wraps the
question text.

**Exercise 3.** Add a French translation to the first question. Then save
the file again and check the XML for both languages.

```python
from ddi_l.models.base import InternationalString

q1.question_texts.append(InternationalString(text="Quel est votre âge ?", lang="fr"))
doc.save("well-being.xml")
```

Open the XML. You should see both `xml:lang="en"` and `xml:lang="fr"` entries
for the first question.

---

## Quiz

???+ question "Question 1: What does ddi.new_study() return?"
    **A.** A string of XML text.

    **B.** A Document object that represents the study.

    **C.** A list of questions.

    **D.** A CSV file.

    ??? success "Answer"
        **B.** `ddi.new_study()` returns a Document object. You use this
        object to add questions, variables, and other items to the study.

???+ question "Question 2: What does doc.add_question() do?"
    **A.** It sends a question to survey respondents.

    **B.** It adds a question to the study and returns a question object.

    **C.** It prints a question on the screen.

    **D.** It deletes a question from the study.

    ??? success "Answer"
        **B.** `doc.add_question()` adds a new question item to the DDI
        study. It returns the question object so you can use it later.

???+ question "Question 3: What does doc.save() do?"
    **A.** It uploads the file to the internet.

    **B.** It prints the document on paper.

    **C.** It writes the study to an XML file on your computer.

    **D.** It validates the document.

    ??? success "Answer"
        **C.** `doc.save("filename.xml")` writes the DDI document to an XML
        file in your current folder.

???+ question "Question 4: How do you add a French translation to a question?"
    **A.** `doc.add_question(text="...", lang="fr")`. This creates a new,
    separate question in French.

    **B.** Append an `InternationalString` with `lang="fr"` to the question's
    `question_texts` list.

    **C.** Change the question's language with `q.lang = "fr"`.

    **D.** You cannot store more than one language in DDI.

    ??? success "Answer"
        **B.** To add a translation, append an `InternationalString` with the
        new language to the question's `question_texts` list. Both language
        versions are stored in the same question item. Option A would create
        a brand-new question, not a translation of an existing one.

???+ question "Question 5: How do you count the questions in a study?"
    **A.** `doc.count_questions()`

    **B.** `len(doc.questions)`

    **C.** `doc.questions.size()`

    **D.** `print(doc)`

    ??? success "Answer"
        **B.** `doc.questions` gives you the list of questions, and `len()`
        counts how many items are in that list.

---

!!! tip "Instructor notes"
    - **This is the "aha" module.** Five lines of Python create a real,
      standards-compliant XML document. Demo it live to make the impact clear.
    - **Live coding:** Type the code on screen, line by line. Let learners
      follow along. Pause after each step to let people catch up.
    - **Common mistake:** Learners often forget the quotes around strings.
      For example, they type `text=What is your age?` instead of
      `text="What is your age?"`. Watch for this during exercises.
    - **Explore the XML together:** Open the saved file on screen and scroll
      through it. Point out the question text inside the tags. Emphasize that
      learners did not need to write any of this XML by hand.
    - **Extension activity:** Ask fast finishers to add two more questions of
      their own and save the file again.
