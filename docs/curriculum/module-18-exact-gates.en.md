---
description: >-
  Optional Module 18 of the ddi-l course: with the logic extra, decide whether
  two gates hold for the same respondents, name a respondent they disagree on,
  and test a gate on respondents you choose.
---

# Module 18 (optional): Decide gates exactly

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Check whether two gates hold for the same respondents with
      `decide()`, and read its verdict: `equivalent`, `different` with a
      respondent who tells them apart, or `unknown` with a reason.
    - **O2.** Give `decide()` the type of each question, taken from the
      spec's response domains, and explain why a whole-number question can
      make two gates agree.
    - **O3.** Test a gate with `evaluate()` on respondents you choose: one who
      left the question empty, one who refused it, one who answered without a
      value, and one who gave a value.
    - **O4.** Review gates translated from a specification document, and name
      for each one that differs from the intended gate a respondent it routes
      wrongly.
    - **O5.** Say what the `logic` extra changes in `equivalent()` and
      `ddi conform`, and what they do without it.

**Prerequisites:** [Module 16](module-16-advanced-questionnaire-spec.en.md).
This module is optional: the capstone does not need it.

!!! warning "Install the spec and logic extras first"
    This module needs the `spec` extra of Module 16 and the `logic` extra,
    which adds the Z3 solver (about 57 MB). `pip install ddi-l` alone
    installs neither:

    ```bash
    pip install -U "ddi-l[spec,logic]"
    ```

**Time:** 45 min self-paced / 60 min instructor-led.

**New in this module:** `decide()`, its verdict (`outcome`, `example`,
`reason`), `Example.describe()`, `evaluate()`, `Answer`, the `types`
argument, `equivalent(exact=...)` and `ddi conform --semantics`.

---

## 1. What a normal form cannot tell you

In Module 16, `normalise()` put each gate in a normal form, and
`equivalent()` compared those forms. A normal form spells things out and
moves `not` inward, but it calculates nothing. So two gates that always agree
can still have different normal forms:

```python
from ddi_l.spec import equivalent

print(equivalent("PetCount > 0", "PetCount >= 1", exact=False))  # -> False
```

`exact=False` asks for the normal forms only, which is all `equivalent()`
does without the `logic` extra. `False` then means only "written
differently". It does not mean that some household is routed differently.

The `logic` extra adds a **solver**: a program that searches every possible
respondent for one that two gates disagree on. When it finds none, the gates
are equivalent. When it finds one, it shows you that respondent.

## 2. Check that the extra is installed

`decide()` asks the solver. Without the extra it raises
`LogicDependencyError`, which says what to install:

```python
from ddi_l.spec import LogicDependencyError, decide

try:
    print(decide("x > 3", "x >= 4").outcome)  # -> different
except LogicDependencyError as error:
    print(error)
```

If you see `different`, the extra works. If you see
`Deciding expressions needs z3-solver: pip install "ddi-l[logic]"`, run that
command.

## 3. Three verdicts

`decide(left, right)` returns a **verdict** with three parts:

| Part | What it holds |
| --- | --- |
| `outcome` | `"equivalent"`, `"different"` or `"unknown"` |
| `example` | For `different`: a respondent one gate holds for and the other does not |
| `reason` | For `unknown`: why the solver could not decide |

```python
same = decide("PetAge + 1 > 11", "PetAge > 10")
print(same.outcome)  # -> equivalent

apart = decide("answered(PetKind) and PetAge > 30", "PetAge > 30")
print(apart.outcome)  # -> different
print(apart.example.describe())  # -> PetAge is 31 and PetKind is empty

unsure = decide('PetName = "Rex"', 'PetName < "S"')
print(unsure.outcome)  # -> unknown
print(unsure.reason)  # -> PetName < "S" compares text by order
```

- The first pair does arithmetic: `PetAge + 1 > 11` holds exactly when
  `PetAge > 10` does. Normalising could not see that; the solver can.
- The second pair differs for a pet aged 31 whose kind was left empty. Only
  the first gate needs an answer to `PetKind`.
- The third pair compares text by alphabetical order, which the solver does
  not model. `unknown` is honest: check such a gate by hand.

`describe()` puts the respondent in words. A question it does not name was
left empty, unless the sentence says otherwise.

!!! tip "One respondent is enough"
    A `different` verdict gives one respondent, not all of them. Fix the
    gate, then run `decide()` again: it may find another. Another version of
    the solver may also pick another respondent than the ones printed here;
    any respondent it gives is one the two gates disagree on.

