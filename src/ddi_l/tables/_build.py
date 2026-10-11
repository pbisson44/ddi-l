"""Turn the rows of a metadata workbook into typed DDI items.

Three passes. The first gives every row of every item table its identity, so
a reference can point at any row, in any table. The second creates each
item's element. The third fills the elements in; a row may add to an item of
another table (a question joins its group), which is why elements stay open
until the end, when each becomes its typed model.

Every problem is collected with its file, row and column, and reported
together: a workbook with ten typos fails once, listing ten fixes.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .._etree import Element
from ..models.base import MaintainableBase
from . import _more
from ._common import (
    Context,
    Entry,
    Identity,
    as_response_domain,
    boolean,
    cc,
    check_required_columns,
    d,
    el,
    entry_of,
    item_element,
    literal_text,
    literal_texts,
    lookup,
    lp,
    multilingual,
    name_element,
    r,
    ref,
    representation,
    reserve,
    single,
    strings,
    typed,
    values,
)
from ._read import RawTable, Row, TableProblem
from ._spec import AUDIENCE, LANGUAGE_TAG, SETTING_NAMES, TABLES, audience_language

# Table -> the element its rows become. ``flow`` rows depend on their type.
ITEM_TAGS: dict[str, str] = {
    "studies": _more.s("StudyUnit"),
    "groups": _more.g("Group"),
    "organizations": _more.a("Organization"),
    "individuals": _more.a("Individual"),
    "concepts": cc("Concept"),
    "universes": cc("Universe"),
    "unit_types": cc("UnitType"),
    "conceptual_variables": cc("ConceptualVariable"),
    "represented_variables": lp("RepresentedVariable"),
    "code_lists": lp("CodeList"),
    "instructions": d("Instruction"),
    "questions": d("QuestionItem"),
    "question_grids": d("QuestionGrid"),
    "question_blocks": d("QuestionBlock"),
    "question_groups": d("QuestionGroup"),
    "instruments": d("Instrument"),
    "variables": lp("Variable"),
    "variable_groups": lp("VariableGroup"),
    "datasets": _more.p("PhysicalInstance"),
    "ncubes": lp("NCube"),
    "methodologies": d("Methodology"),
    "processing_events": d("ProcessingEvent"),
    "quality_statements": r("QualityStatement"),
}

# Tables whose items a study document (``to_study``) has no place for.
FRAGMENT_ONLY = (
    "studies",
    "groups",
    "organizations",
    "individuals",
    "variable_groups",
    "processing_events",
    "quality_statements",
    "comparisons",
)


@dataclass
class Built:
    """The items a workbook describes, by the table they come from."""

    agency: str
    version: str
    language: str
    # table -> items, in row order; items a table implies (the categories of
    # ``codes``, the sequences of ``flow``) are listed under it
    tables: dict[str, list[MaintainableBase]] = field(default_factory=dict)
    keys: dict[str, dict[str, MaintainableBase]] = field(default_factory=dict)


def read_settings(
    tables: dict[str, RawTable],
    *,
    agency: str | None,
    version: str | None,
    language: str | None,
    problems: list[TableProblem],
) -> tuple[str, str, str]:
    """The agency, version and names language, from arguments or settings."""
    found: dict[str, str] = {}
    raw = tables.get("settings")
    if raw is not None:
        for row in raw.rows:
            key = row.cells.get("setting", "").strip().lower()
            value = row.cells.get("value", "")
            if key not in SETTING_NAMES:
                problems.append(
                    TableProblem(
                        raw.where(row, "setting"),
                        f"unknown setting {key!r}; expected "
                        + ", ".join(SETTING_NAMES),
                    )
                )
            elif not value:
                problems.append(TableProblem(raw.where(row, "value"), "is empty"))
            else:
                found[key] = value
    resolved = {
        "agency": agency or found.get("agency"),
        "version": version or found.get("version") or SETTING_NAMES["version"][1],
        "language": language or found.get("language") or SETTING_NAMES["language"][1],
    }
    if not resolved["agency"]:
        problems.append(
            TableProblem(
                "settings",
                "no agency: add a row `agency` to settings, or pass agency=",
            )
        )
    if resolved["language"] and not LANGUAGE_TAG.match(resolved["language"]):
        problems.append(
            TableProblem(
                "settings", f"language {resolved['language']!r} is not a language tag"
            )
        )
    return (
        resolved["agency"] or "",
        resolved["version"] or "1",
        resolved["language"] or "en",
    )


def build(
    tables: dict[str, RawTable],
    *,
    agency: str,
    version: str,
    language: str,
    problems: list[TableProblem],
) -> Built:
    """Build every item, collecting problems into ``problems``."""
    ctx = Context(agency, version, language, problems)
    built = Built(agency, version, language)
    for raw in tables.values():
        check_required_columns(ctx, raw)
    item_tables = [
        tables[table.name]
        for table in TABLES
        if table.item_table and table.name in tables
    ]

    # Pass 1: identities.
    for raw in item_tables:
        for row in raw.rows:
            reserve(ctx, raw, row)

    # Pass 2: elements.
    for raw in item_tables:
        for row in raw.rows:
            entry = entry_of(ctx, raw, row)
            tag = _tag(ctx, raw, row)
            if entry is not None and tag is not None:
                ctx.emit(
                    raw.table.name,
                    item_element(tag, entry.item, raw, row),
                    row.cells["id"],
                )

    # Pass 3: content, in an order where what a table takes over from
    # another (a variable takes its question's response) is there first.
    for name, step in _STEPS:
        if name in tables:
            step(ctx, tables[name])
    for name, column, noun in _PARENTS:
        if name in tables:
            check_parents(ctx, tables[name], column, noun)

    if problems:
        return built
    order = {table.name: index for index, table in enumerate(TABLES)}
    models: dict[int, MaintainableBase] = {}
    for table, element in sorted(ctx.out, key=lambda pair: order[pair[0]]):
        item = typed(element)
        models[id(element)] = item
        built.tables.setdefault(table, []).append(item)
    for (table, key), element in ctx.elements.items():
        built.keys.setdefault(table, {})[key] = models[id(element)]
    return built


def _tag(ctx: Context, raw: RawTable, row: Row) -> str | None:
    if raw.table.name == "flow":
        return _more.flow_tag(ctx, raw, row)
    return ITEM_TAGS[raw.table.name]


Filler = Callable[[Context, RawTable, Row, Entry, Element], None]
Step = Callable[[Context, RawTable], None]


def _rows(fill: Filler) -> Step:
    """A step that fills the element of each row with ``fill``."""

    def step(ctx: Context, raw: RawTable) -> None:
        for row in raw.rows:
            entry = entry_of(ctx, raw, row)
            element = ctx.elements.get((raw.table.name, row.cells.get("id", "")))
            if entry is not None and element is not None:
                fill(ctx, raw, row, entry, element)

    return step


def check_parents(ctx: Context, raw: RawTable, column: str, noun: str) -> None:
    """Report rows that end up inside themselves through ``column``."""
    table = raw.table.name
    known = ctx.index.get(table, {})
    parents = {
        row.cells["id"]: [key for key in values(row, column) if key in known]
        for row in raw.rows
        if entry_of(ctx, raw, row) is not None
    }
    reported: set[str] = set()
    for row in raw.rows:
        start = row.cells.get("id", "")
        if start not in parents or start in reported:
            continue
        if start in parents[start]:
            ctx.problem(raw, row, column, f"a {noun} cannot be its own parent")
            reported.add(start)
            continue
        path = _loop_from(start, parents)
        if path:
            ctx.problem(
                raw,
                row,
                column,
                f"{start!r} ends up inside itself: " + " > ".join(path),
            )
            reported.update(path)


def _loop_from(start: str, parents: dict[str, list[str]]) -> list[str]:
    """The chain of parents from ``start`` back to itself; empty if none."""
    stack: list[tuple[str, list[str]]] = [(start, [start])]
    seen: set[str] = set()
    while stack:
        key, path = stack.pop()
        for parent in parents.get(key, []):
            if parent == start:
                return [*path, start]
            if parent not in seen:
                seen.add(parent)
                stack.append((parent, [*path, parent]))
    return []


# ---------------------------------------------------------------------------
# Concepts, universes and the variable cascade
# ---------------------------------------------------------------------------


def _concept(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(cc("ConceptName"), ctx, row))
    for hit in lookup(ctx, raw, row, "parent", "concepts"):
        if hit.key != row.cells["id"]:
            element.append(ref(cc("SubclassOfReference"), hit.item, "Concept"))


def _universe(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(cc("UniverseName"), ctx, row))
    concept = single(ctx, raw, row, "concept", "concepts")
    if concept is not None:
        element.append(ref(r("DefiningConceptReference"), concept.item, "Concept"))


# Colectica's stand-in for the concept DDI 3.3 requires of a unit type: the
# schema makes r:ConceptReference mandatory by mistake.
_NO_CONCEPT_ID = "00000000-0000-0000-0000-000000000000"
_NO_CONCEPT_NOTE = "Bug in the 3.3 DDI schema requires this reference"


def _unit_type(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(r("Name"), ctx, row))
    concept = single(ctx, raw, row, "concept", "concepts")
    if concept is not None:
        element.append(ref(r("ConceptReference"), concept.item, "Concept"))
        return
    element.append(
        el(
            r("ConceptReference"),
            el(r("Agency"), text=ctx.agency),
            el(r("ID"), text=_NO_CONCEPT_ID),
            el(r("Version"), text="0"),
            el(r("TypeOfObject"), text="Concept"),
            el(
                r("UserAttributePair"),
                el(r("AttributeKey"), text="x:informational"),
                el(r("AttributeValue"), text=_NO_CONCEPT_NOTE),
            ),
        )
    )


def _conceptual_variable(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(cc("ConceptualVariableName"), ctx, row))
    concept = single(ctx, raw, row, "concept", "concepts")
    if concept is not None:
        element.append(ref(r("ConceptReference"), concept.item, "Concept"))
    for hit in lookup(ctx, raw, row, "universe", "universes"):
        element.append(ref(r("UniverseReference"), hit.item, "Universe"))
    unit_type = single(ctx, raw, row, "unit_type", "unit_types")
    if unit_type is not None:
        element.append(ref(r("UnitTypeReference"), unit_type.item, "UnitType"))


def _represented_variable(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(lp("RepresentedVariableName"), ctx, row))
    conceptual = single(ctx, raw, row, "conceptual_variable", "conceptual_variables")
    concept = single(ctx, raw, row, "concept", "concepts")
    unit_type = single(ctx, raw, row, "unit_type", "unit_types")
    if conceptual is not None:
        element.append(
            ref(r("ConceptualVariableReference"), conceptual.item, "ConceptualVariable")
        )
        if concept is not None or unit_type is not None:
            ctx.problem(
                raw,
                row,
                "conceptual_variable",
                "give a conceptual_variable, or a concept and unit_type, not both: "
                "the conceptual variable already has them",
            )
    else:
        if unit_type is not None:
            element.append(ref(r("UnitTypeReference"), unit_type.item, "UnitType"))
        if concept is not None:
            element.append(ref(r("ConceptReference"), concept.item, "Concept"))
    value = representation(ctx, raw, row, "representation")
    if value is None:
        if not row.cells.get("representation"):
            ctx.problem(raw, row, "representation", "is empty")
        return
    ctx.responses[("represented_variables", row.cells["id"])] = value
    element.append(value.to_xml())


# ---------------------------------------------------------------------------
# Code lists
# ---------------------------------------------------------------------------


def _code_list(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(lp("CodeListName"), ctx, row))


def _codes(ctx: Context, raw: RawTable) -> None:
    # (code list id, value) -> (row number, l:Code element)
    seen: dict[tuple[str, str], tuple[int, Element]] = {}
    for row in raw.rows:
        if not row.cells.get("code_list"):
            ctx.problem(raw, row, "code_list", "is empty")
        code_list = single(ctx, raw, row, "code_list", "code_lists")
        value = row.cells.get("value")
        if not value:
            ctx.problem(raw, row, "value", "is empty")
        missing = boolean(ctx, raw, row, "missing")
        if code_list is None or not value:
            continue
        list_key = code_list.key
        if (list_key, value) in seen:
            ctx.problem(
                raw,
                row,
                "value",
                f"{value!r} is already a code of {list_key} (row "
                f"{seen[(list_key, value)][0]})",
            )
            continue
        container = ctx.elements.get(("code_lists", list_key))
        parent = row.cells.get("parent")
        if parent is not None:
            found = seen.get((list_key, parent))
            if found is None:
                ctx.problem(
                    raw,
                    row,
                    "parent",
                    f"no earlier code of {list_key} has value {parent!r}; a "
                    "parent's row comes before its children",
                )
                continue
            container = found[1]
        category = _category(ctx, raw, row, list_key, value, missing)
        code = el(
            lp("Code"),
            el(r("Agency"), text=ctx.agency),
            el(r("ID"), text=ctx.identifier("codes", f"{list_key}/{value}")),
            el(r("Version"), text=ctx.version),
            ref(r("CategoryReference"), category, "Category"),
            el(r("Value"), text=value),
        )
        seen[(list_key, value)] = (row.number, code)
        if container is not None:
            container.append(code)


def _category(
    ctx: Context,
    raw: RawTable,
    row: Row,
    list_key: str,
    value: str,
    missing: bool | None,
) -> Identity:
    """The code's category: its own, or the one its ``category`` key shares."""
    shared_key = row.cells.get("category")
    if shared_key and shared_key in ctx.categories:
        category = ctx.categories[shared_key]
    else:
        key = f"shared/{shared_key}" if shared_key else f"{list_key}/{value}"
        category = ctx.identity("categories", key)
        element = item_element(lp("Category"), category, None, None)
        for column, tag in (("label", "Label"), ("description", "Description")):
            container = multilingual(r(tag), strings(raw, row, column))
            if container is not None:
                element.append(container)
        if missing is not None:
            element.set("isMissing", "true" if missing else "false")
        ctx.emit("codes", element)
        if shared_key:
            ctx.categories[shared_key] = category
    ctx.categories[f"{list_key}/{value}"] = category
    return category


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------


