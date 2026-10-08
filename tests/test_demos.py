"""Ensure every demo script runs, and that what it produces is actually valid.

Demos are the first thing a new user runs, so what they write must pass
``ddi validate`` and ``ddi lint`` with no findings.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from ddi_l import read_ddi, schema_loader
from ddi_l.lint import reset_lint_configuration, run_lint

DEMO_DIR = Path(__file__).resolve().parent.parent / "demo"

DEMO_SCRIPTS = sorted(DEMO_DIR.glob("demo*.py"))

# `demo/` is not shipped in the sdist.
pytestmark = pytest.mark.skipif(
    not DEMO_DIR.is_dir(), reason="demo/ is not shipped in the sdist"
)


@pytest.fixture(autouse=True)
def _demo_output_dir(tmp_path, monkeypatch):
    """Redirect demo artifacts into a temporary directory.

    The demos write real files. Left at their default they overwrite the
    tracked samples under ``demo/output/`` with freshly generated identifiers,
    so a plain ``pytest`` run would dirty the working tree.
    """
    output_dir = tmp_path / "demo-output"
    output_dir.mkdir()
    monkeypatch.setenv("DDI_DEMO_OUTPUT_DIR", str(output_dir))
    return output_dir


@pytest.mark.parametrize(
    "script",
    DEMO_SCRIPTS,
    ids=lambda p: p.stem,
)
def test_demo_runs_without_error(script: Path, _demo_output_dir: Path):
    spec = importlib.util.spec_from_file_location(script.stem, script)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    assert hasattr(module, "main"), f"{script.name} must define a main() function"
    module.main()
    # Every demo is expected to produce at least one artifact, and to produce
    # it in the redirected directory rather than in the repository.
    assert list(_demo_output_dir.iterdir()), f"{script.name} wrote no output"


@pytest.mark.parametrize(
    "script",
    DEMO_SCRIPTS,
    ids=lambda p: p.stem,
)
def test_demo_output_is_schema_valid_and_lint_clean(
    script: Path, _demo_output_dir: Path
):
    """What a demo writes must pass ``ddi validate`` and ``ddi lint`` cleanly.

    Warnings count too: the bar is zero findings.
    """
    reset_lint_configuration()
    spec = importlib.util.spec_from_file_location(script.stem, script)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    module.main()

    artifacts = sorted(_demo_output_dir.rglob("*.xml"))
    assert artifacts, f"{script.name} produced no XML to check"

    for artifact in artifacts:
        schema_errors = [
            issue
            for issue in schema_loader.validate(artifact)
            if (issue.severity or "").lower() == "error"
        ]
        assert not schema_errors, (
            f"{script.name} wrote schema-invalid {artifact.name}: "
            f"{[issue.message for issue in schema_errors]}"
        )

        findings = run_lint(read_ddi(artifact))
        assert not findings, (
            f"{script.name} wrote {artifact.name} with {len(findings)} lint "
            f"finding(s): {[(f.rule_id, f.severity, f.location) for f in findings]}"
        )


def test_demos_do_not_write_into_the_repository(_demo_output_dir: Path):
    """The demo output directory must be overridable, not hard-coded.

    A demo that ignored ``DDI_DEMO_OUTPUT_DIR`` would overwrite the tracked
    samples.
    """
    for script in DEMO_SCRIPTS:
        source = script.read_text(encoding="utf-8")
        assert "DDI_DEMO_OUTPUT_DIR" in source, (
            f"{script.name} must resolve its output directory via _output_dir()"
        )
