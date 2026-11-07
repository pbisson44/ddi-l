"""Compare an instrument with a questionnaire spec: one test per rule.

The instrument (tests/fixtures/spec/pets_conform.ddi33.xml, written by
build_pets_conform.py) and its spec carry the differences the golden
findings list; each other test plants one more, in memory.
"""

from __future__ import annotations

import copy
import importlib
import json
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("yaml", reason="requires the 'spec' extra")
pytest.importorskip("jsonschema", reason="requires the 'spec' extra")

import ddi_l
from ddi_l.spec import (
    ConformError,
    ConformFinding,
    ConformReport,
    conform,
    load_spec,
    spec_from_data,
)
from ddi_l.spec.model import _read
from ddi_l.spec.semantics import logic_available

HERE = Path(__file__).parent / "fixtures"
FIXTURES = HERE / "spec"
XML = (FIXTURES / "pets_conform.ddi33.xml").read_text("utf-8")
SPEC_DATA = _read(FIXTURES / "pets_conform.spec.yaml")


def _id(n: int) -> str:
    return f"55555555-5555-4555-8555-{n:012d}"


# The semantics each test runs `conform` with (`semantics` below).
_MODE = {"semantics": "syntactic"}


@pytest.fixture(autouse=True, params=["syntactic", "smt"])
def semantics(request: pytest.FixtureRequest) -> str:
    """Every test runs with gates compared by normal form, then exactly."""
    if request.param == "smt" and not logic_available():
        pytest.skip("requires the 'logic' extra")
    _MODE["semantics"] = request.param
    return str(request.param)


def _when(example: str) -> str:
    """The respondent a difference shows in, as exact comparison reports it."""
    if _MODE["semantics"] != "smt":
        return ""
    return f" (they differ when {example})"


def _run(
    xml: str = XML,
    change: Callable[[dict[str, Any]], object] | None = None,
    **options: Any,
) -> ConformReport:
    data = copy.deepcopy(SPEC_DATA)
    if change is not None:
        change(data)
    document = ddi_l.read_ddi(xml.encode("utf-8"))
    options.setdefault("semantics", _MODE["semantics"])
    return conform(document, spec_from_data(data), **options)


# The rules whose findings can be about no element, so have no location.
_NO_ELEMENT = {
    "spec.edit.missing",
    "spec.edit.unverifiable",
    "spec.instrument.missing",
    "spec.item.missing",
    "spec.module.missing",
    "spec.variable.derived-is-lookup",
    "spec.variable.import-type",
    "spec.variable.import-undeclared",
}


def _found(report: ConformReport, rule_id: str) -> list[tuple[str | None, str]]:
    findings = [f for f in report.findings if f.rule_id == rule_id]
    # A finding about an element says where it is.
    assert rule_id in _NO_ELEMENT or all(f.location for f in findings)
    return [(finding.item, finding.message) for finding in findings]


def _fields(
    report: ConformReport, rule_id: str, item: str | None
) -> tuple[str | None, str | None, str | None]:
    """The module, expected and actual of the one ``rule_id`` finding on ``item``."""
    (finding,) = [f for f in report.findings if f.rule_id == rule_id and f.item == item]
    return finding.module, finding.expected, finding.actual


def _rules(report: ConformReport) -> set[str]:
    return {finding.rule_id for finding in report.findings}


def _reference(tag: str, n: int, kind: str) -> str:
    return (
        f"    <{tag}>\n      <r:Agency>int.example</r:Agency>\n"
        f"      <r:ID>{_id(n)}</r:ID>\n      <r:Version>1</r:Version>\n"
        f"      <r:TypeOfObject>{kind}</r:TypeOfObject>\n    </{tag}>\n"
    )


def _replace(xml: str, old: str, new: str) -> str:
    assert old in xml, old
    return xml.replace(old, new, 1)


def _module(data: dict[str, Any], module_id: str) -> dict[str, Any]:
    return next(module for module in data["modules"] if module["id"] == module_id)


def _question(data: dict[str, Any], question_id: str) -> dict[str, Any]:
    return next(
        question
        for module in data["modules"]
        for question in module.get("questions", [])
        if question["id"] == question_id
    )


# ---- The whole report ---------------------------------------------------------------


def test_the_planted_differences_are_found() -> None:
    report = conform(
        ddi_l.open_fragment(FIXTURES / "pets_conform.ddi33.xml"),
        load_spec(FIXTURES / "pets_conform.spec.yaml"),
    )
    golden = json.loads((FIXTURES / "pets_conform.findings.json").read_text("utf-8"))
    # A location is an XPath with lxml and the element's tag without it.
    found = report.as_dict()
    for payload in (found, golden):
        for finding in payload["findings"]:
            finding.pop("location")
    assert found == golden


def test_the_report_summarises_and_fails_by_severity() -> None:
    report = _run()
    assert report.summary == {"error": 7, "warning": 8, "info": 2}
    assert report.instrument == "Instrument 55555555 (Pet survey instrument)"
    assert report.failed("error") and report.failed("info")
    pets = next(module for module in report.modules if module.id == "pets")
    assert (pets.found, pets.required) == (True, True)
    assert pets.as_dict()["findings"] == {"error": 4, "warning": 5, "info": 1}
    clean = _run(
        change=lambda d: d.update(
            modules=[{"id": "household", "questions": [{"id": "PetCount"}]}],
            imported_variables=[],
            derived_variables=[],
            edits=[],
            match={"question_id": ["construct_alias"]},
        )
    )
    assert _rules(clean) == {"spec.module.extra"}
    assert not clean.failed("error") and clean.failed("warning")


def test_a_finding_carries_where_it_is() -> None:
    (finding,) = [f for f in _run().findings if f.rule_id == "spec.domain.length"]
    assert finding.as_dict() == {
        "rule_id": "spec.domain.length",
        "message": "The maximum length of PetName is 40; the spec says 50.",
        "severity": "error",
        "location": finding.location,
        "module": "pets",
        "item": "PetName",
        "expected": "50",
        "actual": "40",
    }
    assert finding.location


def test_a_severity_from_the_spec_replaces_the_default() -> None:
    report = _run(change=lambda d: d.update(severities={"spec.item.extra": "info"}))
    (extra,) = [f for f in report.findings if f.rule_id == "spec.item.extra"]
    assert extra.severity == "info"


# ---- Instruments --------------------------------------------------------------------


def test_an_instrument_the_spec_names_must_exist() -> None:
    report = _run(change=lambda d: d.update(instrument="Nope"))
    assert _found(report, "spec.instrument.missing") == [
        (None, "The file has no instrument named 'Nope'.")
    ]
    assert len(report.findings) == 1 and report.instrument is None
    assert [module.found for module in report.modules] == [False, False, False]


def test_a_file_without_an_instrument() -> None:
    document = ddi_l.open_fragment(HERE / "colectica" / "pets_conditions.ddi33.xml")
    report = conform(document, spec_from_data(copy.deepcopy(SPEC_DATA)))
    assert _found(report, "spec.instrument.missing") == [
        (None, "The file has no instrument.")
    ]


def _two_instruments() -> str:
    start = XML.index("<Fragment", XML.index("<ddi:TopLevelReference"))
    end = XML.index("</Fragment>", start) + len("</Fragment>\n")
    second = XML[start:end].replace(_id(1), _id(99))
    return XML[:end] + second + XML[end:]


def test_two_instruments_are_ambiguous_until_one_is_named() -> None:
    xml = _two_instruments()
    report = _run(xml)
    ((_, message),) = _found(report, "spec.instrument.ambiguous")
    assert message.startswith("2 instruments match: Instrument 55555555")
    assert _rules(_run(xml, instrument="Pet survey instrument")) == {
        "spec.instrument.ambiguous"
    }
    chosen = _run(xml, instrument=_id(99))
    assert "spec.instrument.ambiguous" not in _rules(chosen)
    assert chosen.summary == _run().summary


# ---- Modules ----------------------------------------------------------------------


def test_a_required_module_must_exist() -> None:
    report = _run(change=lambda d: _module(d, "visits").update(required=True))
    assert _found(report, "spec.module.missing") == [
        (None, "The module visits is not in the instrument.")
    ]
    # Its question is still found, elsewhere.
    assert [item for item, _ in _found(report, "spec.item.misplaced")] == ["VisitDate"]


def test_two_sequences_with_a_module_id_are_ambiguous() -> None:
    xml = _replace(XML, ">feedback</r:String>", ">household</r:String>")
    report = _run(xml)
    ((_, message),) = _found(report, "spec.module.ambiguous")
    assert message.startswith("The module household matches 2 sequences")


def test_a_module_depth_limits_where_modules_are() -> None:
    report = _run(change=lambda d: d["match"].update(module_depth=3))
    assert {item for item, _ in _found(report, "spec.module.missing")} == {None}
    assert len(_found(report, "spec.module.missing")) == 2


def test_extra_modules_need_one_depth() -> None:
    report = _run(
        change=lambda d: d.update(
            modules=[
                {"id": "household"},
                {"id": "Pets page"},
            ],
            edits=[],
        )
    )
    assert "spec.module.extra" not in _rules(report)


