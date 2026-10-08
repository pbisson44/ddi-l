from pathlib import Path

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import REUSABLE_NS, STUDY_UNIT_NS
from ddi_l.document import DDIFragment
from ddi_l.examples.tests.fixtures.models.regenerate import (
    FIXTURE_DEFAULT_AGENCY,
    _fixture_identifier,
)
from ddi_l.io import read, write
from ddi_l.models import Reference, StudyUnit, qn


def fixture_identifier(seed: str, *, agency: str = FIXTURE_DEFAULT_AGENCY) -> str:
    return _fixture_identifier(seed, agency=agency)


def fixture_urn(
    seed: str,
    *,
    version: str = "1",
    agency: str = FIXTURE_DEFAULT_AGENCY,
) -> str:
    return f"urn:ddi:{agency}:{fixture_identifier(seed, agency=agency)}:{version}"


@pytest.fixture
def minimal_fragment_path(fixtures_dir: Path) -> Path:
    """Provide the path to the minimal fragment XML fixture."""

    return fixtures_dir / "minimal_fragment.xml"


def test_fragment_wrapper_iterates_children(minimal_fragment_path: Path):
    """Fragment wrapper yields fragments and payloads with validation.

    Args:
        minimal_fragment_path: Path to the minimal fragment XML fixture.
    """
    document = read(minimal_fragment_path)
    assert isinstance(document, DDIFragment)

    fragments = list(document.iter_fragments())
    assert len(fragments) == 1
    fragment = fragments[0]
    assert fragment.tag.endswith("Fragment")

    payloads = list(document.iter_fragment_payloads())
    assert len(payloads) == 1
    payload = payloads[0]
    assert payload.tag.endswith("StudyUnit")

    issues = document.validate()
    assert issues == []


def test_fragment_round_trip_preserves_structure(
    minimal_fragment_path: Path, tmp_path: Path
):
    """Round-trip minimal fragment through disk write/read without changes.

    Args:
        minimal_fragment_path: Path to the minimal fragment XML fixture.
        tmp_path: Temporary directory for writing the fragment copy.
    """
    document = read(minimal_fragment_path, validate=True)
    destination = tmp_path / "copy.xml"

    snapshot = document.to_dict()

    write(document, destination)
    reparsed = read(destination, validate=True)
    assert isinstance(reparsed, DDIFragment)

    assert reparsed.to_dict() == snapshot


def test_minimal_fragment_documents_study_metadata(minimal_fragment_path: Path):
    """Minimal fragment fixture records core StudyUnit metadata fields."""

    document = read(minimal_fragment_path, validate=True)
    payloads = list(document.iter_fragment_payloads())  # type: ignore[union-attr]
    assert len(payloads) == 1
    study = StudyUnit.from_xml(payloads[0])

    assert study.identifier == "Census2026"
    assert study.abstracts and study.abstracts[0].text.startswith(
        "Statistics Canada's 2026 Census"
    )

    assert study.citations
    title_container = study.citations[0].find(qn(REUSABLE_NS, "Title"))
    assert title_container is not None
    title_string = title_container.find(qn(REUSABLE_NS, "String"))
    assert title_string is not None
    assert title_string.text == "Census of population - 2026"

    assert study.data_collection_references
    reference = study.data_collection_references[0]
    assert reference.type_of_object == "DataCollection"
    assert reference.agency == "example.agency"

    assert study.other_elements == []


def test_quality_of_life_example_round_trip(tmp_path: Path, fixtures_dir: Path):
    """Round-trip large sample fragment while preserving payload integrity.

    Args:
        tmp_path: Temporary directory for writing the fragment copy.
    """
    source = fixtures_dir.parent.parent / "Quality_of_Life.xml"
    document = read(source, validate=True)
    assert isinstance(document, DDIFragment)

    document.to_xml()
    assert document.validate() == []

    snapshot = document.to_dict()

    destination = tmp_path / "quality_of_life.xml"
    write(document, destination)

    assert document.to_dict() == snapshot

    reparsed = read(destination, validate=True)
    assert isinstance(reparsed, DDIFragment)

    assert reparsed.to_dict() == document.to_dict()


