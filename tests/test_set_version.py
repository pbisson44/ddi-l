"""scripts/set_version.py sets the version in every file that states it."""

from __future__ import annotations

import datetime
import importlib.util
import re
import shutil
import subprocess
import tomllib
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]

# docs/ and the native crate are not shipped in the sdist.
pytestmark = pytest.mark.skipif(
    not (ROOT / "docs").is_dir() or not (ROOT / "native" / "Cargo.lock").is_file(),
    reason="the docs and the native crate are not shipped in the sdist",
)

# Files that may name the current version without stating it.
NOT_SET = {
    "uv.lock",  # re-locked by `uv lock`
    "SECURITY.md",  # its table changes by hand when a series starts
    "tests/test_lint_default_pinned.py",  # says what a past release changed
}


def _script() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "set_version", ROOT / "scripts" / "set_version.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


set_version = _script()


def _read(path: Path) -> str:
    with open(path, encoding="utf-8", newline="") as file:
        return file.read()


def _released() -> datetime.date:
    match = re.search(r'^date-released: "(.+)"', _read(ROOT / "CITATION.cff"), re.M)
    assert match
    return datetime.date.fromisoformat(match.group(1))


def test_each_file_matches_as_it_is() -> None:
    """Setting today's version and date again changes nothing."""
    texts, problems = set_version.plan(
        ROOT, set_version.current_version(ROOT), _released()
    )

    assert problems == []
    assert {path: _read(ROOT / path) for path in texts} == texts


def test_a_new_version_reaches_every_file() -> None:
    texts, problems = set_version.plan(ROOT, "9.8.7", datetime.date(2031, 2, 3))

    assert problems == []
    toml = {
        p: tomllib.loads(t) for p, t in texts.items() if p.endswith((".toml", ".lock"))
    }
    assert toml["pyproject.toml"]["project"]["version"] == "9.8.7"
    assert "ddi-l-native==9.8.7" in toml["pyproject.toml"]["project"]["dependencies"]
    assert toml["native/pyproject.toml"]["project"]["version"] == "9.8.7"
    assert toml["native/fallback/pyproject.toml"]["project"]["version"] == "9.8.7"
    assert toml["native/Cargo.toml"]["package"]["version"] == "9.8.7"
    native = [
        p for p in toml["native/Cargo.lock"]["package"] if p["name"] == "ddi-l-native"
    ]
    assert [p["version"] for p in native] == ["9.8.7"]
    assert 'version: 9.8.7\ndate-released: "2031-02-03"\n' in texts["CITATION.cff"]
    for page in ("README.md", "docs/index.en.md", "docs/index.fr.md"):
        assert "Bisson, P. (2031)" in texts[page]
        assert "(Version 9.8.7)" in texts[page]
    for page in ("docs/index.en.md", "docs/index.fr.md"):
        assert "  year    = {2031},\n  version = {9.8.7},\n" in texts[page]
    assert "\n## 9.8.7 (unreleased)\n" in texts["docs/release-notes.en.md"]
    assert "\n## 9.8.7 (non publiée)\n" in texts["docs/release-notes.fr.md"]


def _copy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """Point the script at a copy of its files; return the commands it runs."""
    for path in [*set_version.FILES, "SECURITY.md"]:
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, tmp_path / path)
    monkeypatch.setattr(set_version, "ROOT", tmp_path)
    commands: list[list[str]] = []
    monkeypatch.setattr(
        set_version.subprocess, "run", lambda command, **_: commands.append(command)
    )
    return commands


def test_it_writes_every_file_then_relocks(tmp_path, monkeypatch, capsys) -> None:
    commands = _copy(tmp_path, monkeypatch)
    current = set_version.current_version(tmp_path)

    assert set_version.main(["minor", "--date", "2031-02-03"]) == 0

    major, minor, _ = current.split(".")
    version = f"{major}.{int(minor) + 1}.0"
    texts, problems = set_version.plan(tmp_path, version, datetime.date(2031, 2, 3))
    assert problems == []
    assert {path: _read(tmp_path / path) for path in texts} == texts
    assert set_version.current_version(tmp_path) == version
    assert commands == [["uv", "lock"]]
    series = f"{major}.{int(minor) + 1}.x"
    assert f"add the {series} series to SECURITY.md" in capsys.readouterr().out


def test_nothing_is_written_unless_every_file_matches(
    tmp_path, monkeypatch, capsys
) -> None:
    commands = _copy(tmp_path, monkeypatch)
    readme = tmp_path / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8").replace("(Version ", "(v"))
    before = {path: _read(tmp_path / path) for path in set_version.FILES}

    assert set_version.main(["9.8.7"]) == 1

    assert {path: _read(tmp_path / path) for path in set_version.FILES} == before
    assert commands == []
    assert "README.md: 0 matches" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("wanted", "expected"),
    [("patch", "1.2.4"), ("minor", "1.3.0"), ("major", "2.0.0"), ("1.10.0", "1.10.0")],
)
def test_the_new_version(wanted: str, expected: str) -> None:
    assert set_version.new_version("1.2.3", wanted) == expected


@pytest.mark.parametrize("wanted", ["1.3.0rc1", "1.3.0-rc.1", "1.3", "v1.3.0"])
def test_only_x_y_z_is_accepted(wanted: str) -> None:
    # Cargo and PyPI write pre-releases differently.
    with pytest.raises(ValueError, match="is not X.Y.Z"):
        set_version.new_version("1.2.3", wanted)


def test_no_other_file_states_the_version() -> None:
    if not (ROOT / ".git").exists() or shutil.which("git") is None:
        pytest.skip("not a git checkout")
    tracked = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout.decode()
    version = re.escape(set_version.current_version(ROOT))
    states = re.compile(rf"(?<![\w.]){version}(?![\w.-])")
    stating = set()
    for path in filter(None, tracked.split("\0")):
        try:
            text = (ROOT / path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if states.search(text):
            stating.add(path)

    assert stating - set(set_version.FILES) - NOT_SET == set(), (
        "These files state the version: add them to EDITS in "
        "scripts/set_version.py, or to NOT_SET here if they only record history."
    )
