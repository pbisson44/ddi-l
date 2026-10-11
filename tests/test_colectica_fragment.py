"""Colectica ``FragmentInstance`` exports read, edit and write back unchanged.

``colectica_group_fragment.xml`` is a Colectica Designer export of a ``Group``
(DDI 3.3, 121 items, UTF-8 with a byte-order mark); only the
``r:VersionResponsibility`` user names were replaced. The larger
``Canadian_Survey_on_Business_conditions.xml`` is a Colectica export of an
``Instrument``. Between them they carry the things the typed models used to
lose: ``versionDate``, ``r:VersionResponsibility``, ``r:BasedOnObject``
lineage, ``audienceLanguage``, bilingual ``r:Label``/``r:Name``, user
attribute pairs inside a reference, and references with no ``r:URN``.
"""

from __future__ import annotations

import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest

import ddi_l as ddi
from ddi_l._etree import Element
from ddi_l.maintainable_registry import maintainable_type_from_name
from tests import TEST_FIXTURES_DIR

GROUP_EXPORT = TEST_FIXTURES_DIR / "colectica_group_fragment.xml"
INSTRUMENT_EXPORT = TEST_FIXTURES_DIR / "Canadian_Survey_on_Business_conditions.xml"
EXPORTS = [
    pytest.param(GROUP_EXPORT, id="group"),
    pytest.param(INSTRUMENT_EXPORT, id="instrument"),
]

Canonical = tuple[str, tuple[tuple[str, str], ...], str, tuple[object, ...]]


def _canonical(element: Element) -> Canonical:
    """Tag, attributes, trimmed text and children, in document order."""
    return (
        element.tag,
        tuple(sorted(element.attrib.items())),
        (element.text or "").strip(),
        tuple(_canonical(child) for child in element),
    )


def _payloads(path: Path) -> Iterator[Element]:
    yield from ddi.DDIFragment.from_xml(path).iter_fragment_payloads()


def _typed_round_trip(element: Element) -> Element:
    cls = maintainable_type_from_name(element.tag.split("}")[-1])
    assert cls is not None, f"no typed model for {element.tag}"
    with warnings.catch_warnings():
        # Items reference each other across fragments; resolving them is the
        # job of the fragment, not of a single item's serializer.
        warnings.simplefilter("ignore")
        return cls.from_xml(element).to_xml()


@pytest.mark.parametrize("path", EXPORTS)
def test_every_item_survives_the_typed_models(path: Path) -> None:
    """``from_xml`` then ``to_xml`` reproduces each item exactly."""
    changed: dict[str, int] = {}
    for element in _payloads(path):
        if _canonical(_typed_round_trip(element)) != _canonical(element):
            name = element.tag.split("}")[-1]
            changed[name] = changed.get(name, 0) + 1
    assert changed == {}


def test_typed_items_keep_lineage_and_version_metadata() -> None:
    """The fields a Colectica repository depends on survive a typed edit."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        items = [
            maintainable_type_from_name(el.tag.split("}")[-1]).from_xml(el)  # type: ignore[union-attr]
            for el in _payloads(GROUP_EXPORT)
        ]
    assert len(items) == 121
    assert all(item.version_responsibility == "STC\\user" for item in items)
    assert sum(item.based_on_object is not None for item in items) == 18
    assert all(item.version_date for item in items)
    assert all(item.other_attributes.get("isUniversallyUnique") for item in items)


def test_version_date_is_settable_on_every_type() -> None:
    """``version_date`` reads and writes the attribute on mapped and unmapped types."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for element in _payloads(GROUP_EXPORT):
            cls = maintainable_type_from_name(element.tag.split("}")[-1])
            assert cls is not None
            item = cls.from_xml(element)
            item.version_date = "2026-01-01T00:00:00Z"
            assert item.to_xml().get("versionDate") == "2026-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# Writing Colectica's layout
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", EXPORTS)
def test_export_is_written_back_byte_for_byte(path: Path) -> None:
    fragment = ddi.open_fragment(path)
    assert fragment.to_colectica_bytes() == path.read_bytes()