def test_fragment_create_serializes_and_round_trips():
    """Programmatic fragment creation serializes and round-trips cleanly."""
    fragment = DDIFragment.create()
    study = StudyUnit(
        urn=fixture_urn("study-id"),
        agency=FIXTURE_DEFAULT_AGENCY,
        identifier=fixture_identifier("study-id"),
        version="1",
        data_collection_references=[
            Reference(
                agency=FIXTURE_DEFAULT_AGENCY,
                identifier=fixture_identifier("collect"),
                version="1",
                type_of_object="DataCollection",
            )
        ],
    )

    element = fragment.set_top_level_reference(study)
    assert element is not None

    fragment.add_fragment(study)

    xml_data = fragment.to_xml()
    xml_text = (
        xml_data.decode("utf-8")
        if isinstance(xml_data, (bytes, bytearray))
        else xml_data
    )
    assert "<TopLevelReference" in xml_text
    assert "<Fragment" in xml_text

    reference = fragment.get_top_level_reference()
    assert reference is not None
    assert reference.agency == FIXTURE_DEFAULT_AGENCY
    assert reference.identifier == fixture_identifier("study-id")
    assert reference.version == "1"
    assert reference.type_of_object == "StudyUnit"
    assert reference.urn == study.urn

    snapshot = fragment.to_dict()

    xml_bytes = (
        xml_data
        if isinstance(xml_data, (bytes, bytearray))
        else xml_text.encode("utf-8")
    )
    reparsed = read(xml_bytes, validate=True)
    assert isinstance(reparsed, DDIFragment)
    assert reparsed.to_dict() == snapshot


def test_fragment_constructor_sets_reference_from_maintainable():
    """Constructing from maintainable seeds top-level reference and payloads."""
    study = StudyUnit(
        agency="example.agency",
        identifier="demo",
        version="1.0",
        data_collection_references=[
            Reference(
                agency="example.agency",
                identifier="collect",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )

    fragment = DDIFragment.create(study)
    reference = fragment.get_top_level_reference()
    assert reference is not None
    assert reference.agency == "example.agency"
    assert reference.identifier == "demo"
    assert reference.version == "1.0"
    assert reference.type_of_object == "StudyUnit"

    payloads = list(fragment.iter_fragment_payloads())
    assert payloads == []

    fragment.add_fragment(study)
    payloads = list(fragment.iter_fragment_payloads())
    assert len(payloads) == 1
    assert payloads[0].tag == StudyUnit.TAG


def test_fragment_reference_round_trip_with_reference_helper():
    """Reference helper stores, retrieves, and clears top-level references."""
    reference = Reference(
        agency="agency",
        identifier="identifier",
        version="1.0",
        type_of_object="StudyUnit",
    )

    fragment = DDIFragment.create()
    assert fragment.get_top_level_reference() is None

    fragment.set_top_level_reference(reference)
    retrieved = fragment.get_top_level_reference()
    assert retrieved is not None
    assert retrieved.agency == reference.agency
    assert retrieved.identifier == reference.identifier
    assert retrieved.version == reference.version
    assert retrieved.type_of_object == reference.type_of_object
    assert retrieved.urn == "urn:ddi:agency:identifier:1.0"

    fragment.set_top_level_reference(None)
    assert fragment.get_top_level_reference() is None


def test_set_top_level_reference_accepts_reference_and_maintainable():
    """set_top_level_reference accepts maintainable objects or explicit references."""
    fragment = DDIFragment.create()
    study = StudyUnit(
        urn="urn:ddi:example.agency:study:2.0",
        agency="example.agency",
        identifier="study",
        version="2.0",
    )

    element = fragment.set_top_level_reference(study)
    assert element is not None
    maintainable_reference = fragment.get_top_level_reference()
    assert maintainable_reference is not None
    assert maintainable_reference.agency == study.agency
    assert maintainable_reference.identifier == study.identifier
    assert maintainable_reference.version == study.version
    assert maintainable_reference.type_of_object == "StudyUnit"
    assert maintainable_reference.urn == study.urn

    explicit_reference = Reference(
        agency="demo", identifier="other", version="3.1", type_of_object="StudyUnit"
    )
    element = fragment.set_top_level_reference(explicit_reference)
    assert element is not None
    reference_round_trip = fragment.get_top_level_reference()
    assert reference_round_trip is not None
    assert reference_round_trip.agency == "demo"
    assert reference_round_trip.identifier == "other"
    assert reference_round_trip.version == "3.1"
    assert reference_round_trip.type_of_object == "StudyUnit"
    assert reference_round_trip.urn == "urn:ddi:demo:other:3.1"

    fragment.set_top_level_reference(None)
    assert fragment.get_top_level_reference() is None


def test_add_fragment_accepts_iterable_payload():
    """add_fragment accepts iterable payloads and stores elements unchanged."""
    fragment = DDIFragment.create()
    study_element = create_element(StudyUnit.TAG)
    study_element.append(create_element(qn(STUDY_UNIT_NS, "DummyChild")))

    fragment.add_fragment([study_element])

    payloads = list(fragment.iter_fragment_payloads())
    assert len(payloads) == 1
    assert payloads[0] is study_element
