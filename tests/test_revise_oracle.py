"""`revise` makes the changes the scan-every-item cascade made, and a dry run none.

The cascade looks up who refers to a revised item in an index built once per
call (and, on the native backend, kept per item while the item is
unchanged); a dry run makes its changes and takes them back. These tests
check both against the reference: the cascade as it was, scanning every
item for each revised one, on a separate copy of the same document.
"""

from __future__ import annotations

from functools import partial
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

import ddi_l
from ddi_l._etree import tostring
from ddi_l.colectica_edit import (
    _LATE_BOUND,
    RevisionPlan,
    RevisionStep,
    _bump,
    _Items,
    _local,
    _repoint,
)
from ddi_l.models import qn
from tests.helpers.examples import examples

FIXTURE = Path(__file__).parent / "fixtures" / "colectica" / "pets_instrument.ddi33.xml"
STAMP = "2026-01-01T00:00:00.0000000Z"
EXAMPLES = examples(300)


def _reference_revise(fragment, identifiers, *, cascade: bool) -> RevisionPlan:
    """The cascade as it was: every latest item scanned per revised item."""
    index = _Items(fragment)
    queue = [index.find(item) for item in identifiers]
    revised: dict[int, RevisionStep] = {}
    order: list[int] = []
    changed: dict[int, list[str]] = {}
    while queue:
        element = queue.pop(0)
        if id(element) in revised:
            continue
        key = index.key(element)
        old, new, declared = _bump(index, element, "someone", STAMP, None)
        revised[id(element)] = RevisionStep(
            _local(element.tag), key[1] if key else "", old, new
        )
        order.append(id(element))
        if not cascade or key is None:
            continue
        superseded = {key: old, **declared}
        for parent in index.latest():
            for reference in index.references(parent):
                target = index.key(reference)
                if (
                    target in superseded
                    and (parent is not element or target != key)
                    and reference.findtext(index.tag("Version")) == superseded[target]
                    and reference.get("lateBound") not in _LATE_BOUND
                ):
                    _repoint(index, reference, superseded[target], new)
                    changed.setdefault(id(parent), []).append(
                        f"{reference.findtext(index.tag('TypeOfObject'))} {target[1]}"
                    )
                    if (
                        parent is not element
                        and id(parent) not in revised
                        and parent not in queue
                    ):
                        queue.append(parent)
    top_updated = False
    top = fragment.root.find(qn(fragment._instance_ns, "TopLevelReference"))
    if top is not None:
        top_key = index.key(top)
        for step_id in order:
            step = revised[step_id]
            if (
                top_key
                and top_key[1] == step.identifier
                and top.findtext(index.tag("Version")) == step.old_version
            ):
                _repoint(index, top, step.old_version, step.new_version)
                top_updated = True
    steps = tuple(
        RevisionStep(
            revised[step_id].item_type,
            revised[step_id].identifier,
            revised[step_id].old_version,
            revised[step_id].new_version,
            tuple(changed.get(step_id, ())),
        )
        for step_id in order
    )
    return RevisionPlan(steps, top_updated)


# Edits between revisions: pin or late-bind a reference, point it at an old
# version, or drop one, so the cascade meets every case.
_EDITS = st.lists(
    st.tuples(
        st.sampled_from(["pin", "late-bind", "stale", "drop"]),
        st.integers(min_value=0, max_value=10_000),
    ),
    max_size=3,
)
_ROUNDS = st.lists(
    st.tuples(
        _EDITS,
        st.lists(st.integers(min_value=0, max_value=10_000), min_size=1, max_size=3),
        st.booleans(),
    ),
    min_size=1,
    max_size=3,
)