def _instruction(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(d("InstructionName"), ctx, row))
    for text in literal_texts(
        d("InstructionText"), strings(raw, row, "text"), ctx.language
    ):
        element.append(text)


def _question_texts(ctx: Context, raw: RawTable) -> None:
    """Check ``question_texts`` and keep its rows for the questions."""
    for row in raw.rows:
        question = row.cells.get("question")
        language = row.cells.get("language")
        audience = row.cells.get("audience")
        text = row.cells.get("text")
        if not question or not language or not text:
            for column, value in (
                ("question", question),
                ("language", language),
                ("text", text),
            ):
                if not value:
                    ctx.problem(raw, row, column, "is empty")
            continue
        if not LANGUAGE_TAG.match(language):
            ctx.problem(raw, row, "language", f"{language!r} is not a language tag")
            continue
        if audience and not AUDIENCE.match(audience):
            ctx.problem(
                raw,
                row,
                "audience",
                f"{audience!r} does not fit: DDI records the audience in a "
                "language tag, so it takes letters and digits, at most 8 "
                "between hyphens (proxy, intvwr, self-resp)",
            )
            continue
        if question not in ctx.index.get("questions", {}):
            ctx.problem(
                raw, row, "question", f"no row in questions has id {question!r}"
            )
            continue
        ctx.question_texts.setdefault(question, []).append(
            (language, audience, text, raw.where(row))
        )


