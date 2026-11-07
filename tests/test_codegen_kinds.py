"""The code generator gives a ``...Name`` field the kind its XSD type calls for.

A name is an ``intl_string`` (repeated ``r:String``) only when its type
derives from ``r:InternationalStringType``. ``a:IndividualName`` is an
``IndividualNameType`` of structured parts and stays a raw element, so its
``a:FirstGiven`` and the like are kept.
"""

from __future__ import annotations

import functools

from codegen.generate_model_bases import _python_kind_for_child
from codegen.xsd_introspect import ChildElement, introspect_schemas

from ddi_l._etree import fromstring
from ddi_l.models._generated.archive import IndividualIdentificationFields

A = "ddi:archive:3_3"


@functools.cache
def _children() -> dict[str, ChildElement]:
    found: dict[str, ChildElement] = {}
    for types in introspect_schemas().values():
        for info in types:
            for child in info.children:
                found.setdefault(child.name, child)
    return found


def test_every_intl_string_name_derives_from_international_string() -> None:
    names = [
        child
        for child in _children().values()
        if _python_kind_for_child(child) == "intl_string"
    ]
    assert len(names) > 100
    assert all(child.is_international_string for child in names)


def test_kinds_follow_the_type() -> None:
    children = _children()
    assert _python_kind_for_child(children[f"{{{A}}}IndividualName"]) == "element"
    assert (
        _python_kind_for_child(children["{ddi:logicalproduct:3_3}VariableName"])
        == "intl_string"
    )
    assert (
        _python_kind_for_child(children["{ddi:datacollection:3_3}ConstructName"])
        == "intl_string"
    )
    # An international string not typed as a *NameType stays raw: a single
    # field would keep only one of its languages.
    assert _python_kind_for_child(children[f"{{{A}}}FullName"]) == "element"


def test_an_individual_name_keeps_its_parts() -> None:
    source = fromstring(
        f'<a:IndividualIdentification xmlns:a="{A}">'
        "<a:IndividualName><a:FirstGiven>Ada</a:FirstGiven>"
        "<a:LastFamily>Lovelace</a:LastFamily></a:IndividualName>"
        "</a:IndividualIdentification>"
    )
    identification = IndividualIdentificationFields.from_xml(source)
    (name,) = identification.individual_names
    assert name.findtext(f"{{{A}}}FirstGiven") == "Ada"
    assert name.findtext(f"{{{A}}}LastFamily") == "Lovelace"