@pytest.mark.parametrize("path", EXPORTS)
def test_typed_rebuild_is_byte_identical(path: Path) -> None:
    """Every item through ``from_xml``/``to_xml``, then Colectica's layout."""
    source = ddi.open_fragment(path)
    rebuilt = ddi.DDIFragment.create(source.get_top_level_reference())
    for element in source.iter_fragment_payloads():
        rebuilt.add_fragment(_typed_round_trip(element))
    assert rebuilt.to_colectica_bytes() == path.read_bytes()


def test_save_writes_colectica_layout_by_default(tmp_path: Path) -> None:
    target = tmp_path / "out.xml"
    ddi.open_fragment(GROUP_EXPORT).save(target)
    assert target.read_bytes() == GROUP_EXPORT.read_bytes()


def test_cli_roundtrip_colectica_layout(tmp_path: Path) -> None:
    from ddi_l.cli import main

    target = tmp_path / "out.xml"
    status = main(
        ["roundtrip", str(GROUP_EXPORT), "--layout", "colectica", "-o", str(target)]
    )
    assert status == 0
    assert target.read_bytes() == GROUP_EXPORT.read_bytes()


def test_colectica_layout_requires_a_fragment() -> None:
    doc = ddi.new_study(title="Survey", agency="example.org")
    with pytest.raises(ddi.DDIWriteError):
        ddi.write_ddi(doc, layout="colectica")


# ---------------------------------------------------------------------------
# Working with items
# ---------------------------------------------------------------------------


def test_items_and_lookup() -> None:
    fragment = ddi.open_fragment(GROUP_EXPORT)
    assert len(fragment.items()) == 121
    variables = fragment.items(ddi.Variable)
    assert len(variables) == 46
    top = fragment.top_level_item()
    assert top is not None and top.identifier == "b4c9838f-48b0-484e-be37-aab89b875e56"
    found = fragment.get(variables[0].identifier)  # type: ignore[arg-type]
    assert found == variables[0]
    assert fragment.get("not-there") is None


def _unique_variable(fragment: ddi.DDIFragment) -> ddi.MaintainableBase:
    """A variable present in a single version in the export."""
    variables = fragment.items(ddi.Variable)
    counts: dict[str | None, int] = {}
    for variable in variables:
        counts[variable.identifier] = counts.get(variable.identifier, 0) + 1
    return next(v for v in variables if counts[v.identifier] == 1)


def test_editing_one_item_changes_only_that_item() -> None:
    import difflib

    fragment = ddi.open_fragment(GROUP_EXPORT)
    variable = _unique_variable(fragment)
    variable.labels.append(ddi.InternationalString("Age", lang="en-CA"))
    fragment.put(variable)
    before = GROUP_EXPORT.read_bytes().decode("utf-8-sig").splitlines()
    after = fragment.to_colectica_bytes().decode("utf-8-sig").splitlines()
    changes = [
        line
        for line in difflib.unified_diff(before, after, lineterm="", n=0)
        if line[:1] in "+-" and line[:3] not in ("+++", "---")
    ]
    assert changes == [
        "+    <r:Label>",
        '+      <r:Content xml:lang="en-CA">Age</r:Content>',
        "+    </r:Label>",
    ]
    assert fragment.validate() == []


def test_get_returns_the_latest_version() -> None:
    fragment = ddi.open_fragment(GROUP_EXPORT)
    versions = [
        v.version
        for v in fragment.items(ddi.Variable)
        if v.identifier == "4bf610ee-6771-44da-ab0b-00655b53b79b"
    ]
    assert len(versions) == 3  # Colectica exported three versions of it
    latest = fragment.get("4bf610ee-6771-44da-ab0b-00655b53b79b")
    assert latest is not None
    assert latest.version == max(versions, key=lambda value: int(value or 0))


def test_put_replaces_previous_version_and_remove_drops_it() -> None:
    fragment = ddi.open_fragment(GROUP_EXPORT)
    variable = _unique_variable(fragment)
    identifier = variable.identifier
    assert identifier is not None
    variable.increment_major_version()
    fragment.put(variable)
    assert len(fragment.items()) == 121
    current = fragment.get(identifier)
    assert current is not None and current.version == variable.version
    assert fragment.remove(identifier) == 1
    assert fragment.get(identifier) is None
    assert len(list(fragment.iter_fragments())) == 120


