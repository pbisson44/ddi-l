"""The documents shown in the OpenAPI schema.

Swagger's "Try it out" prefills its request box from these, so
:data:`SAMPLE_XML` is a small, valid DDI Lifecycle 3.3 instance that passes
schema validation and lint. The JSON and JSON-LD below are the service's own
output for it; ``tests/test_server_examples.py`` checks all three against the
running service, and the tables samples likewise.
"""

from __future__ import annotations

import io
import zipfile
from typing import Any

from litestar.openapi.spec import Example

__all__ = [
    "EXAMPLE_JSONLD_GRAPH",
    "EXAMPLE_JSON_DOCUMENT",
    "EXAMPLE_TABLES_FRAGMENT",
    "EXAMPLE_TABLES_WORKBOOK",
    "EXAMPLE_TABLES_ZIP",
    "EXAMPLE_TEMPLATE_WORKBOOK",
    "EXAMPLE_TEMPLATE_ZIP",
    "EXAMPLE_XML_DOCUMENT",
    "SAMPLE_JSON",
    "SAMPLE_JSONLD",
    "SAMPLE_TABLES",
    "SAMPLE_TABLES_FRAGMENT",
    "SAMPLE_TABLES_WITH_A_PROBLEM",
    "SAMPLE_XML",
    "tables_zip",
]

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<DDIInstance
    xmlns="ddi:instance:3_3"
    xmlns:r="ddi:reusable:3_3"
    xmlns:s="ddi:studyunit:3_3">
  <r:Agency>example.org</r:Agency>
  <r:ID>4d1e9d5a-0a3f-4b1e-9e6f-9d1c2b3a4e5f</r:ID>
  <r:Version>1</r:Version>
  <r:Citation>
    <r:Title>
      <r:String xml:lang="en">Household Survey</r:String>
    </r:Title>
  </r:Citation>
  <s:StudyUnit>
    <r:Agency>example.org</r:Agency>
    <r:ID>7f2b8c14-5d6e-4f7a-8b9c-0d1e2f3a4b5c</r:ID>
    <r:Version>1</r:Version>
    <r:Citation>
      <r:Title>
        <r:String xml:lang="en">Household Survey</r:String>
      </r:Title>
    </r:Citation>
    <r:Abstract>
      <r:Content xml:lang="en">Annual survey of household composition.</r:Content>
    </r:Abstract>
  </s:StudyUnit>
</DDIInstance>
"""

# `POST /v1/convert/json` of SAMPLE_XML. Clark notation throughout -- the keys
# carry the namespace URI, which is what makes the mapping reversible.
SAMPLE_JSON: dict[str, Any] = {
    "@isMaintainable": True,
    "{ddi:reusable:3_3}Agency": "example.org",
    "{ddi:reusable:3_3}ID": {
        "@type": "ID",
        "#text": "4d1e9d5a-0a3f-4b1e-9e6f-9d1c2b3a4e5f",
    },
    "{ddi:reusable:3_3}Version": "1",
    "{ddi:reusable:3_3}Citation": {
        "{ddi:reusable:3_3}Title": {
            "{ddi:reusable:3_3}String": {
                "@{http://www.w3.org/XML/1998/namespace}lang": "en",
                "#text": "Household Survey",
            }
        }
    },
    "{ddi:studyunit:3_3}StudyUnit": {
        "@isMaintainable": True,
        "{ddi:reusable:3_3}Agency": "example.org",
        "{ddi:reusable:3_3}ID": {
            "@type": "ID",
            "#text": "7f2b8c14-5d6e-4f7a-8b9c-0d1e2f3a4b5c",
        },
        "{ddi:reusable:3_3}Version": "1",
        "{ddi:reusable:3_3}Citation": {
            "{ddi:reusable:3_3}Title": {
                "{ddi:reusable:3_3}String": {
                    "@{http://www.w3.org/XML/1998/namespace}lang": "en",
                    "#text": "Household Survey",
                }
            }
        },
        "{ddi:reusable:3_3}Abstract": {
            "{ddi:reusable:3_3}Content": {
                "@{http://www.w3.org/XML/1998/namespace}lang": "en",
                "#text": "Annual survey of household composition.",
            }
        },
    },
}

# `POST /v1/convert/jsonld` of SAMPLE_XML. Nothing like the JSON above: Disco
# keeps only what is useful for discovery, and names it in a vocabulary a triple
# store already understands.
SAMPLE_JSONLD: dict[str, Any] = {
    "@context": {
        "disco": "http://rdf-vocabulary.ddialliance.org/discovery#",
        "dcterms": "http://purl.org/dc/terms/",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "xkos": "http://purl.org/linked-data/xkos#",
        "qb": "http://purl.org/linked-data/cube#",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "adms": "http://www.w3.org/ns/adms#",
    },
    "@graph": [
        {
            "@id": "urn:ddi:example.org:7f2b8c14-5d6e-4f7a-8b9c-0d1e2f3a4b5c:1",
            "@type": "disco:Study",
            "dcterms:title": "Household Survey",
            "dcterms:abstract": [
                {
                    "@value": "Annual survey of household composition.",
                    "@language": "en",
                }
            ],
            "dcterms:publisher": "example.org",
        }
    ],
}

EXAMPLE_XML_DOCUMENT = Example(
    summary="A minimal valid DDI Lifecycle 3.3 instance",
    description=(
        "Passes schema validation and lint with nothing to report. Paste it "
        "into any endpoint that takes XML."
    ),
    value=SAMPLE_XML,
)

EXAMPLE_JSON_DOCUMENT = Example(
    summary="The same document as JSON",
    description="Lossless. `POST /v1/convert/xml` turns it back into the XML above.",
    value=SAMPLE_JSON,
)

EXAMPLE_JSONLD_GRAPH = Example(
    summary="The same document as a Disco graph",
    description="A discovery subset, not a transcription -- and one-way by design.",
    value=SAMPLE_JSONLD,
)


# --- Metadata tables (POST /v1/tables/import, GET /v1/tables/template) ------

#: The example downloads on the documentation site, which Swagger links to:
#: a binary upload has no inline sample.
_DOWNLOADS = "https://pbisson44.github.io/ddi-l/latest/downloads/"

#: A small set of tables: one concept and the variable that measures it.
SAMPLE_TABLES: dict[str, str] = {
    "settings.csv": "setting,value\r\nagency,example.org\r\n",
    "concepts.csv": "id,label@en,label@fr\r\nAGE,Age,Âge\r\n",
    "variables.csv": (
        "id,concept,representation,numeric_type,label@en,label@fr\r\n"
        "AGE,AGE,numeric,Integer,Age in years,Âge en années\r\n"
    ),
}

#: Tables with a mistake: a variable points at a question that is not there.
SAMPLE_TABLES_WITH_A_PROBLEM: dict[str, str] = {
    "settings.csv": "setting,value\r\nagency,example.org\r\n",
    "variables.csv": "id,question\r\nAGE,Q_AGE\r\n",
}


def tables_zip(tables: dict[str, str]) -> bytes:
    """``tables`` as a zip of CSV files, the way the service reads them."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, text in tables.items():
            archive.writestr(name, text.encode("utf-8"))
    return buffer.getvalue()