def _question_text_elements(
    ctx: Context, raw: RawTable, row: Row, extra: list[tuple[str, str | None, str, str]]
) -> list[Element]:
    """One d:QuestionText per language and audience, as Colectica writes them."""
    wordings = [
        (
            string.lang or ctx.language,
            None,
            string.text,
            raw.where(row, f"text@{string.lang}"),
        )
        for string in strings(raw, row, "text")
    ]
    seen: dict[str, str] = {}
    out: list[Element] = []
    for language, audience, text, where in [*wordings, *extra]:
        attribute = audience_language(language, audience)
        if attribute in seen:
            ctx.problems.append(
                TableProblem(
                    where,
                    f"a second wording for language {language}"
                    + (f" and audience {audience}" if audience else "")
                    + f" (the first is at {seen[attribute]})",
                )
            )
            continue
        seen[attribute] = where
        out.append(literal_text(d("QuestionText"), text, language, audience))
    return out


def _question_extras(
    ctx: Context, raw: RawTable, row: Row, element: Element, member_tag: str, kind: str
) -> None:
    """Concept, instructions and groups: the columns every question kind has."""
    concept = single(ctx, raw, row, "concept", "concepts")
    if concept is not None:
        element.append(ref(r("ConceptReference"), concept.item, "Concept"))
    for hit in lookup(ctx, raw, row, "instruction", "instructions"):
        element.append(
            ref(d("InterviewerInstructionReference"), hit.item, "Instruction")
        )
    entry = ctx.index[raw.table.name][row.cells["id"]]
    for hit in lookup(ctx, raw, row, "group", "question_groups"):
        group = ctx.elements.get(("question_groups", hit.key))
        if group is not None:
            group.append(ref(d(member_tag), entry.item, kind))


