"""Random instruments and specs, for testing `ddi_l.spec.conform` against an oracle.

`instrument_documents` draws a `FragmentInstance` whose instrument leads to
a random graph of modules and pages (ordinary sequences), branch bodies,
gates, questions and statements, with constructs shared so that one is
reached by several paths, and a spec over the same names.

`chained_gates` builds an instrument that reaches one question by
``2 ** count`` paths.
"""

from __future__ import annotations

import json
from typing import Any

from hypothesis import strategies as st

AGENCY = "int.example"
_DC = "ddi:datacollection:3_3"
KINDS = ("Module", "Body", "IfThenElse", "QuestionConstruct", "StatementItem")


def _local(kind: str) -> str:
    """The element name of a kind: modules and branch bodies are sequences."""
    return "Sequence" if kind in ("Module", "Body") else kind


def _id(kind: int, index: int) -> str:
    return f"00000000-0000-4000-{8000 + kind:04d}-{index:012d}"


def _identity(identifier: str) -> str:
    return (
        f"<r:URN>urn:ddi:{AGENCY}:{identifier}:1</r:URN>"
        f"<r:Agency>{AGENCY}</r:Agency><r:ID>{identifier}</r:ID>"
        "<r:Version>1</r:Version>"
    )


def _reference(tag: str, identifier: str, type_of_object: str) -> str:
    return (
        f"<{tag}><r:Agency>{AGENCY}</r:Agency><r:ID>{identifier}</r:ID>"
        f"<r:Version>1</r:Version><r:TypeOfObject>{type_of_object}</r:TypeOfObject>"
        f"</{tag}>"
    )


def _name(name: str) -> str:
    return f'<ConstructName><r:String xml:lang="en">{name}</r:String></ConstructName>'


def _binding(source: str, target: str) -> str:
    return (
        "<r:Binding>"
        + _reference("r:SourceParameterReference", source, "OutParameter")
        + _reference("r:TargetParameterReference", target, "InParameter")
        + "</r:Binding>"
    )


def _condition(condition: tuple[str, int, str] | None, parameter: str) -> str:
    """An ``IfCondition``: Neutral, code no reader knows, or none at all."""
    if condition is None:
        return ""
    language, operator, value = condition
    if language != "Neutral":
        content = f"x {value}"
    else:
        content = json.dumps(
            {
                "LogicGroups": [
                    {
                        "GroupBooleanType": 0,
                        "Statements": [
                            {
                                "StatementBooleanType": 0,
                                "Subject": f"urn:ddi:{AGENCY}:{parameter}:1",
                                "Operator": operator,
                                "Value": {
                                    "Value": value,
                                    "ValueNotNeeded": False,
                                    "SelectedCodes": [],
                                },
                            }
                        ],
                    }
                ],
                "Synopsis": "x",
                "Version": 1,
            }
        )
    return (
        f"<IfCondition><r:Command><r:ProgramLanguage>{language}</r:ProgramLanguage>"
        f"<r:CommandContent>{content}</r:CommandContent></r:Command></IfCondition>"
    )


def _document(constructs: list[str], bindings: str = "") -> bytes:
    """A FragmentInstance whose instrument leads to construct 0."""
    instrument = (
        f'<Fragment><Instrument xmlns="{_DC}">{_identity(_id(3, 0))}'
        + _reference("ControlConstructReference", _id(0, 0), "Sequence")
        + "</Instrument></Fragment>"
    )
    top = _reference("TopLevelReference", _id(3, 0), "Instrument")
    if bindings:
        # The bindings go on a construct of their own, which nothing reaches.
        constructs = [
            *constructs,
            f'<Fragment><Sequence xmlns="{_DC}">{_identity(_id(4, 0))}'
            f"{bindings}</Sequence></Fragment>",
        ]
    return (
        '<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3">'
        + top
        + instrument
        + "".join(constructs)
        + "</FragmentInstance>"
    ).encode()


_READABLE = st.tuples(st.just("Neutral"), st.sampled_from([1, 3]), st.just("1"))
_CONDITIONS = st.one_of(
    st.tuples(st.just("Neutral"), st.sampled_from([1, 3]), st.just("1")),
    st.tuples(st.just("Neutral"), st.sampled_from([1, 3]), st.just("1")),
    st.tuples(st.just("SAS"), st.just(0), st.just("1")),
    st.none(),
)