## 4. Who is a respondent?

The solver tries every kind of respondent. For each question, a respondent
can:

| A respondent... | In `describe()` | A comparison such as `PetAge > 10` |
| --- | --- | --- |
| left it empty | `PetAge is empty` | is false |
| refused it | `PetAge is refused` | is false |
| answered without a value, such as "don't know" | `PetAge is answered with no value` | is false |
| gave a value | `PetAge is 12` | compares the value |
| gave several values (a question compared only with `=` and `!=`) | `PetKind is 1 and 2` | `PetKind = 1` holds if 1 is among them |

`missing(x)` means empty or refused. An answer without a value is answered,
so it is not missing. That third row is the one people forget. Module 16
called these two gates for Q6 almost the same:

```python
verdict = decide("not PetAge > 10", "PetAge <= 10 or missing(PetAge)")
print(verdict.outcome)  # -> different
print(verdict.example.describe())  # -> PetAge is answered with no value
```

A respondent who answers "don't know" sees Q6 with the first gate and skips
it with the second. Both may be what a survey wants; the solver makes you
choose on purpose.

## 5. Tell the solver what each question is

Unless told otherwise, the solver lets a number be a fraction:

```python
verdict = decide("PetCount > 0", "PetCount >= 1")
print(verdict.example.describe())  # -> PetCount is 0.25
```

No household has a quarter of a pet. The spec says so: `PetCount` has
`decimals: 0`. The `types` argument passes that on. It maps each name to
`numeric`, `integer`, `date`, `text` or `code`:

```python
print(decide("PetCount > 0", "PetCount >= 1", types={"PetCount": "integer"}).outcome)
# -> equivalent
```

Rather than type each type by hand, read them from the spec. This function
does what `ddi conform` does with the spec's response domains:

```python
from pathlib import Path

from ddi_l.spec import example_spec, load_spec

Path("pet-survey.spec.yaml").write_text(example_spec(), encoding="utf-8")
spec = load_spec("pet-survey.spec.yaml")


def spec_types(spec):
    """What the spec says each question is, as decide() takes it."""
    types = {}
    for question in spec.questions:
        domain = question.domain
        if domain is None:
            continue
        if domain.kind == "numeric":
            types[question.id] = "integer" if domain.decimals == 0 else "numeric"
        else:
            types[question.id] = domain.kind
    return types


types = spec_types(spec)
print(types["PetCount"], types["PetKind"], types["VisitDate"])  # -> integer code date
```

With the extra, `equivalent()` uses the solver too, and takes the same
`types`:

```python
print(equivalent("PetCount > 0", "PetCount >= 1", types=types))  # -> True
```

## 6. Test a gate on respondents you choose

`decide()` searches for a respondent. `evaluate()` does the opposite: you
give it one respondent, and it says whether a gate holds for them. A
respondent is a dictionary from question names to `Answer` objects. An
`Answer` has a state (`"empty"`, `"refused"` or `"answered"`) and, when
answered, a set of values. Numbers are `Fraction`s, so that `0.1` stays
exact:

```python
from fractions import Fraction

from ddi_l.spec import Answer, evaluate

respondents = {
    "left it empty": {},
    "refused": {"PetAge": Answer("refused")},
    "did not know": {"PetAge": Answer("answered")},
    "aged 8": {"PetAge": Answer("answered", frozenset({Fraction(8)}))},
    "aged 12": {"PetAge": Answer("answered", frozenset({Fraction(12)}))},
}
for gate in ("not PetAge > 10", "PetAge <= 10 or missing(PetAge)"):
    print(gate, [evaluate(gate, answers) for answers in respondents.values()])
# -> not PetAge > 10 [True, True, True, True, False]
# -> PetAge <= 10 or missing(PetAge) [True, True, False, True, False]
```

The two rows differ in one column only, "did not know", as `decide()` said.
A table like this is a test of the gate: write the respondents first, say
what the gate should do for each, then check.

A `different` verdict can be checked the same way: its `example` holds
answers that `evaluate()` takes. Take the verdict of section 5, without types:

```python
verdict = decide("PetCount > 0", "PetCount >= 1")
print(evaluate("PetCount > 0", verdict.example.answers))  # -> True
print(evaluate("PetCount >= 1", verdict.example.answers))  # -> False
```

## 7. Review translated gates

