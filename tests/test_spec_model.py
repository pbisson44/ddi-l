"""Questionnaire specs: the schema, the strict reader and the checks."""

from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("yaml", reason="requires the 'spec' extra")
jsonschema = pytest.importorskip("jsonschema", reason="requires the 'spec' extra")

from ddi_l import cli
from ddi_l.spec import model
from ddi_l.spec.model import (
    DomainSpec,
    SpecDependencyError,
    SpecError,
    example_spec,
    load_spec,
    spec_from_data,
    spec_schema,
    validate_spec,
)
from ddi_l.spec.rules import RULE_SEVERITIES

EXAMPLES = Path(model.__file__).parent / "examples"


def _minimal(**extra: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "spec": "s",
        "modules": [{"id": "m", "questions": [{"id": "Q1"}, {"id": "Q2"}]}],
    }
    data.update(extra)
    return data


def _problems(data: Any) -> list[tuple[str, str]]:
    return [(problem.path, problem.message) for problem in validate_spec(data)]


def _write(tmp_path: Path, text: str, name: str = "spec.yaml") -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


# ---- Schema and example -----------------------------------------------------------


def test_the_schema_is_a_valid_draft_2020_12_schema() -> None:
    jsonschema.Draft202012Validator.check_schema(spec_schema())


def test_the_example_is_valid_in_yaml_and_json() -> None:
    from_yaml = load_spec(EXAMPLES / "pet-survey.spec.yaml")
    from_json = load_spec(EXAMPLES / "pet-survey.spec.json")
    assert from_yaml == from_json
    assert from_yaml.name == "pet-survey"
    assert [module.id for module in from_yaml.modules] == [
        "household",
        "pets",
        "visits",
    ]
    kind = from_yaml.module("pets").questions[0]
    assert kind.module == "pets"
    assert kind.domain == DomainSpec(
        "code",
        codes={
            "1": {"en": "Dog", "fr": "Chien"},
            "2": {"en": "Cat", "fr": "Chat"},
            "3": {"en": "Bird", "fr": "Oiseau"},
        },
        code_list="Species",
    )
    age = from_yaml.module("pets").questions[2]
    assert age.domain is not None
    assert (age.domain.minimum, age.domain.maximum) == (Decimal(0), Decimal(40))
    assert from_yaml.blaise.empty == "EMPTY"
    assert [question.id for question in from_yaml.questions] == [
        "PetCount",
        "PetKind",
        "PetName",
        "PetAge",
        "VisitDate",
    ]


def test_the_example_text_is_what_the_files_hold() -> None:
    assert example_spec() == (EXAMPLES / "pet-survey.spec.yaml").read_text("utf-8")
    assert json.loads(example_spec("json"))["spec"] == "pet-survey"
    with pytest.raises(ValueError, match="yaml or json"):
        example_spec("toml")


# ---- The strict YAML reader ------------------------------------------------------


def test_a_key_given_twice_is_an_error(tmp_path: Path) -> None:
    path = _write(tmp_path, "spec: a\nmodules: []\nspec: b\n")
    with pytest.raises(SpecError, match="line 3: the key 'spec' is given twice"):
        load_spec(path)


def test_a_key_given_twice_in_json_is_an_error(tmp_path: Path) -> None:
    path = _write(tmp_path, '{"spec": "a", "spec": "b"}', "spec.json")
    with pytest.raises(SpecError, match="the key 'spec' is given twice"):
        load_spec(path)


def test_code_values_keep_their_leading_zeros(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "spec: s\nmodules:\n  - id: m\n    questions:\n"
        "      - id: Q\n        domain: {code: {values: {01: Yes, 2.50: No}}}\n",
    )
    (question,) = load_spec(path).questions
    assert question.domain is not None and question.domain.codes == {
        "01": {"": "Yes"},
        "2.50": {"": "No"},
    }


@pytest.mark.parametrize(
    ("text", "problem"),
    [
        ("required: no", ("modules[0].required", "'no' is not of type 'boolean'")),
        ("required: yes", ("modules[0].required", "'yes' is not of type 'boolean'")),
        ("required: On", ("modules[0].required", "'On' is not of type 'boolean'")),
        (
            "gate_scope: 2024-01-02",
            ("modules[0].gate_scope", "'2024-01-02' is not one of ['module', 'page']"),
        ),
    ],
)
def test_yaml_1_1_scalars_stay_strings(
    tmp_path: Path, text: str, problem: tuple[str, str]
) -> None:
    path = _write(tmp_path, f"spec: s\nmodules:\n  - id: m\n    {text}\n")
    with pytest.raises(SpecError) as caught:
        load_spec(path)
    assert [(p.path, p.message) for p in caught.value.problems] == [problem]