def _question(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(d("QuestionItemName"), ctx, row))
    extra = ctx.question_texts.get(row.cells["id"], [])
    for text in _question_text_elements(ctx, raw, row, extra):
        element.append(text)
    response = representation(ctx, raw, row, "response")
    if response is not None:
        ctx.responses[("questions", row.cells["id"])] = response
        element.append(as_response_domain(response.to_xml()))
    _question_extras(ctx, raw, row, element, "QuestionItemReference", "QuestionItem")


def _question_grid(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(d("QuestionGridName"), ctx, row))
    for text in _question_text_elements(ctx, raw, row, []):
        element.append(text)
    for rank, column in enumerate(("rows", "columns"), start=1):
        code_list = single(ctx, raw, row, column, "code_lists")
        if code_list is not None:
            element.append(
                el(
                    d("GridDimension"),
                    el(
                        d("CodeDomain"),
                        ref(r("CodeListReference"), code_list.item, "CodeList"),
                    ),
                    rank=str(rank),
                )
            )
    if not row.cells.get("rows"):
        ctx.problem(raw, row, "rows", "a grid needs rows (a code list)")
    response = representation(ctx, raw, row, "response")
    if response is not None:
        element.append(as_response_domain(response.to_xml()))
    _question_extras(ctx, raw, row, element, "QuestionGridReference", "QuestionGrid")


