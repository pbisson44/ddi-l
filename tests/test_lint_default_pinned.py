"""Default ``ddi lint`` output on the bundled fixtures is pinned.

Every rule's output is pinned except ``ddi.reference.*``, whose behaviour
changed on purpose in 0.2.0 and is pinned separately below, before and after.
A finding is pinned by rule, severity and message; locations differ between
the lxml and standard-library backends, so they are left out.

To accept a deliberate change, regenerate the snapshot:

    DDI_L_UPDATE_LINT_BASELINE=1 uv run pytest tests/test_lint_default_pinned.py

and review the diff of ``tests/fixtures/lint_baseline/default_profile.json``.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path

import pytest

import ddi_l
from ddi_l.lint import run_lint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE = (
    PROJECT_ROOT / "tests" / "fixtures" / "lint_baseline" / "default_profile.json"
)


def _fixture_documents() -> list[Path]:
    paths = sorted(
        [
            *(PROJECT_ROOT / "src" / "ddi_l" / "examples").rglob("*.xml"),
            *(PROJECT_ROOT / "tests" / "fixtures").glob("*.xml"),
            *(PROJECT_ROOT / "tests" / "fixtures").glob("golden/*.xml"),
            *(PROJECT_ROOT / "tests" / "fixtures").glob("instances/*.xml"),
        ]
    )
    readable = []
    for path in paths:
        try:
            ddi_l.read_ddi(path)
        except Exception:  # not an instance or fragment: model fixtures, broken XML
            continue
        readable.append(path)
    return readable


def _relative(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _snapshot() -> dict[str, dict[str, object]]:
    snapshot: dict[str, dict[str, object]] = {}
    for path in _fixture_documents():
        findings = [
            (finding.rule_id, finding.severity, finding.message)
            for finding in run_lint(ddi_l.read_ddi(path))
            if not finding.rule_id.startswith("ddi.reference.")
        ]
        rules = Counter(f"{rule}:{severity}" for rule, severity, _ in findings)
        snapshot[_relative(path)] = {
            "count": len(findings),
            "rules": dict(sorted(rules.items())),
            "sha256": hashlib.sha256(json.dumps(findings).encode()).hexdigest(),
        }
    return snapshot


def test_default_lint_output_is_unchanged_outside_reference_rules() -> None:
    snapshot = _snapshot()
    if os.environ.get("DDI_L_UPDATE_LINT_BASELINE"):
        BASELINE.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    assert snapshot == json.loads(BASELINE.read_text())


# Reference findings per fixture, by "rule:severity". 0.1 had one rule,
# ddi.reference.integrity, which matched (agency, id, version) exactly, so it
# reported Colectica's late-bound parameter references (written at version 1
# while the parameter is at, say, 10) and BasedOn provenance links as broken.
REFERENCE_FINDINGS_BEFORE = {
    "src/ddi_l/examples/Quality_of_Life.xml": {"ddi.reference.integrity:warning": 116},
    "tests/fixtures/Canadian_Survey_on_Business_conditions.xml": {
        "ddi.reference.integrity:warning": 1
    },
    "tests/fixtures/colectica_group_fragment.xml": {
        "ddi.reference.integrity:warning": 3
    },
}
REFERENCE_FINDINGS_AFTER = {
    # 108 late-bound references resolve; 6 BasedOn links point outside the
    # file; 2 references to the nil-UUID Concept remain genuinely unresolved.
    "src/ddi_l/examples/Quality_of_Life.xml": {
        "ddi.reference.integrity:warning": 2,
        "ddi.reference.provenance-external:info": 6,
    },
    # The item exists, but at version 1 only; the reference names version 2.
    "tests/fixtures/Canadian_Survey_on_Business_conditions.xml": {
        "ddi.reference.version:warning": 1
    },
    "tests/fixtures/colectica_group_fragment.xml": {
        "ddi.reference.integrity:warning": 1,
        "ddi.reference.provenance-external:info": 2,
    },
}
# Fixtures whose reference findings did not change.
REFERENCE_FINDINGS_UNCHANGED = {
    "tests/fixtures/golden/example_instance.canonical.xml": {
        "ddi.reference.integrity:error": 14
    },
    "tests/fixtures/golden/quality_of_life_instance.canonical.xml": {
        "ddi.reference.integrity:error": 9
    },
    "tests/fixtures/instances/example_instance.xml": {
        "ddi.reference.integrity:error": 14
    },
    "tests/fixtures/instances/quality_of_life_instance.xml": {
        "ddi.reference.integrity:error": 9
    },
    "tests/fixtures/minimal_fragment.xml": {"ddi.reference.integrity:warning": 1},
}


def _reference_findings(path: Path) -> dict[str, int]:
    counts = Counter(
        f"{finding.rule_id}:{finding.severity}"
        for finding in run_lint(ddi_l.read_ddi(path))
        if finding.rule_id.startswith("ddi.reference.")
    )
    return dict(sorted(counts.items()))


@pytest.mark.parametrize(
    "relative", sorted({**REFERENCE_FINDINGS_AFTER, **REFERENCE_FINDINGS_UNCHANGED})
)
def test_reference_findings_after_the_split(relative: str) -> None:
    expected = {**REFERENCE_FINDINGS_AFTER, **REFERENCE_FINDINGS_UNCHANGED}[relative]
    assert _reference_findings(PROJECT_ROOT / relative) == expected


def test_no_other_fixture_reports_reference_findings() -> None:
    pinned = {**REFERENCE_FINDINGS_AFTER, **REFERENCE_FINDINGS_UNCHANGED}
    for path in _fixture_documents():
        if _relative(path) not in pinned:
            assert _reference_findings(path) == {}, _relative(path)


def test_the_split_only_reclassifies_or_removes_findings() -> None:
    """Nothing became more severe: every changed fixture reports fewer
    integrity findings than before, and the rest moved to version or
    provenance."""
    for relative, before in REFERENCE_FINDINGS_BEFORE.items():
        after = REFERENCE_FINDINGS_AFTER[relative]
        assert sum(after.values()) <= sum(before.values())
        assert (
            after.get("ddi.reference.integrity:warning", 0)
            < before["ddi.reference.integrity:warning"]
        )
