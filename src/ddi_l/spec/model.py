"""Questionnaire specs: read, check and hold one.

A spec is a YAML or JSON file (see ``spec.schema.json`` next to this module,
and the example ``examples/pet-survey.spec.yaml``). `load_spec` reads
one, checks it against the schema and then against itself (unique ids,
expressions that parse and name only what the spec declares, code lists that
exist), and returns a `Spec`.

YAML is read strictly: a key given twice is an error, ``01`` stays the string
``"01"`` (a code, not the number 1), only ``true`` and ``false`` are booleans
(``yes``, ``no``, ``on`` and ``off`` are strings) and dates stay strings.

Reading a spec needs the ``spec`` extra: ``pip install "ddi-l[spec]"``.
"""

from __future__ import annotations

import codecs
import json
import math
import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from importlib import resources
from pathlib import Path
from typing import Any

from .compile import BlaiseDialect, _date_fields
from .expression import Expression, ExpressionError, identifiers, parse_expression
from .rules import RULE_SEVERITIES

__all__ = [
    "EXTRA_HINT",
    "DomainSpec",
    "EditMatch",
    "EditSpec",
    "MatchOptions",
    "ModuleSpec",
    "QuestionSpec",
    "Spec",
    "SpecDependencyError",
    "SpecError",
    "SpecProblem",
    "VariableSpec",
    "example_spec",
    "load_spec",
    "spec_from_data",
    "spec_schema",
    "validate_spec",
]

EXTRA_HINT = 'pip install "ddi-l[spec]"'

QUESTION_ID_SOURCES = ("construct_alias", "item_name", "item_alias", "construct_name")
STATEMENT_ID_SOURCES = ("construct_name", "label", "user_id")
MODULE_ID_SOURCES = ("construct_name", "label", "user_id")


class SpecDependencyError(ImportError):
    """The ``spec`` extra is not installed."""

    def __init__(self, module: str) -> None:
        super().__init__(f"Reading a spec needs {module}: {EXTRA_HINT}")


@dataclass(frozen=True)
class SpecProblem:
    """One problem with a spec.

    Attributes:
        path: Where it is: ``modules[1].questions[0].gate``; ``""`` for the
            whole spec.
        message: What is wrong.
    """

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path or 'spec'}: {self.message}"


class SpecError(ValueError):
    """A spec that does not read, or does not pass its checks.

    Attributes:
        problems: Every problem found, in file order.
    """

    def __init__(
        self, problems: Sequence[SpecProblem], source: str | None = None
    ) -> None:
        self.problems = list(problems)
        self.source = source
        where = f"{source}: " if source else ""
        lines = [str(problem) for problem in self.problems]
        if len(lines) == 1:
            super().__init__(where + lines[0])
        else:
            listed = "\n  ".join(lines)
            super().__init__(f"{where}{len(lines)} problems:\n  {listed}")


# ---- The model ---------------------------------------------------------------


@dataclass(frozen=True)
class DomainSpec:
    """A question's expected response domain.

    Attributes:
        kind: ``code``, ``numeric``, ``text`` or ``date``.
        codes: For ``code``: each value and its label by language (``""``
            when the spec gives one label without a language).
        code_list: The ``code_lists`` entry ``codes`` came from, if any.
        minimum: Numeric lower bound.
        maximum: Numeric upper bound.
        min_inclusive: Whether ``minimum`` is allowed (default ``True``).
        max_inclusive: Whether ``maximum`` is allowed (default ``True``).
        decimals: Numeric decimal positions.
        min_length: Text minimum length.
        max_length: Text maximum length.
        date_type: The DDI ``DateTypeCode``.
    """

    kind: str
    codes: dict[str, dict[str, str]] | None = None
    code_list: str | None = None
    minimum: Decimal | None = None
    maximum: Decimal | None = None
    min_inclusive: bool = True
    max_inclusive: bool = True
    decimals: int | None = None
    min_length: int | None = None
    max_length: int | None = None
    date_type: str | None = None


@dataclass(frozen=True)
class QuestionSpec:
    """A question the instrument should ask.

    Attributes:
        id: Its id, found as `MatchOptions.question_id` says.
        module: The id of its module.
        domain: Its expected response domain, if the spec gives one.
        gate: The condition under which it is asked, besides its module's.
        gate_text: ``gate`` as written.
        path: Where it is in the spec.
    """

    id: str
    module: str
    domain: DomainSpec | None = None
    gate: Expression | None = None
    gate_text: str | None = None
    path: str = ""


