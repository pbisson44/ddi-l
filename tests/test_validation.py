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
from tests import SAMPLES_DIR


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
        SAMPLES_DIR / "minimal_instance.xml", include_lint=False
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

    source = SAMPLES_DIR / "invalid_instance_missing_id.xml"
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

    source = SAMPLES_DIR / "invalid_instance_missing_id.xml"
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

    source = SAMPLES_DIR / "invalid_instance_missing_id.xml"
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


# The tests below pin what the validation API passes on and reports; each
# fails if a field, a flag or an option is dropped on the way.


def test_validation_message_to_dict_lists_every_field() -> None:
    message = validation.ValidationMessage(
        message="m",
        severity="warning",
        source="lint",
        xpath="/x",
        context="c",
        location="l",
        rule_id="r",
    )

    assert message.to_dict() == {
        "message": "m",
        "severity": "warning",
        "source": "lint",
        "xpath": "/x",
        "context": "c",
        "location": "l",
        "rule_id": "r",
    }


def test_validation_message_from_lint_finding_copies_every_field() -> None:
    finding = LintFinding(
        rule_id="ddi.maintainable.labels",
        message="No label.",
        severity="warning",
        location="/DDIInstance/StudyUnit",
    )

    message = validation.ValidationMessage.from_lint_finding(finding)

    assert message == validation.ValidationMessage(
        message="No label.",
        severity="warning",
        source="lint",
        location="/DDIInstance/StudyUnit",
        rule_id="ddi.maintainable.labels",
    )


def test_validation_message_from_schema_issue_without_a_location() -> None:
    issue = SchemaValidationIssue(
        message="Schema error", xpath=None, context="ctx", severity="error"
    )

    message = validation.ValidationMessage.from_schema_issue(issue)

    assert message == validation.ValidationMessage(
        message="Schema error",
        severity="error",
        source="schema",
        xpath=None,
        context="ctx",
        location=None,
    )


@pytest.mark.parametrize(
    ("schema_severity", "lint_severity", "expected"),
    [
        (None, None, (False, False)),
        (None, "warning", (False, True)),
        (None, "error", (True, False)),
        ("warning", None, (False, True)),
        ("error", "warning", (True, True)),
        ("ERROR", None, (True, False)),
        ("info", "info", (False, False)),
    ],
)
def test_validation_report_severity_flags(
    schema_severity: str | None, lint_severity: str | None, expected: tuple
) -> None:
    schema_issues = (
        [
            SchemaValidationIssue(
                message="s", xpath=None, context=None, severity=schema_severity
            )
        ]
        if schema_severity
        else []
    )
    lint_findings = (
        [LintFinding(rule_id="r", message="l", severity=lint_severity)]
        if lint_severity
        else []
    )

    report = validation.ValidationReport(
        schema_issues=schema_issues, lint_findings=lint_findings
    )

    assert (report.has_errors(), report.has_warnings()) == expected


def test_validation_report_to_dict_keeps_context_by_default() -> None:
    issue = SchemaValidationIssue(message="s", xpath="/x", context="ctx")
    finding = LintFinding(rule_id="r", message="l", severity="warning")
    report = validation.ValidationReport(schema_issues=[issue], lint_findings=[finding])

    payload = report.to_dict()

    assert payload["schema_issues"] == [issue.to_dict(include_context=True)]
    assert payload["lint_findings"] == [finding.as_dict()]
    assert [message["source"] for message in payload["messages"]] == ["schema", "lint"]
    assert payload["messages"][0]["context"] == "ctx"


def test_validate_document_and_fragment_keep_context_by_default() -> None:
    source = SAMPLES_DIR / "invalid_instance_missing_id.xml"

    report = validation.validate_document(source, include_lint=False)
    assert report.schema_issues
    assert report.schema_issues[0].context

    fragment = DDIFragment.create()
    fragment.add_fragment(
        StudyUnit(
            agency="example.agency",
            identifier="SU",
            version="1.0",
            data_collections=[_build_data_collection()],
        )
    )
    element = fragment.to_etree()
    version = element.find(".//{ddi:reusable:3_3}Version")
    assert version is not None
    version.text = "not a version"
    fragment_report = validation.validate_fragment(element, include_lint=False)
    assert fragment_report.schema_issues
    assert fragment_report.schema_issues[0].context


def test_validate_maintainable_passes_lint_options_on() -> None:
    study = StudyUnit(
        agency="example.agency",
        identifier="SU",
        version="1.0",
        data_collections=[_build_data_collection(labeled=False)],
    )

    by_rule = validation.validate_maintainable(
        study, lint_rules=("ddi.citation.present",)
    )
    assert by_rule.lint_findings == []

    from ddi_l.lint import register_profile

    register_profile("test.citation-only", ["ddi.citation.present"])
    by_profile = validation.validate_maintainable(
        study, lint_profile="test.citation-only"
    )
    assert by_profile.lint_findings == []

    assert (
        validation.validate_maintainable(study, include_lint=False).lint_findings == []
    )


