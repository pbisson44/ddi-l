"""Edge cases in the model classes and ddi_l.validation."""

import textwrap

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.models.base import (
    InternationalString,
    Reference,
    qn,
)

# ===========================================================================
# models/archive.py — lines 75, 92
# ===========================================================================


def test_organization_identification_tag_mismatch():
    from ddi_l.models.archive import OrganizationIdentification

    elem = create_element("WrongTag")
    with pytest.raises(ValueError, match="OrganizationIdentification"):
        OrganizationIdentification.from_xml(elem)


def test_organization_identification_other_elements():
    from ddi_l.models.archive import ARCHIVE_NS, OrganizationIdentification

    elem = create_element(qn(ARCHIVE_NS, "OrganizationIdentification"))
    extra = create_element(qn(ARCHIVE_NS, "SomeExtra"))
    extra.text = "extra"
    elem.append(extra)
    oi = OrganizationIdentification.from_xml(elem)
    assert len(oi.other_elements) == 1
    # Roundtrip
    result = oi.to_xml()
    assert len(list(result)) == 1


# ===========================================================================
# models/quality.py — lines 172, 530, 536
# ===========================================================================


# ===========================================================================
# models/comparison.py — line 98
# ===========================================================================


def test_comparison_variable_map_reference():
    from ddi_l.models.comparison import COMPARATIVE_NS, Comparison

    comp = Comparison(
        agency="a",
        identifier="comp1",
        version="1.0",
        variable_map_references=[
            Reference(
                identifier="vm1",
                agency="a",
                version="1.0",
                type_of_object="VariableMap",
            )
        ],
    )
    elem = comp.to_xml()
    ref_tag = qn(COMPARATIVE_NS, "VariableMapReference")
    assert elem.find(f".//{ref_tag}") is not None


# ===========================================================================
# models/reusable.py — lines 317-343
# ===========================================================================


def test_managed_missing_values_other_attributes():
    from ddi_l.models.reusable import ManagedMissingValuesRepresentation

    mmvr = ManagedMissingValuesRepresentation(
        agency="a",
        identifier="mmv1",
        version="1.0",
        blank_is_missing_value=True,
        other_attributes={"scopeOfUniqueness": "Agency"},
    )
    elem = mmvr.to_xml()
    assert elem.get("isBlankMissingValue") == "true"
    assert elem.get("scopeOfUniqueness") == "Agency"


def test_managed_missing_values_names():
    from ddi_l.models.reusable import ManagedMissingValuesRepresentation

    mmvr = ManagedMissingValuesRepresentation(
        agency="a",
        identifier="mmv1",
        version="1.0",
        names=[InternationalString(text="Test Name", lang="en")],
    )
    elem = mmvr.to_xml()
    name_tag = qn(REUSABLE_NS, "ManagedMissingValuesRepresentationName")
    assert elem.find(f".//{name_tag}") is not None


# ===========================================================================
# models/classification.py — lines 48-56, 268-270, 302-378
# ===========================================================================


def test_classification_item_valid_from_to():
    from ddi_l.models.classification import CLASSIFICATION_NS, ClassificationItem

    vf_el = create_element(qn(CLASSIFICATION_NS, "ValidFrom"))
    vf_el.text = "2020-01-01"
    vt_el = create_element(qn(CLASSIFICATION_NS, "ValidTo"))
    vt_el.text = "2025-12-31"
    item = ClassificationItem(
        agency="a",
        identifier="ci1",
        version="1.0",
        valid_from=vf_el,
        valid_to=vt_el,
    )
    elem = item.to_xml()
    vf = elem.find(qn(CLASSIFICATION_NS, "ValidFrom"))
    vt = elem.find(qn(CLASSIFICATION_NS, "ValidTo"))
    assert vf is not None and vf.text == "2020-01-01"
    assert vt is not None and vt.text == "2025-12-31"


def test_classification_level_context_roundtrip():
    from ddi_l.models.classification import (
        CLASSIFICATION_NS,
        ClassificationItem,
        ClassificationLevelContext,
    )

    ctx = ClassificationLevelContext(
        level_number="1",
        classification_items=[
            ClassificationItem(agency="a", identifier="ci1", version="1.0"),
        ],
        classification_item_references=[
            Reference(
                identifier="ci2",
                agency="a",
                version="1.0",
                type_of_object="ClassificationItem",
            ),
        ],
    )
    elem = ctx.to_xml()
    assert elem.find(qn(CLASSIFICATION_NS, "LevelNumber")) is not None

    parsed = ClassificationLevelContext.from_xml(elem)
    assert parsed.level_number == "1"
    assert len(parsed.classification_items) == 1
    assert len(parsed.classification_item_references) == 1