def test_true_false_and_numbers_still_read(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "spec: s\nmodules:\n  - id: m\n    required: false\n    questions:\n"
        "      - id: Q\n        domain: {numeric: {min: -1.5, max: 1e3, decimals: 0}}\n",
    )
    spec = load_spec(path)
    assert spec.modules[0].required is False
    (question,) = spec.questions
    assert question.domain is not None
    assert (question.domain.minimum, question.domain.maximum) == (
        Decimal("-1.5"),
        Decimal("1000.0"),
    )


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("spec: [unclosed\n", "expected ',' or ']'"),
        ("? [a, b]\n: c\n", "line 1: a key must be a plain value"),
    ],
)
def test_yaml_that_does_not_read(tmp_path: Path, text: str, message: str) -> None:
    with pytest.raises(SpecError, match=message.replace("[", r"\[")):
        load_spec(_write(tmp_path, text))


def test_json_that_does_not_read(tmp_path: Path) -> None:
    with pytest.raises(SpecError, match="Expecting property name"):
        load_spec(_write(tmp_path, "{", "spec.json"))


# ---- Checks ------------------------------------------------------------------------


def test_the_schema_reports_every_problem_with_its_path() -> None:
    data = _minimal(languages=["en", "not a tag"], extra=1)
    data["modules"][0]["questions"][0]["domain"] = {"numeric": {"decimals": -1}}
    # In the order written: spec, modules, then languages and extra.
    assert _problems(data) == [
        ("", "Additional properties are not allowed ('extra' was unexpected)"),
        (
            "modules[0].questions[0].domain.numeric.decimals",
            "-1 is less than the minimum of 0",
        ),
        (
            "languages[1]",
            "'not a tag' does not match '^[A-Za-z]{2,8}(-[A-Za-z0-9]{1,8})*$'",
        ),
    ]


def test_a_code_domain_names_values_or_a_list() -> None:
    data = _minimal()
    data["modules"][0]["questions"][0]["domain"] = {"code": {}}
    ((path, message),) = _problems(data)
    assert path == "modules[0].questions[0].domain.code"
    assert "'values' is a required property" in message


def test_the_whole_spec_must_be_a_mapping() -> None:
    assert _problems([1]) == [("", "[1] is not of type 'object'")]


@pytest.mark.parametrize(
    ("change", "problem"),
    [
        (
            lambda d: d["modules"][0].update(gate="Q1 >"),
            (
                "modules[0].gate",
                "Expected a value, found end of the expression at column 5: Q1 >",
            ),
        ),
        (
            lambda d: d["modules"][0]["questions"][1].update(gate="Other = 1"),
            (
                "modules[0].questions[1].gate",
                "'Other' is not a question or variable of the spec",
            ),
        ),
        (
            lambda d: d["modules"][0]["questions"][0].update(
                domain={"code": {"list": "Nope"}}
            ),
            (
                "modules[0].questions[0].domain.code.list",
                "there is no code list 'Nope'",
            ),
        ),
        (
            lambda d: d["modules"].append({"id": "m"}),
            ("modules[1].id", "the module 'm' is listed twice"),
        ),
        (
            lambda d: d["modules"].append({"id": "n", "questions": [{"id": "Q1"}]}),
            ("modules[1].questions[0].id", "'Q1' is also at modules[0].questions[0]"),
        ),
        (
            lambda d: d["modules"][0].update(statements=["Intro", "Intro"]),
            ("modules[0].statements[1]", "'Intro' is also at modules[0].statements[0]"),
        ),
        (
            lambda d: d.update(
                edits=[{"id": "e", "when": "Q1 > 1"}, {"id": "e", "when": "Q2 > 1"}]
            ),
            ("edits[1].id", "the edit 'e' is listed twice"),
        ),
        (
            lambda d: d.update(edits=[{"id": "e", "when": "Q1 > 1", "module": "x"}]),
            ("edits[0].module", "there is no module 'x'"),
        ),
        (
            lambda d: d.update(edits=[{"id": "e", "when": "Q9 > 1"}]),
            ("edits[0].when", "'Q9' is not a question or variable of the spec"),
        ),
        (
            lambda d: d.update(
                imported_variables=[{"name": "V"}], derived_variables=[{"name": "V"}]
            ),
            ("derived_variables[0].name", "'V' is declared twice"),
        ),
        (
            lambda d: d.update(imported_variables=[{"name": "Q1"}]),
            ("modules[0].questions[0].id", "'Q1' is also a variable"),
        ),
        (
            lambda d: d["modules"][0]["questions"][0].update(
                domain={"numeric": {"min": 5, "max": 1}}
            ),
            ("modules[0].questions[0].domain.numeric", "min is greater than max"),
        ),
        (
            lambda d: d["modules"][0]["questions"][0].update(
                domain={"text": {"min_length": 5, "max_length": 1}}
            ),
            (
                "modules[0].questions[0].domain.text",
                "min_length is greater than max_length",
            ),
        ),
        (
            lambda d: d.update(severities={"spec.nope": "error"}),
            ("severities.spec.nope", "there is no rule 'spec.nope'"),
        ),
        (
            lambda d: d.update(
                languages=["en"], code_lists={"L": {"values": {"1": {"de": "Hund"}}}}
            ),
            ("code_lists.L.values.1", "'de' is not one of the spec's languages"),
        ),
        (
            lambda d: (
                d.update(languages=["en"]),
                d["modules"][0]["questions"][0].update(
                    domain={"code": {"values": {"1": {"fr": "Chien"}}}}
                ),
            ),
            (
                "modules[0].questions[0].domain.code.values.1",
                "'fr' is not one of the spec's languages",
            ),
        ),
        (
            lambda d: d.update(
                languages=["en"],
                edits=[{"id": "e", "when": "Q1 > 1", "message": {"fr": "Non"}}],
            ),
            ("edits[0].message", "'fr' is not one of the spec's languages"),
        ),
    ],
)
def test_checks_of_the_spec_against_itself(
    change: Any, problem: tuple[str, str]
) -> None:
    data = _minimal()
    change(data)
    assert _problems(data) == [problem]


