"""Regression coverage for datacollection models using real-world fragments."""

from __future__ import annotations

from ddi_l._etree import Element, parse_xml
from ddi_l.constants import DATA_COLLECTION_NS
from ddi_l.models import Instrument, Sequence
from tests import TEST_FIXTURES_DIR

EXAMPLE_PATH = TEST_FIXTURES_DIR / "Canadian_Survey_on_Business_conditions.xml"


def test_instrument_and_sequence_round_trip_from_example() -> None:
    """Ensure new datacollection fields survive a to_xml/from_xml round-trip."""

    root: Element = parse_xml(EXAMPLE_PATH)

    instrument_element = root.find(f".//{{{DATA_COLLECTION_NS}}}Instrument")
    assert instrument_element is not None
    instrument = Instrument.from_xml(instrument_element)

    # Sanity-check the parsed fields reflect the sample content.
    assert instrument.user_ids, "expected UserID entries to be parsed"
    assert instrument.user_attribute_pairs, (
        "expected UserAttributePair entries to be parsed"
    )
    assert instrument.version_responsibility is not None
    assert instrument.version_rationales
    assert instrument.control_construct_reference is not None

    instrument_round_tripped = Instrument.from_xml(instrument.to_xml())

    assert instrument_round_tripped.user_ids == instrument.user_ids
    assert (
        instrument_round_tripped.user_attribute_pairs == instrument.user_attribute_pairs
    )
    assert (
        instrument_round_tripped.version_responsibility
        == instrument.version_responsibility
    )
    assert instrument_round_tripped.version_rationales == instrument.version_rationales
    ref_rt = instrument_round_tripped.control_construct_reference
    ref_orig = instrument.control_construct_reference
    assert ref_rt is not None and ref_orig is not None
    assert (
        ref_rt.agency,
        ref_rt.identifier,
        ref_rt.version,
        ref_rt.type_of_object,
    ) == (
        ref_orig.agency,
        ref_orig.identifier,
        ref_orig.version,
        ref_orig.type_of_object,
    )

    sequence_element = root.find(f".//{{{DATA_COLLECTION_NS}}}Sequence")
    assert sequence_element is not None
    sequence = Sequence.from_xml(sequence_element)

    assert sequence.control_construct_references
    assert sequence.construct_sequence is not None
    assert sequence.construct_sequence.item_sequence_type is not None

    sequence_round_tripped = Sequence.from_xml(sequence.to_xml())

    assert [
        (
            reference.agency,
            reference.identifier,
            reference.version,
            reference.type_of_object,
        )
        for reference in sequence_round_tripped.control_construct_references
    ] == [
        (
            reference.agency,
            reference.identifier,
            reference.version,
            reference.type_of_object,
        )
        for reference in sequence.control_construct_references
    ]
    assert sequence_round_tripped.type_of_sequence == sequence.type_of_sequence
    assert sequence_round_tripped.bindings == sequence.bindings
    assert sequence_round_tripped.construct_sequence is not None
    assert (
        sequence_round_tripped.construct_sequence.item_sequence_type
        == sequence.construct_sequence.item_sequence_type
    )
