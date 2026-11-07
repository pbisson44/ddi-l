---
description: >-
  Read, edit and write Colectica Designer FragmentInstance exports with
  ddi-l: every item type as a typed model, and files written back byte for
  byte in Colectica's own layout.
---

# Work with Colectica exports

!!! note "Not affiliated with Colectica"
    `ddi-l` is an independent project. It names Colectica to say which files
    it reads and writes; the Colectica-specific formats described here are
    inferred, not taken from a Colectica specification.

Colectica Designer and Colectica Repository exchange DDI 3.3 as a
`FragmentInstance`: one item per `<Fragment>`, references between items by
Agency, ID and Version, and a `TopLevelReference` naming the item the export
was made for. `ddi-l` reads these files, gives you each item as a typed model,
and writes them back the way Colectica does, so a file you open and save
without editing comes back byte for byte.

## Open an export

`ddi.open_fragment()` opens a `FragmentInstance`. (`ddi.open_ddi()` is for a
`DDIInstance` document and points you here when given a fragment.) So that this
page runs on its own, the first block builds a small export and saves it;
with a real one, start at `open_fragment`.

```python
import ddi_l as ddi

age = ddi.Variable(
    agency="example.org",
    identifier="5f0e3c1a-0b8e-4d3e-9a5e-6a1b2c3d4e5f",
    version="1",
    labels=[
        ddi.InternationalString("Age", lang="en"),
        ddi.InternationalString("Âge", lang="fr"),
    ],
)
ddi.DDIFragment.from_items([age]).save("export.xml")

fragment = ddi.open_fragment("export.xml")
for item in fragment.items():
    print(type(item).__name__, item.identifier, item.version)
```

`items()` parses every item into its model; pass a model class to keep one
type, as in `fragment.items(ddi.Variable)`. Every item type a DDI 3.3 fragment
can carry has a model (161 of them), including the schemes, groups, managed
representations, geographic types and record layouts that have no
hand-written class: those come from `ddi_l.models.items`.

## Look up, edit and put back

`get()` finds an item by ID. A Colectica export can hold several versions of
one item; without a `version=` you get the highest. The models are copies, so
write an edited item back with `put()`:

```python
variable = fragment.get("5f0e3c1a-0b8e-4d3e-9a5e-6a1b2c3d4e5f")
variable.labels.append(ddi.InternationalString("Age (years)", lang="en-CA"))
variable.increment_major_version()
fragment.put(variable)
fragment.save("export.xml")
```

`put()` replaces the item with the same Agency, ID and Version; failing that,
the single item with the same Agency and ID (the version you just bumped);
and otherwise adds the item in a new `<Fragment>`. `remove()` deletes items,
and `top_level_item()` returns the item the `TopLevelReference` names.

Everything you did not touch is written back exactly as read. That includes
`versionDate`, `r:VersionResponsibility`, `r:BasedOnObject` lineage, user
attribute pairs (on items and inside references), multilingual names and
labels kept in one element, `audienceLanguage` on question text,
controlled-vocabulary attributes, the original spelling of values (`"1"` for
true, `"01"`), and references that carry no `r:URN`.

## Versions

Colectica numbers versions with whole numbers (`1`, `2`, ... `78`) and stamps
each version with a `versionDate`. `ddi-l` keeps both conventions when you
bump an item:

- `increment_major_version()` turns `"2"` into `"3"`. On an item that has a
  `versionDate`, it also sets it to now, in Colectica's format
  (`2026-07-16T15:15:11.7905158Z`). An item without one is left without;
  pass `touch=False` to keep the old date.
- `increment_minor_version()` and `increment_subversion()` refuse a
  whole-number version, because Colectica numbers versions with whole
  numbers and a dotted one such as `"3.1"` may not read back. Pass
  `allow_dotted=True` if you do want one. A version that is
  already dotted (`"1.0"`) bumps as before.