@dataclass(frozen=True)
class ModuleSpec:
    """A module: a sequence of the instrument.

    Attributes:
        id: Its id, found as `MatchOptions.module_id` says.
        required: Whether the instrument must have it.
        gate: The condition under which the module runs.
        gate_text: ``gate`` as written.
        gate_scope: ``module`` (the gate wraps the module) or ``page`` (it
            wraps each page).
        statements: The ids of its statements.
        questions: Its questions, in order.
        path: Where it is in the spec.
    """

    id: str
    required: bool = True
    gate: Expression | None = None
    gate_text: str | None = None
    gate_scope: str = "module"
    statements: tuple[str, ...] = ()
    questions: tuple[QuestionSpec, ...] = ()
    path: str = ""


@dataclass(frozen=True)
class EditSpec:
    """An edit check.

    Attributes:
        id: Its id.
        when: The condition under which it fires.
        when_text: ``when`` as written.
        module: The module it belongs to, if the spec says.
        message: Its message, by language.
        severity: ``error``, ``warning`` or ``info``, if the spec says.
        path: Where it is in the spec.
    """

    id: str
    when: Expression
    when_text: str
    module: str | None = None
    message: dict[str, str] = field(default_factory=dict)
    severity: str | None = None
    path: str = ""


@dataclass(frozen=True)
class VariableSpec:
    """An imported or derived variable."""

    name: str
    type: str | None = None
    source: str | None = None
    values: tuple[str, ...] = ()
    path: str = ""


@dataclass(frozen=True)
class EditMatch:
    """How edit checks are stored: a user attribute marks them.

    Attributes:
        attribute: The ``r:AttributeKey`` that marks an edit check.
        value: Its ``r:AttributeValue`` on one.
        id: Where an edit check's id is: ``construct_name``, ``label`` or
            ``user_id``.
    """

    attribute: str
    value: str
    id: str


@dataclass(frozen=True)
class MatchOptions:
    """Where to find each spec id in an instrument.

    Each ``*_id`` lists the places an id may be, in order: the first place
    that holds it anywhere in the instrument is the one used.
    """

    question_id: tuple[str, ...] = QUESTION_ID_SOURCES
    statement_id: tuple[str, ...] = STATEMENT_ID_SOURCES
    module_id: tuple[str, ...] = MODULE_ID_SOURCES
    module_depth: int | None = None
    edits: EditMatch | None = None
    lookup_types: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Spec:
    """A questionnaire spec, checked."""

    name: str
    modules: tuple[ModuleSpec, ...]
    version: str | None = None
    description: str | None = None
    instrument: str | None = None
    languages: tuple[str, ...] = ()
    blaise: BlaiseDialect = field(default_factory=BlaiseDialect)
    match: MatchOptions = field(default_factory=MatchOptions)
    severities: dict[str, str] = field(default_factory=dict)
    code_lists: dict[str, dict[str, dict[str, str]]] = field(default_factory=dict)
    imported_variables: tuple[VariableSpec, ...] = ()
    derived_variables: tuple[VariableSpec, ...] = ()
    edits: tuple[EditSpec, ...] = ()

    @property
    def questions(self) -> Iterator[QuestionSpec]:
        """Every question, module by module."""
        for module in self.modules:
            yield from module.questions

    def module(self, module_id: str) -> ModuleSpec:
        """The module with ``module_id``.

        Raises:
            KeyError: If the spec has no such module.
        """
        for module in self.modules:
            if module.id == module_id:
                return module
        raise KeyError(module_id)

    def severity(self, rule_id: str) -> str:
        """The severity of ``rule_id`` under this spec."""
        return self.severities.get(rule_id, RULE_SEVERITIES[rule_id])


# ---- Reading -----------------------------------------------------------------


def _yaml() -> Any:
    try:
        import yaml
    except ImportError:
        raise SpecDependencyError("PyYAML") from None
    return yaml


def _jsonschema() -> Any:
    try:
        import jsonschema
    except ImportError:
        raise SpecDependencyError("jsonschema") from None
    return jsonschema


