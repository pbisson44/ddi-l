"""The documents shown in the OpenAPI schema.

Swagger's "Try it out" prefills its request box from these, so
:data:`SAMPLE_XML` is a small, valid DDI Lifecycle 3.3 instance that passes
schema validation and lint. The JSON and JSON-LD below are the service's own
output for it; ``tests/test_server_examples.py`` checks all three against the
running service.
"""

from __future__ import annotations

from typing import Any

from litestar.openapi.spec import Example

__all__ = [
    "EXAMPLE_JSONLD_GRAPH",
    "EXAMPLE_JSON_DOCUMENT",
    "EXAMPLE_XML_DOCUMENT",
    "SAMPLE_JSON",
    "SAMPLE_JSONLD",
    "SAMPLE_XML",
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