A colleague translated the "go to" instructions of a specification document
into gates. You have the gates the survey owner intends. Check them all in
one loop:

```python
intended = {
    "PetName": "answered(PetKind)",
    "VetVisits": "PetAge > 10",
    "Toys": "not PetAge > 10",
}
translated = {
    "PetName": "not empty(PetKind) and not refused(PetKind)",
    "VetVisits": "PetAge >= 11",
    "Toys": "PetAge <= 10",
}
for question, gate in intended.items():
    verdict = decide(gate, translated[question], types=types)
    if verdict.outcome == "different":
        print(f"{question}: differs when {verdict.example.describe()}")
    else:
        print(f"{question}: {verdict.outcome}")
# -> PetName: equivalent
# -> VetVisits: equivalent
# -> Toys: differs when PetAge is answered with no value
```

Two translations are written differently and are right. One routes a
"don't know" past `Toys`. That is the line to discuss with your colleague,
not the other two.

## 8. In `ddi conform`

With the extra installed, `ddi conform` compares gates and edits as
`decide()` does, once their normal forms differ. It takes the types from the
spec's domains, as `spec_types()` does. So:

- a gate written differently that always agrees with the spec's is not
  reported: `PetCount >= 1` passes for a spec that says `PetCount > 0`;
- a gate that differs names a respondent in its message:

```text
Module pets is gated by PetCount > 1; the spec says PetCount > 0 (they differ when PetCount is 1).
```

`--semantics syntactic` compares normal forms only, as without the extra;
`--semantics smt` fails when the extra is not installed. From Python, pass
`semantics="syntactic"` or `semantics="smt"` to `conform()`.

| | Without the `logic` extra | With it |
| --- | --- | --- |
| `equivalent()` | Compares normal forms: `False` may be a false alarm | Decides: `False` means a respondent is routed differently |
| `decide()` | Raises `LogicDependencyError` | Returns a verdict |
| `ddi conform` | Reports every gate written differently | Reports only gates that differ, with a respondent |

## 9. Limits

- **Some comparisons are not modelled.** Text compared by order, a name
  compared both with numbers and with text, and a value used as a condition
  give `unknown`. Check those gates by hand.
- **The code list is not read.** `decide()` knows that `PetKind` is a code,
  not which codes it has, so a respondent may answer a code your list lacks.
- **A work limit bounds the solver**, not a clock, so the same pair of gates
  gets the same verdict on every run, however busy the machine. A pair too
  hard to decide within that work is `unknown`.

---

!!! example "Scenario"
    The Pet survey team is reviewing a new version of the questionnaire. A
    colleague translated the specification document's jumps into gates, and
    the build team has changed a few gates "to make them simpler". Before
    anything goes to the field, you check every changed gate against the
    spec and list each respondent who would now see different questions.

---

## Exercises

1. **(O1)** Predict the verdict of each pair, then check it with `decide()`. For each `different`, print the respondent; for each `unknown`, the reason. (a) `missing(PetKind)` and `empty(PetKind) or refused(PetKind)`. (b) `PetAge > 10` and `PetAge * 2 > 20`. (c) `PetKind = 1 or PetKind = 2` and `PetKind != 3`. (d) `PetName = "Rex"` and `PetName < "S"`.

    **Expected output:**

    ```text
    equivalent
    equivalent
    different: PetKind is another value
    unknown: PetName < "S" compares text by order
    ```

    ??? success "Answer"

        ```python
        pairs = [
            ("missing(PetKind)", "empty(PetKind) or refused(PetKind)"),
            ("PetAge > 10", "PetAge * 2 > 20"),
            ("PetKind = 1 or PetKind = 2", "PetKind != 3"),
            ('PetName = "Rex"', 'PetName < "S"'),
        ]
        for left, right in pairs:
            verdict = decide(left, right, types=types)
            if verdict.outcome == "different":
                print(f"different: {verdict.example.describe()}")
            elif verdict.outcome == "unknown":
                print(f"unknown: {verdict.reason}")
            else:
                print(verdict.outcome)
        ```

        (a) is the definition of `missing()`. (b) is arithmetic. (c) differs for a code that neither gate names: the solver does not read the `Species` list, so for it a fourth code exists. A respondent with two codes, 1 and 3, also tells them apart. (d) compares text by order, which the solver does not model.

