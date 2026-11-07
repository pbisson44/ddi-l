"""ddi-l ships no organisation-specific names or tokens.

The library, its documentation and its synthetic fixtures are tool- and
organisation-neutral: anything specific to one organisation (its name, its
survey templates, the tokens of its legacy specifications) belongs in that
organisation's own configuration, not here. This test fails on a new
occurrence; ``tests/org_agnostic_allowlist.txt`` lists the deliberate ones.
"""

from __future__ import annotations

import gzip
import re
import zipfile
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = PROJECT_ROOT / "tests" / "org_agnostic_allowlist.txt"

SCANNED_TREES = ("src", "docs")
# Synthetic fixture directories held to the same boundary. A PR adding a
# fixture directory appends it here.
SCANNED_FIXTURE_DIRS = ("tests/fixtures/colectica", "tests/fixtures/spec")

# Whole words, case-insensitive. "BCP 47" is the language-tag standard, not an
# organisation's system, so it is not a match.
_TOKENS = (
    "statcan",
    "statistique canada",
    "statistics canada",
    "bst",
    "bcp",
    "nonresponse",
    "thisdate",
    "ibsp",
    "gc.ca",
    "aria",
)
# "aria" is one organisation's metadata system; HTML's aria-* attributes are
# not a match.
_PATTERN = re.compile(
    r"\b(statcan|statistique\s+canada|statistics\s+canada|bst|bcp(?![\s-]*47)"
    r"|nonresponse|thisdate|ibsp|gc\.ca|ari[aā](?!-))\b",
    re.IGNORECASE,
)
_SKIPPED_SUFFIXES = {".xsd", ".pyc", ".png", ".jpg", ".svg", ".ico"}
# Workbooks and archives are scanned member by member.
_ARCHIVE_SUFFIXES = {".xlsx", ".zip"}


@dataclass(frozen=True)
class _Entry:
    glob: str
    token: str
    line: int

    def covers(self, path: str, token: str) -> bool:
        return token == self.token and fnmatchcase(path, self.glob)


def _token(match: str) -> str:
    token = " ".join(match.lower().split())
    return "aria" if token == "ariā" else token


def _read_allowlist() -> list[_Entry]:
    entries: list[_Entry] = []
    for number, raw in enumerate(ALLOWLIST.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        glob, _, token = line.partition(" ")
        token = " ".join(token.split())
        assert token in _TOKENS, f"allowlist line {number}: unknown token {token!r}"
        entries.append(_Entry(glob=glob, token=token, line=number))
    return entries


def _scanned_files() -> list[Path]:
    roots = [PROJECT_ROOT / tree for tree in (*SCANNED_TREES, *SCANNED_FIXTURE_DIRS)]
    files: list[Path] = []
    for root in roots:
        for path in root.rglob("*"):
            if (
                path.is_file()
                and "_generated" not in path.parts
                and "__pycache__" not in path.parts
                and path.suffix.lower() not in _SKIPPED_SUFFIXES
            ):
                files.append(path)
    return files


def _occurrences() -> list[tuple[str, str, int]]:
    """Every (path, token, line) the pattern finds in the scanned files."""
    found: list[tuple[str, str, int]] = []
    for path in _scanned_files():
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        for text in _texts(path):
            for match in _PATTERN.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                found.append((relative, _token(match.group(1)), line))
    return found


def _texts(path: Path) -> list[str]:
    """The text of ``path``, or of each member of a workbook or archive.

    A file that is not UTF-8 fails the test rather than going unscanned.
    """
    if path.suffix.lower() in _ARCHIVE_SUFFIXES:
        with zipfile.ZipFile(path) as archive:
            return [archive.read(name).decode("utf-8") for name in archive.namelist()]
    if path.suffix.lower() == ".gz":  # the schema IR
        return [gzip.decompress(path.read_bytes()).decode("utf-8")]
    return [path.read_text(encoding="utf-8")]


def test_no_new_organisation_specific_tokens() -> None:
    entries = _read_allowlist()
    violations = [
        f"{path}:{line}: {token!r}"
        for path, token, line in _occurrences()
        if not any(entry.covers(path, token) for entry in entries)
    ]
    assert not violations, (
        "Organisation-specific tokens found (keep ddi-l neutral, or add a "
        "justified entry to tests/org_agnostic_allowlist.txt):\n"
        + "\n".join(violations[:50])
    )


def _shipped(entry: _Entry) -> bool:
    """Whether the tree an entry names is here; the sdist ships no docs/."""
    top = entry.glob.split("/", 1)[0]
    return any(char in top for char in "*?[") or (PROJECT_ROOT / top).exists()


def test_every_allowlist_entry_is_still_needed() -> None:
    occurrences = _occurrences()
    stale = [
        f"line {entry.line}: {entry.glob} {entry.token}"
        for entry in _read_allowlist()
        if _shipped(entry)
        and not any(entry.covers(path, token) for path, token, _ in occurrences)
    ]
    assert not stale, "Allowlist entries that match nothing:\n" + "\n".join(stale)


def test_the_guard_matches_what_it_should() -> None:
    def tokens(text: str) -> list[str]:
        return [_token(match) for match in _PATTERN.findall(text)]

    assert tokens("agency ca.statcan and Statistics  Canada") == [
        "statcan",
        "statistics canada",
    ]
    assert tokens("the BST template, NONRESPONSE and THISDATE") == [
        "bst",
        "nonresponse",
        "thisdate",
    ]
    assert tokens("a BCP 47 tag, BCP-47, bcp47") == []
    assert tokens("supplied by BCP") == ["bcp"]
    assert tokens("bestiary, abstract, IBSPx") == []
    assert tokens("www.example.gc.ca, Ariā and Aria") == ["gc.ca", "aria", "aria"]
    assert tokens('<a aria-label="x">, a variable, an aria') == ["aria"]


# The course teaches DDI and ddi-l, not one vendor's questionnaire tool:
# guidance for a particular tool lives in the how-to guides.
_CURRICULUM = PROJECT_ROOT / "docs" / "curriculum"
_TOOL_NAMES = re.compile(r"\b(colectica|blaise)\b", re.IGNORECASE)


def test_the_curriculum_names_no_questionnaire_tool() -> None:
    found = []
    for path in sorted(_CURRICULUM.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in _TOOL_NAMES.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            relative = path.relative_to(PROJECT_ROOT).as_posix()
            found.append(f"{relative}:{line}: {match.group(0)}")
    assert not found, "The curriculum names a questionnaire tool:\n" + "\n".join(found)
