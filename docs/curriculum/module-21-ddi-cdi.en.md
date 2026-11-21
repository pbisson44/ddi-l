---
description: >-
  Optional Module 21 of the ddi-l course: describe a study's data with
  DDI-CDI, the DDI Alliance's standard for integrating data across domains,
  and validate the result against its schema.
---

# Module 21 (optional): Describe your data with DDI-CDI

!!! info "Learning objectives"
    By the end of this module, you can:

    - **O1.** Say what DDI-CDI describes, how it differs from DDI-Lifecycle
      and DDI-Codebook, and when a project would use it.
    - **O2.** Map a variable of a `ddi-l` study onto DDI-CDI: an instance
      variable whose values come from a substantive value domain, and whose
      missing values come from a sentinel value domain, each backed by a code
      list.
    - **O3.** Describe a data file as a DDI-CDI wide data structure, with an
      identifier component and measure components, and say how a long
      structure differs.
    - **O4.** Write DDI-CDI 1.0 XML from a `ddi-l` study with Python's
      `xml.etree.ElementTree`, and validate it against the DDI Alliance's
      schema.
    - **O5.** Explain how DDI-CDI identifies objects and links them, and
      compare it with a DDI-Lifecycle URN.

**Prerequisites:** [Module 9](module-09-code-lists.en.md).
[Module 20](module-20-codebook-to-lifecycle.en.md) helps, but is not needed.
This module is optional: the capstone does not need it.

**Time:** 60 min self-paced / 75 min instructor-led.

**New in this module:** DDI-CDI 1.0, `InstanceVariable`,
`SubstantiveValueDomain`, `SentinelValueDomain`, `CodeList`, `Code`,
`Notation`, `Category`, `WideDataStructure`, `IdentifierComponent`,
`MeasureComponent`, `WideDataSet`, `xmlschema.XMLSchema11`.

---

## 1. Three DDI standards

The DDI Alliance published **DDI Cross-Domain Integration** (DDI-CDI) 1.0 in
January 2025. It does not replace the other two standards; it describes
something they do not:

| | DDI-Codebook | DDI-Lifecycle | DDI-CDI |
| --- | --- | --- | --- |
| Describes | One study and its data files | Studies through their life: concepts, questions, questionnaires, variables, data files | Data themselves: each value, in whatever structure it is stored, and the processes that produced it |
| Domains | Social sciences | Social, economic and health statistics | Any domain, so data from different fields can be combined |
| Data structures | A data file of rows and columns | Record layouts and multidimensional tables | Wide, long, multidimensional and key-value |
| Encodings | XML | XML | A UML model, encoded as XML Schema and as an RDF ontology with JSON-LD |

A project uses DDI-CDI when it combines data from several sources, such as a
survey, a register and sensor readings, and needs to say exactly how each
value relates to the others, whatever shape each source has. The survey's
own questions and questionnaire stay in DDI-Lifecycle.

`ddi-l` reads and writes DDI-Lifecycle only. This module reads a `ddi-l`
study and writes the DDI-CDI description of its data with Python's standard
library, then checks it against the DDI Alliance's schema.

## 2. The study to describe

The study is a data file with one row per household, as in earlier modules:
an identifier, the kind of pet, which may be "Don't know", and the number of
pets. The [metadata tables](../spreadsheet-import.en.md) build it in a few
lines:

```python
from pathlib import Path

from ddi_l.tables import load_tables

folder = Path("pets-tables")
folder.mkdir(exist_ok=True)
files = {
    "settings": "setting,value\nagency,example.org\n",
    "code_lists": "id,label@en\nPET_KINDS,Kinds of pet\n",
    "codes": (
        "code_list,value,label@en,missing\n"
        "PET_KINDS,1,Dog,\n"
        "PET_KINDS,2,Cat,\n"
        "PET_KINDS,3,Other pet,\n"
        "PET_KINDS,9,Don't know,true\n"
    ),
    "variables": (
        "id,label@en,representation,code_list,numeric_type,max_length\n"
        "HouseholdId,Household identifier,text,,,10\n"
        "PetKind,Kind of pet,code,PET_KINDS,,\n"
        "PetCount,Number of pets,numeric,,Integer,\n"
    ),
}
for name, text in files.items():
    (folder / f"{name}.csv").write_text(text, encoding="utf-8")

tables = load_tables(folder)
items = {item.identifier: item for item in tables.items}
print(len(tables.variables))  # -> 3
```

