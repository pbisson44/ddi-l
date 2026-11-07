"""Write pets_conform.ddi33.xml: a Pet survey instrument for `ddi conform`.

Synthetic and neutral. Compared with pets_conform.spec.yaml it has, on
purpose:

* household: PetCount's question item is named HouseholdPets (its id
  sources differ);
* pets, gated by PetCount > 0 as the spec says, holding:
  - PetKind, whose code list lacks code 3, adds code 4 and labels code 2
    "Chats" in French;
  - PetName, gated by a Blaise condition equivalent to answered(PetKind),
    with a maximum length of 40 (the spec says 50);
  - PetAge, gated by PetCount > 1 (the spec gates it with nothing), its
    text in English only, range 0-30 with one decimal (0-40, none);
  - VisitDate, which the spec puts in the visits module;
  - PetColour, which the spec does not list;
* feedback: a module the spec does not list;
* a data lookup of OwnerName, OwnerAge (Text) and HasPets;
* an edit check age_range, marked by the user attribute kind=EditCheck,
  firing at PetAge > 25 (the spec says 30).

Run from the repository root to rewrite the fixture:

    python tests/fixtures/spec/build_pets_conform.py
"""

from __future__ import annotations

import json
from pathlib import Path

import ddi_l

HERE = Path(__file__).parent
AGENCY = "int.example"
DATE = "2026-03-01T10:00:00.0000000Z"
D = "ddi:datacollection:3_3"
L = "ddi:logicalproduct:3_3"


def _id(n: int) -> str:
    return f"55555555-5555-4555-8555-{n:012d}"


def _urn(n: int) -> str:
    return f"urn:ddi:{AGENCY}:{_id(n)}:1"


def _head(n: int) -> str:
    return (
        f"<r:URN>{_urn(n)}</r:URN><r:Agency>{AGENCY}</r:Agency>"
        f"<r:ID>{_id(n)}</r:ID><r:Version>1</r:Version>"
    )


def _ref(tag: str, n: int, kind: str, *, late: bool = False) -> str:
    attribute = ' lateBound="true"' if late else ""
    return (
        f"<{tag}{attribute}><r:Agency>{AGENCY}</r:Agency><r:ID>{_id(n)}</r:ID>"
        f"<r:Version>1</r:Version><r:TypeOfObject>{kind}</r:TypeOfObject></{tag}>"
    )


def _strings(tag: str, texts: dict[str, str], child: str = "r:String") -> str:
    inner = "".join(
        f'<{child} xml:lang="{lang}">{text}</{child}>' for lang, text in texts.items()
    )
    return f"<{tag}>{inner}</{tag}>"


def _item(local: str, namespace: str, n: int, body: str, extra: str = "") -> str:
    return (
        f'<{local} isUniversallyUnique="true" versionDate="{DATE}"{extra} '
        f'xmlns="{namespace}">{_head(n)}{body}</{local}>'
    )


def _parameter(tag: str, n: int, alias: str) -> str:
    return (
        f'<r:{tag} isUniversallyUnique="true">{_head(n)}<r:Alias>{alias}</r:Alias>'
        f"</r:{tag}>"
    )


def _binding(source: int, target: int, source_kind: str, target_kind: str) -> str:
    return (
        "<r:Binding>"
        + _ref("r:SourceParameterReference", source, source_kind, late=True)
        + _ref("r:TargetParameterReference", target, target_kind, late=True)
        + "</r:Binding>"
    )


def _name(name: str) -> str:
    return _strings("ConstructName", {"en-CA": name})


def _sequence(
    n: int,
    name: str,
    children: list[tuple[int, str]],
    *,
    then: bool = False,
    body: str = "",
) -> str:
    kind = "<TypeOfSequence>ConditionalChildContainer</TypeOfSequence>" if then else ""
    refs = "".join(_ref("ControlConstructReference", c, k) for c, k in children)
    return _item("Sequence", D, n, _name(name) + body + kind + refs)


def _command(language: str, content: str) -> str:
    escaped = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f"<r:Command><r:ProgramLanguage>{language}</r:ProgramLanguage>"
        f"<r:CommandContent>{escaped}</r:CommandContent></r:Command>"
    )


