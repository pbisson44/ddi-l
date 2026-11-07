"""Which constructs a respondent reaches, against walking every path.

`ddi_l.spec._routing` encodes a flow once for the solver. The oracle here
enumerates every respondent of a small random flow and walks every path of
the flow (`tests.helpers.legacy_instrument`): a respondent's interview is
the path nodes, in walk order, whose gates all hold for them.
"""

from __future__ import annotations

import itertools
from fractions import Fraction

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from tests.helpers.examples import examples

pytest.importorskip("z3", reason="requires the 'logic' extra")

from ddi_l import read_ddi
from ddi_l.colectica_lint import _Context
from ddi_l.spec._instrument import GateTerm
from ddi_l.spec._routing import Routing
from ddi_l.spec.expression import identifiers
from ddi_l.spec.semantics import ANSWERED, Answer, Example, evaluate
from tests.helpers.instrument_documents import instrument_documents
from tests.helpers.legacy_instrument import LegacyInstrumentIndex

EXAMPLES = examples(300)
# Flows with many gates, each reading a question, so that some are nested
# on one question and rule constructs out.
FLOWS = st.booleans().flatmap(
    lambda readable: instrument_documents(
        max_nodes=10,
        kinds_drawn=(
            "Module",
            "Body",
            "IfThenElse",
            "IfThenElse",
            "QuestionConstruct",
        ),
        bound=True,
        readable=readable,
    )
)
# Enough to separate = 1 from > 1, the operators the flows use.
_ANSWERS = (
    None,
    Answer(ANSWERED, frozenset({Fraction(1)})),
    Answer(ANSWERED, frozenset({Fraction(2)})),
)


def _routing(data: bytes) -> tuple[Routing, LegacyInstrumentIndex]:
    context = _Context(read_ddi(data))
    (instrument,) = context.items_of_type("Instrument")
    return Routing(context, instrument), LegacyInstrumentIndex(context, instrument)


def _respondents(routing: Routing):
    names = sorted(
        {
            name
            for conditions in routing._conditions.values()
            for condition in conditions
            for name in identifiers(condition)
        }
    )
    assume(len(_ANSWERS) ** len(names) <= 3000)
    for answers in itertools.product(_ANSWERS, repeat=len(names)):
        yield {
            name: answer for name, answer in zip(names, answers, strict=True) if answer
        }


def _holds(routing: Routing, term: GateTerm, answers) -> bool:
    conditions = [evaluate(c, answers) for c in routing._conditions[id(term.gate)]]
    if term.branch == 0:
        return conditions[0]
    if term.branch > 0:
        return not any(conditions[: term.branch]) and conditions[term.branch]
    return not any(conditions)


def _interview(routing: Routing, legacy: LegacyInstrumentIndex, answers):
    """The constructs a respondent is asked, in order."""
    return [
        node.element
        for node in legacy.nodes
        if all(_holds(routing, term, answers) for term in node.gates)
    ]


@EXAMPLES
@given(FLOWS)
def test_a_construct_is_reachable_when_some_respondent_reaches_it(drawn) -> None:
    routing, legacy = _routing(drawn[0])
    interviews = [_interview(routing, legacy, a) for a in _respondents(routing)]
    reached = {id(element) for interview in interviews for element in interview}
    constructs = routing._order[1:]
    for element in constructs:
        found = routing.flow.check(routing.reached(element))
        assert found is not None
        if routing._cyclic:
            # A loop may count as reached what it alone would reach.
            assert found or id(element) not in reached
        else:
            assert found == (id(element) in reached)
    unreachable = routing.unreachable()
    assert all(id(element) not in reached for element in unreachable)
    if routing._cyclic:
        return
    # The first construct no one reaches, in walk order, is always reported.
    first = next((e for e in constructs if id(e) not in reached), None)
    assert (first is None) == (not unreachable)
    if first is not None:
        assert first in unreachable


@EXAMPLES
@given(FLOWS)
def test_a_respondent_reaches_a_reader_first_as_the_solver_says(drawn) -> None:
    routing, legacy = _routing(drawn[0])
    respondents = list(_respondents(routing))
    constructs = routing._order[1:]
    questions = [c for c in constructs if c.tag.endswith("}QuestionConstruct")]

    def first(interview, reader, producer) -> bool:
        for element in interview:
            if element is producer:
                return False
            if element is reader:
                return True
        return False

    interviews = [_interview(routing, legacy, answers) for answers in respondents]
    for reader, producer in itertools.product(constructs, questions):
        if reader is producer:
            continue
        found = routing.respondent_before(reader, producer)
        expected = any(first(i, reader, producer) for i in interviews)
        if found is False:
            assert not expected
        elif isinstance(found, Example):
            assert expected
            # The respondent given passes: their interview reaches the
            # reader first.
            assert first(_interview(routing, legacy, found.answers), reader, producer)


# ---- Reading gates without a spec ---------------------------------------------

_R = "ddi:reusable:3_3"


