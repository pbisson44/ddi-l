---
description: >-
  Exchange DDI metadata between ddi-l and other tools, most of them open
  source: XML and schema tools, linked data and SPARQL, JSON, spreadsheets,
  R, any language over HTTP, DDI Codebook files from tools such as Dataverse,
  DDI 3.2 tools and questionnaire generators. Each section has an example you
  can run.
---

# Work with other tools

`ddi-l` reads DDI Lifecycle 3.1, 3.2 and 3.3, and writes standard DDI
Lifecycle 3.3 XML that validates against the DDI Alliance's schemas. Most
tools that work with DDI can therefore share files with it. This page shows
how, tool by tool, with examples you can run. Every example uses a small
fictional pet survey.

## What ddi-l exchanges

| Format | ddi-l reads | ddi-l writes | Use it with |
| --- | --- | --- | --- |
| DDI Lifecycle 3.3 XML (`DDIInstance`, `FragmentInstance`) | yes, and edits it | yes | DDI 3.3 tools, any XML tool |
| DDI Lifecycle 3.1 and 3.2 XML | yes: validate, lint, element access | no | DDI 3.1 and 3.2 tools |
| JSON (`ddi to-json`, `ddi from-json`) | yes | yes | web apps, document stores, any language |
| JSON-LD (DDI-RDF Discovery vocabulary) | no | yes, a summary | triple stores, SPARQL, data catalogues |
| CSV files or an Excel workbook | yes | blank templates | spreadsheets, pandas, R |
| HTTP (`ddi serve`) | yes | yes | any language that can send a request |
| DDI Codebook 2.x | no | no | convert it, [as shown below](#ddi-codebook-files) |

## Any XML tool

A file written by `ddi-l` is plain DDI XML. Build the survey once; the
sections below reuse it:

```python
import ddi_l as ddi

doc = ddi.new_study(title="Pet survey", agency="example.org")
question = doc.add_question(
    text="How many pets live in your home?", label="Pet count question"
)
doc.add_variable(name="PetCount", question=question, label="Number of pets")
doc.save("pets.xml")
```

Any XML library can read it. This uses only Python's standard library, not
`ddi-l`:

```python
import xml.etree.ElementTree as ET

NS = {"l": "ddi:logicalproduct:3_3", "r": "ddi:reusable:3_3"}
for variable in ET.parse("pets.xml").iter("{ddi:logicalproduct:3_3}Variable"):
    print(variable.findtext("l:VariableName/r:String", namespaces=NS))
# -> PetCount
```

Any schema validator can check it. `ddi-l` ships the DDI Alliance's schemas,
so `xmllint` (part of the open-source libxml2) can use them directly:

```bash
SCHEMA=$(python -c "from importlib.resources import files; print(files('ddi_l.schemas') / 'ddi' / 'v3_3' / 'instance_3_3.xsd')")
xmllint --noout --schema "$SCHEMA" pets.xml
# -> pets.xml validates
```

The same goes for XSLT processors, XQuery databases and XML editors.

## Linked data: RDF and SPARQL

`ddi-l` writes a study as JSON-LD with the DDI Alliance's
[DDI-RDF Discovery vocabulary](https://rdf-vocabulary.ddialliance.org/discovery.html):
studies, variables, questions, concepts and universes. Any RDF tool can load
it. With the open-source [rdflib](https://github.com/RDFLib/rdflib)
(`pip install rdflib`), a SPARQL query lists each variable and its question:

```python
import json

from ddi_l.jsonld import to_jsonld
from rdflib import Graph

graph = Graph().parse(data=json.dumps(to_jsonld(doc)), format="json-ld")
rows = graph.query("""
    PREFIX disco: <http://rdf-vocabulary.ddialliance.org/discovery#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?name ?text WHERE {
        ?variable a disco:Variable ;
                  skos:prefLabel ?name ;
                  disco:question ?question .
        ?question disco:questionText ?text .
    }
""")
for name, text in rows:
    print(f"{name}: {text}")
# -> PetCount: How many pets live in your home?
```

From the command line, `ddi to-jsonld pets.xml --output pets.jsonld` writes the
same file, ready for a triple store that loads JSON-LD, such as Apache Jena.

The vocabulary describes a study for discovery, so the JSON-LD is a summary:
questionnaire flow, record layouts and the rest are left out, and it does not
convert back to DDI XML. For a full copy, use JSON.

## JSON, for web apps and other languages

`ddi to-json` writes the whole document as JSON, and `ddi from-json` turns it
back into XML:

```bash
ddi to-json pets.xml --output pets.json
ddi from-json pets.json --output pets-again.xml
```

The JSON keeps the XML's structure, with namespaced names as keys, so any
language can read and edit it. See
[Use the command line](cli-recipes.en.md) for more options.

## Spreadsheets and data frames

Many teams keep metadata in spreadsheets. `ddi-l` loads a folder of CSV files
or an Excel workbook as DDI, so anything that writes CSV can feed it:
LibreOffice, Excel, pandas, R or a database export. See
[Load DDI from spreadsheets](spreadsheet-import.en.md) for the layout and
[the templates](spreadsheet-templates.en.md) to start from. The
[DDI Codebook example](#ddi-codebook-files) below writes such tables from
another tool's output.

## R

R can call `ddi-l` through the open-source
[reticulate](https://rstudio.github.io/reticulate/) package: build a study
from a data frame, read variables back into one, validate and lint. See
[Using ddi-l from R](r-users.en.md).

## Any language, over HTTP

`ddi serve` runs an HTTP API (install the `server` extra) that validates,
lints and converts, so a tool in any language can use it without Python:

```bash
ddi serve --port 8080
curl --data-binary @pets.xml http://localhost:8080/v1/validate
```

The API describes itself at `/schema/openapi.json`, so client generators such
as the open-source OpenAPI Generator can build a client for your language.
See [HTTP API](server.en.md).

## DDI Codebook files

DDI Codebook (versions 2.x) is the DDI standard many data archives use to
document studies and their variables. For example, the open-source data repository
[Dataverse](https://github.com/IQSS/dataverse) exports DDI Codebook 2.5.
`ddi-l` does not read DDI Codebook, but its variables, questions and
categories map onto the [spreadsheet tables](spreadsheet-import.en.md), which
`ddi-l` does read. This converts a small DDI Codebook file:

```python
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

from ddi_l.tables import load_tables

Path("codebook.xml").write_text(
    """<codeBook xmlns="ddi:codebook:2_5" version="2.5">
  <dataDscr>
    <var name="PetCount">
      <labl>Number of pets</labl>
      <qstn><qstnLit>How many pets live in your home?</qstnLit></qstn>
    </var>
    <var name="PetKind">
      <labl>Kind of pet</labl>
      <qstn><qstnLit>What kind of pet do you have?</qstnLit></qstn>
      <catgry><catValu>1</catValu><labl>Dog</labl></catgry>
      <catgry><catValu>2</catValu><labl>Cat</labl></catgry>
    </var>
  </dataDscr>
</codeBook>
""",
    encoding="utf-8",
)

C = {"c": "ddi:codebook:2_5"}
tables = {"questions": [], "code_lists": [], "codes": [], "variables": []}
for var in ET.parse("codebook.xml").iterfind(".//c:var", C):
    name = var.get("name")
    label = var.findtext("c:labl", namespaces=C)
    categories = var.findall("c:catgry", C)
    code_list = f"{name}_codes" if categories else ""
    # Without categories, this sketch reads a variable as a whole number.
    kind = {"code_list": code_list, "numeric_type": "" if categories else "Integer"}
    tables["questions"].append(
        {
            "id": f"{name}_q",
            "name": name,
            "text@en": var.findtext("c:qstn/c:qstnLit", namespaces=C),
            "response": "code" if categories else "numeric",
            **kind,
        }
    )
    tables["variables"].append(
        {
            "id": name,
            "name": name,
            "label@en": label,
            "question": f"{name}_q",
            "representation": "code" if categories else "numeric",
            **kind,
        }
    )
    if categories:
        tables["code_lists"].append({"id": code_list, "label@en": label})
        for category in categories:
            tables["codes"].append(
                {
                    "code_list": code_list,
                    "value": category.findtext("c:catValu", namespaces=C),
                    "label@en": category.findtext("c:labl", namespaces=C),
                }
            )

folder = Path("from-codebook")
folder.mkdir(exist_ok=True)
(folder / "settings.csv").write_text(
    "setting,value\nagency,example.org\n", encoding="utf-8"
)
for table, rows in tables.items():
    with open(folder / f"{table}.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

study = load_tables(folder).to_study("Pet survey")
print(study.validate())  # -> []
study.save("pets-lifecycle.xml")
```

The sketch covers names, labels, question text and categories. Codebook files
vary from tool to tool: check what yours writes (missing values, value types,
several languages) and add the matching columns, which
[Load DDI from spreadsheets](spreadsheet-import.en.md) lists.

## DDI 3.1 and 3.2 tools

Some tools write DDI 3.2. For example, CLOSER's open-source questionnaire
editor [Archivist](https://github.com/CLOSER-Cohorts/archivist) documents
questionnaires in DDI Lifecycle 3.2, according to CLOSER. `ddi-l` validates
and lints such files: `ddi validate` reads the version from the file.

```bash
ddi validate archivist-export.xml
```

In Python, `read_ddi()` opens any of the three versions and gives element
access to the XML. `open_ddi()`, with its typed models, is for DDI 3.3 and
says so when given an earlier version.

```python
legacy = ddi.read_ddi("archivist-export.xml")
print(legacy.validate())  # -> []
```

## Questionnaire generators

Some open-source tools turn a questionnaire's DDI description into the
questionnaires that interviewers and respondents use. For example, Insee's
[Eno](https://github.com/InseeFr/Eno) produces web, telephone, face-to-face
and paper questionnaires from DDI, and its designer
[Pogues](https://github.com/InseeFr/Pogues) works with it. Before handing a
questionnaire to such a tool, check it with `ddi-l`: `ddi validate`,
`ddi lint`, and `ddi conform` to compare it with a spec (see
[Check a questionnaire against a spec](spec-conformance.en.md)). Check which DDI
version the tool expects first.

## Colectica

Colectica's tools are commercial. `ddi-l` reads and writes the
`FragmentInstance` files Colectica Designer exports; see
[Work with Colectica exports](colectica.en.md). `ddi-l` is not affiliated with
or endorsed by Colectica.

## Find more tools

The DDI Alliance keeps a catalogue of DDI tools, which you can filter by
licence, at [ddialliance.org/resources/tools](https://ddialliance.org/resources/tools).
Before exchanging files with a tool, check which DDI it uses: Codebook,
Lifecycle 3.x, or the newer Cross-Domain Integration (DDI-CDI), which `ddi-l`
does not read.

## Before you exchange a file

- **Validate and lint it.** `ddi validate` and `ddi lint` catch most problems
  before the other tool does. See [Validate and lint](validation.en.md).
- **Use one DDI version on both sides.** `ddi-l` writes 3.3.
- **Use a registered agency.** Agency IDs come from the DDI Alliance's
  [agency registry](https://ddialliance.org/ddi-agency-id-registry), so items
  from different organisations do not share a URN.
- **Keep identifiers and versions stable.** Bump an item's version when you
  change it, rather than giving it a new ID, so other tools see the same item.
- **Try a round trip.** Send a file through the other tool and back, and
  compare. `ddi-l` keeps what it does not model (user attribute pairs, custom
  namespaces); another tool may drop it.