def test_variables_can_be_named_in_gates() -> None:
    data = _minimal(imported_variables=[{"name": "OwnerName", "type": "text"}])
    data["modules"][0]["gate"] = "answered(OwnerName)"
    assert _problems(data) == []


def test_a_spec_error_lists_every_problem() -> None:
    data = _minimal()
    data["modules"][0]["gate"] = "X > 1 and Y > 1"
    with pytest.raises(SpecError) as caught:
        spec_from_data(data, source="s.yaml")
    assert str(caught.value) == (
        "s.yaml: 2 problems:\n"
        "  modules[0].gate: 'X' is not a question or variable of the spec\n"
        "  modules[0].gate: 'Y' is not a question or variable of the spec"
    )
    data["modules"][0]["gate"] = "X > 1"
    with pytest.raises(SpecError) as single:
        spec_from_data(data)
    assert str(single.value) == (
        "modules[0].gate: 'X' is not a question or variable of the spec"
    )
    assert str(model.SpecProblem("", "bad")) == "spec: bad"


# ---- The model ---------------------------------------------------------------------


def test_the_model_carries_every_part() -> None:
    data = _minimal(
        version="2",
        description="d",
        instrument="Pet instrument",
        languages=["en", "fr"],
        blaise={
            "empty": "E",
            "refused": "R",
            "today": "T",
            "date": "D({year},{month},{day})",
        },
        match={
            "question_id": ["item_name"],
            "module_depth": 2,
            "edits": {"attribute": "kind", "value": "Edit", "id": "user_id"},
            "lookup_types": {"Text": "text"},
        },
        severities={"spec.module.extra": "error"},
        imported_variables=[
            {"name": "V", "type": "text", "source": "register", "values": [1, "a"]}
        ],
        edits=[
            {"id": "e", "when": "Q1 > 1", "message": "Too many", "severity": "warning"}
        ],
    )
    data["modules"][0].update(gate="Q2 = 1", gate_scope="page", statements=["Intro"])
    data["modules"][0]["questions"][0].update(
        gate="Q2 > 0",
        domain={"code": {"values": {"1": "Dog", "2": {"en": "Cat", "fr": "Chat"}}}},
    )
    data["modules"][0]["questions"][1].update(domain={"date": {"type": "Date"}})
    spec = spec_from_data(data)
    assert (spec.version, spec.description, spec.instrument) == (
        "2",
        "d",
        "Pet instrument",
    )
    assert spec.blaise.date == "D({year},{month},{day})"
    assert spec.match.question_id == ("item_name",)
    assert spec.match.statement_id == ("construct_name", "label", "user_id")
    assert spec.match.module_depth == 2
    assert spec.match.edits == model.EditMatch("kind", "Edit", "user_id")
    assert spec.match.lookup_types == {"Text": "text"}
    assert spec.severity("spec.module.extra") == "error"
    assert spec.severity("spec.item.extra") == RULE_SEVERITIES["spec.item.extra"]
    (variable,) = spec.imported_variables
    assert (variable.name, variable.type, variable.source, variable.values) == (
        "V",
        "text",
        "register",
        ("1", "a"),
    )
    module = spec.modules[0]
    assert (module.gate_text, module.gate_scope, module.statements) == (
        "Q2 = 1",
        "page",
        ("Intro",),
    )
    first, second = module.questions
    assert first.gate_text == "Q2 > 0"
    assert first.domain is not None
    # A label without a language is in the first of the spec's languages.
    assert first.domain.codes == {"1": {"en": "Dog"}, "2": {"en": "Cat", "fr": "Chat"}}
    assert second.domain == DomainSpec("date", date_type="Date")
    (edit,) = spec.edits
    assert (edit.when_text, edit.message, edit.severity) == (
        "Q1 > 1",
        {"": "Too many"},
        "warning",
    )
    with pytest.raises(KeyError):
        spec.module("nope")


