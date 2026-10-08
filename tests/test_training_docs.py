"""Regression tests for values documented in training materials."""

from __future__ import annotations

from pathlib import Path

from ddi_l import read_ddi
from ddi_l._etree import create_element
from ddi_l.constants import LOGICAL_PRODUCT_NS, REUSABLE_NS
from ddi_l.document import DDIDocument
from ddi_l.lint import DDI_PROFILE_DEFAULT, run_profile
from ddi_l.models.base import qn
from ddi_l.validation import ValidationMessage, ValidationReport
from tests import EXAMPLES_DIR, PACKAGE_FIXTURES_DIR


def _resolve_example_instance() -> Path:
    candidates = [
        EXAMPLES_DIR / "example_instance.xml",
        PACKAGE_FIXTURES_DIR / "instances" / "example_instance.xml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not locate example_instance.xml in known locations.")


def test_example_instance_lints_completely_clean() -> None:
    """The packaged example must produce no findings at all.

    Zero findings is unambiguous: any change in the generator, the lint
    rules or the label plumbing that adds one shows up here.
    """
    example_path = _resolve_example_instance()
    result = run_profile(read_ddi(example_path), DDI_PROFILE_DEFAULT)

    assert result.lint_findings == [], (
        "examples/example_instance.xml is no longer lint-clean: "
        f"{[(f.rule_id, f.location) for f in result.lint_findings[:5]]}"
    )
    assert result.schema_issues == []


def test_training_docs_messages_snippet_matches_api() -> None:
    """Mirror the doctest snippet illustrating ValidationReport.messages().

    Built from a document with a deliberate finding rather than the packaged
    example: the example lints clean now, and a test of "messages() surfaces
    findings" must not quietly depend on our sample file being flawed.
    """
    document = DDIDocument.create(
        agency="example.agency", identifier="demo", version="1.0"
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

    result = run_profile(document, DDI_PROFILE_DEFAULT)

    assert result.lint_findings, "expected the unlabelled CodeList to be reported"

    combined = ValidationReport(result.schema_issues, result.lint_findings).messages()
    assert len(combined) == len(result.schema_issues) + len(result.lint_findings)
    assert combined and all(isinstance(m, ValidationMessage) for m in combined)
    # The point of messages() is that both sources arrive in one sequence;
    # which comes first is not part of the contract.
    assert "lint" in {message.source for message in combined}