# YAML 1.1 resolvers replaced (bool, int, float) or dropped (timestamp, and
# value, which made "=" a value of its own). merge stays, to refuse "<<".
_YAML_RESOLVED = (
    "tag:yaml.org,2002:bool",
    "tag:yaml.org,2002:int",
    "tag:yaml.org,2002:float",
    "tag:yaml.org,2002:timestamp",
    "tag:yaml.org,2002:value",
)


def _strict_loader() -> Any:
    """A ``SafeLoader`` reading scalars as YAML 1.2 does, refusing repeats."""
    yaml = _yaml()

    class StrictLoader(yaml.SafeLoader):  # type: ignore[name-defined]
        pass

    StrictLoader.yaml_implicit_resolvers = {
        first: [entry for entry in entries if entry[0] not in _YAML_RESOLVED]
        for first, entries in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }
    StrictLoader.add_implicit_resolver(
        "tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$"), list("tf")
    )
    StrictLoader.add_implicit_resolver(
        "tag:yaml.org,2002:int",
        re.compile(r"^-?(?:0|[1-9][0-9]*)$"),
        list("-0123456789"),
    )
    StrictLoader.add_implicit_resolver(
        "tag:yaml.org,2002:float",
        re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?$"),
        list("-0123456789"),
    )

    def mapping(loader: Any, node: Any) -> dict[str, Any]:
        for key_node, _ in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise _YamlProblem("merge keys are not YAML 1.2", key_node)
        result: dict[str, Any] = {}
        for key_node, value_node in node.value:
            if not isinstance(key_node, yaml.ScalarNode):
                raise _YamlProblem("a key must be a plain value", key_node)
            # The key as written: code values keep their leading zeros.
            key = key_node.value
            if key in result:
                raise _YamlProblem(f"the key {key!r} is given twice", key_node)
            result[key] = loader.construct_object(value_node, deep=True)
        return result

    StrictLoader.add_constructor("tag:yaml.org,2002:map", mapping)
    # "<<" stays resolved as merge so a merge key can be refused; as a value
    # it is the text "<<".
    StrictLoader.add_constructor(
        "tag:yaml.org,2002:merge",
        lambda loader, node: loader.construct_scalar(node),
    )
    return StrictLoader


class _YamlProblem(Exception):  # noqa: N818 - internal signal, never escapes
    def __init__(self, message: str, node: Any) -> None:
        super().__init__(message)
        self.line = node.start_mark.line + 1


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"the key {key!r} is given twice")
        result[key] = value
    return result


def _not_json(constant: str) -> Any:
    raise ValueError(f"{constant}: NaN, Infinity and -Infinity are not JSON")


def _read(path: Path) -> Any:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        # utf-8-sig counts from after a byte-order mark.
        start = error.start + (3 if data.startswith(codecs.BOM_UTF8) else 0)
        message = f"the file is not UTF-8 (byte {start}: {error.reason})"
        raise SpecError([SpecProblem("", message)], str(path)) from None
    if path.suffix.lower() == ".json":
        try:
            return json.loads(
                text, object_pairs_hook=_json_object, parse_constant=_not_json
            )
        except (json.JSONDecodeError, ValueError) as error:
            raise SpecError([SpecProblem("", str(error))], str(path)) from None
    yaml = _yaml()
    try:
        return yaml.load(text, Loader=_strict_loader())
    except _YamlProblem as problem:
        message = f"line {problem.line}: {problem}"
        raise SpecError([SpecProblem("", message)], str(path)) from None
    except yaml.YAMLError as error:
        raise SpecError([SpecProblem("", str(error))], str(path)) from None


def spec_schema() -> dict[str, Any]:
    """The JSON Schema a spec is checked against."""
    text = (
        resources.files(__package__)
        .joinpath("spec.schema.json")
        .read_text(encoding="utf-8")
    )
    schema: dict[str, Any] = json.loads(text)
    return schema


def example_spec(format: str = "yaml") -> str:
    """The example spec, the Pet survey, as YAML or JSON text.

    Raises:
        ValueError: For a format other than ``yaml`` or ``json``.
    """
    if format not in ("yaml", "json"):
        raise ValueError(f"format must be yaml or json, not {format!r}.")
    name = f"pet-survey.spec.{format}"
    return (
        resources.files(__package__)
        .joinpath("examples", name)
        .read_text(encoding="utf-8")
    )


