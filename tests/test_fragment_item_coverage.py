"""Every item type a DDI 3.3 fragment can carry survives the typed models.

A Colectica repository exchanges items one per ``<Fragment>``; DDI 3.3 lets a
fragment carry 161 kinds. Real exports cover a handful, so each type is
exercised here with samples built from the XSDs (``tests.helpers.xsd_samples``)
that fill every optional child and attribute to a depth limit, with choice
branches rotated across variants.

For each sample the test checks that it is schema-valid (else the generator,
not the model, is at fault and the case is skipped), that ``from_xml`` then
``to_xml`` reproduces it exactly -- same elements, attributes and text, in the
same order -- and that the output is schema-valid.
"""

from __future__ import annotations

import warnings
from collections.abc import Callable
from functools import lru_cache

import pytest

from ddi_l._etree import USING_LXML, Element, create_element
from ddi_l.constants import INSTANCE_NS
from ddi_l.models._generated.fragment_items import FRAGMENT_ITEM_TYPES
from ddi_l.models.base import MaintainableBase, qn
from ddi_l.schema_loader import _libxml2
from tests.helpers.xsd_samples import build_sample, schema

# Neither is an item: r:Note only annotates the item beside it in a fragment,
# and a whole DDIInstance is the document wrapper (DDIDocument), not a model.
_NOT_ITEMS = {qn(INSTANCE_NS, "DDIInstance"), "{ddi:reusable:3_3}Note"}
ITEM_TAGS = sorted(tag for tag in FRAGMENT_ITEM_TYPES if tag not in _NOT_ITEMS)
VARIANTS = (0, 1, 2)

Canonical = tuple[object, ...]


def _canonical(element: Element) -> Canonical:
    return (
        element.tag,
        tuple(sorted(element.attrib.items())),
        (element.text or "").strip(),
        tuple(_canonical(child) for child in element),
    )


def _in_fragment(element: Element) -> Element:
    root = create_element(qn(INSTANCE_NS, "FragmentInstance"))
    fragment = create_element(qn(INSTANCE_NS, "Fragment"))
    fragment.append(element)
    root.append(fragment)
    return root


@lru_cache(maxsize=1)
def _validator() -> Callable[[Element], str | None]:
    """Strict validation: libxml2 when lxml is installed, else xmlschema.

    Not ``schema_loader.validate``: it passes over the library's own
    extension types and fragment-only gaps, and these samples must be valid
    DDI outright.
    """
    compiled = _libxml2.get_libxml2_schema("3.3") if USING_LXML else None
    if compiled is not None:

        def libxml2(element: Element) -> str | None:
            if compiled.validate(element):
                return None
            return str(compiled.error_log.last_error)

        return libxml2

    def python(element: Element) -> str | None:
        error = next(schema().iter_errors(element), None)
        return None if error is None else str(error.reason)

    return python


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("tag", ITEM_TAGS, ids=lambda tag: tag.split("}")[1])
def test_item_round_trips_exactly(tag: str, variant: int) -> None:
    sample = build_sample(tag, variant=variant)
    if sample is None or _validator()(_in_fragment(sample)) is not None:
        pytest.skip("the generator could not build a valid sample")
    model = MaintainableBase.for_tag(sample.tag)
    assert model is not None, f"no typed model for {sample.tag}"
    with warnings.catch_warnings():
        # Samples reference items that are not in them.
        warnings.simplefilter("ignore")
        output = model.from_xml(sample).to_xml()
    assert _canonical(output) == _canonical(sample)
    assert _validator()(_in_fragment(output)) is None


def test_every_item_type_has_a_model() -> None:
    MaintainableBase.maintainable_types()
    missing = [tag for tag in ITEM_TAGS if MaintainableBase.for_tag(tag) is None]
    assert missing == []


# ---------------------------------------------------------------------------
# Edits still take effect
#
# Content a model does not map is written back as read: a scheme's own
# metadata around the items a module flattens, a StudyUnit's physical data
# products while their items are unchanged, a value wrapper while its fields
# are. These check that an edit is never masked by that.
# ---------------------------------------------------------------------------


def _parsed(tag: str, variant: int = 0) -> MaintainableBase:
    sample = build_sample(tag, variant=variant)
    assert sample is not None
    model = MaintainableBase.for_tag(sample.tag)
    assert model is not None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return model.from_xml(sample)


def _serialize(item: MaintainableBase) -> Element:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return item.to_xml()


def test_edit_inside_a_flattened_scheme_is_written() -> None:
    from ddi_l.models import ConceptualComponent

    component = _parsed("{ddi:conceptualcomponent:3_3}ConceptualComponent")
    assert isinstance(component, ConceptualComponent)
    concept = component.concepts[0]
    concept.version = "99"
    output = _serialize(component)
    scheme = output.find("{ddi:conceptualcomponent:3_3}ConceptScheme")
    assert scheme is not None
    versions = [
        node.findtext("{ddi:reusable:3_3}Version")
        for node in scheme.findall("{ddi:conceptualcomponent:3_3}Concept")
    ]
    assert "99" in versions
    # The scheme's own metadata is still the one read.
    assert scheme.find("{ddi:reusable:3_3}VersionRationale") is not None


def test_removed_items_leave_their_scheme() -> None:
    from ddi_l.models import ConceptualComponent

    component = _parsed("{ddi:conceptualcomponent:3_3}ConceptualComponent")
    assert isinstance(component, ConceptualComponent)
    component.concepts.clear()
    output = _serialize(component)
    assert not output.findall(
        "{ddi:conceptualcomponent:3_3}ConceptScheme/"
        "{ddi:conceptualcomponent:3_3}Concept"
    )


def test_edit_to_a_study_physical_structure_is_written() -> None:
    from ddi_l.models import StudyUnit

    study = _parsed("{ddi:studyunit:3_3}StudyUnit")
    assert isinstance(study, StudyUnit) and study.physical_structures
    study.physical_structures[0].version = "99"
    output = _serialize(study)
    structures = output.findall(".//{ddi:physicaldataproduct:3_3}PhysicalStructure")
    assert any(
        node.findtext("{ddi:reusable:3_3}Version") == "99" for node in structures
    )


def test_edit_to_a_preserved_value_wrapper_is_written() -> None:
    from ddi_l._etree import fromstring
    from ddi_l.models.logicalproduct import NumberRange

    element = fromstring(
        '<r:NumberRange xmlns:r="ddi:reusable:3_3">'
        '<r:Low isInclusive="1">0</r:Low><r:High>120</r:High></r:NumberRange>'
    )
    number_range = NumberRange.from_xml(element)
    assert _canonical(number_range.to_xml()) == _canonical(element)
    number_range.high = "150"
    assert number_range.to_xml().findtext("{ddi:reusable:3_3}High") == "150"