def test_a_missing_file_is_an_os_error(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        load_spec(tmp_path / "nope.yaml")


# ---- Without the extra ------------------------------------------------------------


@pytest.mark.parametrize("module", ["yaml", "jsonschema"])
def test_without_the_extra_the_error_says_what_to_install(
    monkeypatch: pytest.MonkeyPatch, module: str
) -> None:
    monkeypatch.setitem(sys.modules, module, None)
    with pytest.raises(SpecDependencyError, match=r'pip install "ddi-l\[spec\]"'):
        load_spec(EXAMPLES / "pet-survey.spec.yaml")


# ---- ddi spec ------------------------------------------------------------------------


def test_ddi_spec_validate(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    example = EXAMPLES / "pet-survey.spec.yaml"
    assert cli.main(["spec", "validate", str(example)]) == 0
    assert "the spec 'pet-survey' is valid: 3 module(s), 5 question(s), 1 edit(s)." in (
        capsys.readouterr().out
    )
    bad = _write(tmp_path, "spec: s\nmodules:\n  - id: m\n    gate: X > 1\n")
    assert cli.main(["spec", "validate", str(bad)]) == 1
    assert capsys.readouterr().err == (
        f"{bad}: modules[0].gate: 'X' is not a question or variable of the spec\n"
    )


def test_ddi_spec_schema_and_example(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["spec", "schema"]) == 0
    assert json.loads(capsys.readouterr().out) == spec_schema()
    target = tmp_path / "example.json"
    assert cli.main(["spec", "example", "--format", "json", "-o", str(target)]) == 0
    assert target.read_text("utf-8") == example_spec("json")
    assert cli.main(["spec", "example"]) == 0
    assert capsys.readouterr().out == example_spec()


def test_ddi_spec_without_a_subcommand_prints_help(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["spec"]) == 1
    assert "validate" in capsys.readouterr().out


@pytest.mark.parametrize("command", [["validate", "x.yaml"], ["schema"], ["example"]])
def test_ddi_spec_without_the_extra_prints_the_hint(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    command: list[str],
) -> None:
    monkeypatch.setitem(sys.modules, "yaml", None)
    assert cli.main(["spec", *command]) == 1
    assert capsys.readouterr().err == (
        'Error: this command needs the spec extra: pip install "ddi-l[spec]"\n'
    )


def test_a_question_without_a_domain_has_none() -> None:
    spec = spec_from_data(_minimal())
    assert [question.domain for question in spec.questions] == [None, None]


# ---- Review fixes -----------------------------------------------------------------------


def test_whole_numbers_written_as_floats_are_integers(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "spec: s\nmatch: {module_depth: 2.0}\nmodules:\n  - id: m\n    questions:\n"
        "      - id: Q\n        domain: {numeric: {decimals: 0.0}}\n"
        "      - id: T\n        domain: {text: {min_length: 1e0, max_length: 4e1}}\n",
    )
    spec = load_spec(path)
    numeric, text = (question.domain for question in spec.questions)
    assert numeric is not None and text is not None
    assert numeric.decimals == 0 and type(numeric.decimals) is int
    assert (text.min_length, text.max_length) == (1, 40)
    assert type(text.max_length) is int
    assert spec.match.module_depth == 2 and type(spec.match.module_depth) is int


def test_non_finite_numbers_are_refused(tmp_path: Path) -> None:
    with pytest.raises(SpecError, match="NaN, Infinity and -Infinity are not JSON"):
        load_spec(
            _write(
                tmp_path,
                '{"spec": "s", "modules": [{"id": "m", "questions": [{"id": "Q",'
                ' "domain": {"numeric": {"max": Infinity}}}]}]}',
                "spec.json",
            )
        )
    data = _minimal()
    data["modules"][0]["questions"][0]["domain"] = {
        "numeric": {"min": float("-inf"), "max": float("nan")}
    }
    assert _problems(data) == [
        ("modules[0].questions[0].domain.numeric.min", "-inf is not a finite number"),
        ("modules[0].questions[0].domain.numeric.max", "nan is not a finite number"),
    ]


def test_a_date_template_that_cannot_read_back_is_a_problem() -> None:
    assert _problems(_minimal(blaise={"date": "{year}{month:02d}{day:02d}"})) == [
        (
            "blaise.date",
            "The date template needs text before its first field that does not "
            "end with a digit, so a number is never read as a date.",
        )
    ]


def test_a_spec_that_is_not_utf_8_is_a_spec_error(tmp_path: Path) -> None:
    path = tmp_path / "spec.yaml"
    path.write_bytes("spec: café\n".encode("latin-1"))
    with pytest.raises(SpecError, match="not UTF-8"):
        load_spec(path)


def test_a_gate_nested_too_deeply_is_a_problem() -> None:
    gate = "(" * 400 + "Q1 > 1" + ")" * 400
    data = _minimal()
    data["modules"][0]["gate"] = gate
    ((path, message),) = _problems(data)
    assert path == "modules[0].gate"
    assert message.startswith("The expression is nested too deeply")
    data["modules"][0]["gate"] = "not " * 400 + "Q1 > 1"
    assert _problems(data)[0][1].startswith("The expression is nested too deeply")


def test_problems_are_in_document_order() -> None:
    data = _minimal()
    data["modules"] = [
        {"id": f"m{n}", "questions": [{"id": f"Q{n}", "extra": 1}]} for n in range(12)
    ]
    paths = [path for path, _ in _problems(data)]
    assert paths == [f"modules[{n}].questions[0]" for n in range(12)]


def test_problems_follow_the_file_whatever_their_kind() -> None:
    # A oneOf error (a code label of the wrong type) and a plain one, and
    # top-level keys in the order written, not alphabetical.
    data = {"spec": 5, "version": 2, "modules": _minimal()["modules"] * 2}
    data["modules"] = [
        {"id": "m0", "questions": [{"id": "Q0", "extra": 1}]},
        {
            "id": "m1",
            "questions": [{"id": "Q1", "domain": {"code": {"values": {"1": 5}}}}],
        },
    ]
    paths = [path for path, _ in _problems(data)]
    assert paths == [
        "spec",
        "version",
        "modules[0].questions[0]",
        "modules[1].questions[0].domain.code.values.1",
    ]


def test_a_plain_double_less_than_is_text(tmp_path: Path) -> None:
    text = "spec: s\ndescription: <<\nmodules:\n  - id: m\n    questions: [{id: Q}]\n"
    assert load_spec(_write(tmp_path, text)).description == "<<"


def test_the_byte_of_a_decoding_error_counts_a_byte_order_mark(tmp_path: Path) -> None:
    path = tmp_path / "spec.yaml"
    data = b"\xef\xbb\xbfspec: caf\xe9\n"
    path.write_bytes(data)
    offset = data.index(b"\xe9")
    with pytest.raises(SpecError, match=f"byte {offset}:"):
        load_spec(path)


def test_merge_keys_are_refused(tmp_path: Path) -> None:
    text = "base: &b {id: m}\nspec: s\nmodules:\n  - <<: *b\n    questions: [{id: Q}]\n"
    with pytest.raises(SpecError, match="merge keys are not YAML 1.2"):
        load_spec(_write(tmp_path, text))


def test_an_equals_sign_is_a_string(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "spec: s\nmodules:\n  - id: m\n    questions:\n      - id: Q\n"
        "        domain: {code: {values: {1: =}}}\n",
    )
    (question,) = load_spec(path).questions
    assert question.domain is not None and question.domain.codes == {"1": {"": "="}}


def test_a_text_by_language_points_at_the_bad_tag() -> None:
    data = _minimal()
    data["modules"][0]["questions"][0]["domain"] = {
        "code": {"values": {"1": {"en_CA": "Dog"}}}
    }
    assert _problems(data) == [
        (
            "modules[0].questions[0].domain.code.values.1",
            "'en_CA' does not match '^[A-Za-z]{2,8}(-[A-Za-z0-9]{1,8})*$'",
        )
    ]
