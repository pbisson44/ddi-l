"""The ``colectica-questionnaire`` rules: one positive and one negative case each.

``tests/fixtures/colectica/pets_defects.ddi33.xml`` is a synthetic Pet survey
with one planted defect per rule, beside near misses that must stay silent
(a "What ... date of birth" question with a date domain, a number-only
category label, an ``Or``-joined group, a pipe whose language suffix is
declared). The clean fixtures (``pets_latebound``, ``pets_conditions``) are
the other negative cases.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

import ddi_l
from ddi_l import cli
from ddi_l.colectica_lint import _RULES
from ddi_l.lint import (
    COLECTICA_QUESTIONNAIRE_PROFILE,
    DDI_PROFILE_DEFAULT,
    LintFinding,
    configure_lint,
    iter_registered_profiles,
    iter_rule_metadata,
    run_lint,
    run_profile,
)
from ddi_l.spec.semantics import logic_available

FIXTURES = Path(__file__).parent / "fixtures" / "colectica"
DEFECTS = FIXTURES / "pets_defects.ddi33.xml"
LATEBOUND = FIXTURES / "pets_latebound.ddi33.xml"
CONDITIONS = FIXTURES / "pets_conditions.ddi33.xml"
PART_C = [rule_id for rule_id, *_ in _RULES]

# The organisation-specific options the defects fixture is written against.
OPTIONS = {
    "required_languages": ("en-CA", "fr-CA"),
    "variable_code_pattern": r"P\d{4}",
    "ui_chrome_tokens": ("0%", "Previous", "Next"),
    "pipe_prefixes": ("DT_",),
    "pipe_suffixes": ("_E", "_F"),
}


def _lint(
    path: Path | str | bytes, rules: list[str] | None = None
) -> list[LintFinding]:
    document = ddi_l.read_ddi(path)
    if rules is not None:
        return run_lint(document, rules=rules)
    return run_profile(
        document, COLECTICA_QUESTIONNAIRE_PROFILE, include_schema=False
    ).lint_findings


def _by_rule(findings: list[LintFinding]) -> dict[str, list[LintFinding]]:
    grouped: dict[str, list[LintFinding]] = {}
    for finding in findings:
        grouped.setdefault(finding.rule_id, []).append(finding)
    return grouped


@pytest.fixture
def defects() -> dict[str, list[LintFinding]]:
    configure_lint(**OPTIONS)
    return _by_rule(_lint(DEFECTS))


def _edited(old: str, new: str, path: Path = DEFECTS) -> bytes:
    text = path.read_text(encoding="utf-8")
    assert old in text, old
    return text.replace(old, new, 1).encode()


# ---- Positive cases: each planted defect is found ------------------------------

EXPECTED = {
    "colectica.identifiable.shared-id": (
        "error",
        [
            "OutParameter 33333333 is declared in 2 items: QuestionItem 33333333 "
            "(PetKind), QuestionItem 33333333 (PetKindCopy).",
        ],
    ),
    "colectica.binding.dangling": (
        "error",
        [
            "A binding in Sequence 33333333 (Pet survey) has a source OutParameter "
            "33333333 that is not declared in this file.",
        ],
    ),
    "colectica.condition.malformed": (
        "error",
        [
            "IfThenElse 33333333 (Broken gate): Neutral command is not valid JSON: "
            "Expecting property name enclosed in double quotes (line 1, column 2).",
        ],
    ),
    "colectica.flow.read-before-computed": (
        "warning",
        [
            "IfThenElse 33333333 (Vet gate) reads PetAgeNow before QuestionConstruct "
            "33333333 (PetAgeNow) asks it.",
        ],
    ),
    "colectica.flow.unreachable": (
        "warning",
        [
            "StatementItem 33333333 (Old young pet note) is never reached: no answers "
            "meet the gates on every way to it.",
        ],
    ),
    "colectica.condition.multi-answer-question": (
        "warning",
        [
            "IfThenElse 33333333 (Food gate) tests FoodGrams, answer 2 of 2 of "
            "QuestionItem 33333333 (PetFood): Designer's routing view reports a "
            "condition on one answer of a question with several as broken. Ask it as a"
            " question of its own.",
        ],
    ),
    "colectica.condition.empty": (
        "error",
        [
            "IfThenElse 33333333 (Empty gate) has an empty condition; its description "
            'reads "Show to owners only. Afficher aux propriétaires seulement.".',
        ],
    ),
    "colectica.condition.unsatisfiable": (
        "error",
        [
            "IfThenElse 33333333 (No pets) can never be true in group 1 (PetCount): "
            "the statements joined by And contradict each other on one subject.",
        ],
    ),
    "colectica.condition.native-invalid": (
        "error",
        [
            "ComputationItem 33333333 (Many pets) has Blaise code that is not a single"
            " valid expression: it spans 2 lines; it contains statements (goto/set), "
            "not an expression; it uses typographic quotes.",
        ],
    ),
    "colectica.condition.unused-inputs": (
        "warning",
        [
            "IfThenElse 33333333 (No pets) has 1 input(s) its condition never uses: "
            "PetAge.",
        ],
    ),
    "colectica.condition.synopsis-stale": (
        "info",
        [
            "IfThenElse 33333333 (No pets): the stored synopsis does not name "
            'PetCount; the logic reads "(PetCount = 0 and PetCount is empty) or '
            '(PetCount = 0 or PetCount = 1)".',
        ],
    ),
    "colectica.ifthenelse.partial-gate": (
        "warning",
        [
            "IfThenElse 33333333 (Owner gate) gates only StatementItem 33333333 (Owner"
            " intro), while the 2 construct(s) after it in Sequence 33333333 (Owner "
            'page) show unconditionally; its description reads "If an owner, go to the'
            ' owner page. Si propriétaire, aller à la page du propriétaire.". The gate'
            " probably should wrap the whole page.",
        ],
    ),
    "colectica.codedomain.no-codelist": (
        "error",
        [
            "QuestionItem 33333333 (PetColour) has a code domain with no code list.",
        ],
    ),
    "colectica.domain.label-mismatch": (
        "warning",
        [
            'QuestionItem 33333333 (P0012): "P0016" names P0016, but its output is '
            "P0012.",
        ],
    ),
    "colectica.domain.type-mismatch": (
        "warning",
        [
            'QuestionItem 33333333 (PetLeft) asks "Why did the pet leave?" but its '
            "answer is a date.",
        ],
    ),
    "i18n.missing-language": (
        "error",
        [
            "Category 33333333 (Bird): the label has no fr-CA.",
            "StatementItem 33333333 (Only English): the display text has no fr-CA.",
        ],
    ),
    "text.placeholder-unresolved": (
        "warning",
        [
            'StatementItem 33333333 (Welcome): unresolved placeholder "<<insert owner '
            'name>>" in en-CA text.',
        ],
    ),
    "text.ui-chrome": (
        "warning",
        [
            "StatementItem 33333333 (Goodbye): user-interface text '0%', 'Next', "
            "'Previous' in en-CA content.",
        ],
    ),
    "text.pipe-malformed": (
        "error",
        [
            "StatementItem 33333333 (Welcome): the pipe '#{Owner Name}' contains white"
            " space.",
            "StatementItem 33333333 (Welcome): the pipe '#{DT}' is only a prefix.",
        ],
    ),
    "text.pipe-undeclared": (
        "warning",
        [
            "StatementItem 33333333 (Welcome) pipes #{VetName}, which no lookup field,"
            " parameter or known name declares.",
        ],
    ),
    "colectica.lookup.duplicate-field": (
        "error",
        [
            "ComputationItem 33333333 (Owner lookup) lists the lookup field "
            "'OwnerName' 2 times.",
        ],
    ),
    "colectica.lookup.unlisted-output": (
        "error",
        [
            "ComputationItem 33333333 (Owner lookup): the output 'OwnerPhone' is not "
            "one of its lookup fields.",
            "ComputationItem 33333333 (Owner lookup): the output 'Area' is the lookup "
            "field 'Region' under another name.",
        ],
    ),
    "colectica.lookup.suspicious-field": (
        "warning",
        [
            "ComputationItem 33333333 (Owner lookup): the lookup field '01' is named "
            "like a value.",
            "ComputationItem 33333333 (Owner lookup): the lookup field 'Region' is not"
            " assigned.",
        ],
    ),
    "colectica.alias.escape-compounded": (
        "error",
        [
            "OutParameter 33333333 of Sequence 33333333 (Pet survey) has an alias "
            "escaped 3 times over (28 characters): 'Pets_x005F_x005F_x002F_Count'.",
        ],
    ),
    "colectica.alias.malformed": (
        "warning",
        [
            "OutParameter 33333333 of Sequence 33333333 (Pet survey): the alias "
            "'Pets_x002F_Count' holds an XML escape.",
            "OutParameter 33333333 of Sequence 33333333 (Pet survey): the alias "
            "'numberofpetsthatliveinyourhome' looks like concatenated question text.",
            "OutParameter 33333333 of Sequence 33333333 (Pet survey): the alias "
            "'Pets_Count_Count_Count_Count_Count_Count_Count_Count_Count_…' is 88 "
            "characters long.",
        ],
    ),
    "colectica.statement.logic-note": (
        "warning",
        [
            'StatementItem 33333333 (Flow condition) reads "Flow condition": a design '
            "note shown to respondents as content.",
        ],
    ),
}


def test_a_design_note_typed_as_a_note_is_not_reported(tmp_path: Path) -> None:
    # Colectica types a statement that is not shown as a Note.
    text = DEFECTS.read_text(encoding="utf-8-sig")
    marker = "<r:ID>33333333-3333-4333-8333-000000000016</r:ID>"
    assert marker in text
    note = (
        "<r:UserAttributePair><r:AttributeKey>extension:TypeOfStatement</r:AttributeKey>"
        "<r:AttributeValue>Note</r:AttributeValue></r:UserAttributePair>"
    )
    head, tail = text.split(marker, 1)
    version_end = tail.index("</r:Version>") + len("</r:Version>")
    typed = tmp_path / "typed.xml"
    typed.write_text(
        head + marker + tail[:version_end] + note + tail[version_end:], encoding="utf-8"
    )
    found = _by_rule(_lint(typed)).get("colectica.statement.logic-note", [])
    assert [f for f in found if "Flow condition" in f.message] == []


def test_every_part_c_rule_has_an_expected_case() -> None:
    assert sorted(EXPECTED) == sorted(PART_C)


@pytest.mark.parametrize("rule_id", sorted(EXPECTED))
def test_the_planted_defect_is_found(
    rule_id: str, defects: dict[str, list[LintFinding]]
) -> None:
    severity, fragments = EXPECTED[rule_id]
    findings = defects.get(rule_id, [])
    assert len(findings) == len(fragments), [f.message for f in findings]
    for finding, fragment in zip(findings, fragments, strict=True):
        assert finding.severity == severity
        assert finding.message == fragment
        assert finding.location


# ---- Negative cases ----------------------------------------------------------------


@pytest.mark.parametrize(
    "path", [LATEBOUND, CONDITIONS], ids=["latebound", "conditions"]
)
def test_clean_fixtures_raise_no_defect_rule(path: Path) -> None:
    configure_lint(**OPTIONS)
    rule_ids = {finding.rule_id for finding in _lint(path)}
    # The conditions fixture deliberately carries a stale synopsis, an unused
    # input, an unassigned lookup field and English-only texts.
    allowed = {
        "colectica.condition.synopsis-stale",
        "colectica.condition.unused-inputs",
        "colectica.lookup.suspicious-field",
        "i18n.missing-language",
    }
    assert not (rule_ids & set(PART_C)) - allowed


def test_the_profile_lints_the_items_of_a_ddi_instance(fixtures_dir: Path) -> None:
    # Items nest inside schemes in an instance; findings name the item itself.
    configure_lint(required_languages=("en", "fr"))
    findings = _lint(fixtures_dir / "instances" / "example_instance.xml")
    missing = [f for f in findings if f.rule_id == "i18n.missing-language"]
    assert missing
    assert all(
        not f.message.startswith(("StudyUnit", "QuestionScheme")) for f in missing
    )


def test_part_c_rules_stay_out_of_the_default_profile() -> None:
    configure_lint(**OPTIONS)
    profiles = dict(iter_registered_profiles())
    assert not set(PART_C) & set(profiles[DDI_PROFILE_DEFAULT])
    assert set(PART_C) <= set(profiles[COLECTICA_QUESTIONNAIRE_PROFILE])
    default_ids = {f.rule_id for f in run_lint(ddi_l.read_ddi(DEFECTS))}
    assert default_ids
    assert not default_ids & set(PART_C)


def test_near_misses_stay_silent(defects: dict[str, list[LintFinding]]) -> None:
    messages = [f.message for findings in defects.values() for f in findings]
    # "What is the pet's date of birth?" with a date domain.
    assert not any("PetBirth" in message for message in messages)
    # A category labelled "1914" reads the same in every language.
    assert not any("(1914)" in message for message in messages)
    # #{OwnerName_E} and #{OwnerName_F} strip to a declared lookup field.
    assert not any("OwnerName_" in message for message in messages)
    # The compounded alias is not also reported as malformed.
    assert not any("x005F" in f.message for f in defects["colectica.alias.malformed"])
    # Group 2 of "No pets" joins its statements with Or.
    assert "group 2" not in defects["colectica.condition.unsatisfiable"][0].message
    # The empty gate's description does not route to a page.
    assert len(defects["colectica.ifthenelse.partial-gate"]) == 1
    # The senior gate reads the pet's age after its question asks it, and the
    # question has one answer.
    assert not any("(Senior gate)" in message for message in messages)


def test_organisation_specific_rules_do_nothing_until_configured() -> None:
    configured = {
        "i18n.missing-language",
        "colectica.domain.label-mismatch",
        "text.ui-chrome",
    }
    rule_ids = {finding.rule_id for finding in _lint(DEFECTS)}
    assert not rule_ids & configured
    configure_lint(
        placeholder_patterns=(), logic_note_patterns=(), gate_description_patterns=()
    )
    rule_ids = {finding.rule_id for finding in _lint(DEFECTS)}
    assert not rule_ids & {
        "text.placeholder-unresolved",
        "colectica.statement.logic-note",
        "colectica.ifthenelse.partial-gate",
    }


def test_versions_of_one_item_may_share_their_children() -> None:
    text = DEFECTS.read_text(encoding="utf-8")
    opening = '<Fragment xmlns:r="ddi:reusable:3_3" xmlns="ddi:instance:3_3">\n  <QuestionItem'
    start = text.index(opening)
    end = text.index("</Fragment>", start) + len("</Fragment>")
    # Version 2 of PetKind, declaring the same OutParameter as version 1.
    version_2 = (
        text[start:end]
        .replace("8333-000000000001:1</r:URN>", "8333-000000000001:2</r:URN>", 1)
        .replace("<r:Version>1</r:Version>", "<r:Version>2</r:Version>", 1)
    )
    document = (text[:end] + "\n" + version_2 + text[end:]).encode()
    findings = _lint(document, rules=["colectica.identifiable.shared-id"])
    # Still one finding, for the PetKind copy, not for PetKind's own versions.
    assert len(findings) == 1
    assert "PetKindCopy" in findings[0].message


def test_an_empty_or_whitespace_pipe_is_malformed() -> None:
    configure_lint(**OPTIONS)
    document = _edited("#{VetName}", "#{} #{ }")
    messages = [f.message for f in _lint(document, rules=["text.pipe-malformed"])]
    assert any("'#{}' is empty" in message for message in messages)
    assert any("'#{ }' is empty" in message for message in messages)


def test_known_names_declare_a_pipe() -> None:
    configure_lint(**OPTIONS, known_names=("VetName",))
    assert _lint(DEFECTS, rules=["text.pipe-undeclared"]) == []


def test_a_description_missing_a_language_is_info() -> None:
    configure_lint(**OPTIONS)
    document = _edited(
        '<r:Content xml:lang="fr-CA">Afficher aux propriétaires seulement.</r:Content>',
        "",
    )
    findings = _lint(document, rules=["i18n.missing-language"])
    info = [f for f in findings if f.severity == "info"]
    assert [f.message for f in info] == [
        "IfThenElse 33333333 (Empty gate): the condition description has no fr-CA."
    ]


def test_a_missing_synopsis_is_stale() -> None:
    document = _edited('"Synopsis":"PetCount Greater than 0"', '"Synopsis":""')
    findings = _lint(document, rules=["colectica.condition.synopsis-stale"])
    assert any("there is no stored synopsis" in f.message for f in findings)


def test_undeclared_native_inputs_are_named() -> None:
    document = _edited("{{PetCount}} &gt; 5", "{{PetTotal}} &gt; 5")
    (finding,) = _lint(document, rules=["colectica.condition.native-invalid"])
    assert "it names PetTotal, not inputs of the item" in finding.message


_MANY_PETS = "{{PetCount}} &gt; 5 and Owner = \u201cyes\u201d\nset Flag := 1"
_PET_TOTAL = """    <r:OutParameter isUniversallyUnique="true">
      <r:URN>urn:ddi:int.example:33333333-3333-4333-8333-0000000000a1:1</r:URN>
      <r:Agency>int.example</r:Agency>
      <r:ID>33333333-3333-4333-8333-0000000000a1</r:ID>
      <r:Version>1</r:Version>
      <r:Alias>PetTotal</r:Alias>
      <r:NumericRepresentation blankIsMissingValue="false">
        <r:NumericTypeCode>Integer</r:NumericTypeCode>
      </r:NumericRepresentation>
    </r:OutParameter>