@st.composite
def instrument_documents(
    draw: st.DrawFn,
    max_nodes: int = 14,
    cycles: bool = False,
    kinds_drawn: tuple[str, ...] = KINDS,
    bound: bool = False,
    readable: bool = False,
) -> tuple[bytes, dict[str, Any]]:
    """A FragmentInstance whose instrument leads to a random flow, and a spec.

    ``kinds_drawn`` are the kinds of construct drawn (a kind listed twice is
    drawn twice as often); with ``bound``, every gate reads a question; with
    ``readable``, every condition is ``Neutral``.
    """
    conditions = _READABLE if readable else _CONDITIONS
    count = draw(st.integers(min_value=2, max_value=max_nodes))
    kinds = ["Module"] + [draw(st.sampled_from(kinds_drawn)) for _ in range(1, count)]
    questions = [i for i, kind in enumerate(kinds) if kind == "QuestionConstruct"]

    def child() -> int:
        later = st.integers(min_value=1, max_value=count - 1)
        return draw(st.one_of(later, st.just(0)) if cycles else later)

    constructs = []
    bindings = []
    for index, kind in enumerate(kinds):
        body = _identity(_id(0, index))
        if kind == "QuestionConstruct":
            body += _name(f"Q{index}") + (
                f"<r:OutParameter>{_identity(_id(1, index))}"
                f"<r:Alias>Q{index}</r:Alias></r:OutParameter>"
            )
        elif kind == "StatementItem":
            body += _name(f"S{index}")
        elif kind in ("Module", "Body"):
            body += _name(f"M{index}")
            if kind == "Body":
                body += "<TypeOfSequence>ConditionalChildContainer</TypeOfSequence>"
            for _ in range(draw(st.integers(min_value=0, max_value=3))):
                target = child()
                body += _reference(
                    "ControlConstructReference", _id(0, target), _local(kinds[target])
                )
        else:
            parameter = _id(2, index)
            body += _name(f"G{index}") + (
                f"<r:InParameter>{_identity(parameter)}"
                f"<r:Alias>G{index}</r:Alias></r:InParameter>"
            )
            if (bound or draw(st.booleans())) and questions:
                question = draw(st.sampled_from(questions))
                bindings.append(_binding(_id(1, question), parameter))
            body += _condition(draw(conditions), parameter)
            branches = [("Then", child())]
            for _ in range(draw(st.integers(min_value=0, max_value=2))):
                branches.append(("ElseIf", child()))
            if draw(st.booleans()):
                branches.append(("Else", child()))
            for branch, target in branches:
                tag = "Else" if branch == "Else" else "Then"
                reference = _reference(
                    f"{tag}ConstructReference", _id(0, target), _local(kinds[target])
                )
                if branch == "ElseIf":
                    condition = _condition(draw(conditions), parameter)
                    reference = f"<ElseIf>{condition}{reference}</ElseIf>"
                body += reference
        local = _local(kind)
        constructs.append(
            f'<Fragment><{local} xmlns="{_DC}">{body}</{local}></Fragment>'
        )
    document = _document(constructs, "".join(bindings))
    return document, draw(_specs(kinds, questions))


