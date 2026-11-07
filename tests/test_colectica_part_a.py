"""Colectica round-trip and versioning fixes, and the reference-rule split.

The fixtures under ``tests/fixtures/colectica/`` are a synthetic "Pet survey"
in Colectica's layout: ``pets_nobom`` and ``pets_bom`` differ only in the
byte-order mark; ``pets_latebound`` holds a question at version 4 whose
parameters are referenced late-bound at version 1, as Colectica writes them,
and a BasedOn link to the (absent) item it was copied from.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import pytest

import ddi_l
from ddi_l import cli
from ddi_l._etree import fromstring, tostring
from ddi_l.exceptions import DDIModelError
from ddi_l.lint import (
    COLECTICA_QUESTIONNAIRE_PROFILE,
    DDI_PROFILE_DEFAULT,
    SEVERITIES,
    LintFinding,
    iter_registered_profiles,
    register_rule,
    run_lint,
    run_profile,
)
from ddi_l.models.base import MaintainableBase
from ddi_l.xml_utils import sniff_bom

FIXTURES = Path(__file__).parent / "fixtures" / "colectica"
NOBOM = FIXTURES / "pets_nobom.ddi33.xml"
BOM = FIXTURES / "pets_bom.ddi33.xml"
LATEBOUND = FIXTURES / "pets_latebound.ddi33.xml"
UTF8_BOM = b"\xef\xbb\xbf"
COLECTICA_STAMP = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{7}Z$")

QUESTION = "11111111-1111-4111-8111-000000000001"
QUESTION_OUT = "11111111-1111-4111-8111-000000000002"
SOURCE = "11111111-1111-4111-8111-0000000000ff"


# ---- A1: the byte-order mark ---------------------------------------------


def test_fixtures_differ_only_in_the_byte_order_mark() -> None:
    assert BOM.read_bytes() == UTF8_BOM + NOBOM.read_bytes()


@pytest.mark.parametrize(("path", "has_bom"), [(NOBOM, False), (BOM, True)])
def test_save_reproduces_the_source_byte_for_byte(
    tmp_path: Path, path: Path, has_bom: bool
) -> None:
    fragment = ddi_l.open_fragment(path)
    assert fragment.source_bom is has_bom
    target = tmp_path / "out.xml"
    fragment.save(target)
    assert target.read_bytes() == path.read_bytes()
    assert fragment.to_colectica_bytes() == path.read_bytes()


@pytest.mark.parametrize("path", [NOBOM, BOM])
def test_cli_roundtrip_reproduces_the_source_byte_for_byte(
    tmp_path: Path, path: Path
) -> None:
    target = tmp_path / "out.xml"
    status = cli.main(
        ["roundtrip", "--layout", "colectica", str(path), "-o", str(target)]
    )
    assert status == 0
    assert target.read_bytes() == path.read_bytes()


@pytest.mark.parametrize(
    "source",
    [NOBOM.read_bytes(), NOBOM.read_text(encoding="utf-8"), str(NOBOM)],
    ids=["bytes", "text", "path"],
)
def test_read_ddi_records_a_missing_mark(source: object) -> None:
    fragment = ddi_l.read_ddi(source)  # type: ignore[arg-type]
    assert isinstance(fragment, ddi_l.DDIFragment)
    assert fragment.source_bom is False
    assert fragment.to_colectica_bytes() == NOBOM.read_bytes()


def test_read_ddi_records_a_mark_on_a_stream_and_leaves_it_readable() -> None:
    stream = io.BytesIO(BOM.read_bytes())
    fragment = ddi_l.read_ddi(stream)
    assert isinstance(fragment, ddi_l.DDIFragment)
    assert fragment.source_bom is True
    assert fragment.to_colectica_bytes() == BOM.read_bytes()


def test_an_explicit_bom_argument_wins(tmp_path: Path) -> None:
    fragment = ddi_l.open_fragment(NOBOM)
    assert fragment.to_colectica_bytes(bom=True) == BOM.read_bytes()
    target = tmp_path / "out.xml"
    fragment.save(target, bom=True)
    assert target.read_bytes() == BOM.read_bytes()
    assert ddi_l.open_fragment(BOM).to_colectica_bytes(bom=False) == (
        NOBOM.read_bytes()
    )
    assert ddi_l.write_ddi(fragment, layout="colectica", bom=True) == (BOM.read_bytes())


def test_a_fragment_not_read_from_bytes_gets_a_mark_by_default() -> None:
    parsed = ddi_l.open_fragment(NOBOM)
    item = parsed.get(QUESTION)
    assert item is not None
    built = ddi_l.DDIFragment.from_items([item])
    assert built.source_bom is None
    assert built.to_colectica_bytes().startswith(UTF8_BOM)
    element = fromstring(NOBOM.read_bytes())
    assert ddi_l.write_ddi(element, layout="colectica").startswith(UTF8_BOM)
    assert not ddi_l.write_ddi(element, layout="colectica", bom=False).startswith(
        UTF8_BOM
    )


def test_sniff_bom_on_every_source_kind(tmp_path: Path) -> None:
    raw = BOM.read_bytes()
    assert sniff_bom(raw) is True
    assert sniff_bom(bytearray(raw[3:])) is False
    assert sniff_bom(raw.decode("utf-8")) is True
    assert sniff_bom(BOM) is True
    assert sniff_bom(str(NOBOM)) is False
    assert sniff_bom(io.StringIO(raw.decode("utf-8"))) is True
    stream = io.BytesIO(raw)
    stream.read(5)
    # Peeks from where the stream stands and puts it back there.
    assert sniff_bom(stream) is False
    assert stream.tell() == 5
    assert sniff_bom(fromstring(raw[3:])) is None
    assert sniff_bom(123) is None  # type: ignore[arg-type]

    class _Pipe(io.RawIOBase):
        def readable(self) -> bool:
            return True

        def seekable(self) -> bool:
            return False

    assert sniff_bom(_Pipe()) is None  # type: ignore[arg-type]


# ---- A2: bumps refresh versionDate; version responsibility --------------


def _question() -> MaintainableBase:
    item = ddi_l.open_fragment(LATEBOUND).get(QUESTION)
    assert item is not None
    return item


def test_a_bump_refreshes_version_date_in_colectica_format() -> None:
    item = _question()
    before = item.version_date
    assert before == "2026-01-05T10:00:00.0000000Z"
    item.increment_major_version()
    assert item.version == "5"
    assert item.version_date != before
    assert item.version_date is not None
    assert COLECTICA_STAMP.match(item.version_date)
    element = item.to_xml()
    assert element.get("versionDate") == item.version_date


def test_touch_false_leaves_version_date_alone() -> None:
    item = _question()
    item.increment_major_version(touch=False)
    assert item.version_date == "2026-01-05T10:00:00.0000000Z"


def test_an_item_without_a_version_date_does_not_gain_one() -> None:
    item = MaintainableBase(version="1.0")
    item.increment_minor_version()
    assert item.version == "1.1"
    assert item.version_date is None


def test_no_responsibility_is_invented() -> None:
    item = MaintainableBase(version="1")
    item.increment_major_version()
    assert item.version_responsibility is None


def test_the_configured_responsibility_is_recorded() -> None:
    ddi_l.configure(version_responsibility="Questionnaire team")
    item = MaintainableBase(version="1")
    item.increment_major_version()
    assert item.version_responsibility == "Questionnaire team"


def test_an_explicit_responsibility_beats_the_configured_one() -> None:
    ddi_l.configure(version_responsibility="Questionnaire team")
    item = MaintainableBase(version="1.0")
    item.increment_subversion(responsibility="Reviewer")
    assert item.version_responsibility == "Reviewer"


def test_an_explicit_none_records_no_responsibility() -> None:
    ddi_l.configure(version_responsibility="Questionnaire team")
    item = MaintainableBase(version="1")
    item.increment_major_version(responsibility=None)
    assert item.version_responsibility is None


def test_configured_restores_the_previous_configuration() -> None:
    ddi_l.configure(version_responsibility="Outer")
    with ddi_l.configured(version_responsibility="Inner") as inside:
        assert inside.version_responsibility == "Inner"
        assert ddi_l.get_configuration().version_responsibility == "Inner"
    assert ddi_l.get_configuration().version_responsibility == "Outer"
    with pytest.raises(RuntimeError), ddi_l.configured(version_responsibility=None):
        assert ddi_l.get_configuration().version_responsibility is None
        raise RuntimeError
    assert ddi_l.get_configuration().version_responsibility == "Outer"


def test_configure_without_arguments_changes_nothing_and_reset_clears() -> None:
    current = ddi_l.configure(version_responsibility="Team")
    assert ddi_l.configure() is current
    assert ddi_l.reset_configuration() == ddi_l.Configuration()
    assert ddi_l.get_configuration().version_responsibility is None


# ---- A3: an item keeps its versioning scheme ----------------------------


@pytest.mark.parametrize("method", ["increment_minor_version", "increment_subversion"])
def test_a_minor_bump_on_an_integer_version_is_refused(method: str) -> None:
    item = MaintainableBase(identifier="q-1", version="6")
    with pytest.raises(DDIModelError, match="integer versions"):
        getattr(item, method)()
    assert item.version == "6"


def test_allow_dotted_opts_into_a_dotted_version() -> None:
    item = MaintainableBase(version="6")
    item.increment_minor_version(allow_dotted=True)
    assert item.version == "6.1"
    other = MaintainableBase(version="6")
    other.increment_subversion(allow_dotted=True)
    assert other.version == "6.0.1"


def test_a_dotted_version_bumps_as_before() -> None:
    item = MaintainableBase(version="1.0")
    item.increment_minor_version()
    assert item.version == "1.1"
    item.increment_subversion()
    assert item.version == "1.1.1"


def test_an_integer_version_takes_a_major_bump() -> None:
    item = MaintainableBase(version="6")
    item.increment_major_version()
    assert item.version == "7"


# ---- A0: severities and the default profile ------------------------------


def test_severities_are_ordered_least_severe_first() -> None:
    assert SEVERITIES == ("info", "warning", "error")


def test_an_unknown_severity_is_rejected_when_the_finding_is_built() -> None:
    with pytest.raises(ValueError, match="Unknown lint severity 'fatal'"):
        LintFinding(rule_id="x", message="y", severity="fatal")


def test_an_unknown_severity_from_a_callback_is_rejected() -> None:
    class _Finding:
        rule_id = "tests.bad"
        message = "bad"
        severity = "critical"
        location = None

    register_rule(
        "tests.bad",
        lambda document: [_Finding()],  # type: ignore[arg-type]
        default=False,
    )
    fragment = ddi_l.open_fragment(NOBOM)
    with pytest.raises(ValueError, match="critical"):
        run_lint(fragment, rules=["tests.bad"])


def test_run_lint_runs_the_default_profile_only() -> None:
    profiles = dict(iter_registered_profiles())
    fragment = ddi_l.open_fragment(LATEBOUND)
    rule_ids = {finding.rule_id for finding in run_lint(fragment)}
    assert "colectica.maintainable.labels" not in rule_ids
    assert rule_ids <= set(profiles[DDI_PROFILE_DEFAULT])
    assert "colectica.maintainable.labels" not in profiles[DDI_PROFILE_DEFAULT]
    for rule in ("ddi.reference.version", "ddi.reference.provenance-external"):
        assert rule in profiles[DDI_PROFILE_DEFAULT]


def test_a_rule_registered_by_default_joins_the_default_profile() -> None:
    def _custom(document: object) -> list[LintFinding]:
        return [LintFinding(rule_id="tests.custom", message="ran", severity="info")]

    def _profile_only(document: object) -> list[LintFinding]:
        return [LintFinding(rule_id="tests.only", message="ran", severity="info")]

    register_rule("tests.custom", _custom)
    register_rule("tests.only", _profile_only, default=False)
    fragment = ddi_l.open_fragment(NOBOM)
    rule_ids = {finding.rule_id for finding in run_lint(fragment)}
    assert "tests.custom" in rule_ids
    assert "tests.only" not in rule_ids


def test_the_colectica_profile_is_registered() -> None:
    profiles = dict(iter_registered_profiles())
    rules = profiles[COLECTICA_QUESTIONNAIRE_PROFILE]
    assert rules[:4] == (
        "colectica.maintainable.labels",
        "ddi.reference.integrity",
        "ddi.reference.version",
        "ddi.reference.provenance-external",
    )
    # The Part C rules follow; none of them is in the default profile.
    assert not set(rules[4:]) & set(profiles[DDI_PROFILE_DEFAULT])


def _lint_status(path: Path, *args: str) -> int:
    return cli.main(["lint", str(path), "--output", "-", *args])


def test_info_findings_do_not_fail_lint(capsys: pytest.CaptureFixture[str]) -> None:
    only_info = ("--rules", "ddi.reference.provenance-external")
    assert _lint_status(LATEBOUND, *only_info) == 0
    assert '"severity": "info"' in capsys.readouterr().out
    assert _lint_status(LATEBOUND, *only_info, "--fail-severity", "error") == 0
    assert _lint_status(LATEBOUND, *only_info, "--fail-severity", "warning") == 0
    assert _lint_status(LATEBOUND, *only_info, "--fail-severity", "info") == 1


def test_the_colectica_profile_runs_from_the_cli(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _lint_status(LATEBOUND, "--profile", COLECTICA_QUESTIONNAIRE_PROFILE) == 0
    output = capsys.readouterr().out
    assert "colectica.maintainable.labels" in output
    assert "ddi.maintainable.labels" not in output
    status = _lint_status(
        LATEBOUND,
        "--profile",
        COLECTICA_QUESTIONNAIRE_PROFILE,
        "--fail-severity",
        "warning",
    )
    assert status == 1


# ---- A4: reference resolution --------------------------------------------


def _reference_findings(fragment: ddi_l.DDIFragment) -> list[LintFinding]:
    return [
        finding
        for finding in run_lint(fragment)
        if finding.rule_id.startswith("ddi.reference.")
    ]


def _edited(old: str, new: str, count: int = 1) -> ddi_l.DDIFragment:
    text = LATEBOUND.read_text(encoding="utf-8")
    assert text.count(old) >= count, old
    return ddi_l.read_ddi(text.replace(old, new, count))  # type: ignore[return-value]


def test_late_bound_references_at_a_lower_version_resolve() -> None:
    findings = _reference_findings(ddi_l.open_fragment(LATEBOUND))
    assert [(f.rule_id, f.severity) for f in findings] == [
        ("ddi.reference.provenance-external", "info")
    ]
    assert SOURCE in findings[0].message


def test_a_dangling_binding_is_an_integrity_finding() -> None:
    # The binding's source names a parameter that is not in the file.
    fragment = _edited(
        f'<r:SourceParameterReference lateBound="true">\n'
        f"        <r:Agency>int.example</r:Agency>\n"
        f"        <r:ID>{QUESTION_OUT}</r:ID>",
        '<r:SourceParameterReference lateBound="true">\n'
        "        <r:Agency>int.example</r:Agency>\n"
        "        <r:ID>99999999-9999-4999-8999-999999999999</r:ID>",
    )
    integrity = [
        f
        for f in _reference_findings(fragment)
        if f.rule_id == "ddi.reference.integrity"
    ]
    assert len(integrity) == 1
    assert integrity[0].severity == "warning"  # a fragment may be partial
    assert "OutParameter '99999999-9999-4999-8999-999999999999'" in (
        integrity[0].message
    )


def test_an_exact_reference_to_a_missing_version_is_a_version_finding() -> None:
    # The construct points at the question's version 3; only 4 is present.
    fragment = _edited(
        f"<r:ID>{QUESTION}</r:ID>\n      <r:Version>4</r:Version>\n"
        "      <r:TypeOfObject>QuestionItem</r:TypeOfObject>",
        f"<r:ID>{QUESTION}</r:ID>\n      <r:Version>3</r:Version>\n"
        "      <r:TypeOfObject>QuestionItem</r:TypeOfObject>",
    )
    findings = _reference_findings(fragment)
    version = [f for f in findings if f.rule_id == "ddi.reference.version"]
    assert len(version) == 1
    assert version[0].severity == "warning"
    assert "version 3 is not present; available: 4" in version[0].message
    assert not [f for f in findings if f.rule_id == "ddi.reference.integrity"]


def test_a_late_bound_reference_ahead_of_every_version_is_a_version_finding() -> None:
    fragment = _edited(
        f"<r:ID>{QUESTION_OUT}</r:ID>\n        <r:Version>1</r:Version>",
        f"<r:ID>{QUESTION_OUT}</r:ID>\n        <r:Version>9</r:Version>",
    )
    version = [
        f for f in _reference_findings(fragment) if f.rule_id == "ddi.reference.version"
    ]
    assert len(version) == 1
    assert "late-bound at version 9, newer than any present" in version[0].message
    assert "available: 4" in version[0].message


def test_late_bound_written_as_one_is_late_bound() -> None:
    # xs:boolean spells true as "true" or "1".
    fragment = _edited('lateBound="true"', 'lateBound="1"', count=2)
    assert [f.rule_id for f in _reference_findings(fragment)] == [
        "ddi.reference.provenance-external"
    ]


def test_a_late_bound_restriction_limits_the_versions_that_resolve() -> None:
    # The question's parameter is at version 4 only.
    restricted = 'lateBound="true" lateBoundRestriction="{}"'
    within = _edited('lateBound="true"', restricted.format("4"))
    assert [f.rule_id for f in _reference_findings(within)] == [
        "ddi.reference.provenance-external"
    ]
    outside = _edited('lateBound="true"', restricted.format("3"))
    version = [
        f for f in _reference_findings(outside) if f.rule_id == "ddi.reference.version"
    ]
    assert len(version) == 1
    assert "late-bound within version 3, which is not present; available: 4" in (
        version[0].message
    )


def test_a_late_bound_reference_to_an_absent_item_is_unresolved() -> None:
    # Rename the parameter itself, so the late-bound reference has no target.
    fragment = _edited(
        f"<r:ID>{QUESTION_OUT}</r:ID>\n      <r:Version>4</r:Version>",
        "<r:ID>absent</r:ID>\n      <r:Version>4</r:Version>",
    )
    rule_ids = [f.rule_id for f in _reference_findings(fragment)]
    assert rule_ids.count("ddi.reference.integrity") == 1


def test_a_based_on_reference_to_a_present_item_is_silent() -> None:
    fragment = _edited(
        f"<r:ID>{SOURCE}</r:ID>\n        <r:Version>1</r:Version>",
        f"<r:ID>{QUESTION}</r:ID>\n        <r:Version>4</r:Version>",
    )
    assert _reference_findings(fragment) == []


def test_a_based_on_reference_to_another_version_names_the_versions() -> None:
    fragment = _edited(
        f"<r:ID>{SOURCE}</r:ID>\n        <r:Version>1</r:Version>",
        f"<r:ID>{QUESTION}</r:ID>\n        <r:Version>2</r:Version>",
    )
    findings = _reference_findings(fragment)
    assert [(f.rule_id, f.severity) for f in findings] == [
        ("ddi.reference.provenance-external", "info")
    ]
    assert "names version 2, which is not in this file; available: 4" in (
        findings[0].message
    )


def test_unresolved_references_in_an_instance_stay_errors() -> None:
    document = ddi_l.new_study(title="Pets", agency="int.example").inner
    root = fromstring(tostring(document.root))
    # Point the study at a data collection that is not in the document.
    from ddi_l.models.base import Reference

    reference = Reference(
        agency="int.example", identifier="absent", version="1", type_of_object="Concept"
    ).to_xml("ConceptReference")
    next(iter(root)).append(reference)
    findings = run_lint(ddi_l.read_ddi(tostring(root)))
    integrity = [f for f in findings if f.rule_id == "ddi.reference.integrity"]
    assert [f.severity for f in integrity] == ["error"]


# ---- A5: Colectica labels ------------------------------------------------


def _colectica_labels(fragment: ddi_l.DDIFragment) -> list[LintFinding]:
    result = run_profile(
        fragment, COLECTICA_QUESTIONNAIRE_PROFILE, include_schema=False
    )
    return [
        f for f in result.lint_findings if f.rule_id == "colectica.maintainable.labels"
    ]


def test_a_name_satisfies_the_colectica_labels_rule() -> None:
    findings = _colectica_labels(ddi_l.open_fragment(LATEBOUND))
    # The Sequence has a ConstructName and the QuestionItem a QuestionItemName;
    # only the QuestionConstruct has neither a name nor a label.
    assert [f.message for f in findings] == [
        "QuestionConstruct 11111111 has no label or name with text."
    ]
    assert findings[0].severity == "warning"


def test_an_empty_name_does_not_satisfy_the_colectica_labels_rule() -> None:
    fragment = _edited(
        '<r:String xml:lang="en-CA">Pet survey</r:String>',
        '<r:String xml:lang="en-CA">   </r:String>',
    )
    messages = [f.message for f in _colectica_labels(fragment)]
    assert "Sequence 11111111 has no label or name with text." in messages


def test_a_label_satisfies_the_colectica_labels_rule() -> None:
    fragment = _edited(
        '<QuestionItemName>\n      <r:String xml:lang="en-CA">PetCount</r:String>\n'
        "    </QuestionItemName>",
        '<QuestionItemName>\n      <r:String xml:lang="en-CA"></r:String>\n'
        "    </QuestionItemName>\n"
        '    <r:Label>\n      <r:Content xml:lang="en-CA">Pets</r:Content>\n'
        "    </r:Label>",
    )
    messages = [f.message for f in _colectica_labels(fragment)]
    assert not any(message.startswith("QuestionItem ") for message in messages)