# ---- Questions and statements ------------------------------------------------------


def test_a_question_that_is_nowhere_is_missing() -> None:
    report = _run(
        change=lambda d: _module(d, "household")["questions"].append({"id": "Rooms"})
    )
    assert _found(report, "spec.item.missing") == [
        ("Rooms", "The question Rooms of module household is not in the instrument.")
    ]
    assert _fields(report, "spec.item.missing", "Rooms") == ("household", None, None)


def test_a_statement_that_is_nowhere_is_missing() -> None:
    report = _run(change=lambda d: _module(d, "pets")["statements"].append("Outro"))
    assert _found(report, "spec.item.missing") == [
        ("Outro", "The statement Outro of module pets is not in the instrument.")
    ]


def test_a_statement_missing_a_language() -> None:
    xml = _replace(
        XML,
        "      <LiteralText>\n"
        '        <Text xml:lang="fr-CA">Parlons maintenant de vos animaux.</Text>\n'
        "      </LiteralText>\n",
        "",
    )
    report = _run(xml)
    assert ("PetsIntro", "The display text of PetsIntro has no fr.") in _found(
        report, "spec.language.missing"
    )
    assert _fields(report, "spec.language.missing", "PetsIntro") == (
        "pets",
        "en, fr",
        "en-CA",
    )


def test_an_id_on_two_constructs_is_ambiguous() -> None:
    xml = _replace(XML, "<r:Alias>PetColour</r:Alias>", "<r:Alias>PetName</r:Alias>")
    report = _run(xml)
    ((item, message),) = _found(report, "spec.item.ambiguous")
    assert item == "PetName"
    assert message.startswith(
        "The question PetName matches 2 constructs by construct_alias: "
        "QuestionConstruct "
    )
    assert message.count(", QuestionConstruct ") == 1
    assert _fields(report, "spec.item.ambiguous", "PetName") == ("pets", None, None)
    # Matched by another source, the id is unique again.
    by_name = _run(xml, change=lambda d: d["match"].update(question_id=["item_name"]))
    assert "spec.item.ambiguous" not in _rules(by_name)


def test_the_first_source_holding_an_id_wins() -> None:
    report = _run(change=lambda d: d["match"].update(question_id=["item_name"]))
    assert _found(report, "spec.item.missing") == [
        (
            "PetCount",
            "The question PetCount of module household is not in the instrument.",
        )
    ]
    assert "spec.item.id-sources-differ" not in _rules(report)


def test_id_sources_that_disagree_on_a_shared_instrument() -> None:
    # In pets_instrument, PetCount2's construct is aliased PetCount2 and its
    # question item PetCount, as PetCount's are.
    document = ddi_l.open_fragment(HERE / "colectica" / "pets_instrument.ddi33.xml")

    def spec(question: str, **match: list[str]) -> Any:
        return spec_from_data(
            {
                "spec": "s",
                "match": match,
                "modules": [{"id": "Pets block", "questions": [{"id": question}]}],
            }
        )

    report = conform(document, spec("PetCount2"), edits="off")
    assert _found(report, "spec.item.id-sources-differ") == [
        (
            "PetCount2",
            "The question PetCount2 is found by its construct_alias; its "
            "item_alias is 'PetCount'.",
        )
    ]
    by_item_alias = conform(
        document, spec("PetCount", question_id=["item_alias"]), edits="off"
    )
    ((item, message),) = _found(by_item_alias, "spec.item.ambiguous")
    assert item == "PetCount" and "matches 2 constructs by item_alias" in message


def test_a_question_outside_every_spec_module_is_misplaced() -> None:
    def change(data: dict[str, Any]) -> None:
        data["modules"] = [
            module for module in data["modules"] if module["id"] != "household"
        ]
        _module(data, "pets")["questions"].append({"id": "PetCount"})

    report = _run(change=change)
    misplaced = dict(_found(report, "spec.item.misplaced"))
    assert misplaced["PetCount"] == (
        "The question PetCount belongs in module pets, but is in no module of the spec."
    )


# ---- Domains ----------------------------------------------------------------------


def test_another_kind_of_domain() -> None:
    def change(data: dict[str, Any]) -> None:
        _question(data, "PetName")["domain"] = {"numeric": {"max": 50}}
        _question(data, "VisitDate")["domain"] = {"date": {"type": "DateTime"}}

    report = _run(change=change)
    assert _found(report, "spec.domain.type") == [
        ("PetName", "The question PetName has a text domain; the spec says numeric."),
        ("VisitDate", "VisitDate is a Date; the spec says DateTime."),
    ]
    assert _fields(report, "spec.domain.type", "PetName") == ("pets", "numeric", "text")


def test_a_domain_of_a_kind_the_spec_has_no_word_for() -> None:
    text = '    <TextDomain blankIsMissingValue="false" maxLength="40" />\n'
    scale = '    <ScaleDomain blankIsMissingValue="false" />\n'
    report = _run(_replace(XML, text, scale))
    assert _found(report, "spec.domain.type") == [
        (
            "PetName",
            "The question PetName has a ScaleDomain domain; the spec says text.",
        )
    ]
    assert _fields(report, "spec.domain.type", "PetName") == (
        "pets",
        "text",
        "ScaleDomain",
    )


def test_a_question_without_a_domain() -> None:
    xml = _replace(
        XML, '    <TextDomain blankIsMissingValue="false" maxLength="40" />\n', ""
    )
    report = _run(xml)
    assert _found(report, "spec.domain.type") == [
        (
            "PetName",
            "The question PetName has no response domain; the spec says text.",
        )
    ]
    assert _fields(report, "spec.domain.type", "PetName") == ("pets", "text", None)


def _without_item(xml: str, marker: str) -> str:
    """``xml`` without the fragment holding ``marker``."""
    start = xml.rindex("<Fragment", 0, xml.index(marker))
    end = xml.index("</Fragment>\n", start) + len("</Fragment>\n")
    return xml[:start] + xml[end:]


def test_a_code_list_not_in_the_file_cannot_be_compared() -> None:
    report = _run(_without_item(XML, "  <CodeList "))
    assert _found(report, "spec.domain.unverifiable") == [
        (
            "PetKind",
            "The domain of PetKind is not compared: the question has a code list "
            "that is not in the file.",
        )
    ]
    assert not {"spec.code.missing", "spec.code.extra"} & _rules(report)


def test_a_referenced_domain_cannot_be_compared() -> None:
    xml = _replace(
        XML,
        '    <TextDomain blankIsMissingValue="false" maxLength="40" />\n',
        _reference("TextDomainReference", 98, "ManagedTextRepresentation"),
    )
    report = _run(xml)
    ((item, message),) = _found(report, "spec.domain.unverifiable")
    assert item == "PetName" and "refers to its domain" in message


def test_a_label_missing_a_language() -> None:
    xml = _replace(XML, '      <r:Content xml:lang="fr-CA">Chien</r:Content>\n', "")
    report = _run(xml)
    assert ("PetKind", "The label of code 1 of PetKind has no fr.") in _found(
        report, "spec.language.missing"
    )


def test_bounds_must_match_whether_included_or_not() -> None:
    report = _run(
        change=lambda d: _question(d, "PetCount")["domain"]["numeric"].update(
            min_inclusive=False
        )
    )
    assert _found(report, "spec.domain.range") == [
        ("PetCount", "The range of PetCount is [0, 20]; the spec says (0, 20]."),
        ("PetAge", "The range of PetAge is [0, 30]; the spec says [0, 40]."),
    ]


def test_a_minimum_length() -> None:
    report = _run(
        change=lambda d: _question(d, "PetName")["domain"]["text"].update(min_length=1)
    )
    assert (
        "PetName",
        "The minimum length of PetName is unspecified; the spec says 1.",
    ) in (_found(report, "spec.domain.length"))


# ---- Gates ------------------------------------------------------------------------


def test_a_gate_that_differs_shows_both_normal_forms() -> None:
    report = _run(change=lambda d: _module(d, "pets").update(gate="1 < PetCount"))
    ((_, message),) = _found(report, "spec.gate.different")
    assert message == (
        "Module pets is gated by PetCount > 0; the spec says PetCount > 1"
        f"{_when('PetCount is 1')}."
    )
    (finding,) = [f for f in report.findings if f.rule_id == "spec.gate.different"]
    assert (finding.expected, finding.actual) == ("PetCount > 1", "PetCount > 0")


def test_an_equivalent_gate_is_not_reported() -> None:
    report = _run(
        change=lambda d: _question(d, "PetName").update(gate="not missing(PetKind)")
    )
    assert not [item for item, _ in _found(report, "spec.gate.different")]


def test_a_module_gate_on_each_page_is_a_scope_difference() -> None:
    report = _run(change=lambda d: _module(d, "pets").update(gate_scope="page"))
    assert _found(report, "spec.gate.scope") == [
        (None, "The gate of module pets wraps the module; the spec says each page.")
    ]
    assert _fields(report, "spec.gate.scope", None) == ("pets", "page", "module")
    assert not _found(report, "spec.gate.missing")[:-1]


