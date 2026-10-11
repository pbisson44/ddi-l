"""The tables a metadata workbook holds, and the columns each one takes.

One spec drives everything else: the reader checks headers against it, the
builder reads values by these names, and the template writer lays out the
blank and example workbooks from it, so the documentation, the templates and
the loader cannot drift apart.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Separates several values in one cell ("Q_AGE|Q_SEX"). Not a comma or
# semicolon: those are the CSV delimiters Excel writes, depending on locale.
MULTI_VALUE_SEPARATOR = "|"

# A BCP 47 language tag, as xml:lang takes it: "en", "fr-CA", "en-x-proxy".
LANGUAGE_TAG = re.compile(r"^[A-Za-z]{2,8}(-[A-Za-z0-9]{1,8})*$")

# An audience is one or more BCP 47 private-use subtags: "proxy",
# "self-response". See audience_language().
AUDIENCE = re.compile(r"^[A-Za-z0-9]{1,8}(-[A-Za-z0-9]{1,8})*$")

CUSTOM_PREFIX = "custom:"

# Response and representation types, as the `response` and `representation`
# columns spell them.
RESPONSE_TYPES = ("code", "numeric", "text", "datetime")


@dataclass(frozen=True)
class Column:
    """One column of a table.

    ``multilingual`` columns repeat once per language: ``label@en``,
    ``label@fr``. ``reference`` names the table whose ``id`` the column's
    values point to.
    """

    name: str
    help: str
    required: bool = False
    multilingual: bool = False
    reference: str | None = None
    multiple: bool = False


@dataclass(frozen=True)
class Table:
    """One table: a CSV file in a folder, or a sheet in an Excel workbook."""

    name: str
    help: str
    columns: tuple[Column, ...]
    custom: bool = True
    item_table: bool = True
    columns_by_name: dict[str, Column] = field(
        init=False, repr=False, compare=False, hash=False
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "columns_by_name", {column.name: column for column in self.columns}
        )

    @property
    def file_name(self) -> str:
        return f"{self.name}.csv"


_ID = Column(
    "id",
    "Your key for the row, unique in this table. Other tables use it to point "
    "here. Any text without spaces works: AGE, Q_AGE, 101.",
    required=True,
)
_DDI_ID = Column(
    "ddi_id",
    "The DDI identifier (a UUID) to give the item. Leave empty and one is "
    "derived from the agency, the table and `id`, so loading the same tables "
    "again gives the same identifiers. Fill it to update an item that already "
    "exists in Colectica.",
)
_VERSION = Column("version", "The item's version. Defaults to `version` in `settings`.")
_NAME = Column(
    "name",
    "The item's name, in the `settings` language. Defaults to `id`.",
)
_LABEL = Column("label", "A short human-readable label.", multilingual=True)
_DESCRIPTION = Column(
    "description", "A longer description or definition.", multilingual=True
)

_COMMON = (_ID, _DDI_ID, _VERSION, _NAME, _LABEL, _DESCRIPTION)

_RESPONSE_DETAIL = (
    Column(
        "code_list",
        "For `code`: the code list (an `id` in `code_lists`).",
        reference="code_lists",
    ),
    Column(
        "numeric_type",
        "For `numeric`: Integer, Decimal, Float, Double, Long or Short.",
    ),
    Column("min", "For `numeric`: the lowest valid value."),
    Column("max", "For `numeric`: the highest valid value."),
    Column("max_length", "For `text`: the longest valid answer, in characters."),
    Column(
        "date_type",
        "For `datetime`: Date, DateTime, Time, Year, YearMonth or Duration.",
    ),
)

SETTINGS = Table(
    "settings",
    "One row per setting, in two columns: `setting` and `value`.",
    (
        Column("setting", "agency, version or language.", required=True),
        Column("value", "The setting's value.", required=True),
    ),
    custom=False,
    item_table=False,
)

# Rows of the settings table: name -> (required, default, help).
SETTING_NAMES: dict[str, tuple[bool, str | None, str]] = {
    "agency": (
        True,
        None,
        "The maintenance agency of every item, such as ca.statcan.",
    ),
    "version": (False, "1", "The version of every item without its own."),
    "language": (
        False,
        "en",
        "The language of names (the `name` column), such as en or fr-CA.",
    ),
}

CONCEPTS = Table(
    "concepts",
    "What is measured: one row per concept.",
    (
        *_COMMON,
        Column(
            "parent",
            "The broader concept(s) this one narrows (ids in `concepts`).",
            reference="concepts",
            multiple=True,
        ),
    ),
)

UNIVERSES = Table(
    "universes",
    "Who or what is described: one row per universe.",
    (
        *_COMMON,
        Column(
            "concept",
            "The concept that defines the universe (an `id` in `concepts`).",
            reference="concepts",
        ),
    ),
)

CODE_LISTS = Table(
    "code_lists",
    "One row per code list. The codes themselves go in `codes`.",
    _COMMON,
)

CODES = Table(
    "codes",
    "One row per code, in display order. Each code gets a category holding its labels.",
    (
        Column(
            "code_list",
            "The code list the code belongs to (an `id` in `code_lists`).",
            required=True,
            reference="code_lists",
        ),
        Column(
            "value",
            "The code as stored in the data: 1, 01, M. Format the column as "
            "text in Excel so 01 keeps its zero.",
            required=True,
        ),
        _LABEL,
        _DESCRIPTION,
        Column(
            "category",
            "Optional key to share one category between code lists: codes "
            "with the same `category` point to one category, labelled from "
            "the first of them.",
        ),
        Column(
            "missing",
            "true for a missing-value code (Refusal, Don't know).",
        ),
        Column(
            "parent",
            "For a hierarchy (a classification): the `value` of the code this "
            "one sits under, in the same code list. The parent's row comes "
            "first.",
        ),
    ),
    # A category can be shared by several code rows, so no one row's
    # custom columns would be the category's.
    custom=False,
    item_table=False,
)


def _ref(name: str, table: str, help_: str, *, multiple: bool = False) -> Column:
    return Column(name, help_, reference=table, multiple=multiple)


_STUDY = _ref(
    "study",
    "studies",
    "The study it belongs to (an `id` in `studies`). Empty for the only study, "
    "when `studies` has one row.",
)
_CONCEPT = _ref(
    "concept", "concepts", "The concept it measures (an `id` in `concepts`)."
)
_UNIVERSES = _ref(
    "universe", "universes", "Who it describes (ids in `universes`).", multiple=True
)
_UNIT_TYPE = _ref(
    "unit_type",
    "unit_types",
    "The kind of unit it describes (an `id` in `unit_types`).",
)

# ---------------------------------------------------------------------------
# Study, people and groups
# ---------------------------------------------------------------------------

STUDIES = Table(
    "studies",
    "One row per study (a survey cycle, a census, an administrative source).",
    (
        _ID,
        _DDI_ID,
        _VERSION,
        Column("title", "The study's title.", multilingual=True),
        Column("subtitle", "A subtitle.", multilingual=True),
        Column(
            "alternate_title", "Another title, such as an acronym.", multilingual=True
        ),
        Column("abstract", "What the study is about.", multilingual=True),
        Column("purpose", "Why it was done.", multilingual=True),
        Column(
            "creator",
            "Who made it: ids in `organizations` or `individuals`, or names.",
            multiple=True,
        ),
        Column(
            "publisher",
            "Who publishes it: ids in `organizations` or `individuals`, or names.",
            multiple=True,
        ),
        Column("publication_date", "When it was published: 2024, 2024-05, 2024-05-31."),
        Column("kind_of_data", "Survey data, administrative records...", multiple=True),
        Column("analysis_unit", "Persons, households, businesses...", multiple=True),
        _ref("universe", "universes", "Who the study covers (an `id` in `universes`)."),
        _ref(
            "concept",
            "concepts",
            "The concept that defines the study (an `id` in `concepts`).",
        ),
        Column("keywords", "Topics, separated by |.", multilingual=True),
        Column("start_date", "Start of the period covered: 2024-01-01."),
        Column("end_date", "End of the period covered: 2024-12-31."),
        Column("countries", "ISO country codes covered: CA|US.", multiple=True),
        _ref(
            "funder",
            "organizations",
            "Who funds it (ids in `organizations`).",
            multiple=True,
        ),
        Column("grant_number", "The funding grant's number.", multiple=True),
    ),
)

ORGANIZATIONS = Table(
    "organizations",
    "One row per organization: creators, publishers, funders.",
    (
        _ID,
        _DDI_ID,
        _VERSION,
        Column("name", "The organization's name.", required=True, multilingual=True),
        Column("abbreviation", "A short name: StatCan."),
        Column("email", "A contact email address."),
        Column("url", "Its web site."),
        _DESCRIPTION,
    ),
)

INDIVIDUALS = Table(
    "individuals",
    "One row per person.",
    (
        _ID,
        _DDI_ID,
        _VERSION,
        Column("first_name", "Given name."),
        Column("last_name", "Family name."),
        Column("email", "A contact email address."),
        Column("url", "A web page."),
        _DESCRIPTION,
    ),
)

GROUPS = Table(
    "groups",
    "One row per group of studies, such as all cycles of a survey.",
    (
        _ID,
        _DDI_ID,
        _VERSION,
        Column("title", "The group's title.", multilingual=True),
        Column("abstract", "What the group holds.", multilingual=True),
        Column("purpose", "Why the studies are grouped.", multilingual=True),
        Column("type", "The kind of group: Series, Program..."),
        _ref(
            "studies", "studies", "The studies in it (ids in `studies`).", multiple=True
        ),
        _ref("parent", "groups", "The group it sits in (an `id` in `groups`)."),
    ),
)

# ---------------------------------------------------------------------------
# Variable cascade
# ---------------------------------------------------------------------------

UNIT_TYPES = Table(
    "unit_types",
    "One row per kind of unit: person, household, business.",
    (*_COMMON, _CONCEPT),
)

CONCEPTUAL_VARIABLES = Table(
    "conceptual_variables",
    "One row per conceptual variable: a concept measured on a unit type, "
    "with no representation yet.",
    (*_COMMON, _CONCEPT, _UNIVERSES, _UNIT_TYPE),
)

REPRESENTED_VARIABLES = Table(
    "represented_variables",
    "One row per represented variable: a conceptual variable with a "
    "representation, shared by the variables that record it the same way.",
    (
        *_COMMON,
        _ref(
            "conceptual_variable",
            "conceptual_variables",
            "The conceptual variable it represents (an `id` in "
            "`conceptual_variables`).",
        ),
        _CONCEPT,
        _UNIT_TYPE,
        Column(
            "representation",
            "How values are recorded: code, numeric, text or datetime.",
        ),
        *_RESPONSE_DETAIL,
    ),
)

# ---------------------------------------------------------------------------
# Code lists and questions
# ---------------------------------------------------------------------------

_INSTRUCTION = _ref(
    "instruction",
    "instructions",
    "Instructions shown with it (ids in `instructions`).",
    multiple=True,
)
_QUESTION_GROUP = _ref(
    "group",
    "question_groups",
    "The question group(s) it belongs to (ids in `question_groups`).",
    multiple=True,
)

QUESTIONS = Table(
    "questions",
    "One row per question.",
    (
        *_COMMON,
        Column(
            "text",
            "The question as asked. For wording that differs by audience "
            "(proxy, interviewer), add rows to `question_texts`.",
            multilingual=True,
        ),
        Column(
            "concept",
            "The concept the question measures (an `id` in `concepts`).",
            reference="concepts",
        ),
        Column(
            "response",
            "The kind of answer: code, numeric, text or datetime. Empty for "
            "no response domain.",
        ),
        *_RESPONSE_DETAIL,
        _INSTRUCTION,
        _QUESTION_GROUP,
    ),
)

QUESTION_TEXTS = Table(
    "question_texts",
    "Extra wordings of a question, one row per language and audience. Use it "
    "when one question is worded differently for different audiences.",
    (
        Column(
            "question",
            "The question (an `id` in `questions`).",
            required=True,
            reference="questions",
        ),
        Column("language", "The wording's language: en, fr-CA.", required=True),
        Column(
            "audience",
            "Who the wording is for: proxy, intvwr, self-resp. Letters and "
            "digits, at most 8 between hyphens. Empty for everyone.",
        ),
        Column("text", "The wording.", required=True),
    ),
    custom=False,
    item_table=False,
)

VARIABLES = Table(
    "variables",
    "One row per variable (column of your data file).",
    (
        *_COMMON,
        Column(
            "concept",
            "The concept the variable measures (an `id` in `concepts`).",
            reference="concepts",
        ),
        Column(
            "universe",
            "Who the variable describes (ids in `universes`).",
            reference="universes",
            multiple=True,
        ),
        Column(
            "question",
            "The question(s) the variable's values come from (ids in `questions`).",
            reference="questions",
            multiple=True,
        ),
        Column(
            "representation",
            "How the values are recorded: code, numeric, text or datetime. "
            "Empty to take the response of its represented variable, or of "
            "its first question.",
        ),
        *_RESPONSE_DETAIL,
        _UNIT_TYPE,
        _ref(
            "conceptual_variable",
            "conceptual_variables",
            "Its conceptual variable (an `id` in `conceptual_variables`).",
        ),
        _ref(
            "represented_variable",
            "represented_variables",
            "Its represented variable (an `id` in `represented_variables`).",
        ),
        _ref(
            "dataset",
            "datasets",
            "The data file(s) it is a column of (ids in `datasets`), in column order.",
            multiple=True,
        ),
        _ref(
            "group",
            "variable_groups",
            "The variable group(s) it belongs to (ids in `variable_groups`).",
            multiple=True,
        ),
    ),
)

INSTRUCTIONS = Table(
    "instructions",
    "One row per instruction to respondents or interviewers, attached to "
    "questions with their `instruction` column.",
    (*_COMMON, Column("text", "The instruction.", multilingual=True)),
)

QUESTION_GRIDS = Table(
    "question_grids",
    "One row per grid question: rows from one code list, optional columns "
    "from another, one response for each cell.",
    (
        *_COMMON,
        Column("text", "The question as asked.", multilingual=True),
        _CONCEPT,
        _ref(
            "rows",
            "code_lists",
            "The grid's rows (an `id` in `code_lists`).",
        ),
        _ref(
            "columns",
            "code_lists",
            "The grid's columns, if any (an `id` in `code_lists`).",
        ),
        Column("response", "The answer in each cell: code, numeric, text or datetime."),
        *_RESPONSE_DETAIL,
        _INSTRUCTION,
        _QUESTION_GROUP,
    ),
)

QUESTION_BLOCKS = Table(
    "question_blocks",
    "One row per block of questions presented together.",
    (
        *_COMMON,
        Column("intent", "What the block is for.", multilingual=True),
        Column(
            "questions",
            "Its questions, in order: ids in `questions` or `question_grids`.",
            multiple=True,
        ),
        _CONCEPT,
        _INSTRUCTION,
        _QUESTION_GROUP,
    ),
)

QUESTION_GROUPS = Table(
    "question_groups",
    "One row per question group, such as a module of a questionnaire. "
    "Questions join with their `group` column.",
    (
        *_COMMON,
        Column("type", "The kind of group: Module, Topic..."),
        _ref(
            "parent",
            "question_groups",
            "The group it sits in (an `id` in `question_groups`).",
        ),
        _CONCEPT,
    ),
)

INSTRUMENTS = Table(
    "instruments",
    "One row per questionnaire (instrument). Its content is in `flow`.",
    (*_COMMON, _STUDY, Column("type", "The kind of instrument: CAWI, CATI, Paper...")),
)

FLOW = Table(
    "flow",
    "The questionnaire flow: one row per step, in order. Steps nest under a "
    "sequence, condition or loop through `parent`.",
    (
        Column(
            "instrument",
            "The instrument (an `id` in `instruments`).",
            required=True,
            reference="instruments",
        ),
        *_COMMON,
        Column(
            "type",
            "question, statement, sequence, if or loop.",
            required=True,
        ),
        _ref(
            "parent",
            "flow",
            "The sequence, if or loop it is inside (an `id` in `flow`).",
        ),
        Column("branch", "Inside an if: then or else. Defaults to then."),
        Column(
            "question",
            "For question: an id in `questions`, `question_grids` or "
            "`question_blocks`.",
        ),
        Column("text", "For statement: the text shown.", multilingual=True),
        Column("condition", "For if and loop: the condition, such as AGE >= 15."),
        Column(
            "condition_language",
            "The language the condition is written in. Defaults to pseudo-code.",
        ),
    ),
)

VARIABLE_GROUPS = Table(
    "variable_groups",
    "One row per variable group, such as a topic or derived-variable set. "
    "Variables join with their `group` column.",
    (
        *_COMMON,
        Column("type", "The kind of group: Topic, Derived..."),
        _ref(
            "parent",
            "variable_groups",
            "The group it sits in (an `id` in `variable_groups`).",
        ),
        _CONCEPT,
        _UNIVERSES,
    ),
)

DATASETS = Table(
    "datasets",
    "One row per data file. Variables join with their `dataset` column. The "
    "`label` and `description` describe the file's record of variables.",
    (
        *_COMMON,
        Column("title", "The file's title. Defaults to `name`.", multilingual=True),
        Column("file", "Where the file is: a path or URL."),
        _STUDY,
    ),
)

NCUBES = Table(
    "ncubes",
    "One row per n-cube (a multidimensional table of aggregates).",
    (
        *_COMMON,
        Column(
            "dimensions",
            "Its dimensions, in order: ids in `variables`.",
            reference="variables",
            multiple=True,
        ),
        Column("purpose", "What the n-cube is for.", multilingual=True),
        _UNIVERSES,
    ),
)

METHODOLOGIES = Table(
    "methodologies",
    "How a study's data were collected: one row per methodology.",
    (
        *_COMMON,
        _STUDY,
        Column("data_collection", "How data were collected.", multilingual=True),
        Column(
            "time_method", "Cross-section, panel, time series...", multilingual=True
        ),
        Column("sampling", "How the sample was drawn.", multilingual=True),
        Column(
            "deviation", "How the sample departs from its design.", multilingual=True
        ),
        Column("weighting", "How weights were derived.", multilingual=True),
    ),
)

PROCESSING_EVENTS = Table(
    "processing_events",
    "What was done to a study's data after collection: one row per event.",
    (
        *_COMMON,
        _STUDY,
        Column("control", "Checks made on the data.", multilingual=True),
        Column("cleaning", "How the data were cleaned or edited.", multilingual=True),
        Column("weighting", "How the data were weighted.", multilingual=True),
        Column("appraisal", "Response rates, sampling error...", multilingual=True),
    ),
)

QUALITY_STATEMENTS = Table(
    "quality_statements",
    "One row per statement about a study's quality.",
    (*_COMMON, _STUDY, Column("text", "The statement.", multilingual=True)),
)

COMPARISONS = Table(
    "comparisons",
    "How items compare, across studies or cycles: one row per pair. Rows "
    "with the same `map` form one map.",
    (
        Column("map", "Your key for the map the row belongs to.", required=True),
        Column(
            "type",
            "What is compared: concept, universe, question, variable or category.",
            required=True,
        ),
        Column(
            "source", "The item compared from (its id in that table).", required=True
        ),
        Column("target", "The item compared to (its id in that table).", required=True),
        Column("commonality", "What they share.", multilingual=True),
        Column("difference", "How they differ.", multilingual=True),
        Column("weight", "How alike they are, from 0 to 1."),
    ),
    custom=False,
    item_table=False,
)


# In display order; every reference is resolved after all tables are read,
# so a table may point at one that comes later.
TABLES: tuple[Table, ...] = (
    SETTINGS,
    STUDIES,
    GROUPS,
    ORGANIZATIONS,
    INDIVIDUALS,
    CONCEPTS,
    UNIVERSES,
    UNIT_TYPES,
    CONCEPTUAL_VARIABLES,
    REPRESENTED_VARIABLES,
    CODE_LISTS,
    CODES,
    INSTRUCTIONS,
    QUESTIONS,
    QUESTION_TEXTS,
    QUESTION_GRIDS,
    QUESTION_BLOCKS,
    QUESTION_GROUPS,
    INSTRUMENTS,
    FLOW,
    VARIABLES,
    VARIABLE_GROUPS,
    DATASETS,
    NCUBES,
    METHODOLOGIES,
    PROCESSING_EVENTS,
    QUALITY_STATEMENTS,
    COMPARISONS,
)
TABLES_BY_NAME: dict[str, Table] = {table.name: table for table in TABLES}


@dataclass(frozen=True)
class Header:
    """A parsed column header: ``label@fr`` -> column ``label``, language ``fr``."""

    raw: str
    column: str
    language: str | None = None
    custom_key: str | None = None


def is_ignored_header(header: str) -> bool:
    """Notes columns: empty, or starting with ``#`` or ``_``."""
    return not header or header.startswith(("#", "_"))


def expand_headers(table: Table, languages: tuple[str, ...]) -> list[str]:
    """The header row of ``table`` for ``languages``, as the templates use."""
    headers: list[str] = []
    for column in table.columns:
        if column.multilingual:
            headers.extend(f"{column.name}@{language}" for language in languages)
        else:
            headers.append(column.name)
    return headers


def audience_language(language: str, audience: str | None) -> str:
    """The ``audienceLanguage`` of a question wording.

    DDI 3.3 gives a d:QuestionText one attribute to say who it is for,
    ``audienceLanguage``, an ``xs:language``. A wording for everyone uses the
    language itself; a wording for one audience adds the audience as BCP 47
    private-use subtags, so ``fr`` for proxies is ``fr-x-proxy``. The value is
    still a valid language tag, and tools that only read the language see
    ``fr``.
    """
    if not audience:
        return language
    return f"{language}-x-{audience.lower()}"