#: What `POST /v1/tables/import` returns for :data:`SAMPLE_TABLES`. Only the
#: `versionDate` differs from one request to the next.
SAMPLE_TABLES_FRAGMENT = """<?xml version="1.0" encoding="utf-8"?>
<ddi:FragmentInstance xmlns:r="ddi:reusable:3_3" xmlns:ddi="ddi:instance:3_3">
<Fragment xmlns:r="ddi:reusable:3_3" xmlns="ddi:instance:3_3">
  <Concept isUniversallyUnique="true" versionDate="2026-10-10T22:45:50.9038310Z" xmlns="ddi:conceptualcomponent:3_3">
    <r:URN>urn:ddi:example.org:3aac7990-5b13-5b7d-9c6d-689902a0db6d:1</r:URN>
    <r:Agency>example.org</r:Agency>
    <r:ID>3aac7990-5b13-5b7d-9c6d-689902a0db6d</r:ID>
    <r:Version>1</r:Version>
    <ConceptName>
      <r:String xml:lang="en">AGE</r:String>
    </ConceptName>
    <r:Label>
      <r:Content xml:lang="en">Age</r:Content>
      <r:Content xml:lang="fr">Âge</r:Content>
    </r:Label>
  </Concept>
</Fragment>
<Fragment xmlns:r="ddi:reusable:3_3" xmlns="ddi:instance:3_3">
  <Variable isUniversallyUnique="true" versionDate="2026-10-10T22:45:50.9038310Z" xmlns="ddi:logicalproduct:3_3">
    <r:URN>urn:ddi:example.org:9abf8a2b-db06-5f9e-92ab-f7af91f6afff:1</r:URN>
    <r:Agency>example.org</r:Agency>
    <r:ID>9abf8a2b-db06-5f9e-92ab-f7af91f6afff</r:ID>
    <r:Version>1</r:Version>
    <VariableName>
      <r:String xml:lang="en">AGE</r:String>
    </VariableName>
    <r:Label>
      <r:Content xml:lang="en">Age in years</r:Content>
      <r:Content xml:lang="fr">Âge en années</r:Content>
    </r:Label>
    <r:ConceptReference>
      <r:Agency>example.org</r:Agency>
      <r:ID>3aac7990-5b13-5b7d-9c6d-689902a0db6d</r:ID>
      <r:Version>1</r:Version>
      <r:TypeOfObject>Concept</r:TypeOfObject>
    </r:ConceptReference>
    <VariableRepresentation>
      <r:NumericRepresentation>
        <r:NumericTypeCode>Integer</r:NumericTypeCode>
      </r:NumericRepresentation>
    </VariableRepresentation>
  </Variable>
</Fragment>
</ddi:FragmentInstance>
"""  # noqa: E501 - the service's output, verbatim

EXAMPLE_TABLES_WORKBOOK = Example(
    summary="The example workbook",
    description=(
        "A bilingual labour survey that fills every table. Download it, then "
        "choose it as the file to send."
    ),
    external_value=f"{_DOWNLOADS}ddi-tables-example.xlsx",
)

EXAMPLE_TABLES_ZIP = Example(
    summary="The example as CSV files",
    description="The same tables as a zip of CSV files, one file per table.",
    external_value=f"{_DOWNLOADS}ddi-tables-example.zip",
)

EXAMPLE_TABLES_FRAGMENT = Example(
    summary="One concept and its variable",
    description=(
        "From a zip of three CSV files: `settings.csv` (the agency), "
        "`concepts.csv` (AGE) and `variables.csv` (AGE, a numeric variable "
        "measuring that concept). Written as Colectica Designer writes an "
        "export, so it imports into a Colectica repository."
    ),
    value=SAMPLE_TABLES_FRAGMENT,
)

EXAMPLE_TEMPLATE_WORKBOOK = Example(
    summary="The blank workbook",
    description="One sheet per table and a README sheet listing every column.",
    external_value=f"{_DOWNLOADS}ddi-tables-template.xlsx",
)

EXAMPLE_TEMPLATE_ZIP = Example(
    summary="The blank CSV files",
    description="One CSV file per table, and a README.txt listing every column.",
    external_value=f"{_DOWNLOADS}ddi-tables-template.zip",
)