def test_a_page_gate_where_the_spec_gates_the_module() -> None:
    xml = XML
    for n, kind in (
        (32, "StatementItem"),
        (33, "QuestionConstruct"),
        (40, "IfThenElse"),
        (60, "QuestionConstruct"),
        (65, "QuestionConstruct"),
    ):
        xml = _replace(xml, _reference("ControlConstructReference", n, kind), "")
    spec: dict[str, Any] = {
        "spec": "s",
        "modules": [
            {"id": "household", "questions": [{"id": "PetCount"}]},
            {
                "id": "Pets page",
                "gate": "PetCount > 1",
                "questions": [{"id": "PetAge"}],
            },
        ],
    }
    report = conform(ddi_l.read_ddi(xml.encode()), spec_from_data(spec), edits="off")
    assert _found(report, "spec.gate.scope") == [
        (
            None,
            "The gate of module Pets page wraps each page; the spec says the module.",
        )
    ]
    assert _fields(report, "spec.gate.scope", None) == ("Pets page", "module", "page")
    # The pets module's own gate is still compared: the spec puts none there.
    assert [f.rule_id for f in report.findings if f.severity != "info"] == [
        "spec.gate.scope",
        "spec.gate.extra",
    ]
    scoped = copy.deepcopy(spec)
    scoped["modules"][1]["gate_scope"] = "page"
    report = conform(ddi_l.read_ddi(xml.encode()), spec_from_data(scoped), edits="off")
    assert [f.rule_id for f in report.findings if f.severity != "info"] == [
        "spec.gate.extra"
    ]


def test_a_gate_with_an_unknown_operator_cannot_be_compared() -> None:
    xml = _replace(
        XML,
        f'"Subject":"urn:ddi:int.example:{_id(21)}:1","Operator":3',
        f'"Subject":"urn:ddi:int.example:{_id(21)}:1","Operator":99',
    )
    report = _run(xml)
    assert _found(report, "spec.gate.unverifiable") == [
        (
            None,
            "The gate of module pets cannot be compared: operator code 99 is not "
            "known.",
        )
    ]


def test_a_gate_testing_for_don_t_know_cannot_be_compared() -> None:
    xml = _replace(
        XML,
        f'"Subject":"urn:ddi:int.example:{_id(21)}:1","Operator":3',
        f'"Subject":"urn:ddi:int.example:{_id(21)}:1","Operator":16',
    )
    report = _run(xml)
    assert _found(report, "spec.gate.unverifiable") == [
        (
            None,
            "The gate of module pets cannot be compared: DONT_KNOW tests for a "
            "don't-know answer, which the expression language has no word for.",
        )
    ]


def test_native_code_this_reader_does_not_know_cannot_be_compared() -> None:
    xml = _replace(
        XML,
        "NOT ({{PetKind}} = EMPTY) AND NOT ({{PetKind}} = REFUSAL)",
        "{{PetKind}} IN [1, 2]",
    )
    report = _run(xml)
    assert _found(report, "spec.gate.unverifiable") == [
        (
            "PetName",
            "The gate of question PetName cannot be compared: its Blaise code does "
            "not read: Unexpected character '['.",
        )
    ]


def test_without_the_dialect_a_native_gate_reads_differently() -> None:
    report = _run(change=lambda d: d.pop("blaise"))
    ((item, message),) = _found(report, "spec.gate.different")
    assert item == "PetName" and "EMPTY" in message


_ELSE = _reference("ElseConstructReference", 65, "QuestionConstruct")
_THEN_52 = (
    f"      <r:ID>{_id(52)}</r:ID>\n      <r:Version>1</r:Version>\n"
    "      <r:TypeOfObject>Sequence</r:TypeOfObject>\n    </ThenConstructReference>\n"
)
_ELSE_IF = (
    "    <ElseIf>\n      <IfCondition>\n        <r:Command>\n"
    "          <r:ProgramLanguage>Blaise</r:ProgramLanguage>\n"
    "          <r:CommandContent>{{PetCount}} = 1</r:CommandContent>\n"
    "        </r:Command>\n      </IfCondition>\n"
    + _reference("ThenConstructReference", 65, "QuestionConstruct")
    .replace("\n    ", "\n      ")
    .replace("    <Then", "      <Then", 1)
    + "    </ElseIf>\n"
)


def _branch(xml_branch: str) -> str:
    xml = _replace(
        XML, _reference("ControlConstructReference", 65, "QuestionConstruct"), ""
    )
    return _replace(xml, _THEN_52, _THEN_52 + xml_branch)


@pytest.mark.parametrize(
    ("branch", "gate", "different"),
    [
        (_ELSE, "not PetCount > 1", False),
        # Not recognised as the same: they differ when PetCount has no answer.
        (_ELSE, "PetCount <= 1", True),
        (_ELSE_IF, "PetCount = 1 and not PetCount > 1", False),
    ],
)
def test_else_and_else_if_branches_gate_with_what_came_before(
    branch: str, gate: str, different: bool
) -> None:
    def change(data: dict[str, Any]) -> None:
        _module(data, "pets")["questions"].append({"id": "PetColour", "gate": gate})

    report = _run(_branch(branch), change=change)
    differences = [item for item, _ in _found(report, "spec.gate.different")]
    assert ("PetColour" in differences) is different


# ---- Edits ----------------------------------------------------------------------------


def _later_edit(data: dict[str, Any]) -> None:
    """A second edit, which no edit check is: missing after whatever the first is."""
    data["edits"].append({**data["edits"][0], "id": "later"})


def test_edits_are_not_verifiable_by_default() -> None:
    report = _run()
    assert _found(report, "spec.edit.unverifiable") == [
        ("age_range", "The edit age_range: not verifiable (edit storage unknown).")
    ]
    assert _fields(report, "spec.edit.unverifiable", "age_range") == (
        "pets",
        "PetAge > 30",
        None,
    )
    assert not [f for f in _run(edits="off").findings if "edit" in f.rule_id]


def test_strict_edits_compare_the_condition() -> None:
    report = _run(edits="strict")
    assert _found(report, "spec.edit.different") == [
        (
            "age_range",
            "The edit age_range fires on PetAge > 25; the spec says PetAge > 30"
            f"{_when('PetAge is 30')}.",
        )
    ]
    assert _fields(report, "spec.edit.different", "age_range") == (
        "pets",
        "PetAge > 30",
        "PetAge > 25",
    )

    def renamed(data: dict[str, Any]) -> None:
        _later_edit(data)
        data["edits"][0]["id"] = "other"

    report = _run(edits="strict", change=renamed)
    assert _found(report, "spec.edit.missing") == [
        ("other", "No edit check is other."),
        ("later", "No edit check is later."),
    ]
    assert _fields(report, "spec.edit.missing", "other") == (
        "pets",
        "PetAge > 30",
        None,
    )
    agreed = _run(
        edits="strict", change=lambda d: d["edits"][0].update(when="25 < PetAge")
    )
    assert not [f for f in agreed.findings if "edit" in f.rule_id]


def test_strict_edits_need_to_know_where_edits_are() -> None:
    with pytest.raises(ConformError, match="needs the spec's match.edits"):
        _run(edits="strict", change=lambda d: d["match"].pop("edits"))


def test_an_edit_check_marked_otherwise_is_not_one() -> None:
    report = _run(
        edits="strict",
        change=lambda d: d["match"]["edits"].update(value="Something else"),
    )
    assert [item for item, _ in _found(report, "spec.edit.missing")] == ["age_range"]


def test_an_edit_check_that_does_not_read() -> None:
    xml = _replace(XML, '"Synopsis":"PetAge Greater than 25"', '"Synopsis":')
    report = _run(xml, edits="strict", change=_later_edit)
    ((item, message),) = _found(report, "spec.edit.unverifiable")
    assert item == "age_range" and "Neutral command is not valid JSON" in message
    assert _fields(report, "spec.edit.unverifiable", "age_range") == (
        "pets",
        "PetAge > 30",
        None,
    )
    assert [item for item, _ in _found(report, "spec.edit.missing")] == ["later"]


# ---- Variables --------------------------------------------------------------------------


def test_lookup_types_are_compared_only_when_mapped() -> None:
    report = _run(change=lambda d: d["match"].pop("lookup_types"))
    assert "spec.variable.import-type" not in _rules(report)
    assert _rules(report) >= {
        "spec.variable.import-undeclared",
        "spec.variable.derived-is-lookup",
    }


# ---- Options --------------------------------------------------------------------------


def test_one_module_at_a_time() -> None:
    report = _run(module="pets")
    assert {finding.module for finding in report.findings} == {"pets"}
    assert [module.id for module in report.modules] == ["pets"]
    assert not {"spec.module.extra", "spec.variable.import-undeclared"} & _rules(report)
    assert [item for item, _ in _found(report, "spec.edit.unverifiable")] == [
        "age_range"
    ]
    household = _run(module="household")
    assert not _found(household, "spec.edit.unverifiable")


@pytest.mark.parametrize(
    ("options", "message"),
    [
        (
            {"module": "nope"},
            "The spec has no module 'nope'; it has household, pets, visits.",
        ),
        ({"edits": "loud"}, "edits must be one of off, info, strict, not 'loud'."),
        (
            {"semantics": "exact"},
            "semantics must be one of syntactic, smt, not 'exact'.",
        ),
    ],
)
def test_options_that_cannot_run(options: dict[str, Any], message: str) -> None:
    with pytest.raises(ConformError) as caught:
        _run(**options)
    assert str(caught.value) == message