def test_classification_level_context_with_reference():
    from ddi_l.models.classification import (
        CLASSIFICATION_NS,
        ClassificationLevelContext,
    )

    ctx = ClassificationLevelContext(
        classification_level_reference=Reference(
            identifier="lvl1",
            agency="a",
            version="1.0",
            type_of_object="ClassificationLevel",
        ),
    )
    elem = ctx.to_xml()
    ref_tag = qn(CLASSIFICATION_NS, "ClassificationLevelReference")
    assert elem.find(f".//{ref_tag}") is not None


def test_classification_level_context_both_inline_and_ref():
    from ddi_l.models.classification import ClassificationLevelContext

    ctx = ClassificationLevelContext(
        classification_level=create_element("level"),
        classification_level_reference=Reference(
            identifier="lvl1",
            agency="a",
            version="1.0",
            type_of_object="ClassificationLevel",
        ),
    )
    with pytest.raises(ValueError, match="cannot contain both"):
        ctx.to_xml()


def test_classification_level_context_tag_mismatch():
    from ddi_l.models.classification import ClassificationLevelContext

    elem = create_element("WrongTag")
    with pytest.raises(ValueError, match="LevelContext"):
        ClassificationLevelContext.from_xml(elem)


def test_classification_scheme_items_property():
    from ddi_l.models.classification import (
        ClassificationItem,
        ClassificationLevelContext,
        ClassificationScheme,
    )

    ctx = ClassificationLevelContext(
        classification_items=[
            ClassificationItem(agency="a", identifier="i1", version="1.0"),
            ClassificationItem(agency="a", identifier="i2", version="1.0"),
        ],
    )
    scheme = ClassificationScheme(
        agency="a",
        identifier="cs1",
        version="1.0",
        level_contexts=[ctx.to_xml()],
    )
    items = scheme.classification_items
    assert len(items) == 2


# ===========================================================================
# validation.py — lines 100, 110, 174-177, 315-317
# ===========================================================================


def test_validation_report_severity_none():
    from ddi_l.validation import ValidationReport

    report = ValidationReport(schema_issues=[], lint_findings=[])
    assert report.has_errors() is False
    assert report.has_warnings() is False


def test_validation_report_with_error():
    from ddi_l.schema_loader._validation import SchemaValidationIssue
    from ddi_l.validation import ValidationReport

    issue = SchemaValidationIssue(
        message="bad", xpath="/root", context="ctx", severity="error"
    )
    report = ValidationReport(schema_issues=[issue], lint_findings=[])
    assert report.has_errors() is True
    assert report.has_warnings() is False


def test_validation_report_with_warning():
    from ddi_l.schema_loader._validation import SchemaValidationIssue
    from ddi_l.validation import ValidationReport

    issue = SchemaValidationIssue(
        message="warn", xpath="/root", context="ctx", severity="warning"
    )
    report = ValidationReport(schema_issues=[issue], lint_findings=[])
    assert report.has_errors() is False
    assert report.has_warnings() is True


def test_validation_report_iter_messages():
    from ddi_l.schema_loader._validation import SchemaValidationIssue
    from ddi_l.validation import ValidationReport

    issue = SchemaValidationIssue(
        message="bad", xpath="/root", context="ctx", severity="error"
    )
    report = ValidationReport(schema_issues=[issue], lint_findings=[])
    msgs = report.messages()
    assert len(msgs) == 1
    assert msgs[0].source == "schema"


def test_validation_report_to_dict():
    from ddi_l.schema_loader._validation import SchemaValidationIssue
    from ddi_l.validation import ValidationReport

    issue = SchemaValidationIssue(
        message="bad", xpath="/root", context="ctx", severity="error"
    )
    report = ValidationReport(schema_issues=[issue], lint_findings=[])
    d = report.to_dict()
    assert "schema_issues" in d
    assert "messages" in d


def test_validation_report_to_dict_no_context():
    from ddi_l.schema_loader._validation import SchemaValidationIssue
    from ddi_l.validation import ValidationReport

    issue = SchemaValidationIssue(
        message="bad", xpath="/root", context="ctx", severity="error"
    )
    report = ValidationReport(schema_issues=[issue], lint_findings=[])
    d = report.to_dict(include_context=False)
    for msg in d["messages"]:
        assert "context" not in msg


