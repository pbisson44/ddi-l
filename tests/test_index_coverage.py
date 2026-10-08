"""Edge cases and error paths in ddi_l.index."""

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import REUSABLE_NS
from ddi_l.document import DDIDocument
from ddi_l.index import (
    Index,
    ResourceCollection,
    _extract_urn,
    _reference_key,
)
from ddi_l.models.base import Reference, qn
from ddi_l.models.concept import Concept, ConceptualVariable, UnitType, Universe
from ddi_l.models.conceptualcomponent import ConceptualComponent
from ddi_l.models.datacollection import DataCollection, Instrument, QuestionItem
from ddi_l.models.logicalproduct import CodeList, LogicalProduct, Variable
from ddi_l.models.study import StudyUnit

# ---------------------------------------------------------------------------
# ResourceCollection
# ---------------------------------------------------------------------------


def test_resource_collection_add_and_iter():
    col = ResourceCollection()  # type: ignore[var-annotated]
    v = Variable(agency="a", identifier="v1", version="1.0")
    meta = col.add(v)
    assert meta.key == ("a", "v1", "1.0")
    assert list(col) == [v]


def test_resource_collection_add_duplicate_same_object():
    col = ResourceCollection()  # type: ignore[var-annotated]
    v = Variable(agency="a", identifier="v1", version="1.0")
    col.add(v)
    meta2 = col.add(v)  # same object is fine
    assert meta2.key == ("a", "v1", "1.0")


def test_resource_collection_add_duplicate_urn():
    col = ResourceCollection()  # type: ignore[var-annotated]
    v1 = Variable(agency="a", identifier="v1", version="1.0", urn="urn:ddi:a:v1:1.0")
    v2 = Variable(agency="a", identifier="v2", version="1.0", urn="urn:ddi:a:v1:1.0")
    col.add(v1)
    with pytest.raises(ValueError, match="Duplicate URN"):
        col.add(v2)


def test_resource_collection_add_duplicate_key():
    col = ResourceCollection()  # type: ignore[var-annotated]
    v1 = Variable(agency="a", identifier="v1", version="1.0")
    v2 = Variable(agency="a", identifier="v1", version="1.0")
    col.add(v1)
    with pytest.raises(ValueError, match="Duplicate identifier"):
        col.add(v2)


def test_resource_collection_no_identifier():
    col = ResourceCollection()  # type: ignore[var-annotated]
    v = Variable(agency="a", identifier="", version="1.0")
    meta = col.add(v)
    assert meta.key is None


def test_resource_collection_iter_identifier_matches():
    col = ResourceCollection()  # type: ignore[var-annotated]
    v1 = Variable(agency="a", identifier="v1", version="1.0")
    v2 = Variable(agency="b", identifier="v1", version="2.0")
    col.add(v1)
    col.add(v2)
    matches = list(col.iter_identifier_matches("v1"))
    assert len(matches) == 2


def test_resource_collection_iter_identifier_matches_empty():
    col = ResourceCollection()  # type: ignore[var-annotated]
    matches = list(col.iter_identifier_matches("nonexistent"))
    assert matches == []


def test_resource_collection_iter_identifier_version_matches():
    col = ResourceCollection()  # type: ignore[var-annotated]
    v1 = Variable(agency="a", identifier="v1", version="1.0")
    v2 = Variable(agency="b", identifier="v1", version="2.0")
    col.add(v1)
    col.add(v2)
    matches = list(col.iter_identifier_version_matches("v1", "1.0"))
    assert len(matches) == 1


# ---------------------------------------------------------------------------
# _extract_urn / _reference_key
# ---------------------------------------------------------------------------


def test_extract_urn_from_attribute():
    v = Variable(agency="a", identifier="v1", version="1.0", urn="urn:ddi:a:v1:1.0")
    assert _extract_urn(v) == "urn:ddi:a:v1:1.0"