def _path(parts: Sequence[str | int]) -> str:
    text = ""
    for part in parts:
        if isinstance(part, int):
            text += f"[{part}]"
        else:
            text += f".{part}" if text else str(part)
    return text


def validate_spec(data: Any) -> list[SpecProblem]:
    """Every problem with a spec's content, read from YAML or JSON.

    The schema first; the checks of the spec against itself run only when
    the schema passes.
    """
    jsonschema = _jsonschema()
    validator = jsonschema.Draft202012Validator(spec_schema())
    errors = sorted(
        (_reported(error) for error in validator.iter_errors(data)),
        key=lambda error: _document_order(data, error.absolute_path),
    )
    if errors:
        return [
            SpecProblem(_path(list(error.absolute_path)), str(error.message))
            for error in errors
        ]
    return list(_semantic_problems(data))


def _document_order(data: Any, path: Iterable[str | int]) -> list[int]:
    """Where ``path`` is in ``data``: its keys' positions, in the file's order.

    Mappings read from YAML or JSON keep their keys in the order written, so a
    key's position in its mapping is its place in the file.
    """
    order = []
    node = data
    for part in path:
        if isinstance(node, Mapping):
            keys = list(node)
            order.append(keys.index(part) if part in node else len(keys))
            node = node.get(part)
        elif isinstance(node, list) and isinstance(part, int):
            order.append(part)
            node = node[part] if part < len(node) else None
        else:
            order.append(0)
            node = None
    return order


def _reported(error: Any) -> Any:
    """The error to report: for a ``oneOf``, its most telling alternative.

    The alternative that went furthest into the value says the most; between
    equals, any but "is not of type" (the alternative of another type).
    """
    while error.validator == "oneOf" and error.context:
        error = max(
            error.context,
            key=lambda inner: (len(inner.absolute_path), inner.validator != "type"),
        )
    return error


def _text_by_language(value: Any) -> dict[str, str]:
    if isinstance(value, str):
        return {"": value}
    return {str(language): str(text) for language, text in value.items()}


def _semantic_problems(data: Mapping[str, Any]) -> Iterator[SpecProblem]:
    date = data.get("blaise", {}).get("date")
    if date is not None:
        try:
            _date_fields(date)
        except ValueError as error:
            yield SpecProblem("blaise.date", str(error))
    code_lists = data.get("code_lists", {})
    languages = set(data.get("languages", []))
    declared: set[str] = set()
    for kind in ("imported_variables", "derived_variables"):
        for index, variable in enumerate(data.get(kind, [])):
            name = variable["name"]
            if name in declared:
                yield SpecProblem(
                    f"{kind}[{index}].name", f"{name!r} is declared twice"
                )
            declared.add(name)
    seen_modules: set[str] = set()
    seen_items: dict[str, str] = {}
    for m, module in enumerate(data["modules"]):
        if module["id"] in seen_modules:
            yield SpecProblem(
                f"modules[{m}].id", f"the module {module['id']!r} is listed twice"
            )
        seen_modules.add(module["id"])
        for s, statement in enumerate(module.get("statements", [])):
            where = f"modules[{m}].statements[{s}]"
            if statement in seen_items:
                yield SpecProblem(
                    where, f"{statement!r} is also at {seen_items[statement]}"
                )
            seen_items.setdefault(statement, where)
        for q, question in enumerate(module.get("questions", [])):
            where = f"modules[{m}].questions[{q}]"
            if question["id"] in seen_items:
                yield SpecProblem(
                    f"{where}.id",
                    f"{question['id']!r} is also at {seen_items[question['id']]}",
                )
            seen_items.setdefault(question["id"], where)
            if question["id"] in declared:
                yield SpecProblem(
                    f"{where}.id", f"{question['id']!r} is also a variable"
                )
            yield from _domain_problems(
                question.get("domain"), f"{where}.domain", code_lists, languages
            )
    questions = {
        question["id"]
        for module in data["modules"]
        for question in module.get("questions", [])
    }
    names = questions | declared
    for m, module in enumerate(data["modules"]):
        if "gate" in module:
            yield from _expression_problems(module["gate"], f"modules[{m}].gate", names)
        for q, question in enumerate(module.get("questions", [])):
            if "gate" in question:
                yield from _expression_problems(
                    question["gate"], f"modules[{m}].questions[{q}].gate", names
                )
    seen_edits: set[str] = set()
    for e, edit in enumerate(data.get("edits", [])):
        if edit["id"] in seen_edits:
            yield SpecProblem(
                f"edits[{e}].id", f"the edit {edit['id']!r} is listed twice"
            )
        seen_edits.add(edit["id"])
        yield from _expression_problems(edit["when"], f"edits[{e}].when", names)
        if "module" in edit and edit["module"] not in seen_modules:
            yield SpecProblem(
                f"edits[{e}].module", f"there is no module {edit['module']!r}"
            )
        if "message" in edit:
            yield from _language_problems(
                _text_by_language(edit["message"]), f"edits[{e}].message", languages
            )
    for name, code_list in code_lists.items():
        for value, label in code_list["values"].items():
            yield from _language_problems(
                _text_by_language(label),
                f"code_lists.{name}.values.{value}",
                languages,
            )
    for rule_id in data.get("severities", {}):
        if rule_id not in RULE_SEVERITIES:
            yield SpecProblem(f"severities.{rule_id}", f"there is no rule {rule_id!r}")