`items` finds any item by its identifier, which is how the code below
follows a reference: from a variable to its code list, and from a code to its
category.

## 3. Variables in DDI-CDI

Both standards describe a variable at three levels, from the most general to
the most specific:

| Level | What it is | DDI-Lifecycle | DDI-CDI |
| --- | --- | --- | --- |
| Conceptual | What is measured, whatever the answers | `ConceptualVariable` | `ConceptualVariable` |
| Represented | What is measured and how the values are recorded | `RepresentedVariable` | `RepresentedVariable` |
| Instance | A column of one data file | `Variable` | `InstanceVariable` |

In DDI-CDI each level builds on the one above it: an instance variable is a
represented variable, which is a conceptual variable. This module writes the
instance level only.

The other difference is how values are described. In DDI-Lifecycle, a
variable has one code list, and a category is marked `isMissing`. DDI-CDI
splits the values of a variable in two **value domains**:

- a **substantive value domain**: the answers to the question, here Dog, Cat
  and Other pet;
- a **sentinel value domain**: the values that stand for something else,
  such as "Don't know", "Refused" or "Not applicable".

Each value domain takes its values from a **code list**. In a code list, a
**code** links a **notation**, the value stored in the data such as `9`, to
the **category** it stands for, such as "Don't know".

## 4. Identify and link objects

DDI-CDI identifies an object as DDI-Lifecycle does, by an agency, an
identifier and a version, written as three elements of `identifier`. A
link to another object gives the same three parts and the object's class.
Four small functions write them:

```python
import xml.etree.ElementTree as ET

CDI = "http://ddialliance.org/Specification/DDI-CDI/1.0/XMLSchema/"
ET.register_namespace("cdi", CDI)


def cdi(tag, *children, text=None):
    """A cdi: element holding children, or text."""
    element = ET.Element(f"{{{CDI}}}{tag}")
    element.text = text
    element.extend(children)
    return element


def identifier(object_id, agency="example.org", version="1"):
    """What DDI-Lifecycle writes as Agency, ID and Version."""
    return cdi(
        "identifier",
        cdi(
            "ddiIdentifier",
            cdi("dataIdentifier", text=object_id),
            cdi("registrationAuthorityIdentifier", text=agency),
            cdi("versionIdentifier", text=version),
        ),
    )


def link(association, object_id, valid_type, agency="example.org", version="1"):
    """A reference to another object: its identifier and its class."""
    return cdi(
        association,
        cdi(
            "ddiReference",
            cdi("dataIdentifier", text=object_id),
            cdi("registrationAuthorityIdentifier", text=agency),
            cdi("versionIdentifier", text=version),
        ),
        cdi("validType", text=valid_type),
    )


def label(text, language="en"):
    """A label in one language."""
    return cdi(
        "displayLabel",
        cdi(
            "languageSpecificString",
            cdi("content", text=text),
            cdi("language", text=language),
        ),
    )
```

A link's element is named after the association it stands for: its class,
what the link means, and the class it points to. `Code_denotes_Category`, for
example, links a code to the category it denotes. The schema fixes the
order of the elements in each class, which these functions follow.

## 5. Code lists and value domains

A code list gives three objects per code: the category, the notation and
the code that joins them. Each one gets an identifier built from the code
list's and the value, so that links between them are easy to write:

```python
def code_list(list_id, codes):
    """A code list, with a Category, a Notation and a Code per code."""
    objects = []
    code_links = []
    for code in codes:
        category = items[code.category.identifier]
        key = f"{list_id}-{code.value}"
        objects.append(
            cdi(
                "Category",
                label(category.labels[0].text),
                identifier(f"category-{key}"),
            )
        )
        objects.append(
            cdi(
                "Notation",
                cdi("content", cdi("content", text=code.value)),
                identifier(f"notation-{key}"),
            )
        )
        objects.append(
            cdi(
                "Code",
                identifier(f"code-{key}"),
                link("Code_denotes_Category", f"category-{key}", "Category"),
                link("Code_uses_Notation", f"notation-{key}", "Notation"),
            )
        )
        code_links.append(link("CodeList_has_Code", f"code-{key}", "Code"))
    listing = cdi(
        "CodeList",
        identifier(list_id),
        cdi("allowsDuplicates", text="false"),
        *code_links,
    )
    return [*objects, listing]
```

A variable with a code list gets two code lists and two value domains: the
substantive codes, and the codes whose category is missing. Then comes the
instance variable, with its links to its domains:

```python
def describe(variable):
    """The DDI-CDI objects for one ddi-l variable: its domains and itself."""
    name = variable.names[0].text
    objects = []
    domains = []
    coded = variable.variable_representation.code_representation
    if coded is not None:
        codes = items[coded.code_list_reference.identifier].codes
        missing = [c for c in codes if items[c.category.identifier].isMissing]
        answers = [c for c in codes if c not in missing]
        objects += code_list(f"codes-{name}", answers)
        objects.append(
            cdi(
                "SubstantiveValueDomain",
                identifier(f"values-{name}"),
                link(
                    "SubstantiveValueDomain_takesValuesFrom_EnumerationDomain",
                    f"codes-{name}",
                    "CodeList",
                ),
            )
        )
        if missing:
            objects += code_list(f"missing-{name}", missing)
            objects.append(
                cdi(
                    "SentinelValueDomain",
                    identifier(f"missing-values-{name}"),
                    link(
                        "SentinelValueDomain_takesValuesFrom_EnumerationDomain",
                        f"missing-{name}",
                        "CodeList",
                    ),
                )
            )
            domains.append(
                link(
                    "RepresentedVariable_takesSentinelValuesFrom_SentinelValueDomain",
                    f"missing-values-{name}",
                    "SentinelValueDomain",
                )
            )
        domains.append(
            link(
                "RepresentedVariable_takesSubstantiveValuesFrom_SubstantiveValueDomain",
                f"values-{name}",
                "SubstantiveValueDomain",
            )
        )
    objects.append(
        cdi(
            "InstanceVariable",
            label(variable.labels[0].text),
            identifier(f"variable-{name}"),
            cdi("name", cdi("name", text=name)),
            *domains,
        )
    )
    return objects


model = cdi("DDICDIModels")
for variable in tables.variables:
    model.extend(describe(variable))
print(len(model))  # -> 19
```

`PetKind` gives 17 objects: 3 codes of answers and 1 code for "Don't know",
with their categories, notations and codes, 2 code lists, 2 value domains
and the variable. `HouseholdId` and `PetCount` give one instance variable
each. All of them sit side by side in `DDICDIModels`, the root element, and
point to each other by identifier.

## 6. The data structure

A data file with one row per unit and one column per variable is **wide**.
DDI-CDI describes its structure with one **component** per column, each
defined by its variable:

- an **identifier component** for the columns that tell the rows apart,
  here `HouseholdId`;
- a **measure component** for each column of observed values, here `PetKind`
  and `PetCount`.

```python
components = []
structure_links = []
for variable in tables.variables:
    name = variable.names[0].text
    kind = "IdentifierComponent" if name == "HouseholdId" else "MeasureComponent"
    components.append(
        cdi(
            kind,
            identifier(f"component-{name}"),
            link(
                "DataStructureComponent_isDefinedBy_RepresentedVariable",
                f"variable-{name}",
                "InstanceVariable",
            ),
        )
    )
    structure_links.append(
        link("DataStructure_has_DataStructureComponent", f"component-{name}", kind)
    )

model.extend(components)
model.append(cdi("WideDataStructure", identifier("pets-structure"), *structure_links))
model.append(
    cdi(
        "WideDataSet",
        identifier("pets-data"),
        link(
            "DataSet_isStructuredBy_DataStructure",
            "pets-structure",
            "WideDataStructure",
        ),
    )
)
ET.indent(model)
ET.ElementTree(model).write("pets-cdi.xml", encoding="utf-8", xml_declaration=True)
print(len(model))  # -> 24
```

