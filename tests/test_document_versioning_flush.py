"""The documented versioning workflow: open, bump the version, save.

A version bump changes the study's identity, so ``Document`` must replace the
element it loaded rather than look the study up again. The remaining tests
cover APIs the docs call with the objects they have in hand.
"""

from __future__ import annotations

import pytest

import ddi_l as ddi
from ddi_l.document import DDIDocument
from ddi_l.exceptions import DDIModelError
from ddi_l.validation import validate_document


def _study_unit_count(path) -> int:
    return path.read_text(encoding="utf-8").count("<s:StudyUnit")


def test_version_bump_before_first_save_does_not_duplicate_the_study(tmp_path):
    """The workflow module 13 teaches, on a document that was never saved."""
    doc = ddi.new_study(title="Survey", agency="example.org")
    doc.study_unit.version = "1.0.0"
    doc.study_unit.increment_minor_version()

    target = tmp_path / "out.xml"
    doc.save(target)

    assert _study_unit_count(target) == 1
    assert ddi.open_ddi(target).study_unit.version == "1.1.0"


def test_version_bump_after_reopening_does_not_duplicate_the_study(tmp_path):
    """The same workflow starting from a file on disk, which is the documented one."""
    first = tmp_path / "v1.xml"
    original = ddi.new_study(title="Survey", agency="example.org")
    original.add_question(text="How old are you?")
    original.save(first)

    reopened = ddi.open_ddi(first)
    reopened.study_unit.increment_minor_version()
    second = tmp_path / "v2.xml"
    reopened.save(second)

    assert _study_unit_count(second) == 1
    result = ddi.open_ddi(second)
    assert result.study_unit.version == "1.1"
    assert len(result.questions) == 1, "the bump must not drop content"


def test_a_version_rationale_is_schema_valid_and_round_trips(tmp_path):
    """RationaleDescription takes r:String; the InternationalString default,
    r:Content, made every documented rationale fail ``doc.validate()``."""
    from ddi_l.models.base import InternationalString, VersionRationale

    doc = ddi.new_study(title="Survey", agency="example.org")
    question = doc.add_question(text="Do you work from home?")
    for item in (doc.study_unit, question):
        item.increment_minor_version()
        item.version_rationales.append(
            VersionRationale(
                descriptions=[InternationalString(text="Reworded", lang="en")]
            )
        )

    assert doc.validate() == []

    target = tmp_path / "rationale.xml"
    doc.save(target)
    reopened = ddi.open_ddi(target)
    for item in (reopened.study_unit, reopened.questions[0]):
        (rationale,) = item.version_rationales
        assert [(d.text, d.lang) for d in rationale.descriptions] == [
            ("Reworded", "en")
        ]


def test_a_labelled_question_with_version_metadata_is_schema_valid():
    """VersionableType's children precede r:Label; emitting the label first made
    a reworded, labelled question fail ``doc.validate()``."""
    from ddi_l.models.base import InternationalString, VersionRationale

    doc = ddi.new_study(title="Survey", agency="example.org")
    question = doc.add_question(text="Do you work from home?", label="WFH")
    question.version_responsibility = "Survey Design Team"
    question.version_rationales.append(
        VersionRationale(descriptions=[InternationalString(text="Reworded")])
    )

    assert doc.validate() == []


def test_version_bump_inside_a_group_does_not_duplicate_the_study(tmp_path):
    """A grouped study takes a different flush branch, so it is asserted separately."""
    doc = ddi.new_study(title="Survey", agency="example.org")
    doc.add_group()
    doc.study_unit.increment_major_version()

    target = tmp_path / "grouped.xml"
    doc.save(target)

    assert _study_unit_count(target) == 1
    assert ddi.open_ddi(target).study_unit.version == "2"


def test_a_multi_study_series_keeps_every_study_across_a_bump(tmp_path):
    """Extra studies in a series survive a version bump of the primary."""
    doc = ddi.new_study(title="Wave 1", agency="example.org")
    doc.add_study(title="Wave 2")
    doc.study_unit.increment_minor_version()

    target = tmp_path / "series.xml"
    doc.save(target)

    assert _study_unit_count(target) == 2


def test_study_unit_is_reachable_without_a_private_method():
    """The curriculum reached the StudyUnit through ``_get_study()`` in 21 places.

    Publishing that as the documented route would make an underscore-prefixed
    method part of the public API by accident, so there is a public accessor.
    """
    doc = ddi.new_study(title="Survey", agency="example.org")

    assert doc.study_unit is doc._get_study()

    doc.study_unit.set_property("myorg:reviewed", "yes")
    assert doc.study_unit.properties["myorg:reviewed"] == "yes"


def test_study_unit_reports_a_document_with_no_study():
    document = DDIDocument.create(agency="example.org", identifier="d", version="1.0")

    with pytest.raises(DDIModelError, match="no StudyUnit"):
        _ = ddi.document.Document(document).study_unit


def test_validate_document_accepts_the_type_the_docs_hand_it():
    """``docs/validation.en.md`` calls ``validate_document(doc)``.

    ``doc`` there is a ``Document``, as returned by ``new_study()`` and
    ``open_ddi()``.
    """
    doc = ddi.new_study(title="Test", agency="example.org")
    doc.add_question(text="How old are you?")

    report = validate_document(doc)

    assert report.schema_issues == []
    assert isinstance(report.lint_findings, list)


def test_validate_document_sees_unflushed_edits():
    """Coercion goes through ``.inner``, which flushes, so pending edits count."""
    doc = ddi.new_study(title="Test", agency="example.org")
    doc.add_question(text="Is this counted?")

    report = validate_document(doc)

    assert report.to_dict()["schema_issues"] == []


def test_a_mistyped_filename_reports_the_missing_file(tmp_path):
    """``from_xml`` reports a missing file as ``FileNotFoundError``.

    A string that looks like a filename is never well-formed XML, so falling
    through to the text parser could only ever produce a misleading error.
    """
    with pytest.raises(FileNotFoundError):
        DDIDocument.from_xml("no-such-study.xml")

    with pytest.raises(FileNotFoundError):
        DDIDocument.from_xml(tmp_path / "also-missing.xml")


def test_raw_xml_text_is_still_parsed_as_xml():
    """The strictness must not capture genuine XML payloads."""
    document = DDIDocument.from_xml(
        '<DDIInstance xmlns="ddi:instance:3_3">'
        '<r:Agency xmlns:r="ddi:reusable:3_3">example.org</r:Agency>'
        "</DDIInstance>"
    )

    assert document.root.tag == "{ddi:instance:3_3}DDIInstance"


def test_an_existing_path_is_still_parsed_as_a_path(tmp_path):
    source = tmp_path / "real.xml"
    ddi.new_study(title="Survey", agency="example.org").save(source)

    assert DDIDocument.from_xml(source).root.tag == "{ddi:instance:3_3}DDIInstance"
    assert DDIDocument.from_xml(str(source)).root.tag == "{ddi:instance:3_3}DDIInstance"
