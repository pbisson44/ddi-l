"""Tests for the linting helpers."""

from __future__ import annotations

import pytest

import ddi_l.models as models_module
from ddi_l._etree import create_element
from ddi_l.constants import (
    LOGICAL_PRODUCT_NS,
    REUSABLE_NS,
    STUDY_UNIT_NS,
    XML_NS,
)
from ddi_l.document import DDIDocument
from ddi_l.lint import (
    LintFinding,
    configure_lint,
    register_profile,
    register_rule,
    reset_lint_configuration,
    run_lint,
    run_profile,
)
from ddi_l.models import MaintainableBase
from ddi_l.models._generated.label_slots import (
    SCHEMA_NAMESPACES,
    TAGS_ALLOWING_LABEL,
)
from ddi_l.models.base import InternationalString, qn


def _iter_maintainable_models():
    """Yield every distinct maintainable model class exported by ddi_l.models."""
    seen: set[type] = set()
    for name in dir(models_module):
        candidate = getattr(models_module, name)
        if not isinstance(candidate, type):
            continue
        if not issubclass(candidate, MaintainableBase) or candidate is MaintainableBase:
            continue
        if candidate in seen:
            continue
        seen.add(candidate)
        yield candidate


@pytest.fixture(autouse=True)
def _reset_lint_configuration():
    """Ensure lint configuration changes do not leak between tests."""

    reset_lint_configuration()
    yield
    reset_lint_configuration()


def test_lint_passes_for_valid_document():
    """DDIDocument.lint returns no findings for a compliant document."""
    document = DDIDocument.create(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
        title="Demo document",
    )

    findings = document.lint()

    assert findings == []


def test_lint_reports_unapproved_agency():
    """run_lint flags agency values outside a configured allow-list.

    The allow-list is opt-in: with none configured the rule accepts any agency,
    because the library has no basis to decide which organisation identifiers
    are legitimate. Configure one here to exercise the rule at all.
    """
    configure_lint(allowed_agencies=["example.agency"])
    document = DDIDocument.create(
        agency="invalid.agency",
        identifier="demo-id",
        version="1.0",
    )

    findings = run_lint(document, rules=["ddi.agency.allowed"])

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "ddi.agency.allowed"
    assert finding.severity == "error"
    assert finding.message == "Agency 'invalid.agency' is not an allowed value."
    assert finding.location is not None


def test_lint_reports_missing_citation():
    """Citation presence is enforced by the built-in rules."""

    document = DDIDocument.create(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
    )

    findings = run_lint(document, rules=["ddi.citation.present"])

    assert len(findings) == 1
    assert findings[0].rule_id == "ddi.citation.present"
    assert "missing a <Citation>" in findings[0].message


def test_lint_reports_missing_citation_title():
    """When citation titles are required the rule produces an error."""

    document = DDIDocument.create(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
    )
    document.set_citation()  # Create an empty <Citation> container.

    findings = run_lint(document, rules=["ddi.citation.title.present"])

    assert len(findings) == 1
    assert findings[0].rule_id == "ddi.citation.title.present"
    assert findings[0].severity == "error"


def test_lint_reports_missing_required_title_languages():
    """Configurable language coverage requirements surface targeted warnings."""

    configure_lint(required_citation_languages=("en", "fr"))
    document = DDIDocument.create(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
        title="Demo document",
        title_language="en",
    )

    findings = run_lint(document, rules=["ddi.citation.title.languages"])

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "ddi.citation.title.languages"
    assert finding.severity == "warning"
    assert "'fr'" in finding.message

    citation = document.root.find(qn(REUSABLE_NS, "Citation"))
    assert citation is not None
    translated_title = create_element(qn(REUSABLE_NS, "Title"))
    translated_value = create_element(qn(REUSABLE_NS, "String"))
    translated_value.set(qn(XML_NS, "lang"), "fr")
    translated_value.text = "Démonstration"
    translated_title.append(translated_value)
    citation.append(translated_title)

    findings = run_lint(document, rules=["ddi.citation.title.languages"])

    assert findings == []


@pytest.mark.parametrize(
    ("title_language", "expected"),
    [
        ("en", True),
        ("en-CA", True),
        ("en-GB", True),
        ("EN-ca", True),
        ("en-Latn-CA", True),
        ("eng", False),
        ("fr-CA", False),
    ],
    ids=[
        "exact",
        "canadian-english",
        "british-english",
        "case-insensitive",
        "script-and-region",
        "different-language-sharing-a-prefix",
        "french-only",
    ],
)
def test_required_title_language_matches_regional_variants(title_language, expected):
    """A required ``en`` is satisfied by any English tag, per RFC 4647.

    Exact string matching used to report a bilingual Canadian citation carrying
    ``en-CA`` and ``fr-CA`` as missing English -- flagging the very audience the
    library is built for. Matching has to happen on subtag boundaries, so
    ``en-CA`` satisfies ``en`` while ``eng``, a different language that merely
    starts with the same two letters, still does not.
    """
    configure_lint(required_citation_languages=("en",))
    document = DDIDocument.create(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
        title="Demo document",
        title_language=title_language,
    )

    findings = run_lint(document, rules=["ddi.citation.title.languages"])

    assert (findings == []) is expected