# ---- Exact comparison --------------------------------------------------------------


def _pets_gate(gate: str) -> Callable[[dict[str, Any]], None]:
    def change(data: dict[str, Any]) -> None:
        _module(data, "pets")["gate"] = gate

    return change


def _module_gate_findings(report: ConformReport) -> list[ConformFinding]:
    return [
        finding
        for finding in report.findings
        if finding.rule_id == "spec.gate.different" and finding.item is None
    ]


def test_gates_written_differently_that_always_agree(semantics: str) -> None:
    # PetCount is a whole number (decimals: 0): > 0 is >= 1.
    report = _run(change=_pets_gate("PetCount >= 1"))

    assert len(_module_gate_findings(report)) == (0 if semantics == "smt" else 1)


def test_a_difference_comes_with_a_respondent_it_shows_in(semantics: str) -> None:
    (finding,) = _module_gate_findings(_run(change=_pets_gate("PetCount > 1")))

    if semantics == "smt":
        assert finding.example == "PetCount is 1"
        assert finding.as_dict()["example"] == "PetCount is 1"
    else:
        assert finding.example is None
        assert "example" not in finding.as_dict()


def test_a_name_the_spec_types_is_read_as_that_type() -> None:
    # Without the domain, PetCount may be 0.5: > 0 and >= 1 differ.
    def untyped(data: dict[str, Any]) -> None:
        _pets_gate("PetCount >= 1")(data)
        del _question(data, "PetCount")["domain"]

    (finding,) = _module_gate_findings(_run(change=untyped))

    if _MODE["semantics"] == "smt":
        assert finding.example is not None
        name, value = finding.example.split(" is ")
        assert name == "PetCount"
        assert 0 < Fraction(value) < 1
    else:
        assert finding.example is None