2. **(O2)** Without `types`, `decide("PetAge > 30", "PetAge >= 31")` says `different`. Print the respondent. Then decide the pair again with the types of the spec, and explain the change.

    **Expected output:**

    ```text
    PetAge is 30.25
    equivalent
    ```

    ??? success "Answer"

        ```python
        print(decide("PetAge > 30", "PetAge >= 31").example.describe())  # -> PetAge is 30.25
        print(decide("PetAge > 30", "PetAge >= 31", types=types).outcome)  # -> equivalent
        ```

        Without types, a pet can be 30.25 years old, which `PetAge > 30` accepts and `PetAge >= 31` does not. The spec gives `PetAge` `decimals: 0`, so `spec_types()` makes it an `integer`, and no whole number lies between 30 and 31.

3. **(O3)** The spec's edit `age_range` fires when `PetAge > 30`. A second edit should fire when the age is missing. Using the `respondents` of section 6 plus a pet aged 31, print for each respondent whether `PetAge > 30` fires, then whether `missing(PetAge)` fires. Which respondent without a usable age is caught by neither? Write a third edit that catches only that respondent.

    **Expected output:**

    ```text
    [False, False, False, False, False, True]
    [True, True, False, False, False, False]
    [False, False, True, False, False, False]
    ```

    ??? success "Answer"

        ```python
        aged_31 = {"PetAge": Answer("answered", frozenset({Fraction(31)}))}
        everyone = [*respondents.values(), aged_31]
        print([evaluate("PetAge > 30", answers) for answers in everyone])
        print([evaluate("missing(PetAge)", answers) for answers in everyone])
        dont_know = "answered(PetAge) and not (PetAge > 30 or PetAge <= 30)"
        print([evaluate(dont_know, answers) for answers in everyone])
        ```

        The "did not know" respondent is caught by neither: the answer has no value, so the comparison is false, and it is answered, so it is not missing. The expressions have no word for "don't know", but the third edit says it: the age is answered, yet neither `PetAge > 30` nor `PetAge <= 30` holds, which happens only when there is no value to compare.

4. **(O4)** Module 16's housing survey asks `Own` (1 Yes, 2 No), then `YearsOwned` and `Mortgage` to everyone who does not answer "No", then `Refinanced` to owners of more than 5 years. A colleague wrote the gates below. Check each against the intended gate, with `Own` a code and `YearsOwned` a whole number, and print one line per question.

    ```python
    intended = {
        "YearsOwned": "not Own = 2",
        "Mortgage": "not Own = 2",
        "Refinanced": "YearsOwned > 5",
    }
    translated = {
        "YearsOwned": "not Own = 2",
        "Mortgage": "Own = 1",
        "Refinanced": "YearsOwned >= 6",
    }
    ```

    **Expected output:**

    ```text
    YearsOwned: equivalent
    Mortgage: differs when Own is answered with no value
    Refinanced: equivalent
    ```

    ??? success "Answer"

        ```python
        housing = {"Own": "code", "YearsOwned": "integer"}
        for question, gate in intended.items():
            verdict = decide(gate, translated[question], types=housing)
            if verdict.outcome == "different":
                print(f"{question}: differs when {verdict.example.describe()}")
            else:
                print(f"{question}: {verdict.outcome}")
        ```

        `Mortgage` is the one to raise. With `Own = 1`, a respondent who answers "don't know" to `Own`, or leaves it empty or refuses it, skips the mortgage question but still sees `YearsOwned`. Either both questions use `not Own = 2`, or the survey owner decides they are for home owners only and both use `Own = 1`. The two gates written differently for `Refinanced` agree for every whole number of years.

5. **(O1, O3)** Show that a `different` verdict is right: decide `not PetAge > 10` against `PetAge <= 10`, then evaluate both gates on the verdict's respondent.

    **Expected output:**

    ```text
    True
    False
    ```

    ??? success "Answer"

        ```python
        verdict = decide("not PetAge > 10", "PetAge <= 10", types=types)
        print(evaluate("not PetAge > 10", verdict.example.answers))  # -> True
        print(evaluate("PetAge <= 10", verdict.example.answers))  # -> False
        ```

        Whatever respondent the solver gives (an empty, refused or "don't know" age), one gate holds and the other does not. `ddi-l` makes the same check on every `different` verdict before it reports one.