def test_lint_reports_missing_labels_on_maintainables():
    """Lint rule reports maintainables missing label content.

    ``CodeListType`` declares an ``r:Label`` slot, so an unlabelled code list is
    a finding the author can act on. ``StudyUnitType`` has no label slot at all
    and is deliberately not reported.
    """
    document = DDIDocument.create(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
    )
    code_list = create_element(qn(LOGICAL_PRODUCT_NS, "CodeList"))
    for tag, value in (
        ("Agency", "example.agency"),
        ("ID", "code-list-1"),
        ("Version", "1.0"),
    ):
        child = create_element(qn(REUSABLE_NS, tag))
        child.text = value
        code_list.append(child)
    document.root.append(code_list)

    findings = document.lint(rules=["ddi.maintainable.labels"])

    assert len(findings) == 1
    finding = findings[0]
    assert finding.rule_id == "ddi.maintainable.labels"
    assert finding.severity == "warning"
    assert "missing a label" in finding.message


def test_lint_skips_items_the_schema_gives_no_label_slot():
    """Items that cannot carry a Label are never reported as missing one.

    ``l:Code`` is the case that motivated the generated table: it extends
    ``r:IdentifiableType``, so it carries the Agency/ID/Version the rule's
    duck-type matches on, but ``CodeType`` declares no ``r:Label``. Reporting
    it asked the author for an element that cannot validate. ``s:StudyUnit``
    is the same story reached through a registered model.
    """
    document = DDIDocument.create(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
    )
    for namespace, local_name, identifier in (
        (LOGICAL_PRODUCT_NS, "Code", "code-1"),
        (STUDY_UNIT_NS, "StudyUnit", "study-1"),
    ):
        element = create_element(qn(namespace, local_name))
        for tag, value in (
            ("Agency", "example.agency"),
            ("ID", identifier),
            ("Version", "1.0"),
        ):
            child = create_element(qn(REUSABLE_NS, tag))
            child.text = value
            element.append(child)
        document.root.append(element)

    assert document.lint(rules=["ddi.maintainable.labels"]) == []


def test_label_slot_table_agrees_with_generated_element_order():
    """The two sources of schema truth about labels must not diverge.

    ``TAGS_ALLOWING_LABEL`` is keyed by element tag and covers every global
    element; ``_ELEMENT_ORDER`` is keyed by model and covers only the ones we
    generate bases for. Where both speak they are derived from the same XSDs
    and must agree, or the rule's answer depends on whether a model happens to
    be registered.
    """
    label_tag = qn(REUSABLE_NS, "Label")
    compared = 0

    for model in _iter_maintainable_models():
        tag = getattr(model, "TAG", None)
        element_order = getattr(model, "_ELEMENT_ORDER", None)
        if not tag or not element_order:
            continue
        compared += 1
        assert (label_tag in element_order) is (tag in TAGS_ALLOWING_LABEL), (
            f"{model.__name__} ({tag}): _ELEMENT_ORDER and TAGS_ALLOWING_LABEL "
            "disagree about whether the schema allows an r:Label."
        )

    assert compared > 25, f"Expected many models to compare, got {compared}"


def test_allow_labels_agrees_with_the_schema():
    """``ALLOW_LABELS`` is derived from ``TAGS_ALLOWING_LABEL``.

    Scoped to the DDI 3.3 namespaces the table describes. ``MethodologyItem``
    lives in an ddi-l extension namespace, so its own declaration stands.
    """
    compared = 0

    for model in _iter_maintainable_models():
        tag = getattr(model, "TAG", None)
        if not isinstance(tag, str) or not tag:
            continue
        namespace, _, _ = tag[1:].partition("}")
        if namespace not in SCHEMA_NAMESPACES:
            continue
        compared += 1
        assert model.ALLOW_LABELS is (tag in TAGS_ALLOWING_LABEL), (
            f"{model.__name__} ({tag}): ALLOW_LABELS disagrees with the schema."
        )

    assert compared > 25, f"Expected many models to compare, got {compared}"


def test_labels_on_a_slotless_type_warn_instead_of_vanishing():
    """Setting a label where the schema has no slot must not pass in silence.

    Serialization has nowhere valid to put it, so the label is dropped -- but
    dropping a caller's text without saying so is what made this hard to find.
    """
    import warnings

    from ddi_l.models.study import StudyUnit

    study = StudyUnit(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
        labels=[InternationalString(text="My study", lang="en")],
    )
    assert StudyUnit.ALLOW_LABELS is False

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        rendered = study._build_base_element()

    assert rendered.find(qn(REUSABLE_NS, "Label")) is None
    assert any("no r:Label slot on StudyUnit" in str(w.message) for w in caught), (
        f"expected a warning about the dropped label, got {[str(w.message) for w in caught]}"
    )


