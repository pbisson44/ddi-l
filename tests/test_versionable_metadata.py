"""Regression tests for reusable versionable metadata helpers."""

from ddi_l._etree import create_element
from ddi_l.constants import REUSABLE_NS
from ddi_l.models import Instrument, Reference, qn


def test_versionable_metadata_round_trip() -> None:
    based_on_ref = Reference(
        agency="based.agency",
        identifier="instrument-base",
        version="1",
        type_of_object="Instrument",
    )
    based_on_object = create_element(qn(REUSABLE_NS, "BasedOnObject"))
    based_on_object.append(based_on_ref.to_xml("BasedOnReference"))

    instrument = Instrument(
        agency="agency.example",
        identifier="instrument",
        version="1",
        based_on_object=based_on_object,
    )

    element = instrument.to_xml()

    based_on_nodes = element.findall(qn(REUSABLE_NS, "BasedOnObject"))
    assert len(based_on_nodes) == 1
    based_on_node = based_on_nodes[0]
    ref_el = based_on_node.find(qn(REUSABLE_NS, "BasedOnReference"))
    assert ref_el is not None
    based_on_round_trip = Reference.from_xml(ref_el)
    assert based_on_round_trip.agency == "based.agency"
    assert based_on_round_trip.identifier == "instrument-base"
    assert based_on_round_trip.version == "1"

    parsed = Instrument.from_xml(element)
    assert parsed.based_on_object is not None
    parsed_ref_el = parsed.based_on_object.find(qn(REUSABLE_NS, "BasedOnReference"))
    assert parsed_ref_el is not None
    parsed_ref = Reference.from_xml(parsed_ref_el)
    assert parsed_ref.agency == "based.agency"
    assert parsed_ref.identifier == "instrument-base"
    assert parsed_ref.version == "1"

    round_tripped_element = parsed.to_xml()
    rt_based_on = round_tripped_element.find(qn(REUSABLE_NS, "BasedOnObject"))
    assert rt_based_on is not None
    rt_ref_el = rt_based_on.find(qn(REUSABLE_NS, "BasedOnReference"))
    assert rt_ref_el is not None

    rt_ref = Reference.from_xml(rt_ref_el)
    assert rt_ref.agency == "based.agency"
    assert rt_ref.identifier == "instrument-base"
    assert rt_ref.version == "1"

    assert round_tripped_element.tag == Instrument.TAG
    assert parsed.TAG == Instrument.TAG
