"""A ``ConceptualComponent`` writes and reads its module names.

``c:ConceptualComponentModuleName`` set in code was never written, and one
read from a file was kept only as an unmapped element.
"""

from __future__ import annotations

from ddi_l import DDIFragment
from ddi_l._etree import Element, fromstring, tostring
from ddi_l.models import ConceptualComponent, InternationalString
from ddi_l.namespaces import CONCEPTUAL_COMPONENT_NS, REUSABLE_NS

C = CONCEPTUAL_COMPONENT_NS
R = REUSABLE_NS
MODULE_NAME = f"{{{C}}}ConceptualComponentModuleName"
STRING = f"{{{R}}}String"
ITEM = "22222222-2222-4222-8222-000000000950"


def _local_names(element: Element) -> list[str]:
    return [child.tag.rsplit("}", 1)[-1] for child in element]


def test_names_built_in_code_are_written_before_the_label() -> None:
    component = ConceptualComponent(
        agency="int.example",
        identifier=ITEM,
        version="1",
        conceptual_component_module_names=[
            InternationalString("Concepts", lang="en"),
            InternationalString("Concepts", lang="fr"),
        ],
        labels=[InternationalString("Pet concepts", lang="en")],
    )
    element = component.to_xml()
    names = _local_names(element)
    assert names.count("ConceptualComponentModuleName") == 1
    assert names.index("Version") < names.index("ConceptualComponentModuleName")
    assert names.index("ConceptualComponentModuleName") < names.index("Label")
    (container,) = element.findall(MODULE_NAME)
    assert [child.tag for child in container] == [STRING, STRING]
    assert DDIFragment.from_items([component]).validate() == []


def _parsed(child: str) -> tuple[ConceptualComponent, Element]:
    source = fromstring(
        f'<c:ConceptualComponent xmlns:c="{C}" xmlns:r="{R}" '
        'isUniversallyUnique="true">'
        f"<r:Agency>int.example</r:Agency><r:ID>{ITEM}</r:ID>"
        "<r:Version>1</r:Version>"
        f'<c:ConceptualComponentModuleName><r:{child} xml:lang="en">Concepts'
        f"</r:{child}></c:ConceptualComponentModuleName>"
        "</c:ConceptualComponent>"
    )
    return ConceptualComponent.from_xml(source), source


def test_names_read_from_a_file_are_mapped_and_written_as_read() -> None:
    component, source = _parsed("String")
    assert [(n.text, n.lang) for n in component.conceptual_component_module_names] == [
        ("Concepts", "en")
    ]
    assert not [c for c in component.other_elements if c.tag == MODULE_NAME]
    assert tostring(component.to_xml()) == tostring(source)


def test_a_name_read_with_r_content_is_repaired() -> None:
    component, _ = _parsed("Content")
    (container,) = component.to_xml().findall(MODULE_NAME)
    assert [child.tag for child in container] == [STRING]