def _language_problems(
    texts: Mapping[str, str], where: str, languages: set[str]
) -> Iterator[SpecProblem]:
    for language in texts:
        if language and languages and language not in languages:
            yield SpecProblem(where, f"{language!r} is not one of the spec's languages")


def _domain_problems(
    domain: Mapping[str, Any] | None,
    where: str,
    code_lists: Mapping[str, Any],
    languages: set[str],
) -> Iterator[SpecProblem]:
    if domain is None:
        return
    if "code" in domain:
        code = domain["code"]
        if "list" in code and code["list"] not in code_lists:
            yield SpecProblem(
                f"{where}.code.list", f"there is no code list {code['list']!r}"
            )
        for value, label in code.get("values", {}).items():
            yield from _language_problems(
                _text_by_language(label), f"{where}.code.values.{value}", languages
            )
    numeric = domain.get("numeric", {})
    finite = True
    for bound in ("min", "max"):
        value = numeric.get(bound)
        if isinstance(value, float) and not math.isfinite(value):
            finite = False
            yield SpecProblem(
                f"{where}.numeric.{bound}", f"{value} is not a finite number"
            )
    if (
        finite
        and "min" in numeric
        and "max" in numeric
        and numeric["min"] > numeric["max"]
    ):
        yield SpecProblem(f"{where}.numeric", "min is greater than max")
    text = domain.get("text", {})
    if (
        "min_length" in text
        and "max_length" in text
        and text["min_length"] > text["max_length"]
    ):
        yield SpecProblem(f"{where}.text", "min_length is greater than max_length")


def _expression_problems(
    text: str, where: str, names: set[str]
) -> Iterator[SpecProblem]:
    try:
        expression = parse_expression(text)
    except ExpressionError as error:
        yield SpecProblem(where, f"{error.reason} at column {error.column}: {text}")
        return
    for name in identifiers(expression):
        if name not in names:
            yield SpecProblem(
                where, f"{name!r} is not a question or variable of the spec"
            )


# ---- Building the model -------------------------------------------------------


def _decimal(value: Any) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _whole(value: Any) -> Any:
    """A whole number written as a float (``4e1``, ``0.0``) as an ``int``."""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _domain(
    data: Mapping[str, Any] | None,
    code_lists: Mapping[str, Mapping[str, Any]],
    first_language: str,
) -> DomainSpec | None:
    if data is None:
        return None
    ((kind, options),) = data.items()
    if kind == "code":
        values = options.get("values")
        list_name = options.get("list")
        if list_name is not None:
            values = code_lists[list_name]["values"]
        codes = {}
        for value, label in values.items():
            texts = _text_by_language(label)
            if "" in texts and first_language:
                texts = {first_language: texts[""]}
            codes[str(value)] = texts
        return DomainSpec("code", codes=codes, code_list=list_name)
    if kind == "numeric":
        return DomainSpec(
            "numeric",
            minimum=_decimal(options.get("min")),
            maximum=_decimal(options.get("max")),
            min_inclusive=options.get("min_inclusive", True),
            max_inclusive=options.get("max_inclusive", True),
            decimals=_whole(options.get("decimals")),
        )
    if kind == "text":
        return DomainSpec(
            "text",
            min_length=_whole(options.get("min_length")),
            max_length=_whole(options.get("max_length")),
        )
    return DomainSpec("date", date_type=options.get("type"))


