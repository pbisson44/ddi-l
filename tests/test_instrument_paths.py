"""Conformance reads every path to a construct without walking them one by one."""

from __future__ import annotations

import importlib
import time
from collections import Counter
from unittest import mock

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tests.helpers.examples import examples

pytest.importorskip("yaml", reason="requires the 'spec' extra")
pytest.importorskip("jsonschema", reason="requires the 'spec' extra")

from ddi_l import read_ddi
from ddi_l.colectica_lint import _Context
from ddi_l.spec import conform, spec_from_data
from ddi_l.spec._instrument import GateTerm, InstrumentIndex, Node
from tests.helpers.instrument_documents import chained_gates, instrument_documents
from tests.helpers.legacy_instrument import LegacyInstrumentIndex

conform_module = importlib.import_module("ddi_l.spec.conform")
# Under mutation, 100: 30 random instruments miss paths that 300 reach.
EXAMPLES = examples(300, under_mutation=100)
DOCUMENTS = st.booleans().flatmap(lambda cycles: instrument_documents(cycles=cycles))


def _indexes(data: bytes) -> tuple[InstrumentIndex, InstrumentIndex]:
    document = read_ddi(data)
    context = _Context(document)
    (instrument,) = context.items_of_type("Instrument")
    return (
        InstrumentIndex(context, instrument),
        LegacyInstrumentIndex(context, instrument),
    )


@EXAMPLES
@given(DOCUMENTS)
def test_conformance_reports_what_walking_every_path_reports(drawn):
    data, spec_data = drawn
    spec = spec_from_data(spec_data)

    found = conform(read_ddi(data), spec).as_dict()
    with mock.patch.object(conform_module, "InstrumentIndex", LegacyInstrumentIndex):
        legacy = conform(read_ddi(data), spec).as_dict()

    assert found == legacy


@EXAMPLES
@given(DOCUMENTS)
def test_a_node_stands_for_every_path_to_its_construct_under_its_sequences(drawn):
    index, legacy = _indexes(drawn[0])

    def place(node: Node) -> tuple[int, tuple[int, ...]]:
        return (id(node.element), tuple(map(id, node.sequences)))

    def firsts(nodes: list[Node]) -> dict[tuple[int, tuple[int, ...]], Node]:
        found: dict[tuple[int, tuple[int, ...]], Node] = {}
        for node in nodes:
            found.setdefault(place(node), node)
        return found

    def paths(nodes: list[Node]) -> Counter[tuple[int, tuple[int, ...]]]:
        counts = Counter[tuple[int, tuple[int, ...]]]()
        for node in nodes:
            counts[place(node)] += node.paths
        return counts

    # Where a path can meet a construct twice, each path is a node of its own.
    first, legacy_first = firsts(index.nodes), firsts(legacy.nodes)
    assert list(first) == list(legacy_first)
    assert paths(index.nodes) == paths(legacy.nodes)
    for at, node in first.items():
        assert (node.gates, node.entered) == (
            legacy_first[at].gates,
            legacy_first[at].entered,
        )


@EXAMPLES
@given(DOCUMENTS)
def test_the_first_path_with_a_property_is_the_one_walking_finds(drawn):
    index, legacy = _indexes(drawn[0])

    def found(on, below, fold, start, accept):
        targets = [
            node
            for node in on.of_kind("QuestionConstruct", "StatementItem")
            if below in node.sequences
        ]
        path = on.first_path(targets, below, fold, start, accept)
        return None if path is None else (path[0].element, path[0].sequences, path[1])

    def else_branch(seen: bool, term: GateTerm) -> bool:
        return seen or term.branch < 0

    def gates(terms: frozenset[GateTerm], term: GateTerm) -> frozenset[GateTerm]:
        return terms | {term}

    none: frozenset[GateTerm] = frozenset()
    for module in index.nodes:
        if not module.is_page_or_module:
            continue
        below = module.element
        for fold, start, accept in (
            (else_branch, False, bool),
            (else_branch, False, lambda seen: not seen),
            (gates, none, lambda terms: len(terms) > 1),
        ):
            assert found(index, below, fold, start, accept) == found(
                legacy, below, fold, start, accept
            )


