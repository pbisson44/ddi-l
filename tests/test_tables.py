"""Loading DDI items from metadata tables: CSV folders and .xlsx workbooks."""

from __future__ import annotations

import csv
import runpy
import zipfile
from pathlib import Path

import pytest

import ddi_l as ddi
from ddi_l import schema_loader
from ddi_l._etree import tostring
from ddi_l.constants import DATA_COLLECTION_NS
from ddi_l.lint import run_lint
from ddi_l.models.base import qn
from ddi_l.models.concept import Concept, Universe
from ddi_l.models.logicalproduct import CodeList, Variable
from ddi_l.tables import (
    TableImportError,
    load_tables,
    write_table_templates,
)
from ddi_l.tables._xlsx import read_workbook, write_workbook
from tests.helpers.tables import get as _get
from tests.helpers.tables import problems as _problems
from tests.helpers.tables import settings as _settings
from tests.helpers.tables import write as _write

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# docs/ and scripts/ are not in the sdist; tests that read them skip there.
needs_docs = pytest.mark.skipif(
    not (PROJECT_ROOT / "docs").is_dir(), reason="docs/ is not shipped in the sdist"
)


@pytest.fixture
def example(tmp_path: Path) -> Path:
    return write_table_templates(tmp_path / "example", example=True)


@pytest.fixture
def study_tables(tmp_path: Path) -> Path:
    """The example without the tables a study document has no place for."""
    from ddi_l.tables._build import FRAGMENT_ONLY
    from ddi_l.tables._example import EXAMPLE

    folder = tmp_path / "study"
    folder.mkdir()
    for name, rows in EXAMPLE.items():
        if name in FRAGMENT_ONLY:
            continue
        kept = [
            {key: value for key, value in row.items() if key not in ("study", "group")}
            for row in rows
        ]
        headers = list(dict.fromkeys(key for row in kept for key in row))
        with (folder / f"{name}.csv").open("w", encoding="utf-8", newline="") as out:
            writer = csv.DictWriter(out, fieldnames=headers)
            writer.writeheader()
            writer.writerows(kept)
    return folder


# A study's references point at items outside it, which item by item is
# expected; to_fragment() and to_study() do not warn.
_STUDY_REFERENCES = pytest.mark.filterwarnings("ignore::ddi_l.DDIReferenceWarning")


# ---------------------------------------------------------------------------
# The example
# ---------------------------------------------------------------------------


# Items per table in the example: its rows, plus what they imply (a category
# per code, a data collection per study, the sequences of the flow, ...).
EXAMPLE_COUNTS = {
    "studies": 2,
    "groups": 1,
    "organizations": 1,
    "individuals": 1,
    "concepts": 5,
    "universes": 1,
    "unit_types": 1,
    "conceptual_variables": 2,
    "represented_variables": 2,
    "code_lists": 5,
    "codes": 14,
    "instructions": 1,
    "questions": 3,
    "question_grids": 1,
    "question_blocks": 1,
    "question_groups": 3,
    "instruments": 1,
    "flow": 16,
    "variables": 5,
    "variable_groups": 2,
    "datasets": 2,
    "ncubes": 1,
    "methodologies": 1,
    "processing_events": 3,
    "quality_statements": 1,
    "comparisons": 1,
}


def test_example_tables_build_every_kind_of_item(example: Path) -> None:
    tables = load_tables(example)
    assert {name: len(items) for name, items in tables.tables.items()} == (
        EXAMPLE_COUNTS
    )
    assert len(tables.items) == sum(EXAMPLE_COUNTS.values())
    assert (
        len(tables.concepts),
        len(tables.universes),
        len(tables.categories),
        len(tables.code_lists),
        len(tables.questions),
        len(tables.variables),
    ) == (5, 1, 14, 5, 3, 5)
    assert tables.agency == "example.org"


def test_example_fragment_is_schema_valid(example: Path) -> None:
    tables = load_tables(example)
    fragment = tables.to_fragment(version_date="2026-01-01T00:00:00.0000000Z")
    assert schema_loader.validate(fragment.root, raise_error=False) == []
    assert len(fragment.items()) == len(tables.items)


def test_study_tables_make_a_schema_valid_study(study_tables: Path) -> None:
    study = load_tables(study_tables).to_study("Example survey")
    assert study.validate() == []


