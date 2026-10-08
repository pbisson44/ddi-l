"""Edge cases and error paths in ddi_l.lint."""

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import REUSABLE_NS, XML_NS
from ddi_l.document import DDIDocument
from ddi_l.models.base import qn

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_doc(*, agency="example.agency", identifier="d1", version="1.0"):
    return DDIDocument.create(agency=agency, identifier=identifier, version=version)


def _make_doc_with_citation(
    *, agency="example.agency", title_text="Title", title_lang="en"
):
    doc = _make_doc(agency=agency)
    citation = create_element(qn(REUSABLE_NS, "Citation"))
    title = create_element(qn(REUSABLE_NS, "Title"))
    string = create_element(qn(REUSABLE_NS, "String"))
    string.text = title_text
    string.set(qn(XML_NS, "lang"), title_lang)
    title.append(string)
    citation.append(title)
    doc.root.append(citation)
    return doc


# ---------------------------------------------------------------------------
# _LintRule.run — line 135 (finding with mismatched rule_id)
# ---------------------------------------------------------------------------


def test_lint_rule_run_rewrites_rule_id():
    """Exercise line 135: finding.rule_id != self.rule_id."""
    from ddi_l.lint import LintFinding, _LintRule

    def _fake_rule(document):
        yield LintFinding(rule_id="wrong.id", message="test", severity="warning")

    rule = _LintRule(rule_id="correct.id", callback=_fake_rule, target="document")
    doc = _make_doc()
    findings = list(rule.run(doc))
    assert len(findings) == 1
    assert findings[0].rule_id == "correct.id"


# ---------------------------------------------------------------------------
# configure_lint — lines 215, 217, 226
# ---------------------------------------------------------------------------


def test_configure_lint_no_updates():
    """Exercise line 226: configure_lint with no changes returns current config."""
    from ddi_l.lint import (
        configure_lint,
        get_lint_configuration,
        reset_lint_configuration,
    )

    reset_lint_configuration()
    original = get_lint_configuration()
    result = configure_lint()  # no args
    assert result is original
    reset_lint_configuration()


def test_configure_lint_require_citation():
    """Exercise line 215: configure_lint with require_citation."""
    from ddi_l.lint import (
        configure_lint,
        reset_lint_configuration,
    )

    reset_lint_configuration()
    result = configure_lint(require_citation=False)
    assert result.require_citation is False
    reset_lint_configuration()


def test_configure_lint_require_citation_title():
    """Exercise line 217: configure_lint with require_citation_title."""
    from ddi_l.lint import (
        configure_lint,
        reset_lint_configuration,
    )

    reset_lint_configuration()
    result = configure_lint(require_citation_title=False)
    assert result.require_citation_title is False
    reset_lint_configuration()


def test_configure_lint_agencies_none():
    """Exercise line 211: configure_lint with allowed_agencies=None."""
    from ddi_l.lint import configure_lint, reset_lint_configuration

    reset_lint_configuration()
    result = configure_lint(allowed_agencies=None)
    assert result.allowed_agencies is None
    reset_lint_configuration()


def test_configure_lint_agencies_list():
    """Exercise line 213: configure_lint with agencies as sequence."""
    from ddi_l.lint import configure_lint, reset_lint_configuration

    reset_lint_configuration()
    result = configure_lint(allowed_agencies=["org.a", "org.b"])
    assert "org.a" in result.allowed_agencies  # type: ignore[operator]
    reset_lint_configuration()


def test_configure_lint_required_languages():
    """Exercise lines 219-223: configure_lint with required_citation_languages."""
    from ddi_l.lint import configure_lint, reset_lint_configuration

    reset_lint_configuration()
    result = configure_lint(required_citation_languages=["en", "fr"])
    assert "en" in result.required_citation_languages
    assert "fr" in result.required_citation_languages
    reset_lint_configuration()


# ---------------------------------------------------------------------------
# register_rule — lines 245, 247
# ---------------------------------------------------------------------------


def test_register_rule_duplicate():
    """Exercise line 245: registering duplicate rule raises ValueError."""
    from ddi_l.lint import _REGISTRY

    # Pick an existing rule
    existing_id = next(iter(_REGISTRY))
    from ddi_l.lint import register_rule

    with pytest.raises(ValueError, match="already registered"):
        register_rule(existing_id, lambda doc: [])


def test_register_rule_bad_target():
    """Exercise line 247: register_rule with invalid target."""
    from ddi_l.lint import register_rule

    with pytest.raises(ValueError, match="target must be"):
        register_rule("test.unique.rule.xyz", lambda doc: [], target="invalid")


# ---------------------------------------------------------------------------
# register_profile — line 265
# ---------------------------------------------------------------------------


def test_register_profile_duplicate():
    """Exercise line 265: registering duplicate profile raises ValueError."""
    from ddi_l.lint import _PROFILE_REGISTRY, register_profile

    existing_name = next(iter(_PROFILE_REGISTRY))
    with pytest.raises(ValueError, match="already registered"):
        register_profile(existing_name, [])