def test_extract_urn_from_other_elements():
    v = Variable(agency="a", identifier="v1", version="1.0")
    urn_elem = create_element(qn(REUSABLE_NS, "URN"))
    urn_elem.text = "urn:ddi:a:v1:1.0"
    v.other_elements.append(urn_elem)
    assert _extract_urn(v) == "urn:ddi:a:v1:1.0"


def test_extract_urn_none():
    v = Variable(agency="a", identifier="v1", version="1.0")
    assert _extract_urn(v) is None


def test_reference_key_with_identifier():
    ref = Reference(agency="a", identifier="v1", version="1.0")
    assert _reference_key(ref) == ("a", "v1", "1.0")


def test_reference_key_no_identifier():
    ref = Reference(urn="urn:ddi:a:v1:1.0")
    assert _reference_key(ref) is None


# ---------------------------------------------------------------------------
# Index — basic operations
# ---------------------------------------------------------------------------


def test_index_maintainable_classes():
    classes = Index.maintainable_classes()
    assert Variable in classes


def test_index_register_fragment_single():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0")
    idx.register_fragment(v)
    results = list(idx.iter_resources(Variable))
    assert len(results) == 1


def test_index_register_fragment_list():
    idx = Index()
    v1 = Variable(agency="a", identifier="v1", version="1.0")
    v2 = Variable(agency="a", identifier="v2", version="1.0")
    idx.register_fragment([v1, v2])  # type: ignore[arg-type]
    assert len(list(idx.iter_resources(Variable))) == 2


def test_index_register_fragment_unsupported_type():
    idx = Index()
    with pytest.raises(TypeError, match="Unsupported"):
        idx.register_fragment("not a maintainable")  # type: ignore[arg-type]


def test_index_iter_resources_empty():
    idx = Index()
    assert list(idx.iter_resources(Variable)) == []


# ---------------------------------------------------------------------------
# Index — resolve
# ---------------------------------------------------------------------------


def test_index_resolve_by_urn():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0", urn="urn:ddi:a:v1:1.0")
    idx.register_fragment(v)
    ref = Reference(urn="urn:ddi:a:v1:1.0", type_of_object="Variable")
    result = idx.resolve(ref, expected_type=Variable)
    assert result is v


def test_index_resolve_by_identifier():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0")
    idx.register_fragment(v)
    ref = Reference(
        agency="a", identifier="v1", version="1.0", type_of_object="Variable"
    )
    result = idx.resolve(ref, expected_type=Variable)
    assert result is v


def test_index_resolve_not_found():
    idx = Index()
    ref = Reference(identifier="nonexistent", type_of_object="Variable")
    with pytest.raises(LookupError, match="Could not resolve"):
        idx.resolve(ref)


def test_index_resolve_ambiguous():
    idx = Index()
    v1 = Variable(agency="a", identifier="v1", version="1.0")
    cl = CodeList(agency="a", identifier="v1", version="1.0")
    idx.register_fragment(v1)
    idx.register_fragment(cl)
    ref = Reference(identifier="v1")
    with pytest.raises(LookupError, match="ambiguous"):
        idx.resolve(ref)


def test_index_resolve_relaxed_no_agency():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0")
    idx.register_fragment(v)
    ref = Reference(identifier="v1", version="1.0", type_of_object="Variable")
    result = idx.resolve(ref, expected_type=Variable)
    assert result is v


def test_index_resolve_relaxed_identifier_only():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0")
    idx.register_fragment(v)
    ref = Reference(identifier="v1", type_of_object="Variable")
    result = idx.resolve(ref, expected_type=Variable)
    assert result is v


def test_index_resolve_relaxed_multiple_raises():
    idx = Index()
    v1 = Variable(agency="a", identifier="v1", version="1.0")
    v2 = Variable(agency="b", identifier="v1", version="1.0")
    idx.register_fragment(v1)
    idx.register_fragment(v2)
    ref = Reference(identifier="v1", type_of_object="Variable")
    with pytest.raises(LookupError, match="multiple"):
        idx.resolve(ref, expected_type=Variable)


