from __future__ import annotations

from copy import deepcopy
from typing import Any, cast

from ddi_l._etree import (
    cleanup_namespaces,
    fromstring,
    parse_xml,
    tostring,
)
from ddi_l.constants import (
    DATA_COLLECTION_NS,
    DEFAULT_NSMAP,
    GROUP_NS,
    REUSABLE_NS,
    STUDY_UNIT_NS,
)
from ddi_l.models import (
    DataCollection,
    Group,
    Reference,
    ResourcePackage,
    StudyUnit,
    clone_element,
)
from ddi_l.namespace_utils import apply_namespace_map
from tests import EXAMPLES_DIR

EXAMPLE_PATH = EXAMPLES_DIR / "Quality_of_Life.xml"


def _normalize(element, model=None):
    working = fromstring(tostring(element, pretty_print=True))
    cleanup_namespaces(working, DEFAULT_NSMAP)  # type: ignore[arg-type]
    working = fromstring(tostring(working, pretty_print=True))

    nsmap = dict(DEFAULT_NSMAP)
    if model and model.NSMAP:
        nsmap.update({prefix: uri for prefix, uri in model.NSMAP.items() if prefix})
    # ``cleanup_namespaces`` prunes unused declarations; binding the map is
    # ``apply_namespace_map``'s job, and it must be the one used here or the
    # two backends disagree on the root element's prefix.
    working = apply_namespace_map(working, nsmap, preserve_existing=False)

    return tostring(working, pretty_print=True).strip()


_MAINTAINABLE_ATTRS = {
    "isMaintainable",
    "isUniversallyUnique",
    "isVersionable",
    "versionDate",
    "versionNumber",
}


def _strip_metadata(element):
    for node in element.iter():
        for attr in list(node.attrib):
            if attr in _MAINTAINABLE_ATTRS:
                del node.attrib[attr]


def test_quality_of_life_data_collection_round_trip() -> None:
    root = cast(Any, parse_xml(EXAMPLE_PATH))
    element = root.find(f".//{{{DATA_COLLECTION_NS}}}DataCollection")
    assert element is not None

    instance = DataCollection.from_xml(element)

    assert instance.user_ids
    assert instance.version_responsibility is not None
    assert instance.version_rationales
    assert instance.coverage
    assert instance.collection_events
    assert instance.instrument_references
    assert instance.processing_event_scheme_references

    coverage_nodes = element.findall(f"./{{{REUSABLE_NS}}}Coverage")
    assert len(coverage_nodes) == len(instance.coverage)
    for expected_coverage, parsed_coverage in zip(
        coverage_nodes, instance.coverage, strict=False
    ):
        expected_clone = deepcopy(expected_coverage)
        parsed_clone = clone_element(parsed_coverage)
        _strip_metadata(expected_clone)
        _strip_metadata(parsed_clone)
        assert _normalize(parsed_clone) == _normalize(expected_clone)

    event_nodes = element.findall(f"./{{{DATA_COLLECTION_NS}}}CollectionEvent")
    assert len(event_nodes) == len(instance.collection_events)
    for expected_event, parsed_event in zip(
        event_nodes, instance.collection_events, strict=False
    ):
        expected_clone = deepcopy(expected_event)
        parsed_clone = parsed_event.to_xml()
        _strip_metadata(expected_clone)
        _strip_metadata(parsed_clone)
        assert _normalize(parsed_clone, DataCollection) == _normalize(
            expected_clone, DataCollection
        )

    instrument_nodes = element.findall(f"./{{{DATA_COLLECTION_NS}}}InstrumentReference")
    assert [
        (ref.urn, ref.agency, ref.identifier, ref.version, ref.type_of_object)
        for ref in instance.instrument_references
    ] == [
        (
            Reference.from_xml(node).urn,
            Reference.from_xml(node).agency,
            Reference.from_xml(node).identifier,
            Reference.from_xml(node).version,
            Reference.from_xml(node).type_of_object,
        )
        for node in instrument_nodes
    ]

    processing_nodes = element.findall(
        f"./{{{DATA_COLLECTION_NS}}}ProcessingEventSchemeReference"
    )
    assert [
        (ref.urn, ref.agency, ref.identifier, ref.version, ref.type_of_object)
        for ref in instance.processing_event_scheme_references
    ] == [
        (
            Reference.from_xml(node).urn,
            Reference.from_xml(node).agency,
            Reference.from_xml(node).identifier,
            Reference.from_xml(node).version,
            Reference.from_xml(node).type_of_object,
        )
        for node in processing_nodes
    ]