6. **(O5)** With the `logic` extra, `ddi conform` reports: `Module pets is gated by PetCount > 1; the spec says PetCount > 0 (they differ when PetCount is 1).` (a) Who is routed wrongly, and which side do you fix? (b) The instrument had `PetCount >= 1` instead. What does `ddi conform` report with the extra, and what without it?

    ??? success "Answer"

        (a) A household with exactly one pet skips the pets module, though the spec asks it about its pet. The spec is the record, so fix the instrument's gate, unless the survey owner says that one-pet households were meant to skip it; then fix the spec and give it a new version.

        (b) With the extra, nothing: the spec says `PetCount` is a whole number, and for whole numbers `PetCount >= 1` and `PetCount > 0` agree. Without it, `spec.gate.different`, because the normal forms differ. That finding is a false alarm, which is why the report shows both normal forms.

---

## Quiz

???+ question "Question 1 (O1): decide() returns different. What do you know?"
    **A.** The two gates are written differently.

    **B.** At least one respondent sees the item with one gate and not with the other, and `example` holds one.

    **C.** Every respondent is routed differently.

    **D.** The gates use different questions.

    ??? success "Answer"
        **B.** A `different` verdict comes with one respondent the gates
        disagree on. A is true but says less: gates written differently can
        still be equivalent. C and D do not follow.

???+ question "Question 2 (O3): A respondent answers PetAge with “don't know”. Is missing(PetAge) true?"
    **A.** Yes: there is no age.

    **B.** No: the question is answered, without a value, and `missing()` means empty or refused.

    **C.** Only with the `logic` extra.

    **D.** Only if `PetAge` is an integer.

    ??? success "Answer"
        **B.** `missing(x)` is `empty(x) or refused(x)`. An answer without a
        value is neither, and any comparison of it is false.

???+ question "Question 3 (O2): Why does decide() say PetCount > 0 and PetCount >= 1 differ, until you pass types?"
    **A.** Because the solver has a bug with `>=`.

    **B.** Because without types a number may be a fraction, such as 0.25, which the first gate accepts and the second does not.

    **C.** Because `PetCount` might be text.

    **D.** Because one of them reads an empty answer as 0.

    ??? success "Answer"
        **B.** `types={"PetCount": "integer"}`, which `spec_types()` reads
        from `decimals: 0`, rules out fractions, and the two agree.

???+ question "Question 4 (O1): decide() returns unknown. What do you do?"
    **A.** Treat the gates as equivalent.

    **B.** Treat them as different.

    **C.** Read `reason`, and check that pair of gates by hand or rewrite it in a form the solver models.

    **D.** Run it again until it decides.

    ??? success "Answer"
        **C.** `unknown` means the solver could not decide, for the reason
        given. The verdict is the same on every run, so D does not help.

???+ question "Question 5 (O5): Without the logic extra, ddi conform reports spec.gate.different for a gate. What can you conclude?"
    **A.** Some respondent is routed differently.

    **B.** The normal forms differ. The gates may still always agree, so compare the two normal forms in the report, or install the extra and run it again.

    **C.** The instrument is invalid DDI.

    **D.** The spec is wrong.

    ??? success "Answer"
        **B.** Without the extra nothing is calculated: `PetCount >= 1`
        against `PetCount > 0` is reported, though no household is routed
        differently.

---

## Check yourself

- [ ] I can check two gates with `decide()` and read its verdict, its respondent or its reason. (O1)
- [ ] I can read each question's type from the spec and pass it as `types`, and explain why a whole number changes the verdict. (O2)
- [ ] I can test a gate with `evaluate()` on an empty, a refused, a "don't know" and an answered question. (O3)
- [ ] I can review translated gates and name a respondent each wrong one routes differently. (O4)
- [ ] I can say what the `logic` extra changes in `equivalent()` and `ddi conform`. (O5)

---

!!! tip "Instructor notes"
    - Start from Module 16's two gates for Q6 (section 4). Ask the room
      whether they are the same before you run `decide()`. Most say yes.
    - The "answered with no value" row of section 4 surprises everyone. Ask
      for a real question where "don't know" should see the follow-up, and
      one where it should not.
    - Section 6 is a habit worth more than the solver: write the respondents
      and the expected result before checking a gate. Testers do the same.
    - If Z3 cannot be installed on the training machines, section 1 and the
      first example of section 6 still work: `equivalent(exact=False)` and
      `evaluate()` need no solver. Run the rest on the projector.

---

**See also:** [Module 16: Advanced questionnaire specification](module-16-advanced-questionnaire-spec.en.md) | [Check a questionnaire against a spec](../spec-conformance.en.md#decide-whether-two-gates-agree)
