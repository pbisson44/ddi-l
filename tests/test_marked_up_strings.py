"""Labels and descriptions holding XHTML keep it.

``r:Content`` is mixed content: XHTML beside the text. An
:class:`~ddi_l.models.base.InternationalString` holds plain text, the whole of
it, and a string read with markup is written back as read while it is
unchanged; an edited one is written as its text. Each language is its own
string, so editing one keeps the markup of the others.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import ddi_l
from ddi_l._etree import Element, fromstring, tostring
from ddi_l.models import Category, ComputationItem, OutParameter
from ddi_l.models.base import InternationalString, qn
from ddi_l.namespaces import REUSABLE_NS

R = REUSABLE_NS
XHTML = "http://www.w3.org/1999/xhtml"
CONDITIONS = (
    Path(__file__).parent / "fixtures" / "colectica" / "pets_conditions.ddi33.xml"
)
DOG = "22222222-2222-4222-8222-000000000002"
LOOKUP = "22222222-2222-4222-8222-000000000050"


def _x(name: str, text: str) -> str:
    return f'<{name} xmlns="{XHTML}">{text}</{name}>'


LABEL = f'<r:Content xml:lang="en-CA">{_x("b", "Owner")} lookup</r:Content>'
DESCRIPTION_EN = (
    f'<r:Content xml:lang="en-CA">{_x("p", "Reads the owner.")}'
    f"{_x('ul', _x('li', 'Name') + _x('li', 'Region'))}{_x('p', 'Then the pet.')}"
    "</r:Content>"
)
DESCRIPTION_FR = (
    f'<r:Content xml:lang="fr-CA">Lit le {_x("i", "propriétaire")}.</r:Content>'
)
DOG_EN = f'<r:Content xml:lang="en-CA">A {_x("b", "big")} dog</r:Content>'


def _source() -> bytes:
    """The conditions fixture with markup in a category's and a computation's text."""
    text = CONDITIONS.read_text(encoding="utf-8")
    dog = '<r:Content xml:lang="en-CA">Dog</r:Content>'
    assert text.count(dog) == 1
    text = text.replace(dog, DOG_EN)
    name = '<r:String xml:lang="en-CA">Owner lookup</r:String>\n    </ConstructName>'
    assert text.count(name) == 1
    text = text.replace(
        name,
        f"{name}\n    <r:Label>{LABEL}</r:Label>\n    "
        f"<r:Description>{DESCRIPTION_EN}{DESCRIPTION_FR}</r:Description>",
    )
    # Written once, so the layout is the writer's own.
    fragment = ddi_l.read_ddi(text.encode())
    assert isinstance(fragment, ddi_l.DDIFragment)
    return fragment.to_colectica_bytes()


def _fragment() -> ddi_l.DDIFragment:
    fragment = ddi_l.read_ddi(_source())
    assert isinstance(fragment, ddi_l.DDIFragment)
    return fragment


def _contents(element: Element, container: str) -> dict[str, Element]:
    node = element.find(qn(R, container))
    assert node is not None
    return {c.get("{http://www.w3.org/XML/1998/namespace}lang") or "": c for c in node}


def _inline(element: Element) -> str:
    """The content's children and text, without layout whitespace."""
    return " ".join(tostring(element, pretty_print=False).split())


def test_unchanged_marked_up_strings_are_written_as_read() -> None:
    source = _source()
    fragment = _fragment()
    for identifier in (DOG, LOOKUP):
        item = fragment.get(identifier)
        assert item is not None
        fragment.put(item)
    assert fragment.to_colectica_bytes() == source


def test_the_text_is_the_whole_string() -> None:
    fragment = _fragment()
    dog = fragment.get(DOG)
    lookup = fragment.get(LOOKUP)
    assert isinstance(dog, Category) and isinstance(lookup, ComputationItem)
    assert [(s.text, s.lang) for s in dog.labels] == [
        ("A big dog", "en-CA"),
        ("Chien", "fr-CA"),
    ]
    assert [s.text for s in lookup.labels] == ["Owner lookup"]
    assert [s.text for s in lookup.descriptions] == [
        "Reads the owner. Name Region Then the pet.",
        "Lit le propriétaire.",
    ]


def test_editing_one_language_keeps_the_others_markup() -> None:
    lookup = _fragment().get(LOOKUP)
    assert isinstance(lookup, ComputationItem)
    before = _contents(lookup.to_xml(), "Description")
    lookup.descriptions[1].text = "Lit le nom du propriétaire."
    after = _contents(lookup.to_xml(), "Description")
    assert _inline(after["en-CA"]) == _inline(before["en-CA"])
    assert [_local(c.tag) for c in after["en-CA"]] == ["p", "ul", "p"]
    assert (after["fr-CA"].text, len(after["fr-CA"])) == (
        "Lit le nom du propriétaire.",
        0,
    )


