"""Focused tests for questionnaire fragment handling."""

from __future__ import annotations

from pathlib import Path

import pytest

from ddi_l._etree import parse_xml
from ddi_l.constants import DATA_COLLECTION_NS, REUSABLE_NS
from ddi_l.models import DataCollection, qn
from ddi_l.models.datacollection import QuestionScheme


@pytest.fixture(scope="module")
def questionnaire_fixture_dir(fixtures_dir: Path) -> Path:
    """Directory containing questionnaire model fixtures."""

    return fixtures_dir / "models"


def _question_scheme_element(questionnaire_fixture_dir: Path):
    element = parse_xml(questionnaire_fixture_dir / "data_collection_questionnaire.xml")
    assert element is not None
    scheme_el = element.find(qn(DATA_COLLECTION_NS, "QuestionScheme"))
    assert scheme_el is not None
    return element, scheme_el


def _load_question_scheme(questionnaire_fixture_dir: Path) -> QuestionScheme:
    _, scheme_el = _question_scheme_element(questionnaire_fixture_dir)
    return QuestionScheme.from_xml(scheme_el)


def _expected_fragment_identifiers(questionnaire_fixture_dir: Path) -> list[str]:
    _, scheme_el = _question_scheme_element(questionnaire_fixture_dir)
    fragment_tags = {
        qn(DATA_COLLECTION_NS, "QuestionItem"),
        qn(DATA_COLLECTION_NS, "QuestionGrid"),
        qn(DATA_COLLECTION_NS, "QuestionBlock"),
        qn(DATA_COLLECTION_NS, "QuestionGroup"),
    }
    identifiers: list[str] = []
    for child in scheme_el:
        if child.tag not in fragment_tags:
            continue
        identifier = child.findtext(qn(REUSABLE_NS, "ID"))
        if identifier is not None:
            identifiers.append(identifier)
    return identifiers


def test_question_scheme_fragment_order_preserved(
    questionnaire_fixture_dir: Path,
) -> None:
    """Inline fragments maintain the XML ordering when iterated."""

    scheme = _load_question_scheme(questionnaire_fixture_dir)

    identifiers = [fragment.identifier for fragment in scheme.iter_fragments()]
    assert identifiers == _expected_fragment_identifiers(questionnaire_fixture_dir)


def test_data_collection_multilingual_instructions_and_grid_metadata(
    questionnaire_fixture_dir: Path,
) -> None:
    """DataCollection exposes instruction translations and grid dimensions."""

    element = parse_xml(questionnaire_fixture_dir / "data_collection_questionnaire.xml")
    assert element is not None
    collection = DataCollection.from_xml(element)

    # Question fragments are flattened while preserving their sequencing.
    fragment_ids = [fragment.identifier for fragment in collection.question_fragments]
    assert fragment_ids == _expected_fragment_identifiers(questionnaire_fixture_dir)

    grid = collection.question_grids[0]
    assert [dimension.rank for dimension in grid.grid_dimensions] == [1, 2]
    assert grid.grid_dimensions[0].display_code is True
    assert grid.grid_dimensions[1].display_label is False
    assert grid.interviewer_instruction_references[0].attachment_locations == []

    instruction = collection.interviewer_instructions[0]
    assert [text.audience_language for text in instruction.instruction_texts] == [  # type: ignore[attr-defined]
        "en-CA",
        "fr-CA",
    ]
    assert {
        (string.lang, string.text)
        for text in instruction.instruction_texts
        for string in text.texts  # type: ignore[attr-defined]
    } == {
        ("en", "Introduce yourself before beginning."),
        ("fr", "Présentez-vous avant de commencer."),
    }

    inline_reference = collection.question_blocks[0].interviewer_instruction_references[
        0
    ]
    assert inline_reference.is_displayed is False
    scheme_reference = collection.interviewer_instruction_references[0]
    assert scheme_reference.is_displayed is True
