"""What one run builds from a document is built once and shared (`_facts`)."""

from __future__ import annotations

import threading
from collections import Counter
from pathlib import Path

import pytest

from ddi_l import _facts, colectica_lint, colectica_logic, read_ddi
from ddi_l._etree import Element
from ddi_l.colectica_lint import _ITEM_TYPES, _innermost_items, _local
from ddi_l.lint import COLECTICA_QUESTIONNAIRE_PROFILE, run_lint, run_profile
from tests import TEST_FIXTURES_DIR

DEFECTS = TEST_FIXTURES_DIR / "colectica" / "pets_defects.ddi33.xml"


def test_a_build_is_shared_inside_a_scope_only():
    owner, other = object(), object()
    calls: list[object] = []

    def build() -> list[object]:
        calls.append(owner)
        return []

    assert _facts.shared("kind", owner, build) is not _facts.shared(
        "kind", owner, build
    )
    with _facts.run_scope():
        first = _facts.shared("kind", owner, build)
        with _facts.run_scope():  # re-entrant: the same run
            assert _facts.shared("kind", owner, build) is first
        assert _facts.shared("kind", other, build) is not first
        # Building for another owner keeps the first owner's build.
        assert _facts.shared("kind", owner, build) is first
        assert _facts.shared("another kind", owner, build) is not first
        assert _facts.shared_by_value("value", ("a", "b"), build) is (
            _facts.shared_by_value("value", ("a", "b"), build)
        )
        # One key under two kinds is two builds.
        assert _facts.shared_by_value("other", ("a", "b"), build) is not (
            _facts.shared_by_value("value", ("a", "b"), build)
        )
    assert _facts.shared("kind", owner, build) is not first
    assert len(calls) == 8


def test_each_thread_has_its_own_run():
    built: list[str] = []

    def lint(name: str) -> None:
        with _facts.run_scope():
            _facts.shared("kind", DEFECTS, lambda: built.append(name))

    with _facts.run_scope():
        threads = [threading.Thread(target=lint, args=(n,)) for n in "ab"]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    assert sorted(built) == ["a", "b"]


def test_a_profile_run_builds_its_context_and_conditions_once(monkeypatch):
    document = read_ddi(DEFECTS)
    contexts = Counter[int]()
    commands = Counter[tuple[str | None, str | None]]()
    build_context = colectica_lint._context_items
    parse = colectica_lint.parse_command

    def counting_context(target):
        contexts[id(target.root)] += 1
        return build_context(target)

    def counting_parse(language, text):
        commands[(language, text)] += 1
        return parse(language, text)

    monkeypatch.setattr(colectica_lint, "_context_items", counting_context)
    monkeypatch.setattr(colectica_lint, "parse_command", counting_parse)

    findings = run_profile(
        document, COLECTICA_QUESTIONNAIRE_PROFILE, include_schema=False
    ).lint_findings

    assert findings
    assert list(contexts.values()) == [1]
    assert commands and set(commands.values()) == {1}


def test_a_document_edited_between_runs_is_read_afresh():
    document = read_ddi(DEFECTS)
    rule = ["colectica.identifiable.shared-id"]
    assert run_lint(document, rules=rule)

    # Keep the TopLevelReference and the first fragment only.
    for fragment in list(document.root)[2:]:
        document.root.remove(fragment)

    assert run_lint(document, rules=rule) == []


def test_cached_conditions_are_left_as_parsed():
    document = read_ddi(DEFECTS)
    with _facts.run_scope():
        run_profile(document, COLECTICA_QUESTIONNAIRE_PROFILE, include_schema=False)
        context = colectica_lint._Context(document)
        for entry in colectica_lint._conditions(
            context, "IfThenElse", "ComputationItem", "Loop"
        ):
            language = entry.command.findtext(context.r("ProgramLanguage"))
            text = entry.command.findtext(context.r("CommandContent"))
            try:
                fresh = colectica_logic.parse_command(language, text)
            except colectica_logic.ConditionFormatError:
                fresh = None
            assert entry.condition == fresh


def _innermost_by_search(root: Element) -> list[Element]:
    """What `_innermost_items` replaced: a search of each item's subtree."""
    candidates = [
        element
        for element in root.iter()
        if element is not root and _local(element.tag) in _ITEM_TYPES
    ]
    return [
        element
        for element in candidates
        if not any(
            _local(node.tag) in _ITEM_TYPES
            for node in element.iter()
            if node is not element
        )
    ]


@pytest.mark.parametrize(
    "path",
    [
        path
        for path in sorted(TEST_FIXTURES_DIR.glob("*.xml"))
        + sorted((TEST_FIXTURES_DIR / "colectica").glob("*.xml"))
        # Deliberately truncated, for the parser's error tests.
        if path.name != "malformed_instance.xml"
    ],
    ids=lambda path: Path(path).name,
)
def test_innermost_items_are_those_a_subtree_search_finds(path: Path):
    document = read_ddi(path)
    assert _innermost_items(document.root) == _innermost_by_search(document.root)