def _neutral(subject: int, operator: int, value: str, synopsis: str) -> str:
    return json.dumps(
        {
            "LogicGroups": [
                {
                    "GroupBooleanType": 0,
                    "Statements": [
                        {
                            "StatementBooleanType": 0,
                            "Subject": _urn(subject),
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
            "Synopsis": synopsis,
            "Version": 1,
        },
        separators=(",", ":"),
    )


def _gate(
    n: int, name: str, parameter: int, alias: str, command: str, then: int
) -> str:
    return _item(
        "IfThenElse",
        D,
        n,
        _name(name)
        + _parameter("InParameter", parameter, alias)
        + f"<IfCondition>{command}</IfCondition>"
        + _ref("ThenConstructReference", then, "Sequence"),
    )


def _question(
    construct: int,
    name: str,
    *,
    item_name: str | None = None,
    alias: str | None = None,
    texts: dict[str, str],
    domain: str,
) -> list[str]:
    """A QuestionConstruct and its QuestionItem (ids construct .. construct+4)."""
    out, item, item_out = construct + 1, construct + 3, construct + 4
    alias = alias or name
    text = "".join(
        f'<LiteralText><Text xml:lang="{lang}">{value}</Text></LiteralText>'
        for lang, value in texts.items()
    )
    return [
        _item(
            "QuestionConstruct",
            D,
            construct,
            _name(name)
            + _parameter("OutParameter", out, alias)
            + _binding(item_out, out, "OutParameter", "OutParameter")
            + _ref("r:QuestionReference", item, "QuestionItem"),
        ),
        _item(
            "QuestionItem",
            D,
            item,
            _strings("QuestionItemName", {"en-CA": item_name or name})
            + _parameter("OutParameter", item_out, alias)
            + f"<QuestionText>{text}</QuestionText>"
            + domain,
        ),
    ]


def _display(texts: dict[str, str]) -> str:
    inner = "".join(
        f'<LiteralText><Text xml:lang="{lang}">{text}</Text></LiteralText>'
        for lang, text in texts.items()
    )
    return f"<DisplayText>{inner}</DisplayText>"


def _category(n: int, labels: dict[str, str]) -> str:
    return _item(
        "Category", L, n, _strings("r:Label", labels, "r:Content"), ' isMissing="false"'
    )


def _code(n: int, category: int, value: str) -> str:
    return (
        f'<Code isUniversallyUnique="true">{_head(n)}'
        + _ref("r:CategoryReference", category, "Category")
        + f"<r:Value>{value}</r:Value></Code>"
    )


def _lookup() -> str:
    fields = [
        {"Name": "OwnerName", "Type": "Text", "IsAssigned": True, "Identifier": "1"},
        {"Name": "OwnerAge", "Type": "Text", "IsAssigned": True, "Identifier": "2"},
        {"Name": "HasPets", "Type": "Integer", "IsAssigned": True, "Identifier": "3"},
    ]
    content = json.dumps({"DataLookupFields": fields}, separators=(",", ":"))
    return _item(
        "ComputationItem",
        D,
        80,
        _name("Owner lookup")
        + f"<r:CommandCode>{_command('Blaise5DataLookup', content)}</r:CommandCode>",
    )


def _edit() -> str:
    head = _head(85).replace(
        "<r:Version>1</r:Version>",
        "<r:Version>1</r:Version><r:UserAttributePair><r:AttributeKey>kind"
        "</r:AttributeKey><r:AttributeValue>EditCheck</r:AttributeValue>"
        "</r:UserAttributePair>",
    )
    body = (
        _name("age_range")
        + _parameter("InParameter", 86, "PetAge")
        + "<r:CommandCode>"
        + _command("Neutral", _neutral(86, 3, "25", "PetAge Greater than 25"))
        + "</r:CommandCode>"
    )
    return (
        f'<ComputationItem isUniversallyUnique="true" versionDate="{DATE}" '
        f'xmlns="{D}">{head}{body}</ComputationItem>'
    )


def items() -> list[str]:
    numeric = (
        '<NumericDomain blankIsMissingValue="false" decimalPositions="{decimals}">'
        '<r:NumberRange><r:Low isInclusive="true">0</r:Low>'
        '<r:High isInclusive="true">{high}</r:High></r:NumberRange>'
        "<r:NumericTypeCode>{kind}</r:NumericTypeCode></NumericDomain>"
    )
    found = [
        _item(
            "Instrument",
            D,
            1,
            _strings("InstrumentName", {"en-CA": "Pet survey instrument"})
            + _ref("ControlConstructReference", 2, "Sequence"),
        ),
        _sequence(
            2,
            "Root",
            [
                (10, "Sequence"),
                (20, "IfThenElse"),
                (70, "Sequence"),
                (80, "ComputationItem"),
                (85, "ComputationItem"),
            ],
            body=_binding(13, 21, "OutParameter", "InParameter")
            + _binding(34, 41, "OutParameter", "InParameter")
            + _binding(13, 51, "OutParameter", "InParameter")
            + _binding(54, 86, "OutParameter", "InParameter"),
        ),
        _sequence(10, "household", [(11, "Sequence")]),
        _sequence(11, "Household page", [(12, "QuestionConstruct")]),
        *_question(
            12,
            "PetCount",
            item_name="HouseholdPets",
            texts={
                "en-CA": "How many pets live here?",
                "fr-CA": "Combien d\u2019animaux vivent ici\u00a0?",
            },
            domain=numeric.format(decimals=0, high=20, kind="Integer"),
        ),
        _gate(
            20,
            "Pets gate",
            21,
            "PetCount",
            _command("Neutral", _neutral(21, 3, "0", "PetCount Greater than 0")),
            22,
        ),
        _sequence(22, "Pets gate (then)", [(30, "Sequence")], then=True),
        _sequence(30, "pets", [(31, "Sequence")]),
        _sequence(
            31,
            "Pets page",
            [
                (32, "StatementItem"),
                (33, "QuestionConstruct"),
                (40, "IfThenElse"),
                (50, "IfThenElse"),
                (60, "QuestionConstruct"),
                (65, "QuestionConstruct"),
            ],
        ),
        _item(
            "StatementItem",
            D,
            32,
            _name("PetsIntro")
            + _display(
                {
                    "en-CA": "Now, about your pets.",
                    "fr-CA": "Parlons maintenant de vos animaux.",
                }
            ),
        ),
        *_question(
            33,
            "PetKind",
            texts={
                "en-CA": "What kind of pet?",
                "fr-CA": "Quel genre d\u2019animal\u00a0?",
            },
            domain='<CodeDomain blankIsMissingValue="false">'
            + _ref("r:CodeListReference", 90, "CodeList")
            + "</CodeDomain>",
        ),
        _gate(
            40,
            "Name gate",
            41,
            "PetKind",
            _command(
                "Blaise", "NOT ({{PetKind}} = EMPTY) AND NOT ({{PetKind}} = REFUSAL)"
            ),
            42,
        ),
        _sequence(42, "Name gate (then)", [(43, "QuestionConstruct")], then=True),
        *_question(
            43,
            "PetName",
            texts={"en-CA": "What is its name?", "fr-CA": "Quel est son nom\u00a0?"},
            domain='<TextDomain maxLength="40" blankIsMissingValue="false" />',
        ),
        _gate(
            50,
            "Age gate",
            51,
            "PetCount",
            _command("Neutral", _neutral(51, 3, "1", "PetCount Greater than 1")),
            52,
        ),
        _sequence(52, "Age gate (then)", [(53, "QuestionConstruct")], then=True),
        *_question(
            53,
            "PetAge",
            texts={"en-CA": "How old is it?"},
            domain=numeric.format(decimals=1, high=30, kind="Decimal"),
        ),
        *_question(
            60,
            "VisitDate",
            texts={
                "en-CA": "When was the last visit?",
                "fr-CA": "Quand a eu lieu la dernière visite\u00a0?",
            },
            domain='<DateTimeDomain blankIsMissingValue="false"><r:DateTypeCode>Date</r:DateTypeCode></DateTimeDomain>',
        ),
        *_question(
            65,
            "PetColour",
            texts={
                "en-CA": "What colour is it?",
                "fr-CA": "De quelle couleur est-il\u00a0?",
            },
            domain='<TextDomain maxLength="20" blankIsMissingValue="false" />',
        ),
        _sequence(70, "feedback", [(71, "StatementItem")]),
        _item(
            "StatementItem",
            D,
            71,
            _name("Thanks") + _display({"en-CA": "Thank you.", "fr-CA": "Merci."}),
        ),
        _lookup(),
        _edit(),
        _item(
            "CodeList",
            L,
            90,
            _strings("r:Label", {"en-CA": "Species"}, "r:Content")
            + _code(91, 95, "1")
            + _code(92, 96, "2")
            + _code(93, 97, "4"),
        ),
        _category(95, {"en-CA": "Dog", "fr-CA": "Chien"}),
        _category(96, {"en-CA": "Cat", "fr-CA": "Chats"}),
        _category(97, {"en-CA": "Fish", "fr-CA": "Poisson"}),
    ]
    return found


def main() -> None:
    fragments = "".join(
        f'<Fragment xmlns:r="ddi:reusable:3_3" xmlns="ddi:instance:3_3">{item}</Fragment>'
        for item in items()
    )
    text = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<ddi:FragmentInstance xmlns:r="ddi:reusable:3_3" xmlns:ddi="ddi:instance:3_3">'
        + _ref("ddi:TopLevelReference", 1, "Instrument")
        + fragments
        + "</ddi:FragmentInstance>"
    )
    fragment = ddi_l.read_ddi(text.encode("utf-8"))
    assert isinstance(fragment, ddi_l.DDIFragment)
    problems = fragment.validate()
    assert not problems, problems
    (HERE / "pets_conform.ddi33.xml").write_bytes(fragment.to_colectica_bytes())


if __name__ == "__main__":
    main()