def test_adding_a_language_keeps_the_markup() -> None:
    dog = _fragment().get(DOG)
    assert isinstance(dog, Category)
    before = _contents(dog.to_xml(), "Label")
    dog.labels.append(InternationalString("Hund", lang="de"))
    after = _contents(dog.to_xml(), "Label")
    assert _inline(after["en-CA"]) == _inline(before["en-CA"])
    assert after["de"].text == "Hund"


def test_an_edited_marked_up_string_is_written_as_its_text() -> None:
    dog = _fragment().get(DOG)
    assert isinstance(dog, Category)
    dog.labels[0].text = "A large dog"
    label = _contents(dog.to_xml(), "Label")["en-CA"]
    assert (label.text, len(label)) == ("A large dog", 0)


def _local(tag: object) -> str:
    return str(tag).rsplit("}", 1)[-1]


PARAMETER = (
    f'<r:OutParameter xmlns:r="{R}" xmlns:x="{XHTML}" isUniversallyUnique="true">'
    '<r:URN typeOfIdentifier="Canonical">urn:ddi:int.example:'
    "22222222-2222-4222-8222-000000000903:1</r:URN>"
    "<r:Agency>int.example</r:Agency><r:ID>22222222-2222-4222-8222-000000000903</r:ID>"
    "<r:Version>1</r:Version><r:Alias>A</r:Alias>"
    '<r:Description><r:Content xml:lang="en">Kind <x:b>of</x:b> pet</r:Content>'
    '<r:Content xml:lang="fr">Type</r:Content></r:Description></r:OutParameter>'
)


def test_an_edited_parameter_keeps_its_urn_attributes() -> None:
    parameter = OutParameter.from_xml(fromstring(PARAMETER))
    parameter.alias = "B"
    urn = parameter.to_xml().find(qn(R, "URN"))
    assert urn is not None and urn.get("typeOfIdentifier") == "Canonical"


def test_editing_one_parameter_description_keeps_the_others_markup() -> None:
    parameter = OutParameter.from_xml(fromstring(PARAMETER))
    assert [d.text for d in parameter.descriptions] == ["Kind of pet", "Type"]
    parameter.descriptions[1].text = "Genre"
    contents = _contents(parameter.to_xml(), "Description")
    (bold,) = list(contents["en"])
    assert (contents["en"].text, bold.text, bold.tail) == ("Kind ", "of", " pet")
    assert contents["fr"].text == "Genre"


@pytest.mark.parametrize("kind", ["Label", "Description"])
def test_a_maintainable_with_markup_survives_to_xml(kind: str) -> None:
    item = ComputationItem.from_xml(
        fromstring(
            f'<d:ComputationItem xmlns:d="ddi:datacollection:3_3" xmlns:r="{R}" '
            f'xmlns:x="{XHTML}"><r:Agency>int.example</r:Agency>'
            "<r:ID>22222222-2222-4222-8222-000000000904</r:ID><r:Version>1</r:Version>"
            f'<r:{kind}><r:Content xml:lang="en"><x:b>Kind</x:b> of pet</r:Content>'
            f"</r:{kind}></d:ComputationItem>"
        )
    )
    content = _contents(item.to_xml(), kind)["en"]
    assert [_local(c.tag) for c in content] == ["b"]
    assert "".join(content.itertext()) == "Kind of pet"


def test_schema_order_keeps_the_pairs_of_a_repeating_group() -> None:
    # PublisherType repeats (name, then its roles): regrouping all names first
    # would hand one publisher's role to another, so the order read is kept.
    from ddi_l.models.base import order_by_schema

    def name(text: str) -> str:
        return (
            f'<r:PublisherName><r:String xml:lang="en">{text}</r:String>'
            "</r:PublisherName>"
        )

    publisher = fromstring(
        f'<r:Publisher xmlns:r="{R}">{name("Pet Org")}'
        f"<r:PublisherRole>Distributor</r:PublisherRole>{name('Vet Board')}"
        "<r:PublisherRole>Sponsor</r:PublisherRole></r:Publisher>"
    )
    order_by_schema(publisher)
    assert [_local(child.tag) for child in publisher] == [
        "PublisherName",
        "PublisherRole",
        "PublisherName",
        "PublisherRole",
    ]