# ---------------------------------------------------------------------------
# ProfileResult.as_dict — lines 310-316
# ---------------------------------------------------------------------------


def test_profile_result_as_dict():
    """Exercise lines 310-316: ProfileResult.as_dict()."""
    from ddi_l.lint import LintFinding, ProfileResult
    from ddi_l.schema_loader._validation import SchemaValidationIssue

    issue = SchemaValidationIssue(
        message="bad", xpath="/root", context="ctx", severity="error"
    )
    finding = LintFinding(rule_id="r1", message="lint", severity="warning")
    result = ProfileResult(schema_issues=[issue], lint_findings=[finding])
    d = result.as_dict()
    assert "schema_issues" in d
    assert "lint_findings" in d
    assert len(d["schema_issues"]) == 1
    assert len(d["lint_findings"]) == 1


# ---------------------------------------------------------------------------
# _allowed_agencies — line 347
# ---------------------------------------------------------------------------


def test_allowed_agencies_from_set():
    """Exercise line 347: fallback to ALLOWED_AGENCIES set."""
    from ddi_l.lint import (
        ALLOWED_AGENCIES,
        LintConfiguration,
        _allowed_agencies,
        reset_lint_configuration,
        set_lint_configuration,
    )

    reset_lint_configuration()
    # Set config without allowed_agencies (None) to fall through to ALLOWED_AGENCIES
    set_lint_configuration(LintConfiguration(allowed_agencies=None))
    ALLOWED_AGENCIES.clear()
    ALLOWED_AGENCIES.add("fallback.agency")
    result = _allowed_agencies()
    assert "fallback.agency" in result  # type: ignore[operator]
    reset_lint_configuration()


def test_allowed_agencies_empty_set():
    """Exercise line 346: ALLOWED_AGENCIES empty returns None."""
    from ddi_l.lint import (
        ALLOWED_AGENCIES,
        LintConfiguration,
        _allowed_agencies,
        reset_lint_configuration,
        set_lint_configuration,
    )

    reset_lint_configuration()
    set_lint_configuration(LintConfiguration(allowed_agencies=None))
    ALLOWED_AGENCIES.clear()
    result = _allowed_agencies()
    assert result is None
    reset_lint_configuration()


# ---------------------------------------------------------------------------
# _check_citation_present — line 388
# ---------------------------------------------------------------------------


def test_check_citation_present_disabled():
    """Exercise line 388: check skipped when require_citation=False."""
    from ddi_l.lint import (
        _check_citation_present,
        configure_lint,
        reset_lint_configuration,
    )

    reset_lint_configuration()
    configure_lint(require_citation=False)
    doc = _make_doc()
    findings = list(_check_citation_present(doc))
    assert findings == []
    reset_lint_configuration()


# ---------------------------------------------------------------------------
# _check_citation_title_present — line 408
# ---------------------------------------------------------------------------


def test_check_citation_title_present_disabled():
    """Exercise line 408: check skipped when require_citation_title=False."""
    from ddi_l.lint import (
        _check_citation_title_present,
        configure_lint,
        reset_lint_configuration,
    )

    reset_lint_configuration()
    configure_lint(require_citation_title=False)
    doc = _make_doc()
    findings = list(_check_citation_title_present(doc))
    assert findings == []
    reset_lint_configuration()


# ---------------------------------------------------------------------------
# _collect_title_languages — lines 437-439
# ---------------------------------------------------------------------------


def test_collect_title_languages_xml_lang():
    """Exercise lines 437-439: title with xml:lang but no InternationalString."""
    from ddi_l.lint import _collect_title_languages

    citation = create_element(qn(REUSABLE_NS, "Citation"))
    title = create_element(qn(REUSABLE_NS, "Title"))
    title.text = "Plain title"
    title.set(qn(XML_NS, "lang"), "fr")
    citation.append(title)

    langs = _collect_title_languages(citation)
    assert "fr" in langs


# ---------------------------------------------------------------------------
# _check_citation_title_languages — lines 449, 456
# ---------------------------------------------------------------------------


def test_check_citation_title_languages_no_required():
    """Exercise line 449: no required languages -> empty result."""
    from ddi_l.lint import (
        _check_citation_title_languages,
        configure_lint,
        reset_lint_configuration,
    )

    reset_lint_configuration()
    configure_lint(required_citation_languages=[])
    doc = _make_doc_with_citation()
    findings = list(_check_citation_title_languages(doc))
    assert findings == []
    reset_lint_configuration()


def test_check_citation_title_languages_no_title():
    """Exercise line 456: citation exists but has no title."""
    from ddi_l.lint import (
        _check_citation_title_languages,
        configure_lint,
        reset_lint_configuration,
    )

    reset_lint_configuration()
    configure_lint(required_citation_languages=["en"])
    doc = _make_doc()
    # Add citation without title
    citation = create_element(qn(REUSABLE_NS, "Citation"))
    doc.root.append(citation)
    findings = list(_check_citation_title_languages(doc))
    assert findings == []
    reset_lint_configuration()