def test_fragment_top_level_is_the_only_group_or_study(
    example: Path, study_tables: Path
) -> None:
    tables = load_tables(example)
    top = tables.to_fragment().get_top_level_reference()
    assert top is not None
    assert top.identifier == tables.get("groups", "ELS_SERIES").identifier
    question = tables.get("questions", "Q_AGE")
    named = tables.to_fragment(top_level=question).get_top_level_reference()
    assert named is not None and named.identifier == question.identifier
    assert load_tables(study_tables).to_fragment().get_top_level_reference() is None


@_STUDY_REFERENCES
def test_csv_and_xlsx_give_the_same_items(example: Path, tmp_path: Path) -> None:
    workbook = write_table_templates(
        tmp_path / "example.xlsx", example=True, layout="xlsx"
    )
    from_csv = [tostring(item.to_xml()) for item in load_tables(example).items]
    from_xlsx = [tostring(item.to_xml()) for item in load_tables(workbook).items]
    assert from_csv == from_xlsx


def test_identifiers_are_stable_and_follow_the_agency(example: Path) -> None:
    first = [item.identifier for item in load_tables(example).items]
    again = [item.identifier for item in load_tables(example).items]
    other = [item.identifier for item in load_tables(example, agency="other.org").items]
    assert first == again
    assert not set(first) & set(other)


# ---------------------------------------------------------------------------
# Languages, audiences, custom properties and relationships
# ---------------------------------------------------------------------------


def test_labels_carry_every_language(example: Path) -> None:
    concept = _get(load_tables(example), "concepts", "AGE", Concept)
    assert [(s.lang, s.text) for s in concept.labels] == [("en", "Age"), ("fr", "Âge")]
    assert [(s.lang, s.text) for s in concept.names] == [("en", "Age")]


def test_question_texts_by_language_and_audience(example: Path) -> None:
    question = load_tables(example).get("questions", "Q_WORK")
    texts = question.to_xml().findall(qn(DATA_COLLECTION_NS, "QuestionText"))
    assert [t.get("audienceLanguage") for t in texts] == [
        "en",
        "fr",
        "en-x-proxy",
        "fr-x-proxy",
    ]
    proxy_fr = texts[3].findtext(
        f"{qn(DATA_COLLECTION_NS, 'LiteralText')}/{qn(DATA_COLLECTION_NS, 'Text')}"
    )
    assert proxy_fr is not None and proxy_fr.startswith("La semaine dernière")


def test_custom_columns_become_user_attribute_pairs(tmp_path: Path) -> None:
    folder = tmp_path / "t"
    _settings(folder)
    _write(
        folder,
        "concepts",
        [
            ["id", "custom:Steward", "custom:x:Raw", "# note"],
            ["AGE", "Demography", "kept as is", "ignored"],
        ],
    )
    concept = _get(load_tables(folder), "concepts", "AGE", Concept)
    assert [(p.key, p.value) for p in concept.user_attribute_pairs] == [
        ("extension:Steward", "Demography"),
        ("x:Raw", "kept as is"),
    ]


def test_relationships_resolve_by_id(example: Path) -> None:
    tables = load_tables(example)
    age_concept = _get(tables, "concepts", "AGE", Concept)
    demographics = tables.get("concepts", "DEMOGRAPHICS")
    assert [r.identifier for r in age_concept.subclass_of_references] == [
        demographics.identifier
    ]
    universe = _get(tables, "universes", "PERSONS_15", Universe)
    defining = universe.defining_concept_reference
    assert defining is not None and defining.identifier == demographics.identifier
    age = _get(tables, "variables", "AGE", Variable)
    assert [r.identifier for r in age.question_references] == [
        tables.get("questions", "Q_AGE").identifier
    ]
    assert [r.identifier for r in age.universe_references] == [universe.identifier]


def test_variable_takes_its_question_response_unless_it_has_its_own(
    example: Path,
) -> None:
    tables = load_tables(example)
    age = _get(tables, "variables", "AGE", Variable).variable_representation
    assert age is not None and age.numeric_representation is not None
    number_range = age.numeric_representation.number_range
    assert number_range is not None and number_range.high == "120"
    sex = _get(tables, "variables", "SEX", Variable).variable_representation
    assert sex is not None and sex.code_representation is not None
    code_list = sex.code_representation.code_list_reference
    assert code_list is not None
    assert code_list.identifier == tables.get("code_lists", "SEX_CODES").identifier
    person = _get(tables, "variables", "PERSON_ID", Variable).variable_representation
    assert person is not None and person.text_representation is not None
    assert person.text_representation.other_attributes == {"maxLength": "10"}


