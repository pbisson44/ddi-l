# mypy: ignore-errors
"""Tests for document_mixins.py — DocumentQueryMixin, DocumentManipulationMixin, DocumentStatsMixin."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from ddi_l._document_mixins import (
    DocumentManipulationMixin,
    DocumentQueryMixin,
    DocumentStatsMixin,
    MaintainableAccessor,
)
from ddi_l._etree import create_element
from ddi_l.models.base import InternationalString, MaintainableBase, Reference

# ---------------------------------------------------------------------------
# Stub maintainable for testing
# ---------------------------------------------------------------------------


@dataclass
class StubMaintainable(MaintainableBase):
    TAG = "{http://stub}Stub"
    names: list[InternationalString] = field(default_factory=list)
    concept_reference: Reference | None = None
    refs: list[Reference] = field(default_factory=list)

    @classmethod
    def from_xml(cls, element):
        return cls()

    def to_xml(self):
        return create_element(self.TAG)


@dataclass
class StubVariable(MaintainableBase):
    TAG = "{http://stub}Variable"
    names: list[InternationalString] = field(default_factory=list)
    concept_reference: Reference | None = None
    refs: list[Reference] = field(default_factory=list)

    @classmethod
    def from_xml(cls, element):
        return cls()

    def to_xml(self):
        return create_element(self.TAG)


# ---------------------------------------------------------------------------
# Concrete document class using the mixins
# ---------------------------------------------------------------------------


class StubDocument(DocumentQueryMixin, DocumentManipulationMixin, DocumentStatsMixin):
    def __init__(self, maintainables=None):
        self._root = create_element("{http://stub}Root")
        self._index = None
        self._maintainables: list[MaintainableBase] = list(maintainables or [])

    def iter_maintainables(self, *types):
        for m in self._maintainables:
            if not types or isinstance(m, types):
                yield m

    def add_maintainable(self, maintainable):
        self._maintainables.append(maintainable)

    def remove_maintainable(self, maintainable):
        try:
            self._maintainables.remove(maintainable)
            return True
        except ValueError:
            return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make(
    cls=StubMaintainable,
    identifier="id1",
    agency="test.org",
    version="1.0",
    labels=None,
    names=None,
):
    obj = cls()
    obj.identifier = identifier
    obj.agency = agency
    obj.version = version
    if labels is not None:
        obj.labels = labels
    if names is not None:
        obj.names = names
    return obj


def _label(text, lang="en"):
    return InternationalString(text=text, lang=lang)


# ===========================================================================
# DocumentQueryMixin
# ===========================================================================


class TestFindByIdentifier:
    def test_found(self):
        m = _make(identifier="abc")
        doc = StubDocument([m])
        assert doc.find_by_identifier("abc") is m

    def test_not_found(self):
        doc = StubDocument([_make(identifier="abc")])
        assert doc.find_by_identifier("xyz") is None

    def test_type_filter(self):
        s = _make(StubMaintainable, identifier="x")
        v = _make(StubVariable, identifier="x")
        doc = StubDocument([s, v])
        assert doc.find_by_identifier("x", StubVariable) is v


class TestFindByUrn:
    def test_exact_urn_match(self):
        m = _make()
        m.urn = "urn:ddi:test.org:id1:1.0"
        doc = StubDocument([m])
        assert doc.find_by_urn("urn:ddi:test.org:id1:1.0") is m

    def test_computed_urn_match(self):
        m = _make(identifier="id1", agency="test.org", version="1.0")
        doc = StubDocument([m])
        assert doc.find_by_urn("urn:ddi:test.org:id1:1.0") is m

    def test_case_insensitive(self):
        m = _make(identifier="id1", agency="test.org", version="1.0")
        doc = StubDocument([m])
        assert doc.find_by_urn("URN:DDI:test.org:id1:1.0") is m

    def test_not_found(self):
        doc = StubDocument([_make()])
        assert doc.find_by_urn("urn:ddi:nope:nope:1.0") is None

    def test_type_filter(self):
        m = _make(StubMaintainable, identifier="id1", agency="a", version="1.0")
        doc = StubDocument([m])
        assert doc.find_by_urn("urn:ddi:a:id1:1.0", StubVariable) is None
        assert doc.find_by_urn("urn:ddi:a:id1:1.0", StubMaintainable) is m


class TestFindByLabel:
    def test_substring_match(self):
        m = _make(labels=[_label("My Age Variable")])
        doc = StubDocument([m])
        assert doc.find_by_label("age") == [m]

    def test_exact_match(self):
        m = _make(labels=[_label("Age")])
        doc = StubDocument([m])
        assert doc.find_by_label("Age", exact=True) == [m]
        assert doc.find_by_label("Ag", exact=True) == []

    def test_case_sensitive(self):
        m = _make(labels=[_label("Age")])
        doc = StubDocument([m])
        assert doc.find_by_label("age", case_sensitive=True) == []
        assert doc.find_by_label("Age", case_sensitive=True) == [m]

    def test_no_labels_attribute(self):
        m = _make()
        doc = StubDocument([m])
        assert doc.find_by_label("anything") == []

    def test_type_filter(self):
        s = _make(StubMaintainable, labels=[_label("hello")])
        v = _make(StubVariable, labels=[_label("hello")])
        doc = StubDocument([s, v])
        assert doc.find_by_label("hello", StubVariable) == [v]

    def test_none_label_text(self):
        label = _label("")
        label.text = None
        m = _make(labels=[label])
        doc = StubDocument([m])
        assert doc.find_by_label("anything") == []


class TestFindByName:
    def test_substring_match(self):
        m = _make(names=[_label("My Variable Name")])
        doc = StubDocument([m])
        assert doc.find_by_name("variable") == [m]

    def test_exact_match(self):
        m = _make(names=[_label("Age")])
        doc = StubDocument([m])
        assert doc.find_by_name("Age", exact=True) == [m]
        assert doc.find_by_name("Ag", exact=True) == []

    def test_case_sensitive(self):
        m = _make(names=[_label("Age")])
        doc = StubDocument([m])
        assert doc.find_by_name("age", case_sensitive=True) == []

    def test_type_filter(self):
        m = _make(StubVariable, names=[_label("hello")])
        doc = StubDocument([m])
        assert doc.find_by_name("hello", StubMaintainable) == []

    def test_none_name_text(self):
        name = _label("")
        name.text = None
        m = _make(names=[name])
        doc = StubDocument([m])
        assert doc.find_by_name("anything") == []


class TestTypeSpecificAccessors:
    def test_variables_property(self):
        doc = StubDocument()
        accessor = doc.variables
        assert isinstance(accessor, MaintainableAccessor)

    def test_questions_property(self):
        doc = StubDocument()
        accessor = doc.questions
        assert isinstance(accessor, MaintainableAccessor)

    def test_concepts_property(self):
        doc = StubDocument()
        accessor = doc.concepts
        assert isinstance(accessor, MaintainableAccessor)

    def test_code_lists_property(self):
        doc = StubDocument()
        accessor = doc.code_lists
        assert isinstance(accessor, MaintainableAccessor)


class TestResolveReference:
    def test_resolve_by_urn(self):
        m = _make()
        m.urn = "urn:ddi:test.org:id1:1.0"
        doc = StubDocument([m])
        ref = Reference(urn="urn:ddi:test.org:id1:1.0")
        assert doc.resolve_reference(ref) is m

    def test_resolve_by_identifier(self):
        m = _make(identifier="abc", agency="org", version="1.0")
        doc = StubDocument([m])
        ref = Reference(identifier="abc", agency="org", version="1.0")
        assert doc.resolve_reference(ref) is m

    def test_resolve_agency_mismatch(self):
        m = _make(identifier="abc", agency="org1", version="1.0")
        doc = StubDocument([m])
        ref = Reference(identifier="abc", agency="org2", version="1.0")
        assert doc.resolve_reference(ref) is None

    def test_resolve_version_mismatch(self):
        m = _make(identifier="abc", agency="org", version="1.0")
        doc = StubDocument([m])
        ref = Reference(identifier="abc", agency="org", version="2.0")
        assert doc.resolve_reference(ref) is None

    def test_resolve_no_urn_no_identifier(self):
        doc = StubDocument([_make()])
        ref = Reference()
        assert doc.resolve_reference(ref) is None


class TestFindReferencesTo:
    def test_find_by_urn(self):
        target = _make(identifier="t1", agency="org", version="1.0")
        target.urn = "urn:ddi:org:t1:1.0"

        ref = Reference(urn="urn:ddi:org:t1:1.0")
        source = _make(identifier="s1")
        source.concept_reference = ref

        doc = StubDocument([target, source])
        refs = doc.find_references_to(target)
        assert ref in refs

    def test_find_by_identifier_fields(self):
        target = _make(identifier="t1", agency="org", version="1.0")
        ref = Reference(agency="org", identifier="t1", version="1.0")
        source = _make(identifier="s1")
        source.concept_reference = ref

        doc = StubDocument([target, source])
        refs = doc.find_references_to(target)
        assert ref in refs

    def test_ref_in_list(self):
        target = _make(identifier="t1", agency="org", version="1.0")
        ref = Reference(agency="org", identifier="t1", version="1.0")
        source = _make(identifier="s1")
        source.refs = [ref]

        doc = StubDocument([target, source])
        refs = doc.find_references_to(target)
        assert ref in refs

    def test_no_references(self):
        target = _make(identifier="t1", agency="org", version="1.0")
        source = _make(identifier="s1")
        doc = StubDocument([target, source])
        refs = doc.find_references_to(target)
        assert refs == []


class TestFilter:
    def test_predicate(self):
        m1 = _make(identifier="a", version="1.0")
        m2 = _make(identifier="b", version="2.0")
        doc = StubDocument([m1, m2])
        result = doc.filter(lambda m: m.version == "2.0")
        assert result == [m2]

    def test_with_type_filter(self):
        s = _make(StubMaintainable, identifier="a", version="1.0")
        v = _make(StubVariable, identifier="b", version="1.0")
        doc = StubDocument([s, v])
        result = doc.filter(lambda m: True, StubVariable)
        assert result == [v]

    def test_filter_by_agency(self):
        m1 = _make(agency="org1")
        m2 = _make(agency="org2")
        doc = StubDocument([m1, m2])
        assert doc.filter_by_agency("org1") == [m1]

    def test_filter_by_version(self):
        m1 = _make(version="1.0")
        m2 = _make(version="2.0")
        doc = StubDocument([m1, m2])
        assert doc.filter_by_version("2.0") == [m2]


# ===========================================================================
# MaintainableAccessor
# ===========================================================================


class TestMaintainableAccessor:
    def test_getitem(self):
        m = _make(StubMaintainable, identifier="x")
        doc = StubDocument([m])
        accessor = MaintainableAccessor(doc, StubMaintainable)
        assert accessor["x"] is m

    def test_getitem_not_found(self):
        doc = StubDocument([])
        accessor = MaintainableAccessor(doc, StubMaintainable)
        with pytest.raises(KeyError, match="StubMaintainable not found"):
            accessor["missing"]

    def test_get_found(self):
        m = _make(StubMaintainable, identifier="x")
        doc = StubDocument([m])
        accessor = MaintainableAccessor(doc, StubMaintainable)
        assert accessor.get("x") is m

    def test_get_default(self):
        doc = StubDocument([])
        accessor = MaintainableAccessor(doc, StubMaintainable)
        assert accessor.get("missing") is None
        assert accessor.get("missing", "fallback") == "fallback"

    def test_iter(self):
        m1 = _make(StubMaintainable, identifier="a")
        m2 = _make(StubMaintainable, identifier="b")
        doc = StubDocument([m1, m2])
        accessor = MaintainableAccessor(doc, StubMaintainable)
        assert list(accessor) == [m1, m2]

    def test_len(self):
        doc = StubDocument([_make(StubMaintainable), _make(StubMaintainable)])
        accessor = MaintainableAccessor(doc, StubMaintainable)
        assert len(accessor) == 2

    def test_contains(self):
        m = _make(StubMaintainable, identifier="x")
        doc = StubDocument([m])
        accessor = MaintainableAccessor(doc, StubMaintainable)
        assert "x" in accessor
        assert "y" not in accessor

    def test_find(self):
        m = _make(StubMaintainable, labels=[_label("hello world")])
        doc = StubDocument([m])
        accessor = MaintainableAccessor(doc, StubMaintainable)
        assert accessor.find("hello") == [m]
        assert accessor.find("hello", exact=True) == []

    def test_all(self):
        m = _make(StubMaintainable, identifier="a")
        doc = StubDocument([m])
        accessor = MaintainableAccessor(doc, StubMaintainable)
        assert accessor.all() == [m]


# ===========================================================================
# DocumentManipulationMixin
# ===========================================================================


class TestBulkUpdateAgency:
    def test_update(self):
        m1 = _make(agency="old")
        m2 = _make(agency="other")
        doc = StubDocument([m1, m2])
        count = doc.bulk_update_agency("old", "new")
        assert count == 1
        assert m1.agency == "new"
        assert m2.agency == "other"

    def test_updates_urn(self):
        m = _make(agency="old")
        m.urn = "urn:ddi:old:id1:1.0"
        doc = StubDocument([m])
        doc.bulk_update_agency("old", "new")
        assert m.urn == "urn:ddi:new:id1:1.0"

    def test_updates_references(self):
        m = _make(agency="old")
        ref = Reference(agency="old", identifier="r1", version="1.0")
        m.concept_reference = ref
        doc = StubDocument([m])
        doc.bulk_update_agency("old", "new", update_references=True)
        assert ref.agency == "new"

    def test_skip_reference_update(self):
        m = _make(agency="old")
        ref = Reference(agency="old")
        m.concept_reference = ref
        doc = StubDocument([m])
        doc.bulk_update_agency("old", "new", update_references=False)
        assert ref.agency == "old"

    def test_reference_in_list(self):
        m = _make(agency="other")
        ref = Reference(agency="old")
        m.refs = [ref]
        doc = StubDocument([m])
        doc.bulk_update_agency("old", "new")
        assert ref.agency == "new"


class TestIncrementAllVersions:
    def test_minor(self):
        m = _make(version="1.0")
        doc = StubDocument([m])
        count = doc.increment_all_versions("minor")
        assert count == 1
        # Version should have been incremented
        assert m.version != "1.0"

    def test_major(self):
        m = _make(version="1.0")
        doc = StubDocument([m])
        count = doc.increment_all_versions("major")
        assert count == 1

    def test_patch(self):
        m = _make(version="1.0")
        doc = StubDocument([m])
        count = doc.increment_all_versions("patch")
        assert count == 1

    def test_type_filter(self):
        s = _make(StubMaintainable, version="1.0")
        v = _make(StubVariable, version="1.0")
        doc = StubDocument([s, v])
        count = doc.increment_all_versions("minor", StubVariable)
        assert count == 1


class TestRemoveByIdentifier:
    def test_remove_found(self):
        m = _make(identifier="abc")
        doc = StubDocument([m])
        assert doc.remove_by_identifier("abc") is True
        assert list(doc.iter_maintainables()) == []

    def test_remove_not_found(self):
        doc = StubDocument([_make(identifier="abc")])
        assert doc.remove_by_identifier("xyz") is False

    def test_type_filter(self):
        s = _make(StubMaintainable, identifier="x")
        v = _make(StubVariable, identifier="x")
        doc = StubDocument([s, v])
        assert doc.remove_by_identifier("x", StubVariable) is True
        assert list(doc.iter_maintainables()) == [s]


class TestRemoveAll:
    def test_remove_all_of_type(self):
        s1 = _make(StubMaintainable, identifier="a")
        s2 = _make(StubMaintainable, identifier="b")
        v = _make(StubVariable, identifier="c")
        doc = StubDocument([s1, s2, v])
        count = doc.remove_all(StubMaintainable)
        assert count == 2
        assert list(doc.iter_maintainables()) == [v]


class TestCloneMaintainable:
    def test_clone_with_defaults(self):
        m = _make(identifier="orig", agency="org", version="1.0")
        doc = StubDocument([m])
        clone = doc.clone_maintainable(m)
        assert clone.identifier != "orig"
        assert clone.version == "1.0"
        assert clone.urn is None
        assert clone in list(doc.iter_maintainables())

    def test_clone_with_custom_id(self):
        m = _make(identifier="orig")
        doc = StubDocument([m])
        clone = doc.clone_maintainable(m, new_identifier="custom", new_version="2.0")
        assert clone.identifier == "custom"
        assert clone.version == "2.0"

    def test_clone_without_add(self):
        m = _make()
        doc = StubDocument([m])
        doc.clone_maintainable(m, add_to_document=False)
        assert len(list(doc.iter_maintainables())) == 1


class TestMergeFrom:
    def test_merge_new(self):
        m1 = _make(identifier="a", agency="org")
        m2 = _make(identifier="b", agency="org")
        doc1 = StubDocument([m1])
        doc2 = StubDocument([m2])
        count = doc1.merge_from(doc2)
        assert count == 1
        assert len(list(doc1.iter_maintainables())) == 2

    def test_merge_existing_no_overwrite(self):
        m1 = _make(identifier="a", agency="org", version="1.0")
        m2 = _make(identifier="a", agency="org", version="2.0")
        doc1 = StubDocument([m1])
        doc2 = StubDocument([m2])
        count = doc1.merge_from(doc2, overwrite=False)
        assert count == 0

    def test_merge_existing_with_overwrite(self):
        m1 = _make(identifier="a", agency="org", version="1.0")
        m2 = _make(identifier="a", agency="org", version="2.0")
        doc1 = StubDocument([m1])
        doc2 = StubDocument([m2])
        count = doc1.merge_from(doc2, overwrite=True)
        assert count == 1

    def test_merge_type_filter(self):
        s = _make(StubMaintainable, identifier="a", agency="org")
        v = _make(StubVariable, identifier="b", agency="org")
        doc1 = StubDocument([])
        doc2 = StubDocument([s, v])
        count = doc1.merge_from(doc2, type_filter=StubVariable)
        assert count == 1


# ===========================================================================
# DocumentStatsMixin
# ===========================================================================


class TestSummary:
    def test_summary(self):
        m1 = _make(StubMaintainable, identifier="a", agency="org1", version="1.0")
        m2 = _make(StubVariable, identifier="b", agency="org2", version="2.0")
        doc = StubDocument([m1, m2])
        stats = doc.summary()
        assert stats["total_maintainables"] == 2
        assert "StubMaintainable" in stats["by_type"]
        assert "StubVariable" in stats["by_type"]
        assert stats["unique_agencies"] == 2
        assert stats["unique_versions"] == 2

    def test_empty_summary(self):
        doc = StubDocument([])
        stats = doc.summary()
        assert stats["total_maintainables"] == 0


class TestTypeCounts:
    def test_counts(self):
        doc = StubDocument(
            [
                _make(StubMaintainable, identifier="a"),
                _make(StubMaintainable, identifier="b"),
                _make(StubVariable, identifier="c"),
            ]
        )
        counts = doc.type_counts()
        assert counts["StubMaintainable"] == 2
        assert counts["StubVariable"] == 1


class TestPrintSummary:
    def test_prints(self, capsys):
        m = _make(StubMaintainable, identifier="a", agency="org", version="1.0")
        doc = StubDocument([m])
        doc.print_summary()
        captured = capsys.readouterr()
        assert "DDI Document Summary" in captured.out
        assert "Total maintainables: 1" in captured.out
        assert "StubMaintainable: 1" in captured.out