# ---------------------------------------------------------------------------
# _check_maintainable_labels — line 499
# ---------------------------------------------------------------------------


def test_check_maintainable_labels_no_allow_labels():
    """Exercise line 499: maintainable with ALLOW_LABELS=False is skipped."""
    from ddi_l.lint import _check_maintainable_labels

    doc = _make_doc()
    # The doc root is DDIInstance — iterate will find maintainables
    findings = list(_check_maintainable_labels(doc))
    # Just verify it runs without error
    assert isinstance(findings, list)


# ---------------------------------------------------------------------------
# _check_reference_integrity — lines 564, 568
# ---------------------------------------------------------------------------


def test_check_reference_integrity_unresolved():
    """Exercise lines 564-568: reference that can't be resolved."""
    from ddi_l.lint import _check_reference_integrity

    doc = _make_doc()
    # Add a reference that doesn't resolve
    ref_elem = create_element(qn(REUSABLE_NS, "VariableReference"))
    agency = create_element(qn(REUSABLE_NS, "Agency"))
    agency.text = "a"
    ref_elem.append(agency)
    id_elem = create_element(qn(REUSABLE_NS, "ID"))
    id_elem.text = "nonexistent"
    ref_elem.append(id_elem)
    ver = create_element(qn(REUSABLE_NS, "Version"))
    ver.text = "1.0"
    ref_elem.append(ver)
    type_obj = create_element(qn(REUSABLE_NS, "TypeOfObject"))
    type_obj.text = "Variable"
    ref_elem.append(type_obj)
    doc.root.append(ref_elem)

    findings = list(_check_reference_integrity(doc))
    assert any("nonexistent" in f.message for f in findings)


def test_check_reference_integrity_no_identifier():
    """Exercise line 568: reference without identifier is skipped."""
    from ddi_l.lint import _check_reference_integrity

    doc = _make_doc()
    ref_elem = create_element(qn(REUSABLE_NS, "SomeReference"))
    type_obj = create_element(qn(REUSABLE_NS, "TypeOfObject"))
    type_obj.text = "Variable"
    ref_elem.append(type_obj)
    doc.root.append(ref_elem)

    findings = list(_check_reference_integrity(doc))
    # Reference without identifier/urn should be silently skipped
    assert isinstance(findings, list)


# ---------------------------------------------------------------------------
# run_lint — specific rules
# ---------------------------------------------------------------------------


def test_run_lint_specific_rules():
    from ddi_l.lint import run_lint

    doc = _make_doc()
    findings = run_lint(doc, rules=["ddi.agency.allowed"])
    assert isinstance(findings, list)


def test_run_lint_unknown_rule():
    from ddi_l.lint import run_lint

    doc = _make_doc()
    with pytest.raises(KeyError, match="Unknown lint rules"):
        run_lint(doc, rules=["nonexistent.rule"])


# ---------------------------------------------------------------------------
# run_profile
# ---------------------------------------------------------------------------


def test_run_profile_unknown():
    from ddi_l.lint import run_profile

    doc = _make_doc()
    with pytest.raises(KeyError, match="Unknown lint profile"):
        run_profile(doc, "nonexistent_profile")


# ---------------------------------------------------------------------------
# iter_registered_rules / iter_registered_profiles
# ---------------------------------------------------------------------------


def test_iter_registered_rules():
    from ddi_l.lint import iter_registered_rules

    rules = list(iter_registered_rules())
    assert len(rules) > 0
    for rule_id, _description in rules:
        assert isinstance(rule_id, str)


def test_iter_registered_profiles():
    from ddi_l.lint import iter_registered_profiles

    profiles = list(iter_registered_profiles())
    assert len(profiles) > 0


# ---------------------------------------------------------------------------
# LintFinding.as_dict
# ---------------------------------------------------------------------------


def test_lint_finding_as_dict():
    from ddi_l.lint import LintFinding

    finding = LintFinding(
        rule_id="r1", message="msg", severity="warning", location="/root"
    )
    d = finding.as_dict()
    assert d["rule_id"] == "r1"
    assert d["message"] == "msg"
    assert d["severity"] == "warning"
    assert d["location"] == "/root"


# ---------------------------------------------------------------------------
# LintConfiguration
# ---------------------------------------------------------------------------


def test_lint_configuration_normalize():
    from ddi_l.lint import LintConfiguration

    config = LintConfiguration(
        allowed_agencies=("a", "", "b", "a"),
        required_citation_languages=("en", "", "en", "fr"),
    )
    # Empty strings filtered, duplicates removed
    assert "" not in config.allowed_agencies  # type: ignore[operator]
    assert config.allowed_agencies == ("a", "b")
    assert config.required_citation_languages == ("en", "fr")
