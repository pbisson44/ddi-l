"""What the rows of each table become: studies and people, the variable
cascade, code hierarchies, questionnaires and their flow, data files,
methodology, processing, quality and comparisons."""

from __future__ import annotations

from pathlib import Path

import pytest

from ddi_l._etree import Element
from ddi_l.models.base import MaintainableBase
from ddi_l.models.study import StudyUnit
from ddi_l.tables import (
    TableImport,
    TableImportError,
    load_tables,
    write_table_templates,
)
from tests.helpers.tables import child, children, local, problems, ref_id, tables, text


@pytest.fixture(scope="module")
def loaded(tmp_path_factory: pytest.TempPathFactory) -> TableImport:
    folder = tmp_path_factory.mktemp("tables") / "example"
    return load_tables(write_table_templates(folder, example=True))


def _xml(item: MaintainableBase) -> Element:
    if isinstance(item, StudyUnit):
        # Its references point at items in other fragments.
        return item.to_xml(validate_refs=False)
    return item.to_xml()


def xml(loaded: TableImport, table: str, key: str) -> Element:
    return _xml(loaded.get(table, key))


def implied(loaded: TableImport, table: str, tag: str) -> list[Element]:
    """Elements of the items ``table`` implies, of type ``tag``."""
    found = [_xml(item) for item in loaded.tables.get(table, [])]
    return [element for element in found if local(element) == tag]


def by_id(loaded: TableImport, table: str, identifier: str | None) -> Element:
    for item in loaded.tables[table]:
        if item.identifier == identifier:
            return _xml(item)
    raise AssertionError(f"no item {identifier} under {table}")


def ids(loaded: TableImport, table: str, *keys: str) -> list[str | None]:
    return [loaded.get(table, key).identifier for key in keys]


def refs(element: Element, name: str) -> list[str | None]:
    return [ref_id(found) for found in children(element, name)]


# ---------------------------------------------------------------------------
# Studies, groups and people
# ---------------------------------------------------------------------------


def test_study_citation_names_its_people(loaded: TableImport) -> None:
    citation = child(xml(loaded, "studies", "ELS_2024"), "Citation")
    assert [s.text for s in child(citation, "Title")] == [
        "Example Labour Survey, 2024",
        "Enquête exemple sur le travail, 2024",
    ]
    creators = [
        ref_id(child(c, "CreatorReference")) for c in children(citation, "Creator")
    ]
    assert creators == [
        *ids(loaded, "organizations", "EXAMPLE_STATS"),
        *ids(loaded, "individuals", "J_DOE"),
    ]
    publisher = child(child(citation, "Publisher"), "PublisherReference")
    assert ref_id(publisher) == loaded.get("organizations", "EXAMPLE_STATS").identifier
    assert text(citation, "PublicationDate", "SimpleDate") == "2025-03-15"


def test_study_coverage_funding_and_kinds(loaded: TableImport) -> None:
    study = xml(loaded, "studies", "ELS_2024")
    coverage = child(study, "Coverage")
    keywords = children(child(coverage, "TopicalCoverage"), "Keyword")
    assert [k.text for k in keywords] == ["labour", "employment", "travail", "emploi"]
    assert text(coverage, "SpatialCoverage", "CountryCode") == "CA"
    assert (
        text(coverage, "TemporalCoverage", "ReferenceDate", "StartDate") == "2024-01-01"
    )
    assert (
        text(coverage, "TemporalCoverage", "ReferenceDate", "EndDate") == "2024-12-31"
    )
    funding = child(study, "FundingInformation")
    assert refs(funding, "AgencyOrganizationReference") == ids(
        loaded, "organizations", "EXAMPLE_STATS"
    )
    assert text(funding, "GrantNumber") == "G-2024-01"
    assert text(study, "KindOfData") == "Survey data"
    assert text(study, "AnalysisUnit") == "Persons"
    assert refs(study, "UniverseReference") == ids(loaded, "universes", "PERSONS_15")
    assert refs(study, "DefiningConceptReference") == ids(loaded, "concepts", "WORK")