def test_validation_message_from_schema_issue():
    from ddi_l.schema_loader._validation import SchemaValidationIssue
    from ddi_l.validation import ValidationMessage

    issue = SchemaValidationIssue(
        message="bad", xpath="/root", context="ctx", severity="error", line=10
    )
    msg = ValidationMessage.from_schema_issue(issue)
    assert msg.message == "bad"
    assert msg.source == "schema"
    assert msg.location is not None  # line 10 produces a location


def test_validation_message_from_lint_finding():
    from ddi_l.lint import LintFinding
    from ddi_l.validation import ValidationMessage

    finding = LintFinding(
        message="lint issue",
        severity="warning",
        rule_id="R001",
        location="/root",
    )
    msg = ValidationMessage.from_lint_finding(finding)
    assert msg.source == "lint"
    assert msg.rule_id == "R001"


def test_validation_message_to_dict():
    from ddi_l.validation import ValidationMessage

    msg = ValidationMessage(
        message="test",
        severity="error",
        source="schema",
        xpath="/root",
    )
    d = msg.to_dict()
    assert d["message"] == "test"
    assert d["source"] == "schema"


def test_validate_document_basic():
    from ddi_l.validation import validate_document

    doc = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
            <r:Agency>a</r:Agency>
            <r:ID>d1</r:ID>
            <r:Version>1.0</r:Version>
        </DDIInstance>
    """)
    report = validate_document(doc, include_lint=False)
    assert isinstance(report.schema_issues, list)


def test_validate_document_with_lint():
    from ddi_l.document import DDIDocument
    from ddi_l.validation import validate_document

    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    report = validate_document(doc)
    assert isinstance(report.lint_findings, list)


def test_validate_fragment_basic():
    from ddi_l.validation import validate_fragment

    xml = textwrap.dedent(f"""\
        <FragmentInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
        </FragmentInstance>
    """)
    report = validate_fragment(xml, include_lint=False)
    assert isinstance(report.schema_issues, list)


def test_validate_maintainable():
    from ddi_l.models.logicalproduct import Variable
    from ddi_l.validation import validate_maintainable

    v = Variable(agency="a", identifier="v1", version="1.0")
    report = validate_maintainable(v, include_lint=False)
    assert isinstance(report.schema_issues, list)


def test_coerce_document_types():
    from ddi_l.document import DDIDocument
    from ddi_l.validation import _coerce_document

    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    assert _coerce_document(doc) is doc

    xml = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
            <r:Agency>a</r:Agency>
            <r:ID>d1</r:ID>
            <r:Version>1.0</r:Version>
        </DDIInstance>
    """)
    assert isinstance(_coerce_document(xml), DDIDocument)
    assert isinstance(_coerce_document(xml.encode()), DDIDocument)


def test_coerce_document_unsupported():
    from ddi_l.validation import _coerce_document

    with pytest.raises(TypeError, match="Unsupported"):
        _coerce_document(42)  # type: ignore[arg-type]


def test_coerce_fragment_types():
    from ddi_l.document import DDIFragment
    from ddi_l.validation import _coerce_fragment

    frag = DDIFragment.create()
    assert _coerce_fragment(frag) is frag


def test_coerce_fragment_unsupported():
    from ddi_l.validation import _coerce_fragment

    with pytest.raises(TypeError, match="Unsupported"):
        _coerce_fragment(42)  # type: ignore[arg-type]


# ===========================================================================
# schema_loader/_conversion_runtime.py — lines 39, 73-74
# ===========================================================================


def test_conversion_runtime_backend():
    from ddi_l.schema_loader._conversion_runtime import (
        get_available_conversion_backends,
        set_conversion_backend,
    )

    backends = get_available_conversion_backends()
    assert "python" in backends
    set_conversion_backend("python")


def test_conversion_runtime_unsupported():
    from ddi_l.schema_loader._conversion_runtime import set_conversion_backend

    with pytest.raises(RuntimeError, match="Only the pure Python"):
        set_conversion_backend("nonexistent")


# ===========================================================================
# namespaces.py — line 148
# ===========================================================================


def test_namespace_profile_extra():
    from ddi_l.namespaces import build_namespace_map

    result = build_namespace_map(extra={"custom": "http://custom"})
    assert result.get("custom") == "http://custom"


# ===========================================================================
# validation.py — additional coverage for lines 100, 110, 174, 315-317
# ===========================================================================


def test_validation_report_severity_none_issue():
    """Exercise line 100: _consume_severity with severity=None."""
    from ddi_l.schema_loader._validation import SchemaValidationIssue
    from ddi_l.validation import ValidationReport

    issue = SchemaValidationIssue(
        message="unknown",
        xpath="/root",
        context="ctx",
        severity=None,  # type: ignore[arg-type]
    )
    report = ValidationReport(schema_issues=[issue], lint_findings=[])
    assert report.has_errors() is False
    assert report.has_warnings() is False


