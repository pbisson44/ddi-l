from pathlib import Path

import pytest

from ddi_l import open_ddi, validation
from ddi_l.document import DDIDocument, DDIFragment
from ddi_l.exceptions import DDIValidationError, ModelValidationError
from ddi_l.lint import DDI_PROFILE_DEFAULT, LintFinding
from ddi_l.models import (
    CollectionEvent,
    DataCollection,
    InternationalString,
    StudyUnit,
)
from ddi_l.schema_loader import SchemaValidationError, SchemaValidationIssue


@pytest.fixture(scope="module")
def validation_fixtures(fixtures_dir: Path) -> Path:
    """Directory containing validation-related XML fixtures."""

    return fixtures_dir


def _build_data_collection(*, labeled: bool = True) -> DataCollection:
    """Build a DataCollection, optionally without a label.

    ``ddi.maintainable.labels`` only reports types the XSD gives an ``r:Label``
    slot, and ``StudyUnitType`` has none -- so an unlabelled DataCollection is
    what these tests need to produce a finding.
    """
    return DataCollection(
        agency="example.agency",
        identifier="collect",
        version="1.0",
        labels=[InternationalString(text="Collection")] if labeled else [],
        collection_events=[
            CollectionEvent(
                agency="example.agency",
                identifier="collect-event",
                version="1.0",
                labels=[InternationalString(text="Event label")],
            )
        ],
    )


def _build_document_with_unlabeled_collection() -> DDIDocument:
    document = DDIDocument.create(
        agency="example.agency",
        identifier="doc",
        version="1.0",
        title="Demo",
    )
    study = StudyUnit(
        agency="example.agency",
        identifier="SU",
        version="1.0",
        data_collections=[_build_data_collection(labeled=False)],
    )
    document.add_study_unit(study)
    return document


@pytest.mark.parametrize(
    "lint_options",
    (
        pytest.param({"lint_rules": ("ddi.maintainable.labels",)}, id="rules"),
        pytest.param({"lint_profile": DDI_PROFILE_DEFAULT}, id="profile"),
    ),
)
def test_validate_document_surfaces_lint_findings(
    validation_fixtures: Path, lint_options: dict
):
    """validate_document surfaces lint findings for rules and profiles."""

    # Baseline document is fully valid and produces no messages.
    baseline = validation.validate_document(
        validation_fixtures / "minimal_instance.xml", include_lint=False
    )
    assert not baseline.schema_issues
    assert not baseline.has_errors()

    document = _build_document_with_unlabeled_collection()

    report = validation.validate_document(document, **lint_options)
    assert not report.has_errors()
    assert report.has_warnings()
    lint_rule_ids = {finding.rule_id for finding in report.lint_findings}
    assert "ddi.maintainable.labels" in lint_rule_ids
    assert any(message.source == "lint" for message in report.messages())


def test_validation_report_severity_checks_after_iteration(monkeypatch) -> None:
    """Severity helpers inspect issues directly without rewrapping messages."""

    issue = SchemaValidationIssue(
        message="Example error",
        xpath="/Example",
        context=None,
        severity="error",
    )
    finding = LintFinding(
        rule_id="lint.example",
        message="Example warning",
        severity="warning",
    )
    report = validation.ValidationReport(
        schema_issues=[issue],
        lint_findings=[finding],
    )

    schema_calls = 0
    lint_calls = 0

    original_schema = validation.ValidationMessage.from_schema_issue.__func__  # type: ignore[attr-defined]
    original_lint = validation.ValidationMessage.from_lint_finding.__func__  # type: ignore[attr-defined]

    def counting_schema(cls, schema_issue):
        nonlocal schema_calls
        schema_calls += 1
        return original_schema(cls, schema_issue)

    def counting_lint(cls, lint_finding):
        nonlocal lint_calls
        lint_calls += 1
        return original_lint(cls, lint_finding)

    monkeypatch.setattr(
        validation.ValidationMessage, "from_schema_issue", classmethod(counting_schema)
    )
    monkeypatch.setattr(
        validation.ValidationMessage, "from_lint_finding", classmethod(counting_lint)
    )

    messages = list(report.iter_messages())
    assert len(messages) == 2
    assert schema_calls == 1
    assert lint_calls == 1

    assert report.has_errors()
    assert report.has_warnings()

    # Severity helpers should not trigger additional materialization on repeated access.
    assert schema_calls == 1
    assert lint_calls == 1
    assert report.has_errors()
    assert report.has_warnings()


def test_validation_message_locations_include_line_column_and_xpath() -> None:
    issue = SchemaValidationIssue(
        message="Schema error",
        xpath="/Example",
        context=None,
        severity="error",
        line=12,
        column=7,
    )

    message = validation.ValidationMessage.from_schema_issue(issue)

    assert message.location is not None
    assert "line 12, column 7" in message.location
    assert "/Example" in message.location


def test_validation_message_location_keeps_xpath_reference() -> None:
    issue = SchemaValidationIssue(
        message="Schema warning",
        xpath="/Other/Path",
        context=None,
        severity="warning",
        line=3,
        column=14,
    )

    message = validation.ValidationMessage.from_schema_issue(issue)

    assert message.location is not None
    assert "line 3, column 14" in message.location
    assert "/Other/Path" in message.location


