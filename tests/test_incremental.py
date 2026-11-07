"""Incremental lint reports what a full run reports, after any edit.

On the native backend a lint run keeps what it read from each item under
the item's digest (`ddi_l._incremental`), and a later run re-reads only the
items whose digest changed. These tests edit documents at random and check
that each run's findings are a fresh run's, in the same order.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ddi_l import colectica_lint, lint, read_ddi
from ddi_l._etree import NATIVE
from tests.helpers.examples import examples

pytestmark = pytest.mark.skipif(not NATIVE, reason="needs the native backend")

FIXTURES = Path(__file__).parent / "fixtures" / "colectica"
DOCUMENTS = sorted(FIXTURES.glob("pets_*.xml"))
RULES = sorted(
    set(lint._PROFILE_REGISTRY[lint.COLECTICA_QUESTIONNAIRE_PROFILE])
    | set(lint._PROFILE_REGISTRY[lint.DDI_PROFILE_DEFAULT])
)
EXAMPLES = examples(300)

# Texts that the rules react to: pipes, placeholders, conditions, names.
_TEXTS = st.sampled_from(
    [
        "",
        "How many pets?",
        "#{PetCount} pets",
        "#{ }",
        "#{undeclared}",
        "[FILL]",
        "Next",
        "PetCount > 2",
        "PetCount >",
        "true",
        "pets.ddi",
    ]
)

_EDITS = st.lists(
    st.tuples(
        st.sampled_from(
            ["text", "remove", "duplicate", "move", "attribute", "identifier"]
        ),
        st.integers(min_value=0, max_value=10_000),
        _TEXTS,
    ),
    min_size=1,
    max_size=4,
)


def _edit(root, edit) -> None:
    kind, at, value = edit
    nodes = list(root.iter())[1:]
    node = nodes[at % len(nodes)]
    parent = next(p for p in root.iter() if any(c is node for c in p))
    index = list(parent).index(node)
    if kind == "text":
        node.text = value
    elif kind == "remove":
        parent.remove(node)
    elif kind == "duplicate":
        # Repeats every identifier in it: shared IDs, duplicate keys.
        parent.insert(index, copy.deepcopy(node))
    elif kind == "move" and index:
        parent.remove(node)
        parent.insert(index - 1, node)
    elif kind == "attribute":
        node.set("isUniversallyUnique", value or "false")
    elif kind == "identifier":
        identifier = next(
            (child for child in node.iter() if str(child.tag).endswith("}ID")), None
        )
        if identifier is not None:
            identifier.text = f"{identifier.text}{at % 3}"


def _outcome(document) -> object:
    try:
        found = lint.run_lint(document, RULES)
    except Exception as error:  # the same failure either way
        return type(error).__name__
    return [(f.rule_id, f.severity, f.message, f.location) for f in found]


def _fresh(document) -> object:
    cache = document.__dict__.pop("_incremental_cache", None)
    try:
        return _outcome(document)
    finally:
        document.__dict__.pop("_incremental_cache", None)
        if cache is not None:
            document.__dict__["_incremental_cache"] = cache


@EXAMPLES
@given(path=st.sampled_from(DOCUMENTS), rounds=st.lists(_EDITS, max_size=4))
def test_incremental_lint_reports_a_full_runs_findings(path: Path, rounds) -> None:
    document = read_ddi(path)
    assert _outcome(document) == _fresh(document)
    for edits in rounds:
        for edit in edits:
            _edit(document.root, edit)
        assert _outcome(document) == _fresh(document)


def test_a_later_run_reads_only_the_items_that_changed(monkeypatch) -> None:
    document = read_ddi(FIXTURES / "pets_conditions.ddi33.xml")
    read: list[object] = []
    original = colectica_lint._names_and_pipes

    def counting(context, item):
        read.append(item)
        return original(context, item)

    monkeypatch.setattr(colectica_lint, "_names_and_pipes", counting)
    rules = ["text.pipe-undeclared"]
    lint.run_lint(document, rules)
    items = len(read)
    assert items > 1
    read.clear()
    assert lint.run_lint(document, rules) == lint.run_lint(document, rules)
    assert read == []
    text = next(
        node
        for node in document.root.iter()
        if str(node.tag).endswith("}String") and (node.text or "").strip()
    )
    text.text = "#{undeclared}"
    found = lint.run_lint(document, rules)
    assert len(read) == 1
    assert any("#{undeclared}" in finding.message for finding in found)


def test_each_configuration_keeps_its_own_findings() -> None:
    document = read_ddi(FIXTURES / "pets_defects.ddi33.xml")
    rules = ["text.placeholder-unresolved", "text.pipe-undeclared"]
    plain = lint.run_lint(document, rules)
    named = lint.lint_configuration(
        known_names=("undeclared",), placeholder_patterns=(r"\[X\]",)
    )
    configured = lint.run_lint(document, rules, configuration=named)
    assert lint.run_lint(document, rules) == plain
    assert lint.run_lint(document, rules, configuration=named) == configured
    document.__dict__.pop("_incremental_cache")
    assert lint.run_lint(document, rules, configuration=named) == configured


def test_a_rule_reporting_about_another_item_runs_in_full(monkeypatch) -> None:
    document = read_ddi(FIXTURES / "pets_conditions.ddi33.xml")

    def about_the_first(target):
        # Wrongly marked per item: it reports about the first item whatever
        # items it is limited to.
        first = colectica_lint._context_items(target)[1][0]
        context = colectica_lint._Context(target)
        yield context.finding("test.first", "warning", first, "first")

    rule = lint._LintRule("test.first", about_the_first, "document", per_item=True)
    monkeypatch.setitem(lint._REGISTRY, "test.first", rule)
    assert len(lint.run_lint(document, ["test.first"])) == 1
    last = colectica_lint._context_items(document)[1][-1]
    last.set("changed", "1")
    assert len(lint.run_lint(document, ["test.first"])) == 1