def test_put_adds_a_version_beside_several_existing_ones() -> None:
    fragment = ddi.open_fragment(GROUP_EXPORT)
    latest = fragment.get("4bf610ee-6771-44da-ab0b-00655b53b79b")
    assert latest is not None
    latest.increment_major_version()
    fragment.put(latest)
    assert len(fragment.items()) == 122


def test_from_items_writes_like_colectica() -> None:
    variable = ddi.Variable(
        agency="example.org",
        identifier="5f0e3c1a-0b8e-4d3e-9a5e-6a1b2c3d4e5f",
        version="1",
        labels=[
            ddi.InternationalString("Age", lang="en"),
            ddi.InternationalString("Âge", lang="fr"),
        ],
    )
    fragment = ddi.DDIFragment.from_items(
        [variable], version_date="2026-10-08T12:00:00.0000000Z"
    )
    written = fragment.to_colectica_bytes().decode("utf-8")
    assert written.startswith('﻿<?xml version="1.0" encoding="utf-8"?>\n')
    assert (
        '  <Variable isUniversallyUnique="true" '
        'versionDate="2026-10-08T12:00:00.0000000Z" '
        'xmlns="ddi:logicalproduct:3_3">'
    ) in written
    # One r:Label holding both languages, and no URN restating the reference.
    assert written.count("<r:Label>") == 1
    assert "<ddi:TopLevelReference>\n    <r:Agency>" in written
    assert fragment.validate() == []


def test_open_ddi_points_to_open_fragment() -> None:
    with pytest.raises(ValueError, match="open_fragment"):
        ddi.open_ddi(GROUP_EXPORT)


def test_version_date_property() -> None:
    variable = ddi.open_fragment(GROUP_EXPORT).items(ddi.Variable)[0]
    assert variable.version_date == "2025-10-01T18:05:27.0478736Z"


# ---------------------------------------------------------------------------
# Bugs found on the way
# ---------------------------------------------------------------------------


def test_boolean_one_is_true() -> None:
    """xs:boolean "1" is true; it was read as false and written "false"."""
    from ddi_l._etree import fromstring
    from ddi_l.models.base import InternationalString

    container = fromstring(
        '<r:Label xmlns:r="ddi:reusable:3_3">'
        '<r:Content xml:lang="en" isTranslated="1">x</r:Content></r:Label>'
    )
    (string,) = InternationalString.from_container(container)
    assert string.is_translated is True
    assert string.to_child().get("isTranslated") == "1"


def test_data_collection_keeps_identifiers_read_from_a_file() -> None:
    """Non-UUID IDs are an item's identity; rewriting them broke references."""
    from ddi_l._etree import fromstring

    element = fromstring(
        '<d:DataCollection xmlns:d="ddi:datacollection:3_3" '
        'xmlns:r="ddi:reusable:3_3"><r:Agency>example.org</r:Agency>'
        "<r:ID>dc-1</r:ID><r:Version>1</r:Version>"
        "<d:InstrumentReference><r:Agency>example.org</r:Agency>"
        "<r:ID>instrument-1</r:ID><r:Version>1</r:Version>"
        "<r:TypeOfObject>Instrument</r:TypeOfObject></d:InstrumentReference>"
        "</d:DataCollection>"
    )
    output = ddi.DataCollection.from_xml(element).to_xml()
    assert _canonical(output) == _canonical(element)


def test_validation_reports_errors_inside_fragment_study_units() -> None:
    """An error in a fragment's StudyUnit was forgiven, and hid later ones."""
    from ddi_l import schema_loader
    from ddi_l._etree import fromstring

    root = fromstring(
        '<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3" '
        'xmlns:s="ddi:studyunit:3_3"><Fragment><s:StudyUnit>'
        "<r:Agency>example.org</r:Agency><r:ID>s1</r:ID><r:Version>1</r:Version>"
        "<s:Bogus/></s:StudyUnit></Fragment></FragmentInstance>"
    )
    issues = schema_loader.validate(root, raise_error=False)
    assert issues and "Bogus" in issues[0].message


# ---------------------------------------------------------------------------
# Edits are never undone by what is kept from the source
# ---------------------------------------------------------------------------


def test_put_moves_the_top_level_reference_to_the_new_version() -> None:
    fragment = ddi.open_fragment(GROUP_EXPORT)
    top = fragment.top_level_item()
    assert top is not None
    top.increment_major_version()
    fragment.put(top)
    moved = fragment.top_level_item()
    assert moved is not None and moved.version == top.version


