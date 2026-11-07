"""The spreadsheet-import page draws every link the table spec makes, and no other.

Each ``erDiagram`` line reads ``target <card>--<card> table : "column, ..."``:
the column of ``table`` holds ids of ``target``. The diagrams drifted from the
spec once (missing links, a one-to-many where a concept has several parents),
so this test compares them link by link, cardinality included.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ddi_l.tables import _spec

DOCS = Path(__file__).resolve().parents[1] / "docs"

# docs/ is not shipped in the sdist.
pytestmark = pytest.mark.skipif(
    not DOCS.is_dir(), reason="the docs are not shipped in the sdist"
)

# Columns that name rows of more than one table, or of their own table by
# value: the spec gives them no single `reference`. (tables named, many ids)
_SEVERAL = {
    ("question_blocks", "questions"): ({"questions", "question_grids"}, True),
    ("flow", "question"): ({"questions", "question_grids", "question_blocks"}, False),
    ("studies", "creator"): ({"organizations", "individuals"}, True),
    ("studies", "publisher"): ({"organizations", "individuals"}, True),
    ("codes", "parent"): ({"codes"}, False),
    **{
        ("comparisons", column): (
            {"concepts", "universes", "questions", "variables", "codes"},
            False,
        )
        for column in ("source", "target")
    },
}
_LINE = re.compile(r'^\s+(\w+) (\|\||\|o|\}o)--(?:o\||o\{) (\w+) : "([^"]+)"$')


def _drawn(page: Path) -> dict[tuple[str, str, str], str]:
    """(table, column, target) -> the cardinality drawn at the target's end."""
    drawn = {}
    blocks = re.findall(r"```mermaid\nerDiagram\n(.*?)```", page.read_text(), re.S)
    assert blocks, page
    for block in blocks:
        for line in block.splitlines():
            match = _LINE.match(line)
            assert match, f"{page.name}: unreadable line {line!r}"
            target, cardinality, table, columns = match.groups()
            for column in columns.split(", "):
                drawn[(table, column, target)] = cardinality
    return drawn


def _expected() -> dict[tuple[str, str, str], set[str]]:
    """(table, column, target) -> the cardinalities that are right for it."""
    tables = {t.name: t for t in vars(_spec).values() if isinstance(t, _spec.Table)}
    expected = {}
    for table in tables.values():
        for column in table.columns:
            if column.reference:
                targets, many, exact = {column.reference}, column.multiple, True
            elif (table.name, column.name) in _SEVERAL:
                (targets, many), exact = _SEVERAL[(table.name, column.name)], False
            else:
                continue
            if many:
                allowed = {"}o"}
            elif column.required and exact:
                allowed = {"||"}
            else:
                # An optional `study` column still names exactly one study.
                allowed = {"|o", "||"}
            for target in targets:
                expected[(table.name, column.name, target)] = allowed
    return expected


def test_the_diagrams_draw_every_link_of_the_table_spec() -> None:
    drawn = _drawn(DOCS / "spreadsheet-import.en.md")
    expected = _expected()
    assert sorted(set(expected) - set(drawn)) == [], "links not drawn"
    assert sorted(set(drawn) - set(expected)) == [], "links the spec does not make"
    wrong = {key: card for key, card in drawn.items() if card not in expected[key]}
    assert wrong == {}, "wrong cardinality"


def test_both_languages_draw_the_same_diagrams() -> None:
    def diagrams(page: str) -> list[str]:
        text = (DOCS / page).read_text()
        return re.findall(r"```mermaid\nerDiagram\n.*?```", text, re.S)

    assert diagrams("spreadsheet-import.fr.md") == diagrams("spreadsheet-import.en.md")
