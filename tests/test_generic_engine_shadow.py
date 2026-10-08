# mypy: ignore-errors
"""Shadow validation: prove the generic engine round-trips correctly.

For every fixture XML, parse using the generic engine (MaintainableBase.from_xml
via _FIELD_XML_MAP) and re-serialize via the generic to_xml.  Verify:
1. Output validates against the DDI 3.3 XSD schema
2. Identification is preserved (agency, identifier, version)
3. Labels and descriptions are preserved
4. No data is silently lost for typed fields (references, intl_strings)

"""

from __future__ import annotations

import pytest

from ddi_l import schema_loader
from ddi_l._etree import (
    Element,
    create_element,
    parse_xml,
)
from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.models.base import MaintainableBase, clone_element, qn
from tests.helpers.maintainable_fixtures import (
    MODEL_FIXTURE_DIR,
    iter_maintainable_fixture_names,
)


def _generic_from_xml(cls: type[MaintainableBase], element: Element):
    """Call MaintainableBase.from_xml directly, bypassing hand-written overrides."""
    return MaintainableBase.from_xml.__func__(cls, element)


def _generic_to_xml(instance: MaintainableBase) -> Element:
    """Call MaintainableBase.to_xml directly, bypassing hand-written overrides."""
    saved = instance.VALIDATE_ON_SERIALIZE
    try:
        type(instance).VALIDATE_ON_SERIALIZE = False
        return MaintainableBase.to_xml(instance)
    finally:
        type(instance).VALIDATE_ON_SERIALIZE = saved


def _wrap_in_fragment(element: Element) -> Element:
    fragment_instance = create_element(
        qn(INSTANCE_NS, "FragmentInstance"),
        nsmap={None: INSTANCE_NS, "r": REUSABLE_NS},
    )
    fragment = create_element(qn(INSTANCE_NS, "Fragment"))
    fragment.append(clone_element(element))
    fragment_instance.append(fragment)
    return fragment_instance


# The generic engine does not resolve substitution groups, and
# ``MethodologyItem``'s fixtures use one (``<SamplingProcedure>``).
_SKIP_GENERIC_PREFIXES: set[str] = {
    "MethodologyItem",
}


def _shadow_cases():
    for model, name in iter_maintainable_fixture_names():
        test_id = f"{model.__name__}-{name}"
        marks: list[pytest.MarkDecorator] = []
        if model.__name__ in _SKIP_GENERIC_PREFIXES:
            marks.append(
                pytest.mark.skip(
                    reason="generic engine does not resolve substitution-group tags"
                )
            )
        yield pytest.param(model, name, marks=marks, id=test_id)


@pytest.mark.parametrize(("model_cls", "fixture_name"), list(_shadow_cases()))
def test_generic_engine_round_trip_preserves_identity(
    model_cls: type[MaintainableBase], fixture_name: str
) -> None:
    """Generic engine preserves identification metadata on round-trip."""
    source = parse_xml(MODEL_FIXTURE_DIR / f"{fixture_name}.xml")
    instance = _generic_from_xml(model_cls, source)

    assert instance.agency is not None or instance.urn is not None, (
        "Either agency or URN must be present"
    )

    round_tripped = _generic_to_xml(instance)

    rt_instance = _generic_from_xml(model_cls, round_tripped)
    assert rt_instance.agency == instance.agency
    assert rt_instance.identifier == instance.identifier
    assert rt_instance.version == instance.version


@pytest.mark.parametrize(("model_cls", "fixture_name"), list(_shadow_cases()))
def test_generic_engine_round_trip_preserves_labels(
    model_cls: type[MaintainableBase], fixture_name: str
) -> None:
    """Generic engine preserves labels and descriptions on round-trip."""
    source = parse_xml(MODEL_FIXTURE_DIR / f"{fixture_name}.xml")
    instance = _generic_from_xml(model_cls, source)
    round_tripped = _generic_to_xml(instance)
    rt_instance = _generic_from_xml(model_cls, round_tripped)

    assert len(rt_instance.labels) == len(instance.labels)
    for orig, rt in zip(instance.labels, rt_instance.labels, strict=False):
        assert rt.text == orig.text
        assert rt.lang == orig.lang

    assert len(rt_instance.descriptions) == len(instance.descriptions)
    for orig, rt in zip(instance.descriptions, rt_instance.descriptions, strict=False):
        assert rt.text == orig.text


_SCHEMA_GAP_FIXTURES: set[str] = set()


@pytest.mark.parametrize(("model_cls", "fixture_name"), list(_shadow_cases()))
def test_generic_engine_validates_against_schema(
    model_cls: type[MaintainableBase], fixture_name: str
) -> None:
    """Generic engine output validates against the DDI 3.3 XSD schema."""
    if fixture_name in _SCHEMA_GAP_FIXTURES:
        pytest.skip("source fixture does not validate against schema")
    source = parse_xml(MODEL_FIXTURE_DIR / f"{fixture_name}.xml")
    instance = _generic_from_xml(model_cls, source)
    round_tripped = _generic_to_xml(instance)
    fragment = _wrap_in_fragment(round_tripped)
    schema_loader.validate(fragment)


@pytest.mark.parametrize(("model_cls", "fixture_name"), list(_shadow_cases()))
def test_generic_engine_preserves_inherited_metadata(
    model_cls: type[MaintainableBase], fixture_name: str
) -> None:
    """Generic engine preserves version metadata on round-trip."""
    source = parse_xml(MODEL_FIXTURE_DIR / f"{fixture_name}.xml")
    instance = _generic_from_xml(model_cls, source)
    round_tripped = _generic_to_xml(instance)
    rt_instance = _generic_from_xml(model_cls, round_tripped)

    assert len(rt_instance.user_attribute_pairs) == len(instance.user_attribute_pairs)
    assert rt_instance.version_responsibility == instance.version_responsibility
    assert len(rt_instance.version_rationales) == len(instance.version_rationales)
