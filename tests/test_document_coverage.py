"""Edge cases and error paths in ddi_l.document and ddi_l.document_maintainables."""

import textwrap

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.document import (
    DDIDocument,
    DDIFragment,
    _collect_used_namespace_uris,
    _create_international_string,
)
from ddi_l.models.base import Reference, qn
from ddi_l.models.logicalproduct import Variable
from ddi_l.models.study import StudyUnit

# ---------------------------------------------------------------------------
# _create_international_string
# ---------------------------------------------------------------------------


def test_create_international_string():
    elem = _create_international_string("Title", "My Title")
    assert elem.tag == qn(REUSABLE_NS, "Title")


# ---------------------------------------------------------------------------
# _collect_used_namespace_uris
# ---------------------------------------------------------------------------


def test_collect_used_namespace_uris():
    root = create_element(qn(INSTANCE_NS, "DDIInstance"))
    child = create_element(qn(REUSABLE_NS, "ID"))
    root.append(child)
    uris = _collect_used_namespace_uris(root)
    assert INSTANCE_NS in uris
    assert REUSABLE_NS in uris


# ---------------------------------------------------------------------------
# DDIDocument
# ---------------------------------------------------------------------------


def test_document_create_basic():
    doc = DDIDocument.create(agency="a", identifier="doc1", version="1.0")
    assert isinstance(doc, DDIDocument)
    ident = doc.get_identification()
    assert ident["agency"] == "a"
    assert ident["id"] == "doc1"
    assert ident["version"] == "1.0"


def test_document_create_with_title():
    doc = DDIDocument.create(
        agency="a", identifier="doc1", version="1.0", title="My Title"
    )
    xml = doc.to_xml()
    assert "My Title" in xml


def test_document_set_identification():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    doc.set_identification(agency="b", identifier="d2", version="2.0")
    ident = doc.get_identification()
    assert ident["agency"] == "b"
    assert ident["id"] == "d2"


def test_document_set_identification_with_scope():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    doc.set_identification(
        agency="a", identifier="d1", version="1.0", scope_of_uniqueness="Agency"
    )
    assert doc.root.get("scopeOfUniqueness") == "Agency"
    # Update without scope clears it
    doc.set_identification(agency="a", identifier="d1", version="1.0")
    assert doc.root.get("scopeOfUniqueness") is None


def test_document_set_citation():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    citation = doc.set_citation(title="First")
    assert citation is not None
    # Update title
    doc.set_citation(title="Second")
    xml = doc.to_xml()
    assert "Second" in xml


def test_document_set_citation_no_title():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    citation = doc.set_citation()
    assert citation is not None


def test_document_from_xml():
    xml = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
            <r:Agency>a</r:Agency>
            <r:ID>d1</r:ID>
            <r:Version>1.0</r:Version>
        </DDIInstance>
    """)
    doc = DDIDocument.from_xml(xml)
    assert isinstance(doc, DDIDocument)


def test_document_from_xml_no_index():
    xml = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
            <r:Agency>a</r:Agency>
            <r:ID>d1</r:ID>
            <r:Version>1.0</r:Version>
        </DDIInstance>
    """)
    doc = DDIDocument.from_xml(xml, build_index=False)
    assert doc._index is None


def test_document_to_xml():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    xml = doc.to_xml()
    assert "DDIInstance" in xml


def test_document_to_dict():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    d = doc.to_dict()
    assert isinstance(d, dict)


def test_document_from_dict():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    d = doc.to_dict()
    # Wrap in root tag
    root_tag = qn(INSTANCE_NS, "DDIInstance")
    doc2 = DDIDocument.from_dict({root_tag: d})
    assert isinstance(doc2, DDIDocument)


def test_document_to_etree():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    assert doc.to_etree() is doc.root


def test_document_resolver():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    resolver = doc.resolver
    assert resolver is not None
    # Second access returns cached
    assert doc.resolver is resolver


def test_document_invalid_root():
    root = create_element(qn(INSTANCE_NS, "FragmentInstance"))
    with pytest.raises(ValueError, match="DDIInstance"):
        DDIDocument(root)


def test_document_iter_study_units():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    studies = list(doc.iter_study_units())
    assert studies == []


