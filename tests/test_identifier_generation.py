"""Tests covering deterministic identifier generation for maintainables."""

from uuid import uuid5

import pytest

from ddi_l.constants import DATA_COLLECTION_NS, REUSABLE_NS
from ddi_l.exceptions import ModelValidationError
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


def test_generated_ids_shared_across_item_types_are_rejected():
    """Two item types with the same agency:identifier would get one UUID."""

    event = CollectionEvent(agency="org", identifier="main", version="1")
    collection = DataCollection(
        agency="org",
        identifier="main",
        version="1",
        collection_events=[event],
    )

    with pytest.raises(ModelValidationError, match="'org:main'"):
        collection.to_xml()


def test_generated_ids_shared_across_versions_of_one_type_are_allowed():
    """Versions of one item share their identifier, so they share the UUID."""

    first = CollectionEvent(agency="org", identifier="evt", version="1")
    second = CollectionEvent(agency="org", identifier="evt", version="2")
    collection = DataCollection(
        agency="org",
        identifier="dc",
        version="1",
        collection_events=[first, second],
    )

    collection.to_xml()

    assert first._auto_identifier == second._auto_identifier


def test_generated_id_matching_an_item_read_back_is_rejected():
    """An item read back keeps its UUID; a new item must not be given it."""

    written = DataCollection(
        agency="org",
        identifier="main",
        version="1",
        collection_events=[
            CollectionEvent(agency="org", identifier="evt", version="1")
        ],
    )
    collection = DataCollection.from_xml(written.to_xml())
    collection.collection_events.append(
        CollectionEvent(agency="org", identifier="main", version="1")
    )

    with pytest.raises(ModelValidationError, match="'org:main'"):
        collection.to_xml()


def test_identifiers_the_items_already_have_are_written_as_given():
    """Only generated identifiers are checked; explicit ones are not rewritten."""

    shared = "550e8400-e29b-41d4-a716-446655440000"
    collection = DataCollection(
        agency="org",
        identifier=shared,
        version="1",
        collection_events=[
            CollectionEvent(agency="org", identifier=shared, version="1")
        ],
    )

    element = collection.to_xml()

    collection_id_el = element.find(f"{{{REUSABLE_NS}}}ID")
    assert collection_id_el is not None
    assert collection_id_el.text == shared