def test_index_resolve_by_type_of_object():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0")
    idx.register_fragment(v)
    ref = Reference(identifier="v1", type_of_object="Variable")
    result = idx.resolve(ref)
    assert result is v


def test_index_resolve_unknown_type_of_object():
    idx = Index()
    ref = Reference(identifier="x", type_of_object="NonExistent")
    with pytest.raises(LookupError, match="Unsupported TypeOfObject"):
        idx.resolve(ref)


# ---------------------------------------------------------------------------
# Index — get_variable
# ---------------------------------------------------------------------------


def test_index_get_variable():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0")
    idx.register_fragment(v)
    result = idx.get_variable("v1", agency="a", version="1.0")
    assert result is v


def test_index_get_variable_not_found():
    idx = Index()
    with pytest.raises(LookupError):
        idx.get_variable("nonexistent")


# ---------------------------------------------------------------------------
# Index — find_questions
# ---------------------------------------------------------------------------


def test_index_find_questions_empty():
    idx = Index()
    assert idx.find_questions() == []


def test_index_find_questions_no_filter():
    idx = Index()
    q = QuestionItem(agency="a", identifier="q1", version="1.0")
    idx.register_fragment(q)
    assert len(idx.find_questions()) == 1


def test_index_find_questions_insufficient_data():
    idx = Index()
    q = QuestionItem(agency="a", identifier="q1", version="1.0")
    idx.register_fragment(q)
    ref = Reference()  # no URN, no identifier
    with pytest.raises(LookupError, match="Insufficient"):
        idx.find_questions(using_code_list=ref)


# ---------------------------------------------------------------------------
# Index — get_variables_referencing_question
# ---------------------------------------------------------------------------


def test_index_get_variables_referencing_question():
    idx = Index()
    q = QuestionItem(agency="a", identifier="q1", version="1.0")
    v = Variable(
        agency="a",
        identifier="v1",
        version="1.0",
        question_references=[
            Reference(
                identifier="q1",
                agency="a",
                version="1.0",
                type_of_object="QuestionItem",
            )
        ],
    )
    idx.register_fragment(q)
    idx.register_fragment(v)
    results = idx.get_variables_referencing_question(q)
    assert len(results) == 1
    assert results[0] is v


def test_index_get_variables_referencing_question_none():
    idx = Index()
    q = QuestionItem(agency="a", identifier="q1", version="1.0")
    idx.register_fragment(q)
    results = idx.get_variables_referencing_question(q)
    assert results == []


# ---------------------------------------------------------------------------
# Index — _coerce_resource
# ---------------------------------------------------------------------------


def test_index_coerce_resource_passthrough():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0")
    idx.register_fragment(v)
    result = idx._coerce_resource(v, Variable)
    assert result is v


def test_index_coerce_resource_reference():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0")
    idx.register_fragment(v)
    ref = Reference(
        identifier="v1", agency="a", version="1.0", type_of_object="Variable"
    )
    result = idx._coerce_resource(ref, Variable)
    assert result is v


def test_index_coerce_resource_urn_string():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0", urn="urn:ddi:a:v1:1.0")
    idx.register_fragment(v)
    result = idx._coerce_resource("urn:ddi:a:v1:1.0", Variable)
    assert result is v


def test_index_coerce_resource_tuple():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0")
    idx.register_fragment(v)
    result = idx._coerce_resource(("a", "v1", "1.0"), Variable)
    assert result is v


def test_index_coerce_resource_tuple_wrong_length():
    idx = Index()
    with pytest.raises(ValueError, match="agency, identifier, version"):
        idx._coerce_resource(("a", "b"), Variable)  # type: ignore[arg-type]


def test_index_coerce_resource_unsupported():
    idx = Index()
    with pytest.raises(TypeError, match="Unsupported"):
        idx._coerce_resource(42, Variable)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Index — _normalize_reference_details