def test_study_links_its_data_collection_files_and_quality(loaded: TableImport) -> None:
    study = xml(loaded, "studies", "ELS_2024")
    (collection,) = implied(loaded, "studies", "DataCollection")
    assert refs(study, "DataCollectionReference") == [text(collection, "ID")]
    assert refs(collection, "InstrumentReference") == ids(
        loaded, "instruments", "ELS_WEB"
    )
    assert refs(collection, "MethodologyReference") == ids(
        loaded, "methodologies", "ELS_METHOD"
    )
    (scheme,) = implied(loaded, "processing_events", "ProcessingEventScheme")
    assert refs(collection, "ProcessingEventSchemeReference") == [text(scheme, "ID")]
    assert refs(scheme, "ProcessingEventReference") == ids(
        loaded, "processing_events", "PE_EDIT", "PE_WEIGHT"
    )
    assert refs(study, "PhysicalInstanceReference") == ids(
        loaded, "datasets", "PERSONS"
    )
    assert refs(study, "QualityStatementReference") == ids(
        loaded, "quality_statements", "QS_SMALL"
    )


def test_creator_that_is_no_id_is_a_name(tmp_path: Path) -> None:
    folder = tables(
        tmp_path / "t", studies=[["id", "creator"], ["S", "Jane Roe|Data Unit"]]
    )
    citation = child(xml(load_tables(folder), "studies", "S"), "Citation")
    names = [text(c, "CreatorName", "String") for c in children(citation, "Creator")]
    assert names == ["Jane Roe", "Data Unit"]
    assert text(citation, "Title", "String") == "S"


def test_rows_without_a_study_join_the_only_one(tmp_path: Path) -> None:
    folder = tables(
        tmp_path / "t",
        studies=[["id", "title@en"], ["S", "Survey"]],
        instruments=[["id"], ["WEB"]],
        datasets=[["id"], ["FILE"]],
    )
    loaded = load_tables(folder)
    (collection,) = implied(loaded, "studies", "DataCollection")
    assert refs(collection, "InstrumentReference") == ids(loaded, "instruments", "WEB")
    assert refs(xml(loaded, "studies", "S"), "PhysicalInstanceReference") == ids(
        loaded, "datasets", "FILE"
    )


def test_groups_hold_studies_and_subgroups(loaded: TableImport, tmp_path: Path) -> None:
    group = xml(loaded, "groups", "ELS_SERIES")
    assert text(group, "TypeOfGroup") == "Series"
    assert refs(group, "StudyUnitReference") == ids(loaded, "studies", "ELS_2024")
    folder = tables(
        tmp_path / "t",
        groups=[["id", "parent"], ["PROGRAM", ""], ["SERIES", "PROGRAM"]],
    )
    nested = load_tables(folder)
    assert refs(xml(nested, "groups", "PROGRAM"), "GroupReference") == ids(
        nested, "groups", "SERIES"
    )


def test_organizations_and_individuals(loaded: TableImport) -> None:
    organization = xml(loaded, "organizations", "EXAMPLE_STATS")
    name = child(child(organization, "OrganizationIdentification"), "OrganizationName")
    assert [s.text for s in children(name, "String")] == [
        "Example Statistics Agency",
        "Agence exemple de la statistique",
    ]
    assert text(name, "Abbreviation", "String") == "ESA"
    contact = child(organization, "ContactInformation")
    assert text(contact, "URL") == "https://example.org"
    assert text(contact, "Email", "InternetEmail") == "info@example.org"
    person = child(
        child(xml(loaded, "individuals", "J_DOE"), "IndividualIdentification"),
        "IndividualName",
    )
    assert (text(person, "FirstGiven"), text(person, "LastFamily")) == ("Jordan", "Doe")


# ---------------------------------------------------------------------------
# The variable cascade and code hierarchies
# ---------------------------------------------------------------------------


def test_unit_type_without_a_concept_gets_colectica_placeholder(
    loaded: TableImport, tmp_path: Path
) -> None:
    concept = child(xml(loaded, "unit_types", "PERSON"), "ConceptReference")
    assert text(concept, "ID") == "00000000-0000-0000-0000-000000000000"
    assert text(concept, "UserAttributePair", "AttributeKey") == "x:informational"
    folder = tables(
        tmp_path / "t",
        concepts=[["id"], ["PEOPLE"]],
        unit_types=[["id", "concept"], ["PERSON", "PEOPLE"]],
    )
    named = load_tables(folder)
    assert refs(xml(named, "unit_types", "PERSON"), "ConceptReference") == ids(
        named, "concepts", "PEOPLE"
    )