def _edit(fragment, edits) -> None:
    index = _Items(fragment)
    references = [
        (parent, reference)
        for parent in index.latest()
        for reference in index.references(parent)
    ]
    for kind, at in edits:
        if not references:
            return
        parent, reference = references[at % len(references)]
        if kind == "pin":
            if "lateBound" in reference.attrib:
                del reference.attrib["lateBound"]
        elif kind == "late-bind":
            reference.set("lateBound", "true")
        elif kind == "stale":
            version = reference.find(index.tag("Version"))
            if version is not None:
                version.text = "1"
        elif kind == "drop":
            holder = next(
                node for node in parent.iter() if any(c is reference for c in node)
            )
            holder.remove(reference)
            references.remove((parent, reference))


def _identifiers(fragment, picks) -> list[str]:
    index = _Items(fragment)
    keys = [index.key(item) for item in index.latest()]
    return [keys[pick % len(keys)][1] for pick in picks]


def _outcome(call):
    try:
        return call()
    except Exception as error:  # the same failure either way
        return type(error).__name__


@EXAMPLES
@given(rounds=_ROUNDS)
def test_revise_matches_the_scanning_cascade(rounds) -> None:
    fragment = ddi_l.open_fragment(FIXTURE)
    reference = ddi_l.open_fragment(FIXTURE)
    for edits, picks, cascade in rounds:
        _edit(fragment, edits)
        _edit(reference, edits)
        identifiers = _identifiers(fragment, picks)
        before = tostring(fragment.root)
        dry = _outcome(
            partial(
                fragment.revise,
                *identifiers,
                cascade=cascade,
                dry_run=True,
                responsibility="someone",
                version_date=STAMP,
            )
        )
        assert tostring(fragment.root) == before
        found = _outcome(
            partial(
                fragment.revise,
                *identifiers,
                cascade=cascade,
                responsibility="someone",
                version_date=STAMP,
            )
        )
        expected = _outcome(
            partial(_reference_revise, reference, identifiers, cascade=cascade)
        )
        assert found == expected
        assert tostring(fragment.root) == tostring(reference.root)
        if isinstance(found, RevisionPlan):
            # The dry run planned the very changes, and made none.
            assert isinstance(dry, RevisionPlan) and dry.dry_run
            assert (dry.steps, dry.top_level_reference_updated) == (
                found.steps,
                found.top_level_reference_updated,
            )
            assert tostring(fragment.root) != before


def test_a_failed_dry_run_changes_nothing() -> None:
    fragment = ddi_l.open_fragment(FIXTURE)
    index = _Items(fragment)
    # The second item cannot be revised: its version is not a number.
    first, second = list(index.latest())[:2]
    version = second.find(index.tag("Version"))
    first_key, second_key = index.key(first), index.key(second)
    assert version is not None and first_key and second_key
    version.text = "draft"
    before = tostring(fragment.root)
    names = [first_key[1], second_key[1]]
    assert _outcome(lambda: fragment.revise(*names, dry_run=True)) == "DDIModelError"
    assert tostring(fragment.root) == before


def test_a_dry_run_given_an_element_plans_for_that_element() -> None:
    import copy

    fragment = ddi_l.open_fragment(FIXTURE)
    index = _Items(fragment)
    referred = {
        index.key(reference)
        for item in index.latest()
        for reference in index.references(item)
        if reference.get("lateBound") != "true"
    }
    # An item something pins, so revising it cascades.
    original = next(item for item in index.latest() if index.key(item) in referred)
    # The same ID under another agency, in a fragment of its own: nothing
    # refers to it.
    other = copy.deepcopy(original)
    agency = other.find(index.tag("Agency"))
    assert agency is not None
    agency.text = "other.example"
    holder = next(fragment.iter_fragments())
    wrapper = copy.deepcopy(holder)
    wrapper.clear()
    wrapper.append(other)
    fragment.root.append(wrapper)
    dry = fragment.revise(other, dry_run=True, version_date=STAMP)
    real = fragment.revise(other, version_date=STAMP)
    assert dry.steps == real.steps
    assert len(real.steps) == 1
    assert other.findtext(index.tag("Version")) == real.steps[0].new_version
    assert original.findtext(index.tag("Version")) == real.steps[0].old_version
