---
description: >-
  Write what a questionnaire should contain as a YAML or JSON spec, then check
  an instrument against it with ddi conform: modules, questions, codes,
  domains, gates and edits.
---

# Check a questionnaire against a spec

A spec says what a questionnaire should contain: its modules, the questions
and statements in each, their response domains and code lists, the gates
that decide who sees what, and the edit checks. `ddi conform` compares an
instrument with it and reports every difference, with a rule id, a severity,
and the module and item it is about.

The spec is a YAML or JSON file you write, or generate from your own design
documents. `ddi-l` reads nothing else: how you get from your organisation's
documents to a spec is yours to decide.

Reading a spec needs the `spec` extra:

```bash
pip install 'ddi-l[spec]'
```

Without it, `ddi spec` and `ddi conform` print that line and exit with 1. The
expression language and its compilers need nothing beyond the standard
library.

## Write a spec

`ddi spec example` writes the example, a spec for the fictional Pet survey;
`ddi spec schema` writes the JSON Schema a spec is checked against, for an
editor that completes and checks YAML.

```bash
ddi spec example > pet-survey.spec.yaml
ddi spec validate pet-survey.spec.yaml
```

The example in full:

```yaml
spec: pet-survey
version: "1"
description: A small bilingual survey about the pets of a household.
languages: [en, fr]

# The words of your Blaise version, for gates that compile to Blaise.
# ddi-l assumes none of them.
blaise:
  empty: EMPTY
  refused: REFUSAL
  today: SYSDATE

code_lists:
  Species:
    values:
      1: {en: Dog, fr: Chien}
      2: {en: Cat, fr: Chat}
      3: {en: Bird, fr: Oiseau}

imported_variables:
  - {name: OwnerName, type: text, source: register}
derived_variables:
  - {name: HasPets, type: numeric, values: [0, 1]}

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

  - id: visits
    required: false
    questions:
      - id: VisitDate
        domain: {date: {type: Date}}

edits:
  - id: age_range
    when: PetAge > 30
    module: pets
    message:
      en: Is the pet really over 30?
      fr: L’animal a-t-il vraiment plus de 30 ans ?
    severity: warning
```

The parts:

| Key | What it holds |
| --- | --- |
| `spec`, `version`, `description` | The spec's name and your own version and notes. |
| `instrument` | The instrument to check when the file has several: its name, label, user ID or ID. |
| `languages` | The languages every question text and code label must be in (`en` matches `en-CA`). A label written without a language is in the first of them. |
| `blaise` | The Blaise words for empty, refused, today and dates, for gates that are Blaise code. |
| `match` | Where to find each id in the instrument (below). |
| `severities` | A severity for a rule, replacing its default: `{spec.module.extra: error}`. |
| `code_lists` | Code lists that a question names with `list:`. |
| `imported_variables`, `derived_variables` | Variables a data lookup supplies, and variables the instrument computes. |
| `modules` | Each module: its `id`, whether it is `required` (default `true`), its `gate` and `gate_scope` (`module`, the default, or `page`), its `statements` and its `questions`. |
| `edits` | Each edit check: its `id`, the condition it fires on (`when`), its `module`, `message` and `severity`. |

A question has an `id`, a `domain` and a `gate` of its own, which applies on
top of its module's. A domain is one of:

| Domain | Options |
| --- | --- |
| `code` | `values` (each value and its label), or `list` (a `code_lists` entry). |
| `numeric` | `min`, `max`, `min_inclusive` and `max_inclusive` (default `true`), `decimals`. |
| `text` | `min_length`, `max_length`. |
| `date` | `type`: the DDI `DateTypeCode` (`Date`, `DateTime`, `Year`...). |

`ddi spec validate` checks a spec against the schema, then against itself:
ids appear once, every `list:` names a code list, every gate and edit parses
and names only the spec's questions and variables, `min` is below `max`,
labels are in the spec's languages, and `severities` names real rules. Each
problem says where it is:

```text
pet-survey.spec.yaml: modules[1].questions[2].gate: 'PetAgee' is not a question or variable of the spec
```

