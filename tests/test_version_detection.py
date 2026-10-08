"""DDI 3.1 and 3.2 documents are read with their own namespaces."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import ddi_l as ddi
from ddi_l import cli, operations
from ddi_l.document import DDIDocument

EARLIER_VERSIONS = ["minimal_instance_3_1.xml", "minimal_instance_3_2.xml"]


@pytest.mark.parametrize("name", EARLIER_VERSIONS)
def test_read_ddi_detects_the_declared_version(fixtures_dir: Path, name: str) -> None:
    document = ddi.read_ddi(fixtures_dir / name)
    assert isinstance(document, DDIDocument)


@pytest.mark.parametrize("name", EARLIER_VERSIONS)
def test_identification_and_citation_use_the_document_namespaces(
    fixtures_dir: Path, name: str
) -> None:
    document = ddi.read_ddi(fixtures_dir / name)
    assert isinstance(document, DDIDocument)
    identification = document.get_identification()
    assert identification["agency"] == "example.agency"
    assert identification["id"]
    assert identification["version"] == "1.0"

    document.set_identification(agency="other.agency", identifier="x", version="2")
    document.set_citation(title="Renamed")
    reusable = document._reusable_ns
    assert document.get_identification()["agency"] == "other.agency"
    assert "ddi:reusable:3_3" not in document.to_xml()
    title = document.root.find(f"{{{reusable}}}Citation/{{{reusable}}}Title")
    assert title is not None
    assert title[0].tag == f"{{{reusable}}}String"
    assert document.validate() == []


@pytest.mark.parametrize("name", EARLIER_VERSIONS)
def test_typed_models_refuse_earlier_versions(fixtures_dir: Path, name: str) -> None:
    document = ddi.read_ddi(fixtures_dir / name)
    assert isinstance(document, DDIDocument)
    with pytest.raises(ddi.DDIModelError, match="3.3 only"):
        list(document.iter_study_units())
    with pytest.raises(ddi.DDIModelError, match="3.3 only"):
        document.build_index()


@pytest.mark.parametrize("name", EARLIER_VERSIONS)
@pytest.mark.parametrize("command", ["to-json", "lint"])
def test_cli_accepts_earlier_versions(
    fixtures_dir: Path, name: str, command: str, capsys
) -> None:
    exit_code = cli.main([command, str(fixtures_dir / name)])
    captured = capsys.readouterr()
    assert exit_code == 0, captured.err


@pytest.mark.parametrize("name", EARLIER_VERSIONS)
def test_lint_reports_no_false_positives(fixtures_dir: Path, name: str) -> None:
    findings = operations.lint_source((fixtures_dir / name).read_bytes())
    assert findings == []


@pytest.mark.parametrize("name", EARLIER_VERSIONS)
def test_roundtrip_keeps_the_version(
    fixtures_dir: Path, name: str, tmp_path: Path
) -> None:
    target = tmp_path / "out.xml"
    assert (
        cli.main(["roundtrip", str(fixtures_dir / name), "--output", str(target)]) == 0
    )
    original_ns = (fixtures_dir / name).read_text(encoding="utf-8")
    version = "3_1" if "3_1" in name else "3_2"
    assert f"ddi:instance:{version}" in original_ns
    assert f"ddi:instance:{version}" in target.read_text(encoding="utf-8")


def test_to_jsonld_explains_the_version_limit(fixtures_dir: Path, capsys) -> None:
    exit_code = cli.main(["to-jsonld", str(fixtures_dir / "minimal_instance_3_2.xml")])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "3.3" in captured.err


def test_validate_source_honours_the_requested_version(fixtures_dir: Path) -> None:
    data = (fixtures_dir / "minimal_instance.xml").read_bytes()
    as_declared = operations.validate_source(data, lint=False)
    as_3_2 = operations.validate_source(data, version="3.2", lint=False)
    assert as_declared.schema_issues == []
    assert as_3_2.schema_issues, json.dumps(as_3_2.to_dict())