def test_maintainable_with_label_passes():
    """Maintanable objects with labels satisfy lint rule expectations."""
    document = DDIDocument.create(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
    )
    code_list = create_element(qn(LOGICAL_PRODUCT_NS, "CodeList"))
    for tag, value in (
        ("Agency", "example.agency"),
        ("ID", "code-list-1"),
        ("Version", "1.0"),
    ):
        child = create_element(qn(REUSABLE_NS, tag))
        child.text = value
        code_list.append(child)
    label = create_element(qn(REUSABLE_NS, "Label"))
    label_content = create_element(qn(REUSABLE_NS, "Content"))
    label_content.text = "Demo"
    label.append(label_content)
    code_list.append(label)
    document.root.append(code_list)

    findings = run_lint(document, rules=["ddi.maintainable.labels"])

    assert findings == []


def test_configure_lint_updates_allowed_agencies():
    """configure_lint allows consumers to replace the allowed agency list."""

    configure_lint(allowed_agencies=("custom.agency",))

    document = DDIDocument.create(
        agency="custom.agency",
        identifier="demo-id",
        version="1.0",
    )
    assert run_lint(document, rules=["ddi.agency.allowed"]) == []

    failing_document = DDIDocument.create(
        agency="other.agency",
        identifier="demo-id",
        version="1.0",
    )
    findings = run_lint(failing_document, rules=["ddi.agency.allowed"])

    assert len(findings) == 1
    assert findings[0].rule_id == "ddi.agency.allowed"


def test_configure_lint_can_disable_allowed_agency_list():
    """Passing None disables the allow-list so any agency identifier is accepted."""

    configure_lint(allowed_agencies=None)

    document = DDIDocument.create(
        agency="unexpected.agency",
        identifier="demo-id",
        version="1.0",
    )

    findings = run_lint(document, rules=["ddi.agency.allowed"])

    assert findings == []


def test_run_lint_unknown_rule_errors():
    """run_lint raises KeyError when an unknown rule is requested."""
    document = DDIDocument.create(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
    )

    with pytest.raises(KeyError):
        run_lint(document, rules=["does.not.exist"])


def test_register_profile_requires_known_rules():
    """register_profile rejects profiles containing unknown rules."""
    with pytest.raises(KeyError):
        register_profile("tests.invalid", ["does.not.exist"])


def test_run_profile_combines_schema_and_lint_findings():
    """run_profile aggregates schema issues with custom lint findings."""
    document = DDIDocument.create(
        agency="example.agency",
        identifier="demo-id",
        version="1.0",
        title="Demo document",
    )

    agency_element = document.root.find(qn(REUSABLE_NS, "Agency"))
    assert agency_element is not None
    document.root.remove(agency_element)

    rule_id = "tests.custom.rule"

    def _custom_rule(doc: DDIDocument):
        """Emit a deterministic lint finding for profile aggregation."""
        yield LintFinding(
            rule_id=rule_id, message="Custom rule executed.", severity="info"
        )

    register_rule(rule_id, _custom_rule)
    profile_name = "tests.profile"
    register_profile(profile_name, [rule_id, "ddi.agency.allowed"])

    result = run_profile(document, profile_name)

    assert result.schema_issues
    assert any(
        "Missing required identification element" in issue.message
        for issue in result.schema_issues
    )

    lint_ids = {finding.rule_id for finding in result.lint_findings}
    assert lint_ids == {rule_id, "ddi.agency.allowed"}

    lint_without_schema = run_profile(document, profile_name, include_schema=False)
    assert lint_without_schema.schema_issues == []
    assert lint_without_schema.lint_findings == result.lint_findings


def test_allow_labels_is_left_alone_outside_the_ddi_namespaces():
    """A downstream subclass keeps the label configuration it declares.

    ``TAGS_ALLOWING_LABEL`` is generated from the DDI 3.3 schemas and says
    nothing about anyone else's namespace. Deriving from it unconditionally
    would read "absent from the table" as "the schema forbids it" and switch
    labels off for a subclass carrying its own tag -- including one that opts in
    deliberately. ``MaintainableBase``'s own docstring demonstrates exactly such
    a subclass.
    """

    class Downstream(MaintainableBase):
        TAG = "{http://example.org}Downstream"

    class OptsIn(MaintainableBase):
        TAG = "{http://example.org}OptsIn"
        ALLOW_LABELS = True

    assert Downstream.ALLOW_LABELS is True
    assert OptsIn.ALLOW_LABELS is True

    rendered = OptsIn(
        agency="example.org",
        identifier="d",
        version="1.0",
        labels=[InternationalString(text="Mine", lang="en")],
    )._build_base_element()

    assert rendered.find(qn(REUSABLE_NS, "Label")) is not None