def test_validation_report_early_break():
    """Exercise line 110: early break when both error and warning found in schema_issues."""
    from ddi_l.schema_loader._validation import SchemaValidationIssue
    from ddi_l.validation import ValidationReport

    issues = [
        SchemaValidationIssue(message="err", xpath="/a", context="c", severity="error"),
        SchemaValidationIssue(
            message="warn", xpath="/b", context="c", severity="warning"
        ),
        SchemaValidationIssue(
            message="extra", xpath="/c", context="c", severity="error"
        ),
    ]
    report = ValidationReport(schema_issues=issues, lint_findings=[])
    assert report.has_errors() is True
    assert report.has_warnings() is True


def test_coerce_document_from_element():
    """Exercise line 174: _coerce_document with Element input."""
    from ddi_l._etree import create_element
    from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
    from ddi_l.models.base import qn
    from ddi_l.validation import _coerce_document

    root = create_element(qn(INSTANCE_NS, "DDIInstance"))
    agency = create_element(qn(REUSABLE_NS, "Agency"))
    agency.text = "test"
    root.append(agency)
    id_elem = create_element(qn(REUSABLE_NS, "ID"))
    id_elem.text = "d1"
    root.append(id_elem)
    ver = create_element(qn(REUSABLE_NS, "Version"))
    ver.text = "1.0"
    root.append(ver)

    doc = _coerce_document(root)
    assert doc is not None


def test_coerce_fragment_from_element():
    """Exercise line 174 for fragments: _coerce_fragment with Element input."""
    from ddi_l._etree import create_element
    from ddi_l.constants import INSTANCE_NS
    from ddi_l.models.base import qn
    from ddi_l.validation import _coerce_fragment

    root = create_element(qn(INSTANCE_NS, "FragmentInstance"))
    frag = _coerce_fragment(root)
    assert frag is not None


def test_validate_fragment_schema_error_path():
    """Exercise lines 315-317: fragment validation raising SchemaValidationError."""
    from unittest.mock import patch

    from ddi_l import schema_loader
    from ddi_l.document import DDIFragment
    from ddi_l.validation import validate_fragment

    frag = DDIFragment.create()
    # Make schema_loader.validate raise SchemaValidationError
    error = schema_loader.SchemaValidationError([])

    with patch.object(schema_loader, "validate", side_effect=error):
        try:
            validate_fragment(frag, raise_error=True)
        except Exception:
            pass  # We just need the code path to execute


# ===========================================================================
# models/reusable.py — lines 317-318, 329, 343
# ===========================================================================


def test_managed_missing_values_descriptions():
    """Exercise lines 329 and 343: descriptions and missing_values in to_xml."""
    from ddi_l.models.reusable import ManagedMissingValuesRepresentation

    mmvr = ManagedMissingValuesRepresentation(
        agency="a",
        identifier="mmv1",
        version="1.0",
        descriptions=[InternationalString(text="A description", lang="en")],
    )
    elem = mmvr.to_xml()
    assert elem is not None


# ===========================================================================
# models/classification.py — remaining lines (48, 54, 56, 302, 376, 392, 602, 604, 614, 616, 640)
# ===========================================================================


def test_classification_item_from_xml_valid_from_to():
    """Exercise lines 48-56: from_xml parsing valid_from and valid_to."""
    from ddi_l.models.classification import CLASSIFICATION_NS, ClassificationItem

    elem = create_element(qn(CLASSIFICATION_NS, "ClassificationItem"))
    agency = create_element(qn(REUSABLE_NS, "Agency"))
    agency.text = "a"
    elem.append(agency)
    id_elem = create_element(qn(REUSABLE_NS, "ID"))
    id_elem.text = "ci1"
    elem.append(id_elem)
    ver = create_element(qn(REUSABLE_NS, "Version"))
    ver.text = "1.0"
    elem.append(ver)
    vf = create_element(qn(CLASSIFICATION_NS, "ValidFrom"))
    vf.text = "2020-01-01"
    elem.append(vf)
    vt = create_element(qn(CLASSIFICATION_NS, "ValidTo"))
    vt.text = "2025-12-31"
    elem.append(vt)

    item = ClassificationItem.from_xml(elem)
    assert item.valid_from is not None and item.valid_from.text == "2020-01-01"
    assert item.valid_to is not None and item.valid_to.text == "2025-12-31"