@st.composite
def _specs(draw: st.DrawFn, kinds: list[str], questions: list[int]) -> dict[str, Any]:
    """A spec over the flow's names: modules, their questions, statements, gates."""
    modules = [i for i, kind in enumerate(kinds) if kind == "Module"]
    bodies = [i for i, kind in enumerate(kinds) if kind == "Body"]
    statements = [i for i, kind in enumerate(kinds) if kind == "StatementItem"]
    # Most questions are listed; one listed question is nowhere in the flow.
    listed = [f"Q{i}" for i in questions if draw(st.integers(0, 4))]
    if draw(st.booleans()):
        listed.append(f"Q{len(kinds)}")

    def gate() -> st.SearchStrategy[str]:
        comparison = st.builds(
            "{} {} {}".format,
            st.sampled_from(listed),
            st.sampled_from(["=", ">"]),
            st.just("1"),
        )
        return st.one_of(
            comparison,
            st.builds("not ({})".format, comparison),
            st.builds("{} and {}".format, comparison, comparison),
        )

    chosen = draw(st.lists(st.sampled_from(modules), unique=True, min_size=1))
    if draw(st.booleans()) and bodies:
        # A branch body is no module: the spec module is missing.
        chosen.append(draw(st.sampled_from(bodies)))
    spread: list[list[str]] = [[] for _ in chosen]
    for name in listed:
        spread[draw(st.integers(min_value=0, max_value=len(chosen) - 1))].append(name)
    held: list[list[str]] = [[] for _ in chosen]
    for statement in statements:
        if draw(st.integers(0, 3)):
            at = draw(st.integers(min_value=0, max_value=len(chosen) - 1))
            held[at].append(f"S{statement}")
    spec_modules = []
    for module, names_here, statements_here in zip(chosen, spread, held, strict=True):
        entry: dict[str, Any] = {"id": f"M{module}"}
        if draw(st.booleans()) and listed:
            entry["gate"] = draw(gate())
            entry["gate_scope"] = draw(st.sampled_from(["module", "page"]))
        entry["questions"] = [
            {"id": name, **({"gate": draw(gate())} if draw(st.booleans()) else {})}
            for name in names_here
        ]
        if statements_here:
            entry["statements"] = statements_here
        spec_modules.append(entry)
    return {
        "spec": "random",
        "version": "1",
        "languages": ["en"],
        "modules": spec_modules,
    }


def chained_gates(count: int) -> tuple[bytes, dict[str, Any]]:
    """An instrument reaching one question by ``2 ** count`` paths, and its spec.

    In module ``M0``, each of ``count`` gates leads by its Then and by its
    Else to a branch body, and both bodies lead on to the next gate. Below
    the last is the question ``Q1``, which the spec gates with nothing.
    """
    bindings = []
    constructs = [
        f'<Fragment><QuestionConstruct xmlns="{_DC}">{_identity(_id(0, 1))}'
        + _name("Q1")
        + f"<r:OutParameter>{_identity(_id(1, 1))}<r:Alias>Q1</r:Alias>"
        "</r:OutParameter></QuestionConstruct></Fragment>",
        f'<Fragment><QuestionConstruct xmlns="{_DC}">{_identity(_id(0, 2))}'
        + _name("Q2")
        + f"<r:OutParameter>{_identity(_id(1, 2))}<r:Alias>Q2</r:Alias>"
        "</r:OutParameter></QuestionConstruct></Fragment>",
    ]

    def gate(index: int) -> str:
        return _id(0, 100 + index)

    constructs.append(
        f'<Fragment><Sequence xmlns="{_DC}">{_identity(_id(0, 0))}{_name("M0")}'
        + _reference("ControlConstructReference", _id(0, 2), "QuestionConstruct")
        + _reference("ControlConstructReference", gate(0), "IfThenElse")
        + "</Sequence></Fragment>"
    )
    for index in range(count):
        parameter = _id(2, index)
        bindings.append(_binding(_id(1, 2), parameter))
        bodies = (_id(0, 1000 + index), _id(0, 2000 + index))
        constructs.append(
            f'<Fragment><IfThenElse xmlns="{_DC}">{_identity(gate(index))}'
            + _name(f"G{index}")
            + f"<r:InParameter>{_identity(parameter)}<r:Alias>G{index}</r:Alias>"
            "</r:InParameter>"
            + _condition(("Neutral", 3, str(index)), parameter)
            + _reference("ThenConstructReference", bodies[0], "Sequence")
            + _reference("ElseConstructReference", bodies[1], "Sequence")
            + "</IfThenElse></Fragment>"
        )
        following = (
            _reference("ControlConstructReference", gate(index + 1), "IfThenElse")
            if index + 1 < count
            else _reference("ControlConstructReference", _id(0, 1), "QuestionConstruct")
        )
        for body in bodies:
            constructs.append(
                f'<Fragment><Sequence xmlns="{_DC}">{_identity(body)}'
                "<TypeOfSequence>ConditionalChildContainer</TypeOfSequence>"
                f"{following}</Sequence></Fragment>"
            )
    spec = {
        "spec": "chained",
        "version": "1",
        "languages": ["en"],
        "modules": [{"id": "M0", "questions": [{"id": "Q1"}, {"id": "Q2"}]}],
    }
    return _document(constructs, "".join(bindings)), spec
