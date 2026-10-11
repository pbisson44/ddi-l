"""Builders for the study-level tables.

Studies and their groups, people, questionnaires and their flow, data files,
methodology, processing, quality and comparisons.

Some items have no table of their own. A study gets one data collection
holding its instruments, methodology and processing events; an instrument
gets a top sequence holding its flow; a data file gets a data relationship
listing its variables. Their identifiers are derived like any row's, so they
too are the same on every load.
"""

from __future__ import annotations

import re

from .._etree import Element
from ..constants import (
    ARCHIVE_NS,
    COMPARATIVE_NS,
    GROUP_NS,
    PHYSICAL_INSTANCE_NS,
    STUDY_UNIT_NS,
    XML_NS,
)
from ..models.base import InternationalString, qn
from ._common import (
    Context,
    Entry,
    Hit,
    Identified,
    Identity,
    d,
    el,
    entry_of,
    identification,
    is_number,
    item_element,
    literal_texts,
    lookup,
    lp,
    multilingual,
    name_element,
    r,
    ref,
    single,
    strings,
    values,
)
from ._read import RawTable, Row


def s(local: str) -> str:
    return qn(STUDY_UNIT_NS, local)


def g(local: str) -> str:
    return qn(GROUP_NS, local)


def a(local: str) -> str:
    return qn(ARCHIVE_NS, local)


def p(local: str) -> str:
    return qn(PHYSICAL_INSTANCE_NS, local)


def cm(local: str) -> str:
    return qn(COMPARATIVE_NS, local)


# xs:gYear, xs:gYearMonth, xs:date or xs:dateTime: what r:SimpleDate takes.
_DATE = re.compile(
    r"^\d{4}(-\d{2}(-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?)?)?$"
)

_QUESTION_TYPES = {
    "questions": "QuestionItem",
    "question_grids": "QuestionGrid",
    "question_blocks": "QuestionBlock",
}


def _string(text: str, language: str) -> Element:
    return el(r("String"), text=text, **{qn(XML_NS, "lang"): language})


def _title(ctx: Context, raw: RawTable, row: Row, fallback: str) -> Element:
    """r:Citation with the row's ``title@`` strings, or ``fallback``."""
    found = strings(raw, row, "title") or [
        InternationalString(text=fallback, lang=ctx.language)
    ]
    return el(r("Citation"), multilingual(r("Title"), found, child_tag="String"))


def _date(ctx: Context, raw: RawTable, row: Row, column: str) -> str | None:
    value = row.cells.get(column)
    if value is not None and not _DATE.match(value):
        ctx.problem(
            raw,
            row,
            column,
            f"{value!r} is not a date: write 2024, 2024-05 or 2024-05-31",
        )
        return None
    return value


def _study_of(ctx: Context, raw: RawTable, row: Row) -> Hit | None:
    """The row's study: its ``study`` cell, or the only study there is."""
    if row.cells.get("study"):
        return single(ctx, raw, row, "study", "studies")
    studies = ctx.index.get("studies", {})
    if len(studies) == 1:
        key, entry = next(iter(studies.items()))
        return Hit("studies", key, entry.item)
    return None


def _data_collection(ctx: Context, study: Hit) -> Element:
    """The study's data collection, made the first time a row needs it."""
    found = ctx.data_collections.get(study.key)
    if found is not None:
        return found
    identity = ctx.identity("data_collections", study.key)
    element = item_element(d("DataCollection"), identity, None, None)
    entry = ctx.index["studies"][study.key]
    label = multilingual(r("Label"), strings(entry.raw, entry.row, "title"))
    if label is not None:
        element.append(label)
    ctx.emit("studies", element)
    ctx.data_collections[study.key] = element
    unit = ctx.elements.get(("studies", study.key))
    if unit is not None:
        unit.append(ref(r("DataCollectionReference"), identity, "DataCollection"))
    return element


# ---------------------------------------------------------------------------
# Studies, groups and people
# ---------------------------------------------------------------------------