def test_conceptual_and_represented_variables(loaded: TableImport) -> None:
    conceptual = xml(loaded, "conceptual_variables", "CV_AGE")
    assert refs(conceptual, "ConceptReference") == ids(loaded, "concepts", "AGE")
    assert refs(conceptual, "UniverseReference") == ids(
        loaded, "universes", "PERSONS_15"
    )
    assert refs(conceptual, "UnitTypeReference") == ids(loaded, "unit_types", "PERSON")
    represented = xml(loaded, "represented_variables", "RV_AGE")
    assert refs(represented, "ConceptualVariableReference") == ids(
        loaded, "conceptual_variables", "CV_AGE"
    )
    assert text(represented, "NumericRepresentation", "NumericTypeCode") == "Integer"
    variable = xml(loaded, "variables", "AGE")
    assert refs(variable, "RepresentedVariableReference") == ids(
        loaded, "represented_variables", "RV_AGE"
    )
    assert refs(variable, "ConceptualVariableReference") == ids(
        loaded, "conceptual_variables", "CV_AGE"
    )
    assert refs(variable, "UnitTypeReference") == ids(loaded, "unit_types", "PERSON")


def test_variable_takes_its_represented_variable_before_its_question(
    tmp_path: Path,
) -> None:
    folder = tables(
        tmp_path / "t",
        represented_variables=[
            ["id", "representation", "max_length"],
            ["RV", "text", "3"],
        ],
        questions=[["id", "response", "numeric_type"], ["Q", "numeric", "Integer"]],
        variables=[["id", "represented_variable", "question"], ["V", "RV", "Q"]],
    )
    representation = child(
        xml(load_tables(folder), "variables", "V"), "VariableRepresentation"
    )
    assert [local(c) for c in representation] == ["TextRepresentation"]


def test_represented_variable_without_a_conceptual_one(tmp_path: Path) -> None:
    folder = tables(
        tmp_path / "t",
        concepts=[["id"], ["C"]],
        unit_types=[["id"], ["U"]],
        represented_variables=[
            ["id", "concept", "unit_type", "representation", "date_type"],
            ["RV", "C", "U", "datetime", "Date"],
        ],
    )
    loaded = load_tables(folder)
    represented = xml(loaded, "represented_variables", "RV")
    assert refs(represented, "ConceptReference") == ids(loaded, "concepts", "C")
    assert refs(represented, "UnitTypeReference") == ids(loaded, "unit_types", "U")
    assert text(represented, "DateTimeRepresentation", "DateTypeCode") == "Date"


def test_codes_nest_under_their_parent(loaded: TableImport) -> None:
    code_list = xml(loaded, "code_lists", "OCCUPATIONS")
    top = children(code_list, "Code")
    assert [text(code, "Value") for code in top] == ["1", "2"]
    assert [text(code, "Value") for code in children(top[0], "Code")] == ["11", "12"]
    assert [text(code, "Value") for code in children(top[1], "Code")] == ["21"]


# ---------------------------------------------------------------------------
# Questions and the questionnaire
# ---------------------------------------------------------------------------


def test_instructions_attach_to_questions(loaded: TableImport) -> None:
    instruction = xml(loaded, "instructions", "INS_AGE")
    texts = children(instruction, "InstructionText")
    assert [t.get("audienceLanguage") for t in texts] == ["en", "fr"]
    assert (
        text(texts[1], "LiteralText", "Text") == "Inscrivez l'âge en années révolues."
    )
    assert refs(
        xml(loaded, "questions", "Q_AGE"), "InterviewerInstructionReference"
    ) == (ids(loaded, "instructions", "INS_AGE"))


