"""Colectica condition JSON: parse, write back unchanged, edit, render, explain.

``tests/fixtures/colectica/pets_conditions.ddi33.xml`` is a synthetic Pet
survey: a code list whose values start at 2 (so a code's position and its
value differ), an IfThenElse with a ``Neutral`` condition whose stored
synopsis is stale, an unused input, a ``Blaise5DataLookup`` and a native
``Blaise`` command.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import ddi_l
from ddi_l import cli
from ddi_l._etree import fromstring, tostring
from ddi_l.colectica_logic import (
    Condition,
    ConditionFormatError,
    DataLookup,
    GroupBool,
    LogicGroup,
    NativeCondition,
    Operator,
    Statement,
    StmtBool,
    explain_condition,
    parse_command,
    parse_condition,
    render_synopsis,
    serialize_condition,
    write_condition,
)
from ddi_l.models.base import qn

FIXTURE = Path(__file__).parent / "fixtures" / "colectica" / "pets_conditions.ddi33.xml"
SAMPLE = Path(ddi_l.__file__).parent / "examples" / "Quality_of_Life.xml"
R = "ddi:reusable:3_3"


def _id(n: int) -> str:
    return f"22222222-2222-4222-8222-{n:012d}"


ITE, LOOKUP, NATIVE, SEQUENCE = _id(30), _id(50), _id(60), _id(70)
IN_KIND, IN_COUNT, CODE_CAT = _id(31), _id(32), _id(6)


def _urn(n: int) -> str:
    return f"urn:ddi:int.example:{_id(n)}:1"


@pytest.fixture
def fragment() -> ddi_l.DDIFragment:
    return ddi_l.open_fragment(FIXTURE)


def _item(fragment: ddi_l.DDIFragment, identifier: str):
    for payload in fragment.iter_fragment_payloads():
        if payload.findtext(qn(R, "ID")) == identifier:
            return payload
    raise AssertionError(identifier)


def _content(item) -> str:
    command = item.find(f".//{{{R}}}Command")
    return command.findtext(qn(R, "CommandContent"))


# ---- The enums ----------------------------------------------------------


def test_the_enums_list_colectica_s_operator_and_join_codes() -> None:
    # Joins: None = 0, And = 1, Or = 2.
    for joins in (GroupBool, StmtBool):
        assert {member.name: int(member) for member in joins} == {
            "FIRST": 0,
            "AND": 1,
            "OR": 2,
        }
        assert joins.NONE is joins.FIRST
    # Operators, 0 to 17.
    assert {member.name: int(member) for member in Operator} == {
        "NONE": 0,
        "EQUAL_TO": 1,
        "NOT_EQUAL": 2,
        "GREATER_THAN": 3,
        "GREATER_THAN_OR_EQUAL": 4,
        "LESS_THAN": 5,
        "LESS_THAN_OR_EQUAL": 6,
        "EMPTY": 7,
        "NOT_EMPTY": 8,
        "CONTAINS": 9,
        "DOES_NOT_CONTAIN": 10,
        "CONTAINS_ANY": 11,
        "CONTAINS_ALL": 12,
        "CONTAINS_NONE": 13,
        "REFUSED": 14,
        "NOT_REFUSED": 15,
        "DONT_KNOW": 16,
        "NOT_DONT_KNOW": 17,
    }
    assert Operator.EQUAL is Operator.EQUAL_TO
    assert Operator(1).name == "EQUAL_TO"
    assert Operator.EMPTY.known
    assert Operator.NOT_DONT_KNOW.known


def test_every_operator_renders() -> None:
    no_value = (
        Operator.EMPTY,
        Operator.NOT_EMPTY,
        Operator.REFUSED,
        Operator.NOT_REFUSED,
        Operator.DONT_KNOW,
        Operator.NOT_DONT_KNOW,
    )
    texts = {}
    for operator in Operator:
        statement = Statement(
            StmtBool.FIRST,
            "urn:ddi:x:abcdef0123:1",
            operator,
            value=None if operator in no_value else "3",
            value_not_needed=operator in no_value,
        )
        condition = Condition(logic_groups=[LogicGroup(GroupBool.FIRST, [statement])])
        texts[operator] = render_synopsis(condition, fromstring("<root/>"))
    assert texts[Operator.NONE] == "abcdef01 <operator 0> 3"
    assert all(
        "<operator" not in text for op, text in texts.items() if op is not Operator.NONE
    )
    assert texts[Operator.LESS_THAN_OR_EQUAL] == "abcdef01 <= 3"
    assert texts[Operator.NOT_EMPTY] == "abcdef01 is not empty"
    assert texts[Operator.CONTAINS_NONE] == "abcdef01 contains none of 3"


def test_an_unlisted_code_is_kept() -> None:
    unknown = Operator(99)
    assert unknown.name == "UNKNOWN_99"
    assert int(unknown) == 99
    assert not unknown.known
    assert json.dumps({"Operator": unknown}) == '{"Operator": 99}'
    assert GroupBool(5).name == "UNKNOWN_5"
    with pytest.raises(ValueError):
        Operator("7")  # type: ignore[arg-type]


# ---- Parsing ---------------------------------------------------------------


def test_a_neutral_condition_parses(fragment: ddi_l.DDIFragment) -> None:
    condition = parse_condition(_item(fragment, ITE))
    assert isinstance(condition, Condition)
    assert condition.language == "Neutral"
    assert condition.version == 1
    assert not condition.is_empty
    first, second = condition.logic_groups
    assert first.group_bool is GroupBool.FIRST
    assert second.group_bool is GroupBool.AND
    cat = first.statements[0]
    assert cat.subject == _urn(31)
    assert cat.operator is Operator.CONTAINS_ALL
    assert cat.selected_codes == [_urn(6)]
    assert cat.value is None and cat.value_not_needed is False
    greater, refused = second.statements
    assert (greater.operator, greater.value) == (Operator.GREATER_THAN, "2")
    assert refused.stmt_bool is StmtBool.OR
    assert refused.operator is Operator.REFUSED and refused.value_not_needed
    assert len(list(condition.statements)) == 3


def test_every_way_of_pointing_at_the_condition(fragment: ddi_l.DDIFragment) -> None:
    item = _item(fragment, ITE)
    if_condition = item.find("{ddi:datacollection:3_3}IfCondition")
    command = if_condition.find(qn(R, "Command"))
    typed = fragment.get(ITE)
    assert typed is not None
    expected = parse_condition(item)
    for source in (if_condition, command, typed):
        assert parse_condition(source) == expected


def test_an_else_if_branch_has_its_own_condition() -> None:
    else_if = fromstring(
        f'<d:ElseIf xmlns:d="ddi:datacollection:3_3" xmlns:r="{R}">'
        "<!-- a comment is skipped -->"
        "<d:IfCondition><r:Command><r:ProgramLanguage>Blaise</r:ProgramLanguage>"
        "<r:CommandContent>PetCount = 0</r:CommandContent></r:Command>"
        "</d:IfCondition></d:ElseIf>"
    )
    assert parse_condition(else_if) == NativeCondition("PetCount = 0", "Blaise")


def test_an_item_without_a_command_has_no_condition(
    fragment: ddi_l.DDIFragment,
) -> None:
    assert parse_condition(_item(fragment, SEQUENCE)) is None


def test_a_data_lookup_parses(fragment: ddi_l.DDIFragment) -> None:
    lookup = parse_condition(_item(fragment, LOOKUP))
    assert isinstance(lookup, DataLookup)
    assert [(f.name, f.type, f.is_assigned, f.identifier) for f in lookup.fields] == [
        ("OwnerName", "Text", True, "1"),
        ("Région", "Text", False, "2"),
    ]


def test_native_code_is_kept_as_text(fragment: ddi_l.DDIFragment) -> None:
    native = parse_condition(_item(fragment, NATIVE))
    assert native == NativeCondition(text="PetCount > 5", language="Blaise")
    assert serialize_condition(native) == "PetCount > 5"


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("{not json", "not valid JSON"),
        ("[]", "expected a JSON dict"),
        ('{"LogicGroups": {}}', "LogicGroups: expected a JSON list"),
        ('{"LogicGroups": [{"Statements": [1]}]}', "Statement: expected"),
    ],
)
def test_malformed_neutral_json_is_reported(text: str, message: str) -> None:
    with pytest.raises(ConditionFormatError, match=message):
        parse_command("Neutral", text)


def test_malformed_lookup_json_is_reported() -> None:
    with pytest.raises(ConditionFormatError, match="DataLookupFields"):
        parse_command("Blaise5DataLookup", '{"DataLookupFields": 3}')


# ---- Writing back ------------------------------------------------------------


@pytest.mark.parametrize("path", [FIXTURE, SAMPLE], ids=["synthetic", "sample"])
def test_unchanged_conditions_write_back_byte_for_byte(path: Path) -> None:
    root = ddi_l.open_fragment(path).root
    checked = 0
    for command in root.iter(qn(R, "Command")):
        language = command.findtext(qn(R, "ProgramLanguage"))
        text = command.findtext(qn(R, "CommandContent"))
        assert serialize_condition(parse_command(language, text)) == text
        checked += 1
    assert checked >= 3


def test_an_edit_is_written_compactly_in_the_original_key_order(
    fragment: ddi_l.DDIFragment,
) -> None:
    item = _item(fragment, ITE)
    original = _content(item)
    condition = parse_condition(item)
    assert isinstance(condition, Condition)
    condition.logic_groups[1].statements[0].value = "3"
    written = serialize_condition(condition)
    assert written != original
    assert written == original.replace('"Value":"2"', '"Value":"3"')


def test_unmodelled_keys_survive_an_edit() -> None:
    text = (
        '{"Version":1,"LogicGroups":[{"Statements":[{"Subject":"urn:ddi:a:b:1",'
        '"Note":"keep","Operator":7,"StatementBooleanType":0,"Value":'
        '{"ValueNotNeeded":true,"SelectedCodes":[],"Hint":1}}],'
        '"GroupBooleanType":0}],"Synopsis":"b Empty","Extra":[1]}'
    )
    condition = parse_command("Neutral", text)
    assert isinstance(condition, Condition)
    condition.synopsis = "b is empty"
    assert serialize_condition(condition) == text.replace("b Empty", "b is empty")


def test_an_edit_keeps_escaping_the_way_the_source_did() -> None:
    escaped = '{"LogicGroups":[],"Synopsis":"R\\u00e9gion","Version":1}'
    condition = parse_command("Neutral", escaped)
    assert isinstance(condition, Condition)
    assert condition.synopsis == "Région"
    condition.version = 2
    assert serialize_condition(condition) == escaped.replace(":1}", ":2}")

    raw = '{"LogicGroups":[],"Synopsis":"Région","Version":1}'
    condition = parse_command("Neutral", raw)
    assert isinstance(condition, Condition)
    condition.version = 2
    assert serialize_condition(condition) == raw.replace(":1}", ":2}")


def test_an_unlisted_operator_writes_back_unchanged() -> None:
    text = (
        '{"LogicGroups":[{"GroupBooleanType":0,"Statements":[{"StatementBooleanType"'
        ':0,"Subject":"urn:ddi:a:b:1","Operator":99,"Value":{"ValueNotNeeded":true,'
        '"SelectedCodes":[]}}]}],"Synopsis":"","Version":1}'
    )
    condition = parse_command("Neutral", text)
    assert isinstance(condition, Condition)
    statement = condition.logic_groups[0].statements[0]
    assert statement.operator.name == "UNKNOWN_99"
    assert serialize_condition(condition) == text
    condition.synopsis = "changed"
    assert '"Operator":99' in serialize_condition(condition)


def test_a_condition_built_in_code_is_written_as_colectica_does() -> None:
    condition = Condition(
        logic_groups=[
            LogicGroup(
                GroupBool.FIRST,
                [
                    Statement(
                        StmtBool.FIRST,
                        "urn:ddi:a:b:1",
                        Operator.EQUAL_TO,
                        selected_codes=["urn:ddi:a:c:1"],
                    )
                ],
            )
        ],
        synopsis="b = 1",
    )
    assert serialize_condition(condition) == (
        '{"LogicGroups":[{"GroupBooleanType":0,"Statements":[{"StatementBooleanType":0,'
        '"Subject":"urn:ddi:a:b:1","Operator":1,"Value":{"ValueNotNeeded":false,'
        '"SelectedCodes":["urn:ddi:a:c:1"]}}]}],"Synopsis":"b = 1","Version":1}'
    )
    lookup = DataLookup()
    assert serialize_condition(lookup) == '{"DataLookupFields":[]}'


def test_write_condition_changes_only_the_command(
    fragment: ddi_l.DDIFragment, tmp_path: Path
) -> None:
    before = FIXTURE.read_bytes()
    item = _item(fragment, ITE)
    condition = parse_condition(item)
    assert isinstance(condition, Condition)
    write_condition(item, condition)
    assert fragment.to_colectica_bytes() == before

    condition.logic_groups[1].statements[0].value = "4"
    command = write_condition(item, condition)
    assert command.tag == qn(R, "Command")
    after = fragment.to_colectica_bytes()
    assert after == before.replace(b'"Value":"2"', b'"Value":"4"')

    lookup = parse_condition(_item(fragment, LOOKUP))
    assert isinstance(lookup, DataLookup)
    lookup.fields[1].is_assigned = True
    write_condition(_item(fragment, LOOKUP), lookup)
    assert '"IsAssigned":true,"Identifier":"2"' in _content(_item(fragment, LOOKUP))


def test_write_condition_needs_a_command(fragment: ddi_l.DDIFragment) -> None:
    with pytest.raises(ValueError, match="no r:Command"):
        write_condition(_item(fragment, SEQUENCE), NativeCondition("x", "Blaise"))
    bare = fromstring(
        f'<r:Command xmlns:r="{R}"><r:ProgramLanguage>Blaise</r:ProgramLanguage>'
        "</r:Command>"
    )
    with pytest.raises(ValueError, match="no ProgramLanguage or CommandContent"):
        write_condition(bare, NativeCondition("x", "Blaise"))


# ---- Rendering -------------------------------------------------------------


def test_the_rendered_synopsis_names_questions_and_code_values(
    fragment: ddi_l.DDIFragment,
) -> None:
    condition = parse_condition(_item(fragment, ITE))
    assert isinstance(condition, Condition)
    # The stored synopsis says "PetName ... 2 Cat": the wrong variable, and
    # the code's position. The logic selects the code whose value is 3.
    assert condition.synopsis == (
        "(PetName Contains All 2 Cat) And ((PetCount Greater than 2) Or "
        "(PetCount Refused))"
    )
    assert render_synopsis(condition, fragment) == (
        '(PetKind contains all of 3 "Cat") and (PetCount > 2 or PetCount is refused)'
    )
    assert render_synopsis(condition, fragment.root) == render_synopsis(
        condition, fragment
    )


def test_rendering_edge_cases(fragment: ddi_l.DDIFragment) -> None:
    assert render_synopsis(Condition(), fragment) == "(no condition)"
    unknown = Condition(
        logic_groups=[
            LogicGroup(
                GroupBool.FIRST,
                [
                    Statement(StmtBool.FIRST, "urn:ddi:x:abcdef0123:1", Operator(99)),
                    Statement(
                        StmtBool.FIRST,
                        "not-a-urn",
                        Operator.EQUAL_TO,
                        selected_codes=["urn:ddi:x:gone:1"],
                    ),
                ],
            ),
            LogicGroup(GroupBool(4), []),
        ]
    )
    assert render_synopsis(unknown, fragment) == (
        "(abcdef01 <operator 99> <first> not-a-urn = urn:ddi:x:gone:1) <unknown_4> ()"
    )


# ---- Explaining ------------------------------------------------------------


def test_explain_a_neutral_condition(fragment: ddi_l.DDIFragment) -> None:
    explanation = explain_condition(fragment, ITE)
    assert explanation.item_type == "IfThenElse"
    assert explanation.version == "1"
    assert explanation.language == "Neutral"
    assert explanation.rendered_synopsis is not None
    assert explanation.rendered_synopsis.startswith("(PetKind contains all of 3")
    assert explanation.unnamed_subjects == ("PetKind",)
    assert explanation.descriptions == {
        "en-CA": "Show when a cat lives here and there are more than two pets.",
        "fr-CA": "Afficher quand un chat vit ici et qu\u2019il y a plus de deux animaux.",
    }
    assert explanation.used_inputs == ("PetKind", "PetCount")
    assert explanation.unused_inputs == ("PetAge",)
    assert explanation.error is None


def test_explain_a_lookup_and_native_code(fragment: ddi_l.DDIFragment) -> None:
    lookup = explain_condition(fragment, LOOKUP)
    assert (lookup.language, lookup.rendered_synopsis) == (
        "Blaise5DataLookup",
        "OwnerName, Région",
    )
    native = explain_condition(fragment, NATIVE)
    assert native.language == "Blaise"
    assert native.used_inputs == ("PetCount",)
    assert native.unused_inputs == ()


def test_explain_reports_a_malformed_command(fragment: ddi_l.DDIFragment) -> None:
    content = _item(fragment, LOOKUP).find(f".//{{{R}}}CommandContent")
    content.text = "{broken"
    explanation = explain_condition(fragment, LOOKUP)
    assert explanation.language == "Blaise5DataLookup"
    assert explanation.error is not None and "not valid JSON" in explanation.error


def test_explain_an_unknown_identifier(fragment: ddi_l.DDIFragment) -> None:
    with pytest.raises(KeyError):
        explain_condition(fragment, "missing")


def test_explain_condition_cli(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["explain-condition", str(FIXTURE), ITE]) == 0
    text = capsys.readouterr().out
    assert "Synopsis mismatch the stored synopsis does not name PetKind" in text
    assert "Inputs unused     PetAge" in text
    assert "Description fr-CA" in text

    assert cli.main(["explain-condition", str(FIXTURE), ITE, "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["unused_inputs"] == ["PetAge"]
    assert payload["rendered_synopsis"].startswith("(PetKind")

    assert cli.main(["explain-condition", str(FIXTURE), SEQUENCE]) == 0
    assert "(no command)" in capsys.readouterr().out

    assert cli.main(["explain-condition", str(FIXTURE), "missing"]) == 1
    assert "No item with ID 'missing'" in capsys.readouterr().err

    assert cli.main(["explain-condition", "absent.xml", ITE]) == 1


# ---- Loops, repeats and ElseIf branches -------------------------------------

D = "ddi:datacollection:3_3"
LOOP_ID, COUNT_IN, ALPHA_IN, BETA_IN = _id(90), _id(91), _id(92), _id(93)


def _command(language: str, content: str, description: str = "") -> str:
    described = (
        f'<r:Description><r:Content xml:lang="en-CA">{description}</r:Content>'
        "</r:Description>"
        if description
        else ""
    )
    return (
        f"{described}<r:Command><r:ProgramLanguage>{language}</r:ProgramLanguage>"
        f"<r:CommandContent>{content}</r:CommandContent></r:Command>"
    )


def _parameter(identifier: str, alias: str) -> str:
    return (
        f"<r:InParameter><r:Agency>int.example</r:Agency><r:ID>{identifier}</r:ID>"
        f"<r:Version>1</r:Version><r:Alias>{alias}</r:Alias></r:InParameter>"
    )


def _construct(tag: str, body: str, identifier: str = LOOP_ID) -> str:
    return (
        f'<d:{tag} xmlns:d="{D}" xmlns:r="{R}" isUniversallyUnique="true">'
        f"<r:Agency>int.example</r:Agency><r:ID>{identifier}</r:ID>"
        f"<r:Version>1</r:Version>{body}</d:{tag}>"
    )


def _holder(item, name: str):
    found = item.find(qn(D, name))
    assert found is not None, name
    return found


LOOP = _construct(
    "Loop",
    f"<d:InitialValue>{_command('Blaise', 'i := 1')}</d:InitialValue>"
    f"<d:LoopWhile>{_command('Blaise', 'i &lt;= PetCount')}</d:LoopWhile>"
    f"<d:StepValue>{_command('Blaise', 'i := i + 1')}</d:StepValue>",
)


def test_a_loop_condition_is_its_loop_while() -> None:
    loop = fromstring(LOOP)
    expected = NativeCondition("i <= PetCount", "Blaise")
    assert parse_condition(loop) == expected
    assert parse_condition(_holder(loop, "LoopWhile")) == expected
    assert parse_condition(loop, which="LoopWhile") == expected


def test_which_reads_a_loops_initial_and_step_values() -> None:
    loop = fromstring(LOOP)
    first = NativeCondition("i := 1", "Blaise")
    step = NativeCondition("i := i + 1", "Blaise")
    assert parse_condition(loop, which="InitialValue") == first
    assert parse_condition(loop, which="StepValue") == step
    assert parse_condition(_holder(loop, "StepValue")) == step
    assert parse_condition(loop, which="IfCondition") is None
    with pytest.raises(ValueError, match="which must be one of"):
        parse_condition(loop, which="Bogus")


def test_which_must_agree_with_a_holder_passed_directly() -> None:
    loop = fromstring(LOOP)
    loop_while = _holder(loop, "LoopWhile")
    assert parse_condition(loop_while, which="LoopWhile") == parse_condition(loop)
    with pytest.raises(ValueError, match="another holder than this LoopWhile"):
        parse_condition(loop_while, which="StepValue")
    with pytest.raises(ValueError, match="another holder"):
        write_condition(loop_while, NativeCondition("x", "Blaise"), which="StepValue")
    command = loop_while.find(qn(R, "Command"))
    assert command is not None
    with pytest.raises(ValueError, match="which must be one of"):
        parse_condition(command, which="Bogus")
    assert parse_condition(command, which="StepValue") == parse_condition(loop)


def test_write_condition_into_a_loop_changes_only_the_holder_named() -> None:
    loop = fromstring(LOOP)

    def others(*names: str) -> list[str]:
        return [tostring(_holder(loop, name)) for name in names]

    before = others("InitialValue", "StepValue")
    write_condition(loop, NativeCondition("i < 5", "Blaise"))
    assert parse_condition(loop) == NativeCondition("i < 5", "Blaise")
    assert others("InitialValue", "StepValue") == before

    before = others("InitialValue", "LoopWhile")
    write_condition(loop, NativeCondition("i := i + 2", "Blaise"), which="StepValue")
    assert parse_condition(loop, which="StepValue") == NativeCondition(
        "i := i + 2", "Blaise"
    )
    assert others("InitialValue", "LoopWhile") == before
    with pytest.raises(ValueError, match="which must be one of"):
        write_condition(loop, NativeCondition("x", "Blaise"), which="Bogus")


@pytest.mark.parametrize(
    ("tag", "holder"),
    [("RepeatUntil", "UntilCondition"), ("RepeatWhile", "WhileCondition")],
)
def test_a_repeat_condition_is_found(tag: str, holder: str) -> None:
    item = fromstring(
        _construct(tag, f"<d:{holder}>{_command('Blaise', 'Done = 1')}</d:{holder}>")
    )
    expected = NativeCondition("Done = 1", "Blaise")
    assert parse_condition(item) == expected
    assert parse_condition(_holder(item, holder)) == expected


def test_an_if_then_else_reads_its_own_condition_before_its_branches() -> None:
    ite = fromstring(
        _construct(
            "IfThenElse",
            f"<d:IfCondition>{_command('Blaise', 'A = 1')}</d:IfCondition>"
            f"<d:ElseIf><d:IfCondition>{_command('Blaise', 'B = 2')}</d:IfCondition>"
            "</d:ElseIf>",
        )
    )
    assert parse_condition(ite) == NativeCondition("A = 1", "Blaise")


def test_explain_a_loop_condition() -> None:
    neutral = serialize_condition(
        Condition(
            logic_groups=[
                LogicGroup(
                    GroupBool.FIRST,
                    [
                        Statement(
                            StmtBool.FIRST,
                            f"urn:ddi:int.example:{COUNT_IN}:1",
                            Operator.GREATER_THAN,
                            value="0",
                        )
                    ],
                )
            ],
            synopsis="Count > 0",
        )
    )
    loop = fromstring(
        _construct(
            "Loop",
            _parameter(COUNT_IN, "Count")
            + f"<d:LoopWhile>{_command('Neutral', neutral, 'While pets remain.')}"
            "</d:LoopWhile>",
        )
    )
    explanation = explain_condition(loop, LOOP_ID)
    assert explanation.item_type == "Loop"
    assert explanation.language == "Neutral"
    assert explanation.stored_synopsis == "Count > 0"
    assert explanation.rendered_synopsis is not None
    assert "Count" in explanation.rendered_synopsis
    assert explanation.descriptions == {"en-CA": "While pets remain."}
    assert explanation.used_inputs == ("Count",)
    assert explanation.unused_inputs == ()


def test_explain_counts_the_inputs_an_else_if_uses() -> None:
    ite = fromstring(
        _construct(
            "IfThenElse",
            _parameter(ALPHA_IN, "Alpha")
            + _parameter(BETA_IN, "Beta")
            + f"<d:IfCondition>{_command('Blaise', 'Alpha = 1')}</d:IfCondition>"
            f"<d:ElseIf><d:IfCondition>{_command('Blaise', 'Beta = 2')}"
            "</d:IfCondition></d:ElseIf>"
            f"<d:ElseIf><d:IfCondition>{_command('Neutral', '{broken')}"
            "</d:IfCondition></d:ElseIf>",
        )
    )
    explanation = explain_condition(ite, LOOP_ID)
    assert explanation.rendered_synopsis == "Alpha = 1"
    assert explanation.used_inputs == ("Alpha", "Beta")
    assert explanation.unused_inputs is None
    # The unreadable second branch is reported, and may use any input.
    assert explanation.error is not None
    assert explanation.error.startswith("ElseIf 2: Neutral command")


def test_explain_holds_back_unused_inputs_when_a_branch_is_unreadable() -> None:
    ite = fromstring(
        _construct(
            "IfThenElse",
            _parameter(ALPHA_IN, "Alpha")
            + _parameter(BETA_IN, "Beta")
            + f"<d:IfCondition>{_command('Blaise', 'Alpha = 1')}</d:IfCondition>"
            f"<d:ElseIf><d:IfCondition>{_command('Neutral', '{broken')}"
            "</d:IfCondition></d:ElseIf>",
        )
    )
    explanation = explain_condition(ite, LOOP_ID)
    assert explanation.used_inputs == ("Alpha",)
    assert explanation.unused_inputs is None


def test_explain_holds_back_unused_inputs_when_the_condition_is_unreadable(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    gate = _construct(
        "IfThenElse",
        _parameter(ALPHA_IN, "Alpha")
        + f"<d:IfCondition>{_command('Neutral', '{broken')}</d:IfCondition>",
    )
    explanation = explain_condition(fromstring(gate), LOOP_ID)
    assert explanation.error is not None
    assert explanation.error.startswith("Neutral command")
    assert (explanation.used_inputs, explanation.unused_inputs) == ((), None)

    text = FIXTURE.read_text(encoding="utf-8").replace(
        "</ddi:FragmentInstance>",
        f'<Fragment xmlns="ddi:instance:3_3" xmlns:d="{D}">'
        + gate.replace(f' xmlns:d="{D}" xmlns:r="{R}"', "")
        + "</Fragment></ddi:FragmentInstance>",
    )
    path = tmp_path / "gate.ddi33.xml"
    path.write_text(text, encoding="utf-8")
    assert cli.main(["explain-condition", str(path), LOOP_ID]) == 0
    assert "Inputs unused     (not known" in capsys.readouterr().out
    assert cli.main(["explain-condition", str(path), LOOP_ID, "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["unused_inputs"] is None


def test_explain_counts_the_inputs_a_loops_assignments_use() -> None:
    loop = fromstring(
        _construct(
            "Loop",
            _parameter(COUNT_IN, "N")
            + _parameter(ALPHA_IN, "Step")
            + _parameter(BETA_IN, "Spare")
            + f"<d:InitialValue>{_command('Blaise', 'i := 1')}</d:InitialValue>"
            f"<d:LoopWhile>{_command('Blaise', 'i &lt;= N')}</d:LoopWhile>"
            f"<d:StepValue>{_command('Blaise', 'i := i + Step')}</d:StepValue>",
        )
    )
    explanation = explain_condition(loop, LOOP_ID)
    assert explanation.used_inputs == ("N", "Step")
    assert explanation.unused_inputs == ("Spare",)


def test_explain_condition_cli_on_a_loop(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    loop = LOOP.replace(f' xmlns:d="{D}" xmlns:r="{R}"', "")
    text = FIXTURE.read_text(encoding="utf-8").replace(
        "</ddi:FragmentInstance>",
        f'<Fragment xmlns="ddi:instance:3_3" xmlns:d="{D}">{loop}</Fragment>'
        "</ddi:FragmentInstance>",
    )
    path = tmp_path / "loop.ddi33.xml"
    path.write_text(text, encoding="utf-8")
    assert cli.main(["explain-condition", str(path), LOOP_ID, "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["item_type"] == "Loop"
    assert payload["language"] == "Blaise"
    assert payload["rendered_synopsis"] == "i <= PetCount"


def test_two_copies_of_one_version_resolve_to_the_first():
    """Every index takes the first copy in the document, as `_Context` does."""
    from ddi_l.colectica_logic import _Lookup

    root = fromstring(
        b'<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3">'
        b"<Fragment><r:Note><r:Agency>a.org</r:Agency><r:ID>n</r:ID>"
        b"<r:Version>1</r:Version><r:Relationship>first</r:Relationship>"
        b"</r:Note></Fragment>"
        b"<Fragment><r:Note><r:Agency>a.org</r:Agency><r:ID>n</r:ID>"
        b"<r:Version>1</r:Version><r:Relationship>second</r:Relationship>"
        b"</r:Note></Fragment></FragmentInstance>"
    )

    item = _Lookup(root).items[("a.org", "n")]

    assert item.findtext(qn("ddi:reusable:3_3", "Relationship")) == "first"