# ---------------------------------------------------------------------------


def test_normalize_reference_details_maintainable():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0")
    resource, meta = idx._normalize_reference_details(v, Variable)
    assert resource is v
    assert meta.key == ("a", "v1", "1.0")


def test_normalize_reference_details_reference():
    idx = Index()
    ref = Reference(urn="urn:ddi:a:v1:1.0", identifier="v1", agency="a", version="1.0")
    resource, meta = idx._normalize_reference_details(ref, Variable)
    assert resource is None
    assert meta.urn == "urn:ddi:a:v1:1.0"


def test_normalize_reference_details_string_registered():
    idx = Index()
    v = Variable(agency="a", identifier="v1", version="1.0", urn="urn:ddi:a:v1:1.0")
    idx.register_fragment(v)
    resource, meta = idx._normalize_reference_details("urn:ddi:a:v1:1.0", Variable)
    assert resource is None
    assert meta.urn == "urn:ddi:a:v1:1.0"


def test_normalize_reference_details_string_not_registered():
    idx = Index()
    resource, meta = idx._normalize_reference_details("urn:ddi:x:y:1.0", Variable)
    assert resource is None
    assert meta.urn == "urn:ddi:x:y:1.0"
    assert meta.key is None


def test_normalize_reference_details_tuple():
    idx = Index()
    resource, meta = idx._normalize_reference_details(("a", "v1", "1.0"), Variable)
    assert resource is None
    assert meta.key == ("a", "v1", "1.0")


def test_normalize_reference_details_tuple_wrong_length():
    idx = Index()
    with pytest.raises(ValueError):
        idx._normalize_reference_details(("a", "b"), Variable)  # type: ignore[arg-type]


def test_normalize_reference_details_unsupported():
    idx = Index()
    with pytest.raises(TypeError):
        idx._normalize_reference_details(42, Variable)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Index — hierarchical registration
# ---------------------------------------------------------------------------


def test_index_register_study_unit():
    idx = Index()
    su = StudyUnit(agency="a", identifier="su1", version="1.0")
    idx.register_fragment(su)
    assert len(list(idx.iter_resources(StudyUnit))) == 1


def test_index_register_logical_product():
    idx = Index()
    lp = LogicalProduct(
        agency="a",
        identifier="lp1",
        version="1.0",
        variables=[Variable(agency="a", identifier="v1", version="1.0")],
        code_lists=[CodeList(agency="a", identifier="cl1", version="1.0")],
    )
    idx.register_fragment(lp)
    assert len(list(idx.iter_resources(Variable))) == 1
    assert len(list(idx.iter_resources(CodeList))) == 1


def test_index_register_data_collection():
    idx = Index()
    dc = DataCollection(
        agency="a",
        identifier="dc1",
        version="1.0",
        questions=[QuestionItem(agency="a", identifier="q1", version="1.0")],
        instruments=[Instrument(agency="a", identifier="i1", version="1.0")],
    )
    idx.register_fragment(dc)
    assert len(list(idx.iter_resources(QuestionItem))) == 1
    assert len(list(idx.iter_resources(Instrument))) == 1


def test_index_register_conceptual_component():
    idx = Index()
    cc = ConceptualComponent(
        agency="a",
        identifier="cc1",
        version="1.0",
        concepts=[Concept(agency="a", identifier="c1", version="1.0")],
        universes=[Universe(agency="a", identifier="u1", version="1.0")],
        conceptual_variables=[
            ConceptualVariable(agency="a", identifier="cv1", version="1.0")
        ],
        unit_types=[UnitType(agency="a", identifier="ut1", version="1.0")],
    )
    idx.register_fragment(cc)
    assert len(list(idx.iter_resources(Concept))) == 1
    assert len(list(idx.iter_resources(Universe))) == 1


def test_index_from_document():
    doc = DDIDocument.create(agency="a", identifier="doc", version="1.0")
    idx = Index.from_document(doc)
    assert isinstance(idx, Index)
