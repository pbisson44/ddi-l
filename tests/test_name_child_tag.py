"""Names built in code are written with ``r:String``.

Every ``...Name`` element (``d:ConstructName``, ``r:Name``, ``l:VariableName``)
is of a type derived from ``r:InternationalStringType``, whose only child is
``r:String``. Labels and descriptions hold ``r:Content``. A name built in code
used to take ``InternationalString``'s default ``r:Content``, so the item failed
schema validation; names read from a file keep the tag they were read with.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import Any

import pytest

import ddi_l.models
from ddi_l import DDIFragment
from ddi_l._etree import fromstring
from ddi_l.models import ComputationItem, QuestionConstruct
from ddi_l.models.base import InternationalString, MaintainableBase
from ddi_l.namespaces import DATA_COLLECTION_NS, REUSABLE_NS

STRING = f"{{{REUSABLE_NS}}}String"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
CONSTRUCT_NAME = f"{{{DATA_COLLECTION_NS}}}ConstructName"
ITEM = "22222222-2222-4222-8222-000000000901"

# Items that cannot be built from a name alone: the field is never written, or
# the model refuses an item with nothing else in it.
UNBUILDABLE = {
    "ddi_l.models.conceptualcomponent.ConceptualComponent",
    "ddi_l.models.logicalproduct.LogicalProduct",
}


def _public_models() -> list[type[MaintainableBase]]:
    found: dict[str, type[MaintainableBase]] = {}
    for module in pkgutil.walk_packages(ddi_l.models.__path__, "ddi_l.models."):
        if "_generated" in module.name:
            continue
        namespace = importlib.import_module(module.name)
        for name in getattr(namespace, "__all__", ()):
            cls = getattr(namespace, name, None)
            if (
                inspect.isclass(cls)
                and issubclass(cls, MaintainableBase)
                and not name.endswith("Fields")
            ):
                found[f"{cls.__module__}.{cls.__qualname__}"] = cls
    return [found[key] for key in sorted(found)]


def _name_fields() -> list[tuple[Any, str, str, bool]]:
    cases = []
    for cls in _public_models():
        if f"{cls.__module__}.{cls.__qualname__}" in UNBUILDABLE:
            continue
        field_map = getattr(cls, "_FIELD_XML_MAP", {})
        for field_name, (tag, kind, is_list) in field_map.items():
            if kind == "intl_string":
                cases.append((cls, field_name, tag, is_list))
    return cases


NAME_FIELDS = _name_fields()


def test_the_sweep_covers_the_generated_name_fields() -> None:
    # A guard against the discovery above silently finding nothing.
    assert len(NAME_FIELDS) > 100


@pytest.mark.parametrize(
    ("cls", "field_name", "tag", "is_list"),
    NAME_FIELDS,
    ids=[f"{case[0].__name__}.{case[1]}" for case in NAME_FIELDS],
)
def test_a_name_built_in_code_is_written_with_r_string(
    cls: Any, field_name: str, tag: str, is_list: bool
) -> None:
    name = InternationalString(text="x", lang="en")
    item = cls(
        agency="int.example",
        identifier=ITEM,
        version="1",
        **{field_name: [name] if is_list else name},
    )
    containers = item.to_xml().findall(tag)
    assert containers
    assert [child.tag for container in containers for child in container] == [
        STRING
    ] * sum(len(container) for container in containers)
    issues = DDIFragment.from_items([item]).validate()
    assert not [issue for issue in issues if "String' expected" in str(issue)]


@pytest.mark.parametrize("cls", [ComputationItem, QuestionConstruct])
def test_a_named_construct_validates(
    cls: type[ComputationItem] | type[QuestionConstruct],
) -> None:
    item = cls(
        agency="int.example",
        identifier=ITEM,
        version="1",
        construct_names=[
            InternationalString(text="total", lang="en"),
            InternationalString(text="total", lang="fr"),
        ],
    )
    element = item.to_xml()
    (container,) = element.findall(CONSTRUCT_NAME)
    assert [child.tag for child in container] == [STRING, STRING]
    assert DDIFragment.from_items([item]).validate() == []


def _parsed(child: str) -> ComputationItem:
    return ComputationItem.from_xml(
        fromstring(
            f'<d:ComputationItem xmlns:d="{DATA_COLLECTION_NS}" '
            f'xmlns:r="{REUSABLE_NS}" isUniversallyUnique="true">'
            "<r:Agency>int.example</r:Agency>"
            f"<r:ID>{ITEM}</r:ID>"
            "<r:Version>1</r:Version>"
            f'<d:ConstructName><r:{child} xml:lang="en">total</r:{child}>'
            "</d:ConstructName>"
            "</d:ComputationItem>"
        )
    )


def test_a_parsed_name_is_written_as_read() -> None:
    item = _parsed("String")
    assert item.construct_names[0].child_tag == "String"
    (container,) = item.to_xml().findall(CONSTRUCT_NAME)
    assert [child.tag for child in container] == [STRING]


def test_a_language_added_to_a_parsed_name_joins_its_container() -> None:
    item = _parsed("String")
    item.construct_names.append(InternationalString(text="total", lang="fr"))
    (container,) = item.to_xml().findall(CONSTRUCT_NAME)
    assert [child.tag for child in container] == [STRING, STRING]
    assert [child.get(XML_LANG) for child in container] == ["en", "fr"]
    assert DDIFragment.from_items([item]).validate() == []


def test_a_second_string_in_a_language_starts_a_container() -> None:
    item = _parsed("String")
    item.construct_names.append(InternationalString(text="sum", lang="en"))
    containers = item.to_xml().findall(CONSTRUCT_NAME)
    assert [[c.get(XML_LANG) for c in container] for container in containers] == [
        ["en"],
        ["en"],
    ]


def test_an_added_language_joins_the_last_container_read() -> None:
    item = ComputationItem.from_xml(
        fromstring(
            f'<d:ComputationItem xmlns:d="{DATA_COLLECTION_NS}" '
            f'xmlns:r="{REUSABLE_NS}">'
            "<r:Agency>int.example</r:Agency>"
            f"<r:ID>{ITEM}</r:ID>"
            "<r:Version>1</r:Version>"
            '<d:ConstructName><r:String xml:lang="en">total</r:String>'
            "</d:ConstructName>"
            '<d:ConstructName><r:String xml:lang="fr">somme</r:String>'
            "</d:ConstructName>"
            "</d:ComputationItem>"
        )
    )
    item.construct_names.append(InternationalString(text="Summe", lang="de"))
    containers = item.to_xml().findall(CONSTRUCT_NAME)
    assert [[c.get(XML_LANG) for c in container] for container in containers] == [
        ["en"],
        ["fr", "de"],
    ]


def test_an_added_language_keeps_the_container_attributes() -> None:
    item = ComputationItem.from_xml(
        fromstring(
            f'<d:ComputationItem xmlns:d="{DATA_COLLECTION_NS}" '
            f'xmlns:r="{REUSABLE_NS}">'
            "<r:Agency>int.example</r:Agency>"
            f"<r:ID>{ITEM}</r:ID>"
            "<r:Version>1</r:Version>"
            '<r:Label maxLength="40"><r:Content xml:lang="en">Total</r:Content>'
            "</r:Label>"
            "</d:ComputationItem>"
        )
    )
    item.labels.append(InternationalString(text="Total", lang="fr"))
    (label,) = item.to_xml().findall(f"{{{REUSABLE_NS}}}Label")
    assert label.get("maxLength") == "40"
    assert [c.get(XML_LANG) for c in label] == ["en", "fr"]


def test_a_name_read_with_r_content_is_repaired() -> None:
    # r:Content is invalid in a name; the item is written the way the schema
    # requires.
    item = _parsed("Content")
    (container,) = item.to_xml().findall(CONSTRUCT_NAME)
    assert [child.tag for child in container] == [STRING]
    assert DDIFragment.from_items([item]).validate() == []