def test_grid_block_and_question_groups(loaded: TableImport) -> None:
    grid = xml(loaded, "question_grids", "G_SATISFACTION")
    (dimension,) = children(grid, "GridDimension")
    assert dimension.get("rank") == "1"
    assert refs(child(dimension, "CodeDomain"), "CodeListReference") == ids(
        loaded, "code_lists", "JOB_ASPECTS"
    )
    assert refs(child(grid, "CodeDomain"), "CodeListReference") == ids(
        loaded, "code_lists", "SATISFACTION"
    )
    block = xml(loaded, "question_blocks", "B_JOB")
    assert refs(block, "QuestionGridReference") == ids(
        loaded, "question_grids", "G_SATISFACTION"
    )
    assert refs(
        xml(loaded, "question_groups", "MOD_DEMO"), "QuestionItemReference"
    ) == (ids(loaded, "questions", "Q_AGE", "Q_SEX"))
    work = xml(loaded, "question_groups", "MOD_WORK")
    assert refs(work, "QuestionItemReference") == ids(loaded, "questions", "Q_WORK")
    assert refs(work, "QuestionGridReference") == ids(
        loaded, "question_grids", "G_SATISFACTION"
    )
    assert refs(
        xml(loaded, "question_groups", "MOD_ALL"), "QuestionGroupReference"
    ) == (ids(loaded, "question_groups", "MOD_DEMO", "MOD_WORK"))


def test_block_of_questions_and_nested_variable_groups(tmp_path: Path) -> None:
    folder = tables(
        tmp_path / "t",
        questions=[["id", "response", "max_length"], ["Q", "text", "40"]],
        question_blocks=[["id", "questions"], ["B", "Q"]],
        variable_groups=[["id", "parent"], ["ALL", ""], ["SOME", "ALL"]],
    )
    loaded = load_tables(folder)
    assert refs(xml(loaded, "question_blocks", "B"), "QuestionItemReference") == ids(
        loaded, "questions", "Q"
    )
    assert child(xml(loaded, "questions", "Q"), "TextDomain").get("maxLength") == "40"
    assert refs(xml(loaded, "variable_groups", "ALL"), "VariableGroupReference") == (
        ids(loaded, "variable_groups", "SOME")
    )


def _members(loaded: TableImport, sequence: Element) -> list[str | None]:
    return refs(sequence, "ControlConstructReference")


def test_flow_builds_the_questionnaire(loaded: TableImport) -> None:
    instrument = xml(loaded, "instruments", "ELS_WEB")
    (top_id,) = refs(instrument, "ControlConstructReference")
    top = by_id(loaded, "flow", top_id)
    assert _members(loaded, top) == ids(
        loaded, "flow", "F_INTRO", "F_DEMO", "F_IF_15", "F_END"
    )
    kinds = [
        text(r, "TypeOfObject") for r in children(top, "ControlConstructReference")
    ]
    assert kinds == ["StatementItem", "Sequence", "IfThenElse", "StatementItem"]
    assert _members(loaded, xml(loaded, "flow", "F_DEMO")) == ids(
        loaded, "flow", "F_AGE", "F_SEX"
    )
    condition = xml(loaded, "flow", "F_IF_15")
    command = child(child(condition, "IfCondition"), "Command")
    assert (text(command, "ProgramLanguage"), text(command, "CommandContent")) == (
        "pseudo-code",
        "AGE >= 15",
    )
    then = by_id(loaded, "flow", ref_id(child(condition, "ThenConstructReference")))
    assert _members(loaded, then) == ids(loaded, "flow", "F_WORK", "F_IF_WORKED")
    otherwise = by_id(
        loaded, "flow", ref_id(child(condition, "ElseConstructReference"))
    )
    assert _members(loaded, otherwise) == ids(loaded, "flow", "F_TOO_YOUNG")
    loop = xml(loaded, "flow", "F_JOBS")
    assert text(loop, "LoopWhile", "Command", "CommandContent") == "job <= JOB_COUNT"
    (body_id,) = _members(loaded, loop)
    assert _members(loaded, by_id(loaded, "flow", body_id)) == ids(
        loaded, "flow", "F_JOB"
    )
    question = child(xml(loaded, "flow", "F_JOB"), "QuestionReference")
    assert text(question, "TypeOfObject") == "QuestionBlock"
    assert ref_id(question) == loaded.get("question_blocks", "B_JOB").identifier
    intro = children(xml(loaded, "flow", "F_INTRO"), "DisplayText")
    assert [t.get("audienceLanguage") for t in intro] == ["en", "fr"]


# ---------------------------------------------------------------------------
# Variables, data files and n-cubes
# ---------------------------------------------------------------------------


def test_variable_groups_list_their_variables(loaded: TableImport) -> None:
    group = xml(loaded, "variable_groups", "VG_DEMO")
    assert text(group, "TypeOfVariableGroup") == "Topic"
    assert refs(group, "VariableReference") == ids(loaded, "variables", "AGE", "SEX")


