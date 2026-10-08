"""Model objects returned by the Document facade stay attached to it."""

from __future__ import annotations

import threading

import pytest

import ddi_l as ddi
from ddi_l.exceptions import DDIModelError, DuplicateIdentifierError
from ddi_l.models.base import (
    InternationalString,
    should_validate_on_serialize,
    suppress_serialize_validation,
)
from ddi_l.models.study import StudyUnit


def _study() -> ddi.Document:
    return ddi.new_study(title="Handles", agency="example.org")


@pytest.mark.parametrize(
    "trigger",
    [
        "to_xml",
        "validate",
        "groups",
        "ddi_profiles",
        "comparisons",
        "resource_packages",
        "local_holding_packages",
        "translation_information",
    ],
)
def test_held_variable_survives_flush(trigger: str) -> None:
    doc = _study()
    variable = doc.add_variable(name="age")
    attribute = getattr(doc, trigger)
    if callable(attribute):
        attribute()

    variable.labels.append(InternationalString(text="Age in years", lang="en"))

    assert "Age in years" in doc.to_xml()
    assert doc.variables[0] is variable


def test_held_variable_survives_save(tmp_path) -> None:
    doc = _study()
    variable = doc.add_variable(name="age")
    doc.save(tmp_path / "first.xml")

    variable.labels.append(InternationalString(text="Age label", lang="en"))
    doc.save(tmp_path / "second.xml")

    assert "Age label" in (tmp_path / "second.xml").read_text(encoding="utf-8")


def test_study_unit_handle_is_live_after_validate() -> None:
    doc = _study()
    study = doc.study_unit
    doc.validate()
    assert doc.study_unit is study


def test_held_variable_survives_add_group() -> None:
    doc = _study()
    variable = doc.add_variable(name="age")
    doc.add_group()

    variable.labels.append(InternationalString(text="Grouped label", lang="en"))

    assert "Grouped label" in doc.to_xml()


def test_inner_hands_over_the_xml_tree() -> None:
    doc = _study()
    doc.add_variable(name="age")
    inner = doc.inner
    assert inner is doc.inner
    assert [v.names[0].text for v in doc.variables] == ["age"]


def test_find_and_remove_reach_non_primary_studies() -> None:
    doc = _study()
    wave2 = doc.add_study(title="Wave 2")
    income = doc.study(wave2.identifier).add_variable(name="income")

    assert doc.find(income.identifier) is income
    assert doc.remove(income.identifier) is True
    assert doc.find(income.identifier) is None
    assert "income" not in doc.to_xml()


def test_a_reopened_series_tracks_every_study(tmp_path) -> None:
    doc = _study()
    wave2 = doc.add_study(title="Wave 2")
    income = doc.study(wave2.identifier).add_variable(name="income")
    path = tmp_path / "series.xml"
    doc.save(path)

    reopened = ddi.open_ddi(path)
    found = reopened.find(income.identifier)
    assert found is not None
    assert reopened.study(wave2.identifier).study_unit.identifier == wave2.identifier
    with pytest.raises(DuplicateIdentifierError):
        reopened.add_variable(name="copy", identifier=income.identifier)

    found.names[0] = InternationalString("household_income")
    reopened.save(path)
    xml = path.read_text(encoding="utf-8")
    assert xml.count("<s:StudyUnit") == 2
    assert "household_income" in xml


def test_find_and_remove_reach_items_outside_the_registry() -> None:
    doc = _study()
    dataset = doc.add_dataset(name="Responses")
    cube = doc.add_ncube(name="Cube")

    assert doc.find(dataset.identifier) is dataset
    assert doc.find(cube.identifier) is cube
    assert doc.remove(dataset.identifier) is True
    assert doc.find(dataset.identifier) is None


def test_find_returns_items_not_references() -> None:
    doc = _study()
    question = doc.add_question(text="How old are you?")
    doc.add_variable(name="age", question=question)
    assert doc.find(question.identifier) is question


def test_duplicate_identifier_is_rejected() -> None:
    doc = _study()
    doc.add_variable(name="a", identifier="shared")
    with pytest.raises(DuplicateIdentifierError):
        doc.add_variable(name="b", identifier="shared")
    with pytest.raises(DuplicateIdentifierError):
        doc.add_question(text="Q?", identifier="shared")


def test_duplicate_identifier_error_is_a_value_error() -> None:
    assert issubclass(DuplicateIdentifierError, ValueError)
    assert issubclass(DuplicateIdentifierError, DDIModelError)


@pytest.mark.parametrize(
    ("call", "error"),
    [
        (lambda doc: doc.add_variable(name=123), TypeError),
        (lambda doc: doc.add_variable(name=""), ValueError),
        (lambda doc: doc.add_question(text="   "), ValueError),
        (lambda doc: doc.add_study(title=""), ValueError),
        (lambda doc: doc.add_variable(name="x", identifier=""), ValueError),
    ],
)
def test_invalid_input_fails_at_the_call(call, error) -> None:
    with pytest.raises(error):
        call(_study())


def test_new_study_rejects_empty_title() -> None:
    with pytest.raises(ValueError):
        ddi.new_study(title="", agency="example.org")


def test_write_ddi_accepts_a_document() -> None:
    doc = _study()
    doc.add_variable(name="age")
    payload = ddi.write_ddi(doc)
    assert payload.startswith(b"<?xml")
    assert b"age" in payload


def test_document_rejects_earlier_ddi_versions(fixtures_dir) -> None:
    with pytest.raises(DDIModelError, match="3.3"):
        ddi.open_ddi(fixtures_dir / "minimal_instance_3_2.xml")


def test_serialize_validation_suppression_is_thread_local() -> None:
    study = StudyUnit(agency="example.org", identifier="s", version="1")
    seen: list[bool] = []
    inside = threading.Event()
    release = threading.Event()

    def suppressed() -> None:
        with suppress_serialize_validation():
            inside.set()
            release.wait(timeout=5)

    worker = threading.Thread(target=suppressed)
    worker.start()
    inside.wait(timeout=5)
    seen.append(should_validate_on_serialize(study))
    release.set()
    worker.join()

    assert seen == [True]
    with suppress_serialize_validation():
        assert should_validate_on_serialize(study) is False
    assert should_validate_on_serialize(study) is True


def _document_with_dangling_reference() -> ddi.Document:
    doc = _study()
    question = doc.add_question(text="Removed later?")
    doc.add_variable(name="age", question=question)
    doc.remove(question.identifier)
    return doc


def test_to_xml_does_not_check_references() -> None:
    import warnings

    doc = _document_with_dangling_reference()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        doc.to_xml()


def test_save_warns_once_about_dangling_references(tmp_path) -> None:
    from ddi_l.exceptions import DDIReferenceWarning

    doc = _document_with_dangling_reference()
    with pytest.warns(DDIReferenceWarning) as record:
        doc.save(tmp_path / "study.xml")

    assert len(record) == 1
    assert record[0].filename == __file__
    warning = record[0].message
    assert isinstance(warning, DDIReferenceWarning)
    assert len(warning.records) == 1