def test_a_question_reached_by_a_million_paths_is_compared_at_once():
    data, spec_data = chained_gates(20)
    spec = spec_from_data(spec_data)

    start = time.perf_counter()
    report = conform(read_ddi(data), spec)
    elapsed = time.perf_counter() - start

    assert [
        (finding.item, finding.message)
        for finding in report.findings
        if finding.rule_id == "spec.gate.unverifiable"
    ] == [
        (
            "Q1",
            "The gate of question Q1 cannot be compared: it is reached by "
            "1048576 paths with different gates.",
        )
    ]
    assert elapsed < 5


def test_an_output_without_an_alias_gives_no_alias() -> None:
    from tests.helpers.instrument_documents import _DC, _document, _id, _identity

    def output(index: int, alias: str | None) -> str:
        named = "" if alias is None else f"<r:Alias>{alias}</r:Alias>"
        return f"<r:OutParameter>{_identity(_id(1, index))}{named}</r:OutParameter>"

    question = (
        f'<Fragment><QuestionConstruct xmlns="{_DC}">{_identity(_id(0, 1))}'
        + output(1, None)
        + output(2, "  ")
        + output(3, "Q1")
        + output(4, "Q1")
        + "</QuestionConstruct></Fragment>"
    )
    sequence = (
        f'<Fragment><Sequence xmlns="{_DC}">{_identity(_id(0, 0))}'
        f"<ControlConstructReference><r:Agency>int.example</r:Agency>"
        f"<r:ID>{_id(0, 1)}</r:ID><r:Version>1</r:Version>"
        "<r:TypeOfObject>QuestionConstruct</r:TypeOfObject>"
        "</ControlConstructReference></Sequence></Fragment>"
    )
    index, _ = _indexes(_document([sequence, question]))
    (node,) = index.of_kind("QuestionConstruct")

    assert index.ids(node.element, "construct_alias") == ["Q1"]


def _fragment(kind: str, index: int, body: str) -> str:
    from tests.helpers.instrument_documents import _DC, _id, _identity

    return (
        f'<Fragment><{kind} xmlns="{_DC}">{_identity(_id(0, index))}{body}'
        f"</{kind}></Fragment>"
    )


def _to(tag: str, index: int, kind: str) -> str:
    from tests.helpers.instrument_documents import _id, _reference

    return _reference(tag, _id(0, index), kind)


def test_each_branch_of_a_gate_is_its_own_term() -> None:
    from tests.helpers.instrument_documents import _document

    gate = (
        _to("ThenConstructReference", 2, "StatementItem")
        + "<ElseIf>"
        + _to("ThenConstructReference", 3, "StatementItem")
        + "</ElseIf><ElseIf>"
        + _to("ThenConstructReference", 4, "StatementItem")
        + "</ElseIf>"
        + _to("ElseConstructReference", 5, "StatementItem")
    )
    index, _ = _indexes(
        _document(
            [
                _fragment(
                    "Sequence", 0, _to("ControlConstructReference", 1, "IfThenElse")
                ),
                _fragment("IfThenElse", 1, gate),
                *(_fragment("StatementItem", n, "") for n in (2, 3, 4, 5)),
            ]
        )
    )

    assert [
        [term.branch for term in node.gates] for node in index.of_kind("StatementItem")
    ] == [[0], [1], [2], [-1]]


def test_the_bodies_of_repeats_are_followed() -> None:
    from tests.helpers.instrument_documents import _document

    index, _ = _indexes(
        _document(
            [
                _fragment(
                    "Sequence",
                    0,
                    _to("ControlConstructReference", 1, "RepeatUntil")
                    + _to("ControlConstructReference", 2, "RepeatWhile"),
                ),
                _fragment(
                    "RepeatUntil", 1, _to("UntilConstructReference", 3, "StatementItem")
                ),
                _fragment(
                    "RepeatWhile", 2, _to("WhileConstructReference", 4, "StatementItem")
                ),
                _fragment("StatementItem", 3, ""),
                _fragment("StatementItem", 4, ""),
            ]
        )
    )

    assert len(index.of_kind("StatementItem")) == 2