def test_validate_maintainable_reports_schema_errors():
    """validate_maintainable wraps the payload in a fragment and validates it."""

    valid = StudyUnit(
        agency="example.agency",
        identifier="SU",
        version="1.0",
        data_collections=[_build_data_collection()],
    )
    assert not validation.validate_maintainable(valid).schema_issues

    broken = StudyUnit(
        agency="example.agency",
        data_collections=[_build_data_collection()],
    )  # Missing identifier/version metadata.
    with pytest.raises(ModelValidationError, match="requires identifier, version"):
        validation.validate_maintainable(broken)


def test_validate_fragment_surfaces_lint_findings():
    """Fragment validation reuses lint pipeline for maintainable payloads."""

    fragment = DDIFragment.create()
    study = StudyUnit(
        agency="example.agency",
        identifier="SU",
        version="1.0",
        data_collections=[_build_data_collection(labeled=False)],
    )
    fragment.add_fragment(study)

    report = validation.validate_fragment(
        fragment, lint_rules=("ddi.maintainable.labels",)
    )
    assert any(
        finding.rule_id == "ddi.maintainable.labels" for finding in report.lint_findings
    )

    profile_report = validation.validate_fragment(
        fragment, lint_profile=DDI_PROFILE_DEFAULT
    )
    assert any(
        finding.rule_id == "ddi.maintainable.labels"
        for finding in profile_report.lint_findings
    )

    no_lint = validation.validate_fragment(fragment, include_lint=False)
    assert no_lint.lint_findings == []


def test_validate_maintainable_surfaces_lint_findings_with_profiles():
    """Maintainable validation can execute lint profiles for granular edits."""

    study = StudyUnit(
        agency="example.agency",
        identifier="SU",
        version="1.0",
        data_collections=[_build_data_collection(labeled=False)],
    )
    report = validation.validate_maintainable(study, lint_profile=DDI_PROFILE_DEFAULT)

    assert any(
        finding.rule_id == "ddi.maintainable.labels" for finding in report.lint_findings
    )

    # Labelling the DataCollection clears it. The StudyUnit itself stays
    # unlabelled on purpose: the schema gives StudyUnitType no r:Label slot, so
    # adding one would make the fragment invalid rather than cleaner.
    labeled_study = StudyUnit(
        agency="example.agency",
        identifier="SU",
        version="1.0",
        data_collections=[_build_data_collection()],
    )
    clean_report = validation.validate_maintainable(
        labeled_study, lint_profile=DDI_PROFILE_DEFAULT
    )
    assert clean_report.lint_findings == []


def test_validate_document_raise_error_provides_context(
    validation_fixtures: Path,
) -> None:
    """validate_document raises DDIValidationError with filename + XPath details."""

    source = validation_fixtures / "invalid_instance_missing_id.xml"
    with pytest.raises(DDIValidationError) as excinfo:
        validation.validate_document(source, include_lint=False, raise_error=True)

    error = excinfo.value
    assert error.issues
    assert error.issues[0].xpath == "/DDIInstance"
    assert error.location is not None
    assert error.location.filename == str(source)
    assert error.location.xpath == "/DDIInstance"


def test_document_validate_raise_error_wraps_schema_error(
    validation_fixtures: Path,
) -> None:
    """DDIDocument.validate raises DDIValidationError with XPath hints."""

    source = validation_fixtures / "invalid_instance_missing_id.xml"
    document = DDIDocument.from_xml(source)

    with pytest.raises(DDIValidationError) as excinfo:
        document.validate(raise_error=True)

    error = excinfo.value
    assert error.issues
    assert error.location is not None
    assert error.location.xpath == "/DDIInstance"
    assert error.location.filename is None


def test_validate_document_can_redact_context(validation_fixtures: Path) -> None:
    """Validation helpers omit contextual snippets when requested."""

    source = validation_fixtures / "invalid_instance_missing_id.xml"
    report = validation.validate_document(
        source,
        include_lint=False,
        include_context=False,
    )

    assert report.schema_issues
    assert all(issue.context is None for issue in report.schema_issues)

    payload = report.to_dict(include_context=False)
    assert "context" not in payload["schema_issues"][0]
    assert "context" not in payload["messages"][0]


def test_schema_validation_error_is_a_ddi_validation_error(tmp_path: Path) -> None:
    """The umbrella exception the docs name must actually catch schema failures.

    ``open_ddi(..., validate=True)`` raises ``SchemaValidationError``, which
    ``except DDIValidationError`` (as the docs recommend) must catch.
    """
    bad = tmp_path / "bad.xml"
    bad.write_text('<DDIInstance xmlns="ddi:instance:3_3"><NotAThing/></DDIInstance>')

    assert issubclass(SchemaValidationError, DDIValidationError)

    with pytest.raises(DDIValidationError) as umbrella:
        open_ddi(bad, validate=True)
    assert umbrella.value.issues

    with pytest.raises(SchemaValidationError) as concrete:
        open_ddi(bad, validate=True)
    assert concrete.value.issues
    # The rendered message must not gain a location suffix from the base class.
    assert str(concrete.value) == concrete.value.issues[0].message or str(
        concrete.value
    ).startswith(concrete.value.issues[0].message)
