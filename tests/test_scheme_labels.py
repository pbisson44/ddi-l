"""``set_scheme_label()`` must reach every wrapper the model layer generates.

Scheme wrappers (``ConceptScheme``, ``QuestionScheme``, ``CategoryScheme``
and the rest) are created during serialization. Two code paths build them --
``_append_child_identification`` and LogicalProduct's
``_append_inline_scheme_identification`` -- so each wrapper type is checked.
"""

from __future__ import annotations

import pytest

from ddi_l import schema_loader
from ddi_l._etree import create_element
from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.models import (
    Category,
    CodeItem,
    CodeList,
    Concept,
    ConceptualComponent,
    DataCollection,
    Instrument,
    InternationalString,
    LogicalProduct,
    QuestionItem,
    Reference,
    Universe,
    Variable,
    clone_element,
    qn,
)
from ddi_l.models._generated.label_slots import TAGS_ALLOWING_LABEL

AGENCY = "example.agency"
VERSION = "1.0"


def _name(text: str) -> InternationalString:
    return InternationalString(text=text, lang="en", child_tag="String")


def _conceptual_component() -> ConceptualComponent:
    return ConceptualComponent(
        agency=AGENCY,
        identifier="cc",
        version=VERSION,
        concepts=[
            Concept(agency=AGENCY, identifier="c1", version=VERSION, names=[_name("C")])
        ],
        universes=[
            Universe(
                agency=AGENCY, identifier="u1", version=VERSION, names=[_name("U")]
            )
        ],
        has_concept_scheme=True,
        has_universe_scheme=True,
    )


def _data_collection() -> DataCollection:
    return DataCollection(
        agency=AGENCY,
        identifier="dc",
        version=VERSION,
        questions=[QuestionItem(agency=AGENCY, identifier="q1", version=VERSION)],
        instruments=[
            Instrument(
                agency=AGENCY, identifier="i1", version=VERSION, names=[_name("I")]
            )
        ],
    )


def _logical_product() -> LogicalProduct:
    return LogicalProduct(
        agency=AGENCY,
        identifier="lp",
        version=VERSION,
        categories=[
            Category(
                agency=AGENCY, identifier="cat1", version=VERSION, names=[_name("Cat")]
            )
        ],
        code_lists=[
            CodeList(
                agency=AGENCY,
                identifier="cl1",
                version=VERSION,
                names=[_name("CL")],
                codes=[
                    # CodeType requires both a CategoryReference and a Value.
                    CodeItem(
                        agency=AGENCY,
                        identifier="code1",
                        version=VERSION,
                        value="1",
                        category=Reference(
                            type_of_object="Category",
                            agency=AGENCY,
                            identifier="cat1",
                            version=VERSION,
                        ),
                    )
                ],
            )
        ],
        variables=[
            Variable(
                agency=AGENCY, identifier="v1", version=VERSION, names=[_name("V")]
            )
        ],
    )


@pytest.mark.parametrize(
    ("build_model", "scheme"),
    [
        (_conceptual_component, "ConceptScheme"),
        (_conceptual_component, "UniverseScheme"),
        (_data_collection, "QuestionScheme"),
        (_data_collection, "InstrumentScheme"),
        # LogicalProduct reaches these through a *different* identification
        # helper than the three above.
        (_logical_product, "CategoryScheme"),
        (_logical_product, "CodeListScheme"),
        (_logical_product, "VariableScheme"),
    ],
)
def test_set_scheme_label_reaches_the_generated_wrapper(build_model, scheme) -> None:
    """The label lands on the wrapper, in the position the XSD requires."""
    model = build_model()
    model.set_scheme_label(scheme, f"My {scheme}")

    element = model.to_xml()
    wrapper = next(
        (node for node in element.iter() if node.tag.split("}")[-1] == scheme), None
    )
    assert wrapper is not None, f"{scheme} was not emitted at all"

    children = [child.tag.split("}")[-1] for child in wrapper]
    assert "Label" in children, f"{scheme} children were {children}"
    # r:Label follows identification and precedes the scheme's members.
    assert children.index("Label") > children.index("Version")


@pytest.mark.parametrize(
    ("build_model", "scheme"),
    [
        (_conceptual_component, "ConceptScheme"),
        (_data_collection, "QuestionScheme"),
        (_logical_product, "CategoryScheme"),
    ],
)
def test_labelled_schemes_still_validate(build_model, scheme) -> None:
    """A label added this way must not break schema validation."""
    model = build_model()
    model.set_scheme_label(scheme, f"My {scheme}")

    fragment_instance = create_element(
        qn(INSTANCE_NS, "FragmentInstance"),
        nsmap={None: INSTANCE_NS, "r": REUSABLE_NS},
    )
    fragment = create_element(qn(INSTANCE_NS, "Fragment"))
    fragment.append(clone_element(model.to_xml()))
    fragment_instance.append(fragment)

    assert schema_loader.validate(fragment_instance, raise_error=False) == []


def test_set_scheme_label_refuses_a_scheme_with_no_label_slot() -> None:
    """Labelling something the schema forbids must fail loudly, not silently."""
    model = _logical_product()

    with pytest.raises(ValueError, match="no element named"):
        model.set_scheme_label("NotARealScheme", "nope")

    # l:Code is the real-world case: Identifiable, carries Agency/ID/Version,
    # and CodeType declares no r:Label.
    assert qn("ddi:logicalproduct:3_3", "Code") not in TAGS_ALLOWING_LABEL