def test_validate_rejects_an_unsupported_source_by_kind() -> None:
    with pytest.raises(TypeError, match="Unsupported document source type"):
        validation.validate_document(42)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="Unsupported fragment source type"):
        validation.validate_fragment(42)  # type: ignore[arg-type]


def _schema_invalid_study() -> StudyUnit:
    """A study the models accept and the schema rejects (a bad language tag)."""
    collection = _build_data_collection()
    collection.labels = [InternationalString(text="Collection", lang="fr_CA")]
    return StudyUnit(
        agency="example.agency",
        identifier="SU",
        version="1.0",
        data_collections=[collection],
    )


def test_validate_maintainable_passes_schema_options_on() -> None:
    study = _schema_invalid_study()

    report = validation.validate_maintainable(study, include_lint=False)
    assert report.schema_issues
    assert report.schema_issues[0].context

    redacted = validation.validate_maintainable(
        study, include_lint=False, include_context=False
    )
    assert redacted.schema_issues[0].context is None

    with pytest.raises(DDIValidationError):
        validation.validate_maintainable(study, include_lint=False, raise_error=True)


def test_validate_fragment_raises_when_asked() -> None:
    fragment = DDIFragment.create()
    fragment.add_fragment(_schema_invalid_study())

    assert validation.validate_fragment(fragment, include_lint=False).schema_issues
    with pytest.raises(DDIValidationError):
        validation.validate_fragment(fragment, include_lint=False, raise_error=True)


def test_validate_document_and_fragment_pass_the_version_on() -> None:
    source = SAMPLES_DIR / "minimal_instance.xml"
    assert not validation.validate_document(source, include_lint=False).schema_issues
    # Against 3.2, the 3.3 namespace is not the instance namespace.
    assert validation.validate_document(
        source, include_lint=False, version="3.2"
    ).schema_issues

    fragment = DDIFragment.create()
    fragment.add_fragment(
        StudyUnit(
            agency="example.agency",
            identifier="SU",
            version="1.0",
            data_collections=[_build_data_collection()],
        )
    )
    assert not validation.validate_fragment(fragment, include_lint=False).schema_issues
    assert validation.validate_fragment(
        fragment, include_lint=False, version="3.2"
    ).schema_issues


def test_validate_document_passes_lint_options_on() -> None:
    document = _build_document_with_unlabeled_collection()

    by_rule = validation.validate_document(
        document, lint_rules=("ddi.citation.present",)
    )
    assert by_rule.lint_findings == []

    from ddi_l.lint import register_profile

    register_profile("test.citation-only", ["ddi.citation.present"])
    by_profile = validation.validate_document(
        document, lint_profile="test.citation-only"
    )
    assert by_profile.lint_findings == []


def test_validate_document_accepts_a_document() -> None:
    import ddi_l as ddi

    doc = ddi.new_study(title="T", agency="example.org")
    doc.add_question(text="Q?")

    assert not validation.validate_document(doc, include_lint=False).schema_issues


def test_validation_message_from_schema_issue_keeps_the_xpath() -> None:
    issue = SchemaValidationIssue(message="s", xpath="/x", context=None)

    assert validation.ValidationMessage.from_schema_issue(issue).xpath == "/x"


def test_validation_report_reads_every_issue_for_severity() -> None:
    # Both severities in one list: stopping at the first would miss the second.
    def issue(severity: str) -> SchemaValidationIssue:
        return SchemaValidationIssue(
            message="s", xpath=None, context=None, severity=severity
        )

    def finding(severity: str) -> LintFinding:
        return LintFinding(rule_id="r", message="l", severity=severity)

    both_schema = validation.ValidationReport(
        schema_issues=[issue("warning"), issue("error")], lint_findings=[]
    )
    assert (both_schema.has_errors(), both_schema.has_warnings()) == (True, True)

    both_lint = validation.ValidationReport(
        schema_issues=[], lint_findings=[finding("error"), finding("warning")]
    )
    assert (both_lint.has_errors(), both_lint.has_warnings()) == (True, True)

    first_in_schema = validation.ValidationReport(
        schema_issues=[issue("error"), issue("warning")],
        lint_findings=[finding("warning")],
    )
    assert (first_in_schema.has_errors(), first_in_schema.has_warnings()) == (
        True,
        True,
    )


def test_unsupported_source_error_names_the_type() -> None:
    with pytest.raises(TypeError, match="'int'"):
        validation.validate_document(42)  # type: ignore[arg-type]


def test_validate_fragment_error_names_the_file(tmp_path: Path) -> None:
    fragment = DDIFragment.create()
    fragment.add_fragment(_schema_invalid_study())
    path = tmp_path / "fragment.xml"
    path.write_text(fragment.to_xml(), encoding="utf-8")

    with pytest.raises(DDIValidationError) as excinfo:
        validation.validate_fragment(path, include_lint=False, raise_error=True)

    error = excinfo.value
    assert error.issues
    assert error.location is not None
    assert error.location.filename == str(path)
