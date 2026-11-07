"""Editing a questionnaire: version cascade, moving and wrapping, copies.

``tests/fixtures/colectica/pets_instrument.ddi33.xml`` is a synthetic
instrument five levels deep (Instrument, Root, Section A, Pets page, Pets
block), an entry page whose gate wraps only the first of its eleven
statements, a late-bound reference to the Pets block, and a question copy
that kept its source's OutParameter ID.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import ddi_l
from ddi_l._etree import create_element, tostring
from ddi_l.colectica_edit import (
    EditResult,
    _Items,
    _next_major,
    _pinned,
    _set_rationale,
)
from ddi_l.colectica_logic import Condition, NativeCondition
from ddi_l.exceptions import DDIModelError
from ddi_l.lint import run_lint

FIXTURE = Path(__file__).parent / "fixtures" / "colectica" / "pets_instrument.ddi33.xml"
R = "{ddi:reusable:3_3}"
STAMP = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{7}Z$")


def i(n: int) -> str:
    return f"44444444-4444-4444-8444-{n:012d}"


INSTRUMENT, ROOT, SECTION, PETS_PAGE, PETS_BLOCK = i(1), i(2), i(3), i(4), i(5)
LATE_GATE, ENTRY_PAGE, OWNER_GATE, OWNER_THEN = i(6), i(40), i(41), i(42)
QUESTION, SHARED, COPY = i(60), i(61), i(62)
CONSTRUCT, COPY_CONSTRUCT, SUMMARY = i(70), i(71), i(80)


@pytest.fixture
def fragment() -> ddi_l.DDIFragment:
    return ddi_l.open_fragment(FIXTURE)


def _payload(fragment: ddi_l.DDIFragment, identifier: str):
    found = [
        payload
        for payload in fragment.iter_fragment_payloads()
        if payload.findtext(f"{R}ID") == identifier
    ]
    assert len(found) == 1, identifier
    return found[0]


def _version(fragment: ddi_l.DDIFragment, identifier: str) -> str | None:
    return _payload(fragment, identifier).findtext(f"{R}Version")


# ---- revise ----------------------------------------------------------------


def test_revising_a_leaf_bumps_it_and_exactly_its_four_ancestors(
    fragment: ddi_l.DDIFragment,
) -> None:
    plan = fragment.revise(PETS_BLOCK)
    assert [(s.identifier, s.old_version, s.new_version) for s in plan] == [
        (PETS_BLOCK, "9", "10"),
        (PETS_PAGE, "2", "3"),
        (SECTION, "4", "5"),
        (ROOT, "7", "8"),
        (INSTRUMENT, "3", "4"),
    ]
    assert plan.steps[1].changed_references == (f"Sequence {PETS_BLOCK}",)
    assert plan.top_level_reference_updated
    assert not plan.dry_run
    # The references now name the new versions, URNs included.
    page = _payload(fragment, PETS_PAGE)
    assert page.find(f".//{{*}}ControlConstructReference/{R}Version").text == "10"
    assert page.findtext(f"{R}URN").endswith(f":{PETS_PAGE}:3")
    assert STAMP.match(page.get("versionDate"))
    top = fragment.get_top_level_reference()
    assert top is not None and top.version == "4"


def test_late_bound_references_are_left_alone(fragment: ddi_l.DDIFragment) -> None:
    fragment.revise(PETS_BLOCK)
    gate = _payload(fragment, LATE_GATE)
    assert gate.findtext(f"{R}Version") == "1"
    then = gate.find("{ddi:datacollection:3_3}ThenConstructReference")
    assert then.findtext(f"{R}Version") == "1"
    assert then.get("lateBound") == "true"


def test_a_dry_run_changes_nothing(fragment: ddi_l.DDIFragment) -> None:
    before = fragment.to_colectica_bytes()
    plan = fragment.revise(PETS_BLOCK, dry_run=True)
    assert plan.dry_run and len(plan) == 5
    assert fragment.to_colectica_bytes() == before
    element_plan = fragment.revise(_payload(fragment, PETS_BLOCK), dry_run=True)
    assert [s.identifier for s in element_plan] == [s.identifier for s in plan]


def test_without_cascade_only_the_item_changes(fragment: ddi_l.DDIFragment) -> None:
    plan = fragment.revise(PETS_BLOCK, cascade=False)
    assert [s.identifier for s in plan] == [PETS_BLOCK]
    assert not plan.top_level_reference_updated
    assert _version(fragment, PETS_PAGE) == "2"


def test_shared_ancestors_are_revised_once(fragment: ddi_l.DDIFragment) -> None:
    plan = fragment.revise(PETS_BLOCK, OWNER_THEN)
    identifiers = [step.identifier for step in plan]
    assert len(identifiers) == len(set(identifiers))
    assert _version(fragment, SECTION) == "5"
    assert _version(fragment, INSTRUMENT) == "4"


def test_revise_records_responsibility(fragment: ddi_l.DDIFragment) -> None:
    fragment.revise(PETS_BLOCK, cascade=False, responsibility="Pet team")
    assert _payload(fragment, PETS_BLOCK).findtext(f"{R}VersionResponsibility") == (
        "Pet team"
    )
    with ddi_l.configured(version_responsibility="Survey team"):
        fragment.revise(PETS_PAGE, cascade=False)
    assert _payload(fragment, PETS_PAGE).findtext(f"{R}VersionResponsibility") == (
        "Survey team"
    )
    assert not fragment.validate()


def _rationale(fragment: ddi_l.DDIFragment, identifier: str) -> dict[str, str]:
    holders = _payload(fragment, identifier).findall(f"{R}VersionRationale")
    assert len(holders) <= 1
    if not holders:
        return {}
    strings = holders[0].findall(f"{R}RationaleDescription/{R}String")
    return {
        s.get("{http://www.w3.org/XML/1998/namespace}lang", ""): s.text or ""
        for s in strings
    }


def test_revise_records_one_rationale_on_every_item_it_revises(
    fragment: ddi_l.DDIFragment,
) -> None:
    # As Colectica records a save's message on every item it saves.
    plan = fragment.revise(
        COPY, rationale={"en-CA": "Ask for the pet's age", "fr-CA": "Demander l'âge"}
    )
    assert len(plan.steps) > 1
    for step in plan:
        assert _rationale(fragment, step.identifier) == {
            "en-CA": "Ask for the pet's age",
            "fr-CA": "Demander l'âge",
        }
    # Before r:BasedOnObject, as DDI 3.3 orders them.
    children = [child.tag.rsplit("}", 1)[-1] for child in _payload(fragment, COPY)]
    assert children.index("VersionRationale") < children.index("BasedOnObject")
    assert not fragment.validate()
    fragment.revise(PETS_BLOCK, cascade=False, rationale="One string")
    assert _rationale(fragment, PETS_BLOCK) == {"": "One string"}


def test_revise_drops_the_rationale_of_the_previous_version(
    fragment: ddi_l.DDIFragment,
) -> None:
    fragment.revise(PETS_BLOCK, cascade=False, rationale="Rename the block")
    fragment.revise(PETS_BLOCK, cascade=False)
    assert _rationale(fragment, PETS_BLOCK) == {}
    fragment.revise(PETS_BLOCK, cascade=False, rationale="First")
    fragment.revise(PETS_BLOCK, cascade=False, rationale="Second")
    assert _rationale(fragment, PETS_BLOCK) == {"": "Second"}
    plan = fragment.revise(PETS_BLOCK, rationale="Not yet", dry_run=True)
    assert plan.dry_run and _rationale(fragment, PETS_BLOCK) == {"": "Second"}
    assert not fragment.validate()


def test_revise_refuses_what_it_cannot_do(fragment: ddi_l.DDIFragment) -> None:
    with pytest.raises(KeyError, match="missing"):
        fragment.revise("missing")
    _payload(fragment, PETS_BLOCK).find(f"{R}Version").text = "v9"
    with pytest.raises(DDIModelError, match="non-numeric version"):
        fragment.revise(PETS_BLOCK)
    _payload(fragment, PETS_BLOCK).remove(
        _payload(fragment, PETS_BLOCK).find(f"{R}Version")
    )
    with pytest.raises(DDIModelError, match="has no r:Version"):
        fragment.revise(PETS_BLOCK)


def _nested(fragment: ddi_l.DDIFragment, identifier: str, nested: str):
    found = [
        node
        for node in _payload(fragment, identifier).iter()
        if node.findtext(f"{R}ID") == nested and not node.tag.endswith("Reference")
    ]
    assert len(found) == 1, nested
    return found[0]


def test_what_an_item_declares_takes_its_new_version(
    fragment: ddi_l.DDIFragment,
) -> None:
    # Colectica gives an item's parameters and codes the item's version.
    fragment.revise(CONSTRUCT, cascade=False)
    parameter = _nested(fragment, CONSTRUCT, i(72))
    assert parameter.findtext(f"{R}Version") == "2"
    assert parameter.findtext(f"{R}URN") == f"urn:ddi:int.example:{i(72)}:2"
    # Also when it did not have the item's version before.
    fragment.revise(OWNER_GATE, cascade=False)
    assert _version(fragment, OWNER_GATE) == "3"
    parameter = _nested(fragment, OWNER_GATE, i(52))
    assert parameter.findtext(f"{R}Version") == "3"
    assert parameter.findtext(f"{R}URN").endswith(f":{i(52)}:3")
    assert not fragment.validate()


def test_a_pinned_reference_to_a_declared_parameter_follows_it(
    fragment: ddi_l.DDIFragment,
) -> None:
    source = _payload(fragment, SUMMARY).find(f".//{R}SourceParameterReference")
    del source.attrib["lateBound"]
    plan = fragment.revise(QUESTION)
    assert source.findtext(f"{R}Version") == "2"
    summary = next(step for step in plan if step.identifier == SUMMARY)
    assert summary.changed_references == (f"OutParameter {i(61)}",)
    assert _version(fragment, SUMMARY) == "2"
    # The construct pins the question, so it is revised for that alone: its
    # late-bound binding keeps the version it names.
    construct = _payload(fragment, CONSTRUCT).find(f".//{R}SourceParameterReference")
    assert construct.findtext(f"{R}Version") == "1"
    step = next(step for step in plan if step.identifier == CONSTRUCT)
    assert step.changed_references == (f"QuestionItem {QUESTION}",)


def test_one_revision_is_one_moment(fragment: ddi_l.DDIFragment) -> None:
    plan = fragment.revise(PETS_BLOCK)
    dates = {_payload(fragment, step.identifier).get("versionDate") for step in plan}
    assert len(dates) == 1
    assert STAMP.match(dates.pop() or "")
    moment = "2030-01-02T03:04:05.0000000Z"
    plan = fragment.revise(PETS_BLOCK, version_date=moment)
    assert {
        _payload(fragment, step.identifier).get("versionDate") for step in plan
    } == {moment}
    assert fragment.revise(PETS_BLOCK, version_date=moment, dry_run=True).dry_run


def test_new_items_get_the_configured_responsibility(
    fragment: ddi_l.DDIFragment,
) -> None:
    from ddi_l.models import InternationalString, StatementItem

    thanks = StatementItem(
        agency="int.example",
        identifier=i(95),
        version="1",
        construct_names=[InternationalString("Thanks", lang="en-CA")],
    )
    with ddi_l.configured(version_responsibility="Pet team"):
        fragment.insert_construct(ENTRY_PAGE, thanks)
        result = fragment.wrap_in_condition(
            ENTRY_PAGE, [i(11)], NativeCondition("IsOwner = 1", "Blaise")
        )
    created = [i(95), *result.created]
    for identifier in created:
        payload = _payload(fragment, identifier)
        assert payload.findtext(f"{R}VersionResponsibility") == "Pet team"
    gate, then = (_payload(fragment, n) for n in result.created)
    assert gate.get("versionDate") == then.get("versionDate")
    assert not fragment.validate()
    # Without one configured, none is written.
    plain = fragment.wrap_in_condition(
        ENTRY_PAGE, [i(13)], NativeCondition("x", "Blaise")
    )
    assert (
        _payload(fragment, plain.created[0]).find(f"{R}VersionResponsibility") is None
    )


def test_a_new_items_parameters_are_identified_as_colectica_writes_them(
    fragment: ddi_l.DDIFragment,
) -> None:
    from ddi_l.models import OutParameter, QuestionConstruct

    construct = QuestionConstruct(
        agency="int.example",
        identifier=i(96),
        version="1",
        out_parameters=[
            OutParameter(
                agency="int.example", identifier=i(97), version="1", alias="Again"
            ),
            OutParameter(agency="int.example", identifier=i(98), alias="Unversioned"),
        ],
    )
    fragment.insert_construct(SUMMARY, construct)
    for nested in (i(97), i(98)):
        parameter = _nested(fragment, i(96), nested)
        assert parameter.get("isUniversallyUnique") == "true"
        assert parameter.findtext(f"{R}Version") == "1"
        assert parameter.findtext(f"{R}URN") == f"urn:ddi:int.example:{nested}:1"
    assert not fragment.validate()


def test_a_copy_and_what_it_declares_start_at_version_1(
    fragment: ddi_l.DDIFragment,
) -> None:
    fragment.revise(CONSTRUCT, cascade=False)
    copy, id_map = fragment.duplicate(CONSTRUCT)
    assert copy.identifier is not None
    parameter = _nested(fragment, copy.identifier, id_map[i(72)])
    assert parameter.findtext(f"{R}Version") == "1"
    assert parameter.findtext(f"{R}URN") == f"urn:ddi:int.example:{id_map[i(72)]}:1"


def test_editing_needs_a_ddi_3_3_fragment() -> None:
    text = FIXTURE.read_text(encoding="utf-8").replace(":3_3", ":3_2")
    old = ddi_l.read_ddi(text.encode())
    assert isinstance(old, ddi_l.DDIFragment)
    for call in (
        lambda: old.revise(PETS_BLOCK),
        lambda: old.move_construct(i(11), ENTRY_PAGE, OWNER_THEN),
        lambda: old.insert_construct(SUMMARY, i(11)),
        lambda: old.duplicate(QUESTION),
        lambda: old.repair_shared_identifiables(),
    ):
        with pytest.raises(DDIModelError, match="DDI 3.3 only"):
            call()


# ---- The scripted fix of an entry page ------------------------------------------


def test_moving_the_page_into_its_gate_changes_six_items(
    fragment: ddi_l.DDIFragment,
) -> None:
    touched: set[str] = set()
    for n in range(1, 11):
        touched.update(
            fragment.move_construct(i(10 + n), ENTRY_PAGE, OWNER_THEN).touched
        )
    assert touched == {ENTRY_PAGE, OWNER_THEN}
    before = {
        payload.findtext(f"{R}ID") or "": payload.findtext(f"{R}Version")
        for payload in fragment.iter_fragment_payloads()
    }

    plan = fragment.revise(*sorted(touched))

    after = {
        payload.findtext(f"{R}ID") or "": payload.findtext(f"{R}Version")
        for payload in fragment.iter_fragment_payloads()
    }
    changed = {key for key in before if before[key] != after[key]}
    assert changed == {ENTRY_PAGE, OWNER_THEN, OWNER_GATE, SECTION, ROOT, INSTRUMENT}
    assert len(plan) == 6
    for identifier in changed:
        assert STAMP.match(_payload(fragment, identifier).get("versionDate"))
    then = _payload(fragment, OWNER_THEN)
    assert len(then.findall("{ddi:datacollection:3_3}ControlConstructReference")) == 11
    assert not fragment.validate()
    # The partial gate the lint rule reported is gone.
    assert not run_lint(fragment, rules=["colectica.ifthenelse.partial-gate"])


def test_move_construct_inserts_at_an_index(fragment: ddi_l.DDIFragment) -> None:
    fragment.move_construct(i(11), ENTRY_PAGE, OWNER_THEN, index=0)
    then = _payload(fragment, OWNER_THEN)
    ids = [
        ref.findtext(f"{R}ID")
        for ref in then.findall("{ddi:datacollection:3_3}ControlConstructReference")
    ]
    assert ids == [i(11), i(10)]
    # Within one sequence: a reorder touches the sequence once.
    result = fragment.move_construct(i(10), OWNER_THEN, OWNER_THEN, index=0)
    assert result.touched == (OWNER_THEN,)


def test_move_construct_into_an_empty_sequence(fragment: ddi_l.DDIFragment) -> None:
    fragment.move_construct(i(10), OWNER_THEN, SUMMARY)
    summary = _payload(fragment, SUMMARY)
    assert summary.findall("{ddi:datacollection:3_3}ControlConstructReference")
    assert not fragment.validate()


def test_move_construct_requires_the_construct_to_be_there(
    fragment: ddi_l.DDIFragment,
) -> None:
    with pytest.raises(KeyError, match="does not contain"):
        fragment.move_construct(i(11), OWNER_THEN, ENTRY_PAGE)


# ---- insert_construct ---------------------------------------------------------------

D = "{ddi:datacollection:3_3}"


def _construct_ids(fragment: ddi_l.DDIFragment, sequence: str) -> list[str]:
    return [
        ref.findtext(f"{R}ID") or ""
        for ref in _payload(fragment, sequence).findall(f"{D}ControlConstructReference")
    ]


def test_insert_construct_places_a_copy(fragment: ddi_l.DDIFragment) -> None:
    before = {
        payload.findtext(f"{R}ID"): tostring(payload)
        for payload in fragment.iter_fragment_payloads()
    }
    copy, _ = fragment.duplicate(CONSTRUCT)
    result = fragment.insert_construct(SUMMARY, copy)
    assert result.touched == (SUMMARY,)
    assert result.created == ()
    assert _construct_ids(fragment, SUMMARY) == [copy.identifier]
    reference = _payload(fragment, SUMMARY).find(f"{D}ControlConstructReference")
    assert reference is not None and reference.find(f"{R}URN") is None
    assert reference.findtext(f"{R}TypeOfObject") == "QuestionConstruct"
    for payload in fragment.iter_fragment_payloads():
        identifier = payload.findtext(f"{R}ID")
        if identifier not in (SUMMARY, copy.identifier):
            assert tostring(payload) == before[identifier]
    assert not fragment.validate()


def test_insert_construct_positions(fragment: ddi_l.DDIFragment) -> None:
    first, _ = fragment.duplicate(i(11))
    middle, _ = fragment.duplicate(i(11))
    last, _ = fragment.duplicate(i(11))
    fragment.insert_construct(ENTRY_PAGE, first, index=0)
    fragment.insert_construct(ENTRY_PAGE, middle, before=i(12))
    fragment.insert_construct(ENTRY_PAGE, last, after=i(20))
    ids = _construct_ids(fragment, ENTRY_PAGE)
    assert ids[0] == first.identifier
    assert ids[ids.index(i(12)) - 1] == middle.identifier
    assert ids[-1] == last.identifier
    assert ids.index(i(20)) == len(ids) - 2


def test_insert_construct_adds_a_new_item(fragment: ddi_l.DDIFragment) -> None:
    from ddi_l.models import InternationalString, StatementItem

    thanks = StatementItem(
        agency="int.example",
        identifier=i(90),
        version="1",
        construct_names=[InternationalString("Thanks", lang="en-CA")],
    )
    result = fragment.insert_construct(ENTRY_PAGE, thanks)
    assert result == EditResult(touched=(ENTRY_PAGE,), created=(i(90),))
    payload = _payload(fragment, i(90))
    assert payload.get("isUniversallyUnique") == "true"
    assert STAMP.match(payload.get("versionDate") or "")
    assert payload.findtext(f"{R}URN") == f"urn:ddi:int.example:{i(90)}:1"
    assert _construct_ids(fragment, ENTRY_PAGE)[-1] == i(90)

    # The page and what pins it up to the instrument; the new item stays at 1.
    plan = fragment.revise(*result.touched)
    assert {step.identifier for step in plan} == {
        ENTRY_PAGE,
        SECTION,
        ROOT,
        INSTRUMENT,
    }
    assert plan.top_level_reference_updated
    assert not fragment.validate()


def test_insert_construct_without_colectica_conventions(
    fragment: ddi_l.DDIFragment,
) -> None:
    from ddi_l.models import StatementItem

    plain = StatementItem(agency="int.example", identifier=i(91), version="1")
    fragment.insert_construct(SUMMARY, plain, colectica=False)
    assert _payload(fragment, i(91)).get("versionDate") is None


def test_insert_construct_refuses_what_it_cannot_do(
    fragment: ddi_l.DDIFragment,
) -> None:
    from ddi_l.models import QuestionItem

    with pytest.raises(KeyError, match="missing"):
        fragment.insert_construct("missing", i(11))
    with pytest.raises(DDIModelError, match="place the QuestionConstruct"):
        fragment.insert_construct(SUMMARY, QUESTION)
    with pytest.raises(DDIModelError, match="place the QuestionConstruct"):
        fragment.insert_construct(
            SUMMARY, QuestionItem(agency="int.example", identifier=i(92), version="1")
        )
    assert not [p for p in fragment.iter_fragment_payloads() if i(92) in tostring(p)]
    with pytest.raises(DDIModelError, match="is not a Sequence"):
        fragment.insert_construct(OWNER_GATE, i(11))
    with pytest.raises(ValueError, match="move_construct"):
        fragment.insert_construct(ENTRY_PAGE, i(11))
    with pytest.raises(ValueError, match="cannot contain itself"):
        fragment.insert_construct(SUMMARY, SUMMARY)
    with pytest.raises(ValueError, match="at most one"):
        fragment.insert_construct(SUMMARY, i(11), index=0, after=i(12))
    with pytest.raises(KeyError, match="does not contain"):
        fragment.insert_construct(SUMMARY, i(11), before=i(12))


def test_a_failed_insert_adds_nothing(fragment: ddi_l.DDIFragment) -> None:
    from ddi_l.models import StatementItem

    before = fragment.to_colectica_bytes()
    new = StatementItem(agency="int.example", identifier=i(93), version="1")
    with pytest.raises(KeyError, match="does not contain"):
        fragment.insert_construct(SUMMARY, new, before=i(12))
    assert fragment.to_colectica_bytes() == before
    # Retried with an anchor that is there, it is reported as created.
    result = fragment.insert_construct(ENTRY_PAGE, new, before=i(12))
    assert result.created == (i(93),)


def test_a_new_construct_needs_its_identification(
    fragment: ddi_l.DDIFragment,
) -> None:
    from ddi_l.models import StatementItem

    before = fragment.to_colectica_bytes()
    with pytest.raises(ValueError, match="it has no identifier"):
        fragment.insert_construct(
            SUMMARY, StatementItem(agency="int.example", version="1")
        )
    with pytest.raises(ValueError, match="it has no agency, version"):
        fragment.insert_construct(SUMMARY, StatementItem(identifier=i(94)))
    assert fragment.to_colectica_bytes() == before


def test_a_negative_index_counts_from_the_end(fragment: ddi_l.DDIFragment) -> None:
    copy, _ = fragment.duplicate(i(11))
    fragment.insert_construct(ENTRY_PAGE, copy, index=-1)
    ids = _construct_ids(fragment, ENTRY_PAGE)
    assert ids[-2:] == [copy.identifier, i(20)]
    fragment.move_construct(i(12), ENTRY_PAGE, ENTRY_PAGE, index=-2)
    assert _construct_ids(fragment, ENTRY_PAGE)[-3:] == [i(12), copy.identifier, i(20)]


def test_a_sequence_cannot_take_in_its_ancestor(fragment: ddi_l.DDIFragment) -> None:
    before = fragment.to_colectica_bytes()
    with pytest.raises(ValueError, match="which contains it"):
        fragment.insert_construct(ENTRY_PAGE, ROOT)
    # Moving makes the same cycle: the entry page holds the gate whose Then
    # sequence would hold the page.
    with pytest.raises(ValueError, match="which contains it"):
        fragment.move_construct(ENTRY_PAGE, SECTION, OWNER_THEN)
    with pytest.raises(ValueError, match="cannot contain itself"):
        fragment.move_construct(ENTRY_PAGE, SECTION, ENTRY_PAGE)
    assert fragment.to_colectica_bytes() == before


def test_the_cycle_check_follows_the_version_pinned(
    fragment: ddi_l.DDIFragment,
) -> None:
    from ddi_l.models.base import clone_element

    # A version 2 of the entry page without its gate; the section still pins
    # version 1, which holds the gate whose Then sequence is OWNER_THEN.
    newer = clone_element(_payload(fragment, ENTRY_PAGE))
    version = newer.find(f"{R}Version")
    assert version is not None
    version.text = "2"
    gate_ref = next(
        ref
        for ref in newer.findall("{ddi:datacollection:3_3}ControlConstructReference")
        if ref.findtext(f"{R}ID") == OWNER_GATE
    )
    newer.remove(gate_ref)
    fragment.add_fragment(newer)
    with pytest.raises(ValueError, match="which contains it"):
        fragment.move_construct(ENTRY_PAGE, SECTION, OWNER_THEN)


def test_a_copy_does_not_contain_its_source(fragment: ddi_l.DDIFragment) -> None:
    # The copy names its source in r:BasedOnObject: lineage, not flow.
    copy, _ = fragment.duplicate(OWNER_THEN)
    result = fragment.insert_construct(OWNER_THEN, copy)
    assert result.touched == (OWNER_THEN,)


# ---- wrap_in_condition --------------------------------------------------------------


def test_wrap_in_condition(fragment: ddi_l.DDIFragment) -> None:
    result = fragment.wrap_in_condition(
        ENTRY_PAGE,
        [i(11), i(12)],
        NativeCondition("IsOwner = 1", "Blaise"),
        name="Owner details gate",
    )
    gate_id, then_id = result.created
    assert result.touched == (ENTRY_PAGE,)
    page = _payload(fragment, ENTRY_PAGE)
    refs = [
        ref.findtext(f"{R}ID")
        for ref in page.findall("{ddi:datacollection:3_3}ControlConstructReference")
    ]
    assert refs[:2] == [OWNER_GATE, gate_id]
    assert i(11) not in refs and i(12) not in refs
    then = _payload(fragment, then_id)
    assert then.findtext("{ddi:datacollection:3_3}TypeOfSequence") == (
        "ConditionalChildContainer"
    )
    gate = fragment.get(gate_id)
    assert gate is not None and gate.version == "1"
    assert "IsOwner = 1" in tostring(_payload(fragment, gate_id))
    name = _payload(fragment, gate_id).find(f".//{R}String")
    assert name.get("{http://www.w3.org/XML/1998/namespace}lang") == "en-CA"
    assert not fragment.validate()


def test_wrap_in_condition_with_a_neutral_condition(
    fragment: ddi_l.DDIFragment,
) -> None:
    result = fragment.wrap_in_condition(ENTRY_PAGE, [i(13)], Condition(synopsis="All"))
    content = _payload(fragment, result.created[0]).findtext(f".//{R}CommandContent")
    assert content == '{"LogicGroups":[],"Synopsis":"All","Version":1}'


def test_wrap_in_condition_requires_every_construct(
    fragment: ddi_l.DDIFragment,
) -> None:
    with pytest.raises(KeyError, match="every construct"):
        fragment.wrap_in_condition(
            ENTRY_PAGE, [i(11), i(10)], NativeCondition("x", "Blaise")
        )


# ---- duplicate ----------------------------------------------------------------------


def test_duplicate_gives_the_copy_and_what_it_declares_new_ids(
    fragment: ddi_l.DDIFragment,
) -> None:
    copy, id_map = fragment.duplicate(CONSTRUCT)
    assert set(id_map) == {CONSTRUCT, i(72)}
    assert copy.identifier == id_map[CONSTRUCT]
    assert copy.version == "1"
    payload = _payload(fragment, copy.identifier)
    text = tostring(payload)
    assert id_map[i(72)] in text and i(72) not in text  # its own parameter
    assert SHARED in text  # the question's parameter it binds is not its own
    based_on = payload.find(f"{R}BasedOnObject/{R}BasedOnReference")
    assert based_on.findtext(f"{R}ID") == CONSTRUCT
    assert payload.findtext(f"{R}URN") == f"urn:ddi:int.example:{copy.identifier}:1"
    assert STAMP.match(payload.get("versionDate"))
    assert not fragment.validate()


def test_duplicate_with_a_chosen_id_replaces_an_earlier_based_on(
    fragment: ddi_l.DDIFragment,
) -> None:
    copy, id_map = fragment.duplicate(
        COPY, new_id="55555555-5555-4555-8555-000000000001"
    )
    assert copy.identifier == "55555555-5555-4555-8555-000000000001"
    payload = _payload(fragment, copy.identifier)
    based_on = payload.findall(f"{R}BasedOnObject")
    assert len(based_on) == 1
    assert based_on[0].findtext(f"{R}BasedOnReference/{R}ID") == COPY
    assert id_map[SHARED] != SHARED


# ---- repair_shared_identifiables -------------------------------------------------------


def test_repair_plans_without_changing_by_default(fragment: ddi_l.DDIFragment) -> None:
    before = fragment.to_colectica_bytes()
    plan = fragment.repair_shared_identifiables()
    assert plan.dry_run
    assert fragment.to_colectica_bytes() == before
    (step,) = plan.steps
    assert step.item_type == "OutParameter"
    assert step.old_id == SHARED
    assert step.kept_in == f"QuestionItem {QUESTION}"
    assert step.copy == f"QuestionItem {COPY}"
    assert step.rebound == 1
    # The summary binds the shared ID directly: which copy it means is unknown.
    assert step.ambiguous == (f"Sequence {SUMMARY}",)
    assert set(plan.touched) == {COPY, COPY_CONSTRUCT}


def test_repair_applies_the_plan(fragment: ddi_l.DDIFragment) -> None:
    plan = fragment.repair_shared_identifiables(dry_run=False)
    (step,) = plan.steps
    copy_text = tostring(_payload(fragment, COPY))
    assert step.new_id in copy_text and SHARED not in copy_text
    construct_text = tostring(_payload(fragment, COPY_CONSTRUCT))
    assert step.new_id in construct_text and SHARED not in construct_text
    assert SHARED in tostring(_payload(fragment, QUESTION))
    assert SHARED in tostring(_payload(fragment, CONSTRUCT))
    assert SHARED in tostring(_payload(fragment, SUMMARY))
    assert not run_lint(fragment, rules=["colectica.identifiable.shared-id"])
    assert len(fragment.revise(*plan.touched)) >= 2
    assert not fragment.repair_shared_identifiables().steps


def test_the_earliest_item_keeps_the_id(fragment: ddi_l.DDIFragment) -> None:
    # Without dates, the item with no BasedOnObject is the original.
    for identifier in (QUESTION, COPY):
        del _payload(fragment, identifier).attrib["versionDate"]
    (step,) = fragment.repair_shared_identifiables().steps
    assert step.kept_in == f"QuestionItem {QUESTION}"
    # An earlier date wins over a missing BasedOnObject.
    _payload(fragment, COPY).set("versionDate", "2025-01-01T00:00:00.0000000Z")
    _payload(fragment, QUESTION).set("versionDate", "2026-01-01T00:00:00.0000000Z")
    (step,) = fragment.repair_shared_identifiables().steps
    assert step.kept_in == f"QuestionItem {COPY}"


# Helpers the version cascade relies on, tested directly: mutation testing
# showed the cascade tests pass whatever they return in these cases.

_TWO_VERSIONS = """\
<FragmentInstance xmlns="ddi:instance:3_3" xmlns:r="ddi:reusable:3_3"
    xmlns:d="ddi:datacollection:3_3">
  <TopLevelReference>
    <r:Agency>example.org</r:Agency><r:ID>q</r:ID><r:Version>2</r:Version>
    <r:TypeOfObject>QuestionItem</r:TypeOfObject>
  </TopLevelReference>
  <Fragment><d:QuestionItem>
    <r:Agency>example.org</r:Agency><r:ID>q</r:ID><r:Version>1</r:Version>
  </d:QuestionItem></Fragment>
  <Fragment><d:QuestionItem>
    <r:Agency>example.org</r:Agency><r:ID>q</r:ID><r:Version>2</r:Version>
  </d:QuestionItem></Fragment>
