from __future__ import annotations

import pytest

from ddi_l._etree import (
    Element,
    cleanup_namespaces,
    fromstring,
    parse_xml,
    tostring,
)
from ddi_l.constants import (
    DATA_COLLECTION_NS,
    DEFAULT_NSMAP,
    REUSABLE_NS,
    STUDY_UNIT_NS,
)
from ddi_l.models import StudyUnit, qn
from ddi_l.namespace_utils import apply_namespace_map
from tests import PACKAGE_FIXTURES_DIR

FIXTURE_DIR = PACKAGE_FIXTURES_DIR / "models"


def _normalized(element: Element) -> str:
    working = fromstring(tostring(element, pretty_print=True))
    cleanup_namespaces(working, DEFAULT_NSMAP)  # type: ignore[arg-type]
    # ``cleanup_namespaces`` only prunes declarations that are unused; it is
    # not what *binds* one. Establishing ``xmlns="ddi:studyunit:3_3"`` here
    # takes ``apply_namespace_map``, which returns a root because lxml fixes
    # an element's prefix at creation and cannot rebind it in place.
    working = apply_namespace_map(
        working,
        {None: STUDY_UNIT_NS, "d": DATA_COLLECTION_NS, "r": REUSABLE_NS},
        preserve_existing=False,
    )
    return tostring(working, pretty_print=True).strip()


def _identifier(element: Element, path: str) -> str:
    value = element.findtext(path)
    assert value is not None
    return value


@pytest.mark.parametrize(
    "scenario",
    ["nonsurvey_admin", "nonsurvey_sensor"],
)
def test_study_unit_nonsurvey_round_trip(scenario: str) -> None:
    source = parse_xml(FIXTURE_DIR / f"study_unit_{scenario}.xml")
    study = StudyUnit.from_xml(source)

    assert study.data_collections, "Expected inline data collection content"
    data_collection = study.data_collections[0]

    assert len(data_collection.collection_activities) == 1
    assert len(data_collection.observation_plans) == 1
    assert len(data_collection.data_capture_methods) == 1

    activity = data_collection.collection_activities[0]
    plan = data_collection.observation_plans[0]
    method = data_collection.data_capture_methods[0]

    if scenario == "nonsurvey_admin":
        assert activity.names[0].text == "Records import"
        assert activity.activity_types[0].text == "BatchLoad"
        expected_activity_identifier = _identifier(
            source,
            f".//{{{DATA_COLLECTION_NS}}}DataCollection/"
            f"{{{DATA_COLLECTION_NS}}}CollectionActivityReference/{qn(REUSABLE_NS, 'ID')}",
        )
        assert (
            data_collection.collection_activity_references[0].identifier
            == expected_activity_identifier
        )
        assert plan.plan_types[0].text == "Administrative"
        assert plan.observation_units[0].text == "Case"
        expected_plan_scheme_identifier = _identifier(
            source,
            f".//{{{DATA_COLLECTION_NS}}}DataCollection/"
            f"{{{DATA_COLLECTION_NS}}}ObservationPlanSchemeReference/{qn(REUSABLE_NS, 'ID')}",
        )
        assert (
            data_collection.observation_plan_scheme_references[0].identifier
            == expected_plan_scheme_identifier
        )
        assert method.method_types[0].text == "AdministrativeRecords"
        expected_method_scheme_identifier = _identifier(
            source,
            f".//{{{DATA_COLLECTION_NS}}}DataCollection/"
            f"{{{DATA_COLLECTION_NS}}}DataCaptureMethodSchemeReference/{qn(REUSABLE_NS, 'ID')}",
        )
        assert (
            data_collection.data_capture_method_scheme_references[0].identifier
            == expected_method_scheme_identifier
        )
    else:
        assert activity.names[0].text == "Sensor sweep"
        assert activity.activity_types[0].text == "AutomatedPolling"
        expected_activity_identifier = _identifier(
            source,
            f".//{{{DATA_COLLECTION_NS}}}DataCollection/"
            f"{{{DATA_COLLECTION_NS}}}CollectionActivityReference/{qn(REUSABLE_NS, 'ID')}",
        )
        assert (
            data_collection.collection_activity_references[0].identifier
            == expected_activity_identifier
        )
        assert plan.plan_types[0].text == "Sensor"
        assert plan.observation_units[0].text == "Station"
        assert method.method_types[0].text == "SensorFeed"
        expected_method_identifier = _identifier(
            source,
            f".//{{{DATA_COLLECTION_NS}}}DataCollection/"
            f"{{{DATA_COLLECTION_NS}}}DataCaptureMethodReference/{qn(REUSABLE_NS, 'ID')}",
        )
        assert (
            data_collection.data_capture_method_references[0].identifier
            == expected_method_identifier
        )

    serialized = study.to_xml()
    expected = parse_xml(FIXTURE_DIR / f"study_unit_{scenario}.golden.xml")

    assert _normalized(serialized) == _normalized(expected)