YAML is read strictly, as YAML 1.2. A key given twice is an error, and so is
a merge key (`<<`); `01` stays the string `"01"`, a code, not the number 1;
only `true` and `false` are booleans, so `no` and `off` stay strings; dates
and `=` stay strings; and a whole number written `4e1` is `40`. A spec must
be UTF-8, JSON's `NaN` and `Infinity` are refused, and a gate may nest
parentheses, `not` and minus 50 deep at most.

## Gates and edits: the expression language

A gate or an edit condition is an expression:

```text
PetCount > 0 and answered(PetKind)
not refused(OwnerAge) or OwnerAge >= 18
VisitDate <= today()
```

From the loosest binding to the tightest:

| Operators | Meaning |
| --- | --- |
| `or`, `\|\|` | either side |
| `and`, `&&` | both sides |
| `not` | negation |
| `=` `==` `!=` `<` `<=` `>` `>=` | one comparison; they do not chain: write `1 < x and x < 3`, not `1 < x < 3` |
| `+` `-` | addition, subtraction |
| `*` `/` | multiplication, division |
| `-` | negation of a number |

Operands are numbers (`3`, `2.5`), strings (`"text"` or `'text'`, a quote
doubled inside), ISO dates (`2024-05-31`: write spaces around a minus to
subtract), the ids of questions and variables, parentheses, and five
functions:

| Function | True when |
| --- | --- |
| `answered(x)` | `x` has an answer: neither empty nor refused |
| `missing(x)` | `x` has no answer: empty or refused |
| `empty(x)` | `x` was not answered |
| `refused(x)` | `x` was refused |
| `today()` | (a value) the date of the interview |

Keywords and function names are case-insensitive; ids are not. A number is
compared as a number, so `01` is `1`: write a code whose leading zero matters
as a string, `"01"`. `identifiers()` lists the ids an expression uses, in
order of first use, and `walk()` yields each of its nodes.

Two gates are compared after normalising them: `missing(x)` becomes `empty(x)
or refused(x)` and `answered(x)` its negation, a value compared with a
question goes on the right, `not` moves inward over `and` and `or`, and the
parts of an `and` or an `or` are sorted. In an `and`, an answer test beside a
comparison of the same question goes, since a comparison is false without an
answer: `answered(x) and x > 3` is `x > 3`. In a gate stored as Colectica's
`Neutral` form, which stores `"2"` and `2` alike, a quoted plain number
compares as that number (`x = "2"` matches `x = 2`); `"02"`, `"+2"` or `" 2"`
stay text, and in Blaise code a quoted number is always text.

```python
from ddi_l.spec import equivalent, format_expression, normalise, parse_expression

gate = parse_expression("not (answered(PetKind) and 3 < PetCount)")
print(format_expression(normalise(gate)))
print(equivalent("answered(x)", "not missing(x)"))
print(equivalent("x > 3", "x >= 4"))
```

The last line prints `False`. Normalising calculates nothing, so `x > 3` and
`x >= 4` have different normal forms. Without the `logic` extra that is all
`equivalent()` knows, so a gate reported as different may still be right; the
report shows both normal forms so you can tell. With the extra, `equivalent()`
decides the rest: these two still differ, for an `x` between 3 and 4, and
agree when `x` is a whole number. Nor is `not (x > 3)` the same as `x <= 3`: an unanswered `x`
makes the first true and the second false.

### Decide whether two gates agree

With the `logic` extra (`pip install 'ddi-l[logic]'`, which adds the Z3
solver), `decide()` tells whether two gates hold for the same respondents.
When they do not, it gives a respondent they disagree on:

```python
from ddi_l.spec import decide

verdict = decide("answered(x)", "x > 3 or x <= 3")
print(verdict.outcome)  # -> different
print(verdict.example.describe())  # -> x is answered with no value
print(decide("x > 3", "x >= 4", types={"x": "integer"}).outcome)  # -> equivalent
print(decide('Owner = "Ana"', 'Owner < "B"').reason)  # -> compares text by order
```

A respondent leaves each question empty, refuses it or answers it, and an
answer may have no value to compare, such as a don't-know. A comparison holds
only when every question it reads has a value and nothing in it divides by
zero. How each name is read:

- a question compared only with `=` and `!=` may take several answers: `x = 1`
  holds when 1 is among them, `x != 1` when it has answers and 1 is not one;
- a question that is ordered (`<`...), calculated, or compared with a date or
  `today()` takes one value;
