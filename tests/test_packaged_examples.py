"""The examples shipped in the wheel must survive our own quality gates.

These files are the first thing a new user opens, so they must pass
``ddi validate`` and have no lint errors (warnings are allowed).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from ddi_l import read_ddi, schema_loader
from ddi_l.lint import reset_lint_configuration, run_lint
from tests import EXAMPLES_DIR

EXAMPLE_NAMES = ["example_instance.xml", "Quality_of_Life.xml"]


@pytest.fixture(autouse=True)
def _reset_lint_configuration():
    reset_lint_configuration()
    yield
    reset_lint_configuration()


@pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
def test_packaged_example_is_schema_valid(example_name: str) -> None:
    """Every packaged example validates against the bundled DDI 3.3 schema."""
    document = read_ddi(EXAMPLES_DIR / example_name)

    issues = schema_loader.validate(document.root, raise_error=False)

    assert issues == [], (
        f"{example_name} has {len(issues)} schema issue(s): "
        f"{[str(issue) for issue in issues[:5]]}"
    )


@pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
def test_packaged_example_has_no_lint_errors(example_name: str) -> None:
    """No packaged example carries an error-severity lint finding."""
    document = read_ddi(EXAMPLES_DIR / example_name)

    errors = [finding for finding in run_lint(document) if finding.severity == "error"]

    assert errors == [], (
        f"{example_name} has {len(errors)} lint error(s): "
        f"{[(f.rule_id, f.location) for f in errors[:5]]}"
    )


def test_generated_example_references_resolve() -> None:
    """Every reference in the example we generate resolves within the document.

    ``ddi.reference.integrity`` is only a warning for fragments, so this is
    checked separately. ``Quality_of_Life.xml`` is exempt: it is a third-party
    fragment whose references legitimately point outside it.
    """
    document = read_ddi(EXAMPLES_DIR / "example_instance.xml")

    dangling = [
        finding
        for finding in run_lint(document)
        if finding.rule_id == "ddi.reference.integrity"
    ]

    assert dangling == [], (
        f"example_instance.xml has {len(dangling)} unresolvable reference(s): "
        f"{[f.location for f in dangling[:5]]}"
    )


def test_example_builder_writes_to_the_current_folder(tmp_path, monkeypatch):
    import ddi_l
    from ddi_l.examples import build_and_validate

    monkeypatch.chdir(tmp_path)
    build_and_validate.main(["--refresh", "--refresh-fragment"])

    assert (tmp_path / "example_instance.xml").is_file()
    assert (tmp_path / "example_fragment.xml").is_file()
    # The package folder on sys.path would let ddi_l/io.py shadow stdlib io.
    package_dir = str(Path(ddi_l.__file__).resolve().parent)
    assert package_dir not in sys.path
