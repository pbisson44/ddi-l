"""A question's wording in each language is its own d:QuestionText.

DDI 3.3 (QuestionItem/QuestionText): "the full QuestionText must be repeated
for multi-language versions of the content ... languages cannot be mixed
within a dynamic text". Two d:LiteralText in one d:QuestionText are two parts
of one text, so a translation put there reads as part of the question.
"""

from __future__ import annotations

from pathlib import Path

from ddi_l import InternationalString, new_study, open_ddi, read_ddi
from ddi_l.constants import DATA_COLLECTION_NS, XML_NS

QUESTION_TEXT = f"{{{DATA_COLLECTION_NS}}}QuestionText"
TEXT = f"{{{DATA_COLLECTION_NS}}}Text"
LANG = f"{{{XML_NS}}}lang"


def _texts_per_container(xml: str) -> list[list[tuple[str | None, str]]]:
    root = read_ddi(xml).root
    return [
        [(text.get(LANG), text.text or "") for text in container.iter(TEXT)]
        for container in root.iter(QUESTION_TEXT)
    ]


def test_a_translation_added_in_code_gets_its_own_question_text() -> None:
    doc = new_study(title="Pet survey", agency="example.org")
    question = doc.add_question(text="How many pets live in your home?")
    question.question_texts.append(
        InternationalString(text="Combien d'animaux vivent chez vous ?", lang="fr")
    )

    xml = doc.to_xml()

    assert _texts_per_container(xml) == [
        [("en", "How many pets live in your home?")],
        [("fr", "Combien d'animaux vivent chez vous ?")],
    ]
    assert doc.validate() == []


def test_parts_in_one_language_still_share_one_question_text() -> None:
    doc = new_study(title="Pet survey", agency="example.org")
    question = doc.add_question(text="How many pets ")
    question.question_texts.append(
        InternationalString(text="live in your home?", lang="en")
    )

    assert _texts_per_container(doc.to_xml()) == [
        [("en", "How many pets "), ("en", "live in your home?")],
    ]


def test_both_languages_read_back(tmp_path: Path) -> None:
    doc = new_study(title="Pet survey", agency="example.org")
    question = doc.add_question(text="How many pets live in your home?")
    question.question_texts.append(
        InternationalString(text="Combien d'animaux vivent chez vous ?", lang="fr")
    )

    doc.save(tmp_path / "pets.xml")

    reread = open_ddi(tmp_path / "pets.xml")

    assert [(s.lang, s.text) for s in reread.questions[0].question_texts] == [
        ("en", "How many pets live in your home?"),
        ("fr", "Combien d'animaux vivent chez vous ?"),
    ]