- numbers may be fractions unless `types` says `integer`, and dates are whole
  days. `types` gives each name one of `numeric`, `integer`, `date`, `text`
  or `code`.

The verdict is `equivalent`, `different` with its `example`, or `unknown` with
a `reason`: text compared by order, a condition compared as a value, a name
compared with numbers and with text, or two names compared when either may
take several answers. Two gates that differ only for a question answered with
several codes are `unknown` too, since that depends on the question.
`evaluate()` tells whether an expression holds for one respondent, and every
`different` verdict is checked with it. A work limit, not a clock, bounds the
solver, so a verdict is the same on every run.

## Write a gate for Colectica

`compile_condition()` turns a gate into what Colectica stores in an
`r:Command`. Its condition editor's JSON (`Neutral`) holds what Colectica's
operator codes (listed in
[Work with Colectica exports](colectica.en.md#the-codes-are-colecticas)) can
say:

| Expression | Statement |
| --- | --- |
| `x = 3`, `x != 3` (`x` has no codes) | `Equal`, `NotEqual` 3 |
| `x > 3`, `x >= 3`, `x < 3`, `x <= 3` | `GreaterThan`, `GreaterThanOrEqual`, `LessThan`, `LessThanOrEqual` 3 |
| `empty(x)`, `not empty(x)` | `Empty`, `NotEmpty` |
| `refused(x)`, `not refused(x)` | `Refused`, `NotRefused` |
| `x = 2`, `x = 2 or x = 3` (`x` is coded) | `ContainsAny` those codes |
| `x = 2 and x = 3` (`x` is coded) | `ContainsAll` those codes |
| `x != 2`, `x != 2 and x != 3` (`x` is coded) | `ContainsNone` those codes |

So `answered(x)`, which is `not empty(x) and not refused(x)`, is two
statements, and `missing(x)` is `Empty` or `Refused`. Statements are joined in
one group by `and` or `or`, or in groups joined by one `and` or `or` (`(a or
b) and c`). A choice among one coded question's codes is one statement
wherever it sits, so `a and (x = 2 or x = 3) or b` fits too.

`ddi-l` reads every comparison statement as the expression language reads a
comparison: false when the question has no answer. Whether Colectica does is
not known. It matters most for `NotEqual` and `ContainsNone`, which a reader
could also take to hold when nothing was answered; check such a gate in a
preview.

```python
from ddi_l.colectica_logic import serialize_condition
from ddi_l.spec import BlaiseDialect, compile_condition

subjects = {
    "PetCount": "urn:ddi:example.org:in-count:1",
    "PetKind": "urn:ddi:example.org:in-kind:1",
}
codes = {"PetKind": {"2": "urn:ddi:example.org:code-cat:1"}}
compiled = compile_condition(
    "PetCount > 0 and PetKind = 2", subjects=subjects, codes=codes
)
print(compiled.condition.language, compiled.inputs)
print(serialize_condition(compiled.condition))
```

`subjects` gives the `r:InParameter` of the item that each id is bound to,
and `codes` gives the `l:Code` of each coded value.

Anything else is written as Blaise code, and `fallback_reason` says why:
- a `not` in front of a comparison: `not (x = 3)` holds when `x` has no
  answer, and whether `NotEqual` does is not known;
- arithmetic, dates or `today()`;
- one question compared with another, or text compared with `<`, `<=`, `>`
  or `>=`;
- `and` and `or` mixed inside a group (other than a choice among one coded
  question's codes), since in what order Colectica evaluates them is not
  documented.

Blaise names inputs as `{{name}}` and puts every comparison in parentheses.
The words it uses for empty, refused, today and dates come from a
`BlaiseDialect`, which has no defaults. Without the word it needs, nothing is
compiled, and the reason names the setting. A date template must read back
without doubt: `{year}`, `{month}` and `{day}` each once, text before the
first field that does not end with a digit, something other than digits
between fields, no digit right after a field, and format specs only of the
form `0Nd` (`{month:02d}`; a width pads, so a wider value still reads back),
so `TODATE({year}, {month}, {day})` is fine and `{year}{month:02d}{day:02d}`
is refused:

```python
dialect = BlaiseDialect(empty="EMPTY", refused="REFUSAL")
gate = "answered(PetKind) and not (PetCount = 0)"
compiled = compile_condition(gate, subjects=subjects, dialect=dialect)
print(compiled.condition.text)
print(compiled.fallback_reason)

unset = compile_condition(gate, subjects=subjects)
print(unset.condition, unset.missing_settings)
```

`parse_blaise()` and `condition_to_expression()` read the two forms back into
expressions; `ddi conform` uses them to compare an instrument's gates with
the spec's. `compile_condition()` uses them too: it reads back what it compiled
and compares that with the gate, by normal form and then with the `logic`
extra when it is installed. `compiled.verified` is `True` when they agree,
`False` when they do not, and `None` when it could not tell;
`compile_condition(..., validate=True)` raises instead of returning a
condition that differs, and names a respondent it differs on.

```python
print(compiled.verified)  # -> True
```

## Check an instrument

```bash
ddi conform instrument.xml --spec pet-survey.spec.yaml --format table
```

```text
pet-survey: Instrument 55555555 (Pet survey instrument)
module     severity  rule                             item       message
---------  --------  -------------------------------  ---------  --------------------------------------------------------------------------------------------------
household  info      spec.item.id-sources-differ      PetCount   The question PetCount is found by its construct_alias; its item_name is 'HouseholdPets'.
pets       error     spec.code.missing                PetKind    The question PetKind does not offer the code(s) 3.
pets       error     spec.code.extra                  PetKind    The question PetKind offers the code(s) 4, which the spec does not list.
pets       warning   spec.code.label                  PetKind    Code 2 of PetKind is labelled 'Chats' in fr; the spec says 'Chat'.
pets       error     spec.domain.length               PetName    The maximum length of PetName is 40; the spec says 50.
pets       warning   spec.language.missing            PetAge     The question text of PetAge has no fr.
pets       error     spec.domain.range                PetAge     The range of PetAge is [0, 30]; the spec says [0, 40].
pets       warning   spec.domain.decimals             PetAge     PetAge allows 1 decimal(s); the spec says 0.
pets       warning   spec.gate.extra                  PetAge     Question PetAge is gated by PetCount > 1; the spec gates it with nothing.
pets       warning   spec.item.extra                  PetColour  Module pets has the question QuestionConstruct 55555555 (PetColour), which the spec does not list.
visits     warning   spec.item.misplaced              VisitDate  The question VisitDate belongs in module visits, but is in module pets.
-          warning   spec.module.extra                feedback   The instrument has the module Sequence 55555555 (feedback), which the spec does not list.
-          error     spec.variable.derived-is-lookup  HasPets    The derived variable HasPets is a data lookup field: it is imported, not computed.
pets       info      spec.edit.unverifiable           age_range  The edit age_range: not verifiable (edit storage unknown).
5 error(s), 7 warning(s), 2 info.
```

| Option | Effect |
| --- | --- |
| `--spec SPEC` | The spec (required). |
| `--module ID` | Compare one module only; modules the spec does not list and variables are then not checked, and an item the module holds that the spec lists in another module is reported as extra. |
| `--instrument NAME` | The instrument to compare when the file has several. |
| `--edits off\|info\|strict` | How to check edits (below). Default: `info`. |
| `--format json\|table` | JSON (default): the spec, the instrument, a summary, each module's result and the findings; or a table. |
| `-o PATH`, `--indent N` | Where to write, and the JSON indentation. |
| `--fail-severity info\|warning\|error` | The least severe finding that fails the run. Default: `error`. |

`ddi conform` exits with:

- **0**: no finding reaches `--fail-severity`;
- **1**: one does, or the `spec` extra is not installed;
- **2**: the comparison cannot run: the spec does not read or pass its
  checks, `--module` names no module of the spec, `--edits strict` and the
  spec has no `match.edits`, or the instrument file does not read.

From Python:

<!-- docs-test: skip -->
```python
import ddi_l as ddi
from ddi_l.spec import conform, load_spec

report = conform(ddi.read_ddi("instrument.xml"), load_spec("pet-survey.spec.yaml"))
print(report.summary)
for finding in report.findings:
    print(
        finding.severity, finding.rule_id, finding.module, finding.item, finding.message
    )
```

### Where ids are found

Each id is looked for in the places `match` lists, in order. The first place
that holds an id anywhere in the instrument is the one used. An id found
there on several constructs is reported as ambiguous, never guessed.

| Key | Default | Places |
| --- | --- | --- |
| `question_id` | `[construct_alias, item_name, item_alias, construct_name]` | the alias of the question construct's `r:OutParameter`, the question item's name, its output alias, the construct's name |
| `statement_id` | `[construct_name, label, user_id]` | the statement's `ConstructName`, `r:Label`, `r:UserID` |
| `module_id` | `[construct_name, label, user_id]` | the same, on a sequence |
| `module_depth` | any depth | the depth of module sequences: the instrument's own sequence is 1, its children 2 |
| `edits` | none | how edit checks are stored, for `--edits strict` |
| `lookup_types` | none | a data lookup field type and the spec type it stands for: `{Text: text, Integer: numeric}` |

A module is a sequence. A sequence typed `ConditionalChildContainer` is the
body of an `IfThenElse` branch, never a module or a page; a page is any other
sequence inside a module. When several places hold different ids for one
question (its construct alias and its item name, say), the question is
found by the first, and `spec.item.id-sources-differ` says what the others
hold.

A module found on several sequences is `spec.module.ambiguous`; none of its
candidates is reported as an extra module, and the items inside them are
neither misplaced nor gate-checked. An item referenced from several places is
compared where the spec puts it: it is misplaced only when none of its places
is in its module, and each other module holding it reports it as
`spec.item.extra`. A referenced domain (a `ManagedNumericRepresentation`,
say) is compared like an inline one; of a `StructuredMixedResponseDomain`,
the one domain of the spec's kind is compared.

### Gates

A module's gate is every condition on the way from the instrument to the
module; a question's own gate is every condition between its module and the
question. The Then branch of an `IfThenElse` adds its condition; an `ElseIf`
branch adds its condition and the negation of those before it; the Else
branch adds the negation of them all. With `gate_scope: page`, the module's
gate is expected on each page instead of on the module. A statement has no
gate of its own in a spec: with `gate_scope: page`, its page gate must be one
of the gates between its module and it (`spec.gate.missing` or
`spec.gate.different` otherwise), and a further gate of its own is not
compared.

When the paths to an item inside its module carry gates that are not
equivalent, its gate is `spec.gate.unverifiable`.

With the `logic` extra, gates and edits are decided as `decide()` does after
their normal forms are compared, so a gate written differently that always
agrees with the spec's is not reported. The spec's response domains and
variable types say what each name is: a numeric domain with no decimals is a
whole number, so `PetCount > 0` and `PetCount >= 1` agree. A gate or an edit
that differs names a respondent the two disagree on, in the message and in the
finding's `example`:

```text
Module pets is gated by PetCount > 0; the spec says PetCount > 1 (they differ when PetCount is 1).
```

`--semantics syntactic` (`conform(semantics="syntactic")`) compares normal
forms only, as without the extra; `--semantics smt` fails without it.

A `Neutral` condition's subjects are followed through their bindings, those
of each item's latest version, to the question they come from. A question
the spec does not list is named by its first id, so a gate bound to the
wrong question reads as that question; one output of a question with several
(a grid's cell) is named by its alias, or, when the spec does not know that
alias, by the spec variable an alias on the way names. A subject bound to no
question is named by the output its bindings end at (a data lookup's field):
an alias never hides which question, output or field a gate is bound to. Blaise code
is read with the spec's `blaise` words, its `{{name}}` inputs named the same
way.

### Edits

Where an instrument stores its edit checks is not known in general, so by
default each edit is reported as **info: not verifiable (edit storage
unknown)**. `--edits off` leaves edits out.

`--edits strict` looks for them, once the spec says how they are stored. An
edit check is a `ComputationItem` marked by a user attribute; its id is in
one of its `construct_name`, `label` or `user_id`:

```yaml
match:
  edits: {attribute: kind, value: EditCheck, id: construct_name}
```

Colectica, for instance, marks its computations with an
`r:UserAttributePair` whose `r:AttributeKey` reads `x:TypeOfComputation`:
set `attribute` and `value` to what your exports hold. An edit with no such
check is `spec.edit.missing`; one whose condition differs from `when` is
`spec.edit.different`.

## Rules

| Rule | Default | Reported when |
| --- | --- | --- |
| `spec.instrument.missing` | error | No instrument in the file matches the spec's `instrument`, or the file has none. |
| `spec.instrument.ambiguous` | error | Several instruments match; name one with `instrument` or `--instrument`. |
| `spec.module.missing` | error | A required module is not in the instrument. |
| `spec.module.ambiguous` | error | Several sequences carry a module's id. |
| `spec.module.extra` | warning | A sequence at the modules' depth that the spec does not list. |
| `spec.item.missing` | error | A question or statement is not found. |
| `spec.item.ambiguous` | error | Several constructs carry a question's or statement's id. |
| `spec.item.extra` | warning | A question or statement in a module that the spec does not list there, or lists in another module. |
| `spec.item.misplaced` | warning | A question or statement found only in other modules than the spec's. |
| `spec.item.id-sources-differ` | info | The id sources of a question disagree (its construct name and its item name, say). |
| `spec.code.missing` | error | A code the spec lists is not offered. |
| `spec.code.extra` | error | A code is offered the spec does not list. |
| `spec.code.label` | warning | A code's category label differs from the spec's, in one language. |
| `spec.language.missing` | warning | A question's or statement's text, or a code's label, lacks one of the spec's languages. |
| `spec.domain.type` | error | The response domain is of another kind (code, numeric, text, date), or a mixed domain holds none of the spec's kind. |
| `spec.domain.length` | error | A text domain's minimum or maximum length differs. |
| `spec.domain.range` | error | A numeric domain's bounds, or whether they are included, differ. |
| `spec.domain.decimals` | warning | A numeric domain's decimals differ. |
| `spec.domain.unverifiable` | info | The question's domain cannot be read (several, a mixed domain with several of the spec's kind, a reference not in the file, a code list that cannot be resolved). |
| `spec.gate.missing` | error | The spec gates a module or question, and nothing gates it. |
| `spec.gate.different` | error | The gate differs from the spec's; both normal forms are shown. |
| `spec.gate.extra` | warning | A module or question is gated, and the spec gates it with nothing. |
| `spec.gate.scope` | error | The gate wraps each page where the spec says the module, or the reverse. |
| `spec.gate.unverifiable` | warning | The stored gate cannot be read back into an expression (an operator code not listed, a don't-know test, and and or mixed, malformed `Neutral` JSON, native code this reader does not know), or paths to the item carry different gates. |
| `spec.edit.unverifiable` | info | Not verifiable (edit storage unknown): reported for each edit unless `--edits strict` or `off`. |
| `spec.edit.missing` | error | With `--edits strict`, no edit check carries the edit's id. |
| `spec.edit.different` | error | With `--edits strict`, the edit check's condition differs from `when`. |
| `spec.variable.import-undeclared` | error | An imported variable is not a field of any data lookup the instrument reaches. |
| `spec.variable.import-type` | warning | An imported variable's lookup field type differs (with `match.lookup_types`). |
| `spec.variable.derived-is-lookup` | error | A derived variable is a data lookup field: it is imported, not computed. |

## Limits

- **Only the operator codes' names are known.** A code not listed, and
  `DontKnow` and `NotDontKnow` (the expression language has no "don't
  know"), are reported as unverifiable.
- **How a statement treats a question with no answer is not known.**
  `ddi-l` reads every comparison as false without an answer, as the
  expression language does.
- **The order of `and` and `or` inside a group is not known.** Gates
  that mix them in one group are reported as unverifiable, and none is
  compiled that way.
- **Without the `logic` extra, nothing is calculated.** Normalising does
  not prove arithmetic equivalence: `x > 3` and `x >= 4` are reported as
  different even for a whole-number question. With it, what `decide()`
  cannot model, such as text compared by order, is still compared by normal
  form.
- **A question compared only with `=` and `!=` may take several answers**,
  unless its domain says otherwise. Two gates that differ only for several
  answers (`x = 1 and x = 2` and `x = 1 and x = 3`) are reported as
  different, without a respondent.
- **Where edits are stored is not known in general**, hence `--edits info`
  by default.
- **A comparison under `not` is kept as written**, since it differs from its
  opposite when the question has no answer.