The same values could be stored **long**: one row per household and
variable, with a column naming the variable and a column holding its value.
DDI-CDI describes that file with a long data structure, in which those two
columns are a variable descriptor component and a variable value component.
The variables, value domains and code lists stay the same: that is what lets
DDI-CDI say that two files hold the same data in different shapes.

## 7. Validate against the schema

The DDI Alliance publishes the DDI-CDI 1.0 XML Schema on its
[DDI-CDI page](https://ddialliance.org/ddi-cdi_v1.0), and in the release on
GitHub. Download it once:

<!-- docs-test: skip -- downloads the schema -->
```python
from urllib.request import urlretrieve

urlretrieve(
    "https://raw.githubusercontent.com/ddi-cdi/ddi-cdi/v1.0/"
    "build/encoding/xml-schema/ddi-cdi.xsd",
    "ddi-cdi.xsd",
)
```

Then validate with `xmlschema`, which `pip install ddi-l` installs:

<!-- docs-test: skip -- needs the downloaded schema -->
```python
import xmlschema

schema = xmlschema.XMLSchema11("ddi-cdi.xsd")
print(schema.is_valid("pets-cdi.xml"))  # -> True
for error in schema.iter_errors("pets-cdi.xml"):
    print(error.path, error.reason)
```

!!! warning "Use XMLSchema11"
    The DDI-CDI schema says that it needs an XML Schema 1.1 processor.
    `xmlschema.XMLSchema`, the XML Schema 1.0 validator, honours that and
    skips the whole schema: it then reports that `DDICDIModels` "is not an
    element of the schema". `xmlschema.XMLSchema11` reads it.

An error names the element where the file departs from the schema. The most
common one comes from writing the elements of a class in another order than
the schema's.

## 8. What this sketch leaves out

DDI-CDI can say much more than this file does:

- **The other levels of each variable.** A represented variable shared by
  several data files, and a conceptual variable with its concept and unit
  type (households here), would let another file's variables point to the
  same ones.
- **The values themselves.** A data point is one cell of the file, and a
  datum the value in it. Describing them lets DDI-CDI trace a single value
  from one file to another.
- **The physical file.** How the columns are laid out in a CSV file or a
  fixed-width file, and the formats of statistical software.
- **The process.** Activities and steps record how data were produced or
  transformed, from collection to the published file.

The DDI Alliance also publishes DDI-CDI as an RDF ontology, with a JSON-LD
encoding: the same classes and associations, for linked-data systems.

---

## Exercises

1. **(O1)** For each project, which DDI standard fits best? (a) An archive
   documents a deposited survey file for its catalogue. (b) A statistical
   agency keeps its questions and code lists in a bank, reused by every wave.
   (c) A research team combines a survey, hospital records and air-quality
   readings, and must show how each value was derived.

    ??? success "Answer"

        (a) DDI-Codebook, or DDI-Lifecycle if the archive wants item-level
        reuse: one study and its file. (b) DDI-Lifecycle: each question and
        code list is an item with its own identifier and version, referred to
        by every wave. (c) DDI-CDI: data from different domains and shapes,
        and the processes that link them. The survey's questionnaire would
        still be described in DDI-Lifecycle.

2. **(O2, O5)** Read `pets-cdi.xml` back with ElementTree. For each instance
   variable, print its name and the classes of the value domains it takes
   values from.

    **Expected output:**

    ```text
    HouseholdId []
    PetKind ['SentinelValueDomain', 'SubstantiveValueDomain']
    PetCount []
    ```

    ??? success "Answer"

        ```python
        written = ET.parse("pets-cdi.xml").getroot()
        N = {"cdi": CDI}
        for variable in written.iterfind("cdi:InstanceVariable", N):
            name = variable.findtext("cdi:name/cdi:name", namespaces=N)
            domains = [
                valid_type.text for valid_type in variable.iterfind("*/cdi:validType", N)
            ]
            print(name, domains)
        ```

        A link holds the class of the object it points to in `validType`, so
        a program knows what it will find without following the link.
        `HouseholdId` and `PetCount` have no code list, so this sketch gives
        them no value domain.

3. **(O3)** The same pet data are stored long, with the columns
   `HouseholdId`, `Variable` and `Value`: `Variable` holds `PetKind` or
   `PetCount`, and `Value` the answer. Name the kind of data structure and the
   component each column gets.

    ??? success "Answer"

        A long data structure (`LongDataStructure`). `HouseholdId` is an
        identifier component, as in the wide file. `Variable` is a variable
        descriptor component: its values name the variables, and it is
        defined by a descriptor variable whose values are `PetKind` and
        `PetCount`. `Value` is a variable value component: it holds the
        values of several variables in one column. `PetKind` and `PetCount`
        keep their instance variables and value domains.

4. **(O4)** Give every category a French label as well as an English one.
   Change `label()` to take several `(text, language)` pairs, label the
   categories with *Chien*, *Chat*, *Autre animal* and *Ne sait pas*, write
   the file again, and print how many French strings it holds.

    **Expected output:**

    ```text
    4
    ```

    ??? success "Answer"

        ```python
        def label(*strings):
            """A label in each language given, as (text, language) pairs."""
            return cdi(
                "displayLabel",
                *(
                    cdi(
                        "languageSpecificString",
                        cdi("content", text=text),
                        cdi("language", text=language),
                    )
                    for text, language in strings
                ),
            )


        french = {"Dog": "Chien", "Cat": "Chat", "Other pet": "Autre animal"}
        french["Don't know"] = "Ne sait pas"
        written = ET.parse("pets-cdi.xml").getroot()
        N = {"cdi": CDI}
        for category in written.iterfind("cdi:Category", N):
            english = category.findtext(
                "cdi:displayLabel/cdi:languageSpecificString/cdi:content", namespaces=N
            )
            category.remove(category.find("cdi:displayLabel", N))
            category.insert(0, label((english, "en"), (french[english], "fr")))
        ET.indent(written)
        ET.ElementTree(written).write("pets-cdi.xml", encoding="utf-8", xml_declaration=True)
        print(
            sum(1 for language in written.iter(f"{{{CDI}}}language") if language.text == "fr")
        )  # -> 4
        ```

        The new label goes first in each category, where the schema puts
        `displayLabel`, before `identifier`. Validate the file again to check.

5. **(O5)** Print the DDI-Lifecycle URN of the `PetKind` variable in the
   tables, then the three parts DDI-CDI writes for the same variable in
   `pets-cdi.xml`. What would make the two point to the same thing?

    ??? success "Answer"

        ```python
        pet_kind = tables.get("variables", "PetKind")
        print(pet_kind.to_reference().urn)
        # -> urn:ddi:example.org:e96e0842-d74e-5893-a7ba-b3c3fabda24d:1
        written = ET.parse("pets-cdi.xml").getroot()
        N = {"cdi": CDI}
        for variable in written.iterfind("cdi:InstanceVariable", N):
            if variable.findtext("cdi:name/cdi:name", namespaces=N) == "PetKind":
                parts = variable.find("cdi:identifier/cdi:ddiIdentifier", N)
                print([part.text for part in parts])
        # -> ['variable-PetKind', 'example.org', '1']
        ```

        Both have an agency, an identifier and a version. The DDI-CDI file
        uses identifiers of its own, such as `variable-PetKind`. To make the
        two descriptions of the variable the same object, give DDI-CDI the
        DDI-Lifecycle identifier: pass `pet_kind.identifier` and
        `pet_kind.version` to `identifier()` instead.

---

## Quiz

???+ question "Question 1 (O1): What does DDI-CDI describe that DDI-Lifecycle does not?"
    **A.** Questionnaires and their routing.

    **B.** The data themselves, in wide, long, multidimensional or key-value structures, and the processes that produced them, across domains.

    **C.** Code lists.

    **D.** Study titles.

    ??? success "Answer"
        **B.** Questionnaires are DDI-Lifecycle's strength; both have code
        lists. DDI-CDI describes data in any shape, from any domain, down to
        a single value.

???+ question "Question 2 (O2): A variable has the codes 1 Dog, 2 Cat and 9 Don't know. How does DDI-CDI hold them?"
    **A.** One code list, with 9 marked as missing.

    **B.** A substantive value domain with a code list of 1 and 2, and a sentinel value domain with a code list of 9.

    **C.** Three instance variables.

    **D.** In the data structure.

    ??? success "Answer"
        **B.** DDI-CDI separates the answers from the values that stand for
        something else. DDI-Lifecycle does it with one code list and the
        `isMissing` flag of a category.

???+ question "Question 3 (O3): In a wide data structure, what does the household identifier column get?"
    **A.** A measure component.

    **B.** An identifier component, defined by the identifier's variable.

    **C.** A variable value component.

    **D.** Nothing: identifiers are not described.

    ??? success "Answer"
        **B.** Identifier components tell the rows apart; measure components
        hold what was observed.

???+ question "Question 4 (O4): xmlschema.XMLSchema says DDICDIModels is not an element of the schema. Why?"
    **A.** The file has the wrong namespace.

    **B.** The DDI-CDI schema needs an XML Schema 1.1 processor; the 1.0 validator skips it, so use `xmlschema.XMLSchema11`.

    **C.** The schema file is corrupted.

    **D.** `DDICDIModels` must be the last element.

    ??? success "Answer"
        **B.** The schema declares `vc:minVersion="1.1"`. An XML Schema 1.0
        processor honours that by ignoring the schema's content.

???+ question "Question 5 (O5): What does a DDI-CDI link hold?"
    **A.** The other object, copied in full.

    **B.** The other object's identifier (data identifier, registration authority and version) and its class in `validType`.

    **C.** A file path.

    **D.** A URN only.

    ??? success "Answer"
        **B.** `ddiReference` gives the same three parts as a DDI-Lifecycle
        URN, and `validType` says which class to expect.

---

## Check yourself

- [ ] I can say what DDI-CDI describes, and when to use it next to DDI-Lifecycle and DDI-Codebook. (O1)
- [ ] I can map a coded variable with missing values onto an instance variable, two value domains and their code lists. (O2)
- [ ] I can describe a data file as a wide data structure, and name the components a long one would use. (O3)
- [ ] I can write DDI-CDI XML from a `ddi-l` study and validate it with `xmlschema.XMLSchema11`. (O4)
- [ ] I can explain a DDI-CDI identifier and link, and how they compare with a DDI-Lifecycle URN. (O5)

---

!!! tip "Instructor notes"
    - Start with the table of section 1 and a real case from the room: a
      project that combines files of different shapes. DDI-CDI makes sense
      once learners have felt that problem.
    - The split between substantive and sentinel values (section 3) is the
      idea learners keep. Ask which values of a familiar variable are
      sentinels before showing the code.
    - Download the schema before the session if the room's network is slow:
      it is about 1 MB.
    - The file is long for three variables. That is the point of the
      exercise on identifiers: in practice a program writes DDI-CDI, as it
      does here, and nobody types it.

---

**See also:** [Module 20: From DDI-Codebook to DDI-Lifecycle, built for reuse](module-20-codebook-to-lifecycle.en.md) | [Work with other tools](../interoperability.en.md) | [DDI-CDI at the DDI Alliance](https://ddialliance.org/ddi-cdi_v1.0)