def test_codes_share_a_category_by_key(example: Path) -> None:
    tables = load_tables(example)
    sex = _get(tables, "code_lists", "SEX_CODES", CodeList)
    yes_no = _get(tables, "code_lists", "YES_NO", CodeList)
    sex_category, yes_no_category = sex.codes[2].category, yes_no.codes[2].category
    assert sex_category is not None and yes_no_category is not None
    assert sex_category.identifier == yes_no_category.identifier
    shared = [c for c in tables.categories if c.identifier == sex_category.identifier]
    assert shared[0].isMissing is True
    assert [s.text for s in shared[0].labels] == ["Not stated", "Non déclaré"]


def test_ddi_id_keeps_an_existing_identifier(tmp_path: Path) -> None:
    folder = tmp_path / "t"
    _settings(folder)
    _write(
        folder,
        "concepts",
        [
            ["id", "ddi_id", "version"],
            ["AGE", "4bf610ee-6771-44da-ab0b-00655b53b79b", "3"],
        ],
    )
    concept = _get(load_tables(folder), "concepts", "AGE", Concept)
    assert (concept.identifier, concept.version) == (
        "4bf610ee-6771-44da-ab0b-00655b53b79b",
        "3",
    )


_UUID = "4bf610ee-6771-44da-ab0b-00655b53b79b"


@pytest.mark.parametrize(
    ("ddi_id", "version", "expected"),
    [
        # A URN gives its identifier, and its version when the row has none.
        (f"urn:ddi:example.org:{_UUID}:3", "", (_UUID, "3")),
        # "urn:ddi:" and the agency are read whatever their case.
        (f"URN:DDI:Example.ORG:{_UUID}:3", "", (_UUID, "3")),
        # The row's own version wins over the URN's.
        (f"urn:ddi:example.org:{_UUID}:3", "4", (_UUID, "4")),
        # An identifier scoped to its maintainable has two parts.
        ("VS1.V1", "", ("VS1.V1", "1")),
    ],
)
def test_ddi_id_takes_a_urn_of_the_tables_agency(
    tmp_path: Path, ddi_id: str, version: str, expected: tuple[str, str]
) -> None:
    folder = tmp_path / "t"
    _settings(folder)
    _write(folder, "concepts", [["id", "ddi_id", "version"], ["AGE", ddi_id, version]])

    concept = _get(load_tables(folder), "concepts", "AGE", Concept)

    assert (concept.agency, concept.identifier, concept.version) == (
        "example.org",
        *expected,
    )


