---
description: >-
  Read, edit and write Colectica Designer FragmentInstance exports with
  ddi-l: every item type as a typed model, and files written back byte for
  byte in Colectica's own layout.
---

# Work with Colectica exports

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
[Load DDI from spreadsheets](spreadsheet-import.md):
`load_tables(...).to_fragment()` gives the same kind of fragment.

## Layout

`save()` writes Colectica's layout by default: UTF-8 with a byte-order mark,
the `ddi:` prefix on the root and `TopLevelReference`, each `<Fragment>` at
the left margin declaring the reusable namespace as `r:`, each item declaring
its module's namespace as the default, attributes in schema order, two-space
indentation. `save(path, layout="default")` writes this library's usual
pretty-printed layout instead.

From the command line:

```bash
ddi validate export.xml
ddi lint export.xml
ddi roundtrip export.xml --layout colectica -o copy.xml
```

`ddi roundtrip --layout colectica` on an unedited export writes an identical
file.