- `responsibility="..."` records who made the change as
  `r:VersionResponsibility`. To record the same name on every bump, set it
  once with `ddi.configure(version_responsibility="...")`;
  `responsibility=None` records none on one bump, whatever is configured.
  `ddi-l` never invents one.

```python
variable = fragment.get("5f0e3c1a-0b8e-4d3e-9a5e-6a1b2c3d4e5f")
variable.increment_major_version(responsibility="Questionnaire team")
print(variable.version, variable.version_date, variable.version_responsibility)

try:
    variable.increment_minor_version()
except ddi.DDIModelError as error:
    print(error)

with ddi.configured(version_responsibility="Questionnaire team"):
    variable.increment_major_version()
fragment.put(variable)
```

`ddi.configured(...)` applies a setting inside a `with` block, in the current
thread or task only, and restores the previous one afterwards. `ddi.reset_configuration()` restores the defaults.

## Lint an export

`ddi lint --profile colectica-questionnaire` runs the checks written for
Colectica content:

```bash
ddi lint export.xml --profile colectica-questionnaire
```

- **`colectica.maintainable.labels`** accepts any of `r:Label`, `r:Name` or
  an item's own name element (`ConstructName`, `QuestionItemName`, ...),
  provided it holds text. Colectica items usually carry a name rather than a
  label, so the default profile's `ddi.maintainable.labels` reports nearly
  all of them.
- **References resolve the way Colectica means them.** A reference marked
  `lateBound="true"` means "the latest version". Colectica writes late-bound
  parameter references at version 1 while the parameter itself is at, say, 4,
  so any version present resolves one (`lateBound="1"` counts too). With a
  `lateBoundRestriction` such as `4`, only versions within major version 4
  do. A late-bound reference naming a version newer than any present, or
  whose restriction matches no version present, is reported by
  `ddi.reference.version`.
- **`ddi.reference.version`** (warning) reports an exact reference whose item
  is in the file, but at other versions only, and lists the versions that are
  there.
- **`ddi.reference.provenance-external`** (info) reports a
  `r:BasedOnReference`, or a reference inside an `r:UserAttributePair`, whose
  item is not in the file. These record where an item was copied from, and
  the source usually lives elsewhere.
- **`ddi.reference.integrity`** keeps everything else that does not resolve.
  It is a warning in a fragment, which may be partial, and an error in a
  `DDIInstance`.

`info` findings never fail `ddi lint`. Use `--fail-severity warning` or
`--fail-severity info` for a stricter gate.

The profile also checks a questionnaire's own design for common problems,
each named after the item it is found in (type, short ID and name):