def test_exact_comparison_needs_the_logic_extra(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("ddi_l.spec.conform")
    monkeypatch.setattr(module, "logic_available", lambda: False)

    with pytest.raises(ConformError, match=r"needs the logic extra"):
        _run(semantics="smt")
    # By default it compares normal forms, as without the extra.
    report = _run(change=_pets_gate("PetCount >= 1"), semantics=None)
    assert len(_module_gate_findings(report)) == 1


# ---- What cannot be read ----------------------------------------------------------------


def test_a_question_with_several_domains_is_not_compared() -> None:
    xml = _replace(
        XML,
        '    <TextDomain blankIsMissingValue="false" maxLength="40" />\n',
        '    <TextDomain blankIsMissingValue="false" maxLength="40" />\n'
        '    <TextDomain blankIsMissingValue="false" maxLength="50" />\n',
    )
    report = _run(xml)
    ((item, message),) = _found(report, "spec.domain.unverifiable")
    assert (item, message) == (
        "PetName",
        "The domain of PetName is not compared: the question has several domains.",
    )
    assert _fields(report, "spec.domain.unverifiable", "PetName") == (
        "pets",
        None,
        None,
    )


def test_a_construct_whose_question_is_not_in_the_file() -> None:
    xml = _without_item(XML, f"<r:URN>urn:ddi:int.example:{_id(46)}:1</r:URN>")
    report = _run(xml)
    assert _found(report, "spec.domain.unverifiable") == [
        ("PetName", "The question PetName asks no question in the file.")
    ]


def test_an_edit_on_two_edit_checks_is_ambiguous() -> None:
    start = XML.rindex("<Fragment", 0, XML.index("<r:AttributeKey>kind"))
    end = XML.index("</Fragment>\n", start) + len("</Fragment>\n")
    copied = XML[start:end].replace(_id(85), _id(87)).replace(_id(86), _id(88))
    xml = _replace(
        XML[:end] + copied + XML[end:],
        _reference("ControlConstructReference", 85, "ComputationItem"),
        _reference("ControlConstructReference", 85, "ComputationItem")
        + _reference("ControlConstructReference", 87, "ComputationItem"),
    )
    report = _run(xml, edits="strict", change=_later_edit)
    assert _found(report, "spec.item.ambiguous") == [
        (
            "age_range",
            "The edit age_range matches 2 edit checks: ComputationItem 55555555 "
            "(age_range), ComputationItem 55555555 (age_range).",
        )
    ]
    assert _fields(report, "spec.item.ambiguous", "age_range") == ("pets", None, None)
    assert [item for item, _ in _found(report, "spec.edit.missing")] == ["later"]


@pytest.mark.parametrize(
    ("language", "reason"),
    [
        ("Blaise5DataLookup", "it is a data lookup"),
        ("R", "it is R code"),
    ],
)
def test_a_gate_that_is_not_a_condition_cannot_be_compared(
    language: str, reason: str
) -> None:
    xml = _replace(
        XML,
        "<r:ProgramLanguage>Neutral</r:ProgramLanguage>\n        <r:CommandContent>"
        '{"LogicGroups":[{"GroupBooleanType":0,"Statements":[{"StatementBooleanType"'
        f':0,"Subject":"urn:ddi:int.example:{_id(21)}',
        f"<r:ProgramLanguage>{language}</r:ProgramLanguage>\n        <r:CommandContent>"
        '{"LogicGroups":[{"GroupBooleanType":0,"Statements":[{"StatementBooleanType"'
        f':0,"Subject":"urn:ddi:int.example:{_id(21)}',
    )
    assert _found(_run(xml), "spec.gate.unverifiable") == [
        (None, f"The gate of module pets cannot be compared: {reason}.")
    ]


def test_a_gate_without_a_command_cannot_be_compared() -> None:
    start = XML.index("<r:Command>", XML.index(">Name gate<"))
    end = XML.index("</r:Command>", start) + len("</r:Command>")
    report = _run(XML[:start] + XML[end:])
    assert _found(report, "spec.gate.unverifiable") == [
        (
            "PetName",
            "The gate of question PetName cannot be compared: it holds no condition.",
        )
    ]


def test_a_subject_bound_to_nothing_known_cannot_be_compared() -> None:
    xml = _replace(
        XML,
        "<r:Alias>PetCount</r:Alias>\n    </r:InParameter>\n    <IfCondition>",
        "<r:Alias>Pets</r:Alias>\n    </r:InParameter>\n    <IfCondition>",
    )
    xml = _replace(
        xml,
        f"<r:ID>{_id(21)}</r:ID>\n        <r:Version>1</r:Version>\n"
        "        <r:TypeOfObject>InParameter</r:TypeOfObject>",
        f"<r:ID>{_id(29)}</r:ID>\n        <r:Version>1</r:Version>\n"
        "        <r:TypeOfObject>InParameter</r:TypeOfObject>",
    )
    ((_, message),) = _found(_run(xml), "spec.gate.unverifiable")
    assert message.endswith("is bound to no known question.")


def test_native_arithmetic_reads_back() -> None:
    xml = _replace(
        XML,
        "NOT ({{PetKind}} = EMPTY) AND NOT ({{PetKind}} = REFUSAL)",
        "-{{PetKind}} &lt; -1",
    )
    report = _run(
        xml, change=lambda d: _question(d, "PetName").update(gate="-PetKind < -1")
    )
    assert not _found(report, "spec.gate.different")


def test_a_cycle_and_a_dangling_reference_are_not_followed() -> None:
    cycle = _reference("ControlConstructReference", 30, "Sequence")
    dangling = _reference("ControlConstructReference", 97, "Sequence")
    xml = _replace(
        XML,
        _reference("ControlConstructReference", 65, "QuestionConstruct"),
        _reference("ControlConstructReference", 65, "QuestionConstruct")
        + cycle
        + dangling,
    )
    assert _run(xml).summary == _run().summary


def test_bounds_that_are_not_numbers_and_decimal_bounds() -> None:
    xml = _replace(
        XML,
        '<r:High isInclusive="true">30</r:High>',
        '<r:High isInclusive="true">old</r:High>',
    )
    report = _run(
        xml,
        change=lambda d: _question(d, "PetAge")["domain"]["numeric"].update(min=0.5),
    )
    assert (
        "PetAge",
        "The range of PetAge is [0, ]; the spec says [0.5, 40].",
    ) in _found(report, "spec.domain.range")


def test_a_question_without_text_has_no_language_to_miss() -> None:
    start = XML.index("<QuestionText>", XML.index(f"<r:ID>{_id(56)}</r:ID>"))
    end = XML.index("</QuestionText>", start) + len("</QuestionText>")
    report = _run(XML[:start] + XML[end:])
    assert "PetAge" not in [item for item, _ in _found(report, "spec.language.missing")]


# ---- Documentation ---------------------------------------------------------------

DOCS = Path(__file__).resolve().parents[1] / "docs"


@pytest.mark.skipif(not DOCS.is_dir(), reason="docs/ is not shipped in the sdist")
@pytest.mark.parametrize("language", ["en", "fr"])
def test_every_rule_is_documented_with_its_severity(language: str) -> None:
    from ddi_l.spec import RULES

    text = (DOCS / f"spec-conformance.{language}.md").read_text("utf-8")
    missing = [
        rule.rule_id
        for rule in RULES
        if f"| `{rule.rule_id}` | {rule.severity} |" not in text
    ]
    assert missing == []


def test_a_quoted_plain_number_in_a_gate_is_that_number() -> None:
    # A Neutral condition stores "0" and 0 alike.
    report = _run(change=lambda d: _module(d, "pets").update(gate='PetCount > "0"'))
    assert not _found(report, "spec.gate.different")
    report = _run(change=lambda d: _module(d, "pets").update(gate='PetCount > "00"'))
    assert _found(report, "spec.gate.different")


# ---- Review fixes: conformance --------------------------------------------------------


def _xml_without(*references: tuple[int, str]) -> str:
    xml = XML
    for n, kind in references:
        xml = _replace(xml, _reference("ControlConstructReference", n, kind), "")
    return xml


def test_a_then_branch_reads_only_its_own_condition() -> None:
    # C6: an unreadable ElseIf does not make the Then branch unverifiable.
    else_if = _ELSE_IF.replace("Blaise", "R")
    report = _run(_branch(else_if))
    assert not _found(report, "spec.gate.unverifiable")
    assert [item for item, _ in _found(report, "spec.gate.extra")] == ["PetAge"]


def test_an_item_on_several_paths() -> None:
    # C7: PetKind asked in household too: not misplaced, but extra there.
    xml = _replace(
        XML,
        _reference("ControlConstructReference", 12, "QuestionConstruct"),
        _reference("ControlConstructReference", 12, "QuestionConstruct")
        + _reference("ControlConstructReference", 33, "QuestionConstruct"),
    )
    report = _run(xml)
    assert not [i for i, _ in _found(report, "spec.item.misplaced") if i == "PetKind"]
    assert (
        "PetKind",
        "Module household has the question QuestionConstruct "
        "55555555 (PetKind), which the spec lists in module pets.",
    ) in _found(report, "spec.item.extra")
    # PetAge under its gate and again, ungated, on the same page.
    xml = _replace(
        XML,
        _reference("ControlConstructReference", 60, "QuestionConstruct"),
        _reference("ControlConstructReference", 53, "QuestionConstruct")
        + _reference("ControlConstructReference", 60, "QuestionConstruct"),
    )
    report = _run(xml)
    assert (
        "PetAge",
        "The gate of question PetAge cannot be compared: it is "
        "reached by 2 paths with different gates.",
    ) in _found(report, "spec.gate.unverifiable")
    assert "PetAge" not in [i for i, _ in _found(report, "spec.gate.extra")]
    # PetAge in the Then and in the Else of the same gate.
    report = _run(
        _replace(
            XML,
            _THEN_52,
            _THEN_52 + _reference("ElseConstructReference", 53, "QuestionConstruct"),
        )
    )
    assert "PetAge" in [i for i, _ in _found(report, "spec.gate.unverifiable")]
    # Two paths with the same gate (twice in one Then) are compared as one.
    twice = _reference("ControlConstructReference", 53, "QuestionConstruct")
    report = _run(_replace(XML, twice, twice + twice))
    assert "PetAge" not in [i for i, _ in _found(report, "spec.gate.unverifiable")]
    assert "PetAge" in [i for i, _ in _found(report, "spec.gate.extra")]


def test_bindings_come_from_the_latest_version() -> None:
    # C8: an older version of the root sequence bound the Pets gate elsewhere.
    marker = f"<r:URN>urn:ddi:int.example:{_id(2)}:1</r:URN>"
    start = XML.rindex("<Fragment", 0, XML.index(marker))
    end = XML.index("</Fragment>\n", start) + len("</Fragment>\n")
    current = XML[start:end]
    old_binding = (
        f"<r:ID>{_id(13)}</r:ID>\n        <r:Version>1</r:Version>\n"
        "        <r:TypeOfObject>OutParameter</r:TypeOfObject>\n"
        "      </r:SourceParameterReference>\n"
        '      <r:TargetParameterReference lateBound="true">\n'
        f"        <r:Agency>int.example</r:Agency>\n        <r:ID>{_id(21)}</r:ID>"
    )
    older = _replace(current, old_binding, old_binding.replace(_id(13), _id(34), 1))
    newer = current.replace(f"{_id(2)}:1</r:URN>", f"{_id(2)}:2</r:URN>").replace(
        f"<r:ID>{_id(2)}</r:ID>\n    <r:Version>1</r:Version>",
        f"<r:ID>{_id(2)}</r:ID>\n    <r:Version>2</r:Version>",
    )
    for xml in (
        XML[:start] + older + newer + XML[end:],
        XML[:start] + newer + older + XML[end:],
    ):
        assert not [i for i, _ in _found(_run(xml), "spec.gate.different") if i is None]


def test_an_ambiguous_module_does_not_cascade() -> None:
    # C9: the pets page is also named pets.
    xml = _replace(XML, ">Pets page</r:String>", ">pets</r:String>")
    report = _run(xml)
    assert [i for i, _ in _found(report, "spec.module.ambiguous")] == [None]
    assert "pets" not in [i for i, _ in _found(report, "spec.module.extra")]
    for rule in ("spec.item.misplaced", "spec.gate.extra", "spec.gate.different"):
        assert not [
            f for f in report.findings if f.rule_id == rule and f.module == "pets"
        ], rule


def test_a_gate_bound_to_a_question_the_spec_does_not_list() -> None:
    # C10: the Pets gate's input (alias PetCount) is bound to PetColour.
    old = (
        f"<r:ID>{_id(13)}</r:ID>\n        <r:Version>1</r:Version>\n"
        "        <r:TypeOfObject>OutParameter</r:TypeOfObject>\n"
        "      </r:SourceParameterReference>\n"
        '      <r:TargetParameterReference lateBound="true">\n'
        f"        <r:Agency>int.example</r:Agency>\n        <r:ID>{_id(21)}</r:ID>"
    )
    xml = _replace(XML, old, old.replace(_id(13), _id(66), 1))
    assert _found(_run(xml), "spec.gate.different")[0] == (
        None,
        "Module pets is gated by PetColour > 0; the spec says PetCount > 0"
        f"{_when('PetColour is answered with no value and PetCount is 1')}.",
    )


def _mixed(inner_text: str) -> str:
    code = (
        '    <CodeDomain blankIsMissingValue="false">\n      <r:CodeListReference>\n'
        "        <r:Agency>int.example</r:Agency>\n"
        f"        <r:ID>{_id(90)}</r:ID>\n        <r:Version>1</r:Version>\n"
        "        <r:TypeOfObject>CodeList</r:TypeOfObject>\n      </r:CodeListReference>\n"
        "    </CodeDomain>\n"
    )
    mixed = (
        "    <StructuredMixedResponseDomain>\n      <ResponseDomainInMixed>\n"
        + code
        + "      </ResponseDomainInMixed>\n      <ResponseDomainInMixed>\n"
        + inner_text
        + "      </ResponseDomainInMixed>\n    </StructuredMixedResponseDomain>\n"
    )
    return _replace(XML, code, mixed)


def test_a_mixed_domain_compares_its_one_domain_of_the_kind() -> None:
    # C11
    report = _run(_mixed('        <TextDomain blankIsMissingValue="false" />\n'))
    assert not _found(report, "spec.domain.type")
    assert [i for i, _ in _found(report, "spec.code.missing")] == ["PetKind"]
    report = _run(_mixed('        <CodeDomain blankIsMissingValue="false" />\n'))
    assert (
        "PetKind",
        "The domain of PetKind is not compared: the question has a "
        "mixed domain with 2 code domains.",
    ) in _found(report, "spec.domain.unverifiable")


def test_an_infinite_bound() -> None:
    # C12
    xml = _replace(
        XML,
        '<r:High isInclusive="true">30</r:High>',
        '<r:HighDouble isInclusive="true">INF</r:HighDouble>',
    )
    ((_, message),) = [
        f for f in _found(_run(xml), "spec.domain.range") if f[0] == "PetAge"
    ]
    assert message == "The range of PetAge is [0, INF]; the spec says [0, 40]."


def test_a_second_construct_asking_a_listed_question_is_extra() -> None:
    # C13: another construct asks PetCount's question item, on the pets page.
    marker = f"<r:URN>urn:ddi:int.example:{_id(12)}:1</r:URN>"
    start = XML.rindex("<Fragment", 0, XML.index(marker))
    end = XML.index("</Fragment>\n", start) + len("</Fragment>\n")
    copied = (
        XML[start:end]
        .replace(_id(12), _id(99))
        .replace(_id(13), _id(98))
        .replace(">PetCount<", ">PetCountAgain<")
    )
    xml = _replace(
        XML[:end] + copied + XML[end:],
        _reference("ControlConstructReference", 60, "QuestionConstruct"),
        _reference("ControlConstructReference", 60, "QuestionConstruct")
        + _reference("ControlConstructReference", 99, "QuestionConstruct"),
    )
    report = _run(xml)
    assert "PetCountAgain" in [i for i, _ in _found(report, "spec.item.extra")]
    assert not _found(report, "spec.item.ambiguous")


def test_strict_edits_come_from_the_instrument() -> None:
    # C14: a second instrument's age_range edit is not this one's.
    start = XML.rindex("<Fragment", 0, XML.index("<r:AttributeKey>kind"))
    end = XML.index("</Fragment>\n", start) + len("</Fragment>\n")
    copied = XML[start:end].replace(_id(85), _id(87)).replace(_id(86), _id(88))
    report = _run(XML[:end] + copied + XML[end:], edits="strict")
    assert not _found(report, "spec.item.ambiguous")
    assert [i for i, _ in _found(report, "spec.edit.different")] == ["age_range"]


def test_one_module_of_a_one_module_spec() -> None:
    # C15: --module leaves out extra modules and variables even then.
    def one(data: dict[str, Any]) -> None:
        data["modules"] = [_module(data, "household")]
        data["edits"] = []

    report = _run(change=one, module="household")
    assert not [f for f in report.findings if f.rule_id.startswith("spec.module.extra")]
    assert not [f for f in report.findings if f.rule_id.startswith("spec.variable")]


def _pets_page_spec() -> dict[str, Any]:
    return {
        "spec": "s",
        "modules": [
            {"id": "household", "questions": [{"id": "PetCount"}]},
            {
                "id": "Pets page",
                "gate": "PetCount > 1",
                "questions": [{"id": "PetAge"}, {"id": "PetName"}],
            },
        ],
    }


def test_a_page_gate_with_an_unreadable_gate_below_it() -> None:
    # C16: the Name gate (in R) sits inside the Age gate, next to PetAge.
    xml = _xml_without(
        (32, "StatementItem"),
        (33, "QuestionConstruct"),
        (40, "IfThenElse"),
        (60, "QuestionConstruct"),
        (65, "QuestionConstruct"),
    )
    xml = _replace(
        xml,
        _reference("ControlConstructReference", 53, "QuestionConstruct"),
        _reference("ControlConstructReference", 53, "QuestionConstruct")
        + _reference("ControlConstructReference", 40, "IfThenElse"),
    )
    xml = xml.replace(
        "<r:ProgramLanguage>Blaise</r:ProgramLanguage>",
        "<r:ProgramLanguage>R</r:ProgramLanguage>",
    )
    report = conform(
        ddi_l.read_ddi(xml.encode()), spec_from_data(_pets_page_spec()), edits="off"
    )
    rules = [f.rule_id for f in report.findings if f.severity != "info"]
    assert "spec.gate.scope" in rules
    assert ("PetAge", "spec.gate.extra") not in [
        (f.item, f.rule_id) for f in report.findings
    ]


def test_inclusive_zero_is_false() -> None:
    # C19
    xml = _replace(
        XML, '<r:Low isInclusive="true">0</r:Low>', '<r:Low isInclusive="0">0</r:Low>'
    )
    report = _run(
        xml,
        change=lambda d: _question(d, "PetCount")["domain"]["numeric"].update(
            min_inclusive=False
        ),
    )
    assert "PetCount" not in [i for i, _ in _found(report, "spec.domain.range")]


def test_a_referenced_domain_is_compared() -> None:
    # C18
    managed = f"""<Fragment xmlns:r="ddi:reusable:3_3" xmlns="ddi:instance:3_3">
  <r:ManagedTextRepresentation isUniversallyUnique="true" versionDate="2026-03-01T10:00:00.0000000Z" maxLength="40">
    <r:URN>urn:ddi:int.example:{_id(120)}:1</r:URN>
    <r:Agency>int.example</r:Agency>
    <r:ID>{_id(120)}</r:ID>
    <r:Version>1</r:Version>
  </r:ManagedTextRepresentation>
</Fragment>
"""
    xml = _replace(
        XML,
        '    <TextDomain blankIsMissingValue="false" maxLength="40" />\n',
        _reference("TextDomainReference", 120, "ManagedTextRepresentation"),
    )
    report = _run(
        _replace(xml, "</ddi:FragmentInstance>", managed + "</ddi:FragmentInstance>")
    )
    assert not _found(report, "spec.domain.unverifiable")
    assert _found(report, "spec.domain.length") == [
        ("PetName", "The maximum length of PetName is 40; the spec says 50.")
    ]
    report = _run(xml)  # the managed representation is not in the file
    assert _found(report, "spec.domain.unverifiable") == [
        (
            "PetName",
            "The domain of PetName is not compared: the question refers to its "
            "domain (TextDomainReference), which is not in the file.",
        )
    ]


@pytest.mark.parametrize(
    "statement",
    [
        '{"StatementBooleanType":null,"Subject":"S","Operator":3,"Value":{"Value":"0"}}',
        '{"StatementBooleanType":0,"Subject":"S","Operator":3.5,"Value":{"Value":"0"}}',
        '{"StatementBooleanType":0,"Subject":"S","Operator":true,"Value":{"Value":"0"}}',
    ],
)
def test_malformed_neutral_is_unverifiable(statement: str) -> None:
    # C20
    original = (
        '{"LogicGroups":[{"GroupBooleanType":0,"Statements":[{"StatementBooleanType":0,'
        f'"Subject":"urn:ddi:int.example:{_id(21)}:1","Operator":3,'
        '"Value":{"Value":"0","ValueNotNeeded":false,"SelectedCodes":[]}}]}],'
        '"Synopsis":"PetCount Greater than 0","Version":1}'
    )
    statement = statement.replace('"S"', f'"urn:ddi:int.example:{_id(21)}:1"')
    broken = '{"LogicGroups":[{"GroupBooleanType":0,"Statements":[' + statement + "]}]}"
    report = _run(_replace(XML, original, broken))
    assert [i for i, _ in _found(report, "spec.gate.unverifiable")] == [None]


@pytest.mark.parametrize(
    ("gate_alias", "output_alias", "different"),
    [
        ("Adults", "Adults", False),  # the gate's alias names the spec variable
        ("Kids", "Adults", False),  # the output's alias does
        ("Kids", "Other", True),  # neither: read as PetCount.Other
    ],
)
def test_one_output_of_a_question_with_several(
    gate_alias: str, output_alias: str, different: bool
) -> None:
    # R7: PetCount's construct has a second output, which the Pets gate reads.
    second = (
        '    <r:OutParameter isUniversallyUnique="true">\n'
        f"      <r:URN>urn:ddi:int.example:{_id(14)}:1</r:URN>\n"
        "      <r:Agency>int.example</r:Agency>\n"
        f"      <r:ID>{_id(14)}</r:ID>\n"
        "      <r:Version>1</r:Version>\n"
        f"      <r:Alias>{output_alias}</r:Alias>\n"
        "    </r:OutParameter>\n"
    )
    first_end = (
        f"<r:ID>{_id(13)}</r:ID>\n      <r:Version>1</r:Version>\n"
        "      <r:Alias>PetCount</r:Alias>\n    </r:OutParameter>\n"
    )
    xml = _replace(XML, first_end, first_end + second)
    binding = (
        f"<r:ID>{_id(13)}</r:ID>\n        <r:Version>1</r:Version>\n"
        "        <r:TypeOfObject>OutParameter</r:TypeOfObject>\n"
        "      </r:SourceParameterReference>\n"
        '      <r:TargetParameterReference lateBound="true">\n'
        f"        <r:Agency>int.example</r:Agency>\n        <r:ID>{_id(21)}</r:ID>"
    )
    xml = _replace(xml, binding, binding.replace(_id(13), _id(14), 1))
    xml = _replace(
        xml,
        f"<r:ID>{_id(21)}</r:ID>\n      <r:Version>1</r:Version>\n"
        "      <r:Alias>PetCount</r:Alias>",
        f"<r:ID>{_id(21)}</r:ID>\n      <r:Version>1</r:Version>\n"
        f"      <r:Alias>{gate_alias}</r:Alias>",
    )

    def change(data: dict[str, Any]) -> None:
        data["derived_variables"].append({"name": "Adults", "type": "numeric"})
        _module(data, "pets")["gate"] = "Adults > 0"

    found = [i for i, _ in _found(_run(xml, change=change), "spec.gate.different")]
    assert (None in found) is different


# ---- Second review --------------------------------------------------------------


@pytest.mark.parametrize(
    "gated_first", [True, False], ids=["gated-first", "direct-first"]
)
def test_a_module_reached_twice_reads_each_path_from_the_module(
    gated_first: bool,
) -> None:
    gate = _reference("ControlConstructReference", 20, "IfThenElse")
    pets = _reference("ControlConstructReference", 30, "Sequence")
    report = _run(_replace(XML, gate, gate + pets if gated_first else pets + gate))
    assert not _found(report, "spec.gate.unverifiable")
    assert [item for item, _ in _found(report, "spec.gate.extra")] == ["PetAge"]


@pytest.mark.parametrize(
    ("operator", "reason"), [("true", "expected an integer code, got true")]
)
def test_an_unreadable_gate_on_another_path_is_reported(
    operator: str, reason: str
) -> None:
    then_name = _reference("ControlConstructReference", 43, "QuestionConstruct")
    age = _reference("ControlConstructReference", 53, "QuestionConstruct")
    xml = _replace(XML, then_name, then_name + age)
    age_json = '"Operator":3,"Value":{"Value":"1"'
    xml = _replace(xml, age_json, age_json.replace("3", operator, 1))
    report = _run(
        xml, change=lambda d: _question(d, "PetAge").update(gate="answered(PetKind)")
    )
    ((item, message),) = _found(report, "spec.gate.unverifiable")
    assert item == "PetAge"
    assert message.endswith(f"the gate on one cannot be read (Operator: {reason}).")


def test_only_the_latest_version_binds_even_when_it_has_no_bindings() -> None:
    import re

    marker = f"<r:URN>urn:ddi:int.example:{_id(2)}:1</r:URN>"
    start = XML.rindex("<Fragment", 0, XML.index(marker))
    end = XML.index("</Fragment>\n", start) + len("</Fragment>\n")
    current = XML[start:end]
    bindings = re.findall(r"    <r:Binding>.*?</r:Binding>\n", current, re.S)
    # Version 1 binds the Pets gate's input to PetKind; version 2 binds nothing
    # (its bindings moved into the gates themselves).
    older = current.replace(bindings[0], bindings[0].replace(_id(13), _id(34), 1))
    newer = current
    for binding in bindings:
        newer = newer.replace(binding, "")
    newer = newer.replace(f"{_id(2)}:1</r:URN>", f"{_id(2)}:2</r:URN>").replace(
        f"<r:ID>{_id(2)}</r:ID>\n    <r:Version>1</r:Version>",
        f"<r:ID>{_id(2)}</r:ID>\n    <r:Version>2</r:Version>",
    )
    xml = XML[:start] + older + newer + XML[end:]
    for holder, binding in zip((20, 40, 50, 85), bindings, strict=True):
        head = f"<r:URN>urn:ddi:int.example:{_id(holder)}:1</r:URN>"
        close = xml.index("</r:InParameter>\n", xml.index(head)) + len(
            "</r:InParameter>\n"
        )
        xml = xml[:close] + binding + xml[close:]
    report = _run(xml)
    assert not [f for f in report.findings if f.module == "pets" and f.item is None]


def test_an_ambiguous_module_does_not_cascade_into_other_modules() -> None:
    report = _run(_replace(XML, ">Pets page</r:String>", ">pets</r:String>"))
    assert "VisitDate" not in [i for i, _ in _found(report, "spec.item.misplaced")]
    assert "VisitDate" not in [i for i, _ in _found(report, "spec.gate.different")]


_PET_COUNT_OUTPUT = (
    f"<r:ID>{_id(13)}</r:ID>\n      <r:Version>1</r:Version>\n"
    "      <r:Alias>PetCount</r:Alias>\n    </r:OutParameter>\n"
)
_PETS_GATE_BINDING = (
    f"<r:ID>{_id(13)}</r:ID>\n        <r:Version>1</r:Version>\n"
    "        <r:TypeOfObject>OutParameter</r:TypeOfObject>\n"
    "      </r:SourceParameterReference>\n"
    '      <r:TargetParameterReference lateBound="true">\n'
    f"        <r:Agency>int.example</r:Agency>\n        <r:ID>{_id(21)}</r:ID>"
)


def _output(n: int, alias: str) -> str:
    return (
        '    <r:OutParameter isUniversallyUnique="true">\n'
        f"      <r:URN>urn:ddi:int.example:{_id(n)}:1</r:URN>\n"
        "      <r:Agency>int.example</r:Agency>\n"
        f"      <r:ID>{_id(n)}</r:ID>\n"
        "      <r:Version>1</r:Version>\n"
        f"      <r:Alias>{alias}</r:Alias>\n"
        "    </r:OutParameter>\n"
    )


@pytest.mark.parametrize(
    ("cell", "read"), [("Adults", "Adults > 0"), ("Kids", "PetCount.Kids > 0")]
)
def test_a_gate_bound_to_a_grid_cell_reads_as_the_cell(cell: str, read: str) -> None:
    # The gate's own input is aliased PetCount; the cell it is bound to rules.
    xml = _replace(XML, _PET_COUNT_OUTPUT, _PET_COUNT_OUTPUT + _output(14, cell))
    xml = _replace(
        xml, _PETS_GATE_BINDING, _PETS_GATE_BINDING.replace(_id(13), _id(14), 1)
    )
    report = _run(
        xml,
        change=lambda d: d["derived_variables"].append(
            {"name": "Adults", "type": "numeric"}
        ),
    )
    ((_, message),) = _found(report, "spec.gate.different")
    example = {
        "Adults": "Adults is answered with no value and PetCount is 1",
        "Kids": "PetCount is 1 and PetCount.Kids is answered with no value",
    }[cell]
    assert message == (
        f"Module pets is gated by {read}; the spec says PetCount > 0{_when(example)}."
    )


def test_a_gate_bound_to_a_lookup_field_reads_as_the_field() -> None:
    head = (
        f"<r:ID>{_id(80)}</r:ID>\n    <r:Version>1</r:Version>\n    <ConstructName>\n"
        '      <r:String xml:lang="en-CA">Owner lookup</r:String>\n    </ConstructName>\n'
    )
    xml = _replace(XML, head, head + _output(81, "OwnerAge"))
    xml = _replace(
        xml, _PETS_GATE_BINDING, _PETS_GATE_BINDING.replace(_id(13), _id(81), 1)
    )
    ((_, message),) = _found(_run(xml), "spec.gate.different")
    assert (
        message == "Module pets is gated by OwnerAge > 0; the spec says PetCount > 0"
        f"{_when('OwnerAge is answered with no value and PetCount is 1')}."
    )


def _mixed_for_pet_name(*inner: str) -> str:
    text = '    <TextDomain blankIsMissingValue="false" maxLength="40" />\n'
    mixed = (
        "    <StructuredMixedResponseDomain>\n"
        + "".join(
            f"      <ResponseDomainInMixed>\n{domain}      </ResponseDomainInMixed>\n"
            for domain in inner
        )
        + "    </StructuredMixedResponseDomain>\n"
    )
    return _replace(XML, text, mixed)


_NUMERIC = (
    '        <NumericDomain blankIsMissingValue="false" decimalPositions="0" />\n'
)
_CODE = '        <CodeDomain blankIsMissingValue="false" />\n'


@pytest.mark.parametrize(
    ("inner", "found", "actual"),
    [
        ((_NUMERIC,), "numeric", "mixed(numeric)"),
        ((_NUMERIC, _CODE), "code, numeric", "mixed(numeric, code)"),
        ((), "no", "mixed()"),
    ],
)
def test_a_mixed_domain_with_nothing_of_the_kind_is_another_kind(
    inner: tuple[str, ...], found: str, actual: str
) -> None:
    report = _run(_mixed_for_pet_name(*inner))
    assert (
        "PetName",
        f"The question PetName has a mixed domain of {found} domains; "
        "the spec says text.",
    ) in _found(report, "spec.domain.type")
    assert _fields(report, "spec.domain.type", "PetName") == ("pets", "text", actual)


def test_a_mixed_domain_that_refers_to_a_domain_not_in_the_file() -> None:
    reference = _reference("TextDomainReference", 98, "ManagedTextRepresentation")
    report = _run(_mixed_for_pet_name(_NUMERIC, reference))
    assert _found(report, "spec.domain.unverifiable") == [
        (
            "PetName",
            "The domain of PetName is not compared: the question has a mixed domain "
            "that refers to a domain not in the file (TextDomainReference).",
        )
    ]


def test_module_option_reports_an_item_where_it_is() -> None:
    # PetKind (module pets) is also asked on the household page.
    ref = _reference("ControlConstructReference", 12, "QuestionConstruct")
    xml = _replace(
        XML, ref, ref + _reference("ControlConstructReference", 33, "QuestionConstruct")
    )

    def extras(module: str | None) -> list[tuple[str | None, str | None]]:
        report = _run(xml, module=module) if module else _run(xml)
        return [
            (f.module, f.item)
            for f in report.findings
            if f.rule_id == "spec.item.extra" and f.item == "PetKind"
        ]

    assert extras(None) == [("household", "PetKind")]
    assert extras("household") == [("household", "PetKind")]
    assert extras("pets") == []


@pytest.mark.parametrize(
    ("codes", "unverifiable"),
    [
        ("null", False),
        ("5", True),
        ('"x"', True),
        ("0", True),
        ("false", True),
        ('""', True),
        ("{}", True),
    ],
)
def test_selected_codes_must_be_a_list(codes: str, unverifiable: bool) -> None:
    xml = _replace(
        XML,
        f'{_id(21)}:1","Operator":3,"Value":{{"Value":"0","ValueNotNeeded":false,'
        '"SelectedCodes":[]}',
        f'{_id(21)}:1","Operator":3,"Value":{{"Value":"0","ValueNotNeeded":false,'
        f'"SelectedCodes":{codes}}}',
    )
    found = [f for f in _run(xml).findings if f.module == "pets" and f.item is None]
    assert [f.rule_id for f in found] == (
        ["spec.gate.unverifiable"] if unverifiable else []
    )


def test_a_quoted_number_in_blaise_code_is_text() -> None:
    # Neutral stores "1" and 1 alike; Blaise does not.
    native = "NOT ({{PetKind}} = EMPTY) AND NOT ({{PetKind}} = REFUSAL)"
    report = _run(
        _replace(XML, native, '{{PetKind}} &lt;&gt; "1"'),
        change=lambda d: _question(d, "PetName").update(gate="PetKind != 1"),
    )
    assert (
        "PetName",
        'Question PetName is gated by PetKind != "1"; the spec says PetKind != 1.',
    ) in _found(report, "spec.gate.different")


def test_a_variable_alias_names_a_cell_the_spec_does_not_name() -> None:
    # The gate's input is aliased Adults, a spec variable, and bound to a cell
    # whose own alias (Kids) the spec does not know: the cell is Adults.
    xml = _replace(XML, _PET_COUNT_OUTPUT, _PET_COUNT_OUTPUT + _output(14, "Kids"))
    xml = _replace(
        xml, _PETS_GATE_BINDING, _PETS_GATE_BINDING.replace(_id(13), _id(14), 1)
    )
    xml = _replace(
        xml,
        "<r:Alias>PetCount</r:Alias>\n    </r:InParameter>\n    <IfCondition>",
        "<r:Alias>Adults</r:Alias>\n    </r:InParameter>\n    <IfCondition>",
    )

    def change(data: dict[str, Any]) -> None:
        data["derived_variables"].append({"name": "Adults", "type": "numeric"})
        data["modules"][1]["gate"] = "Adults > 0"

    report = _run(xml, change=change)
    assert not [f for f in report.findings if f.module == "pets" and f.item is None]


def test_a_neutral_gate_above_does_not_make_blaise_numbers_loose() -> None:
    # PetName under the Age gate (Neutral) and the Name gate, whose Blaise
    # code compares with "1": text, whatever gate is above it.
    native = "NOT ({{PetKind}} = EMPTY) AND NOT ({{PetKind}} = REFUSAL)"
    name_gate = _reference("ControlConstructReference", 40, "IfThenElse")
    age = _reference("ControlConstructReference", 53, "QuestionConstruct")
    xml = _replace(XML, native, '{{PetKind}} &lt;&gt; "1"')
    xml = _replace(_replace(xml, name_gate, ""), age, age + name_gate)
    report = _run(
        xml,
        change=lambda d: _question(d, "PetName").update(
            gate="PetCount > 1 and PetKind != 1"
        ),
    )
    assert "PetName" in [item for item, _ in _found(report, "spec.gate.different")]


def test_a_cell_aliased_as_another_question_is_still_the_cell() -> None:
    xml = _replace(XML, _PET_COUNT_OUTPUT, _PET_COUNT_OUTPUT + _output(14, "PetAge"))
    xml = _replace(
        xml, _PETS_GATE_BINDING, _PETS_GATE_BINDING.replace(_id(13), _id(14), 1)
    )
    report = _run(xml, change=lambda d: d["modules"][1].update(gate="PetAge > 0"))
    ((_, message),) = _found(report, "spec.gate.different")
    assert message.startswith("Module pets is gated by PetCount.PetAge > 0")


def test_an_ambiguous_module_not_checked_still_holds_its_items() -> None:
    xml = _replace(XML, ">Pets page</r:String>", ">pets</r:String>")
    report = _run(xml, module="visits")
    assert not [f for f in report.findings if f.item == "VisitDate"]


def test_a_part_the_spec_lists_as_a_question_is_named_by_it() -> None:
    """A question in parts: each part the spec lists is its own question."""
    xml = _replace(XML, _PET_COUNT_OUTPUT, _PET_COUNT_OUTPUT + _output(14, "PetLegs"))

    def listed(data: dict[str, Any]) -> None:
        data["modules"][0]["questions"].append({"id": "PetLegs"})

    # The pets gate reads the PetCount part; the spec also lists PetLegs.
    assert not _found(_run(xml, change=listed), "spec.gate.different")

    def other_part(data: dict[str, Any]) -> None:
        listed(data)
        data["modules"][1].update(gate="PetLegs > 0")

    ((_, message),) = _found(_run(xml, change=other_part), "spec.gate.different")
    assert message.startswith("Module pets is gated by PetCount > 0;")


# ---- A page gate on statements ------------------------------------------------------


def _builder() -> Any:
    import importlib.util

    found = importlib.util.spec_from_file_location(
        "build_pets_conform", FIXTURES / "build_pets_conform.py"
    )
    assert found is not None and found.loader is not None
    module = importlib.util.module_from_spec(found)
    found.loader.exec_module(module)
    return module


def _feedback_gated(gates: list[tuple[int, str, str]]) -> str:
    """The fixture with its feedback statement under ``gates``, outermost first.

    Each gate is ``(operator code, value, synopsis)`` on PetCount, fed from the
    household question through the feedback module.
    """
    b = _builder()
    first = 100
    child = (71, "StatementItem")
    made = []
    for depth in reversed(range(len(gates))):
        operator, value, synopsis = gates[depth]
        n = first + 10 * depth
        inner = depth + 1 < len(gates)
        passed = (
            b._parameter("InParameter", n + 3, "PetCount")
            + b._binding(n + 3, n + 11, "InParameter", "InParameter")
            if inner
            else ""
        )
        made.append(
            b._sequence(
                n + 2, f"Thanks gate {depth} (then)", [child], then=True, body=passed
            )
        )
        made.append(
            b._item(
                "IfThenElse",
                b.D,
                n,
                b._name(f"Thanks gate {depth}")
                + b._parameter("InParameter", n + 1, "PetCount")
                + (
                    b._binding(n + 1, n + 3, "InParameter", "InParameter")
                    if inner
                    else ""
                )
                + "<IfCondition>"
                + b._command("Neutral", b._neutral(n + 1, operator, value, synopsis))
                + "</IfCondition>"
                + b._ref("ThenConstructReference", n + 2, "Sequence"),
            )
        )
        child = (n, "IfThenElse")
    items = []
    for item in b.items():
        if b._head(70) in item:
            item = b._sequence(
                70,
                "feedback",
                [child],
                body=b._parameter("InParameter", 75, "PetCount")
                + b._binding(75, first + 1, "InParameter", "InParameter"),
            )
        elif b._head(2) in item:
            item = item.replace(
                "<r:Binding>",
                b._binding(13, 75, "OutParameter", "InParameter") + "<r:Binding>",
                1,
            )
        items.append(item)
    fragments = "".join(
        f'<Fragment xmlns:r="ddi:reusable:3_3" xmlns="ddi:instance:3_3">{item}</Fragment>'
        for item in [*items, *made]
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<ddi:FragmentInstance xmlns:r="ddi:reusable:3_3" xmlns:ddi="ddi:instance:3_3">'
        + b._ref("ddi:TopLevelReference", 1, "Instrument")
        + fragments
        + "</ddi:FragmentInstance>"
    )


def _feedback_page_gate(data: dict[str, Any]) -> None:
    data["modules"].append(
        {
            "id": "feedback",
            "gate": "PetCount > 0",
            "gate_scope": "page",
            "statements": ["Thanks"],
        }
    )


def _gate_findings(report: ConformReport) -> list[tuple[str, str | None, str]]:
    return [
        (finding.rule_id, finding.item, finding.message)
        for finding in report.findings
        if finding.rule_id.startswith("spec.gate.") and finding.module == "feedback"
    ]


def test_a_page_gate_on_a_statement_is_compared() -> None:
    xml = _feedback_gated([(3, "0", "PetCount > 0")])
    assert not ddi_l.read_ddi(xml.encode()).validate()
    assert _gate_findings(_run(xml, change=_feedback_page_gate)) == []
    report = _run(
        _feedback_gated([(3, "5", "PetCount > 5")]), change=_feedback_page_gate
    )
    assert _gate_findings(report) == [
        (
            "spec.gate.different",
            "Thanks",
            "Statement Thanks is gated by PetCount > 5; the spec puts it under its "
            f"page gate, PetCount > 0{_when('PetCount is 1')}.",
        )
    ]


def test_a_statement_without_its_page_gate_is_reported() -> None:
    assert _gate_findings(_run(change=_feedback_page_gate)) == [
        (
            "spec.gate.missing",
            "Thanks",
            "Statement Thanks is not gated; the spec says PetCount > 0.",
        )
    ]


def test_a_statement_may_carry_a_gate_of_its_own_under_its_page_gate() -> None:
    # The spec gives a statement no gate of its own: only the page gate is checked.
    xml = _feedback_gated([(3, "0", "PetCount > 0"), (3, "3", "PetCount > 3")])
    assert not ddi_l.read_ddi(xml.encode()).validate()
    assert _gate_findings(_run(xml, change=_feedback_page_gate)) == []


def test_a_statement_under_a_gate_that_cannot_be_read() -> None:
    report = _run(
        _feedback_gated([(99, "0", "PetCount ? 0")]), change=_feedback_page_gate
    )
    assert _gate_findings(report) == [
        (
            "spec.gate.unverifiable",
            "Thanks",
            "The gate of statement Thanks cannot be compared: operator code 99 is "
            "not known.",
        )
    ]
