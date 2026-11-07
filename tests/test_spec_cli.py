"""``ddi conform``: exit codes, output formats and options."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("yaml", reason="requires the 'spec' extra")
pytest.importorskip("jsonschema", reason="requires the 'spec' extra")

from ddi_l import cli

FIXTURES = Path(__file__).parent / "fixtures" / "spec"
INSTRUMENT = str(FIXTURES / "pets_conform.ddi33.xml")
SPEC = str(FIXTURES / "pets_conform.spec.yaml")


def _write(tmp_path: Path, text: str, name: str = "spec.yaml") -> str:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


# Only PetCount, found as the spec says: the modules the spec does not list
# are the only findings, warnings.
CLEAN = """\
spec: household-only
match: {question_id: [construct_alias]}
modules:
  - id: household
    questions:
      - id: PetCount
        domain: {numeric: {min: 0, max: 20, decimals: 0}}
"""


def test_findings_as_json_and_exit_1_on_errors(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["conform", INSTRUMENT, "--spec", SPEC]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["spec"] == "pet-survey-conform"
    assert payload["summary"] == {"error": 7, "warning": 8, "info": 2}
    assert [module["id"] for module in payload["modules"]] == [
        "household",
        "pets",
        "visits",
    ]
    assert payload["findings"][0]["rule_id"] == "spec.item.id-sources-differ"


def test_exit_0_when_nothing_reaches_the_fail_severity(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    spec = _write(tmp_path, CLEAN)
    assert cli.main(["conform", INSTRUMENT, "--spec", spec]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert {f["rule_id"] for f in payload["findings"]} == {"spec.module.extra"}
    assert (
        cli.main(["conform", INSTRUMENT, "--spec", spec, "--fail-severity", "warning"])
        == 1
    )


def test_a_table_with_a_summary(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["conform", INSTRUMENT, "--spec", SPEC, "--format", "table"]) == 1
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "pet-survey-conform: Instrument 55555555 (Pet survey instrument)"
    assert lines[1].split() == ["module", "severity", "rule", "item", "message"]
    assert lines[-1] == "7 error(s), 8 warning(s), 2 info."
    assert any(
        line.startswith("pets       error     spec.code.missing") for line in lines
    )


def test_output_to_a_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "report.json"
    code = cli.main(
        ["conform", INSTRUMENT, "--spec", SPEC, "-o", str(target), "--indent", "4"]
    )
    assert code == 1
    assert capsys.readouterr().out == ""
    assert json.loads(target.read_text("utf-8"))["summary"]["error"] == 7
    table = tmp_path / "report.txt"
    cli.main(
        ["conform", INSTRUMENT, "--spec", SPEC, "--format", "table", "-o", str(table)]
    )
    assert table.read_text("utf-8").endswith("7 error(s), 8 warning(s), 2 info.\n")


@pytest.mark.parametrize(
    ("mode", "edit_rules"),
    [
        ("off", []),
        ("info", ["spec.edit.unverifiable"]),
        ("strict", ["spec.edit.different"]),
    ],
)
def test_edits_modes(
    capsys: pytest.CaptureFixture[str], mode: str, edit_rules: list[str]
) -> None:
    cli.main(["conform", INSTRUMENT, "--spec", SPEC, "--edits", mode])
    findings = json.loads(capsys.readouterr().out)["findings"]
    assert [f["rule_id"] for f in findings if "edit" in f["rule_id"]] == edit_rules


def test_one_module(capsys: pytest.CaptureFixture[str]) -> None:
    cli.main(["conform", INSTRUMENT, "--spec", SPEC, "--module", "household"])
    payload = json.loads(capsys.readouterr().out)
    assert [module["id"] for module in payload["modules"]] == ["household"]
    assert [f["rule_id"] for f in payload["findings"]] == [
        "spec.item.id-sources-differ"
    ]


def test_an_instrument_by_name(capsys: pytest.CaptureFixture[str]) -> None:
    cli.main(["conform", INSTRUMENT, "--spec", SPEC, "--instrument", "Nope"])
    payload = json.loads(capsys.readouterr().out)
    assert [f["rule_id"] for f in payload["findings"]] == ["spec.instrument.missing"]
    assert payload["instrument"] is None


def test_an_unknown_module_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["conform", INSTRUMENT, "--spec", SPEC, "--module", "nope"]) == 2
    assert capsys.readouterr().err == (
        "ddi conform: The spec has no module 'nope'; it has household, pets, visits.\n"
    )


def test_strict_edits_without_match_exit_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    spec = _write(tmp_path, CLEAN)
    assert cli.main(["conform", INSTRUMENT, "--spec", spec, "--edits", "strict"]) == 2
    assert "needs the spec's match.edits" in capsys.readouterr().err


def test_a_bad_spec_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    spec = _write(tmp_path, "spec: s\nmodules:\n  - id: m\n    gate: X > 1\n")
    assert cli.main(["conform", INSTRUMENT, "--spec", spec]) == 2
    assert capsys.readouterr().err == (
        f"{spec}: modules[0].gate: 'X' is not a question or variable of the spec\n"
    )
    assert cli.main(["conform", INSTRUMENT, "--spec", str(tmp_path / "none.yaml")]) == 2
    assert "No such file" in capsys.readouterr().err


def test_an_instrument_that_does_not_read_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = _write(tmp_path, "<not xml", "broken.xml")
    assert cli.main(["conform", broken, "--spec", SPEC]) == 2
    assert capsys.readouterr().err.startswith("Error: ")


def test_without_the_extra_the_hint(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(sys.modules, "jsonschema", None)
    assert cli.main(["conform", INSTRUMENT, "--spec", SPEC]) == 1
    assert capsys.readouterr().err == (
        'Error: this command needs the spec extra: pip install "ddi-l[spec]"\n'
    )


@pytest.mark.parametrize(
    ("text", "encoding", "error"),
    [
        (
            "spec: s\nblaise: {date: 'D{year}{month}{day}'}\nmodules: [{id: m}]\n",
            "utf-8",
            "blaise.date",
        ),
        ("spec: café\nmodules: [{id: m}]\n", "latin-1", "not UTF-8"),
        (
            "spec: s\nmodules: [{id: m, gate: '"
            + "(" * 400
            + "x"
            + ")" * 400
            + "'}]\n",
            "utf-8",
            "nested too deeply",
        ),
    ],
    ids=["date-template", "latin-1", "deep-gate"],
)
def test_a_spec_that_cannot_be_used_exits_2(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    text: str,
    encoding: str,
    error: str,
) -> None:
    path = tmp_path / "spec.yaml"
    path.write_bytes(text.encode(encoding))
    assert cli.main(["conform", INSTRUMENT, "--spec", str(path)]) == 2
    assert error in capsys.readouterr().err
    assert cli.main(["spec", "validate", str(path)]) in (1, 2)


@pytest.mark.skipif(
    not __import__("ddi_l.spec.semantics").spec.semantics.logic_available(),
    reason="requires the 'logic' extra",
)
@pytest.mark.parametrize(
    ("semantics", "example"), [("smt", "PetCount is 1"), ("syntactic", None)]
)
def test_how_gates_are_compared(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    semantics: str,
    example: str | None,
) -> None:
    text = Path(SPEC).read_text(encoding="utf-8")
    assert "    gate: PetCount > 0\n" in text
    spec = _write(
        tmp_path, text.replace("    gate: PetCount > 0\n", "    gate: PetCount > 1\n")
    )

    cli.main(["conform", INSTRUMENT, "--spec", spec, "--semantics", semantics])

    (finding,) = [
        f
        for f in json.loads(capsys.readouterr().out)["findings"]
        if f["rule_id"] == "spec.gate.different" and f["item"] is None
    ]
    assert finding.get("example") == example
