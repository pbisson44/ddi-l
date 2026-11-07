"""The in-memory operations behind the HTTP API and the CLI.

Mutation testing showed these pass on options and branches no other test
checks: fragment roots, ``version=``, the default layout and format, and the
messages a caller sees.
"""

from __future__ import annotations

import io
import zipfile

import pytest

from ddi_l import operations
from ddi_l.document import DDIDocument, DDIFragment
from ddi_l.lint import DDI_PROFILE_DEFAULT, ProfileResult, register_profile
from ddi_l.schema_loader import fromstring
from tests import SAMPLES_DIR, TEST_FIXTURES_DIR

INSTANCE = (SAMPLES_DIR / "minimal_instance.xml").read_bytes()
FRAGMENT = (TEST_FIXTURES_DIR / "minimal_fragment.xml").read_bytes()
INSTANCE_3_2 = (TEST_FIXTURES_DIR / "minimal_instance_3_2.xml").read_bytes()

I33 = "{ddi:instance:3_3}"
I32 = "{ddi:instance:3_2}"


def test_wrap_element_picks_the_wrapper_from_the_root() -> None:
    assert isinstance(operations.wrap_element(fromstring(INSTANCE)), DDIDocument)
    assert isinstance(operations.wrap_element(fromstring(INSTANCE_3_2)), DDIDocument)

    fragment_root = fromstring(FRAGMENT)
    fragment = operations.wrap_element(fragment_root)
    assert isinstance(fragment, DDIFragment)
    assert fragment.root is fragment_root

    with pytest.raises(
        ValueError, match=r"^Root element must be DDIInstance or FragmentInstance\.$"
    ):
        operations.wrap_element(fromstring(b'<Other xmlns="urn:example"/>'))


def test_coerce_json_payload_writes_booleans_as_xml_text() -> None:
    coerced = operations.coerce_json_payload({"a": True, "b": [False]})

    assert coerced == {f"{I33}DDIInstance": {"a": "true", "b": ["false"]}}


def test_coerce_json_payload_keeps_a_payload_that_names_its_root() -> None:
    payload = {f"{I33}FragmentInstance": {"x": "1"}}

    assert operations.coerce_json_payload(payload) == payload


@pytest.mark.parametrize(
    ("payload", "root"),
    [
        # Only a payload of more than one key is wrapped; the order of the
        # keys does not matter.
        (
            {"{ddi:reusable:3_3}Agency": "a", "{ddi:instance:3_3}Fragment": []},
            "FragmentInstance",
        ),
        (
            {
                "{ddi:reusable:3_3}Agency": "a",
                "{ddi:instance:3_3}TopLevelReference": {},
            },
            "FragmentInstance",
        ),
        # A key that names no element is skipped, not the end of the search.
        ({"@lang": "en", "{ddi:instance:3_3}Fragment": []}, "FragmentInstance"),
        ({"{ddi:reusable:3_3}Agency": "a", "{ddi:reusable:3_3}ID": "b"}, "DDIInstance"),
    ],
)
def test_coerce_json_payload_chooses_the_root_from_the_keys(
    payload: dict, root: str
) -> None:
    assert list(operations.coerce_json_payload(payload)) == [f"{I33}{root}"]


def test_coerce_json_payload_uses_the_version_given() -> None:
    coerced = operations.coerce_json_payload({"a": "1", "b": "2"}, version="3.2")

    assert list(coerced) == [f"{I32}DDIInstance"]


def test_validate_source_lints_by_default_and_validates_fragments() -> None:
    report = operations.validate_source(FRAGMENT)
    assert report.schema_issues == []
    assert [f.rule_id for f in report.lint_findings] == ["ddi.reference.integrity"]

    assert operations.validate_source(FRAGMENT, lint=False).lint_findings == []


def test_validate_source_passes_the_version_on() -> None:
    # Against 3.2, the 3.3 namespace is not the instance namespace.
    assert operations.validate_source(INSTANCE, version="3.2").schema_issues
    assert operations.validate_source(FRAGMENT, version="3.2").schema_issues


def test_lint_source_lints_a_fragment_with_and_without_a_profile() -> None:
    findings = operations.lint_source(FRAGMENT)
    assert isinstance(findings, list)
    assert [f.rule_id for f in findings] == ["ddi.reference.integrity"]

    result = operations.lint_source(FRAGMENT, profile=DDI_PROFILE_DEFAULT)
    assert isinstance(result, ProfileResult)
    assert [f.rule_id for f in result.lint_findings] == ["ddi.reference.integrity"]

    register_profile("test.citation-only", ["ddi.citation.present"])
    narrow = operations.lint_source(FRAGMENT, profile="test.citation-only")
    assert isinstance(narrow, ProfileResult)
    assert narrow.lint_findings == []


def test_lint_source_runs_a_profile_on_an_instance() -> None:
    result = operations.lint_source(INSTANCE, profile=DDI_PROFILE_DEFAULT)

    assert isinstance(result, ProfileResult)
    assert result.lint_findings == []


