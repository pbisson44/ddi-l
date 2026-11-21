---
description: >-
  Optional Module 20 of the ddi-l course: convert the DDI-Codebook files of
  several waves into DDI-Lifecycle, writing once each question, code list and
  universe the codebooks repeat, and carry over what makes the result FAIR.
---

# Module 20 (optional): From DDI-Codebook to DDI-Lifecycle, built for reuse

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Explain why a DDI-Codebook file cannot share a question, a code
      list or a universe with another study, and how DDI-Lifecycle lets every
      wave of a survey refer to the same item.
    - **O2.** Read DDI-Codebook files, version 2.5 or 2.6, with Python's
      `xml.etree.ElementTree`: each study's citation and data files, and each
      variable's name, label, question and categories.
    - **O3.** Find what the codebooks repeat (the same question, the same
      categories, the same universe) and decide when a repeat is the same item
      and when a change of wording makes it another one.
    - **O4.** Write the metadata tables so that each repeated item appears once,
      referred to by every variable that uses it, and load several waves as one
      series into a schema-valid DDI-Lifecycle file.
    - **O5.** Carry over what makes the result findable and reusable: each
      wave's DOI, a licence a program can read, a record of the conversion and
      a label on every item.

**Prerequisites:** [Module 9](module-09-code-lists.en.md) and
[Module 15](module-15-update-and-version.en.md).
[Module 1](module-01-what-is-metadata.en.md#4-how-ddi-makes-data-fair) covers
the FAIR principles this module puts into practice. This module is optional:
the capstone does not need it.

**Time:** 60 min self-paced / 75 min instructor-led.

**New in this module:** DDI-Codebook files (`stdyDscr`, `fileDscr`,
`dataDscr`, `var`, `catgry`), `xml.etree.ElementTree`, `load_tables()`,
`to_fragment()`, the `groups` and `datasets` tables, the `studies` table's
`identifier`, `copyright` and `license` columns, and `run_lint()`.

---

## 1. One codebook per study, nothing shared

Many data archives describe their holdings in **DDI-Codebook** (DDI-C), the
DDI Alliance's first standard; this course teaches **DDI-Lifecycle** (DDI-L).
The difference that matters here is what each lets you share:

| | DDI-Codebook | DDI-Lifecycle |
| --- | --- | --- |
| One file holds | One study, complete in itself | Any items, from one study or many |
| A question, a code list | Written inside each variable that uses it | An item of its own, which variables refer to |
| Identifiers | Local to the file, such as `ID="V1"` | A URN, `urn:ddi:agency:id:version`, that any file can refer to |
| A survey run every year | One codebook per year, each repeating the same questions and categories | One question and one code list, referred to by every year's variables |

A codebook cannot point outside itself, so each wave's codebook copies
everything again. Nothing in the files says that `PetKind` asks the same
question in 2022 and in 2023: a person has to compare them. If a category's
label is corrected, it has to be corrected in every codebook.

Converting to DDI-Lifecycle one codebook at a time would keep those copies,
each with an identifier of its own. This module converts with reuse in mind:
it reads every wave first, finds what they repeat, and writes each repeated
item once.

`ddi-l` reads and writes DDI-Lifecycle only. You read the codebooks with
Python's standard library, and hand their content to `ddi-l` through the
[metadata tables](../spreadsheet-import.en.md).

## 2. Two waves, two codebooks

A made-up survey ran in 2022 and in 2023, and its archive wrote one codebook
per wave, in the same layout each year. The function below writes them, so
that you can see what changes from one year to the next. Both files are
valid against the DDI Alliance's DDI-Codebook 2.5 schema.

```python
from pathlib import Path

VARIABLES = {
    "PetCount": """
    <var ID="V1" name="PetCount" files="F1" dcml="0">
      <labl>Number of pets</labl>
      <qstn>
        <qstnLit>{count_question}</qstnLit>
      </qstn>
      <varFormat type="numeric"/>
    </var>""",
    "PetKind": """
    <var ID="V2" name="PetKind" files="F1">
      <labl>Kind of pet</labl>
      <qstn>
        <qstnLit>What kind of pet do you have?</qstnLit>
      </qstn>{kinds}
      <varFormat type="numeric"/>
    </var>""",
    "SecondPetKind": """
    <var ID="V3" name="SecondPetKind" files="F1">
      <labl>Kind of second pet</labl>
      <qstn>
        <qstnLit>What kind is your second pet?</qstnLit>
      </qstn>{kinds}
      <varFormat type="numeric"/>
    </var>""",
}
KINDS = "".join(
    f"""
      <catgry{' missing="Y"' if value == "9" else ""}>
        <catValu>{value}</catValu>
        <labl>{label}</labl>
      </catgry>"""
    for value, label in [
        ("1", "Dog"),
        ("2", "Cat"),
        ("3", "Other pet"),
        ("9", "Don't know"),
    ]
)


def write_codebook(year, doi, count_question, names):
    """One wave's codebook: the same layout every year, as an archive writes it."""
    variables = "".join(
        VARIABLES[name].format(count_question=count_question, kinds=KINDS)
        for name in names
    )
    Path(f"pets-{year}.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<codeBook xmlns="ddi:codebook:2_5" version="2.5">
  <stdyDscr>
    <citation>
      <titlStmt>
        <titl>Pet Ownership Survey {year}</titl>
        <IDNo agency="DOI">{doi}</IDNo>
      </titlStmt>
      <rspStmt>
        <AuthEnty>Example Research Institute</AuthEnty>
      </rspStmt>
      <distStmt>
        <distrbtr>Example Data Archive</distrbtr>
        <distDate date="{year}-09-15">15 September {year}</distDate>
      </distStmt>
    </citation>
    <stdyInfo>
      <sumDscr>
        <anlyUnit>Households</anlyUnit>
        <universe>Households with at least one pet</universe>
        <dataKind>Survey data</dataKind>
      </sumDscr>
    </stdyInfo>
    <dataAccs>
      <useStmt>
        <conditions>Free to reuse with attribution (CC BY 4.0).</conditions>
      </useStmt>
    </dataAccs>
  </stdyDscr>
  <fileDscr ID="F1">
    <fileTxt>
      <fileName>pets-{year}.csv</fileName>
    </fileTxt>
  </fileDscr>
  <dataDscr>{variables}
  </dataDscr>
</codeBook>
""",
        encoding="utf-8",
    )


write_codebook(
    2022,
    "10.5072/FK2PETS22",
    "How many pets live in your home?",
    ["PetCount", "PetKind"],
)
write_codebook(
    2023,
    "10.5072/FK2PETS23",
    "How many pets live in your household?",
    ["PetCount", "PetKind", "SecondPetKind"],
)
```

Open `pets-2022.xml` and `pets-2023.xml` side by side. Between the two
years:

- `PetKind` asks the same question, with the same four categories;
- `PetCount` is worded differently: "home" became "household";
- 2023 adds `SecondPetKind`, a new question with the same categories as
  `PetKind`, copied once more.

The two codebooks hold five questions and three copies of the four
categories. `10.5072` is the DOI prefix set aside for tests, so these DOIs
resolve nowhere; an archive's codebook carries the study's real DOI.

## 3. Read a codebook

Every element of a codebook is in its namespace, `ddi:codebook:2_5` for
version 2.5 and `ddi:codebook:2_6` for 2.6. The function reads it from the
root element, so it reads either version, and returns what the conversion
needs as plain Python values:

```python
import xml.etree.ElementTree as ET


def text(element, path, C):
    """The text at path under element, spaces tidied, or an empty string."""
    found = element.findtext(path, namespaces=C) or ""
    return " ".join(found.split())


def read_codebook(path):
    """What one codebook says: its study, its data files and its variables."""
    root = ET.parse(path).getroot()
    C = {"c": root.tag[1:].split("}")[0]}
    study = root.find("c:stdyDscr", C)
    id_no = study.find("c:citation/c:titlStmt/c:IDNo", C)
    variables = []
    for var in root.iterfind("c:dataDscr/c:var", C):
        categories = tuple(
            (text(c, "c:catValu", C), text(c, "c:labl", C), c.get("missing") == "Y")
            for c in var.iterfind("c:catgry", C)
        )
        variables.append(
            {
                "name": var.get("name"),
                "label": text(var, "c:labl", C),
                "question": text(var, "c:qstn/c:qstnLit", C),
                "file": var.get("files"),
                "format": var.find("c:varFormat", C).get("type"),
                "decimals": var.get("dcml", "0"),
                "categories": categories,
            }
        )
    return {
        "title": text(study, "c:citation/c:titlStmt/c:titl", C),
        "identifier": id_no.text.strip(),
        "identifier_agency": id_no.get("agency"),
        "creator": text(study, "c:citation/c:rspStmt/c:AuthEnty", C),
        "publisher": text(study, "c:citation/c:distStmt/c:distrbtr", C),
        "published": study.find("c:citation/c:distStmt/c:distDate", C).get("date"),
        "analysis_unit": text(study, "c:stdyInfo/c:sumDscr/c:anlyUnit", C),
        "kind_of_data": text(study, "c:stdyInfo/c:sumDscr/c:dataKind", C),
        "universe": text(study, "c:stdyInfo/c:sumDscr/c:universe", C),
        "files": {
            f.get("ID"): text(f, "c:fileTxt/c:fileName", C)
            for f in root.iterfind("c:fileDscr", C)
        },
        "variables": variables,
    }


waves = {year: read_codebook(f"pets-{year}.xml") for year in (2022, 2023)}
for year, wave in waves.items():
    print(year, wave["identifier"], [var["name"] for var in wave["variables"]])
```

**Expected output:**

```text
2022 10.5072/FK2PETS22 ['PetCount', 'PetKind']
2023 10.5072/FK2PETS23 ['PetCount', 'PetKind', 'SecondPetKind']
```

`find()` returns the first matching element, or `None`; `findtext()` its
text; `iterfind()` goes through every match. A variable's categories become
a tuple of `(value, label, missing)`, which Python can compare with another
variable's in one step.

## 4. Find what the codebooks repeat

Group the variables of all waves by what they share: their question, their
categories, and their study's universe. Two variables ask the same question
when both its wording and its answers match:

```python
def question_key(var):
    """A question: its wording, and its categories or else its number format."""
    return var["question"], var["categories"] or (var["format"], var["decimals"])


def repeats(waves):
    """The questions, code lists and universes of all waves, and who uses each."""
    questions = {}  # (wording, answers) -> the variables that ask it
    code_lists = {}  # categories -> the variables that use them
    universes = {}  # wording -> the waves that cover it
    for year, wave in waves.items():
        universes.setdefault(wave["universe"], []).append(year)
        for var in wave["variables"]:
            where = f"{var['name']} {year}"
            questions.setdefault(question_key(var), []).append(where)
            if var["categories"]:
                code_lists.setdefault(var["categories"], []).append(where)
    return questions, code_lists, universes


questions, code_lists, universes = repeats(waves)
print(len(questions), len(code_lists), len(universes))  # -> 4 1 1
for (wording, _), users in questions.items():
    print(users, wording)
print(list(code_lists.values()))
```

**Expected output:**

```text
4 1 1
['PetCount 2022'] How many pets live in your home?
['PetKind 2022', 'PetKind 2023'] What kind of pet do you have?
['PetCount 2023'] How many pets live in your household?
['SecondPetKind 2023'] What kind is your second pet?
[['PetKind 2022', 'PetKind 2023', 'SecondPetKind 2023']]
```

Five questions in the codebooks are four distinct ones; three copies of the
categories are one code list; and both waves cover the same universe.

The answers are part of the question because every variable takes its
answers from its question (section 5). Had the 2023 wave added a category to
*What kind of pet do you have?*, the two waves would ask two questions with
the same wording, each with its own code list; grouped by wording alone,
`PetKind 2023` would have been given the 2022 categories.

Comparing wording is a rule a program can apply, but sameness is a decision.
The two `PetCount` wordings differ by one word, so the converter keeps them
apart. Whether "home" and "household" count the same pets is for the
survey's owner to say. If they do, map one wording to the other before
converting (exercise 4); if the change matters a little, Module 15's
versions are the way to record it.

## 5. Write each item once

Each distinct question, code list and universe gets one row, with an id
(`Q1`, `CL1`, `U1`) that every variable using it names. The rest follows the
waves:

- a **group** of type `Series` holds the studies;
- each wave is a **study**, with its citation;
- each wave's data file is a **dataset** of its study;
- each variable gets one row per wave, and names its dataset, its question
  and its universe.

```python
def response(var, code_list_ids):
    """The questions columns that say what kind of answer a variable records."""
    if var["categories"]:
        return {"response": "code", "code_list": code_list_ids[var["categories"]]}
    if var["format"] == "numeric":
        decimal = var["decimals"] != "0"
        return {
            "response": "numeric",
            "numeric_type": "Decimal" if decimal else "Integer",
        }
    return {"response": "text"}


def build_tables(waves):
    """The metadata tables of all waves, with each repeated item written once."""
    questions, code_lists, universes = repeats(waves)
    question_ids = {key: f"Q{n}" for n, key in enumerate(questions, 1)}
    code_list_ids = {cats: f"CL{n}" for n, cats in enumerate(code_lists, 1)}
    universe_ids = {wording: f"U{n}" for n, wording in enumerate(universes, 1)}
    variables = [
        (year, var) for year, wave in waves.items() for var in wave["variables"]
    ]

    tables = {
        "settings": [{"setting": "agency", "value": "example.org"}],
        "groups": [
            {
                "id": "PETS",
                "title@en": "Pet Ownership Survey",
                "type": "Series",
                "studies": "|".join(f"PETS{year}" for year in waves),
            }
        ],
        "universes": [
            {"id": uid, "label@en": wording} for wording, uid in universe_ids.items()
        ],
        "code_lists": [],
        "codes": [],
        "questions": [],
        "studies": [],
        "datasets": [],
        "variables": [],
    }
    for categories, list_id in code_list_ids.items():
        first = next(var for _, var in variables if var["categories"] == categories)
        tables["code_lists"].append({"id": list_id, "label@en": first["label"]})
        for value, label, missing in categories:
            tables["codes"].append(
                {
                    "code_list": list_id,
                    "value": value,
                    "label@en": label,
                    "missing": "true" if missing else "",
                }
            )
    for key, question_id in question_ids.items():
        first = next(var for _, var in variables if question_key(var) == key)
        tables["questions"].append(
            {"id": question_id, "text@en": key[0], **response(first, code_list_ids)}
        )
    for year, wave in waves.items():
        tables["studies"].append(
            {
                "id": f"PETS{year}",
                "title@en": wave["title"],
                "identifier": wave["identifier"],
                "identifier_agency": wave["identifier_agency"],
                "creator": wave["creator"],
                "publisher": wave["publisher"],
                "publication_date": wave["published"],
                "analysis_unit": wave["analysis_unit"],
                "kind_of_data": wave["kind_of_data"],
                "universe": universe_ids[wave["universe"]],
            }
        )
        for file_id, file_name in wave["files"].items():
            tables["datasets"].append(
                {
                    "id": f"{file_id}_{year}",
                    "name": file_name,
                    "label@en": f"{wave['title']} data",
                    "file": file_name,
                    "study": f"PETS{year}",
                }
            )
    for year, var in variables:
        tables["variables"].append(
            {
                "id": f"{var['name']}_{year}",
                "name": var["name"],
                "label@en": var["label"],
                "question": question_ids[question_key(var)],
                "dataset": f"{var['file']}_{year}",
                "universe": universe_ids[waves[year]["universe"]],
            }
        )
    return tables


tables = build_tables(waves)
print(len(tables["questions"]), len(tables["codes"]), len(tables["variables"]))
# -> 4 4 5
```

A variable takes its question's response, so `PetKind` gets the code list
without naming it twice. A codebook says only `numeric` or `character`;
`dcml="0"`, no decimals, is what makes `PetCount` a whole number. The
codebook's `IDNo` and its `agency` go to the `identifier` and
`identifier_agency` columns, which write the DOI into the study's citation.

## 6. Load and check the reuse

Write each table as a CSV file, load the folder, and write one
DDI-Lifecycle file for both waves:

```python
import csv

from ddi_l.tables import load_tables


def write_tables(folder, tables):
    """One CSV file per table, with every column any of its rows uses."""
    folder = Path(folder)
    folder.mkdir(exist_ok=True)
    for name, rows in tables.items():
        headers = list(dict.fromkeys(key for row in rows for key in row))
        with open(folder / f"{name}.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)


write_tables("pets-tables", tables)
loaded = load_tables("pets-tables")
fragment = loaded.to_fragment()
print(fragment.validate())  # -> []
fragment.save("pets-lifecycle.xml")

asked_2022 = loaded.get("variables", "PetKind_2022").question_references[0]
asked_2023 = loaded.get("variables", "PetKind_2023").question_references[0]
print(asked_2022.urn == asked_2023.urn)  # -> True
print(fragment.get_top_level_reference().type_of_object)  # -> Group
```

`to_fragment()` writes a DDI-Lifecycle `FragmentInstance`, one fragment per
item, with the series as its top-level item. `to_study()`, which writes one
study like the documents of the earlier modules, has no place for a series
or for several studies.

`PetKind` in 2022 and `PetKind` in 2023 now point to the same question by its
URN, and three variables point to the same code list. A third wave would add
its study, its data file and its variables, and refer to the same items
again. Correcting a category's label is now one change, in one place.

## 7. Findable and reusable

[Module 1](module-01-what-is-metadata.en.md#4-how-ddi-makes-data-fair)
showed how DDI supports the FAIR principles. A conversion is the moment to
carry over, or add, what codebooks often hold loosely:

- **A persistent identifier.** Each wave's DOI, from its `IDNo`, is now in
  its study's citation as an `r:InternationalIdentifier`, and every item has
  a URN. The URNs say `example.org`, the made-up agency this course uses; a
  real agency is registered with the DDI Alliance, as
  [Module 3](module-03-first-study.en.md) explains.
- **A licence a program can read.** DDI-Codebook 2.5 has no licence element:
  conditions of use are free text in `useStmt`. Version 2.6 adds a `license`
  element whose `URI` attribute holds the licence's web address. In
  DDI-Lifecycle, the `license` column writes it as `dcterms:license` in the
  study's citation. Give it the address, not the name.
- **A label on every item.** The codebooks labelled their variables but not
  their questions, and a label is what a catalogue or a question bank lists.
  `run_lint()` runs the checks of `ddi lint` on a fragment, and finds them.

The licence and the labels go in the tables, so every later conversion keeps
them:

```python
from ddi_l.lint import run_lint

print(len(run_lint(fragment)))  # -> 4
for row in tables["studies"]:
    row["license"] = "https://creativecommons.org/licenses/by/4.0/"
for question in tables["questions"]:
    asker = next(v for v in tables["variables"] if v["question"] == question["id"])
    question["label@en"] = asker["label@en"]
write_tables("pets-tables", tables)
```

The four findings were `ddi.maintainable.labels`, one per question.

- **A record of the conversion.** Record where the metadata came from as each
  study's version rationale, as in Module 15. The tables give you each item
  before it is written, so you can add it there. Then check the result and
  save it:

```python
from ddi_l.models.base import InternationalString, VersionRationale

loaded = load_tables("pets-tables")
for year in waves:
    loaded.get("studies", f"PETS{year}").version_rationales.append(
        VersionRationale(
            descriptions=[
                InternationalString(
                    text=f"Converted from the DDI-Codebook 2.5 file pets-{year}.xml."
                )
            ]
        )
    )
fragment = loaded.to_fragment()
print(fragment.validate())  # -> []
print(run_lint(fragment))  # -> []
fragment.save("pets-lifecycle.xml")
```

## 8. What this conversion leaves out

- **Reuse beyond questions and code lists.** Both `PetKind` variables could
  also share a represented variable, which says they record the same thing
  in the same way: see the `represented_variables` table of the
  [metadata tables guide](../spreadsheet-import.en.md).
- **Several languages.** A codebook may repeat `titl` or `labl` with
  `xml:lang`; give each language its column, such as `label@fr`.
- **Statistics and methodology.** A variable's `sumStat` (frequencies,
  means) describes the data rather than the study and stays with the
  archive; `method/dataColl` maps onto the `methodologies` table.

Before you convert real codebooks, list the elements they use, and compare
the waves before deciding what is the same: tools and teams write
DDI-Codebook differently.

---

## Exercises

1. **(O1)** A colleague converts each codebook to its own DDI-Lifecycle file,
   one at a time. Both files are valid. What do they lose compared with the
   conversion of this module?

    ??? success "Answer"

        Each file gets its own `PetKind` question and its own code list, with
        different URNs: nothing says that 2022 and 2023 asked the same
        question with the same categories, which is exactly what comparing
        the waves needs. A corrected category label has to be corrected in
        every file again. Converting all waves together, and writing each
        repeated item once, keeps that knowledge in the metadata.

2. **(O2)** Make a DDI-Codebook 2.6 copy of `pets-2023.xml`: change the
   namespace and version, and add a `license` element as the first child of
   `dataAccs`. Read its namespace from the root, and print it with the
   licence's `URI`.

    **Expected output:**

    ```text
    ddi:codebook:2_6 https://creativecommons.org/licenses/by/4.0/
    ```

    ??? success "Answer"

        ```python
        source = Path("pets-2023.xml").read_text(encoding="utf-8")
        source = source.replace(
            'xmlns="ddi:codebook:2_5" version="2.5"',
            'xmlns="ddi:codebook:2_6" version="2.6"',
        )
        source = source.replace(
            "    <dataAccs>\n",
            "    <dataAccs>\n"
            '      <license URI="https://creativecommons.org/licenses/by/4.0/">'
            "CC BY 4.0</license>\n",
        )
        Path("pets-2023-2.6.xml").write_text(source, encoding="utf-8")

        root_26 = ET.parse("pets-2023-2.6.xml").getroot()
        C_26 = {"c": root_26.tag[1:].split("}")[0]}
        licence = root_26.find("c:stdyDscr/c:dataAccs/c:license", C_26)
        print(C_26["c"], licence.get("URI"))
        # -> ddi:codebook:2_6 https://creativecommons.org/licenses/by/4.0/
        ```

        `read_codebook()` reads this file as it is, because it takes the
        namespace from the root. A converter can take the licence from
        `license/@URI` when a codebook has one, and ask a person when it has
        only `useStmt` text.

3. **(O3, O4)** The survey runs again in 2024, with the 2023 questionnaire.
   Write its codebook with `write_codebook()`, add it to `waves`, and print
   the number of distinct questions and code lists, then the number of rows
   of `questions` and `variables` in the rebuilt tables.

    **Expected output:**

    ```text
    4 1
    4 8
    ```

    ??? success "Answer"

        ```python
        write_codebook(
            2024,
            "10.5072/FK2PETS24",
            "How many pets live in your household?",
            ["PetCount", "PetKind", "SecondPetKind"],
        )
        waves[2024] = read_codebook("pets-2024.xml")
        questions, code_lists, universes = repeats(waves)
        print(len(questions), len(code_lists))  # -> 4 1
        tables = build_tables(waves)
        print(len(tables["questions"]), len(tables["variables"]))  # -> 4 8
        ```

        The third wave adds a study, a data file and three variables, and not
        one question or code list: its variables refer to the items the first
        two waves already have.

4. **(O3)** The survey's owner decides that "How many pets live in your
   home?" and "How many pets live in your household?" ask the same thing.
   Map the 2023 wording to the 2022 one in every wave, rebuild and load the
   tables, and check that `PetCount` in 2022 and in 2024 now ask the same
   question.

    **Expected output:**

    ```text
    3
    True
    ```

    ??? success "Answer"

        ```python
        same = {"How many pets live in your household?": "How many pets live in your home?"}
        for wave in waves.values():
            for var in wave["variables"]:
                var["question"] = same.get(var["question"], var["question"])
        tables = build_tables(waves)
        print(len(tables["questions"]))  # -> 3
        write_tables("pets-tables", tables)
        loaded = load_tables("pets-tables")
        first = loaded.get("variables", "PetCount_2022").question_references[0]
        last = loaded.get("variables", "PetCount_2024").question_references[0]
        print(first.urn == last.urn)  # -> True
        ```

        The decision is recorded in one place, the `same` mapping, which the
        owner can review. The question keeps the 2022 wording; if the 2023
        wording should be kept as well, a new version of the question
        (Module 15) records the change instead.

5. **(O5)** Give every variable and question a French label (`label@fr`),
   using *Nombre d'animaux*, *Type d'animal* and *Type du deuxième animal*.
   Load the tables, and print the French label of `PetKind_2023` and the
   number of lint findings.

    **Expected output:**

    ```text
    Type d'animal
    0
    ```

    ??? success "Answer"

        ```python
        french = {
            "PetCount": "Nombre d'animaux",
            "PetKind": "Type d'animal",
            "SecondPetKind": "Type du deuxième animal",
        }
        for variable in tables["variables"]:
            variable["label@fr"] = french[variable["name"]]
        for question in tables["questions"]:
            asker = next(v for v in tables["variables"] if v["question"] == question["id"])
            question["label@en"] = asker["label@en"]
            question["label@fr"] = french[asker["name"]]
        write_tables("pets-tables", tables)

        loaded = load_tables("pets-tables")
        labels = loaded.get("variables", "PetKind_2023").labels
        print(next(label.text for label in labels if label.lang == "fr"))
        # -> Type d'animal
        print(len(run_lint(loaded.to_fragment())))  # -> 0
        ```

        The column header carries the language, so `label@en` and `label@fr`
        become one label with two strings. Because each question is written
        once, it is translated once, for every wave.

---

## Quiz

???+ question "Question 1 (O1): Why can two DDI-Codebook files not share PetKind's categories?"
    **A.** DDI-Codebook has no categories.

    **B.** A codebook is complete in itself: its identifiers are local to the file, and nothing in it can refer to an item in another file.

    **C.** The categories are in different languages.

    **D.** They can, with `catgry`.

    ??? success "Answer"
        **B.** Each wave's codebook writes the categories again. In
        DDI-Lifecycle the code list is an item with a URN, which every wave's
        variables refer to.

???+ question "Question 2 (O3): The 2022 and 2023 codebooks word one question differently. What does the converter of this module do?"
    **A.** It merges them, since the variable has the same name.

    **B.** It keeps two questions, and leaves the decision to merge them to the survey's owner, who can map one wording to the other.

    **C.** It stops with an error.

    **D.** It keeps the most recent wording only.

    ??? success "Answer"
        **B.** A variable name is not a question. A program can compare
        wordings, but whether two wordings ask the same thing is a decision.

???+ question "Question 3 (O4): In the tables, what ties PetKind_2023 to the 2023 study?"
    **A.** Its name.

    **B.** Its `dataset` column: the 2023 data file, whose `study` is `PETS2023`.

    **C.** Its question.

    **D.** The order of the rows.

    ??? success "Answer"
        **B.** The question is shared by both waves; the data file belongs to
        one study, and the variable is a column of that file.

???+ question "Question 4 (O4): Two waves, three variables with the same four categories. How many code lists does the DDI-Lifecycle file hold?"
    **A.** Three.

    **B.** One, which the three variables refer to.

    **C.** Two, one per wave.

    **D.** None: categories stay in the variables.

    ??? success "Answer"
        **B.** The categories are compared as a whole, and the same set
        becomes one code list.

???+ question "Question 5 (O5): A codebook's conditions of use say “Free to reuse with attribution (CC BY 4.0).” What should the converted file hold?"
    **A.** The same sentence, in a custom property.

    **B.** The licence's web address in the citation's `dcterms:license`, through the `license` column.

    **C.** Nothing: licences are the archive's business.

    **D.** The word "CC BY 4.0" in the title.

    ??? success "Answer"
        **B.** A web address names one licence without ambiguity, and a
        program can recognize it. The sentence is clear to a person only.

---

## Check yourself

- [ ] I can explain why codebooks repeat questions and categories, and how DDI-Lifecycle lets every wave refer to one item. (O1)
- [ ] I can read DDI-Codebook 2.5 or 2.6 files' citations, files and variables with ElementTree. (O2)
- [ ] I can find the questions, code lists and universes several codebooks repeat, and say when a repeat is the same item. (O3)
- [ ] I can write the tables with each repeated item once, and load several waves as one series. (O4)
- [ ] I can carry over the DOI, add a licence address, a record of the conversion and labels, and check them with the linter. (O5)

---

!!! tip "Instructor notes"
    - Start with two codebooks of the same survey from the room's own
      archive, if there are any. Ask learners to find what changed between
      the years before running any code.
    - The decision in section 4 is the heart of the module: who says that
      two wordings are the same question? Let the room argue about "home"
      and "household".
    - Exercise 3 shows the payoff: a third wave adds no question. Run it on
      the projector.
    - Learners often expect `ddi-l` to read codebooks itself. It does not, by
      design: the tables are the documented way in, and they report every
      problem with its row and column.

---

**See also:** [Load DDI from spreadsheets](../spreadsheet-import.en.md) | [Work with other tools](../interoperability.en.md#ddi-codebook-files) | [Module 21: Describe your data with DDI-CDI](module-21-ddi-cdi.en.md)