</FragmentInstance>
"""


def _reference(version: str, late_bound: str | None = None, identifier: str = "q"):
    reference = create_element("{ddi:reusable:3_3}QuestionReference")
    if late_bound is not None:
        reference.set("lateBound", late_bound)
    for name, text in (
        ("Agency", "example.org"),
        ("ID", identifier),
        ("Version", version),
    ):
        child = create_element(f"{{ddi:reusable:3_3}}{name}")
        child.text = text
        reference.append(child)
    return reference


@pytest.mark.parametrize(
    ("version", "late_bound", "expected"),
    [
        ("1", None, "1"),
        ("2", None, "2"),
        ("1", "true", "2"),
        ("1", " 1 ", "2"),
        ("1", "false", "1"),
        ("9", None, "2"),
    ],
)
def test_pinned_reads_the_version_a_reference_names(
    version: str, late_bound: str | None, expected: str
) -> None:
    items = _Items(ddi_l.DDIFragment.from_xml(_TWO_VERSIONS))

    pinned = _pinned(items, _reference(version, late_bound))

    assert pinned is not None
    assert items.version(pinned) == expected


def test_pinned_is_none_for_an_item_not_in_the_fragment() -> None:
    items = _Items(ddi_l.DDIFragment.from_xml(_TWO_VERSIONS))

    assert _pinned(items, _reference("1", identifier="other")) is None


@pytest.mark.parametrize(
    ("version", "expected"),
    [("6", "7"), ("1.2", "2.0"), ("1.2.3", "2.0.0"), ("9.0", "10.0")],
)
def test_next_major_resets_the_parts_after_the_first(
    version: str, expected: str
) -> None:
    assert _next_major(version) == expected


def test_next_major_refuses_a_non_numeric_version() -> None:
    with pytest.raises(DDIModelError, match="non-numeric"):
        _next_major("1.a")


@pytest.mark.parametrize(
    "responsibility_tag", ["VersionResponsibility", "VersionResponsibilityReference"]
)
def test_rationale_follows_the_version_responsibility(responsibility_tag: str) -> None:
    fragment = ddi_l.DDIFragment.from_xml(_TWO_VERSIONS)
    items = _Items(fragment)
    question = items.find("q")
    responsibility = items.tag(responsibility_tag)
    holder = create_element(responsibility)
    holder.text = "someone"
    question.insert(3, holder)
    question.append(create_element("{ddi:datacollection:3_3}QuestionItemName"))

    _set_rationale(items, question, "Why")

    names = [child.tag.rsplit("}", 1)[1] for child in question]
    assert names.index("VersionRationale") == names.index(responsibility_tag) + 1