def test_only_a_conditional_child_container_is_a_branch_body() -> None:
    from tests.helpers.instrument_documents import _document

    def typed(kind: str) -> str:
        return f"<TypeOfSequence>{kind}</TypeOfSequence>"

    index, _ = _indexes(
        _document(
            [
                _fragment(
                    "Sequence",
                    0,
                    _to("ControlConstructReference", 1, "Sequence")
                    + _to("ControlConstructReference", 2, "Sequence")
                    + _to("ControlConstructReference", 3, "Sequence"),
                ),
                _fragment("Sequence", 1, typed("ConditionalChildContainer")),
                _fragment("Sequence", 2, typed("Loop")),
                _fragment("Sequence", 3, "<TypeOfSequence/>"),
            ]
        )
    )

    assert [node.is_page_or_module for node in index.nodes] == [True, False, True, True]


def test_a_construct_the_instrument_leads_to_twice_has_two_paths() -> None:
    from tests.helpers.instrument_documents import _DC, _id, _identity

    sequence = _fragment("Sequence", 0, "")
    twice = _to("ControlConstructReference", 0, "Sequence") * 2
    data = (
        '<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3">'
        + _to("TopLevelReference", 0, "Instrument").replace(_id(0, 0), _id(3, 0))
        + f'<Fragment><Instrument xmlns="{_DC}">{_identity(_id(3, 0))}{twice}'
        + "</Instrument></Fragment>"
        + sequence
        + "</FragmentInstance>"
    ).encode()
    index, _ = _indexes(data)

    (node,) = index.nodes
    assert node.paths == 2


def test_one_id_under_two_agencies_is_two_constructs() -> None:
    from tests.helpers.instrument_documents import AGENCY, _document

    other = "other.example"
    outer = _fragment(
        "Sequence",
        0,
        _to("ControlConstructReference", 0, "Sequence").replace(AGENCY, other),
    )
    inner = (
        _fragment("Sequence", 0, _to("ControlConstructReference", 1, "StatementItem"))
        .replace(f"{AGENCY}:", f"{other}:")
        .replace(
            f"<r:Agency>{AGENCY}</r:Agency><r:ID>",
            f"<r:Agency>{other}</r:Agency><r:ID>",
            1,
        )
    )
    index, _ = _indexes(_document([outer, inner, _fragment("StatementItem", 1, "")]))

    assert [node.kind for node in index.nodes] == [
        "Sequence",
        "Sequence",
        "StatementItem",
    ]


def test_ids_come_from_the_place_each_source_names() -> None:
    from tests.helpers.instrument_documents import _document, _id

    item = _id(0, 2)
    construct = (
        '<r:Label><r:Content xml:lang="en">Pets</r:Content></r:Label>'
        '<r:UserID typeOfUserID="x">PET-1</r:UserID>'
        "<r:QuestionReference><r:Agency>int.example</r:Agency>"
        f"<r:ID>{item}</r:ID><r:Version>1</r:Version>"
        "<r:TypeOfObject>QuestionItem</r:TypeOfObject></r:QuestionReference>"
    )
    question = (
        '<QuestionItemName><r:String xml:lang="en">PetCount</r:String>'
        '</QuestionItemName><QuestionText><LiteralText><Text xml:lang="en">'
        "How many?</Text></LiteralText></QuestionText>"
    )
    index, _ = _indexes(
        _document(
            [
                _fragment(
                    "Sequence",
                    0,
                    _to("ControlConstructReference", 1, "QuestionConstruct"),
                ),
                _fragment("QuestionConstruct", 1, construct),
                _fragment("QuestionItem", 2, question),
            ]
        )
    )
    (node,) = index.of_kind("QuestionConstruct")

    assert index.ids(node.element, "label") == ["Pets"]
    assert index.ids(node.element, "user_id") == ["PET-1"]
    assert index.ids(node.element, "item_name") == ["PetCount"]
