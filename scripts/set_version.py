#!/usr/bin/env python3
"""Set ddi-l's version in every file that states it, then re-lock.

    uv run python scripts/set_version.py 0.3.0
    uv run python scripts/set_version.py patch --date 2027-01-15

ddi-l and ddi-l-native share one version. The argument is the new version
(X.Y.Z) or the part to bump (major, minor or patch). --date is the release
date for CITATION.cff, whose year the citations repeat; it defaults to today.
Nothing is written unless every file below matches, then `uv lock` runs.

tests/test_set_version.py fails when another file starts stating the version.
"""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_V = r"(\d+\.\d+\.\d+)"
_Y = r"(\d{4})"

# (file, pattern, value): the pattern matches once, and its group is replaced
# by the version, the release date or its year. uv.lock is left to `uv lock`.
EDITS: list[tuple[str, str, str]] = [
    ("pyproject.toml", r'^version = "' + _V + '"', "version"),
    ("pyproject.toml", r'"ddi-l-native==' + _V + '"', "version"),
    ("native/pyproject.toml", r'^version = "' + _V + '"', "version"),
    ("native/fallback/pyproject.toml", r'^version = "' + _V + '"', "version"),
    ("native/Cargo.toml", r'^version = "' + _V + '"', "version"),
    (
        "native/Cargo.lock",
        r'^name = "ddi-l-native"\r?\nversion = "' + _V + '"',
        "version",
    ),
    ("CITATION.cff", r"^version: " + _V, "version"),
    ("CITATION.cff", r'^date-released: "(\d{4}-\d{2}-\d{2})"', "date"),
    ("docs/release-notes.en.md", r"^## " + _V + r" \(unreleased\)", "version"),
    ("docs/release-notes.fr.md", r"^## " + _V + r" \(non publiée\)", "version"),
]
for _page in ("README.md", "docs/index.en.md", "docs/index.fr.md"):
    EDITS.append((_page, r"\(Version " + _V + r"\)", "version"))
    EDITS.append((_page, r"Bisson, P\. \(" + _Y + r"\)", "year"))
for _page in ("docs/index.en.md", "docs/index.fr.md"):
    EDITS.append((_page, r"^  version = \{" + _V + r"\},", "version"))
    EDITS.append((_page, r"^  year    = \{" + _Y + r"\},", "year"))

FILES = sorted({path for path, _, _ in EDITS})


def current_version(root: Path) -> str:
    """The version in `root`'s pyproject.toml."""
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return str(project["project"]["version"])


def new_version(current: str, wanted: str) -> str:
    """`wanted` itself, or `current` with its major, minor or patch bumped."""
    if wanted in ("major", "minor", "patch"):
        major, minor, patch = (int(part) for part in current.split("."))
        return {
            "major": f"{major + 1}.0.0",
            "minor": f"{major}.{minor + 1}.0",
            "patch": f"{major}.{minor}.{patch + 1}",
        }[wanted]
    if not re.fullmatch(r"\d+\.\d+\.\d+", wanted):
        # Cargo and PyPI write pre-releases differently (0.3.0-rc.1, 0.3.0rc1).
        raise ValueError(f"{wanted!r} is not X.Y.Z, major, minor or patch")
    return wanted


def plan(
    root: Path, version: str, date: datetime.date
) -> tuple[dict[str, str], list[str]]:
    """The new text of each file, and the problems that stop the change."""
    values = {"version": version, "date": date.isoformat(), "year": str(date.year)}
    texts: dict[str, str] = {}
    problems: list[str] = []
    for path, pattern, value in EDITS:
        if path not in texts:
            try:
                with open(root / path, encoding="utf-8", newline="") as file:
                    texts[path] = file.read()
            except FileNotFoundError:
                problems.append(f"{path}: missing")
                texts[path] = ""
                continue
        matches = list(re.finditer(pattern, texts[path], re.MULTILINE))
        if len(matches) != 1:
            problems.append(f"{path}: {len(matches)} matches for {pattern!r}")
            continue
        start, end = matches[0].span(1)
        texts[path] = texts[path][:start] + values[value] + texts[path][end:]
    return texts, problems


def main(argv: list[str] | None = None) -> int:
    """Write the new version everywhere and re-lock; 1 if a file does not match."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("version", help="X.Y.Z, or major, minor or patch")
    parser.add_argument(
        "--date",
        type=datetime.date.fromisoformat,
        default=datetime.date.today(),
        help="release date, YYYY-MM-DD (default: today)",
    )
    args = parser.parse_args(argv)
    try:
        version = new_version(current_version(ROOT), args.version)
    except ValueError as error:
        parser.error(str(error))

    texts, problems = plan(ROOT, version, args.date)
    if problems:
        print("Nothing changed:", *problems, sep="\n  ", file=sys.stderr)
        return 1
    for path, text in texts.items():
        with open(ROOT / path, "w", encoding="utf-8", newline="") as file:
            file.write(text)
    print(f"Version {version}, released {args.date}:", *FILES, sep="\n  ")

    subprocess.run(["uv", "lock"], cwd=ROOT, check=True)
    series = ".".join(version.split(".")[:2])
    if f"{series}.x" not in (ROOT / "SECURITY.md").read_text(encoding="utf-8"):
        print(f"Still to do: add the {series}.x series to SECURITY.md's table.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