- **Identifiers and bindings:** a parameter or code declared in two items (a
  copy that kept its source's IDs), a binding to a parameter the file does
  not declare.
- **Conditions:** malformed or empty conditions (with the description that
  probably holds the intended logic), groups that can never be true, native
  code that is not one expression, inputs a condition never uses, a stored
  synopsis that names another variable, and a gate that wraps only the first
  construct of a page.
- **Domains:** a code domain without a code list, a domain label naming
  another variable, a question whose wording does not fit its answer type.
- **Text:** missing translations, unresolved template placeholders,
  user-interface words pasted from mock-ups, malformed or undeclared
  `#{name}` pipes, and statements that are design notes.
- **Lookups and aliases:** duplicate or suspicious data lookup fields, and
  parameter aliases whose escaping compounded (`_x005F_`) or that hold
  question text.

Several rules depend on your organisation's conventions: required languages,
the names the run-time system supplies, a variable naming scheme. They do
nothing until configured:

```bash
ddi lint export.xml --profile colectica-questionnaire --format table \
  --required-language en-CA --required-language fr-CA \
  --known-names runtime-names.txt --lint-config lint.json
```

The [lint rule reference](lint-rules.en.md) lists every rule with an example
finding, and every option.

## Conditions

DDI defines where an `IfThenElse` or a `ComputationItem` keeps its logic, an
`r:Command`, but not what goes inside it: `r:ProgramLanguage` names the
language and `r:CommandContent` holds the code as text. Colectica writes three
kinds of content, which `ddi_l.colectica_logic` reads:

| `r:ProgramLanguage` | Content | Parsed into |
| --- | --- | --- |
| `Neutral` | JSON from Colectica's condition editor: groups of statements | `Condition` |
| `Blaise5DataLookup` | JSON listing the fields a data lookup reads | `DataLookup` |
| anything else (`Blaise`, ...) | native code | `NativeCondition` (the text, unchanged) |

A `Neutral` statement compares a **subject**, the URN of one of the item's
`r:InParameter`s, with a value or a set of codes. A parent sequence binds that
parameter to a question's answer.

```python
from ddi_l.colectica_logic import Operator, parse_command, serialize_condition

text = (
    '{"LogicGroups":[{"GroupBooleanType":0,"Statements":[{"StatementBooleanType":0,'
    '"Subject":"urn:ddi:example.org:q1-in:1","Operator":3,"Value":{"Value":"2",'
    '"ValueNotNeeded":false,"SelectedCodes":[]}}]}],"Synopsis":"Q1 Greater than 2",'
    '"Version":1}'
)
condition = parse_command("Neutral", text)
statement = condition.logic_groups[0].statements[0]
print(statement.operator is Operator.GREATER_THAN, statement.value)
assert serialize_condition(condition) == text  # unchanged: written back as read

statement.value = "3"
print(serialize_condition(condition))
```

`parse_condition(item)` does the same from an `IfThenElse` or
`ComputationItem` (an element or a typed model), and `write_condition(item,
condition)` writes an edited condition back into it. An unchanged condition is
written back byte for byte. An edited one is written the way Colectica writes
JSON: no spaces, keys in the order read, and non-ASCII characters escaped only
if the source escaped them.

Loops keep their condition the same way: a `Loop` in `d:LoopWhile`, a
`RepeatUntil` in `d:UntilCondition` and a `RepeatWhile` in `d:WhileCondition`,
which `parse_condition()` and `write_condition()` read and write. A `Loop`'s
`d:InitialValue` and `d:StepValue` hold assignments rather than a condition;
`which="InitialValue"` or `which="StepValue"` reaches them. Each `d:ElseIf` of
an `IfThenElse` has a condition of its own: pass the `ElseIf` element. The
lint rules check every branch, and an input that only an `ElseIf` tests counts
as used, there and in `ddi explain-condition`.

### The codes are Colectica's

The integers in the JSON are Colectica's codes: `Operator` for a statement's
operator, `GroupBool` and `StmtBool` for how groups and statements join. A
value not listed is kept unchanged, so a condition using it still parses and
writes back as read (`Operator(99).name == "UNKNOWN_99"`).

| Enum | Values |
| --- | --- |
| `GroupBool` (how a group joins the groups before it) | `0` None (`FIRST`, the first group), `1` And, `2` Or |
| `StmtBool` (how a statement joins the statements before it) | `0` None (`FIRST`, the first statement), `1` And, `2` Or |
| `Operator` | `0` None, `1` Equal (`EQUAL_TO`), `2` NotEqual, `3` GreaterThan, `4` GreaterThanOrEqual, `5` LessThan, `6` LessThanOrEqual, `7` Empty, `8` NotEmpty, `9` Contains, `10` DoesNotContain, `11` ContainsAny, `12` ContainsAll, `13` ContainsNone, `14` Refused, `15` NotRefused, `16` DontKnow, `17` NotDontKnow |

Only the codes' names are known: not how a statement treats a question with
no answer, nor in what order `And` and `Or` mixed in one group are evaluated;
[Check a questionnaire against a spec](spec-conformance.en.md#write-a-gate-for-colectica)
says how `ddi-l` reads them.

### Check a stored synopsis

Colectica stores a `Synopsis` next to the logic: the text its editor last
showed. It can be stale, and it numbers codes by their position in the list
rather than their value. `render_synopsis(condition, fragment)` writes one from
the logic itself, naming each subject after the question bound to it and each
code by its value and label. From the command line, `ddi explain-condition`
shows both, the condition's description, and which of the item's inputs the
condition uses:

```bash
ddi explain-condition export.xml 22222222-2222-4222-8222-000000000030
```

```text
Item              IfThenElse 22222222-2222-4222-8222-000000000030 (version 1)
Language          Neutral
Stored synopsis   (PetName Contains All 2 Cat) And ((PetCount Greater than 2) Or (PetCount Refused))
Rendered          (PetKind contains all of 3 "Cat") and (PetCount > 2 or PetCount is refused)
Synopsis mismatch the stored synopsis does not name PetKind
Description en-CA Show when a cat lives here and there are more than two pets.
Inputs used       PetKind, PetCount
Inputs unused     PetAge
```

`--format json` prints the same as JSON, and `explain_condition(fragment, id)`
returns it as a `ConditionExplanation`.

## Repair a template

Colectica references an item at a fixed version. Change a sequence, give it a
new version, and every item pointing at the old version is out of date: its
reference needs the new version, which changes that item in turn, up to the
instrument. `DDIFragment` does that walk, and edits a fragment's sequences
without leaving its references behind.

- **`revise(*items, cascade=True, dry_run=False, responsibility=None,
  version_date=None, rationale=None)`** gives each item the next major version, and gives it
  to every identifiable the item declares too (its parameters, its codes), as
  Colectica numbers them. Every item revised in one call gets the same
  `versionDate` (`version_date`, or now), as when Colectica saves several
  items at once, and `responsibility` (or the one set with
  `ddi.configure()`). With `cascade`, every item referring to an old version,
  of an item or of what it declares, is re-pointed and revised too, each
  once, up to the top; the `TopLevelReference` follows. Late-bound references
  already mean "the latest version" and are left alone. `rationale` (a
  string, or `{language: text}`) is recorded as the `r:VersionRationale` of
  every item revised, as Colectica records the message of a save on every
  item it saves; the rationale an item carried is dropped either way, since
  it explained the previous version. `dry_run=True` returns the plan and
  changes nothing.
- **`move_construct(construct, from_sequence, to_sequence, index=None)`**
  moves a construct between sequences.
- **`insert_construct(sequence, construct, index=None, before=None,
  after=None)`** places a construct in a sequence: one already in the
  fragment, or a new typed item, which is added with what Colectica writes on
  every item: the configured responsibility among it, and an `r:URN` and the
  item's version on each identifiable it declares.
- **`wrap_in_condition(sequence, constructs, condition)`** puts constructs
  under a new `IfThenElse`, in a Then sequence of type
  `ConditionalChildContainer`. The two new items share one `versionDate` and
  record the configured responsibility.
- **`duplicate(item)`** copies an item with new IDs for it and everything it
  declares, and records the source in `r:BasedOnObject`. The copy and what it
  declares start at version 1. A copy made this way shares no parameter ID
  with its source; place it with `insert_construct()`.
- **`repair_shared_identifiables(dry_run=True)`** gives each copy of a shared
  identifiable (what `colectica.identifiable.shared-id` reports) an ID of its
  own, keeping the original's: the earliest `versionDate`, else the item with
  no `r:BasedOnObject`. The bindings in the copy's own question constructs
  follow; any other reference to the shared ID is listed as ambiguous rather
  than guessed.

The editing helpers change no version: they return the items they touched,
for `revise()`. A page whose gate wraps only its first statement, fixed:

<!-- docs-test: skip -- fragment: the IDs are those of the reader's own template -->
```python
fragment = ddi.open_fragment("template.xml")

touched = set()
for statement in statements_after_the_gate:
    result = fragment.move_construct(statement, entry_page, gate_then_sequence)
    touched.update(result.touched)

plan = fragment.revise(*touched, dry_run=True)
for step in plan:
    print(step.item_type, step.identifier, step.old_version, "->", step.new_version)

fragment.revise(*touched, responsibility="Questionnaire team")
fragment.save("template.xml")
```

Only the items on the path from the change to the instrument get a new
version: the two sequences touched, the `IfThenElse` pinning the Then
sequence, and the section, root and instrument above them.

A new statement after a page's last question, the same way:

<!-- docs-test: skip -- fragment: the IDs are those of the reader's own template -->
```python
from ddi_l.models import InternationalString, StatementItem

thanks = StatementItem(
    agency="example.org",
    identifier=new_statement_id,
    version="1",
    construct_names=[InternationalString("Thanks", lang="en")],
)
result = fragment.insert_construct(page, thanks, after=last_question)
fragment.revise(*result.touched)
```

!!! warning "Re-import not verified"
    Whether Colectica accepts items whose identifiables were given new IDs by
    `repair_shared_identifiables()` on re-import has not been verified. Try it
    on a copy of the repository first.

## Build a fragment from scratch

`DDIFragment.from_items()` writes one item per `<Fragment>`, names the first
in the `TopLevelReference`, and gives each item what Colectica writes on every
item: `isUniversallyUnique="true"`, a `versionDate` (now, in Colectica's
seven-digit UTC format, unless you pass one) and an `r:URN`. References are
identified by Agency, ID and Version alone, as Colectica writes them.

```python
question = ddi.QuestionItem(
    agency="example.org",
    identifier="c2b1a9e4-7d3f-4b8a-9e21-0f6d5c4b3a29",
    version="1",
    question_texts=[ddi.InternationalString("What is your age?", lang="en")],
)
package = ddi.DDIFragment.from_items([question, age])
print(package.validate())
package.save("package.xml")
```

To build many items at once from metadata kept in spreadsheets (a study, its
questionnaire, variables, data files and more), see
[Load DDI from spreadsheets](spreadsheet-import.en.md):
`load_tables(...).to_fragment()` gives the same kind of fragment.

## Layout

A file you read is written back with its unchanged parts as they were read,
byte for byte, whatever tool wrote it: `save()`, `to_xml()`,
`ddi.write_ddi()`, `ddi roundtrip` and the HTTP API. Only what you add or
change is laid out, in Colectica's layout for a `FragmentInstance`. Any
other `FragmentInstance` (built in code, or by `ddi from-json`) is written all
in Colectica's layout. That is UTF-8, the `ddi:` prefix on the root and
`TopLevelReference`, each `<Fragment>` at the left margin declaring the
reusable namespace as `r:`, each item declaring its module's namespace as the
default, attributes in schema order, two-space indentation.
`layout="colectica"` (`--layout colectica`, `?layout=colectica`) writes the
whole file in Colectica's layout, and `layout="default"` in this library's
usual pretty-printed layout, as do `pretty_print=False`,
`xml_declaration=False` or an encoding other than UTF-8, which only that
layout has. A `DDIInstance` read from a file keeps its own layout the same
way, when it uses the canonical prefixes (`r`, `s`, `d`...); one built in code
is written in this library's layout.

From the command line:

```bash
ddi validate export.xml
ddi lint export.xml
ddi roundtrip export.xml -o copy.xml
```

`ddi roundtrip` on an unedited export writes an identical file.

Inline XHTML keeps its spaces. In
`<r:Content><b>Kind</b> <i>of pet</i></r:Content>` the space between the two
elements is text: the label reads "Kind of pet" on both backends, and the
file is written back as read. Whitespace between XHTML blocks (`<p>`,
`<ul>`...) is layout. lxml drops blank text as it reads, so a file where
inline XHTML has no text before it in its element is parsed a second time,
keeping every blank and then removing the indentation: reading such a file
takes up to twice as long, and other files are read as before.

### Byte-order mark

Most Colectica exports start with a UTF-8 byte-order mark; some exports from
Colectica's server-side tools have none. `ddi-l` records which one it read
(`fragment.source_bom`) and writes the same, so both kinds round-trip byte
for byte. Pass `bom=True` or `bom=False` to `save()`, `to_colectica_bytes()`
or `ddi.write_ddi()` to choose. A fragment built in
code gets a mark.