def test_unusable_ddi_ids_and_versions_are_reported_where_they_are(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "t"
    _settings(folder)
    deprecated = "urn:ddi:example.org:ConceptScheme:CS1:Concept:C1:1"
    _write(
        folder,
        "concepts",
        [
            ["id", "ddi_id", "version"],
            ["A", "my concept", ""],
            ["B", f"urn:ddi:other.org:{_UUID}:1", ""],
            ["C", deprecated, ""],
            ["D", "urn:ddi:example.org:C1", ""],
            ["E", "CS1.C1.X", ""],
            ["F", "", "v2"],
            ["G", _UUID, ""],
        ],
    )
    _write(
        folder,
        "universes",
        [["id", "ddi_id"], ["U", f"urn:ddi:example.org:{_UUID}:2"]],
    )

    assert _problems(folder) == [
        "concepts.csv, row 2, column ddi_id: 'my concept' is neither a DDI "
        "identifier nor a DDI URN (urn:ddi:agency:id:version)",
        "concepts.csv, row 3, column ddi_id: the URN's agency 'other.org' is not "
        "the tables' agency, 'example.org'",
        f"concepts.csv, row 4, column ddi_id: {deprecated!r} is a deprecated DDI "
        "URN; give its canonical form, urn:ddi:agency:id:version",
        "concepts.csv, row 5, column ddi_id: 'urn:ddi:example.org:C1' is not a "
        "DDI URN: expected urn:ddi:agency:id:version",
        "concepts.csv, row 6, column ddi_id: 'CS1.C1.X' is neither a DDI "
        "identifier nor a DDI URN (urn:ddi:agency:id:version)",
        "concepts.csv, row 7, column version: 'v2' is not a DDI version: "
        "whole numbers separated by dots, such as 1, 2 or 1.1",
        f"universes.csv, row 2, column ddi_id: {_UUID!r} is already the DDI "
        "identifier of concepts.csv, row 8",
    ]


@pytest.mark.parametrize(
    ("setting", "value", "expected"),
    [
        (
            "agency",
            "Statistics Canada",
            "agency 'Statistics Canada' is not a DDI agency: letters, digits "
            "and hyphens, in parts separated by dots, such as example.org",
        ),
        (
            "version",
            "v1",
            "version 'v1' is not a DDI version: whole numbers separated by "
            "dots, such as 1, 2 or 1.1",
        ),
    ],
)
def test_settings_agency_and_version_must_be_ddi_ones(
    tmp_path: Path, setting: str, value: str, expected: str
) -> None:
    folder = tmp_path / "t"
    _write(
        folder,
        "settings",
        [["setting", "value"], ["agency", "example.org"], [setting, value]],
    )
    _write(folder, "concepts", [["id"], ["C1"]])

    assert _problems(folder) == [f"settings: {expected}"]


def test_an_agency_passed_in_is_checked_too(tmp_path: Path) -> None:
    folder = tmp_path / "t"
    _settings(folder)
    _write(folder, "concepts", [["id"], ["C1"]])

    problems = _problems(folder, agency="my agency")

    assert problems == [
        "settings: agency 'my agency' is not a DDI agency: letters, digits and "
        "hyphens, in parts separated by dots, such as example.org"
    ]


def test_semicolon_csv_from_a_french_excel(tmp_path: Path) -> None:
    folder = tmp_path / "t"
    _write(
        folder, "settings", [["setting", "value"], ["agency", "example.org"]], sep=";"
    )
    _write(folder, "concepts", [["id", "label@fr"], ["AGE", "Âge, en années"]], sep=";")
    concept = _get(load_tables(folder), "concepts", "AGE", Concept)
    assert concept.labels[0].text == "Âge, en années"


# ---------------------------------------------------------------------------
# Problems are reported together, with where they are
# ---------------------------------------------------------------------------


def test_every_problem_is_reported_with_its_place(tmp_path: Path) -> None:
    folder = tmp_path / "t"
    _settings(folder)
    _write(
        folder,
        "concepts",
        [["id", "lable@en", "parent"], ["AGE", "Age", "NOPE"], ["AGE", "", ""]],
    )
    _write(
        folder,
        "questions",
        [["id", "text@en", "response"], ["Q1", "How old?", "numeric"]],
    )
    _write(
        folder,
        "question_texts",
        [
            ["question", "language", "audience", "text"],
            ["Q1", "en", "interviewer", "Ask the age."],
            ["Q1", "en", "", "Duplicate wording."],
        ],
    )
    _write(folder, "codes", [["code_list", "value", "missing"], ["CL", "1", "maybe"]])
    problems = _problems(folder)
    expected = [
        "concepts.csv, column lable@en: not a column of concepts",
        "concepts.csv, row 2, column parent: no row in concepts has id 'NOPE'",
        "concepts.csv, row 3, column id: 'AGE' is already the id of row 2",
        "codes.csv, row 2, column code_list: no row in code_lists has id 'CL'",
        "question_texts.csv, row 2, column audience: 'interviewer' does not fit",
        "question_texts.csv, row 3: a second wording for language en",
        "questions.csv, row 2, column numeric_type: response numeric needs",
    ]
    for start in expected:
        assert any(problem.startswith(start) for problem in problems), (start, problems)


def test_missing_agency_and_required_columns(tmp_path: Path) -> None:
    folder = tmp_path / "t"
    _write(folder, "codes", [["value"], ["1"]])
    problems = _problems(folder)
    assert any("no agency" in p for p in problems)
    assert any(
        p.startswith("codes.csv, column code_list: this required") for p in problems
    )


def test_unknown_sheet_in_a_workbook(tmp_path: Path) -> None:
    workbook = tmp_path / "t.xlsx"
    write_workbook(
        workbook,
        [
            ("settings", [["setting", "value"], ["agency", "example.org"]], True),
            ("concept", [["id"], ["AGE"]], True),
            ("README", [["anything"]], True),
        ],
    )
    problems = _problems(workbook)
    assert any(
        p.startswith("t.xlsx, sheet concept: not a known table") for p in problems
    )


def test_empty_source_is_reported(tmp_path: Path) -> None:
    folder = tmp_path / "t"
    _settings(folder)
    assert any("no rows found" in p for p in _problems(folder))


# ---------------------------------------------------------------------------
# Templates and downloads
# ---------------------------------------------------------------------------


def test_blank_template_has_language_columns(tmp_path: Path) -> None:
    folder = write_table_templates(tmp_path / "blank", languages=("en", "fr-CA"))
    header = (folder / "questions.csv").read_text(encoding="utf-8-sig").splitlines()[0]
    assert "text@en,text@fr-CA" in header
    assert (folder / "README.txt").is_file()


def test_blank_workbook_keeps_codes_as_text(tmp_path: Path) -> None:
    workbook = write_table_templates(tmp_path / "blank.xlsx", layout="xlsx")
    sheets = read_workbook(workbook)
    assert next(iter(sheets)) == "README"
    assert sheets["codes"][0][:2] == ["code_list", "value"]
    with zipfile.ZipFile(workbook) as archive:
        styles = archive.read("xl/styles.xml").decode()
    assert 'numFmtId="49"' in styles  # the text format, so 01 stays 01


def test_example_is_english_and_french_only(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="English and French"):
        write_table_templates(tmp_path / "x", example=True, languages=("en",))


def _zip_contents(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


@needs_docs
def test_committed_downloads_match_the_generator(tmp_path: Path) -> None:
    """docs/downloads holds what scripts/build_table_templates.py writes.

    Compared entry by entry, not byte for byte: zlib versions compress
    differently.
    """
    script = runpy.run_path(str(PROJECT_ROOT / "scripts" / "build_table_templates.py"))
    script["build"](tmp_path)
    committed = PROJECT_ROOT / "docs" / "downloads"
    for name in script["FILES"]:
        assert _zip_contents(tmp_path / name) == _zip_contents(committed / name), (
            f"{name} is stale: run uv run python scripts/build_table_templates.py"
        )


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def test_cli_template_then_import(
    tmp_path: Path, study_tables: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from ddi_l.cli import main

    assert main(["tables", "template", str(tmp_path / "ex"), "--example"]) == 0
    output = tmp_path / "out.xml"
    assert main(["tables", "import", str(tmp_path / "ex"), "-o", str(output)]) == 0
    fragment = ddi.open_fragment(output)
    assert len(fragment.items()) == sum(EXAMPLE_COUNTS.values())
    study = tmp_path / "study.xml"
    command = ["tables", "import", str(study_tables), "--study", "S", "-o", str(study)]
    assert main(command) == 0
    assert ddi.open_ddi(study).validate() == []
    capsys.readouterr()
    command[2] = str(tmp_path / "ex")
    assert main(command) == 1
    assert "studies: has rows; a study document has no place" in capsys.readouterr().err


def test_cli_import_reports_problems(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from ddi_l.cli import main

    folder = tmp_path / "t"
    _settings(folder)
    _write(folder, "variables", [["id", "question"], ["AGE", "Q_AGE"]])
    assert main(["tables", "import", str(folder)]) == 1
    assert "no row in questions has id 'Q_AGE'" in capsys.readouterr().err


def test_question_name_is_written(example: Path) -> None:
    question = load_tables(example).get("questions", "Q_AGE")
    name = question.to_xml().find(qn(DATA_COLLECTION_NS, "QuestionItemName"))
    assert name is not None and "Q_AGE" in tostring(name)


# ---------------------------------------------------------------------------
# Values each column checks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("table", "rows", "expected"),
    [
        (
            "questions",
            [["id", "response"], ["Q1", "slider"]],
            "column response: 'slider' is not one of code, numeric, text, datetime",
        ),
        (
            "questions",
            [["id", "response"], ["Q1", "code"]],
            "column code_list: response code needs a code list",
        ),
        (
            "questions",
            [
                ["id", "response", "numeric_type", "min"],
                ["Q1", "numeric", "Integer", "ten"],
            ],
            "column min: 'ten' is not a number",
        ),
        (
            "questions",
            [["id", "response", "max_length"], ["Q1", "text", "long"]],
            "column max_length: 'long' is not a whole number",
        ),
        (
            "questions",
            [["id", "response"], ["Q1", "datetime"]],
            "column date_type: response datetime needs a date_type",
        ),
        (
            "variables",
            [["id", "concept"], ["V1", "A|B"]],
            "column concept: no row in concepts has id 'A'",
        ),
        (
            "concepts",
            [["id", "parent"], ["C1", "C1"]],
            "column parent: a concept cannot be its own parent",
        ),
        ("concepts", [["id", "label"], ["C1", "x"]], "column label: needs a language"),
        ("concepts", [["id", "label@e n"], ["C1", "x"]], "is not a language tag"),
        ("concepts", [["id", "name@en"], ["C1", "x"]], "name does not take a language"),
        ("concepts", [["id", "custom:"], ["C1", "x"]], "custom: needs a name"),
        ("concepts", [["id", "id"], ["C1", "x"]], "column id appears twice"),
        ("concepts", [["id"], ["C1", "stray"]], "row 2: has values under no header"),
        ("concepts", [["name"], ["Age"]], "column id: is empty"),
        (
            "question_texts",
            [["question", "language", "text", "custom:x"], ["Q", "en", "t", "v"]],
            "question_texts takes no custom columns",
        ),
        (
            "question_texts",
            [["question", "language", "text"], ["NOPE", "e n", ""]],
            "column text: is empty",
        ),
        (
            "codes",
            [["code_list", "value"], ["", "1"]],
            "codes.csv, row 2, column code_list",
        ),
        (
            "studies",
            [["id", "identifier"], ["S", "10.5072/FK2"]],
            "column identifier_agency: say who manages the identifier '10.5072/FK2'",
        ),
        (
            "studies",
            [["id", "identifier_agency"], ["S", "DOI"]],
            "column identifier: identifier_agency is 'DOI' but there is no identifier",
        ),
    ],
)
def test_bad_values_are_reported(
    tmp_path: Path, table: str, rows: list[list[str]], expected: str
) -> None:
    folder = tmp_path / "t"
    _settings(folder)
    _write(folder, table, rows)
    if table == "codes":
        _write(folder, "code_lists", [["id"], ["CL"]])
    problems = _problems(folder)
    assert any(expected in problem for problem in problems), problems


def test_a_study_cites_its_identifier_copyright_and_licence(tmp_path: Path) -> None:
    """A study with questions and no questionnaire flow, as from DDI-Codebook."""
    folder = tmp_path / "t"
    _settings(folder)
    _write(
        folder,
        "studies",
        [
            [
                "id",
                "title@en",
                "identifier",
                "identifier_agency",
                "copyright@en",
                "copyright@fr",
                "license",
            ],
            [
                "PETS",
                "Pet survey",
                "10.5072/FK2PETS",
                "DOI",
                "Example Institute",
                "Institut Exemple",
                "https://creativecommons.org/licenses/by/4.0/",
            ],
        ],
    )
    _write(folder, "questions", [["id", "response"], ["Q1", "text"]])
    _write(folder, "variables", [["id", "question"], ["V1", "Q1"]])

    fragment = load_tables(folder).to_fragment()

    assert schema_loader.validate(fragment.root, raise_error=False) == []
    xml = fragment.to_colectica_bytes().decode("utf-8")
    assert "<r:IdentifierContent>10.5072/FK2PETS</r:IdentifierContent>" in xml
    assert "<r:ManagingAgency>DOI</r:ManagingAgency>" in xml
    assert '<r:String xml:lang="fr">Institut Exemple</r:String>' in xml
    assert (
        '<license xmlns="http://purl.org/dc/terms/">'
        "https://creativecommons.org/licenses/by/4.0/</license>"
    ) in xml
    # No questionnaire, so no data collection: DDI 3.3 needs none.
    assert fragment.root.find(f".//{qn(DATA_COLLECTION_NS, 'DataCollection')}") is None


def test_a_data_file_labels_its_relationship_and_its_record(tmp_path: Path) -> None:
    folder = tmp_path / "t"
    _settings(folder)
    _write(folder, "datasets", [["id", "label@en"], ["F1", "Pet survey data"]])
    _write(
        folder,
        "variables",
        [["id", "label@en", "representation", "dataset"], ["V1", "Name", "text", "F1"]],
    )

    fragment = load_tables(folder).to_fragment()

    assert schema_loader.validate(fragment.root, raise_error=False) == []
    assert run_lint(fragment) == []
    xml = fragment.to_colectica_bytes().decode("utf-8")
    assert xml.count('<r:Content xml:lang="en">Pet survey data</r:Content>') == 2


def test_settings_problems(tmp_path: Path) -> None:
    folder = tmp_path / "t"
    _write(
        folder,
        "settings",
        [
            ["setting", "value"],
            ["agency", "example.org"],
            ["colour", "blue"],
            ["version", ""],
            ["language", "english please"],
        ],
    )
    _write(folder, "concepts", [["id"], ["C1"]])
    problems = _problems(folder)
    assert any("unknown setting 'colour'" in p for p in problems)
    assert any("column value: is empty" in p for p in problems)
    assert any("language 'english please' is not a language tag" in p for p in problems)


def test_duplicate_code_and_booleans(tmp_path: Path) -> None:
    folder = tmp_path / "t"
    _settings(folder)
    _write(folder, "code_lists", [["id"], ["CL"]])
    _write(
        folder,
        "codes",
        [
            ["code_list", "value", "missing"],
            ["CL", "1", "non"],
            ["CL", "1", ""],
        ],
    )
    problems = _problems(folder)
    assert any("'1' is already a code of CL (row 2)" in p for p in problems)


def test_workbook_cells_of_every_kind(tmp_path: Path) -> None:
    """Shared strings, numbers, booleans and gaps, as Excel itself writes."""
    workbook = tmp_path / "excel.xlsx"
    sheet = (
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<sheetData>"
        '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c>'
        '<c r="C1" t="s"><v>2</v></c></row>'
        '<row r="3"><c r="A3" t="s"><v>3</v></c><c r="B3"><v>2.0</v></c>'
        '<c r="C3" t="b"><v>1</v></c></row>'
        "</sheetData></worksheet>"
    )
    shared = (
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<si><t>code_list</t></si><si><t>value</t></si><si><t>missing</t></si>"
        "<si><r><t>C</t></r><r><t>L</t></r></si></sst>"
    )
    main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    pkg = "http://schemas.openxmlformats.org/package/2006/relationships"
    with zipfile.ZipFile(workbook, "w") as archive:
        archive.writestr(
            "xl/workbook.xml",
            f'<workbook xmlns="{main}" xmlns:r="{rel}"><sheets>'
            '<sheet name="codes" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            f'<Relationships xmlns="{pkg}"><Relationship Id="rId1" '
            f'Type="{rel}/worksheet" Target="/xl/worksheets/sheet1.xml"/>'
            "</Relationships>",
        )
        archive.writestr("xl/worksheets/sheet1.xml", sheet)
        archive.writestr("xl/sharedStrings.xml", shared)
    rows = read_workbook(workbook)["codes"]
    assert rows == [["code_list", "value", "missing"], [], ["CL", "2", "true"]]


def test_source_that_is_neither_folder_nor_workbook(tmp_path: Path) -> None:
    text = tmp_path / "tables.txt"
    text.write_text("x")
    with pytest.raises(TableImportError, match="neither a folder"):
        load_tables(text)
    with pytest.raises(TableImportError, match="does not exist"):
        load_tables(tmp_path / "missing")


def test_unknown_layout(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="layout"):
        write_table_templates(tmp_path / "x", layout="ods")  # type: ignore[arg-type]


@needs_docs
@pytest.mark.parametrize("lang", ["en", "fr"])
def test_every_column_is_documented(lang: str) -> None:
    """The guide lists every table and column the loader accepts."""
    from ddi_l.tables import TABLES

    page = (PROJECT_ROOT / "docs" / f"spreadsheet-import.{lang}.md").read_text(
        encoding="utf-8"
    )
    for table in TABLES:
        assert f"### {table.name}" in page or f"`{table.name}`" in page, table.name
        for column in table.columns:
            assert f"`{column.name}" in page, (table.name, column.name)


# ---------------------------------------------------------------------------
# A zip of CSV files, and what an untrusted file may make the reader do
# ---------------------------------------------------------------------------


def _zip(path: Path, entries: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return path


@_STUDY_REFERENCES
def test_a_zip_of_csv_files_loads_like_the_folder(
    example: Path, tmp_path: Path
) -> None:
    entries = {
        f"my-survey/{path.name}": path.read_bytes() for path in example.iterdir()
    }
    entries["__MACOSX/my-survey/._concepts.csv"] = b"\x00\x01"
    archive = _zip(tmp_path / "tables.zip", entries)
    from_folder = [tostring(item.to_xml()) for item in load_tables(example).items]
    from_zip = [tostring(item.to_xml()) for item in load_tables(archive).items]
    assert from_zip == from_folder


def test_zip_problems_name_the_file(tmp_path: Path) -> None:
    archive = _zip(
        tmp_path / "tables.zip",
        {
            "settings.csv": b"setting,value\r\nagency,example.org\r\n",
            "concept.csv": b"id\r\nAGE\r\n",
            "a/concepts.csv": b"id\r\nAGE\r\n",
            "b/concepts.csv": b"id\r\nSEX\r\n",
            "variables.csv": "id,label@fr\r\nAGE,\xc2ge\r\n".encode("latin-1"),
        },
    )
    problems = _problems(archive)
    assert any(p.startswith("concept.csv: not a known table") for p in problems)
    assert any(
        p == "b/concepts.csv: a second concepts.csv; the first is a/concepts.csv"
        for p in problems
    )
    assert "variables.csv: is not UTF-8 text; save it as CSV UTF-8" in problems


@pytest.mark.parametrize(
    ("name", "data", "expected"),
    [
        ("t.xlsx", b"not a zip", "t.xlsx is not a readable .xlsx workbook"),
        ("t.zip", b"not a zip", "t.zip is not a readable .zip of CSV files"),
    ],
)
def test_unreadable_archives_are_reported(
    tmp_path: Path, name: str, data: bytes, expected: str
) -> None:
    source = tmp_path / name
    source.write_bytes(data)
    with pytest.raises(TableImportError, match=expected):
        load_tables(source)


def _sheet_workbook(path: Path, sheet_xml: str) -> Path:
    main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    pkg = "http://schemas.openxmlformats.org/package/2006/relationships"
    return _zip(
        path,
        {
            "xl/workbook.xml": (
                f'<workbook xmlns="{main}" xmlns:r="{rel}"><sheets>'
                '<sheet name="concepts" sheetId="1" r:id="rId1"/></sheets></workbook>'
            ).encode(),
            "xl/_rels/workbook.xml.rels": (
                f'<Relationships xmlns="{pkg}"><Relationship Id="rId1" '
                f'Type="{rel}/worksheet" Target="worksheets/sheet1.xml"/>'
                "</Relationships>"
            ).encode(),
            "xl/worksheets/sheet1.xml": (
                f'<worksheet xmlns="{main}"><sheetData>{sheet_xml}</sheetData>'
                "</worksheet>"
            ).encode(),
        },
    )


@pytest.mark.parametrize(
    ("sheet", "expected"),
    [
        (
            '<row r="2000000"><c r="A2000000" t="inlineStr"><is><t>x</t></is></c></row>',
            "row 2000000 is beyond Excel's last row",
        ),
        (
            '<row r="1"><c r="ZZZZ1" t="inlineStr"><is><t>x</t></is></c></row>',
            "cell ZZZZ1 is beyond Excel's last column",
        ),
    ],
)
def test_a_workbook_cannot_ask_for_endless_rows_or_columns(
    tmp_path: Path, sheet: str, expected: str
) -> None:
    """A row number of two million would otherwise pad two million rows."""
    workbook = _sheet_workbook(tmp_path / "t.xlsx", sheet)
    with pytest.raises(TableImportError, match=expected):
        load_tables(workbook, agency="example.org")


def test_an_archive_that_expands_too_far_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ddi_l.tables import _xlsx

    monkeypatch.setattr(_xlsx, "MAX_UNCOMPRESSED_BYTES", 1000)
    archive = _zip(tmp_path / "t.zip", {"concepts.csv": b"id\r\n" + b"A\r\n" * 600})
    with pytest.raises(TableImportError, match="expands to more than"):
        load_tables(archive, agency="example.org")


@_STUDY_REFERENCES
def test_bytes_load_in_memory_like_the_file(tmp_path: Path) -> None:
    workbook = write_table_templates(tmp_path / "t.xlsx", example=True, layout="xlsx")
    from_file = [tostring(item.to_xml()) for item in load_tables(workbook).items]
    from_bytes = [
        tostring(item.to_xml()) for item in load_tables(workbook.read_bytes()).items
    ]
    assert from_bytes == from_file
    with pytest.raises(TableImportError, match="not an .xlsx workbook or a .zip"):
        load_tables(b"plain text")
    empty = _zip(
        tmp_path / "empty.zip",
        {"settings.csv": b"setting,value\r\nagency,example.org\r\n"},
    )
    with pytest.raises(TableImportError) as raised:
        load_tables(empty.read_bytes())
    assert str(raised.value.problems[0]).startswith("tables.zip: no rows found")
