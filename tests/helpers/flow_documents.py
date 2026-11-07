"""Random Colectica-shaped flows, for testing flow walks against their oracles.

`flow_documents` draws a `FragmentInstance` whose instrument leads to a
random graph of sequences, conditions, questions, computations and
statements. Constructs share children, so one is reached by several paths;
containers bind their children's inputs to outputs anywhere in the flow, or
to an input of their own that their own container binds in turn.
"""

from __future__ import annotations

import json

from hypothesis import strategies as st

AGENCY = "int.example"
CONTAINERS = ("Sequence", "IfThenElse")
LEAVES = ("QuestionConstruct", "ComputationItem", "StatementItem")
_DC = "ddi:datacollection:3_3"


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


def _parameter(tag: str, identifier: str, alias: str) -> str:
    return f"<r:{tag}>{_identity(identifier)}<r:Alias>{alias}</r:Alias></r:{tag}>"


def _condition(subject: str) -> str:
    neutral = {
        "LogicGroups": [
            {
                "GroupBooleanType": 0,
                "Statements": [
                    {
                        "StatementBooleanType": 0,
                        "Subject": f"urn:ddi:{AGENCY}:{subject}:1",
                        "Operator": 1,
                        "Value": {
                            "Value": "1",
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
    return (
        "<IfCondition><r:Command><r:ProgramLanguage>Neutral</r:ProgramLanguage>"
        f"<r:CommandContent>{json.dumps(neutral)}</r:CommandContent>"
        "</r:Command></IfCondition>"
    )


@st.composite
def flow_documents(draw: st.DrawFn, max_nodes: int = 12, cycles: bool = False) -> bytes:
    """A FragmentInstance whose instrument leads to a random flow."""
    count = draw(st.integers(min_value=2, max_value=max_nodes))
    kinds = ["Sequence"] + [
        draw(st.sampled_from(CONTAINERS + LEAVES)) for _ in range(1, count)
    ]
    has_input = [
        kind in ("IfThenElse", "ComputationItem", "StatementItem")
        or draw(st.booleans())
        for kind in kinds
    ]
    has_output = [kind in ("QuestionConstruct", "ComputationItem") for kind in kinds]
    outputs = [index for index in range(count) if has_output[index]]

    def child_choices(index: int) -> st.SearchStrategy[int]:
        later = st.integers(min_value=min(index + 1, count - 1), max_value=count - 1)
        if cycles:
            return st.one_of(later, st.integers(min_value=0, max_value=count - 1))
        return later

    children: list[list[tuple[str, int]]] = []
    for index, kind in enumerate(kinds):
        if kind == "Sequence" and index + 1 < count:
            picked = draw(st.lists(child_choices(index), max_size=3))
            children.append([("ControlConstructReference", c) for c in picked])
        elif kind == "IfThenElse" and index + 1 < count:
            branches = [("ThenConstructReference", draw(child_choices(index)))]
            if draw(st.booleans()):
                branches.append(("ElseIf", draw(child_choices(index))))
            if draw(st.booleans()):
                branches.append(("ElseConstructReference", draw(child_choices(index))))
            children.append(branches)
        else:
            children.append([])

    fragments = []
    for index, kind in enumerate(kinds):
        parts = [_identity(_id(0, index))]
        parts.append(
            f'<ConstructName><r:String xml:lang="en">N{index}</r:String>'
            "</ConstructName>"
        )
        if has_input[index]:
            parts.append(_parameter("InParameter", _id(2, index), f"In{index}"))
        if has_output[index]:
            parts.append(_parameter("OutParameter", _id(1, index), f"Out{index}"))
        # A container binds the input of a child, and of its ElseIf branches.
        for _, child in children[index]:
            if has_input[child] and draw(st.booleans()):
                sources = [("OutParameter", _id(1, k)) for k in outputs]
                if has_input[index]:
                    sources.append(("InParameter", _id(2, index)))
                if sources:
                    kind_of, source = draw(st.sampled_from(sources))
                    parts.append(
                        "<r:Binding>"
                        + _reference("r:SourceParameterReference", source, kind_of)
                        + _reference(
                            "r:TargetParameterReference",
                            _id(2, child),
                            "InParameter",
                        )
                        + "</r:Binding>"
                    )
        if kind == "IfThenElse":
            parts.append(_condition(_id(2, index)))
        for tag, child in children[index]:
            target = _reference(
                "ThenConstructReference" if tag == "ElseIf" else tag,
                _id(0, child),
                kinds[child],
            )
            if tag == "ElseIf":
                parts.append(f"<ElseIf>{_condition(_id(2, index))}{target}</ElseIf>")
            else:
                parts.append(target)
        body = "".join(parts)
        fragments.append(f'<Fragment><{kind} xmlns="{_DC}">{body}</{kind}></Fragment>')

    instrument = (
        f'<Fragment><Instrument xmlns="{_DC}">{_identity(_id(3, 0))}'
        + _reference("ControlConstructReference", _id(0, 0), "Sequence")
        + "</Instrument></Fragment>"
    )
    top = _reference("TopLevelReference", _id(3, 0), "Instrument")
    return (
        '<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3">'
        + top
        + instrument
        + "".join(fragments)
        + "</FragmentInstance>"
    ).encode()


def chained_diamonds(count: int) -> bytes:
    """An instrument reaching one page by ``2 ** count`` paths.

    Each of ``count`` gates leads by its Then and by its Else to a page of
    its own, and both pages lead on to the next gate. Below the last, a
    computation reads a question the instrument asks only after them all.
    """
    fragments: list[str] = []
    ids = {
        "root": _id(0, 0),
        "bottom": _id(0, 1),
        "reader": _id(0, 2),
        "asked": _id(0, 3),
    }

    def construct(kind: str, identifier: str, name: str, body: str) -> None:
        fragments.append(
            f'<Fragment><{kind} xmlns="{_DC}">{_identity(identifier)}'
            f'<ConstructName><r:String xml:lang="en">{name}</r:String>'
            f"</ConstructName>{body}</{kind}></Fragment>"
        )

    def gate(index: int) -> str:
        return _id(0, 100 + index) if index < count else ids["bottom"]

    construct(
        "Sequence",
        ids["root"],
        "Root",
        _reference("ControlConstructReference", gate(0), "IfThenElse")
        + _reference("ControlConstructReference", ids["asked"], "QuestionConstruct"),
    )
    for index in range(count):
        then_page, else_page = _id(0, 1000 + index), _id(0, 2000 + index)
        construct(
            "IfThenElse",
            gate(index),
            f"Gate {index}",
            _reference("ThenConstructReference", then_page, "Sequence")
            + _reference("ElseConstructReference", else_page, "Sequence"),
        )
        following = "Sequence" if index + 1 == count else "IfThenElse"
        for page, name in ((then_page, f"Then {index}"), (else_page, f"Else {index}")):
            construct(
                "Sequence",
                page,
                name,
                _reference("ControlConstructReference", gate(index + 1), following),
            )
    construct(
        "Sequence",
        ids["bottom"],
        "Bottom",
        "<r:Binding>"
        + _reference("r:SourceParameterReference", _id(1, 3), "OutParameter")
        + _reference("r:TargetParameterReference", _id(2, 2), "InParameter")
        + "</r:Binding>"
        + _reference("ControlConstructReference", ids["reader"], "ComputationItem"),
    )
    construct(
        "ComputationItem",
        ids["reader"],
        "Reader",
        _parameter("InParameter", _id(2, 2), "Asked"),
    )
    construct(
        "QuestionConstruct",
        ids["asked"],
        "Asked",
        _parameter("OutParameter", _id(1, 3), "Asked"),
    )
    instrument = (
        f'<Fragment><Instrument xmlns="{_DC}">{_identity(_id(3, 0))}'
        + _reference("ControlConstructReference", ids["root"], "Sequence")
        + "</Instrument></Fragment>"
    )
    top = _reference("TopLevelReference", _id(3, 0), "Instrument")
    return (
        '<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3">'
        + top
        + instrument
        + "".join(fragments)
        + "</FragmentInstance>"
    ).encode()