def test_to_jsonld_payload_refuses_a_fragment() -> None:
    with pytest.raises(
        ValueError,
        match=r"^JSON-LD conversion needs a DDIInstance; a FragmentInstance has no "
        r"study to describe\.$",
    ):
        operations.to_jsonld_payload(FRAGMENT)

    import ddi_l as ddi

    study = ddi.new_study(title="T", agency="example.org").to_xml().encode("utf-8")
    assert operations.to_jsonld_payload(study)


def test_from_json_payload_writes_the_version_given() -> None:
    payload = operations.to_json_payload(INSTANCE_3_2)

    xml = operations.from_json_payload(payload, version="3.2")

    assert fromstring(xml).tag == f"{I32}DDIInstance"


def test_from_json_payload_writes_a_fragment_as_colectica_does() -> None:
    export = (TEST_FIXTURES_DIR / "colectica_group_fragment.xml").read_bytes()

    xml = operations.from_json_payload(operations.to_json_payload(export))

    assert xml.startswith(b'\xef\xbb\xbf<?xml version="1.0" encoding="utf-8"?>')
    assert fromstring(xml).tag == f"{I33}FragmentInstance"


def test_roundtrip_source_defaults_and_messages() -> None:
    assert fromstring(operations.roundtrip_source(INSTANCE)).tag == f"{I33}DDIInstance"

    with pytest.raises(
        ValueError,
        match=r"^Unknown layout 'tight'; expected 'default' or 'colectica'\.$",
    ):
        operations.roundtrip_source(INSTANCE, layout="tight")
    with pytest.raises(
        ValueError,
        match=r"^The colectica layout writes a FragmentInstance; this document is a "
        r"DDIInstance\.$",
    ):
        operations.roundtrip_source(INSTANCE, layout="colectica")


def test_tables_import_writes_colectica_layout_by_default() -> None:
    workbook = operations.tables_template(example=True)

    xml = operations.tables_import(workbook)

    # Colectica's layout: a byte-order mark and a lower-case encoding name.
    assert xml.startswith(b'\xef\xbb\xbf<?xml version="1.0" encoding="utf-8"?>')
    assert fromstring(xml).tag == f"{I33}FragmentInstance"


def test_tables_template_defaults_to_a_blank_workbook() -> None:
    blank = operations.tables_template()
    example = operations.tables_template(example=True)

    names = zipfile.ZipFile(io.BytesIO(blank)).namelist()
    assert "xl/workbook.xml" in names
    assert blank != example


@pytest.mark.parametrize(
    ("options", "message"),
    [
        (
            {"template_format": "csv"},
            r"^Unknown format 'csv'; expected 'xlsx' or 'zip'\.$",
        ),
        ({"languages": ()}, r"^Give at least one language\.$"),
        (
            {"languages": ("en", "fr_CA")},
            r"^'fr_CA' is not a language tag, such as en or fr-CA\.$",
        ),
    ],
)
def test_tables_template_messages(options: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        operations.tables_template(**options)


def test_a_fragment_is_linted_as_a_fragment() -> None:
    """As `ddi lint` does: its dangling reference is a warning, its scope the
    fragment, and it has no instance agency to check."""
    from ddi_l.lint import lint_configuration

    strict = lint_configuration(allowed_agencies=["other.agency"])
    findings = operations.lint_source(FRAGMENT, configuration=strict)

    assert isinstance(findings, list)
    assert [(f.rule_id, f.severity) for f in findings] == [
        ("ddi.reference.integrity", "warning")
    ]
    assert "this fragment" in findings[0].message
    assert operations.validate_source(FRAGMENT).lint_findings[0].severity == ("warning")


def test_lint_source_selects_and_skips_rules_as_the_cli_does() -> None:
    from ddi_l.lint import lint_configuration

    strict = lint_configuration(allowed_agencies=["other.agency"])
    only = operations.lint_source(
        INSTANCE, rules=["ddi.agency.allowed"], configuration=strict
    )
    assert isinstance(only, list)
    assert {f.rule_id for f in only} == {"ddi.agency.allowed"}

    skipped = operations.lint_source(
        INSTANCE, skip_rules=["ddi.agency.allowed"], configuration=strict
    )
    assert isinstance(skipped, list)
    assert "ddi.agency.allowed" not in {f.rule_id for f in skipped}

    profiled = operations.lint_source(
        INSTANCE,
        profile=DDI_PROFILE_DEFAULT,
        skip_rules=["ddi.agency.allowed"],
        configuration=strict,
    )
    assert isinstance(profiled, ProfileResult)
    assert "ddi.agency.allowed" not in {f.rule_id for f in profiled.lint_findings}


def test_parse_lint_configuration_reads_a_json_object() -> None:
    configuration = operations.parse_lint_configuration(
        '{"allowed_agencies": ["a.org"], "required_languages": ["en", "fr"]}'
    )
    assert configuration.allowed_agencies == ("a.org",)
    assert configuration.required_languages == ("en", "fr")
    assert configuration.required_citation_languages == ("en",)

    for text in (
        "[1]",
        "{",
        '{"no_such_option": 1}',
        '{"placeholder_patterns": ["("]}',
    ):
        with pytest.raises(ValueError):
            operations.parse_lint_configuration(text)
