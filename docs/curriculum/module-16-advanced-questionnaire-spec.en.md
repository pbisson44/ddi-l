---
description: >-
  Module 16 of the ddi-l course: write a questionnaire spec, give gates and
  edit checks the meaning you intend on a missing answer, and check an
  instrument against the spec.
---

# Module 16: Advanced questionnaire specification

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Write a YAML spec for a short survey (modules, questions with
      response domains, gates and an edit check) that `ddi spec validate`
      accepts with no errors.
    - **O2.** Predict whether a gate or an edit check is true when an answer
      is missing, and write the condition that matches a stated intent.
    - **O3.** Rewrite the "go to" and "otherwise" instructions of a
      specification document as gates.
    - **O4.** Replace a pair of language-specific variables with one variable
      whose code list carries labels in both languages.
    - **O5.** Run `ddi conform` on an instrument, decide for each finding
      whether the spec or the instrument is wrong, and list the items that
      need a new version.

**Prerequisites:** [Module 7](module-07-cli-validation.en.md),
[Module 10](module-10-questionnaire-flows.en.md) and
[Module 15](module-15-update-and-version.en.md). Install the spec extra:
`pip install "ddi-l[spec]"`.

**Time:** 75 min self-paced / 90 min instructor-led.

**New in this module:** `ddi spec example`, `ddi spec validate`,
`ddi conform`, `example_spec()`, `load_spec()`, `parse_expression()`,
`normalise()`, `format_expression()`, `equivalent()`, `conform()`.

---

## 1. The spec is the source

In Module 10 you turned a written questionnaire specification into an
**instrument**: the questionnaire as DDI, its questions and the flow that
orders them. In many teams the specification is two documents kept by hand
beside the instrument: a **specification document** that shows each page of
the questionnaire, and a **spreadsheet** that lists the variables. The
documents and the instrument drift apart, and nobody can say which one is
right.

A **questionnaire spec** turns this around. It is a small file in **YAML**, a
plain-text format where indentation shows what belongs to what. It says what
the instrument must contain, and nothing about layout:

- its **modules**: the sections of the questionnaire, each a `Sequence` in
  the instrument;
- its **questions**, each with a **response domain** (or **domain**): the kind
  of answer it accepts, such as a code from a list, a number in a range, text
  or a date;
- its **gates**: conditions that decide whether a module or a question is
  shown;
- its **edit checks**: rules that test an answer and show a message when it
  looks wrong;
- the variables that come from outside the interview (**imported**, from a
  sample file for example) or are computed during it (**derived**).

ddi-l reads the spec and compares an instrument with it, so the spec stays the
record, and every version of the instrument is checked against it.

ddi-l ships a small spec for a fictional Pet survey. From the command line,
`ddi spec example` writes it, and `ddi spec validate` checks it against the
spec schema and against itself (every id appears once, every gate names a
question or variable of the spec, every minimum is below its maximum):

```bash
ddi spec example > pet-survey.spec.yaml
ddi spec validate pet-survey.spec.yaml
```

```text
pet-survey.spec.yaml: the spec 'pet-survey' is valid: 3 module(s), 5 question(s), 1 edit(s).
```

When something is wrong, each problem gives its place in the file as a path.
Positions count from 0, so `modules[1].questions[2]` is the third question of
the second module:

```text
pet-survey.spec.yaml: modules[1].questions[2].gate: 'PetAgee' is not a question or variable of the spec
```

Open `pet-survey.spec.yaml`. Its main parts look like this:

```yaml
spec: pet-survey
version: "1"
languages: [en, fr]

code_lists:
  Species:
    values:
      1: {en: Dog, fr: Chien}
      2: {en: Cat, fr: Chat}
      3: {en: Bird, fr: Oiseau}

modules:
  - id: household
    questions:
      - id: PetCount
        domain: {numeric: {min: 0, max: 20, decimals: 0}}

  - id: pets
    gate: PetCount > 0
    statements: [PetsIntro]
    questions:
      - id: PetKind
        domain: {code: {list: Species}}
      - id: PetName
        domain: {text: {max_length: 50}}
        gate: answered(PetKind)
      - id: PetAge
        domain: {numeric: {min: 0, max: 40, decimals: 0}}

edits:
  - id: age_range
    when: PetAge > 30
    module: pets
    message:
      en: Is the pet really over 30?
      fr: L’animal a-t-il vraiment plus de 30 ans ?
    severity: warning
```

The full file also has a third module, `visits`, and the imported and derived
variables. You can read it from Python too:

```python
from pathlib import Path

from ddi_l.spec import example_spec, load_spec

Path("pet-survey.spec.yaml").write_text(example_spec(), encoding="utf-8")
spec = load_spec("pet-survey.spec.yaml")
modules = [module.id for module in spec.modules]
print(spec.name, modules)  # -> pet-survey ['household', 'pets', 'visits']
```

Each module lists its questions, each with a domain and, if it has one, a gate:

```python
pets = spec.module("pets")
print(f"Gate: {pets.gate_text}")  # -> Gate: PetCount > 0
for question in pets.questions:
    kind, gate = question.domain.kind, question.gate_text or "-"
    print(question.id, kind, gate)  # -> PetName text answered(PetKind)
```

Where each part of a specification document or spreadsheet goes:

| Specification document or spreadsheet | Spec |
| --- | --- |
| A section, a group of pages | a module (`modules`) |
| A question and its answer boxes | a question with a `domain` |
| A list of answer categories | `code_lists`, used by a `code` domain |
| "Ask if ...", a condition on showing something | a `gate` on the module or the question |
| An edit rule and its message | an entry in `edits`, with `when`, `message` and `severity` |
| A value read from a sample file | `imported_variables` |
| A value calculated during the interview | `derived_variables` |
| Piped text with one copy of a variable per language | one variable, often a code (section 5) |

!!! tip "Two things to remember"
    - The spec says what the instrument contains, not how it looks.
    - A gate names questions and variables by id, never by question number. Numbers change when a question moves; ids do not.

## 2. Gates, edits and missing answers

