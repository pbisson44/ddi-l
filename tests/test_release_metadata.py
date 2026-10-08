"""Version and packaging metadata that lives in more than one file.

`__version__` comes from installed metadata; `CITATION.cff` and `SECURITY.md`
restate the version by hand and must agree with pyproject.toml.
"""

from __future__ import annotations

import datetime as _datetime
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _project_version() -> str:
    data = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def test_citation_version_matches_pyproject() -> None:
    """CITATION.cff restates the version; it must agree with pyproject."""
    citation = (PROJECT_ROOT / "CITATION.cff").read_text(encoding="utf-8")

    versions = [
        line.split(":", 1)[1].strip().strip("\"'")
        for line in citation.splitlines()
        if line.startswith("version:")
    ]

    assert versions == [_project_version()], (
        f"CITATION.cff says {versions}, pyproject says {_project_version()!r}"
    )


def test_citation_release_date_is_not_in_the_future() -> None:
    """`date-released` must describe a release that has happened.

    It stood at 2026-12-01 while the release was being prepared in August --
    a date four months out, which would have been published to Zenodo and every
    downstream citation index as fact. A placeholder here is not obviously wrong
    when read, so assert it instead.
    """
    citation = (PROJECT_ROOT / "CITATION.cff").read_text(encoding="utf-8")

    dates = [
        line.split(":", 1)[1].strip().strip("\"'")
        for line in citation.splitlines()
        if line.startswith("date-released:")
    ]

    assert len(dates) == 1, f"expected one date-released, found {dates}"
    released = _datetime.date.fromisoformat(dates[0])
    today = _datetime.date.today()

    assert released <= today, (
        f"CITATION.cff date-released is {released}, which is in the future "
        f"(today is {today}). Set it to the actual release date."
    )


def test_security_policy_covers_the_current_release_series() -> None:
    """SECURITY.md's support table must name the current major.minor series."""
    security = (PROJECT_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    major_minor = ".".join(_project_version().split(".")[:2])

    assert f"{major_minor}." in security, (
        f"SECURITY.md does not mention the {major_minor}.x series"
    )


@pytest.mark.parametrize(
    "relative_path",
    ["LICENSE", "SECURITY.md", "CITATION.cff", "CODE_OF_CONDUCT.md", "CHANGELOG.md"],
)
def test_community_health_files_are_present_and_non_trivial(relative_path: str) -> None:
    """These ship in the sdist now, so an empty one would be published."""
    path = PROJECT_ROOT / relative_path

    assert path.is_file(), f"{relative_path} is missing"
    assert len(path.read_text(encoding="utf-8").strip()) > 100, (
        f"{relative_path} looks like a stub"
    )


def test_readme_has_no_relative_links() -> None:
    """PyPI renders the README against pypi.org, so relative links 404 there."""
    import re

    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    relative = [
        match.group(0)
        for match in re.finditer(r"\]\(([^)]+)\)", readme)
        if not match.group(1).startswith(("http://", "https://", "#", "mailto:"))
    ]

    assert relative == [], f"README links that break on PyPI: {relative}"