def test_dataset_lists_its_variables_in_order(loaded: TableImport) -> None:
    instance = xml(loaded, "datasets", "PERSONS")
    assert children(instance, "Label") == []
    assert text(instance, "DataFileIdentification", "DataFileURI") == (
        "data/els2024_persons.csv"
    )
    (relationship_id,) = refs(instance, "DataRelationshipReference")
    relationship = by_id(loaded, "datasets", relationship_id)
    record = child(relationship, "LogicalRecord")
    assert text(record, "Label", "Content") == "One record per respondent"
    assert refs(child(record, "VariablesInRecord"), "VariableUsedReference") == ids(
        loaded, "variables", "PERSON_ID", "AGE", "SEX", "WORKED", "OCCUPATION"
    )


def test_ncube_dimensions_are_ranked(loaded: TableImport) -> None:
    cube = xml(loaded, "ncubes", "WORK_BY_SEX")
    dimensions = children(cube, "Dimension")
    assert [d.get("rank") for d in dimensions] == ["1", "2"]
    assert [ref_id(child(d, "VariableReference")) for d in dimensions] == ids(
        loaded, "variables", "SEX", "WORKED"
    )
    assert cube.get("dimensionCount") == "2"


# ---------------------------------------------------------------------------
# Methodology, processing, quality and comparisons
# ---------------------------------------------------------------------------


def test_methodology_parts_have_identities_and_descriptions(
    loaded: TableImport,
) -> None:
    methodology = xml(loaded, "methodologies", "ELS_METHOD")
    parts = [
        "DataCollectionMethodology",
        "TimeMethod",
        "WeightingMethodology",
        "SamplingProcedure",
        "DeviationFromSampleDesign",
    ]
    for name in parts:
        part = child(methodology, name)
        assert text(part, "ID")
        assert len(children(child(part, "Description"), "Content")) == 2


def test_processing_event_operations(loaded: TableImport) -> None:
    editing = xml(loaded, "processing_events", "PE_EDIT")
    assert text(editing, "ControlOperation", "Description", "Content") == (
        "Range and consistency edits."
    )
    assert text(
        editing, "DataAppraisalInformation", "OtherAppraisalProcess", "Content"
    ) == ("Response rate: 62%.")
    weighting = child(xml(loaded, "processing_events", "PE_WEIGHT"), "Weighting")
    assert text(weighting, "ID")


def test_quality_statement_text(loaded: TableImport) -> None:
    statement = xml(loaded, "quality_statements", "QS_SMALL")
    assert len(children(child(statement, "OtherStatementOfQuality"), "Content")) == 2


def test_comparisons_make_maps(loaded: TableImport, tmp_path: Path) -> None:
    (concept_map,) = [_xml(item) for item in loaded.tables["comparisons"]]
    assert local(concept_map) == "ConceptMap"
    assert text(concept_map, "MapName", "String") == "AGE_2023_2024"
    (item_map,) = children(concept_map, "ItemMap")
    assert refs(item_map, "SourceItemReference") == ids(loaded, "concepts", "AGE_2023")
    assert refs(item_map, "TargetItemReference") == ids(loaded, "concepts", "AGE")
    correspondence = child(item_map, "Correspondence")
    assert text(correspondence, "CommonalityWeight") == "0.9"
    assert len(children(child(correspondence, "Difference"), "Content")) == 2
    folder = tables(
        tmp_path / "t",
        code_lists=[["id"], ["OLD"], ["NEW"]],
        codes=[
            ["code_list", "value", "category"],
            ["OLD", "1", ""],
            ["NEW", "1", "SHARED"],
        ],
        comparisons=[
            ["map", "type", "source", "target"],
            ["M", "category", "OLD/1", "SHARED"],
        ],
    )
    (category_map,) = [_xml(item) for item in load_tables(folder).tables["comparisons"]]
    assert local(category_map) == "CategoryMap"
    item_map = child(category_map, "ItemMap")
    assert text(item_map, "SourceItemReference", "TypeOfObject") == "Category"