def test_cleared_string_attributes_stay_cleared() -> None:
    from ddi_l._etree import fromstring
    from ddi_l.models.base import InternationalString

    container = fromstring(
        '<r:Label xmlns:r="ddi:reusable:3_3"><r:Content xml:lang="en" '
        'isTranslated="true" translationSourceLanguage="fr" '
        'translationDate="2026-01-01" isTranslatable="false">x</r:Content></r:Label>'
    )
    (string,) = InternationalString.from_container(container)
    string.lang = None
    string.is_translated = None
    string.translation_source_language = None
    string.translation_date = None
    # Only the attribute no field covers is still written.
    assert dict(string.to_child().attrib) == {"isTranslatable": "false"}

    plain = fromstring(
        '<r:Label xmlns:r="ddi:reusable:3_3" xml:lang="en" isPlainText="1">x</r:Label>'
    )
    (string,) = InternationalString.from_container(plain)
    assert string.to_child().get("isPlainText") == "1"
    string.lang = None
    string.is_plain_text = None
    assert dict(string.to_child().attrib) == {}


def test_edit_to_a_numeric_looking_string_is_written() -> None:
    from tests.helpers.xsd_samples import build_sample

    sample = build_sample("{ddi:logicalproduct:3_3}ClassificationItem")
    assert sample is not None
    code = sample.find("{ddi:logicalproduct:3_3}ItemCode")
    assert code is not None
    code.text = "01"
    model = ddi.MaintainableBase.for_tag(sample.tag)
    assert model is not None
    item = model.from_xml(sample)
    assert item.to_xml().findtext("{ddi:logicalproduct:3_3}ItemCode") == "01"
    item.item_code = "1"  # type: ignore[attr-defined]
    assert item.to_xml().findtext("{ddi:logicalproduct:3_3}ItemCode") == "1"


def test_attributes_in_unknown_namespaces_keep_their_namespace() -> None:
    from ddi_l._etree import fromstring

    variable = ddi.Variable(agency="example.org", identifier="v1", version="1").to_xml()
    variable.set("{urn:example:one}flag", "a")
    variable.set("{urn:example:two}flag", "b")
    fragment = ddi.DDIFragment.from_items([variable])
    root = fromstring(
        fragment.to_colectica_bytes().decode("utf-8-sig").split("\n", 1)[1]
    )
    written = root.find(".//{ddi:logicalproduct:3_3}Variable")
    assert written is not None
    assert written.get("{urn:example:one}flag") == "a"
    assert written.get("{urn:example:two}flag") == "b"


def test_from_items_drops_every_restated_reference_urn() -> None:
    """Removing a URN while walking the tree skipped the next reference."""
    concepts = [
        ddi.Concept(agency="example.org", identifier=f"c{n}", version="1")
        for n in range(3)
    ]
    variable = ddi.Variable(
        agency="example.org",
        identifier="v1",
        version="1",
        concept_references=[
            ddi.Reference(
                type_of_object="Concept",
                agency=c.agency,
                identifier=c.identifier,
                version=c.version,
            )
            for c in concepts
        ],
    )
    written = ddi.DDIFragment.from_items([variable]).to_colectica_bytes().decode()
    references = written.split("<r:ConceptReference>")[1:]
    assert len(references) == 3
    assert not any(
        "<r:URN>" in ref.split("</r:ConceptReference>")[0] for ref in references
    )


def test_a_study_in_a_fragment_points_at_its_siblings_without_warning() -> None:
    """Each item of a fragment is in a fragment of its own, so a study's
    references always point outside it; that is not worth a warning."""
    universe = ddi.Universe(agency="example.org", identifier="u1", version="1")
    study = ddi.StudyUnit(
        agency="example.org",
        identifier="s1",
        version="1",
        universe_references=[
            ddi.Reference(
                type_of_object="Universe",
                agency="example.org",
                identifier="u1",
                version="1",
            )
        ],
        data_collection_references=[
            ddi.Reference(
                type_of_object="DataCollection",
                agency="example.org",
                identifier="dc1",
                version="1",
            )
        ],
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", ddi.DDIReferenceWarning)
        fragment = ddi.DDIFragment.from_items([study, universe])
        fragment.put(study)
    assert len(fragment.items()) == 2
