"""The checked-in schema IR is what the compiler makes from the bundled schemas.

Regenerate it with ``uv run python -m codegen.schema_ir`` after changing a
schema or upgrading xmlschema.
"""

from __future__ import annotations

import gzip
import json

import pytest
from codegen.schema_ir import ir_path

from ddi_l._schema_versions import SUPPORTED_SCHEMA_VERSIONS
from ddi_l.schema_loader._cache import get_schema
from ddi_l.schema_loader._ir import UnsupportedSchemaError, build


@pytest.mark.parametrize("version", SUPPORTED_SCHEMA_VERSIONS)
def test_the_checked_in_ir_is_current(version: str) -> None:
    shipped = json.loads(gzip.decompress(ir_path(version).read_bytes()))
    assert build(get_schema(version)).data == shipped


def test_the_ir_is_numbered_the_same_each_time() -> None:
    schema = get_schema("3.3")
    first, second = build(schema), build(schema)
    assert first.data["digest"] == second.data["digest"]
    assert first.element_objects == second.element_objects


def test_a_choice_repeated_as_optional_items_is_one_automaton() -> None:
    """``(a? | b?){1,2}`` is ambiguous as written but has one deterministic DFA."""
    import xmlschema

    schema = xmlschema.XMLSchema(
        """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
          <xs:element name="r"><xs:complexType>
            <xs:choice minOccurs="1" maxOccurs="2">
              <xs:element name="a" minOccurs="0"/>
              <xs:element name="b" minOccurs="0"/>
            </xs:choice>
          </xs:complexType></xs:element>
        </xs:schema>"""
    )
    ir = build(schema)
    element = ir.elements[ir.roots[ir.name("r")]]
    model = ir.models[ir.complex[element["type"][1]]["model"]]
    start = model["states"][0]
    assert start["accept"]
    assert len(start["edges"]) == 2


def test_an_all_group_is_refused() -> None:
    import xmlschema

    schema = xmlschema.XMLSchema(
        """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
          <xs:element name="r"><xs:complexType>
            <xs:all><xs:element name="a"/></xs:all>
          </xs:complexType></xs:element>
        </xs:schema>"""
    )
    with pytest.raises(UnsupportedSchemaError, match="'all'"):
        build(schema)