"""


def _program(content: str) -> bytes:
    """The defects fixture with Many pets given an output and ``content``."""
    command = (
        "    <r:CommandCode>\n      <r:Command>\n"
        "        <r:ProgramLanguage>Blaise</r:ProgramLanguage>\n"
        f"        <r:CommandContent>{_MANY_PETS}"
    )
    text = DEFECTS.read_text(encoding="utf-8")
    assert text.count(command) == 1
    return text.replace(
        command, _PET_TOTAL + command.replace(_MANY_PETS, content)
    ).encode()


def test_a_computation_with_outputs_holds_a_program() -> None:
    program = (
        "IF {{PetCount}} &gt; 5 THEN\n  {{PetTotal}} := {{PetCount}}\nENDIF\n"
        'Note := "the pet\u2019s \u201cname\u201d"'
    )
    findings = _lint(_program(program), rules=["colectica.condition.native-invalid"])
    assert not [f for f in findings if "(Many pets)" in f.message]


def test_a_program_names_only_its_parameters() -> None:
    program = "{{PetTotal}} := {{PetWeight}} + 1\nset Flag := \u20181\u2019"
    (finding,) = _lint(_program(program), rules=["colectica.condition.native-invalid"])
    assert finding.message.endswith(
        "(Many pets) has Blaise code that is not a valid program: it contains goto "
        "or set, which Blaise does not have; it uses typographic quotes; it names "
        "PetWeight, not inputs or outputs of the item."
    )


def test_typographic_quotes_inside_a_string_are_text() -> None:
    condition = '{{PetCount}} &gt; 5 and Owner = "l\u2019ami \u201cRex\u201d"'
    document = _edited(_MANY_PETS, condition)
    assert not _lint(document, rules=["colectica.condition.native-invalid"])


def test_an_apostrophe_in_a_blaise_comment_hides_no_code() -> None:
    # { the owner's choice } is a comment: the quote in it opens no string.
    condition = (
        "{ the owner\u2019s choice } {{PetCount}} &gt; 5 and Owner = \u201cyes\u201d"
        " { that's all }"
    )
    (finding,) = _lint(
        _edited(_MANY_PETS, condition), rules=["colectica.condition.native-invalid"]
    )
    assert finding.message.endswith("it uses typographic quotes.")
    # A {{name}} input is not a comment.
    clean = "{ the owner's choice } {{PetCount}} &gt; 5"
    assert not _lint(
        _edited(_MANY_PETS, clean), rules=["colectica.condition.native-invalid"]
    )


@pytest.mark.parametrize(
    "condition",
    [
        "{ only owners }\n{{PetCount}} &gt; 5",
        "{{PetCount}} &gt; 5\n{ only owners }",
        "{ only\nowners } {{PetCount}} &gt; 5",
    ],
)
def test_a_comment_on_its_own_line_is_not_a_second_line(condition: str) -> None:
    document = _edited(_MANY_PETS, condition)
    assert not _lint(document, rules=["colectica.condition.native-invalid"])


def test_a_when_question_answered_with_codes_is_a_mismatch() -> None:
    document = _edited("What colour is your pet?", "When did you adopt your pet?")
    (finding,) = _lint(document, rules=["colectica.domain.type-mismatch"])[1:]
    assert "is a code or text, not a date" in finding.message


def test_a_malformed_lookup_is_reported_and_skipped_by_lookup_rules() -> None:
    document = _edited('{"DataLookupFields":[', '{"DataLookupFields":3,"x":[')
    rules = [
        "colectica.condition.malformed",
        "colectica.lookup.duplicate-field",
        "colectica.lookup.suspicious-field",
    ]
    counts = Counter(f.rule_id for f in _lint(document, rules=rules))
    assert counts == {"colectica.condition.malformed": 2}


def test_lookup_outputs_match_fields_by_name_when_fields_have_no_identifier() -> None:
    # Region loses its Identifier; the output for it is then found by its name.
    region = '"IsAssigned":false,"Identifier":"33333333-3333-4333-8333-000000000092"}'
    document = _edited(region, '"IsAssigned":false}')
    document = document.replace(
        b"<r:Alias>Area</r:Alias>", b"<r:Alias>Region</r:Alias>"
    )
    findings = _lint(document, rules=["colectica.lookup.unlisted-output"])
    assert [f.message.split(": ", 1)[1] for f in findings] == [
        "the output 'OwnerPhone' is not one of its lookup fields."
    ]


def test_unused_inputs_of_native_code() -> None:
    # The owner gate rewritten as native code that ignores its PetCount input.
    text = DEFECTS.read_text(encoding="utf-8")
    line = next(line for line in text.splitlines() if "PetCount Greater than 0" in line)
    native = text.replace(
        line, "        <r:CommandContent>Total &gt; 0</r:CommandContent>"
    )
    lines = native.splitlines()
    index = lines.index("        <r:CommandContent>Total &gt; 0</r:CommandContent>")
    lines[index - 1] = "        <r:ProgramLanguage>Blaise</r:ProgramLanguage>"
    findings = _lint(
        "\n".join(lines).encode(), rules=["colectica.condition.unused-inputs"]
    )
    assert any(
        "(Owner gate) has 1 input(s) its condition never uses: PetCount." in f.message
        for f in findings
    )


def _with_items(*items: str) -> bytes:
    """The clean conditions fixture with ``items`` appended, one per fragment."""
    fragments = "".join(
        '<Fragment xmlns="ddi:instance:3_3" xmlns:d="ddi:datacollection:3_3">'
        f"{item}</Fragment>"
        for item in items
    )
    text = CONDITIONS.read_text(encoding="utf-8")
    return text.replace(
        "</ddi:FragmentInstance>", f"{fragments}</ddi:FragmentInstance>"
    ).encode()


def _synthetic(tag: str, identifier: str, name: str, body: str) -> str:
    return (
        f'<d:{tag} isUniversallyUnique="true"><r:Agency>int.example</r:Agency>'
        f"<r:ID>22222222-2222-4222-8222-{identifier}</r:ID><r:Version>1</r:Version>"
        f'<d:ConstructName><r:String xml:lang="en-CA">{name}</r:String>'
        f"</d:ConstructName>{body}</d:{tag}>"
    )


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


def _input(identifier: str, alias: str) -> str:
    return (
        "<r:InParameter><r:Agency>int.example</r:Agency>"
        f"<r:ID>22222222-2222-4222-8222-{identifier}</r:ID><r:Version>1</r:Version>"
        f"<r:Alias>{alias}</r:Alias></r:InParameter>"
    )


EMPTY_NEUTRAL = '{"LogicGroups":[],"Synopsis":"","Version":1}'
SYNTHETIC = ("(Each pet)", "(Ask again)", "(Gate)")


def _lint_synthetic(document: bytes, rules: list[str]) -> list[LintFinding]:
    """The findings about the appended items (the fixture has its own)."""
    return [
        finding
        for finding in _lint(document, rules=rules)
        if any(name in finding.message for name in SYNTHETIC)
    ]


def test_loop_repeat_and_else_if_conditions_are_checked() -> None:
    document = _with_items(
        _synthetic(
            "Loop",
            "000000000901",
            "Each pet",
            f"<d:InitialValue>{_command('Blaise', 'i := 1')}</d:InitialValue>"
            f"<d:LoopWhile>{_command('Neutral', '{not json')}</d:LoopWhile>",
        ),
        _synthetic(
            "RepeatUntil",
            "000000000902",
            "Ask again",
            f"<d:UntilCondition>"
            f"{_command('Neutral', EMPTY_NEUTRAL, 'Until the owner says no.')}"
            "</d:UntilCondition>",
        ),
        _synthetic(
            "IfThenElse",
            "000000000903",
            "Gate",
            _input("000000000904", "Alpha")
            + _input("000000000905", "Beta")
            + f"<d:IfCondition>{_command('Blaise', 'Alpha = 1')}</d:IfCondition>"
            f"<d:ElseIf><d:IfCondition>{_command('Blaise', 'Beta = 2')}"
            "</d:IfCondition></d:ElseIf>"
            f"<d:ElseIf><d:IfCondition>{_command('Neutral', '{not json')}"
            "</d:IfCondition></d:ElseIf>",
        ),
    )
    rules = [
        "colectica.condition.malformed",
        "colectica.condition.empty",
        "colectica.condition.unused-inputs",
    ]
    found = _by_rule(_lint_synthetic(document, rules))
    malformed = [f.message for f in found["colectica.condition.malformed"]]
    assert len(malformed) == 2
    assert malformed[0].startswith("Loop 22222222 (Each pet): Neutral command")
    assert malformed[1].startswith(
        "IfThenElse 22222222 (Gate), ElseIf 2: Neutral command"
    )
    (empty,) = found["colectica.condition.empty"]
    assert empty.message == (
        "RepeatUntil 22222222 (Ask again) has an empty condition; its description "
        'reads "Until the owner says no.".'
    )
    # Beta is used by the first ElseIf, so neither input is unused; the
    # unreadable second branch is reported as malformed instead.
    assert "colectica.condition.unused-inputs" not in found


def test_an_input_used_only_by_an_else_if_is_used() -> None:
    def gate(else_if: str) -> bytes:
        return _with_items(
            _synthetic(
                "IfThenElse",
                "000000000903",
                "Gate",
                _input("000000000904", "Alpha")
                + _input("000000000905", "Beta")
                + _input("000000000906", "Gamma")
                + f"<d:IfCondition>{_command('Blaise', 'Alpha = 1')}</d:IfCondition>"
                f"<d:ElseIf><d:IfCondition>{_command('Blaise', else_if)}"
                "</d:IfCondition></d:ElseIf>",
            )
        )

    rules = ["colectica.condition.unused-inputs"]
    (finding,) = _lint_synthetic(gate("Beta = 2"), rules)
    assert finding.message == (
        "IfThenElse 22222222 (Gate) has 1 input(s) its conditions never use: Gamma."
    )
    assert _lint_synthetic(gate("Beta = 2 or Gamma = 3"), rules) == []


@pytest.mark.parametrize("empty_branch", ["main", "ElseIf"])
def test_an_empty_branch_is_left_to_the_empty_rule(empty_branch: str) -> None:
    empty = _command("Neutral", EMPTY_NEUTRAL, "If Alpha is 1")
    filled = _command("Blaise", "Beta = 2")
    main, branch = (empty, filled) if empty_branch == "main" else (filled, empty)
    document = _with_items(
        _synthetic(
            "IfThenElse",
            "000000000903",
            "Gate",
            _input("000000000904", "Alpha")
            + _input("000000000905", "Beta")
            + f"<d:IfCondition>{main}</d:IfCondition>"
            f"<d:ElseIf><d:IfCondition>{branch}</d:IfCondition></d:ElseIf>",
        )
    )
    rules = ["colectica.condition.empty", "colectica.condition.unused-inputs"]
    found = [f.rule_id for f in _lint_synthetic(document, rules)]
    assert found == ["colectica.condition.empty"]


def test_an_empty_else_if_condition_is_reported_with_its_branch() -> None:
    document = _with_items(
        _synthetic(
            "IfThenElse",
            "000000000903",
            "Gate",
            f"<d:IfCondition>{_command('Blaise', 'A = 1')}</d:IfCondition>"
            "<d:ElseIf><d:IfCondition>"
            f"{_command('Neutral', EMPTY_NEUTRAL, 'Second branch.')}"
            "</d:IfCondition></d:ElseIf>",
        )
    )
    (finding,) = _lint_synthetic(document, ["colectica.condition.empty"])
    assert finding.message == (
        "IfThenElse 22222222 (Gate), ElseIf 1 has an empty condition; its "
        'description reads "Second branch.".'
    )


# ---- Metadata, configuration and CLI ------------------------------------------------


def test_every_rule_documents_its_severity_and_an_example() -> None:
    infos = {info.rule_id: info for info in iter_rule_metadata()}
    profile = dict(iter_registered_profiles())[COLECTICA_QUESTIONNAIRE_PROFILE]
    for rule_id in profile:
        info = infos[rule_id]
        assert info.severity and info.example and info.summary, rule_id
    assert infos["colectica.condition.empty"].profiles == (
        COLECTICA_QUESTIONNAIRE_PROFILE,
    )
    assert not infos["colectica.condition.empty"].default
    assert infos["ddi.reference.integrity"].default


def test_heuristic_rules_report_warnings_at_most(
    defects: dict[str, list[LintFinding]],
) -> None:
    infos = {info.rule_id: info for info in iter_rule_metadata()}
    heuristic = [
        rule_id
        for rule_id in PART_C
        if "*Heuristic.*" in (infos[rule_id].description or "")
    ]
    assert len(heuristic) == 6
    for rule_id in heuristic:
        assert infos[rule_id].severity == "warning"
        assert all(f.severity != "error" for f in defects.get(rule_id, []))


def test_lint_options_are_validated() -> None:
    with pytest.raises(TypeError, match="Unknown lint option"):
        configure_lint(unknown_option=True)
    with pytest.raises(ValueError, match="Invalid lint pattern"):
        configure_lint(variable_code_pattern="(")
    with pytest.raises(TypeError, match="not a string"):
        configure_lint(required_languages="en")


def test_lint_table_and_config_options(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    names = tmp_path / "names.txt"
    names.write_text("# supplied at run time\nVetName\n", encoding="utf-8")
    config = tmp_path / "lint.json"
    config.write_text(
        json.dumps(
            {
                "variable_code_pattern": r"P\d{4}",
                "ui_chrome_tokens": ["0%", "Previous", "Next"],
                "pipe_prefixes": ["DT_"],
                "pipe_suffixes": ["_E", "_F"],
            }
        ),
        encoding="utf-8",
    )
    status = cli.main(
        [
            "lint",
            str(DEFECTS),
            "--profile",
            COLECTICA_QUESTIONNAIRE_PROFILE,
            "--format",
            "table",
            "--required-language",
            "en-CA",
            "--required-language",
            "fr-CA",
            "--known-names",
            str(names),
            "--lint-config",
            str(config),
        ]
    )
    assert status == 1
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].split() == ["severity", "rule", "message"]
    assert lines[2].startswith("error ")
    assert not any(line != line.rstrip() for line in lines)
    assert any("text.ui-chrome" in line for line in lines)
    assert not any("#{VetName}" in line for line in lines)


def test_lint_table_to_a_file_with_several_inputs(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    status = cli.main(
        [
            "lint",
            str(LATEBOUND),
            str(CONDITIONS),
            "--format",
            "table",
            "--output",
            str(out),
        ]
    )
    assert status == 0
    written = sorted(path.name for path in out.iterdir())
    assert written == [
        "pets_conditions.ddi33.lint.txt",
        "pets_latebound.ddi33.lint.txt",
    ]
    text = (out / "pets_latebound.ddi33.lint.txt").read_text(encoding="utf-8")
    assert text.splitlines()[0].endswith("pets_latebound.ddi33.xml")
    assert "ddi.reference.provenance-external" in text


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("[1, 2]", "takes a JSON object"),
        ('{"bogus": 1}', "Unknown lint option"),
        ('{"placeholder_patterns": ["("]}', "Invalid lint pattern"),
    ],
)
def test_bad_lint_config_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], content: str, message: str
) -> None:
    config = tmp_path / "lint.json"
    config.write_text(content, encoding="utf-8")
    assert cli.main(["lint", str(LATEBOUND), "--lint-config", str(config)]) == 2
    assert message in capsys.readouterr().err


def test_missing_known_names_file_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["lint", str(LATEBOUND), "--known-names", "absent.txt"]) == 2
    assert "absent.txt" in capsys.readouterr().err


def test_list_rules_includes_the_part_c_rules(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["lint", "--list-rules"]) == 0
    listed = {json.loads(line)["id"] for line in capsys.readouterr().out.splitlines()}
    assert set(PART_C) <= listed


def test_a_lookup_branch_leaves_the_inputs_alone() -> None:
    lookup = _command(
        "Blaise5DataLookup",
        '{"DataLookupFields":[{"Name":"Region","Type":"String","IsAssigned":true}]}',
    )
    document = _with_items(
        _synthetic(
            "IfThenElse",
            "000000000903",
            "Gate",
            _input("000000000904", "Alpha")
            + _input("000000000905", "Beta")
            + f"<d:IfCondition>{_command('Blaise', 'Alpha = 1')}</d:IfCondition>"
            f"<d:ElseIf><d:IfCondition>{lookup}</d:IfCondition></d:ElseIf>",
        )
    )
    assert _lint_synthetic(document, ["colectica.condition.unused-inputs"]) == []


def test_an_input_passed_on_to_the_then_branch_is_used() -> None:
    """An input the IfThenElse binds onward feeds what it holds."""

    def ref(tag: str, identifier: str, kind: str) -> str:
        return (
            f'<r:{tag} lateBound="true"><r:Agency>int.example</r:Agency>'
            f"<r:ID>22222222-2222-4222-8222-{identifier}</r:ID>"
            f"<r:Version>1</r:Version><r:TypeOfObject>{kind}</r:TypeOfObject></r:{tag}>"
        )

    passed_on = (
        "<r:Binding>"
        + ref("SourceParameterReference", "000000000905", "InParameter")
        + ref("TargetParameterReference", "000000000907", "InParameter")
        + "</r:Binding>"
    )
    document = _with_items(
        _synthetic(
            "IfThenElse",
            "000000000903",
            "Gate",
            _input("000000000904", "Alpha")
            + _input("000000000905", "Beta")
            + _input("000000000906", "Gamma")
            + passed_on
            + f"<d:IfCondition>{_command('Blaise', 'Alpha = 1')}</d:IfCondition>",
        )
    )
    (finding,) = _lint_synthetic(document, ["colectica.condition.unused-inputs"])
    assert finding.message == (
        "IfThenElse 22222222 (Gate) has 1 input(s) its condition never uses: Gamma."
    )


# ---- The flow: a page reused by an early exit -----------------------------------------


def _flow_instrument(*, exit_first: bool) -> bytes:
    """A Pet survey whose Thanks page is reached from an early exit and at the end.

    The Thanks page's gate reads PetAge. With ``exit_first``, the exit comes
    before the PetAge question, so on that path the page reads PetAge before
    it is asked.
    """

    def i(n: int) -> str:
        return f"66666666-6666-4666-8666-{n:012d}"

    def head(n: int) -> str:
        return (
            f"<r:URN>urn:ddi:int.example:{i(n)}:1</r:URN><r:Agency>int.example"
            f"</r:Agency><r:ID>{i(n)}</r:ID><r:Version>1</r:Version>"
        )

    def ref(tag: str, n: int, kind: str) -> str:
        return (
            f"<{tag}><r:Agency>int.example</r:Agency><r:ID>{i(n)}</r:ID>"
            f"<r:Version>1</r:Version><r:TypeOfObject>{kind}</r:TypeOfObject></{tag}>"
        )

    def param(tag: str, n: int, alias: str) -> str:
        return (
            f'<r:{tag} isUniversallyUnique="true">{head(n)}<r:Alias>{alias}</r:Alias>'
            f"</r:{tag}>"
        )

    def bind(source: int, target: int, kinds: str = "Out,In") -> str:
        s, t = kinds.split(",")
        return (
            "<r:Binding>"
            + ref("r:SourceParameterReference", source, f"{s}Parameter")
            + ref("r:TargetParameterReference", target, f"{t}Parameter")
            + "</r:Binding>"
        )

    def name(text: str, tag: str = "ConstructName") -> str:
        return f'<{tag}><r:String xml:lang="en">{text}</r:String></{tag}>'

    def item(local: str, n: int, body: str) -> str:
        return (
            f'<{local} isUniversallyUnique="true" xmlns="ddi:datacollection:3_3">'
            f"{head(n)}{body}</{local}>"
        )

    def gate(
        n: int,
        label: str,
        inputs: str,
        subject: int,
        value: str,
        then: int,
        extra: str = "",
    ) -> str:
        condition = (
            '{"LogicGroups":[{"GroupBooleanType":0,"Statements":[{"StatementBooleanType"'
            f':0,"Subject":"urn:ddi:int.example:{i(subject)}:1","Operator":1,"Value":'
            f'{{"Value":"{value}","ValueNotNeeded":false,"SelectedCodes":[]}}}}]}}],'
            f'"Synopsis":"{label}","Version":1}}'
        )
        return item(
            "IfThenElse",
            n,
            name(label)
            + inputs
            + extra
            + "<IfCondition><r:Command><r:ProgramLanguage>Neutral</r:ProgramLanguage>"
            + f"<r:CommandContent>{condition}</r:CommandContent></r:Command></IfCondition>"
            + ref("ThenConstructReference", then, "Sequence"),
        )

    def question(n: int, label: str, output: int) -> str:
        return item(
            "QuestionItem",
            n,
            name(label, "QuestionItemName")
            + param("OutParameter", output, label)
            + f'<QuestionText><LiteralText><Text xml:lang="en">{label}?</Text>'
            "</LiteralText></QuestionText>"
            '<NumericDomain blankIsMissingValue="false"><r:NumericTypeCode>Integer'
            "</r:NumericTypeCode></NumericDomain>",
        )

    def construct(n: int, label: str, output: int, source: int, of: int) -> str:
        return item(
            "QuestionConstruct",
            n,
            name(label)
            + param("OutParameter", output, label)
            + bind(source, output, "Out,Out")
            + ref("r:QuestionReference", of, "QuestionItem"),
        )

    # The PetAge question sits on a page that re-exports its answer.
    order = [
        (222, "QuestionConstruct"),
        (210, "IfThenElse"),
        (260, "Sequence"),
    ]
    if not exit_first:
        order = [order[0], order[2], order[1]]
    items = [
        item(
            "Instrument",
            200,
            name("Pet survey", "InstrumentName")
            + ref("ControlConstructReference", 201, "Sequence"),
        ),
        item(
            "Sequence",
            201,
            name("Root")
            + bind(223, 211)
            + bind(261, 212)
            + bind(261, 241)
            + "".join(ref("ControlConstructReference", n, k) for n, k in order)
            + ref("ControlConstructReference", 240, "Sequence"),
        ),
        question(220, "PetCount", 221),
        construct(222, "PetCount", 223, 221, 220),
        question(230, "PetAge", 231),
        construct(232, "PetAge", 233, 231, 230),
        item(
            "Sequence",
            260,
            name("Age page")
            + param("OutParameter", 261, "PetAge")
            + bind(233, 261, "Out,Out")
            + ref("ControlConstructReference", 232, "QuestionConstruct"),
        ),
        gate(
            210,
            "Exit gate",
            param("InParameter", 211, "PetCount") + param("InParameter", 212, "PetAge"),
            211,
            "0",
            240,
            extra=bind(212, 241, "In,In"),
        ),
        item(
            "Sequence",
            240,
            name("Thanks page")
            + param("InParameter", 241, "PetAge")
            + bind(241, 251, "In,In")
            + ref("ControlConstructReference", 250, "IfThenElse"),
        ),
        gate(250, "Vet gate", param("InParameter", 251, "PetAge"), 251, "2", 255),
        item(
            "Sequence",
            255,
            name("Vet branch")
            + "<TypeOfSequence>ConditionalChildContainer</TypeOfSequence>"
            + ref("ControlConstructReference", 256, "StatementItem"),
        ),
        item(
            "StatementItem",
            256,
            name("Vet note")
            + '<DisplayText audienceLanguage="en"><LiteralText><Text>See a vet.</Text></LiteralText></DisplayText>',
        ),
    ]
    fragments = "".join(
        f'<Fragment xmlns:r="ddi:reusable:3_3" xmlns="ddi:instance:3_3">{x}</Fragment>'
        for x in items
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<ddi:FragmentInstance xmlns:r="ddi:reusable:3_3" xmlns:ddi="ddi:instance:3_3">'
        + ref("ddi:TopLevelReference", 200, "Instrument")
        + fragments
        + "</ddi:FragmentInstance>"
    ).encode()


def test_a_page_reused_by_an_early_exit_reads_before_the_question() -> None:
    rules = ["colectica.flow.read-before-computed"]
    document = _flow_instrument(exit_first=True)
    assert not ddi_l.read_ddi(document).validate()
    findings = _lint(document, rules)
    message = (
        "IfThenElse 66666666 (Vet gate), reached through IfThenElse 66666666 "
        "(Exit gate), reads PetAge before QuestionConstruct 66666666 (PetAge) asks it."
    )
    if logic_available():
        # The solver finds a respondent the exit takes there first.
        message += " For example, when PetCount is 0."
    assert [(f.severity, f.message) for f in findings] == [("warning", message)]
    # Asked before the exit, the value is there on both paths to the page.
    assert _lint(_flow_instrument(exit_first=False), rules) == []


def test_a_read_no_respondent_meets_first_is_only_information() -> None:
    pytest.importorskip("z3", reason="requires the 'logic' extra")
    rules = ["colectica.flow.read-before-computed"]
    # No answer takes the exit: PetCount is 0 and more than 5.
    document = _flow_instrument(exit_first=True).replace(
        b'"Operator":1,"Value":{"Value":"0","ValueNotNeeded":false,'
        b'"SelectedCodes":[]}}]',
        b'"Operator":1,"Value":{"Value":"0","ValueNotNeeded":false,'
        b'"SelectedCodes":[]}},{"StatementBooleanType":1,"Subject":'
        b'"urn:ddi:int.example:66666666-6666-4666-8666-000000000211:1","Operator":3,'
        b'"Value":{"Value":"5","ValueNotNeeded":false,"SelectedCodes":[]}}]',
    )
    findings = _lint(document, rules)
    assert [(f.severity, f.message) for f in findings] == [
        (
            "info",
            "IfThenElse 66666666 (Vet gate), reached through IfThenElse 66666666 "
            "(Exit gate), reads PetAge before QuestionConstruct 66666666 (PetAge) "
            "asks it. No respondent reaches it before then, so only Designer's "
            "routing view reports it.",
        )
    ]
    # The page is reached later all the same: nothing is unreachable.
    assert _lint(document, ["colectica.flow.unreachable"]) == []


def test_without_the_logic_extra_a_flow_is_not_checked_for_reach(monkeypatch) -> None:
    from ddi_l.spec import semantics

    monkeypatch.setattr(semantics, "logic_available", lambda: False)
    findings = _lint(DEFECTS, ["colectica.flow.unreachable"])
    assert [(f.severity, f.message) for f in findings] == [
        (
            "info",
            "Sequence 33333333 (Pet survey) was not checked for constructs no "
            'respondent reaches: that needs the logic extra (pip install "ddi-l[logic]").',
        )
    ]
    # The other flow rules run as they do without the solver.
    (finding,) = _lint(DEFECTS, ["colectica.flow.read-before-computed"])
    assert finding.severity == "warning"