def test_document_add_study_unit():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    su = StudyUnit(
        agency="a",
        identifier="su1",
        version="1.0",
        data_collection_references=[
            Reference(
                identifier="dc1",
                agency="a",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    doc.add_study_unit(su)
    studies = list(doc.iter_study_units())
    assert len(studies) == 1


def test_document_resolve_maintainable():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    su = StudyUnit(
        agency="a",
        identifier="su1",
        version="1.0",
        data_collection_references=[
            Reference(
                identifier="dc1",
                agency="a",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    doc.add_study_unit(su)
    result = doc.resolve(("a", "su1", "1.0"), type=StudyUnit)
    assert isinstance(result, StudyUnit)


def test_document_resolve_passthrough():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    su = StudyUnit(
        agency="a",
        identifier="su1",
        version="1.0",
        data_collection_references=[
            Reference(
                identifier="dc1",
                agency="a",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    # Passing a MaintainableBase directly returns it
    result = doc.resolve(su, type=StudyUnit)
    assert result is su


def test_document_resolve_wrong_type():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    v = Variable(agency="a", identifier="v1", version="1.0")
    with pytest.raises(TypeError, match="does not match"):
        doc.resolve(v, type=StudyUnit)


def test_document_resolve_bad_type_arg():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    with pytest.raises(TypeError, match="subclass"):
        doc.resolve(("a", "su1", "1.0"), type=str)  # type: ignore[arg-type]


def test_document_resolve_by_reference():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    su = StudyUnit(
        agency="a",
        identifier="su1",
        version="1.0",
        data_collection_references=[
            Reference(
                identifier="dc1",
                agency="a",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    doc.add_study_unit(su)
    ref = Reference(
        identifier="su1", agency="a", version="1.0", type_of_object="StudyUnit"
    )
    result = doc.resolve(ref)
    assert isinstance(result, StudyUnit)


def test_document_resolve_by_string():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    su = StudyUnit(
        agency="a",
        identifier="su1",
        version="1.0",
        urn="urn:ddi:a:su1:1.0",
        data_collection_references=[
            Reference(
                identifier="dc1",
                agency="a",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    doc.add_study_unit(su)
    result = doc.resolve("urn:ddi:a:su1:1.0", type=StudyUnit)
    assert isinstance(result, StudyUnit)


def test_document_resolve_tuple_wrong_length():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    with pytest.raises(ValueError, match="agency, identifier, version"):
        doc.resolve(("a", "b"))  # type: ignore[arg-type]


def test_document_resolve_unsupported_type():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    with pytest.raises(TypeError, match="Unsupported"):
        doc.resolve(42)  # type: ignore[arg-type]


def test_document_replace_maintainable():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    su = StudyUnit(
        agency="a",
        identifier="su1",
        version="1.0",
        data_collection_references=[
            Reference(
                identifier="dc1",
                agency="a",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    doc.add_study_unit(su)
    # Replace with same identity (identifier match)
    su2 = StudyUnit(
        agency="a",
        identifier="su1",
        version="1.0",
        data_collection_references=[
            Reference(
                identifier="dc2",
                agency="a",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    doc.replace_maintainable(su2)


def test_document_remove_maintainable():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    su = StudyUnit(
        agency="a",
        identifier="su1",
        version="1.0",
        data_collection_references=[
            Reference(
                identifier="dc1",
                agency="a",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    doc.add_study_unit(su)
    removed = doc.remove_maintainable(("a", "su1", "1.0"), maintainable_type=StudyUnit)
    assert removed is True


def test_document_remove_maintainable_not_found():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    removed = doc.remove_maintainable(
        ("a", "nonexist", "1.0"), maintainable_type=StudyUnit
    )
    assert removed is False


# ---------------------------------------------------------------------------
# DDIFragment
# ---------------------------------------------------------------------------


def test_fragment_create():
    frag = DDIFragment.create()
    assert isinstance(frag, DDIFragment)


def test_fragment_invalid_root():
    root = create_element(qn(INSTANCE_NS, "DDIInstance"))
    with pytest.raises(ValueError, match="FragmentInstance"):
        DDIFragment(root)


def test_fragment_from_xml():
    xml = textwrap.dedent(f"""\
        <FragmentInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
        </FragmentInstance>
    """)
    frag = DDIFragment.from_xml(xml)
    assert isinstance(frag, DDIFragment)


def test_fragment_to_xml():
    frag = DDIFragment.create()
    xml = frag.to_xml()
    assert "FragmentInstance" in xml


def test_fragment_to_dict():
    frag = DDIFragment.create()
    d = frag.to_dict()
    # Empty fragment may return dict, str, or None
    assert d is None or isinstance(d, (dict, str))


def test_fragment_to_etree():
    frag = DDIFragment.create()
    assert frag.to_etree() is frag.root


def test_fragment_set_top_level_reference():
    frag = DDIFragment.create()
    ref = Reference(
        identifier="v1", agency="a", version="1.0", type_of_object="Variable"
    )
    elem = frag.set_top_level_reference(ref)
    assert elem is not None
    retrieved = frag.get_top_level_reference()
    assert retrieved is not None
    assert retrieved.identifier == "v1"


def test_fragment_set_top_level_reference_from_maintainable():
    frag = DDIFragment.create()
    v = Variable(agency="a", identifier="v1", version="1.0")
    elem = frag.set_top_level_reference(v)
    assert elem is not None


def test_fragment_set_top_level_reference_clear():
    frag = DDIFragment.create()
    ref = Reference(
        identifier="v1", agency="a", version="1.0", type_of_object="Variable"
    )
    frag.set_top_level_reference(ref)
    frag.set_top_level_reference(None)
    assert frag.get_top_level_reference() is None


def test_fragment_set_top_level_reference_unsupported():
    frag = DDIFragment.create()
    with pytest.raises(TypeError, match="Unsupported"):
        frag.set_top_level_reference("not valid")  # type: ignore[arg-type]


def test_fragment_add_fragment_maintainable():
    frag = DDIFragment.create()
    v = Variable(agency="a", identifier="v1", version="1.0")
    elem = frag.add_fragment(v)
    assert elem is not None


def test_fragment_add_fragment_element():
    frag = DDIFragment.create()
    elem = create_element("test")
    result = frag.add_fragment(elem)
    assert result is not None


def test_fragment_add_fragment_iterable():
    frag = DDIFragment.create()
    e1 = create_element("a")
    e2 = create_element("b")
    result = frag.add_fragment([e1, e2])
    assert result is not None


def test_fragment_add_fragment_bad_iterable():
    frag = DDIFragment.create()
    with pytest.raises(TypeError, match="Element instances"):
        frag.add_fragment(["not", "elements"])  # type: ignore[list-item]


def test_fragment_iter_fragments():
    frag = DDIFragment.create()
    v = Variable(agency="a", identifier="v1", version="1.0")
    frag.add_fragment(v)
    fragments = list(frag.iter_fragments())
    assert len(fragments) == 1


def test_fragment_iter_fragment_payloads():
    frag = DDIFragment.create()
    v = Variable(agency="a", identifier="v1", version="1.0")
    frag.add_fragment(v)
    payloads = list(frag.iter_fragment_payloads())
    assert len(payloads) == 1


def test_fragment_create_with_top_level():
    ref = Reference(
        identifier="v1", agency="a", version="1.0", type_of_object="Variable"
    )
    frag = DDIFragment.create(top_level=ref)
    retrieved = frag.get_top_level_reference()
    assert retrieved is not None


# ---------------------------------------------------------------------------
# document_maintainables — MaintainableManagementMixin
# ---------------------------------------------------------------------------


def test_iter_maintainables_bad_type():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    with pytest.raises(TypeError, match="subclass"):
        list(doc.iter_maintainables(str))  # type: ignore[type-var]


def test_add_maintainable_bad_type():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    with pytest.raises(TypeError, match="MaintainableBase"):
        doc.add_maintainable("not a maintainable")  # type: ignore[arg-type]


def test_replace_maintainable_bad_type():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    with pytest.raises(TypeError, match="MaintainableBase"):
        doc.replace_maintainable("not a maintainable")  # type: ignore[arg-type]


def test_replace_maintainable_no_identity():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    su = StudyUnit(
        agency=None,
        identifier="",
        version=None,
        data_collection_references=[
            Reference(
                identifier="dc1",
                agency="a",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    with pytest.raises(ValueError, match="URN or identifier"):
        doc.replace_maintainable(su)


def test_replace_maintainable_not_found():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    su = StudyUnit(
        agency="a",
        identifier="notfound",
        version="1.0",
        data_collection_references=[
            Reference(
                identifier="dc1",
                agency="a",
                version="1.0",
                type_of_object="DataCollection",
            )
        ],
    )
    with pytest.raises(LookupError, match="not found"):
        doc.replace_maintainable(su)


def test_remove_maintainable_no_identity():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    ref = Reference()  # empty
    with pytest.raises(ValueError, match="URN or identifier"):
        doc.remove_maintainable(ref)


def test_reference_metadata_str():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    urn, key, _cls = doc._reference_metadata("urn:ddi:a:su1:1.0")
    assert urn == "urn:ddi:a:su1:1.0"
    assert key is None


def test_reference_metadata_tuple():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    urn, key, _cls = doc._reference_metadata(("a", "su1", "1.0"))
    assert urn is None
    assert key == ("a", "su1", "1.0")


def test_reference_metadata_tuple_wrong_length():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    with pytest.raises(ValueError, match="agency, identifier, version"):
        doc._reference_metadata(("a", "b"))  # type: ignore[arg-type]


def test_reference_metadata_unsupported():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    with pytest.raises(TypeError, match="Unsupported"):
        doc._reference_metadata(42)  # type: ignore[arg-type]


def test_reference_metadata_reference_with_type():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    ref = Reference(
        identifier="su1", agency="a", version="1.0", type_of_object="StudyUnit"
    )
    _urn, key, cls = doc._reference_metadata(ref)
    assert key == ("a", "su1", "1.0")
    assert cls is StudyUnit


def test_metadata_matches_urn():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    assert doc._metadata_matches("urn:1", None, "urn:1", None) is True
    assert doc._metadata_matches("urn:1", None, "urn:2", None) is False


def test_metadata_matches_key():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    assert (
        doc._metadata_matches(None, ("a", "x", "1.0"), None, ("a", "x", "1.0")) is True
    )
    assert (
        doc._metadata_matches(None, ("a", "x", "1.0"), None, ("a", "y", "1.0")) is False
    )


def test_metadata_matches_version_mismatch():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    assert (
        doc._metadata_matches(None, ("a", "x", "1.0"), None, ("a", "x", "2.0")) is False
    )


def test_metadata_matches_agency_mismatch():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    assert (
        doc._metadata_matches(None, ("a", "x", "1.0"), None, ("b", "x", "1.0")) is False
    )


def test_metadata_matches_none_both():
    doc = DDIDocument.create(agency="a", identifier="d1", version="1.0")
    assert doc._metadata_matches(None, None, None, None) is False