A gate, or an edit check's `when`, is an expression: comparisons joined by
`and`, `or` and `not`, with five functions for answers that are not there:
`answered(x)`, `missing(x)`, `empty(x)` (not answered), `refused(x)` and
`today()`. The full grammar is in
[Check a questionnaire against a spec](../spec-conformance.en.md#gates-and-edits-the-expression-language).

The rule that matters most: **a comparison is false when the question has no answer.** So the three expressions below are not the same:

| `PetAge` | `PetAge > 30` | `not PetAge > 30` | `PetAge <= 30` |
| --- | --- | --- | --- |
| 35 | true | false | false |
| 12 | false | true | true |
| not answered | false | **true** | false |

`not PetAge > 30` shows a question to someone who never gave the age;
`PetAge <= 30` does not. Neither is wrong. Choose the one you mean, and write
it so a reader can see the choice: `PetAge <= 30 or missing(PetAge)` says out
loud what `not PetAge > 30` says quietly.

The same holds for "not equal": `PetKind != 1` is false when `PetKind` has no
answer, and `not PetKind = 1` is true.

`missing(x)` is `empty(x) or refused(x)`, and `answered(x)` is its negation.
Beside a comparison of the same question, `answered(x)` adds nothing, since
the comparison already needs an answer.

To compare two gates, ddi-l first rewrites each one in a standard form, its
**normal form**: `missing(x)` is spelled out, `not` is moved inward, the parts
of an `and` or an `or` are sorted, and an answer test that a comparison
already implies is dropped:

```python
from ddi_l.spec import equivalent, format_expression, normalise, parse_expression


def normal(text):
    return format_expression(normalise(parse_expression(text)))


print(normal("answered(PetAge) and PetAge > 30"))  # -> PetAge > 30
print(normal("missing(PetAge)"))  # -> empty(PetAge) or refused(PetAge)
print(equivalent("PetKind = 1 or PetKind = 2", "PetKind = 2 or PetKind = 1"))  # -> True
print(equivalent("PetAge > 30", "PetAge >= 31"))  # -> False
```

`equivalent()` compares normal forms first, and normalising calculates
nothing. Without the `logic` extra that is all it does, so `PetAge > 30` and
`PetAge >= 31` are different gates even for whole numbers. With the extra it
decides the rest: they still differ when `PetAge` may be a fraction, and agree
with `types={"PetAge": "integer"}`; `ddi conform` reads that from the spec's
domain. `not PetAge > 30` and `PetAge <= 30 or missing(PetAge)` look alike but
differ for an answer with no value to compare, a don't-know: the first holds
and the second does not. Pick one form and use it in both the spec and the
instrument. When a check reports two gates as different, read both before you
change either.

An **edit check's `when` is the error condition**: the check fires when it is
true. In the Pet survey, `age_range` fires when `PetAge > 30`. Because a
comparison is false on a missing answer, an edit never fires on a question
nobody answered. If a missing answer is itself the error, say so with
`missing(x)`.

## 3. From "go to" and "otherwise" to gates

Specification documents route with jumps: "If no pets, go to Section 3". An
instrument routes with structure: a module or a question runs when its gate is
true. To translate a jump, ask what the jump skips, and gate that:

| Specification document | Spec |
| --- | --- |
| Q1 PetCount. If 0, go to Section 3. | module `pets`, `gate: PetCount > 0` |
| Q3 PetName. Ask if Q2 is answered. | question `PetName`, `gate: answered(PetKind)` |
| If Q4 > 10 ask Q5, otherwise Q6. | `Q5`: `gate: PetAge > 10`; `Q6`: a gate you choose (below) |

"Otherwise" hides a decision. Q6 could be `not PetAge > 10` (it also shows
when the age is missing) or `PetAge <= 10` (it does not). Write the one the
survey needs, and check that the two gates together cover every case you want
covered, with no case in both.

Write the complement as a second gate rather than as an "else" branch, unless
you know your tool runs else branches. Two gates read the same in every tool
and in the spec.

## 4. Edit checks

An edit check needs four things: an id, the error condition, a message in each
language, and a severity.

```yaml
edits:
  - id: age_range
    when: PetAge > 30
    module: pets
    message:
      en: Is the pet really over 30?
      fr: L’animal a-t-il vraiment plus de 30 ans ?
    severity: warning
```

```python
edit = spec.edits[0]
print(edit.id, edit.when_text, edit.severity)  # -> age_range PetAge > 30 warning
```

- A **warning** (a soft edit) lets the respondent confirm and go on; an
  **error** (a hard edit) does not.
- Do not write an edit for what the domain already enforces. `PetAge` has a
  maximum of 40, so an edit for `PetAge > 40` would never fire.
- Write the message as a question the respondent can answer, in both
  languages.

## 5. Bilingual by design

DDI stores every text once per language (`xml:lang`). One question has its
English and its French text side by side; one code has an English and a French
label.

**Piped text** (also called a text fill) is a value inserted into a question's
text when the question is shown, such as the pet's kind in "What is your
dog's name?". Some teams keep one copy of each piped variable per language,
such as `RefMonth_en` and `RefMonth_fr`. Variables need no language suffix:

- **A value from a closed list** (a month, a species) is a code. Its code list
  carries the labels in both languages, and piping `RefMonth` into a
  question's text shows the label of the language in use. One variable
  replaces `RefMonth_en` and `RefMonth_fr`. Check once that your tool's piped
  text shows the label and not the code.
- **A value without words** (a year, an amount, a name) needs one variable and
  no labels.
- **A form that one language's grammar needs** (in French, *de janvier* but
  *d'avril*) is a second code list with labels in that language, used by that
  language's text only.
- **Only free text that differs by language** needs two variables.

```yaml
code_lists:
  Month:
    values:
      1: {en: January, fr: janvier}
      2: {en: February, fr: février}
      # ... to 12
derived_variables:
  - {name: RefMonth, type: code, values: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
```

In the instrument, declare each piped variable as an input of the item whose
text shows it, so the text and its value travel together. `ddi conform`
reports a question text or a code label missing in one of the spec's
languages (`spec.language.missing`).

## 6. Check the instrument against the spec

`ddi conform` finds each module, question and gate of the spec in an
instrument and reports what differs. To see it at work you need an
instrument. The block below builds a draft of the Pet survey's instrument
with the constructs of Module 10, the way a build team might deliver a first
version. It has some problems on purpose.

`ddi conform` finds a question by the name of its `QuestionConstruct`, and a
module by the name of its `Sequence` (among other places that the spec's
`match` block can change), so each is named after its id in the spec:

```python
import ddi_l as ddi
from ddi_l.models.base import InternationalString
from ddi_l.models.datacollection import (
    IfThenElse,
    Instrument,
    QuestionConstruct,
    Sequence,
    StatementItem,
)

draft = ddi.new_study(title="Pet Survey", agency="example.org")


def ask(name, en, fr=None):
    """Add a question in English (and French) and the construct that asks it."""
    question = draft.add_question(text=en, label=name)
    if fr:
        question.question_texts.append(InternationalString(text=fr, lang="fr"))
    return draft.add_item(
        QuestionConstruct, name=name, question_reference=question.to_reference()
    )


count = ask("PetCount", "How many pets live here?", "Combien d'animaux vivent ici ?")
intro = draft.add_item(StatementItem, name="PetsIntro")
kind = ask("PetKind", "What kind of pet is it?", "Quelle sorte d'animal est-ce ?")
name = ask("PetName", "What is its name?", "Quel est son nom ?")
age = ask("PetAge", "How old is it?")
colour = ask("PetColour", "What colour is it?", "De quelle couleur est-il ?")

ask_name = draft.add_item(IfThenElse, name="Ask PetName")
ask_name.set_condition("answered(PetKind)")
ask_name.then_construct_reference = name.to_reference()

household = draft.add_item(
    Sequence, name="household", control_construct_references=[count.to_reference()]
)
pets = draft.add_item(
    Sequence,
    name="pets",
    control_construct_references=[
        intro.to_reference(),
        kind.to_reference(),
        ask_name.to_reference(),
        age.to_reference(),
        colour.to_reference(),
    ],
)
main = draft.add_item(
    Sequence,
    name="Pet survey",
    control_construct_references=[household.to_reference(), pets.to_reference()],
)
instrument = draft.add_item(Instrument, name="Pet survey instrument")
instrument.control_construct_reference = main.to_reference()

print(draft.validate())  # -> []
draft.save("pet-instrument.xml")
```

The draft is valid DDI. Now compare it with the spec. `--module pets` compares
only the `pets` module, which keeps the output short:

```bash
ddi conform pet-instrument.xml --spec pet-survey.spec.yaml --module pets --format table
```

```text
pet-survey: Instrument 0e8d208b (Pet survey instrument)
module  severity  rule                    item       message
------  --------  ----------------------  ---------  --------------------------------------------------------------------------------------------------
pets    error     spec.gate.missing       -          Module pets is not gated; the spec says PetCount > 0.
pets    error     spec.domain.type        PetKind    The question PetKind has no response domain; the spec says code.
pets    error     spec.domain.type        PetName    The question PetName has no response domain; the spec says text.
pets    warning   spec.gate.unverifiable  PetName    The gate of question PetName cannot be compared: it is python code.
pets    warning   spec.language.missing   PetAge     The question text of PetAge has no fr.
pets    error     spec.domain.type        PetAge     The question PetAge has no response domain; the spec says numeric.
pets    warning   spec.item.extra         PetColour  Module pets has the question QuestionConstruct 92df660e (PetColour), which the spec does not list.
pets    info      spec.edit.unverifiable  age_range  The edit age_range: not verifiable (edit storage unknown).
4 error(s), 3 warning(s), 1 info.
```

The short ids (`0e8d208b`, `92df660e`) are the start of generated
identifiers, so yours differ. Each row is a **finding**: the module, its
severity, the rule that found it, the spec item it is about, and a message.
The last line counts them. `ddi conform` exits with 1 when there is at least
one error, so a script or a CI job can stop on it. The same check from
Python:

```python
from ddi_l.spec import conform

report = conform(ddi.read_ddi("pet-instrument.xml"), spec, module="pets")
print(report.summary)  # -> {'error': 4, 'warning': 3, 'info': 1}
```

What the rules in this module mean (the full list is in
[Check a questionnaire against a spec](../spec-conformance.en.md#rules)):

| Rule | Severity | What it means |
| --- | --- | --- |
| `spec.gate.missing` | error | The spec gates something the instrument shows to everyone. |
| `spec.gate.different` | error | The gates differ; both normal forms are shown. |
| `spec.domain.type` | error | The response domain is of another kind, or missing. |
| `spec.language.missing` | warning | A text or label lacks one of the spec's languages. |
| `spec.item.extra` | warning | The instrument has a question the spec does not list there. |
| `spec.gate.unverifiable` | warning | The stored gate cannot be read back. Check it by hand. |
| `spec.edit.unverifiable` | info | Where the instrument stores edit checks is not known. Check them by hand. |

Errors are differences to resolve; warnings and info say what is extra or
what was not compared. A clean run means 0 errors, not 0 findings.

The draft stores its gate as plain text, set with `set_condition()` in Module
10. `ddi conform` reads gates in the forms that questionnaire tools store; it
cannot read this one back, so it says so with a warning rather than guess.

**Spec or instrument?** For each error, ask which of the two says what the
survey needs. The spec is the record, so the instrument is usually the one to
fix. But a spec can be wrong too: a question added on purpose that nobody
wrote into the spec, or a bound typed wrong. Then fix the spec, give it a new
`version`, and run the check again.

## 7. Version the change

A DDI reference names one exact version of an item (Module 15). When you fix
an item, it gets a new version, so every item that refers to it must be
revised to point at the new version, and so on up to the instrument. Items
that refer to nothing you changed keep their versions. A new item, such as a
new gate, starts at its first version, and the item that now refers to it is
revised.

For example, fixing the condition of `Ask PetName` changes that
`IfThenElse`. The `pets` sequence refers to it, so it is revised; the main
sequence refers to `pets`, and the instrument refers to the main sequence, so
both are revised too. The `household` sequence and the questions keep their
versions.

Make the whole fix one release: one date (`versionDate`) and one
responsibility (the person who made it) for every new and revised item, as in
[Module 15](module-15-update-and-version.en.md). Then run `ddi conform` again on
the new version, and keep its output with the release.

## 8. Spec-writing checklist

- [ ] Every module and question has an id that does not depend on its number.
- [ ] Every question has a domain, with bounds where the answer has bounds.
- [ ] Every "go to" is a gate on what it skips; every "otherwise" is a second gate.
- [ ] For each gate, you decided what happens when an answer is missing.
- [ ] Every edit's `when` is the error, its message is in each language, its severity is set.
- [ ] No variable has a language suffix.
- [ ] `ddi spec validate` passes, and `ddi conform` reports 0 errors.
- [ ] A copy of the spec with one gate or bound changed gives exactly one new error.

---

!!! example "Scenario"
    The Pet survey team sends you a specification document and a spreadsheet
    of variables. Section 1 says: "Q1 How many pets live here? (0 to 20). If
    0, go to Section 3." Section 2 says: "Q2 What kind of pet is it? (Dog,
    Cat, Bird). Q3 What is its name? (text, up to 50 characters; ask if Q2 is
    answered). Q4 How old is it? (0 to 40 years). If Q4 > 10, ask Q5 (vet
    visits last year, 0 to 50), otherwise ask Q6 (number of toys, 0 to 99)."
    Section 3 says: "Q7 When did you last visit a vet? (a date)." The
    spreadsheet lists `KindText_en` and `KindText_fr` for the pet kind piped
    into Q3's text, and an edit: "Q4 over 30: please confirm."

    Your task: decide what each gate does with a missing answer, write the
    spec, and check an instrument against it.

---

## Exercises

1. **(O2)** Write the gates for Q5 and Q6 of the scenario. Q6 must show when the age is missing. Check their normal forms. Then predict whether the scenario's edit, `when: PetAge > 30`, fires for a pet aged 35, a pet aged 12, and a pet with no age.

    **Expected output:**

    ```text
    PetAge > 10
    not PetAge > 10
    ```

    ??? success "Answer"
        Q5 is `PetAge > 10`. Q6 shows when Q5 does not, including a missing age, so it is `not PetAge > 10` (or, saying the same out loud, `PetAge <= 10 or missing(PetAge)`; pick one form and keep it).

        ```python
        print(normal("PetAge > 10"))  # -> PetAge > 10
        print(normal("not PetAge > 10"))  # -> not PetAge > 10
        ```

        Had Q6 been `PetAge <= 10`, a respondent with no age would see neither Q5 nor Q6.

        The edit fires for 35 only. For 12 the comparison is false, and for a missing age a comparison is always false. To flag a missing age, you would write a second edit with `when: missing(PetAge)`.

2. **(O3)** A specification document for a housing survey says: "H1 Do you own your home? (1 Yes, 2 No). If No, go to H4. H2 How many years ago did you buy it? H3 Do you have a mortgage? H4 How many rooms are there?" The questions' ids are `Own`, `YearsOwned`, `Mortgage` and `Rooms`. (a) Write the gate on H2 and H3 that does exactly what the jump says, including when H1 has no answer. (b) The survey owner says H2 and H3 are for owners only. Write that gate. Check both with `normal()`.

    **Expected output:**

    ```text
    not Own = 2
    Own = 1
    ```

    ??? success "Answer"
        (a) The jump fires only on "No". A respondent who did not answer H1 does not jump, so sees H2 and H3: the gate is `not Own = 2`. (b) Owners only: `Own = 1`. The two differ only when H1 has no answer, so write the one the survey means. H4 has no gate: everyone sees it.

        ```python
        print(normal("not Own = 2"))  # -> not Own = 2
        print(normal("Own = 1"))  # -> Own = 1
        ```

3. **(O4)** Replace `KindText_en` and `KindText_fr` with one variable, and write the YAML of the code list it uses.

    ??? success "Answer"
        The pet kind comes from a closed list, so it is a code: the question `PetKind` itself, with the code list `Species`, whose labels are in English and French. Q3's English text pipes in `PetKind`, and so does its French text; each shows the label of its language (check once that your tool's piped text shows labels). No derived variable is needed, since the answer already is the value.

        ```yaml
        code_lists:
          Species:
            values:
              1: {en: Dog, fr: Chien}
              2: {en: Cat, fr: Chat}
              3: {en: Bird, fr: Oiseau}
        ```

4. **(O1)** Write `my-pets.spec.yaml` for the scenario: three modules (`household`, `pets`, `visits`), the seven questions with their domains, the gates of the `pets` module, of Q3 and of exercise 1, and the edit as a soft check. Name the questions `PetCount`, `PetKind`, `PetName`, `PetAge`, `VetVisits`, `Toys` and `LastVisit`. Run `ddi spec validate my-pets.spec.yaml`.

    **Expected output:**

    ```text
    my-pets.spec.yaml: the spec 'my-pets' is valid: 3 module(s), 7 question(s), 1 edit(s).
    ```

    ??? success "Answer"
        ```yaml
        spec: my-pets
        version: "1"
        languages: [en, fr]

        code_lists:
          Species:
            values:
              1: {en: Dog, fr: Chien}
              2: {en: Cat, fr: Chat}
              3: {en: Bird, fr: Oiseau}

        modules:
          - id: household
            questions:
              - id: PetCount
                domain: {numeric: {min: 0, max: 20, decimals: 0}}

          - id: pets
            gate: PetCount > 0
            questions:
              - id: PetKind
                domain: {code: {list: Species}}
              - id: PetName
                domain: {text: {max_length: 50}}
                gate: answered(PetKind)
              - id: PetAge
                domain: {numeric: {min: 0, max: 40, decimals: 0}}
              - id: VetVisits
                domain: {numeric: {min: 0, max: 50, decimals: 0}}
                gate: PetAge > 10
              - id: Toys
                domain: {numeric: {min: 0, max: 99, decimals: 0}}
                gate: not PetAge > 10

          - id: visits
            questions:
              - id: LastVisit
                domain: {date: {type: Date}}

        edits:
          - id: age_over_30
            when: PetAge > 30
            module: pets
            message:
              en: Is the pet really over 30?
              fr: L’animal a-t-il vraiment plus de 30 ans ?
            severity: warning
        ```

        "If 0, go to Section 3" becomes the gate of the module it skips, `pets`. If `ddi spec validate` reports a problem, its path says where: `modules[1].questions[2]` is the third question of the second module.

5. **(O5)** Build the draft instrument of section 6 if you have not, and run `ddi conform pet-instrument.xml --spec pet-survey.spec.yaml --module pets --format table`. For each finding, say whether the spec or the instrument is wrong, and what to change. The survey owner tells you `PetColour` was added on purpose this wave. Then list the items that get a new version when you add PetAge's French text and the module gate.

    **Expected output:** the table of section 6, ending with:

    ```text
    4 error(s), 3 warning(s), 1 info.
    ```

    ??? success "Answer"
        | Finding | Wrong | What to change |
        | --- | --- | --- |
        | `spec.gate.missing` (module `pets`) | instrument | Show `pets` only when `PetCount > 0`: wrap it in an `IfThenElse` with that condition. |
        | `spec.domain.type` (PetKind, PetName, PetAge) | instrument | The draft's questions have no response domain. Give PetKind the `Species` codes, PetName text up to 50 characters, PetAge a number from 0 to 40. |
        | `spec.gate.unverifiable` (PetName) | neither | Check by hand: the draft's condition reads `answered(PetKind)`, the spec's gate. Nothing to change. |
        | `spec.language.missing` (PetAge) | instrument | Add the French text of the question. |
        | `spec.item.extra` (PetColour) | spec | It was added on purpose: add `PetColour` and its domain to the `pets` module of the spec, and give the spec a new `version`. |
        | `spec.edit.unverifiable` (age_range) | neither | Not compared. Check the edit in the instrument by hand. |

        Items with a new version after the two fixes: PetAge's question (new text); the PetAge construct, which refers to it; the `pets` sequence, which refers to the construct; the new `IfThenElse` for the module gate, at its first version; the main sequence, which now refers to that `IfThenElse` instead of to `pets`; and the instrument. The `household` sequence, the other questions and constructs, and `Ask PetName` keep their versions. All new and revised items share one `versionDate` and one responsibility.

6. **(O2, O5)** For an instrument whose gates it can read, `ddi conform` reports: `spec.gate.different  Toys  Question Toys is gated by PetAge <= 10; the spec says not PetAge > 10.` Which one is right, and what do you change?

    ??? success "Answer"
        The scenario says Q6 shows when Q5 does not, so a missing age must show Q6: the spec (`not PetAge > 10`) is right. Change the instrument's gate. The two gates differ only for a missing age, which is why `equivalent()` and `ddi conform` treat them as different.

---

## Quiz

???+ question "Question 1 (O2): PetAge has no answer. Which gate is true?"
    **A.** `PetAge > 30`

    **B.** `PetAge <= 30`

    **C.** `not PetAge > 30`

    **D.** `PetAge != 30`

    ??? success "Answer"
        **C.** A comparison is false without an answer, so A, B and D are
        false, and `not` turns A's false into true.

???+ question "Question 2 (O2): An edit check has when: PetAge > 30. A respondent skips PetAge. Does the check fire?"
    **A.** Yes: a missing answer is an error.

    **B.** No: a comparison is false without an answer. To flag a missing
    age, write an edit with `when: missing(PetAge)`.

    **C.** Only if its severity is `error`.

    **D.** Only in the French version.

    ??? success "Answer"
        **B.** The check fires when `when` is true, and `PetAge > 30` is
        false when there is no answer.

???+ question "Question 3 (O3): The document says: if Q4 > 10 ask Q5, otherwise Q6. A respondent with no age must see Q6. Which gate do you write for Q6?"
    **A.** `PetAge <= 10`

    **B.** No gate: an else branch is enough.

    **C.** `PetAge < 10`

    **D.** `not PetAge > 10`

    ??? success "Answer"
        **D.** `not PetAge > 10` is true when `PetAge > 10` is false,
        including when the age is missing. A and C are false on a missing
        age (and C also hides Q6 from a pet aged exactly 10). A second gate
        reads the same in every tool, which an else branch does not.

???+ question "Question 4 (O4): Why does a month need no language-specific copies of its variable?"
    **A.** A code's label is stored in each language, and piped text shows
    the label of the language in use.

    **B.** Months are numbers.

    **C.** French has no month names.

    **D.** The data file holds both.

    ??? success "Answer"
        **A.** One code, two labels, one variable.

???+ question "Question 5 (O1): ddi spec validate prints this. What do you fix?"
    ```text
    my.spec.yaml: modules[0].questions[1].domain.numeric: min is greater than max
    ```

    **A.** The name of the first module.

    **B.** The bounds of the second question of the first module.

    **C.** The gate of the first question.

    **D.** Nothing: it is a warning.

    ??? success "Answer"
        **B.** Positions count from 0, so `modules[0].questions[1]` is the
        second question of the first module, and its numeric `min` is above
        its `max`. `ddi spec validate` reports problems, not warnings: the
        spec does not load until you fix it.

???+ question "Question 6 (O5): ddi conform reports 0 errors and 12 warnings. Is the instrument right?"
    **A.** No: warnings are errors.

    **B.** Only if the warnings drop to 0.

    **C.** It cannot tell.

    **D.** Yes, as far as the spec says; the warnings say what is extra or
    was not compared.

    ??? success "Answer"
        **D.** Read the warnings: a shared module that another spec covers
        is a typical one, and an unverifiable gate needs a check by hand. To
        be sure the check is live, change one gate in a copy of the spec and
        expect exactly one new error.

???+ question "Question 7 (O5): ddi conform reports spec.item.extra for PetColour, which the survey owner added on purpose. What do you change?"
    **A.** Remove `PetColour` from the instrument.

    **B.** Nothing: warnings can be ignored.

    **C.** Add `PetColour` to the spec and give the spec a new version.

    **D.** Rename `PetColour` so it is not found.

    ??? success "Answer"
        **C.** Here the spec is the one that is wrong: it does not list a
        question the survey needs. Fix the record, version it, and run the
        check again.

???+ question "Question 8 (O5): You fix the condition of the IfThenElse that gates PetName, inside the pets sequence. Which items get a new version?"
    **A.** The `IfThenElse`, the `pets` sequence, the main sequence and the
    instrument.

    **B.** Only the `IfThenElse`.

    **C.** Every item in the instrument.

    **D.** Only the instrument.

    ??? success "Answer"
        **A.** The changed item and every item that refers to it, up to the
        instrument. Items that refer to nothing you changed, such as the
        `household` sequence, keep their versions.

---

## Going further (optional)

### When your tool cannot say it

A questionnaire tool stores each gate in a form it can run. Many have a
condition editor with a fixed set of operators, and fall back on code in a
scripting language for anything else. A gate the editor holds stays editable
by spec writers; a gate in code needs a programmer to change it. So write
gates the editor can hold, as long as the meaning stays exactly the same.

Start from the operators the tool's documentation lists. An operator the
documentation lists can be used as it describes; one you have only seen in an
exported file is a guess. Documentation can be incomplete too: it may name an
operator without saying what it does with a missing answer, and then a gate
that depends on it should be checked in a preview.

Suppose your tool's editor offers `=`, `>`, "is empty", "is refused" and "any
of" for a coded question, joined by `and` or `or`, and nothing else. Three
rewrites keep the meaning exactly and let more gates fit:

1. **Drop an answer test a comparison already implies.**
   `answered(PetAge) and PetAge > 30` needs "is not empty", which the editor
   lacks. Its normal form (section 2) is `PetAge > 30`, which fits.
2. **Read a choice among one question's codes as one "any of".** In
   `PetCount > 1 and (PetKind = 1 or PetKind = 2)`, the part in parentheses
   is "PetKind is any of 1, 2": one condition, joined to the other by `and`.
3. **Use a value set the spec declares.** `HasPets` is declared with the
   values 0 and 1, so `HasPets != 1` is `HasPets = 0`. The expressions alone
   cannot tell you that:

    ```python
    print(equivalent("HasPets != 1", "HasPets = 0"))  # -> False
    print(spec.derived_variables[0].values)  # -> ('0', '1')
    ```

    The values come from the spec, so the rewrite is yours to make. Note
    beside the gate where the values come from, so whoever changes them knows
    to change the gate too.

Anything else stays in the tool's code, and that is fine: it is still exact.
What you must never do is guess an undocumented part of a tool's format, an
operator number say, to force a gate into the editor. A wrong guess is a wrong
gate that looks right. If a gap matters, report it to the tool's maker with a
fictional example, and keep the code until the answer comes.

**Optional exercise.** Your tool's editor offers what the paragraph above
assumes. Which of these can it hold, after an exact rewrite where one exists?
`PetCount > 2`, `PetKind = 1 or PetKind = 3`, `answered(PetName)`,
`PetCount < 2`, `answered(PetCount) and PetCount > 2`.

??? note "Answer"
    - `PetCount > 2`: yes, as written.
    - `PetKind = 1 or PetKind = 3`: yes, as "PetKind is any of 1, 3".
    - `answered(PetName)`: no. It is "not empty and not refused", and the
      editor has no "not". It stays in code.
    - `PetCount < 2`: yes, after a rewrite. The spec declares PetCount a whole
      number from 0, so `PetCount < 2` is `PetCount = 0 or PetCount = 1`.
    - `answered(PetCount) and PetCount > 2`: yes. Its normal form drops the
      answer test.

    ```python
    domain = spec.module("household").questions[0].domain
    print(domain.minimum, domain.maximum, domain.decimals)  # -> 0 20 0
    print(normal("answered(PetCount) and PetCount > 2"))  # -> PetCount > 2
    ```

---

## Check yourself

- [ ] I can write a YAML spec for a short survey that `ddi spec validate` accepts with no errors. (O1)
- [ ] I can predict whether a gate or an edit check is true when an answer is missing, and write the condition I mean. (O2)
- [ ] I can rewrite "go to" and "otherwise" instructions as gates. (O3)
- [ ] I can replace language-specific copies of a variable with one variable whose code list has labels in both languages. (O4)
- [ ] I can run `ddi conform`, decide whether the spec or the instrument is wrong for each finding, and list the items that need a new version. (O5)

---

!!! tip "Instructor notes"
    - Start with the missing-answer table in section 2 on the board. Ask the room to fill in the last row before you show it; most people get `not PetAge > 30` wrong.
    - Bring a real page of a specification document if you have one, with its jumps and "otherwise". Translating one page into gates together is the best exercise in the module.
    - Before learners run `ddi conform` in section 6, ask them to predict its findings from the draft's code. The problems are there on purpose: no module gate, no response domains, no French text for PetAge, an extra question.
    - Learners used to spreadsheets ask for one variable per language out of habit. Show the code list with two labels and the piped text in both languages.
    - Section 7 applies Module 15; if learners are fresh from it, go fast.
    - The Going further section is where tool knowledge meets spec writing. Stress that a gate kept in the tool's own code is a correct answer, and that guessing an undocumented format is the one thing never to do.

---

**See also:** [Module 10: Questionnaire flows](module-10-questionnaire-flows.en.md) | [Check a questionnaire against a spec](../spec-conformance.en.md)