def test_quality_of_life_study_unit_round_trip() -> None:
    root = cast(Any, parse_xml(EXAMPLE_PATH))
    element = root.find(f".//{{{STUDY_UNIT_NS}}}StudyUnit")
    assert element is not None

    instance = StudyUnit.from_xml(element)

    assert instance.user_ids
    assert instance.version_responsibility is not None
    assert instance.version_rationales
    assert instance.citations
    assert instance.abstracts
    assert instance.funding_information
    assert instance.purposes
    assert instance.coverage
    assert instance.required_resource_packages
    assert instance.data_collection_references
    assert instance.physical_instance_references
    assert instance.universe_references

    funding_nodes = element.findall(f"./{{{REUSABLE_NS}}}FundingInformation")
    assert len(funding_nodes) == len(instance.funding_information)
    for expected_funding, parsed_funding in zip(
        funding_nodes, instance.funding_information, strict=False
    ):
        expected_clone = deepcopy(expected_funding)
        parsed_clone = clone_element(parsed_funding)
        _strip_metadata(expected_clone)
        _strip_metadata(parsed_clone)
        assert _normalize(parsed_clone) == _normalize(expected_clone)

    coverage_nodes = element.findall(f"./{{{REUSABLE_NS}}}Coverage")
    assert len(coverage_nodes) == len(instance.coverage)
    for expected_coverage, parsed_coverage in zip(
        coverage_nodes, instance.coverage, strict=False
    ):
        expected_clone = deepcopy(expected_coverage)
        parsed_clone = clone_element(parsed_coverage)
        _strip_metadata(expected_clone)
        _strip_metadata(parsed_clone)
        assert _normalize(parsed_clone) == _normalize(expected_clone)

    required_nodes = element.findall(f"./{{{REUSABLE_NS}}}RequiredResourcePackages")
    assert len(required_nodes) == len(instance.required_resource_packages)
    for expected_required, parsed_required in zip(
        required_nodes, instance.required_resource_packages, strict=False
    ):
        expected_clone = deepcopy(expected_required)
        parsed_clone = clone_element(parsed_required)
        _strip_metadata(expected_clone)
        _strip_metadata(parsed_clone)
        assert _normalize(parsed_clone) == _normalize(expected_clone)

    def _reference_tuple(ref: Reference) -> tuple[str | None, ...]:
        return (ref.urn, ref.agency, ref.identifier, ref.version, ref.type_of_object)

    data_collection_nodes = element.findall(
        f"./{{{REUSABLE_NS}}}DataCollectionReference"
    )
    assert [_reference_tuple(ref) for ref in instance.data_collection_references] == [
        _reference_tuple(Reference.from_xml(node)) for node in data_collection_nodes
    ]

    physical_nodes = element.findall(f"./{{{REUSABLE_NS}}}PhysicalInstanceReference")
    assert [_reference_tuple(ref) for ref in instance.physical_instance_references] == [
        _reference_tuple(Reference.from_xml(node)) for node in physical_nodes
    ]

    universe_nodes = element.findall(f"./{{{REUSABLE_NS}}}UniverseReference")
    assert [_reference_tuple(ref) for ref in instance.universe_references] == [
        _reference_tuple(Reference.from_xml(node)) for node in universe_nodes
    ]


def test_quality_of_life_group_round_trip() -> None:
    root = cast(Any, parse_xml(EXAMPLE_PATH))
    element = root.find(f".//{{{GROUP_NS}}}Group")
    assert element is not None

    instance = Group.from_xml(element)

    assert instance.citation is not None
    assert instance.funding_informations
    assert instance.coverage is not None


def test_quality_of_life_resource_package_round_trip() -> None:
    root = cast(Any, parse_xml(EXAMPLE_PATH))
    element = root.find(f".//{{{GROUP_NS}}}ResourcePackage")
    assert element is not None

    instance = ResourcePackage.from_xml(element)

    assert instance.citation is not None