def _variables(
    items: Sequence[Mapping[str, Any]], kind: str
) -> tuple[VariableSpec, ...]:
    return tuple(
        VariableSpec(
            name=item["name"],
            type=item.get("type"),
            source=item.get("source"),
            values=tuple(str(value) for value in item.get("values", ())),
            path=f"{kind}[{index}]",
        )
        for index, item in enumerate(items)
    )


def _match(data: Mapping[str, Any]) -> MatchOptions:
    edits = data.get("edits")
    return MatchOptions(
        question_id=tuple(data.get("question_id", QUESTION_ID_SOURCES)),
        statement_id=tuple(data.get("statement_id", STATEMENT_ID_SOURCES)),
        module_id=tuple(data.get("module_id", MODULE_ID_SOURCES)),
        module_depth=_whole(data.get("module_depth")),
        edits=None
        if edits is None
        else EditMatch(edits["attribute"], edits["value"], edits["id"]),
        lookup_types=dict(data.get("lookup_types", {})),
    )


def spec_from_data(data: Any, *, source: str | None = None) -> Spec:
    """Check a spec's content (read from YAML or JSON) and build the model.

    Raises:
        SpecError: If the content does not pass the checks.
        SpecDependencyError: Without the ``spec`` extra.
    """
    problems = validate_spec(data)
    if problems:
        raise SpecError(problems, source)
    languages = tuple(data.get("languages", ()))
    first_language = languages[0] if languages else ""
    code_lists = data.get("code_lists", {})
    lists = {
        name: {
            str(value): _text_by_language(label)
            for value, label in entry["values"].items()
        }
        for name, entry in code_lists.items()
    }
    modules = []
    for m, module in enumerate(data["modules"]):
        questions = tuple(
            QuestionSpec(
                id=question["id"],
                module=module["id"],
                domain=_domain(question.get("domain"), code_lists, first_language),
                gate=parse_expression(question["gate"]) if "gate" in question else None,
                gate_text=question.get("gate"),
                path=f"modules[{m}].questions[{q}]",
            )
            for q, question in enumerate(module.get("questions", []))
        )
        modules.append(
            ModuleSpec(
                id=module["id"],
                required=module.get("required", True),
                gate=parse_expression(module["gate"]) if "gate" in module else None,
                gate_text=module.get("gate"),
                gate_scope=module.get("gate_scope", "module"),
                statements=tuple(module.get("statements", ())),
                questions=questions,
                path=f"modules[{m}]",
            )
        )
    edits = tuple(
        EditSpec(
            id=edit["id"],
            when=parse_expression(edit["when"]),
            when_text=edit["when"],
            module=edit.get("module"),
            message=_text_by_language(edit.get("message", {})),
            severity=edit.get("severity"),
            path=f"edits[{e}]",
        )
        for e, edit in enumerate(data.get("edits", []))
    )
    blaise = data.get("blaise", {})
    return Spec(
        name=data["spec"],
        modules=tuple(modules),
        version=data.get("version"),
        description=data.get("description"),
        instrument=data.get("instrument"),
        languages=languages,
        blaise=BlaiseDialect(
            empty=blaise.get("empty"),
            refused=blaise.get("refused"),
            today=blaise.get("today"),
            date=blaise.get("date"),
        ),
        match=_match(data.get("match", {})),
        severities=dict(data.get("severities", {})),
        code_lists=lists,
        imported_variables=_variables(
            data.get("imported_variables", []), "imported_variables"
        ),
        derived_variables=_variables(
            data.get("derived_variables", []), "derived_variables"
        ),
        edits=edits,
    )


def load_spec(path: str | Path) -> Spec:
    """Read and check the spec in ``path`` (``.json``; YAML otherwise).

    Raises:
        SpecError: If the file does not read, or its content does not pass
            the checks; every problem is listed with where it is.
        SpecDependencyError: Without the ``spec`` extra.
        OSError: If the file cannot be read.
    """
    path = Path(path)
    return spec_from_data(_read(path), source=str(path))