def _question_block(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(d("QuestionBlockName"), ctx, row))
    intent = multilingual(d("QuestionBlockIntent"), strings(raw, row, "intent"))
    if intent is not None:
        element.append(intent)
    for hit in lookup(ctx, raw, row, "questions", "questions", "question_grids"):
        if hit.table == "questions":
            element.append(ref(d("QuestionItemReference"), hit.item, "QuestionItem"))
        else:
            element.append(ref(d("QuestionGridReference"), hit.item, "QuestionGrid"))
    _question_extras(ctx, raw, row, element, "QuestionBlockReference", "QuestionBlock")


def _question_group(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    kind = row.cells.get("type")
    if kind:
        element.append(el(d("TypeOfQuestionGroup"), text=kind))
    element.append(name_element(d("QuestionGroupName"), ctx, row))
    concept = single(ctx, raw, row, "concept", "concepts")
    if concept is not None:
        element.append(ref(r("ConceptReference"), concept.item, "Concept"))
    parent = single(ctx, raw, row, "parent", "question_groups")
    container = ctx.elements.get(("question_groups", parent.key)) if parent else None
    if container is not None and parent is not None and parent.key != row.cells["id"]:
        container.append(ref(d("QuestionGroupReference"), entry.item, "QuestionGroup"))


# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------


def _variable(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(lp("VariableName"), ctx, row))
    represented = single(ctx, raw, row, "represented_variable", "represented_variables")
    if represented is not None:
        element.append(
            ref(
                r("RepresentedVariableReference"),
                represented.item,
                "RepresentedVariable",
            )
        )
    conceptual = single(ctx, raw, row, "conceptual_variable", "conceptual_variables")
    if conceptual is not None:
        element.append(
            ref(r("ConceptualVariableReference"), conceptual.item, "ConceptualVariable")
        )
    for hit in lookup(ctx, raw, row, "universe", "universes"):
        element.append(ref(r("UniverseReference"), hit.item, "Universe"))
    concept = single(ctx, raw, row, "concept", "concepts")
    if concept is not None:
        element.append(ref(r("ConceptReference"), concept.item, "Concept"))
    questions = lookup(ctx, raw, row, "question", "questions")
    for hit in questions:
        element.append(ref(r("QuestionReference"), hit.item, "QuestionItem"))
    unit_type = single(ctx, raw, row, "unit_type", "unit_types")
    if unit_type is not None:
        element.append(ref(r("UnitTypeReference"), unit_type.item, "UnitType"))

    value = representation(ctx, raw, row, "representation")
    if value is None and not row.cells.get("representation"):
        # None of its own: its represented variable's, or its first question's.
        sources = [("represented_variables", represented.key)] if represented else []
        sources += [("questions", hit.key) for hit in questions[:1]]
        for source in sources:
            if source in ctx.responses:
                value = ctx.responses[source]
                break
    if value is not None:
        element.append(el(lp("VariableRepresentation"), value.to_xml()))

    for hit in lookup(ctx, raw, row, "dataset", "datasets"):
        _more.add_to_dataset(ctx, hit.key, entry.item)
    for hit in lookup(ctx, raw, row, "group", "variable_groups"):
        group = ctx.elements.get(("variable_groups", hit.key))
        if group is not None:
            group.append(ref(r("VariableReference"), entry.item, "Variable"))


def _variable_group(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    kind = row.cells.get("type")
    if kind:
        element.append(el(lp("TypeOfVariableGroup"), text=kind))
    element.append(name_element(lp("VariableGroupName"), ctx, row))
    for hit in lookup(ctx, raw, row, "universe", "universes"):
        element.append(ref(r("UniverseReference"), hit.item, "Universe"))
    concept = single(ctx, raw, row, "concept", "concepts")
    if concept is not None:
        element.append(ref(r("ConceptReference"), concept.item, "Concept"))
    parent = single(ctx, raw, row, "parent", "variable_groups")
    container = ctx.elements.get(("variable_groups", parent.key)) if parent else None
    if container is not None and parent is not None and parent.key != row.cells["id"]:
        container.append(ref(lp("VariableGroupReference"), entry.item, "VariableGroup"))


def _ncube(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(lp("NCubeName"), ctx, row))
    for hit in lookup(ctx, raw, row, "universe", "universes"):
        element.append(ref(r("UniverseReference"), hit.item, "Universe"))
    purpose = multilingual(r("Purpose"), strings(raw, row, "purpose"))
    if purpose is not None:
        element.append(purpose)
    dimensions = lookup(ctx, raw, row, "dimensions", "variables")
    for rank, hit in enumerate(dimensions, start=1):
        element.append(
            el(
                lp("Dimension"),
                ref(r("VariableReference"), hit.item, "Variable"),
                rank=str(rank),
            )
        )
    if dimensions:
        element.set("dimensionCount", str(len(dimensions)))
    elif not row.cells.get("dimensions"):
        ctx.problem(raw, row, "dimensions", "an n-cube needs at least one dimension")


_STEPS: list[tuple[str, Step]] = [
    ("concepts", _rows(_concept)),
    ("universes", _rows(_universe)),
    ("unit_types", _rows(_unit_type)),
    ("conceptual_variables", _rows(_conceptual_variable)),
    ("represented_variables", _rows(_represented_variable)),
    ("code_lists", _rows(_code_list)),
    ("codes", _codes),
    ("instructions", _rows(_instruction)),
    ("question_texts", _question_texts),
    ("questions", _rows(_question)),
    ("question_grids", _rows(_question_grid)),
    ("question_blocks", _rows(_question_block)),
    ("question_groups", _rows(_question_group)),
    ("studies", _rows(_more.study)),
    ("groups", _rows(_more.group)),
    ("organizations", _rows(_more.organization)),
    ("individuals", _rows(_more.individual)),
    ("instruments", _rows(_more.instrument)),
    ("flow", _more.flow),
    ("variable_groups", _rows(_variable_group)),
    ("variables", _rows(_variable)),
    ("datasets", _rows(_more.dataset)),
    ("ncubes", _rows(_ncube)),
    ("methodologies", _rows(_more.methodology)),
    ("processing_events", _rows(_more.processing_event)),
    ("quality_statements", _rows(_more.quality_statement)),
    ("comparisons", _more.comparisons),
]

# Tables whose rows nest through a parent column: (table, column, noun).
_PARENTS = [
    ("concepts", "parent", "concept"),
    ("groups", "parent", "group"),
    ("question_groups", "parent", "question group"),
    ("variable_groups", "parent", "variable group"),
    ("flow", "parent", "flow step"),
]


__all__ = ["FRAGMENT_ONLY", "Built", "build", "read_settings"]
