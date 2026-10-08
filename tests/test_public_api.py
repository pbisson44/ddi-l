"""The public API surface, error types and labelling behave as documented."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import ddi_l as ddi
from ddi_l import cli
from ddi_l.exceptions import (
    DDIParseError,
    DDIReadError,
    DDIReferenceError,
)
from ddi_l.models.base import Reference

MALFORMED = "<DDIInstance xmlns='ddi:instance:3_3'>\n  <Broken>\n</DDIInstance>"


def test_removed_aliases_are_not_exported() -> None:
    for name in ("read", "write", "qn"):
        assert name not in ddi.__all__
        with pytest.raises(AttributeError):
            getattr(ddi, name)


def test_malformed_xml_raises_parse_error_with_position(tmp_path: Path) -> None:
    with pytest.raises(DDIParseError) as excinfo:
        ddi.read_ddi(MALFORMED)
    assert isinstance(excinfo.value, DDIReadError)
    assert excinfo.value.location is not None
    assert excinfo.value.location.line == 3
    assert "Malformed XML" in str(excinfo.value)

    path = tmp_path / "broken.xml"
    path.write_text(MALFORMED, encoding="utf-8")
    with pytest.raises(DDIParseError):
        ddi.open_ddi(path)


def test_unresolvable_reference_raises_reference_error() -> None:
    document = ddi.new_study(title="Refs", agency="example.org").inner
    reference = Reference(
        agency="example.org",
        identifier="missing",
        version="1",
        type_of_object="Variable",
    )
    with pytest.raises(DDIReferenceError) as excinfo:
        document.resolver.resolve(reference)
    assert isinstance(excinfo.value, LookupError)
    assert "missing" in str(excinfo.value)


def test_unknown_study_raises_reference_error() -> None:
    doc = ddi.new_study(title="Wave 1", agency="example.org")
    with pytest.raises(DDIReferenceError):
        doc.study("nope")


def test_every_helper_accepts_a_label_and_output_lints_clean() -> None:
    doc = ddi.new_study(title="Labels", agency="example.org")
    doc.add_variable(name="age", label="Age")
    doc.add_ncube(name="Cube", label="Cube")
    doc.add_comparison(name="Waves", label="Waves")
    doc.add_ddi_profile(name="Profile", label="Profile")
    doc.add_archive(label="Archive")
    doc.add_data_relationship(label="Records")
    doc.add_dataset(name="Rows")
    doc.add_record_layout()

    assert doc.lint() == []
    assert doc.validate() == []


def test_add_study_accepts_a_language() -> None:
    doc = ddi.new_study(title="Wave 1", agency="example.org")
    wave2 = doc.add_study(title="Vague 2", lang="fr")
    assert wave2.abstracts[0].lang == "fr"


def test_reprs_are_concise() -> None:
    doc = ddi.new_study(title="My Survey", agency="example.org")
    doc.add_variable(name="age")
    assert repr(doc) == (
        "Document(title='My Survey', agency='example.org', questions=0, variables=1)"
    )
    assert repr(doc.inner) == "DDIDocument(root='DDIInstance', ddi_version='3.3')"
    assert repr(doc.study()).startswith("StudyCursor(identifier=")


def test_output_directory_with_a_single_input(fixtures_dir: Path, tmp_path: Path):
    source = fixtures_dir / "minimal_instance.xml"
    assert cli.main(["to-json", str(source), "--output", str(tmp_path)]) == 0
    written = tmp_path / "minimal_instance.json"
    assert json.loads(written.read_text(encoding="utf-8"))


def test_cli_errors_are_not_quoted(fixtures_dir: Path, capsys) -> None:
    source = fixtures_dir / "minimal_instance.xml"
    assert cli.main(["lint", "--profile", "bogus", str(source)]) == 1
    assert capsys.readouterr().err.strip() == (
        "Error: Unknown lint profile requested: bogus"
    )


def test_ddi_version_rejects_unknown_values(fixtures_dir: Path, capsys) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["lint", "--ddi-version", "4.0", str(fixtures_dir / "x.xml")])
    assert excinfo.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_parsed_scheme_labels_survive_reserialization(tmp_path: Path) -> None:
    doc = ddi.new_study(title="Schemes", agency="example.org")
    doc.add_variable(name="age", label="Age")
    path = tmp_path / "study.xml"
    doc.save(path)

    reopened = ddi.open_ddi(path)
    assert reopened.variables  # parse the study into the model layer
    assert "Variable scheme" in reopened.to_xml()
    assert reopened.lint() == []


def test_parse_errors_state_the_position_once() -> None:
    with pytest.raises(DDIParseError) as excinfo:
        ddi.read_ddi(MALFORMED)
    assert str(excinfo.value).count("column") == 1
