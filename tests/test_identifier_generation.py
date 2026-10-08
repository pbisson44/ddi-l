"""Tests covering deterministic identifier generation for maintainables."""

from uuid import uuid5

from ddi_l.constants import DATA_COLLECTION_NS, REUSABLE_NS
from ddi_l.models.datacollection import (
    _REFERENCE_NAMESPACE,
    CollectionEvent,
    DataCollection,
)


def test_serializing_maintainables_generates_deterministic_uuid_ids():
    """Human-readable identifiers are replaced with deterministic UUIDs."""

    event = CollectionEvent(agency="org", identifier="evt", version="1")
    collection = DataCollection(
        agency="org",
        identifier="dc",
        version="1",
        collection_events=[event],
    )

    element = collection.to_xml()

    expected_collection_id = str(uuid5(_REFERENCE_NAMESPACE, "org:dc"))
    expected_event_id = str(uuid5(_REFERENCE_NAMESPACE, "org:evt"))

    collection_id_el = element.find(f"{{{REUSABLE_NS}}}ID")
    assert collection_id_el is not None
    assert collection_id_el.text == expected_collection_id

    event_el = element.find(f"{{{DATA_COLLECTION_NS}}}CollectionEvent")
    assert event_el is not None
    event_id_el = event_el.find(f"{{{REUSABLE_NS}}}ID")
    assert event_id_el is not None
    assert event_id_el.text == expected_event_id

    assert collection._auto_identifier == expected_collection_id
    assert event._auto_identifier == expected_event_id

    reparsed = DataCollection.from_xml(element)
    assert reparsed.identifier == expected_collection_id
    assert reparsed.collection_events[0].identifier == expected_event_id
