"""Guardrails for model-layer coverage and round-trip fidelity.

These turn the "nothing is lost" claim into checked assertions:

- every XSD complex type has a generated dataclass, and
- the generic engine preserves unrecognized child elements *and* attributes
  verbatim through a from_xml -> to_xml cycle.
"""

from __future__ import annotations

from codegen.coverage_audit import attribute_drop_set, audit

from ddi_l._etree import tostring
from ddi_l.models.group import ResourcePackage


def test_every_xsd_complex_type_has_a_generated_class():
    """Type coverage must stay at 100% (508/508 today)."""
    result = audit()
    assert result["missing_class"] == []
    assert result["modeled_types"] == result["total_types"]


def test_no_hand_written_wrapper_drops_unknown_attributes():
    """Every hand-written wrapper preserves unknown attributes on round-trip."""
    assert attribute_drop_set() == []


def test_generic_engine_preserves_unknown_children_and_attributes():
    """Unmapped attributes and children survive a round-trip via passthrough."""
    package = ResourcePackage(agency="ex.org", identifier="RP1", version="1")
    element = package.to_xml()
    # An attribute with no _ATTR_XML_MAP entry, and a child with no field.
    element.set("externalReferenceDefaultURI", "http://example.org/base")
    element.set("isMaintainable", "true")
    from ddi_l._etree import create_element

    unknown_child = create_element("{ddi:reusable:3_3}SomeFutureElement")
    unknown_child.text = "keepme"
    element.append(unknown_child)

    restored = ResourcePackage.from_xml(element)
    assert restored.other_attributes["externalReferenceDefaultURI"] == (
        "http://example.org/base"
    )
    assert restored.other_attributes["isMaintainable"] == "true"

    serialized = tostring(restored.to_xml())
    text = serialized.decode() if isinstance(serialized, bytes) else serialized
    assert 'externalReferenceDefaultURI="http://example.org/base"' in text
    assert 'isMaintainable="true"' in text
    assert "SomeFutureElement" in text
    assert "keepme" in text


def test_field_coverage_stays_high():
    """Named child-field coverage should not regress below the current level."""
    result = audit()
    # Child elements: nearly all are named fields; the rest round-trip via
    # other_elements. Guard against a large regression.
    coverage = result["named_child_slots"] / result["total_child_slots"]
    assert coverage > 0.98