def _flow(gate_one: str, gate_two: str, extra: str = "") -> bytes:
    """Module 0: question 1 (output PetCount), then gate 2, whose Then is gate
    3, whose Then is statement 4. Both gates read the question."""
    from tests.helpers.instrument_documents import (
        _binding,
        _document,
        _id,
        _identity,
        _name,
        _reference,
    )

    def item(local: str, index: int, body: str) -> str:
        return (
            f'<Fragment><{local} xmlns="ddi:datacollection:3_3">'
            f"{_identity(_id(0, index))}{body}</{local}></Fragment>"
        )

    def gate(index: int, condition: str, then: int) -> str:
        parameter = _id(2, index)
        return item(
            "IfThenElse",
            index,
            _name(f"G{index}")
            + f"<r:InParameter>{_identity(parameter)}<r:Alias>Count</r:Alias>"
            "</r:InParameter>"
            + condition
            + _reference("ThenConstructReference", _id(0, then), "Sequence"),
        )

    module = item(
        "Sequence",
        0,
        _name("M0")
        + _reference("ControlConstructReference", _id(0, 1), "QuestionConstruct")
        + _reference("ControlConstructReference", _id(0, 2), "IfThenElse"),
    )
    question = item(
        "QuestionConstruct",
        1,
        _name("Q1")
        + f"<r:OutParameter>{_identity(_id(1, 1))}<r:Alias>PetCount</r:Alias>"
        "</r:OutParameter>",
    )
    statement = item("StatementItem", 4, _name("S4"))
    bindings = _binding(_id(1, 1), _id(2, 2)) + _binding(_id(1, 1), _id(2, 3))
    return _document(
        [
            module,
            question,
            gate(2, gate_one, 3),
            gate(3, gate_two, 4),
            statement,
            extra,
        ],
        bindings,
    )


def _command(language: str, content: str) -> str:
    return (
        f"<IfCondition><r:Command><r:ProgramLanguage>{language}</r:ProgramLanguage>"
        f"<r:CommandContent>{content}</r:CommandContent></r:Command></IfCondition>"
    )


def _neutral(parameter: str, operator: int, value: str, codes: str = "") -> str:
    selected = f'"{codes}"' if codes else ""
    return _command(
        "Neutral",
        '{"LogicGroups":[{"GroupBooleanType":0,"Statements":[{'
        f'"StatementBooleanType":0,"Subject":"urn:ddi:int.example:{parameter}:1",'
        f'"Operator":{operator},"Value":{{"Value":"{value}","ValueNotNeeded":false,'
        f'"SelectedCodes":[{selected}]}}}}]}}],"Synopsis":"x","Version":1}}',
    )


def _read(data: bytes) -> tuple[Routing, dict[str, list[str]]]:
    from ddi_l.spec.expression import format_expression

    context = _Context(read_ddi(data))
    (instrument,) = context.items_of_type("Instrument")
    routing = Routing(context, instrument)
    names = {
        context.describe(element).split()[-1].strip("()"): [
            format_expression(c) for c in routing._conditions[id(element)]
        ]
        for element in routing._order
        if id(element) in routing._conditions
    }
    return routing, names


def test_a_blaise_gate_reads_its_parameters_by_the_question_they_are_bound_to():
    from tests.helpers.instrument_documents import _id

    routing, conditions = _read(
        _flow(_command("Blaise", "Count &gt; 2"), _neutral(_id(2, 3), 5, "1"))
    )
    assert conditions == {"G2": ["PetCount > 2"], "G3": ["PetCount < 1"]}
    # The Then branch of G3 asks for more than 2 and less than 1 pets.
    assert [_local(e) for e in routing.unreachable()] == ["S4"]


def test_a_code_is_read_as_its_value():
    from tests.helpers.instrument_documents import _id

    code = (
        f'<Fragment><Code xmlns="ddi:logicalproduct:3_3">'
        f"<r:Agency>int.example</r:Agency><r:ID>{_id(5, 1)}</r:ID>"
        "<r:Version>1</r:Version><r:Value>3</r:Value></Code></Fragment>"
    )
    urn = f"urn:ddi:int.example:{_id(5, 1)}:1"
    routing, conditions = _read(
        _flow(_neutral(_id(2, 2), 11, "", urn), _neutral(_id(2, 3), 2, "3"), code)
    )
    assert conditions == {"G2": ["PetCount = 3"], "G3": ["PetCount != 3"]}
    assert [_local(e) for e in routing.unreachable()] == ["S4"]


def test_a_condition_it_cannot_read_is_a_fact_of_its_own():
    from tests.helpers.instrument_documents import _id

    routing, conditions = _read(
        _flow(_command("SAS", "count &gt; 2"), _command("Neutral", "{not json"))
    )
    assert all(c[0].startswith("answered(#") for c in conditions.values())
    assert routing.unreachable() == []
    # Two gates that read one name as a number and as text: the second is
    # read as a fact of its own.
    routing, conditions = _read(
        _flow(_neutral(_id(2, 2), 3, "2"), _neutral(_id(2, 3), 1, "many"))
    )
    assert conditions["G2"] == ["PetCount > 2"]
    assert conditions["G3"][0].startswith("answered(#")


def _local(element) -> str:
    return element.findtext(f"{{ddi:datacollection:3_3}}ConstructName/{{{_R}}}String")