def study(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    key = row.cells["id"]
    # Every study gets its data collection, even an empty one: ddi-l writes
    # no study without one.
    _data_collection(ctx, Hit("studies", key, entry.item))
    citation = _title(ctx, raw, row, key)
    for column, tag in (
        ("subtitle", "SubTitle"),
        ("alternate_title", "AlternateTitle"),
    ):
        container = multilingual(r(tag), strings(raw, row, column), child_tag="String")
        if container is not None:
            citation.append(container)
    for column, role in (("creator", "Creator"), ("publisher", "Publisher")):
        for value in values(row, column):
            agent = _agent(ctx, raw, row, column, value, role)
            if agent is not None:
                citation.append(agent)
    published = _date(ctx, raw, row, "publication_date")
    if published:
        citation.append(el(r("PublicationDate"), el(r("SimpleDate"), text=published)))
    element.append(citation)

    for column, tag in (("abstract", "Abstract"), ("purpose", "Purpose")):
        container = multilingual(r(tag), strings(raw, row, column))
        if container is not None:
            element.append(container)
    concept = single(ctx, raw, row, "concept", "concepts")
    if concept is not None:
        element.append(ref(r("DefiningConceptReference"), concept.item, "Concept"))
    universe = single(ctx, raw, row, "universe", "universes")
    if universe is not None:
        element.append(ref(r("UniverseReference"), universe.item, "Universe"))

    funders = lookup(ctx, raw, row, "funder", "organizations")
    grants = values(row, "grant_number")
    if funders or grants:
        funding = el(r("FundingInformation"))
        for hit in funders:
            funding.append(
                ref(r("AgencyOrganizationReference"), hit.item, "Organization")
            )
        for grant in grants:
            funding.append(el(r("GrantNumber"), text=grant))
        element.append(funding)

    coverage = _coverage(ctx, raw, row)
    if coverage is not None:
        element.append(coverage)
    for column, tag in (
        ("analysis_unit", "AnalysisUnit"),
        ("kind_of_data", "KindOfData"),
    ):
        for value in values(row, column):
            element.append(el(r(tag), text=value))


def _agent(
    ctx: Context, raw: RawTable, row: Row, column: str, value: str, role: str
) -> Element | None:
    """A creator or publisher: a reference to an id in people, else a name."""
    hits = [
        (table, ctx.index[table][value].item)
        for table in ("organizations", "individuals")
        if value in ctx.index.get(table, {})
    ]
    if len(hits) > 1:
        ctx.problem(
            raw,
            row,
            column,
            f"{value!r} is an id in organizations and individuals; use an id "
            "that is in one of them only",
        )
        return None
    if hits:
        table, item = hits[0]
        kind = "Organization" if table == "organizations" else "Individual"
        return el(r(role), ref(r(f"{role}Reference"), item, kind))
    return el(r(role), el(r(f"{role}Name"), _string(value, ctx.language)))


def _coverage(ctx: Context, raw: RawTable, row: Row) -> Element | None:
    key = row.cells["id"]
    parts: list[Element] = []
    keywords = [
        el(
            r("Keyword"),
            text=word.strip(),
            **{qn(XML_NS, "lang"): string.lang or ctx.language},
        )
        for string in strings(raw, row, "keywords")
        for word in string.text.split("|")
        if word.strip()
    ]
    if keywords:
        parts.append(
            el(
                r("TopicalCoverage"),
                *identification(ctx.identity("coverages", f"{key}/topical")),
                *keywords,
            )
        )
    countries = values(row, "countries")
    if countries:
        parts.append(
            el(
                r("SpatialCoverage"),
                *identification(ctx.identity("coverages", f"{key}/spatial")),
                *(el(r("CountryCode"), text=country) for country in countries),
            )
        )
    start = _date(ctx, raw, row, "start_date")
    end = _date(ctx, raw, row, "end_date")
    if start or end:
        when = el(r("ReferenceDate"))
        if start:
            when.append(el(r("StartDate"), text=start))
        if end:
            when.append(el(r("EndDate"), text=end))
        parts.append(
            el(
                r("TemporalCoverage"),
                *identification(ctx.identity("coverages", f"{key}/temporal")),
                when,
            )
        )
    return el(r("Coverage"), *parts) if parts else None


def group(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    kind = row.cells.get("type")
    if kind:
        element.append(el(g("TypeOfGroup"), text=kind))
    element.append(_title(ctx, raw, row, row.cells["id"]))
    for column, tag in (("abstract", "Abstract"), ("purpose", "Purpose")):
        container = multilingual(r(tag), strings(raw, row, column))
        if container is not None:
            element.append(container)
    for hit in lookup(ctx, raw, row, "studies", "studies"):
        element.append(ref(r("StudyUnitReference"), hit.item, "StudyUnit"))
    parent = single(ctx, raw, row, "parent", "groups")
    container = ctx.elements.get(("groups", parent.key)) if parent else None
    if container is not None and parent is not None and parent.key != row.cells["id"]:
        container.append(ref(r("GroupReference"), entry.item, "Group"))


def _contact(row: Row) -> Element | None:
    url, email = row.cells.get("url"), row.cells.get("email")
    if not url and not email:
        return None
    contact = el(a("ContactInformation"))
    if url:
        contact.append(el(a("URL"), text=url))
    if email:
        contact.append(el(a("Email"), el(r("InternetEmail"), text=email)))
    return contact


def organization(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    names = strings(raw, row, "name")
    if not names:
        ctx.problem(raw, row, "name", "is empty")
    name = el(a("OrganizationName"), *(string.to_child("String") for string in names))
    abbreviation = row.cells.get("abbreviation")
    if abbreviation:
        name.append(el(r("Abbreviation"), _string(abbreviation, ctx.language)))
    element.append(el(a("OrganizationIdentification"), name))
    contact = _contact(row)
    if contact is not None:
        element.append(contact)


def individual(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    first, last = row.cells.get("first_name"), row.cells.get("last_name")
    if not first and not last:
        ctx.problem(raw, row, "last_name", "give a first_name, a last_name or both")
    name = el(a("IndividualName"))
    if first:
        name.append(el(a("FirstGiven"), text=first))
    if last:
        name.append(el(a("LastFamily"), text=last))
    element.append(el(a("IndividualIdentification"), name))
    contact = _contact(row)
    if contact is not None:
        element.append(contact)


# ---------------------------------------------------------------------------
# Questionnaires
# ---------------------------------------------------------------------------

# flow ``type`` -> the control construct it becomes
FLOW_TYPES = {
    "question": "QuestionConstruct",
    "statement": "StatementItem",
    "sequence": "Sequence",
    "if": "IfThenElse",
    "loop": "Loop",
}
_WORDS = {construct: word for word, construct in FLOW_TYPES.items()}
_CONTAINERS = ("Sequence", "IfThenElse", "Loop")
_BRANCHES = {"then": "then", "else": "else", "alors": "then", "sinon": "else"}
_DEFAULT_CONDITION_LANGUAGE = "pseudo-code"


def flow_tag(ctx: Context, raw: RawTable, row: Row) -> str | None:
    kind = (row.cells.get("type") or "").strip().lower()
    if kind in FLOW_TYPES:
        return d(FLOW_TYPES[kind])
    if not kind:
        ctx.problem(raw, row, "type", "is empty")
    else:
        ctx.problem(
            raw,
            row,
            "type",
            f"{row.cells['type']!r} is not one of " + ", ".join(FLOW_TYPES),
        )
    return None


def instrument(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(d("InstrumentName"), ctx, row))
    kind = row.cells.get("type")
    if kind:
        element.append(el(d("TypeOfInstrument"), text=kind))
    study_hit = _study_of(ctx, raw, row)
    if study_hit is not None:
        _data_collection(ctx, study_hit).append(
            ref(d("InstrumentReference"), entry.item, "Instrument")
        )


def _command(row: Row) -> Element:
    return el(
        r("Command"),
        el(
            r("ProgramLanguage"),
            text=row.cells.get("condition_language") or _DEFAULT_CONDITION_LANGUAGE,
        ),
        el(r("CommandContent"), text=row.cells.get("condition", "")),
    )


def _sequence(
    ctx: Context, key: str, name: str, members: list[tuple[str, Identified]]
) -> Identity:
    """A sequence the flow implies (an instrument's top, a branch, a loop body)."""
    identity = ctx.identity("flow_sequences", key)
    element = item_element(d("Sequence"), identity, None, None)
    element.append(el(d("ConstructName"), _string(name, ctx.language)))
    for kind, item in members:
        element.append(ref(d("ControlConstructReference"), item, kind))
    element.append(
        el(
            d("ConstructSequence"),
            el(d("ItemSequenceType"), text="InOrderOfAppearance"),
        )
    )
    ctx.emit("flow", element)
    return identity


def flow(ctx: Context, raw: RawTable) -> None:
    """Build each step, then put each in its parent, branch or instrument."""
    kinds: dict[str, str] = {}
    instruments: dict[str, str] = {}
    steps: list[tuple[Row, Entry, Element]] = []
    for row in raw.rows:
        entry = entry_of(ctx, raw, row)
        element = ctx.elements.get(("flow", row.cells.get("id", "")))
        if entry is None or element is None:
            continue
        key = row.cells["id"]
        kind = element.tag.rsplit("}", 1)[-1]
        kinds[key] = kind
        owner = single(ctx, raw, row, "instrument", "instruments")
        if owner is None:
            if not row.cells.get("instrument"):
                ctx.problem(raw, row, "instrument", "is empty")
            continue
        instruments[key] = owner.key
        steps.append((row, entry, element))
        element.append(name_element(d("ConstructName"), ctx, row))
        if kind == "QuestionConstruct":
            question = single(ctx, raw, row, "question", *_QUESTION_TYPES)
            if question is not None:
                element.append(
                    ref(
                        r("QuestionReference"),
                        question.item,
                        _QUESTION_TYPES[question.table],
                    )
                )
            elif not row.cells.get("question"):
                ctx.problem(raw, row, "question", "a question step needs a question")
        elif kind == "StatementItem":
            texts = strings(raw, row, "text")
            if not texts:
                ctx.problem(raw, row, "text", "a statement needs its text")
            for text in literal_texts(d("DisplayText"), texts, ctx.language):
                element.append(text)
        elif kind in ("IfThenElse", "Loop"):
            if not row.cells.get("condition"):
                ctx.problem(
                    raw, row, "condition", f"{row.cells['type']} needs a condition"
                )
            tag = "IfCondition" if kind == "IfThenElse" else "LoopWhile"
            element.append(el(d(tag), _command(row)))

    # (container id, branch) or ("", instrument id) -> members in row order
    members: dict[tuple[str, str], list[tuple[str, Identified]]] = {}
    for row, entry, _ in steps:
        key = row.cells["id"]
        parent = row.cells.get("parent")
        branch = row.cells.get("branch")
        if parent is None:
            if branch:
                ctx.problem(raw, row, "branch", "is only for a step inside an if")
            members.setdefault(("", instruments[key]), []).append(
                (kinds[key], entry.item)
            )
            continue
        if parent not in ctx.index.get("flow", {}):
            ctx.problem(raw, row, "parent", f"no row in flow has id {parent!r}")
            continue
        if parent not in instruments:
            continue  # the parent's own row has a problem, reported already
        if instruments[parent] != instruments[key]:
            ctx.problem(
                raw,
                row,
                "parent",
                f"{parent!r} is in instrument {instruments[parent]}, not "
                f"{instruments[key]}",
            )
            continue
        if kinds[parent] not in _CONTAINERS:
            ctx.problem(
                raw,
                row,
                "parent",
                f"{parent!r} is a {_WORDS[kinds[parent]]} step; only a sequence, "
                "if or loop holds other steps",
            )
            continue
        side = ""
        if kinds[parent] == "IfThenElse":
            side = _BRANCHES.get((branch or "then").strip().lower(), "")
            if not side:
                ctx.problem(raw, row, "branch", f"{branch!r} is not then or else")
                continue
        elif branch:
            ctx.problem(raw, row, "branch", "is only for a step inside an if")
        members.setdefault((parent, side), []).append((kinds[key], entry.item))

    for row, _, element in steps:
        key = row.cells["id"]
        kind = kinds[key]
        if kind == "Sequence":
            for member_kind, item in members.get((key, ""), []):
                element.append(ref(d("ControlConstructReference"), item, member_kind))
            element.append(
                el(
                    d("ConstructSequence"),
                    el(d("ItemSequenceType"), text="InOrderOfAppearance"),
                )
            )
        elif kind == "IfThenElse":
            for side, tag in (
                ("then", "ThenConstructReference"),
                ("else", "ElseConstructReference"),
            ):
                inside = members.get((key, side))
                if inside:
                    made = _sequence(ctx, f"{key}/{side}", f"{key} {side}", inside)
                    element.append(ref(d(tag), made, "Sequence"))
        elif kind == "Loop":
            inside = members.get((key, ""))
            if inside:
                body = _sequence(ctx, f"{key}/body", f"{key} body", inside)
                element.append(ref(d("ControlConstructReference"), body, "Sequence"))

    for owner_key, owned in ctx.index.get("instruments", {}).items():
        inside = members.get(("", owner_key))
        holder = ctx.elements.get(("instruments", owner_key))
        if inside and holder is not None:
            name = owned.row.cells.get("name") or owner_key
            top = _sequence(ctx, f"instrument/{owner_key}", name, inside)
            holder.append(ref(d("ControlConstructReference"), top, "Sequence"))


# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------


def add_to_dataset(ctx: Context, dataset: str, variable: Identified) -> None:
    ctx.dataset_variables.setdefault(dataset, []).append(variable)


def dataset(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    key = row.cells["id"]
    name = row.cells.get("name") or key
    element.append(_title(ctx, raw, row, name))
    # A physical instance has no label or description; its record has.
    moved = [child for child in element if child.tag in (r("Label"), r("Description"))]
    for child in moved:
        element.remove(child)
    record = el(
        lp("LogicalRecord"),
        *identification(ctx.identity("logical_records", key)),
        el(lp("LogicalRecordName"), _string(name, ctx.language)),
        *moved,
        el(
            lp("VariablesInRecord"),
            *(
                ref(lp("VariableUsedReference"), variable, "Variable")
                for variable in ctx.dataset_variables.get(key, [])
            ),
        ),
    )
    relationship_id = ctx.identity("data_relationships", key)
    relationship = item_element(lp("DataRelationship"), relationship_id, None, None)
    relationship.append(el(lp("DataRelationshipName"), _string(name, ctx.language)))
    relationship.append(record)
    ctx.emit("datasets", relationship)
    element.append(
        ref(r("DataRelationshipReference"), relationship_id, "DataRelationship")
    )
    location = row.cells.get("file")
    if location:
        element.append(
            el(p("DataFileIdentification"), el(p("DataFileURI"), text=location))
        )
    study_hit = _study_of(ctx, raw, row)
    unit = ctx.elements.get(("studies", study_hit.key)) if study_hit else None
    if unit is not None:
        unit.append(ref(r("PhysicalInstanceReference"), entry.item, "PhysicalInstance"))


# ---------------------------------------------------------------------------
# Methodology, processing and quality
# ---------------------------------------------------------------------------

_METHODOLOGY_PARTS = (
    ("data_collection", "DataCollectionMethodology"),
    ("time_method", "TimeMethod"),
    ("sampling", "SamplingProcedure"),
    ("deviation", "DeviationFromSampleDesign"),
    ("weighting", "WeightingMethodology"),
)


def methodology(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    key = row.cells["id"]
    element.append(name_element(d("MethodologyName"), ctx, row))
    for column, tag in _METHODOLOGY_PARTS:
        description = multilingual(r("Description"), strings(raw, row, column))
        if description is not None:
            element.append(
                el(
                    d(tag),
                    *identification(
                        ctx.identity("methodology_parts", f"{key}/{column}")
                    ),
                    description,
                )
            )
    study_hit = _study_of(ctx, raw, row)
    if study_hit is None:
        return
    if study_hit.key in ctx.methodologies:
        ctx.problem(
            raw,
            row,
            "study",
            f"study {study_hit.key} already has a methodology (row "
            f"{ctx.methodologies[study_hit.key]}); DDI gives a study one",
        )
        return
    ctx.methodologies[study_hit.key] = row.number
    _data_collection(ctx, study_hit).append(
        ref(d("MethodologyReference"), entry.item, "Methodology")
    )


def processing_event(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    key = row.cells["id"]
    element.append(name_element(d("ProcessingEventName"), ctx, row))
    for column, tag in (
        ("control", "ControlOperation"),
        ("cleaning", "CleaningOperation"),
    ):
        description = multilingual(r("Description"), strings(raw, row, column))
        if description is not None:
            element.append(el(d(tag), description))
    weighting = multilingual(r("Description"), strings(raw, row, "weighting"))
    if weighting is not None:
        element.append(
            el(
                d("Weighting"),
                *identification(ctx.identity("weightings", key)),
                weighting,
            )
        )
    appraisal = multilingual(d("OtherAppraisalProcess"), strings(raw, row, "appraisal"))
    if appraisal is not None:
        element.append(el(d("DataAppraisalInformation"), appraisal))
    study_hit = _study_of(ctx, raw, row)
    if study_hit is None:
        return
    scheme = ctx.processing_schemes.get(study_hit.key)
    if scheme is None:
        identity = ctx.identity("processing_event_schemes", study_hit.key)
        scheme = item_element(d("ProcessingEventScheme"), identity, None, None)
        ctx.emit("processing_events", scheme)
        ctx.processing_schemes[study_hit.key] = scheme
        _data_collection(ctx, study_hit).append(
            ref(d("ProcessingEventSchemeReference"), identity, "ProcessingEventScheme")
        )
    scheme.append(ref(d("ProcessingEventReference"), entry.item, "ProcessingEvent"))


def quality_statement(
    ctx: Context, raw: RawTable, row: Row, entry: Entry, element: Element
) -> None:
    element.append(name_element(r("QualityStatementName"), ctx, row))
    text = multilingual(r("OtherStatementOfQuality"), strings(raw, row, "text"))
    if text is not None:
        element.append(text)
    study_hit = _study_of(ctx, raw, row)
    unit = ctx.elements.get(("studies", study_hit.key)) if study_hit else None
    if unit is not None:
        unit.append(ref(r("QualityStatementReference"), entry.item, "QualityStatement"))


# ---------------------------------------------------------------------------
# Comparisons
# ---------------------------------------------------------------------------

# comparisons ``type`` -> (map element, table of its items, their type)
MAP_TYPES = {
    "concept": ("ConceptMap", "concepts", "Concept"),
    "universe": ("UniverseMap", "universes", "Universe"),
    "question": ("QuestionMap", "questions", "QuestionItem"),
    "variable": ("VariableMap", "variables", "Variable"),
    "category": ("CategoryMap", "", "Category"),
}


def comparisons(ctx: Context, raw: RawTable) -> None:
    # map key -> (type, first row number, cm:*Map element)
    maps: dict[str, tuple[str, int, Element]] = {}
    for row in raw.rows:
        key = row.cells.get("map")
        kind = (row.cells.get("type") or "").strip().lower()
        if not key:
            ctx.problem(raw, row, "map", "is empty")
        if kind not in MAP_TYPES:
            ctx.problem(
                raw,
                row,
                "type",
                "is empty"
                if not kind
                else f"{row.cells['type']!r} is not one of " + ", ".join(MAP_TYPES),
            )
        if not key or kind not in MAP_TYPES:
            continue
        if key in maps and maps[key][0] != kind:
            ctx.problem(
                raw,
                row,
                "type",
                f"map {key} compares {maps[key][0]} items (row {maps[key][1]}); "
                "one map compares one kind",
            )
            continue
        tag, table, type_of_object = MAP_TYPES[kind]
        ends: list[Identified] = []
        for column in ("source", "target"):
            if not row.cells.get(column):
                ctx.problem(raw, row, column, "is empty")
            elif table:
                hit = single(ctx, raw, row, column, table)
                if hit is not None:
                    ends.append(hit.item)
            else:
                category = ctx.categories.get(row.cells[column])
                if category is None:
                    ctx.problem(
                        raw,
                        row,
                        column,
                        f"no category {row.cells[column]!r}: write code_list/value "
                        "(SexCodes/1) or a `category` key of codes",
                    )
                else:
                    ends.append(category)
        weight = row.cells.get("weight")
        if weight is not None and not (is_number(weight) and 0 <= float(weight) <= 1):
            ctx.problem(raw, row, "weight", f"{weight!r} is not a number from 0 to 1")
            continue
        if len(ends) != 2:
            continue
        if key not in maps:
            identity = ctx.identity("comparisons", key)
            element = item_element(cm(tag), identity, None, None)
            element.append(el(cm("MapName"), _string(key, ctx.language)))
            ctx.emit("comparisons", element)
            maps[key] = (kind, row.number, element)
        correspondence = el(
            cm("Correspondence"),
            multilingual(cm("Commonality"), strings(raw, row, "commonality")),
            multilingual(r("Difference"), strings(raw, row, "difference")),
            el(cm("CommonalityWeight"), text=weight) if weight is not None else None,
        )
        source, target = ends
        maps[key][2].append(
            el(
                cm("ItemMap"),
                *identification(
                    ctx.identity(
                        "item_maps",
                        f"{key}/{row.cells['source']}/{row.cells['target']}",
                    )
                ),
                ref(cm("SourceItemReference"), source, type_of_object),
                ref(cm("TargetItemReference"), target, type_of_object),
                correspondence if len(correspondence) else None,
            )
        )
