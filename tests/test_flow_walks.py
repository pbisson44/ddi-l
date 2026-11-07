"""Flow walks that no longer enumerate paths report what walking every path did."""

from __future__ import annotations

import time
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from ddi_l import read_ddi
from ddi_l.lint import run_lint
from tests.helpers.examples import examples
from tests.helpers.flow_documents import chained_diamonds, flow_documents
from tests.helpers.legacy_flow import legacy_read_before_computed

RULE = ["colectica.flow.read-before-computed"]


def _found(
    data: bytes,
) -> tuple[list[tuple[str, str | None]], list[tuple[str, str | None]]]:
    document = read_ddi(data)
    legacy = [(f.message, f.location) for f in legacy_read_before_computed(document)]
    found = [(f.message, f.location) for f in run_lint(document, rules=RULE)]
    return legacy, found


def _same(found, legacy) -> bool:
    """The legacy findings; with the solver, a finding may name a respondent."""
    return len(found) == len(legacy) and all(
        location == old_location and (message == old or message.startswith(f"{old} "))
        for (message, location), (old, old_location) in zip(found, legacy, strict=True)
    )


# Under mutation, 100: 30 random flows miss walks that 300 reach.
@examples(300, under_mutation=100)
@given(st.booleans().flatmap(lambda cycles: flow_documents(cycles=cycles)))
def test_read_before_computed_reports_what_every_path_reports(data: bytes):
    legacy, found = _found(data)

    assert _same(found, legacy)


# Flows that may loop back only: the walk then falls back to every path,
# which few of the flows above reach when they draw few examples.
@examples(300, under_mutation=100)
@given(flow_documents(cycles=True))
def test_a_flow_that_may_loop_reports_what_every_path_reports(data: bytes):
    legacy, found = _found(data)

    assert _same(found, legacy)


def test_a_flow_that_loops_back_is_walked_path_by_path():
    # A flow drawn by flow_documents(cycles=True) that loops and has a
    # finding: few draws loop, so mutation runs, which draw few, get it here.
    data = (
        Path(__file__).parent / "fixtures" / "flows" / "looping_flow.xml"
    ).read_bytes()
    legacy, found = _found(data)

    assert len(legacy) == 1
    assert _same(found, legacy)


def test_a_page_reached_by_many_paths_is_reported_as_before():
    legacy, found = _found(chained_diamonds(10))

    assert _same(found, legacy)
    assert len(found) == 1


def test_a_million_paths_are_not_walked_one_by_one():
    document = read_ddi(chained_diamonds(20))

    start = time.perf_counter()
    findings = run_lint(document, rules=RULE)
    elapsed = time.perf_counter() - start

    (finding,) = findings
    assert finding.message.startswith(
        "ComputationItem 00000000 (Reader), reached through Sequence 00000000 "
        "(Then 19), reads Asked before QuestionConstruct 00000000 (Asked) asks it."
    )
    assert elapsed < 5
