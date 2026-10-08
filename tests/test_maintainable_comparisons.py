"""Unit tests for maintainable comparison helpers."""

from __future__ import annotations

from dataclasses import replace

from ddi_l._etree import create_element, parse_xml
from ddi_l.constants import REUSABLE_NS
from ddi_l.models import (
    Concept,
    ConceptualComponent,
    DataCollection,
    InternationalString,
    MaintainableBase,
    clone_element,
    qn,
)
from tests.helpers.maintainable_fixtures import MODEL_FIXTURE_DIR


def _load_fixture(model_cls: type[MaintainableBase], name: str) -> MaintainableBase:
    element = parse_xml(MODEL_FIXTURE_DIR / f"{name}.xml")
    return model_cls.from_xml(element)


def test_equals_identical_instances() -> None:
    instance = _load_fixture(DataCollection, "data_collection_minimal")
    other = _load_fixture(DataCollection, "data_collection_minimal")

    assert instance.equals(other)
    assert other.equals(instance)
    assert instance.diff(other) == []


def test_diff_reports_changes() -> None:
    instance = _load_fixture(DataCollection, "data_collection_minimal")
    modified = replace(instance, version="2")

    diffs = instance.diff(modified)
    assert not instance.equals(modified)
    assert diffs
    assert any("version" in diff.lower() for diff in diffs)


def test_ignore_label_order() -> None:
    labels = [
        InternationalString(text="Primary", lang="en"),
        InternationalString(text="Secondaire", lang="fr"),
    ]
    base = Concept(
        agency="ca.statcan",
        identifier="concept-order",
        version="1",
        labels=list(labels),
    )
    reordered = replace(base, labels=list(reversed(labels)))

    assert not base.equals(reordered)
    assert any("labels" in diff for diff in base.diff(reordered))
    assert base.equals(reordered, ignore_label_order=True)


def test_ignore_other_elements_order() -> None:
    child_one = create_element(qn(REUSABLE_NS, "Extra"))
    child_one.text = "alpha"
    child_two = create_element(qn(REUSABLE_NS, "Extra"))
    child_two.text = "beta"

    base = Concept(
        agency="ca.statcan",
        identifier="concept-extra",
        version="1",
        other_elements=[child_one, child_two],
    )
    reordered = replace(
        base,
        other_elements=[clone_element(child_two), clone_element(child_one)],
    )

    assert not base.equals(reordered)
    assert any("other_elements" in diff for diff in base.diff(reordered))
    assert base.equals(reordered, ignore_other_elements_order=True)


def test_nested_differences_include_child_paths() -> None:
    concept = Concept(
        agency="ca.statcan",
        identifier="concept-nested",
        version="1",
        names=[InternationalString(text="Satisfaction", lang="en")],
    )
    component = ConceptualComponent(
        agency="ca.statcan",
        identifier="component",
        version="1",
        concepts=[concept],
    )
    modified_concept = replace(
        concept,
        names=[InternationalString(text="Engagement", lang="en")],
    )
    modified_component = replace(component, concepts=[modified_concept])

    diffs = component.diff(modified_component)
    assert not component.equals(modified_component)
    assert any("concepts[0]" in diff and "names" in diff for diff in diffs)