def test_to_study_refuses_tables_a_study_has_no_place_for(loaded: TableImport) -> None:
    with pytest.raises(TableImportError) as raised:
        loaded.to_study("Example")
    named = {str(problem).split(":")[0] for problem in raised.value.problems}
    assert named == {
        "studies",
        "groups",
        "organizations",
        "individuals",
        "variable_groups",
        "processing_events",
        "quality_statements",
        "comparisons",
    }


# ---------------------------------------------------------------------------
# Problems
# ---------------------------------------------------------------------------

_INSTRUMENT = {"instruments": [["id"], ["I"], ["J"]]}


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        (
            {
                **_INSTRUMENT,
                "flow": [["instrument", "id", "type"], ["I", "F", "maybe"]],
            },
            "flow.csv, row 2, column type: 'maybe' is not one of question, "
            "statement, sequence, if, loop",
        ),
        (
            {**_INSTRUMENT, "flow": [["instrument", "id", "type"], ["I", "F", ""]]},
            "column type: is empty",
        ),
        (
            {
                **_INSTRUMENT,
                "questions": [["id"], ["Q"]],
                "flow": [
                    ["instrument", "id", "type", "parent", "question"],
                    ["I", "F1", "question", "", "Q"],
                    ["I", "F2", "question", "F1", "Q"],
                ],
            },
            "row 3, column parent: 'F1' is a question step; only a sequence, if "
            "or loop holds other steps",
        ),
        (
            {
                **_INSTRUMENT,
                "flow": [
                    ["instrument", "id", "type", "parent", "branch", "text@en"],
                    ["I", "S", "sequence", "", "", ""],
                    ["I", "F", "statement", "S", "else", "Hi"],
                ],
            },
            "row 3, column branch: is only for a step inside an if",
        ),
        (
            {
                **_INSTRUMENT,
                "flow": [
                    [
                        "instrument",
                        "id",
                        "type",
                        "parent",
                        "branch",
                        "condition",
                        "text@en",
                    ],
                    ["I", "C", "if", "", "", "X = 1", ""],
                    ["I", "F", "statement", "C", "maybe", "", "Hi"],
                ],
            },
            "row 3, column branch: 'maybe' is not then or else",
        ),
        (
            {
                **_INSTRUMENT,
                "flow": [
                    ["instrument", "id", "type", "parent", "text@en"],
                    ["I", "S", "sequence", "", ""],
                    ["J", "F", "statement", "S", "Hi"],
                ],
            },
            "row 3, column parent: 'S' is in instrument I, not J",
        ),
        (
            {**_INSTRUMENT, "flow": [["instrument", "id", "type"], ["I", "C", "loop"]]},
            "column condition: loop needs a condition",
        ),
        (
            {
                **_INSTRUMENT,
                "flow": [["instrument", "id", "type"], ["I", "Q", "question"]],
            },
            "column question: a question step needs a question",
        ),
        (
            {
                **_INSTRUMENT,
                "flow": [["instrument", "id", "type"], ["I", "T", "statement"]],
            },
            "column text: a statement needs its text",
        ),
        (
            {
                **_INSTRUMENT,
                "flow": [
                    ["instrument", "id", "type", "parent"],
                    ["I", "S", "sequence", "NOPE"],
                ],
            },
            "column parent: no row in flow has id 'NOPE'",
        ),
        (
            {
                **_INSTRUMENT,
                "flow": [["instrument", "id", "type"], ["", "S", "sequence"]],
            },
            "column instrument: is empty",
        ),
        (
            {
                **_INSTRUMENT,
                "flow": [
                    ["instrument", "id", "type", "parent"],
                    ["I", "A", "sequence", "B"],
                    ["I", "B", "sequence", "A"],
                ],
            },
            "column parent: 'A' ends up inside itself: A > B > A",
        ),
        (
            {
                **_INSTRUMENT,
                "flow": [
                    ["instrument", "id", "type", "branch", "text@en"],
                    ["I", "T", "statement", "then", "Hi"],
                ],
            },
            "row 2, column branch: is only for a step inside an if",
        ),
        (
            {
                "concepts": [["id"], ["A"], ["B"]],
                "universes": [["id", "concept"], ["U", "A|B"]],
            },
            "column concept: takes one id, not several",
        ),
        (
            {
                "code_lists": [["id"], ["CL"]],
                "codes": [
                    ["code_list", "value", "missing"],
                    ["CL", "", ""],
                    ["X", "1", "maybe"],
                ],
            },
            "row 2, column value: is empty",
        ),
        (
            {"codes": [["code_list", "value", "missing"], ["X", "1", "maybe"]]},
            "column missing: 'maybe' is not true or false",
        ),
        (
            {
                "questions": [["id"], ["Q"]],
                "question_texts": [
                    ["question", "language", "text"],
                    ["Q", "en_CA", "Hi"],
                ],
            },
            "column language: 'en_CA' is not a language tag",
        ),
        (
            {"groups": [["id", "parent"], ["G", "G"]]},
            "column parent: a group cannot be its own parent",
        ),
        (
            {"question_groups": [["id", "parent"], ["A", "B"], ["B", "A"]]},
            "'A' ends up inside itself",
        ),
        (
            {
                "code_lists": [["id"], ["CL"]],
                "codes": [["code_list", "value", "parent"], ["CL", "11", "1"]],
            },
            "column parent: no earlier code of CL has value '1'",
        ),
        (
            {
                "concepts": [["id"], ["C"]],
                "conceptual_variables": [["id"], ["CV"]],
                "represented_variables": [
                    ["id", "conceptual_variable", "concept", "representation"],
                    ["RV", "CV", "C", "text"],
                ],
            },
            "give a conceptual_variable, or a concept and unit_type, not both",
        ),
        (
            {"represented_variables": [["id"], ["RV"]]},
            "column representation: is empty",
        ),
        (
            {"question_grids": [["id"], ["G"]]},
            "column rows: a grid needs rows",
        ),
        (
            {
                "questions": [["id"], ["Q"]],
                "question_grids": [["id", "rows"], ["Q", "CL"]],
                "code_lists": [["id"], ["CL"]],
                "question_blocks": [["id", "questions"], ["B", "Q"]],
            },
            "column questions: 'Q' is an id in questions and question_grids",
        ),
        (
            {"ncubes": [["id"], ["N"]]},
            "column dimensions: an n-cube needs at least one dimension",
        ),
        (
            {
                "studies": [["id"], ["S"]],
                "methodologies": [["id", "study"], ["M1", "S"], ["M2", "S"]],
            },
            "row 3, column study: study S already has a methodology (row 2)",
        ),
        (
            {"studies": [["id", "publication_date"], ["S", "May 2024"]]},
            "column publication_date: 'May 2024' is not a date",
        ),
        (
            {"organizations": [["id", "abbreviation"], ["O", "ESA"]]},
            "column name: is empty",
        ),
        (
            {"individuals": [["id", "email"], ["P", "p@example.org"]]},
            "give a first_name, a last_name or both",
        ),
        (
            {
                "organizations": [["id", "name@en"], ["X", "Org"]],
                "individuals": [["id", "last_name"], ["X", "Doe"]],
                "studies": [["id", "creator"], ["S", "X"]],
            },
            "column creator: 'X' is an id in organizations and individuals",
        ),
        (
            {
                "comparisons": [
                    ["map", "type", "source", "target"],
                    ["M", "dataset", "A", "B"],
                ]
            },
            "column type: 'dataset' is not one of concept, universe, question",
        ),
        (
            {
                "concepts": [["id"], ["A"], ["B"]],
                "universes": [["id"], ["U"], ["V"]],
                "comparisons": [
                    ["map", "type", "source", "target"],
                    ["M", "concept", "A", "B"],
                    ["M", "universe", "U", "V"],
                ],
            },
            "row 3, column type: map M compares concept items (row 2)",
        ),
        (
            {
                "concepts": [["id"], ["A"], ["B"]],
                "comparisons": [
                    ["map", "type", "source", "target", "weight"],
                    ["M", "concept", "A", "B", "2"],
                ],
            },
            "column weight: '2' is not a number from 0 to 1",
        ),
        (
            {
                "comparisons": [
                    ["map", "type", "source", "target"],
                    ["M", "category", "CL/1", ""],
                ],
            },
            "column source: no category 'CL/1'",
        ),
        (
            {"comparisons": [["map", "type", "source", "target"], ["", "", "A", "B"]]},
            "column map: is empty",
        ),
    ],
)
def test_problems_are_reported(
    tmp_path: Path, rows: dict[str, list[list[str]]], expected: str
) -> None:
    found = problems(tables(tmp_path / "t", **rows))
    assert any(expected in problem for problem in found), found
